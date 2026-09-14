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
  const stats = (p.stats || []).map((t) => `
    <div class="stat reveal reveal-d2">
      <div class="stat-num">${esc(t.num)}</div>
      <div class="stat-label">${esc(t.label)}</div>
    </div>`).join("");
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

function renderPhotos() {
  const list = SITE_DATA.photos || [];
  const box = $("#photo-grid");
  if (!list.length) {
    box.innerHTML = emptyTip("还没有照片 · 把照片放进 assets/images，并在 js/data.js 登记");
    return;
  }
  const size = PAGE_SIZE.photos;
  const total = Math.ceil(list.length / size);
  pageState.photos = Math.min(Math.max(1, pageState.photos), total);
  const start = (pageState.photos - 1) * size;
  const slice = list.map((item, idx) => ({ item, idx })).slice(start, start + size);

  box.innerHTML = slice.map(({ item: ph, idx }) => `
    <figure class="photo-card reveal" data-idx="${idx}" tabindex="0" role="button" aria-label="查看 ${esc(ph.title)}">
      <img src="${esc(ph.src)}" alt="${esc(ph.title)}" loading="lazy">
      <span class="photo-seal">影</span>
      <figcaption class="photo-meta">
        <span class="photo-title">${esc(ph.title)}</span>
        <span class="photo-place">${esc(ph.place)}</span>
      </figcaption>
    </figure>`).join("") + paginationHTML("photos", total);

  box.querySelectorAll("img").forEach((img, i) =>
    bindImgFallback(img, `assets/images/travel-${(i % 6) + 1}.svg`));

  box.querySelectorAll(".photo-card").forEach((el) => {
    el.addEventListener("click", () => openLightbox(+el.dataset.idx));
    el.addEventListener("keydown", (e) => {
      if (e.key === "Enter" || e.key === " ") { e.preventDefault(); openLightbox(+el.dataset.idx); }
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
const PAGE_SIZE = { travel: 3, photos: 6 };
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
    <p class="contact-poem">愿 以 山 水 之 名 · 与 君 相 遇</p>
    <p class="contact-sub">若想聊聊旅行、摄影或茶饭闲事，欢迎随时来敲门</p>
    <div class="contact-list">${items}</div>`;
}

function emptyTip(text) {
  return `<div class="empty-tip reveal">${esc(text)}</div>`;
}

/* ═══════════ 灯箱 ═══════════ */
const lightbox = $("#lightbox");
function openLightbox(idx) {
  const ph = SITE_DATA.photos[idx];
  if (!ph) return;
  $("#lightbox-img").src = ph.src;
  $("#lightbox-img").alt = ph.title;
  $("#lightbox-caption").textContent = `${ph.title} · ${ph.place}`;
  lightbox.classList.add("open");
  lightbox.setAttribute("aria-hidden", "false");
  document.body.style.overflow = "hidden";
}
function closeLightbox() {
  lightbox.classList.remove("open");
  lightbox.setAttribute("aria-hidden", "true");
  document.body.style.overflow = "";
}
$("#lightbox-close").addEventListener("click", closeLightbox);
lightbox.querySelector(".lightbox-backdrop").addEventListener("click", closeLightbox);

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
  if (e.key === "Escape") { closeLightbox(); closeModal(); }
});

/* ═══════════ Tab 切换 ═══════════ */
document.querySelectorAll("#works-tabs .tab").forEach((btn) => {
  btn.addEventListener("click", () => {
    document.querySelectorAll("#works-tabs .tab").forEach((b) => b.classList.remove("active"));
    document.querySelectorAll(".tab-panel").forEach((p) => p.classList.remove("active"));
    btn.classList.add("active");
    $("#panel-" + btn.dataset.tab).classList.add("active");
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

/* ═══════════ 启动 ═══════════ */
renderSite();
renderProfile();
renderTravel();
renderPhotos();
renderSocial();
renderHobbies();
renderContact();
initReveal();
onScroll();
