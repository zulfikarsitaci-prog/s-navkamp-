import sqlite3
import hashlib
import os
import streamlit as st
from datetime import datetime, timedelta

def get_db_connection():
    # 1. Neon (PostgreSQL) Bağlantısı
    if "DATABASE_URL" in st.secrets:
        try:
            import psycopg2
            return psycopg2.connect(st.secrets["DATABASE_URL"]), "postgres"
        except ImportError:
            pass 
            
    # 2. Yerel (SQLite) Bağlantısı
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DB_PATH = os.path.join(BASE_DIR, "education_platform.db")
    return sqlite3.connect(DB_PATH, check_same_thread=False), "sqlite"

def run_query(query, params=(), fetch=False):
    conn, db_type = get_db_connection()
    cursor = conn.cursor()
    
    if db_type == "postgres":
        query = query.replace("?", "%s")
        query = query.replace("INTEGER PRIMARY KEY AUTOINCREMENT", "SERIAL PRIMARY KEY")
    
    try:
        cursor.execute(query, params)
        if fetch:
            return cursor.fetchall()
        else:
            conn.commit()
            return True
    except Exception as e:
        return False
    finally:
        conn.close()

def create_database():
    tables = [
        'CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE, password TEXT, role TEXT, last_seen TEXT)',
        'CREATE TABLE IF NOT EXISTS announcements (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, content TEXT, date TEXT, author TEXT)',
        'CREATE TABLE IF NOT EXISTS messages (id INTEGER PRIMARY KEY AUTOINCREMENT, sender TEXT, receiver TEXT, message TEXT, timestamp TEXT, is_read INTEGER DEFAULT 0)',
        'CREATE TABLE IF NOT EXISTS global_messages (id INTEGER PRIMARY KEY AUTOINCREMENT, sender TEXT, message TEXT, timestamp TEXT)',
        'CREATE TABLE IF NOT EXISTS relationships (id INTEGER PRIMARY KEY AUTOINCREMENT, user1 TEXT, user2 TEXT, status TEXT)',
        'CREATE TABLE IF NOT EXISTS grades (id INTEGER PRIMARY KEY AUTOINCREMENT, student_username TEXT, lesson TEXT, grade INTEGER, date TEXT)'
    ]
    for t in tables: run_query(t)

# --- KULLANICI İŞLEMLERİ ---
def add_user(u, p, r):
    try:
        h = hashlib.sha256(p.encode()).hexdigest()
        return run_query("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", (u, h, r))
    except: return False

def login_user(u, p):
    h = hashlib.sha256(p.encode()).hexdigest()
    res = run_query("SELECT * FROM users WHERE username = ? AND password = ?", (u, h), fetch=True)
    return res[0] if res else None

# EKSİK OLAN FONKSİYON (EKLENDİ)
def get_all_users():
    return run_query("SELECT username, role, last_seen FROM users", fetch=True)

# EKSİK OLAN FONKSİYON (EKLENDİ)
def delete_user(username):
    run_query("DELETE FROM users WHERE username = ?", (username,))

# --- AKTİVİTE ---
def update_activity(u):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    run_query("UPDATE users SET last_seen = ? WHERE username = ?", (now, u))

def get_online_users(minutes=5):
    users = run_query("SELECT username, role, last_seen FROM users WHERE last_seen IS NOT NULL", fetch=True)
    online = []
    now = datetime.now()
    for u in users:
        try:
            last = datetime.strptime(u[2], "%Y-%m-%d %H:%M:%S")
            if now - last < timedelta(minutes=minutes): online.append({"Kullanıcı": u[0], "Rol": u[1], "Son İşlem": last.strftime("%H:%M")})
        except: pass
    return online

# --- MESAJLAŞMA ---
def send_message(s, r, m):
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    run_query("INSERT INTO messages (sender, receiver, message, timestamp, is_read) VALUES (?, ?, ?, ?, 0)", (s, r, m, now))

def get_unread_messages(u):
    return run_query("SELECT id, sender, message FROM messages WHERE receiver = ? AND is_read = 0", (u,), fetch=True)

def get_my_messages(u):
    return run_query("SELECT id, sender, message, timestamp, is_read FROM messages WHERE receiver = ? ORDER BY id DESC", (u,), fetch=True)

def mark_messages_as_read(r, s):
    run_query("UPDATE messages SET is_read = 1 WHERE receiver = ? AND sender = ?", (r, s))

def mark_as_read(msg_id):
    run_query("UPDATE messages SET is_read = 1 WHERE id = ?", (msg_id,))

def get_conversation(u1, u2):
    return run_query("SELECT sender, message, timestamp FROM messages WHERE (sender = ? AND receiver = ?) OR (sender = ? AND receiver = ?) ORDER BY id ASC", (u1, u2, u2, u1), fetch=True)

def send_global_message(s, m):
    now = datetime.now().strftime("%H:%M")
    run_query("INSERT INTO global_messages (sender, message, timestamp) VALUES (?, ?, ?)", (s, m, now))

def get_global_messages(limit=50):
    msgs = run_query("SELECT sender, message, timestamp FROM global_messages ORDER BY id DESC LIMIT 50", fetch=True)
    return msgs[::-1] if msgs else []

# --- ARKADAŞLIK ---
def send_friend_request(s, r):
    if not run_query("SELECT * FROM relationships WHERE (user1=? AND user2=?) OR (user1=? AND user2=?)", (s, r, r, s), fetch=True):
        run_query("INSERT INTO relationships (user1, user2, status) VALUES (?, ?, ?)", (s, r, 'pending'))
        return True, "İstek gönderildi."
    return False, "Zaten ekli."

def get_pending_requests(u): return run_query("SELECT id, user1 FROM relationships WHERE user2=? AND status='pending'", (u,), fetch=True)
def accept_request(u1, u2): run_query("UPDATE relationships SET status='accepted' WHERE user1=? AND user2=?", (u1, u2))
def get_friends(u):
    rows = run_query("SELECT user1, user2 FROM relationships WHERE (user1=? OR user2=?) AND status='accepted'", (u, u), fetch=True)
    return [r[1] if r[0] == u else r[0] for r in rows]
def get_searchable_students(my_u):
    all_s = [u[0] for u in run_query("SELECT username FROM users WHERE role='student'", fetch=True)]
    friends = get_friends(my_u)
    return [s for s in all_s if s != my_u and s not in friends]

# --- NOTLAR ---
def add_announcement(t, c, a):
    d = datetime.now().strftime("%Y-%m-%d %H:%M")
    run_query("INSERT INTO announcements (title, content, date, author) VALUES (?, ?, ?, ?)", (t, c, d, a))
def get_announcements(): return run_query("SELECT * FROM announcements ORDER BY id DESC", fetch=True)
