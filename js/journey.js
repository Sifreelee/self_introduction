(function () {
  const config = window.JOURNEY_CONFIG || {};
  function cover(group) { return group.cover || ((group.photos || [])[0] || {}).src || ''; }
  function albumLink(gi) {
    closeCityMap();
    openAlbum(gi);
  }
  function renderRecent() {
    const host = document.getElementById('recent-glance');
    const pick = config.recent || {};
    let gi = SITE_DATA.photos.findIndex(group => group.city === pick.album);
    if (gi < 0) gi = SITE_DATA.photos.findIndex(group => cover(group));
    if (gi < 0) { host.hidden = true; return; }
    const group = SITE_DATA.photos[gi];
    const image = pick.album === group.city && pick.src ? pick.src : cover(group);
    if (!image) { host.hidden = true; return; }
    host.innerHTML = `<div class="curated-intro"><span class="curated-eyebrow">光影手记 · 私藏一页</span><h2>荔荔精选</h2><p>${esc(pick.note || '留住一眼风景，也留住走过的时光。')}</p><span class="curated-location">此刻翻到 · ${esc(group.city)}</span><span class="glance-footnote">以影存真 · 以行记日</span></div>
      <a class="glance-paper" data-album-url="${esc(getAlbumShareUrl(gi))}" href="${esc(getAlbumShareUrl(gi))}">
        <div class="glance-image"><img src="${esc(image)}" alt="${esc(pick.title || group.city)}" loading="lazy"><span class="glance-seal">精选</span></div>
        <div class="glance-caption"><h3>${esc(pick.title || group.city)}</h3><span>${esc(group.city)}</span></div>
        <span class="glance-open">翻开这本相册</span>
      </a>`;
    host.querySelector('a').addEventListener('click', e => {
      if (e.ctrlKey || e.metaKey || e.shiftKey || e.altKey) return;
      e.preventDefault(); openAlbum(gi);
    });
    bindImgFallback(host.querySelector('img'), cover(group));
  }
  function cityAlbums(city, forPhotos = false) {
    const explicit = (config.cityAlbums || {})[city] || [];
    return SITE_DATA.photos.map((group, gi) => ({group, gi})).filter(({group}) =>
      forPhotos && Object.prototype.hasOwnProperty.call(config.cityAlbums || {}, city) ? explicit.includes(group.city) : explicit.includes(group.city) || group.city.includes(city)
      || (group.cities || []).includes(city)
      || (group.photos || []).some(photo => (photo.title || '').includes(city)));
  }
  function renderMapEntry() {
    const places = (SITE_DATA.cities || []).map(parseCity);
    const lit = new Set(places.map(city => PROVINCE_ID[city.prov]).filter(Boolean));
    const entry = document.getElementById('journey-map-entry');
    entry.innerHTML = `<span class="map-entry-art" aria-hidden="true"><svg viewBox="0 0 1000 810">${Object.entries(CHINA_PROVINCES).map(([pid, province]) => `<path d="${province.d}" class="portal-province${lit.has(pid) ? ' visited' : ''}"/>`).join('')}</svg></span><span class="map-entry-copy"><span class="map-entry-kicker">把走过的地方，留在地图上</span><strong>点亮中国</strong><span class="map-entry-count">${new Set(places.map(city => city.name)).size} 座城市 · ${lit.size} 个省级行政区 · 一路拾光</span></span><span class="map-entry-action">展开行走地图</span>`;
    entry.addEventListener('click', openCityMap);
  }
  window.initMapExplorer = function () {
    const body = document.getElementById('city-map-body');
    const parsed = (SITE_DATA.cities || []).map(parseCity);
    const preview = document.createElement('section');
    preview.className = 'province-preview';
    preview.setAttribute('aria-label', '省份照片预览');
    preview.innerHTML = '<div class="province-preview-title">把鼠标移到点亮的省份，看看沿途风景</div><div class="province-samples"></div>';
    body.querySelector('.city-map-stage').after(preview);
    const chooser = document.createElement('div');
    chooser.className = 'city-album-chooser';
    chooser.hidden = true;
    body.querySelector('.city-map-list').after(chooser);
    const cache = new Map();
    const counts = {};
    parsed.forEach(city => { counts[city.prov] = (counts[city.prov] || 0) + 1; });
    const slots = Math.max(6, ...Object.values(counts));
    preview.style.setProperty('--sample-rows', Math.ceil(slots / 3));
    let currentPid = '';
    function sample(pid, force) {
      if (pid === currentPid && !force) return;
      const cities = parsed.filter(city => PROVINCE_ID[city.prov] === pid);
      if (!cities.length) return;
      currentPid = pid;
      const province = cities[0].prov;
      if (!cache.has(pid)) {
        const photos = new Map();
        cities.forEach(city => cityAlbums(city.name, true).forEach(({group, gi}) => {
          const preferred = (config.cityPhotos || {})[city.name] || [];
          const shared = (config.cityPhotoMatch || {})[city.name] === 'title' || (!group.city.includes(city.name) && !(config.cityAlbums || {})[city.name]?.includes(group.city));
          (group.photos || []).filter(photo => (!shared || (photo.title || '').includes(city.name)) && (!preferred.length || preferred.includes(photo.src))).forEach(photo => {
            if (photo.src && !photos.has(photo.src)) photos.set(photo.src, {src: photo.src, city: city.name, title: photo.title || city.name, gi});
          });
        }));
        cache.set(pid, [...photos.values()]);
      }
      const pool = cache.get(pid).slice();
      for (let i = pool.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [pool[i], pool[j]] = [pool[j], pool[i]];
      }
      const picks = [], used = new Set();
      cities.forEach(city => {
        const photo = pool.find(photo => photo.city === city.name && !used.has(photo.src));
        if (photo) { picks.push(photo); used.add(photo.src); }
        else picks.push({city: city.name, title: '照片待整理'});
      });
      preview.querySelector('.province-preview-title').innerHTML = `<strong>${esc(province)}</strong><span>${esc(cities.map(city => city.name).join(' · '))}</span>`;
      preview.querySelector('.province-samples').innerHTML = picks.map(photo => photo.src ? `<a class="province-sample" data-album="${photo.gi}" data-album-url="${esc(getAlbumShareUrl(photo.gi))}" href="${esc(getAlbumShareUrl(photo.gi))}"><span class="province-photo-city">${esc(photo.city)}</span><img src="${esc(photo.src)}" alt="${esc(photo.title)}"><span class="province-photo-title">${esc(photo.title)}</span></a>` : `<div class="province-sample sample-placeholder"><span class="province-photo-city">${esc(photo.city || '待续')}</span><span class="sample-empty-image">${esc(photo.title)}</span></div>`).join('');
      preview.querySelectorAll('[data-album]').forEach(link => link.addEventListener('click', e => {
        if (e.ctrlKey || e.metaKey || e.shiftKey || e.altKey) return;
        e.preventDefault(); albumLink(+link.dataset.album);
      }));
      focusProvince(pid, null);
    }
    function visitCity(chip) {
      const city = chip.childNodes[0].textContent.trim();
      const albums = cityAlbums(city);
      chooser.hidden = false;
      chooser.innerHTML = `<h4>${esc(city)} · ${albums.length ? `相关相册 ${albums.length} 本，请选择` : '照片还在整理'}</h4>${albums.map(({group, gi}) => `<a href="${esc(getAlbumShareUrl(gi))}" data-album="${gi}">${esc(group.city)}<small>${(group.photos || []).length} 张</small></a>`).join('')}`;
      chooser.querySelectorAll('[data-album]').forEach(link => link.addEventListener('click', e => {
        if (e.ctrlKey || e.metaKey || e.shiftKey || e.altKey) return;
        e.preventDefault(); albumLink(+link.dataset.album);
      }));
      chooser.scrollIntoView({behavior: 'smooth', block: 'nearest'});
    }
    const tip = body.querySelector('.city-map-tip');
    if (tip) tip.textContent = '悬停省份随机看照片 · 点击城市查看相关相册，自行选择进入（手机可点省份预览）';
    body.querySelectorAll('.province-fill.lit').forEach(path => {
      path.setAttribute('role', 'button'); path.setAttribute('tabindex', '0');
      const name = Object.keys(PROVINCE_ID).find(key => PROVINCE_ID[key] === path.dataset.pid);
      path.setAttribute('aria-label', '预览' + name + '的照片');
      path.addEventListener('mouseenter', () => sample(path.dataset.pid, true));
      path.addEventListener('focus', () => sample(path.dataset.pid));
      path.addEventListener('keydown', e => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); sample(path.dataset.pid, true); } });
    });
    body.onclick = e => {
      const province = e.target.closest('.province-fill.lit');
      if (province) sample(province.dataset.pid, true);
      const chip = e.target.closest('.city-chip[data-pid]');
      if (chip) visitCity(chip);
    };
    body.querySelectorAll('.city-chip[data-pid]').forEach(chip => chip.addEventListener('keydown', e => {
      if (e.key === 'Enter' || e.key === ' ') visitCity(chip);
    }));
    const first = parsed.find(city => PROVINCE_ID[city.prov]);
    if (first) sample(PROVINCE_ID[first.prov]);
  };
  renderRecent();
  renderMapEntry();
})();
