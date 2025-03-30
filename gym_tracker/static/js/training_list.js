/**
 * GymTracker 360 - Módulo de gestión de entrenamientos
 * Funcionalidades para la lista de entrenamientos organizados por semana
 */

document.addEventListener('DOMContentLoaded', function() {
    // Inicializar componentes
    initializeRoutineSelector();
    initializeRoutineToggles();
    initializeFirstWeekExpansion();
    setupEditTrainingButtons();
    setupDeleteTrainingButtons();
    setupAddSetButtons();
    setupSaveSetButton();
    enhanceTrainingCards();
});

/**
 * Inicializa el selector de rutinas y carga los días asociados
 */
function initializeRoutineSelector() {
    const routineSelect = document.getElementById('routineSelect');
    const routineDaySelect = document.getElementById('routineDaySelect');
    
    if (!routineSelect || !routineDaySelect) return;
    
    routineSelect.addEventListener('change', function() {
        const routineId = this.value;
        
        // Gestionar estado de selección vacía
        if (!routineId) {
            routineDaySelect.innerHTML = '<option value="">Primero selecciona una rutina</option>';
            routineDaySelect.disabled = true;
            return;
        }
        
        // Activar selector y mostrar cargando
        routineDaySelect.disabled = false;
        routineDaySelect.innerHTML = '<option value="">Cargando días...</option>';
        
        // Animación de carga
        routineSelect.classList.add('loading');
        
        // Cargar días de la rutina usando fetch API
        fetch(`/trainings/routine/${routineId}/days/`)
            .then(response => {
                if (!response.ok) {
                    throw new Error('Error en la respuesta del servidor');
                }
                return response.json();
            })
            .then(data => {
                populateRoutineDays(data, routineDaySelect);
                routineSelect.classList.remove('loading');
            })
            .catch(error => {
                console.error('Error al cargar los días:', error);
                routineDaySelect.innerHTML = '<option value="">Error al cargar días</option>';
                routineSelect.classList.remove('loading');
            });
    });
}

/**
 * Rellena el selector de días con los datos obtenidos del servidor
 */
function populateRoutineDays(data, routineDaySelect) {
    // Limpiar selector
    routineDaySelect.innerHTML = '';
    
    // Añadir opción por defecto
    const defaultOption = document.createElement('option');
    defaultOption.value = '';
    defaultOption.textContent = 'Selecciona un día';
    routineDaySelect.appendChild(defaultOption);
    
    // Añadir cada día disponible
    data.days.forEach(day => {
        const option = document.createElement('option');
        option.value = day.id;
        option.textContent = `${day.day_of_week} - ${day.focus || 'Sin enfoque'}`;
        routineDaySelect.appendChild(option);
    });
    
    // Efecto de aparición
    routineDaySelect.classList.add('fade-in');
    setTimeout(() => routineDaySelect.classList.remove('fade-in'), 500);
}

/**
 * Inicializa los toggles para mostrar/ocultar detalles de rutina
 */
function initializeRoutineToggles() {
    document.querySelectorAll('.routine-header').forEach(header => {
        header.addEventListener('click', function() {
            const routineDetails = this.nextElementSibling;
            const toggleIcon = this.querySelector('.toggle-icon');
            
            // Alternar clases para efecto visual - mejor manejo que toggle
            if (routineDetails.classList.contains('d-none')) {
                routineDetails.classList.remove('d-none');
                routineDetails.classList.add('show');
                this.classList.add('expanded');
                
                // Animar el icono
                toggleIcon.classList.replace('fa-chevron-down', 'fa-chevron-up');
            } else {
                routineDetails.classList.add('d-none');
                routineDetails.classList.remove('show');
                this.classList.remove('expanded');
                
                // Animar el icono
                toggleIcon.classList.replace('fa-chevron-up', 'fa-chevron-down');
            }
        });
    });
}

/**
 * Expande automáticamente la primera semana al cargar la página
 */
function initializeFirstWeekExpansion() {
    const weekContainers = document.querySelectorAll('.week-container');
    if (weekContainers.length === 0) return;
    
    // Esperar un momento para aplicar la animación después de que la página cargue
    setTimeout(() => {
        // Mostrar la primera semana expandida con clase de animación
        const firstWeek = weekContainers[0];
        firstWeek.classList.add('active');
        
        // Expandir automáticamente el primer día y rutina para mostrar el contenido
        const firstRoutineHeader = firstWeek.querySelector('.routine-header');
        if (firstRoutineHeader) {
            firstRoutineHeader.click();
        }
    }, 500);
}

/**
 * Configura los botones de edición de entrenamiento
 */
function setupEditTrainingButtons() {
    document.querySelectorAll('.edit-training').forEach(button => {
        button.addEventListener('click', function(e) {
            e.stopPropagation(); // Evitar propagación del clic
            const trainingId = this.getAttribute('data-training-id');
            
            // Animación antes de la redirección
            this.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
            this.disabled = true;
            
            // Redireccionar después de una breve animación
            setTimeout(() => {
                window.location.href = `/trainings/training/${trainingId}/edit/`;
            }, 300);
        });
    });
}

/**
 * Configura los botones para eliminar entrenamientos con confirmación mejorada
 */
function setupDeleteTrainingButtons() {
    document.querySelectorAll('.delete-training').forEach(button => {
        button.addEventListener('click', function(e) {
            e.stopPropagation(); // Evitar propagación del clic
            const trainingId = this.getAttribute('data-training-id');
            
            // Crear overlay de confirmación con animación
            showDeleteConfirmation(trainingId);
        });
    });
}

/**
 * Muestra un diálogo de confirmación personalizado para eliminar un entrenamiento
 */
function showDeleteConfirmation(trainingId) {
    // Crear overlay de confirmación
    const confirmBox = document.createElement('div');
    confirmBox.className = 'position-fixed top-0 start-0 w-100 h-100 d-flex align-items-center justify-content-center';
    confirmBox.style.backgroundColor = 'rgba(0,0,0,0.5)';
    confirmBox.style.zIndex = '9999';
    confirmBox.style.opacity = '0';
    confirmBox.style.transition = 'opacity 0.3s ease';
    
    // HTML del diálogo
    confirmBox.innerHTML = `
        <div class="card shadow p-3 border-0 rounded-3" style="max-width: 400px; transform: scale(0.9); transition: transform 0.3s ease;">
            <div class="card-body text-center">
                <i class="fas fa-exclamation-triangle text-warning fa-3x mb-3"></i>
                <h5>¿Eliminar este entrenamiento?</h5>
                <p class="text-muted">Esta acción no se puede deshacer</p>
                <div class="d-flex justify-content-center mt-3">
                    <button class="btn btn-secondary me-2 confirm-cancel">Cancelar</button>
                    <button class="btn btn-danger confirm-delete">Eliminar</button>
                </div>
            </div>
        </div>
    `;
    
    // Añadir al DOM y animar entrada
    document.body.appendChild(confirmBox);
    setTimeout(() => {
        confirmBox.style.opacity = '1';
        confirmBox.querySelector('.card').style.transform = 'scale(1)';
    }, 10);
    
    // Manejar cancelación
    confirmBox.querySelector('.confirm-cancel').addEventListener('click', function() {
        animateAndRemoveConfirmBox(confirmBox);
    });
    
    // Manejar confirmación
    confirmBox.querySelector('.confirm-delete').addEventListener('click', function() {
        // Mostrar animación de carga
        this.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
        this.disabled = true;
        
        // Crear y enviar formulario de eliminación
        setTimeout(() => {
            submitDeleteForm(trainingId);
        }, 300);
    });
    
    // Cerrar al hacer clic fuera del diálogo
    confirmBox.addEventListener('click', function(e) {
        if (e.target === confirmBox) {
            animateAndRemoveConfirmBox(confirmBox);
        }
    });
}

/**
 * Anima la salida y elimina el cuadro de confirmación
 */
function animateAndRemoveConfirmBox(confirmBox) {
    confirmBox.style.opacity = '0';
    confirmBox.querySelector('.card').style.transform = 'scale(0.9)';
    setTimeout(() => {
        document.body.removeChild(confirmBox);
    }, 300);
}

/**
 * Envía el formulario para eliminar un entrenamiento
 */
function submitDeleteForm(trainingId) {
    const form = document.createElement('form');
    form.method = 'POST';
    form.action = `/trainings/training/${trainingId}/delete/`;
    
    // Añadir CSRF token
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    const csrfInput = document.createElement('input');
    csrfInput.type = 'hidden';
    csrfInput.name = 'csrfmiddlewaretoken';
    csrfInput.value = csrfToken;
    form.appendChild(csrfInput);
    
    document.body.appendChild(form);
    form.submit();
}

/**
 * Configura los botones para añadir series manualmente
 */
function setupAddSetButtons() {
    document.querySelectorAll('.add-set-btn').forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const trainingId = this.getAttribute('data-training-id');
            
            // Animar botón con efecto de pulso
            this.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
            this.classList.add('pulse');
            
            // Abrir modal para añadir serie con ligero retraso para la animación
            setTimeout(() => {
                this.innerHTML = '<i class="fas fa-plus me-1"></i> Añadir serie';
                this.classList.remove('pulse');
                
                openAddSetModal(trainingId);
            }, 300);
        });
    });
}

/**
 * Abre el modal para añadir una serie con animación
 */
function openAddSetModal(trainingId) {
    const setModal = new bootstrap.Modal(document.getElementById('addSetModal'));
    document.getElementById('set-training-id').value = trainingId;
    
    // Limpiar campos
    document.getElementById('set-number').value = '';
    document.getElementById('set-weight').value = '';
    document.getElementById('set-reps').value = '';
    
    // Restablecer estado de los campos
    document.querySelectorAll('#add-set-form .form-control').forEach(control => {
        control.classList.remove('is-invalid');
    });
    
    setModal.show();
}

/**
 * Configura el botón para guardar series
 */
function setupSaveSetButton() {
    const saveButton = document.getElementById('save-set-btn');
    if (!saveButton) return;
    
    saveButton.addEventListener('click', function() {
        const trainingId = document.getElementById('set-training-id').value;
        const setNumber = document.getElementById('set-number').value;
        const weight = document.getElementById('set-weight').value;
        const reps = document.getElementById('set-reps').value;
        
        // Validar campos requeridos
        if (!validateSetForm(setNumber, reps)) {
            return;
        }
        
        // Animar botón
        this.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
        this.disabled = true;
        
        // Crear datos para la API
        const data = {
            training_id: trainingId,
            set_number: setNumber,
            weight: weight || 0,
            reps: reps
        };
        
        // Enviar datos a la API
        saveSet(data, this);
    });
}

/**
 * Valida el formulario de series
 */
function validateSetForm(setNumber, reps) {
    let isValid = true;
    const formControls = document.querySelectorAll('#add-set-form .form-control');
    
    formControls.forEach(control => {
        // Limpiar estado previo
        control.classList.remove('is-invalid');
        
        // Validar campos requeridos
        if (control.hasAttribute('required') && !control.value) {
            control.classList.add('is-invalid');
            // Efecto de shake para campos inválidos
            control.classList.add('shake');
            setTimeout(() => control.classList.remove('shake'), 500);
            isValid = false;
        }
    });
    
    return isValid;
}

/**
 * Guarda una serie mediante una llamada a la API
 */
function saveSet(data, button) {
    fetch('/trainings/session/' + data.training_id + '/sets/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
        },
        body: JSON.stringify(data)
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Error en la respuesta del servidor');
        }
        return response.json();
    })
    .then(result => {
        handleSetSaveResult(result, button);
    })
    .catch(error => {
        console.error('Error:', error);
        showSaveError(button, 'Error al guardar la serie');
    });
}

/**
 * Gestiona el resultado del guardado de la serie
 */
function handleSetSaveResult(result, button) {
    if (result.status === 'success') {
        // Mostrar indicador de éxito
        button.innerHTML = '<i class="fas fa-check"></i>';
        button.classList.replace('btn-primary', 'btn-success');
        
        // Efecto de confeti
        showSuccessAnimation();
        
        // Cerrar modal con retraso para ver la animación
        setTimeout(() => {
            const modal = bootstrap.Modal.getInstance(document.getElementById('addSetModal'));
            modal.hide();
            
            // Recargar la página para mostrar los cambios
            window.location.reload();
        }, 800);
    } else {
        showSaveError(button, 'Error al guardar la serie: ' + result.message);
    }
}

/**
 * Muestra animación de éxito
 */
function showSuccessAnimation() {
    // Implementar confeti u otra animación de éxito aquí si se desea
}

/**
 * Muestra error al guardar
 */
function showSaveError(button, message) {
    button.innerHTML = '<i class="fas fa-times"></i>';
    button.classList.replace('btn-primary', 'btn-danger');
    alert(message);
    
    // Restaurar botón después de mostrar el error
    setTimeout(() => {
        button.innerHTML = 'Guardar';
        button.classList.replace('btn-danger', 'btn-primary');
        button.disabled = false;
    }, 1500);
}

/**
 * Mejora las tarjetas de entrenamiento con efectos visuales
 */
function enhanceTrainingCards() {
    document.querySelectorAll('.training-routine-card').forEach(card => {
        // Efectos de hover avanzados
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-3px)';
            this.style.boxShadow = '0 8px 15px rgba(0,0,0,0.1)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
            this.style.boxShadow = '0 2px 5px rgba(0,0,0,0.05)';
        });
    });
}

// Añadir estilos dinámicos para animaciones
const style = document.createElement('style');
style.textContent = `
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.05); }
        100% { transform: scale(1); }
    }
    
    .pulse {
        animation: pulse 0.5s ease infinite;
    }
    
    @keyframes shake {
        0%, 100% { transform: translateX(0); }
        25% { transform: translateX(-5px); }
        75% { transform: translateX(5px); }
    }
    
    .shake {
        animation: shake 0.4s ease;
    }
    
    .loading {
        opacity: 0.7;
        pointer-events: none;
    }
`;
document.head.appendChild(style); 