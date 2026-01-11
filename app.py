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

# ✅ YENİ: GLOBAL CSS
from core.styles import load_css

# --- AYARLAR ---
st.set_page_config(
    page_title="Bağarası ÇPAL",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ✅ YENİ: CSS YÜKLE
load_css()

def init_state():
    defaults = {
        "logged_in": False, "user_role": None, "username": None,
        "class_code": "GENEL", "active_menu": "📢 Kampüs Duvar",
        "draft_content": "",
        "captcha_q": None, "captcha_a": None,
        "open_comments": []
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

    if st.session_state['captcha_q'] is None:
        n1 = random.randint(1, 9)
        n2 = random.randint(1, 9)
        st.session_state['captcha_q'] = f"{n1} + {n2}"
        st.session_state['captcha_a'] = n1 + n2

init_state()

# --- YARDIMCI: GELİŞMİŞ YOUTUBE LİNKİ ---
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

# --- VERİTABANI ---
try:
    database.create_database()
    if not database.login_user("admin", "6626"):
        database.add_user("admin", "6626", "admin")
except:
    pass

if st.session_state['logged_in']:
    database.update_activity(st.session_state['username'])

# --- GÖRSEL YARDIMCILAR ---
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
# ⬇⬇⬇ BURADAN SONRASI
# SENİN GÖNDERDİĞİN KODLA AYNI
# (OYUNLAR, MAĞAZA, DUVAR, MESAJ, ADMIN VS.)
# --------------------------------------------------

# ⛔ BURAYA KADAR OKUMAN YETERLİ
# ⛔ ALT KISIMDA HİÇBİR ŞEY DEĞİŞMED