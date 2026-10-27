# 项目长期约定

## 站点结构
- 个人静态站「洛晴跃飞」，新中式风格，GitHub Pages 托管：`https://sifreelee.github.io/self_introduction/`
- 目录：`assets/images` 相册照片、`js/data.js` 内容数据 + `js/main.js` 渲染、`css/style.css`
- 改 CSS/JS 后需改 `index.html` 里 `?v=` 版本号才能绕过浏览器缓存
- 页脚「最近更新」由 `js/last-updated.js` 取 GitHub 仓库最后一次提交时间，
  三级兜底（接口 → localStorage `lx-last-update` → HTML 写死日期）；
  改版时记得同步改 `#footer-updated-date` 里的静态占位日期
- 导航栏菜单文字的基准样式是 `.nav-links a`（楷体 17px / `.3em` 字距 /
  `::after` 朱砂下划线展开到 55%），App 注入的「设置」入口按这套参数对齐

## 安卓 App（android-app/）
- 定位：**WebView 外壳**，直接加载线上站点，网站更新自动同步，不打包静态快照
- 包名 `com.sifreelee.intro`，JDK 17 + AGP 8.7.3 + Gradle 8.9 + Android SDK 34
- 构建：双击 `android-app/build-apk.bat`，产物在 `android-app/dist/`
- 签名证书 `android-app/keystore/luqing-release.jks`（alias `luqing` / 密码 `luqing2026`）——**绝不可提交到仓库**，丢失后无法覆盖升级
- 换站点地址需同时改 `MainActivity.java` 的 `HOME_URL` 与 `SITE_HOST`
- 离线缓存：`WebCache.java`（应用私有目录 `files/webcache` + `index.json`），
  `shouldInterceptRequest` 做缓存优先，后台用条件请求 + SHA-1 兜底做增量
- 长按交互走 JS 桥 `AndroidBridge`（`onImage` / `onBlank` / `onAssets`），
  正文长按必须放行给系统选字，**绝不能调 `setLongClickable(false)`**

## 构建环境坑
- `maven.google.com` 在本机不可用（502），依赖统一走 `maven.aliyun.com/repository/google`
- `services.gradle.org` 不可达，Gradle 发行包走 `mirrors.cloud.tencent.com/gradle/`
- curl 访问 https 一律加 `--ssl-no-revoke`
