# database/db_manager.py
# (Файлдың басы өзгеріссіз қалады...)
# ... get_db_connection(), init_db(), add_or_update_user(), get_user_role() функцияларынан кейін...

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
    """Барлық анимелер тізімін беттеп қайтарады."""
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
    """Ең көп көрілген анимелер тізімін қайтарады."""
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
    """Белгілі бір баптаудың мәнін қайтарады (мысалы, vip_description)."""
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
