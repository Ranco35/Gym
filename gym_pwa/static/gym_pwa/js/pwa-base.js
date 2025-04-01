/**
 * Funcionalidades base para la PWA de GymWorl
 */

// Comprobar si el navegador soporta service worker
if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        navigator.serviceWorker.register('/serviceworker.js')
            .then(registration => {
                console.log('Service Worker registrado con éxito:', registration.scope);
            })
            .catch(error => {
                console.error('Error al registrar el Service Worker:', error);
            });
    });
}

// Gestión del estado online/offline
function updateOnlineStatus() {
    const statusIndicator = document.getElementById('connection-status');
    if (!statusIndicator) return;
    
    if (navigator.onLine) {
        statusIndicator.classList.add('online');
        statusIndicator.classList.remove('offline');
        statusIndicator.title = 'Conectado';
        
        // Si tenemos datos pendientes de sincronizar, intentar sincronizar
        if (window.syncPendingData && typeof window.syncPendingData === 'function') {
            window.syncPendingData();
        }
    } else {
        statusIndicator.classList.add('offline');
        statusIndicator.classList.remove('online');
        statusIndicator.title = 'Sin conexión';
    }
}

// Inicializar estados
document.addEventListener('DOMContentLoaded', () => {
    // Actualizar estado de conexión inicial
    updateOnlineStatus();
    
    // Configurar event listeners para cambios en la conexión
    window.addEventListener('online', updateOnlineStatus);
    window.addEventListener('offline', updateOnlineStatus);
    
    // Mostrar nombre de usuario (si está disponible)
    const userNameElement = document.getElementById('user-name');
    if (userNameElement) {
        // Intentar obtener el nombre de usuario desde localStorage
        const userName = localStorage.getItem('userName');
        if (userName) {
            userNameElement.textContent = userName;
        }
    }
    
    // Activar enlace de navegación actual
    const currentPath = window.location.pathname;
    const navItems = document.querySelectorAll('.pwa-nav-item');
    navItems.forEach(item => {
        if (currentPath.includes(item.getAttribute('href'))) {
            item.classList.add('active');
        }
    });
});

// API para almacenamiento local de datos
class LocalStorage {
    static set(key, value) {
        try {
            const serialized = JSON.stringify(value);
            localStorage.setItem(key, serialized);
            return true;
        } catch (error) {
            console.error('Error al guardar en localStorage:', error);
            return false;
        }
    }
    
    static get(key) {
        try {
            const serialized = localStorage.getItem(key);
            if (serialized === null) return null;
            return JSON.parse(serialized);
        } catch (error) {
            console.error('Error al leer de localStorage:', error);
            return null;
        }
    }
    
    static remove(key) {
        try {
            localStorage.removeItem(key);
            return true;
        } catch (error) {
            console.error('Error al eliminar de localStorage:', error);
            return false;
        }
    }
}

// Clase para manejar sincronización con el servidor
class SyncManager {
    constructor(endpoint = '/pwa/api/sync/') {
        this.endpoint = endpoint;
        this.pendingQueue = LocalStorage.get('pendingSyncQueue') || [];
    }
    
    addToQueue(data, type) {
        this.pendingQueue.push({
            data,
            type,
            timestamp: new Date().toISOString(),
            id: Math.random().toString(36).substr(2, 9)
        });
        
        LocalStorage.set('pendingSyncQueue', this.pendingQueue);
        
        // Intentar sincronizar de inmediato si estamos online
        if (navigator.onLine) {
            this.sync();
        }
    }
    
    async sync() {
        if (this.pendingQueue.length === 0) return;
        if (!navigator.onLine) return;
        
        // Obtener el token CSRF
        const csrfToken = this.getCsrfToken();
        
        // Intentar sincronizar cada elemento en la cola
        for (let i = 0; i < this.pendingQueue.length; i++) {
            const item = this.pendingQueue[i];
            
            try {
                const response = await fetch(`${this.endpoint}${item.type}/`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': csrfToken
                    },
                    body: JSON.stringify(item.data)
                });
                
                if (response.ok) {
                    // Eliminar de la cola si la sincronización fue exitosa
                    this.pendingQueue.splice(i, 1);
                    i--; // Ajustar el índice
                }
            } catch (error) {
                console.error('Error al sincronizar:', error);
                // Continuar con el siguiente item
            }
        }
        
        // Actualizar la cola en localStorage
        LocalStorage.set('pendingSyncQueue', this.pendingQueue);
    }
    
    getCsrfToken() {
        // Intentar obtener el token de una cookie o meta tag
        const csrfCookie = document.cookie
            .split('; ')
            .find(row => row.startsWith('csrftoken='));
            
        if (csrfCookie) {
            return csrfCookie.split('=')[1];
        }
        
        // Si no hay cookie, intentar obtenerlo de un meta tag
        const csrfMeta = document.querySelector('meta[name="csrf-token"]');
        if (csrfMeta) {
            return csrfMeta.getAttribute('content');
        }
        
        return '';
    }
}

// Exportar utilidades para usar en otros scripts
window.gymWorl = {
    storage: LocalStorage,
    syncManager: new SyncManager()
}; 