/* ══════════════════════════════════════════════════════════════
 * 页脚「最近更新」——显示网页内容最后一次改动的时间
 *
 * 取值来源按优先级：
 *   1. GitHub 仓库默认分支最后一次提交时间（push 完自动就是新的）
 *   2. localStorage 里上次取到的值（离线 / 接口被限流时兜底）
 *   3. index.html 里写死的静态日期（首次访问且完全没网时才用）
 *
 * 只读公开接口，不需要 token，失败不影响页面其它功能。
 * ══════════════════════════════════════════════════════════════ */
(function () {
  var REPO = 'sifreelee/self_introduction';
  var CACHE_KEY = 'lx-last-update';
  var TIMEOUT_MS = 4000;

  var dateEl = document.getElementById('footer-updated-date');
  if (!dateEl) return;

  function pad(n) {
    return n < 10 ? '0' + n : '' + n;
  }

  function format(iso) {
    if (!iso) return '';
    var d = new Date(iso);
    if (isNaN(d.getTime())) return '';
    return d.getFullYear() + '-' + pad(d.getMonth() + 1) + '-' + pad(d.getDate());
  }

  function readCache() {
    try {
      return localStorage.getItem(CACHE_KEY) || '';
    } catch (e) {
      return '';
    }
  }

  function writeCache(text) {
    try {
      localStorage.setItem(CACHE_KEY, text);
    } catch (e) {
      /* 隐私模式等场景写入失败，忽略即可 */
    }
  }

  function apply(text) {
    if (!text) return;
    dateEl.textContent = text;
    dateEl.setAttribute('datetime', text);
    var box = document.getElementById('footer-updated');
    if (box) box.classList.add('is-on');
  }

  // 先用上次的记录垫上，网络回来再覆盖，避免出现「—」的空档
  apply(readCache());

  // 老浏览器没有 fetch 就到此为止，保留 HTML 里的静态日期
  if (typeof fetch !== 'function') return;

  var opts = {};
  var timer = null;
  if (typeof AbortController === 'function') {
    var ctrl = new AbortController();
    opts.signal = ctrl.signal;
    timer = setTimeout(function () {
      try { ctrl.abort(); } catch (e) {}
    }, TIMEOUT_MS);
  } else {
    timer = setTimeout(function () {}, TIMEOUT_MS);
  }

  fetch('https://api.github.com/repos/' + REPO + '/commits?per_page=1', opts)
    .then(function (res) {
      return res && res.ok ? res.json() : null;
    })
    .then(function (list) {
      if (timer) clearTimeout(timer);
      if (!Array.isArray(list) || !list.length) return;
      var c = list[0].commit || {};
      var iso = (c.committer && c.committer.date) || (c.author && c.author.date);
      var text = format(iso);
      if (!text) return;
      writeCache(text);
      apply(text);
    })
    .catch(function () {
      if (timer) clearTimeout(timer);
      // 接口挂了就用缓存值，什么都不用做
    });
})();
