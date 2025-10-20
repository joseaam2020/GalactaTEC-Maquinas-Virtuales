import sqlite3
from datetime import datetime
import bcrypt
import screens.main_window

# Conecta o crea la base de datos local
#conn = sqlite3.connect("GalactaDB.db")
#cursor = conn.cursor()

# ----------------------------------------------------------
# 🔹 Crear tabla si no existe
# ----------------------------------------------------------
#cursor.execute("""
#CREATE TABLE IF NOT EXISTS players (
#    id INTEGER PRIMARY KEY AUTOINCREMENT,
#    username TEXT UNIQUE NOT NULL,
#    full_name TEXT NOT NULL,
#    email TEXT UNIQUE NOT NULL,
#    password_hash BLOB NOT NULL,
#    photo_path TEXT,
#    ship_image TEXT,
#    music_pref TEXT,
#    created_at TEXT
#)
#               
#               
#""")
#conn.commit()
#
#
## ----------------------------------------------------------
## 🔹 Crear tabla de puntajes
## ----------------------------------------------------------
#cursor.execute("""
#CREATE TABLE IF NOT EXISTS scores (
#    id_score INTEGER PRIMARY KEY AUTOINCREMENT,
#    player_id INTEGER NOT NULL,
#    score INTEGER NOT NULL,
#    created_at TEXT,
#    FOREIGN KEY (player_id) REFERENCES players(id)
#)
#""")
#conn.commit()


# ----------------------------------------------------------
# 🔹 Registrar jugador
# ----------------------------------------------------------
def register_player(username, full_name, email, password, photo_path, ship_image, music_pref,db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        cursor.execute("""
            INSERT INTO players (username, full_name, email, password_hash, photo_path, ship_image, music_pref, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (username, full_name, email, password_hash, photo_path, ship_image, music_pref, datetime.utcnow().isoformat()))
        conn.commit()
        print("✅ Jugador registrado correctamente.")
        return True
    except sqlite3.IntegrityError as e:
        print("❌ Error: El nombre de usuario o correo ya existen.")
        return False
    except Exception as e:
        print("❌ Error al registrar:", e)
        return False

# ----------------------------------------------------------
# 🔹 Login
# ----------------------------------------------------------
def login_player(username, password, db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT username, password_hash FROM players WHERE username = ?
    """, (username,))



    print("Base de datos")
    print(username, password)
   
    result = cursor.fetchone() # Le pide a la base de datos el resultado
    #print(result)
    
    if result:
        stores_username, stored_hash = result # Devuelve los resultado se la base de datos
        if bcrypt.checkpw(password.encode('utf-8'), stored_hash):
            print(f"✅ Bienvenido, {username}!")
            return True
        else:
            print("❌ Contraseña incorrecta.")
    else:
        print("❌ Usuario no encontrado.")
    

    return False

# ----------------------------------------------------------
# 🔹 Actualizar datos del jugador
# ----------------------------------------------------------
def update_player(username, **updates):
    allowed = {"full_name", "email", "photo_path", "ship_image", "music_pref"}
    fields = []
    values = []
    for key, value in updates.items():
        if key in allowed:
            fields.append(f"{key} = ?")
            values.append(value)
    if not fields:
        print("⚠️ No hay datos válidos para actualizar.")
        return False
    values.append(username)
    query = f"UPDATE players SET {', '.join(fields)} WHERE username = ?"
    cursor.execute(query, values)
    conn.commit()
    print("✅ Datos actualizados correctamente.")
    return True

# ----------------------------------------------------------
# 🔹 Mostrar todos (solo para depuración)
# ----------------------------------------------------------
def show_all_players():
    cursor.execute("SELECT username, full_name, email, photo_path, ship_image, music_pref FROM players")
    for row in cursor.fetchall():
        print(row)

# ----------------------------------------------------------
# 🔹 Guardar un puntaje
# ----------------------------------------------------------
def add_score(username, score):
    try:
        # Obtener el id del jugador por su username
        cursor.execute("SELECT id FROM players WHERE username = ?", (username,))
        result = cursor.fetchone()
        
        if not result:
            print("❌ Jugador no encontrado.")
            return False
        
        player_id = result[0]
        
        # Insertar el puntaje
        cursor.execute("""
            INSERT INTO scores (player_id, score, created_at)
            VALUES (?, ?, ?)
        """, (player_id, score, datetime.utcnow().isoformat()))
        
        conn.commit()
        print(f"✅ Puntaje {score} guardado para el jugador '{username}'.")
        return True
    
    except Exception as e:
        print("❌ Error al guardar puntaje:", e)
        return False

# ----------------------------------------------------------
# 🔹 Mostrar puntajes de un jugador
# ----------------------------------------------------------
def show_scores(username):
    cursor.execute("""
        SELECT p.username, s.score, s.created_at
        FROM scores s
        JOIN players p ON s.player_id = p.id
        WHERE p.username = ?
        ORDER BY s.created_at DESC
    """, (username,))
    
    results = cursor.fetchall()
    if not results:
        print("⚠️ No hay puntajes registrados para este jugador.")
    else:
        print(f"🏆 Puntajes de {username}:")
        for row in results:
            print(f"  → {row[1]} puntos ({row[2]})")

def get_top_6_scores(db_path):
    """
    Obtiene la puntuación más alta de cada jugador y devuelve los 5 mejores como un diccionario.

    Args:
        db_path (str): Ruta al archivo de base de datos SQLite (.db).

    Returns:
        Dict[str, Dict[str, Any]]: Diccionario donde la clave es el nombre del jugador y el valor es otro diccionario
        con su 'puntaje' y la 'direccion_imagen' (photo_path).
    """
    # Conexión a la base de datos
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Consulta para obtener top 5 con nombre y foto
    cursor.execute("""
        SELECT p.username, MAX(s.score) AS max_score, p.photo_path
        FROM scores s
        JOIN players p ON s.player_id = p.id
        GROUP BY s.player_id
        ORDER BY max_score DESC
        LIMIT 6;
    """)

    # Convertimos los resultados a un diccionario
    top_scores = {}
    for username, max_score, photo_path in cursor.fetchall():
        top_scores[username] = {
            "score": max_score,
            "img_path": photo_path
        }

    # Cerrar conexión
    conn.close()

    return top_scores

def username_exists(username, db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM players WHERE username = ? LIMIT 1", (username,))
    return cursor.fetchone() is not None
