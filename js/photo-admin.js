(function () {
  const auth = PhotoAdminAuth.create();
  const toggle = document.getElementById('admin-mode');
  const entry = document.getElementById('admin-login-entry');
  const dialog = document.getElementById('admin-login');
  const form = document.getElementById('admin-login-form');
  const error = document.getElementById('admin-login-error');
  const status = document.getElementById('admin-status');
  const download = document.getElementById('photo-download');
  const actions = document.getElementById('photo-actions');
  let timer, lastFocus;
  function update() {
    const active = auth.isAdmin();
    entry.textContent = active ? '管理' : '登录';
    entry.setAttribute('aria-label', active ? '管理管理员登录状态' : '管理员登录');
    form.hidden = active;
    document.getElementById('admin-session').hidden = !active;
    document.getElementById('admin-login-title').textContent = active ? '管理员模式' : '管理员登录';
    document.body.classList.toggle('photo-guest', !active);
    download.textContent = active ? '下载照片' : '管理员登录后下载';
    status.textContent = active ? (auth.persistent()
      ? '管理员模式有效至 ' + new Date(auth.expiresAt()).toLocaleString('zh-CN')
      : '管理员模式已开启；浏览器无法记住登录，仅本次页面有效') : '';
    clearTimeout(timer);
    if (active) timer = setTimeout(update, Math.min(auth.expiresAt() - Date.now(), 24 * 60 * 60 * 1000));
    return active;
  }
  function requestLogin() {
    if (actions.open) actions.close();
    if (dialog.open) return;
    lastFocus = document.activeElement;
    error.textContent = '';
    form.reset();
    update();
    dialog.showModal();
    if (auth.isAdmin()) document.getElementById('admin-logout').focus();
    else toggle.focus();
  }
  function logout() { auth.logout(); update(); }
  window.photoAdmin = {isAdmin: update, requestLogin, logout};
  entry.addEventListener('click', requestLogin);
  document.getElementById('admin-logout').addEventListener('click', () => { logout(); dialog.close(); });
  // 兼容 App 设置按钮在页面脚本之前或之后注入，确保登录总在设置左边。
  const utilities = document.getElementById('nav-utilities');
  function placeSettings() {
    const settings = document.getElementById('lx-settings-btn');
    if (settings && settings.parentNode !== utilities) utilities.appendChild(settings);
  }
  const navigation = document.querySelector('.nav-inner');
  new MutationObserver(placeSettings).observe(navigation, {childList: true, subtree: true});
  placeSettings();
  dialog.addEventListener('close', () => {
    document.getElementById('admin-password').value = '';
    auth.isAdmin() || auth.logout(); // 取消尚未完成的异步登录。
    update();
    if (lastFocus) lastFocus.focus();
  });
  document.getElementById('admin-cancel').addEventListener('click', () => dialog.close());
  form.addEventListener('submit', async e => {
    e.preventDefault();
    const submit = form.querySelector('[type="submit"]');
    submit.disabled = true;
    error.textContent = '';
    try {
      const ok = await auth.login(document.getElementById('admin-user').value.trim(), document.getElementById('admin-password').value);
      if (ok && dialog.open) dialog.close();
      else if (dialog.open) error.textContent = '账号或密码不正确';
    } catch (err) { error.textContent = err.message; }
    finally { document.getElementById('admin-password').value = ''; submit.disabled = false; update(); }
  });
  async function savePhoto(img) {
    if (!update()) { requestLogin(); return; }
    if (!img || !img.getAttribute('src')) return;
    const url = new URL(img.currentSrc || img.src, location.href);
    if (url.origin !== location.origin || !['https:', 'http:', 'file:'].includes(url.protocol)) return;
    if (window.AndroidBridge && typeof window.AndroidBridge.downloadImage === 'function') {
      window.AndroidBridge.downloadImage(url.href, img.alt || '照片');
      return;
    }
    download.disabled = true;
    try {
      const response = await fetch(url.href);
      if (!response.ok) throw new Error('照片下载失败，请稍后重试');
      const blob = await response.blob();
      if (!update()) { requestLogin(); return; }
      const objectUrl = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = objectUrl;
      link.download = decodeURIComponent(url.pathname.split('/').pop()) || '照片.jpg';
      document.body.appendChild(link);
      link.click(); link.remove();
      setTimeout(() => URL.revokeObjectURL(objectUrl), 60000);
    } catch (err) { status.textContent = err.message || '照片下载失败，请稍后重试'; }
    finally { download.disabled = false; }
  }
  download.addEventListener('click', () => savePhoto(document.getElementById('lightbox-img')));
  const scope = '.photo-album,.photo-shot,#album-browser,#lightbox';
  document.addEventListener('contextmenu', e => {
    const area = e.target.closest && e.target.closest(scope);
    if (!area || update()) return;
    e.preventDefault();
    if (window.AndroidBridge) return; // App 使用原生长按菜单。
    const card = e.target.closest('.photo-album,.photo-shot');
    const url = card ? getAlbumShareUrl(+card.dataset.gi) : area.dataset.albumUrl;
    const share = document.getElementById('photo-share-link');
    share.hidden = !url;
    share.onclick = async () => {
      try { await navigator.clipboard.writeText(url); actions.close(); }
      catch (_) { actions.close(); window.prompt('复制相册链接', url); }
    };
    if (!actions.open) actions.showModal();
  }, true);
  document.getElementById('photo-action-login').addEventListener('click', requestLogin);
  document.getElementById('photo-action-close').addEventListener('click', () => actions.close());
  document.addEventListener('dragstart', e => {
    if (e.target.closest && e.target.closest(scope) && !update()) e.preventDefault();
  });
  document.addEventListener('visibilitychange', update);
  window.addEventListener('focus', update);
  window.addEventListener('storage', update);
  update();
})();
