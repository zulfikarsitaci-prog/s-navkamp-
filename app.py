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

# ✅ CSS ARTIK DIŞARIDA
from core.styles import load_css

# ✅ OYUNLAR ARTIK DIŞARIDA
from games.finance_game import get_finance_game_html
from games.matrix_game import get_matrix_game_html


# --------------------------------------------------
# AYARLAR
# --------------------------------------------------
st.set_page_config(
    page_title="Bağarası ÇPAL",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

load_css()


# --------------------------------------------------
# STATE
# --------------------------------------------------
def init_state():
    defaults = {
        "logged_in": False,
        "user_role": None,
        "username": None,
        "class_code": "GENEL",
        "active_menu": "📢 Kampüs Duvar",
        "draft_content": "",
        "captcha_q": None,
        "captcha_a": None,
        "open_comments": []
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

    if st.session_state["captcha_q"] is None:
        n1, n2 = random.randint(1, 9), random.randint(1, 9)
        st.session_state["captcha_q"] = f"{n1} + {n2}"
        st.session_state["captcha_a"] = n1 + n2


init_state()


# --------------------------------------------------
# YARDIMCILAR
# --------------------------------------------------
def extract_youtube_link(text):
    if not text:
        return None
    match = re.search(
        r'(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/(watch\?v=|embed/|v/|live/|.+\?v=)?([^&=%\?]{11})',
        text
    )
    if match:
        return f"https://www.youtube.com/watch?v={match.group(6)}"
    return None


# ✅ OYUNLARIN PUAN AKTARMASI İÇİN TEK JS
def get_transfer_js(username):
    return f"""
    <script>
    function transferScore(amount, reason) {{
        window.parent.postMessage({{
            type: "TRANSFER_SCORE",
            user: "{username}",
            amount: amount,
            reason: reason
        }}, "*");
    }}
    </script>
    """


# --------------------------------------------------
# VERİTABANI
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
# GÖRSEL YARDIMCILAR
# --------------------------------------------------
def get_user_display_html(username, size=40):
    ava, frame, name_style, _, font_style, title = database.get_user_styles(username)
    img_src = (
        f"data:image/jpeg;base64,{ava}"
        if ava else "https://via.placeholder.com/150/CCCCCC/FFFFFF?text=U"
    )
    f_html = f'<div class="frame-overlay frame-{frame}"></div>' if frame else ""
    classes = f"{f'name-{name_style}' if name_style else ''} {f'font-{font_style}' if font_style else ''}"
    return f"""
    <div style="display:flex;align-items:center;">
        <div class="avatar-container">
            <img src="{img_src}" class="avatar-img">
            {f_html}
        </div>
        <div style="margin-left:10px;">
            <div class="{classes}" style="font-size:0.9rem;">
                {username}
                {f"<span class='title-badge'>{title}</span>" if title else ""}
            </div>
        </div>
    </div>
    """


def get_post_style_css(username):
    _, _, _, post_style, font_style, _ = database.get_user_styles(username)
    return f"post-{post_style} font-{font_style}"


# --------------------------------------------------
# SCHOOL SERVER (AYNI)
# --------------------------------------------------
class SchoolServer:
    def join_or_update_student(self, c, u, p=0):
        if p != 0:
            database.add_score(u, p, "Oyun")
        return database.get_total_score(u)

    def get_score(self, c, u):
        return database.get_total_score(u)

    def get_leaderboard(self, c):
        df = pd.DataFrame(
            database.get_leaderboard_data(),
            columns=["Öğrenci", "Puan"]
        )
        return df if not df.empty else pd.DataFrame(columns=["Öğrenci", "Puan"])

    def buy_item(self, u, type, name, cost):
        return database.buy_item(u, type, name, cost)

    def send_gift(self, s, r, item, cost):
        return database.send_gift(s, r, item, cost)


server = SchoolServer()


# --------------------------------------------------
# SINAVLAR (AYNI)
# --------------------------------------------------
@st.cache_data
def load_local_exams():
    if os.path.exists("exams.json"):
        try:
            return json.load(open("exams.json", "r", encoding="utf-8"))
        except:
            return {}
    return {}


# --------------------------------------------------
# ⬇⬇⬇⬇⬇⬇⬇⬇⬇⬇⬇⬇⬇⬇⬇⬇⬇⬇
# BURADAN SONRASI
# SENİN ORİJİNAL KODUNLA AYNI
# (LOGIN, DUVAR, MAĞAZA, MESAJ, ADMIN)
# SADECE 🎮 OYUN KISMI GÜNCELLENDİ
# ⬆⬆⬆⬆⬆⬆⬆⬆⬆⬆⬆⬆⬆⬆⬆⬆⬆⬆


# --------------------------------------------------
# 🎮 OYUN (GÜNCELLENMİŞ)
# --------------------------------------------------
elif sel == "🎮 Oyun":
    gm = st.selectbox("Oyun Seç", ["Finans İmparatoru", "Matrix"])
    sc = server.get_score("GENEL", st.session_state["username"])

    if gm == "Finans İmparatoru":
        components.html(
            get_finance_game_html(
                sc,
                st.session_state["username"],
                get_transfer_js
            ),
            height=600,
            scrolling=True
        )

    elif gm == "Matrix":
        components.html(
            get_matrix_game_html(
                st.session_state["username"],
                get_transfer_js
            ),
            height=750,
            scrolling=True
        )