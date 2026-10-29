package com.sifreelee.intro;

import android.Manifest;
import android.annotation.SuppressLint;
import android.app.Activity;
import android.app.AlertDialog;
import android.content.ActivityNotFoundException;
import android.content.ClipData;
import android.content.ClipboardManager;
import android.content.Context;
import android.content.DialogInterface;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.graphics.Color;
import android.net.Uri;
import android.os.Build;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.view.KeyEvent;
import android.view.View;
import android.view.ViewGroup;
import android.view.ViewGroup.LayoutParams;
import android.webkit.JavascriptInterface;
import android.webkit.WebResourceError;
import android.webkit.WebResourceRequest;
import android.webkit.WebResourceResponse;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.widget.Button;
import android.widget.CheckBox;
import android.widget.FrameLayout;
import android.widget.LinearLayout;
import android.widget.ProgressBar;
import android.widget.RadioButton;
import android.widget.RadioGroup;
import android.widget.ScrollView;
import android.widget.SeekBar;
import android.widget.TextView;
import android.widget.Toast;

import org.json.JSONArray;

import java.io.ByteArrayOutputStream;
import java.io.File;
import java.io.FileInputStream;
import java.io.InputStream;
import java.net.HttpURLConnection;
import java.net.URL;
import java.util.ArrayList;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Set;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

import androidx.swiperefreshlayout.widget.SwipeRefreshLayout;

/**
 * 洛晴跃飞 —— 原生 WebView 壳。
 *
 * 设计要点：
 * 1. 直接加载线上站点，网站内容一更新，App 立即可见，无需重新打包发版。
 * 2. 支持下拉刷新、系统返回键回退网页历史。
 * 3. 首屏加载失败（断网）时展示本地离线页，可一键重试。
 * 4. 站外链接交给系统浏览器，App 内不承载第三方页面。
 * 5. 可选离线缓存：首次启动询问，之后增量同步；有缓存时优先走本地。
 * 6. 长按图片可保存到相册，长按页尾可管理缓存。
 */
public class MainActivity extends Activity {

    /** 线上站点入口 */
    private static final String HOME_URL = "https://sifreelee.github.io/self_introduction/";
    /** 站点所属主机，用于判断是否为站内链接 */
    private static final String SITE_HOST = "sifreelee.github.io";
    /** 本地离线提示页 */
    private static final String OFFLINE_URL = "file:///android_asset/offline.html";

    /**
     * 是否启用「导航栏下滑收起、上滑唤出」。
     *
     * 站点本身的 .navbar 是 position:fixed，滚动时只切换 .scrolled 背景，
     * 从不隐藏，因此在手机上会常驻 68px 顶栏。这段注入脚本只在 App 内追加行为，
     * 不改动网站源码，关掉本开关即可恢复原样。
     */
    private static final boolean ENABLE_NAV_AUTOHIDE = true;

    /**
     * 注入脚本要点：
     * 1. 只在纵向位移超过阈值时判断，避免轻微抖动误触发；
     * 2. 页面顶部附近不收起，避免刚进页面就消失；
     * 3. 展开的汉堡菜单不做收起，否则菜单会跟着顶栏一起被推走；
     * 4. 点击导航锚点后短暂抑制，避免平滑滚动过程中顶栏闪烁。
     */
    private static final String NAV_AUTOHIDE_JS =
            "(function(){"
            + "if(window.__navAutoHide)return;window.__navAutoHide=1;"
            + "var nav=document.getElementById('navbar');if(!nav)return;"
            + "var st=document.createElement('style');"
            + "st.textContent='.navbar{transition:background .45s,box-shadow .45s,"
            + "border-color .45s,transform .28s ease!important}"
            + ".navbar.nav-autohide{transform:translateY(-105%)!important;"
            + "box-shadow:none!important}';"
            + "document.head.appendChild(st);"
            + "var lastY=window.scrollY||0,hold=0,TH=8;"
            + "document.addEventListener('click',function(e){"
            + "var a=e.target&&e.target.closest?e.target.closest('.nav-links a'):null;"
            + "if(a)hold=Date.now()+900;},true);"
            + "function menuOpen(){"
            + "var l=document.getElementById('nav-links');"
            + "var t=document.getElementById('nav-toggle');"
            + "return (l&&l.classList.contains('show'))||(t&&t.classList.contains('open'));}"
            + "window.addEventListener('scroll',function(){"
            + "var y=window.scrollY||window.pageYOffset||0;var dy=y-lastY;"
            + "if(Math.abs(dy)<TH)return;lastY=y;"
            + "if(Date.now()<hold||menuOpen())return;"
            + "var h=nav.offsetHeight||68;"
            + "if(dy>0&&y>h*1.2){nav.classList.add('nav-autohide');}"
            + "else if(dy<0){nav.classList.remove('nav-autohide');}"
            + "},{passive:true});"
            + "})();";

    /**
     * 页面交互注入脚本：长按图片 → 保存；长按空白 → 缓存管理。
     *
     * 刻意不接管文字区域的长按，WebView 自带的选择 + 复制菜单要保留，
     * 一旦在这里 preventDefault 或 prevent 冒泡，文本就无法选中了。
     */
    private static final String INTERACT_JS =
            "(function(){"
            + "if(window.__lxInteract)return;window.__lxInteract=1;"
            + "var LP=520,timer=null,sx=0,sy=0,moved=false;"
            + "function clear(){if(timer){clearTimeout(timer);timer=null;}}"
            + "function abs(u){try{return new URL(u,location.href).href;}catch(e){return u;}}"
            + "function handle(el){"
            + "if(!el||!el.tagName)return;"
            + "var img=el.tagName==='IMG'?el:(el.closest?el.closest('img'):null);"
            + "if(img){"
            + "var src=img.currentSrc||img.src;"
            + "if(src){window.AndroidBridge.onImage(abs(src),img.alt||'',img.title||'');}"
            + "return;}"
            + "if(el.closest&&el.closest('p,h1,h2,h3,h4,h5,li,blockquote,td,pre,code,"
            + ".album-browser-note-inner,.about-text'))return;"
            + "if(el.closest&&el.closest('a,button,input,textarea,select,.nav-links'))return;"
            + "window.AndroidBridge.onBlank();}"
            + "document.addEventListener('touchstart',function(e){"
            + "if(e.touches.length!==1){clear();return;}"
            + "var t=e.touches[0];sx=t.clientX;sy=t.clientY;moved=false;"
            + "var el=e.target;clear();"
            + "timer=setTimeout(function(){timer=null;if(!moved)handle(el);},LP);"
            + "},{passive:true});"
            + "document.addEventListener('touchmove',function(e){"
            + "if(!timer)return;var t=e.touches[0];"
            + "if(Math.abs(t.clientX-sx)>10||Math.abs(t.clientY-sy)>10){moved=true;clear();}"
            + "},{passive:true});"
            + "document.addEventListener('touchend',clear,{passive:true});"
            + "document.addEventListener('touchcancel',clear,{passive:true});"
            + "})();";

    /**
     * 资源枚举脚本：把 SITE_DATA 里所有图片/视频路径 + 页面实际引用的
     * css/js/图标汇总成绝对地址列表，交给原生层做离线缓存。
     *
     * 不硬编码数据结构，递归遍历对象，因此以后 data.js 增删字段也不用改这里。
     */
    private static final String COLLECT_JS =
            "(function(){"
            + "var set={};"
            + "function abs(u){try{return new URL(u,location.href).href;}catch(e){return null;}}"
            + "function add(u){if(typeof u!=='string'||!u)return;"
            + "if(!/\\.(jpg|jpeg|png|gif|webp|bmp|svg|mp4|webm|mp3|css|js)(\\?|$)/i.test(u))return;"
            + "var a=abs(u);if(a)set[a]=1;}"
            + "function walk(v,d){"
            + "if(d>10||v==null)return;"
            + "if(typeof v==='string'){add(v);return;}"
            + "if(Object.prototype.toString.call(v)==='[object Array]'){"
            + "for(var i=0;i<v.length;i++)walk(v[i],d+1);return;}"
            + "if(typeof v==='object'){for(var k in v){if(Object.prototype.hasOwnProperty.call(v,k))walk(v[k],d+1);}}}"
            + "try{walk(SITE_DATA,0);}catch(e){}"
            + "var i,n;"
            + "n=document.querySelectorAll('img[src]');for(i=0;i<n.length;i++)add(n[i].getAttribute('src'));"
            + "n=document.querySelectorAll('video[src],source[src]');for(i=0;i<n.length;i++)add(n[i].getAttribute('src'));"
            + "n=document.querySelectorAll('link[rel=\"stylesheet\"]');for(i=0;i<n.length;i++)add(n[i].getAttribute('href'));"
            + "n=document.querySelectorAll('link[rel=\"icon\"]');for(i=0;i<n.length;i++)add(n[i].getAttribute('href'));"
            + "n=document.querySelectorAll('script[src]');for(i=0;i<n.length;i++)add(n[i].getAttribute('src'));"
            + "set[location.href.split('#')[0]]=1;"
            + "var out=[];for(var k in set){out.push(k);}"
            + "try{window.AndroidBridge.onAssets(JSON.stringify(out));}catch(e){}"
            + "})();";

    /**
     * 「仅打开时缓存」专用：只收页面 DOM 里真实出现过的资源。
     *
     * 不能用上面的 COLLECT_JS —— 它会遍历 data.js，把全站 695 张照片
     * 一次性全捞出来，于是「仅打开」变成「全量预下载」，和这个选项的
     * 含义正好相反，还会让用户以为缓存不听话、一开就狂下载。
     *
     * 只用 DOM：相册封面、页面里真正渲染出的图片、样式与脚本。
     * 点进某个相册后，那里的大图进了 DOM，才会被收进来。
     */
    private static final String COLLECT_DOM_JS =
            "(function(){"
            + "var set={};"
            + "function abs(u){try{return new URL(u,location.href).href;}catch(e){return null;}}"
            + "function add(u){if(typeof u!=='string'||!u)return;"
            + "if(!/\\.(jpg|jpeg|png|gif|webp|bmp|svg|mp4|webm|mp3|css|js)(\\?|$)/i.test(u))return;"
            + "var a=abs(u);if(a)set[a]=1;}"
            + "var i,n;"
            + "n=document.querySelectorAll('img[src]');for(i=0;i<n.length;i++)add(n[i].getAttribute('src'));"
            + "n=document.querySelectorAll('video[src],source[src]');for(i=0;i<n.length;i++)add(n[i].getAttribute('src'));"
            + "n=document.querySelectorAll('link[rel=\"stylesheet\"]');for(i=0;i<n.length;i++)add(n[i].getAttribute('href'));"
            + "n=document.querySelectorAll('link[rel=\"icon\"]');for(i=0;i<n.length;i++)add(n[i].getAttribute('href'));"
            + "n=document.querySelectorAll('script[src]');for(i=0;i<n.length;i++)add(n[i].getAttribute('src'));"
            + "set[location.href.split('#')[0]]=1;"
            + "var out=[];for(var k in set){out.push(k);}"
            + "try{window.AndroidBridge.onAssets(JSON.stringify(out));}catch(e){}"
            + "})();";

    /**
     * 在导航栏里、三条杠左侧插入「设置」入口。
     *
     * 站点结构是 .nav-inner(flex, space-between) 包着 .nav-logo / #nav-toggle / #nav-links。
     * 把入口插到 #nav-toggle 之前并给 margin-left:auto，视觉上就是
     * 「大标题 …… 设置 三条杠」，贴着三条杠，不进下拉菜单。
     * 万一站点改版拿不到 #nav-toggle，退化为追加到 .nav-inner 末尾；
     * 再不行还有长按空白页兜底。
     *
     * 外观与 .nav-links a 完全一致（楷体 / 17px / .3em 字距 / 朱砂下划线），
     * 不额外加边框和底色，看起来就是菜单位里的一项，只是位置挪到了导航栏上。
     */
    private static final String SETTINGS_BTN_JS =
            "(function(){"
            // 同一个页面重复注入直接返回；换页后由 window 级重试循环重新装
            + "if(document.getElementById('lx-settings-btn'))return;"
            + "function ensure(){"
            + "if(document.getElementById('lx-settings-btn'))return;"
            + "var inner=document.querySelector('.nav-inner');"
            + "if(!inner)return;"
            + "var st=document.getElementById('lx-settings-style');"
            + "if(!st){st=document.createElement('style');st.id='lx-settings-style';"
            // 与 css/style.css 里 .nav-links a 同一套排版参数
            + "st.textContent='#lx-settings-btn{"
            + "margin-left:auto;margin-right:0;"
            + "position:relative;display:block;box-sizing:border-box;"
            + "padding:8px 16px;border:0;background:none;outline:none;"
            + "font-family:var(--font-kai);font-size:17px;line-height:1.35;"
            + "letter-spacing:.3em;white-space:nowrap;"
            + "color:var(--ink-2);cursor:pointer;"
            + "-webkit-tap-highlight-color:transparent;"
            + "-webkit-appearance:none;appearance:none;"
            + "transition:color .3s}"
            // 同款下划线：居中、2px、朱砂、点击/选中时展开到 55%
            + "#lx-settings-btn::after{content:\"\";position:absolute;left:50%;bottom:2px;"
            + "width:0;height:2px;background:var(--cinnabar);"
            + "transform:translateX(-50%);transition:width .35s}"
            + "#lx-settings-btn:hover,#lx-settings-btn:active,"
            + "#lx-settings-btn.lx-active{color:var(--cinnabar)}"
            + "#lx-settings-btn:hover::after,#lx-settings-btn:active::after,"
            + "#lx-settings-btn.lx-active::after{width:55%}';"
            + "document.head.appendChild(st);}"
            + "var b=document.createElement('button');"
            + "b.id='lx-settings-btn';b.type='button';b.textContent='设置';"
            + "b.setAttribute('aria-label','设置');"
            + "b.addEventListener('click',function(e){"
            + "e.preventDefault();e.stopPropagation();"
            + "b.classList.add('lx-active');"
            + "var t=document.getElementById('nav-toggle');if(t)t.classList.remove('open');"
            + "var ul=document.getElementById('nav-links');if(ul)ul.classList.remove('show');"
            + "try{window.AndroidBridge.onSettings();}catch(err){}"
            + "});"
            + "var toggle=document.getElementById('nav-toggle');"
            + "if(toggle&&toggle.parentNode===inner){inner.insertBefore(b,toggle);}"
            + "else{inner.appendChild(b);}"
            + "}"
            // 立即试一次；导航栏还没渲染出来就每 100ms 再试，最多 12 秒。
            // 这样页面刚打开、标题栏一出现，「设置」就已经在上面了，
            // 不用等几十张相册封面加载完（onPageFinished 可能晚好几秒）。
            + "var n=0;"
            + "function tick(){ensure();"
            + "if(document.getElementById('lx-settings-btn'))return;"
            + "if(++n<120)setTimeout(tick,100);}"
            + "tick();"
            + "document.addEventListener('DOMContentLoaded',ensure);"
            + "window.addEventListener('load',ensure);"
            + "if(window.__lxBtnTick)clearInterval(window.__lxBtnTick);"
            + "var m=0;"
            + "window.__lxBtnTick=setInterval(function(){"
            + "if(document.getElementById('lx-settings-btn')){"
            + "clearInterval(window.__lxBtnTick);window.__lxBtnTick=0;return;}"
            // 兜底轮询最多 15 秒，站点若结构性改动导致找不到导航栏就自然停下
            + "if(++m>38){clearInterval(window.__lxBtnTick);window.__lxBtnTick=0;return;}"
            + "ensure();},400);"
            + "})();";

    /** 设置面板关掉后收回导航栏上的下划线选中态 */
    private static final String SETTINGS_BTN_IDLE_JS =
            "(function(){var b=document.getElementById('lx-settings-btn');"
            + "if(b)b.classList.remove('lx-active');})();";

    private WebSwipeRefreshLayout refreshLayout;
    private FrameLayout root;
    private ProgressBar progressBar;
    private WebView webView;

    private WebCache cache;
    private final Handler ui = new Handler(Looper.getMainLooper());
    private final ExecutorService io = Executors.newFixedThreadPool(2);

    /** 用户已授权保存但尚未落盘的图片地址（等运行时权限回调） */
    private String pendingSaveUrl;
    private String pendingSaveName;
    private String userAgent;

    /** 下次收集到资源清单时强制执行同步（菜单/下拉刷新触发），忽略节流 */
    private boolean pendingForceSync;
    /** 下次同步是否连本地已有的资源也跟服务器核对一遍（手动「立即同步」） */
    private boolean pendingDeepSync;
    /** 本次会话是否已为「新内容」自动刷新过一次，避免来回 reload */
    private boolean autoReloaded;
    /** 本轮导航是否已注入过导航栏「设置」入口 */
    private boolean btnInjected;
    /** 是否已用本地缓存主文档兜底过，防止断网时反复触发 */
    private boolean fallbackLoaded;

    /** 普通打开时的同步节流窗口：6 小时内不重复做全量条件请求 */
    private static final long SYNC_MIN_INTERVAL_MS = 6 * 60 * 60 * 1000L;

    private static final int REQ_SAVE_IMAGE = 1001;

    @SuppressLint("SetJavaScriptEnabled")
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        applyEdgeToEdge();

        root = new FrameLayout(this);

        webView = new WebView(this);
        webView.setBackgroundColor(Color.WHITE);

        /*
         * 关键：WebView 必须是 SwipeRefreshLayout 的【直接】子 View。
         * 若中间再套一层 ViewGroup，SwipeRefreshLayout 的 canChildScrollUp()
         * 会去问那层容器能否上滑，容器恒返回 false，于是外壳永远以为"已在顶部"，
         * 每次手指下拉（想往回滚）都被下拉刷新拦截 —— 表现为页面只能单向下滑。
         */
        refreshLayout = new WebSwipeRefreshLayout(this);
        refreshLayout.bindWebView(webView);
        refreshLayout.setColorSchemeColors(0xFFB03A2E);
        refreshLayout.addView(webView, new ViewGroup.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT,
                ViewGroup.LayoutParams.MATCH_PARENT));
        root.addView(refreshLayout, new FrameLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT,
                ViewGroup.LayoutParams.MATCH_PARENT));

        // 顶部细进度条浮在外层，不能塞进 SwipeRefreshLayout（它只允许一个子 View）
        progressBar = new ProgressBar(this, null, android.R.attr.progressBarStyleHorizontal);
        progressBar.setLayoutParams(new FrameLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT, dp(3)));
        progressBar.setMax(100);
        progressBar.setVisibility(View.GONE);
        root.addView(progressBar);

        refreshLayout.setOnRefreshListener(() -> {
            if (webView == null) return;
            // 主文档本来就走网络；这里再强制后台同步一次（忽略节流），
            // 本地已有的图片不会重复下载
            pendingForceSync = true;
            webView.reload();
        });

        setContentView(root);

        cache = WebCache.get(this);
        configureWebView();

        // 首次安装才弹「离线浏览」询问；设置面板不再自动弹出，
        // 由导航栏上的「设置」按钮点击打开（长按页面空白处同一入口）。
        askCacheIfFirstRun();

        if (savedInstanceState != null) {
            webView.restoreState(savedInstanceState);
        } else {
            webView.loadUrl(HOME_URL);
        }
    }

    /** 内容延伸到状态栏下方，页面白底更自然；同时把 WebView 下推避免被状态栏遮挡 */
    private void applyEdgeToEdge() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.LOLLIPOP) {
            getWindow().setStatusBarColor(0xFFF4F1EA);
            getWindow().setNavigationBarColor(0xFFFFFFFF);
        }
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
            getWindow().getDecorView().setSystemUiVisibility(
                    View.SYSTEM_UI_FLAG_LIGHT_STATUS_BAR);
        }
    }

    private void configureWebView() {
        WebSettings s = webView.getSettings();
        s.setJavaScriptEnabled(true);
        s.setDomStorageEnabled(true);
        s.setDatabaseEnabled(true);
        s.setLoadWithOverviewMode(true);
        s.setUseWideViewPort(true);
        s.setSupportZoom(false);
        s.setBuiltInZoomControls(false);
        s.setDisplayZoomControls(false);
        s.setCacheMode(WebSettings.LOAD_DEFAULT);
        s.setMixedContentMode(WebSettings.MIXED_CONTENT_NEVER_ALLOW);
        s.setMediaPlaybackRequiresUserGesture(true);
        s.setTextZoom(100);
        // 站点为移动优先的响应式布局，保持自身 viewport 缩放策略即可
        s.setBlockNetworkImage(false);
        // 按用户已保存的缓存策略调整 HTTP 缓存行为
        syncWebViewCacheMode();

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.LOLLIPOP) {
            s.setAllowFileAccess(false);
            s.setAllowContentAccess(false);
        }

        userAgent = s.getUserAgentString();

        // 注入 JS 桥：图片长按、空白长按、资源清单回传。
        // 注意：绝不能调 setLongClickable(false)，那会连带废掉 WebView 的
        // 长按选中文字能力，文本就无法复制了。
        webView.addJavascriptInterface(new Bridge(), "AndroidBridge");

        webView.setWebViewClient(new WebViewClient() {

            @Override
            public boolean shouldOverrideUrlLoading(WebView view, WebResourceRequest request) {
                Uri uri = request.getUrl();
                return handleUri(uri);
            }

            @Override
            @SuppressWarnings("deprecation")
            public boolean shouldOverrideUrlLoading(WebView view, String url) {
                return handleUri(Uri.parse(url));
            }

            @Override
            public void onPageStarted(WebView view, String url, android.graphics.Bitmap favicon) {
                progressBar.setVisibility(View.VISIBLE);
                // 新一轮导航：允许重新注入导航栏入口
                btnInjected = false;
            }

            @Override
            public void onPageCommitVisible(WebView view, String url) {
                // 页面一开始可见就插「设置」，不等图片全部加载完。
                // 站点首页有几十张相册封面，onPageFinished 往往要等好几秒，
                // 那几秒里标题栏是空的，看起来就好像没有设置入口。
                if (url != null && url.startsWith("http")) {
                    injectSettingsBtn(view);
                }
            }

            @Override
            public void onPageFinished(WebView view, String url) {
                progressBar.setVisibility(View.GONE);
                refreshLayout.setRefreshing(false);
                if (url == null || !url.startsWith("http")) return;
                if (ENABLE_NAV_AUTOHIDE) {
                    view.evaluateJavascript(NAV_AUTOHIDE_JS, null);
                }
                // 先装交互脚本（长按），再枚举资源并触发缓存同步
                view.evaluateJavascript(INTERACT_JS, null);
                injectSettingsBtn(view);
                collectAndSync(view);
                // 恢复用户上次设定的每行相册数
                applyDensity();
            }

            @Override
            public WebResourceResponse shouldInterceptRequest(WebView view,
                                                              WebResourceRequest request) {
                try {
                    if (cache == null || !cache.isEnabled()) return null;
                    if (!"GET".equalsIgnoreCase(request.getMethod())) return null;
                    Uri u = request.getUrl();
                    if (u == null || !"https".equals(u.getScheme())) return null;
                    String host = u.getHost();
                    if (host == null || !(host.equals(SITE_HOST)
                            || host.endsWith("." + SITE_HOST))) {
                        return null;
                    }
                    // 主文档永远走网络：这样站点一更新，下次打开就是最新版，
                    // 用户不需要任何额外操作。WebView 自身的 HTTP 缓存会处理
                    // 304，实际流量很小。断网时由 onReceivedError 回退本地副本。
                    if (request.isForMainFrame()) return null;
                    File f = cache.fileFor(u.toString());
                    if (f == null || !f.exists() || f.length() == 0) return null;

                    String mime = WebCache.mimeOf(u.toString());
                    String enc = null;
                    if (mime.startsWith("text/") || mime.contains("javascript")
                            || mime.contains("json") || mime.contains("xml")) {
                        enc = "UTF-8";
                    }
                    return new WebResourceResponse(mime, enc, new FileInputStream(f));
                } catch (Exception e) {
                    // 拦截失败就退化为正常网络请求，不能让页面白屏
                    return null;
                }
            }

            @Override
            public void onReceivedError(WebView view, WebResourceRequest request,
                                        WebResourceError error) {
                if (request.isForMainFrame()) {
                    // 主文档拉不到（断网 / 弱网）→ 用本地缓存副本顶上，
                    // 里面的图片样式仍由上面的拦截层从缓存提供
                    if (!loadCachedDocument()) showOfflinePage();
                }
            }

            @Override
            @SuppressWarnings("deprecation")
            public void onReceivedError(WebView view, int errorCode, String description,
                                        String failingUrl) {
                // API 23 以下无 isForMainFrame，仅在主文档失败时兜底
                if (failingUrl != null && failingUrl.equals(view.getUrl())) {
                    showOfflinePage();
                }
            }
        });

        webView.setWebChromeClient(new android.webkit.WebChromeClient() {
            @Override
            public void onProgressChanged(WebView view, int newProgress) {
                progressBar.setProgress(newProgress);
                if (newProgress >= 100) {
                    progressBar.setVisibility(View.GONE);
                } else {
                    progressBar.setVisibility(View.VISIBLE);
                }
            }
        });
    }

    /**
     * @return true 表示已由外部处理（不再由 WebView 加载）
     */
    private boolean handleUri(Uri uri) {
        if (uri == null) return false;
        String scheme = uri.getScheme() == null ? "" : uri.getScheme().toLowerCase();
        String host = uri.getHost() == null ? "" : uri.getHost().toLowerCase();

        if ("http".equals(scheme) || "https".equals(scheme)) {
            if (host.equals(SITE_HOST) || host.endsWith("." + SITE_HOST)) {
                return false; // 站内，交给 WebView
            }
            openExternally(uri);
            return true;
        }
        // 锚点、javascript: 等交给 WebView；其余自定义协议（tel/mailto/...）交给系统
        if ("file".equals(scheme) || "about".equals(scheme) || "javascript".equals(scheme)
                || "data".equals(scheme)) {
            return false;
        }
        openExternally(uri);
        return true;
    }

    private void openExternally(Uri uri) {
        try {
            startActivity(new Intent(Intent.ACTION_VIEW, uri));
        } catch (ActivityNotFoundException ignored) {
            // 没有可处理的 App，静默忽略
        }
    }

    private void showOfflinePage() {
        progressBar.setVisibility(View.GONE);
        refreshLayout.setRefreshing(false);
        webView.loadUrl(OFFLINE_URL);
    }

    /**
     * 断网兜底：把缓存里的主文档直接渲染出来。
     *
     * 用 loadDataWithBaseURL 把 base 设成线上地址，页面里的相对路径图片、
     * 样式仍然会走 shouldInterceptRequest 从本地缓存取，所以整页能正常显示。
     *
     * @return false 表示本地没有可用副本，调用方应显示离线页
     */
    private boolean loadCachedDocument() {
        if (cache == null || webView == null || fallbackLoaded) return false;
        File f = cache.fileFor(HOME_URL);
        if (f == null || !f.exists() || f.length() == 0) {
            // 缓存键可能记的是不带尾斜杠的形式，两个都试
            String alt = HOME_URL.endsWith("/")
                    ? HOME_URL.substring(0, HOME_URL.length() - 1)
                    : HOME_URL + "/";
            File f2 = cache.fileFor(alt);
            if (f2 != null && f2.exists() && f2.length() > 0) f = f2;
        }
        if (f == null || !f.exists() || f.length() == 0) return false;

        byte[] data = readFile(f);
        if (data == null || data.length == 0) return false;
        final String html;
        try {
            html = new String(data, "UTF-8");
        } catch (Exception e) {
            return false;
        }
        if (html.length() == 0) return false;

        fallbackLoaded = true;
        toast("网络不可用，正在显示上次缓存的页面");
        webView.loadDataWithBaseURL(HOME_URL, html, "text/html", "UTF-8", null);
        return true;
    }

    // ═════════════════ 离线缓存 ═════════════════

    /**
     * 首次打开才询问缓存方式，之后随时可以在「设置」里改。
     */
    private void askCacheIfFirstRun() {
        if (!cache.isFirstRun()) return;

        final boolean[] wifiOnly = {true};
        String[] items = {"仅 Wi-Fi 下缓存（推荐）"};
        new AlertDialog.Builder(this)
                .setTitle("离线浏览")
                .setMessage("站内共约 700 张照片，全量缓存可能占用 200 MB 以上空间；"
                        + "之后只下载有改动的部分。\n\n"
                        + "也可以只缓存看过的内容，或完全不缓存。此选项之后可在「设置」中修改。")
                .setMultiChoiceItems(items, new boolean[]{true},
                        new DialogInterface.OnMultiChoiceClickListener() {
                            @Override
                            public void onClick(DialogInterface d, int which, boolean checked) {
                                wifiOnly[0] = checked;
                            }
                        })
                .setPositiveButton("全部缓存", new DialogInterface.OnClickListener() {
                    @Override
                    public void onClick(DialogInterface d, int w) {
                        cache.setWifiOnly(wifiOnly[0]);
                        cache.setMode(WebCache.MODE_FULL);
                        syncWebViewCacheMode();
                        startSync("开始缓存全部内容…", false);
                    }
                })
                .setNeutralButton("仅打开时缓存", new DialogInterface.OnClickListener() {
                    @Override
                    public void onClick(DialogInterface d, int w) {
                        cache.setWifiOnly(wifiOnly[0]);
                        cache.setMode(WebCache.MODE_OPENED);
                        syncWebViewCacheMode();
                        toast("之后看过的页面会自动留存");
                    }
                })
                .setNegativeButton("不缓存", new DialogInterface.OnClickListener() {
                    @Override
                    public void onClick(DialogInterface d, int w) {
                        cache.setWifiOnly(wifiOnly[0]);
                        cache.setMode(WebCache.MODE_OFF);
                        syncWebViewCacheMode();
                    }
                })
                .setCancelable(false)
                .show();
    }

    /**
     * 往导航栏注入「设置」入口。
     *
     * 每次导航只调用一次（onProgressChanged 每 10% 触发一次，别反复 evaluate）。
     * 注入脚本自带重试，所以哪怕这一刻 .nav-inner 还没渲染出来也能补上。
     */
    private void injectSettingsBtn(WebView view) {
        if (view == null || btnInjected) return;
        btnInjected = true;
        view.evaluateJavascript(SETTINGS_BTN_JS, null);
    }

    /**
     * 按当前缓存模式选资源清单脚本：
     * 「全部缓存」用 COLLECT_JS（含 data.js 里的全部照片）；
     * 「仅打开」用 COLLECT_DOM_JS（只认页面里真出现过的）。
     */
    private void collectAndSync(WebView view) {
        if (view == null) return;
        boolean opened = cache != null && cache.getMode() == WebCache.MODE_OPENED;
        view.evaluateJavascript(opened ? COLLECT_DOM_JS : COLLECT_JS, null);
    }

    /**
     * 拉起一次同步：先从当前页面收集资源清单，再交给缓存层增量下载。
     *
     * @param deep true = 忽略保质期，把本地已有的也跟服务器核对一遍（手动「立即同步」）
     */
    private void startSync(final String startTip, final boolean deep) {
        if (webView == null) return;
        if (!cache.isEnabled()) {
            toast("缓存未开启");
            return;
        }
        if (startTip != null) toast(startTip);
        pendingForceSync = true;
        pendingDeepSync = deep;
        collectAndSync(webView);
    }

    /** 由 JS 回传的资源清单触发实际下载 */
    private void syncAssets(final List<String> urls) {
        if (urls == null || urls.isEmpty()) return;

        boolean force = pendingForceSync;
        boolean deep = pendingDeepSync;
        pendingForceSync = false;
        pendingDeepSync = false;

        // 断网时不做同步，否则会弹出一屏「失败 N 项」
        if (fallbackLoaded) return;
        if (!cache.isOnline()) return;

        final boolean openedMode = cache.getMode() == WebCache.MODE_OPENED;

        // 普通打开时节流：刚同步过就不重复打 700 个条件请求。
        // 「仅打开」模式必须每页都存，否则浏览过的内容留不下来。
        if (!force && !openedMode && cache.getLastSync() > 0
                && System.currentTimeMillis() - cache.getLastSync() < SYNC_MIN_INTERVAL_MS) {
            return;
        }

        final List<String> targets = cache.filterForMode(new ArrayList<>(urls));
        if (targets.isEmpty()) return;

        cache.sync(targets, userAgent, deep, new WebCache.SyncCallback() {
            @Override
            public void onFinished(WebCache.SyncResult result, boolean ok, String message) {
                final String text;
                if (!ok) {
                    text = message;
                } else if (result.changed() == 0) {
                    text = result.unchanged == 0
                            ? "本地已是最新，未重复下载"
                            : "内容已是最新（核对 " + result.unchanged + " 项）";
                } else {
                    text = "已更新：" + result.summary();
                }
                ui.post(new Runnable() {
                    @Override
                    public void run() {
                        // 只在「手动触发」或「确实拿到新内容」时提示；
                        // 自动同步没变化就完全静默，重开不被打断。
                        boolean notify = force || (!openedMode && ok && result.changed() > 0);
                        if (notify) toast(text);
                        // 页面 / 脚本有更新时刷新一次：
                        // 新的 data.js 生效后，COLLECT_JS 才能枚举出这次新增的照片，
                        // 所以刷新后必须再强制同步一轮去补那些新 URL。
                        if (ok && result.changed() > 0 && !autoReloaded && webView != null) {
                            autoReloaded = true;
                            pendingForceSync = true;
                            webView.reload();
                        }
                    }
                });
            }
        });
    }

    private void showCacheMenu() {
        // 旧版只有缓存开关的简易菜单，已被完整的设置面板取代；
        // 保留此方法仅为兼容早期调用点，实际统一走 showSettings()。
        showSettings();
    }

    // ═════════════════ 设置面板 ═════════════════

    private static final String PREF_APP = "app_pref";
    private static final String KEY_COLS = "photo_columns";

    /** 每行相册数；0 表示跟随站点自身响应式规则 */
    private int photoColumns() {
        return getSharedPreferences(PREF_APP, MODE_PRIVATE).getInt(KEY_COLS, 2);
    }

    private void setPhotoColumns(int n) {
        getSharedPreferences(PREF_APP, MODE_PRIVATE).edit().putInt(KEY_COLS, n).apply();
        applyDensity();
    }

    /**
     * 站点用的是固定列数（.photo-grid 手机端为 repeat(2,1fr)），
     * 单纯缩放不会改变每行相册数，所以直接覆盖列数；
     * 每个格子是 1fr，列数变了格子自然跟着缩放。
     * 同一份列数也作用于相册内部的大图网格，浏览时观感才一致。
     */
    private void applyDensity() {
        if (webView == null) return;
        int n = photoColumns();
        String js = "(function(n){"
                + "var id='lx-density';"
                + "var st=document.getElementById(id);"
                + "if(n<=0){if(st&&st.parentNode)st.parentNode.removeChild(st);return;}"
                + "if(!document.head)return;"
                + "if(!st){st=document.createElement('style');st.id=id;document.head.appendChild(st);}"
                + "st.textContent='.photo-grid,.album-browser-grid{grid-template-columns:repeat('+n+',1fr)!important}';"
                + "})(" + n + ");";
        webView.evaluateJavascript(js, null);
    }

    /** 按缓存策略调整 WebView 自身的 HTTP 缓存行为 */
    private void syncWebViewCacheMode() {
        if (webView == null || cache == null) return;
        WebSettings s = webView.getSettings();
        s.setCacheMode(cache.getMode() == WebCache.MODE_OFF
                ? WebSettings.LOAD_NO_CACHE
                : WebSettings.LOAD_DEFAULT);
    }

    private void showSettings() {
        final LinearLayout box = new LinearLayout(this);
        box.setOrientation(LinearLayout.VERTICAL);
        int p = dp(20);
        box.setPadding(p, dp(4), p, dp(4));

        // ── 缓存方式 ──
        box.addView(sectionTitle("缓存方式"));

        final RadioGroup group = new RadioGroup(this);
        final RadioButton rbFull = new RadioButton(this);
        rbFull.setText("全部缓存（页面 + 全部照片）");
        rbFull.setId(1001);
        final RadioButton rbOpened = new RadioButton(this);
        rbOpened.setText("仅打开时缓存（浏览过的才保留）");
        rbOpened.setId(1002);
        final RadioButton rbOff = new RadioButton(this);
        rbOff.setText("不缓存（每次重新加载）");
        rbOff.setId(1003);
        group.addView(rbFull);
        group.addView(rbOpened);
        group.addView(rbOff);

        int mode = cache.getMode();
        if (mode == WebCache.MODE_FULL) group.check(1001);
        else if (mode == WebCache.MODE_OFF) group.check(1003);
        else group.check(1002); // OPENED，以及旧版的 SHELL 一并视为仅打开

        box.addView(group);

        // ── 进度区（仅「全部缓存」下显示）──
        final LinearLayout progressBox = new LinearLayout(this);
        progressBox.setOrientation(LinearLayout.VERTICAL);
        progressBox.setPadding(dp(36), 0, 0, dp(8));

        final TextView tvProgress = new TextView(this);
        tvProgress.setTextSize(13);
        tvProgress.setTextColor(0xFF6B6459);
        progressBox.addView(tvProgress);

        final ProgressBar pb = new ProgressBar(this, null,
                android.R.attr.progressBarStyleHorizontal);
        pb.setMax(100);
        LinearLayout.LayoutParams pbLp = new LinearLayout.LayoutParams(
                LayoutParams.MATCH_PARENT, dp(4));
        pbLp.topMargin = dp(6);
        progressBox.addView(pb, pbLp);

        final Button btnSync = new Button(this);
        btnSync.setText("立即同步");
        btnSync.setAllCaps(false);
        LinearLayout.LayoutParams btnLp = new LinearLayout.LayoutParams(
                LayoutParams.WRAP_CONTENT, LayoutParams.WRAP_CONTENT);
        btnLp.topMargin = dp(6);
        progressBox.addView(btnSync, btnLp);

        box.addView(progressBox);

        // ── 仅 Wi-Fi ──
        final CheckBox cbWifi = new CheckBox(this);
        cbWifi.setText("仅在 Wi-Fi 下缓存");
        cbWifi.setChecked(cache.isWifiOnly());
        box.addView(cbWifi);

        box.addView(divider());
        box.addView(sectionTitle("显示密度"));

        final TextView tvCols = new TextView(this);
        tvCols.setTextSize(14);
        tvCols.setText(colsLabel(photoColumns()));
        box.addView(tvCols);

        final SeekBar sb = new SeekBar(this);
        sb.setMax(4);
        sb.setProgress(photoColumns());
        box.addView(sb);

        TextView tvColsHint = new TextView(this);
        tvColsHint.setTextSize(12);
        tvColsHint.setTextColor(0xFF948C7E);
        tvColsHint.setText("数值越大，每行看到的相册越多、单张越小；0 为跟随站点默认。");
        box.addView(tvColsHint);

        box.addView(divider());

        final TextView tvStats = new TextView(this);
        tvStats.setTextSize(13);
        tvStats.setTextColor(0xFF6B6459);
        box.addView(tvStats);

        final Button btnClear = new Button(this);
        btnClear.setText("清除已缓存内容");
        btnClear.setAllCaps(false);
        box.addView(btnClear);

        ScrollView scroll = new ScrollView(this);
        scroll.addView(box);

        final AlertDialog dialog = new AlertDialog.Builder(this)
                .setTitle("设置")
                .setView(scroll)
                .setPositiveButton("关闭", null)
                .create();

        final boolean[] alive = {true};

        final Runnable refreshUi = new Runnable() {
            @Override
            public void run() {
                if (!alive[0]) return;
                boolean full = group.getCheckedRadioButtonId() == 1001;
                progressBox.setVisibility(full ? View.VISIBLE : View.GONE);

                int total = cache.progressTotal();
                int done = cache.progressDone();
                if (cache.isSyncing()) {
                    if (total <= 0) {
                        // 本地全都齐了，正在逐个核对是否有更新
                        pb.setIndeterminate(true);
                        tvProgress.setText("正在检查更新…");
                    } else {
                        pb.setIndeterminate(false);
                        pb.setProgress(done * 100 / total);
                        tvProgress.setText("正在核对 " + done + " / " + total + " 项 · "
                                + humanSize(cache.progressBytes()));
                    }
                    btnSync.setEnabled(false);
                } else {
                    pb.setIndeterminate(false);
                    pb.setProgress(total > 0 && done >= total ? 100 : 0);
                    String last = cache.getLastSync() == 0 ? "尚未缓存"
                            : "上次同步：" + android.text.format.DateFormat.format(
                            "MM-dd HH:mm", cache.getLastSync());
                    tvProgress.setText(last + " · 已缓存 " + cache.count() + " 项");
                    btnSync.setEnabled(true);
                }
                tvStats.setText("缓存占用：" + humanSize(cache.totalBytes())
                        + " · " + cache.count() + " 项");
                ui.postDelayed(this, 600);
            }
        };

        group.setOnCheckedChangeListener(new RadioGroup.OnCheckedChangeListener() {
            @Override
            public void onCheckedChanged(RadioGroup g, int checkedId) {
                int m;
                if (checkedId == 1001) m = WebCache.MODE_FULL;
                else if (checkedId == 1003) m = WebCache.MODE_OFF;
                else m = WebCache.MODE_OPENED;
                cache.setMode(m);
                syncWebViewCacheMode();
                if (m == WebCache.MODE_FULL) {
                    startSync("开始缓存…", false);
                } else if (m == WebCache.MODE_OFF) {
                    toast("已关闭缓存，之后每次都会重新加载");
                }
                ui.removeCallbacks(refreshUi);
                ui.post(refreshUi);
            }
        });

        cbWifi.setOnCheckedChangeListener((btn, checked) -> cache.setWifiOnly(checked));

        sb.setOnSeekBarChangeListener(new SeekBar.OnSeekBarChangeListener() {
            @Override
            public void onProgressChanged(SeekBar seekBar, int value, boolean fromUser) {
                tvCols.setText(colsLabel(value));
            }

            @Override
            public void onStartTrackingTouch(SeekBar seekBar) {
            }

            @Override
            public void onStopTrackingTouch(SeekBar seekBar) {
                setPhotoColumns(seekBar.getProgress());
            }
        });

        btnSync.setOnClickListener(v -> startSync("立即同步…", true));

        btnClear.setOnClickListener(v -> {
            new AlertDialog.Builder(this)
                    .setTitle("清除缓存")
                    .setMessage("将删除已缓存的页面与照片。清除后断网将无法浏览。")
                    .setPositiveButton("清除", (d, w) -> {
                        cache.clear();
                        toast("缓存已清除");
                        ui.removeCallbacks(refreshUi);
                        ui.post(refreshUi);
                    })
                    .setNegativeButton("取消", null)
                    .show();
        });

        dialog.setOnDismissListener(d -> {
            alive[0] = false;
            ui.removeCallbacks(refreshUi);
            // 面板关闭后收回导航栏「设置」的下划线选中态
            if (webView != null) webView.evaluateJavascript(SETTINGS_BTN_IDLE_JS, null);
        });
        dialog.show();
        ui.post(refreshUi);
    }

    private String colsLabel(int n) {
        if (n <= 0) return "每行相册：跟随站点默认";
        return "每行相册：" + n + " 个";
    }

    private TextView sectionTitle(String text) {
        TextView tv = new TextView(this);
        tv.setText(text);
        tv.setTextSize(13);
        tv.setTextColor(0xFFB03A2E);
        tv.setPadding(0, dp(14), 0, dp(6));
        return tv;
    }

    private View divider() {
        View v = new View(this);
        v.setBackgroundColor(0x1A000000);
        LinearLayout.LayoutParams lp = new LinearLayout.LayoutParams(
                LayoutParams.MATCH_PARENT, 1);
        lp.topMargin = dp(16);
        lp.bottomMargin = dp(4);
        v.setLayoutParams(lp);
        return v;
    }

    // ═════════════════ 图片与文字 ═════════════════

    /** 长按图片后的操作菜单 */
    private void onImageLongPress(final String url, String alt, String title) {
        String label = title != null && !title.isEmpty() ? title
                : (alt != null && !alt.isEmpty() ? alt : "图片");
        final String fileName = MediaSaver.sanitizeName(label);

        String[] items = {"保存图片到相册", "复制图片链接"};
        new AlertDialog.Builder(this)
                .setTitle(label.length() > 24 ? label.substring(0, 24) + "…" : label)
                .setItems(items, new DialogInterface.OnClickListener() {
                    @Override
                    public void onClick(DialogInterface d, int which) {
                        if (which == 0) {
                            requestSaveImage(url, fileName);
                        } else {
                            copyToClipboard(url);
                            toast("图片链接已复制");
                        }
                    }
                })
                .setNegativeButton("取消", null)
                .show();
    }

    private void requestSaveImage(String url, String name) {
        if (MediaSaver.needsLegacyPermission()
                && checkSelfPermission(Manifest.permission.WRITE_EXTERNAL_STORAGE)
                != PackageManager.PERMISSION_GRANTED) {
            pendingSaveUrl = url;
            pendingSaveName = name;
            requestPermissions(
                    new String[]{Manifest.permission.WRITE_EXTERNAL_STORAGE},
                    REQ_SAVE_IMAGE);
            return;
        }
        doSaveImage(url, name);
    }

    @Override
    public void onRequestPermissionsResult(int requestCode, String[] permissions,
                                           int[] grantResults) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults);
        if (requestCode != REQ_SAVE_IMAGE) return;
        boolean granted = grantResults.length > 0
                && grantResults[0] == PackageManager.PERMISSION_GRANTED;
        if (granted && pendingSaveUrl != null) {
            doSaveImage(pendingSaveUrl, pendingSaveName);
        } else {
            toast("未获得存储权限，无法保存到相册");
        }
        pendingSaveUrl = null;
        pendingSaveName = null;
    }

    /** 优先用已缓存的文件，避免重复下载；没有缓存才走网络 */
    private void doSaveImage(final String url, final String name) {
        toast("正在保存…");
        io.execute(new Runnable() {
            @Override
            public void run() {
                byte[] data = null;
                String errTmp = null;
                try {
                    File cached = cache != null ? cache.fileFor(url) : null;
                    if (cached != null && cached.exists()) {
                        data = readFile(cached);
                    }
                    if (data == null) {
                        data = httpGet(url);
                    }
                    if (data == null) errTmp = "图片下载失败，请检查网络";
                } catch (Exception e) {
                    errTmp = "下载出错：" + e.getMessage();
                }
                final String err = errTmp;

                final MediaSaver.Result r;
                if (data == null) {
                    r = null;
                } else {
                    r = MediaSaver.save(MainActivity.this, data, name, "image/jpeg");
                }

                ui.post(new Runnable() {
                    @Override
                    public void run() {
                        if (r == null) {
                            toast(err == null ? "保存失败" : err);
                        } else {
                            toast(r.message);
                        }
                    }
                });
            }
        });
    }

    private void copyToClipboard(String text) {
        ClipboardManager cm = (ClipboardManager) getSystemService(Context.CLIPBOARD_SERVICE);
        if (cm == null) return;
        cm.setPrimaryClip(ClipData.newPlainText("image_url", text));
    }

    private static byte[] readFile(File f) {
        FileInputStream in = null;
        try {
            in = new FileInputStream(f);
            ByteArrayOutputStream bos = new ByteArrayOutputStream();
            byte[] buf = new byte[16384];
            int n;
            while ((n = in.read(buf)) > 0) bos.write(buf, 0, n);
            return bos.toByteArray();
        } catch (Exception e) {
            return null;
        } finally {
            if (in != null) try { in.close(); } catch (Exception ignored) {}
        }
    }

    private static byte[] httpGet(String url) {
        HttpURLConnection c = null;
        try {
            c = (HttpURLConnection) new URL(url).openConnection();
            c.setConnectTimeout(15000);
            c.setReadTimeout(40000);
            if (c.getResponseCode() != HttpURLConnection.HTTP_OK) return null;
            InputStream in = c.getInputStream();
            ByteArrayOutputStream bos = new ByteArrayOutputStream();
            byte[] buf = new byte[16384];
            int n;
            while ((n = in.read(buf)) > 0) bos.write(buf, 0, n);
            in.close();
            return bos.toByteArray();
        } catch (Exception e) {
            return null;
        } finally {
            if (c != null) c.disconnect();
        }
    }

    private void toast(String msg) {
        Toast.makeText(this, msg, Toast.LENGTH_SHORT).show();
    }

    private static String humanSize(long bytes) {
        if (bytes < 1024) return bytes + " B";
        if (bytes < 1024 * 1024) return String.format(java.util.Locale.ROOT,
                "%.0f KB", bytes / 1024.0);
        if (bytes < 1024L * 1024 * 1024) return String.format(java.util.Locale.ROOT,
                "%.1f MB", bytes / 1024.0 / 1024.0);
        return String.format(java.util.Locale.ROOT,
                "%.2f GB", bytes / 1024.0 / 1024.0 / 1024.0);
    }

    /** JS 桥。所有方法都在 WebView 的 JS 线程被调用，必须切回主线程 */
    private class Bridge {

        @JavascriptInterface
        public void onImage(final String url, final String alt, final String title) {
            ui.post(new Runnable() {
                @Override
                public void run() {
                    onImageLongPress(url, alt, title);
                }
            });
        }

        @JavascriptInterface
        public void onBlank() {
            ui.post(new Runnable() {
                @Override
                public void run() {
                    // 长按空白处 = 设置入口的兜底（菜单注入失败时仍可用）
                    showSettings();
                }
            });
        }

        @JavascriptInterface
        public void onSettings() {
            ui.post(new Runnable() {
                @Override
                public void run() {
                    showSettings();
                }
            });
        }

        @JavascriptInterface
        public void onAssets(final String json) {
            try {
                JSONArray arr = new JSONArray(json);
                final List<String> urls = new ArrayList<>();
                Set<String> seen = new LinkedHashSet<>();
                for (int i = 0; i < arr.length(); i++) {
                    String u = arr.optString(i, null);
                    if (u != null && seen.add(u)) urls.add(u);
                }
                ui.post(new Runnable() {
                    @Override
                    public void run() {
                        syncAssets(urls);
                    }
                });
            } catch (Exception ignored) {
            }
        }
    }

    @Override
    public boolean onKeyDown(int keyCode, KeyEvent event) {
        if (keyCode == KeyEvent.KEYCODE_BACK && webView != null) {
            String url = webView.getUrl();
            boolean onOffline = url != null && url.startsWith("file:///android_asset/");
            if (!onOffline && webView.canGoBack()) {
                webView.goBack();
                return true;
            }
            if (onOffline) {
                // 离线页返回时重新尝试线上地址
                webView.loadUrl(HOME_URL);
                return true;
            }
        }
        return super.onKeyDown(keyCode, event);
    }

    @Override
    protected void onSaveInstanceState(Bundle outState) {
        super.onSaveInstanceState(outState);
        if (webView != null) webView.saveState(outState);
    }

    @Override
    protected void onPause() {
        super.onPause();
        if (webView != null) webView.onPause();
    }

    @Override
    protected void onResume() {
        super.onResume();
        if (webView != null) webView.onResume();
        // 回到前台允许再试一次「联网取最新」，断网兜底过也能自愈
        fallbackLoaded = false;
    }

    @Override
    protected void onDestroy() {
        if (webView != null) {
            if (refreshLayout != null) refreshLayout.removeView(webView);
            webView.stopLoading();
            webView.setWebChromeClient(null);
            webView.setWebViewClient(null);
            webView.destroy();
            webView = null;
        }
        super.onDestroy();
    }

    private int dp(int value) {
        return Math.round(value * getResources().getDisplayMetrics().density);
    }

    /**
     * 把"是否还能往上滑"的判断直接指向 WebView 的真实滚动位置。
     *
     * 框架默认实现是 child.canScrollVertically(-1)，一旦子 View 不是 WebView
     * （例如被一层 FrameLayout 包住）就会恒为 false，导致下拉刷新吞掉所有回滚手势。
     * 这里显式绑定 WebView，避免以后调整布局时再次踩坑。
     */
    private static class WebSwipeRefreshLayout extends SwipeRefreshLayout {

        private WebView boundWebView;

        WebSwipeRefreshLayout(Context context) {
            super(context);
        }

        void bindWebView(WebView view) {
            this.boundWebView = view;
        }

        @Override
        public boolean canChildScrollUp() {
            if (boundWebView != null) {
                return boundWebView.canScrollVertically(-1);
            }
            return super.canChildScrollUp();
        }
    }
}
