#!/bin/bash

echo "========================================"
echo "🏋️ Iniciando Gym desde WSL..."
echo "========================================"

# === VARIABLES ===
REMOTE_USER=django
REMOTE_HOST=134.199.224.217
REMOTE_PORT=5432
LOCAL_PORT=5433
PROYECTO_DIR="/mnt/c/Users/eduar/DJANGO/gym"
VENV_DIR="$PROYECTO_DIR/venv"
DJANGO_PORT=8000

# === FUNCIONES DE CHEQUEO DE PUERTOS ===
check_port() {
    local port=$1
    if lsof -i :$port | grep LISTEN > /dev/null; then
        echo "🔍 El puerto $port ya está en uso en local."
        return 0
    else
        echo "✅ El puerto $port está libre en local."
        return 1
    fi
}

# === 1. Verificar si el túnel ya está abierto ===
echo "📡 Verificando túnel SSH en el puerto local $LOCAL_PORT..."
check_port $LOCAL_PORT

if [ $? -eq 0 ]; then
    echo "🔄 Túnel SSH ya estaba abierto."
else
    echo "🚀 Abriendo túnel SSH a DigitalOcean..."
    ssh -fN -L $LOCAL_PORT:localhost:$REMOTE_PORT $REMOTE_USER@$REMOTE_HOST

    if [ $? -ne 0 ]; then
        echo "❌ Error al establecer túnel SSH. Verifica tus credenciales o si el servidor está activo."
        exit 1
    fi

    echo "✅ Túnel SSH activo en localhost:$LOCAL_PORT"
fi

# === 2. Activar entorno virtual ===
echo "💻 Activando entorno virtual..."
source "$VENV_DIR/bin/activate"

# === 3. Navegar al proyecto ===
cd "$PROYECTO_DIR/gymworl" || {
    echo "❌ No se encontró el directorio gymworl"
    exit 1
}

# === 4. Abrir navegador ===
echo "🌐 Abriendo navegador en http://localhost:$DJANGO_PORT..."
/mnt/c/Program\ Files/Mozilla\ Firefox/firefox.exe "http://localhost:$DJANGO_PORT" &

# === 5. Correr servidor ===
echo "🚀 Ejecutando Django en 0.0.0.0:$DJANGO_PORT..."
python manage.py runserver 0.0.0.0:$DJANGO_PORT
