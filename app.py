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
# 1. AYARLAR VE STATE
# ==========================================
st.set_page_config(page_title="Bağarası ÇPAL", page_icon="🎓", layout="wide", initial_sidebar_state="expanded")

def init_state():
    defaults = {
        "logged_in": False, 
        "user_role": None, 
        "username": None, 
        "class_code": "GENEL",
        "active_menu": "📢 Kampüs Duvar" # Menü hafızası eklendi
    }
    for k, v in defaults.items():
        if k not in st.session_state: st.session_state[k] = v

init_state()

st.markdown("""
<style>
    .login-container { text-align: center; margin-top: 50px; }
    .login-title { font-family: 'Helvetica', sans-serif; font-size: 2.2rem; font-weight: 700; color: #FFD700; text-shadow: 0 0 10px rgba(0,0,0,0.5); }
    .top-bar { background: #1e293b; padding: 10px; border-radius: 8px; display: flex; justify-content: space-between; border-bottom: 2px solid #FFD700; margin-bottom: 10px; }
    .user-greeting { font-weight: bold; color: #e2e8f0; }
    .post-card { background: #1e293b; padding: 15px; border-radius: 10px; margin-bottom: 15px; border: 1px solid #334155; }
    .comment-sec { background: #0f172a; padding: 10px; margin-top: 10px; border-radius: 5px; font-size: 0.9rem; }
    /* Menü Stil */
    div[data-testid="stRadio"] > div { flex-direction: row; justify-content: center; gap: 20px; }
    iframe { width: 100% !important; }
</style>
""", unsafe_allow_html=True)

# Veritabanı ve Giriş Kontrolü
database.create_database()
if not database.login_user("admin", "6626"): database.add_user("admin", "6626", "admin")
if st.session_state['logged_in']: database.update_activity(st.session_state['username'])

# ==========================================
# 2. SERVER & OYUN MANTIĞI
# ==========================================
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

# --- TRANSFER YAKALAYICI (DÜZELTİLDİ: Sayfayı Değiştirmez) ---
if "t_user" in st.query_params and "t_amt" in st.query_params:
    try:
        u, a = st.query_params["t_user"], int(st.query_params["t_amt"])
        role = database.get_user_role(u)
        if role:
            st.session_state['logged_in'] = True
            st.session_state['username'] = u
            st.session_state['user_role'] = role
            # KRİTİK: Menüyü 'Oyun' olarak ayarla
            st.session_state['active_menu'] = "🎮 Oyun"
            
            if a > 0: 
                database.add_score(u, a, "Oyun")
                st.toast(f"✅ {a} Puan Eklendi!", icon="💰")
                time.sleep(1)
            
            st.query_params.clear()
            st.rerun()
    except Exception as e: 
        st.error(f"Hata: {e}")
        st.query_params.clear()

# --- GÜVENLİ TRANSFER KODU ---
def get_transfer_js(username):
    return f"""
    function autoTransfer(){{
        let val = 0;
        if(typeof score !== 'undefined' && score > 0) val = score;
        else if(typeof money !== 'undefined' && typeof startBalance !== 'undefined') val = Math.floor(money-startBalance);
        
        if(val <= 0){{ alert("Aktaracak puan yok!"); return; }}
        
        let btn = document.getElementById('bBtn') || document.getElementById('mBtn');
        if(btn) {{ btn.innerText="GÖNDERİLİYOR..."; btn.disabled=true; }}
        
        let u="{username}";
        try {{
            const url = new URL(window.top.location.href);
            url.searchParams.set('t_user', u);
            url.searchParams.set('t_amt', val);
            url.searchParams.set('ts', Date.now());
            const link = document.createElement('a');
            link.href = url.toString();
            link.target = "_top";
            document.body.appendChild(link);
            link.click();
        }} catch(e){{ alert("Hata: " + e.message); }}
    }}
    """

# --- OYUN HTML FONKSİYONLARI ---
def get_lifesim_html():
    return """<!DOCTYPE html><html lang="tr"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0"><style>body{background:#020617;color:#e2e8f0;font-family:sans-serif;padding:10px;text-align:center}.card{background:#1e293b;padding:20px;border-radius:15px;border:1px solid #334155;max-width:500px;margin:0 auto}.btn{display:block;width:100%;padding:15px;margin:10px 0;border:none;border-radius:8px;font-weight:bold;cursor:pointer}.btn-a{background:#3b82f6;color:white}.btn-b{background:#059669;color:white}.stats{display:flex;justify-content:space-around;margin-bottom:20px;color:#facc15;font-weight:bold}</style></head><body><div class="card"><div class="stats"><span>💰 <span id="m">1000</span></span><span>❤️ <span id="h">100</span></span><span>🎂 <span id="a">18</span></span></div><h3 id="qt" style="color:#38bdf8"></h3><p id="qx"></p><div id="chs"></div><div id="ai" style="color:#94a3b8;font-style:italic;margin-top:10px"></div></div><script>let s={m:1000,h:100,a:18}; const ev=[{t:"İş Fırsatı",q:"Garsonluk yap?",a:{t:"Evet (+Para,-Enerji)",m:500,h:-5},b:{t:"Hayır",m:0,h:5}},{t:"Yatırım",q:"Altın al?",a:{t:"Al (-1000)",m:-1000,h:0},b:{t:"Sakla",m:0,h:0}},{t:"Sağlık",q:"Hasta oldun.",a:{t:"Doktor (-200)",m:-200,h:10},b:{t:"Geçer",m:0,h:-10}}]; function nxt(c){s.a++; let e=ev[Math.floor(Math.random()*ev.length)]; let ch=c==1?e.a:e.b; s.m+=(ch.m||0); s.h+=(ch.h||0); if(s.h<=0) return end(); upd(e);} function upd(e){document.getElementById('m').innerText=s.m; document.getElementById('h').innerText=s.h; document.getElementById('a').innerText=s.a; document.getElementById('qt').innerText=e.t; document.getElementById('qx').innerText=e.q; document.getElementById('chs').innerHTML=`<button class="btn btn-a" onclick="nxt(1)">${e.a.t}</button><button class="btn btn-b" onclick="nxt(2)">${e.b.t}</button>`;} function end(){document.body.innerHTML="<h1 style='color:red'>Oyun Bitti</h1><button onclick='location.reload()'>Tekrar</button>";} upd(ev[0]);</script></body></html>"""

def get_finance_game_html(start, user):
    js = get_transfer_js(user)
    return f"""<!DOCTYPE html><html><head><meta name="viewport" content="width=device-width, initial-scale=1.0"><style>body{{background:#0f172a;color:white;font-family:sans-serif;text-align:center;padding:10px}} .grid{{display:grid;grid-template-columns:repeat(3,1fr);gap:5px}} .card{{background:#1e293b;padding:5px;border-radius:5px;font-size:10px;cursor:pointer}} .btn{{background:#3b82f6;width:80px;height:80px;border-radius:50%;margin:15px auto;display:flex;align-items:center;justify-content:center;font-size:30px;cursor:pointer}} .bank{{background:#10b981;color:white;width:100%;padding:10px;border:none;border-radius:5px;margin-top:10px;font-weight:bold}}</style></head><body><div>💰 <span id="m">{start}</span></div><div class="btn" onclick="c()">👆</div><div class="grid" id="g"></div><button id="bBtn" class="bank" onclick="autoTransfer()">🏦 AKTAR</button><script>let money={start}, startBalance={start}; const a=[{{n:"Limonata",c:100,g:1,k:0}},{{n:"Simit",c:500,g:5,k:0}},{{n:"Kantin",c:2000,g:25,k:0}},{{n:"Yazılım",c:10000,g:150,k:0}},{{n:"Fabrika",c:50000,g:800,k:0}},{{n:"Banka",c:200000,g:5000,k:0}}]; function u(){{document.getElementById('m').innerText=Math.floor(money); let h=''; a.forEach((x,i)=>{{let p=Math.floor(x.c*Math.pow(1.2,x.k)); h+=`<div class="card" onclick="b(${{i}})"><b>${{x.n}}</b> (${{x.k}})<br><span style="color:#f87171">${{p}}</span><br><span style="color:#34d399">+${{x.g}}</span></div>`}}); document.getElementById('g').innerHTML=h;}} function c(){{money++;u()}} function b(i){{let x=a[i],p=Math.floor(x.c*Math.pow(1.2,x.k)); if(money>=p){{money-=p;x.k++;u()}}}} setInterval(()=>{{let g=a.reduce((t,x)=>t+(x.k*x.g),0); if(g>0){{money+=g;u()}}}},1000); u(); {js} </script></body></html>"""

def get_matrix_game_html(user):
    js = get_transfer_js(user)
    return f"""<!DOCTYPE html><html><head><meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no"><style>body{{background:#050505;color:#FFD700;margin:0;overflow:hidden;touch-action:none;text-align:center}} canvas{{background:#111;border:2px solid #333;margin-top:10px}} .btn{{position:absolute;top:10px;right:10px;background:#B8860B;border:none;padding:5px 15px;border-radius:15px;font-weight:bold;color:#000}}</style></head><body><div style="padding:10px;display:flex;justify-content:space-between"><span>PUAN: <span id="s">0</span></span><button id="mBtn" class="btn" onclick="autoTransfer()">AKTAR</button></div><canvas id="c"></canvas><script>const cvs=document.getElementById('c'), ctx=cvs.getContext('2d'); const R=10, C=8; let SQ=25, grid=[], pieces=[], drag=null, score=0; const SHAPES=[[[1]],[[1,1]],[[1],[1]],[[1,1,1]],[[1,0],[1,0],[1,1]]]; function rs(){{let w=window.innerWidth, h=window.innerHeight; SQ=Math.floor(Math.min((w-20)/C,(h-100)/R)); SQ=Math.min(SQ,35); cvs.width=SQ*C; cvs.height=SQ*R+120; d();}} window.addEventListener('resize',rs); function init(){{grid=Array(R).fill().map(()=>Array(C).fill(0)); score=0; document.getElementById('s').innerText=0; rs(); sp();}} function sp(){{pieces=[]; let y=R*SQ+20, w=cvs.width/3; for(let i=0;i<3;i++){{let s=SHAPES[Math.floor(Math.random()*SHAPES.length)]; pieces.push({{s:s,x:w*i+5,y:y,bx:w*i+5,by:y,sc:0.6}});}} d();}} function d(){{ctx.fillStyle="#050505"; ctx.fillRect(0,0,cvs.width,cvs.height); for(let r=0;r<R;r++) for(let c=0;c<C;c++) {{ctx.strokeStyle="#222"; ctx.strokeRect(c*SQ,r*SQ,SQ,SQ); if(grid[r][c]) {{ctx.fillStyle="#D500F9"; ctx.fillRect(c*SQ+1,r*SQ+1,SQ-2,SQ-2)}}}} ctx.strokeStyle="gold"; ctx.beginPath(); ctx.moveTo(0,R*SQ); ctx.lineTo(cvs.width,R*SQ); ctx.stroke(); pieces.forEach(p=>{{if(p!==drag) ds(p.s,p.x,p.y,SQ*p.sc,"#888")}}); if(drag) ds(drag.s,drag.x,drag.y,SQ,"#D500F9");}} function ds(s,x,y,z,c){{ctx.fillStyle=c; for(let r=0;r<s.length;r++) for(let k=0;k<s[r].length;k++) if(s[r][k]) ctx.fillRect(x+k*z,y+r*z,z,z);}} function gp(e){{let r=cvs.getBoundingClientRect(),t=e.touches?e.touches[0]:e; return {{x:t.clientX-r.left,y:t.clientY-r.top}}}} function chk(){{for(let r=0;r<R;r++) if(grid[r].every(x=>x)) {{grid[r].fill(0); score+=50;}} for(let c=0;c<C;c++) {{let f=true; for(let r=0;r<R;r++) if(!grid[r][c]) f=false; if(f) {{for(let r=0;r<R;r++) grid[r][c]=0; score+=50;}}}} document.getElementById('s').innerText=score; if(pieces.length===0) sp();}} cvs.addEventListener('touchstart',e=>{{let p=gp(e); pieces.forEach(pi=>{{if(p.x>=pi.x&&p.x<=pi.x+60&&p.y>=pi.y&&p.y<=pi.y+60) drag=pi;}});}},{{passive:false}}); cvs.addEventListener('touchmove',e=>{{e.preventDefault(); if(drag){{let p=gp(e); drag.x=p.x-20; drag.y=p.y-20; d();}}}},{{passive:false}}); cvs.addEventListener('touchend',e=>{{if(drag){{let gx=Math.round(drag.x/SQ), gy=Math.round(drag.y/SQ), fit=true; for(let r=0;r<drag.s.length;r++) for(let c=0;c<drag.s[r].length;c++) if(drag.s[r][c]) {{if(gx+c<0||gx+c>=C||gy+r>=R||grid[gy+r][gx+c]) fit=false;}} if(fit){{for(let r=0;r<drag.s.length;r++) for(let c=0;c<drag.s[r].length;c++) if(drag.s[r][c]) grid[gy+r][gx+c]=1; pieces=pieces.filter(p=>p!==drag); score+=10; chk();}} else {{drag.x=drag.bx; drag.y=drag.by;}} drag=null; d();}}}},{{passive:false}}); init(); {js} </script></body></html>"""

# ==========================================
# 3. ANA ARAYÜZ
# ==========================================
if not st.session_state['logged_in']:
    st.markdown('<div class="login-container"><h1 class="login-title">🎓 Dijital Kampüs</h1></div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        with st.form("login"):
            u = st.text_input("Kullanıcı Adı"); p = st.text_input("Şifre", type="password")
            if st.form_submit_button("Giriş"):
                user = database.login_user(u, p)
                if user:
                    st.session_state['logged_in'], st.session_state['user_role'], st.session_state['username'] = True, user[3], user[1]
                    if user[3]=="student": server.join_or_update_student("GENEL", user[1], 0)
                    st.rerun()
                else: st.error("Hatalı")
        with st.expander("Kayıt"):
            with st.form("reg"):
                nu = st.text_input("Kullanıcı"); np = st.text_input("Şifre", type="password")
                if st.form_submit_button("Kayıt Ol"):
                    if database.add_user(nu, np, "student"): st.success("Başarılı"); st.rerun()
else:
    with st.sidebar:
        st.title(st.session_state['username'])
        if st.button("Çıkış"): st.session_state['logged_in']=False; st.rerun()

    st.markdown(f'<div class="top-bar"><div class="user-greeting">Merhaba, {st.session_state["username"]}</div><div class="role-badge">{st.session_state["user_role"]}</div></div>', unsafe_allow_html=True)
    
    # MENÜ (Sekmeler yerine Radio)
    menu_options = ["📢 Kampüs Duvar", "💬 Mesaj", "🏆 Puan", "📚 Ders", "🎮 Oyun", "🧬 LifeSim"]
    
    # Session state'deki seçimi kullan
    default_ix = 0
    if st.session_state['active_menu'] in menu_options:
        default_ix = menu_options.index(st.session_state['active_menu'])
        
    selected = st.radio("", menu_options, index=default_ix, horizontal=True, label_visibility="collapsed")
    
    # Eğer kullanıcı elle değiştirdiyse state'i güncelle
    if selected != st.session_state['active_menu']:
        st.session_state['active_menu'] = selected
        st.rerun()

    # --- SAYFA İÇERİKLERİ ---
    if selected == "📢 Kampüs Duvar":
        st.subheader("Kampüs Duvar")
        with st.expander("Paylaş", expanded=False):
            with st.form("share"):
                txt = st.text_area("İçerik"); img = st.file_uploader("Resim", type=['png','jpg'])
                if st.form_submit_button("Paylaş"):
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
                    with st.form(f"c{p[0]}"):
                        ct = st.text_input("Yorum"); 
                        if st.form_submit_button("Yolla"): database.add_comment(p[0], st.session_state['username'], ct); st.rerun()
                st.divider()

    elif selected == "💬 Mesaj":
        friends = database.get_friends(st.session_state['username'])
        if st.session_state['user_role'] == 'student' and "admin" not in friends: friends.insert(0, "admin")
        if st.session_state['user_role'] == 'admin': friends = [u[0] for u in database.get_all_users() if u[0]!="admin"]
        target = st.selectbox("Kişi", friends) if friends else None
        if target:
            for s, m, t in database.get_conversation(st.session_state['username'], target):
                st.info(f"{s}: {m}")
            if txt := st.chat_input("Yaz..."): database.send_message(st.session_state['username'], target, txt); st.rerun()
        else: st.info("Kimse yok.")

    elif selected == "🏆 Puan":
        st.metric("Puan", server.get_score("GENEL", st.session_state['username']))
        st.dataframe(server.get_leaderboard("GENEL"), use_container_width=True)

    elif selected == "📚 Ders":
        EX = load_local_exams()
        if EX:
            cls = st.selectbox("Sınıf", list(EX.keys())); lsn = st.selectbox("Ders", list(EX[cls].keys()))
            with st.form("ex"):
                for i, q in enumerate(EX[cls][lsn]):
                    st.write(f"{i+1}. {q.get('text') or q.get('question')}")
                    if q['type']=='test': st.radio("Cv", q['options'], key=f"q{i}")
                    else: st.text_input("Cv", key=f"q{i}")
                if st.form_submit_button("Bitir"):
                    p = sum([x.get('points',0) for x in EX[cls][lsn]])
                    database.add_score(st.session_state['username'], p, "Sınav"); st.success(f"{p} Puan!"); time.sleep(1); st.rerun()

    elif selected == "🎮 Oyun":
        gm = st.selectbox("Seç", ["Finans İmparatoru", "Asset Matrix"])
        sc = server.get_score("GENEL", st.session_state['username'])
        if gm == "Finans İmparatoru": components.html(get_finance_game_html(sc, st.session_state['username']), height=600)
        else: components.html(get_matrix_game_html(st.session_state['username']), height=750)

    elif selected == "🧬 LifeSim":
        components.html(get_lifesim_html(), height=600)
