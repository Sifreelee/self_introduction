// 使用真实 renderPhotos 验证空相册、自选封面及原有相册均能渲染。
const fs = require('fs');
const vm = require('vm');
const assert = require('assert');
const source = fs.readFileSync(require('path').join(__dirname, '../js/main.js'), 'utf8');
const render = source.slice(source.indexOf('function renderPhotos()'), source.indexOf('function renderSocial()'));
const box = {innerHTML: '', querySelectorAll: () => []};
const context = {
  SITE_DATA: {photos: [
    {city: '新建空相册', photos: []},
    {city: '只有封面', cover: 'assets/images/封面.jpg', photos: []},
    {city: '原有相册', photos: [{src: 'assets/images/原图.jpg', title: '原图'}]}
  ]},
  $: () => box, photoQuery: '', pageState: {photos: 1}, PAGE_SIZE: {photos: 9},
  setSearchHint: () => {}, paginationHTML: () => '', esc: s => String(s),
  hitHTML: s => s, starHTML: () => '', sealHTML: () => '', bindPagination: () => {},
  bindImgFallback: () => {}, shotName: p => p.title, emptyTip: s => s
};
vm.createContext(context);
vm.runInContext(render + '\nrenderPhotos();', context);
assert(box.innerHTML.includes('新建空相册'));
assert(box.innerHTML.includes('待添新影'));
assert(box.innerHTML.includes('assets/images/封面.jpg'));
assert(box.innerHTML.includes('原有相册'));
assert.equal((box.innerHTML.match(/class="photo-wrap/g) || []).length, 3);
context.photoQuery = '新建空相册';
vm.runInContext('renderPhotos();', context);
assert(box.innerHTML.includes('新建空相册'));
assert(!box.innerHTML.includes('原有相册'));
console.log('Website: empty albums, chosen covers, existing albums and search passed.');
