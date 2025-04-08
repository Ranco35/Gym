#!/bin/bash
# Script para iniciar el servidor de desarrollo Django para la PWA

echo "===== Iniciando servidor de desarrollo para GymWorl PWA ====="
echo "Este script inicia el servidor Django con SQLite para desarrollo local"

# Activar el entorno virtual
VENV_PATH="venv/bin/activate"
if [ -f "$VENV_PATH" ]; then
    echo "Activando entorno virtual..."
    source "$VENV_PATH"
else
    echo "No se encontró entorno virtual en $VENV_PATH"
    echo "Continuando sin entorno virtual..."
fi

# Configurar el módulo de configuración de Django
export DJANGO_SETTINGS_MODULE=gymworl.settings

# Verificar migraciones pendientes
echo "Verificando migraciones pendientes..."
python manage.py makemigrations

# Aplicar migraciones
echo "Aplicando migraciones..."
python manage.py migrate

# Recopilar archivos estáticos
echo "Recopilando archivos estáticos..."
python manage.py collectstatic --noinput

# Iniciar el servidor
echo "Iniciando servidor en http://127.0.0.1:8000/pwa/"
echo "Para probar la PWA, abre esa URL en tu navegador"
echo "Para probar las funcionalidades offline, usa la consola del navegador y el script pwa-test.js"
echo "Presiona Ctrl+C para detener el servidor"
echo ""

python manage.py runserver

echo "Servidor detenido"