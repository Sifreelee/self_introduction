// 在真实 Chromium 触控环境中同时运行网页与 App 注入脚本。
const fs = require('fs'), path = require('path'), assert = require('assert');
const {spawn} = require('child_process');
const root = path.resolve(__dirname, '../..');
const work = fs.mkdtempSync(path.join(root, 'android-app/.gradle-temp/gesture-'));
const java = fs.readFileSync(path.join(root, 'android-app/app/src/main/java/com/sifreelee/intro/MainActivity.java'), 'utf8');
function injected(name) {
  const block = java.split('private static final String ' + name + ' =')[1];
  let result = '';
  for (const line of block.split('\n')) {
    const match = line.match(/^\s*(?:\+\s*)?("(?:[^"\\]|\\.)*")\s*(;)?\s*$/);
    if (!match) continue;
    result += JSON.parse(match[1]);
    if (match[2]) return result;
  }
  throw Error('Cannot extract ' + name);
}
const delay = ms => new Promise(resolve => setTimeout(resolve, ms));
let browser, socket, seq = 0;
const pending = new Map(), errors = [];
async function until(fn) { for (let i=0;i<100;i++) {if(await fn()) return;await delay(100);}throw Error('Timed out'); }
function send(method, params={}) { return new Promise((resolve,reject)=>{const id=++seq;const t=setTimeout(()=>reject(Error(method+' timed out')),15000);pending.set(id,{resolve:r=>{clearTimeout(t);resolve(r)},reject});socket.send(JSON.stringify({id,method,params}));}); }
async function evaluate(expression) {const r=await send('Runtime.evaluate',{expression,awaitPromise:true,returnByValue:true});if(r.exceptionDetails)throw Error(JSON.stringify(r.exceptionDetails));return r.result.value;}
async function touch(type, p) {await send('Input.dispatchTouchEvent',{type,touchPoints:type==='touchEnd'?[]:[{x:p.x,y:p.y}]});}
async function center(selector) {return evaluate(`(()=>{const r=document.querySelector(${JSON.stringify(selector)}).getBoundingClientRect();return {x:r.x+r.width/2,y:r.y+r.height/2}})()`);}
(async()=>{
 const profile=path.join(work,'profile');
 browser=spawn('C:/Program Files/Google/Chrome/Application/chrome.exe',['--headless=new','--no-sandbox','--disable-features=RendererCodeIntegrity','--disable-gpu','--no-first-run','--disable-crash-reporter','--disable-breakpad','--user-data-dir='+profile,'--disk-cache-dir='+path.join(work,'cache'),'--remote-debugging-port=0','about:blank'],{windowsHide:true,stdio:'ignore',env:{...process.env,TEMP:work,TMP:work,LOCALAPPDATA:work}});
 const portFile=path.join(profile,'DevToolsActivePort');await until(()=>fs.existsSync(portFile));
 const port=fs.readFileSync(portFile,'utf8').split('\n')[0];const pages=await(await fetch('http://127.0.0.1:'+port+'/json/list')).json();
 socket=new WebSocket(pages.find(p=>p.type==='page').webSocketDebuggerUrl);await new Promise((resolve,reject)=>{socket.addEventListener('open',resolve,{once:true});socket.addEventListener('error',reject,{once:true});});
 socket.addEventListener('message',event=>{const m=JSON.parse(event.data);if(m.method==='Runtime.exceptionThrown')errors.push(m.params.exceptionDetails);const p=pending.get(m.id);if(!p)return;pending.delete(m.id);m.error?p.reject(Error(JSON.stringify(m.error))):p.resolve(m.result);});
 await send('Page.enable');await send('Runtime.enable');await send('Emulation.setDeviceMetricsOverride',{width:390,height:844,deviceScaleFactor:1,mobile:true});await send('Emulation.setTouchEmulationEnabled',{enabled:true,maxTouchPoints:1});
 await send('Page.navigate',{url:process.env.LOCAL_SITE_URL||'http://127.0.0.1:59542/#moments'});await until(()=>evaluate(`!!document.querySelector('.video-stage')`));
 await evaluate(`window.bridgeCalls={settings:0,blank:0,image:0};window.AndroidBridge={onSettings(){bridgeCalls.settings++},onBlank(){bridgeCalls.blank++},onAlbumImage(){bridgeCalls.image++}}`);
 await evaluate(injected('INTERACT_JS'));await evaluate(injected('SETTINGS_BTN_JS'));
 await evaluate(`document.getElementById('moments').scrollIntoView({block:'start',behavior:'instant'});window.scrollBy(0,-90);const blank=document.createElement('div');blank.id='blank-check';Object.assign(blank.style,{position:'fixed',top:'90px',left:'0px',width:'70px',height:'70px',zIndex:1000});document.body.append(blank)`);await delay(500);
 let p=await center('#blank-check');await touch('touchStart',p);await delay(800);await touch('touchEnd',p);assert.deepEqual(await evaluate('bridgeCalls'),{settings:0,blank:0,image:0},'Blank hold must do nothing');await evaluate(`document.getElementById('blank-check').remove()`);
 p=await center('.video-stage');await touch('touchStart',p);await delay(800);assert(await evaluate(`!document.querySelector('.video-stage video').paused`),'Hold plays video with App script injected');assert.deepEqual(await evaluate('bridgeCalls'),{settings:0,blank:0,image:0});await touch('touchEnd',p);await delay(100);assert(await evaluate(`document.querySelector('.video-stage video').paused`),'Release pauses preview');
 await delay(750);await touch('touchStart',p);await delay(60);await touch('touchEnd',p);await delay(100);assert(await evaluate(`!document.querySelector('.video-stage video').paused`));await touch('touchStart',p);await delay(60);await touch('touchEnd',p);await delay(100);assert(await evaluate(`document.querySelector('.video-stage video').paused`));
 await touch('touchStart',p);await delay(800);assert(await evaluate(`!document.querySelector('.video-stage video').paused`),'Long hold also works after manual pause');await touch('touchEnd',p);await delay(100);assert(await evaluate(`document.querySelector('.video-stage video').paused`));
 await evaluate(`document.getElementById('lx-settings-btn').click()`);assert.equal(await evaluate('bridgeCalls.settings'),1);assert.equal(await evaluate('bridgeCalls.blank'),0);assert.equal(await evaluate('bridgeCalls.image'),0);
 assert.equal(errors.length,0,JSON.stringify(errors));
 console.log('PASS: App injection leaves blank holds alone; native touch hold/release, tap/pause/hold replay work; only Settings click opens settings.');
})().catch(error=>{console.error(error);process.exitCode=1}).finally(()=>{if(socket)socket.close();if(browser)browser.kill();});
