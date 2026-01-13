import streamlit as st
import streamlit.components.v1 as components
import random

# --- MODÜL IMPORTLARI ---
import database.core as core
import database.users as users
import database.social as social
import database.score as score
import ui.styles as styles
import ui.sidebar as sidebar
import ui.campus as campus
import ui.shop as shop
import ui.lessons as lessons
import ui.admin as admin_page
import games.finance as fin_game
import games.matrix as mtx_game

# --- AYARLAR ---
st.set_page_config(page_title="Dijital Kampüs", page_icon="🎓", layout="wide", initial_sidebar_state="expanded")

# --- BAŞLANGIÇ DURUMU ---
def init_state():
    defaults = {
        "logged_in": False, "user_role": None, "username": None, 
        "active_story_index": 0, "active_story_open": False,
        "draft_content": "", "open_comments": [],
        "captcha_q": None, "captcha_a": None
    }
    for k, v in defaults.items():
        if k not in st.session_state: st.session_state[k] = v

    if st.session_state['captcha_q'] is None:
        n1 = random.randint(1, 9); n2 = random.randint(1, 9)
        st.session_state['captcha_q'] = f"{n1} + {n2}"; st.session_state['captcha_a'] = n1 + n2

init_state()

# --- CSS YÜKLE ---
st.markdown(styles.MAIN_CSS, unsafe_allow_html=True)

# --- DB & ADMIN ---
try:
    core.create_tables()
    if not users.login_user("admin", "6626"): 
        users.add_user("admin", "6626", "admin")
except: pass

if st.session_state['logged_in']: 
    users.update_activity(st.session_state['username'])

# --- URL AKSİYONLARI ---
if "action" in st.query_params:
    try:
        act = st.query_params["action"]
        u = st.query_params.get("u")
        # Basit validasyon: Kullanıcı var mı?
        if users.get_user_styles(u)[0] is not None: 
            if act == "transfer":
                a = int(st.query_params["a"])
                st.session_state.update({'logged_in':True, 'username':u})
                if a > 0: 
                    score.add_score(u, a, "Oyun")
                    st.toast(f"✅ {a} Puan!", icon="💰") # SLEEP YOK
            elif act == "buy":
                t, v, c = st.query_params["t"], st.query_params["v"], int(st.query_params["c"])
                st.session_state.update({'logged_in':True, 'username':u})
                ok, msg = users.buy_item(u, t, v, c)
                if ok: st.toast(f"🎉 {msg}", icon="🛍️") # SLEEP YOK
                else: st.toast(f"❌ {msg}", icon="⚠️")
        st.query_params.clear(); st.rerun()
    except: st.query_params.clear()

# --- ANA AKIŞ ---
is_logged_in = sidebar.render_sidebar()

if not is_logged_in:
    sidebar.render_login_page()
else:
    # --- MENÜ ---
    menu_options = ["Kampüs Duvar", "Puan", "Ders", "Oyun", "Mağaza", "Mesaj"]
    if st.session_state.get('user_role') == 'admin':
        menu_options.append("Yönetim")
        
    selected_page = st.radio("Menü", menu_options, horizontal=True, label_visibility="collapsed")

    # --- SAYFALAR ---
    if selected_page == "Kampüs Duvar":
        campus.render_campus_wall()

    elif selected_page == "Puan":
        st.subheader("🏆 Liderlik Tablosu")
        my_sc = score.get_total_score(st.session_state['username'])
        st.info(f"Senin Puanın: **{my_sc:,}**")
        st.dataframe(score.get_leaderboard_data(), use_container_width=True)

    elif selected_page == "Mağaza":
        shop.render_shop()
        
    elif selected_page == "Yönetim":
        admin_page.render_admin_panel()

    elif selected_page == "Ders":
        lessons.render_lessons()

    elif selected_page == "Oyun":
        gm = st.selectbox("Oyun Seç", ["Finans İmparatoru", "Asset Matrix"])
        sc = score.get_total_score(st.session_state['username'])
        if gm == "Finans İmparatoru": 
            components.html(fin_game.get_finance_game_html(sc, st.session_state['username']), height=600)
        else: 
            components.html(mtx_game.get_matrix_game_html(st.session_state['username']), height=750)
        
    elif selected_page == "Mesaj":
        st.subheader("💬 Mesajlar")
        friends = social.get_friends(st.session_state['username'])
        
        if st.session_state['user_role'] == 'student' and "admin" not in friends: 
            friends.insert(0, "admin")
        if st.session_state['user_role'] == 'admin': 
            all_users = users.get_all_users_list()
            friends = [u[0] for u in all_users if u[0] != "admin"]
            
        target = st.selectbox("Kime Mesaj Yazacaksın?", friends) if friends else None
        
        if target:
            msgs = social.get_conversation(st.session_state['username'], target)
            for s, m, t in msgs:
                is_me = (s == st.session_state['username'])
                align = "flex-direction:row-reverse;" if is_me else "flex-direction:row;"
                bg = "#3b82f6" if is_me else "#334155"
                ava_html = styles.get_user_display_html(s, size=30)
                st.markdown(f"""
                <div style='display:flex; {align} align-items:center; margin-bottom:10px;'>
                    <div style='margin:0 10px;'>{ava_html}</div>
                    <div style='padding:10px 15px; border-radius:15px; background:{bg}; color:white; max-width:70%; font-size:0.9rem;'>
                        {m}<div style='font-size:0.6rem; opacity:0.7; text-align:right; margin-top:5px;'>{t[-5:]}</div>
                    </div>
                </div>""", unsafe_allow_html=True)
            
            if txt := st.chat_input("Mesaj yaz..."):
                social.send_message(st.session_state['username'], target, txt)
                st.rerun()
        else:
            st.info("Henüz arkadaşın yok. Yan panelden arkadaş ekleyebilirsin.")
