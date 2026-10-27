package com.sifreelee.intro;

import android.content.ContentValues;
import android.content.Context;
import android.media.MediaScannerConnection;
import android.net.Uri;
import android.os.Build;
import android.os.Environment;
import android.provider.MediaStore;
import android.text.TextUtils;

import java.io.File;
import java.io.FileOutputStream;
import java.io.OutputStream;

/**
 * 把图片写入系统相册。
 *
 * Android 10 起走 MediaStore 的分区存储，无需任何权限；
 * Android 7~9 仍需写外部存储权限，落到公共 Pictures 目录后主动触发媒体扫描。
 */
public class MediaSaver {

    private static final String ALBUM = "洛晴跃飞";

    public static class Result {
        public boolean ok;
        public String message;

        Result(boolean ok, String message) {
            this.ok = ok;
            this.message = message;
        }
    }

    /** 是否还需要申请存储权限（仅 Android 9 及以下） */
    public static boolean needsLegacyPermission() {
        return Build.VERSION.SDK_INT < Build.VERSION_CODES.Q;
    }

    public static String sanitizeName(String raw) {
        if (TextUtils.isEmpty(raw)) return "image";
        String s = raw.trim();
        // 去掉扩展名，统一由调用方补
        int dot = s.lastIndexOf('.');
        if (dot > 0 && dot > s.length() - 8) s = s.substring(0, dot);
        // 去掉文件系统与 URL 不友好字符
        s = s.replaceAll("[\\\\/:*?\"<>|\\s]+", "_");
        if (s.length() > 60) s = s.substring(0, 60);
        if (s.isEmpty()) s = "image";
        return s;
    }

    public static Result save(Context ctx, byte[] data, String baseName, String mime) {
        String name = sanitizeName(baseName);
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
            return saveModern(ctx, data, name, mime);
        }
        return saveLegacy(ctx, data, name, mime);
    }

    private static Result saveModern(Context ctx, byte[] data, String name, String mime) {
        Uri uri = null;
        try {
            ContentValues v = new ContentValues();
            v.put(MediaStore.Images.Media.DISPLAY_NAME, name + ".jpg");
            v.put(MediaStore.Images.Media.MIME_TYPE,
                    TextUtils.isEmpty(mime) ? "image/jpeg" : mime);
            v.put(MediaStore.Images.Media.RELATIVE_PATH,
                    Environment.DIRECTORY_PICTURES + File.separator + ALBUM);
            v.put(MediaStore.Images.Media.IS_PENDING, 1);

            uri = ctx.getContentResolver()
                    .insert(MediaStore.Images.Media.EXTERNAL_CONTENT_URI, v);
            if (uri == null) return new Result(false, "系统拒绝创建图片记录");

            OutputStream os = ctx.getContentResolver().openOutputStream(uri);
            if (os == null) return new Result(false, "无法写入相册");
            try {
                os.write(data);
                os.flush();
            } finally {
                os.close();
            }

            ContentValues done = new ContentValues();
            done.put(MediaStore.Images.Media.IS_PENDING, 0);
            ctx.getContentResolver().update(uri, done, null, null);

            return new Result(true, "已保存到相册 Pictures/" + ALBUM);
        } catch (Exception e) {
            if (uri != null) {
                try {
                    ctx.getContentResolver().delete(uri, null, null);
                } catch (Exception ignored) {
                }
            }
            return new Result(false, "保存失败：" + e.getMessage());
        }
    }

    @SuppressWarnings("deprecation")
    private static Result saveLegacy(Context ctx, byte[] data, String name, String mime) {
        FileOutputStream fos = null;
        try {
            File base = Environment.getExternalStoragePublicDirectory(
                    Environment.DIRECTORY_PICTURES);
            File dir = new File(base, ALBUM);
            if (!dir.exists() && !dir.mkdirs()) {
                return new Result(false, "无法创建目录 Pictures/" + ALBUM);
            }
            File out = uniqueFile(dir, name, ".jpg");
            fos = new FileOutputStream(out);
            fos.write(data);
            fos.flush();
            fos.close();
            fos = null;

            MediaScannerConnection.scanFile(ctx,
                    new String[]{out.getAbsolutePath()},
                    new String[]{TextUtils.isEmpty(mime) ? "image/jpeg" : mime},
                    null);

            return new Result(true, "已保存到相册 Pictures/" + ALBUM);
        } catch (Exception e) {
            return new Result(false, "保存失败：" + e.getMessage());
        } finally {
            if (fos != null) try { fos.close(); } catch (Exception ignored) {}
        }
    }

    /** 同名文件自动加序号，避免覆盖 */
    private static File uniqueFile(File dir, String name, String ext) {
        File f = new File(dir, name + ext);
        int i = 2;
        while (f.exists() && i < 1000) {
            f = new File(dir, name + "_" + i + ext);
            i++;
        }
        return f;
    }
}
