from datetime import datetime, timedelta
import streamlit as st
from .core import run_query
from .users import compress_image

# --- POST VE BİLDİRİM (DEĞİŞMEDİ) ---
@st.cache_data(ttl=2)
def get_posts(limit=20): return run_query("SELECT id, username, content, image_data, timestamp, likes FROM posts ORDER BY id DESC LIMIT ?", (limit,), fetch=True) or []
@st.cache_data(ttl=5)
def get_comments(pid): return run_query("SELECT username, content, timestamp FROM comments WHERE post_id = ? ORDER BY id ASC", (pid,), fetch=True) or []
@st.cache_data(ttl=10)
def get_unread_notification_count(u):
    q = "SELECT COUNT(c.id) FROM comments c JOIN posts p ON c.post_id = p.id WHERE p.username = ? AND c.username != ? AND c.is_read = 0"
    res = run_query(q, (u, u), fetch=True)
    return res[0][0] if res else 0
@st.cache_data(ttl=10)
def get_unread_notifications(u):
    q = "SELECT c.username, c.content, p.content FROM comments c JOIN posts p ON c.post_id = p.id WHERE p.username = ? AND c.username != ? AND c.is_read = 0"
    return run_query(q, (u, u), fetch=True) or []

# --- HİKAYE FONKSİYONLARI (GÜNCELLENDİ) ---
def add_story(u, img, txt=""):
    d = compress_image(img) if img else None
    t = datetime.now()
    ts = t.strftime("%Y-%m-%d %H:%M")
    # Bitiş zamanını kaydet
    exp = (t + timedelta(hours=24)).strftime("%Y-%m-%d %H:%M")
    run_query("INSERT INTO stories (username, content, image_data, timestamp, expires_at) VALUES (?, ?, ?, ?, ?)", (u, txt, d, ts, exp))
    get_active_stories.clear()
    get_my_stories.clear()

def delete_story(story_id):
    run_query("DELETE FROM stories WHERE id = ?", (story_id,))
    get_active_stories.clear()
    get_my_stories.clear()

def get_active_stories():
    # Sadece süresi dolmamış (expires_at > şimdiki zaman) hikayeleri çek
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    # Not: SQLite/Postgres tarih karşılaştırması string formatında düzgün çalışır (Y-m-d H:M formatı sayesinde)
    return run_query("SELECT id, username, content, image_data, timestamp FROM stories WHERE expires_at > ? ORDER BY id DESC", (now,), fetch=True) or []

def get_my_stories(username):
    # Senin hikayelerin (Silmek için, süresi dolsa bile görebilirsin istersen burayı da filtreleyebiliriz ama yönetim için kalsın)
    return run_query("SELECT id, content, timestamp, expires_at FROM stories WHERE username = ? ORDER BY id DESC", (username,), fetch=True) or []

# --- DİĞERLERİ (DEĞİŞMEDİ) ---
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
    get_comments.clear(pid); get_unread_notification_count.clear(u); get_unread_notifications.clear(u)
def mark_notifications_read(u):
    run_query("UPDATE comments SET is_read = 1 WHERE id IN (SELECT c.id FROM comments c JOIN posts p ON c.post_id = p.id WHERE p.username = ? AND c.username != ?)", (u, u))
    get_unread_notification_count.clear(u); get_unread_notifications.clear(u)
def send_message(s, r, m): run_query("INSERT INTO messages (sender, receiver, message, timestamp, is_read) VALUES (?, ?, ?, ?, 0)", (s, r, m, datetime.now().strftime("%Y-%m-%d %H:%M")))
def get_conversation(u1, u2): return run_query("SELECT sender, message, timestamp FROM messages WHERE (sender = ? AND receiver = ?) OR (sender = ? AND receiver = ?) ORDER BY id ASC", (u1, u2, u2, u1), fetch=True) or []
def get_friends(u):
    rows = run_query("SELECT user1, user2 FROM relationships WHERE (user1=? OR user2=?) AND status='accepted'", (u, u), fetch=True)
    return [r[1] if r[0] == u else r[0] for r in rows] if rows else []
def get_searchable_users(my_u):
    all_users = [u[0] for u in run_query("SELECT username FROM users", fetch=True) or []]
    friends = get_friends(my_u)
    return [u for u in all_users if u != my_u and u not in friends and u != "admin"]
def send_friend_request(s, r):
    check = run_query("SELECT * FROM relationships WHERE (user1=? AND user2=?) OR (user1=? AND user2=?)", (s, r, r, s), fetch=True)
    if not check:
        run_query("INSERT INTO relationships (user1, user2, status) VALUES (?, ?, ?)", (s, r, 'pending'))
        return True, "İstek yollandı."
    return False, "Zaten ekli."
def get_pending_requests(u): return run_query("SELECT id, user1 FROM relationships WHERE user2=? AND status='pending'", (u,), fetch=True) or []
def accept_request(sender, me): run_query("UPDATE relationships SET status='accepted' WHERE user1=? AND user2=?", (sender, me))
