// Script para eliminar botones duplicados en la página de ejecución de entrenamiento
document.addEventListener('DOMContentLoaded', function() {
    // Buscar todos los botones "Saltar Ejercicio"
    const skipButtons = document.querySelectorAll('a[href*="action=skip"]');
    
    // Si hay más de uno, eliminar todos menos el primero
    if (skipButtons.length > 1) {
        for (let i = 1; i < skipButtons.length; i++) {
            skipButtons[i].parentNode.removeChild(skipButtons[i]);
        }
    }
    
    // Buscar todos los botones "Terminar Entrenamiento"
    const finishButtons = document.querySelectorAll('a[href*="action=end_early"]');
    
    // Si hay más de uno, eliminar todos menos el primero
    if (finishButtons.length > 1) {
        for (let i = 1; i < finishButtons.length; i++) {
            finishButtons[i].parentNode.removeChild(finishButtons[i]);
        }
    }
    
    // Reorganizar los botones en un contenedor flex
    const firstSkipButton = skipButtons[0];
    const firstFinishButton = finishButtons[0];
    
    if (firstSkipButton && firstFinishButton) {
        // Crear un nuevo contenedor flex
        const buttonContainer = document.createElement('div');
        buttonContainer.className = 'd-flex justify-content-between mb-4 mt-4';
        
        // Mover los botones al nuevo contenedor
        firstSkipButton.parentNode.insertBefore(buttonContainer, firstSkipButton);
        buttonContainer.appendChild(firstSkipButton);
        buttonContainer.appendChild(firstFinishButton);
        
        // Aplicar clases a los botones
        firstSkipButton.className = 'btn btn-warning btn-lg';
        firstFinishButton.className = 'btn btn-danger btn-lg';
    }
}); 