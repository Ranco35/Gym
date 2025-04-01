/**
 * API para gestionar ejercicios
 */
const ExerciseAPI = {
    /**
     * Obtiene todos los ejercicios
     * @returns {Promise} Promise con la respuesta
     */
    getAll: async function() {
        try {
            const response = await fetch('/api/exercises/');
            if (!response.ok) {
                throw new Error(`Error ${response.status}: ${response.statusText}`);
            }
            return await response.json();
        } catch (error) {
            console.error('Error obteniendo ejercicios:', error);
            throw error;
        }
    },

    /**
     * Obtiene un ejercicio por su slug
     * @param {string} slug Slug del ejercicio
     * @returns {Promise} Promise con la respuesta
     */
    getBySlug: async function(slug) {
        try {
            const response = await fetch(`/api/exercises/${slug}/`);
            if (!response.ok) {
                throw new Error(`Error ${response.status}: ${response.statusText}`);
            }
            return await response.json();
        } catch (error) {
            console.error(`Error obteniendo ejercicio ${slug}:`, error);
            throw error;
        }
    },

    /**
     * Exporta los ejercicios seleccionados
     * @param {Array} ids Array de IDs a exportar
     * @returns {Promise} Promise con la respuesta
     */
    export: async function(ids = []) {
        try {
            console.log('Iniciando exportación de ejercicios...');
            
            // Crear un modal de carga si no existe
            let loadingModal = document.getElementById('loadingExportModal');
            if (!loadingModal) {
                loadingModal = document.createElement('div');
                loadingModal.id = 'loadingExportModal';
                loadingModal.className = 'modal fade show';
                loadingModal.style.display = 'block';
                loadingModal.style.backgroundColor = 'rgba(0,0,0,0.5)';
                loadingModal.innerHTML = `
                    <div class="modal-dialog modal-dialog-centered">
                        <div class="modal-content">
                            <div class="modal-body text-center p-5">
                                <div class="spinner-border text-primary mb-3" style="width: 3rem; height: 3rem;" role="status">
                                    <span class="visually-hidden">Cargando...</span>
                                </div>
                                <h5 class="mb-3">Exportando ejercicios</h5>
                                <p class="mb-0">Por favor espere mientras se procesa su solicitud...</p>
                            </div>
                        </div>
                    </div>
                `;
                document.body.appendChild(loadingModal);
            } else {
                loadingModal.style.display = 'block';
            }
            
            // Mostrar indicador visual si existe en el DOM
            const exportBtn = document.querySelector('#exportBtn');
            if (exportBtn) {
                exportBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Exportando...';
                exportBtn.disabled = true;
            }
            
            let url = '/exercises/export-json/';
            if (ids.length > 0) {
                url += '?' + ids.map(id => `ids=${id}`).join('&');
            }
            
            console.log('Redirigiendo a:', url);
            
            try {
                // Usar fetch en lugar de redirección directa para poder detectar errores
                const response = await fetch(url, {
                    method: 'GET',
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest'
                    }
                });
                
                if (!response.ok) {
                    throw new Error(`Error ${response.status}: ${response.statusText}`);
                }
                
                // Crear un link de descarga y hacer clic automáticamente
                const blob = await response.blob();
                const downloadUrl = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.style.display = 'none';
                a.href = downloadUrl;
                a.download = 'exercises_export.json';
                document.body.appendChild(a);
                a.click();
                window.URL.revokeObjectURL(downloadUrl);
                
                console.log('Exportación completada con éxito');
            } catch (error) {
                console.error('Error en fetch:', error);
                alert('Error al exportar: ' + error.message);
            } finally {
                // Ocultar modal de carga
                if (loadingModal) {
                    loadingModal.style.display = 'none';
                }
                
                // Restaurar el botón si existe
                if (exportBtn) {
                    exportBtn.innerHTML = '<i class="fas fa-file-code me-2"></i>Exportar a JSON';
                    exportBtn.disabled = false;
                }
            }
            
            return true;
        } catch (error) {
            console.error('Error exportando ejercicios:', error);
            
            // Ocultar modal de carga si existe
            const loadingModal = document.getElementById('loadingExportModal');
            if (loadingModal) {
                loadingModal.style.display = 'none';
            }
            
            // Restaurar el botón si existe
            const exportBtn = document.querySelector('#exportBtn');
            if (exportBtn) {
                exportBtn.innerHTML = '<i class="fas fa-file-code me-2"></i>Exportar a JSON';
                exportBtn.disabled = false;
            }
            
            // Mostrar alerta de error
            alert('Error al exportar ejercicios: ' + error.message);
            throw error;
        }
    },

    /**
     * Importa ejercicios desde un archivo JSON
     * @param {Object|Array} data Datos a importar
     * @returns {Promise} Promise con la respuesta
     */
    import: async function(data) {
        console.log('Iniciando importación de ejercicios...');
        
        // Crear un modal de carga para la importación
        let loadingModal = document.getElementById('loadingImportModal');
        if (!loadingModal) {
            loadingModal = document.createElement('div');
            loadingModal.id = 'loadingImportModal';
            loadingModal.className = 'modal fade show';
            loadingModal.style.display = 'block';
            loadingModal.style.backgroundColor = 'rgba(0,0,0,0.5)';
            loadingModal.innerHTML = `
                <div class="modal-dialog modal-dialog-centered">
                    <div class="modal-content">
                        <div class="modal-body text-center p-5">
                            <div class="spinner-border text-primary mb-3" style="width: 3rem; height: 3rem;" role="status">
                                <span class="visually-hidden">Cargando...</span>
                            </div>
                            <h5 class="mb-3">Importando ejercicios</h5>
                            <p class="mb-0">Por favor espere mientras se procesan los datos...</p>
                        </div>
                    </div>
                </div>
            `;
            document.body.appendChild(loadingModal);
        } else {
            loadingModal.style.display = 'block';
        }
        
        try {
            console.log('Enviando datos al servidor:', typeof data, Array.isArray(data) ? data.length : 'no es array');
            
            const response = await fetch('/exercises/import/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCsrfToken(),
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: JSON.stringify(data)
            });
            
            console.log('Respuesta recibida:', response.status, response.statusText);
            
            // Si la respuesta no es exitosa, mostrar mensaje detallado
            if (!response.ok) {
                const errorText = await response.text();
                console.error('Error en respuesta:', errorText);
                throw new Error(`Error ${response.status}: ${response.statusText}`);
            }
            
            const result = await response.json();
            console.log('Datos de respuesta:', result);
            
            // Ocultar modal de carga
            if (loadingModal) {
                loadingModal.style.display = 'none';
            }
            
            return result;
        } catch (error) {
            console.error('Error importando ejercicios:', error);
            
            // Ocultar modal de carga
            if (loadingModal) {
                loadingModal.style.display = 'none';
            }
            
            // Mostrar alerta de error
            alert('Error al importar ejercicios: ' + error.message);
            throw error;
        }
    }
};

/**
 * Obtiene el token CSRF de las cookies
 * @returns {string} Token CSRF
 */
function getCsrfToken() {
    const name = 'csrftoken';
    const cookies = document.cookie.split(';');
    for (let cookie of cookies) {
        const [cookieName, cookieValue] = cookie.trim().split('=');
        if (cookieName === name) {
            return cookieValue;
        }
    }
    return '';
} 