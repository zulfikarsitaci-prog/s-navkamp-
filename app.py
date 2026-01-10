import streamlit as st
import pandas as pd
import sqlite3
import hashlib
import os
import time
import random
import base64
import re
import io
from datetime import datetime
from PIL import Image

# --- AYARLAR ---
st.set_page_config(page_title="Bağarası ÇPAL", page_icon="🎓", layout="wide", initial_sidebar_state="expanded")

# --- VERİTABANI BAĞLANTISI ---
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
    except Exception as e: return False
    finally: cursor.close()

# --- VERİTABANI OLUŞTURMA & MIGRATION ---
def create_database():
    tables = [
        'CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE, password TEXT, role TEXT, last_seen TEXT, avatar_data TEXT, frame TEXT, name_style TEXT, post_style TEXT, font_style TEXT, title TEXT, change_count INTEGER DEFAULT 0, emoji_packs TEXT DEFAULT "Temel")',
        'CREATE TABLE IF NOT EXISTS grades (id INTEGER PRIMARY KEY AUTOINCREMENT, student_username TEXT, lesson TEXT, grade INTEGER, date TEXT)',
        'CREATE TABLE IF NOT EXISTS posts (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, content TEXT, image_data TEXT, timestamp TEXT, likes INTEGER DEFAULT 0)',
        'CREATE TABLE IF NOT EXISTS comments (id INTEGER PRIMARY KEY AUTOINCREMENT, post_id INTEGER, username TEXT, content TEXT, timestamp TEXT, is_read INTEGER DEFAULT 0)',
        'CREATE TABLE IF NOT EXISTS messages (id INTEGER PRIMARY KEY AUTOINCREMENT, sender TEXT, receiver TEXT, message TEXT, timestamp TEXT, is_read INTEGER DEFAULT 0)',
        'CREATE TABLE IF NOT EXISTS relationships (id INTEGER PRIMARY KEY AUTOINCREMENT, user1 TEXT, user2 TEXT, status TEXT)',
    ]
    for t in tables: run_query(t)
    
    # Eksik sütunları ekle (Eski DB varsa bozulmasın diye)
    cols = ["emoji_packs", "change_count", "avatar_data", "frame", "name_style", "post_style", "font_style", "title"]
    for col in cols:
        try: 
            dtype = "INTEGER DEFAULT 0" if col == "change_count" else "TEXT"
            run_query(f"ALTER TABLE users ADD COLUMN {col} {dtype}")
        except: pass

    # Admin Kullanıcısını Garantiye Al
    h = hashlib.sha256("6626".encode()).hexdigest()
    run_query("INSERT OR IGNORE INTO users (username, password, role, emoji_packs) VALUES (?, ?, ?, ?)", ("admin", h, "admin", "Temel"))

# --- YARDIMCI FONKSİYONLAR ---
def compress_image(image_file):
    try:
        img = Image.open(image_file).convert("RGB")
        img.thumbnail((600, 600))
        buffer = io.BytesIO()
        img.save(buffer, format="JPEG", quality=60)
        return base64.b64encode(buffer.getvalue()).decode()
    except: return None

def extract_youtube_link(text):
    if not text: return None
    match = re.search(r'(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/(watch\?v=|embed/|v/|live/|.+\?v=)?([^&=%\?]{11})', text)
    if match: return f"https://www.youtube.com/watch?v={match.group(6)}"
    return None

# --- KULLANICI İŞLEMLERİ ---
def login_user(u, p):
    h = hashlib.sha256(p.encode()).hexdigest()
    res = run_query("SELECT id, username, password, role FROM users WHERE username = ? AND password = ?", (u, h), fetch=True)
    return res[0] if res else None

def add_user(u, p, r):
    try:
        h = hashlib.sha256(p.encode()).hexdigest()
        success = run_query("INSERT INTO users (username, password, role, emoji_packs) VALUES (?, ?, ?, ?)", (u, h, r, "Temel"))
        if success:
            count = run_query("SELECT COUNT(*) FROM users", fetch=True)[0][0]
            if count <= 10:
                run_query("UPDATE users SET title = ?, frame = ? WHERE username = ?", ("KURUCU", "Gold", u))
                d = datetime.now().strftime("%Y-%m-%d %H:%M")
                run_query("INSERT INTO grades (student_username, lesson, grade, date) VALUES (?, ?, ?, ?)", (u, "İlk 10 Bonusu", 50000, d))
            return True, count
        return False, 0
    except: return False, 0

# --- EMOJI & MAĞAZA SİSTEMİ ---
EMOJI_PACKS_DATA = {
    "Temel": {"price": 0, "icons": ["😀", "😂", "😍", "😎", "🤔", "👍", "❤️", "🔥", "✨", "🎉"]},
    "Neon": {"price": 50000, "icons": ["👾", "🤖", "👽", "🦄", "🌈", "⚡", "💎", "🔮", "🧬", "🧿"]},
    "Korku": {"price": 75000, "icons": ["💀", "👻", "🧛", "🧟", "🕸️", "⚰️", "🔪", "🩸", "🎃", "🦇"]},
    "Zengin": {"price": 100000, "icons": ["💰", "💸", "🤑", "🏦", "💎", "💍", "👑", "🥂", "🏎️", "🚁"]},
    "Okul": {"price": 25000, "icons": ["🎓", "📚", "✏️", "🎒", "🏫", "📝", "📏", "📐", "🔬", "💻"]}
}

def get_user_emojis(username):
    res = run_query("SELECT emoji_packs FROM users WHERE username = ?", (username,), fetch=True)
    packs = res[0][0].split(",") if res and res[0][0] else ["Temel"]
    return packs

def buy_emoji_pack_logic(username, pack_name, cost):
    current_packs = get_user_emojis(username)
    if pack_name in current_packs: return False, "Zaten var."
    
    score = get_total_score(username)
    if score >= cost:
        add_score(username, -cost, "Mağaza: Emoji")
        new_packs = ",".join(current_packs + [pack_name])
        run_query("UPDATE users SET emoji_packs = ? WHERE username = ?", (new_packs, username))
        return True, "Paket alındı!"
    return False, "Puan yetersiz."

# --- VERİ ÇEKME FONKSİYONLARI ---
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

# --- ARKADAŞ & HEDİYE SİSTEMİ ---
def get_all_users_list(my_u):
    res = run_query("SELECT username FROM users WHERE username != ? AND username != 'admin'", (my_u,), fetch=True)
    return [r[0] for r in res] if res else []

def get_friends(u):
    rows = run_query("SELECT user1, user2 FROM relationships WHERE (user1=? OR user2=?) AND status='accepted'", (u, u), fetch=True)
    friends = []
    if rows:
        for r in rows: friends.append(r[1] if r[0] == u else r[0])
    return friends

def get_searchable_users(my_u):
    all_users = [r[0] for r in run_query("SELECT username FROM users WHERE username != 'admin' AND username != ?", (my_u,), fetch=True) or []]
    friends = get_friends(my_u)
    return [u for u in all_users if u not in friends]

# --- DİĞER İŞLEMLER ---
def add_post(u, c, i=None):
    d = compress_image(i) if i else None
    t = datetime.now().strftime("%Y-%m-%d %H:%M")
    run_query("INSERT INTO posts (username, content, image_data, timestamp, likes) VALUES (?, ?, ?, ?, 0)", (u, c, d, t))
def like_post(id): run_query("UPDATE posts SET likes = likes + 1 WHERE id = ?", (id,))
def delete_post(pid): run_query("DELETE FROM comments WHERE post_id = ?", (pid,)); run_query("DELETE FROM posts WHERE id = ?", (pid,))
def update_post(pid, c): run_query("UPDATE posts SET content = ? WHERE id = ?", (c, pid))
def add_comment(pid, u, c):
    t = datetime.now().strftime("%Y-%m-%d %H:%M")
    run_query("INSERT INTO comments (post_id, username, content, timestamp, is_read) VALUES (?, ?, ?, ?, 0)", (pid, u, c, t))
def update_avatar(u, img):
    d = compress_image(img)
    if d: run_query("UPDATE users SET avatar_data = ? WHERE username = ?", (d, u)); return True
    return False
def change_username_logic(current_user, new_user):
    if run_query("SELECT id FROM users WHERE username = ?", (new_user,), fetch=True): return False, "İsim dolu."
    res = run_query("SELECT change_count FROM users WHERE username = ?", (current_user,), fetch=True)
    change_count = res[0][0] if res else 0
    cost = 0 if change_count == 0 else 500000
    if get_total_score(current_user) < cost: return False, f"Yetersiz bakiye! Gerekli: {cost:,}"
    try:
        if cost > 0: add_score(current_user, -cost, "İsim Değişikliği")
        tables_cols = [("users", "username"), ("grades", "student_username"), ("posts", "username"), ("comments", "username"), ("messages", "sender"), ("messages", "receiver"), ("relationships", "user1"), ("relationships", "user2"), ("announcements", "author")]
        for t, c in tables_cols: run_query(f"UPDATE {t} SET {c} = ? WHERE {c} = ?", (new_user, current_user))
        run_query("UPDATE users SET change_count = change_count + 1 WHERE username = ?", (new_user,))
        return True, "Değiştirildi!"
    except Exception as e: return False, str(e)
def add_score(u, a, s="Sistem"):
    d = datetime.now().strftime("%Y-%m-%d %H:%M")
    run_query("INSERT INTO grades (student_username, lesson, grade, date) VALUES (?, ?, ?, ?)", (u, s, a, d))
def buy_item(u, type, value, cost):
    if get_total_score(u) >= cost:
        add_score(u, -cost, f"Mağaza: {value}")
        col = {"frame":"frame","name":"name_style","post":"post_style","font":"font_style","title":"title"}.get(type,"")
        if col: run_query(f"UPDATE users SET {col} = ? WHERE username = ?", (value, u)); return True, "Hayırlı olsun!"
    return False, "Puan yetersiz."
def send_gift(sender, receiver, gift_name, cost):
    if get_total_score(sender) >= cost:
        add_score(sender, -cost, f"Hediye: {gift_name} -> {receiver}")
        send_message(sender, receiver, f"🎁 SANA BİR HEDİYE GÖNDERDİ: {gift_name}!")
        return True, "Hediye gönderildi!"
    return False, "Puan yetersiz."
def update_activity(u):
    n = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    run_query("UPDATE users SET last_seen = ? WHERE username = ?", (n, u))
def send_message(s, r, m):
    t = datetime.now().strftime("%Y-%m-%d %H:%M")
    run_query("INSERT INTO messages (sender, receiver, message, timestamp) VALUES (?, ?, ?, ?)", (s, r, m, t))
def send_friend_request(s, r):
    if run_query("SELECT * FROM relationships WHERE (user1=? AND user2=?) OR (user1=? AND user2=?)", (s, r, r, s), fetch=True): return False, "Zaten ekli/istek var."
    run_query("INSERT INTO relationships (user1, user2, status) VALUES (?, ?, ?)", (s, r, 'pending')); return True, "İstek yollandı."
def get_pending_requests(u): return run_query("SELECT id, user1 FROM relationships WHERE user2=? AND status='pending'", (u,), fetch=True) or []
def accept_request(sender, me): run_query("UPDATE relationships SET status='accepted' WHERE user1=? AND user2=?", (sender, me))
def get_unread_notification_count(u):
    q = "SELECT COUNT(c.id) FROM comments c JOIN posts p ON c.post_id = p.id WHERE p.username = ? AND c.username != ? AND c.is_read = 0"
    res = run_query(q, (u, u), fetch=True)
    return res[0][0] if res else 0
def mark_notifications_read(u):
    run_query("UPDATE comments SET is_read = 1 WHERE id IN (SELECT c.id FROM comments c JOIN posts p ON c.post_id = p.id WHERE p.username = ? AND c.username != ?)", (u, u))
def delete_user(u):
    if u == "admin": return False
    run_query("DELETE FROM grades WHERE student_username = ?", (u,))
    run_query("DELETE FROM posts WHERE username = ?", (u,))
    run_query("DELETE FROM comments WHERE username = ?", (u,))
    run_query("DELETE FROM messages WHERE sender = ? OR receiver = ?", (u, u))
    run_query("DELETE FROM relationships WHERE user1 = ? OR user2 = ?", (u, u))
    run_query("DELETE FROM users WHERE username = ?", (u,))
    return True
def get_conversation(u1, u2):
    return run_query("SELECT sender, message, timestamp FROM messages WHERE (sender = ? AND receiver = ?) OR (sender = ? AND receiver = ?) ORDER BY id ASC", (u1, u2, u2, u1), fetch=True) or []

# --- INIT ---
def init_state():
    defaults = {
        "logged_in": False, "username": None, "user_role": None, "active_menu": "📢 Kampüs Duvar",
        "draft_content": "", "chat_target": None, "captcha_q": None, "captcha_a": None,
        "open_comments": [] # Yorumları açık postlar
    }
    for k, v in defaults.items():
        if k not in st.session_state: st.session_state[k] = v
    if not st.session_state['captcha_q']:
        n1, n2 = random.randint(1,9), random.randint(1,9)
        st.session_state['captcha_q'] = f"{n1} + {n2}"; st.session_state['captcha_a'] = n1 + n2

init_state()
create_database()

# --- CSS STİLLERİ ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@700&family=Orbitron:wght@700&family=Rye&family=Dancing+Script:wght@700&family=Metal+Mania&display=swap');
    
    .login-container { text-align: center; margin-top: 20px; }
    .login-main { font-family: 'Cinzel', serif; color: #FFD700; font-size: 2.2rem; text-shadow: 2px 2px 4px #000; }
    .login-sub { color: #94a3b8; font-family: sans-serif; letter-spacing: 1px; }
    
    .post-card { background: #1e293b; border: 1px solid #334155; border-radius: 12px; padding: 15px; margin-bottom: 5px; box-shadow: 0 4px 6px rgba(0,0,0,0.3); }
    .post-header { display: flex; align-items: center; border-bottom: 1px solid #334155; padding-bottom: 8px; margin-bottom: 8px; }
    .post-content { color: #e2e8f0; white-space: pre-wrap; margin-bottom: 10px; }
    
    div.stButton > button { background: transparent !important; border: none !important; color: #94a3b8 !important; padding: 0 !important; font-size: 1.3rem !important; box-shadow: none !important; }
    div.stButton > button:hover { color: #FFD700 !important; transform: scale(1.1); }
    
    div[data-testid="column"] { width: auto !important; flex: 0 0 auto !important; min-width: 0 !important; padding: 0 !important; margin-right: 15px !important; }
    div[data-testid="stHorizontalBlock"] { flex-wrap: nowrap !important; align-items: center !important; }

    .shop-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 6px; margin-top: 10px; }
    @media only screen and (max-width: 600px) { .shop-grid { grid-template-columns: repeat(3, 1fr); } }
    .shop-item { background: #0f172a; border: 1px solid #334155; border-radius: 8px; padding: 5px; text-align: center; height: 110px; display: flex; flex-direction: column; justify-content: space-between; }
    .shop-name { font-size: 0.65rem; color: #cbd5e1; }
    .shop-price { background: #10b981; color: white; padding: 2px 8px; border-radius: 8px; font-size: 0.65rem; }

    .avatar-img { width: 40px; height: 40px; border-radius: 50%; object-fit: cover; }
    .frame-overlay { position: absolute; top: -3px; left: -3px; width: 46px; height: 46px; pointer-events: none; }
    
    .frame-Gold { border: 2px solid #FFD700; border-radius: 50%; box-shadow: 0 0 5px #FFD700; }
    .frame-Neon { border: 2px solid #00ffff; border-radius: 50%; box-shadow: 0 0 5px #00ffff; }
    .frame-Fire { border: 2px solid #ff4500; border-radius: 50%; box-shadow: 0 0 10px #ff4500; }
    .frame-King { border: 3px solid #ffd700; border-radius: 50%; box-shadow: 0 0 10px #ffd700; }
    
    .name-Glitch { color: #00ffff; text-shadow: 1px 0 #ff00ff; font-weight: bold; }
    .name-Fire { color: #ff4500; text-shadow: 0 0 3px #ff0000; font-weight: bold; }
    .name-Gold { background: linear-gradient(to right, #BF953F, #FCF6BA, #B38728); -webkit-background-clip: text; color: transparent; font-weight: 900; }
    
    .font-Cinzel { font-family: 'Cinzel', serif; } .font-Orbitron { font-family: 'Orbitron', sans-serif; }
    .font-Rye { font-family: 'Rye', serif; } .font-Dancing { font-family: 'Dancing Script', cursive; }
    .font-Metallic { font-family: 'Metal Mania', cursive; color: #b0b0b0; text-shadow: 2px 2px 0px #000; }
    
    .post-Cyan { color: #00ffff !important; } .post-Lime { color: #00ff00 !important; } .post-Pink { color: #ff69b4 !important; } .post-Gold { color: #ffd700 !important; }
    .title-badge { background: #334155; color: #94a3b8; padding: 1px 5px; border-radius: 3px; font-size: 0.6rem; margin-left: 4px; }
</style>
""", unsafe_allow_html=True)

def get_user_display_html(username, size=40):
    styles = get_user_styles(username)
    ava, frame, name_style, _, font_style, title = styles
    img_src = f"data:image/jpeg;base64,{ava}" if ava else "https://via.placeholder.com/150/CCCCCC/FFFFFF?text=U"
    f_html = f'<div class="frame-overlay frame-{frame}"></div>' if frame else ""
    classes = f"{f'name-{name_style}' if name_style else ''} {f'font-{font_style}' if font_style else ''}"
    return f'<div style="display:flex;align-items:center;"><div style="position:relative;margin-right:10px;"><img src="{img_src}" class="avatar-img">{f_html}</div><div class="{classes}" style="font-size:0.9rem;">{username} {f"<span class='title-badge'>{title}</span>" if title else ""}</div></div>'

def get_post_css(username):
    s = get_user_styles(username)
    return f"post-{s[3]} font-{s[4]}"

def emoji_picker_component(key_prefix):
    user_packs = get_user_emojis(st.session_state['username'])
    with st.popover("😀"):
        tabs = st.tabs(user_packs)
        for i, pack in enumerate(user_packs):
            with tabs[i]:
                icons = EMOJI_PACKS_DATA.get(pack, EMOJI_PACKS_DATA["Temel"])["icons"]
                cols = st.columns(5)
                for idx, icon in enumerate(icons):
                    if cols[idx % 5].button(icon, key=f"{key_prefix}_{pack}_{idx}"):
                        st.session_state['draft_content'] += icon
                        st.rerun()

# --- ANA AKIŞ ---
if not st.session_state['logged_in']:
    st.markdown('<div class="login-container"><div class="login-sub">Muhasebe ve Finansman Alanı</div><div class="login-main">DİJİTAL GELİŞİM PLATFORMU</div><div class="login-sub">~ Dijital Kampüs ~</div></div>', unsafe_allow_html=True)
    
    with st.sidebar:
        # SIFIRLAMA BUTONU (GİRİŞ YAPAMAYANLAR İÇİN)
        if st.button("⚠️ Veritabanını Sıfırla"):
            try:
                os.remove("education_platform.db")
                st.success("Veritabanı sıfırlandı! Şimdi admin/6626 ile giriş yap.")
                time.sleep(2)
                st.rerun()
            except: st.error("Dosya bulunamadı veya silinemedi.")

    with st.container():
        with st.form("login"):
            u = st.text_input("Kullanıcı Adı")
            p = st.text_input("Şifre", type="password")
            if st.form_submit_button("Giriş"):
                user = login_user(u, p)
                if user:
                    st.session_state.update({'logged_in':True, 'username':user[1], 'user_role':user[3]})
                    st.rerun()
                else: st.error("Hatalı!")
        
        with st.expander("Kayıt Ol"):
            with st.form("reg"):
                nu = st.text_input("Kullanıcı"); np = st.text_input("Şifre", type="password")
                st.write(f"Güvenlik: **{st.session_state['captcha_q']} = ?**")
                ans = st.number_input("Cevap", step=1)
                if st.form_submit_button("Kayıt"):
                    if ans == st.session_state['captcha_a']:
                        res, rank = add_user(nu, np, "student")
                        if res:
                            st.session_state['captcha_q'] = None
                            if rank<=10: st.balloons(); st.success("KURUCU ünvanı kazandın!")
                            else: st.success("Kaydedildi.")
                        else: st.error("İsim dolu.")
                    else: st.error("Yanlış cevap."); st.session_state['captcha_q'] = None; st.rerun()

else:
    with st.sidebar:
        st.markdown(get_user_display_html(st.session_state['username'], 70), unsafe_allow_html=True)
        st.write("")
        with st.expander("⚙️ Hesabım"):
            nname = st.text_input("Yeni İsim")
            cost = 0 if get_user_change_count(st.session_state['username']) == 0 else 500000
            if st.button(f"Değiştir ({cost:,} P)"):
                if nname:
                    ok, msg = change_username_logic(st.session_state['username'], nname)
                    if ok: st.session_state['username'] = nname; st.success(msg); time.sleep(2); st.rerun()
                    else: st.error(msg)
            st.divider()
            uimg = st.file_uploader("Fotoğraf", type=['png','jpg'])
            if uimg:
                if update_avatar(st.session_state['username'], uimg): st.success("Oldu!"); time.sleep(1); st.rerun()
            st.divider()
            su = st.selectbox("Arkadaş Ekle", get_searchable_users(st.session_state['username']))
            if st.button("İstek Gönder"):
                ok, msg = send_friend_request(st.session_state['username'], su)
                if ok: st.success(msg)
                else: st.warning(msg)
        
        reqs = get_pending_requests(st.session_state['username'])
        if reqs:
            st.info("İstekler Var")
            for r in reqs:
                c1, c2 = st.columns([2,1])
                c1.write(r[1])
                if c2.button("Kabul", key=f"ac_{r[0]}"): accept_request(r[1], st.session_state['username']); st.rerun()
        
        st.write(""); 
        if st.button("🚪 Çıkış"): st.session_state['logged_in']=False; st.rerun()

    st.markdown(f'<div style="background:#1e293b;padding:10px;border-radius:8px;border-bottom:2px solid #FFD700;margin-bottom:10px;color:white;">Merhaba, <b>{st.session_state["username"]}</b></div>', unsafe_allow_html=True)
    
    mark_notifications_read(st.session_state['username'])
    menu = ["📢 Kampüs Duvar", "💬 Mesaj", "🏆 Puan", "🛒 Mağaza", "🎮 Oyun"]
    if st.session_state['user_role'] == 'admin': menu.append("⚙️ Admin")
    sel = st.radio("", menu, horizontal=True, label_visibility="collapsed")

    if sel == "📢 Kampüs Duvar":
        st.subheader("Kampüs Duvar")
        ms = get_total_score(st.session_state['username'])
        if ms >= 1000000 or st.session_state['user_role'] == 'admin':
            with st.expander("✨ Paylaşım (-100,000 P)", expanded=False):
                col_e, col_t = st.columns([0.1, 0.9])
                with col_e: emoji_picker_component("pe")
                with col_t: txt = st.text_area("İçerik", value=st.session_state['draft_content'], key="ptxt")
                img = st.file_uploader("Resim", type=['png','jpg'])
                if st.button("Paylaş"):
                    if ms >= 100000:
                        add_score(st.session_state['username'], -100000, "Post")
                        add_post(st.session_state['username'], txt, img)
                        st.session_state['draft_content'] = ""
                        st.rerun()
                    else: st.error("Yetersiz Puan")
        else: st.info("Paylaşım için 1M Puan gerekli.")

        posts = get_posts(20)
        for p in posts:
            st.markdown(f"""
            <div class="post-card">
                <div class="post-header">
                    {get_user_display_html(p[1], 35)}
                    <span style="color:gray;font-size:0.7rem;margin-left:auto;">{p[4]}</span>
                </div>
                <div class="{get_post_css(p[1])} post-content">{p[2] if p[2] else ''}</div>
                {f'<img src="data:image/jpeg;base64,{p[3]}" style="width:100%;border-radius:8px;">' if p[3] else ''}
            </div>
            """, unsafe_allow_html=True)
            
            if p[2]:
                yt = extract_youtube_link(p[2])
                if yt: st.video(yt)

            c1, c2, c3, c4 = st.columns([0.15, 0.15, 0.15, 0.55])
            with c1: 
                if st.button(f"❤️ {p[5]}", key=f"l_{p[0]}"): like_post(p[0]); st.rerun()
            with c2: st.markdown("<div style='padding-top:4px;color:#94a3b8;cursor:default;'>💬</div>", unsafe_allow_html=True)
            with c3:
                if st.button("🔄", key=f"r_{p[0]}"): 
                    st.session_state['draft_content'] = f"Alıntı (@{p[1]}): {p[2]}"
                    st.toast("Yukarı taşındı!")

            with c4:
                _, sc2 = st.columns([0.8, 0.2])
                with sc2:
                    with st.popover("➕"):
                        if st.button("💬 Yorum Yap", key=f"cbtn_{p[0]}"):
                            if p[0] in st.session_state['open_comments']: st.session_state['open_comments'].remove(p[0])
                            else: st.session_state['open_comments'].append(p[0])
                            st.rerun()
                        if st.button("🔄 Paylaş", key=f"rpbtn_{p[0]}"):
                            st.session_state['draft_content'] = f"Alıntı (@{p[1]}): {p[2]}"
                            st.rerun()
                        if st.session_state['username'] == p[1] or st.session_state['user_role'] == 'admin':
                            if st.button("🗑️ Sil", key=f"dbtn_{p[0]}"): delete_post(p[0]); st.rerun()

            if p[0] in st.session_state['open_comments']:
                coms = get_comments(p[0])
                if coms:
                    for c in coms: st.markdown(f"<div class='comment-box'>{get_user_display_html(c[0], 20)} {c[1]}</div>", unsafe_allow_html=True)
                
                ce, ct = st.columns([0.15, 0.85])
                with ce: emoji_picker_component(f"cem_{p[0]}")
                with ct: cmt = st.text_input("Yorum...", key=f"cin_{p[0]}", label_visibility="collapsed")
                
                if st.button("Gönder", key=f"csend_{p[0]}"):
                    full_cmt = (st.session_state['draft_content'] + " " + cmt).strip()
                    if full_cmt:
                        add_comment(p[0], st.session_state['username'], full_cmt)
                        st.session_state['draft_content'] = ""
                        st.rerun()
            st.write("")

    elif sel == "💬 Mesaj":
        st.subheader("Mesajlaşma")
        friends = get_friends(st.session_state['username'])
        if not friends: st.warning("Henüz arkadaşın yok. Yan menüden ekleyebilirsin.")
        else:
            target = st.selectbox("Kime:", friends)
            if target:
                msgs = get_conversation(st.session_state['username'], target)
                for m in msgs:
                    align = "row-reverse" if m[0] == st.session_state['username'] else "row"
                    bg = "#2563eb" if m[0] == st.session_state['username'] else "#334155"
                    st.markdown(f"""<div style="display:flex;flex-direction:{align};margin-bottom:5px;">
                        <div style="background:{bg};padding:8px;border-radius:10px;max-width:70%;">{m[1]}</div>
                    </div>""", unsafe_allow_html=True)
                
                c1, c2 = st.columns([0.1, 0.9])
                with c1: emoji_picker_component("msg_em")
                with c2: msg_txt = st.text_input("Mesaj", key="msg_in")
                
                if st.button("Gönder"):
                    full_msg = (st.session_state['draft_content'] + " " + msg_txt).strip()
                    if full_msg:
                        send_message(st.session_state['username'], target, full_msg)
                        st.session_state['draft_content'] = ""
                        st.rerun()

    elif sel == "🛒 Mağaza":
        st.header("Mağaza")
        st.metric("Bakiye", f"{get_total_score(st.session_state['username']):,} P")
        tabs = st.tabs(["Çerçeve", "İsim", "Font", "Hediye", "Emoji"])
        
        with tabs[4]: # EMOJI
            st.info("Mesajlarda kullan.")
            cols = st.columns(4)
            for i, (pn, pd) in enumerate(EMOJI_PACKS_DATA.items()):
                if pn == "Temel": continue
                with cols[i%4]:
                    st.markdown(f"<div class='shop-item'><div style='font-size:2rem'>{pd['icons'][0]}</div><div class='shop-name'>{pn}</div><div class='shop-price'>{pd['price']:,}</div></div>", unsafe_allow_html=True)
                    if st.button("Al", key=f"bp_{pn}"):
                        ok, msg = buy_emoji_pack_logic(st.session_state['username'], pn, pd['price'])
                        if ok: st.success(msg); time.sleep(1); st.rerun()
                        else: st.error(msg)

        with tabs[3]: # HEDİYE
            st.info("Okuldaki herkese.")
            all_users = get_all_users_list(st.session_state['username'])
            t_user = st.selectbox("Kime:", all_users)
            gifts = [("Kahve ☕", 5000), ("Çikolata 🍫", 10000), ("Gül 🌹", 25000), ("Taç 👑", 100000)]
            cols = st.columns(4)
            for i, (gn, gp) in enumerate(gifts):
                with cols[i]:
                    st.markdown(f"<div class='shop-item'><div class='shop-name'>{gn}</div><div class='shop-price'>{gp:,}</div></div>", unsafe_allow_html=True)
                    if st.button("Gönder", key=f"g_{i}"):
                        ok, msg = send_gift(st.session_state['username'], t_user, gn, gp)
                        if ok: st.success(msg)
                        else: st.error(msg)
        
        # Diğer sekmeler...
        with tabs[0]: 
            items = [{"n": "Gold", "c": 50000, "t": "frame", "v": "Gold"}, {"n": "Neon", "c": 150000, "t": "frame", "v": "Neon"}, {"n": "Alev", "c": 300000, "t": "frame", "v": "Fire"}, {"n": "Kral", "c": 2000000, "t": "frame", "v": "King"}]
            cols = st.columns(4)
            for i, it in enumerate(items):
                with cols[i]:
                    st.markdown(f"<div class='shop-item'><div class='shop-name'>{it['n']}</div><div class='shop-price'>{it['c']:,}</div></div>", unsafe_allow_html=True)
                    if st.button("Al", key=f"bi_{i}"):
                        ok, msg = buy_item(st.session_state['username'], it['t'], it['v'], it['c'])
                        if ok: st.success(msg); time.sleep(1); st.rerun()
                        else: st.error(msg)

    elif sel == "🏆 Puan":
        st.dataframe(pd.DataFrame(run_query("SELECT student_username, SUM(grade) as T FROM grades GROUP BY student_username ORDER BY T DESC", fetch=True), columns=["Öğrenci","Puan"]), use_container_width=True)

    elif sel == "⚙️ Admin":
        st.write("Admin Paneli")
        all_u = get_all_users()
        tu = st.selectbox("Kullanıcı", all_u)
        np = st.number_input("Puan", value=0)
        if st.button("Güncelle"): add_score(tu, np, "Admin"); st.success("Tamam!")
        if st.button("Sil"): delete_user(tu); st.rerun()
