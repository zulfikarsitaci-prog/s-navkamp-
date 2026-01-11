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

# --- AYARLAR ---
st.set_page_config(page_title="Bağarası ÇPAL", page_icon="🎓", layout="wide", initial_sidebar_state="expanded")

# --- GELİŞMİŞ SINAV VERİSİ ---
def create_full_exams_json():
    data = {
      "9. Sınıf": {
        "Mesleki Gelişim Atölyesi": [
          {"type": "scenario", "text": "SENARYO 1: Mehmet Amca tarlasını telefon uygulamasıyla suluyor.", "sub_questions": [{"q": "1. Teknoloji amacı?", "a": "Verim"}, {"q": "2. Akıllı saat türü?", "a": "Giyilebilir"}], "points": 20},
          {"type": "text", "question": "3. Ofis teknolojisi (1 tane)?", "answer": "Bilgisayar", "keywords": ["bilgisayar", "yazıcı"], "points": 10},
          {"type": "test", "question": "10. Sanal asistan hangi teknolojidir?", "options": ["Blockchain", "Yapay Zeka", "Bulut", "IoT"], "answer": "Yapay Zeka", "points": 10}
        ],
        "Temel Muhasebe": [
          {"type": "calculation", "text": "KIDEM TAZMİNATI: 4 Yıl 5 Ay 18 Gün. Brüt: 30.000 TL.", "inputs": [{"label": "4 Yıllık", "correct": 120000}, {"label": "5 Aylık", "correct": 12500}, {"label": "TOPLAM", "correct": 150500}], "points": 20},
          {"type": "text", "question": "Kasa hesabı kodu?", "answer": "100", "points": 10}
        ]
      }
    }
    if not os.path.exists("exams.json"):
        with open("exams.json", "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

create_full_exams_json()

def init_state():
    defaults = {
        "logged_in": False, "user_role": None, "username": None, 
        "class_code": "GENEL", "active_menu": "📢 Kampüs Duvar", 
        "draft_content": "", "captcha_q": None, "captcha_a": None,
        "open_comments": [], "wall_mode": "Tüm Kampüs"
    }
    for k, v in defaults.items():
        if k not in st.session_state: st.session_state[k] = v

    if st.session_state['captcha_q'] is None:
        n1 = random.randint(1, 9); n2 = random.randint(1, 9)
        st.session_state['captcha_q'] = f"{n1} + {n2}"; st.session_state['captcha_a'] = n1 + n2

init_state()
database.create_database()

# --- YARDIMCI ---
def extract_youtube_link(text):
    if not text: return None
    match = re.search(r'(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/(watch\?v=|embed/|v/|live/|.+\?v=)?([^&=%\?]{11})', text)
    if match: return f"https://www.youtube.com/watch?v={match.group(6)}"
    return None

# --- CSS (MİNİMAL MAĞAZA) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@700&family=Orbitron:wght@700&family=Rye&family=Dancing+Script:wght@700&family=Metal+Mania&family=Press+Start+2P&family=Creepster&display=swap');

    .login-container { text-align: center; margin-top: 10px; }
    .login-main { font-family: 'Cinzel', serif; color: #FFD700; font-size: 1.8rem; text-shadow: 2px 2px 4px #000; font-weight: bold; }
    
    /* POST KARTI */
    .post-card { background-color: #1e293b; border: 1px solid #334155; border-radius: 8px; padding: 10px; margin-bottom: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.3); }
    .post-header { display: flex; align-items: center; border-bottom: 1px solid #334155; padding-bottom: 5px; margin-bottom: 5px; }
    .post-content { color: #e2e8f0; font-size: 0.9rem; white-space: pre-wrap; margin-bottom: 5px; }
    
    /* BUTONLAR */
    div.stButton > button { background-color: transparent !important; border: none !important; color: #94a3b8 !important; padding: 0px 2px !important; font-size: 1.1rem !important; margin-right: 10px !important; box-shadow: none !important;}
    div.stButton > button:hover { color: #FFD700 !important; transform: scale(1.1); }
    
    /* KOLON SIKIŞTIRMA VE MOBİL GRİD ZORLAMA */
    /* Bu ayar mobilde kolonların alt alta inmesini engeller ve yan yana 3 tane sığdırır */
    [data-testid="column"] {
        min-width: 0 !important;
        flex: 1 1 0 !important;
        padding: 0 2px !important; /* Çok az boşluk */
    }
    
    .comment-box { background: #0f172a; padding: 5px; border-radius: 4px; margin-top: 4px; font-size: 0.8rem; border-left: 2px solid #334155; }
    
    /* MİNİMAL MAĞAZA KARTI */
    .shop-item { 
        background: #0f172a; 
        border: 1px solid #334155; 
        border-radius: 6px; 
        padding: 4px; 
        text-align: center; 
        height: 95px; /* ÇOK KÜÇÜK */
        display: flex; 
        flex-direction: column; 
        align-items: center; 
        justify-content: space-between; 
    }
    .shop-preview { width: 30px; height: 30px; margin-bottom: 2px; display: flex; align-items: center; justify-content: center; border-radius: 50%; border: 1px solid #334155; }
    .shop-name { font-size: 0.6rem; color: #cbd5e1; font-weight: bold; margin-bottom: 1px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 100%;}
    
    /* SATIN AL BUTONU (ÖZEL HEDEFLEME) */
    div[data-testid="stVerticalBlock"] button {
        border: 1px solid #10b981 !important;
        background-color: rgba(16, 185, 129, 0.2) !important;
        color: white !important;
        font-size: 0.6rem !important;
        padding: 2px !important;
        height: 20px !important;
        width: 100%;
        border-radius: 4px !important;
    }

    /* STİLLER */
    .avatar-img { width: 35px; height: 35px; border-radius: 50%; object-fit: cover; }
    .frame-overlay { position: absolute; top: -2px; left: -2px; width: 39px; height: 39px; pointer-events: none; }
    
    .frame-Gold { border: 2px solid #FFD700; border-radius: 50%; }
    .frame-Neon { border: 2px solid #00ffff; border-radius: 50%; }
    .frame-Fire { border: 2px solid #ff4500; border-radius: 50%; }
    .frame-King { border: 3px solid #ffd700; border-radius: 50%; }
    .frame-Matrix { border: 2px dotted #00ff00; border-radius: 50%; }
    .frame-Ice { border: 2px solid #00bfff; border-radius: 50%; }
    .frame-Dark { border: 2px solid #333; border-radius: 50%; }
    .frame-Nature { border: 2px solid #2ecc71; border-radius: 50%; }

    .name-Glitch { color: #00ffff; text-shadow: 1px 0 #ff00ff; font-weight: bold; }
    .name-Fire { color: #ff4500; text-shadow: 0 0 3px #ff0000; font-weight: bold; }
    .name-Gold { background: linear-gradient(to right, #BF953F, #FCF6BA, #B38728); -webkit-background-clip: text; color: transparent; font-weight: 900; }
    .name-Neon { color: #fff; text-shadow: 0 0 5px #fff, 0 0 10px #ff00de; font-weight: bold; }
    
    .font-Cinzel { font-family: 'Cinzel', serif; } 
    .font-Orbitron { font-family: 'Orbitron', sans-serif; }
    
    .title-badge { background: #334155; color: #94a3b8; padding: 1px 4px; border-radius: 3px; font-size: 0.55rem; margin-left: 3px; }
</style>
""", unsafe_allow_html=True)

# --- GÖRSEL YARDIMCILAR ---
def get_user_display_html(username, size=40):
    ava, frame, name_style, _, font_style, title = database.get_user_styles(username)
    img_src = f"data:image/jpeg;base64,{ava}" if ava else "https://via.placeholder.com/150/CCCCCC/FFFFFF?text=U"
    f_html = f'<div class="frame-overlay frame-{frame}"></div>' if frame else ""
    classes = f"{f'name-{name_style}' if name_style else ''} {f'font-{font_style}' if font_style else ''}"
    return f'<div style="display:flex;align-items:center;"><div class="avatar-container"><img src="{img_src}" class="avatar-img">{f_html}</div><div style="margin-left:8px;"><div class="{classes}" style="font-size:0.85rem;">{username} {f"<span class='title-badge'>{title}</span>" if title else ""}</div></div></div>'

def get_post_style_css(username):
    _, _, _, post_style, font_style, _ = database.get_user_styles(username)
    return f"post-{post_style} font-{font_style}"

class SchoolServer:
    def join_or_update_student(self, c, u, p=0): 
        if p!=0: database.add_score(u, p, "Oyun")
        return database.get_total_score(u)
    def get_score(self, c, u): return database.get_total_score(u)
    def get_leaderboard(self, c):
        data = database.get_leaderboard_data()
        df = pd.DataFrame(data, columns=["Öğrenci","Puan"]) if data else pd.DataFrame(columns=["Öğrenci","Puan"])
        return df
    def buy_item(self, u, type, name, cost): return database.buy_item(u, type, name, cost)
    def send_gift(self, s, r, item, cost): return database.send_gift(s, r, item, cost)
server = SchoolServer()

# --- OYUNLAR ---
def get_finance_game_html(start, user):
    js = f"""function autoTransfer(){{let v=0;if(typeof score!=='undefined'&&score>0)v=score;else if(typeof money!=='undefined')v=Math.floor(money-startBalance);if(v<=0){{alert("Puan yok!");return;}}try{{const u=new URL(window.top.location.href);u.searchParams.set('action','transfer');u.searchParams.set('u',"{user}");u.searchParams.set('a',v);u.searchParams.set('ts',Date.now());const l=document.createElement('a');l.href=u.toString();l.target="_top";document.body.appendChild(l);l.click();}}catch(e){{alert(e.message);}}}}"""
    return f"""<!DOCTYPE html><html><head><meta name="viewport" content="width=device-width,initial-scale=1.0"><style>body{{background:#0f172a;color:#fff;font-family:sans-serif;padding:5px;text-align:center}}.card{{background:#1e293b;padding:8px;border:1px solid #475569;cursor:pointer}}.btn{{background:radial-gradient(circle,#3b82f6,#1d4ed8);width:80px;height:80px;border-radius:50%;margin:10px auto;display:flex;align-items:center;justify-content:center;font-size:30px;}}</style></head><body><div style="color:#fbbf24">💰 <span id="m">{start}</span></div><div class="btn" onclick="clk()">👆</div><button onclick="autoTransfer()" style="background:#10b981;color:white;width:100%;padding:10px;border:none;">🏦 BANKA</button><script>let money={start},startBalance={start};function clk(){{money+=1;document.getElementById('m').innerText=money.toLocaleString();}}{js}</script></body></html>"""

def get_matrix_game_html(user):
    return "Matrix Game Placeholder"

# --- ARAYÜZ ---
if not st.session_state['logged_in']:
    st.markdown('<div class="login-container"><div class="login-main">DİJİTAL GELİŞİM</div></div>', unsafe_allow_html=True)
    with st.sidebar:
        if st.button("⚠️ SİSTEMİ SIFIRLA"):
            try:
                if os.path.exists("education_platform.db"): os.remove("education_platform.db")
                st.success("Sıfırlandı!"); time.sleep(1); st.rerun()
            except: st.error("Hata.")
    with st.container():
        with st.form("login"):
            u = st.text_input("Kullanıcı")
            p = st.text_input("Şifre", type="password")
            if st.form_submit_button("Giriş"):
                user = database.login_user(u, p)
                if user:
                    st.session_state.update({'logged_in':True, 'username':user[1], 'user_role':user[3]})
                    database.update_activity(user[1])
                    st.rerun()
                else: st.error("Hatalı!")
        with st.expander("Kayıt"):
            with st.form("reg"):
                nu = st.text_input("Kullanıcı"); np = st.text_input("Şifre", type="password")
                st.write(f"Güvenlik: {st.session_state['captcha_q']} = ?")
                ans = st.number_input("Cevap", step=1)
                if st.form_submit_button("Kayıt"):
                    if ans == st.session_state['captcha_a']:
                        res, rank = database.add_user(nu, np, "student")
                        if res: st.success("Tamam!"); st.session_state['captcha_q'] = None
                        else: st.error("Dolu.")
                    else: st.error("Yanlış.")
else:
    database.update_activity(st.session_state['username'])
    with st.sidebar:
        st.markdown(get_user_display_html(st.session_state['username'], size=60), unsafe_allow_html=True)
        if st.button("Çıkış"): st.session_state['logged_in']=False; st.rerun()

    noti_count = database.get_unread_notification_count(st.session_state['username'])
    noti_text = f"🔔({noti_count})" if noti_count > 0 else "🔔"
    menu = ["Duvar", "Mesaj", "Puan", "Ders", "Oyun", "Mağaza", noti_text]
    if st.session_state['user_role'] == 'admin': menu.append("Admin")
    
    sel = st.radio("", menu, horizontal=True, label_visibility="collapsed")

    if sel == "Duvar":
        st.session_state['wall_mode'] = st.selectbox("", ["Tüm Kampüs", "Benim Profilim"], label_visibility="collapsed")
        
        if database.get_total_score(st.session_state['username']) >= 1000000 or st.session_state['user_role'] == 'admin':
            with st.expander("Paylaş", expanded=False):
                with st.form("sh"):
                    txt = st.text_area("İçerik")
                    img = st.file_uploader("Resim", type=['png','jpg'])
                    if st.form_submit_button("Gönder"):
                        database.add_score(st.session_state['username'], -100000, "Post")
                        database.add_post(st.session_state['username'], txt, img)
                        st.rerun()
        
        all_posts = database.get_posts(50)
        posts = [p for p in all_posts if p[1] == st.session_state['username']] if st.session_state['wall_mode'] == "Benim Profilim" else all_posts

        for p in posts:
            st.markdown(f"""
            <div class="post-card">
                <div class="post-header">{get_user_display_html(p[1], size=30)}<small style="margin-left:auto;color:#888">{p[4]}</small></div>
                <div class="{get_post_style_css(p[1])} post-content">{p[2] if p[2] else ''}</div>
                {f'<img src="data:image/jpeg;base64,{p[3]}" class="post-image" style="width:100%;border-radius:5px;">' if p[3] else ''}
            </div>""", unsafe_allow_html=True)
            if p[2]:
                yt = extract_youtube_link(p[2])
                if yt: st.video(yt)

            c1, c2, c3, c4 = st.columns([1,1,1,4])
            with c1: 
                if st.button(f"❤️ {p[5]}", key=f"l_{p[0]}"): database.like_post(p[0]); st.rerun()
            with c2: 
                if st.button("💬", key=f"c_btn_{p[0]}"):
                    if p[0] in st.session_state['open_comments']: st.session_state['open_comments'].remove(p[0])
                    else: st.session_state['open_comments'].append(p[0])
                    st.rerun()
            with c3:
                if st.button("🔄", key=f"r_{p[0]}"): st.toast("Alıntılandı")
            
            if p[0] in st.session_state['open_comments']:
                coms = database.get_comments(p[0])
                for c in coms: st.markdown(f"<div class='comment-box'><b>{c[0]}</b>: {c[1]}</div>", unsafe_allow_html=True)
                with st.form(f"c_form_{p[0]}", clear_on_submit=True):
                    ct = st.text_input("Yorum", label_visibility="collapsed")
                    if st.form_submit_button("Yaz"): 
                        if ct: database.add_comment(p[0], st.session_state['username'], ct); st.rerun()

    elif sel == "Mağaza":
        st.header(f"💎 {database.get_total_score(st.session_state['username']):,} P")
        tabs = st.tabs(["Çerçeve", "İsim", "Font", "Hediye"])
        
        # --- KOMPAKT MAĞAZA FONKSİYONU ---
        def render_shop_tab(items, type_key):
            # Mobilde 3, PC'de 4 kolon olması için st.columns(3) veya 4 kullanıyoruz
            # Ama CSS ile genişlikleri eziyoruz.
            rows = [items[i:i+3] for i in range(0, len(items), 3)]
            for row in rows:
                cols = st.columns(3)
                for i, it in enumerate(row):
                    with cols[i]:
                        preview = f'<div class="shop-preview"><div class="{it.get("css", "")}" style="width:100%;height:100%;border-radius:50%;"></div></div>' if type_key == "frame" else f'<div style="font-size:0.8rem;margin-bottom:5px;">Aa</div>'
                        st.markdown(f'<div class="shop-item">{preview}<div class="shop-name">{it["n"]}</div></div>', unsafe_allow_html=True)
                        if st.button(f"{it['c']//1000}K", key=f"buy_{type_key}_{it['n']}"):
                            ok, msg = database.buy_item(st.session_state['username'], it['t'], it['v'], it['c'])
                            if ok: st.success("Aldın!"); time.sleep(1); st.rerun()
                            else: st.error("Para yok")

        with tabs[0]:
            items = [{"n":"Gold","c":50000,"t":"frame","v":"Gold","css":"frame-Gold"}, {"n":"Neon","c":150000,"t":"frame","v":"Neon","css":"frame-Neon"}, {"n":"Alev","c":300000,"t":"frame","v":"Fire","css":"frame-Fire"}, {"n":"Kral","c":2000000,"t":"frame","v":"King","css":"frame-King"}, {"n":"Buz","c":750000,"t":"frame","v":"Ice","css":"frame-Ice"}, {"n":"Doğa","c":250000,"t":"frame","v":"Nature","css":"frame-Nature"}]
            render_shop_tab(items, "frame")

        with tabs[1]:
            items = [{"n":"Glitch","c":100000,"t":"name","v":"Glitch"}, {"n":"Neon","c":500000,"t":"name","v":"Neon"}, {"n":"Gold","c":750000,"t":"name","v":"Gold"}]
            render_shop_tab(items, "name")

        with tabs[3]: # Hediye
            st.info("Hediye Gönder")
            u_list = database.get_all_users_list(st.session_state['username'])
            tgt = st.selectbox("Kime", u_list)
            gifts = [{"n":"Kahve","c":5000}, {"n":"Gül","c":25000}, {"n":"Araba","c":500000}]
            rows = [gifts[i:i+3] for i in range(0, len(gifts), 3)]
            for row in rows:
                cols = st.columns(3)
                for i, g in enumerate(row):
                    with cols[i]:
                        st.markdown(f'<div class="shop-item"><div class="shop-name">{g["n"]}</div></div>', unsafe_allow_html=True)
                        if st.button(f"{g['c']//1000}K", key=f"g_{g['n']}"):
                            database.send_gift(st.session_state['username'], tgt, g['n'], g['c'])
                            st.success("Gitti!")

    elif sel == "Mesaj":
        st.subheader("Mesajlar")
        fr = database.get_friends(st.session_state['username'])
        tgt = st.selectbox("Kişi", fr) if fr else None
        if tgt:
            msgs = database.get_conversation(st.session_state['username'], tgt)
            for m in msgs:
                align = "row-reverse" if m[0]==st.session_state['username'] else "row"
                bg = "#2563eb" if m[0]==st.session_state['username'] else "#334155"
                st.markdown(f"<div style='display:flex;flex-direction:{align};margin-bottom:5px'><div style='background:{bg};padding:5px 10px;border-radius:10px;font-size:0.9rem'>{m[1]}</div></div>", unsafe_allow_html=True)
            with st.form("mf", clear_on_submit=True):
                if st.form_submit_button("Yolla"):
                    mt = st.session_state.get('msg_val') # Streamlit form trick needed usually, but keeping simple
                    pass # Simplified for space, use chat_input in real usage
            if txt:=st.chat_input("Yaz"): database.send_message(st.session_state['username'], tgt, txt); st.rerun()
        else: st.info("Arkadaş yok.")

    elif sel == "Puan":
        st.dataframe(server.get_leaderboard("GENEL"), use_container_width=True)

    elif sel == "Ders":
        EX = load_local_exams()
        if EX:
            c = st.selectbox("Sınıf", list(EX.keys())); l = st.selectbox("Ders", list(EX[c].keys()))
            with st.form("ex"):
                for i, q in enumerate(EX[c][l]):
                    st.write(f"{i+1}. {q.get('question') or q.get('text')}")
                    if q.get('options'): st.radio("Cevap", q['options'], key=f"q{i}")
                    else: st.text_input("Cevap", key=f"q{i}")
                if st.form_submit_button("Bitir"):
                    database.add_score(st.session_state['username'], 50, "Sınav"); st.success("Puan eklendi!"); time.sleep(1); st.rerun()

    elif sel.startswith("🔔"):
        database.mark_notifications_read(st.session_state['username']); st.success("Bildirimler okundu.")
