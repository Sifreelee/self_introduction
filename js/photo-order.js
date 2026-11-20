/* 同组照片按数字及中文序号排列，保留其他组和相册的手动顺序。 */
(function (root) {
  function ordinal(text) {
    if (/^\d+$/.test(text)) return Number(text);
    if (!/^[零一二三四五六七八九十百]+$/.test(text)) return 0;
    let total = 0, current = 0;
    for (const ch of text) {
      if (ch === '十' || ch === '百') {
        total += (current || 1) * (ch === '十' ? 10 : 100);
        current = 0;
      } else current = '零一二三四五六七八九'.indexOf(ch);
    }
    return total + current;
  }
  function key(photo) {
    let path = String(photo.src || '').replace(/\\/g, '/').split(/[?#]/)[0];
    try { path = decodeURIComponent(path); } catch (_) { /* 保留原路径 */ }
    const slash = path.lastIndexOf('/');
    let stem = path.slice(slash + 1).replace(/\.[^.]*$/, '');
    let number = 0;
    let match = /^(.*?)\s*其\s*([零一二三四五六七八九十百\d]+)$/.exec(stem);
    if (!match) match = /^(.*?)[ _-]*(\d+)$/.exec(stem);
    if (!match) {
      const chinese = /^(.*?)[ _-]*([零一二三四五六七八九十百]+)$/.exec(stem);
      if (chinese && chinese[1] && ordinal(chinese[2]) >= 11) match = chinese;
    }
    if (match && ordinal(match[2])) {
      stem = match[1].replace(/[ _-]+$/, '');
      number = ordinal(match[2]);
    }
    return { group: path.slice(0, slash + 1).toLowerCase() + stem.toLowerCase(), number };
  }
  function orderPhotos(photos) {
    const groups = new Map();
    photos.forEach((photo, index) => {
      const value = key(photo);
      if (!photo.src) value.group = 'missing-src-' + index;
      if (!groups.has(value.group)) groups.set(value.group, []);
      groups.get(value.group).push({ photo, index, number: value.number });
    });
    return Array.from(groups.values()).flatMap(items =>
      items.slice().sort((a, b) => a.number - b.number || a.index - b.index).map(item => item.photo));
  }
  root.orderPhotos = orderPhotos;
  if (typeof module !== 'undefined' && module.exports) module.exports = { orderPhotos };
})(typeof window !== 'undefined' ? window : globalThis);
