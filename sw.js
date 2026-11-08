// Build Hub service worker: network first, cached copy when offline.
var C = 'bh-202611080403';
var CDN = /^https:\/\/(cdn\.jsdelivr\.net|cdnjs\.cloudflare\.com|fonts\.googleapis\.com|fonts\.gstatic\.com)\//;
self.addEventListener('install', function (e) { self.skipWaiting(); e.waitUntil(caches.open(C).then(function (c) { return c.addAll(['./', 'icon-192.png']); })); });
self.addEventListener('activate', function (e) { e.waitUntil(caches.keys().then(function (k) { return Promise.all(k.filter(function (n) { return n !== C; }).map(function (n) { return caches.delete(n); })); }).then(function () { return self.clients.claim(); })); });
self.addEventListener('fetch', function (e) {
  var r = e.request, u = new URL(r.url);
  if (r.method !== 'GET' || !(u.origin === location.origin || CDN.test(r.url))) return;
  e.respondWith(fetch(r).then(function (res) { if (res.ok || res.type === 'opaque') { var cp = res.clone(); caches.open(C).then(function (c) { c.put(r, cp); }); } return res; })
    .catch(function () { return caches.match(r, { ignoreSearch: r.mode === 'navigate' }).then(function (m) { return m || caches.match('./'); }); }));
});
