const assert = require('assert');
const {webcrypto} = require('crypto');
const fs = require('fs');
const path = require('path');
const {create, KEY, TTL} = require('../js/photo-admin-auth.js');

(async () => {
  let now = Date.UTC(2026, 10, 23);
  const items = new Map();
  const storage = {getItem: key => items.get(key) || null,
    setItem: (key, value) => items.set(key, value), removeItem: key => items.delete(key)};
  const options = {storage, crypto: webcrypto, now: () => now};
  const auth = create(options);
  assert(!auth.isAdmin());
  assert(!await auth.login('wrong', 'wrong'));
  assert(!await auth.login('sifree', 'wrong'));
  assert(!auth.isAdmin());
  // Inject the supplied password at execution time so the test does not store it in source.
  const password = process.env.PHOTO_ADMIN_TEST_PASSWORD;
  assert(password, 'Set PHOTO_ADMIN_TEST_PASSWORD to run the credential test');
  assert(await auth.login('sifree', password));
  assert(auth.isAdmin());
  const expires = auth.expiresAt();
  assert.equal(expires, now + TTL);
  assert(!items.get(KEY).includes(password));
  assert(create(options).isAdmin(), 'refresh/app restart retains login');
  const validRecord = items.get(KEY);
  items.set(KEY, '{corrupt-session');
  assert(!auth.isAdmin(), 'corrupt storage revokes an already active session');
  items.set(KEY, validRecord);
  assert(auth.isAdmin());
  now += TTL - 1;
  assert(auth.isAdmin());
  assert.equal(auth.expiresAt(), expires, 'browsing must not extend the 30-day deadline');
  now++;
  assert(!auth.isAdmin(), 'expires exactly at 30 days');
  assert(!create(options).isAdmin());
  assert(await auth.login('sifree', password));
  const secondTab = create(options);
  assert(secondTab.isAdmin());
  auth.logout();
  assert(!secondTab.isAdmin(), 'logout propagates to another tab');
  assert(!create(options).isAdmin());
  items.set(KEY, '{invalid json');
  assert(!auth.isAdmin());
  items.set(KEY, JSON.stringify({version: 1, user: 'sifree', issuedAt: now, expiresAt: now + TTL * 2}));
  assert(!auth.isAdmin(), 'reject malformed validity period');
  const ephemeral = create({...options, storage: null});
  assert(await ephemeral.login('sifree', password));
  assert(ephemeral.isAdmin());
  assert(!ephemeral.persistent());
  ephemeral.logout();
  assert(!ephemeral.isAdmin());
  const pending = auth.login('sifree', password);
  auth.logout();
  assert(!await pending, 'cancel pending login');
  assert(!auth.isAdmin());
  console.log('Admin auth: credentials, refresh, fixed 30-day expiry, logout, cross-tab logout, corrupt storage, storage unavailable and cancelled login passed.');

  const html = fs.readFileSync(path.join(__dirname, '../index.html'), 'utf8');
  const ui = fs.readFileSync(path.join(__dirname, '../js/photo-admin.js'), 'utf8');
  const ids = new Set([...html.matchAll(/\bid="([^"]+)"/g)].map(m => m[1]));
  const native = fs.readFileSync(path.join(__dirname, '../android-app/app/src/main/java/com/sifreelee/intro/MainActivity.java'), 'utf8');
  for (const match of native.matchAll(/\.id='([^']+)'/g)) ids.add(match[1]);
  for (const match of ui.matchAll(/getElementById\('([^']+)'\)/g)) {
    assert(ids.has(match[1]), 'Missing actual HTML element: ' + match[1]);
  }
  console.log('Admin UI: all controls match actual page elements.');
})().catch(error => { console.error(error); process.exitCode = 1; });
