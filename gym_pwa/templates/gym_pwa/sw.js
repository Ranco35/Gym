// Service Worker para GymWorl PWA - v{{ version }}
// Versión optimizada para uso con DigitalOcean Spaces

const CACHE_NAME = 'gymworl-cache-v{{ version }}';
const STATIC_CACHE = 'gymworl-static-v{{ version }}';
const DYNAMIC_CACHE = 'gymworl-dynamic-v{{ version }}';
const API_CACHE = 'gymworl-api-v{{ version }}';

// Recursos que se cachearán al instalar el Service Worker
const INITIAL_CACHE_URLS = [
  '/pwa/',
  '/pwa/offline/',
  '/static/gym_pwa/css/pwa-styles.css',
  '/static/gym_pwa/js/pwa-scripts.js',
  '/static/gym_pwa/img/logo.png',
  '/static/gym_pwa/img/icons/favicon.ico',
  '/static/gym_pwa/img/icons/icon-72x72.png',
  '/static/gym_pwa/img/icons/icon-96x96.png',
  '/static/gym_pwa/img/icons/icon-128x128.png',
  '/static/gym_pwa/img/icons/icon-144x144.png',
  '/static/gym_pwa/img/icons/icon-152x152.png',
  '/static/gym_pwa/img/icons/icon-192x192.png',
  '/static/gym_pwa/img/icons/icon-384x384.png',
  '/static/gym_pwa/img/icons/icon-512x512.png',
  'https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css',
  'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.1/css/all.min.css',
  'https://code.jquery.com/jquery-3.5.1.slim.min.js',
  'https://cdn.jsdelivr.net/npm/@popperjs/core@2.5.4/dist/umd/popper.min.js',
  'https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/js/bootstrap.min.js'
];

// Instalación del Service Worker
self.addEventListener('install', event => {
  console.log('[Service Worker] Instalando Service Worker');

  event.waitUntil(
    caches.open(STATIC_CACHE)
      .then(cache => {
        console.log('[Service Worker] Precacheando archivos');
        return cache.addAll(INITIAL_CACHE_URLS);
      })
      .then(() => {
        console.log('[Service Worker] Instalación completada');
        return self.skipWaiting();
      })
  );
});

// Activación del Service Worker
self.addEventListener('activate', event => {
  console.log('[Service Worker] Activando nuevo Service Worker');

  // Eliminar cachés antiguos
  event.waitUntil(
    caches.keys()
      .then(cacheNames => {
        return Promise.all(
          cacheNames.map(cacheName => {
            if (
              cacheName !== STATIC_CACHE &&
              cacheName !== DYNAMIC_CACHE &&
              cacheName !== API_CACHE
            ) {
              console.log('[Service Worker] Eliminando caché antigua:', cacheName);
              return caches.delete(cacheName);
            }
          })
        );
      })
      .then(() => {
        console.log('[Service Worker] Activación completada');
        return self.clients.claim();
      })
  );
});

// Interceptar las peticiones de red
self.addEventListener('fetch', event => {
  const url = new URL(event.request.url);
  
  // No interceptar peticiones a DigitalOcean Spaces
  if (event.request.url.includes('nyc3.digitaloceanspaces.com')) {
    console.log('[Service Worker] Pasando petición a DigitalOcean Spaces:', event.request.url);
    return;
  }
  
  // Ignorar solicitudes de API y administrador
  if (event.request.url.includes('/api/') || 
      event.request.url.includes('/admin/')) {
    return;
  }
  
  // Estrategia para recursos estáticos: Cache first, luego network
  if (
    INITIAL_CACHE_URLS.includes(url.pathname) ||
    event.request.url.includes('/static/') ||
    event.request.url.includes('.css') ||
    event.request.url.includes('.js') ||
    event.request.url.includes('.png') ||
    event.request.url.includes('.jpg') ||
    event.request.url.includes('.webp') ||
    event.request.url.includes('.ico')
  ) {
    event.respondWith(
      caches.match(event.request)
        .then(cachedResponse => {
          if (cachedResponse) {
            return cachedResponse;
          }
          
          return fetch(event.request)
            .then(response => {
              if (!response || response.status !== 200 || response.type !== 'basic') {
                return response;
              }
              
              const responseClone = response.clone();
              caches.open(STATIC_CACHE).then(cache => {
                cache.put(event.request, responseClone);
              });
              
              return response;
            });
        })
    );
    return;
  }
  
  // Estrategia "Network First" para todas las demás solicitudes
  event.respondWith(
    fetch(event.request)
      .then(response => {
        // Almacenar en caché la respuesta exitosa
        if (response && response.status === 200) {
          const responseClone = response.clone();
          caches.open(DYNAMIC_CACHE).then(cache => {
            cache.put(event.request, responseClone);
          });
        }
        return response;
      })
      .catch(() => {
        // Si la solicitud falla, intentar obtenerla de la caché
        return caches.match(event.request)
          .then(cachedResponse => {
            if (cachedResponse) {
              return cachedResponse;
            }

            // Si no está en caché, verificar si es una solicitud de página
            if (event.request.mode === 'navigate') {
              return caches.match('/pwa/offline/');
            }

            // Si no es ninguno de los anteriores, devolver un error
            return new Response('Not found', {
              status: 404,
              statusText: 'Not found'
            });
          });
      })
  );
});
