#!/usr/bin/env python
import sqlite3
import os

def añadir_columna_creator():
    """
    Añade la columna creator_id a la tabla exercises_exercise y establece Eduardo como creador.
    """
    try:
        # Ruta a la base de datos SQLite
        db_path = 'db.sqlite3'
        
        # Verificar que el archivo existe
        if not os.path.exists(db_path):
            print(f"Error: No se encontró la base de datos en {db_path}")
            return
        
        # Conectar a la base de datos
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Verificar si la columna ya existe
        cursor.execute("PRAGMA table_info(exercises_exercise)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'creator_id' not in columns:
            print("Añadiendo columna 'creator_id' a la tabla exercises_exercise...")
            
            # Añadir la columna creator_id
            cursor.execute("ALTER TABLE exercises_exercise ADD COLUMN creator_id INTEGER NULL REFERENCES users_customuser(id)")
            
            # Buscar un usuario con nombre o usuario "Eduardo"
            cursor.execute("SELECT id FROM users_customuser WHERE first_name = 'Eduardo' OR username = 'eduardo' LIMIT 1")
            result = cursor.fetchone()
            
            if result:
                user_id = result[0]
                print("Se encontró un usuario existente llamado Eduardo.")
            else:
                # Si no existe Eduardo, crear nuevo usuario
                print("Creando nuevo usuario 'Eduardo'...")
                cursor.execute("""
                    INSERT INTO users_customuser 
                    (password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, 
                    date_joined, role, phone_number, bio, profile_picture)
                    VALUES 
                    ('pbkdf2_sha256$600000$salt$hash', datetime('now'), 1, 'eduardo', 'Eduardo', '', 
                    'eduardo@example.com', 1, 1, datetime('now'), 'ADMIN', '', '', '')
                """)
                user_id = cursor.lastrowid
                print(f"Usuario 'Eduardo' creado con ID {user_id}")
            
            # Asignar Eduardo como creador a todos los ejercicios
            cursor.execute(f"UPDATE exercises_exercise SET creator_id = {user_id}")
            conn.commit()
            
            # Contar cuántos ejercicios se actualizaron
            cursor.execute("SELECT COUNT(*) FROM exercises_exercise")
            total_ejercicios = cursor.fetchone()[0]
            
            print(f"Se asignó 'Eduardo' como creador a {total_ejercicios} ejercicios.")
            print("Columna creator_id añadida con éxito.")
        else:
            print("La columna 'creator_id' ya existe en la tabla exercises_exercise.")
            
            # Verificar si hay ejercicios sin creador
            cursor.execute("SELECT COUNT(*) FROM exercises_exercise WHERE creator_id IS NULL")
            ejercicios_sin_creador = cursor.fetchone()[0]
            
            if ejercicios_sin_creador > 0:
                # Buscar o crear usuario Eduardo
                cursor.execute("SELECT id FROM users_customuser WHERE first_name = 'Eduardo' OR username = 'eduardo' LIMIT 1")
                result = cursor.fetchone()
                
                if result:
                    user_id = result[0]
                else:
                    # Crear usuario Eduardo
                    cursor.execute("""
                        INSERT INTO users_customuser 
                        (password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, 
                        date_joined, role, phone_number, bio, profile_picture)
                        VALUES 
                        ('pbkdf2_sha256$600000$salt$hash', datetime('now'), 1, 'eduardo', 'Eduardo', '', 
                        'eduardo@example.com', 1, 1, datetime('now'), 'ADMIN', '', '', '')
                    """)
                    user_id = cursor.lastrowid
                
                # Asignar creador a los ejercicios que no lo tienen
                cursor.execute(f"UPDATE exercises_exercise SET creator_id = {user_id} WHERE creator_id IS NULL")
                conn.commit()
                print(f"Se asignó 'Eduardo' como creador a {ejercicios_sin_creador} ejercicios que no tenían creador.")
        
        # Cerrar conexión
        conn.close()
            
    except Exception as e:
        print(f"Error al añadir columna creator_id: {str(e)}")

if __name__ == "__main__":
    añadir_columna_creator() 