import sys
import subprocess
import pkg_resources

def check_dependencies():
    """Verifica y instala las dependencias necesarias."""
    required = {'sqlalchemy', 'fastapi', 'python-jose', 'passlib', 'python-multipart',
                'bcrypt', 'pydantic', 'psycopg2-binary', 'python-dotenv', 'alembic'}
    
    installed = {pkg.key for pkg in pkg_resources.working_set}
    missing = required - installed
    
    if missing:
        print("Instalando dependencias faltantes...")
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
        print("Dependencias instaladas correctamente.")
    else:
        print("Todas las dependencias están instaladas.")

if __name__ == "__main__":
    check_dependencies()