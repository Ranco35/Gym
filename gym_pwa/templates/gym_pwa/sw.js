// Service Worker para GymWorl PWA - v{{ version }}
const CACHE_NAME = 'gymworl-cache-v{{ version }}';

// Recursos que se cachearán al instalar el Service Worker
const INITIAL_CACHE_URLS = [
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
    caches.open(CACHE_NAME)
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
            if (cacheName !== CACHE_NAME) {
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
  // Ignorar solicitudes de API y administrador
  if (event.request.url.includes('/api/') || 
      event.request.url.includes('/admin/')) {
    return;
  }
  
  // Estrategia "Network First" para todas las demás solicitudes
  event.respondWith(
    fetch(event.request)
      .then(response => {
        // Almacenar en caché la respuesta exitosa
        if (response && response.status === 200) {
          const responseClone = response.clone();
          caches.open(CACHE_NAME).then(cache => {
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