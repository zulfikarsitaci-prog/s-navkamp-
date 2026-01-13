from .core import run_query
import hashlib
import io
from PIL import Image

# --- RESİM SIKIŞTIRMA (Sistemin Çökmemesi İçin Şart) ---
def compress_image(image_file):
    if not image_file: return None
    try:
        img = Image.open(image_file)
        if img.mode != 'RGB':
            img = img.convert('RGB')
        if img.height > 1000 or img.width > 1000:
            img.thumbnail((1000, 1000))
        buf = io.BytesIO()
        img.save(buf, format='JPEG', quality=60)
        return buf.getvalue()
    except:
        return None

# --- ŞİFRELEME YARDIMCISI ---
def make_hash(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

# --- GİRİŞ VE KAYIT (ESKİ SİSTEM MANTIĞI) ---
def add_user(username, password, role="student"):
    # İsim kontrolü
    if run_query("SELECT * FROM users WHERE username = ?", (username,), fetch=True):
        return False, "Bu isim alınmış."
    
    # Yeni kayıtları şifreli yapalım (Güvenlik için)
    # Ama eski kullanıcıları etkilemez.
    hashed_pw = make_hash(password)
    
    run_query("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", 
              (username, hashed_pw, role))
    run_query("INSERT INTO inventory (username, item_type, item_value) VALUES (?, ?, ?)", (username, "title", "Çırak"))
    return True, "Kayıt Başarılı"

def login_user(username, password):
    # Kullanıcıyı bul
    users_data = run_query("SELECT * FROM users WHERE username = ?", (username,), fetch=True)
    
    if users_data:
        user = users_data[0] # (id, user, pwd, role...)
        stored_pwd = user[2] # Veritabanındaki şifre
        
        # 1. YÖNTEM: DÜZ METİN KONTROLÜ (Eski Kullanıcılar İçin)
        if stored_pwd == password:
            return user
            
        # 2. YÖNTEM: ŞİFRELİ KONTROL (Yeni Kullanıcılar İçin)
        if stored_pwd == make_hash(password):
            return user
            
    return None

# --- EKSİK OLAN TÜM FONKSİYONLAR (HATA VERMEMESİ İÇİN) ---

def get_user_change_count(username):
    res = run_query("SELECT change_count FROM users WHERE username = ?", (username,), fetch=True)
    return res[0][0] if res else 0

def update_avatar(username, file_obj):
    blob = compress_image(file_obj)
    if blob:
        run_query("UPDATE users SET avatar = ? WHERE username = ?", (blob, username))
        return True
    return False

def change_username_logic(old_name, new_name):
    if not new_name or len(new_name) < 3: return False, "İsim çok kısa."
    if run_query("SELECT * FROM users WHERE username = ?", (new_name,), fetch=True): return False, "Bu isim dolu."

    from .score import get_total_score, add_score
    cost = 500000 if get_user_change_count(old_name) > 0 else 0

    if cost > 0 and get_total_score(old_name) < cost:
        return False, "Yetersiz Puan"
    
    if cost > 0: add_score(old_name, -cost, "İsim Değişikliği")

    try:
        # İsim değişince her yeri güncelle
        run_query("UPDATE users SET username = ?, change_count = change_count + 1 WHERE username = ?", (new_name, old_name))
        tables = ["scores", "posts", "inventory", "likes", "comments", "poll_votes", "stories", "notifications", "friends", "messages"]
        for t in tables:
            try: run_query(f"UPDATE {t} SET username = ? WHERE username = ?", (new_name, old_name))
            except: pass
            
        # Mesajlardaki gönderici/alıcı sütunlarını da güncelle
        try: run_query("UPDATE messages SET sender = ? WHERE sender = ?", (new_name, old_name))
        except: pass
        try: run_query("UPDATE messages SET receiver = ? WHERE receiver = ?", (new_name, old_name))
        except: pass
            
        return True, "İsim değiştirildi."
    except:
        return False, "Hata oluştu."

def get_user_styles(username):
    res = run_query("SELECT avatar, frame, name_style, bg_style, font_style, title FROM users WHERE username = ?", (username,), fetch=True)
    if res: return res[0]
    return (None, None, None, None, None, "Çırak")

def get_user_role(username):
    res = run_query("SELECT role FROM users WHERE username = ?", (username,), fetch=True)
    return res[0][0] if res else None

def update_activity(username):
    run_query("UPDATE users SET last_active = CURRENT_TIMESTAMP WHERE username = ?", (username,))

def buy_item(username, item_type, item_value, cost):
    from .score import get_total_score, add_score
    if get_total_score(username) < cost: return False, "Yetersiz Puan!"
    
    check = run_query("SELECT * FROM inventory WHERE username=? AND item_type=? AND item_value=?", (username, item_type, item_value), fetch=True)
    if not check:
        add_score(username, -cost, f"Alındı: {item_value}")
        run_query("INSERT INTO inventory (username, item_type, item_value) VALUES (?, ?, ?)", (username, item_type, item_value))
    
    col_map = {"frame": "frame", "name_style": "name_style", "font_style": "font_style", "title": "title"}
    if item_type in col_map:
        run_query(f"UPDATE users SET {col_map[item_type]} = ? WHERE username = ?", (item_value, username))
    return True, "İşlem Başarılı"

# --- ADMIN ---
def get_all_users_list():
    return run_query("SELECT username, role, title FROM users", fetch=True)

def set_user_role(username, role):
    run_query("UPDATE users SET role = ? WHERE username = ?", (role, username))

def admin_update_score(username, amount, reason):
    from .score import add_score
    add_score(username, amount, reason)

def delete_user(username):
    run_query("DELETE FROM users WHERE username = ?", (username,))
