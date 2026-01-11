import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import random
import database
import re
import time
import os
import json

# --- AYARLAR ---
st.set_page_config(page_title="Bağarası ÇPAL", page_icon="🎓", layout="wide", initial_sidebar_state="expanded")

# --- SINAV VERİSİ ---
def check_exams_json():
    if not os.path.exists("exams.json"):
        data = {
            "9. Sınıf": {
                "Muhasebe": [{"question": "Kasa hesabı kodu nedir?", "options": ["100", "102", "300"], "answer": "100", "points": 20, "type":"test"}],
            },
            "10. Sınıf": {
                "Genel Muhasebe": [{"question": "Bilançonun sol tarafı?", "answer": "Aktif", "points": 20, "type":"text"}]
            }
        }
        with open("exams.json", "w", encoding="utf-8") as f: json.dump(data, f, ensure_ascii=False)
check_exams_json()

# --- CSS (MAVİ KUTU, CİNZEL, STİL) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@700&family=Orbitron:wght@700&family=Roboto:wght@300;700&display=swap');

    /* GİRİŞ EKRANI */
    .login-container { 
        text-align: center; 
        background: linear-gradient(135deg, #1e3a8a 0%, #172554 100%);
        padding: 40px; 
        border-radius: 20px; 
        border: 2px solid #60a5fa;
        margin-bottom: 20px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.5);
    }
    .login-sub { color: #93c5fd; font-family: 'Roboto', sans-serif; letter-spacing: 3px; font-size: 1.1rem; }
    .login-main { 
        font-family: 'Cinzel', serif; color: #fbbf24; 
        font-size: 2.8rem; text-shadow: 2px 2px 4px #000; 
        font-weight: bold; margin: 10px 0; 
    }
    .login-bottom { color: #e0f2fe; font-family: 'Orbitron', sans-serif; font-size: 0.9rem; }

    /* DASHBOARD CARD */
    .metric-card {
        background: #1e293b; border: 1px solid #475569; border-radius: 8px; padding: 15px;
        text-align: center; color: white; cursor: default;
    }
    .metric-val { font-size: 1.5rem; font-weight: bold; color: #fbbf24; }
    .metric-lbl { font-size: 0.9rem; color: #cbd5e1; }

    /* MAĞAZA STİLİ */
    .shop-item { 
        background: #0f172a; 
        border: 1px solid #334155; 
        border-radius: 12px; 
        padding: 10px; 
        text-align: center; 
        display: flex; 
        flex-direction: column; 
        align-items: center; 
        justify-content: space-between; 
        height: 160px; 
        margin-bottom: 10px;
    }
    .shop-icon-box { font-size: 3rem; margin-bottom: 5px; }
    .shop-name { font-size: 0.85rem; color: #cbd5e1; font-weight: bold; margin-bottom: 5px; }
    
    /* POST KARTI */
    .post-card { background-color: #0f172a; border: 1px solid #334155; border-radius: 15px; padding: 15px; margin-bottom: 15px; }
    .post-header { display: flex; align-items: center; margin-bottom: 10px; border-bottom: 1px solid #1e293b; padding-bottom: 5px; }
    
    /* ÇERÇEVELER VE İSİMLER */
    .avatar-img { width: 50px; height: 50px; border-radius: 50%; object-fit: cover; margin-right:10px; }
    .frame-overlay { position: absolute; top: -3px; left: -3px; width: 56px; height: 56px; pointer-events: none; }
    
    .frame-Gold { border: 2px solid #FFD700; box-shadow: 0 0 10px #FFD700; }
    .frame-Neon { border: 2px solid #00ffff; box-shadow: 0 0 10px #00ffff; }
    .frame-Fire { border: 2px solid #ff4500; box-shadow: 0 0 15px #ff0000; }
    .frame-King { border: 3px solid #ffd700; box-shadow: 0 0 15px #ffd700; }
    .frame-Matrix { border: 2px dotted #00ff00; }
    
    .name-Glitch { color: #00ffff; text-shadow: 2px 0 #ff00ff; }
    .name-Gold { background: linear-gradient(to right, #BF953F, #FCF6BA, #B38728); -webkit-background-clip: text; color: transparent; font-weight: bold; }
    
    /* BUTONLAR */
    div.stButton > button { width: 100%; border-radius: 5px; border: 1px solid #334155; }
    div.stButton > button:hover { border-color: #fbbf24; color: #fbbf24; }
</style>
""", unsafe_allow_html=True)

# --- INIT ---
def init():
    if 'logged_in' not in st.session_state:
        st.session_state.update({'logged_in': False, 'username': None, 'role': None, 'active_menu': 'Ana Sayfa', 'captcha': None, 'open_comments': []})
    if st.session_state['captcha'] is None:
        n1, n2 = random.randint(1,10), random.randint(1,10)
        st.session_state['captcha'] = {'q': f"{n1} + {n2}", 'a': n1+n2}

database.create_database()
init()

# --- YARDIMCILAR ---
def get_user_display_html(username, size=40):
    u = database.get_user_data(username)
    ava, frame, name_style = u[2], u[3], u[4]
    img = f"data:image/jpeg;base64,{ava}" if ava else "https://via.placeholder.com/150"
    fr = f"frame-{frame}" if frame else ""
    nm = f"name-{name_style}" if name_style else ""
    
    return f"""
    <div style="display:flex;align-items:center;">
        <div style="position:relative;">
            <img src="{img}" class="avatar-img {fr}">
        </div>
        <div style="font-weight:bold; color:white;" class="{nm}">{username}</div>
    </div>
    """

def extract_yt(text):
    if not text: return None
    match = re.search(r'(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/(watch\?v=|embed/|v/|live/|.+\?v=)?([^&=%\?]{11})', text)
    return f"https://www.youtube.com/watch?v={match.group(6)}" if match else None

# --- OYUNLAR ---
def get_finance_game(user, start_score):
    js = f"""
    <div style='text-align:center; color:white; background:#111; padding:20px; border-radius:10px;'>
        <h2>💰 Finans İmparatoru</h2>
        <h1 id='score' style='color:gold; font-size:3em;'>{start_score}</h1>
        <button onclick='addScore()' style='font-size:60px; background:none; border:none; cursor:pointer;'>🏦</button>
        <p>Kasayı artırmak için tıkla!</p>
        <button onclick='saveScore()' style='background:#10b981; color:white; padding:10px 20px; border:none; border-radius:5px; cursor:pointer; width:100%; margin-top:10px;'>KASAYI KAYDET</button>
    </div>
    <script>
        let score = {start_score};
        function addScore() {{ score += 100; document.getElementById('score').innerText = score.toLocaleString(); }}
        function saveScore() {{
            const url = window.parent.location.href.split('?')[0];
            window.parent.location.href = `${{url}}?action=game_save&u={user}&s=${{score}}&t=${{Date.now()}}`;
        }}
    </script>
    """
    return js

def get_matrix_game(user):
    js = f"""
    <style>body{{margin:0;overflow:hidden;background:black;}}canvas{{display:block;}}#ui{{position:absolute;top:10px;left:10px;color:#0f0;font-family:monospace;font-size:20px;}}#btn{{position:absolute;top:10px;right:10px;background:#0f0;color:black;border:none;padding:10px;cursor:pointer;font-weight:bold;}}</style>
    <div id="ui">Veri: <span id="score">0</span></div>
    <button id="btn" onclick="save()">VERİYİ YÜKLE</button>
    <canvas id="c"></canvas>
    <script>
        var c = document.getElementById("c");
        var ctx = c.getContext("2d");
        c.width = window.innerWidth; c.height = window.innerHeight;
        var font_size = 14;
        var columns = c.width/font_size;
        var drops = [];
        for(var x=0; x<columns; x++) drops[x] = 1;
        var score = 0;

        function draw() {{
            ctx.fillStyle = "rgba(0, 0, 0, 0.05)";
            ctx.fillRect(0, 0, c.width, c.height);
            ctx.fillStyle = "#0F0";
            ctx.font = font_size + "px arial";
            for(var i=0; i<drops.length; i++) {{
                var text = Math.floor(Math.random()*2);
                ctx.fillText(text, i*font_size, drops[i]*font_size);
                if(drops[i]*font_size > c.height && Math.random() > 0.975) {{
                    drops[i] = 0; score += 1;
                    document.getElementById('score').innerText = score;
                }}
                drops[i]++;
            }}
        }}
        setInterval(draw, 33);
        function save() {{
            const url = window.parent.location.href.split('?')[0];
            window.parent.location.href = `${{url}}?action=game_matrix&u={user}&s=${{score}}&t=${{Date.now()}}`;
        }}
    </script>
    """
    return js

# --- GİRİŞ & KAYIT ---
if not st.session_state['logged_in']:
    st.markdown("""
        <div class="login-container">
            <div class="login-sub">Muhasebe ve Finansman Alanı</div>
            <div class="login-main">DİJİTAL GELİŞİM PLATFORMU</div>
            <div class="login-bottom">~ Dijital Kampüs ~</div>
        </div>
    """, unsafe_allow_html=True)
    
    c1, c2, c3 = st.columns([1,2,1])
    with c2:
        t1, t2 = st.tabs(["GİRİŞ YAP", "KAYIT OL"])
        with t1:
            with st.form("l"):
                u = st.text_input("Kullanıcı Adı"); p = st.text_input("Şifre", type="password")
                if st.form_submit_button("Giriş"):
                    usr = database.login_user(u, p)
                    if usr:
                        st.session_state.update({'logged_in':True, 'username':usr[1], 'role':usr[3], 'active_menu':'Ana Sayfa'})
                        st.rerun()
                    else: st.error("Hatalı!")
        with t2:
            with st.form("r"):
                nu = st.text_input("Kullanıcı"); np = st.text_input("Şifre", type="password")
                st.write(f"Güvenlik: {st.session_state['captcha']['q']} = ?"); ans = st.number_input("Cevap", step=1)
                if st.form_submit_button("Kayıt"):
                    if ans == st.session_state['captcha']['a']:
                        res, code = database.add_user(nu, np, "student")
                        if res: st.success("Tamam! Giriş yap."); st.session_state['captcha']=None
                        else: st.error("İsim dolu.")
                    else: st.error("Yanlış cevap.")

else:
    me = st.session_state['username']
    
    # Oyun puanı kontrol
    if "action" in st.query_params:
        act = st.query_params["action"]
        if act == "game_save":
            try:
                s = int(st.query_params["s"])
                curr = database.get_user_data(me)[0]
                if s > curr: database.add_score(me, s - curr); st.toast(f"{s - curr} Puan Kazandın!")
            except: pass
        elif act == "game_matrix":
            try:
                s = int(st.query_params["s"])
                if s > 0: database.add_score(me, s); st.toast(f"Matrix: {s} Puan!")
            except: pass
        st.query_params.clear()

    # --- SIDEBAR ---
    with st.sidebar:
        st.markdown(get_user_display_html(me, size=60), unsafe_allow_html=True)
        
        with st.expander("Profili Düzenle"):
            nbio = st.text_area("Bio", value=database.get_user_data(me)[1])
            if st.button("Kaydet", key="bio"): database.update_bio(me, nbio); st.rerun()
            uimg = st.file_uploader("Foto", type=['png','jpg'])
            if uimg:
                if database.update_avatar(me, uimg): st.success("Yüklendi!"); time.sleep(1); st.rerun()

        noti = database.get_unread_notification_count(me)
        noti_txt = f"Mesajlar ({noti})" if noti > 0 else "Mesajlar"
        
        menu = ["Ana Sayfa", "Profilim", "Sınıfım", noti_txt, "Kampüs Duvarı", "Mağaza", "Dersler", "Oyunlar", "Liderlik"]
        if st.session_state['role'] == 'admin': menu.append("YÖNETİCİ")
        
        sel = st.radio("Navigasyon", menu, label_visibility="collapsed")
        
        st.divider()
        if st.button("ÇIKIŞ YAP"): st.session_state['logged_in']=False; st.rerun()

    # --- SAYFALAR ---
    if sel == "Ana Sayfa":
        st.subheader("Kontrol Paneli")
        sc = database.get_user_data(me)[0]
        rank = 1 
        
        c1, c2, c3 = st.columns(3)
        c1.markdown(f"<div class='metric-card'><div class='metric-val'>{sc:,}</div><div class='metric-lbl'>Puan</div></div>", unsafe_allow_html=True)
        c2.markdown(f"<div class='metric-card'><div class='metric-val'>{rank}.</div><div class='metric-lbl'>Sıra</div></div>", unsafe_allow_html=True)
        c3.markdown(f"<div class='metric-card'><div class='metric-val'>{noti}</div><div class='metric-lbl'>Mesaj</div></div>", unsafe_allow_html=True)
        
        st.write("")
        st.info("👋 Hoşgeldin! Sol menüyü kullan.")

    elif sel == "Kampüs Duvarı":
        st.subheader("📢 Kampüs Duvarı")
        
        sc = database.get_user_data(me)[0]
        if sc >= 500000 or st.session_state['role']=='admin':
            with st.expander("Paylaşım Yap (-100.000 P)"):
                with st.form("p"):
                    t = st.text_area("İçerik"); y = st.text_input("Youtube"); i = st.file_uploader("Resim")
                    if st.form_submit_button("Paylaş"):
                        database.add_score(me, -100000); database.add_post(me, t, i, extract_yt(y), "campus"); st.rerun()
        
        posts = database.get_posts(limit=20)
        for p in posts:
            st.markdown(f"""<div class="post-card"><div class="post-header">{get_user_display_html(p[1],30)} <small style="margin-left:auto">{p[5]}</small></div><div class="post-content">{p[2]}</div>{f'<img src="data:image/jpeg;base64,{p[3]}" style="width:100%;border-radius:10px;">' if p[3] else ''}</div>""", unsafe_allow_html=True)
            if p[4]: st.video(p[4])
            c1, c2 = st.columns([1,5])
            if c1.button(f"❤️ {p[6]}", key=f"l_{p[0]}"): database.like_post(p[0]); st.rerun()
            with c2.popover("💬 Yorum"):
                for cm in database.get_comments(p[0]): st.caption(f"{cm[0]}: {cm[1]}")
                nc = st.text_input("Yaz", key=f"c_{p[0]}")
                if st.button("Gönder", key=f"b_{p[0]}"): database.add_comment(p[0], me, nc); st.rerun()

    elif sel == "Mağaza":
        st.header("💎 Kampüs Mağazası")
        st.metric("Bakiye", f"{database.get_user_data(me)[0]:,} P")
        
        tabs = st.tabs(["Çerçeveler", "İsimler", "Hediyeler"])
        
        def render_shop(items, kind):
            rows = [items[i:i+4] for i in range(0, len(items), 4)]
            for row in rows:
                cols = st.columns(4)
                for i, x in enumerate(row):
                    with cols[i]:
                        vis = ""
                        if kind == "frame": vis = f'<div style="font-size:3rem;">🖼️</div>'
                        elif kind == "name": vis = f'<div style="font-size:3rem;">✨</div>'
                        elif kind == "gift": vis = f'<div style="font-size:3rem;">{x["i"]}</div>'
                        
                        st.markdown(f'<div class="shop-item"><div class="shop-icon-box">{vis}</div><div class="shop-name">{x["n"]}</div></div>', unsafe_allow_html=True)
                        
                        uniq = f"buy_{kind}_{x['n']}_{i}"
                        if st.button(f"AL {x['c']//1000}K", key=uniq):
                            if kind == "gift": st.warning("Hediyeler sekmesinden gönderiniz.")
                            else:
                                ok, msg = database.buy_item(me, kind, x['v'], x['c'])
                                if ok: st.success(msg); time.sleep(1); st.rerun()
                                else: st.error(msg)

        with tabs[0]:
            items = [{"n":"Gold","v":"Gold","c":50000}, {"n":"Neon","v":"Neon","c":150000}, {"n":"Alev","v":"Fire","c":300000}, {"n":"Kral","v":"King","c":1000000}]
            render_shop(items, "frame")
        
        with tabs[1]:
            items = [{"n":"Glitch","v":"Glitch","c":100000}, {"n":"Gold","v":"Gold","c":750000}]
            render_shop(items, "name")
            
        with tabs[2]:
            st.info("Hediye Gönder")
            tu = st.selectbox("Kime", database.get_all_users_list(me))
            gifts = [{"n":"Kahve","c":5000,"i":"☕"}, {"n":"Gül","c":25000,"i":"🌹"}, {"n":"Araba","c":500000,"i":"🏎️"}]
            render_shop(gifts, "gift")
            
            sel_g = st.selectbox("Hediye Seç", [g['n'] for g in gifts])
            if st.button("Seçileni Gönder"):
                cost = next(g['c'] for g in gifts if g['n']==sel_g)
                ok, msg = database.send_gift(me, tu, sel_g, cost)
                if ok: st.success(msg); time.sleep(1); st.rerun()
                else: st.error(msg)

    elif sel.startswith("Mesaj"):
        st.header("💬 Mesajlar")
        database.mark_notifications_read(me)
        fr = database.get_mutual_friends(me)
        if not fr: st.info("Mesajlaşmak için birini takip et ve o da seni takip etsin.")
        else:
            tgt = st.selectbox("Kişi", fr)
            for s, m, t in database.get_conversation(me, tgt):
                align = "row-reverse" if s==me else "row"
                bg = "#2563eb" if s==me else "#334155"
                st.markdown(f"<div style='display:flex;flex-direction:{align};margin:5px'><div style='background:{bg};padding:10px;border-radius:10px;color:white'>{m}</div></div>", unsafe_allow_html=True)
            with st.form("msg"):
                if st.form_submit_button("Yolla"): pass
            if t:=st.chat_input("Yaz"): database.send_message(me, tgt, t); st.rerun()

    elif sel == "Oyunlar":
        gm = st.selectbox("Seç", ["Finans İmparatoru", "Matrix Veri Avcısı"])
        if gm == "Finans İmparatoru": components.html(get_finance_game(database.get_user_data(me)[0], me), height=600)
        else: components.html(get_matrix_game(me), height=500)

    elif sel == "Dersler":
        if os.path.exists("exams.json"):
            d = json.load(open("exams.json"))
            c = st.selectbox("Sınıf", d.keys()); l = st.selectbox("Ders", d[c].keys())
            with st.form("ex"):
                s = 0
                for i, q in enumerate(d[c][l]):
                    st.write(f"{i+1}. {q.get('question')}"); a = st.text_input("Cevap", key=f"q{i}")
                    if a == q.get('answer'): s+=q.get('points')
                if st.form_submit_button("Bitir"): database.add_score(me, s); st.success(f"Puan: {s}"); time.sleep(2); st.rerun()

    elif sel == "Liderlik":
        st.dataframe(pd.DataFrame(database.get_leaderboard_data(), columns=["Öğrenci","Puan"]), use_container_width=True)

    elif sel == "Profilim":
        st.subheader("Profilim")
        for p in database.get_posts(user_filter=me): st.markdown(f"<div class='post-card'>{p[2]}</div>", unsafe_allow_html=True)

    elif sel == "Sınıfım":
        cls = database.get_user_data(me)[6]
        if not cls:
            c = st.text_input("Sınıf Kodu"); 
            if st.button("Katıl"): database.join_class(me, c); st.rerun()
            if st.session_state['role']=='teacher':
                n=st.text_input("Ad"); k=st.text_input("Kod"); 
                if st.button("Oluştur"): database.create_class(me, n, k); st.success("Tamam")
        else:
            st.success(f"Sınıf: {cls}"); posts = database.get_posts("class", cls)
            with st.form("cp"):
                if st.form_submit_button("Yaz") and (t:=st.text_input("Mesaj")): database.add_post(me, t, None, None, "class", cls); st.rerun()
            for p in posts: st.markdown(f"<div class='post-card'><b>{p[1]}</b>: {p[2]}</div>", unsafe_allow_html=True)

    elif sel == "YÖNETİCİ":
        st.header("Yönetici")
        df = pd.DataFrame(database.get_all_users_admin(), columns=["Kullanıcı","Puan","Rol","Sınıf"])
        st.dataframe(df)
        tgt = st.selectbox("Kullanıcı", df['Kullanıcı'])
        if st.button("Sil"): database.delete_user_admin(tgt); st.rerun()
        val = st.number_input("Puan", value=0)
        if st.button("Ekle"): database.add_score(tgt, val); st.success("Tamam")
        st.write("Mesajlar"); st.table(database.admin_get_all_messages())
