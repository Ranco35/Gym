#!/usr/bin/env python
import sqlite3
import os

def verificar_y_arreglar_ejercicios():
    """
    Verifica y arregla los ejercicios sin creador, asignándoles Eduardo.
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
        
        # Obtener la estructura completa de la tabla para mostrar
        cursor.execute("PRAGMA table_info(exercises_exercise)")
        columns = cursor.fetchall()
        print("Estructura completa de la tabla exercises_exercise:")
        for col in columns:
            col_id, col_name, col_type, not_null, default_val, pk = col
            print(f"  - {col_name} ({col_type})")
        
        # Verificar si hay ejercicios
        cursor.execute("SELECT COUNT(*) FROM exercises_exercise")
        total_ejercicios = cursor.fetchone()[0]
        print(f"Total de ejercicios en la base de datos: {total_ejercicios}")
        
        # Verificar si hay ejercicios sin creador
        cursor.execute("SELECT COUNT(*) FROM exercises_exercise WHERE creator_id IS NULL")
        ejercicios_sin_creador = cursor.fetchone()[0]
        print(f"Ejercicios sin creador: {ejercicios_sin_creador}")
        
        if ejercicios_sin_creador > 0:
            # Buscar o crear usuario Eduardo
            cursor.execute("SELECT id FROM users_customuser WHERE first_name = 'Eduardo' OR username = 'eduardo' LIMIT 1")
            result = cursor.fetchone()
            
            if result:
                user_id = result[0]
                print(f"Usuario Eduardo encontrado con ID: {user_id}")
            else:
                # Crear usuario Eduardo
                print("Creando usuario Eduardo...")
                cursor.execute("""
                    INSERT INTO users_customuser 
                    (password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, 
                    date_joined, role, phone_number, bio, profile_picture)
                    VALUES 
                    ('pbkdf2_sha256$600000$salt$hash', datetime('now'), 1, 'eduardo', 'Eduardo', '', 
                    'eduardo@example.com', 1, 1, datetime('now'), 'ADMIN', '', '', '')
                """)
                user_id = cursor.lastrowid
                print(f"Usuario Eduardo creado con ID: {user_id}")
            
            # Asignar creador a los ejercicios que no lo tienen
            cursor.execute(f"UPDATE exercises_exercise SET creator_id = {user_id} WHERE creator_id IS NULL")
            conn.commit()
            print(f"Se asignó 'Eduardo' como creador a {ejercicios_sin_creador} ejercicios.")
        else:
            print("Todos los ejercicios ya tienen creador asignado.")
        
        # Verificar los ejercicios para ver sus creadores
        print("\nVerificando algunos ejercicios al azar:")
        cursor.execute("""
            SELECT e.id, e.name, e.creator_id, u.username, u.first_name 
            FROM exercises_exercise e
            LEFT JOIN users_customuser u ON e.creator_id = u.id
            LIMIT 5
        """)
        for row in cursor.fetchall():
            exercise_id, name, creator_id, username, first_name = row
            creator_name = first_name if first_name else username
            print(f"  - Ejercicio ID {exercise_id}: '{name}' - Creador: {creator_name} (ID: {creator_id})")
        
        # Cerrar conexión
        conn.close()
            
    except Exception as e:
        print(f"Error al verificar y arreglar ejercicios: {str(e)}")

if __name__ == "__main__":
    verificar_y_arreglar_ejercicios() 