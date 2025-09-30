# database/db_manager.py
import psycopg2
import logging
from contextlib import contextmanager
from config import DATABASE_URL, SUPER_ADMINS

logger = logging.getLogger(__name__)

@contextmanager
def get_db_connection():
    """PostgreSQL-мен қауіпсіз байланыс орнату."""
    conn = None
    try:
        conn = psycopg2.connect(DATABASE_URL)
        yield conn
    except psycopg2.OperationalError as e:
        logger.error(f"Ma'lumotlar bazasiga ulanishda xatolik yuz berdi: {e}")
        raise
    finally:
        if conn:
            conn.close()

def init_db():
    """Бот іске қосылғанда барлық кестелерді жасайды немесе тексереді."""
    create_tables_sql = """
    CREATE TABLE IF NOT EXISTS users (
        user_id BIGINT PRIMARY KEY,
        role VARCHAR(20) NOT NULL DEFAULT 'user', -- 'user', 'vip', 'admin'
        username VARCHAR(255),
        first_name VARCHAR(255),
        vip_expires_at TIMESTAMP WITH TIME ZONE,
        join_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
    );
    CREATE TABLE IF NOT EXISTS animes (
        id SERIAL PRIMARY KEY,
        code VARCHAR(50) UNIQUE NOT NULL,
        name VARCHAR(255) NOT NULL,
        description TEXT,
        views BIGINT DEFAULT 0
    );
    CREATE TABLE IF NOT EXISTS settings (
        key VARCHAR(255) PRIMARY KEY,
        value TEXT
    );
    """
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(create_tables_sql)
                # Бастапқы VIP сипаттамасын қосу
                cur.execute(
                    "INSERT INTO settings (key, value) VALUES (%s, %s) ON CONFLICT (key) DO NOTHING",
                    ('vip_description', "👑 VIP a'zolik haqida ma'lumot shu yerda bo'ladi.")
                )
                for admin_id in SUPER_ADMINS:
                    cur.execute(
                        "INSERT INTO users (user_id, role) VALUES (%s, 'admin') ON CONFLICT (user_id) DO UPDATE SET role = 'admin';",
                        (admin_id,)
                    )
                conn.commit()
        logger.info("Barcha jadvallar muvaffaqiyatli yaratildi/tekshirildi.")
    except Exception as e:
        logger.error(f"Jadvallarni yaratishda xatolik: {e}")

def add_or_update_user(user_id: int, username: str, first_name: str):
    """Жаңа пайдаланушыны қосады немесе ескісінің деректерін жаңартады."""
    sql = "INSERT INTO users (user_id, username, first_name) VALUES (%s, %s, %s) ON CONFLICT (user_id) DO UPDATE SET username = EXCLUDED.username, first_name = EXCLUDED.first_name;"
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, (user_id, username, first_name))
                conn.commit()
    except Exception as e:
        logger.error(f"Foydalanuvchi {user_id} ni qo'shishda/yangilashda xatolik: {e}")

def get_user_role(user_id: int) -> str:
    """Пайдаланушының рөлін (user, vip, admin) қайтарады."""
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT role FROM users WHERE user_id = %s", (user_id,))
                result = cur.fetchone()
                return result[0] if result else 'user'
    except Exception as e:
        logger.error(f"Foydalanuvchi {user_id} rolini olishda xatolik: {e}")
        return 'user'

# --- Анимемен жұмыс істеу функциялары ---

def find_anime_by_name(name_query: str):
    sql = "SELECT code, name, description FROM animes WHERE name ILIKE %s"
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, (f'%{name_query}%',))
                return cur.fetchone()
    except Exception as e:
        logger.error(f"'{name_query}' animesini izlashda xatolik: {e}")
        return None
        
def find_anime_by_code(code: str):
    sql = "SELECT code, name, description FROM animes WHERE code = %s"
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, (code.upper(),))
                return cur.fetchone()
    except Exception as e:
        logger.error(f"'{code}' kodli anime izlashda xatolik: {e}")
        return None

def get_all_animes_paginated(page: int = 1, limit: int = 10):
    offset = (page - 1) * limit
    sql = "SELECT code, name FROM animes ORDER BY name LIMIT %s OFFSET %s"
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, (limit, offset))
                return cur.fetchall()
    except Exception as e:
        logger.error(f"Animelar ro'yxatini olishda xatolik: {e}")
        return []

def get_top_viewed_animes(limit: int = 20):
    sql = "SELECT code, name, views FROM animes ORDER BY views DESC LIMIT %s"
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, (limit,))
                return cur.fetchall()
    except Exception as e:
        logger.error(f"Eng ko'p ko'rilgan animelarni olishda xatolik: {e}")
        return []

# --- Баптаулармен жұмыс ---
def get_setting(key: str) -> str:
    sql = "SELECT value FROM settings WHERE key = %s"
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, (key,))
                result = cur.fetchone()
                return result[0] if result else None
    except Exception as e:
        logger.error(f"'{key}' sozlamasini olishda xatolik: {e}")
        return None
