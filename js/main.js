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
  const stats = (p.stats || []).map((t) => {
    // 抵达城市：数字自动跟随 cities 数量；快门次数：可点击跳转到行迹
    let num = t.num;
    let extra = "";
    if (t.label === "抵达城市") { num = cityCount + "+"; extra = ' data-city'; }
    if (t.label === "快门次数") { extra = ' data-goto="works"'; }
    return `
    <div class="stat reveal reveal-d2"${extra}>
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

  // 「抵达城市」→ 打开点亮中国地图；「快门次数」→ 跳转到行迹
  $("#profile-content").querySelectorAll(".stat").forEach((el) => {
    if (el.hasAttribute("data-city")) {
      el.style.cursor = "pointer";
      el.setAttribute("role", "button");
      el.setAttribute("tabindex", "0");
      el.addEventListener("click", openCityMap);
      el.addEventListener("keydown", (e) => { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); openCityMap(); } });
    } else if (el.getAttribute("data-goto") === "works") {
      el.style.cursor = "pointer";
      el.setAttribute("role", "button");
      el.setAttribute("tabindex", "0");
      el.addEventListener("click", () => {
        const target = document.getElementById("works");
        if (target) target.scrollIntoView({ behavior: "smooth" });
      });
    }
  });
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

function renderPhotos() {
  const groups = SITE_DATA.photos || [];
  const box = $("#photo-grid");
  if (!groups.length) {
    box.innerHTML = emptyTip("还没有照片 · 把照片放进 assets/images，并在 js/data.js 登记");
    return;
  }
  // 按图集（城市）数量分页，每页显示 PAGE_SIZE.photos 本图集
  const size = PAGE_SIZE.photos;
  const total = Math.ceil(groups.length / size);
  pageState.photos = Math.min(Math.max(1, pageState.photos), total);
  const start = (pageState.photos - 1) * size;
  const slice = groups.map((g, gi) => ({ g, gi })).slice(start, start + size);

  // 每个城市一张封面卡片（用第一张照片做封面）
  box.innerHTML = slice.map(({ g, gi }) => {
    const cover = g.photos[0];
    if (!cover) return "";
    return `
      <figure class="photo-card photo-album reveal" data-gi="${gi}" tabindex="0" role="button" aria-label="查看 ${esc(g.city)} 图集">
        <img src="${esc(cover.src)}" alt="${esc(g.city)}" loading="lazy">
        ${sealHTML(g)}
        <span class="album-count">${g.photos.length} 张</span>
        <figcaption class="photo-meta">
          <span class="photo-title">${esc(g.city)}</span>
          <span class="photo-place">共 ${g.photos.length} 张</span>
        </figcaption>
      </figure>`;
  }).join("") + paginationHTML("photos", total);

  box.querySelectorAll("img").forEach((img, i) =>
    bindImgFallback(img, `assets/images/travel-${(i % 6) + 1}.svg`));

  box.querySelectorAll(".photo-album").forEach((el) => {
    el.addEventListener("click", () => openAlbum(+el.dataset.gi));
    el.addEventListener("keydown", (e) => {
      if (e.key === "Enter" || e.key === " ") { e.preventDefault(); openAlbum(+el.dataset.gi); }
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

/* ═══════════ 灯箱（支持图集内多张切换） ═══════════ */
const lightbox = $("#lightbox");
let albumPhotos = [];   // 当前图集的照片数组
let albumCity = "";     // 当前图集城市名
let albumIndex = 0;     // 当前照片索引

function showLightboxPhoto() {
  const ph = albumPhotos[albumIndex];
  if (!ph) return;
  $("#lightbox-img").src = ph.src;
  $("#lightbox-img").alt = ph.title;
  $("#lightbox-caption").textContent = `${ph.title} · ${albumCity}`;
  // 只有一张照片时隐藏切换按钮
  $("#lightbox-prev").style.display = albumPhotos.length > 1 ? "flex" : "none";
  $("#lightbox-next").style.display = albumPhotos.length > 1 ? "flex" : "none";
}

function openAlbum(gi) {
  const group = SITE_DATA.photos[gi];
  if (!group || !group.photos.length) return;
  albumPhotos = group.photos;
  albumCity = group.city;
  albumIndex = 0;
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
  if (e.key === "Escape") { closeLightbox(); closeModal(); closeCityMap(); }
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

  // 渲染 34 个省级行政区 path，点亮的省上色（仅展示，不可点击）
  const provincePaths = Object.keys(CHINA_PROVINCES).map((pid) => {
    const p = CHINA_PROVINCES[pid];
    const lit = litProvinces.has(pid);
    return `<path class="province${lit ? " lit" : ""}" data-pid="${pid}" d="${p.d}"/>`;
  }).join("");

  // 城市列表（词条 + 逐个点亮动画，附小字：直辖市/特别行政区显示「中国」）
  const chips = parsed.map((c, i) => {
    const sub = citySubLabel(c.name, c.prov);
    return `<span class="city-chip" style="--i:${i}">${esc(c.name)}<i>${esc(sub)}</i></span>`;
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
        <g class="province-layer">${provincePaths}</g>
        ${southChinaSeaInset()}
      </svg>
    </div>
    ${hint}
    <div class="city-map-list">${chips}</div>`;
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
initReveal();
addSectionClouds();
onScroll();
