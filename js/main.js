/* ═══════════════════════════════════════════════════════════
   渲染与交互引擎 · 无需修改本文件
   内容修改请前往 js/data.js
   ═══════════════════════════════════════════════════════════ */

/* ─────────── 内置图标集（描边风格） ─────────── */
const ICONS = {
  brush: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><path d="M20 3l-9.5 9.5"/><path d="M20 3c-2.5.5-5 2-6.5 3.5"/><path d="M10.5 12.5c-2 .5-4 2.5-4.5 5.5-2 .5-3.5 2-4 3 3.5.5 6.5-.5 8-2s2-3.5 1.5-5z" fill="currentColor" fill-opacity=".12"/><path d="M6 17.5L4 21"/></svg>`,
  camera: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><path d="M3 8h3l1.5-2.5h9L18 8h3v11H3z"/><circle cx="12" cy="13.5" r="3.6"/><circle cx="12" cy="13.5" r="1.2" fill="currentColor" stroke="none"/></svg>`,
  tea: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><path d="M5 11h12v4.5a5 5 0 0 1-5 5h-2a5 5 0 0 1-5-5z"/><path d="M17 12.5h1.5a2.5 2.5 0 0 1 0 5H17"/><path d="M8.5 8c-.8-1 .8-2 0-3M12 8c-.8-1 .8-2 0-3M15.5 8c-.8-1 .8-2 0-3"/></svg>`,
  mountain: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><path d="M2 19l6.5-11 3 5 2-3.2L22 19z"/><path d="M8.5 8l1.6 2.6M13.5 9.8l1.8-2.6 2.2 3.4"/></svg>`,
  book: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><path d="M12 6.5C10 5 7.5 4.5 4 4.5v13c3.5 0 6 .5 8 2 2-1.5 4.5-2 8-2v-13c-3.5 0-6 .5-8 2z"/><path d="M12 6.5v13"/><path d="M7 9.5c1.5 0 3 .3 4 1M7 12.5c1.5 0 3 .3 4 1M17 9.5c-1.5 0-3 .3-4 1M17 12.5c-1.5 0-3 .3-4 1"/></svg>`,
  guqin: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><rect x="2.5" y="8" width="19" height="9" rx="4.5"/><path d="M6 8v9M9.5 8v9M13 8v9M16.5 8v9M20 8v9"/><circle cx="6" cy="6" r="1" fill="currentColor" stroke="none"/><circle cx="18" cy="6" r="1" fill="currentColor" stroke="none"/></svg>`,
  chess: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="7" r="3.2"/><path d="M12 10.2V14"/><path d="M8 14h8v3H8z"/><path d="M6.5 17h11"/><path d="M4 20.5h16"/></svg>`,
  flower: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="2.2"/><path d="M12 9.8C12 7 13 5 12 3M12 14.2c0 2.8-1 4.8 0 6.8M9.8 12c-2.8 0-4.8-1-6.8 0M14.2 12c2.8 0 4.8 1 6.8 0"/><path d="M10.4 10.4C8.4 8.6 7.6 6.6 5.8 5.8M13.6 13.6c2 1.8 2.8 3.8 4.6 4.6M13.6 10.4c1.8-2 3.8-2.8 4.6-4.6M10.4 13.6c-1.8 2-3.8 2.8-4.6 4.6"/></svg>`,
  music: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><path d="M9 18V5l10-2v13"/><circle cx="6.5" cy="18" r="2.5"/><circle cx="16.5" cy="16" r="2.5"/></svg>`,
  run: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><circle cx="14.5" cy="4.5" r="1.8"/><path d="M13 8.5l-3 3 2.5 3-1.5 6M13 8.5l3.5 2 3-1M13 8.5L9 9 6.5 6M10 11.5l-3.5 1.5L4 11"/></svg>`,
  stamp: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><rect x="3.5" y="3.5" width="17" height="17"/><rect x="6" y="6" width="12" height="12" stroke-width="1"/><path d="M6 9.5c1.5 0 1.5-1.5 3-1.5s1.5 1.5 3 1.5 1.5-1.5 3-1.5M6 14.5c1.5 0 1.5-1.5 3-1.5s1.5 1.5 3 1.5 1.5-1.5 3-1.5"/></svg>`,
  mail: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="5.5" width="18" height="13" rx="1.5"/><path d="M3.5 7l8.5 6 8.5-6"/></svg>`,
  wechat: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><path d="M9.5 4C5.9 4 3 6.3 3 9.2c0 1.7 1 3.2 2.6 4.2L5 15.5l2.4-1.2c.6.1 1.3.2 2 .2h.5"/><path d="M21 14.5c0-2.5-2.4-4.5-5.3-4.5S10.5 12 10.5 14.5 12.8 19 15.7 19c.6 0 1.3-.1 1.8-.2l2 1-.5-1.7c1.2-.8 2-2 2-3.6z"/><circle cx="8" cy="8.5" r=".8" fill="currentColor" stroke="none"/><circle cx="12" cy="8.5" r=".8" fill="currentColor" stroke="none"/><circle cx="14" cy="13.5" r=".7" fill="currentColor" stroke="none"/><circle cx="17.5" cy="13.5" r=".7" fill="currentColor" stroke="none"/></svg>`,
  weibo: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><path d="M10 12c-2.8.3-5 2-5 4 0 2.2 2.7 3.8 6 3.5 3.5-.3 6-2.3 5.5-4.5"/><circle cx="10.5" cy="16" r="1.6"/><path d="M13.5 10.5c1.5-.5 3 .3 3.5 1.8M13.5 7.5c3-1 6 .5 7 3.5M13.5 7.5c.3 0 .5.2.5.5"/></svg>`,
  github: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><path d="M9 19c-4 1.5-4-2.5-6-3m12 5v-3.5c0-1 .1-1.4-.5-2 2.8-.3 4.5-1.4 4.5-5a4 4 0 0 0-1-2.7 3.7 3.7 0 0 0-.1-2.8s-1.1-.3-3.5 1.3a12 12 0 0 0-6 0C6.1 3.7 5 4 5 4a3.7 3.7 0 0 0-.1 2.8A4 4 0 0 0 4 9.5c0 3.6 1.7 4.7 4.5 5-.6.6-.6 1.2-.5 2V21"/></svg>`,
  qq: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><path d="M6 9.5a6 6 0 0 1 12 0c0 4 1.5 5.5 2.5 7-1.5.5-2.5 0-3.5 1-1 1-2.5 1.5-5 1.5s-4-.5-5-1.5c-1-1-2-1.5-3.5-1 1-1.5 2.5-3 2.5-7z"/><path d="M9 13.5h.01M15 13.5h.01"/></svg>`,
  phone: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><path d="M5 4h4l1.5 4.5-2.2 1.7a13 13 0 0 0 5.5 5.5l1.7-2.2L20 15v4a2 2 0 0 1-2.2 2A16.5 16.5 0 0 1 3 6.2 2 2 0 0 1 5 4z"/></svg>`,
  location: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><path d="M12 21s7-5.5 7-11a7 7 0 1 0-14 0c0 5.5 7 11 7 11z"/><circle cx="12" cy="10" r="2.6"/></svg>`,
  link: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><path d="M10 14a4 4 0 0 0 5.7 0l3-3a4 4 0 0 0-5.7-5.7L11.5 6.8"/><path d="M14 10a4 4 0 0 0-5.7 0l-3 3a4 4 0 0 0 5.7 5.7l1.5-1.5"/></svg>`
};
const icon = (name) => ICONS[name] || ICONS.link;

/* ─────────── 工具 ─────────── */
const $ = (sel) => document.querySelector(sel);
const esc = (s) => String(s == null ? "" : s)
  .replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")
  .replace(/"/g, "&quot;").replace(/'/g, "&#39;");

/* 图片加载失败时回退到水墨占位图 */
function bindImgFallback(img, fallback) {
  img.addEventListener("error", () => { img.src = fallback; }, { once: true });
}

/* ═══════════ 渲染 ═══════════ */

function renderSite() {
  const s = SITE_DATA.site;
  document.title = s.name + " · 个人主页";
  $("#nav-name").textContent = s.name;
  $("#nav-seal").textContent = s.seal || s.name.slice(0, 1);
  $("#hero-title").textContent = s.heroTitle;
  $("#hero-seal").textContent = s.heroSeal;
  $("#hero-quote").textContent = s.heroQuote;
  $("#hero-sub").textContent = s.heroSub;
  $("#footer-motto").textContent = s.footerMotto;
  $("#footer-text").textContent = s.footerText;
}

function renderProfile() {
  const p = SITE_DATA.profile;
  const cityCount = (SITE_DATA.cities || []).length;
  const stats = (p.stats || []).map((t, i) => {
    // 抵达城市：数字自动跟随 cities 数量
    // data-goto：点击后跳转，works = 滚到行迹；photos/travel/videos = 切到对应标签页
    let num = t.num;
    let extra = "";
    if (t.label === "抵达城市") { num = cityCount + "+"; extra = ' data-city'; }
    if (t.label === "快门次数") { extra = ' data-goto="photos"'; }   // → 照片集
    if ((t.label || "").indexOf("年头") > -1) { extra = ' data-goto="travel"'; }
    // 「热爱程度」「爱好广泛度」这类标签都指向「所好」版块
    if (/热爱|爱好/.test(t.label || "")) { extra = ' data-goto="hobbies"'; }
    return `
    <div class="stat reveal reveal-d2" style="--i:${i}"${extra}>
      <div class="stat-num">${esc(num)}</div>
      <div class="stat-label">${esc(t.label)}</div>
    </div>`;
  }).join("");
  const tags = (p.tags || []).map((t) => `<span>${esc(t)}</span>`).join("");
  const bio = (p.bio || []).map((t) => `<p>${esc(t)}</p>`).join("");

  $("#profile-content").innerHTML = `
    <div class="portrait-frame reveal">
      <img src="${esc(p.portrait)}" alt="肖像">
      <span class="portrait-caption">${esc(p.portraitCaption || "小像")}</span>
    </div>
    <div class="profile-info">
      <div class="profile-name-row reveal reveal-d1">
        <h3 class="profile-name">${esc(p.name)}</h3>
        <span class="profile-en">${esc(p.enName)}</span>
      </div>
      <div class="profile-tags reveal reveal-d1">${tags}</div>
      <div class="profile-bio reveal reveal-d2">${bio}</div>
      <div class="profile-stats">${stats}</div>
    </div>`;

  bindImgFallback($("#profile-content img"), "assets/images/placeholder-portrait.svg");

  // 「抵达城市」→ 打开点亮中国地图；带 data-goto 的 → 跳转到对应版块
  $("#profile-content").querySelectorAll(".stat").forEach((el) => {
    if (el.hasAttribute("data-city")) {
      el.style.cursor = "pointer";
      el.setAttribute("role", "button");
      el.setAttribute("tabindex", "0");
      el.title = "看看去过哪些地方";
      const open = () => { tapStat(el); openCityMap(); };
      el.addEventListener("click", open);
      el.addEventListener("keydown", (e) => { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); open(); } });
    } else if (el.getAttribute("data-goto")) {
      const key = el.getAttribute("data-goto");
      el.style.cursor = "pointer";
      el.setAttribute("role", "button");
      el.setAttribute("tabindex", "0");
      el.title = { travel: "去看看旅行随笔", photos: "去看看照片集",
                   videos: "去看看影像集", hobbies: "去看看所好" }[key] || "去看看行迹";
      el.addEventListener("click", () => gotoWorksPanel(key, el));
      el.addEventListener("keydown", (e) => {
        if (e.key === "Enter" || e.key === " ") { e.preventDefault(); gotoWorksPanel(key, el); }
      });
    }
  });
}

/* ═══════════ 统计数字跳转（切标签 + 缩放聚焦） ═══════════ */
function gotoWorksPanel(key, triggerEl) {
  const REDUCED = prefersReducedMotion();

  // 1) 数字本身轻轻一按，给出点击反馈
  tapStat(triggerEl);

  // 2) 找目标：先找「行迹」里的标签页，找不到就当作整块版块（如 hobbies / works）
  const panel = document.getElementById("panel-" + key) || document.getElementById(key);
  if (!panel) return;

  // 3) 切到目标标签页（已激活就不重复切，只重播动效）
  const btn = document.querySelector('#works-tabs .tab[data-tab="' + key + '"]');
  if (btn && !btn.classList.contains("active")) btn.click();

  // 4) 平滑滚动过去；先切页再算位置，高度才准
  requestAnimationFrame(() => {
    const y = panel.getBoundingClientRect().top + window.scrollY - 90;
    window.scrollTo({ top: y, behavior: REDUCED ? "auto" : "smooth" });
  });

  // 5) 轻微缩放后落定，把视线引过去
  //    整块版块（如「爱好」）只缩放内容区，避免整屏缩放撑出横向滚动条
  if (!REDUCED) zoomPulse(panel.querySelector("[data-zoom-target]") || panel);
}

// 数字轻按反馈（四个统计项统一）
function tapStat(el) {
  if (!el || prefersReducedMotion()) return;
  el.classList.remove("stat-tap");
  void el.offsetWidth;          // 强制重排，保证动画能重播
  el.classList.add("stat-tap");
}

function prefersReducedMotion() {
  return !!(window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches);
}

/* 缩放聚焦：版块从略大收回原尺寸。
   用脚本驱动动画，播完自动结束，页面里不会留下任何残留元素。 */
function zoomPulse(panel) {
  if (typeof panel.animate !== "function") return;   // 老浏览器直接跳过
  panel.style.transformOrigin = "50% 22%";
  panel.animate(
    [
      { transform: "scale(1.016)" },
      { transform: "scale(.998)", offset: .6 },
      { transform: "scale(1)" }
    ],
    { duration: 440, easing: "cubic-bezier(.22,.9,.24,1)" }
  );
}

function renderTravel() {
  const list = SITE_DATA.travel || [];
  const box = $("#travel-list");
  if (!list.length) {
    box.innerHTML = emptyTip("还没有随笔 · 在 js/data.js 的 travel 中添加您的第一篇");
    return;
  }
  const size = PAGE_SIZE.travel;
  const total = Math.ceil(list.length / size);
  pageState.travel = Math.min(Math.max(1, pageState.travel), total);
  const start = (pageState.travel - 1) * size;
  const slice = list.map((item, idx) => ({ item, idx })).slice(start, start + size);

  box.innerHTML = slice.map(({ item: t, idx }) => `
    <article class="travel-item reveal" data-idx="${idx}" tabindex="0" role="button" aria-label="阅读 ${esc(t.title)}">
      <div class="travel-cover">
        <img src="${esc(t.cover)}" alt="${esc(t.title)}" loading="lazy">
        <span class="travel-date">${esc(t.date)}</span>
      </div>
      <div class="travel-body">
        <h3 class="travel-title">${esc(t.title)}</h3>
        <div class="travel-place">${esc(t.place)}</div>
        <p class="travel-excerpt">${esc(t.excerpt)}</p>
        <span class="travel-more">展开细读</span>
      </div>
    </article>`).join("") + paginationHTML("travel", total);

  box.querySelectorAll("img").forEach((img, i) =>
    bindImgFallback(img, `assets/images/travel-${(i % 6) + 1}.svg`));

  box.querySelectorAll(".travel-item").forEach((el) => {
    el.addEventListener("click", () => openArticle(+el.dataset.idx));
    el.addEventListener("keydown", (e) => {
      if (e.key === "Enter" || e.key === " ") { e.preventDefault(); openArticle(+el.dataset.idx); }
    });
  });
  bindPagination(box, "travel");
}

/* 图集卡片悬浮印章：优先用该城市自己的 seal，其次用 site.photoSeal，都没有则用「影」
   字数变多时自动缩小字号并改成长条，避免撑破方框 */
function sealHTML(group) {
  const text = group.seal || (SITE_DATA.site && SITE_DATA.site.photoSeal) || "影";
  const n = text.length;
  const size = n <= 1 ? 16 : n === 2 ? 12 : 10;
  const box = n <= 1 ? "" : `width:auto;min-width:34px;padding:0 7px;letter-spacing:.06em;`;
  return `<span class="photo-seal" style="font-size:${size}px;${box}">${esc(text)}</span>`;
}

/* 图集星标：圆形铜钱样式的中式标记（仅封面左上角，深朱半透明）
   在 data.js 的图集里写一行 star: true 即可开启
   造型：外圆外郭 + 内方孔（方孔钱），深红色，低透明度，尽量不打扰画面 */
function starHTML(group) {
  if (!group.star) return "";
  return `<svg class="album-star" viewBox="0 0 40 40" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
    <rect class="coin-hole" x="13" y="13" width="14" height="14" rx="3.8"/>
    <path class="coin-body" fill-rule="evenodd" d="M20,3 A17,17 0 0,1 20,37 A17,17 0 0,1 20,3 Z M16.6,13.3 L23.4,13.3 A3.3,3.3 0 0 1 26.7,16.6 L26.7,23.4 A3.3,3.3 0 0 1 23.4,26.7 L16.6,26.7 A3.3,3.3 0 0 1 13.3,23.4 L13.3,16.6 A3.3,3.3 0 0 1 16.6,13.3 Z"/>
  </svg>`;
}

/* 相册搜索：既按相册名（城市）过滤，也按相册内的图片名（标题 / 文件名）过滤；
   命中时跳过分页、一次列全，清空即回到原界面 */
let photoQuery = "";

/* 文件名的「裸名」：assets/images/zb2/zb201.jpg → zb201（便于按文件名搜） */
function shotBaseName(src) {
  return (src || "").split("/").pop().replace(/\.[A-Za-z0-9]+$/, "");
}
/* 命中片段标红：先按原始下标切开再各自转义，避免转义后的实体被误伤 */
function hitHTML(text, q) {
  const raw = text || "";
  if (!q) return esc(raw);
  const i = raw.toLowerCase().indexOf(String(q).toLowerCase());
  if (i < 0) return esc(raw);
  return esc(raw.slice(0, i)) + '<b class="hit">' + esc(raw.slice(i, i + q.length)) + "</b>" + esc(raw.slice(i + q.length));
}

function setSearchHint(nAlbum, nShot, q) {
  const hint = $("#album-search-hint");
  const btn = $("#album-search-clear");
  if (btn) btn.hidden = !q;
  if (!hint) return;
  if (!q) { hint.hidden = true; hint.innerHTML = ""; return; }
  hint.hidden = false;
  const n = nAlbum + nShot;
  if (!n) {
    hint.innerHTML = `没有名字含「${esc(photoQuery.trim())}」的相册或照片`;
    return;
  }
  const parts = [];
  if (nAlbum) parts.push(`<b>${nAlbum}</b> 个相册`);
  if (nShot) parts.push(`<b>${nShot}</b> 张照片`);
  hint.innerHTML = `找到 ${parts.join("、")}`;
}

/* 页脚访问量（不蒜子）默认不显示：等它把数字填进来再淡入。
   脚本被广告拦截、服务 502、或本地 file:// 打开时，数字一直是占位符，
   这时整块保持隐藏，不会露出「访客 — 人」这种尴尬的半成品。 */
function initBusuanzi() {
  const box = $("#footer-count");
  if (!box) return;
  const uv = $("#busuanzi_value_site_uv"), pv = $("#busuanzi_value_site_pv");
  const hasNum = (el) => el && el.textContent.trim() && el.textContent.trim() !== "—";
  let tries = 0;
  const timer = setInterval(() => {
    if (hasNum(uv) || hasNum(pv)) { box.classList.add("is-on"); clearInterval(timer); }
    else if (++tries > 20) clearInterval(timer);      // 约 6 秒还没数字，就当没这回事
  }, 300);
}

function initAlbumSearch() {
  const form = $("#album-search"), input = $("#album-search-input"), btn = $("#album-search-clear");
  if (!input) return;
  const apply = () => {
    photoQuery = input.value || "";
    renderPhotos();
    initReveal();
  };
  input.addEventListener("input", apply);                 // 边打边筛，相册数量少不必节流
  if (form) form.addEventListener("submit", (e) => e.preventDefault());
  if (btn) btn.addEventListener("click", () => {
    input.value = "";
    apply();
    input.focus();
  });
}

function renderPhotos() {
  const groups = SITE_DATA.photos || [];
  const box = $("#photo-grid");
  const q = photoQuery.trim().toLowerCase();
  if (!groups.length) {
    box.innerHTML = emptyTip("还没有照片 · 把照片放进 assets/images，并在 js/data.js 登记");
    setSearchHint(0, 0, q);
    return;
  }

  let slice, pager = "", shots = [];
  if (q) {
    // 搜索：相册名命中 → 相册卡片；照片标题或文件名命中 → 照片卡片。两者都一次列全
    slice = [];
    groups.forEach((g, gi) => {
      if ((g.city || "").toLowerCase().includes(q)) slice.push({ g, gi });
      (g.photos || []).forEach((p, pi) => {
        const name = (p.title || "") + " " + shotBaseName(p.src);
        if (name.toLowerCase().includes(q)) shots.push({ g, gi, p, pi });
      });
    });
    setSearchHint(slice.length, shots.length, q);
    if (!slice.length && !shots.length) {
      box.innerHTML = emptyTip("换个关键词试试 · 目前共有 " + groups.length + " 个相册");
      return;
    }
  } else {
    const pool = groups.map((g, gi) => ({ g, gi }));
    setSearchHint(0, 0, q);
    const size = PAGE_SIZE.photos;
    const total = Math.ceil(pool.length / size);
    pageState.photos = Math.min(Math.max(1, pageState.photos), total);
    const start = (pageState.photos - 1) * size;
    slice = pool.slice(start, start + size);
    pager = paginationHTML("photos", total);
  }

  // 每个城市一张封面卡片（用第一张照片做封面）
  const albumHTML = slice.map(({ g, gi }) => {
    const cover = g.photos[0];
    if (!cover) return "";
    return `
      <div class="photo-wrap reveal">
        ${starHTML(g)}
        <figure class="photo-card photo-album" data-gi="${gi}" tabindex="0" role="button" aria-label="查看 ${esc(g.city)} 图集">
          <img src="${esc(cover.src)}" alt="${esc(g.city)}" loading="lazy">
          ${sealHTML(g)}
          <span class="album-count">${g.photos.length} 张</span>
          <figcaption class="photo-meta">
            <span class="photo-title">${hitHTML(g.city, q)}</span>
            <span class="photo-place">共 ${g.photos.length} 张</span>
          </figcaption>
        </figure>
      </div>`;
  }).join("");

  // 命中的单张照片：左上角标城市，右下角标照片名，点开直接放大（可在该图集内前后翻）
  const shotHTML = shots.map(({ g, gi, p, pi }) => {
    const label = p.title || shotBaseName(p.src);
    return `
      <div class="photo-wrap reveal">
        <figure class="photo-card photo-shot" data-gi="${gi}" data-pi="${pi}" tabindex="0" role="button" aria-label="查看 ${esc(label)}（${esc(g.city)}）">
          <img src="${esc(p.src)}" alt="${esc(label)}" loading="lazy">
          ${sealHTML(g)}
          <span class="album-count">${hitHTML(g.city, q)}</span>
          <figcaption class="photo-meta">
            <span class="photo-title">${hitHTML(label, q)}</span>
            <span class="photo-place">${esc(g.city)}</span>
          </figcaption>
        </figure>
      </div>`;
  }).join("");

  box.innerHTML = albumHTML + shotHTML + pager;

  box.querySelectorAll("img").forEach((img, i) =>
    bindImgFallback(img, `assets/images/travel-${(i % 6) + 1}.svg`));

  box.querySelectorAll(".photo-album").forEach((el) => {
    el.addEventListener("click", () => openAlbum(+el.dataset.gi));
    el.addEventListener("keydown", (e) => {
      if (e.key === "Enter" || e.key === " ") { e.preventDefault(); openAlbum(+el.dataset.gi); }
    });
  });
  // 搜索结果的单张照片：点开直接进灯箱，且前后翻的是它所在图集的全部照片
  box.querySelectorAll(".photo-shot").forEach((el) => {
    const jump = () => {
      const g = SITE_DATA.photos[+el.dataset.gi];
      if (!g) return;
      albumPhotos = g.photos || [];
      albumCity = g.city || "";
      openLightbox(+el.dataset.pi);
    };
    el.addEventListener("click", jump);
    el.addEventListener("keydown", (e) => {
      if (e.key === "Enter" || e.key === " ") { e.preventDefault(); jump(); }
    });
  });
  bindPagination(box, "photos");
}

function renderSocial() {
  const list = SITE_DATA.social || [];
  const box = $("#social-grid");
  if (!list.length) {
    box.innerHTML = emptyTip("还没有社交平台 · 在 js/data.js 的 social 中添加");
    return;
  }
  box.innerHTML = list.map((s) => `
    <a class="social-card reveal" href="${esc(s.link)}" target="_blank" rel="noopener">
      <div class="social-name">${esc(s.name)}</div>
      <div class="social-desc">${esc(s.desc)}</div>
      <span class="social-arrow">进入 →</span>
    </a>`).join("");
}

/* ─────────── 分页 ─────────── */
/* 每页显示的条数，可自行调整 */
const PAGE_SIZE = { travel: 3, photos: 9};
const pageState = { travel: 1, photos: 1 };

function paginationHTML(key, total) {
  if (total <= 1) return "";
  const p = pageState[key];
  return `
    <div class="pagination">
      <button class="page-btn" data-step="-1" ${p <= 1 ? "disabled" : ""}>上 一 页</button>
      <span class="page-info">第 ${p} / ${total} 页</span>
      <button class="page-btn" data-step="1" ${p >= total ? "disabled" : ""}>下 一 页</button>
    </div>`;
}

function bindPagination(box, key) {
  box.querySelectorAll(".page-btn").forEach((btn) => {
    btn.addEventListener("click", () => {
      const step = +btn.dataset.step;
      const list = SITE_DATA[key] || [];
      const total = Math.ceil(list.length / PAGE_SIZE[key]);
      pageState[key] = Math.min(Math.max(1, pageState[key] + step), total);
      if (key === "travel") renderTravel();
      else if (key === "photos") renderPhotos();
      initReveal();
      const panel = document.getElementById("panel-" + key);
      if (panel) {
        const y = panel.getBoundingClientRect().top + window.scrollY - 90;
        window.scrollTo({ top: y, behavior: "smooth" });
      }
    });
  });
}

function renderHobbies() {
  const list = SITE_DATA.hobbies || [];
  $("#hobby-grid").innerHTML = list.map((h, i) => `
    <div class="hobby-card reveal ${i % 4 === 1 ? "reveal-d1" : i % 4 === 2 ? "reveal-d2" : i % 4 === 3 ? "reveal-d3" : ""}">
      <div class="hobby-icon">${icon(h.icon)}</div>
      <h3 class="hobby-name">${esc(h.name)}</h3>
      <div class="hobby-en">${esc(h.en)}</div>
      <p class="hobby-desc">${esc(h.desc)}</p>
      <span class="hobby-corner">${esc(h.name.slice(0, 1))}</span>
    </div>`).join("");
}

function renderContact() {
  const s = SITE_DATA.site || {};
  const list = SITE_DATA.contact || [];
  const items = list.map((c) => {
    const inner = c.value
      ? `<span class="c-label">${esc(c.label)}：</span><span class="c-value">${esc(c.value)}</span>`
      : `<span class="c-label">${esc(c.label)}：</span>`;
    return c.link
      ? `<a class="contact-item" href="${esc(c.link)}" target="_blank" rel="noopener">${inner}</a>`
      : `<div class="contact-item">${inner}</div>`;
  }).join("");
  $("#contact-content").innerHTML = `
    <p class="contact-poem">${esc(s.contactPoem || "愿以自由之名 · 与君相遇")}</p>
    <p class="contact-sub">${esc(s.contactSub || "若想聊聊旅行、摄影或茶饭闲事，欢迎随时来敲门")}</p>
    <div class="contact-list">${items}</div>`;
}

function emptyTip(text) {
  return `<div class="empty-tip reveal">${esc(text)}</div>`;
}

/* ═══════════ 图集缩略图选择器（点击相册封面先弹出，一行三张、可下滑） ═══════════ */
const albumBrowser = $("#album-browser");
let browserPhotos = [];   // 当前选择器里的照片数组
let browserGroup = null;  // 当前图集对象（含 city / seal）

/* 右侧极细下滑进度条：按滚动比例定位滑块；内容不足一屏时整条隐藏 */
function updateBrowserRail() {
  const grid = $("#album-browser-grid");
  const rail = $("#album-browser-rail");
  const thumb = $("#album-browser-rail-thumb");
  if (!grid || !rail || !thumb) return;
  const total = grid.scrollHeight;
  const view = grid.clientHeight;
  if (!view || total <= view + 2) { rail.classList.remove("is-on"); return; }
  rail.classList.add("is-on");
  const railH = rail.clientHeight;
  const thumbH = Math.max(24, railH * view / total);
  const ratio = Math.min(1, Math.max(0, grid.scrollTop / (total - view)));
  thumb.style.height = thumbH + "px";
  thumb.style.transform = `translateY(${ratio * (railH - thumbH)}px)`;
}

$("#album-browser-grid").addEventListener("scroll", updateBrowserRail, { passive: true });
window.addEventListener("resize", updateBrowserRail);

/* 瀑布流占位：网格行高 8px、间距 14px，按单元格实际高度换算成占几行，
   这样高矮不一的照片能各自贴着上一张排，空位被压到最小 */
const ROW = 8, GAP = 14;
const thumbMasonry = window.ResizeObserver ? new ResizeObserver((entries) => {
  for (const en of entries) {
    const cell = en.target;
    const h = cell.getBoundingClientRect().height;
    if (!h) continue;
    cell.style.gridRowEnd = `span ${Math.max(1, Math.ceil((h + GAP) / (ROW + GAP)))}`;
  }
  updateBrowserRail();
}) : null;

function openAlbum(gi) {
  const group = SITE_DATA.photos[gi];
  if (!group || !group.photos.length) return;
  browserGroup = group;
  browserPhotos = group.photos;

  // 标题 / 印章 / 数量
  const title = $("#album-browser-title");
  title.textContent = group.city;
  const seal = $("#album-browser-seal");
  seal.textContent = group.seal || (SITE_DATA.site && SITE_DATA.site.photoSeal) || "影";
  seal.style.display = seal.textContent ? "flex" : "none";
  $("#album-browser-count").textContent = `共 ${group.photos.length} 张`;

  // 渲染缩略图（一行三张）
  const grid = $("#album-browser-grid");
  // 直接摆照片：一行三张，各自保留原始比例，不再塞进统一的小方框
  grid.innerHTML = group.photos.map((p, i) => `
    <button class="thumb-cell reveal" data-i="${i}" type="button" aria-label="查看 ${esc(p.title)}">
      <img src="${esc(p.src)}" alt="${esc(p.title)}">
      <span class="thumb-title">${esc(p.title)}</span>
    </button>`).join("");
  // 瀑布流占位：按每张实际高度占掉对应的细行数，尽量补平高低差带来的空位
  if (thumbMasonry) {
    thumbMasonry.disconnect();
    grid.querySelectorAll(".thumb-cell").forEach((c) => thumbMasonry.observe(c));
  }
  grid.querySelectorAll("img").forEach((img, i) =>
    bindImgFallback(img, `assets/images/travel-${(i % 6) + 1}.svg`));

  // 点击缩略图 → 进灯箱（此时才把图集交给灯箱，保证灯箱拿到照片列表）
  grid.querySelectorAll(".thumb-cell").forEach((el) => {
    el.addEventListener("click", () => {
      albumPhotos = browserPhotos;
      albumCity = browserGroup ? browserGroup.city : "";
      openLightbox(+el.dataset.i);
    });
  });

  albumBrowser.classList.add("open");
  albumBrowser.setAttribute("aria-hidden", "false");
  document.body.style.overflow = "hidden";
  // 渐入：滚动容器先滚回顶部，再让缩略图依次浮现
  grid.scrollTop = 0;
  const cells = grid.querySelectorAll(".thumb-cell");
  cells.forEach((el, i) => { el.style.animationDelay = `${Math.min(i, 24) * 0.04}s`; });

  // 进度条：图片陆续加载会改变总高度，得多刷几次
  updateBrowserRail();
  requestAnimationFrame(updateBrowserRail);
  grid.querySelectorAll("img").forEach((img) => {
    if (!img.complete) img.addEventListener("load", updateBrowserRail, { once: true });
  });
  setTimeout(updateBrowserRail, 400);
}

function closeAlbumBrowser() {
  albumBrowser.classList.remove("open");
  albumBrowser.setAttribute("aria-hidden", "true");
  document.body.style.overflow = "";
}
$("#album-browser-close").addEventListener("click", closeAlbumBrowser);
albumBrowser.querySelector(".album-browser-backdrop").addEventListener("click", closeAlbumBrowser);

/* ═══════════ 灯箱（支持图集内多张切换） ═══════════ */
const lightbox = $("#lightbox");
let albumPhotos = [];   // 当前图集的照片数组
let albumCity = "";     // 当前图集城市名
let albumIndex = 0;     // 当前照片索引

/* 玻璃壳要严丝合缝贴着照片：照片被 max-height 压窄后，外层 span 不会自动跟着缩，
   所以按照片的实际渲染尺寸把壳子对齐一次（切换照片 / 改窗口都会触发） */
const lightboxShell = document.querySelector(".lightbox-shot");
const lightboxImg = $("#lightbox-img");
if (lightboxShell && lightboxImg && window.ResizeObserver) {
  new ResizeObserver(() => {
    const w = lightboxImg.offsetWidth, h = lightboxImg.offsetHeight;
    if (!w || !h) return;
    if (Math.abs(lightboxShell.offsetWidth - w) < 1 && Math.abs(lightboxShell.offsetHeight - h) < 1) return;
    lightboxShell.style.width = w + "px";
    lightboxShell.style.height = h + "px";
  }).observe(lightboxImg);
}

function showLightboxPhoto() {
  const ph = albumPhotos[albumIndex];
  if (!ph) return;
  const img = $("#lightbox-img");
  img.src = ph.src;
  img.alt = ph.title;
  // 没写标题时只显示城市名，避免出现「 · 北京」这种空标题
  $("#lightbox-caption").textContent = ph.title ? `${ph.title} · ${albumCity}` : albumCity;
  // 只有一张照片时隐藏切换按钮
  $("#lightbox-prev").style.display = albumPhotos.length > 1 ? "flex" : "none";
  $("#lightbox-next").style.display = albumPhotos.length > 1 ? "flex" : "none";
}

function openLightbox(index) {
  if (!albumPhotos.length) return;
  albumIndex = (index + albumPhotos.length) % albumPhotos.length;
  showLightboxPhoto();
  lightbox.classList.add("open");
  lightbox.setAttribute("aria-hidden", "false");
  document.body.style.overflow = "hidden";
}

function lightboxStep(delta) {
  if (!albumPhotos.length) return;
  albumIndex = (albumIndex + delta + albumPhotos.length) % albumPhotos.length;
  showLightboxPhoto();
}

function closeLightbox() {
  lightbox.classList.remove("open");
  lightbox.setAttribute("aria-hidden", "true");
  document.body.style.overflow = "";
  // 关闭灯箱后回到缩略图选择器（它仍开着），而不是直接回到照片墙
  if (albumBrowser.classList.contains("open")) {
    document.body.style.overflow = "hidden";
  }
}
$("#lightbox-close").addEventListener("click", closeLightbox);
lightbox.querySelector(".lightbox-backdrop").addEventListener("click", closeLightbox);
$("#lightbox-prev").addEventListener("click", (e) => { e.stopPropagation(); lightboxStep(-1); });
$("#lightbox-next").addEventListener("click", (e) => { e.stopPropagation(); lightboxStep(1); });

/* ═══════════ 随笔卷轴 ═══════════ */
const modal = $("#article-modal");
function openArticle(idx) {
  const t = SITE_DATA.travel[idx];
  if (!t) return;
  const paras = (t.content || []).map((p) => `<p>${esc(p)}</p>`).join("");
  $("#modal-body").innerHTML = `
    <span class="article-tag">${esc(t.place)}</span>
    <h3 class="article-title">${esc(t.title)}</h3>
    <div class="article-meta">${esc(t.date)} · ${esc(t.place)}</div>
    <div class="article-divider"></div>
    <figure class="article-cover"><img src="${esc(t.cover)}" alt="${esc(t.title)}"></figure>
    <div class="article-content">${paras}</div>
    <div class="article-end">· 卷 终 ·</div>`;
  bindImgFallback($("#modal-body img"), "assets/images/travel-1.svg");
  modal.classList.add("open");
  modal.setAttribute("aria-hidden", "false");
  document.body.style.overflow = "hidden";
  modal.scrollTop = 0;
}
function closeModal() {
  modal.classList.remove("open");
  modal.setAttribute("aria-hidden", "true");
  document.body.style.overflow = "";
}
$("#modal-close").addEventListener("click", closeModal);
modal.querySelector(".modal-backdrop").addEventListener("click", closeModal);

document.addEventListener("keydown", (e) => {
  if (e.key === "Escape") {
    if (lightbox.classList.contains("open")) { closeLightbox(); return; }
    if (albumBrowser.classList.contains("open")) { closeAlbumBrowser(); return; }
    closeModal(); closeCityMap();
  }
  if (lightbox.classList.contains("open")) {
    if (e.key === "ArrowLeft") lightboxStep(-1);
    if (e.key === "ArrowRight") lightboxStep(1);
  }
});

/* ═══════════ Tab 切换 ═══════════ */
document.querySelectorAll("#works-tabs .tab").forEach((btn) => {
  btn.addEventListener("click", () => {
    document.querySelectorAll("#works-tabs .tab").forEach((b) => b.classList.remove("active"));
    document.querySelectorAll(".tab-panel").forEach((p) => p.classList.remove("active"));
    btn.classList.add("active");
    const panel = $("#panel-" + btn.dataset.tab);
    panel.classList.add("active");
    // 面板刚从隐藏变可见，视口内的卡片直接显示，避免渐显动画不触发留下空白
    initReveal();
    requestAnimationFrame(() => {
      panel.querySelectorAll(".reveal:not(.visible)").forEach((el) => {
        const r = el.getBoundingClientRect();
        if (r.top < window.innerHeight && r.bottom > 0) el.classList.add("visible");
      });
    });
  });
});

/* ═══════════ 渐显动画 ═══════════ */
let observer = null;
function initReveal() {
  if (!observer) {
    observer = new IntersectionObserver((entries) => {
      entries.forEach((en) => {
        if (en.isIntersecting) { en.target.classList.add("visible"); observer.unobserve(en.target); }
      });
    }, { threshold: 0.12, rootMargin: "0px 0px -30px 0px" });
  }
  document.querySelectorAll(".reveal:not(.visible)").forEach((el) => observer.observe(el));
}

/* ═══════════ 导航 ═══════════ */
const navbar = $("#navbar");
const navToggle = $("#nav-toggle");
const navLinks = $("#nav-links");

navToggle.addEventListener("click", () => {
  navToggle.classList.toggle("open");
  navLinks.classList.toggle("show");
});
navLinks.querySelectorAll("a").forEach((a) => a.addEventListener("click", () => {
  navToggle.classList.remove("open");
  navLinks.classList.remove("show");
}));

const sections = ["hero", "profile", "works", "hobbies", "contact"];
function onScroll() {
  navbar.classList.toggle("scrolled", window.scrollY > 40);
  const pos = window.scrollY + 120;
  let current = "hero";
  sections.forEach((id) => {
    const el = document.getElementById(id);
    if (el && el.offsetTop <= pos) current = id;
  });
  navLinks.querySelectorAll("a").forEach((a) => {
    a.classList.toggle("active", a.getAttribute("href") === "#" + current);
  });
}
window.addEventListener("scroll", onScroll, { passive: true });

/* ═══════════ 点亮中国 · 按省点亮 ═══════════
   点击「其人」区的「抵达城市」弹出；城市由 data.js 的 cities 数组驱动，
   数量完全独立于行迹（photos/travel），只认这里输入的 cities。
   规则：按省点亮 —— 一个省有任意一座去过的城市即整块点亮。
   地图轮廓来自 js/china-map.js（含台湾省、香港、澳门，南海诸岛/九段线以附图补充）。 */
const cityMapModal = $("#city-map-modal");

// 省份中文名 → 省份 id（与 china-map.js 的 CHINA_PROVINCES 键对应）
const PROVINCE_ID = {
  "北京": "CNBJ", "天津": "CNTJ", "上海": "CNSH", "重庆": "CNCQ",
  "河北": "CNHE", "山西": "CNSX", "内蒙古": "CNNM", "辽宁": "CNLN",
  "吉林": "CNJL", "黑龙江": "CNHL", "江苏": "CNJS", "浙江": "CNZJ",
  "安徽": "CNAH", "福建": "CNFJ", "江西": "CNJX", "山东": "CNSD",
  "河南": "CNHA", "湖北": "CNHB", "湖南": "CNHN", "广东": "CNGD",
  "广西": "CNGX", "海南": "CNHI", "四川": "CNSC", "贵州": "CNGZ",
  "云南": "CNYN", "西藏": "CNXZ", "陕西": "CNSN", "甘肃": "CNGS",
  "青海": "CNQH", "宁夏": "CNNX", "新疆": "CNXJ",
  "台湾": "CNTW", "香港": "CNHK", "澳门": "CNMO"
};

// 省份 id → 中文名（反向）
const PID_NAME = {};
Object.keys(PROVINCE_ID).forEach((n) => { PID_NAME[PROVINCE_ID[n]] = n; });

/* ─────────── 城市 → 省份 自动识别表 ───────────
   覆盖全国主要地级市/直辖市/自治区首府/特别行政区。
   用户只需填城市名，这里自动匹配所属省份并点亮。
   找不到的城市会归入「未识别」，可在弹窗里手动点击省份点亮。 */
const CITY_PROVINCE = {
  "北京": "北京", "天津": "天津", "上海": "上海", "重庆": "重庆",
  "石家庄": "河北", "唐山": "河北", "秦皇岛": "河北", "邯郸": "河北", "保定": "河北", "张家口": "河北", "承德": "河北", "廊坊": "河北",
  "太原": "山西", "大同": "山西", "平遥": "山西", "忻州": "山西", "临汾": "山西", "运城": "山西",
  "呼和浩特": "内蒙古", "包头": "内蒙古", "鄂尔多斯": "内蒙古", "呼伦贝尔": "内蒙古", "赤峰": "内蒙古",
  "沈阳": "辽宁", "大连": "辽宁", "鞍山": "辽宁", "丹东": "辽宁", "锦州": "辽宁", "营口": "辽宁",
  "长春": "吉林", "吉林": "吉林", "延吉": "吉林", "四平": "吉林", "通化": "吉林",
  "哈尔滨": "黑龙江", "齐齐哈尔": "黑龙江", "大庆": "黑龙江", "牡丹江": "黑龙江", "佳木斯": "黑龙江", "漠河": "黑龙江",
  "南京": "江苏", "苏州": "江苏", "无锡": "江苏", "徐州": "江苏", "常州": "江苏", "扬州": "江苏", "南通": "江苏", "连云港": "江苏", "镇江": "江苏", "盐城": "江苏", "淮安": "江苏",
  "杭州": "浙江", "宁波": "浙江", "温州": "浙江", "绍兴": "浙江", "嘉兴": "浙江", "金华": "浙江", "舟山": "浙江", "台州": "浙江", "湖州": "浙江", "丽水": "浙江", "衢州": "浙江",
  "合肥": "安徽", "黄山": "安徽", "芜湖": "安徽", "安庆": "安徽", "蚌埠": "安徽", "马鞍山": "安徽",
  "福州": "福建", "厦门": "福建", "泉州": "福建", "漳州": "福建", "莆田": "福建", "三明": "福建", "龙岩": "福建", "南平": "福建",
  "南昌": "江西", "景德镇": "江西", "九江": "江西", "上饶": "江西", "赣州": "江西", "婺源": "江西",
  "济南": "山东", "青岛": "山东", "淄博": "山东", "泰安": "山东", "青州": "山东", "烟台": "山东", "潍坊": "山东", "威海": "山东", "临沂": "山东", "济宁": "山东", "日照": "山东", "聊城": "山东", "德州": "山东", "滨州": "山东", "菏泽": "山东", "东营": "山东", "枣庄": "山东",
  "郑州": "河南", "洛阳": "河南", "开封": "河南", "安阳": "河南", "南阳": "河南", "信阳": "河南", "焦作": "河南", "登封": "河南",
  "武汉": "湖北", "宜昌": "湖北", "襄阳": "湖北", "荆州": "湖北", "十堰": "湖北", "黄冈": "湖北", "恩施": "湖北",
  "长沙": "湖南", "张家界": "湖南", "岳阳": "湖南", "衡阳": "湖南", "株洲": "湖南", "湘潭": "湖南", "凤凰": "湖南",
  "广州": "广东", "深圳": "广东", "珠海": "广东", "汕头": "广东", "佛山": "广东", "东莞": "广东", "中山": "广东", "惠州": "广东", "湛江": "广东", "潮州": "广东", "江门": "广东", "韶关": "广东",
  "南宁": "广西", "桂林": "广西", "柳州": "广西", "北海": "广西", "阳朔": "广西",
  "海口": "海南", "三亚": "海南", "儋州": "海南", "文昌": "海南",
  "成都": "四川", "绵阳": "四川", "乐山": "四川", "峨眉山": "四川", "宜宾": "四川", "泸州": "四川", "自贡": "四川", "都江堰": "四川", "康定": "四川", "稻城": "四川",
  "贵阳": "贵州", "遵义": "贵州", "安顺": "贵州", "黔东南": "贵州", "荔波": "贵州",
  "昆明": "云南", "大理": "云南", "丽江": "云南", "香格里拉": "云南", "西双版纳": "云南", "腾冲": "云南", "瑞丽": "云南", "建水": "云南",
  "拉萨": "西藏", "日喀则": "西藏", "林芝": "西藏", "那曲": "西藏",
  "西安": "陕西", "咸阳": "陕西", "延安": "陕西", "宝鸡": "陕西", "汉中": "陕西", "华山": "陕西",
  "兰州": "甘肃", "敦煌": "甘肃", "嘉峪关": "甘肃", "张掖": "甘肃", "天水": "甘肃", "酒泉": "甘肃",
  "西宁": "青海", "格尔木": "青海", "玉树": "青海",
  "银川": "宁夏", "中卫": "宁夏", "吴忠": "宁夏",
  "乌鲁木齐": "新疆", "喀什": "新疆", "伊犁": "新疆", "吐鲁番": "新疆", "库尔勒": "新疆", "阿勒泰": "新疆",
  "台北": "台湾", "高雄": "台湾", "台中": "台湾", "花莲": "台湾", "台南": "台湾",
  "香港": "香港", "澳门": "澳门"
};

// 直辖市 / 特别行政区：城市名本身即省级，小字显示「中国」
const DIRECT_MUNICIPALITIES = new Set(["北京", "天津", "上海", "重庆", "香港", "澳门"]);

/* 解析一条城市记录 → { name, prov }
   支持两种写法：
   ① "城市名"          —— 自动识别省份
   ② "城市名@省份"      —— 显式指定省份（小众地名推荐） */
function parseCity(entry) {
  const raw = (entry || "").trim();
  if (!raw) return { name: "", prov: "" };
  // 含 @ 则显式指定省份
  if (raw.indexOf("@") >= 0) {
    const parts = raw.split("@");
    const name = (parts[0] || "").trim();
    let prov = (parts[1] || "").trim();
    // 去掉省份后缀，统一为 PROVINCE_ID 的键
    prov = prov.replace(/省|市|自治区|特别行政区|壮族|回族|维吾尔/g, "");
    return { name, prov };
  }
  // 纯城市名：自动识别
  return { name: raw, prov: detectProvince(raw) };
}

// 根据城市名识别所属省份（未识别返回 ""）
function detectProvince(cityName) {
  const name = (cityName || "").trim();
  if (!name) return "";
  // 先精确匹配
  if (CITY_PROVINCE[name]) return CITY_PROVINCE[name];
  // 再尝试去尾「市」等后缀
  const bare = name.replace(/[市县区州]$/, "");
  if (CITY_PROVINCE[bare]) return CITY_PROVINCE[bare];
  return "";
}

// 城市词条的小字：直辖市/特别行政区显示「中国」，其余显示省份名
function citySubLabel(name, prov) {
  if (DIRECT_MUNICIPALITIES.has(name)) return "中国";
  return prov || "待补录";
}

// 南海诸岛附图（右下角小图）：仅南海诸岛岛礁示意（东沙、西沙、中沙、南沙、曾母暗沙等）
function southChinaSeaInset() {
  return `
    <g class="scs-inset" transform="translate(770,560) scale(0.62)">
      <circle class="scs-island" cx="118" cy="50" r="2.6"/>
      <circle class="scs-island" cx="132" cy="44" r="2.2"/>
      <circle class="scs-island" cx="150" cy="40" r="2.2"/>
      <circle class="scs-island" cx="166" cy="40" r="2.2"/>
      <circle class="scs-island" cx="182" cy="46" r="2.2"/>
      <circle class="scs-island" cx="196" cy="60" r="2.2"/>
      <circle class="scs-island" cx="200" cy="82" r="2.2"/>
      <circle class="scs-island" cx="176" cy="105" r="2.2"/>
      <circle class="scs-island" cx="140" cy="98" r="2.2"/>
      <circle class="scs-island" cx="108" cy="70" r="2.2"/>
      <text class="scs-label" x="130" y="140">南海诸岛</text>
    </g>`;
}

function renderCityMap() {
  const cities = SITE_DATA.cities || [];
  // 解析每条城市记录，去重得到「点亮省份」集合
  const litProvinces = new Set();
  const unpaired = [];   // 未匹配到省份的城市
  const parsed = cities.map((entry) => {
    const { name, prov } = parseCity(entry);
    const pid = PROVINCE_ID[prov];
    if (prov && pid) {
      litProvinces.add(pid);
    } else if (!pid) {
      unpaired.push(name);
    }
    return { name, prov };
  });

  // 渲染 34 个省级行政区：填充与描边分成两层。
  // 原因：SVG 按文档顺序绘制，若一个 path 同时带 fill+stroke，后画的邻省填充会
  // 盖掉先画省份一半的描边，边界就会显得断断续续。拆层后所有描边统一压在填充之上。
  const pids = Object.keys(CHINA_PROVINCES);
  const fillPaths = pids.map((pid) => {
    const p = CHINA_PROVINCES[pid];
    return `<path class="province province-fill${litProvinces.has(pid) ? " lit" : ""}" data-pid="${pid}" d="${p.d}"/>`;
  }).join("");
  const linePaths = pids.map((pid) => {
    const p = CHINA_PROVINCES[pid];
    return `<path class="province province-line${litProvinces.has(pid) ? " lit" : ""}" data-pid="${pid}" d="${p.d}"/>`;
  }).join("");

  // 城市列表（词条 + 逐个点亮动画，附小字：直辖市/特别行政区显示「中国」）
  // data-pid：能对应到省份的词条才可点，点了地图上同省会高亮
  const chips = parsed.map((c, i) => {
    const sub = citySubLabel(c.name, c.prov);
    const pid = PROVINCE_ID[c.prov] || "";
    const attr = pid
      ? ` data-pid="${pid}" title="看看${esc(c.name)}在哪儿"`
      : ` title="还没匹配到省份，可在 data.js 里写成「${esc(c.name)}@省份」"`;
    return `<span class="city-chip" style="--i:${i}"${attr}>${esc(c.name)}<i>${esc(sub)}</i></span>`;
  }).join("");

  const hint = unpaired.length
    ? `<div class="city-map-hint">以下城市暂未匹配到省份，可在 data.js 里写成「城市名@省份」：${unpaired.map(u => esc(u)).join("、")}</div>`
    : "";

  $("#city-map-body").innerHTML = `
    <div class="city-map-head">
      <h3 class="city-map-title">点亮中国</h3>
      <div class="city-map-count">已走过 <em>${cities.length}</em> 座城市 · 点亮 <em>${litProvinces.size}</em> 个省级行政区</div>
    </div>
    <div class="city-map-stage">
      <svg class="city-map-svg" viewBox="0 0 1000 810" preserveAspectRatio="xMidYMid meet" xmlns="http://www.w3.org/2000/svg">
        <g class="province-layer">${fillPaths}</g>
        <g class="province-line-layer">${linePaths}</g>
        ${southChinaSeaInset()}
        <!-- 高亮省：整块压在最上层，填充 + 描边一起画，边界一定完整 -->
        <g class="province-active-layer" id="map-active-layer"></g>
      </svg>
      <span class="map-disclaimer">地图仅示意，非标准地图</span>
    </div>
    ${hint}
    ${parsed.length ? '<div class="city-map-tip">点城市名，地图上会高亮它所在的省</div>' : ""}
    <div class="city-map-list">${chips}</div>`;

  bindCityChipFocus();
}

/* ─────────── 城市词条 ↔ 地图省份 联动 ───────────
   点（或悬停）下方城市词条，地图上对应的省份高亮、其余淡下去；
   再点一次取消，点别的则切换。未匹配到省份的词条不可点。 */
let cityMapLockedPid = "";

/* pid 为空 = 取消高亮。city 与 city 之间互不关联：
   点淄博只亮山东、只高亮「淄博」这一个词条，同省的济南不会被牵动，
   其余省份也保持原色不淡化。 */
function focusProvince(pid, chipEl) {
  const body = document.getElementById("city-map-body");
  if (!body) return;
  // 词条：只高亮被点（或被悬停）的那一个
  body.querySelectorAll(".city-chip").forEach((el) => {
    el.classList.toggle("active", !!chipEl && el === chipEl);
  });
  // 省份：在最上层重画一份「填充 + 黑边」的副本。
  // 若只给底层省份加粗描边，邻省的描边会在共享边界上盖掉它，轮廓就断了；
  // 放到最上层单独画，整圈边界都在最上面，完整且连续。
  const layer = body.querySelector("#map-active-layer");
  if (!layer) return;
  const p = pid ? CHINA_PROVINCES[pid] : null;
  layer.innerHTML = p
    ? `<path class="pa-fill" data-pid="${pid}" d="${p.d}"/>` +
      `<path class="pa-line" data-pid="${pid}" d="${p.d}"/>`
    : "";
}

function bindCityChipFocus() {
  cityMapLockedPid = "";
  const chips = document.querySelectorAll("#city-map-body .city-chip[data-pid]");
  chips.forEach((chip) => {
    const pid = chip.getAttribute("data-pid");
    chip.setAttribute("role", "button");
    chip.setAttribute("tabindex", "0");
    const toggle = () => {
      cityMapLockedPid = (cityMapLockedPid === pid) ? "" : pid;
      focusProvince(cityMapLockedPid, cityMapLockedPid ? chip : null);
    };
    chip.addEventListener("click", toggle);
    chip.addEventListener("keydown", (e) => {
      if (e.key === "Enter" || e.key === " ") { e.preventDefault(); toggle(); }
    });
    // 没锁定时，鼠标划过即预览高亮
    chip.addEventListener("mouseenter", () => { if (!cityMapLockedPid) focusProvince(pid, chip); });
    chip.addEventListener("mouseleave", () => { if (!cityMapLockedPid) focusProvince(""); });
  });
}

function openCityMap() {
  renderCityMap();
  cityMapModal.classList.add("open");
  cityMapModal.setAttribute("aria-hidden", "false");
  document.body.style.overflow = "hidden";
}
function closeCityMap() {
  cityMapModal.classList.remove("open");
  cityMapModal.setAttribute("aria-hidden", "true");
  document.body.style.overflow = "";
}
$("#city-map-close").addEventListener("click", closeCityMap);
cityMapModal.querySelector(".modal-backdrop").addEventListener("click", closeCityMap);

/* ═══════════ 各板块柔和浮云 ═══════════
   每板块注入云层，多形态，缓慢柔和漂移 */
const SECTION_CLOUDS = [
  // 扁平低云
  "M0,22 C8,20 18,22 28,20 C34,14 46,14 52,20 C60,16 74,16 82,21 C90,18 94,22 90,25 C76,28 60,28 44,26 C30,28 14,28 4,26 C-2,25 -2,23 0,22 Z",
  // 圆润朵云
  "M0,40 C-14,40 -20,30 -12,25 C-18,15 -8,6 4,10 C8,-2 24,-5 32,3 C42,-5 58,-1 62,11 C72,9 80,20 74,28 C82,34 76,44 64,43 C56,46 40,46 30,43 C18,46 8,46 0,40 Z",
  // 长条舒展云
  "M0,30 C10,26 22,30 34,27 C42,18 58,18 66,27 C76,22 92,24 100,30 C108,26 120,28 122,34 C106,40 86,40 66,38 C46,40 26,40 12,38 C2,37 -2,33 0,30 Z"
];

function addSectionClouds() {
  document.querySelectorAll("#profile, #works, #hobbies, #contact").forEach((sec, i) => {
    const layer = document.createElement("div");
    layer.className = "sec-cloud-layer";
    layer.setAttribute("aria-hidden", "true");
    const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
    svg.setAttribute("viewBox", "0 0 1440 800");
    svg.setAttribute("preserveAspectRatio", "xMidYMax slice");
    const gradId = "secCloudGrad" + i;
    svg.innerHTML =
      '<defs><linearGradient id="' + gradId + '" x1="0" y1="0" x2="0" y2="1">' +
      '<stop offset="0%" stop-color="#FFFFFF"/><stop offset="55%" stop-color="#EAF1F6"/>' +
      '<stop offset="100%" stop-color="#B8CBD8"/></linearGradient></defs>';
    // 每板块 4 朵云：形态轮换、位置与漂移方向随机
    for (let k = 0; k < 4; k++) {
      const d = SECTION_CLOUDS[(i + k) % 3];
      const cx = 120 + Math.random() * 1200;          // 初始横向位置随机
      const cy = 120 + Math.random() * 520;           // 初始纵向位置随机
      const dir = Math.random() < 0.5 ? 1 : -1;       // 左右漂移方向随机
      const dist = 120 + Math.random() * 280;         // 漂移距离随机
      const dur = 5 + Math.random() * 2.3;           // 时长随机 5~7.3s，最低速约为之前的 1/3
      const sc = 1.3 + Math.random() * 1.6;           // 尺寸随机
      const o = 0.35 + Math.random() * 0.25;          // 不透明度随机（更透）
      const g = document.createElementNS("http://www.w3.org/2000/svg", "g");
      g.setAttribute("class", "scloud");
      g.setAttribute("style",
        "--cx:" + cx + "px; --cy:" + cy + "px; --dx:" + (dist * dir) + "px;" +
        "--dur:" + dur.toFixed(1) + "s; --sc:" + sc.toFixed(2) + "; --o:" + o.toFixed(2) + ";");
      g.innerHTML = '<path fill="url(#' + gradId + ')" d="' + d + '"/>';
      svg.appendChild(g);
    }
    layer.appendChild(svg);
    sec.appendChild(layer);
  });
}

/* ═══════════ 启动 ═══════════ */
renderSite();
renderProfile();
renderTravel();
renderPhotos();
renderSocial();
renderHobbies();
renderContact();
initAlbumSearch();
initBusuanzi();
initReveal();
addSectionClouds();
onScroll();
