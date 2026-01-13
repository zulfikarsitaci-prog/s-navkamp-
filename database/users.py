from .core import run_query
import hashlib
import io
from PIL import Image

# --- YARDIMCI: Resim Sıkıştırma ---
def compress_image(image_file):
    if not image_file: return None
    try:
        img = Image.open(image_file)
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Boyutlandırma (Çok büyükse küçült)
        if img.height > 1000 or img.width > 1000:
            img.thumbnail((1000, 1000))
            
        buf = io.BytesIO()
        img.save(buf, format='JPEG', quality=60)
        return buf.getvalue()
    except Exception as e:
        print(f"Resim hatası: {e}")
        return None

# --- YARDIMCI: Şifreleme ---
def make_hash(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def check_hash(password, hashed_text):
    if make_hash(password) == hashed_text:
        return True
    return False

# --- TEMEL GİRİŞ/KAYIT ---
def add_user(username, password, role="student"):
    if run_query("SELECT * FROM users WHERE username = ?", (username,), fetch=True):
        return False, "Bu isim alınmış."
    
    run_query("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", 
              (username, make_hash(password), role))
    run_query("INSERT INTO inventory (username, item_type, item_value) VALUES (?, ?, ?)", (username, "title", "Çırak"))
    return True, "Kayıt Başarılı"

def login_user(username, password):
    users = run_query("SELECT * FROM users WHERE username = ?", (username,), fetch=True)
    if users:
        user = users[0]
        if check_hash(password, user[2]):
            return user
    return None

# --- PROFİL YÖNETİMİ (EKSİK OLAN KISIMLAR) ---
def get_user_change_count(username):
    # İsim değiştirme sayısını getir
    res = run_query("SELECT change_count FROM users WHERE username = ?", (username,), fetch=True)
    return res[0][0] if res else 0

def update_avatar(username, file_obj):
    # Avatar güncelle
    blob = compress_image(file_obj)
    if blob:
        run_query("UPDATE users SET avatar = ? WHERE username = ?", (blob, username))
        return True
    return False

def change_username_logic(old_name, new_name):
    # İsim değiştirme mantığı
    if not new_name or len(new_name) < 3: return False, "İsim çok kısa."
    if run_query("SELECT * FROM users WHERE username = ?", (new_name,), fetch=True): return False, "Bu isim dolu."

    from .score import get_total_score, add_score
    count = get_user_change_count(old_name)
    cost = 500000 if count > 0 else 0

    if cost > 0:
        if get_total_score(old_name) < cost: return False, "Yetersiz Puan"
        add_score(old_name, -cost, "İsim Değişikliği")

    # Kritik tablolarda güncelleme
    try:
        run_query("UPDATE users SET username = ?, change_count = change_count + 1 WHERE username = ?", (new_name, old_name))
        run_query("UPDATE scores SET username = ? WHERE username = ?", (new_name, old_name))
        run_query("UPDATE posts SET username = ? WHERE username = ?", (new_name, old_name))
        run_query("UPDATE inventory SET username = ? WHERE username = ?", (new_name, old_name))
        return True, "İsim değiştirildi. Lütfen tekrar giriş yap."
    except:
        return False, "Veritabanı hatası."

# --- STİL & VERİ ÇEKME ---
def get_user_styles(username):
    res = run_query("SELECT avatar, frame, name_style, bg_style, font_style, title FROM users WHERE username = ?", (username,), fetch=True)
    if res:
        return res[0]
    return (None, None, None, None, None, "Çırak")

def get_user_role(username):
    res = run_query("SELECT role FROM users WHERE username = ?", (username,), fetch=True)
    return res[0][0] if res else None

def update_activity(username):
    run_query("UPDATE users SET last_active = CURRENT_TIMESTAMP WHERE username = ?", (username,))

# --- SATIN ALMA ---
def buy_item(username, item_type, item_value, cost):
    from .score import get_total_score, add_score
    
    current_score = get_total_score(username)
    if current_score < cost:
        return False, "Yetersiz Puan!"
    
    check = run_query("SELECT * FROM inventory WHERE username=? AND item_type=? AND item_value=?", 
                      (username, item_type, item_value), fetch=True)
    if not check:
        add_score(username, -cost, f"Satın Alma: {item_value}")
        run_query("INSERT INTO inventory (username, item_type, item_value) VALUES (?, ?, ?)", 
                  (username, item_type, item_value))
    
    col_map = {"frame": "frame", "name_style": "name_style", "font_style": "font_style", "title": "title"}
    if item_type in col_map:
        col = col_map[item_type]
        run_query(f"UPDATE users SET {col} = ? WHERE username = ?", (item_value, username))
        
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
