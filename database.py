import sqlite3
import hashlib
import os
import streamlit as st
from datetime import datetime
import psycopg2
from PIL import Image
import io
import base64

@st.cache_resource(ttl=3600)
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
    if db_type == "postgres" and conn.closed != 0:
        st.cache_resource.clear(); conn, db_type = get_db_connection()
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
        'CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE, password TEXT, role TEXT, last_seen TEXT, avatar_data TEXT, frame TEXT, name_style TEXT, post_style TEXT)',
        'CREATE TABLE IF NOT EXISTS announcements (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, content TEXT, date TEXT, author TEXT)',
        'CREATE TABLE IF NOT EXISTS messages (id INTEGER PRIMARY KEY AUTOINCREMENT, sender TEXT, receiver TEXT, message TEXT, timestamp TEXT, is_read INTEGER DEFAULT 0)',
        'CREATE TABLE IF NOT EXISTS global_messages (id INTEGER PRIMARY KEY AUTOINCREMENT, sender TEXT, message TEXT, timestamp TEXT)',
        'CREATE TABLE IF NOT EXISTS relationships (id INTEGER PRIMARY KEY AUTOINCREMENT, user1 TEXT, user2 TEXT, status TEXT)',
        'CREATE TABLE IF NOT EXISTS grades (id INTEGER PRIMARY KEY AUTOINCREMENT, student_username TEXT, lesson TEXT, grade INTEGER, date TEXT)',
        'CREATE TABLE IF NOT EXISTS posts (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, content TEXT, image_data TEXT, timestamp TEXT, likes INTEGER DEFAULT 0)',
        'CREATE TABLE IF NOT EXISTS comments (id INTEGER PRIMARY KEY AUTOINCREMENT, post_id INTEGER, username TEXT, content TEXT, timestamp TEXT, is_read INTEGER DEFAULT 0)'
    ]
    for t in tables: run_query(t)
    
    # MIGRATION: Yeni sütunları güvenli şekilde ekle
    columns = ["avatar_data", "frame", "name_style", "post_style"]
    for col in columns:
        try: run_query(f"ALTER TABLE users ADD COLUMN {col} TEXT")
        except: pass
    try: run_query("ALTER TABLE comments ADD COLUMN is_read INTEGER DEFAULT 0")
    except: pass

def compress_image(image_file, max_size=(800, 800), quality=70):
    if not image_file: return None
    try:
        img = Image.open(image_file).convert("RGB")
        img.thumbnail(max_size, Image.Resampling.LANCZOS)
        buffer = io.BytesIO()
        img.save(buffer, format="JPEG", quality=quality)
        return base64.b64encode(buffer.getvalue()).decode()
    except: return None

# --- GETTERS ---
@st.cache_data(ttl=3)
def get_posts(limit=20): return run_query("SELECT id, username, content, image_data, timestamp, likes FROM posts ORDER BY id DESC LIMIT ?", (limit,), fetch=True) or []

@st.cache_data(ttl=5)
def get_comments(pid): return run_query("SELECT username, content, timestamp FROM comments WHERE post_id = ? ORDER BY id ASC", (pid,), fetch=True) or []

@st.cache_data(ttl=10)
def get_leaderboard_data(): return run_query("SELECT student_username, SUM(grade) as total FROM grades GROUP BY student_username ORDER BY total DESC", fetch=True) or []

@st.cache_data(ttl=60)
def get_user_styles(u):
    # Avatar, Çerçeve, İsim Stili, Post Stili hepsini tek seferde çek
    try: 
        res = run_query("SELECT avatar_data, frame, name_style, post_style FROM users WHERE username = ?", (u,), fetch=True)
        return res[0] if res else (None, None, None, None)
    except: return (None, None, None, None)

@st.cache_data(ttl=5)
def get_total_score(u):
    res = run_query("SELECT SUM(grade) FROM grades WHERE student_username = ?", (u,), fetch=True)
    return res[0][0] if res and res[0][0] else 0

@st.cache_data(ttl=10)
def get_unread_notification_count(u):
    q = "SELECT COUNT(c.id) FROM comments c JOIN posts p ON c.post_id = p.id WHERE p.username = ? AND c.username != ? AND c.is_read = 0"
    res = run_query(q, (u, u), fetch=True)
    return res[0][0] if res else 0

@st.cache_data(ttl=10)
def get_unread_notifications(u):
    q = "SELECT c.username, c.content, p.content FROM comments c JOIN posts p ON c.post_id = p.id WHERE p.username = ? AND c.username != ? AND c.is_read = 0"
    return run_query(q, (u, u), fetch=True) or []

# --- SETTERS ---
def add_user(u, p, r):
    try:
        h = hashlib.sha256(p.encode()).hexdigest()
        return run_query("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", (u, h, r))
    except: return False
def login_user(u, p):
    h = hashlib.sha256(p.encode()).hexdigest()
    res = run_query("SELECT id, username, password, role FROM users WHERE username = ? AND password = ?", (u, h), fetch=True)
    return res[0] if res else None
def get_user_role(u):
    res = run_query("SELECT role FROM users WHERE username = ?", (u,), fetch=True)
    return res[0][0] if res and res[0] else None
def update_avatar(u, img):
    data = compress_image(img)
    if data:
        run_query("UPDATE users SET avatar_data = ? WHERE username = ?", (data, u))
        get_user_styles.clear(u)
        return True
    return False
def add_score(u, a, s="Sistem"):
    d = datetime.now().strftime("%Y-%m-%d %H:%M")
    run_query("INSERT INTO grades (student_username, lesson, grade, date) VALUES (?, ?, ?, ?)", (u, s, a, d))
    get_total_score.clear(u)
    get_leaderboard_data.clear()

# MAĞAZA SATIN ALMA
def buy_item(u, type, value, cost):
    current = get_total_score(u)
    if current >= cost:
        add_score(u, -cost, f"Mağaza: {value}")
        if type == "frame": col = "frame"
        elif type == "name": col = "name_style"
        elif type == "post": col = "post_style"
        
        run_query(f"UPDATE users SET {col} = ? WHERE username = ?", (value, u))
        get_user_styles.clear(u)
        return True, "Hayırlı olsun!"
    return False, "Puan yetersiz."

def get_all_users(): return run_query("SELECT username, role, last_seen FROM users", fetch=True) or []
def delete_user(u): run_query("DELETE FROM users WHERE username = ?", (u,))
def update_activity(u):
    n = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    run_query("UPDATE users SET last_seen = ? WHERE username = ?", (n, u))
def add_post(u, c, i=None):
    d = compress_image(i) if i else None
    t = datetime.now().strftime("%Y-%m-%d %H:%M")
    run_query("INSERT INTO posts (username, content, image_data, timestamp, likes) VALUES (?, ?, ?, ?, 0)", (u, c, d, t))
    get_posts.clear()
def like_post(id): 
    run_query("UPDATE posts SET likes = likes + 1 WHERE id = ?", (id,))
    get_posts.clear()
def delete_post(pid):
    run_query("DELETE FROM comments WHERE post_id = ?", (pid,))
    run_query("DELETE FROM posts WHERE id = ?", (pid,))
    get_posts.clear()
def update_post(pid, c):
    run_query("UPDATE posts SET content = ? WHERE id = ?", (c, pid))
    get_posts.clear()
def add_comment(pid, u, c):
    t = datetime.now().strftime("%Y-%m-%d %H:%M")
    run_query("INSERT INTO comments (post_id, username, content, timestamp, is_read) VALUES (?, ?, ?, ?, 0)", (pid, u, c, t))
    get_comments.clear(pid); get_unread_notification_count.clear(); get_unread_notifications.clear()
def mark_notifications_read(u):
    run_query("UPDATE comments SET is_read = 1 WHERE id IN (SELECT c.id FROM comments c JOIN posts p ON c.post_id = p.id WHERE p.username = ? AND c.username != ?)", (u, u))
    get_unread_notification_count.clear(u); get_unread_notifications.clear(u)
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
