package com.sifreelee.intro;

import android.content.Context;
import android.content.SharedPreferences;
import android.net.ConnectivityManager;
import android.net.NetworkCapabilities;
import android.net.NetworkInfo;
import android.os.Build;
import android.webkit.MimeTypeMap;

import org.json.JSONArray;
import org.json.JSONObject;

import java.io.ByteArrayOutputStream;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.InputStream;
import java.net.HttpURLConnection;
import java.net.URL;
import java.security.MessageDigest;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicInteger;

/**
 * 站点离线缓存。
 *
 * 设计：
 * 1. 所有响应体落盘到应用私有目录 files/webcache，索引单独存 index.json。
 * 2. 拦截层做「缓存优先」——有缓存直接返回文件，没有才走网络，
 *    保证弱网/断网时页面能立刻起来。
 * 3. 后台同步用条件请求（If-None-Match / If-Modified-Since），
 *    服务端 304 就跳过，只下载真正变化的资源，实现增量更新。
 */
public class WebCache {

    /** 缓存策略：不缓存 / 仅页面与文字（旧版遗留） / 全量 / 仅打开时缓存 */
    public static final int MODE_OFF = 0;
    public static final int MODE_SHELL = 1;
    public static final int MODE_FULL = 2;
    /** 仅缓存用户实际打开过的内容：不主动同步，交给 WebView 自身的 HTTP 缓存 */
    public static final int MODE_OPENED = 3;

    private static final String PREF = "webcache_pref";
    private static final String KEY_MODE = "mode";
    private static final String KEY_WIFI_ONLY = "wifi_only";
    private static final String KEY_LAST_SYNC = "last_sync";

    private static final String DIR_NAME = "webcache";
    private static final String INDEX_NAME = "index.json";
    private static final int THREADS = 4;

    private final Context app;
    private final File dir;
    private final File indexFile;
    private final Map<String, Entry> entries = new ConcurrentHashMap<>();
    private final Object indexLock = new Object();
    private final SharedPreferences prefs;

    // 同步进度（由设置面板轮询读取，故用 volatile 而非回调）
    private volatile int pDone;
    private volatile int pTotal;
    private volatile long pBytes;
    private volatile boolean syncing;

    /** 单条缓存记录 */
    public static class Entry {
        String url;
        String fileName;
        String etag;
        String lastModified;
        String hash;
        long size;
        long savedAt;
        /**
         * 上次与服务器核对的时间（可能只是 304，文件没重写）。
         * 与 savedAt 分开记，才能实现「本地已有就不联网」。
         */
        long checkedAt;
    }

    /**
     * 图片等媒体文件的核对保质期：这段时间内本地已有就不再发请求。
     * 页面 / 样式 / 脚本不适用，每次同步都会核对，保证站点改版立刻可见。
     */
    private static final long MEDIA_CHECK_TTL_MS = 7L * 24 * 3600 * 1000;

    /** 同步结果统计 */
    public static class SyncResult {
        public int added;
        public int updated;
        public int unchanged;
        public int failed;
        public int skipped;

        public int changed() {
            return added + updated;
        }

        public String summary() {
            return "新增 " + added + "，更新 " + updated
                    + "，未变 " + unchanged
                    + (failed > 0 ? "，失败 " + failed : "")
                    + (skipped > 0 ? "，跳过 " + skipped : "");
        }
    }

    private static WebCache instance;

    public static synchronized WebCache get(Context ctx) {
        if (instance == null) instance = new WebCache(ctx.getApplicationContext());
        return instance;
    }

    private WebCache(Context ctx) {
        this.app = ctx;
        this.dir = new File(ctx.getFilesDir(), DIR_NAME);
        if (!dir.exists()) dir.mkdirs();
        this.indexFile = new File(dir, INDEX_NAME);
        this.prefs = ctx.getSharedPreferences(PREF, Context.MODE_PRIVATE);
        loadIndex();
        // 旧版「仅页面文字」这一档已从界面移除，读到就归并到「仅打开时缓存」，
        // 避免出现「选项显示仅打开、实际行为却是旧逻辑」的错位
        if (getMode() == MODE_SHELL) setMode(MODE_OPENED);
    }

    // ───────────────────────── 配置 ─────────────────────────

    public int getMode() {
        return prefs.getInt(KEY_MODE, -1); // -1 表示尚未询问过
    }

    public void setMode(int mode) {
        prefs.edit().putInt(KEY_MODE, mode).apply();
    }

    public boolean isFirstRun() {
        return getMode() < 0;
    }

    public boolean isEnabled() {
        return getMode() > MODE_OFF;
    }

    /** 是否由本缓存层提供内容（全量/仅页面文字）；「仅打开」交给 WebView 自身缓存 */
    public boolean shouldServeFromCache() {
        int m = getMode();
        return m == MODE_FULL || m == MODE_SHELL;
    }

    /** 当前是否正在同步 */
    public boolean isSyncing() {
        return syncing;
    }

    public int progressDone() {
        return pDone;
    }

    public int progressTotal() {
        return pTotal;
    }

    public long progressBytes() {
        return pBytes;
    }

    public boolean isWifiOnly() {
        return prefs.getBoolean(KEY_WIFI_ONLY, true);
    }

    public void setWifiOnly(boolean v) {
        prefs.edit().putBoolean(KEY_WIFI_ONLY, v).apply();
    }

    public long getLastSync() {
        return prefs.getLong(KEY_LAST_SYNC, 0L);
    }

    public boolean isOnWifi() {
        ConnectivityManager cm = (ConnectivityManager)
                app.getSystemService(Context.CONNECTIVITY_SERVICE);
        if (cm == null) return false;
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
            NetworkCapabilities nc = cm.getNetworkCapabilities(cm.getActiveNetwork());
            if (nc == null) return false;
            // 判定为「不计费网络」即视作 Wi-Fi / 以太网
            return nc.hasCapability(NetworkCapabilities.NET_CAPABILITY_NOT_METERED);
        }
        NetworkInfo info = cm.getActiveNetworkInfo();
        return info != null && info.isConnected()
                && info.getType() == ConnectivityManager.TYPE_WIFI;
    }

    public boolean isOnline() {
        ConnectivityManager cm = (ConnectivityManager)
                app.getSystemService(Context.CONNECTIVITY_SERVICE);
        if (cm == null) return false;
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
            NetworkCapabilities nc = cm.getNetworkCapabilities(cm.getActiveNetwork());
            return nc != null && nc.hasCapability(NetworkCapabilities.NET_CAPABILITY_INTERNET);
        }
        NetworkInfo info = cm.getActiveNetworkInfo();
        return info != null && info.isConnected();
    }

    // ───────────────────────── 读取 ─────────────────────────

    public File fileFor(String url) {
        Entry e = entries.get(url);
        if (e == null) return null;
        File f = new File(dir, e.fileName);
        return f.exists() ? f : null;
    }

    public int count() {
        return entries.size();
    }

    public long totalBytes() {
        long sum = 0;
        for (Entry e : entries.values()) sum += e.size;
        return sum;
    }

    // ───────────────────────── 写入 ─────────────────────────

    private void put(String url, byte[] data, String etag, String lastModified,
                     String hash) throws Exception {
        String name = sha1(url) + extOf(url);
        File f = new File(dir, name);
        File tmp = new File(dir, name + ".tmp");
        FileOutputStream fos = null;
        try {
            fos = new FileOutputStream(tmp);
            fos.write(data);
            fos.flush();
            if (f.exists() && !f.delete()) {
                // 删不掉就覆盖写，不影响正确性
            }
            if (!tmp.renameTo(f)) {
                // 部分文件系统不允许改名，退化为复制
                FileOutputStream direct = new FileOutputStream(f);
                direct.write(data);
                direct.close();
                tmp.delete();
            }
        } finally {
            if (fos != null) fos.close();
        }

        Entry e = new Entry();
        e.url = url;
        e.fileName = name;
        e.etag = etag;
        e.lastModified = lastModified;
        e.hash = hash;
        e.size = data.length;
        e.savedAt = System.currentTimeMillis();
        e.checkedAt = e.savedAt;
        entries.put(url, e);
    }

    // ───────────────────────── 同步 ─────────────────────────

    /**
     * 增量同步一组 URL。
     *
     * 默认是「只补缺口」：本地已有且仍在保质期内的图片直接跳过，一个请求都不发；
     * 页面 / 样式 / 脚本每次都会核对，保证站点改版能立刻被发现。
     *
     * @param urls   待同步的绝对地址（调用方给的是当前页枚举到的清单）
     * @param deep   true = 忽略保质期，全部与服务器核对一遍（手动「立即同步」用）
     * @param onDone 回调
     */
    public void sync(final List<String> urls, final String userAgent,
                     final boolean deep, final SyncCallback onDone) {
        final int mode = getMode();
        // MODE_OPENED 也允许同步：调用方传入的是「当前这一页」的资源清单，
        // 于是天然等于「浏览过的才留下」，不需要额外逻辑。
        if (mode != MODE_FULL && mode != MODE_SHELL && mode != MODE_OPENED) {
            if (onDone != null) {
                onDone.onFinished(new SyncResult(), false, "缓存未开启");
            }
            return;
        }
        if (urls == null || urls.isEmpty()) {
            if (onDone != null) onDone.onFinished(new SyncResult(), false, "没有可同步的资源");
            return;
        }
        if (isWifiOnly() && !isOnWifi()) {
            if (onDone != null) onDone.onFinished(new SyncResult(), false, "当前非 Wi-Fi，已按设置跳过");
            return;
        }

        final long now = System.currentTimeMillis();
        final List<String> targets = new ArrayList<>();
        int preSkipped = 0;
        for (String u : urls) {
            if (u == null) continue;
            if (mode == MODE_SHELL && isMedia(u)) continue; // 只缓存页面与文字
            // 本地已有 + 在保质期内 + 是图片这类不会随页面改版而变的东西 → 直接跳过
            if (!deep && isMedia(u)) {
                Entry e = entries.get(u);
                if (e != null && e.checkedAt > 0
                        && now - e.checkedAt < MEDIA_CHECK_TTL_MS) {
                    preSkipped++;
                    continue;
                }
            }
            targets.add(u);
        }

        final SyncResult result = new SyncResult();
        result.skipped = preSkipped;
        final AtomicInteger index = new AtomicInteger(0);
        final java.util.concurrent.atomic.AtomicLong bytes =
                new java.util.concurrent.atomic.AtomicLong(0);
        final ExecutorService pool = Executors.newFixedThreadPool(THREADS);
        // 进度只统计真正要处理的项，避免「跑了 695 项其实只下 20 个」的错觉
        final int total = targets.size();

        pDone = 0;
        pTotal = total;
        pBytes = 0;
        syncing = true;

        for (final String url : targets) {
            pool.execute(new Runnable() {
                @Override
                public void run() {
                    int r = fetchOne(url, userAgent, bytes);
                    synchronized (result) {
                        if (r == R_ADDED) result.added++;
                        else if (r == R_UPDATED) result.updated++;
                        else if (r == R_UNCHANGED) result.unchanged++;
                        else result.failed++;
                    }
                    pDone = index.incrementAndGet();
                    pBytes = bytes.get();
                }
            });
        }

        pool.shutdown();
        new Thread(new Runnable() {
            @Override
            public void run() {
                try {
                    pool.awaitTermination(30, TimeUnit.MINUTES);
                } catch (InterruptedException ignored) {
                }
                syncing = false;
                saveIndex();
                prefs.edit().putLong(KEY_LAST_SYNC, System.currentTimeMillis()).apply();
                if (onDone != null) {
                    onDone.onFinished(result, true,
                            total == 0 && result.skipped > 0
                                    ? "本地已是最新，无需重新缓存"
                                    : "共 " + total + " 项需核对");
                }
            }
        }).start();
    }

    private static final int R_ADDED = 0;
    private static final int R_UPDATED = 1;
    private static final int R_UNCHANGED = 2;
    private static final int R_FAILED = 3;

    private int fetchOne(String url, String userAgent,
                         java.util.concurrent.atomic.AtomicLong bytes) {
        HttpURLConnection conn = null;
        try {
            Entry old = entries.get(url);
            conn = (HttpURLConnection) new URL(url).openConnection();
            conn.setConnectTimeout(15000);
            conn.setReadTimeout(40000);
            conn.setInstanceFollowRedirects(true);
            if (userAgent != null) conn.setRequestProperty("User-Agent", userAgent);
            if (old != null) {
                if (old.etag != null) conn.setRequestProperty("If-None-Match", old.etag);
                if (old.lastModified != null) {
                    conn.setRequestProperty("If-Modified-Since", old.lastModified);
                }
            }

            int code = conn.getResponseCode();
            if (code == HttpURLConnection.HTTP_NOT_MODIFIED) {
                // 服务器确认没变：只把「核对时间」推到当下，文件不动、流量几乎为零
                if (old != null) old.checkedAt = System.currentTimeMillis();
                return R_UNCHANGED;
            }
            if (code != HttpURLConnection.HTTP_OK) {
                return R_FAILED;
            }

            byte[] data = readAll(conn.getInputStream(), 24 * 1024 * 1024);
            if (data == null) return R_FAILED;

            // 服务端若没按预期返回 304，可能出现「200 但内容其实没变」，
            // 用内容哈希兜底，避免每次都判成更新、白白重写文件并触发页面刷新
            String hash = sha1Bytes(data);
            if (old != null && hash.equals(old.hash)) {
                old.checkedAt = System.currentTimeMillis();
                return R_UNCHANGED;
            }

            put(url, data,
                    conn.getHeaderField("ETag"),
                    conn.getHeaderField("Last-Modified"),
                    hash);
            bytes.addAndGet(data.length);
            return old == null ? R_ADDED : R_UPDATED;
        } catch (Exception e) {
            return R_FAILED;
        } finally {
            if (conn != null) conn.disconnect();
        }
    }

    /** 首次全量缓存：不排除任何资源 */
    public List<String> filterForMode(List<String> urls) {
        if (getMode() != MODE_SHELL) return urls;
        List<String> out = new ArrayList<>();
        for (String u : urls) if (!isMedia(u)) out.add(u);
        return out;
    }

    public void clear() {
        entries.clear();
        File[] files = dir.listFiles();
        if (files != null) {
            for (File f : files) if (!INDEX_NAME.equals(f.getName())) f.delete();
        }
        prefs.edit().remove(KEY_LAST_SYNC).apply();
    }

    // ───────────────────────── 索引持久化 ─────────────────────────

    private void loadIndex() {
        if (!indexFile.exists()) return;
        FileInputStream in = null;
        try {
            in = new FileInputStream(indexFile);
            ByteArrayOutputStream bos = new ByteArrayOutputStream();
            byte[] buf = new byte[8192];
            int n;
            while ((n = in.read(buf)) > 0) bos.write(buf, 0, n);
            JSONArray arr = new JSONArray(new String(bos.toByteArray(), "UTF-8"));
            for (int i = 0; i < arr.length(); i++) {
                JSONObject o = arr.getJSONObject(i);
                Entry e = new Entry();
                e.url = o.optString("url");
                e.fileName = o.optString("file");
                e.etag = o.optString("etag", null);
                e.lastModified = o.optString("lm", null);
                e.hash = o.optString("hash", null);
                e.size = o.optLong("size");
                e.savedAt = o.optLong("ts");
                // 旧版索引没有 ck 字段，记为 0：下次同步会正常核对一遍，不会误跳过
                e.checkedAt = o.optLong("ck");
                if (e.url != null && e.fileName != null
                        && new File(dir, e.fileName).exists()) {
                    entries.put(e.url, e);
                }
            }
        } catch (Exception ignored) {
        } finally {
            if (in != null) try { in.close(); } catch (Exception ignored) {}
        }
    }

    private void saveIndex() {
        synchronized (indexLock) {
            FileOutputStream out = null;
            try {
                JSONArray arr = new JSONArray();
                for (Entry e : entries.values()) {
                    JSONObject o = new JSONObject();
                    o.put("url", e.url);
                    o.put("file", e.fileName);
                    o.put("etag", e.etag == null ? JSONObject.NULL : e.etag);
                    o.put("lm", e.lastModified == null ? JSONObject.NULL : e.lastModified);
                    o.put("hash", e.hash == null ? JSONObject.NULL : e.hash);
                    o.put("size", e.size);
                    o.put("ts", e.savedAt);
                    o.put("ck", e.checkedAt);
                    arr.put(o);
                }
                out = new FileOutputStream(indexFile);
                out.write(arr.toString().getBytes("UTF-8"));
                out.flush();
            } catch (Exception ignored) {
            } finally {
                if (out != null) try { out.close(); } catch (Exception ignored) {}
            }
        }
    }

    // ───────────────────────── 工具 ─────────────────────────

    public interface SyncCallback {
        void onFinished(SyncResult result, boolean ok, String message);
    }

    /**
     * 是否是图片 / 视频这类「内容不随页面改版而变」的媒体资源。
     *
     * 必须先剥掉 ?v=1.2.3 这类查询串再判扩展名，否则站点给图片加了版本参数后
     * 会被当成普通资源，每次同步都重新核对，「跳过已有」就失效了。
     */
    public static boolean isMedia(String url) {
        String ext = extOf(url);
        if (ext.startsWith(".")) ext = ext.substring(1);
        switch (ext) {
            case "jpg": case "jpeg": case "png": case "gif":
            case "webp": case "bmp": case "svg":
            case "mp4": case "webm": case "mp3":
                return true;
            default:
                return false;
        }
    }

    public static String mimeOf(String url) {
        String ext = extOf(url);
        if (ext.startsWith(".")) ext = ext.substring(1);
        String mime = MimeTypeMap.getSingleton().getMimeTypeFromExtension(
                ext.toLowerCase(Locale.ROOT));
        if (mime != null) return mime;
        if ("css".equals(ext)) return "text/css";
        if ("js".equals(ext)) return "application/javascript";
        if ("svg".equals(ext)) return "image/svg+xml";
        return "application/octet-stream";
    }

    private static String extOf(String url) {
        String path = url;
        int q = path.indexOf('?');
        if (q >= 0) path = path.substring(0, q);
        int slash = path.lastIndexOf('/');
        String name = slash >= 0 ? path.substring(slash + 1) : path;
        int dot = name.lastIndexOf('.');
        if (dot <= 0 || dot == name.length() - 1) return "";
        String ext = name.substring(dot).toLowerCase(Locale.ROOT);
        return ext.length() > 6 ? "" : ext;
    }

    private static String sha1(String s) {
        try {
            return sha1Bytes(s.getBytes("UTF-8"));
        } catch (Exception e) {
            return String.valueOf(s.hashCode());
        }
    }

    private static String sha1Bytes(byte[] data) {
        try {
            MessageDigest md = MessageDigest.getInstance("SHA-1");
            byte[] d = md.digest(data);
            StringBuilder sb = new StringBuilder();
            for (byte b : d) sb.append(String.format(Locale.ROOT, "%02x", b));
            return sb.toString();
        } catch (Exception e) {
            return String.valueOf(data.length);
        }
    }

    private static byte[] readAll(InputStream in, int max) throws Exception {
        if (in == null) return null;
        ByteArrayOutputStream bos = new ByteArrayOutputStream();
        byte[] buf = new byte[16384];
        int n;
        int total = 0;
        while ((n = in.read(buf)) > 0) {
            total += n;
            if (total > max) {
                in.close();
                return null;
            }
            bos.write(buf, 0, n);
        }
        in.close();
        return bos.toByteArray();
    }
}
