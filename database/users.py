import streamlit as st
from .core import run_query
import hashlib
from datetime import datetime

# --- YARDIMCI FONKSİYONLAR ---
def make_hashes(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def check_hashes(password, hashed_text):
    if make_hashes(password) == hashed_text:
        return hashed_text
    return False

def compress_image(image):
    import io
    from PIL import Image
    import base64
    
    img = Image.open(image)
    if img.mode != "RGB":
        img = img.convert("RGB")
    
    # Resmi küçült (Thumbnail)
    img.thumbnail((200, 200))
    
    # Sıkıştır
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='JPEG', quality=60)
    return base64.b64encode(img_byte_arr.getvalue()).decode('utf-8')

# --- KULLANICI İŞLEMLERİ ---
def add_user(username, password, role="student"):
    if run_query("SELECT * FROM users WHERE username = ?", (username,), fetch=True):
        return False, "Kullanıcı adı alınmış."
    
    hashed_pw = make_hashes(password)
    run_query("INSERT INTO users (username, password, role, frame, name_style, title, avatar_data) VALUES (?, ?, ?, ?, ?, ?, ?)", 
              (username, hashed_pw, role, "", "", "Çırak", None))
    return True, "Kayıt Başarılı"

def login_user(username, password):
    hashed_pw = make_hashes(password)
    result = run_query("SELECT * FROM users WHERE username = ? AND password = ?", (username, hashed_pw), fetch=True)
    return result[0] if result else None

@st.cache_data(ttl=60)
def get_user_styles(username):
    # Avatar, Çerçeve, İsim Stili, Post Stili, Font Stili, Ünvan
    res = run_query("SELECT avatar_data, frame, name_style, post_style, font_style, title FROM users WHERE username = ?", (username,), fetch=True)
    if res:
        return res[0]
    return (None, "", "", "", "", "Çırak")

# --- EKSİK OLAN FONKSİYON BURAYA EKLENDİ ---
def get_all_users():
    """Sistemdeki tüm kullanıcı adlarını döndürür."""
    return run_query("SELECT username FROM users", fetch=True) or []
# -------------------------------------------

def update_avatar(username, image_file):
    img_data = compress_image(image_file)
    run_query("UPDATE users SET avatar_data = ? WHERE username = ?", (img_data, username))
    get_user_styles.clear()
    return True

def get_user_change_count(username):
    res = run_query("SELECT change_count FROM users WHERE username = ?", (username,), fetch=True)
    return res[0][0] if res else 0

def change_username_logic(old_user, new_user):
    count = get_user_change_count(old_user)
    if not new_user: return False, "Boş olamaz."
    
    check = run_query("SELECT * FROM users WHERE username = ?", (new_user,), fetch=True)
    if check: return False, "Bu isim kullanımda."
    
    run_query("UPDATE users SET username = ?, change_count = change_count + 1 WHERE username = ?", (new_user, old_user))
    run_query("UPDATE posts SET username = ? WHERE username = ?", (new_user, old_user))
    run_query("UPDATE comments SET username = ? WHERE username = ?", (new_user, old_user))
    
    return True, "İsim değişti! Lütfen tekrar giriş yap."

def update_activity(username):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    run_query("UPDATE users SET last_seen = ? WHERE username = ?", (now, username))

# --- MAĞAZA SATIN ALMA ---
def buy_item(username, item_type, item_value, cost):
    from .score import get_total_score, add_score
    
    current_score = get_total_score(username)
    
    if current_score >= cost:
        try:
            add_score(username, -cost, f"Mağaza: {item_value}")
            query = f"UPDATE users SET {item_type} = ? WHERE username = ?"
            run_query(query, (item_value, username))
            
            get_user_styles.clear()
            
            return True, "Satın alma başarılı! Güle güle kullan."
        except Exception as e:
            return False, f"Hata oluştu: {e}"
    else:
        return False, "Yetersiz Bakiye!"
     # --- ADMIN FONKSİYONLARI ---
def get_all_users_list():
    # Tüm kullanıcı adlarını getir
    res = run_query("SELECT username, role, title FROM users", fetch=True)
    return res if res else []

def set_user_role(username, new_role):
    # Birini admin yapmak veya student'a düşürmek için
    run_query("UPDATE users SET role = ? WHERE username = ?", (new_role, username))
    return True

def admin_update_score(username, amount, reason="Admin İşlemi"):
    from .score import add_score
    # Puan ekle veya sil (eksi değer gönderilirse siler)
    add_score(username, amount, reason)
    return True

        
