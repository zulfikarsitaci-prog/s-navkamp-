import sqlite3
import hashlib
import os
import streamlit as st
from datetime import datetime, timedelta

# --- VERİTABANI BAĞLANTI AYARLARI ---
# Eğer Streamlit Secrets içinde bağlantı bilgisi varsa PostgreSQL (Bulut) kullanır.
# Yoksa yerel SQLite dosyasını kullanır.

def get_db_connection():
    # 1. PostgreSQL (Bulut - Kalıcı) Kontrolü
    if "DATABASE_URL" in st.secrets:
        try:
            import psycopg2
            return psycopg2.connect(st.secrets["DATABASE_URL"]), "postgres"
        except ImportError:
            pass # Kütüphane yoksa SQLite'a düş
            
    # 2. SQLite (Yerel - Geçici)
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DB_PATH = os.path.join(BASE_DIR, "education_platform.db")
    return sqlite3.connect(DB_PATH, check_same_thread=False), "sqlite"

def run_query(query, params=(), fetch=False):
    conn, db_type = get_db_connection()
    cursor = conn.cursor()
    
    # Postgres için ? yerine %s kullanılması gerekir
    if db_type == "postgres":
        query = query.replace("?", "%s")
        # AUTOINCREMENT düzeltmesi
        query = query.replace("INTEGER PRIMARY KEY AUTOINCREMENT", "SERIAL PRIMARY KEY")
    
    try:
        cursor.execute(query, params)
        if fetch:
            result = cursor.fetchall()
            return result
        else:
            conn.commit()
            return True
    except Exception as e:
        return False
    finally:
        conn.close()

def create_database():
    # Tabloları oluştur (Her iki veritabanı türüyle uyumlu)
    tables = [
        'CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE, password TEXT, role TEXT, last_seen TEXT)',
        'CREATE TABLE IF NOT EXISTS announcements (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, content TEXT, date TEXT, author TEXT)',
        'CREATE TABLE IF NOT EXISTS messages (id INTEGER PRIMARY KEY AUTOINCREMENT, sender TEXT, receiver TEXT, message TEXT, timestamp TEXT, is_read INTEGER DEFAULT 0)',
        'CREATE TABLE IF NOT EXISTS global_messages (id INTEGER PRIMARY KEY AUTOINCREMENT, sender TEXT, message TEXT, timestamp TEXT)',
        'CREATE TABLE IF NOT EXISTS relationships (id INTEGER PRIMARY KEY AUTOINCREMENT, user1 TEXT, user2 TEXT, status TEXT)',
        'CREATE TABLE IF NOT EXISTS grades (id INTEGER PRIMARY KEY AUTOINCREMENT, student_username TEXT, lesson TEXT, grade INTEGER, date TEXT)'
    ]
    for table_sql in tables:
        run_query(table_sql)

# --- KULLANICI İŞLEMLERİ ---
def add_user(username, password, role):
    try:
        hashed = hashlib.sha256(password.encode()).hexdigest()
        return run_query("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", (username, hashed, role))
    except: return False

def login_user(username, password):
    hashed = hashlib.sha256(password.encode()).hexdigest()
    res = run_query("SELECT * FROM users WHERE username = ? AND password = ?", (username, hashed), fetch=True)
    return res[0] if res else None

def get_all_users():
    return run_query("SELECT username, role, last_seen FROM users", fetch=True)

def delete_user(username):
    run_query("DELETE FROM users WHERE username = ?", (username,))

# --- İLİŞKİLER ---
def send_friend_request(sender, receiver):
    check = run_query("SELECT * FROM relationships WHERE (user1=? AND user2=?) OR (user1=? AND user2=?)", (sender, receiver, receiver, sender), fetch=True)
    if not check:
        run_query("INSERT INTO relationships (user1, user2, status) VALUES (?, ?, ?)", (sender, receiver, 'pending'))
        return True, "İstek gönderildi."
    return False, "Zaten ekli veya istek var."

def get_pending_requests(username):
    return run_query("SELECT id, user1 FROM relationships WHERE user2=? AND status='pending'", (username,), fetch=True)

def accept_request(user1, user2):
    run_query("UPDATE relationships SET status='accepted' WHERE user1=? AND user2=?", (user1, user2))

def get_friends(username):
    rows = run_query("SELECT user1, user2 FROM relationships WHERE (user1=? OR user2=?) AND status='accepted'", (username, username), fetch=True)
    friends = []
    for r in rows:
        friends.append(r[1] if r[0] == username else r[0])
    return friends

def get_searchable_students(my_username):
    all_students = [u[0] for u in run_query("SELECT username FROM users WHERE role='student'", fetch=True)]
    my_friends = get_friends(my_username)
    return [s for s in all_students if s != my_username and s not in my_friends]

# --- AKTİVİTE & MESAJLAŞMA ---
def update_activity(username):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    run_query("UPDATE users SET last_seen = ? WHERE username = ?", (now, username))

def get_online_users(minutes=5):
    users = run_query("SELECT username, role, last_seen FROM users WHERE last_seen IS NOT NULL", fetch=True)
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
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    run_query("INSERT INTO messages (sender, receiver, message, timestamp, is_read) VALUES (?, ?, ?, ?, 0)", (sender, receiver, message, now))

def get_unread_messages(username):
    return run_query("SELECT id, sender, message FROM messages WHERE receiver = ? AND is_read = 0", (username,), fetch=True)

def mark_as_read(msg_id):
    run_query("UPDATE messages SET is_read = 1 WHERE id = ?", (msg_id,))

def mark_messages_as_read(receiver, sender):
    run_query("UPDATE messages SET is_read = 1 WHERE receiver = ? AND sender = ?", (receiver, sender))

def get_my_messages(username):
    return run_query("SELECT id, sender, message, timestamp, is_read FROM messages WHERE receiver = ? ORDER BY id DESC", (username,), fetch=True)

def get_conversation(user1, user2):
    return run_query("SELECT sender, message, timestamp FROM messages WHERE (sender = ? AND receiver = ?) OR (sender = ? AND receiver = ?) ORDER BY id ASC", (user1, user2, user2, user1), fetch=True)

# --- GENEL SOHBET ---
def send_global_message(sender, message):
    now = datetime.now().strftime("%H:%M")
    run_query("INSERT INTO global_messages (sender, message, timestamp) VALUES (?, ?, ?)", (sender, message, now))

def get_global_messages(limit=50):
    msgs = run_query("SELECT sender, message, timestamp FROM global_messages ORDER BY id DESC LIMIT 50", fetch=True) # Limit parametresi string içinde düzeltildi
    return msgs[::-1] if msgs else []

# --- DUYURU ---
def add_announcement(title, content, author):
    date = datetime.now().strftime("%Y-%m-%d %H:%M")
    run_query("INSERT INTO announcements (title, content, date, author) VALUES (?, ?, ?, ?)", (title, content, date, author))

def get_announcements():
    return run_query("SELECT * FROM announcements ORDER BY id DESC", fetch=True)
