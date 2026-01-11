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

# --- CSS ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@700&family=Orbitron:wght@700&family=Roboto:wght@300;700&display=swap');

    .login-box {
        background: linear-gradient(135deg, #1e3a8a 0%, #1e40af 100%);
        padding: 40px; border-radius: 20px; text-align: center;
        box-shadow: 0 10px 25px rgba(0,0,0,0.5); border: 2px solid #60a5fa; margin-bottom: 20px;
    }
    .login-title { font-family: 'Cinzel', serif; color: #fbbf24; font-size: 2.2rem; text-shadow: 2px 2px 4px #000; margin-bottom: 5px; }
    .login-sub { font-family: 'Roboto', sans-serif; color: #e0f2fe; font-size: 1.1rem; letter-spacing: 2px; }

    /* DASHBOARD CARD */
    .metric-card {
        background: #1e293b; border: 1px solid #475569; border-radius: 8px; padding: 15px;
        text-align: center; color: white;
    }
    .metric-val { font-size: 1.5rem; font-weight: bold; color: #fbbf24; }
    .metric-lbl { font-size: 0.9rem; color: #cbd5e1; }

    /* MAĞAZA STİLİ */
    .shop-item { background: #0f172a; border: 1px solid #334155; border-radius: 12px; padding: 10px; text-align: center; display: flex; flex-direction: column; align-items: center; justify-content: space-between; height: 180px; }
    .shop-preview { width: 80px; height: 80px; border-radius: 50%; background-color: #333; margin-bottom: 10px; background-size: cover; background-position: center; border: 3px solid transparent; display: flex; align-items: center; justify-content: center; font-size: 2rem;}
    .shop-name { font-size: 0.9rem; color: #cbd5e1; font-weight: bold; margin-bottom: 5px; }
    
    /* PROFİL KARTI */
    .profile-card { text-align: center; padding: 10px; background: #1e293b; border-radius: 10px; margin-bottom: 10px; border: 1px solid #334155; }
    .profile-bio { font-size: 0.85rem; color: #94a3b8; font-style: italic; margin-top: 5px; }
    .profile-stats { display: flex; justify-content: space-around; margin-top: 10px; font-size: 0.8rem; color: white; }
    
    /* POST KARTI */
    .post-card { background-color: #0f172a; border: 1px solid #334155; border-radius: 15px; padding: 15px; margin-bottom: 15px; }
    .post-header { display: flex; align-items: center; margin-bottom: 10px; border-bottom: 1px solid #1e293b; padding-bottom: 5px; }
    
    /* ÇERÇEVELER VE İSİMLER */
    .avatar-img { width: 70px; height: 70px; border-radius: 50%; object-fit: cover; margin-bottom: 5px; }
    .frame-Gold { border: 3px solid #FFD700; box-shadow: 0 0 10px #FFD700; }
    .frame-Neon { border: 3px solid #00ffff; box-shadow: 0 0 10px #00ffff; }
    .frame-Fire { border: 3px solid #ff4500; box-shadow: 0 0 15px #ff0000; }
    .frame-King { border: 3px solid #ffd700; box-shadow: 0 0 15px #ffd700; }
    .frame-Matrix { border: 2px dotted #00ff00; }
    .name-Glitch { color: #00ffff; text-shadow: 2px 0 #ff00ff; }
    .name-Gold { background: linear-gradient(to right, #BF953F, #FCF6BA, #B38728); -webkit-background-clip: text; color: transparent; font-weight: bold; }
    
    div.stButton > button { width: 100%; border-radius: 5px; }
</style>
""", unsafe_allow_html=True)

# --- INIT ---
def init():
    if 'logged_in' not in st.session_state:
        st.session_state.update({'logged_in': False, 'username': None, 'role': None, 'active_menu': 'Ana Sayfa', 'captcha': None})
    if st.session_state['captcha'] is None:
        n1, n2 = random.randint(1,10), random.randint(1,10)
        st.session_state['captcha'] = {'q': f"{n1} + {n2}", 'a': n1+n2}

    # Sınav dosyası yoksa oluştur
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

database.create_database()
init()

# --- YARDIMCILAR ---
def get_profile_html(username):
    u = database.get_user_data(username)
    score, bio, ava, frame, name_style, _, _ = u
    img = f"data:image/jpeg;base64,{ava}" if ava else "https://via.placeholder.com/150"
    fr = f"frame-{frame}" if frame else ""
    nm = f"name-{name_style}" if name_style else ""
    fol = database.get_followers_count(username)
    foll = database.get_following_count(username)
    
    return f"""
    <div class="profile-card">
        <img src="{img}" class="avatar-img {fr}">
        <div style="font-weight:bold; color:white;" class="{nm}">{username}</div>
        <div class="profile-bio">{bio if bio else 'Bio yok.'}</div>
        <div class="profile-stats">
            <div><b>{fol}</b><br>Takipçi</div>
            <div><b>{foll}</b><br>Takip</div>
            <div><b>{score:,}</b><br>Puan</div>
        </div>
    </div>
    """

def get_avatar_mini(username):
    u = database.get_user_data(username)
    ava = u[2]
    img = f"data:image/jpeg;base64,{ava}" if ava else "https://via.placeholder.com/150"
    return f'<img src="{img}" style="width:30px;height:30px;border-radius:50%;margin-right:10px;">'

def extract_yt(text):
    match = re.search(r'(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/(watch\?v=|embed/|v/|live/|.+\?v=)?([^&=%\?]{11})', text)
    return f"https://www.youtube.com/watch?v={match.group(6)}" if match else None

# --- OYUNLAR (ÇALIŞAN SÜRÜM) ---
def get_finance_game(user, start_score):
    # Basit Tıklama Oyunu - Puanı tarayıcıda tutar, kaydet deyince sunucuya yollar
    return f"""
    <div style='text-align:center; color:white; background:#111; padding:20px; border-radius:10px;'>
        <h2>💰 Finans İmparatoru</h2>
        <h1 id='score' style='color:gold; font-size:3em;'>{start_score}</h1>
        <button onclick='addScore()' style='font-size:50px; background:none; border:none; cursor:pointer;'>🏦</button>
        <p style='color:gray'>Tıkla ve Kazan!</p>
        <br>
        <button onclick='saveScore()' style='background:#10b981; color:white; padding:10px 20px; border:none; border-radius:5px; cursor:pointer;'>KASAYI KAYDET</button>
    </div>
    <script>
        let score = {start_score};
        function addScore() {{
            score += 10;
            document.getElementById('score').innerText = score.toLocaleString();
        }}
        function saveScore() {{
            const url = window.parent.location.href.split('?')[0];
            const newUrl = `${{url}}?action=game_save&u={user}&s=${{score}}&t=${{Date.now()}}`;
            window.parent.location.href = newUrl;
        }}
    </script>
    """

def get_matrix_game(user):
    # Matrix Yağmuru Oyunu - Basitleştirilmiş
    return f"""
    <div style='background:black; color:#0f0; padding:20px; text-align:center; border-radius:10px; font-family:monospace;'>
        <h2>MATRIX VERİ AVCISI</h2>
        <p>Aşağıdaki kod parçalarına tıkla!</p>
        <div id="game-area" style="height:300px; position:relative; overflow:hidden; border:1px solid #0f0;"></div>
        <h3 id="m-score">Veri: 0</h3>
        <button onclick='saveMatrix()' style='background:#0f0; color:black; padding:5px 15px; border:none; margin-top:10px;'>VERİYİ YÜKLE</button>
    </div>
    <script>
        let mScore = 0;
        const area = document.getElementById('game-area');
        
        function spawnCode() {{
            const el = document.createElement('div');
            el.innerText = Math.random() > 0.5 ? '1' : '0';
            el.style.position = 'absolute';
            el.style.left = Math.random() * 90 + '%';
            el.style.top = '-20px';
            el.style.color = '#0f0';
            el.style.cursor = 'pointer';
            el.style.fontSize = '20px';
            
            el.onclick = function() {{
                mScore += 5;
                document.getElementById('m-score').innerText = 'Veri: ' + mScore;
                el.remove();
            }};
            
            area.appendChild(el);
            
            let pos = -20;
            const fall = setInterval(() => {{
                pos += 2;
                el.style.top = pos + 'px';
                if (pos > 300) {{ clearInterval(fall); el.remove(); }}
            }}, 50);
        }}
        
        setInterval(spawnCode, 800);
        
        function saveMatrix() {{
            if(mScore > 0) {{
                const url = window.parent.location.href.split('?')[0];
                const newUrl = `${{url}}?action=game_matrix&u={user}&s=${{mScore}}&t=${{Date.now()}}`;
                window.parent.location.href = newUrl;
            }}
        }}
    </script>
    """

# --- GİRİŞ & KAYIT ---
if not st.session_state['logged_in']:
    st.markdown("""
        <div class="login-box">
            <div class="login-title">DİJİTAL GELİŞİM KAMPÜSÜ</div>
            <div class="login-sub">MUHASEBE VE FİNANSMAN ALANI</div>
        </div>
    """, unsafe_allow_html=True)
    
    t1, t2 = st.tabs(["GİRİŞ YAP", "KAYIT OL"])
    with t1:
        with st.form("l"):
            u = st.text_input("Kullanıcı Adı"); p = st.text_input("Şifre", type="password")
            if st.form_submit_button("Giriş"):
                usr = database.login_user(u, p)
                if usr:
                    st.session_state.update({'logged_in':True, 'username':usr[1], 'role':usr[3], 'active_menu':'Ana Sayfa'})
                    database.update_activity(usr[1])
                    st.rerun()
                else: st.error("Hatalı kullanıcı veya şifre.")
    with t2:
        with st.form("r"):
            nu = st.text_input("Kullanıcı Belirle"); np = st.text_input("Şifre Belirle", type="password")
            st.write(f"Güvenlik: {st.session_state['captcha']['q']} = ?"); ans = st.number_input("Cevap", step=1)
            if st.form_submit_button("Kayıt Ol"):
                if ans == st.session_state['captcha']['a']:
                    if database.add_user(nu, np, "student"): st.success("Kayıt başarılı! Giriş yapabilirsin."); st.session_state['captcha']=None
                    else: st.error("Bu isim kullanılıyor.")
                else: st.error("Matematik sorusu yanlış.")

else:
    # --- ANA EKRAN ---
    me = st.session_state['username']
    database.update_activity(me)
    
    # Oyun Puanı Yakalama
    if "action" in st.query_params:
        act = st.query_params["action"]
        if act == "game_save":
            try:
                s = int(st.query_params["s"])
                curr = database.get_user_data(me)[0]
                if s > curr: database.add_score(me, s - curr); st.toast(f"{s - curr} Puan Eklendi!")
            except: pass
        elif act == "game_matrix":
            try:
                s = int(st.query_params["s"])
                if s > 0: database.add_score(me, s); st.toast(f"Matrix'ten {s} Veri Puanı!")
            except: pass
        st.query_params.clear()

    # --- SIDEBAR (YENİ DÜZEN) ---
    with st.sidebar:
        st.markdown(get_profile_html(me), unsafe_allow_html=True)
        
        with st.expander("Profili Düzenle"):
            nbio = st.text_area("Bio", value=database.get_user_data(me)[1])
            if st.button("Kaydet", key="bio_save"): database.update_bio(me, nbio); st.rerun()
            uimg = st.file_uploader("Fotoğraf Değiştir", type=['jpg','png'])
            if uimg: 
                if database.update_avatar(me, uimg): st.success("Resim güncellendi!"); time.sleep(1); st.rerun()

        # MENÜ
        noti = database.get_unread_count(me)
        noti_txt = f"Mesajlar ({noti})" if noti > 0 else "Mesajlar"
        
        # İstediğin sıralama: Profil, Sınıf, Mesaj en üstte
        menus = ["Ana Sayfa", "Profilim", "Sınıfım", noti_txt, "Kampüs Duvarı", "Mağaza", "Dersler", "Oyunlar", "Liderlik"]
        if st.session_state['role'] == 'admin': menus.append("YÖNETİCİ")
        
        sel = st.radio("Navigasyon", menus, label_visibility="collapsed")
        
        st.divider()
        sch = st.selectbox("Kullanıcı Ara", database.get_all_users_list(me))
        if st.button("Takip Et"):
            if database.follow_user(me, sch): st.success("Takip edildi!")
            else: st.warning("Zaten takip ediyorsun.")
            
        if st.button("ÇIKIŞ"): st.session_state['logged_in']=False; st.rerun()

    # --- SAYFALAR ---
    
    if sel == "Ana Sayfa":
        st.subheader(f"Kontrol Paneli")
        
        # Üst İstatistikler (Küçük)
        sc, bio, _, _, _, role, cls = database.get_user_data(me)
        rank = database.get_user_rank(me)
        
        col1, col2, col3, col4 = st.columns(4)
        col1.markdown(f"<div class='metric-card'><div class='metric-val'>{sc:,}</div><div class='metric-lbl'>Puan</div></div>", unsafe_allow_html=True)
        col2.markdown(f"<div class='metric-card'><div class='metric-val'>{rank}.</div><div class='metric-lbl'>Sıra</div></div>", unsafe_allow_html=True)
        col3.markdown(f"<div class='metric-card'><div class='metric-val'>{noti}</div><div class='metric-lbl'>Mesaj</div></div>", unsafe_allow_html=True)
        col4.markdown(f"<div class='metric-card'><div class='metric-val'>{cls if cls else '-'}</div><div class='metric-lbl'>Sınıf</div></div>", unsafe_allow_html=True)
        
        st.write("")
        st.info("👋 Hoşgeldin! Soldaki menüden istediğin yere gidebilirsin.")

    elif sel == "Kampüs Duvarı":
        st.subheader("📢 Kampüs Duvarı")
        wall_type = st.selectbox("Görünüm", ["Tüm Kampüs", "Benim Profilim"], label_visibility="collapsed")
        
        sc = database.get_user_data(me)[0]
        if sc >= 500000 or st.session_state['role']=='admin':
            with st.expander("Paylaşım Yap (-100.000 P)"):
                with st.form("p"):
                    t = st.text_area("İçerik"); y = st.text_input("Youtube Link"); i = st.file_uploader("Resim", type=['jpg','png'])
                    if st.form_submit_button("Paylaş"):
                        database.add_score(me, -100000); database.add_post(me, t, i, extract_yt(y), "campus"); st.rerun()
        
        posts = database.get_posts("campus")
        if wall_type == "Benim Profilim": posts = [p for p in posts if p[1] == me]
        
        for p in posts:
            st.markdown(f"""<div class="post-card"><div class="post-header">{get_avatar_mini(p[1])}<b>{p[1]}</b> <small style="margin-left:auto">{p[5]}</small></div><div class="post-content">{p[2]}</div>{f'<img src="data:image/jpeg;base64,{p[3]}" style="width:100%;border-radius:10px;">' if p[3] else ''}</div>""", unsafe_allow_html=True)
            if p[4]: st.video(p[4])
            c1, c2 = st.columns([1,5])
            if c1.button(f"❤️ {p[6]}", key=f"l{p[0]}"): database.like_post(p[0]); st.rerun()
            with c2.popover("💬 Yorumlar"):
                for cm in database.get_comments(p[0]): st.caption(f"**{cm[0]}**: {cm[1]}")
                nc = st.text_input("Yaz", key=f"c{p[0]}")
                if st.button("Gönder", key=f"b{p[0]}"): database.add_comment(p[0], me, nc); st.rerun()

    elif sel == "Mağaza":
        st.header("💎 Mağaza")
        t1, t2, t3, t4 = st.tabs(["🖼️ Çerçeve", "✨ İsim", "✒️ Font", "🎁 Hediye"])
        
        def render_shop(items, type_key):
            rows = [items[i:i+4] for i in range(0, len(items), 4)]
            for row in rows:
                cols = st.columns(4)
                for i, x in enumerate(row):
                    with cols[i]:
                        # Görsel (HTML/CSS)
                        if type_key == "frame":
                            vis = f'<div class="shop-preview"><div class="{x["css"]}" style="width:100%;height:100%;border-radius:50%;background:url(https://api.dicebear.com/7.x/avataaars/svg?seed={x["n"]}) center/cover;"></div></div>'
                        elif type_key == "name":
                            vis = f'<div style="font-size:1.5rem;margin-bottom:10px;">✨</div>'
                        elif type_key == "gift":
                            vis = f'<div style="font-size:3rem;margin-bottom:5px;">{x["i"]}</div>'
                        else:
                            vis = f'<div style="font-size:1.5rem;margin-bottom:10px;">Aa</div>'

                        st.markdown(f'<div class="shop-item">{vis}<div class="shop-name">{x["n"]}</div></div>', unsafe_allow_html=True)
                        
                        if type_key != "gift":
                            if st.button(f"AL {x['c']//1000}K", key=f"buy_{type_key}_{x['n']}_{i}"):
                                if database.buy_item(me, type_key, x['v'], x['c']): st.success("Hayırlı olsun!"); time.sleep(1); st.rerun()
                                else: st.error("Bakiye yetersiz")

        with t1:
            items = [{"n":"Gold","v":"Gold","c":50000,"css":"frame-Gold"}, {"n":"Neon","v":"Neon","c":150000,"css":"frame-Neon"}, {"n":"Alev","v":"Fire","c":300000,"css":"frame-Fire"}, {"n":"Kral","v":"King","c":1000000,"css":"frame-King"}]
            render_shop(items, "frame")
        with t2:
            items = [{"n":"Glitch","v":"Glitch","c":100000}, {"n":"Gold","v":"Gold","c":750000}]
            render_shop(items, "name")
        with t3:
            items = [{"n":"Cinzel","v":"Cinzel","c":150000}, {"n":"Orbitron","v":"Orbitron","c":250000}]
            render_shop(items, "name") # Font DB'de name_style
        with t4:
            st.info("Birini seçip hediye gönder")
            tu = st.selectbox("Kime", database.get_all_users_list(me))
            gifts = [{"n":"Kahve","c":5000,"i":"☕"}, {"n":"Gül","c":25000,"i":"🌹"}, {"n":"Araba","c":500000,"i":"🏎️"}]
            render_shop(gifts, "gift")
            
            # Hediye Butonları Manuel (Selectbox ile değil, grid altındaki butonlarla)
            # Ama render_shop fonksiyonu otomatik buton koyuyor, gift için özelleştirelim:
            st.write("---")
            g_sel = st.selectbox("Hediye Seç", [g['n'] for g in gifts])
            if st.button("Seçileni Gönder"):
                cost = next(g['c'] for g in gifts if g['n']==g_sel)
                if database.send_gift(me, tu, g_sel, cost): st.success("Gitti!"); st.rerun()
                else: st.error("Para yok")

    elif sel.startswith("Mesaj"):
        st.subheader("Mesajlar")
        database.mark_read(me)
        fr = database.get_mutual_friends(me)
        if not fr: st.info("Mesajlaşmak için karşılıklı takipleşmelisiniz.")
        else:
            tgt = st.selectbox("Kişi", fr)
            msgs = database.get_conversation(me, tgt)
            for m in msgs:
                align = "row-reverse" if m[0]==me else "row"
                bg = "#2563eb" if m[0]==me else "#334155"
                st.markdown(f"<div style='display:flex;flex-direction:{align};margin:5px'><div style='background:{bg};padding:10px;border-radius:10px'>{m[1]}</div></div>", unsafe_allow_html=True)
            with st.form("msg"):
                if st.form_submit_button("Yolla"): pass
            if txt:=st.chat_input("Yaz"): database.send_message(me, tgt, txt); st.rerun()

    elif sel == "Oyunlar":
        gm = st.selectbox("Oyun", ["Finans İmparatoru", "Matrix Veri Avcısı"])
        if gm == "Finans İmparatoru":
            components.html(get_finance_game(database.get_user_data(me)[0], me), height=600)
        else:
            components.html(get_matrix_game(me), height=500)

    elif sel == "Dersler":
        if os.path.exists("exams.json"):
            d = json.load(open("exams.json"))
            c = st.selectbox("Sınıf", d.keys()); l = st.selectbox("Ders", d[c].keys())
            with st.form("ex"):
                s = 0
                for i, q in enumerate(d[c][l]):
                    st.write(f"{i+1}. {q.get('question')}"); ans = st.text_input("Cv", key=f"q{i}")
                    if ans == q.get('answer'): s+=q.get('points')
                if st.form_submit_button("Bitir"): database.add_score(me, s); st.success(f"Puan: {s}"); time.sleep(2); st.rerun()

    elif sel == "Liderlik":
        st.dataframe(pd.DataFrame(database.get_leaderboard_data(), columns=["Öğrenci","Puan"]), use_container_width=True)

    elif sel == "Profilim":
        st.subheader("Profilim")
        posts = database.get_posts(user_filter=me)
        for p in posts: st.markdown(f"<div class='post-card'>{p[2]}</div>", unsafe_allow_html=True)

    elif sel == "Sınıfım":
        cls = database.get_user_data(me)[6]
        if not cls:
            code = st.text_input("Sınıf Kodu")
            if st.button("Katıl"): database.join_class(me, code); st.rerun()
            if st.session_state['role']=='teacher':
                n = st.text_input("Sınıf Adı"); c = st.text_input("Kodu")
                if st.button("Oluştur"): database.create_class(me, n, c); st.success("Tamam")
        else:
            st.success(f"Sınıf: {cls}")
            with st.form("cp"):
                if st.form_submit_button("Yaz") and (t:=st.text_input("Mesaj")): 
                    database.add_post(me, t, None, None, "class", cls); st.rerun()
            for p in database.get_posts("class", cls): st.markdown(f"<div class='post-card'><b>{p[1]}</b>: {p[2]}</div>", unsafe_allow_html=True)

    elif sel == "YÖNETİCİ":
        st.header("Admin")
        users = database.get_all_users_admin()
        df = pd.DataFrame(users, columns=["Kullanıcı","Puan","Rol","Sınıf"])
        st.dataframe(df)
        tgt = st.selectbox("Kullanıcı", df['Kullanıcı'])
        c1, c2 = st.columns(2)
        if c1.button("Sil"): database.delete_user_admin(tgt); st.rerun()
        val = c2.number_input("Puan", value=0)
        if c2.button("Ekle"): database.add_score(tgt, val); st.success("Tamam")
        st.write("Mesajlar"); st.table(database.admin_get_all_messages())
