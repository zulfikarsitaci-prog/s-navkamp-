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

# --- LIFESIM ---
def get_lifesim_html():
    return """
<!DOCTYPE html><html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>body{background:#0f172a;color:#e2e8f0;font-family:sans-serif;padding:20px;text-align:center}.card{background:#1e293b;padding:20px;border-radius:15px;border:1px solid #334155;max-width:500px;margin:0 auto;box-shadow:0 10px 25px rgba(0,0,0,0.5)}.btn{display:block;width:100%;padding:15px;margin:10px 0;border:none;border-radius:8px;font-size:16px;cursor:pointer;font-weight:bold}.btn-a{background:#3b82f6;color:white}.btn-b{background:#ef4444;color:white}.stats{display:flex;justify-content:space-around;margin-bottom:20px;color:#facc15;font-weight:bold}.ai{font-style:italic;color:#94a3b8;margin-top:15px;border-top:1px solid #334155;padding-top:10px}</style>
</head><body><div class="card"><div class="stats"><span>💰 <span id="m">1000</span></span><span>❤️ <span id="h">100</span></span><span>🧠 <span id="k">0</span></span></div><h2 id="qt" style="color:#FFD700"></h2><p id="qx" style="font-size:18px"></p><div id="chs"></div><div id="ai" class="ai"></div></div>
<script>
let s={m:1000,h:100,k:0,idx:0};
const d=[
 {t:"Başlangıç",q:"Okul bitti. 1000 TL var. Ne yapacaksın?",a:{t:"E-Ticaret (-500)",m:-500,k:20,n:1,ai:"Cesurca! Risk almadan başarı gelmez."},b:{t:"Faiz (+50)",m:50,k:0,n:2,ai:"Güvenli ama yavaş."}},
 {t:"Müşteri Yok",q:"Site boş. Ne yapmalı?",a:{t:"Reklam Ver (-200)",m:-200,k:10,n:3,ai:"Para harcamadan para kazanılmaz."},b:{t:"Blog Yaz",m:0,k:30,n:3,ai:"Bilgi güçtür, içerik kraldır."}},
 {t:"Yatırımcı",q:"Yatırımcı %50 hisse istiyor.",a:{t:"Sat (+50000)",m:50000,k:0,n:4,ai:"Nakit kraldır ama kontrolü kaybettin."},b:{t:"Reddet",m:0,k:50,n:4,ai:"Özgürlük paha biçilemez."}},
 {t:"Sonuç",q:"Yolun sonu...",a:{t:"Başa Dön",n:0},b:{t:"Bitir",n:0}}
];
function r(){
 let x=d[s.idx]; document.getElementById('qt').innerText=x.t; document.getElementById('qx').innerText=x.q;
 document.getElementById('m').innerText=s.m; document.getElementById('h').innerText=s.h; document.getElementById('k').innerText=s.k;
 let h=`<button class="btn btn-a" onclick="c(1)">${x.a.t}</button><button class="btn btn-b" onclick="c(2)">${x.b.t}</button>`;
 document.getElementById('chs').innerHTML=h;
}
function c(o){
 let x=d[s.idx], ch=o===1?x.a:x.b;
 s.m+=(ch.m||0); s.k+=(ch.k||0); s.idx=ch.n||0;
 document.getElementById('ai').innerText="Sokrat: "+(ch.ai||"...");
 r();
}
r();
</script></body></html>"""

# --- GÜVENLİ TRANSFER KODU ---
def get_transfer_js(username):
    return f"""
    function autoTransfer(){{
        if(score<=0 && (typeof money === 'undefined' || (money-startBalance)<=0)){{alert("Aktaracak puan yok!");return;}}
        let b=document.getElementById('bBtn')||document.getElementById('mBtn');
        if(b){{b.innerText="İŞLENİYOR...";b.disabled=true;}}
        let u="{username}";
        let v = 0;
        if(typeof score !== 'undefined' && score > 0) v = score;
        else if(typeof money !== 'undefined') v = Math.floor(money-startBalance);
        
        try{{
            window.top.location.href = window.top.location.href.split('?')[0] + `?t_user=${{u}}&t_amt=${{v}}&ts=`+Date.now();
        }} catch(e){{alert("Hata: "+e.message);}}
    }}
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
    function u(){{document.getElementById('m').innerText=Math.floor(money); document.getElementById('c').innerText=a.reduce((t,x)=>t+(x.k*x.g),0).toFixed(1)+'/s';
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

# --- GİRİŞ & ARAYÜZ ---
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
    
    t1, t2, t3, t4, t5, t6 = st.tabs([" Kampüs Duvar", "💬 Mesaj", "🏆 Puan", "📚 Ders", "🎮 Oyun", "🧬 LifeSim"])

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
