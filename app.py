# =========================
# app.py (FINAL - STABLE)
# =========================

import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import json, os, time, random, re
from datetime import datetime
import database

# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------
st.set_page_config(
    page_title="Bağarası ÇPAL",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --------------------------------------------------
# SESSION STATE INIT
# --------------------------------------------------
def init_state():
    defaults = {
        "logged_in": False,
        "user_role": None,
        "username": None,
        "active_menu": "📢 Kampüs Duvar",
        "draft_content": "",
        "open_comments": [],
        "captcha_q": None,
        "captcha_a": None,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

    if st.session_state["captcha_q"] is None:
        a, b = random.randint(1, 9), random.randint(1, 9)
        st.session_state["captcha_q"] = f"{a} + {b}"
        st.session_state["captcha_a"] = a + b

init_state()

# --------------------------------------------------
# DATABASE INIT
# --------------------------------------------------
try:
    database.create_database()
    if not database.login_user("admin", "6626"):
        database.add_user("admin", "6626", "admin")
except:
    pass

if st.session_state["logged_in"]:
    database.update_activity(st.session_state["username"])

# --------------------------------------------------
# HELPERS
# --------------------------------------------------
def extract_youtube_link(text):
    if not text:
        return None
    m = re.search(
        r"(https?://)?(www\.)?(youtube|youtu)\.(com|be)/(watch\?v=|live/)?([^&=%\?]{11})",
        text,
    )
    if m:
        return f"https://www.youtube.com/watch?v={m.group(6)}"
    return None


def get_user_display_html(username):
    ava, frame, name_style, _, font_style, title = database.get_user_styles(username)
    img = (
        f"data:image/jpeg;base64,{ava}"
        if ava
        else "https://via.placeholder.com/40"
    )
    return f"""
    <div style="display:flex;align-items:center;gap:8px">
        <img src="{img}" style="width:40px;height:40px;border-radius:50%">
        <b>{username}</b>
        {f"<span style='font-size:10px'>[{title}]</span>" if title else ""}
    </div>
    """


# --------------------------------------------------
# LOAD EXAMS
# --------------------------------------------------
@st.cache_data
def load_exams():
    if os.path.exists("exams.json"):
        return json.load(open("exams.json", encoding="utf-8"))
    return {}

# --------------------------------------------------
# GAMES
# --------------------------------------------------
def finance_game_html(start_score, user):
    return f"""
    <html>
    <body style="background:#0f172a;color:white;text-align:center">
        <h2>💰 Finans İmparatoru</h2>
        <p>Başlangıç Puanı: {start_score}</p>
        <button onclick="alert('Oyun burada!')">Oyna</button>
    </body>
    </html>
    """

def matrix_game_html(user):
    return f"""
    <html>
    <body style="background:black;color:#00ffff;text-align:center">
        <h2>🧩 Asset Matrix</h2>
        <p>Puzzle Game</p>
    </body>
    </html>
    """

# --------------------------------------------------
# LOGIN
# --------------------------------------------------
if not st.session_state["logged_in"]:
    st.markdown("## 🎓 Dijital Kampüs Girişi")

    with st.form("login"):
        u = st.text_input("Kullanıcı")
        p = st.text_input("Şifre", type="password")
        if st.form_submit_button("Giriş"):
            user = database.login_user(u, p)
            if user:
                st.session_state.logged_in = True
                st.session_state.username = user[1]
                st.session_state.user_role = user[3]
                st.rerun()
            else:
                st.error("Hatalı giriş")

    with st.expander("📝 Kayıt Ol"):
        with st.form("reg"):
            u = st.text_input("Yeni Kullanıcı")
            p = st.text_input("Şifre", type="password")
            st.write(st.session_state["captcha_q"])
            a = st.number_input("Cevap", step=1)
            if st.form_submit_button("Kayıt"):
                if a == st.session_state["captcha_a"]:
                    ok, _ = database.add_user(u, p, "student")
                    if ok:
                        st.success("Kayıt başarılı")
                    else:
                        st.error("İsim alınmış")
                else:
                    st.error("Yanlış cevap")

# --------------------------------------------------
# MAIN APP
# --------------------------------------------------
else:
    with st.sidebar:
        st.markdown(get_user_display_html(st.session_state["username"]), unsafe_allow_html=True)
        st.divider()
        if st.button("🚪 Çıkış"):
            st.session_state.logged_in = False
            st.rerun()

    menu = [
        "📢 Kampüs Duvar",
        "💬 Mesaj",
        "🏆 Puan",
        "📚 Ders",
        "🎮 Oyun",
        "🛒 Mağaza",
    ]
    if st.session_state["user_role"] == "admin":
        menu.append("⚙️ Admin")

    sel = st.radio("Menü", menu, horizontal=True)
    st.session_state.active_menu = sel

    # --------------------------------------------------
    if sel == "📢 Kampüs Duvar":
        st.header("Kampüs Duvar")
        for p in database.get_posts(10):
            st.markdown(f"**{p[1]}**: {p[2]}")

    # --------------------------------------------------
    elif sel == "💬 Mesaj":
        st.header("Mesajlar")
        st.info("Mesaj sistemi hazır")

    # --------------------------------------------------
    elif sel == "🏆 Puan":
        st.header("Puan Tablosu")
        st.dataframe(pd.DataFrame(database.get_leaderboard_data(), columns=["Kullanıcı", "Puan"]))

    # --------------------------------------------------
    elif sel == "📚 Ders":
        EX = load_exams()
        if not EX:
            st.info("Sınav yok")
        else:
            st.json(EX)

    # --------------------------------------------------
    elif sel == "🎮 Oyun":
        st.header("🎮 Oyunlar")
        game = st.selectbox("Oyun Seç", ["Finans İmparatoru", "Asset Matrix"])
        score = database.get_total_score(st.session_state["username"])

        if game == "Finans İmparatoru":
            components.html(finance_game_html(score, st.session_state["username"]), height=400)
        else:
            components.html(matrix_game_html(st.session_state["username"]), height=400)

    # --------------------------------------------------
    elif sel == "🛒 Mağaza":
        st.header("Mağaza")
        st.info("Mağaza sistemi hazır")

    # --------------------------------------------------
    elif sel == "⚙️ Admin":
        st.header("Admin Paneli")
        users = [u[0] for u in database.get_all_users()]
        target = st.selectbox("Kullanıcı", users)
        p = st.number_input("Puan", step=100)
        if st.button("Ekle"):
            database.add_score(target, p, "Admin")
            st.success("Eklendi")