import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import random
import database
import re
import time

# --- AYARLAR ---
st.set_page_config(page_title="Bağarası ÇPAL Dijital", page_icon="🎓", layout="wide", initial_sidebar_state="expanded")

# --- CSS (Mavi Kutu, Havalı Tasarım) ---
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
    .login-sub { font-family: 'Roboto', sans-serif; color: #e0f2fe; font-size: 1.2rem; letter-spacing: 2px; }

    /* POST KARTI */
    .post-card {
        background-color: #0f172a; 
        border: 1px solid #334155;
        border-radius: 15px;
        padding: 15px;
        margin-bottom: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
    .post-header { display: flex; align-items: center; border-bottom: 1px solid #1e293b; padding-bottom: 10px; margin-bottom: 10px; }
    .post-avatar { width: 40px; height: 40px; border-radius: 50%; object-fit: cover; margin-right: 10px; border: 2px solid #fbbf24; }
    .post-user { font-weight: bold; color: #e2e8f0; font-size: 1rem; }
    .post-content { color: #cbd5e1; font-size: 0.95rem; line-height: 1.5; white-space: pre-wrap; margin-bottom: 10px; }
    
    /* BUTONLAR */
    .action-btn { background: transparent; border: none; color: #94a3b8; font-size: 1.2rem; cursor: pointer; }
    .action-btn:hover { color: #fbbf24; }
    
    /* MAĞAZA GRİD */
    .shop-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 15px; }
    .shop-item { background: #1e293b; border: 1px solid #475569; border-radius: 10px; padding: 10px; text-align: center; }
    
    /* ÇERÇEVE EFEKTLERİ */
    .frame-Gold { border: 3px solid #FFD700; box-shadow: 0 0 8px #FFD700; }
    .frame-Neon { border: 3px solid #00ffff; box-shadow: 0 0 8px #00ffff; }
    .frame-Fire { border: 3px solid #ff4500; box-shadow: 0 0 10px #ff0000; }
    
    /* İSİM EFEKTLERİ */
    .name-Glitch { color: #00ffff; text-shadow: 2px 0 #ff00ff; }
    .name-Gold { background: linear-gradient(to right, #BF953F, #FCF6BA, #B38728); -webkit-background-clip: text; color: transparent; font-weight: bold; }
    
</style>
""", unsafe_allow_html=True)

# --- INIT ---
def init():
    if 'logged_in' not in st.session_state:
        st.session_state.update({
            'logged_in': False, 'username': None, 'role': None, 'class_code': None,
            'active_tab': 'Kampüs Duvarı', 'captcha': None
        })
    if st.session_state['captcha'] is None:
        n1, n2, op = random.randint(1,10), random.randint(1,10), random.choice(['+','-','*'])
        res = eval(f"{n1}{op}{n2}")
        st.session_state['captcha'] = {'q': f"{n1} {op} {n2}", 'a': res}

database.create_database()
init()

# --- YARDIMCILAR ---
def get_avatar_html(username, size=40):
    u_info = database.get_user_info(username) # score, role, class, avatar, frame, name
    ava = u_info[3]
    frame = u_info[4]
    name_style = u_info[5]
    
    img_src = f"data:image/jpeg;base64,{ava}" if ava else "https://via.placeholder.com/150"
    frame_class = f"frame-{frame}" if frame else ""
    name_class = f"name-{name_style}" if name_style else ""
    
    return f"""
    <div style="display:flex; align-items:center;">
        <img src="{img_src}" class="post-avatar {frame_class}" style="width:{size}px; height:{size}px;">
        <span class="post-user {name_class}" style="font-size:{size/2.5}px;">{username}</span>
    </div>
    """

def extract_yt(text):
    match = re.search(r'(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/(watch\?v=|embed/|v/|live/|.+\?v=)?([^&=%\?]{11})', text)
    return f"https://www.youtube.com/watch?v={match.group(6)}" if match else None

# --- GİRİŞ & KAYIT ---
if not st.session_state['logged_in']:
    st.markdown("""
    <div class="login-box">
        <div class="login-title">BAĞARASI ÇPAL</div>
        <div class="login-sub">MUHASEBE VE FİNANSMAN ALANI</div>
    </div>
    """, unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["GİRİŞ YAP", "KAYIT OL"])
    
    with tab1:
        with st.form("login"):
            u = st.text_input("Kullanıcı Adı")
            p = st.text_input("Şifre", type="password")
            if st.form_submit_button("Giriş"):
                user = database.login_user(u, p)
                if user:
                    st.session_state.update({'logged_in':True, 'username':user[1], 'role':user[3], 'class_code':user[4]})
                    st.rerun()
                else: st.error("Hatalı bilgiler.")

    with tab2:
        with st.form("reg"):
            nu = st.text_input("Kullanıcı Adı Belirle")
            np = st.text_input("Şifre Belirle", type="password")
            st.write(f"Güvenlik Sorusu: {st.session_state['captcha']['q']} = ?")
            ans = st.number_input("Cevap", step=1)
            if st.form_submit_button("Kayıt Ol"):
                if ans == st.session_state['captcha']['a']:
                    if database.add_user(nu, np, "student"):
                        st.success("Kayıt Başarılı! Giriş yapabilirsin.")
                        st.session_state['captcha'] = None
                    else: st.error("Bu isim alınmış.")
                else: st.error("Matematik sorusu yanlış!")
                
else:
    # --- ANA UYGULAMA ---
    me = st.session_state['username']
    my_info = database.get_user_info(me) # score, role, class...
    my_score = my_info[0]
    
    # SİDEBAR
    with st.sidebar:
        st.markdown(get_avatar_html(me, 60), unsafe_allow_html=True)
        st.metric("Puan", f"{my_score:,}")
        
        # Sınıf Bilgisi
        if my_info[2]: st.info(f"Sınıf: {my_info[2]}")
        else: st.warning("Sınıfın Yok")
        
        # Bildirimler
        noti = database.get_notifications(me)
        noti_lbl = f"🔔 ({noti})" if noti > 0 else "🔔"
        
        menu = ["Kampüs Duvarı", "Profilim", "Sınıfım", "Mesajlar", "Mağaza", "Dersler", "Oyunlar", "Liderlik"]
        if st.session_state['role'] == 'admin': menu.append("YÖNETİCİ PANELİ")
        
        sel = st.radio("Menü", menu, label_visibility="collapsed")
        
        # Arkadaş Arama / Takip
        st.divider()
        st.write("🔍 Kullanıcı Ara")
        search_u = st.selectbox("Kişi Seç", database.get_all_users_except_me(me))
        if st.button("Takip Et"):
            if database.follow_user(me, search_u): st.success(f"{search_u} takip edildi!")
            else: st.warning("Zaten takip ediyorsun.")
            
        st.divider()
        if st.button("Çıkış Yap"): st.session_state['logged_in']=False; st.rerun()

    # --- SAYFALAR ---
    
    if sel == "Kampüs Duvarı" or sel == "Profilim" or sel == "Sınıfım":
        # Gönderi Alanı
        wall_type = "campus"
        posts = []
        
        if sel == "Kampüs Duvarı":
            st.title("📢 Kampüs Duvarı")
            st.info("⚠️ Buraya yazmak için 500.000 Puanın olmalı. Her post 100.000 Puan siler.")
            if my_score >= 500000 or st.session_state['role'] == 'admin':
                with st.expander("✨ Bir şeyler paylaş..."):
                    with st.form("post_campus"):
                        txt = st.text_area("Mesajın")
                        yt = st.text_input("YouTube Linki (Opsiyonel)")
                        img = st.file_uploader("Resim", type=['png','jpg'])
                        if st.form_submit_button("Paylaş (-100.000 P)"):
                            if my_score >= 100000:
                                database.add_score(me, -100000)
                                database.add_post(me, txt, img, extract_yt(yt), "campus")
                                st.success("Paylaşıldı!"); time.sleep(1); st.rerun()
                            else: st.error("Puan yetersiz.")
            posts = database.get_posts("campus")
            
        elif sel == "Profilim":
            st.title("👤 Kendi Duvarım")
            with st.form("post_profile"):
                txt = st.text_area("Not al...")
                if st.form_submit_button("Kaydet (Ücretsiz)"):
                    database.add_post(me, txt, None, None, "personal")
                    st.rerun()
            posts = database.get_posts(user_filter=me)
            
        elif sel == "Sınıfım":
            st.title("🏫 Sınıf Duvarı")
            if st.session_state['role'] == 'teacher':
                with st.expander("Yeni Sınıf Oluştur"):
                    nc = st.text_input("Sınıf Kodu (Örn: 9A_MUH)")
                    nn = st.text_input("Sınıf Adı")
                    if st.button("Oluştur"):
                        if database.create_class(me, nn, nc): st.success("Sınıf açıldı!"); database.join_class(me, nc); st.rerun()
            
            if not st.session_state['class_code']:
                cc = st.text_input("Sınıf Kodunu Gir")
                if st.button("Sınıfa Katıl"):
                    ok, cname = database.join_class(me, cc)
                    if ok: st.success(f"{cname} sınıfına katıldın!"); st.session_state['class_code']=cc; st.rerun()
                    else: st.error("Kod hatalı.")
            else:
                st.success(f"Şu an {st.session_state['class_code']} sınıfındasın.")
                with st.form("post_class"):
                    txt = st.text_area("Sınıfa Duyuru/Mesaj")
                    if st.form_submit_button("Paylaş"):
                        database.add_post(me, txt, None, None, "class", st.session_state['class_code'])
                        st.rerun()
                posts = database.get_posts("class", st.session_state['class_code'])

        # Postları Listele
        for p in posts:
            # p: id, username, content, image, yt, timestamp, likes
            st.markdown(f"""
            <div class="post-card">
                <div class="post-header">
                    {get_avatar_html(p[1], 30)}
                    <span style="margin-left:auto; color:gray; font-size:0.8rem;">{p[5]}</span>
                </div>
                <div class="post-content">{p[2]}</div>
                {f'<img src="data:image/jpeg;base64,{p[3]}" style="width:100%; border-radius:10px; margin-top:10px;">' if p[3] else ''}
            </div>
            """, unsafe_allow_html=True)
            
            if p[4]: st.video(p[4])
            
            # Alt Butonlar (Kalp ve Artı)
            c1, c2 = st.columns([1, 10])
            with c1:
                if st.button(f"❤️ {p[6]}", key=f"like_{p[0]}"):
                    database.like_post(p[0]); st.rerun()
            with c2:
                # Popover (Artı İşareti)
                with st.popover("➕ İşlemler"):
                    st.write("Yorumlar:")
                    comments = database.get_comments(p[0])
                    for c in comments:
                        st.caption(f"**{c[0]}:** {c[1]}")
                    
                    with st.form(f"com_{p[0]}"):
                        new_c = st.text_input("Yorum Yaz")
                        if st.form_submit_button("Gönder"):
                            database.add_comment(p[0], me, new_c)
                            st.rerun()
                    st.divider()
                    if st.button("Paylaş", key=f"share_{p[0]}"):
                        st.toast("Link kopyalandı! (Simülasyon)")

    elif sel == "Mesajlar":
        st.header("💬 Mesajlar")
        database.mark_read(me) # Sayfaya girince okundu say
        friends = database.get_mutual_friends(me)
        
        if not friends:
            st.info("Mesajlaşmak için birini takip etmelisin ve o da seni takip etmeli (Karşılıklı Takip).")
        else:
            target = st.selectbox("Kimle Sohbet?", friends)
            
            # Sohbet Geçmişi
            msgs = database.get_conversation(me, target)
            for m in msgs:
                align = "row-reverse" if m[0] == me else "row"
                bg = "#1d4ed8" if m[0] == me else "#334155" # Mavi vs Gri
                st.markdown(f"""
                <div style="display:flex; flex-direction:{align}; margin-bottom:5px;">
                    <div style="background:{bg}; padding:8px 12px; border-radius:15px; max-width:70%; color:white;">
                        {m[1]}
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            with st.form("send_msg", clear_on_submit=True):
                txt = st.text_input("Mesaj...")
                if st.form_submit_button("Gönder"):
                    if txt:
                        database.send_message(me, target, txt)
                        st.rerun()

    elif sel == "Mağaza":
        st.header("🛒 Kampüs Mağazası")
        st.metric("Bakiyen", f"{my_score:,} P")
        
        tabs = st.tabs(["Çerçeveler", "İsim Efektleri", "Hediyeler"])
        
        with tabs[0]: # ÇERÇEVELER
            items = [
                {"n": "Gold", "c": 50000, "t": "frame", "v": "Gold"},
                {"n": "Neon", "c": 150000, "t": "frame", "v": "Neon"},
                {"n": "Alev", "c": 300000, "t": "frame", "v": "Fire"},
                {"n": "Matrix", "c": 500000, "t": "frame", "v": "Matrix"}
            ]
            cols = st.columns(4)
            for i, item in enumerate(items):
                with cols[i]:
                    st.markdown(f"<div class='shop-item'><b>{item['n']}</b><br>{item['c']:,} P</div>", unsafe_allow_html=True)
                    if st.button("Satın Al", key=f"bf_{i}"):
                        if database.buy_item(me, "frame", item['v'], item['c']):
                            st.success("Hayırlı olsun!"); time.sleep(1); st.rerun()
                        else: st.error("Para yetersiz.")

        with tabs[1]: # İSİMLER
            items = [
                {"n": "Glitch", "c": 100000, "t": "name", "v": "Glitch"},
                {"n": "Gold", "c": 750000, "t": "name", "v": "Gold"}
            ]
            cols = st.columns(4)
            for i, item in enumerate(items):
                with cols[i]:
                    st.markdown(f"<div class='shop-item'><b>{item['n']}</b><br>{item['c']:,} P</div>", unsafe_allow_html=True)
                    if st.button("Satın Al", key=f"bn_{i}"):
                        if database.buy_item(me, "name", item['v'], item['c']):
                            st.success("Aldın!"); time.sleep(1); st.rerun()
        
        with tabs[2]: # HEDİYELER
            st.subheader("Arkadaşına Hediye Gönder")
            target_user = st.selectbox("Kime:", database.get_all_users_except_me(me))
            gifts = [("Kahve ☕", 5000), ("Çikolata 🍫", 10000), ("Gül 🌹", 25000), ("Araba 🏎️", 500000)]
            
            cols = st.columns(4)
            for i, (gname, gcost) in enumerate(gifts):
                with cols[i]:
                    st.markdown(f"<div class='shop-item'><b>{gname}</b><br>{gcost:,} P</div>", unsafe_allow_html=True)
                    if st.button("Gönder", key=f"gift_{i}"):
                        if database.send_gift(me, target_user, gname, gcost):
                            st.success("Gönderildi!")
                        else: st.error("Paran yok.")

    elif sel == "Dersler":
        st.header("📚 Sınav Modülü")
        # JSON Dosyasını oku (Önceki promp'taki veri)
        if not os.path.exists("exams.json"):
            st.error("Sınav verisi bulunamadı.")
        else:
            with open("exams.json", "r", encoding="utf-8") as f:
                data = json.load(f)
            
            cls = st.selectbox("Sınıf Seç", list(data.keys()))
            sbj = st.selectbox("Ders Seç", list(data[cls].keys()))
            
            questions = data[cls][sbj]
            
            with st.form("exam_form"):
                score = 0
                total_p = 0
                for i, q in enumerate(questions):
                    q_type = q.get('type', 'text')
                    st.markdown(f"**Soru {i+1}:** {q.get('text') or q.get('question')}")
                    
                    if q_type == 'test':
                        ans = st.radio("Cevap", q['options'], key=f"q_{i}")
                        if ans == q['answer']: score += q['points']
                    elif q_type == 'text':
                        ans = st.text_input("Cevabınız", key=f"q_{i}")
                        # Basit kontrol
                        if ans and ans.lower() == q['answer'].lower(): score += q['points']
                    
                    total_p += q.get('points', 0)
                    st.markdown("---")
                
                if st.form_submit_button("Sınavı Bitir"):
                    database.add_score(me, score, f"Sınav: {sbj}")
                    st.balloons()
                    st.success(f"Puanın: {score} / {total_p}")

    elif sel == "Liderlik":
        st.header("🏆 Liderlik Tablosu")
        data = database.get_leaderboard_data()
        df = pd.DataFrame(data, columns=["Öğrenci", "Puan"])
        st.dataframe(df, use_container_width=True)

    elif sel == "YÖNETİCİ PANELİ":
        st.error("⚠️ YÖNETİCİ ALANI")
        
        tab_users, tab_spy = st.tabs(["Kullanıcı Yönetimi", "Casus Modu"])
        
        with tab_users:
            all_users = database.admin_get_all_users() # username, score, role, class
            df_users = pd.DataFrame(all_users, columns=["Kullanıcı", "Puan", "Rol", "Sınıf"])
            st.dataframe(df_users)
            
            target = st.selectbox("İşlem Yapılacak Kişi", df_users["Kullanıcı"].tolist())
            c1, c2 = st.columns(2)
            with c1:
                val = st.number_input("Puan Ekle/Sil (-/+)", value=0)
                if st.button("Puanı İşle"):
                    database.add_score(target, val, "Admin Eliyle")
                    st.success("İşlendi.")
            with c2:
                if st.button("KULLANICIYI SİL", type="primary"):
                    database.admin_delete_user(target)
                    st.error("Silindi!")
                    st.rerun()

        with tab_spy:
            st.write("🕵️ Tüm Mesajlar")
            msgs = database.admin_get_all_messages()
            st.table(pd.DataFrame(msgs, columns=["Kimden", "Kime", "Mesaj", "Zaman"]))
