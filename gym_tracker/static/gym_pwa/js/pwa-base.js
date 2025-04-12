// Registro del Service Worker
if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        navigator.serviceWorker.register('/serviceworker.js')
            .then(registration => {
                console.log('ServiceWorker registrado con éxito:', registration.scope);
            })
            .catch(error => {
                console.log('Error al registrar el ServiceWorker:', error);
            });
    });
}

// Funciones de utilidad para la PWA
const PWA = {
    // Verificar si la app está instalada
    isInstalled: () => {
        return window.matchMedia('(display-mode: standalone)').matches ||
               window.navigator.standalone ||
               document.referrer.includes('android-app://');
    },

    // Mostrar mensaje de instalación
    showInstallPrompt: () => {
        const deferredPrompt = window.deferredPrompt;
        if (deferredPrompt) {
            deferredPrompt.prompt();
            deferredPrompt.userChoice.then((choiceResult) => {
                if (choiceResult.outcome === 'accepted') {
                    console.log('Usuario aceptó instalar la PWA');
                }
                window.deferredPrompt = null;
            });
        }
    },

    // Manejar eventos de conexión
    handleConnection: () => {
        window.addEventListener('online', () => {
            console.log('Conexión restaurada');
            // Aquí puedes agregar lógica para sincronizar datos
        });

        window.addEventListener('offline', () => {
            console.log('Conexión perdida');
            // Aquí puedes agregar lógica para modo offline
        });
    },

    // Inicializar la PWA
    init: () => {
        PWA.handleConnection();
        
        // Capturar el evento de instalación
        window.addEventListener('beforeinstallprompt', (e) => {
            e.preventDefault();
            window.deferredPrompt = e;
        });
    }
};

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', () => {
    PWA.init();
}); 