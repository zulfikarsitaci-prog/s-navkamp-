import streamlit as st
import pandas as pd
import time
import random
import database
import re
import os

# --- AYARLAR ---
st.set_page_config(page_title="Bağarası ÇPAL", page_icon="🎓", layout="wide", initial_sidebar_state="expanded")

def init_state():
    defaults = {
        "logged_in": False, "username": None, "user_role": None, 
        "active_menu": "📢 Kampüs Duvar", "draft_content": "", 
        "captcha_q": None, "captcha_a": None, "open_comments": []
    }
    for k, v in defaults.items():
        if k not in st.session_state: st.session_state[k] = v
    
    if st.session_state['captcha_q'] is None:
        n1 = random.randint(1,9); n2 = random.randint(1,9)
        st.session_state['captcha_q'] = f"{n1} + {n2}"; st.session_state['captcha_a'] = n1 + n2

init_state()
database.create_database()

# --- YARDIMCILAR ---
def extract_youtube_link(text):
    if not text: return None
    match = re.search(r'(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/(watch\?v=|embed/|v/|live/|.+\?v=)?([^&=%\?]{11})', text)
    if match: return f"https://www.youtube.com/watch?v={match.group(6)}"
    return None

# --- CSS (KOYU TEMA, CİNZEL FONT, DÜZGÜN İKONLAR) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@700&family=Orbitron:wght@700&family=Rye&family=Dancing+Script:wght@700&family=Metal+Mania&display=swap');

    /* GİRİŞ EKRANI */
    .login-container { text-align: center; margin-top: 20px; }
    .login-main { font-family: 'Cinzel', serif; color: #FFD700; font-size: 2.2rem; text-shadow: 2px 2px 4px #000; font-weight: bold; }
    .login-sub { color: #94a3b8; font-family: sans-serif; letter-spacing: 1px; font-size: 1rem; }

    /* POST KARTI */
    .post-card {
        background-color: #1e293b; 
        border: 1px solid #334155; 
        border-radius: 12px; 
        padding: 15px; 
        margin-bottom: 5px; 
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
    .post-header { display: flex; align-items: center; border-bottom: 1px solid #334155; padding-bottom: 8px; margin-bottom: 8px; }
    .post-content { color: #e2e8f0; font-size: 0.95rem; line-height: 1.5; white-space: pre-wrap; margin-bottom: 10px; }
    
    /* BUTONLARI İKON GİBİ GÖSTERME (HATA ÇÖZÜMÜ) */
    div.stButton > button {
        background-color: transparent !important;
        border: none !important;
        color: #94a3b8 !important;
        padding: 0px !important;
        font-size: 1.3rem !important;
        box-shadow: none !important;
        margin-right: 15px !important;
    }
    div.stButton > button:hover { color: #FFD700 !important; transform: scale(1.1); }
    
    /* YATAY HİZALAMA */
    div[data-testid="column"] { padding: 0 !important; min-width: 0 !important; flex: 0 0 auto !important; width: auto !important; }
    div[data-testid="stHorizontalBlock"] { align-items: center !important; flex-wrap: nowrap !important; }

    /* MAĞAZA */
    .shop-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 6px; margin-top: 10px; }
    .shop-item { background: #0f172a; border: 1px solid #334155; border-radius: 8px; padding: 5px; text-align: center; height: 110px; display: flex; flex-direction: column; justify-content: space-between; }
    .shop-name { font-size: 0.65rem; color: #cbd5e1; }
    .shop-price { background: #10b981; color: white; padding: 2px 8px; border-radius: 8px; font-size: 0.65rem; }

    /* STİLLER */
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
    .comment-box { background: #0f172a; padding: 8px; border-radius: 6px; margin-top: 6px; font-size: 0.85rem; border-left: 3px solid #334155; }
</style>
""", unsafe_allow_html=True)

def get_user_display_html(username, size=40):
    styles = database.get_user_styles(username)
    ava, frame, name_style, _, font_style, title = styles
    img_src = f"data:image/jpeg;base64,{ava}" if ava else "https://via.placeholder.com/150/CCCCCC/FFFFFF?text=U"
    f_html = f'<div class="frame-overlay frame-{frame}"></div>' if frame else ""
    classes = f"{f'name-{name_style}' if name_style else ''} {f'font-{font_style}' if font_style else ''}"
    return f'<div style="display:flex;align-items:center;"><div style="position:relative;margin-right:10px;"><img src="{img_src}" class="avatar-img">{f_html}</div><div class="{classes}" style="font-size:0.9rem;">{username} {f"<span class='title-badge'>{title}</span>" if title else ""}</div></div>'

def get_post_css(username):
    s = database.get_user_styles(username)
    return f"post-{s[3]} font-{s[4]}"

# --- SAYFALAR ---
if not st.session_state['logged_in']:
    st.markdown('<div class="login-container"><div class="login-sub">Muhasebe ve Finansman Alanı</div><div class="login-main">DİJİTAL GELİŞİM PLATFORMU</div><div class="login-sub">~ Dijital Kampüs ~</div></div>', unsafe_allow_html=True)
    
    with st.sidebar:
        # --- SIFIRLAMA BUTONU ---
        st.warning("Eğer giriş yapamıyorsanız:")
        if st.button("⚠️ SİSTEMİ SIFIRLA (Onarım)"):
            try:
                if os.path.exists("education_platform.db"):
                    os.remove("education_platform.db")
                    st.success("Sıfırlandı! Sayfayı yenile.")
                    time.sleep(1)
                    st.rerun()
            except: st.error("Silinemedi.")

    with st.container():
        with st.form("login"):
            u = st.text_input("Kullanıcı Adı")
            p = st.text_input("Şifre", type="password")
            if st.form_submit_button("Giriş"):
                user = database.login_user(u, p)
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
                        res, rank = database.add_user(nu, np, "student")
                        if res:
                            st.session_state['captcha_q'] = None
                            if rank<=10: st.balloons(); st.success("KURUCU oldun!")
                            else: st.success("Kaydedildi.")
                        else: st.error("İsim dolu.")
                    else: st.error("Yanlış cevap."); st.session_state['captcha_q'] = None; st.rerun()

else:
    # --- MENÜ ---
    with st.sidebar:
        st.markdown(get_user_display_html(st.session_state['username'], 70), unsafe_allow_html=True)
        st.write("")
        with st.expander("⚙️ Hesabım"):
            nname = st.text_input("Yeni İsim")
            cost = 0 if database.get_user_change_count(st.session_state['username']) == 0 else 500000
            if st.button(f"Değiştir ({cost:,} P)"):
                if nname:
                    ok, msg = database.change_username_logic(st.session_state['username'], nname)
                    if ok: st.session_state['username'] = nname; st.success(msg); time.sleep(1); st.rerun()
                    else: st.error(msg)
            st.divider()
            uimg = st.file_uploader("Fotoğraf", type=['png','jpg'])
            if uimg:
                if database.update_avatar(st.session_state['username'], uimg): st.success("Yüklendi!"); time.sleep(1); st.rerun()
        
        st.write("")
        if st.button("🚪 Çıkış"): st.session_state['logged_in']=False; st.rerun()

    st.markdown(f'<div style="background:#1e293b;padding:10px;border-radius:8px;border-bottom:2px solid #FFD700;margin-bottom:10px;color:white;">Merhaba, <b>{st.session_state["username"]}</b></div>', unsafe_allow_html=True)
    
    database.mark_notifications_read(st.session_state['username'])
    menu = ["📢 Kampüs Duvar", "💬 Mesaj", "🏆 Puan", "🛒 Mağaza", "🎮 Oyun"]
    if st.session_state['user_role'] == 'admin': menu.append("⚙️ Admin")
    sel = st.radio("", menu, horizontal=True, label_visibility="collapsed")

    if sel == "📢 Kampüs Duvar":
        st.subheader("Kampüs Duvar")
        ms = database.get_total_score(st.session_state['username'])
        
        if ms >= 1000000 or st.session_state['user_role'] == 'admin':
            with st.expander("✨ Paylaşım (-100,000 P)", expanded=False):
                with st.form("sh"):
                    txt = st.text_area("İçerik", value=st.session_state['draft_content'])
                    img = st.file_uploader("Resim", type=['png','jpg'])
                    if st.form_submit_button("Paylaş"):
                        if ms >= 100000:
                            database.add_score(st.session_state['username'], -100000, "Post")
                            database.add_post(st.session_state['username'], txt, img)
                            st.session_state['draft_content'] = ""
                            st.rerun()
                        else: st.error("Yetersiz Puan")
        else: st.info("Paylaşım için 1M Puan.")

        for p in database.get_posts(20):
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

            # --- İKONLAR (YAN YANA) ---
            c1, c2, c3, c4 = st.columns([0.15, 0.15, 0.15, 0.55])
            with c1: 
                if st.button(f"❤️ {p[5]}", key=f"l_{p[0]}"): database.like_post(p[0]); st.rerun()
            with c2: 
                # Yorum görsel
                st.markdown("<div style='padding-top:4px;color:#94a3b8;cursor:default;'>💬</div>", unsafe_allow_html=True)
            with c3:
                if st.button("🔄", key=f"r_{p[0]}"): 
                    st.session_state['draft_content'] = f"Alıntı (@{p[1]}): {p[2]}"
                    st.toast("Yukarı taşındı!")

            with c4:
                _, sc2 = st.columns([0.8, 0.2])
                with sc2:
                    with st.popover("➕"):
                        if st.button("💬 Yorum Yap", key=f"cmbtn_{p[0]}"):
                            if p[0] in st.session_state['open_comments']: st.session_state['open_comments'].remove(p[0])
                            else: st.session_state['open_comments'].append(p[0])
                            st.rerun()
                        if st.button("🔄 Paylaş", key=f"rpbtn_{p[0]}"):
                            st.session_state['draft_content'] = f"Alıntı (@{p[1]}): {p[2]}"
                            st.rerun()
                        if st.session_state['username'] == p[1] or st.session_state['user_role'] == 'admin':
                            if st.button("🗑️ Sil", key=f"dbtn_{p[0]}"): database.delete_post(p[0]); st.rerun()

            if p[0] in st.session_state['open_comments']:
                coms = database.get_comments(p[0])
                if coms:
                    for c in coms: st.markdown(f"<div class='comment-box'>{get_user_display_html(c[0], 20)} {c[1]}</div>", unsafe_allow_html=True)
                
                with st.form(f"c_form_{p[0]}", clear_on_submit=True):
                    cmt = st.text_input("Yorum...", label_visibility="collapsed")
                    if st.form_submit_button("Gönder"):
                        if cmt:
                            database.add_comment(p[0], st.session_state['username'], cmt)
                            st.rerun()
            st.write("")

    elif sel == "💬 Mesaj":
        st.subheader("Mesajlaşma")
        all_users = database.get_all_users_list()
        # Kendisi hariç
        all_users = [u for u in all_users if u != st.session_state['username']]
        
        target = st.selectbox("Kime:", all_users)
        if target:
            msgs = database.get_conversation(st.session_state['username'], target)
            for m in msgs:
                align = "row-reverse" if m[0] == st.session_state['username'] else "row"
                bg = "#2563eb" if m[0] == st.session_state['username'] else "#334155"
                st.markdown(f"""<div style="display:flex;flex-direction:{align};margin-bottom:5px;">
                    <div style="background:{bg};padding:8px;border-radius:10px;max-width:70%;">{m[1]}</div>
                </div>""", unsafe_allow_html=True)
            
            with st.form("msg_form", clear_on_submit=True):
                msg_txt = st.text_input("Mesaj")
                if st.form_submit_button("Gönder"):
                    if msg_txt:
                        database.send_message(st.session_state['username'], target, msg_txt)
                        st.rerun()

    elif sel == "🛒 Mağaza":
        st.header("Mağaza")
        st.metric("Bakiye", f"{database.get_total_score(st.session_state['username']):,} P")
        
        tabs = st.tabs(["Çerçeve", "İsim", "Font"])
        
        # Basit Mağaza Öğeleri (Yer kazanmak için döngüyle)
        with tabs[0]: 
            items = [{"n": "Gold", "c": 50000, "t": "frame", "v": "Gold"}, {"n": "Neon", "c": 150000, "t": "frame", "v": "Neon"}, {"n": "Alev", "c": 300000, "t": "frame", "v": "Fire"}, {"n": "Kral", "c": 2000000, "t": "frame", "v": "King"}]
            cols = st.columns(4)
            for i, it in enumerate(items):
                with cols[i]:
                    st.markdown(f"<div class='shop-item'><div class='shop-name'>{it['n']}</div><div class='shop-price'>{it['c']:,}</div></div>", unsafe_allow_html=True)
                    if st.button("Al", key=f"bi_{i}"):
                        ok, msg = database.buy_item(st.session_state['username'], it['t'], it['v'], it['c'])
                        if ok: st.success(msg); time.sleep(1); st.rerun()
                        else: st.error(msg)

    elif sel == "🏆 Puan":
        st.dataframe(pd.DataFrame(database.run_query("SELECT student_username, SUM(grade) as T FROM grades GROUP BY student_username ORDER BY T DESC", fetch=True), columns=["Öğrenci","Puan"]), use_container_width=True)

    elif sel == "⚙️ Admin":
        st.write("Admin Paneli")
        all_u = database.get_all_users_list()
        tu = st.selectbox("Kullanıcı", all_u)
        if st.button("Sil"): database.delete_user(tu); st.rerun()
