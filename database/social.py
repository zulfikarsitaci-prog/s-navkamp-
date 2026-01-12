from datetime import datetime, timedelta
import random
import streamlit as st
from .core import run_query
from .users import compress_image
# Puan eklemek için score modülünü fonksiyon içinde çağıracağız (Circular import önlemek için)

# --- ÖNBELLEK (CACHE) ---
@st.cache_data(ttl=2)
def get_posts(limit=20): 
    # Anket seçeneklerini de çekiyoruz (poll_options)
    return run_query("SELECT id, username, content, image_data, timestamp, likes, poll_options FROM posts ORDER BY id DESC LIMIT ?", (limit,), fetch=True) or []

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

# --- GÜNLÜK ŞANS KUTUSU ---
def try_open_daily_box(username):
    from .score import add_score # Burada import ediyoruz
    
    # 1. Zaman Kontrolü
    res = run_query("SELECT last_daily_box FROM users WHERE username = ?", (username,), fetch=True)
    last_date_str = res[0][0] if res and res[0][0] else None
    
    now = datetime.now()
    
    if last_date_str:
        try:
            last_date = datetime.strptime(last_date_str, "%Y-%m-%d %H:%M:%S")
            diff = now - last_date
            if diff.total_seconds() < 86400: # 24 saat = 86400 saniye
                remaining = timedelta(seconds=86400 - diff.total_seconds())
                hours, remainder = divmod(remaining.seconds, 3600)
                minutes, _ = divmod(remainder, 60)
                return False, f"Kutuyu açmak için {hours} sa {minutes} dk beklemelisin!", None
        except:
            pass # Tarih formatı hatası varsa devam et (ilk kez gibi davran)

    # 2. Ödül Belirleme (Algoritma)
    rand = random.randint(1, 100)
    reward_type = ""
    msg = ""

    if rand <= 5: # %5 Şans: Efsanevi Eşya
        items = [("frame", "Ghost", "👻 Hayalet Çerçeve"), ("title", "Kahin", "🔮 Kahin Ünvanı")]
        item = random.choice(items)
        col = item[0]
        # Kullanıcıda zaten var mı kontrol etmiyoruz, direkt veriyoruz (Basitlik için)
        run_query(f"UPDATE users SET {col} = ? WHERE username = ?", (item[1], username))
        msg = f"İNANILMAZ! Nadir Eşya Kazandın: {item[2]}"
        reward_type = "item"
        
    elif rand <= 20: # %15 Şans: Büyük Puan
        points = random.randint(5000, 10000)
        add_score(username, points, "Şans Kutusu")
        msg = f"SÜPER! {points:,} Puan Kazandın!"
        reward_type = "points"
        
    else: # %80 Şans: Standart Puan
        points = random.randint(1000, 4000)
        add_score(username, points, "Şans Kutusu")
        msg = f"Tebrikler! {points:,} Puan Çıktı."
        reward_type = "points"

    # 3. Tarihi Güncelle
    new_date = now.strftime("%Y-%m-%d %H:%M:%S")
    run_query("UPDATE users SET last_daily_box = ? WHERE username = ?", (new_date, username))
    
    # Cache temizle (Stil değişmiş olabilir)
    from .users import get_user_styles
    get_user_styles.clear()
    
    return True, msg, reward_type

# --- ANKET SİSTEMİ ---
def add_poll_post(u, content, options_list):
    # Options listesini stringe çevir (Örn: "Evet,Hayır,Belki")
    opts_str = ",".join([o.strip() for o in options_list if o.strip()])
    t = datetime.now().strftime("%Y-%m-%d %H:%M")
    run_query("INSERT INTO posts (username, content, timestamp, likes, poll_options) VALUES (?, ?, ?, 0, ?)", (u, content, t, opts_str))
    get_posts.clear()

def vote_poll(post_id, username, option_index):
    # Önce daha önce oy vermiş mi bak
    check = run_query("SELECT id FROM poll_votes WHERE post_id = ? AND username = ?", (post_id, username), fetch=True)
    if check:
        return False, "Zaten oy kullandın!"
    
    run_query("INSERT INTO poll_votes (post_id, username, option_index) VALUES (?, ?, ?)", (post_id, username, option_index))
    return True, "Oy verildi!"

def get_poll_results(post_id, options_str):
    if not options_str: return [], 0, False
    options = options_str.split(",")
    # Sonuçları hesapla
    votes = run_query("SELECT option_index FROM poll_votes WHERE post_id = ?", (post_id,), fetch=True) or []
    total_votes = len(votes)
    
    # Her seçeneğin sayısını bul
    counts = [0] * len(options)
    for v in votes:
        idx = v[0]
        if 0 <= idx < len(counts):
            counts[idx] += 1
            
    # Kullanıcı oy vermiş mi?
    my_vote = run_query("SELECT option_index FROM poll_votes WHERE post_id = ? AND username = ?", (post_id, st.session_state.get('username')), fetch=True)
    has_voted = True if my_vote else False
    
    return list(zip(options, counts)), total_votes, has_voted

# --- HİKAYE FONKSİYONLARI (CACHE EKLENDİ) ---
@st.cache_data(ttl=60)
def get_active_stories():
    # Sadece süresi dolmamış hikayeleri çek
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    return run_query("SELECT id, username, content, image_data, timestamp FROM stories WHERE expires_at > ? ORDER BY id DESC", (now,), fetch=True) or []

@st.cache_data(ttl=60)
def get_my_stories(username):
    return run_query("SELECT id, content, timestamp, expires_at FROM stories WHERE username = ? ORDER BY id DESC", (username,), fetch=True) or []

def add_story(u, img, txt=""):
    d = compress_image(img) if img else None
    t = datetime.now()
    ts = t.strftime("%Y-%m-%d %H:%M")
    exp = (t + timedelta(hours=24)).strftime("%Y-%m-%d %H:%M")
    run_query("INSERT INTO stories (username, content, image_data, timestamp, expires_at) VALUES (?, ?, ?, ?, ?)", (u, txt, d, ts, exp))
    
    # Artık hata vermez çünkü fonksiyonlar @st.cache_data ile işaretlendi
    get_active_stories.clear()
    get_my_stories.clear()

def delete_story(story_id):
    run_query("DELETE FROM stories WHERE id = ?", (story_id,))
    get_active_stories.clear()
    get_my_stories.clear()

# --- DİĞERLERİ ---
def add_post(u, c, i=None):
    d = compress_image(i) if i else None
    t = datetime.now().strftime("%Y-%m-%d %H:%M")
    run_query("INSERT INTO posts (username, content, image_data, timestamp, likes) VALUES (?, ?, ?, ?, 0)", (u, c, d, t))
    get_posts.clear()

def like_post(id): run_query("UPDATE posts SET likes = likes + 1 WHERE id = ?", (id,)); get_posts.clear()
def delete_post(pid): 
    run_query("DELETE FROM comments WHERE post_id = ?", (pid,))
    run_query("DELETE FROM posts WHERE id = ?", (pid,))
    run_query("DELETE FROM poll_votes WHERE post_id = ?", (pid,))
    get_posts.clear()

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
