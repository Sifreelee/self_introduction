/* 相册自定义标签 · 功能冒烟测试
   用 jsdom 真实加载 index.html，模拟「点开图集 → 点标签 → 再点取消」，
   断言标签栏渲染、命中数量、数量文案都正确。

   运行：node smoke_test_tags.js
*/
const fs = require("fs");
const { JSDOM } = require("jsdom");

const ROOT = "F:/WorkBuddy/personal-website";
const read = (p) => fs.readFileSync(ROOT + "/" + p, "utf8");

let html = read("index.html").replace(/<script[^>]*src="[^"]*"[^>]*><\/script>/g, "");
const dom = new JSDOM(html, { runScripts: "dangerously", pretendToBeVisual: true, url: "http://localhost/" });
const w = dom.window;

// jsdom 没有这两个 API，补最小桩件
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

// 1) 打开第一本图集（文物介绍及科普）
$(".photo-album").dispatchEvent(new w.MouseEvent("click", { bubbles: true }));

const bar = $("#album-tagbar");
ok("标签栏已显示", bar && !bar.hidden);
const chips = [...bar.querySelectorAll(".tag-chip")].map((el) => ({
  tag: el.dataset.tag, num: +el.querySelector(".tag-chip-num").textContent, on: el.classList.contains("is-on")
}));
ok("全部 + 6 个标签 = 7 个圆角框", chips.length === 7, chips.map((c) => `${c.tag || "全部"}(${c.num})`).join(" "));
ok("默认选中「全部」", chips[0].on && !chips.slice(1).some((c) => c.on));
ok("全部 = 184 张", chips[0].num === 184, String(chips[0].num));
const cells0 = $("#album-browser-grid").querySelectorAll(".thumb-cell").length;
ok("未筛选时渲染 184 张缩略图", cells0 === 184, String(cells0));

// 2) 点「青铜器」
const bronze = [...bar.querySelectorAll(".tag-chip")].find((el) => el.dataset.tag === "青铜器");
bronze.dispatchEvent(new w.MouseEvent("click", { bubbles: true }));
const cells1 = $("#album-browser-grid").querySelectorAll(".thumb-cell").length;
ok("点「青铜器」后只剩 46 张", cells1 === 46, String(cells1));
ok("数量文案变成「46 / 184 张」", $("#album-browser-count").textContent === "46 / 184 张",
  $("#album-browser-count").textContent);
const onChip = $("#album-tagbar .tag-chip.is-on");
ok("「青铜器」框处于选中态", onChip && onChip.dataset.tag === "青铜器");

// 3) 再点一次 → 取消
$("#album-tagbar .tag-chip.is-on").dispatchEvent(new w.MouseEvent("click", { bubbles: true }));
const cells2 = $("#album-browser-grid").querySelectorAll(".thumb-cell").length;
ok("再点一次回到 184 张", cells2 === 184, String(cells2));
ok("数量文案回到「共 184 张」", $("#album-browser-count").textContent === "共 184 张",
  $("#album-browser-count").textContent);

// 3.5) 只认网页显示名：文件名里带「金银器」、但标题是「青铜器 / 陶瓷」的 2 张不该被算进来
const gold = [...$("#album-tagbar").querySelectorAll(".tag-chip")].find((el) => el.dataset.tag === "金银器");
ok("「金银器」标签命中 35 张（不再把文件名里的 2 张算进来）",
  +gold.querySelector(".tag-chip-num").textContent === 35,
  gold.querySelector(".tag-chip-num").textContent);
gold.dispatchEvent(new w.MouseEvent("click", { bubbles: true }));
const goldTitles = [...$("#album-browser-grid").querySelectorAll(".thumb-title")].map((el) => el.textContent);
ok("筛出来的每张标题都真的含「金银器」",
  goldTitles.length === 35 && goldTitles.every((t) => t.includes("金银器")),
  goldTitles.length + " 张");

// 4) 没配标签的图集不显示标签栏（第 13 本：江苏 徐州，只有 1 张照片）
w.openAlbum(12);
ok("未配 tags 的图集隐藏标签栏", $("#album-tagbar").hidden,
  "当前相册：" + $("#album-browser-title").textContent);
ok("未配 tags 的图集仍能正常显示照片",
  $("#album-browser-grid").querySelectorAll(".thumb-cell").length === 1);

console.log(fail ? `\n${fail} 项未通过` : "\n全部通过");
w.close();
process.exit(fail ? 1 : 0);
