import sqlite3
from config import HEAD_ADMINS # Бас админдер тізімін импорттау

DB_NAME = "bot_database.db"

def init_db():
    """Дерекқорды дайындау және қажетті кестелерді құру"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Қолданушылар кестесі (users)
    # status: 'user' (қарапайым), 'vip'
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        username TEXT,
        first_name TEXT,
        status TEXT DEFAULT 'user'
    )
    """)

    # Қарапайым админдер кестесі (admins)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS admins (
        user_id INTEGER PRIMARY KEY
    )
    """)
    
    # ... Болашақта аниме, каналдарға арналған кестелер осында қосылады ...

    conn.commit()
    conn.close()
    print("Дерекқор (база) сәтті дайындалды.")

def add_user(user_id: int, username: str, first_name: str):
    """Қолданушыны базаға қосу (егер ол бұрыннан жоқ болса)"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Қолданушының базада бар-жоғын тексеру
    cursor.execute("SELECT user_id FROM users WHERE user_id = ?", (user_id,))
    if cursor.fetchone() is None:
        # Егер жоқ болса, жаңадан қосу
        cursor.execute("INSERT INTO users (user_id, username, first_name) VALUES (?, ?, ?)",
                       (user_id, username, first_name))
        conn.commit()
    
    conn.close()

def get_user_status(user_id: int) -> str:
    """Қолданушының статусын анықтайтын негізгі функция"""
    # 1. Бас админ екенін config файлынан тексеру
    if user_id in HEAD_ADMINS:
        return 'bosh_admin'

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # 2. Қарапайым админ екенін базадағы 'admins' кестесінен тексеру
    cursor.execute("SELECT user_id FROM admins WHERE user_id = ?", (user_id,))
    if cursor.fetchone():
        conn.close()
        return 'oddiy_admin'
    
    # 3. VIP статусын базадағы 'users' кестесінен тексеру
    cursor.execute("SELECT status FROM users WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    conn.close()

    if result and result[0] == 'vip':
        return 'vip'
    
    # 4. Егер ешқайсысы болмаса, ол - қарапайым қолданушы
    return 'user'
