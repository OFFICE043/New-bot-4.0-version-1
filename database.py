import sqlite3
from config import HEAD_ADMINS

DB_NAME = "bot_database.db"

def query_db(query, params=(), fetch=None):
    """Дерекқорға сұраныс жіберіп, қосылымды басқаратын көмекші функция."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(query, params)
    
    if fetch == "one":
        result = cursor.fetchone()
    elif fetch == "all":
        result = cursor.fetchall()
    else:
        result = None
    
    conn.commit()
    conn.close()
    return result

def init_db():
    """Бот іске қосылғанда барлық кестелерді құру немесе тексеру"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Қолданушылар кестесі
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        username TEXT,
        first_name TEXT,
        status TEXT DEFAULT 'user'
    )""")
    
    # Админдер кестесі (Бас админдерден басқа)
    cursor.execute("CREATE TABLE IF NOT EXISTS admins (user_id INTEGER PRIMARY KEY)")
    
    # Анимелер кестесі
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS anime (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        code TEXT UNIQUE NOT NULL,
        name TEXT NOT NULL,
        description TEXT,
        post_link TEXT,
        view_count INTEGER DEFAULT 0
    )""")
    
    # Қолдау сұраныстарының кестесі
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS support_tickets (
        ticket_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        message_text TEXT,
        status TEXT DEFAULT 'open',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )""")
    
    # Жалпы баптаулар кестесі (мысалы, VIP ақпараты үшін)
    cursor.execute("CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT)")
    
    # Тексеру үшін алдын ала мәліметтерді қосу
    cursor.execute("SELECT key FROM settings WHERE key = 'vip_info'")
    if cursor.fetchone() is None:
        vip_text = """⭐️ VIP a'zolik afzalliklari:
1. VIP a'zolar uchun yaratilgan maxsus komandalarga kirish.
2. 1 oy davomida hech qanday kanalga obuna bo'lmasdan anime tomosha qilish."""
        cursor.execute("INSERT INTO settings (key, value) VALUES ('vip_info', ?)", (vip_text,))

    cursor.execute("SELECT code FROM anime WHERE code = '101'")
    if cursor.fetchone() is None:
        cursor.execute("INSERT INTO anime (code, name, description) VALUES (?, ?, ?)", 
                       ('101', 'Naruto', 'Mashhur shinobi animesi.'))

    conn.commit()
    conn.close()
    print("Дерекқор (база) барлық кестелерімен сәтті дайындалды.")

# --- Қолданушы функциялары ---
def add_user(user_id: int, username: str, first_name: str):
    query_db("INSERT OR IGNORE INTO users (user_id, username, first_name) VALUES (?, ?, ?)", (user_id, username, first_name))

def get_user_status(user_id: int) -> str:
    if user_id in HEAD_ADMINS:
        return 'bosh_admin'
    
    if query_db("SELECT user_id FROM admins WHERE user_id = ?", (user_id,), fetch="one"):
        return 'oddiy_admin'
    
    user_data = query_db("SELECT status FROM users WHERE user_id = ?", (user_id,), fetch="one")
    return user_data[0] if user_data and user_data[0] == 'vip' else 'user'
    
def get_all_user_ids():
    rows = query_db("SELECT user_id FROM users", fetch="all")
    return [row[0] for row in rows] if rows else []

def get_users_count():
    result = query_db("SELECT COUNT(*) FROM users", fetch="one")
    return result[0] if result else 0

# --- Админдерді басқару ---
def add_admin(user_id: int):
    if user_id in HEAD_ADMINS: return # Бас админді қосуға болмайды
    query_db("INSERT OR IGNORE INTO admins (user_id) VALUES (?)", (user_id,))

def remove_admin(user_id: int):
    if user_id in HEAD_ADMINS: return # Бас админді өшіруге болмайды
    query_db("DELETE FROM admins WHERE user_id = ?", (user_id,))

def get_all_admins():
    admins = query_db("SELECT user_id FROM admins", fetch="all")
    admin_ids = {admin[0] for admin in admins} if admins else set()
    admin_ids.update(HEAD_ADMINS)
    return list(admin_ids)

# --- Анимені басқару ---
def add_anime(code: str, name: str, description: str):
    query_db("INSERT OR IGNORE INTO anime (code, name, description) VALUES (?, ?, ?)", (code, name, description))

def get_anime_by_code(code: str):
    return query_db("SELECT id, code, name, description FROM anime WHERE code = ?", (code,), fetch="one")
    
def search_anime_by_name(name: str):
    return query_db("SELECT code, name, description FROM anime WHERE name LIKE ?", ('%' + name + '%',), fetch="all")

def delete_anime(code: str):
    query_db("DELETE FROM anime WHERE code = ?", (code,))
    
def get_all_anime():
    return query_db("SELECT code, name FROM anime ORDER BY code", fetch="all")
    
def get_anime_count():
    result = query_db("SELECT COUNT(*) FROM anime", fetch="one")
    return result[0] if result else 0

# --- Басқа функциялар ---
def get_setting(key: str):
    result = query_db("SELECT value FROM settings WHERE key = ?", (key,), fetch="one")
    return result[0] if result else None
    
def create_support_ticket(user_id: int, message: str):
    query_db("INSERT INTO support_tickets (user_id, message_text) VALUES (?, ?)", (user_id, message))
