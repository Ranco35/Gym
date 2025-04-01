/**
 * Service Worker para la PWA de GymWorl
 */

const CACHE_NAME = 'gymworl-pwa-v1';
const STATIC_ASSETS = [
    '/',
    '/pwa/',
    '/pwa/static/gym_pwa/css/pwa-styles.css',
    '/pwa/static/gym_pwa/js/pwa-base.js',
    '/pwa/static/gym_pwa/icons/default-exercise.png',
    '/pwa/static/gym_pwa/icons/icon-192x192.png',
    '/pwa/static/gym_pwa/icons/icon-512x512.png',
    '/manifest.json'
];

// Instalación del Service Worker
self.addEventListener('install', event => {
    console.log('Service Worker: Instalando...');
    
    // Precaching de recursos estáticos
    event.waitUntil(
        caches.open(CACHE_NAME)
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
                    if (cache !== CACHE_NAME) {
                        console.log('Service Worker: Limpiando cache antigua:', cache);
                        return caches.delete(cache);
                    }
                })
            );
        })
    );
    
    return self.clients.claim();
});

// Interceptar peticiones fetch
self.addEventListener('fetch', event => {
    // No interceptar peticiones de DigitalOcean Spaces
    if (event.request.url.includes('nyc3.digitaloceanspaces.com')) {
        return;
    }
    
    // No interceptar peticiones de API para sincronización
    if (event.request.url.includes('/api/sync/')) {
        return;
    }
    
    // Para peticiones de API normales, usar estrategia "network first, cache fallback"
    if (event.request.url.includes('/api/')) {
        event.respondWith(
            fetch(event.request)
                .then(response => {
                    // Clonar la respuesta para guardarla en cache
                    const responseClone = response.clone();
                    caches.open(CACHE_NAME).then(cache => {
                        cache.put(event.request, responseClone);
                    });
                    return response;
                })
                .catch(() => {
                    // Si falla la red, intentar servir desde cache
                    return caches.match(event.request);
                })
        );
    } else {
        // Para recursos estáticos y páginas HTML, usar "cache first, network fallback"
        event.respondWith(
            caches.match(event.request)
                .then(cachedResponse => {
                    // Devolver la respuesta cacheada si existe
                    if (cachedResponse) {
                        return cachedResponse;
                    }
                    
                    // Si no existe en cache, buscar en la red
                    return fetch(event.request)
                        .then(response => {
                            // Verificar que sea una respuesta válida
                            if (!response || response.status !== 200 || response.type !== 'basic') {
                                return response;
                            }
                            
                            // Clonar la respuesta para guardarla en cache
                            const responseClone = response.clone();
                            caches.open(CACHE_NAME).then(cache => {
                                cache.put(event.request, responseClone);
                            });
                            
                            return response;
                        });
                })
        );
    }
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
        body: event.data.text() || 'Nueva notificación',
        icon: '/pwa/static/gym_pwa/icons/icon-192x192.png',
        badge: '/pwa/static/gym_pwa/icons/badge.png',
        vibrate: [100, 50, 100],
        data: {
            url: '/'
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
        clients.openWindow(event.notification.data.url)
    );
}); 