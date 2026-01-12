import streamlit as st
import streamlit.components.v1 as components
import time
import random

# Modül Importları
import database.core as core
import database.users as users
import database.social as social
import database.score as score
import ui.styles as styles
import ui.sidebar as sidebar
import ui.campus as campus
import ui.shop as shop
import ui.lessons as lessons
import games.finance as fin_game
import games.matrix as mtx_game

# --- AYARLAR ---
st.set_page_config(page_title="Bağarası ÇPAL", page_icon="🎓", layout="wide", initial_sidebar_state="expanded")

# --- BAŞLANGIÇ DURUMU ---
def init_state():
    defaults = {
        "logged_in": False, "user_role": None, "username": None, 
        "active_menu": "📢 Kampüs Duvar", "draft_content": "",
        "captcha_q": None, "captcha_a": None, "open_comments": []
    }
    for k, v in defaults.items():
        if k not in st.session_state: st.session_state[k] = v

    if st.session_state['captcha_q'] is None:
        n1 = random.randint(1, 9); n2 = random.randint(1, 9)
        st.session_state['captcha_q'] = f"{n1} + {n2}"; st.session_state['captcha_a'] = n1 + n2

init_state()

# --- CSS YÜKLE ---
st.markdown(styles.MAIN_CSS, unsafe_allow_html=True)

# --- VERİTABANI BAŞLAT ---
try:
    core.create_tables()
    if not users.login_user("admin", "6626"): users.add_user("admin", "6626", "admin")
except: pass
if st.session_state['logged_in']: users.update_activity(st.session_state['username'])

# --- URL AKSİYONLARI (Transfer/Satın Alma) ---
if "action" in st.query_params:
    try:
        act = st.query_params["action"]
        u = st.query_params.get("u")
        if users.get_user_role(u): # Geçerli kullanıcı mı?
            if act == "transfer":
                a = int(st.query_params["a"])
                st.session_state.update({'logged_in':True, 'username':u, 'active_menu':"🎮 Oyun"})
                if a > 0: score.add_score(u, a, "Oyun"); st.toast(f"✅ {a} Puan!", icon="💰"); time.sleep(1)
            elif act == "buy":
                t, v, c = st.query_params["t"], st.query_params["v"], int(st.query_params["c"])
                st.session_state.update({'logged_in':True, 'username':u, 'active_menu':"🛒 Mağaza"})
                ok, msg = score.buy_item(u, t, v, c)
                if ok: st.toast(f"🎉 {msg}", icon="🛍️"); time.sleep(1)
                else: st.toast(f"❌ {msg}", icon="⚠️")
            elif act == "gift":
                t, g, c = st.query_params["t"], st.query_params["g"], int(st.query_params["c"])
                st.session_state.update({'logged_in':True, 'username':u, 'active_menu':"🛒 Mağaza"})
                ok, msg = score.send_gift(u, t, g, c)
                if ok: st.toast(f"🎁 {msg}", icon="✅"); time.sleep(1)
                else: st.toast(f"❌ {msg}", icon="⚠️")
        st.query_params.clear(); st.rerun()
    except: st.query_params.clear()

# --- ANA AKIŞ ---
is_logged_in = sidebar.render_sidebar()

if not is_logged_in:
    sidebar.render_login_page()
else:
    # Üst Bar
    st.markdown(f'<div class="top-bar"><div class="user-greeting">Merhaba, {st.session_state["username"]}</div><div class="role-badge">{st.session_state.get("user_role", "student")}</div></div>', unsafe_allow_html=True)
    
    # Menü
    noti_count = social.get_unread_notification_count(st.session_state['username'])
    noti_text = f"🔔 ({noti_count})" if noti_count > 0 else "🔔"
    menu_ops = ["📢 Kampüs Duvar", "💬 Mesaj", "🏆 Puan", "📚 Ders", "🎮 Oyun", "🛒 Mağaza", noti_text]
    if st.session_state['user_role'] == 'admin': menu_ops.append("⚙️ Admin")
    
    curr = st.session_state['active_menu']
    if curr.startswith("🔔") and curr != noti_text: curr = noti_text
    
    ix = 0
    if curr in menu_ops: ix = menu_ops.index(curr)
    sel = st.radio("", menu_ops, index=ix, horizontal=True, label_visibility="collapsed")
    if sel != st.session_state['active_menu']: st.session_state['active_menu'] = sel; st.rerun()

    # Sayfa Yönlendirme
    if sel == "📢 Kampüs Duvar":
        campus.render_campus_wall()

    elif sel == "🛒 Mağaza":
        shop.render_shop()

    elif sel == "📚 Ders":
        lessons.render_lessons()

    elif sel == "🏆 Puan":
        st.metric("Puan", score.get_total_score(st.session_state['username']))
        st.dataframe(score.get_leaderboard_data(), use_container_width=True)

    elif sel == "🎮 Oyun":
        gm = st.selectbox("Seç", ["Finans İmparatoru", "Asset Matrix"])
        sc = score.get_total_score(st.session_state['username'])
        if gm == "Finans İmparatoru": components.html(fin_game.get_finance_game_html(sc, st.session_state['username']), height=600)
        else: components.html(mtx_game.get_matrix_game_html(st.session_state['username']), height=750)
        
    elif sel == "💬 Mesaj":
        friends = social.get_friends(st.session_state['username'])
        if st.session_state['user_role'] == 'student' and "admin" not in friends: friends.insert(0, "admin")
        if st.session_state['user_role'] == 'admin': friends = [u[0] for u in users.get_all_users() if u[0]!="admin"]
        target = st.selectbox("Kişi", friends) if friends else None
        if target:
            for s, m, t in social.get_conversation(st.session_state['username'], target):
                ava_html = styles.get_user_display_html(s, size=30)
                align = "flex-direction:row-reverse;background:#2563eb" if s == st.session_state['username'] else "flex-direction:row;background:#334155"
                st.markdown(f"""<div style='display:flex;{align};align-items:center;margin:5px;'>{ava_html} <div style='padding:10px;border-radius:10px;margin:5px;color:white;background:inherit'>{m}</div></div>""", unsafe_allow_html=True)
            if txt := st.chat_input("Yaz..."): social.send_message(st.session_state['username'], target, txt); st.rerun()
        else: st.info("Kimse yok.")

    elif sel.startswith("🔔"):
        st.header("Bildirimler")
        notis = social.get_unread_notifications(st.session_state['username'])
        if not notis: st.info("Temiz.")
        else:
            for who, comment, post_summary in notis:
                st.warning(f"**{who}**: '{comment}' (Gönderi: {post_summary[:20]}...)")
            social.mark_notifications_read(st.session_state['username'])

    elif sel == "⚙️ Admin":
        st.header("Admin")
        st.subheader("Kullanıcı Düzenle")
        all_u = [u[0] for u in users.get_all_users()]
        target_u = st.selectbox("Kullanıcı", all_u)
        new_p = st.number_input("Puan Ekle", value=0)
        if st.button("Güncelle"): score.add_score(target_u, new_p, "Admin"); st.success("Tamam!")
        st.divider()
        st.subheader("Casus Modu")
        spy_u = st.selectbox("Kimin Mesajları?", all_u, key="spu")
        spy_p = st.selectbox("Kiminle?", all_u, key="spp")
        if st.button("Oku"):
            msgs = social.get_conversation(spy_u, spy_p)
            for s, m, t in msgs: st.write(f"**{s}**: {m} ({t})")
        st.divider()
        if st.button("Sil"): users.delete_user(target_u); st.error("Silindi!"); st.rerun()
