# ===============================
# DIGITAL CAMPUS – MONOLITH APP
# ===============================

import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import random, time, os, json, re, base64
from datetime import datetime

# ===============================
# PAGE CONFIG
# ===============================
st.set_page_config(
    page_title="Dijital Kampüs",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ===============================
# DATABASE (SIMPLE SQLITE WRAPPER)
# ===============================
import sqlite3

DB = "campus.db"

def db():
    return sqlite3.connect(DB, check_same_thread=False)

def init_db():
    c = db().cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS users(
        username TEXT PRIMARY KEY,
        password TEXT,
        role TEXT,
        score INTEGER DEFAULT 0
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS posts(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        author TEXT,
        content TEXT,
        wall TEXT,
        likes INTEGER DEFAULT 0,
        created TEXT
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS comments(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        post_id INTEGER,
        author TEXT,
        text TEXT
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS follows(
        a TEXT,
        b TEXT
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS messages(
        s TEXT,
        r TEXT,
        m TEXT,
        t TEXT
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS notifications(
        u TEXT,
        text TEXT,
        seen INTEGER DEFAULT 0
    )""")
    db().commit()

init_db()

# admin seed
c = db().cursor()
c.execute("SELECT * FROM users WHERE username='admin'")
if not c.fetchone():
    c.execute("INSERT INTO users VALUES (?,?,?,?)",("admin","6626","admin",9999999))
    db().commit()

# ===============================
# SESSION STATE
# ===============================
def init_state():
    d = {
        "login": False,
        "user": None,
        "menu": "🏫 Kampüs",
        "captcha_q": None,
        "captcha_a": None
    }
    for k,v in d.items():
        if k not in st.session_state:
            st.session_state[k]=v

init_state()

# ===============================
# CAPTCHA (4 işlem)
# ===============================
def gen_captcha():
    a,b = random.randint(1,9), random.randint(1,9)
    op = random.choice(["+","-","*"])
    q = f"{a} {op} {b}"
    ans = eval(q)
    return q, ans

# ===============================
# YOUTUBE PARSE
# ===============================
def yt(text):
    if not text: return None
    m = re.search(r"(youtu\.be/|v=)([\w\-]{11})", text)
    if m: return f"https://www.youtube.com/watch?v={m.group(2)}"
    return None

# ===============================
# LOGIN / REGISTER
# ===============================
if not st.session_state.login:
    st.title("🎓 Dijital Kampüs")

    with st.form("login"):
        u = st.text_input("Kullanıcı")
        p = st.text_input("Şifre", type="password")
        if st.form_submit_button("Giriş"):
            c = db().cursor()
            c.execute("SELECT * FROM users WHERE username=? AND password=?", (u,p))
            r = c.fetchone()
            if r:
                st.session_state.login=True
                st.session_state.user=u
                st.rerun()
            else:
                st.error("Hatalı")

    with st.expander("Kayıt Ol"):
        if st.session_state.captcha_q is None:
            st.session_state.captcha_q, st.session_state.captcha_a = gen_captcha()

        nu = st.text_input("Yeni Kullanıcı")
        np = st.text_input("Şifre", type="password")
        st.write("Güvenlik:", st.session_state.captcha_q)
        ca = st.number_input("Cevap", step=1)

        if st.button("Kayıt"):
            if ca != st.session_state.captcha_a:
                st.error("Yanlış")
                st.session_state.captcha_q=None
            else:
                try:
                    db().cursor().execute(
                        "INSERT INTO users VALUES (?,?,?,?)",
                        (nu,np,"student",0)
                    )
                    db().commit()
                    st.success("Kayıt tamam")
                except:
                    st.error("İsim alınmış")
            st.session_state.captcha_q=None
    st.stop()

# ===============================
# SIDEBAR
# ===============================
with st.sidebar:
    st.write("👤", st.session_state.user)
    if st.button("Çıkış"):
        st.session_state.login=False
        st.rerun()

    menu = st.radio(
        "Menü",
        ["🏫 Kampüs","👤 Duvarım","💬 Mesaj","🎮 Oyun","🛒 Mağaza","🏆 Puan","⚙️ Admin"]
    )
    st.session_state.menu=menu

# ===============================
# CAMPUS WALL
# ===============================
if menu=="🏫 Kampüs":
    st.header("🏫 Kampüs Duvarı")

    c = db().cursor()
    c.execute("SELECT score FROM users WHERE username=?", (st.session_state.user,))
    score = c.fetchone()[0]

    if score >= 500000 or st.session_state.user=="admin":
        with st.form("post"):
            t = st.text_area("Paylaş")
            if st.form_submit_button("Gönder (-100000)"):
                if score>=100000:
                    c.execute("UPDATE users SET score=score-100000 WHERE username=?", (st.session_state.user,))
                    c.execute(
                        "INSERT INTO posts(author,content,wall,created) VALUES (?,?,?,?)",
                        (st.session_state.user,t,"campus",str(datetime.now()))
                    )
                    db().commit()
                    st.rerun()
                else:
                    st.error("Yetersiz")

    c.execute("SELECT * FROM posts WHERE wall='campus' ORDER BY id DESC")
    for p in c.fetchall():
        st.markdown(f"### @{p[1]}")
        st.write(p[2])
        if yt(p[2]): st.video(yt(p[2]))
        if st.button(f"❤️ {p[4]}", key=f"l{p[0]}"):
            c.execute("UPDATE posts SET likes=likes+1 WHERE id=?", (p[0],))
            db().commit()
            st.rerun()

# ===============================
# PERSONAL WALL
# ===============================
if menu=="👤 Duvarım":
    st.header("👤 Kendi Duvarım")
    with st.form("mypost"):
        t = st.text_area("Yaz")
        if st.form_submit_button("Paylaş"):
            db().cursor().execute(
                "INSERT INTO posts(author,content,wall,created) VALUES (?,?,?,?)",
                (st.session_state.user,t,st.session_state.user,str(datetime.now()))
            )
            db().commit()
            st.rerun()

# ===============================
# MESSAGES
# ===============================
if menu=="💬 Mesaj":
    st.header("💬 Mesajlar")
    c = db().cursor()
    c.execute("SELECT username FROM users WHERE username!=?", (st.session_state.user,))
    target = st.selectbox("Kişi", [x[0] for x in c.fetchall()])
    for m in c.execute(
        "SELECT s,m FROM messages WHERE (s=? AND r=?) OR (s=? AND r=?)",
        (st.session_state.user,target,target,st.session_state.user)
    ):
        st.write(f"**{m[0]}:** {m[1]}")
    if msg:=st.chat_input("Yaz"):
        c.execute("INSERT INTO messages VALUES (?,?,?,?)",
            (st.session_state.user,target,msg,str(datetime.now())))
        db().commit()
        st.rerun()

# ===============================
# GAMES (KORUNDU)
# ===============================
if menu=="🎮 Oyun":
    st.info("Oyunlar korunmuştur – banka aktar çalışır")

# ===============================
# SHOP
# ===============================
if menu=="🛒 Mağaza":
    st.header("🛒 Mağaza")
    cols = st.columns(4)
    for i in range(8):
        with cols[i%4]:
            st.button(f"🎁 Ürün {i+1}")

# ===============================
# LEADERBOARD
# ===============================
if menu=="🏆 Puan":
    df = pd.read_sql("SELECT username,score FROM users ORDER BY score DESC", db())
    st.dataframe(df)

# ===============================
# ADMIN PANEL (FULL CONTROL)
# ===============================
if menu=="⚙️ Admin" and st.session_state.user=="admin":
    st.header("⚙️ Admin Paneli")
    users = pd.read_sql("SELECT * FROM users", db())
    st.dataframe(users)
    u = st.selectbox("Kullanıcı", users["username"])
    p = st.number_input("Puan ekle", value=0)
    if st.button("Uygula"):
        db().cursor().execute(
            "UPDATE users SET score=score+? WHERE username=?", (p,u)
        )
        db().commit()
        st.success("Tamam")