import sys
import os
from pathlib import Path

# Agregar el directorio raíz del proyecto al PATH de Python
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from src.database import SessionLocal
from src.models.user import User, UserRole
from src.auth.jwt_handler import get_password_hash

def create_superuser():
    db = SessionLocal()
    try:
        # Verificar si ya existe un superusuario
        superuser = db.query(User).filter(User.email == "edu@gymtracker.com").first()
        if not superuser:
            # Crear superusuario
            superuser = User(
                email="edu@gymtracker.com",
                username="edu",
                hashed_password=get_password_hash("123123"),
                full_name="Eduardo",
                role=UserRole.ADMIN
            )
            db.add(superuser)
            db.commit()
            print("Superusuario creado exitosamente")
            print("Email: edu@gymtracker.com")
            print("Contraseña: 123123")
        else:
            print("Ya existe un superusuario")
    finally:
        db.close()

if __name__ == "__main__":
    create_superuser()