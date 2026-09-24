/* 相册自定义标签 · 功能冒烟测试
   用 jsdom 真实加载 index.html，模拟「点开图集 → 点标签 → 再点取消」，
   断言标签栏渲染、命中数量、数量文案都正确。

   期望值全部从 js/data.js 现算，不写死数字 —— 您增删照片、
   改标签之后重跑，测的还是「功能对不对」，而不是「数字变没变」。

   运行：node smoke_test_tags.js
*/
const fs = require("fs");
const vm = require("vm");
const { JSDOM } = require("jsdom");

const ROOT = "F:/WorkBuddy/personal-website";
const read = (p) => fs.readFileSync(ROOT + "/" + p, "utf8");

/* 把 data.js 当数据源读进来（它顶层是一句 const SITE_DATA = {...}） */
const SD = vm.runInNewContext(read("js/data.js") + "\n;SITE_DATA;", {});

/* 与 main.js 里 shotName / shotHasTag 完全一致的匹配规则：
   只看网页显示名（title），title 为空才用文件名兜底；不区分大小写 */
const shotName = (p) => ((p && p.title) || "").trim()
  || (p && p.src || "").split("/").pop().replace(/\.[A-Za-z0-9]+$/, "");
const hits = (photos, tag) =>
  photos.filter((p) => shotName(p).toLowerCase().includes(tag.toLowerCase()));

let html = read("index.html").replace(/<script[^>]*src="[^"]*"[^>]*><\/script>/g, "");
const dom = new JSDOM(html, { runScripts: "dangerously", pretendToBeVisual: true, url: "http://localhost/" });
const w = dom.window;

// jsdom 没有这几个 API，补最小桩件
w.IntersectionObserver = class { observe() {} unobserve() {} disconnect() {} };
w.ResizeObserver = class { observe() {} unobserve() {} disconnect() {} };
w.matchMedia = () => ({ matches: false, addEventListener() {} });
w.scrollTo = () => {};

// 用 <script> 注入，保证 const 声明落在 window 全局词法环境里
["js/china-map.js", "js/data.js", "js/album-desc.js", "js/main.js"].forEach((f) => {
  const el = w.document.createElement("script");
  el.textContent = read(f);
  w.document.body.appendChild(el);
});

const $ = (s) => w.document.querySelector(s);
let fail = 0;
const ok = (name, cond, extra) => {
  console.log((cond ? "  PASS  " : "  FAIL  ") + name + (extra ? "   → " + extra : ""));
  if (!cond) fail++;
};
const chip = (tag) => [...$("#album-tagbar").querySelectorAll(".tag-chip")]
  .find((el) => el.dataset.tag === tag);
const cellCount = () => $("#album-browser-grid").querySelectorAll(".thumb-cell").length;

// ── 第一本带标签的图集 ─────────────────────────────────────────
const gi = SD.photos.findIndex((g) => (g.tags || []).length > 0);
const G = SD.photos[gi];
const total = G.photos.length;
console.log("目标图集：%s（%d 张，%d 个标签）\n", G.city, total, G.tags.length);

// 1) 打开图集
w.openAlbum(gi);

const bar = $("#album-tagbar");
ok("标签栏已显示", bar && !bar.hidden);
ok("圆角框数量 = 标签数 + 1 个「全部」",
  bar.querySelectorAll(".tag-chip").length === G.tags.length + 1,
  [...bar.querySelectorAll(".tag-chip")].map((el) => `${el.dataset.tag || "全部"}(${el.querySelector(".tag-chip-num").textContent})`).join(" "));

const allChip = chip("");
ok("默认选中「全部」，且张数 = 全部照片",
  allChip.classList.contains("is-on") && +allChip.querySelector(".tag-chip-num").textContent === total,
  String(+allChip.querySelector(".tag-chip-num").textContent));
ok("未筛选时渲染全部照片", cellCount() === total, String(cellCount()));
ok("未筛选时文案为「共 N 张」",
  $("#album-browser-count").textContent === `共 ${total} 张`,
  $("#album-browser-count").textContent);

// 2) 逐个点标签：命中数应与按「网页显示名」算出来的一致
G.tags.forEach((t) => {
  const want = hits(G.photos, t).length;
  const el = chip(t);
  if (!el) { ok(`标签「${t}」已渲染`, false); return; }
  el.dispatchEvent(new w.MouseEvent("click", { bubbles: true }));

  const showed = +chip(t).querySelector(".tag-chip-num").textContent;
  const shown = cellCount();
  ok(`「${t}」：框上张数 ${showed} = 实际显示 ${shown} = 规则算出 ${want}`,
    showed === want && shown === want, `${showed} / ${shown} / ${want}`);

  if (want) {
    const titles = [...$("#album-browser-grid").querySelectorAll(".thumb-title")].map((e) => e.textContent);
    ok(`「${t}」：每张标题都真的含这个词`,
      titles.length === want && titles.every((x) => x.toLowerCase().includes(t.toLowerCase())));
  }

  // 点第二次 → 取消
  chip(t).dispatchEvent(new w.MouseEvent("click", { bubbles: true }));
  ok(`「${t}」：再点一次回到全部`, cellCount() === total && chip("").classList.contains("is-on"));
});

// 3) 一次全 lattice 检查：命中 0 的标签应显示为半透明
const empties = G.tags.filter((t) => hits(G.photos, t).length === 0);
ok("零命中标签标为半透明",
  empties.every((t) => chip(t) && chip(t).classList.contains("is-empty")),
  empties.length ? empties.join("、") : "（本图集没有零命中标签）");

// 4) 没配 tags 的图集不显示标签栏
const ngi = SD.photos.findIndex((g) => !(g.tags || []).length);
if (ngi >= 0) {
  w.openAlbum(ngi);
  ok("未配 tags 的图集隐藏标签栏", $("#album-tagbar").hidden,
    "当前相册：" + $("#album-browser-title").textContent);
  ok("未配 tags 的图集仍能正常显示照片",
    cellCount() === SD.photos[ngi].photos.length, String(cellCount()));
}

console.log(fail ? `\n${fail} 项未通过` : "\n全部通过");
w.close();
process.exit(fail ? 1 : 0);
