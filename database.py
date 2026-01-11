import sqlite3
import hashlib
import os
import streamlit as st
from datetime import datetime
import base64
from PIL import Image
import io

# --- BAĞLANTI ---
@st.cache_resource(ttl=3600)
def get_db_connection():
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DB_PATH = os.path.join(BASE_DIR, "education_platform_v2.db") # Yeni DB ismi
    return sqlite3.connect(DB_PATH, check_same_thread=False)

def run_query(query, params=(), fetch=False):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(query, params)
        if fetch: return cursor.fetchall()
        else: conn.commit(); return True
    except Exception as e: return False
    finally: cursor.close()

def create_database():
    tables = [
        'CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE, password TEXT, role TEXT, class_code TEXT, avatar_data TEXT, frame TEXT, name_style TEXT, score INTEGER DEFAULT 0)',
        'CREATE TABLE IF NOT EXISTS posts (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, content TEXT, image_data TEXT, youtube_link TEXT, wall_type TEXT, target_class TEXT, timestamp TEXT, likes INTEGER DEFAULT 0)',
        'CREATE TABLE IF NOT EXISTS comments (id INTEGER PRIMARY KEY AUTOINCREMENT, post_id INTEGER, username TEXT, content TEXT, timestamp TEXT, is_read INTEGER DEFAULT 0)',
        'CREATE TABLE IF NOT EXISTS messages (id INTEGER PRIMARY KEY AUTOINCREMENT, sender TEXT, receiver TEXT, message TEXT, timestamp TEXT, is_read INTEGER DEFAULT 0)',
        'CREATE TABLE IF NOT EXISTS followers (id INTEGER PRIMARY KEY AUTOINCREMENT, follower TEXT, followed TEXT)',
        'CREATE TABLE IF NOT EXISTS classes (id INTEGER PRIMARY KEY AUTOINCREMENT, code TEXT UNIQUE, name TEXT, teacher TEXT)',
        'CREATE TABLE IF NOT EXISTS grades (id INTEGER PRIMARY KEY AUTOINCREMENT, student_username TEXT, lesson TEXT, grade INTEGER, date TEXT)'
    ]
    for t in tables: run_query(t)
    
    if not login_user("admin", "6626"):
        h = hashlib.sha256("6626".encode()).hexdigest()
        run_query("INSERT INTO users (username, password, role, score) VALUES (?, ?, ?, ?)", ("admin", h, "admin", 9999999))

# --- KULLANICI ---
def login_user(u, p):
    h = hashlib.sha256(p.encode()).hexdigest()
    res = run_query("SELECT id, username, password, role, class_code, score FROM users WHERE username = ? AND password = ?", (u, h), fetch=True)
    return res[0] if res else None

def add_user(u, p, r):
    try:
        h = hashlib.sha256(p.encode()).hexdigest()
        success = run_query("INSERT INTO users (username, password, role, score) VALUES (?, ?, ?, ?)", (u, h, r, 5000)) # Başlangıç puanı
        return True
    except: return False

def get_user_info(u):
    res = run_query("SELECT score, role, class_code, avatar_data, frame, name_style FROM users WHERE username = ?", (u,), fetch=True)
    return res[0] if res else (0, 'student', None, None, None, None)

# --- SOSYAL (TAKİP & MESAJ) ---
def follow_user(follower, followed):
    if follower == followed: return False
    # Zaten takip ediyor mu?
    check = run_query("SELECT id FROM followers WHERE follower = ? AND followed = ?", (follower, followed), fetch=True)
    if not check:
        run_query("INSERT INTO followers (follower, followed) VALUES (?, ?)", (follower, followed))
        # Bildirim gönder
        send_message("Sistem", followed, f"{follower} seni takip etmeye başladı! Sen de onu takip edersen mesajlaşabilirsiniz.")
        return True
    return False

def get_mutual_friends(u):
    # Karşılıklı takipleşenleri getir (Mesajlaşma için)
    q = """
    SELECT f1.followed 
    FROM followers f1 
    JOIN followers f2 ON f1.followed = f2.follower 
    WHERE f1.follower = ? AND f2.followed = ?
    """
    res = run_query(q, (u, u), fetch=True)
    return [r[0] for r in res] if res else []

def get_all_users_except_me(me):
    res = run_query("SELECT username FROM users WHERE username != 'admin' AND username != ?", (me,), fetch=True)
    return [r[0] for r in res] if res else []

# --- DUVAR & POST ---
def add_post(u, c, img=None, yt=None, w_type="campus", t_class=None):
    img_d = compress_image(img) if img else None
    t = datetime.now().strftime("%Y-%m-%d %H:%M")
    run_query("INSERT INTO posts (username, content, image_data, youtube_link, wall_type, target_class, timestamp) VALUES (?, ?, ?, ?, ?, ?, ?)", (u, c, img_d, yt, w_type, t_class, t))

def get_posts(wall_type="campus", target_class=None, user_filter=None):
    if user_filter: # Kişisel duvar
        return run_query("SELECT id, username, content, image_data, youtube_link, timestamp, likes FROM posts WHERE username = ? ORDER BY id DESC LIMIT 50", (user_filter,), fetch=True)
    elif wall_type == "class" and target_class:
        return run_query("SELECT id, username, content, image_data, youtube_link, timestamp, likes FROM posts WHERE wall_type = 'class' AND target_class = ? ORDER BY id DESC LIMIT 50", (target_class,), fetch=True)
    else: # Genel Kampüs
        return run_query("SELECT id, username, content, image_data, youtube_link, timestamp, likes FROM posts WHERE wall_type = 'campus' ORDER BY id DESC LIMIT 50", fetch=True)

def like_post(id): run_query("UPDATE posts SET likes = likes + 1 WHERE id = ?", (id,))
def add_comment(pid, u, c):
    t = datetime.now().strftime("%Y-%m-%d %H:%M")
    run_query("INSERT INTO comments (post_id, username, content, timestamp) VALUES (?, ?, ?, ?)", (pid, u, c, t))
    # Post sahibine bildirim (basitçe okunmamış yorum sayısı artar)

def get_comments(pid): return run_query("SELECT username, content FROM comments WHERE post_id = ?", (pid,), fetch=True) or []

# --- SINIF SİSTEMİ ---
def create_class(teacher, name, code):
    try:
        run_query("INSERT INTO classes (code, name, teacher) VALUES (?, ?, ?)", (code, name, teacher))
        return True
    except: return False

def join_class(student, code):
    # Sınıf var mı?
    cls = run_query("SELECT name FROM classes WHERE code = ?", (code,), fetch=True)
    if cls:
        run_query("UPDATE users SET class_code = ? WHERE username = ?", (code, student))
        return True, cls[0][0]
    return False, None

# --- DİĞER ---
def add_score(u, val, reason="Sistem"):
    run_query("UPDATE users SET score = score + ? WHERE username = ?", (val, u))
    # Geçmiş kaydı (opsiyonel)
    
def send_message(s, r, m):
    t = datetime.now().strftime("%Y-%m-%d %H:%M")
    run_query("INSERT INTO messages (sender, receiver, message, timestamp) VALUES (?, ?, ?, ?)", (s, r, m, t))

def get_conversation(u1, u2):
    return run_query("SELECT sender, message, timestamp FROM messages WHERE (sender=? AND receiver=?) OR (sender=? AND receiver=?) ORDER BY id ASC", (u1, u2, u2, u1), fetch=True) or []

def get_notifications(u):
    # Okunmamış mesaj sayısı
    m = run_query("SELECT COUNT(*) FROM messages WHERE receiver = ? AND is_read = 0", (u,), fetch=True)[0][0]
    return m

def mark_read(u):
    run_query("UPDATE messages SET is_read = 1 WHERE receiver = ?", (u,))

def compress_image(image_file):
    try:
        img = Image.open(image_file).convert("RGB"); img.thumbnail((600, 600))
        buffer = io.BytesIO(); img.save(buffer, format="JPEG", quality=60)
        return base64.b64encode(buffer.getvalue()).decode()
    except: return None

# --- ADMIN ---
def admin_get_all_users(): return run_query("SELECT username, score, role, class_code FROM users", fetch=True)
def admin_delete_user(u):
    run_query("DELETE FROM users WHERE username=?",(u,))
    run_query("DELETE FROM posts WHERE username=?",(u,))
def admin_get_all_messages(): return run_query("SELECT sender, receiver, message, timestamp FROM messages ORDER BY id DESC LIMIT 100", fetch=True)
def buy_item(u, item_type, item_val, cost):
    current_score = get_user_info(u)[0]
    if current_score >= cost:
        add_score(u, -cost)
        col = {"frame":"frame", "name":"name_style"}.get(item_type)
        if col: run_query(f"UPDATE users SET {col} = ? WHERE username = ?", (item_val, u))
        return True
    return False
