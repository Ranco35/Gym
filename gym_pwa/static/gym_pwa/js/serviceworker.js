/**
 * Service Worker para la PWA de GymWorl
 * Versión optimizada para uso con DigitalOcean Spaces
 */

const CACHE_NAME = 'gymworl-pwa-v2';
const STATIC_CACHE = 'gymworl-static-v2';
const DYNAMIC_CACHE = 'gymworl-dynamic-v2';
const API_CACHE = 'gymworl-api-v2';

// Recursos que se cachearán en la instalación
const STATIC_ASSETS = [
    '/pwa/',
    '/pwa/static/gym_pwa/css/pwa-styles.css',
    '/pwa/static/gym_pwa/js/pwa-base.js',
    '/pwa/static/gym_pwa/js/pwa-scripts.js',
    '/pwa/static/gym_pwa/icons/default-exercise.png',
    '/pwa/static/gym_pwa/icons/icon-192x192.png',
    '/pwa/static/gym_pwa/icons/icon-512x512.png',
    '/manifest.json',
    '/static/gym_pwa/img/no-image.png',
    'https://code.jquery.com/jquery-3.5.1.slim.min.js',
    'https://cdn.jsdelivr.net/npm/@popperjs/core@2.5.4/dist/umd/popper.min.js',
    'https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/js/bootstrap.min.js',
    'https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css',
    'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.1/css/all.min.css'
];

// Instalación del Service Worker
self.addEventListener('install', event => {
    console.log('Service Worker: Instalando...');
    
    // Precaching de recursos estáticos
    event.waitUntil(
        caches.open(STATIC_CACHE)
            .then(cache => {
                console.log('Service Worker: Cacheando archivos estáticos');
                return cache.addAll(STATIC_ASSETS);
            })
            .then(() => self.skipWaiting())
    );
});

// Activación del Service Worker
self.addEventListener('activate', event => {
    console.log('Service Worker: Activado');
    
    // Limpiar caches antiguas
    event.waitUntil(
        caches.keys().then(cacheNames => {
            return Promise.all(
                cacheNames.map(cache => {
                    if (
                        cache !== STATIC_CACHE && 
                        cache !== DYNAMIC_CACHE && 
                        cache !== API_CACHE
                    ) {
                        console.log('Service Worker: Limpiando cache antigua:', cache);
                        return caches.delete(cache);
                    }
                })
            );
        }).then(() => {
            console.log('Service Worker: Caches limpias y listo para controlar la aplicación');
            return self.clients.claim();
        })
    );
});

// Interceptar peticiones fetch
self.addEventListener('fetch', event => {
    const url = new URL(event.request.url);
    
    // No interceptar peticiones a DigitalOcean Spaces
    if (event.request.url.includes('nyc3.digitaloceanspaces.com')) {
        console.log('Service Worker: Pasando petición a DigitalOcean Spaces:', event.request.url);
        return;
    }
    
    // No interceptar peticiones de API para sincronización
    if (event.request.url.includes('/api/sync/')) {
        return;
    }
    
    // Estrategia para peticiones de API: Network first, luego cache
    if (event.request.url.includes('/api/')) {
        event.respondWith(
            fetch(event.request)
                .then(response => {
                    const responseClone = response.clone();
                    caches.open(API_CACHE).then(cache => {
                        cache.put(event.request, responseClone);
                    });
                    return response;
                })
                .catch(() => {
                    return caches.match(event.request);
                })
        );
        return;
    }
    
    // Estrategia para recursos estáticos: Cache first, luego network
    if (
        STATIC_ASSETS.includes(url.pathname) ||
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
    
    // Estrategia para páginas HTML: Network first con timeout, luego cache
    if (event.request.headers.get('accept').includes('text/html')) {
        event.respondWith(
            fetch(event.request)
                .then(response => {
                    // Guardar en caché dinámica
                    const responseClone = response.clone();
                    caches.open(DYNAMIC_CACHE).then(cache => {
                        cache.put(event.request, responseClone);
                    });
                    
                    return response;
                })
                .catch(() => {
                    return caches.match(event.request)
                        .then(cachedResponse => {
                            if (cachedResponse) {
                                return cachedResponse;
                            }
                            
                            // Si tampoco está en caché, mostrar página offline
                            return caches.match('/pwa/offline/');
                        });
                })
        );
        return;
    }
    
    // Estrategia por defecto: Stale-while-revalidate
    event.respondWith(
        caches.match(event.request)
            .then(cachedResponse => {
                const fetchPromise = fetch(event.request)
                    .then(networkResponse => {
                        if (networkResponse && networkResponse.status === 200) {
                            const responseClone = networkResponse.clone();
                            caches.open(DYNAMIC_CACHE).then(cache => {
                                cache.put(event.request, responseClone);
                            });
                        }
                        return networkResponse;
                    })
                    .catch(() => {
                        console.log('Service Worker: Fallo en la red para:', event.request.url);
                    });
                
                return cachedResponse || fetchPromise;
            })
    );
});

// Gestión de sincronización en segundo plano
self.addEventListener('sync', event => {
    if (event.tag === 'sync-pending-data') {
        event.waitUntil(syncPendingData());
    }
});

// Función para sincronizar datos pendientes
function syncPendingData() {
    return self.clients.matchAll()
        .then(clients => {
            if (clients && clients.length > 0) {
                // Enviar mensaje a la página web para realizar la sincronización
                clients[0].postMessage({
                    action: 'sync-data'
                });
            }
            return Promise.resolve();
        });
}

// Gestión de notificaciones push
self.addEventListener('push', event => {
    const options = {
        body: event.data ? event.data.text() : 'Nueva notificación de GymWorl',
        icon: '/pwa/static/gym_pwa/icons/icon-192x192.png',
        badge: '/pwa/static/gym_pwa/icons/badge.png',
        vibrate: [100, 50, 100],
        data: {
            url: '/pwa/'
        }
    };
    
    event.waitUntil(
        self.registration.showNotification('GymWorl', options)
    );
});

// Gestión de clicks en notificaciones
self.addEventListener('notificationclick', event => {
    event.notification.close();
    
    event.waitUntil(
        clients.matchAll({type: 'window'})
            .then(windowClients => {
                // Verificar si ya hay una ventana abierta y enfocarla
                for (let client of windowClients) {
                    if (client.url === event.notification.data.url && 'focus' in client) {
                        return client.focus();
                    }
                }
                
                // Si no hay ventana abierta, abrir una nueva
                if (clients.openWindow) {
                    return clients.openWindow(event.notification.data.url);
                }
            })
    );
});
