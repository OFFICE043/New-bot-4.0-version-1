import sqlite3
from config import HEAD_ADMINS

DB_NAME = "bot_database.db"

def query_db(query, params=(), fetch=None):
    """A helper function to query the database and handle connections."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(query, params)
    if fetch == "one": result = cursor.fetchone()
    elif fetch == "all": result = cursor.fetchall()
    else: result = None
    conn.commit()
    conn.close()
    return result

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    # Users table
    cursor.execute("CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY, username TEXT, first_name TEXT, status TEXT DEFAULT 'user')")
    # Admins table
    cursor.execute("CREATE TABLE IF NOT EXISTS admins (user_id INTEGER PRIMARY KEY)")
    # Anime table
    cursor.execute("CREATE TABLE IF NOT EXISTS anime (id INTEGER PRIMARY KEY AUTOINCREMENT, code TEXT UNIQUE NOT NULL, name TEXT NOT NULL, description TEXT, post_link TEXT, view_count INTEGER DEFAULT 0)")
    # Settings table
    cursor.execute("CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT)")
    conn.commit()
    conn.close()
    print("Дерекқор (база) барлық кестелерімен сәтті дайындалды.")

# --- User Functions ---
def add_user(user_id: int, username: str, first_name: str):
    query_db("INSERT OR IGNORE INTO users (user_id, username, first_name) VALUES (?, ?, ?)", (user_id, username, first_name))

def get_user_status(user_id: int) -> str:
    if user_id in HEAD_ADMINS: return 'bosh_admin'
    if query_db("SELECT user_id FROM admins WHERE user_id = ?", (user_id,), fetch="one"): return 'oddiy_admin'
    user_data = query_db("SELECT status FROM users WHERE user_id = ?", (user_id,), fetch="one")
    return user_data[0] if user_data and user_data[0] == 'vip' else 'user'
    
def get_all_user_ids():
    rows = query_db("SELECT user_id FROM users", fetch="all")
    return [row[0] for row in rows] if rows else []

def get_users_count():
    result = query_db("SELECT COUNT(*) FROM users", fetch="one")
    return result[0] if result else 0

# --- Admin Management Functions ---
def add_admin(user_id: int):
    query_db("INSERT OR IGNORE INTO admins (user_id) VALUES (?)", (user_id,))

def remove_admin(user_id: int):
    query_db("DELETE FROM admins WHERE user_id = ?", (user_id,))

def get_all_admins():
    admins = query_db("SELECT user_id FROM admins", fetch="all")
    admin_ids = {admin[0] for admin in admins} if admins else set()
    admin_ids.update(HEAD_ADMINS)
    return list(admin_ids)

# --- Anime Management Functions ---
def add_anime(code: str, name: str, description: str):
    query_db("INSERT INTO anime (code, name, description) VALUES (?, ?, ?)", (code, name, description))

def get_anime_by_code(code: str):
    return query_db("SELECT id, code, name, description FROM anime WHERE code = ?", (code,), fetch="one")

def delete_anime(code: str):
    query_db("DELETE FROM anime WHERE code = ?", (code,))
    
def get_all_anime():
    return query_db("SELECT code, name FROM anime ORDER BY name", fetch="all")
    
def get_anime_count():
    result = query_db("SELECT COUNT(*) FROM anime", fetch="one")
    return result[0] if result else 0
