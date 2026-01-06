import sqlite3
import hashlib
import os
from datetime import datetime, timedelta

# --- VERİTABANI DOSYA YOLUNU SABİTLEME ---
# Bu ayar, uygulamanın çalıştığı klasörü bulur ve db dosyasını oraya sabitler.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "education_platform.db")

def connect():
    return sqlite3.connect(DB_PATH, check_same_thread=False)

def create_database():
    conn = connect()
    cursor = conn.cursor()
    # Temel Tablolar
    cursor.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE, password TEXT, role TEXT, last_seen TEXT)')
    cursor.execute('CREATE TABLE IF NOT EXISTS announcements (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, content TEXT, date TEXT, author TEXT)')
    cursor.execute('CREATE TABLE IF NOT EXISTS messages (id INTEGER PRIMARY KEY AUTOINCREMENT, sender TEXT, receiver TEXT, message TEXT, timestamp TEXT, is_read INTEGER DEFAULT 0)')
    # Genel Sohbet
    cursor.execute('CREATE TABLE IF NOT EXISTS global_messages (id INTEGER PRIMARY KEY AUTOINCREMENT, sender TEXT, message TEXT, timestamp TEXT)')
    # İlişkiler (Arkadaşlık)
    cursor.execute('CREATE TABLE IF NOT EXISTS relationships (id INTEGER PRIMARY KEY AUTOINCREMENT, user1 TEXT, user2 TEXT, status TEXT)')
    # Notlar/Puanlar
    cursor.execute('CREATE TABLE IF NOT EXISTS grades (id INTEGER PRIMARY KEY AUTOINCREMENT, student_username TEXT, lesson TEXT, grade INTEGER, date TEXT)')
    
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

# --- TAKİPLEŞME ---
def send_friend_request(sender, receiver):
    conn = connect()
    check = conn.execute("SELECT * FROM relationships WHERE (user1=? AND user2=?) OR (user1=? AND user2=?)", (sender, receiver, receiver, sender)).fetchone()
    if not check:
        conn.execute("INSERT INTO relationships (user1, user2, status) VALUES (?, ?, ?)", (sender, receiver, 'pending'))
        conn.commit()
        conn.close()
        return True, "İstek gönderildi."
    conn.close()
    return False, "Zaten ekli veya istek var."

def get_pending_requests(username):
    conn = connect()
    reqs = conn.execute("SELECT id, user1 FROM relationships WHERE user2=? AND status='pending'", (username,)).fetchall()
    conn.close()
    return reqs

def accept_request(user1, user2):
    conn = connect()
    conn.execute("UPDATE relationships SET status='accepted' WHERE user1=? AND user2=?", (user1, user2))
    conn.commit()
    conn.close()

def get_friends(username):
    conn = connect()
    rows = conn.execute("SELECT user1, user2 FROM relationships WHERE (user1=? OR user2=?) AND status='accepted'", (username, username)).fetchall()
    conn.close()
    friends = []
    for r in rows:
        if r[0] == username: friends.append(r[1])
        else: friends.append(r[0])
    return friends

def get_searchable_students(my_username):
    conn = connect()
    all_students = [u[0] for u in conn.execute("SELECT username FROM users WHERE role='student'").fetchall()]
    conn.close()
    my_friends = get_friends(my_username)
    searchable = [s for s in all_students if s != my_username and s not in my_friends]
    return searchable

# --- AKTİVİTE ---
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

# --- ÖZEL MESAJLAŞMA ---
def send_message(sender, receiver, message):
    conn = connect()
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    conn.execute("INSERT INTO messages (sender, receiver, message, timestamp, is_read) VALUES (?, ?, ?, ?, 0)", (sender, receiver, message, now))
    conn.commit()
    conn.close()

def get_unread_messages(username):
    conn = connect()
    msgs = conn.execute("SELECT id, sender, message FROM messages WHERE receiver = ? AND is_read = 0", (username,)).fetchall()
    conn.close()
    return msgs

def mark_as_read(msg_id):
    conn = connect()
    conn.execute("UPDATE messages SET is_read = 1 WHERE id = ?", (msg_id,))
    conn.commit()
    conn.close()

def mark_messages_as_read(receiver, sender):
    conn = connect()
    conn.execute("UPDATE messages SET is_read = 1 WHERE receiver = ? AND sender = ?", (receiver, sender))
    conn.commit()
    conn.close()

def get_my_messages(username):
    conn = connect()
    msgs = conn.execute("SELECT id, sender, message, timestamp, is_read FROM messages WHERE receiver = ? ORDER BY id DESC", (username,)).fetchall()
    conn.close()
    return msgs

def get_conversation(user1, user2):
    conn = connect()
    sql = "SELECT sender, message, timestamp FROM messages WHERE (sender = ? AND receiver = ?) OR (sender = ? AND receiver = ?) ORDER BY id ASC"
    msgs = conn.execute(sql, (user1, user2, user2, user1)).fetchall()
    conn.close()
    return msgs

# --- GENEL SOHBET ---
def send_global_message(sender, message):
    conn = connect()
    now = datetime.now().strftime("%H:%M")
    conn.execute("INSERT INTO global_messages (sender, message, timestamp) VALUES (?, ?, ?)", (sender, message, now))
    conn.commit()
    conn.close()

def get_global_messages(limit=50):
    conn = connect()
    msgs = conn.execute("SELECT sender, message, timestamp FROM global_messages ORDER BY id DESC LIMIT ?", (limit,)).fetchall()
    conn.close()
    return msgs[::-1]

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
