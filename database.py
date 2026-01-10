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
        try: return psycopg2.connect(st.secrets["DATABASE_URL"])
        except: return None
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DB_PATH = os.path.join(BASE_DIR, "education_platform.db")
    return sqlite3.connect(DB_PATH, check_same_thread=False)

def run_query(query, params=(), fetch=False):
    conn = get_db_connection()
    if not conn: return False
    try:
        if hasattr(conn, 'closed') and conn.closed != 0:
            st.cache_resource.clear(); conn = get_db_connection()
    except: pass
    cursor = conn.cursor()
    if "psycopg2" in str(type(conn)):
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
        'CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE, password TEXT, role TEXT, last_seen TEXT, avatar_data TEXT, frame TEXT, name_style TEXT, post_style TEXT, font_style TEXT, title TEXT)',
        'CREATE TABLE IF NOT EXISTS grades (id INTEGER PRIMARY KEY AUTOINCREMENT, student_username TEXT, lesson TEXT, grade INTEGER, date TEXT)',
        'CREATE TABLE IF NOT EXISTS posts (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, content TEXT, image_data TEXT, timestamp TEXT, likes INTEGER DEFAULT 0)',
        'CREATE TABLE IF NOT EXISTS comments (id INTEGER PRIMARY KEY AUTOINCREMENT, post_id INTEGER, username TEXT, content TEXT, timestamp TEXT, is_read INTEGER DEFAULT 0)',
        'CREATE TABLE IF NOT EXISTS messages (id INTEGER PRIMARY KEY AUTOINCREMENT, sender TEXT, receiver TEXT, message TEXT, timestamp TEXT, is_read INTEGER DEFAULT 0)',
        'CREATE TABLE IF NOT EXISTS global_messages (id INTEGER PRIMARY KEY AUTOINCREMENT, sender TEXT, message TEXT, timestamp TEXT)',
        'CREATE TABLE IF NOT EXISTS relationships (id INTEGER PRIMARY KEY AUTOINCREMENT, user1 TEXT, user2 TEXT, status TEXT)',
        'CREATE TABLE IF NOT EXISTS announcements (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, content TEXT, date TEXT, author TEXT)'
    ]
    for t in tables: run_query(t)
    cols = ["avatar_data", "frame", "name_style", "post_style", "font_style", "title"]
    for col in cols:
        try: run_query(f"ALTER TABLE users ADD COLUMN {col} TEXT")
        except: pass

def compress_image(image_file, max_size=(600, 600), quality=60):
    if not image_file: return None
    try:
        img = Image.open(image_file).convert("RGB")
        img.thumbnail(max_size, Image.Resampling.LANCZOS)
        buffer = io.BytesIO()
        img.save(buffer, format="JPEG", quality=quality)
        return base64.b64encode(buffer.getvalue()).decode()
    except: return None

# --- CACHE ---
@st.cache_data(ttl=3)
def get_posts(limit=20): return run_query("SELECT id, username, content, image_data, timestamp, likes FROM posts ORDER BY id DESC LIMIT ?", (limit,), fetch=True) or []
@st.cache_data(ttl=5)
def get_comments(pid): return run_query("SELECT username, content, timestamp FROM comments WHERE post_id = ? ORDER BY id ASC", (pid,), fetch=True) or []
@st.cache_data(ttl=30)
def get_leaderboard_data(): return run_query("SELECT student_username, SUM(grade) as total FROM grades GROUP BY student_username ORDER BY total DESC", fetch=True) or []
@st.cache_data(ttl=5)
def get_user_styles(u):
    try: 
        res = run_query("SELECT avatar_data, frame, name_style, post_style, font_style, title FROM users WHERE username = ?", (u,), fetch=True)
        return res[0] if res else (None, None, None, None, None, None)
    except: return (None, None, None, None, None, None)
@st.cache_data(ttl=3)
def get_total_score(u):
    res = run_query("SELECT SUM(grade) FROM grades WHERE student_username = ?", (u,), fetch=True)
    return res[0][0] if res and res[0][0] else 0
@st.cache_data(ttl=10)
def get_unread_notifications(u):
    q = "SELECT c.username, c.content, p.content FROM comments c JOIN posts p ON c.post_id = p.id WHERE p.username = ? AND c.username != ? AND c.is_read = 0"
    return run_query(q, (u, u), fetch=True) or []

# --- FUNCTIONS ---
def login_user(u, p):
    h = hashlib.sha256(p.encode()).hexdigest()
    res = run_query("SELECT id, username, password, role FROM users WHERE username = ? AND password = ?", (u, h), fetch=True)
    return res[0] if res else None
def add_user(u, p, r):
    try:
        h = hashlib.sha256(p.encode()).hexdigest()
        return run_query("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", (u, h, r))
    except: return False
def update_avatar(u, img):
    d = compress_image(img)
    if d:
        run_query("UPDATE users SET avatar_data = ? WHERE username = ?", (d, u))
        get_user_styles.clear(u)
        return True
    return False
def add_score(u, a, s="Sistem"):
    d = datetime.now().strftime("%Y-%m-%d %H:%M")
    run_query("INSERT INTO grades (student_username, lesson, grade, date) VALUES (?, ?, ?, ?)", (u, s, a, d))
    get_total_score.clear(u); get_leaderboard_data.clear()
def buy_item(u, type, value, cost):
    current = get_total_score(u)
    if current >= cost:
        add_score(u, -cost, f"Mağaza: {value}")
        col = ""
        if type == "frame": col = "frame"
        elif type == "name": col = "name_style"
        elif type == "post": col = "post_style"
        elif type == "font": col = "font_style"
        elif type == "title": col = "title"
        if col:
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
def like_post(id): run_query("UPDATE posts SET likes = likes + 1 WHERE id = ?", (id,)); get_posts.clear()
def delete_post(pid): run_query("DELETE FROM comments WHERE post_id = ?", (pid,)); run_query("DELETE FROM posts WHERE id = ?", (pid,)); get_posts.clear()
def update_post(pid, c): run_query("UPDATE posts SET content = ? WHERE id = ?", (c, pid)); get_posts.clear()
def add_comment(pid, u, c):
    t = datetime.now().strftime("%Y-%m-%d %H:%M")
    run_query("INSERT INTO comments (post_id, username, content, timestamp, is_read) VALUES (?, ?, ?, ?, 0)", (pid, u, c, t))
    get_comments.clear(pid); get_unread_notifications.clear()
def mark_notifications_read(u):
    run_query("UPDATE comments SET is_read = 1 WHERE id IN (SELECT c.id FROM comments c JOIN posts p ON c.post_id = p.id WHERE p.username = ? AND c.username != ?)", (u, u))
    get_unread_notifications.clear(u)
def send_message(s, r, m): run_query("INSERT INTO messages (sender, receiver, message, timestamp, is_read) VALUES (?, ?, ?, ?, 0)", (s, r, m, datetime.now().strftime("%Y-%m-%d %H:%M")))
def get_conversation(u1, u2): return run_query("SELECT sender, message, timestamp FROM messages WHERE (sender = ? AND receiver = ?) OR (sender = ? AND receiver = ?) ORDER BY id ASC", (u1, u2, u2, u1), fetch=True) or []
def get_friends(u):
    rows = run_query("SELECT user1, user2 FROM relationships WHERE (user1=? OR user2=?) AND status='accepted'", (u, u), fetch=True)
    return [r[1] if r[0] == u else r[0] for r in rows] if rows else []
