/* Gov Awareness — Service Worker */
const CACHE_NAME = "gov-awareness-v1";
const STATIC_ASSETS = [
  "/",
  "/index.html",
  "/static/js/main.chunk.js",
  "/static/js/bundle.js",
  "/manifest.json",
  "/icons/icon-192.png",
  "/icons/icon-512.png"
];

/* Install: pre-cache shell */
self.addEventListener("install", event => {
  event.waitUntil(
    caches.open(CACHE_NAME).then(cache => {
      return cache.addAll(STATIC_ASSETS.map(url => {
        return new Request(url, { cache: "reload" });
      })).catch(() => {});
    })
  );
  self.skipWaiting();
});

/* Activate: clean up old caches */
self.addEventListener("activate", event => {
  event.waitUntil(
    caches.keys().then(keys =>
      Promise.all(
        keys.filter(k => k !== CACHE_NAME).map(k => caches.delete(k))
      )
    )
  );
  self.clients.claim();
});

/* Fetch: network-first for API, cache-first for assets */
self.addEventListener("fetch", event => {
  const { request } = event;
  const url = new URL(request.url);

  /* Skip non-GET and cross-origin API calls */
  if (request.method !== "GET") return;
  if (url.pathname.startsWith("/scheme_match") ||
      url.pathname.startsWith("/legal_advisory") ||
      url.pathname.startsWith("/scheme_directory")) return;

  /* For same-origin requests: network-first with cache fallback */
  if (url.origin === self.location.origin) {
    event.respondWith(
      fetch(request)
        .then(response => {
          if (response && response.status === 200 && response.type === "basic") {
            const clone = response.clone();
            caches.open(CACHE_NAME).then(cache => cache.put(request, clone));
          }
          return response;
        })
        .catch(() => caches.match(request).then(r => r || caches.match("/")))
    );
  }
});

/* Push notifications (future-ready) */
self.addEventListener("push", event => {
  const data = event.data?.json() || {};
  event.waitUntil(
    self.registration.showNotification(data.title || "Gov Awareness", {
      body: data.body || "New government schemes available for you.",
      icon: "/icons/icon-192.png",
      badge: "/icons/icon-96.png"
    })
  );
});
