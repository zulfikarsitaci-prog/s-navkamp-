from datetime import datetime
import streamlit as st
from .core import run_query
# Not: Burada users.py import edersek döngüsel bağımlılık olabilir, get_user_styles orada.
# Bu yüzden styles cache temizlemeyi users modülünden çağırmak yerine app.py cache.clear() yaparız veya burada sadece query çalıştırırız.

@st.cache_data(ttl=30)
def get_leaderboard_data(): return run_query("SELECT student_username, SUM(grade) as total FROM grades GROUP BY student_username ORDER BY total DESC", fetch=True) or []

@st.cache_data(ttl=3)
def get_total_score(u):
    res = run_query("SELECT SUM(grade) FROM grades WHERE student_username = ?", (u,), fetch=True)
    return res[0][0] if res and res[0][0] else 0

def add_score(u, a, s="Sistem"):
    d = datetime.now().strftime("%Y-%m-%d %H:%M")
    run_query("INSERT INTO grades (student_username, lesson, grade, date) VALUES (?, ?, ?, ?)", (u, s, a, d))
    get_total_score.clear(u); get_leaderboard_data.clear()

def buy_item(u, type, value, cost):
    current = get_total_score(u)
    if current >= cost:
        add_score(u, -cost, f"Mağaza: {value}")
        col = ""
        if type == "frame": col = "frame"
        elif type == "name": col = "name_style"
        elif type == "post": col = "post_style"
        elif type == "font": col = "font_style"
        elif type == "title": col = "title"
        if col:
            run_query(f"UPDATE users SET {col} = ? WHERE username = ?", (value, u))
            # get_user_styles cache'i app tarafında temizlenmeli veya users.py'dan import edilmeli (dikkatli olunmalı)
            from .users import get_user_styles
            get_user_styles.clear(u)
            return True, "Hayırlı olsun!"
    return False, "Puan yetersiz."

def send_gift(sender, receiver, gift_name, cost):
    from .social import send_message
    current = get_total_score(sender)
    if current >= cost:
        add_score(sender, -cost, f"Hediye: {gift_name} -> {receiver}")
        msg_text = f"🎁 SANA BİR HEDİYE GÖNDERDİ: {gift_name}!"
        send_message(sender, receiver, msg_text)
        return True, "Hediye gönderildi!"
    return False, "Puan yetersiz."
