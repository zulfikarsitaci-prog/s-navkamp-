from .core import run_query
import hashlib

# --- YARDIMCI: Şifreleme ---
def make_hash(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def check_hash(password, hashed_text):
    if make_hash(password) == hashed_text:
        return True
    return False

# --- TEMEL FONKSİYONLAR ---
def add_user(username, password, role="student"):
    # Önce var mı bak
    if run_query("SELECT * FROM users WHERE username = ?", (username,), fetch=True):
        return False, "Bu isim alınmış."
    
    run_query("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", 
              (username, make_hash(password), role))
    
    # Başlangıç İtemleri
    run_query("INSERT INTO inventory (username, item_type, item_value) VALUES (?, ?, ?)", (username, "title", "Çırak"))
    return True, "Kayıt Başarılı"

def login_user(username, password):
    users = run_query("SELECT * FROM users WHERE username = ?", (username,), fetch=True)
    if users:
        user = users[0] # (id, user, pass, role, ...)
        # user[2] şifredir
        if check_hash(password, user[2]):
            return user
    return None

# --- STİL & VERİ ÇEKME ---
def get_user_styles(username):
    res = run_query("SELECT avatar, frame, name_style, bg_style, font_style, title FROM users WHERE username = ?", (username,), fetch=True)
    if res:
        return res[0] # (ava, frame, name, bg, font, title)
    return (None, None, None, None, None, "Çırak")

def get_user_role(username):
    res = run_query("SELECT role FROM users WHERE username = ?", (username,), fetch=True)
    return res[0][0] if res else None

def update_activity(username):
    run_query("UPDATE users SET last_active = CURRENT_TIMESTAMP WHERE username = ?", (username,))

# --- SATIN ALMA & ENVANTER ---
def buy_item(username, item_type, item_value, cost):
    # 1. Para yetiyor mu?
    from .score import get_total_score, add_score # Döngüsel importu önlemek için içeride
    
    current_score = get_total_score(username)
    if current_score < cost:
        return False, "Yetersiz Puan!"
    
    # 2. Zaten var mı?
    check = run_query("SELECT * FROM inventory WHERE username=? AND item_type=? AND item_value=?", 
                      (username, item_type, item_value), fetch=True)
    if check:
        # Zaten varsa sadece kuşan (Equip)
        pass
    else:
        # Yoksa satın al (Puan düş)
        add_score(username, -cost, f"Satın Alma: {item_value}")
        run_query("INSERT INTO inventory (username, item_type, item_value) VALUES (?, ?, ?)", 
                  (username, item_type, item_value))
    
    # 3. İtemi Kullan (Update User)
    col_map = {"frame": "frame", "name_style": "name_style", "font_style": "font_style", "title": "title"}
    if item_type in col_map:
        col = col_map[item_type]
        run_query(f"UPDATE users SET {col} = ? WHERE username = ?", (item_value, username))
        
    return True, "İşlem Başarılı"

# --- ADMIN İŞLEMLERİ ---
def get_all_users_list():
    return run_query("SELECT username, role, title FROM users", fetch=True)

def set_user_role(username, role):
    run_query("UPDATE users SET role = ? WHERE username = ?", (role, username))

def admin_update_score(username, amount, reason):
    from .score import add_score
    add_score(username, amount, reason)

def delete_user(username):
    run_query("DELETE FROM users WHERE username = ?", (username,))
