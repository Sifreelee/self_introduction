/* 静态网站的下载入口控制；原图为公开资源，不提供服务端访问保护。 */
(function (root) {
  const KEY = 'photo-admin-session-v2';
  const TTL = 30 * 24 * 60 * 60 * 1000;
  const PASSWORD_HASH = "4eceff2d63a93e460ae3d00cc2869e712d8b0413abb45c7344a43abf03c5f35e";
  function create(options = {}) {
    const clock = options.now || Date.now;
    const cryptoApi = options.crypto || root.crypto;
    let storage = options.storage;
    if (storage === undefined) {
      try { storage = root.localStorage; } catch (_) { storage = null; }
    }
    let session = null, persistent = true, generation = 0;
    function valid(value) {
      const now = clock();
      return value && value.version === 1 && value.user === 'sifree'
        && Number.isSafeInteger(value.issuedAt) && Number.isSafeInteger(value.expiresAt)
        && value.issuedAt <= now && value.expiresAt === value.issuedAt + TTL
        && value.expiresAt > now;
    }
    function read() {
      if (storage && persistent) {
        let raw;
        try { raw = storage.getItem(KEY); } catch (_) { persistent = false; }
        if (persistent) {
          try { session = JSON.parse(raw); } catch (_) { session = null; }
        }
      }
      if (!valid(session)) session = null;
      return session;
    }
    function logout() {
      generation++;
      session = null;
      try { if (storage) storage.removeItem(KEY); } catch (_) { persistent = false; }
    }
    async function login(user, password) {
      const attempt = ++generation;
      if (user !== 'sifree') return false;
      if (!cryptoApi || !cryptoApi.subtle) throw new Error('请通过 HTTPS 网站登录管理员模式。');
      const bytes = new TextEncoder().encode(user + ':' + password);
      const digest = await cryptoApi.subtle.digest('SHA-256', bytes);
      const hash = Array.from(new Uint8Array(digest), b => b.toString(16).padStart(2, '0')).join('');
      if (hash !== PASSWORD_HASH || attempt !== generation) return false;
      const issuedAt = clock();
      session = {version: 1, user, issuedAt, expiresAt: issuedAt + TTL};
      try {
        if (!storage) throw new Error('Storage unavailable');
        storage.setItem(KEY, JSON.stringify(session));
        persistent = true;
      } catch (_) { persistent = false; }
      return true;
    }
    return {login, logout, isAdmin: () => !!read(),
      expiresAt: () => { const value = read(); return value ? value.expiresAt : 0; },
      persistent: () => persistent};
  }
  const api = {create, KEY, TTL};
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
  else root.PhotoAdminAuth = api;
})(typeof globalThis !== 'undefined' ? globalThis : window);
