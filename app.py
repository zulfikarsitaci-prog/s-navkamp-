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

# --- CSS ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@700&family=Orbitron:wght@700&family=Roboto:wght@300;700&display=swap');

    /* GİRİŞ EKRANI */
    .login-box {
        background: linear-gradient(135deg, #1e3a8a 0%, #1e40af 100%);
        padding: 40px; border-radius: 20px; text-align: center;
        box-shadow: 0 10px 25px rgba(0,0,0,0.5); border: 2px solid #60a5fa; margin-bottom: 20px;
    }
    .login-title { font-family: 'Cinzel', serif; color: #fbbf24; font-size: 2.2rem; text-shadow: 2px 2px 4px #000; margin-bottom: 5px; }
    .login-sub { font-family: 'Roboto', sans-serif; color: #e0f2fe; font-size: 1.1rem; letter-spacing: 2px; }

    /* DASHBOARD CARD */
    .dash-card {
        background: #1e293b; border: 1px solid #475569; border-radius: 10px; padding: 20px;
        text-align: center; cursor: pointer; transition: transform 0.2s; height: 120px; display:flex; flex-direction:column; justify-content:center; align-items:center;
    }
    .dash-card:hover { transform: scale(1.05); border-color: #fbbf24; }
    .dash-icon { font-size: 2.5rem; margin-bottom: 10px; }
    .dash-text { font-size: 1rem; color: white; font-weight: bold; }

    /* MAĞAZA STİLİ */
    .shop-item { background: #0f172a; border: 1px solid #334155; border-radius: 8px; padding: 10px; text-align: center; height: 140px; display: flex; flex-direction: column; align-items: center; justify-content: space-between; }
    .shop-icon-box { font-size: 2rem; margin-bottom: 5px; }
    .shop-name { font-size: 0.8rem; color: #cbd5e1; font-weight: bold; }
    .shop-btn button { width: 100%; font-size: 0.7rem; padding: 2px; }

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

# --- OYUNLAR ---
def get_finance_game(user, start_score):
    js = f"""<script>
    let score = {start_score};
    function clickBtn() {{ score += 10; document.getElementById('s').innerText = score.toLocaleString(); }}
    function save() {{ window.parent.location.href = `?action=game_save&u={user}&s=${{score}}`; }}
    </script>
    <div style='text-align:center; color:white; background:#111; padding:20px;'>
    <h2>💰 Finans İmparatoru</h2>
    <h1 id='s'>{start_score}</h1>
    <button onclick='clickBtn()' style='font-size:40px; background:none; border:none; cursor:pointer'>👆</button>
    <br><br>
    <button onclick='save()' style='background:green; color:white; padding:10px; border:none;'>KASAYI KAYDET</button>
    </div>
    """
    return js

def get_matrix_game(user):
    return """<div style="text-align:center;color:#0f0;background:black;padding:50px;">MATRIX OYUNU YAKINDA...</div>"""

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
    
    if "action" in st.query_params and st.query_params["action"] == "game_save":
        try:
            s = int(st.query_params["s"])
            curr = database.get_user_data(me)[0]
            if s > curr: database.add_score(me, s - curr)
            st.toast("Oyun Kaydedildi!")
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
        st.subheader(f"Hoşgeldin, {me} 👋")
        
        # Dashboard Grid
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown('<div class="dash-card"><div class="dash-icon">📢</div><div class="dash-text">Kampüs Duvarı</div></div>', unsafe_allow_html=True)
            if st.button("Duvara Git", key="d_wall"): st.session_state['active_menu']="Kampüs Duvarı"; st.rerun()
        with c2:
            st.markdown('<div class="dash-card"><div class="dash-icon">💎</div><div class="dash-text">Mağaza</div></div>', unsafe_allow_html=True)
            if st.button("Alışveriş Yap", key="d_shop"): st.session_state['active_menu']="Mağaza"; st.rerun()
        with c3:
            st.markdown('<div class="dash-card"><div class="dash-icon">🎮</div><div class="dash-text">Oyunlar</div></div>', unsafe_allow_html=True)
            if st.button("Oyun Oyna", key="d_game"): st.session_state['active_menu']="Oyunlar"; st.rerun()
            
        c4, c5, c6 = st.columns(3)
        with c4:
            st.markdown('<div class="dash-card"><div class="dash-icon">📚</div><div class="dash-text">Dersler</div></div>', unsafe_allow_html=True)
            if st.button("Ders Çalış", key="d_lesson"): st.session_state['active_menu']="Dersler"; st.rerun()
        with c5:
            st.markdown('<div class="dash-card"><div class="dash-icon">🏆</div><div class="dash-text">Liderlik</div></div>', unsafe_allow_html=True)
            if st.button("Sıralama", key="d_rank"): st.session_state['active_menu']="Liderlik"; st.rerun()
        with c6:
            st.markdown('<div class="dash-card"><div class="dash-icon">💬</div><div class="dash-text">Mesajlar</div></div>', unsafe_allow_html=True)
            if st.button("Sohbet", key="d_msg"): st.session_state['active_menu']=noti_txt; st.rerun()

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
        st.header("💎 Kampüs Mağazası")
        st.metric("Bakiye", f"{database.get_user_data(me)[0]:,} P")
        t1, t2, t3, t4 = st.tabs(["Çerçeveler", "İsimler", "Fontlar", "Hediyeler"])
        
        def render_shop(items, type_key):
            rows = [items[i:i+4] for i in range(0, len(items), 4)]
            for row in rows:
                cols = st.columns(4)
                for i, x in enumerate(row):
                    with cols[i]:
                        prev = f'<div style="font-size:2rem">{x.get("icon", "📦")}</div>'
                        st.markdown(f'<div class="shop-item"><div class="shop-icon-box">{prev}</div><div class="shop-name">{x["n"]}</div></div>', unsafe_allow_html=True)
                        key_uniq = f"btn_{type_key}_{x['n']}_{i}" # Uniq key
                        if st.button(f"AL ({x['c']//1000}K)", key=key_uniq):
                            if database.buy_item(me, type_key, x['v'], x['c']): st.success("Aldın!"); time.sleep(1); st.rerun()
                            else: st.error("Para yok")

        with t1:
            items = [{"n":"Gold","v":"Gold","c":50000,"icon":"🟡"}, {"n":"Neon","v":"Neon","c":150000,"icon":"🔵"}, {"n":"Alev","v":"Fire","c":300000,"icon":"🔥"}, {"n":"Kral","v":"King","c":1000000,"icon":"👑"}]
            render_shop(items, "frame")
        with t2:
            items = [{"n":"Glitch","v":"Glitch","c":100000,"icon":"👾"}, {"n":"Gold","v":"Gold","c":750000,"icon":"✨"}]
            render_shop(items, "name")
        with t3:
            items = [{"n":"Cinzel","v":"Cinzel","c":150000,"icon":"✒️"}, {"n":"Orbitron","v":"Orbitron","c":250000,"icon":"🤖"}]
            render_shop(items, "name") # Font DB'de name_style ile aynı mantıkta tutuluyor basitleştirmek için
        with t4:
            st.info("Hediye Gönder")
            tu = st.selectbox("Kime", database.get_all_users_list(me))
            gifts = [{"n":"Kahve","c":5000,"i":"☕"}, {"n":"Gül","c":25000,"i":"🌹"}, {"n":"Araba","c":500000,"i":"🏎️"}]
            for g in gifts:
                if st.button(f"{g['i']} {g['n']} ({g['c']})"):
                    if database.send_gift(me, tu, g['n'], g['c']): st.success("Gitti!")
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
        gm = st.selectbox("Seç", ["Finans İmparatoru", "Matrix"])
        if gm == "Finans İmparatoru": components.html(get_finance_game(database.get_user_data(me)[0], me), height=600)
        else: st.info("Matrix Yapım Aşamasında")

    elif sel == "Dersler":
        if os.path.exists("exams.json"):
            d = json.load(open("exams.json"))
            c = st.selectbox("Sınıf", d.keys()); l = st.selectbox("Ders", d[c].keys())
            with st.form("ex"):
                s = 0
                for i, q in enumerate(d[c][l]):
                    st.write(f"{i+1}. {q.get('question')}")
                    if q.get('type')=='test': 
                        if st.radio("Cevap", q['options'], key=f"q{i}") == q['answer']: s += q['points']
                    else: 
                        if st.text_input("Cevap", key=f"q{i}") == q['answer']: s += q['points']
                if st.form_submit_button("Bitir"): database.add_score(me, s); st.success(f"Puan: {s}"); time.sleep(2); st.rerun()

    elif sel == "Liderlik":
        st.dataframe(pd.DataFrame(database.get_leaderboard_data(), columns=["Öğrenci","Puan"]), use_container_width=True)

    elif sel == "Profilim":
        st.subheader("Profilim")
        st.info("Profil ayarlarını soldaki menüden yapabilirsin.")
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
