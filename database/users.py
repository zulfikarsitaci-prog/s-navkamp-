import hashlib
from datetime import datetime
import streamlit as st
from PIL import Image
import io
import base64
from .core import run_query
from .score import add_score, get_total_score

# --- YARDIMCI: Resim İşleme ---
def compress_image(image_file, max_size=(600, 600), quality=60):
    if not image_file: return None
    try:
        img = Image.open(image_file)
        if img.mode != 'RGB': img = img.convert("RGB")
        img.thumbnail(max_size, Image.Resampling.LANCZOS)
        buffer = io.BytesIO()
        img.save(buffer, format="JPEG", quality=quality)
        # Veritabanına BLOB (binary) olarak kaydediyoruz
        return buffer.getvalue()
    except: return None

# --- GİRİŞ & KAYIT ---
def login_user(u, p):
    # Şifreyi hashleyip kontrol et
    h = hashlib.sha256(p.encode()).hexdigest()
    res = run_query("SELECT id, username, password, role FROM users WHERE username = ? AND password = ?", (u, h), fetch=True)
    return res[0] if res else None

def add_user(u, p, r):
    try:
        # Önce isim kontrolü
        if run_query("SELECT id FROM users WHERE username = ?", (u,), fetch=True):
            return False, "Bu isim zaten alınmış."
            
        h = hashlib.sha256(p.encode()).hexdigest()
        run_query("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", (u, h, r))
        
        # İlk 10 kullanıcıya ödül mantığı
        count_res = run_query("SELECT COUNT(*) FROM users", fetch=True)
        user_count = count_res[0][0] if count_res else 999
        
        if user_count <= 10:
            run_query("UPDATE users SET title = ?, frame = ? WHERE username = ?", ("KURUCU", "Gold", u))
            add_score(u, 50000, "İlk 10 Bonusu!")
        else:
            # Standart başlangıç
            run_query("UPDATE users SET title = ? WHERE username = ?", ("Çırak", u))
            run_query("INSERT INTO inventory (username, item_type, item_value) VALUES (?, ?, ?)", (u, "title", "Çırak"))
            
        return True, user_count
    except Exception as e: 
        print(f"Kayıt Hatası: {e}")
        return False, 999

# --- PROFİL İŞLEMLERİ ---
def update_avatar(u, img):
    d = compress_image(img) # Binary veri döner
    if d:
        # Sütun adı 'avatar' olarak düzeltildi (avatar_data değil)
        run_query("UPDATE users SET avatar = ? WHERE username = ?", (d, u))
        get_user_styles.clear()
        return True
    return False

@st.cache_data(ttl=5)
def get_user_styles(u):
    try: 
        # Sütun adı 'avatar'
        res = run_query("SELECT avatar, frame, name_style, bg_style, font_style, title FROM users WHERE username = ?", (u,), fetch=True)
        # Eğer stil yoksa varsayılanları döndür
        if res: return res[0]
        return (None, None, None, None, None, "Çırak")
    except: return (None, None, None, None, None, "Çırak")

def change_username_logic(current_user, new_user):
    if len(new_user) < 3: return False, "İsim çok kısa."
    if run_query("SELECT id FROM users WHERE username = ?", (new_user,), fetch=True):
        return False, "Bu isim zaten kullanılıyor."
    
    res = run_query("SELECT change_count FROM users WHERE username = ?", (current_user,), fetch=True)
    change_count = res[0][0] if res else 0
    cost = 0 if change_count == 0 else 500000
    
    if get_total_score(current_user) < cost:
        return False, f"Yetersiz bakiye! Gerekli: {cost:,} P"
    
    try:
        if cost > 0: add_score(current_user, -cost, "İsim Değişikliği")
        
        # Tüm tablolarda güncelle
        tables_cols = [
            ("users", "username"), ("scores", "username"), ("posts", "username"),
            ("comments", "username"), ("messages", "sender"), ("messages", "receiver"),
            ("friends", "u1"), ("friends", "u2"), ("inventory", "username"),
            ("likes", "username"), ("poll_votes", "username"), ("stories", "username")
        ]
        
        for table, col in tables_cols:
            try: run_query(f"UPDATE {table} SET {col} = ? WHERE {col} = ?", (new_user, current_user))
            except: pass
            
        run_query("UPDATE users SET change_count = change_count + 1 WHERE username = ?", (new_user,))
        get_user_styles.clear()
        return True, "İsim başarıyla değiştirildi! Lütfen tekrar giriş yap."
    except Exception as e:
        return False, f"Hata oluştu: {e}"

# --- EKSİK OLAN SATIN ALMA FONKSİYONU ---
def buy_item(username, item_type, item_value, cost):
    current_score = get_total_score(username)
    if current_score < cost:
        return False, "Yetersiz Puan!"
    
    # Zaten var mı kontrolü
    check = run_query("SELECT * FROM inventory WHERE username=? AND item_type=? AND item_value=?", 
                      (username, item_type, item_value), fetch=True)
    
    if not check:
        add_score(username, -cost, f"Satın Alma: {item_value}")
        run_query("INSERT INTO inventory (username, item_type, item_value) VALUES (?, ?, ?)", 
                  (username, item_type, item_value))
    
    # Otomatik Kuşanma
    col_map = {"frame": "frame", "name_style": "name_style", "font_style": "font_style", "title": "title"}
    if item_type in col_map:
        run_query(f"UPDATE users SET {col_map[item_type]} = ? WHERE username = ?", (item_value, username))
        get_user_styles.clear()
        
    return True, "İşlem Başarılı"

# --- DİĞERLERİ ---
def get_all_users_list(): return run_query("SELECT username, role, title FROM users", fetch=True) or []
def delete_user(u): run_query("DELETE FROM users WHERE username = ?", (u,))
def update_activity(u):
    try: run_query("UPDATE users SET last_active = CURRENT_TIMESTAMP WHERE username = ?", (u,))
    except: pass
def get_user_role(u):
    res = run_query("SELECT role FROM users WHERE username = ?", (u,), fetch=True)
    return res[0][0] if res else None
def get_user_change_count(u):
    res = run_query("SELECT change_count FROM users WHERE username = ?", (u,), fetch=True)
    return res[0][0] if res else 0
def set_user_role(u, r): run_query("UPDATE users SET role = ? WHERE username = ?", (r, u))
