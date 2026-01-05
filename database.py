import sqlite3
import hashlib
from datetime import datetime, timedelta

def connect():
    return sqlite3.connect('education_platform.db', check_same_thread=False)

def create_database():
    conn = connect()
    cursor = conn.cursor()
    
    # Kullanıcılar Tablosu (last_seen eklendi)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users
        (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE, password TEXT, role TEXT, last_seen TEXT)
    ''')
    
    # Duyurular
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS announcements
        (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, content TEXT, date TEXT, author TEXT)
    ''')
    
    # Mesajlar Tablosu (YENİ)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages
        (id INTEGER PRIMARY KEY AUTOINCREMENT, sender TEXT, receiver TEXT, message TEXT, timestamp TEXT, is_read INTEGER DEFAULT 0)
    ''')
    
    conn.commit()
    conn.close()

# --- KULLANICI İŞLEMLERİ ---
def add_user(username, password, role):
    conn = connect()
    try:
        hashed = hashlib.sha256(password.encode()).hexdigest()
        conn.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", (username, hashed, role))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def login_user(username, password):
    conn = connect()
    hashed = hashlib.sha256(password.encode()).hexdigest()
    cursor = conn.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, hashed))
    user = cursor.fetchone()
    conn.close()
    return user

def get_all_users():
    conn = connect()
    users = conn.execute("SELECT username, role, last_seen FROM users").fetchall()
    conn.close()
    return users

def delete_user(username):
    conn = connect()
    conn.execute("DELETE FROM users WHERE username = ?", (username,))
    conn.commit()
    conn.close()

# --- AKTİVİTE VE MESAJLAŞMA (YENİ) ---
def update_activity(username):
    """Kullanıcının son görülme zamanını günceller"""
    conn = connect()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn.execute("UPDATE users SET last_seen = ? WHERE username = ?", (now, username))
    conn.commit()
    conn.close()

def get_online_users(minutes_threshold=5):
    """Son X dakikada aktif olan kullanıcıları getirir"""
    conn = connect()
    cursor = conn.cursor()
    # SQLite'da tarih karşılaştırması string üzerinden yapılır, Python tarafında filtrelemek daha güvenlidir.
    cursor.execute("SELECT username, role, last_seen FROM users WHERE last_seen IS NOT NULL")
    all_users = cursor.fetchall()
    conn.close()
    
    online_users = []
    now = datetime.now()
    for u in all_users:
        try:
            last_seen = datetime.strptime(u[2], "%Y-%m-%d %H:%M:%S")
            if now - last_seen < timedelta(minutes=minutes_threshold):
                online_users.append({"username": u[0], "role": u[1], "time": u[2]})
        except: pass
    return online_users

def send_message(sender, receiver, message):
    conn = connect()
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    conn.execute("INSERT INTO messages (sender, receiver, message, timestamp) VALUES (?, ?, ?, ?)", (sender, receiver, message, now))
    conn.commit()
    conn.close()

def get_my_messages(username):
    conn = connect()
    msgs = conn.execute("SELECT sender, message, timestamp FROM messages WHERE receiver = ? ORDER BY id DESC", (username,)).fetchall()
    conn.close()
    return msgs

# --- DUYURULAR ---
def add_announcement(title, content, author):
    conn = connect()
    date = datetime.now().strftime("%Y-%m-%d %H:%M")
    conn.execute("INSERT INTO announcements (title, content, date, author) VALUES (?, ?, ?, ?)", (title, content, date, author))
    conn.commit()
    conn.close()

def get_announcements():
    conn = connect()
    anns = conn.execute("SELECT * FROM announcements ORDER BY id DESC").fetchall()
    conn.close()
    return anns
