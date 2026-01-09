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

st.set_page_config(page_title="Bağarası ÇPAL", page_icon="🎓", layout="wide", initial_sidebar_state="expanded")

def init_state():
    defaults = {"logged_in": False, "user_role": None, "username": None, "class_code": "GENEL"}
    for k, v in defaults.items():
        if k not in st.session_state: st.session_state[k] = v
init_state()

st.markdown("""
<style>
    .login-container { text-align: center; margin-top: 50px; }
    .login-title { font-family: 'Helvetica', sans-serif; font-size: 2.2rem; font-weight: 700; color: #FFD700; text-shadow: 0 0 10px rgba(0,0,0,0.5); }
    .top-bar { background: #1e293b; padding: 10px; border-radius: 8px; display: flex; justify-content: space-between; border-bottom: 2px solid #FFD700; }
    .user-greeting { font-weight: bold; color: #e2e8f0; }
    .post-card { background: #1e293b; padding: 15px; border-radius: 10px; margin-bottom: 15px; border: 1px solid #334155; }
    .comment-sec { background: #0f172a; padding: 10px; margin-top: 10px; border-radius: 5px; font-size: 0.9rem; }
    iframe { width: 100% !important; }
</style>
""", unsafe_allow_html=True)

database.create_database()
if not database.login_user("admin", "6626"): database.add_user("admin", "6626", "admin")
if st.session_state['logged_in']: database.update_activity(st.session_state['username'])

class SchoolServer:
    def join_or_update_student(self, c, u, p=0): 
        if p!=0: database.add_score(u, p, "Oyun")
        return database.get_total_score(u)
    def get_score(self, c, u): return database.get_total_score(u)
    def get_leaderboard(self, c):
        conn, db = database.get_db_connection()
        try:
            df = pd.read_sql_query("SELECT student_username, SUM(grade) as total FROM grades GROUP BY student_username ORDER BY total DESC", conn)
            conn.close()
            return df if not df.empty else pd.DataFrame(columns=["Öğrenci","Puan"])
        except: conn.close(); return pd.DataFrame(columns=["Öğrenci","Puan"])
server = SchoolServer()

@st.cache_data
def load_local_exams():
    if os.path.exists("exams.json"):
        try:
            with open("exams.json", "r", encoding="utf-8") as f: return json.load(f)
        except: return {}
    return {}

# --- GÜVENLİ TRANSFER KODU (Mobil Uyumlu) ---
# Bu kod "The operation is insecure" hatasını çözer.
def get_transfer_js(username):
    return f"""
    function autoTransfer(){{
        if(score<=0 && (typeof money === 'undefined' || (money-startBalance)<=0)){{alert("Aktaracak puan yok!");return;}}
        
        let btn = document.getElementById('bBtn') || document.getElementById('mBtn');
        if(btn) {{ btn.innerText="GÖNDERİLİYOR..."; btn.disabled=true; }}
        
        let u="{username}";
        let v = 0;
        if(typeof score !== 'undefined' && score > 0) v = score;
        else if(typeof money !== 'undefined') v = Math.floor(money-startBalance);
        
        // GÜVENLİ YÖNTEM: Link Oluştur ve Tıkla
        try {{
            const url = new URL(window.top.location.href);
            url.searchParams.set('t_user', u);
            url.searchParams.set('t_amt', v);
            url.searchParams.set('ts', Date.now());
            
            const link = document.createElement('a');
            link.href = url.toString();
            link.target = "_top"; // Bu en önemli kısım
            document.body.appendChild(link);
            link.click();
        }} catch(e){{
            alert("Hata: " + e.message);
            if(btn) btn.innerText = "HATA";
        }}
    }}
    """

# --- LIFESIM 2.0 (GELİŞMİŞ SOKRATİK MOD) ---
def get_lifesim_html():
    return """
<!DOCTYPE html><html lang="tr"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>
body{background:#020617;color:#e2e8f0;font-family:'Segoe UI',sans-serif;padding:10px;text-align:center;overflow:hidden;}
.card{background:linear-gradient(145deg, #1e293b, #0f172a);padding:20px;border-radius:20px;border:1px solid #334155;max-width:500px;margin:0 auto;box-shadow:0 0 20px rgba(0,0,0,0.7);position:relative;}
.header{display:flex;justify-content:space-between;margin-bottom:20px;border-bottom:2px solid #334155;padding-bottom:10px;}
.stat-box{text-align:center;width:30%;background:#0f172a;padding:5px;border-radius:8px;}
.stat-val{font-size:18px;font-weight:bold;display:block;}
.stat-label{font-size:10px;color:#94a3b8;text-transform:uppercase;}
.progress-container{width:100%;background:#334155;height:6px;border-radius:3px;margin-top:5px;overflow:hidden;}
.progress-bar{height:100%;transition:width 0.5s;}
.q-title{color:#38bdf8;font-size:22px;margin:10px 0;font-weight:bold;}
.q-text{font-size:16px;line-height:1.6;margin-bottom:20px;min-height:60px;}
.btn{display:block;width:100%;padding:16px;margin:10px 0;border:none;border-radius:12px;font-size:15px;cursor:pointer;font-weight:bold;transition:0.2s;text-align:left;position:relative;overflow:hidden;}
.btn:active{transform:scale(0.98);}
.btn-a{background:linear-gradient(90deg, #2563eb, #1d4ed8);color:white;box-shadow:0 4px 10px rgba(37,99,235,0.3);}
.btn-b{background:linear-gradient(90deg, #059669, #047857);color:white;box-shadow:0 4px 10px rgba(5,150,105,0.3);}
.ai-box{background:#1e1b4b;border-left:4px solid #818cf8;padding:10px;text-align:left;font-style:italic;color:#c7d2fe;font-size:13px;margin-top:15px;border-radius:4px;}
.log{font-size:11px;color:#64748b;margin-top:20px;height:30px;overflow:hidden;}
</style>
</head><body>
<div class="card">
    <div class="header">
        <div class="stat-box">
            <span id="money" class="stat-val" style="color:#fbbf24">1000</span>
            <span class="stat-label">Varlık (TL)</span>
        </div>
        <div class="stat-box">
            <span id="health" class="stat-val" style="color:#f87171">100</span>
            <span class="stat-label">Sağlık</span>
            <div class="progress-container"><div id="bar-h" class="progress-bar" style="width:100%;background:#f87171"></div></div>
        </div>
        <div class="stat-box">
            <span id="age" class="stat-val" style="color:#e2e8f0">18</span>
            <span class="stat-label">Yaş</span>
        </div>
    </div>

    <div id="game-screen">
        <div id="q-title" class="q-title">Başlangıç</div>
        <div id="q-text" class="q-text">Lise bitti. Hayat önünde kocaman bir okyanus gibi duruyor. İlk adımın ne olacak?</div>
        
        <button class="btn btn-a" onclick="nextTurn(1)"><span id="btn-a-txt">Üniversiteye Git (-4 Yıl, Bilgi+)</span></button>
        <button class="btn btn-b" onclick="nextTurn(2)"><span id="btn-b-txt">İşe Gir (Para+, Deneyim+)</span></button>
        
        <div id="ai-msg" class="ai-box">Sokrat: "Sorgulanmamış hayat yaşamaya değmez. Seçimlerin kaderindir."</div>
    </div>
    
    <div id="end-screen" style="display:none;">
        <h2 style="color:#f87171">Oyun Bitti!</h2>
        <p id="end-reason"></p>
        <button class="btn btn-a" onclick="location.reload()">Yeniden Doğ</button>
    </div>
    
    <div id="log" class="log">Simülasyon başlatıldı...</div>
</div>

<script>
let state = { money: 1000, health: 100, age: 18, knowledge: 0, job: "İşsiz" };
const events = [
    {t:"Kripto Fırsatı", q:"Arkadaşın şüpheli bir coin'e yatırım yapmanı öneriyor.", a:{t:"Yatır (-500 TL)", m:-500, h:0, msg:"Risk aldın! Bazen batarsın bazen çıkarsın."}, b:{t:"Reddet", m:0, h:0, msg:"Güvenli liman."}},
    {t:"Sağlık Sorunu", q:"Çok çalışmaktan yorgun düştün.", a:{t:"Doktora Git (-200 TL)", m:-200, h:10, msg:"Sağlık her şeyden önemlidir."}, b:{t:"Dinlen (Ücretsiz)", m:0, h:5, msg:"Zaman en iyi ilaçtır."}},
    {t:"Ek İş", q:"Hafta sonları boşsun.", a:{t:"Garsonluk Yap", m:1000, h:-5, msg:"Emek olmadan yemek olmaz."}, b:{t:"Yat Uyu", m:0, h:5, msg:"Dinlenmek de bir ihtiyaçtır."}},
    {t:"Yatırım", q:"Borsa düşüşte. Ne yapacaksın?", a:{t:"Hisse Al (-2000)", m:-2000, h:0, msg:"Krizler fırsattır."}, b:{t:"Bekle", m:0, h:0, msg:"Sabır erdemdir."}},
    {t:"Eğitim", q:"Yeni bir dil kursu var.", a:{t:"Katıl (-1000)", m:-1000, h:0, msg:"Dil insanın aynasıdır."}, b:{t:"Gerek Yok", m:0, h:0, msg:"Mevcut bilginle yetindin."}}
];

function nextTurn(choice) {
    // 1. Yaş İlerlemesi
    state.age += 1;
    
    // 2. Rastgele Olay Seçimi
    let evt = events[Math.floor(Math.random() * events.length)];
    
    // 3. Karar Etkileri
    let impact = { m:0, h:0 };
    if (choice === 1) { // A Seçeneği (Genelde Risk/Eğitim)
        impact.m = evt.a.m || -100;
        impact.h = evt.a.h || 0;
        setAI(evt.a.msg);
    } else { // B Seçeneği (Genelde Güvenli/Çalışma)
        impact.m = evt.b.m || 100;
        impact.h = evt.b.h || 0;
        setAI(evt.b.msg);
    }
    
    // 4. Sabit Yaşam Giderleri ve Maaş
    state.money -= 500; // Yıllık yaşam gideri
    if(state.money < 0) { state.health -= 10; setLog("Parasızlıktan sağlığın bozuldu!"); }
    
    // 5. Değerleri Güncelle
    state.money += impact.m;
    state.health += impact.h;
    if(state.health > 100) state.health = 100;
    
    // 6. Arayüzü Güncelle
    updateUI(evt);
    
    // 7. Oyun Bitti mi?
    if(state.health <= 0) gameOver("Sağlığını kaybettin.");
    if(state.age >= 65) gameOver("Emekli oldun! Tebrikler.");
}

function updateUI(evt) {
    document.getElementById('money').innerText = state.money;
    document.getElementById('health').innerText = state.health;
    document.getElementById('bar-h').style.width = state.health + "%";
    document.getElementById('age').innerText = state.age;
    
    // Yeni Soruyu Yaz
    document.getElementById('q-title').innerText = evt.t;
    document.getElementById('q-text').innerText = evt.q;
    document.getElementById('btn-a-txt').innerText = evt.a.t;
    document.getElementById('btn-b-txt').innerText = evt.b.t;
}

function setAI(msg) {
    document.getElementById('ai-msg').innerText = "Sokrat: \"" + msg + "\"";
}

function setLog(msg) {
    document.getElementById('log').innerText = msg;
}

function gameOver(reason) {
    document.getElementById('game-screen').style.display = 'none';
    document.getElementById('end-screen').style.display = 'block';
    document.getElementById('end-reason').innerText = reason + " Toplam Varlık: " + state.money + " TL";
}
</script></body></html>
"""

# --- FINANS HTML ---
def get_finance_game_html(start, user):
    js_code = get_transfer_js(user)
    return f"""<!DOCTYPE html><html><head><meta name="viewport" content="width=device-width, initial-scale=1.0"><style>body{{background:#0f172a;color:white;font-family:sans-serif;text-align:center;padding:10px}} .dash{{background:#1e293b;padding:10px;border-radius:10px;display:flex;justify-content:space-between}} .btn{{background:radial-gradient(circle,#3b82f6,#1d4ed8);width:80px;height:80px;border-radius:50%;margin:15px auto;display:flex;align-items:center;justify-content:center;font-size:30px;cursor:pointer}} .grid{{display:grid;grid-template-columns:repeat(3,1fr);gap:5px}} .card{{background:#1e293b;padding:5px;border:1px solid #334155;border-radius:5px;font-size:10px;cursor:pointer}} .bank{{background:#10b981;color:white;width:100%;padding:10px;border:none;border-radius:5px;margin-top:10px;font-weight:bold}}</style></head><body>
    <div class="dash"><div>💰 <span id="m">{start}</span></div><div>⚡ <span id="c">0/s</span></div></div>
    <div class="btn" onclick="clk()">👆</div><div class="grid" id="g"></div><button id="bBtn" class="bank" onclick="autoTransfer()">🏦 AKTAR</button>
    <script>
    let money={start}, startBalance={start}, score=0;
    const a=[{{n:"Limonata",c:100,g:1,k:0}},{{n:"Simit",c:500,g:5,k:0}},{{n:"Kantin",c:2000,g:25,k:0}},{{n:"Yazılım",c:10000,g:150,k:0}},{{n:"Fabrika",c:50000,g:800,k:0}},{{n:"Banka",c:200000,g:5000,k:0}}];
    function u(){{document.getElementById('m').innerText=Math.floor(money).toLocaleString(); document.getElementById('c').innerText=a.reduce((t,x)=>t+(x.k*x.g),0).toFixed(1)+'/s';
    let h=''; a.forEach((x,i)=>{{let p=Math.floor(x.c*Math.pow(1.2,x.k)); h+=`<div class="card" onclick="b(${{i}})"><b>${{x.n}}</b> (${{x.k}})<br><span style="color:#f87171">${{p}}</span><br><span style="color:#34d399">+${{x.g}}</span></div>`}}); document.getElementById('g').innerHTML=h;}}
    function clk(){{money++;u()}} function b(i){{let x=a[i],p=Math.floor(x.c*Math.pow(1.2,x.k)); if(money>=p){{money-=p;x.k++;u()}}}}
    setInterval(()=>{{let g=a.reduce((t,x)=>t+(x.k*x.g),0); if(g>0){{money+=g;u()}}}},1000); u();
    {js_code}
    </script></body></html>"""

# --- MATRIX HTML ---
def get_matrix_game_html(user):
    js_code = get_transfer_js(user)
    return f"""<!DOCTYPE html><html><head><meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no"><style>body{{background:#050505;color:#FFD700;margin:0;overflow:hidden;touch-action:none;text-align:center}} canvas{{background:#111;border:2px solid #333;margin-top:10px}} .btn{{position:absolute;top:10px;right:10px;background:#B8860B;border:none;padding:5px 15px;border-radius:15px;font-weight:bold;color:#000}}</style></head><body>
    <div style="padding:10px;display:flex;justify-content:space-between"><span>PUAN: <span id="s">0</span></span><button id="mBtn" class="btn" onclick="autoTransfer()">AKTAR</button></div>
    <canvas id="c"></canvas>
    <script>
    const cvs=document.getElementById('c'), ctx=cvs.getContext('2d');
    const R=10, C=8; let SQ=25, grid=[], pieces=[], drag=null, score=0;
    const SHAPES=[[[1]],[[1,1]],[[1],[1]],[[1,1],[1,1]],[[1,1,1]],[[1,0],[1,0],[1,1]]];
    function rs(){{let w=window.innerWidth, h=window.innerHeight; SQ=Math.floor(Math.min((w-20)/C,(h-100)/R)); SQ=Math.min(SQ,35); cvs.width=SQ*C; cvs.height=SQ*R+120; d();}}
    window.addEventListener('resize',rs);
    function init(){{grid=Array(R).fill().map(()=>Array(C).fill(0)); score=0; document.getElementById('s').innerText=0; rs(); sp();}}
    function sp(){{pieces=[]; let y=R*SQ+20, w=cvs.width/3; for(let i=0;i<3;i++){{let s=SHAPES[Math.floor(Math.random()*SHAPES.length)]; pieces.push({{s:s,x:w*i+5,y:y,bx:w*i+5,by:y,sc:0.6}});}} d();}}
    function d(){{
     ctx.fillStyle="#050505"; ctx.fillRect(0,0,cvs.width,cvs.height);
     for(let r=0;r<R;r++) for(let c=0;c<C;c++) {{ctx.strokeStyle="#222"; ctx.strokeRect(c*SQ,r*SQ,SQ,SQ); if(grid[r][c]) {{ctx.fillStyle="#D500F9"; ctx.fillRect(c*SQ+1,r*SQ+1,SQ-2,SQ-2)}}}}
     ctx.strokeStyle="gold"; ctx.beginPath(); ctx.moveTo(0,R*SQ); ctx.lineTo(cvs.width,R*SQ); ctx.stroke();
     pieces.forEach(p=>{{if(p!==drag) ds(p.s,p.x,p.y,SQ*p.sc,"#888")}});
     if(drag) ds(drag.s,drag.x,drag.y,SQ,"#D500F9");
    }}
    function ds(s,x,y,z,c){{ctx.fillStyle=c; for(let r=0;r<s.length;r++) for(let k=0;k<s[r].length;k++) if(s[r][k]) ctx.fillRect(x+k*z,y+r*z,z,z);}}
    function gp(e){{let r=cvs.getBoundingClientRect(),t=e.touches?e.touches[0]:e; return {{x:t.clientX-r.left,y:t.clientY-r.top}}}}
    function chk(){{
     for(let r=0;r<R;r++) if(grid[r].every(x=>x)) {{grid[r].fill(0); score+=50;}} 
     for(let c=0;c<C;c++) {{let f=true; for(let r=0;r<R;r++) if(!grid[r][c]) f=false; if(f) {{for(let r=0;r<R;r++) grid[r][c]=0; score+=50;}}}}
     document.getElementById('s').innerText=score;
     if(pieces.length===0) sp();
    }}
    cvs.addEventListener('touchstart',e=>{{let p=gp(e); pieces.forEach(pi=>{{if(p.x>=pi.x&&p.x<=pi.x+60&&p.y>=pi.y&&p.y<=pi.y+60) drag=pi;}});}},{{passive:false}});
    cvs.addEventListener('touchmove',e=>{{e.preventDefault(); if(drag){{let p=gp(e); drag.x=p.x-20; drag.y=p.y-20; d();}}}},{{passive:false}});
    cvs.addEventListener('touchend',e=>{{if(drag){{
     let gx=Math.round(drag.x/SQ), gy=Math.round(drag.y/SQ), fit=true;
     for(let r=0;r<drag.s.length;r++) for(let c=0;c<drag.s[r].length;c++) if(drag.s[r][c]) {{if(gx+c<0||gx+c>=C||gy+r>=R||grid[gy+r][gx+c]) fit=false;}}
     if(fit){{for(let r=0;r<drag.s.length;r++) for(let c=0;c<drag.s[r].length;c++) if(drag.s[r][c]) grid[gy+r][gx+c]=1; pieces=pieces.filter(p=>p!==drag); score+=10; chk();}}
     else {{drag.x=drag.bx; drag.y=drag.by;}} drag=null; d();
    }}}},{{passive:false}});
    init();
    {js_code}
    </script></body></html>"""

# --- TRANSFER ---
if "t_user" in st.query_params and "t_amt" in st.query_params:
    try:
        u, a = st.query_params["t_user"], int(st.query_params["t_amt"])
        role = database.get_user_role(u)
        if role:
            st.session_state['logged_in'], st.session_state['username'], st.session_state['user_role'] = True, u, role
            if a > 0: database.add_score(u, a, "Oyun"); st.toast(f"✅ {a} Puan Eklendi!", icon="💰")
            time.sleep(1); st.query_params.clear(); st.rerun()
    except: st.query_params.clear()

# --- GİRİŞ ---
if not st.session_state['logged_in']:
    st.markdown('<div class="login-container"><h1 class="login-title">🎓 Dijital Kampüs</h1></div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        with st.form("login"):
            u = st.text_input("Kullanıcı Adı")
            p = st.text_input("Şifre", type="password")
            if st.form_submit_button("Giriş"):
                user = database.login_user(u, p)
                if user:
                    st.session_state['logged_in'], st.session_state['user_role'], st.session_state['username'] = True, user[3], user[1]
                    if user[3]=="student": server.join_or_update_student("GENEL", user[1], 0)
                    st.rerun()
                else: st.error("Hatalı bilgi.")
        with st.expander("Kayıt Ol"):
            with st.form("reg"):
                nu = st.text_input("Yeni Kullanıcı")
                np = st.text_input("Şifre", type="password")
                if st.form_submit_button("Kayıt"):
                    if database.add_user(nu, np, "student"): st.success("Oldu! Giriş yap.")
                    else: st.error("Dolu.")
else:
    with st.sidebar:
        st.title(st.session_state['username'])
        st.caption(st.session_state['user_role'])
        if st.button("Çıkış"): st.session_state['logged_in']=False; st.rerun()

    st.markdown(f'<div class="top-bar"><div class="user-greeting">Merhaba, {st.session_state["username"]}</div><div class="role-badge">{st.session_state["user_role"]}</div></div>', unsafe_allow_html=True)
    
    t1, t2, t3, t4, t5, t6 = st.tabs(["📢 Kampüs Duvar", "💬 Mesaj", "🏆 Puan", "📚 Ders", "🎮 Oyun", "🧬 LifeSim"])

    with t1:
        st.subheader("Kampüs Duvar")
        with st.expander("Paylaşım Yap", expanded=False):
            with st.form("share"):
                txt = st.text_area("İçerik")
                img = st.file_uploader("Resim", type=['png','jpg'])
                if st.form_submit_button("Gönder"):
                    im_s = base64.b64encode(img.read()).decode() if img else None
                    if txt or im_s: database.add_post(st.session_state['username'], txt, im_s); st.rerun()
        
        for p in database.get_posts(15):
            with st.container():
                st.markdown(f"**{p[1]}** <small>{p[4]}</small>", unsafe_allow_html=True)
                if p[2]: st.write(p[2])
                if p[3]: st.markdown(f'<img src="data:image/png;base64,{p[3]}" style="width:100%;border-radius:10px">', unsafe_allow_html=True)
                c1, c2 = st.columns([1, 4])
                if c1.button(f"❤️ {p[5]}", key=f"l{p[0]}"): database.like_post(p[0]); st.rerun()
                comments = database.get_comments(p[0])
                if comments:
                    with st.expander(f"💬 Yorumlar ({len(comments)})"):
                        for c in comments: st.markdown(f"<div class='comment-sec'><b>{c[0]}</b>: {c[1]}</div>", unsafe_allow_html=True)
                with st.popover("Yorum Yaz"):
                    with st.form(f"cform{p[0]}"):
                        ctxt = st.text_input("Yorum")
                        if st.form_submit_button("Gönder"): database.add_comment(p[0], st.session_state['username'], ctxt); st.rerun()
                st.divider()

    with t2:
        friends = database.get_friends(st.session_state['username'])
        if st.session_state['user_role'] == 'student' and "admin" not in friends: friends.insert(0, "admin")
        if st.session_state['user_role'] == 'admin': friends = [u[0] for u in database.get_all_users() if u[0]!="admin"]
        target = st.selectbox("Kişi Seç", friends) if friends else None
        if target:
            msgs = database.get_conversation(st.session_state['username'], target)
            for s, m, t in msgs:
                align = "chat-bubble-me" if s == st.session_state['username'] else "chat-bubble-other"
                st.markdown(f"<div class='{align}'>{m}</div>", unsafe_allow_html=True)
            st.markdown("<div style='clear:both'></div>", unsafe_allow_html=True)
            if txt := st.chat_input("Mesaj..."): database.send_message(st.session_state['username'], target, txt); st.rerun()
        else: st.info("Kimse yok.")

    with t3:
        score = server.get_score("GENEL", st.session_state['username'])
        st.metric("Puan", score)
        st.dataframe(server.get_leaderboard("GENEL"), use_container_width=True)

    with t4:
        st.info("Sınavlar...")
        EX = load_local_exams()
        if EX:
            cls = st.selectbox("Sınıf", list(EX.keys()))
            lsn = st.selectbox("Ders", list(EX[cls].keys()))
            qs = EX[cls][lsn]
            with st.form("ex"):
                for i, q in enumerate(qs):
                    st.write(f"{i+1}. {q.get('text') or q.get('question')}")
                    if q['type']=='test': st.radio("Cevap", q['options'], key=f"q{i}")
                    else: st.text_input("Cevap", key=f"q{i}")
                if st.form_submit_button("Bitir"):
                    p = sum([x.get('points',0) for x in qs])
                    database.add_score(st.session_state['username'], p, "Sınav")
                    st.success(f"{p} Puan Eklendi!"); time.sleep(2); st.rerun()

    with t5:
        gm = st.selectbox("Oyun", ["Finans İmparatoru", "Asset Matrix"])
        score = server.get_score("GENEL", st.session_state['username'])
        if gm == "Finans İmparatoru": components.html(get_finance_game_html(score, st.session_state['username']), height=600)
        else: components.html(get_matrix_game_html(st.session_state['username']), height=750)

    with t6: components.html(get_lifesim_html(), height=600)
