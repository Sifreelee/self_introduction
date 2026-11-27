/* 独立动效层：删除本文件与 motion.css 的引用即可回到原版。 */
(() => {
  'use strict';
  const root = document.documentElement;
  const reduced = window.matchMedia('(prefers-reduced-motion: reduce)');
  let timer;
  let visible = false;
  let holding = false;
  let busy = false;
  let current = 0;
  const host = document.getElementById('recent-glance');
  const paper = host && host.querySelector('.glance-paper');
  const frame = paper && paper.querySelector('.glance-image');
  const initial = frame && frame.querySelector('img');
  const pick = (window.JOURNEY_CONFIG || {}).recent || {};
  const group = SITE_DATA.photos.find(g => g.city === pick.album);
  const slides = [];
  if (initial) {
    slides.push({ src: initial.getAttribute('src'), title: initial.alt });
    for (const photo of (group && group.photos || [])) {
      if (photo.src && !slides.some(s => s.src === photo.src)) slides.push({ src: photo.src, title: photo.title || group.city });
      if (slides.length >= 4) break;
    }
  }
  let count, next;
  function automatic() { return !reduced.matches && !document.hidden && visible && !holding; }
  function schedule() {
    clearTimeout(timer);
    if (automatic() && slides.length > 1 && !busy) timer = setTimeout(() => changeSlide((current + 1) % slides.length, false), 6500);
  }
  function sync() {
    root.classList.toggle('motion-paused', reduced.matches);
    root.classList.toggle('motion-sleeping', document.hidden);
    schedule();
  }
  reduced.addEventListener('change', sync);
  document.addEventListener('visibilitychange', sync);

  async function changeSlide(index, manual) {
    clearTimeout(timer);
    if (busy || (!manual && !automatic())) return;
    busy = true;
    next.disabled = true;
    const incoming = new Image();
    incoming.alt = slides[index].title;
    incoming.className = 'is-incoming';
    incoming.decoding = 'async';
    incoming.src = slides[index].src;
    try {
      await incoming.decode();
      // 等待图片期间可能滚出视口或暂停；不再自动换图。
      if (!manual && !automatic()) return;
      const previous = frame.querySelector('img.is-current');
      frame.appendChild(incoming);
      // 先让新图以透明状态进入渲染，再开始交叉淡入。
      await new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve)));
      incoming.classList.add('is-current');
      if (previous) previous.classList.remove('is-current');
      current = index;
      paper.querySelector('.glance-caption h3').textContent = slides[index].title;
      count.textContent = `流动的明信片 · ${current + 1} / ${slides.length}`;
      await new Promise(resolve => setTimeout(resolve, reduced.matches ? 0 : 1450));
      if (previous) previous.remove();
      incoming.classList.remove('is-incoming');
    } catch (_) {
      incoming.remove();
      // 失败的图片不参与后续循环，保留当前图片及相册入口。
      slides.splice(index, 1);
      if (index < current) current--;
      count.textContent = `流动的明信片 · ${current + 1} / ${slides.length}`;
    } finally {
      busy = false;
      next.disabled = slides.length < 2;
      schedule();
    }
  }
  if (initial && slides.length > 1) {
    frame.classList.add('motion-postcard');
    initial.classList.add('is-current');
    const controls = document.createElement('div');
    controls.className = 'postcard-controls';
    count = document.createElement('span');
    count.textContent = `流动的明信片 · 1 / ${slides.length}`;
    next = document.createElement('button');
    next.type = 'button';
    next.className = 'postcard-control';
    next.textContent = '换一张';
    next.setAttribute('aria-label', '查看下一张精选相册照片');
    next.addEventListener('click', () => changeSlide((current + 1) % slides.length, true));
    controls.append(count, next);
    host.querySelector('.curated-intro').appendChild(controls);
    function hold(value) { holding = value; frame.classList.toggle('postcard-hold', value); schedule(); }
    paper.addEventListener('mouseenter', () => hold(true));
    paper.addEventListener('mouseleave', () => hold(paper.contains(document.activeElement)));
    paper.addEventListener('focusin', () => hold(true));
    paper.addEventListener('focusout', e => hold(paper.contains(e.relatedTarget)));
  }
  if ('IntersectionObserver' in window) {
    const observer = new IntersectionObserver(entries => {
      for (const entry of entries) {
        entry.target.classList.toggle('motion-outside', !entry.isIntersecting);
        if (entry.target === host) visible = entry.isIntersecting;
      }
      schedule();
    });
    [document.getElementById('hero'), host, ...document.querySelectorAll('.sec-cloud-layer')].filter(Boolean).forEach(el => observer.observe(el));
  } else { visible = true; }
  sync();
})();
