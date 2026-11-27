/* 零碎日月：静音悬停 / 长按预览，松开后暂停，进度保留。 */
(() => {
  'use strict';
  const grid = document.getElementById('video-grid');
  const panel = document.getElementById('panel-photos');
  if (!grid || !panel) return;
  const preview = new URLSearchParams(location.search).get('preview') === '1';
  const entries = [...((window.VIDEO_CONFIG || {}).videos || [])];
  const controllers = [];
  const localUrls = [];
  let active = null;
  const viewer = document.createElement('dialog');
  viewer.className = 'video-viewer';
  viewer.setAttribute('aria-label', '放大查看视频');
  viewer.innerHTML = '<button type="button" class="lightbox-close" aria-label="关闭放大视频">&times;</button><figure class="lightbox-figure"><div class="video-viewer-screen"></div><figcaption></figcaption></figure>';
  document.body.appendChild(viewer);
  let restoreViewer = null;
  viewer.querySelector('button').addEventListener('click', () => viewer.close());
  viewer.addEventListener('click', event => { if (event.target === viewer) viewer.close(); });
  viewer.addEventListener('close', () => { if (restoreViewer) { const restore = restoreViewer; restoreViewer = null; restore(); } });
  const time = seconds => {
    if (!Number.isFinite(seconds) || seconds < 0) return '0:00';
    const value = Math.floor(seconds);
    return Math.floor(value / 60) + ':' + String(value % 60).padStart(2, '0');
  };
  function text(tag, className, value) {
    const node = document.createElement(tag);
    node.className = className;
    node.textContent = value;
    return node;
  }
  function card(item) {
    const article = document.createElement('article');
    article.className = 'video-card';
    const stage = document.createElement('div');
    stage.className = 'video-stage';
    stage.tabIndex = 0;
    stage.setAttribute('role', 'button');
    stage.setAttribute('aria-label', `${item.title || '未命名视频'}，悬停或长按预览，单击或按空格切换暂停和继续`);
    stage.setAttribute('aria-pressed', 'false');
    const video = document.createElement('video');
    video.preload = 'metadata';
    video.muted = true;
    video.defaultMuted = true;
    video.playsInline = true;
    video.setAttribute('playsinline', '');
    video.setAttribute('webkit-playsinline', '');
    video.setAttribute('disablepictureinpicture', '');
    video.setAttribute('aria-hidden', 'true');
    const poster = new Image();
    poster.className = 'video-poster';
    poster.alt = '';
    poster.loading = 'lazy';
    if (item.poster) poster.src = item.poster;
    else poster.hidden = true;
    poster.addEventListener('error', () => { poster.hidden = true; });
    const play = document.createElement('span');
    play.className = 'video-play';
    play.setAttribute('aria-hidden', 'true');
    play.innerHTML = '<svg viewBox="0 0 16 16"><path d="M3 1L14 8 3 15Z"/></svg>';
    const overlay = document.createElement('div');
    overlay.className = 'video-overlay';
    const state = text('span', 'video-state', item.src ? '悬停 / 长按播放' : '等待视频');
    const clock = text('span', 'video-time', '0:00 / --:--');
    overlay.append(state, clock);
    stage.append(video, poster, play, overlay);
    const media = document.createElement('div');
    media.className = 'video-media';
    const sound = document.createElement('button');
    sound.type = 'button';
    sound.className = 'video-sound';
    function updateSound() {
      const label = video.muted ? '开启声音' : '关闭声音';
      sound.setAttribute('aria-label', label);
      sound.setAttribute('aria-pressed', String(!video.muted));
      sound.title = label;
      sound.innerHTML = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M11 5L6 9H3v6h3l5 4Z"/>' + (video.muted ? '<path d="M16 9l6 6m0-6l-6 6"/>' : '<path d="M15 8a6 6 0 010 8m3-11a10 10 0 010 14"/>') + '</svg>';
    }
    sound.addEventListener('click', event => { event.stopPropagation(); video.muted = !video.muted; updateSound(); });
    updateSound();
    const expand = document.createElement('button');
    expand.type = 'button';
    expand.className = 'video-expand';
    expand.setAttribute('aria-label', `放大查看${item.title || '视频'}`);
    expand.title = '放大查看';
    expand.disabled = !item.src;
    expand.innerHTML = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M3 9V3h6m6 0h6v6M3 15v6h6m6 0h6v-6"/></svg>';
    media.append(stage, sound, expand);
    const progress = document.createElement('input');
    progress.type = 'range';
    progress.className = 'video-progress';
    progress.min = 0;
    progress.max = 1000;
    progress.step = 1;
    progress.value = 0;
    progress.disabled = !item.src;
    progress.setAttribute('aria-label', `${item.title || '视频'}的播放进度`);
    const meta = document.createElement('div');
    meta.className = 'photo-meta';
    meta.append(text('h3', 'photo-title', item.title || '未命名视频'));
    article.append(media, progress, meta);
    if (item.description) article.append(text('p', 'video-description', item.description));
    const place = document.createElement('details');
    place.className = 'video-place';
    place.append(text('summary', '', '拍摄地'), text('span', 'video-place-value', item.location || '拍摄地待填写'));
    article.append(place);
    let wanted = false, holdTimer, touchStart = null, failed = false, destroyed = false, pendingSeek = null;
    let manual = false, longPressed = false, suppressClickUntil = 0, hoverCount = 0, playRequest = 0;
    const update = () => {
      const duration = video.duration;
      progress.value = Number.isFinite(duration) && duration > 0 ? video.currentTime / duration * 1000 : 0;
      progress.style.setProperty('--played', `${Number(progress.value) / 10}%`);
      clock.textContent = `${time(video.currentTime)} / ${Number.isFinite(duration) ? time(duration) : '--:--'}`;
      progress.setAttribute('aria-valuetext', clock.textContent);
    };
    function stop() {
      playRequest++;
      wanted = false;
      clearTimeout(holdTimer);
      holdTimer = null;
      touchStart = null;
      video.pause();
      article.classList.remove('is-playing');
      stage.setAttribute('aria-pressed', 'false');
      if (!failed) state.textContent = item.src ? (video.currentTime > 0 ? '已暂停' : '悬停 / 长按播放') : '等待视频';
      if (active === controller) active = null;
    }
    async function start() {
      if (!item.src || failed || destroyed || !panel.classList.contains('active') || document.hidden) return;
      if (active && active !== controller) active.stop();
      active = controller;
      wanted = true;
      const request = ++playRequest;
      state.textContent = '正在加载';
      if (!video.getAttribute('src')) video.src = item.src;
      if (video.ended) video.currentTime = 0;
      try {
        await video.play();
        if (request !== playRequest) return;
        if (!wanted || destroyed) { video.pause(); return; }
      } catch (error) {
        if (request !== playRequest || !wanted || destroyed) return;
        stop();
        state.textContent = error.name === 'NotAllowedError' ? '按住空格或长按重试' : '暂时无法播放';
      }
    }
    const controller = {
      stop,
      prepare() { if (item.src && !failed && !destroyed && !video.getAttribute('src')) { video.src = item.src; video.load(); } },
      stopPreview() { if (!manual) stop(); },
      destroy() { stop(); destroyed = true; video.removeAttribute('src'); video.load(); }
    };
    controllers.push(controller);
    expand.addEventListener('click', () => {
      if (viewer.open) viewer.close();
      const wasPlaying = wanted || !video.paused;
      stopAll();
      manual = true;
      const previousOverflow = document.body.style.overflow;
      video.controls = true;
      video.removeAttribute('aria-hidden');
      if (item.poster) video.poster = item.poster;
      if (!video.getAttribute('src')) video.src = item.src;
      viewer.querySelector('.video-viewer-screen').appendChild(video);
      viewer.querySelector('figcaption').textContent = item.title || '未命名视频';
      restoreViewer = () => {
        stop();
        video.controls = false;
        video.setAttribute('aria-hidden', 'true');
        stage.prepend(video);
        document.body.style.overflow = previousOverflow;
        update();
        expand.focus({preventScroll:true});
      };
      viewer.showModal();
      document.body.style.overflow = 'hidden';
      if (wasPlaying) start();
    });
    video.addEventListener('playing', () => {
      if (viewer.contains(video)) { wanted = true; active = controller; }
      if (!wanted) { video.pause(); return; }
      article.classList.add('is-playing');
      stage.setAttribute('aria-pressed', 'true');
      state.textContent = '静音播放中';
    });
    video.addEventListener('pause', () => {
      if (viewer.contains(video)) { wanted = false; article.classList.remove('is-playing'); stage.setAttribute('aria-pressed', 'false'); }
    });
    video.addEventListener('waiting', () => { if (wanted) state.textContent = '正在缓冲'; });
    video.addEventListener('timeupdate', update);
    video.addEventListener('loadedmetadata', () => {
      if (pendingSeek !== null && Number.isFinite(video.duration)) { video.currentTime = video.duration * pendingSeek; pendingSeek = null; }
      update();
    });
    progress.addEventListener('pointerdown', stop);
    progress.addEventListener('keydown', stop);
    progress.addEventListener('input', () => {
      stop();
      const fraction = Number(progress.value) / 1000;
      progress.style.setProperty('--played', `${fraction * 100}%`);
      if (Number.isFinite(video.duration) && video.duration > 0) {
        video.currentTime = video.duration * fraction;
        update();
      } else {
        pendingSeek = fraction;
        state.textContent = '正在定位';
        if (!video.getAttribute('src')) { video.src = item.src; video.load(); }
      }
    });
    video.addEventListener('ended', () => { stop(); manual = false; state.textContent = '已播完 · 点击重播'; });
    video.addEventListener('error', () => { if (destroyed) return; failed = true; stop(); state.textContent = '视频暂时无法加载'; });
    function mouseEnter(event) {
      if (event.pointerType !== 'mouse' || manual || media.contains(event.relatedTarget)) return;
      hoverCount++;
      if (hoverCount >= 2) manual = true;
      start();
    }
    media.addEventListener('pointerenter', mouseEnter);
    media.addEventListener('pointerleave', () => controller.stopPreview());
    stage.addEventListener('pointerdown', event => {
      if (event.pointerType === 'mouse' || !event.isPrimary || (touchStart && touchStart.id !== event.pointerId)) return;
      touchStart = {id: event.pointerId, x: event.clientX, y: event.clientY};
      longPressed = false;
      clearTimeout(holdTimer);
      holdTimer = setTimeout(() => { longPressed = true; manual = false; start(); }, 400);
    });
    stage.addEventListener('pointermove', event => {
      if (touchStart && Math.hypot(event.clientX - touchStart.x, event.clientY - touchStart.y) > 12) { suppressClickUntil = Date.now() + 700; clearTimeout(holdTimer); controller.stopPreview(); }
    });
    stage.addEventListener('pointerup', event => {
      if (event.pointerType !== 'mouse') {
        clearTimeout(holdTimer);
        if (longPressed) suppressClickUntil = Date.now() + 700;
        controller.stopPreview();
      }
    });
    stage.addEventListener('pointercancel', () => { clearTimeout(holdTimer); suppressClickUntil = Date.now() + 700; controller.stopPreview(); });
    function togglePlayback() {
      manual = true;
      if (wanted || !video.paused) stop(); else start();
    }
    stage.addEventListener('click', () => { if (Date.now() >= suppressClickUntil) togglePlayback(); });
    stage.addEventListener('contextmenu', event => event.preventDefault());
    stage.addEventListener('keydown', event => {
      if (event.key === ' ' || event.key === 'Enter') { event.preventDefault(); if (!event.repeat) togglePlayback(); }
      if (event.key === 'Escape') stop();
    });
    stage.addEventListener('keyup', event => { if (event.key === ' ' || event.key === 'Enter') event.preventDefault(); });
    stage.addEventListener('blur', event => { if (!media.contains(event.relatedTarget)) controller.stopPreview(); });
    return article;
  }
  const observer = new IntersectionObserver(changes => {
    for (const change of changes) {
      const index = [...grid.children].indexOf(change.target);
      if (controllers[index]) {
        if (change.isIntersecting) controllers[index].prepare();
        else controllers[index].stopPreview();
      }
    }
  });
  function render() {
    if (viewer.open) viewer.close();
    observer.disconnect();
    controllers.splice(0).forEach(controller => controller.destroy());
    grid.replaceChildren();
    if (!entries.length && !preview) {
      grid.append(text('div', 'video-empty', '零碎的日常，也值得被记住。影像即将抵达。'));
      return;
    }
    const list = entries.length ? entries : [
      {title: '海风经过', description: '一段视频，一帧日常。', location: '大连 · 海边', poster: 'assets/images/travel-9.jpg'},
      {title: '沿途一刻', description: '给走过的风景，留一点时间。', location: '旅途中', poster: 'assets/images/hero-ink-bg.jpg'}
    ];
    list.forEach(item => { const node = card(item); grid.append(node); observer.observe(node); });
  }
  function stopAll() { controllers.forEach(controller => controller.stop()); }
  document.addEventListener('visibilitychange', () => { if (document.hidden) stopAll(); });
  window.addEventListener('blur', stopAll);
  window.addEventListener('pointerup', event => { if (event.pointerType !== 'mouse') controllers.forEach(controller => controller.stopPreview()); });
  window.addEventListener('pointercancel', () => controllers.forEach(controller => controller.stopPreview()));
  new MutationObserver(() => { if (!panel.classList.contains('active')) stopAll(); }).observe(panel, {attributes:true, attributeFilter:['class']});
  if (preview) {
    const tools = document.getElementById('video-preview-tools');
    tools.hidden = false;
    tools.className = 'video-preview-tools';
    tools.innerHTML = `<p>本地试映 · 下方为版式示例，可选择自己的视频体验播放。所选文件不会上传，刷新后清除。</p>
      <form class="video-preview-fields">
        <label>名字<input name="title" placeholder="给这段日常起个名字" maxlength="100"></label>
        <label>简介<input name="description" placeholder="记下这一刻" maxlength="500"></label>
        <label>地点<input name="location" placeholder="城市 · 地点" maxlength="100"></label>
        <label class="video-file-label">视频<input name="file" type="file" accept="video/*" required></label>
        <button type="submit">加入试映</button>
      </form><p class="video-preview-note" role="status"></p>`;
    tools.querySelector('form').addEventListener('submit', event => {
      event.preventDefault();
      const form = event.currentTarget;
      const file = form.elements.file.files[0];
      if (!file) return;
      const src = URL.createObjectURL(file);
      localUrls.push(src);
      entries.push({title: form.elements.title.value.trim() || file.name.replace(/\.[^.]+$/, ''), description: form.elements.description.value.trim(), location: form.elements.location.value.trim(), src});
      render();
      tools.querySelector('[role="status"]').textContent = `已加入「${entries[entries.length - 1].title}」，可悬停或长按试播。`;
      form.reset();
    });
  }
  render();
  if (location.hash === '#moments') document.querySelector('[data-tab="photos"]').click();
  window.addEventListener('pagehide', () => { stopAll(); });
  window.addEventListener('unload', () => localUrls.forEach(url => URL.revokeObjectURL(url)));
})();
