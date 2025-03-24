# Gym Tracker API

Sistema de seguimiento de entrenamiento en gimnasio con autenticación y roles de usuario.

## Requisitos

- Python 3.8+
- PostgreSQL
- pip

## Configuración

1. Crear entorno virtual:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

2. Instalar dependencias:
```bash
pip install -r requirements.txt
```

3. Configurar variables de entorno:
- Copiar `.env.example` a `.env`
- Actualizar las variables según tu configuración

4. Crear base de datos PostgreSQL:
```sql
CREATE DATABASE gym_tracker;
```

5. Ejecutar migraciones:
```bash
alembic upgrade head
```

## Ejecución

```bash
uvicorn src.main:app --reload
```

La API estará disponible en `http://localhost:8000`

## Documentación API

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Roles de Usuario

1. Usuario Final
   - Registro de entrenamientos
   - Seguimiento de progreso
   - Visualización de rutinas asignadas

2. Entrenador
   - Gestión de clientes
   - Creación de rutinas
   - Seguimiento de progreso de clientes

3. Administrador
   - Gestión de usuarios
   - Configuración del sistema
   - Reportes y análisis