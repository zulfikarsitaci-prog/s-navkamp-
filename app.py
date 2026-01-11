import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import requests
import json
import os
import time
import random
import database
import base64
import re
from datetime import datetime

# --- AYARLAR ---
st.set_page_config(page_title="Bağarası ÇPAL", page_icon="🎓", layout="wide", initial_sidebar_state="expanded")

# --- SINAV VERİSİ (Otomatik Oluştur) ---
def check_exams_json():
    if not os.path.exists("exams.json"):
        data = {
            "9. Sınıf": {
                "Muhasebe": [{"question": "Kasa hesabı kodu nedir?", "options": ["100", "102", "300"], "answer": "100", "points": 20, "type":"test"}],
                "Mesleki Gelişim": [{"question": "Etkili iletişimde en önemli unsur?", "options": ["Dinlemek", "Konuşmak"], "answer": "Dinlemek", "points": 20, "type":"test"}]
            },
            "10. Sınıf": {
                "Genel Muhasebe": [{"question": "Bilanço sol tarafı?", "answer": "Aktif", "points": 20, "type":"text"}]
            }
        }
        with open("exams.json", "w", encoding="utf-8") as f: json.dump(data, f, ensure_ascii=False)

check_exams_json()

# --- CSS (Mavi Kutu, Instagram Profil, Mağaza) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@700&family=Orbitron:wght@700&family=Roboto:wght@300;700&display=swap');

    /* GİRİŞ EKRANI */
    .login-box {
        background: linear-gradient(135deg, #1e3a8a 0%, #1e40af 100%);
        padding: 40px;
        border-radius: 20px;
        text-align: center;
        box-shadow: 0 10px 25px rgba(0,0,0,0.5);
        border: 2px solid #60a5fa;
        margin-bottom: 20px;
    }
    .login-title { font-family: 'Cinzel', serif; color: #fbbf24; font-size: 2.5rem; text-shadow: 2px 2px 4px #000; margin-bottom: 10px; }
    
    /* PROFİL KARTI (Instagram Style) */
    .profile-card { text-align: center; padding: 10px; background: #1e293b; border-radius: 10px; margin-bottom: 10px; border: 1px solid #334155; }
    .profile-bio { font-size: 0.9rem; color: #94a3b8; font-style: italic; margin-top: 5px; }
    .profile-stats { display: flex; justify-content: space-around; margin-top: 10px; font-size: 0.8rem; color: white; }
    
    /* POST KARTI */
    .post-card { background-color: #0f172a; border: 1px solid #334155; border-radius: 15px; padding: 15px; margin-bottom: 15px; }
    .post-header { display: flex; align-items: center; margin-bottom: 10px; border-bottom: 1px solid #1e293b; padding-bottom: 5px; }
    .post-content { color: #cbd5e1; font-size: 0.95rem; white-space: pre-wrap; }
    
    /* MAĞAZA (Mobil Uyumlu Grid) */
    .shop-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px; } 
    @media (min-width: 768px) { .shop-grid { grid-template-columns: repeat(4, 1fr); } }
    
    .shop-item { background: #1e293b; border: 1px solid #475569; border-radius: 8px; padding: 10px; text-align: center; height: 130px; display: flex; flex-direction: column; align-items: center; justify-content: space-between; }
    .shop-icon { font-size: 2rem; margin-bottom: 5px; }
    .shop-name { font-size: 0.8rem; color: white; font-weight: bold; }
    
    /* BUTONLAR */
    div.stButton > button { width: 100%; border-radius: 5px; font-weight: bold; }
    
    /* ÇERÇEVE EFEKTLERİ */
    .avatar-img { width: 80px; height: 80px; border-radius: 50%; object-fit: cover; margin-bottom: 5px; }
    .frame-Gold { border: 3px solid #FFD700; box-shadow: 0 0 10px #FFD700; }
    .frame-Neon { border: 3px solid #00ffff; box-shadow: 0 0 10px #00ffff; }
    .frame-Fire { border: 3px solid #ff4500; box-shadow: 0 0 15px #ff0000; }
</style>
""", unsafe_allow_html=True)

# --- INIT ---
def init():
    if 'logged_in' not in st.session_state:
        st.session_state.update({'logged_in': False, 'username': None, 'role': None, 'active_menu': 'Profilim', 'captcha': None})
    if st.session_state['captcha'] is None:
        n1, n2 = random.randint(1,10), random.randint(1,10)
        st.session_state['captcha'] = {'q': f"{n1} + {n2}", 'a': n1+n2}

database.create_database()
init()

# --- YARDIMCILAR ---
def get_profile_html(username):
    u = database.get_user_data(username) # score, bio, avatar, frame, name, role, class
    score, bio, ava, frame, name_style, _, _ = u
    
    img_src = f"data:image/jpeg;base64,{ava}" if ava else "https://via.placeholder.com/150"
    fr_cls = f"frame-{frame}" if frame else ""
    nm_cls = f"name-{name_style}" if name_style else ""
    
    followers = database.get_followers_count(username)
    following = database.get_following_count(username)
    
    return f"""
    <div class="profile-card">
        <img src="{img_src}" class="avatar-img {fr_cls}">
        <div style="font-size:1.2rem; font-weight:bold; color:white;" class="{nm_cls}">{username}</div>
        <div class="profile-bio">{bio if bio else 'Bio henüz girilmedi.'}</div>
        <div class="profile-stats">
            <div><b>{followers}</b><br>Takipçi</div>
            <div><b>{following}</b><br>Takip</div>
            <div><b>{score:,}</b><br>Puan</div>
        </div>
    </div>
    """

def extract_yt(text):
    match = re.search(r'(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/(watch\?v=|embed/|v/|live/|.+\?v=)?([^&=%\?]{11})', text)
    return f"https://www.youtube.com/watch?v={match.group(6)}" if match else None

# --- OYUN HTML ---
def get_game_html(u):
    return f"""<!DOCTYPE html><html><body style='background:#111;color:white;text-align:center'><div style='font-size:24px;color:gold'>💰 <span id='s'>0</span></div><button onclick='c()' style='font-size:50px;background:none;border:none;cursor:pointer'>👆</button><br><br><button onclick='b()' style='background:green;color:white;padding:10px;border-radius:5px'>BANKAYA AT</button><script>let m=0;function c(){{m++;document.getElementById('s').innerText=m}}function b(){{if(m>0){{const a=document.createElement('a');a.href=`?action=game_score&u={u}&s=${{m}}&t=${{Date.now()}}`;a.target='_top';a.click();}}}}</script></body></html>"""

# --- GİRİŞ & KAYIT ---
if not st.session_state['logged_in']:
    st.markdown('<div class="login-box"><div class="login-title">BAĞARASI ÇPAL</div><div style="color:white">MUHASEBE ALANI</div></div>', unsafe_allow_html=True)
    t1, t2 = st.tabs(["GİRİŞ", "KAYIT"])
    with t1:
        with st.form("l"):
            u = st.text_input("Kullanıcı"); p = st.text_input("Şifre", type="password")
            if st.form_submit_button("Giriş"):
                usr = database.login_user(u, p)
                if usr:
                    st.session_state.update({'logged_in':True, 'username':usr[1], 'role':usr[3]})
                    st.rerun()
                else: st.error("Hata")
    with t2:
        with st.form("r"):
            nu = st.text_input("Kullanıcı"); np = st.text_input("Şifre", type="password")
            st.write(f"Soru: {st.session_state['captcha']['q']} = ?"); ans = st.number_input("Cevap", step=1)
            if st.form_submit_button("Kayıt"):
                if ans == st.session_state['captcha']['a']:
                    if database.add_user(nu, np, "student"): st.success("Oldu!"); st.session_state['captcha']=None
                    else: st.error("İsim dolu")
                else: st.error("Yanlış cevap")

else:
    # --- ANA EKRAN ---
    me = st.session_state['username']
    
    # URL Parametre Kontrolü (Oyun Puanı İçin)
    if "action" in st.query_params and st.query_params["action"] == "game_score":
        try:
            scr = int(st.query_params["s"])
            if scr > 0: database.add_score(me, scr); st.toast(f"{scr} Puan Eklendi!")
        except: pass
        st.query_params.clear()

    # --- SOL MENÜ ---
    with st.sidebar:
        st.markdown(get_profile_html(me), unsafe_allow_html=True)
        
        # Profil Düzenleme (Modal Mantığı Expander ile)
        with st.expander("✏️ Profili Düzenle"):
            nbio = st.text_area("Biyografi", value=database.get_user_data(me)[1])
            if st.button("Bio Kaydet"): database.update_bio(me, nbio); st.rerun()
            
            uimg = st.file_uploader("Yeni Fotoğraf", type=['jpg','png'])
            if uimg:
                if database.update_avatar(me, uimg): st.success("Yüklendi!"); time.sleep(1); st.rerun()

        # Bildirim
        noti = database.get_unread_count(me)
        noti_txt = f"Mesajlar ({noti})" if noti > 0 else "Mesajlar"
        
        # Menü Sıralaması
        menu = ["Profilim", "Sınıfım", noti_txt, "Kampüs Duvarı", "Mağaza", "Dersler", "Oyunlar", "Liderlik"]
        if st.session_state['role'] == 'admin': menu.append("YÖNETİCİ")
        
        sel = st.radio("Menü", menu, label_visibility="collapsed")
        
        st.divider()
        search = st.selectbox("Kullanıcı Ara", database.get_all_users_list(me))
        if st.button("Takip Et"):
            if database.follow_user(me, search): st.success("Takip edildi!")
            else: st.warning("Zaten takip ediyorsun.")
            
        if st.button("Çıkış"): st.session_state['logged_in']=False; st.rerun()

    # --- SAYFALAR ---
    
    if sel == "Profilim":
        st.subheader(f"👤 {me} Duvarı")
        with st.form("my_post"):
            txt = st.text_area("Bir şeyler yaz...")
            if st.form_submit_button("Paylaş"):
                database.add_post(me, txt, None, None, "personal")
                st.rerun()
        
        posts = database.get_posts(user_filter=me)
        for p in posts:
            st.info(f"{p[5]}\n\n{p[2]}") # Basit görünüm

    elif sel == "Sınıfım":
        my_class = database.get_user_data(me)[6]
        if not my_class:
            st.warning("Bir sınıfa üye değilsin.")
            code = st.text_input("Sınıf Kodu Gir")
            if st.button("Katıl"):
                ok, cname = database.join_class(me, code)
                if ok: st.success(f"{cname} sınıfına hoşgeldin!"); st.rerun()
                else: st.error("Kod hatalı.")
            
            if st.session_state['role'] == 'teacher':
                with st.expander("Sınıf Oluştur (Öğretmen)"):
                    cn = st.text_input("Sınıf Adı"); cc = st.text_input("Sınıf Kodu")
                    if st.button("Oluştur"): database.create_class(me, cn, cc); st.success("Oluşturuldu!")
        else:
            st.success(f"🏫 Sınıf: {my_class} Duvarı")
            with st.form("class_post"):
                txt = st.text_area("Sınıfa mesaj...")
                if st.form_submit_button("Gönder"):
                    database.add_post(me, txt, None, None, "class", my_class)
                    st.rerun()
            
            posts = database.get_posts("class", my_class)
            for p in posts:
                st.markdown(f"<div class='post-card'><b>{p[1]}</b>: {p[2]}</div>", unsafe_allow_html=True)

    elif sel.startswith("Mesaj"):
        st.header("💬 Mesajlaşma")
        database.mark_read(me)
        friends = database.get_mutual_friends(me)
        if not friends: st.info("Mesajlaşmak için karşılıklı takipleşmelisiniz.")
        else:
            tgt = st.selectbox("Kime:", friends)
            msgs = database.get_conversation(me, tgt)
            for m in msgs:
                align = "row-reverse" if m[0]==me else "row"
                bg = "#2563eb" if m[0]==me else "#334155"
                st.markdown(f"<div style='display:flex;flex-direction:{align};margin:5px'><div style='background:{bg};padding:10px;border-radius:10px'>{m[1]}</div></div>", unsafe_allow_html=True)
            
            with st.form("msg"):
                mt = st.text_input("Mesaj")
                if st.form_submit_button("Yolla") and mt:
                    database.send_message(me, tgt, mt); st.rerun()

    elif sel == "Kampüs Duvarı":
        st.subheader("📢 Kampüs Duvarı")
        st.info("Buraya yazmak için 500.000 Puan Bakiye gerekir. Her post -100.000 Puandır.")
        
        score = database.get_user_data(me)[0]
        if score >= 500000 or st.session_state['role']=='admin':
            with st.expander("Paylaşım Yap"):
                with st.form("cp"):
                    c = st.text_area("İçerik")
                    yt = st.text_input("Youtube Linki")
                    im = st.file_uploader("Resim", type=['png','jpg'])
                    if st.form_submit_button("Paylaş"):
                        database.add_score(me, -100000)
                        database.add_post(me, c, im, extract_yt(yt), "campus")
                        st.rerun()
        
        posts = database.get_posts("campus")
        for p in posts:
            # p: id, username, content, image, yt, timestamp, likes
            st.markdown(f"""
            <div class="post-card">
                <div class="post-header">
                    <b>@{p[1]}</b> <small style="margin-left:auto">{p[5]}</small>
                </div>
                <div class="post-content">{p[2]}</div>
                {f'<img src="data:image/jpeg;base64,{p[3]}" style="width:100%;border-radius:10px;">' if p[3] else ''}
            </div>""", unsafe_allow_html=True)
            if p[4]: st.video(p[4])
            
            c1, c2 = st.columns([1, 5])
            if c1.button(f"❤️ {p[6]}", key=f"l{p[0]}"): database.like_post(p[0]); st.rerun()
            with c2:
                with st.popover("➕ Yorum/Paylaş"):
                    coms = database.get_comments(p[0])
                    for cm in coms: st.caption(f"{cm[0]}: {cm[1]}")
                    nc = st.text_input("Yorum", key=f"c{p[0]}")
                    if st.button("Gönder", key=f"b{p[0]}"): database.add_comment(p[0], me, nc); st.rerun()

    elif sel == "Mağaza":
        st.header("💎 Kampüs Mağazası")
        st.metric("Bakiye", f"{database.get_user_data(me)[0]:,} P")
        
        t1, t2, t3 = st.tabs(["Çerçeveler", "İsimler", "Hediyeler"])
        
        def render_items(items, itype):
            # Mobilde 2'li, PC'de 4'lü grid için özel CSS kullanmıştık ama 
            # Streamlit columns ile de basitçe yapalım:
            rows = [items[i:i+4] for i in range(0, len(items), 4)]
            for row in rows:
                cols = st.columns(4)
                for i, x in enumerate(row):
                    with cols[i]:
                        icon = "🖼️" if itype=="frame" else "🔤" if itype=="name_style" else "🎁"
                        st.info(f"{icon} {x['n']}")
                        if st.button(f"AL {x['c']//1000}K", key=f"b_{x['n']}"):
                            if itype=="gift":
                                # Hediye için kullanıcı seçimi gerekir, basitleştirilmiş:
                                st.error("Hediye sekmesinden gönderiniz.")
                            else:
                                if database.buy_item(me, itype, x['v'], x['c']): st.success("Aldın!"); time.sleep(1); st.rerun()
                                else: st.error("Para yok")

        with t1:
            frames = [{"n":"Gold","v":"Gold","c":50000}, {"n":"Neon","v":"Neon","c":150000}, {"n":"Alev","v":"Fire","c":300000}, {"n":"Kral","v":"King","c":1000000}]
            render_items(frames, "frame")
        
        with t2:
            names = [{"n":"Glitch","v":"Glitch","c":100000}, {"n":"Neon","v":"Neon","c":500000}, {"n":"Altın","v":"Gold","c":750000}]
            render_items(names, "name_style")
            
        with t3:
            st.write("Arkadaşına Hediye Yolla")
            u_list = database.get_all_users_list(me)
            to = st.selectbox("Kime", u_list)
            g_list = ["Kahve (5K)", "Çikolata (10K)", "Gül (25K)", "Araba (500K)"]
            g_sel = st.selectbox("Hediye", g_list)
            if st.button("Gönder"):
                cost = int(re.search(r'\((\d+)K\)', g_sel).group(1)) * 1000
                if database.send_gift(me, to, g_sel.split('(')[0], cost): st.success("Gitti!")
                else: st.error("Bakiye yetersiz")

    elif sel == "Dersler":
        st.header("📚 Sınav Merkezi")
        if os.path.exists("exams.json"):
            data = json.load(open("exams.json", encoding="utf-8"))
            cls = st.selectbox("Sınıf", data.keys())
            lsn = st.selectbox("Ders", data[cls].keys())
            
            with st.form("exam"):
                sc = 0
                for i, q in enumerate(data[cls][lsn]):
                    st.write(f"{i+1}. {q.get('question') or q.get('text')}")
                    if q.get('options'):
                        ans = st.radio("Cevap", q['options'], key=f"q{i}")
                        if ans == q.get('answer'): sc += q.get('points', 0)
                    else:
                        ans = st.text_input("Cevap", key=f"t{i}")
                        if ans and ans.lower() == q.get('answer', '').lower(): sc += q.get('points', 0)
                
                if st.form_submit_button("Bitir"):
                    database.add_score(me, sc, "Sınav")
                    st.balloons(); st.success(f"Puan: {sc}"); time.sleep(2); st.rerun()

    elif sel == "Oyunlar":
        gm = st.selectbox("Oyun", ["Finans İmparatoru", "Matrix"])
        if gm == "Finans İmparatoru":
            components.html(get_finance_game_html(database.get_user_data(me)[0], me), height=600)
        else:
            st.write("Matrix oyunu yapım aşamasında.")

    elif sel == "Liderlik":
        st.dataframe(pd.DataFrame(database.get_leaderboard_data(), columns=["Öğrenci", "Puan"]), use_container_width=True)

    elif sel == "YÖNETİCİ":
        st.header("Yönetici Paneli")
        tab_u, tab_m = st.tabs(["Kullanıcılar", "Mesajlar (Casus)"])
        
        with tab_u:
            all_u = database.get_all_users_admin()
            df = pd.DataFrame(all_u, columns=["Kullanıcı", "Puan", "Rol", "Sınıf"])
            st.dataframe(df)
            
            tgt = st.selectbox("Kullanıcı Seç", df['Kullanıcı'])
            c1, c2 = st.columns(2)
            if c1.button("Kullanıcıyı SİL"): database.delete_user_admin(tgt); st.rerun()
            val = c2.number_input("Puan Ekle", value=0)
            if c2.button("Ekle"): database.add_score(tgt, val); st.success("Eklendi.")
            
        with tab_m:
            msgs = database.admin_get_all_messages()
            st.table(pd.DataFrame(msgs, columns=["Kimden", "Kime", "Mesaj", "Tarih"]))
