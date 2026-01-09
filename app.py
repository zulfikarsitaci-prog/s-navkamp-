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
from datetime import datetime

# ==========================================
# 1. SAYFA VE STİL
# ==========================================
st.set_page_config(
    page_title="Bağarası ÇPAL - Dijital Kampüs",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- DEVLET (STATE) ---
def init_state():
    defaults = {"logged_in": False, "user_role": None, "username": None, "class_code": "GENEL"}
    for key, val in defaults.items():
        if key not in st.session_state: st.session_state[key] = val
init_state()

# --- CSS ---
st.markdown("""
<style>
    .login-container { display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center; margin-top: 50px; }
    .login-title { font-family: 'Helvetica', sans-serif; font-size: 2.2rem; font-weight: 700; color: #FFD700; text-shadow: 0 0 10px rgba(0,0,0,0.5); margin-bottom: 20px; }
    div[data-testid="stSidebar"] button { width: 100%; border-radius: 8px; padding: 12px 15px; font-weight: bold; transition: all 0.3s; border: 1px solid rgba(255,255,255,0.1); margin-bottom: 5px; font-size: 1rem; }
    div[data-testid="stSidebar"] button:first-of-type { background-color: #2563eb; color: white; } 
    div[data-testid="stSidebar"] button:last-of-type { background-color: #dc2626; color: white; margin-top: 20px; } 
    .top-bar { background-color: #1e293b; padding: 10px 15px; border-radius: 8px; display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px; border-bottom: 2px solid #FFD700; }
    .user-greeting { font-size: 1rem; font-weight: bold; color: #e2e8f0; }
    .role-badge { background: #FFD700; color: #000; padding: 3px 10px; border-radius: 4px; font-size: 0.75rem; font-weight: 900; }
    .chat-bubble-me { background-color: #2563eb; color: white; padding: 10px; border-radius: 15px 15px 0 15px; margin: 5px; text-align: right; float: right; clear: both; max-width: 70%; }
    .chat-bubble-other { background-color: #334155; color: white; padding: 10px; border-radius: 15px 15px 15px 0; margin: 5px; text-align: left; float: left; clear: both; max-width: 70%; }
    .post-card { background-color: #1e293b; padding: 15px; border-radius: 10px; margin-bottom: 15px; border: 1px solid #334155; }
    iframe { width: 100% !important; }
</style>
""", unsafe_allow_html=True)

# Veritabanı
database.create_database()
if not database.login_user("admin", "6626"): database.add_user("admin", "6626", "admin")
if st.session_state['logged_in'] and st.session_state['username']: database.update_activity(st.session_state['username'])

# ==========================================
# 2. SERVER & YARDIMCILAR
# ==========================================
class SchoolServer:
    def __init__(self): pass
    def join_or_update_student(self, c, u, p=0): 
        if p!=0: database.add_score(u, p, "Oyun")
        return database.get_total_score(u)
    def get_score(self, c, u): return database.get_total_score(u)
    def get_leaderboard(self, c):
        conn, db = database.get_db_connection()
        try:
            df = pd.read_sql_query("SELECT student_username, SUM(grade) as total FROM grades GROUP BY student_username ORDER BY total DESC", conn)
            conn.close()
            if not df.empty: df.columns=["Öğrenci","Puan"]; return df
        except: conn.close()
        return pd.DataFrame(columns=["Öğrenci","Puan"])
    def get_active_students_in_class(self, c): return []

server = SchoolServer()

@st.cache_data
def load_meslek_sorular():
    URL = "https://raw.githubusercontent.com/zulfikarsitaci-prog/s-navkamp-/main/sorular.json"
    try: return requests.get(URL).json()
    except: return {}

@st.cache_data
def load_local_exams():
    if os.path.exists("exams.json"):
        try:
            with open("exams.json", "r", encoding="utf-8") as f: return json.load(f)
        except: return {}
    return {}

# --- YENİ LIFESIM (Gelişmiş Sokratik Mod) ---
def get_lifesim_html():
    return """
<!DOCTYPE html>
<html lang="tr">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>
body { background:#0f172a; color:#e2e8f0; font-family:sans-serif; padding:20px; text-align:center; }
.card { background:#1e293b; padding:20px; border-radius:15px; border:1px solid #334155; max-width:500px; margin:0 auto; box-shadow:0 10px 25px rgba(0,0,0,0.5); }
.btn { display:block; width:100%; padding:15px; margin:10px 0; border:none; border-radius:8px; font-size:16px; cursor:pointer; transition:0.2s; font-weight:bold; }
.btn-a { background:#3b82f6; color:white; } .btn-a:hover { background:#2563eb; }
.btn-b { background:#ef4444; color:white; } .btn-b:hover { background:#dc2626; }
.stats { display:flex; justify-content:space-around; margin-bottom:20px; font-size:14px; font-weight:bold; color:#facc15; }
.ai-msg { font-style:italic; color:#94a3b8; margin-top:15px; font-size:13px; border-top:1px solid #334155; padding-top:10px; }
</style>
</head>
<body>
<div class="card">
    <div class="stats">
        <span>💰 Para: <span id="money">1000</span> TL</span>
        <span>❤️ Sağlık: <span id="health">100</span></span>
        <span>🧠 Bilgi: <span id="know">0</span></span>
    </div>
    <h2 id="q-title" style="color:#FFD700;">Girişimci Ruhu</h2>
    <p id="q-text" style="font-size:18px; line-height:1.5;">Okul bitti. Cebinde biriktirdiğin 1000 TL var. Ne yapacaksın?</p>
    <div id="choices">
        <button class="btn btn-a" onclick="choose(1)">Küçük bir e-ticaret sitesi kur (-500 TL)</button>
        <button class="btn btn-b" onclick="choose(2)">Parayı faize yatırıp bekle (+50 TL)</button>
    </div>
    <div id="ai-feedback" class="ai-msg">Sokrat: "Başlamak için en iyi zaman şimdidir, peki risk almaya hazır mısın?"</div>
</div>
<script>
let state = { m:1000, h:100, k:0, step:0 };
const scenarios = [
    { t:"Girişimci Ruhu", q:"Okul bitti. Cebinde 1000 TL var. Ne yapacaksın?", 
      a:{txt:"E-Ticaret Sitesi Kur (-500 TL)", m:-500, k:20, nxt:1, ai:"Risk aldın! Ticaret cesaret ister. Müşteri bulmak için ne yapacaksın?"}, 
      b:{txt:"Parayı Faize Yatır (+50 TL)", m:50, k:0, nxt:2, ai:"Güvenli liman. Ama gemiler limanda çürümek için yapılmamıştır."} },
    { t:"İlk Müşteri", q:"Siteni kurdun ama kimse gelmiyor. Reklam mı yaparsın, içerik mi üretirsin?",
      a:{txt:"Paralı Reklam Ver (-200 TL)", m:-200, k:10, nxt:3, ai:"Para parayı çeker derler. Hızlı çözüm, ama sürdürülebilir mi?"},
      b:{txt:"Blog Yazısı Yaz (Bedava)", m:0, k:30, nxt:3, ai:"Bilgi en büyük sermayedir. Geç olur ama güç olmaz."} },
    { t:"Yatırımcı Teklifi", q:"İşlerin büyüdü! Bir yatırımcı %50 hisse için 50.000 TL teklif ediyor.",
      a:{txt:"Kabul Et (+50.000 TL)", m:50000, k:0, nxt:4, ai:"Nakite kavuştun ama kontrolü paylaştın. Ortaklık evlilik gibidir."},
      b:{txt:"Reddet, Kendi Yağında Kavrul", m:0, k:50, nxt:4, ai:"Özgürlük paha biçilemez. Zor olacak ama zafer senin olacak."} },
    { t:"Sonuç", q:"Hayat bir yolculuktur...", a:{txt:"Yeniden Başla", nxt:0}, b:{txt:"Bitir", nxt:0} }
];
function choose(opt) {
    let s = scenarios[state.step];
    let ch = opt===1 ? s.a : s.b;
    state.m += (ch.m || 0); state.k += (ch.k || 0);
    state.step = ch.nxt || 0;
    if(state.step >= scenarios.length) state.step = 0; 
    update();
    document.getElementById('ai-feedback').innerText = "Sokrat: \"" + ch.ai + "\"";
}
function update() {
    document.getElementById('money').innerText = state.m;
    document.getElementById('health').innerText = state.h;
    document.getElementById('know').innerText = state.k;
    let s = scenarios[state.step];
    document.getElementById('q-title').innerText = s.t;
    document.getElementById('q-text').innerText = s.q;
    document.querySelector('.btn-a').innerText = s.a.txt;
    document.querySelector('.btn-b').innerText = s.b.txt;
}
</script>
</body>
</html>
"""

# --- OYUN JS (ANDROID FIX) ---
# Android WebView ve Chrome mobilde 'assign' bazen iframe içinde bloklanır.
# 'window.top.location.href' en güvenli yöntemdir.
JS_AUTO_TRANSFER = """
function autoTransfer(){
    if(score<=0){alert("Puanın yok, neyi aktaracaksın?");return;}
    let btn = document.getElementById('mBtn') || document.getElementById('bBtn');
    if(btn) { btn.innerText="İŞLENİYOR..."; btn.disabled=true; }
    
    // Kullanıcı adını al (Python'dan inject edilecek)
    let user = "{username}";
    
    // Güvenli URL oluştur
    try {
        const url = new URL(window.top.location.href);
        url.searchParams.set('t_user', user);
        url.searchParams.set('t_amt', Math.floor(score || money - startBalance));
        url.searchParams.set('ts', Date.now());
        window.top.location.href = url.toString();
    } catch(e) {
        alert("Transfer hatası: " + e.message);
    }
}
"""

def get_finance_game_html(start_money, username):
    return f"""<!DOCTYPE html><html lang="tr"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no"><style>body{{background:#0f172a;color:#e2e8f0;font-family:sans-serif;padding:10px;margin:0;}} .dashboard{{display:flex;justify-content:space-between;background:#1e293b;padding:10px;border-radius:10px;margin-bottom:10px;}} .money-val{{font-size:18px;color:#34d399;font-weight:bold;}} .asset-grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(100px,1fr));gap:5px;}} .asset-card{{background:#1e293b;padding:8px;border:1px solid #334155;border-radius:5px;cursor:pointer;}} .clicker-btn{{background:radial-gradient(circle,#3b82f6,#1d4ed8);width:90px;height:90px;border-radius:50%;margin:0 auto 15px;display:flex;align-items:center;justify-content:center;font-size:30px;box-shadow:0 0 15px #3b82f6;}} .bank-btn{{background:#10b981;color:white;width:100%;padding:15px;border:none;border-radius:8px;font-weight:bold;margin-top:10px;font-size:16px;}}</style></head><body><div class="dashboard"><div>SERMAYE<div id="money" class="money-val">{start_money}</div></div><div>GELİR<div id="cps" style="color:#facc15">0.0</div></div></div><div class="clicker-btn" onclick="manualWork()">👆</div><div class="asset-grid" id="market"></div><button id="bBtn" class="bank-btn" onclick="autoTransfer()">🏦 KÂRI BANKAYA AKTAR</button><script>let money={start_money}, startBalance={start_money}; const assets=[{{name:"Limonata",cost:150,gain:0.5,count:0}},{{name:"Simit",cost:1000,gain:3.5,count:0}},{{name:"Kantin",cost:5000,gain:15,count:0}},{{name:"Kırtasiye",cost:20000,gain:55,count:0}},{{name:"Yazılım",cost:80000,gain:200,count:0}},{{name:"Fabrika",cost:1000000,gain:3500,count:0}}]; function updateUI(){{document.getElementById('money').innerText=Math.floor(money).toLocaleString(); let total=assets.reduce((t,a)=>t+(a.count*a.gain),0); document.getElementById('cps').innerText=total.toFixed(1); let m=document.getElementById('market'); m.innerHTML=''; assets.forEach((a,i)=>{{let c=Math.floor(a.cost*Math.pow(1.2,a.count)); let d=document.createElement('div'); d.className='asset-card'; d.onclick=()=>buy(i); d.innerHTML=`<b>${{a.name}}</b> (${{a.count}})<br><span style='color:#f87171'>${{c}}</span><br><span style='color:#34d399'>+${{a.gain}}</span>`; m.appendChild(d);}});}} function manualWork(){{money+=1;updateUI();}} function buy(i){{let a=assets[i],c=Math.floor(a.cost*Math.pow(1.2,a.count)); if(money>=c){{money-=c;a.count++;updateUI();}}}} {JS_AUTO_TRANSFER.replace('{username}', username)} setInterval(()=>{{let t=assets.reduce((x,y)=>x+(y.count*y.gain),0); if(t>0){{money+=t;updateUI();}}}},1000); updateUI();</script></body></html>"""

def get_matrix_game_html(username):
    return f"""<!DOCTYPE html><html lang="tr"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no"><style>body{{margin:0;background:#050505;color:#FFD700;font-family:sans-serif;text-align:center;overflow:hidden;touch-action:none;}} #game-container{{position:absolute;top:0;left:0;width:100%;height:100%;display:flex;flex-direction:column;align-items:center;padding-top:10px;}} .header{{width:95%;display:flex;justify-content:space-between;padding:5px;background:#111;border-bottom:1px solid #FFD700;font-size:14px;}} canvas{{background:#0f0f0f;border:2px solid #333;box-shadow:0 0 10px rgba(0,0,0,0.8);}} .bank-btn{{position:absolute;top:10px;right:10px;z-index:100;background:#B8860B;color:black;border:none;padding:8px 15px;border-radius:20px;font-weight:bold;cursor:pointer;}} .overlay{{position:absolute;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,0.95);display:flex;flex-direction:column;justify-content:center;z-index:50;}} .hidden{{display:none !important;}} .big-btn{{background:transparent;border:2px solid #FFD700;color:#FFD700;padding:15px;font-size:20px;cursor:pointer;margin-top:20px;}}</style></head><body><div id="game-container"><button id="mBtn" class="bank-btn" onclick="autoTransfer()">🏦 AKTAR</button><div class="header"><div>PUAN: <span id="score">0</span></div></div><canvas id="gameCanvas"></canvas><div id="start" class="overlay"><h1>MATRIX 8x10</h1><p>Sürükle & Bırak</p><button class="big-btn" onclick="init()">BAŞLA</button></div><div id="end" class="overlay hidden"><h1 style="color:red">BİTTİ</h1><button class="big-btn" onclick="init()">TEKRAR</button></div></div><script>const cvs=document.getElementById('gameCanvas'), ctx=cvs.getContext('2d'); const COLS=8,ROWS=10; let SQ=30, grid=[], pieces=[], dragP=null, score=0, dragOff={{x:0,y:0}}; const SHAPES=[[[1]],[[1,1]],[[1],[1]],[[1,1],[1,1]],[[1,1,1]],[[1,0],[1,0],[1,1]]]; function resize(){{let w=window.innerWidth, h=window.innerHeight; SQ=Math.floor(Math.min((w-20)/COLS, (h-100)/ROWS)); SQ=Math.max(20,Math.min(SQ,50)); cvs.width=SQ*COLS; cvs.height=SQ*ROWS+100; draw();}} window.addEventListener('resize',resize); function init(){{grid=Array(ROWS).fill().map(()=>Array(COLS).fill(0)); score=0; document.getElementById('score').innerText=0; document.getElementById('start').classList.add('hidden'); document.getElementById('end').classList.add('hidden'); resize(); spawn();}} function spawn(){{pieces=[]; let y=ROWS*SQ+20, w=cvs.width/3; for(let i=0;i<3;i++){{let s=SHAPES[Math.floor(Math.random()*SHAPES.length)]; pieces.push({{s:s, x:w*i+10, y:y, bx:w*i+10, by:y, sc:0.6}});}} draw(); check();}} function draw(){{ctx.fillStyle="#050505"; ctx.fillRect(0,0,cvs.width,cvs.height); for(let r=0;r<ROWS;r++) for(let c=0;c<COLS;c++) {{ ctx.strokeStyle="#222"; ctx.strokeRect(c*SQ,r*SQ,SQ,SQ); if(grid[r][c]) {{ctx.fillStyle="#D500F9"; ctx.fillRect(c*SQ+1,r*SQ+1,SQ-2,SQ-2);}} }} ctx.beginPath(); ctx.moveTo(0,ROWS*SQ); ctx.lineTo(cvs.width,ROWS*SQ); ctx.strokeStyle="gold"; ctx.stroke(); pieces.forEach(p=>{{if(p!==dragP) ds(p.s,p.x,p.y,SQ*p.sc,"#888");}}); if(dragP) ds(dragP.s,dragP.x,dragP.y,SQ,"#D500F9");}} function ds(s,x,y,z,c){{ctx.fillStyle=c; for(let r=0;r<s.length;r++) for(let k=0;k<s[r].length;k++) if(s[r][k]) ctx.fillRect(x+k*z,y+r*z,z,z);}} function getPos(e){{let r=cvs.getBoundingClientRect(), t=e.touches?e.touches[0]:e; return {{x:t.clientX-r.left,y:t.clientY-r.top}};}} function check(){{if(pieces.length===0) spawn();}} cvs.addEventListener('mousedown',e=>{{let p=getPos(e); pieces.forEach(pi=>{{if(p.x>=pi.x&&p.x<=pi.x+50&&p.y>=pi.y&&p.y<=pi.y+50) dragP=pi;}});}}); cvs.addEventListener('mousemove',e=>{{if(dragP){{let p=getPos(e); dragP.x=p.x-20; dragP.y=p.y-20; draw();}}}}); cvs.addEventListener('mouseup',e=>{{if(dragP){{let gx=Math.round(dragP.x/SQ), gy=Math.round(dragP.y/SQ); let fits=true; for(let r=0;r<dragP.s.length;r++) for(let c=0;c<dragP.s[r].length;c++) if(dragP.s[r][c]) {{if(gy+r>=ROWS || gx+c>=COLS || gx+c<0 || grid[gy+r][gx+c]) fits=false;}} if(fits){{for(let r=0;r<dragP.s.length;r++) for(let c=0;c<dragP.s[r].length;c++) if(dragP.s[r][c]) grid[gy+r][gx+c]=1; pieces=pieces.filter(p=>p!==dragP); score+=10; document.getElementById('score').innerText=score;}} else {{dragP.x=dragP.bx; dragP.y=dragP.by;}} dragP=null; draw(); check();}}}}); cvs.addEventListener('touchstart',e=>{{let p=getPos(e); pieces.forEach(pi=>{{if(p.x>=pi.x&&p.x<=pi.x+50&&p.y>=pi.y&&p.y<=pi.y+50) dragP=pi;}});}},{{passive:false}}); cvs.addEventListener('touchmove',e=>{{e.preventDefault(); if(dragP){{let p=getPos(e); dragP.x=p.x-20; dragP.y=p.y-20; draw();}}}},{{passive:false}}); cvs.addEventListener('touchend',e=>{{if(dragP){{let gx=Math.round(dragP.x/SQ), gy=Math.round(dragP.y/SQ); let fits=true; for(let r=0;r<dragP.s.length;r++) for(let c=0;c<dragP.s[r].length;c++) if(dragP.s[r][c]) {{if(gy+r>=ROWS || gx+c>=COLS || gx+c<0 || grid[gy+r][gx+c]) fits=false;}} if(fits){{for(let r=0;r<dragP.s.length;r++) for(let c=0;c<dragP.s[r].length;c++) if(dragP.s[r][c]) grid[gy+r][gx+c]=1; pieces=pieces.filter(p=>p!==dragP); score+=10; document.getElementById('score').innerText=score;}} else {{dragP.x=dragP.bx; dragP.y=dragP.by;}} dragP=null; draw(); check();}}}}); {JS_AUTO_TRANSFER.replace('{username}', username)} setTimeout(resize,100); </script></body></html>"""

# ==========================================
# 3. MANTIK VE ARAYÜZ
# ==========================================

# --- OTOMATİK TRANSFER (Giriş Yapılmamışsa Bile Çalışır) ---
if "t_user" in st.query_params and "t_amt" in st.query_params:
    try:
        t_user = st.query_params["t_user"]
        t_amt = int(st.query_params["t_amt"])
        role = database.get_user_role(t_user)
        if role:
            st.session_state['logged_in'] = True
            st.session_state['username'] = t_user
            st.session_state['user_role'] = role
            if t_amt > 0:
                database.add_score(t_user, t_amt, "Oyun")
                st.toast(f"✅ {t_amt} Puan Eklendi!", icon="💰")
                time.sleep(1)
            st.query_params.clear()
            st.rerun()
    except: st.query_params.clear()

# --- GİRİŞ EKRANI ---
if not st.session_state['logged_in']:
    st.markdown('<div class="login-container"><h1 class="login-title">🎓 Bağarası ÇPAL Dijital Kampüs</h1></div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        tab_log, tab_reg = st.tabs(["Giriş Yap", "Kayıt Ol"])
        with tab_log:
            with st.form("login"):
                u = st.text_input("Kullanıcı Adı")
                p = st.text_input("Şifre", type="password")
                if st.form_submit_button("Giriş"):
                    user = database.login_user(u, p)
                    if user:
                        st.session_state['logged_in'] = True
                        st.session_state['user_role'] = user[3]
                        st.session_state['username'] = user[1]
                        if user[3] == "student": server.join_or_update_student("GENEL", user[1], 0)
                        st.rerun()
                    else: st.error("Hatalı bilgi.")
        with tab_reg:
            with st.form("reg"):
                nu = st.text_input("Kullanıcı Adı")
                np = st.text_input("Şifre", type="password")
                if st.form_submit_button("Kayıt Ol"):
                    if database.add_user(nu, np, "student"): st.success("Başarılı! Giriş yapın.")
                    else: st.error("Kullanıcı adı dolu.")

# --- ANA UYGULAMA ---
else:
    # Sol Menü
    with st.sidebar:
        if st.button("🏠 Ana Sayfa"): st.rerun()
        st.divider()
        st.title(st.session_state['username'])
        st.caption(f"Rol: {st.session_state['user_role']}")
        if st.session_state['user_role'] == "student":
            code = st.text_input("Sınıf Kodu", placeholder="1234")
            if st.button("Sınıfa Gir"): 
                server.join_or_update_student(code, st.session_state['username'])
                st.success("Girdin!")
        st.markdown("<br><br>", unsafe_allow_html=True)
        if st.button("🚪 Çıkış"): 
            st.session_state['logged_in'] = False; st.rerun()

    # Üst Bar
    role_tr = "Öğrenci" if st.session_state['user_role'] == "student" else "Yönetici"
    st.markdown(f'<div class="top-bar"><div class="user-greeting">Merhaba, {st.session_state["username"]}</div><div class="role-badge">{role_tr}</div></div>', unsafe_allow_html=True)

    # Sekmeler
    t1, t2, t3, t4, t5, t6 = st.tabs([" Kampüs Duvarı", "💬 Sohbet", "🏆 Puanlar", "📚 Dersler", "🎮 Oyunlar", "🧬 LifeSim"])

    # 1. KAMPÜS DUVARI (SOSYAL MEDYA)
    with t1:
        st.subheader("📢 Kampüs Duvarı")
        with st.expander("Yeni Gönderi Paylaş", expanded=False):
            with st.form("new_post"):
                txt = st.text_area("Ne düşünüyorsun?")
                img_file = st.file_uploader("Resim Ekle (İsteğe bağlı)", type=['png', 'jpg', 'jpeg'])
                if st.form_submit_button("Paylaş"):
                    img_str = None
                    if img_file:
                        try: img_str = base64.b64encode(img_file.read()).decode()
                        except: pass
                    if txt or img_str:
                        database.add_post(st.session_state['username'], txt, img_str)
                        st.success("Paylaşıldı!")
                        time.sleep(1); st.rerun()
        
        posts = database.get_posts(20)
        for p in posts:
            with st.container():
                st.markdown(f"**{p[1]}** <span style='color:gray;font-size:12px'>{p[4]}</span>", unsafe_allow_html=True)
                if p[2]: st.write(p[2])
                if p[3]: st.markdown(f'<img src="data:image/png;base64,{p[3]}" style="max-width:100%;border-radius:10px;">', unsafe_allow_html=True)
                if st.button(f"❤️ Beğen ({p[5]})", key=f"like_{p[0]}"):
                    database.like_post(p[0]); st.rerun()
                st.divider()

    # 2. SOHBET (Admin herkesle, Öğrenci Admin+Arkadaşla)
    with t2:
        st.subheader("💬 Sohbet Odası")
        friends = database.get_friends(st.session_state['username'])
        # Öğrenciyse Admin'i ekle
        if st.session_state['user_role'] == 'student' and 'admin' not in friends: friends.insert(0, "admin")
        # Adminse tüm öğrencileri getir
        if st.session_state['user_role'] == 'admin':
            all_users = [u[0] for u in database.get_all_users() if u[0] != 'admin']
            friends = all_users
        
        # Genel Sohbet ve Özel Mesaj Seçimi
        mode = st.radio("Mod:", ["Genel Sohbet", "Özel Mesaj"], horizontal=True)
        
        if mode == "Genel Sohbet":
            msgs = database.get_global_messages()
            for m in msgs:
                with st.chat_message("user" if m[0] == st.session_state['username'] else "assistant", avatar="👤"):
                    st.markdown(f"**{m[0]}**: {m[1]}")
            if p := st.chat_input("Genel sohbete yaz..."):
                database.send_global_message(st.session_state['username'], p); st.rerun()
        else:
            if not friends: st.info("Mesajlaşacak kimse yok.")
            else:
                target = st.selectbox("Kişi Seç:", friends)
                msgs = database.get_conversation(st.session_state['username'], target)
                for sender, txt, ts in msgs:
                    align = "chat-bubble-me" if sender == st.session_state['username'] else "chat-bubble-other"
                    st.markdown(f"<div class='{align}'>{txt}</div>", unsafe_allow_html=True)
                st.markdown("<div style='clear:both'></div>", unsafe_allow_html=True)
                if p := st.chat_input(f"@{target} kişisine yaz..."):
                    database.send_message(st.session_state['username'], target, p); st.rerun()

    # 3. PUANLAR
    with t3:
        sc = server.get_score("GENEL", st.session_state['username'])
        st.metric("Toplam Puan", f"{sc} ₺")
        st.subheader("Liderlik Tablosu")
        st.dataframe(server.get_leaderboard("GENEL"), use_container_width=True)

    # 4. DERSLER (TYT Yok, Sadece Meslek)
    with t4:
        st.subheader("Mesleki Sınavlar")
        EXAM_DATA = load_local_exams()
        if EXAM_DATA:
            eg = st.selectbox("Sınıf", list(EXAM_DATA.keys()))
            if eg:
                el = st.selectbox("Ders", list(EXAM_DATA[eg].keys()))
                if el:
                    qs = EXAM_DATA[eg][el]
                    with st.form("exam_form"):
                        for i, q in enumerate(qs):
                            st.write(f"**{i+1}. {q.get('text') or q.get('question')}**")
                            if q['type'] == 'test': st.radio("Cevap", q['options'], key=f"q{i}")
                            elif q['type'] == 'text': st.text_input("Cevap", key=f"q{i}")
                            st.divider()
                        if st.form_submit_button("Sınavı Bitir"):
                            total_p = sum([q.get('points', 0) for q in qs])
                            server.join_or_update_student("GENEL", st.session_state['username'], total_p)
                            st.success(f"Tebrikler! {total_p} Puan Eklendi.")
                            time.sleep(2); st.rerun()
        else: st.warning("Sınav yüklenemedi.")

    # 5. OYUNLAR (Düzeltilmiş)
    with t5:
        gm = st.selectbox("Oyun Seç", ["Finans İmparatoru", "Asset Matrix"])
        curr = server.get_score("GENEL", st.session_state['username'])
        if gm == "Finans İmparatoru": components.html(get_finance_game_html(curr, st.session_state['username']), height=600)
        else: components.html(get_matrix_game_html(st.session_state['username']), height=750)

    # 6. LIFESIM (YENİ SOKRATİK MOD)
    with t6:
        st.subheader("🧬 LifeSim: Sokratik Yolculuk")
        components.html(get_lifesim_html(), height=600, scrolling=True)
