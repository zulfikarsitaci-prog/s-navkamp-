import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import json, os, time, random, re
from datetime import datetime
import database

# -------------------------------------------------
# AYARLAR
# -------------------------------------------------
st.set_page_config(
    page_title="Bağarası ÇPAL",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -------------------------------------------------
# SESSION STATE
# -------------------------------------------------
def init_state():
    defaults = {
        "logged_in": False,
        "user_role": None,
        "username": None,
        "active_menu": "📢 Kampüs Duvar",
        "captcha_q": None,
        "captcha_a": None
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

    if st.session_state["captcha_q"] is None:
        a, b = random.randint(1, 9), random.randint(1, 9)
        st.session_state["captcha_q"] = f"{a} + {b}"
        st.session_state["captcha_a"] = a + b

init_state()

# -------------------------------------------------
# VERİTABANI
# -------------------------------------------------
database.create_database()
if not database.login_user("admin", "6626"):
    database.add_user("admin", "6626", "admin")

# -------------------------------------------------
# YARDIMCI
# -------------------------------------------------
def get_transfer_js(username):
    return f"""
    function autoTransfer(){{
        let val = typeof score !== 'undefined' ? score : 0;
        if(val<=0){{ alert("Puan yok"); return; }}
        const u=new URL(window.top.location.href);
        u.searchParams.set("action","transfer");
        u.searchParams.set("u","{username}");
        u.searchParams.set("a",val);
        window.top.location.href=u.toString();
    }}
    """

# -------------------------------------------------
# OYUNLAR (ÇALIŞAN)
# -------------------------------------------------
def get_finance_game_html(start, user):
    js = get_transfer_js(user)
    return f"""
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>
body{{background:#0f172a;color:white;text-align:center;font-family:sans-serif}}
.btn{{width:90px;height:90px;border-radius:50%;background:#3b82f6;
display:flex;align-items:center;justify-content:center;font-size:32px;margin:20px auto;cursor:pointer}}
.bank{{background:#10b981;color:white;border:none;padding:12px 20px;border-radius:10px}}
</style>
</head>
<body>
<h2>💰 <span id="m">{start}</span></h2>
<div class="btn" onclick="money+=1;upd()">👆</div>
<button class="bank" onclick="autoTransfer()">🏦 Bankaya Aktar</button>

<script>
let money={start};
let score=0;
function upd(){{
  document.getElementById("m").innerText=money;
  score=money;
}}
{js}
</script>
</body>
</html>
"""

def get_matrix_game_html(user):
    js = get_transfer_js(user)
    return f"""
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>
body{{background:black;color:#00ffff;text-align:center}}
canvas{{border:2px solid #00ffff;margin-top:10px}}
</style>
</head>
<body>
<h3>PUAN: <span id="s">0</span></h3>
<button onclick="autoTransfer()">AKTAR</button>
<canvas id="c" width="300" height="300"></canvas>

<script>
let score=0;
const ctx=document.getElementById("c").getContext("2d");
ctx.fillStyle="#00ffff";
ctx.fillRect(100,100,50,50);
score=100;
document.getElementById("s").innerText=score;
{js}
</script>
</body>
</html>
"""

# -------------------------------------------------
# GİRİŞ
# -------------------------------------------------
if not st.session_state["logged_in"]:
    st.title("🎓 Dijital Kampüs")

    with st.form("login"):
        u = st.text_input("Kullanıcı")
        p = st.text_input("Şifre", type="password")
        if st.form_submit_button("Giriş"):
            user = database.login_user(u, p)
            if user:
                st.session_state.update(
                    logged_in=True,
                    username=user[1],
                    user_role=user[3]
                )
                st.rerun()
            else:
                st.error("Hatalı giriş")

    with st.expander("Kayıt Ol"):
        nu = st.text_input("Yeni Kullanıcı")
        np = st.text_input("Şifre", type="password")
        st.write("Güvenlik:", st.session_state["captcha_q"])
        ca = st.number_input("Cevap", step=1)
        if st.button("Kayıt"):
            if ca == st.session_state["captcha_a"]:
                ok, _ = database.add_user(nu, np, "student")
                if ok:
                    st.success("Kayıt tamam")
                else:
                    st.error("İsim alınmış")
            else:
                st.error("Yanlış cevap")

    st.stop()

# -------------------------------------------------
# MENÜ
# -------------------------------------------------
menu = ["📢 Kampüs Duvar", "🎮 Oyun", "🏆 Puan"]
sel = st.radio("Menü", menu, horizontal=True)

# -------------------------------------------------
# SAYFALAR
# -------------------------------------------------
if sel == "📢 Kampüs Duvar":
    st.header("Kampüs Duvar")
    st.info("Duvar içeriği burada")

elif sel == "🎮 Oyun":
    st.header("🎮 Oyunlar")

    game = st.selectbox("Oyun Seç", ["Finans İmparatoru", "Asset Matrix"])
    score = database.get_total_score(st.session_state["username"])

    if game == "Finans İmparatoru":
        components.html(
            get_finance_game_html(score, st.session_state["username"]),
            height=500
        )
    else:
        components.html(
            get_matrix_game_html(st.session_state["username"]),
            height=500
        )

elif sel == "🏆 Puan":
    st.metric("Puan", database.get_total_score(st.session_state["username"]))

# -------------------------------------------------
# TRANSFER
# -------------------------------------------------
if "action" in st.query_params:
    if st.query_params["action"] == "transfer":
        u = st.query_params["u"]
        a = int(st.query_params["a"])
        database.add_score(u, a, "Oyun")
        st.success(f"{a} puan eklendi")
        st.query_params.clear()
        time.sleep(1)
        st.rerun()