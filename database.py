import sqlite3
import hashlib
from datetime import datetime, timedelta

def connect():
    return sqlite3.connect('education_platform.db', check_same_thread=False)

def create_database():
    conn = connect()
    cursor = conn.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE, password TEXT, role TEXT, last_seen TEXT)')
    cursor.execute('CREATE TABLE IF NOT EXISTS announcements (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, content TEXT, date TEXT, author TEXT)')
    # is_read sütunu mesajın okunup okunmadığını tutar
    cursor.execute('CREATE TABLE IF NOT EXISTS messages (id INTEGER PRIMARY KEY AUTOINCREMENT, sender TEXT, receiver TEXT, message TEXT, timestamp TEXT, is_read INTEGER DEFAULT 0)')
    cursor.execute('CREATE TABLE IF NOT EXISTS grades (id INTEGER PRIMARY KEY AUTOINCREMENT, student_username TEXT, lesson TEXT, grade INTEGER, date TEXT)')
    conn.commit()
    conn.close()

# --- KULLANICI ---
def add_user(username, password, role):
    conn = connect()
    try:
        hashed = hashlib.sha256(password.encode()).hexdigest()
        conn.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", (username, hashed, role))
        conn.commit()
        return True
    except sqlite3.IntegrityError: return False
    finally: conn.close()

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

# --- AKTİVİTE & MESAJLAŞMA ---
def update_activity(username):
    conn = connect()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn.execute("UPDATE users SET last_seen = ? WHERE username = ?", (now, username))
    conn.commit()
    conn.close()

def get_online_users(minutes=5):
    conn = connect()
    cursor = conn.execute("SELECT username, role, last_seen FROM users WHERE last_seen IS NOT NULL")
    users = cursor.fetchall()
    conn.close()
    online = []
    now = datetime.now()
    for u in users:
        try:
            last = datetime.strptime(u[2], "%Y-%m-%d %H:%M:%S")
            if now - last < timedelta(minutes=minutes):
                online.append({"Kullanıcı": u[0], "Rol": u[1], "Son İşlem": last.strftime("%H:%M")})
        except: pass
    return online

def send_message(sender, receiver, message):
    conn = connect()
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    conn.execute("INSERT INTO messages (sender, receiver, message, timestamp, is_read) VALUES (?, ?, ?, ?, 0)", (sender, receiver, message, now))
    conn.commit()
    conn.close()

def get_my_messages(username):
    # Tüm mesajları getirir
    conn = connect()
    msgs = conn.execute("SELECT id, sender, message, timestamp, is_read FROM messages WHERE receiver = ? ORDER BY id DESC", (username,)).fetchall()
    conn.close()
    return msgs

def get_unread_messages(username):
    # Sadece okunmamış mesajları getirir
    conn = connect()
    msgs = conn.execute("SELECT id, sender, message FROM messages WHERE receiver = ? AND is_read = 0", (username,)).fetchall()
    conn.close()
    return msgs

def mark_as_read(msg_id):
    # Mesajı okundu işaretler
    conn = connect()
    conn.execute("UPDATE messages SET is_read = 1 WHERE id = ?", (msg_id,))
    conn.commit()
    conn.close()

# --- DUYURU ---
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
