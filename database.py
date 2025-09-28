import os
import psycopg2
from psycopg2 import pool
from dotenv import load_dotenv
from config import HEAD_ADMINS

load_dotenv()

db_pool = None

def get_pool():
    """Байланыс пулын құру немесе қайтару"""
    global db_pool
    if db_pool is None:
        try:
            db_pool = psycopg2.pool.SimpleConnectionPool(
                minconn=1,
                maxconn=10,
                dsn=os.getenv("DATABASE_URL")
            )
            print("✅ PostgreSQL (Supabase) базасына қосылды!")
            init_db() # Бірінші рет қосылғанда кестелерді құру
        except psycopg2.OperationalError as e:
            print(f"❌ Базаға қосылу мүмкін болмады: {e}")
            db_pool = None
    return db_pool

def execute_query(query, params=None, fetch=None):
    """Базаға сұраныс жіберуге арналған негізгі функция (қателерді өңдеумен)"""
    conn = None
    pool = get_pool()
    if pool is None: return None
    try:
        conn = pool.getconn()
        with conn.cursor() as cursor:
            cursor.execute(query, params)
            if fetch == "one": return cursor.fetchone()
            if fetch == "all": return cursor.fetchall()
            conn.commit()
    except psycopg2.Error as e:
        print(f"❌ Сұраныс орындауда қате: {e}")
        # Қате болған жағдайда транзакцияны қайтару
        if conn: conn.rollback()
        return None
    finally:
        if conn: pool.putconn(conn)

def init_db():
    """Барлық қажетті кестелерді құру"""
    commands = [
        """CREATE TABLE IF NOT EXISTS users (
            user_id BIGINT PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            status TEXT DEFAULT 'user',
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        )""",
        "CREATE TABLE IF NOT EXISTS admins (user_id BIGINT PRIMARY KEY)",
        """CREATE TABLE IF NOT EXISTS anime (
            id SERIAL PRIMARY KEY,
            code TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            description TEXT,
            post_link TEXT,
            view_count INTEGER DEFAULT 0
        )""",
        """CREATE TABLE IF NOT EXISTS support_tickets (
            ticket_id SERIAL PRIMARY KEY,
            user_id BIGINT,
            message_text TEXT,
            status TEXT DEFAULT 'open',
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        )""",
        "CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT)"
    ]
    for command in commands:
        execute_query(command)
    
    # Алдын ала мәліметтерді қосу
    vip_info_check = execute_query("SELECT key FROM settings WHERE key = 'vip_info'", fetch="one")
    if not vip_info_check:
        vip_text = """⭐️ VIP a'zolik afzalliklari:
1. VIP a'zolar uchun yaratilgan maxsus komandalarga kirish.
2. 1 oy davomida hech qanday kanalga obuna bo'lmasdan anime tomosha qilish."""
        execute_query("INSERT INTO settings (key, value) VALUES (%s, %s)", ('vip_info', vip_text))

    print("База кестелері дайын.")

# --- Қолданушы функциялары ---
def add_user(user_id: int, username: str, first_name: str):
    query = "INSERT INTO users (user_id, username, first_name) VALUES (%s, %s, %s) ON CONFLICT (user_id) DO NOTHING"
    execute_query(query, (user_id, username, first_name))

def get_user_status(user_id: int) -> str:
    if user_id in HEAD_ADMINS: return 'bosh_admin'
    if execute_query("SELECT user_id FROM admins WHERE user_id = %s", (user_id,), fetch="one"): return 'oddiy_admin'
    user_data = execute_query("SELECT status FROM users WHERE user_id = %s", (user_id,), fetch="one")
    return user_data[0] if user_data and user_data[0] == 'vip' else 'user'

# ... (Басқа барлық қажетті функциялар осындай стильде жазылады) ...
# ... (add_anime, search_anime, add_admin, remove_admin, etc.) ...
