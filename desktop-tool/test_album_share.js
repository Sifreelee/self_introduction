const assert = require('assert');
const fs = require('fs');
const path = require('path');
const vm = require('vm');
const root = path.join(__dirname, '..');
const source = fs.readFileSync(path.join(root, 'js/main.js'), 'utf8');
const html = fs.readFileSync(path.join(root, 'index.html'), 'utf8');
const pageIds = new Set([...html.matchAll(/\bid="([^"]+)"/g)].map(match => match[1]));
const albumName = '中国 武汉 & 江城 #1';
let opened = -1, scrolled = false, selectedPhotos = false;
const context = {
  URL, SITE_DATA: {photos: [{city: albumName}, {city: '北京'}]},
  window: {location: {href: 'https://example.com/site/?from=friend#profile'}},
  $: selector => pageIds.has(selector.slice(1))
    ? {scrollIntoView() { scrolled = true; }} : null,
  document: {querySelector: selector => selector === '#works-tabs .tab[data-tab="photos"]'
    ? {classList: {contains: () => false}, click() { selectedPhotos = true; }} : null},
  openAlbum(gi) { opened = gi; }
};
vm.createContext(context);
vm.runInContext(source.slice(source.indexOf('function getAlbumShareUrl('), source.indexOf('function renderPhotos()')), context);
const link = context.getAlbumShareUrl(0);
assert.equal(new URL(link).searchParams.get('album'), albumName);
assert.equal(new URL(link).searchParams.get('from'), 'friend');
assert(pageIds.has(new URL(link).hash.slice(1)), 'shared link anchor must exist in the actual HTML');
context.SITE_DATA.photos.reverse();
context.window.location.href = link;
context.openSharedAlbum();
assert.equal(opened, 1, 'reordering albums must preserve shared destination');
assert(scrolled);
assert(selectedPhotos, 'shared links activate the photos panel');
opened = -1;
context.window.location.href = link.replace(/#[^#]*$/, '#photos');
context.openSharedAlbum();
assert.equal(opened, 1, 'previously shared links still open the album');
opened = -1;
context.window.location.href = 'https://example.com/site/?album=missing';
context.openSharedAlbum();
assert.equal(opened, -1);

// Execute the actual Java-injected script with touch events and a native bridge stub.
const java = fs.readFileSync(path.join(root, 'android-app/app/src/main/java/com/sifreelee/intro/MainActivity.java'), 'utf8');
const block = java.slice(java.indexOf('private static final String INTERACT_JS ='), java.indexOf('private static final String COLLECT_JS ='));
const injected = [...block.matchAll(/"(?:[^"\\]|\\.)*"/g)].map(m => JSON.parse(m[0])).join('');
const handlers = {}, calls = [];
let pending;
const touch = {
  window: {AndroidBridge: {onAlbumImage: (...args) => calls.push(args), onBlank() { calls.push('blank'); }}},
  document: {addEventListener: (name, fn) => { handlers[name] = fn; }},
  URL, location: {href: 'https://example.com/site/'},
  getAlbumShareUrl: gi => `https://example.com/site/?album=${gi}#photos`,
  setTimeout(fn) { pending = fn; return 1; }, clearTimeout() { pending = null; }
};
vm.runInNewContext(injected, touch);
const card = {dataset: {gi: '2'}};
const image = {tagName: 'IMG', src: 'photo.jpg', alt: '封面', closest(selector) {
  return selector.includes('.photo-album') ? card : null;
}};
function press(target) {
  handlers.touchstart({touches: [{clientX: 0, clientY: 0}], target});
  pending();
}
press(image);
assert.equal(calls[0][0], 'https://example.com/site/photo.jpg');
assert.equal(calls[0][3], 'https://example.com/site/?album=2#photos');
let prevented = false;
handlers.click({preventDefault() { prevented = true; }, stopImmediatePropagation() {}});
assert(prevented, 'long press must not also open the album');
const count = calls.length;
handlers.touchstart({touches: [{clientX: 0, clientY: 0}], target: image});
handlers.touchmove({touches: [{clientX: 0, clientY: 30}]});
assert.equal(pending, null, 'scrolling cancels long press');
assert.equal(calls.length, count);
press({tagName: 'SPAN', closest: selector => selector.includes('.photo-album') ? card : null});
assert.equal(calls.at(-1)[0], '', 'empty albums have no image to save');
assert.equal(calls.at(-1)[3], 'https://example.com/site/?album=2#photos');
press({tagName: 'IMG', src: 'thumb.jpg', closest: selector => selector.includes('#album-browser') ? {dataset: {albumUrl: link}} : null});
assert.equal(calls.at(-1)[3], link, 'album thumbnails retain their album link');
press({tagName: 'P', closest: selector => selector.includes('p,h1') ? {} : null});
assert.notEqual(calls.at(-1), 'blank', 'text long press keeps native text selection');
console.log('Album sharing: encoded names, reorder, missing album, cover/thumbnail/empty album, gesture cancellation and text selection passed.');
