import sqlite3
import hashlib
import os
import streamlit as st
from datetime import datetime
import psycopg2

# --- BAĞLANTIYI HAFIZADA TUT (CACHE) ---
@st.cache_resource(ttl=3600)  # 1 Saat boyunca bağlantıyı koparma
def get_db_connection():
    if "DATABASE_URL" in st.secrets:
        try:
            conn = psycopg2.connect(st.secrets["DATABASE_URL"])
            return conn, "postgres"
        except: return None, None
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DB_PATH = os.path.join(BASE_DIR, "education_platform.db")
    return sqlite3.connect(DB_PATH, check_same_thread=False), "sqlite"

def run_query(query, params=(), fetch=False):
    conn, db_type = get_db_connection()
    if not conn: return False
    
    # Bağlantı koptuysa hafızayı temizle ve tekrar bağlan
    if db_type == "postgres" and conn.closed != 0:
        st.cache_resource.clear()
        conn, db_type = get_db_connection()

    cursor = conn.cursor()
    if db_type == "postgres":
        query = query.replace("?", "%s").replace("INTEGER PRIMARY KEY AUTOINCREMENT", "SERIAL PRIMARY KEY")
    
    try:
        cursor.execute(query, params)
        if fetch: return cursor.fetchall()
        else: conn.commit(); return True
    except:
        try: conn.rollback()
        except: pass
        return False
    finally: cursor.close()

def create_database():
    tables = [
        'CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE, password TEXT, role TEXT, last_seen TEXT, avatar_data TEXT)',
        'CREATE TABLE IF NOT EXISTS announcements (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, content TEXT, date TEXT, author TEXT)',
        'CREATE TABLE IF NOT EXISTS messages (id INTEGER PRIMARY KEY AUTOINCREMENT, sender TEXT, receiver TEXT, message TEXT, timestamp TEXT, is_read INTEGER DEFAULT 0)',
        'CREATE TABLE IF NOT EXISTS global_messages (id INTEGER PRIMARY KEY AUTOINCREMENT, sender TEXT, message TEXT, timestamp TEXT)',
        'CREATE TABLE IF NOT EXISTS relationships (id INTEGER PRIMARY KEY AUTOINCREMENT, user1 TEXT, user2 TEXT, status TEXT)',
        'CREATE TABLE IF NOT EXISTS grades (id INTEGER PRIMARY KEY AUTOINCREMENT, student_username TEXT, lesson TEXT, grade INTEGER, date TEXT)',
        'CREATE TABLE IF NOT EXISTS posts (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, content TEXT, image_data TEXT, timestamp TEXT, likes INTEGER DEFAULT 0)',
        'CREATE TABLE IF NOT EXISTS comments (id INTEGER PRIMARY KEY AUTOINCREMENT, post_id INTEGER, username TEXT, content TEXT, timestamp TEXT)'
    ]
    for t in tables: run_query(t)
    try: run_query("ALTER TABLE users ADD COLUMN avatar_data TEXT")
    except: pass

# --- ÖNBELLEKLİ VERİ ÇEKME FONKSİYONLARI ---
# Bu fonksiyonlar veriyi her seferinde internetten çekmez, hafızadan getirir.

@st.cache_data(ttl=3) # 3 saniyede bir yenile (Anlık hız için)
def get_posts(limit=20):
    return run_query("SELECT id, username, content, image_data, timestamp, likes FROM posts ORDER BY id DESC LIMIT ?", (limit,), fetch=True) or []

@st.cache_data(ttl=5)
def get_comments(post_id):
    return run_query("SELECT username, content, timestamp FROM comments WHERE post_id = ? ORDER BY id ASC", (post_id,), fetch=True) or []

@st.cache_data(ttl=10)
def get_leaderboard_data(): # Bu özel fonksiyonu app.py içinde kullanacağız
    return run_query("SELECT student_username, SUM(grade) as total FROM grades GROUP BY student_username ORDER BY total DESC", fetch=True) or []

@st.cache_data(ttl=60)
def get_avatar(u):
    try: return run_query("SELECT avatar_data FROM users WHERE username = ?", (u,), fetch=True)[0][0]
    except: return None

@st.cache_data(ttl=5)
def get_total_score(u):
    res = run_query("SELECT SUM(grade) FROM grades WHERE student_username = ?", (u,), fetch=True)
    return res[0][0] if res and res[0][0] else 0

# --- YAZMA İŞLEMLERİ (CACHE YOK - ANINDA GİTMELİ) ---
def add_user(u, p, r):
    try:
        h = hashlib.sha256(p.encode()).hexdigest()
        return run_query("INSERT INTO users (username, password, role, avatar_data) VALUES (?, ?, ?, ?)", (u, h, r, None))
    except: return False

def login_user(u, p):
    h = hashlib.sha256(p.encode()).hexdigest()
    res = run_query("SELECT id, username, password, role FROM users WHERE username = ? AND password = ?", (u, h), fetch=True)
    return res[0] if res else None

def get_user_role(u):
    res = run_query("SELECT role FROM users WHERE username = ?", (u,), fetch=True)
    return res[0][0] if res and res[0] else None

def update_avatar(u, img_data):
    run_query("UPDATE users SET avatar_data = ? WHERE username = ?", (img_data, u))
    get_avatar.clear() # Cache'i temizle ki yeni resim görünsün

def add_score(u, a, s="Sistem"):
    d = datetime.now().strftime("%Y-%m-%d %H:%M")
    run_query("INSERT INTO grades (student_username, lesson, grade, date) VALUES (?, ?, ?, ?)", (u, s, a, d))
    get_total_score.clear() # Puan değişince hafızayı temizle

def get_all_users(): return run_query("SELECT username, role, last_seen FROM users", fetch=True) or []
def delete_user(u): run_query("DELETE FROM users WHERE username = ?", (u,))
def update_activity(u):
    n = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    run_query("UPDATE users SET last_seen = ? WHERE username = ?", (n, u))

def add_post(u, c, i=None):
    t = datetime.now().strftime("%Y-%m-%d %H:%M")
    run_query("INSERT INTO posts (username, content, image_data, timestamp, likes) VALUES (?, ?, ?, ?, 0)", (u, c, i, t))
    get_posts.clear() # Yeni post atılınca listeyi yenile

def like_post(id): 
    run_query("UPDATE posts SET likes = likes + 1 WHERE id = ?", (id,))
    get_posts.clear()

def delete_post(post_id):
    run_query("DELETE FROM comments WHERE post_id = ?", (post_id,))
    run_query("DELETE FROM posts WHERE id = ?", (post_id,))
    get_posts.clear()

def update_post(post_id, new_content):
    run_query("UPDATE posts SET content = ? WHERE id = ?", (new_content, post_id))
    get_posts.clear()

def add_comment(pid, u, c):
    t = datetime.now().strftime("%Y-%m-%d %H:%M")
    run_query("INSERT INTO comments (post_id, username, content, timestamp) VALUES (?, ?, ?, ?)", (pid, u, c, t))
    get_comments.clear() # Yorum atılınca o postun yorumlarını yenile

def send_message(s, r, m):
    n = datetime.now().strftime("%Y-%m-%d %H:%M")
    run_query("INSERT INTO messages (sender, receiver, message, timestamp, is_read) VALUES (?, ?, ?, ?, 0)", (s, r, m, n))

def get_unread_messages(u): return run_query("SELECT id, sender, message FROM messages WHERE receiver = ? AND is_read = 0", (u,), fetch=True) or []
def get_my_messages(u): return run_query("SELECT id, sender, message, timestamp, is_read FROM messages WHERE receiver = ? ORDER BY id DESC", (u,), fetch=True) or []
def mark_messages_as_read(r, s): run_query("UPDATE messages SET is_read = 1 WHERE receiver = ? AND sender = ?", (r, s))
def mark_as_read(mid): run_query("UPDATE messages SET is_read = 1 WHERE id = ?", (mid,))
def get_conversation(u1, u2): return run_query("SELECT sender, message, timestamp FROM messages WHERE (sender = ? AND receiver = ?) OR (sender = ? AND receiver = ?) ORDER BY id ASC", (u1, u2, u2, u1), fetch=True) or []
def send_global_message(s, m):
    n = datetime.now().strftime("%H:%M")
    run_query("INSERT INTO global_messages (sender, message, timestamp) VALUES (?, ?, ?)", (s, m, n))
def get_global_messages(limit=50): return run_query("SELECT sender, message, timestamp FROM global_messages ORDER BY id DESC LIMIT 50", fetch=True) or []
def send_friend_request(s, r):
    if not run_query("SELECT * FROM relationships WHERE (user1=? AND user2=?) OR (user1=? AND user2=?)", (s, r, r, s), fetch=True):
        run_query("INSERT INTO relationships (user1, user2, status) VALUES (?, ?, ?)", (s, r, 'pending')); return True, "İstek yollandı."
    return False, "Ekli."
def get_pending_requests(u): return run_query("SELECT id, user1 FROM relationships WHERE user2=? AND status='pending'", (u,), fetch=True) or []
def accept_request(u1, u2): run_query("UPDATE relationships SET status='accepted' WHERE user1=? AND user2=?", (u1, u2))
def get_friends(u):
    rows = run_query("SELECT user1, user2 FROM relationships WHERE (user1=? OR user2=?) AND status='accepted'", (u, u), fetch=True)
    return [r[1] if r[0] == u else r[0] for r in rows] if rows else []
def get_searchable_students(my_u):
    all_s = [u[0] for u in run_query("SELECT username FROM users WHERE role='student'", fetch=True) or []]
    return [s for s in all_s if s != my_u and s not in get_friends(my_u)]
def add_announcement(t, c, a):
    d = datetime.now().strftime("%Y-%m-%d %H:%M")
    run_query("INSERT INTO announcements (title, content, date, author) VALUES (?, ?, ?, ?)", (t, c, d, a))
def get_announcements(): return run_query("SELECT * FROM announcements ORDER BY id DESC", fetch=True) or []
