import streamlit as st
from .core import run_query
import hashlib

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
    # Varsayılan değerlerle kullanıcı oluştur
    run_query("INSERT INTO users (username, password, role, frame, name_style, title, avatar_data) VALUES (?, ?, ?, ?, ?, ?, ?)", 
              (username, hashed_pw, role, "", "", "Çırak", None))
    return True, "Kayıt Başarılı"

def login_user(username, password):
    hashed_pw = make_hashes(password)
    result = run_query("SELECT * FROM users WHERE username = ? AND password = ?", (username, hashed_pw), fetch=True)
    return result[0] if result else None

def get_user_styles(username):
    # Avatar, Çerçeve, İsim Stili, Post Stili, Font Stili, Ünvan
    res = run_query("SELECT avatar_data, frame, name_style, post_style, font_style, title FROM users WHERE username = ?", (username,), fetch=True)
    if res:
        return res[0]
    return (None, "", "", "", "", "Çırak")

def update_avatar(username, image_file):
    img_data = compress_image(image_file)
    run_query("UPDATE users SET avatar_data = ? WHERE username = ?", (img_data, username))
    get_user_styles.clear()
    return True

def get_user_change_count(username):
    res = run_query("SELECT change_count FROM users WHERE username = ?", (username,), fetch=True)
    return res[0][0] if res else 0

def change_username_logic(old_user, new_user):
    # İsim değiştirme mantığı
    count = get_user_change_count(old_user)
    cost = 500000 if count > 0 else 0
    
    # Puan kontrolü burada yapılabilir (döngüsel import olmaması için basitleştirildi)
    # Şimdilik sadece isim boş mu ve alınmış mı ona bakalım
    if not new_user: return False, "Boş olamaz."
    
    check = run_query("SELECT * FROM users WHERE username = ?", (new_user,), fetch=True)
    if check: return False, "Bu isim kullanımda."
    
    # İsim güncelle
    run_query("UPDATE users SET username = ?, change_count = change_count + 1 WHERE username = ?", (new_user, old_user))
    # İlişkili tabloları güncelle (posts, comments vb. normalde ID ile bağlı olmalı ama text ise güncellenmeli)
    run_query("UPDATE posts SET username = ? WHERE username = ?", (new_user, old_user))
    run_query("UPDATE comments SET username = ? WHERE username = ?", (new_user, old_user))
    
    return True, "İsim değişti! Lütfen tekrar giriş yap."

# --- MAĞAZA SATIN ALMA (BU FONKSİYON EKSİKTİ) ---
def buy_item(username, item_type, item_value, cost):
    # Puan sistemini buradan çağırıyoruz (Circular import önlemek için fonksiyon içinde)
    from .score import get_total_score, add_score
    
    # 1. Bakiyeyi Kontrol Et
    current_score = get_total_score(username)
    
    if current_score >= cost:
        try:
            # 2. Puanı Düş (Negatif puan ekleyerek)
            add_score(username, -cost, f"Mağaza: {item_value}")
            
            # 3. Eşyayı Ver
            # item_type: 'frame', 'name_style', 'title' vb. (veritabanı sütun isimleri)
            # item_value: 'King', 'Gold', 'Emperor' vb.
            
            query = f"UPDATE users SET {item_type} = ? WHERE username = ?"
            run_query(query, (item_value, username))
            
            # Cache'i temizle ki hemen görünsün
            get_user_styles.clear()
            
            return True, "Satın alma başarılı! Güle güle kullan."
        except Exception as e:
            return False, f"Hata oluştu: {e}"
    else:
        return False, "Yetersiz Bakiye!"
