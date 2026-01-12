import hashlib
from datetime import datetime
import streamlit as st
from PIL import Image
import io
import base64
from .core import run_query
from .score import add_score, get_total_score # Score modülünden import

# Yardımcı: Resim Sıkıştırma
def compress_image(image_file, max_size=(600, 600), quality=60):
    if not image_file: return None
    try:
        img = Image.open(image_file).convert("RGB")
        img.thumbnail(max_size, Image.Resampling.LANCZOS)
        buffer = io.BytesIO()
        img.save(buffer, format="JPEG", quality=quality)
        return base64.b64encode(buffer.getvalue()).decode()
    except: return None

def login_user(u, p):
    h = hashlib.sha256(p.encode()).hexdigest()
    res = run_query("SELECT id, username, password, role FROM users WHERE username = ? AND password = ?", (u, h), fetch=True)
    return res[0] if res else None

def add_user(u, p, r):
    try:
        h = hashlib.sha256(p.encode()).hexdigest()
        success = run_query("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", (u, h, r))
        if success:
            count_res = run_query("SELECT COUNT(*) FROM users", fetch=True)
            user_count = count_res[0][0] if count_res else 999
            if user_count <= 10:
                run_query("UPDATE users SET title = ?, frame = ? WHERE username = ?", ("KURUCU", "Gold", u))
                add_score(u, 50000, "İlk 10 Bonusu!")
                return True, user_count
        return success, 999
    except: return False, 999

def update_avatar(u, img):
    d = compress_image(img)
    if d:
        run_query("UPDATE users SET avatar_data = ? WHERE username = ?", (d, u))
        get_user_styles.clear(u)
        return True
    return False

@st.cache_data(ttl=5)
def get_user_styles(u):
    try: 
        res = run_query("SELECT avatar_data, frame, name_style, post_style, font_style, title FROM users WHERE username = ?", (u,), fetch=True)
        return res[0] if res else (None, None, None, None, None, None)
    except: return (None, None, None, None, None, None)

def change_username_logic(current_user, new_user):
    if run_query("SELECT id FROM users WHERE username = ?", (new_user,), fetch=True):
        return False, "Bu isim zaten kullanılıyor."
    
    res = run_query("SELECT change_count FROM users WHERE username = ?", (current_user,), fetch=True)
    change_count = res[0][0] if res else 0
    cost = 0 if change_count == 0 else 500000
    
    current_score = get_total_score(current_user)
    if current_score < cost:
        return False, f"Yetersiz bakiye! İkinci değişim için {cost:,} puan lazım."
    
    try:
        if cost > 0: add_score(current_user, -cost, "İsim Değişikliği")
        tables_cols = [
            ("users", "username"), ("grades", "student_username"), ("posts", "username"),
            ("comments", "username"), ("messages", "sender"), ("messages", "receiver"),
            ("relationships", "user1"), ("relationships", "user2"), ("announcements", "author")
        ]
        for table, col in tables_cols:
            run_query(f"UPDATE {table} SET {col} = ? WHERE {col} = ?", (new_user, current_user))
            
        run_query("UPDATE users SET change_count = change_count + 1 WHERE username = ?", (new_user,))
        get_user_styles.clear(current_user)
        get_total_score.clear(current_user)
        return True, "İsim başarıyla değiştirildi! Lütfen tekrar giriş yap."
    except Exception as e:
        return False, f"Hata oluştu: {e}"

def get_all_users(): return run_query("SELECT username, role, last_seen FROM users", fetch=True) or []
def delete_user(u): run_query("DELETE FROM users WHERE username = ?", (u,))
def update_activity(u):
    n = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    run_query("UPDATE users SET last_seen = ? WHERE username = ?", (n, u))
def get_user_role(u):
    res = run_query("SELECT role FROM users WHERE username = ?", (u,), fetch=True)
    return res[0][0] if res and res[0] else None
def get_user_change_count(u):
    res = run_query("SELECT change_count FROM users WHERE username = ?", (u,), fetch=True)
    return res[0][0] if res else 0
    

