import sqlite3
from config import HEAD_ADMINS

DB_NAME = "bot_database.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    # Users table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY, username TEXT, first_name TEXT, status TEXT DEFAULT 'user'
    )""")
    # Admins table
    cursor.execute("CREATE TABLE IF NOT EXISTS admins (user_id INTEGER PRIMARY KEY)")
    # Anime table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS anime (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        code TEXT UNIQUE NOT NULL, name TEXT NOT NULL, description TEXT,
        post_link TEXT, view_count INTEGER DEFAULT 0
    )""")
    # Support tickets table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS support_tickets (
        ticket_id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER,
        message_text TEXT, status TEXT DEFAULT 'open', created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )""")
    # Settings table for VIP info and other texts
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT)""")
    
    # Add default data if not exists
    cursor.execute("SELECT key FROM settings WHERE key = 'vip_info'")
    if cursor.fetchone() is None:
        vip_text = """⭐️ VIP a'zolik afzalliklari:
1. VIP a'zolar uchun yaratilgan maxsus komandalarga kirish.
2. Ular uchun maxsus reaksiya beriladi.
3. 1 oy davomida hech qanday kanalga obuna bo'lmasdan anime tomosha qilish.
4. Botga yangi anime yuklanganda birinchi sizga xabar yuboriladi."""
        cursor.execute("INSERT INTO settings (key, value) VALUES ('vip_info', ?)", (vip_text,))

    cursor.execute("SELECT code FROM anime WHERE code = '101'")
    if cursor.fetchone() is None:
        cursor.execute("INSERT INTO anime (code, name, description) VALUES (?, ?, ?)", 
                       ('101', 'Naruto', 'Mashhur shinobi animesi.'))
    cursor.execute("SELECT code FROM anime WHERE code = '102'")
    if cursor.fetchone() is None:
        cursor.execute("INSERT INTO anime (code, name, description) VALUES (?, ?, ?)", 
                       ('102', 'Bleach', 'Ruhlar olami haqida anime.'))

    conn.commit()
    conn.close()
    print("Дерекқор (база) барлық кестелерімен сәтті дайындалды.")

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

# --- User Functions ---
def add_user(user_id: int, username: str, first_name: str):
    query_db("INSERT OR IGNORE INTO users (user_id, username, first_name) VALUES (?, ?, ?)", (user_id, username, first_name))

def get_user_status(user_id: int) -> str:
    if user_id in HEAD_ADMINS: return 'bosh_admin'
    if query_db("SELECT user_id FROM admins WHERE user_id = ?", (user_id,), fetch="one"): return 'oddiy_admin'
    user_data = query_db("SELECT status FROM users WHERE user_id = ?", (user_id,), fetch="one")
    return user_data[0] if user_data and user_data[0] == 'vip' else 'user'

# --- Anime Functions ---
def search_anime_by_code(code: str):
    return query_db("SELECT code, name, description FROM anime WHERE code = ?", (code,), fetch="one")

def search_anime_by_name(name: str):
    return query_db("SELECT code, name, description FROM anime WHERE name LIKE ?", ('%' + name + '%',), fetch="all")
    
def get_all_anime():
    return query_db("SELECT code, name FROM anime ORDER BY name", fetch="all")
    
def get_top_anime(limit: int = 20):
    return query_db("SELECT code, name, view_count FROM anime ORDER BY view_count DESC LIMIT ?", (limit,), fetch="all")

# --- Settings/Tickets Functions ---
def get_setting(key: str):
    result = query_db("SELECT value FROM settings WHERE key = ?", (key,), fetch="one")
    return result[0] if result else None
    
def create_support_ticket(user_id: int, message: str):
    query_db("INSERT INTO support_tickets (user_id, message_text) VALUES (?, ?)", (user_id, message))
