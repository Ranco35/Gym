#!/usr/bin/env python
import os

def fix_trainers_views():
    """
    Corrige el archivo de views.py en la app trainers.
    """
    # Ruta al archivo
    file_path = 'gymworl/trainers/views.py'
    
    # Leer el contenido actual
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.readlines()
    
    # Corregir el contenido
    fixed_content = []
    for line in content:
        # Reemplazar 'training-list' por 'training-list-create'
        if 'training-list' in line and not 'training-list-create' in line:
            line = line.replace('training-list', 'training-list-create')
        
        # Eliminar líneas que contengan "Exception Type: NoReverseMatch"
        if "Exception Type:" not in line and "NoReverseMatch" not in line:
            fixed_content.append(line)
    
    # Escribir el contenido corregido
    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(fixed_content)
    
    print(f"Archivo {file_path} corregido correctamente.")

if __name__ == "__main__":
    fix_trainers_views() 