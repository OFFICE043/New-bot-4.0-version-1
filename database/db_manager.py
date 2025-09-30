# database/db_manager.py
import psycopg2
import logging
from contextlib import contextmanager
from config import DATABASE_URL, SUPER_ADMINS

logger = logging.getLogger(__name__)

@contextmanager
def get_db_connection():
    """PostgreSQL-мен қауіпсіз байланыс орнату үшін контекст менеджері."""
    try:
        conn = psycopg2.connect(DATABASE_URL)
        logger.info("Ma'lumotlar bazasiga muvaffaqiyatli ulanildi.")
        yield conn
    except psycopg2.OperationalError as e:
        logger.error(f"Ma'lumotlar bazasiga ulanishda xatolik: {e}")
        raise
    finally:
        if 'conn' in locals() and conn:
            conn.close()
            logger.info("Ma'lumotlar bazasi bilan aloqa uzildi.")

def init_db():
    """Деректер базасының кестелерін жасайды (егер олар жоқ болса)."""
    create_tables_sql = """
    CREATE TABLE IF NOT EXISTS users (
        user_id BIGINT PRIMARY KEY,
        role VARCHAR(20) NOT NULL DEFAULT 'user',
        username VARCHAR(255),
        first_name VARCHAR(255),
        join_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
    );
    CREATE TABLE IF NOT EXISTS animes (
        id SERIAL PRIMARY KEY,
        code VARCHAR(50) UNIQUE NOT NULL,
        name VARCHAR(255) NOT NULL,
        description TEXT,
        views BIGINT DEFAULT 0
    );
    """
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(create_tables_sql)
                
                # Super Admin-дерді базаға қосу/жаңарту
                for admin_id in SUPER_ADMINS:
                    cur.execute(
                        """
                        INSERT INTO users (user_id, role) VALUES (%s, 'admin')
                        ON CONFLICT (user_id) DO UPDATE SET role = 'admin';
                        """,
                        (admin_id,)
                    )
                conn.commit()
        logger.info("Barcha jadvallar muvaffaqiyatli yaratildi/tekshirildi.")
    except Exception as e:
        logger.error(f"Jadvallarni yaratishda xatolik: {e}")


# --- Пайдаланушылармен жұмыс істеу функциялары ---

def add_or_update_user(user_id: int, username: str, first_name: str):
    """Жаңа пайдаланушыны қосады немесе ескісінің деректерін жаңартады."""
    sql = """
    INSERT INTO users (user_id, username, first_name) VALUES (%s, %s, %s)
    ON CONFLICT (user_id) DO UPDATE SET 
        username = EXCLUDED.username, 
        first_name = EXCLUDED.first_name;
    """
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, (user_id, username, first_name))
                conn.commit()
    except Exception as e:
        logger.error(f"Foydalanuvchi {user_id} ni qo'shishda xatolik: {e}")

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
    """Анимені аты бойынша іздейді."""
    # Бұл жерде күрделірек іздеу логикасы болуы мүмкін (LIKE, ILIKE, Full-Text Search)
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
    """Анимені коды бойынша іздейді."""
    sql = "SELECT code, name, description FROM animes WHERE code = %s"
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, (code.upper(),))
                return cur.fetchone()
    except Exception as e:
        logger.error(f"'{code}' kodli anime izlashda xatolik: {e}")
        return None

# ... Басқа да ДБ функциялары...
