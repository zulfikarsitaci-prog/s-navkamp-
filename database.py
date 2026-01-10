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
    DB_PATH = os.path.join(BASE_DIR, "education_platform.db")
    return sqlite3.connect(DB_PATH, check_same_thread=False)

def run_query(query, params=(), fetch=False):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(query, params)
        if fetch: return cursor.fetchall()
        else: conn.commit(); return True
    except Exception as e:
        return False
    finally: cursor.close()

def create_database():
    # Temel Tablolar
    tables = [
        'CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE, password TEXT, role TEXT, last_seen TEXT, avatar_data TEXT, frame TEXT, name_style TEXT, post_style TEXT, font_style TEXT, title TEXT, change_count INTEGER DEFAULT 0)',
        'CREATE TABLE IF NOT EXISTS grades (id INTEGER PRIMARY KEY AUTOINCREMENT, student_username TEXT, lesson TEXT, grade INTEGER, date TEXT)',
        'CREATE TABLE IF NOT EXISTS posts (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, content TEXT, image_data TEXT, timestamp TEXT, likes INTEGER DEFAULT 0)',
        'CREATE TABLE IF NOT EXISTS comments (id INTEGER PRIMARY KEY AUTOINCREMENT, post_id INTEGER, username TEXT, content TEXT, timestamp TEXT, is_read INTEGER DEFAULT 0)',
        'CREATE TABLE IF NOT EXISTS messages (id INTEGER PRIMARY KEY AUTOINCREMENT, sender TEXT, receiver TEXT, message TEXT, timestamp TEXT, is_read INTEGER DEFAULT 0)',
        'CREATE TABLE IF NOT EXISTS relationships (id INTEGER PRIMARY KEY AUTOINCREMENT, user1 TEXT, user2 TEXT, status TEXT)',
    ]
    for t in tables: run_query(t)
    
    # Admin Hesabı
    if not login_user("admin", "6626"):
        h = hashlib.sha256("6626".encode()).hexdigest()
        run_query("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", ("admin", h, "admin"))

# --- KULLANICI İŞLEMLERİ ---
def login_user(u, p):
    h = hashlib.sha256(p.encode()).hexdigest()
    res = run_query("SELECT id, username, password, role FROM users WHERE username = ? AND password = ?", (u, h), fetch=True)
    return res[0] if res else None

def add_user(u, p, r):
    try:
        h = hashlib.sha256(p.encode()).hexdigest()
        success = run_query("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", (u, h, r))
        if success:
            count = run_query("SELECT COUNT(*) FROM users", fetch=True)[0][0]
            if count <= 10:
                run_query("UPDATE users SET title = ?, frame = ? WHERE username = ?", ("KURUCU", "Gold", u))
                add_score(u, 50000, "İlk 10 Bonusu")
            return True, count
        return False, 0
    except: return False, 0

# --- EKSİK OLAN FONKSİYONLAR EKLENDİ ---
def get_searchable_users(my_u):
    # Admin ve kendisi hariç tüm kullanıcıları al
    all_users_res = run_query("SELECT username FROM users WHERE username != 'admin' AND username != ?", (my_u,), fetch=True)
    all_users = [r[0] for r in all_users_res] if all_users_res else []
    
    # Zaten arkadaş olduklarını filtrele
    friends = get_friends(my_u)
    return [u for u in all_users if u not in friends]

def get_all_users_list():
    res = run_query("SELECT username FROM users WHERE username != 'admin'", fetch=True)
    return [r[0] for r in res] if res else []

def get_friends(u):
    rows = run_query("SELECT user1, user2 FROM relationships WHERE (user1=? OR user2=?) AND status='accepted'", (u, u), fetch=True)
    friends = []
    if rows:
        for r in rows: friends.append(r[1] if r[0] == u else r[0])
    return friends

def send_friend_request(s, r):
    if run_query("SELECT * FROM relationships WHERE (user1=? AND user2=?) OR (user1=? AND user2=?)", (s, r, r, s), fetch=True): return False, "Zaten ekli/istek var."
    run_query("INSERT INTO relationships (user1, user2, status) VALUES (?, ?, ?)", (s, r, 'pending')); return True, "İstek yollandı."

def get_pending_requests(u): 
    return run_query("SELECT id, user1 FROM relationships WHERE user2=? AND status='pending'", (u,), fetch=True) or []

def accept_request(sender, me): 
    run_query("UPDATE relationships SET status='accepted' WHERE user1=? AND user2=?", (sender, me))

def update_activity(u):
    n = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    run_query("UPDATE users SET last_seen = ? WHERE username = ?", (n, u))

# --- DİĞER FONKSİYONLAR ---
def get_posts(limit=20): return run_query("SELECT id, username, content, image_data, timestamp, likes FROM posts ORDER BY id DESC LIMIT ?", (limit,), fetch=True) or []
def get_comments(pid): return run_query("SELECT username, content, timestamp FROM comments WHERE post_id = ? ORDER BY id ASC", (pid,), fetch=True) or []
def get_total_score(u):
    res = run_query("SELECT SUM(grade) FROM grades WHERE student_username = ?", (u,), fetch=True)
    return res[0][0] if res and res[0][0] else 0
def get_user_styles(u):
    res = run_query("SELECT avatar_data, frame, name_style, post_style, font_style, title FROM users WHERE username = ?", (u,), fetch=True)
    return res[0] if res else (None, None, None, None, None, None)
def get_user_change_count(u):
    res = run_query("SELECT change_count FROM users WHERE username = ?", (u,), fetch=True)
    return res[0][0] if res else 0

def compress_image(image_file):
    try:
        img = Image.open(image_file).convert("RGB")
        img.thumbnail((600, 600))
        buffer = io.BytesIO()
        img.save(buffer, format="JPEG", quality=60)
        return base64.b64encode(buffer.getvalue()).decode()
    except: return None

def add_post(u, c, i=None):
    d = compress_image(i) if i else None
    t = datetime.now().strftime("%Y-%m-%d %H:%M")
    run_query("INSERT INTO posts (username, content, image_data, timestamp, likes) VALUES (?, ?, ?, ?, 0)", (u, c, d, t))

def like_post(id): run_query("UPDATE posts SET likes = likes + 1 WHERE id = ?", (id,))
def delete_post(pid): 
    run_query("DELETE FROM comments WHERE post_id = ?", (pid,))
    run_query("DELETE FROM posts WHERE id = ?", (pid,))
def update_post(pid, c): run_query("UPDATE posts SET content = ? WHERE id = ?", (c, pid))
def add_comment(pid, u, c):
    t = datetime.now().strftime("%Y-%m-%d %H:%M")
    run_query("INSERT INTO comments (post_id, username, content, timestamp, is_read) VALUES (?, ?, ?, ?, 0)", (pid, u, c, t))

def add_score(u, a, s="Sistem"):
    d = datetime.now().strftime("%Y-%m-%d %H:%M")
    run_query("INSERT INTO grades (student_username, lesson, grade, date) VALUES (?, ?, ?, ?)", (u, s, a, d))

def buy_item(u, type, value, cost):
    if get_total_score(u) >= cost:
        add_score(u, -cost, f"Mağaza: {value}")
        col = {"frame":"frame","name":"name_style","post":"post_style","font":"font_style","title":"title"}.get(type,"")
        if col: run_query(f"UPDATE users SET {col} = ? WHERE username = ?", (value, u)); return True, "Satın alındı!"
    return False, "Puan yetersiz."

def update_avatar(u, img):
    d = compress_image(img)
    if d: run_query("UPDATE users SET avatar_data = ? WHERE username = ?", (d, u)); return True
    return False

def change_username_logic(current_user, new_user):
    if run_query("SELECT id FROM users WHERE username = ?", (new_user,), fetch=True): return False, "İsim kullanımda."
    change_count = get_user_change_count(current_user)
    cost = 0 if change_count == 0 else 500000
    if get_total_score(current_user) < cost: return False, "Yetersiz bakiye."
    try:
        if cost > 0: add_score(current_user, -cost, "İsim Değişikliği")
        tables_cols = [("users", "username"), ("grades", "student_username"), ("posts", "username"), ("comments", "username"), ("messages", "sender"), ("messages", "receiver")]
        for t, c in tables_cols: run_query(f"UPDATE {t} SET {c} = ? WHERE {c} = ?", (new_user, current_user))
        run_query("UPDATE users SET change_count = change_count + 1 WHERE username = ?", (new_user,))
        return True, "İsim değiştirildi!"
    except: return False, "Hata oluştu."

def send_message(s, r, m):
    t = datetime.now().strftime("%Y-%m-%d %H:%M")
    run_query("INSERT INTO messages (sender, receiver, message, timestamp) VALUES (?, ?, ?, ?)", (s, r, m, t))

def get_conversation(u1, u2):
    return run_query("SELECT sender, message, timestamp FROM messages WHERE (sender = ? AND receiver = ?) OR (sender = ? AND receiver = ?) ORDER BY id ASC", (u1, u2, u2, u1), fetch=True) or []

def get_unread_notification_count(u):
    res = run_query("SELECT COUNT(c.id) FROM comments c JOIN posts p ON c.post_id = p.id WHERE p.username = ? AND c.username != ? AND c.is_read = 0", (u, u), fetch=True)
    return res[0][0] if res else 0

def mark_notifications_read(u):
    run_query("UPDATE comments SET is_read = 1 WHERE id IN (SELECT c.id FROM comments c JOIN posts p ON c.post_id = p.id WHERE p.username = ? AND c.username != ?)", (u, u))

def delete_user(u):
    if u == "admin": return
    run_query("DELETE FROM users WHERE username=?",(u,))
    run_query("DELETE FROM posts WHERE username=?",(u,))
