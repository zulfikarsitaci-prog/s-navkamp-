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

# --- AYARLAR ---
st.set_page_config(page_title="Bağarası ÇPAL", page_icon="🎓", layout="wide", initial_sidebar_state="expanded")
TEACHER_NAME = "Mustafa"

def init_state():
    defaults = {"logged_in": False, "user_role": None, "username": None, "class_code": "GENEL", "active_menu": "📢 Kampüs Duvar", "draft_content": ""}
    for k, v in defaults.items():
        if k not in st.session_state: st.session_state[k] = v
init_state()

# --- CSS (HATA DÜZELTİCİ VE STİL) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@700&family=Orbitron:wght@700&family=Rye&family=Dancing+Script:wght@700&family=Metal+Mania&display=swap');

    .top-bar { background: #1e293b; padding: 10px; border-radius: 8px; display: flex; justify-content: space-between; border-bottom: 2px solid #FFD700; margin-bottom: 10px; }
    .user-greeting { font-weight: bold; color: #e2e8f0; font-size: 1rem; }
    
    /* POST KARTI (Modern ve Temiz) */
    .post-card-container {
        background-color: #1e293b;
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 15px 15px 5px 15px; /* Alt padding azaltıldı butonlar için */
        margin-bottom: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    .post-header { display: flex; align-items: center; margin-bottom: 8px; }
    .post-date { color: #94a3b8; font-size: 0.7rem; margin-left: auto; }
    .post-text { color: #e2e8f0; font-size: 0.95rem; line-height: 1.5; white-space: pre-wrap; margin-bottom: 8px; }
    .post-img { width: 100%; border-radius: 8px; margin-top: 5px; object-fit: cover; max-height: 400px; }
    
    /* BUTONLARI KÜÇÜLTME VE GİZLEME (Magic CSS) */
    /* Streamlit butonlarının varsayılan arka planını ve sınırlarını kaldır */
    div.stButton > button {
        background-color: transparent !important;
        border: none !important;
        color: #94a3b8 !important;
        padding: 0px 5px !important;
        font-size: 1.1rem !important;
        margin: 0 !important;
        box-shadow: none !important;
        transition: 0.3s;
    }
    div.stButton > button:hover {
        color: #FFD700 !important; /* Altın rengi hover */
        transform: scale(1.2);
    }
    div.stButton > button:active {
        color: #fff !important;
    }
    div.stButton {
        display: inline-block;
        margin-right: 10px;
    }

    /* YORUM ALANI */
    .comment-sec { background: #0f172a; padding: 8px; margin-top: 5px; border-radius: 8px; font-size: 0.85rem; border-left: 2px solid #334155; display: flex; align-items: center; }
    
    /* MAĞAZA */
    .shop-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 8px; margin-top: 10px; }
    @media only screen and (max-width: 600px) { .shop-grid { grid-template-columns: repeat(3, 1fr); } }
    .shop-item { background: #0f172a; border: 1px solid #334155; border-radius: 8px; padding: 5px; text-align: center; display: flex; flex-direction: column; align-items: center; justify-content: space-between; height: 120px; transition: 0.2s; }
    .shop-item:hover { border-color: #FFD700; transform: translateY(-2px); }
    .shop-name { font-size: 0.7rem; font-weight: bold; margin-top: 5px; color: #cbd5e1; }
    .shop-price { background: #10b981; color: white; padding: 2px 8px; border-radius: 10px; font-size: 0.65rem; font-weight: bold; margin-top: auto; }
    .gift-icon { font-size: 2.5rem; margin-top: 5px; }

    /* FONT & STİLLER */
    .font-Cinzel { font-family: 'Cinzel', serif !important; }
    .font-Orbitron { font-family: 'Orbitron', sans-serif !important; }
    .font-Rye { font-family: 'Rye', serif !important; }
    .font-Dancing { font-family: 'Dancing Script', cursive !important; }
    .font-Metallic { font-family: 'Metal Mania', cursive !important; color: #b0b0b0 !important; text-shadow: 2px 2px 0px #000; letter-spacing: 1px; }

    .avatar-container { position: relative; display: inline-block; margin-right: 10px; vertical-align: middle; }
    .avatar-img { width: 40px; height: 40px; border-radius: 50%; object-fit: cover; }
    .frame-overlay { position: absolute; top: -3px; left: -3px; width: 46px; height: 46px; pointer-events: none; z-index: 2; }
    
    .frame-Gold { border: 2px solid #FFD700; border-radius: 50%; box-shadow: 0 0 5px #FFD700; }
    .frame-Neon { border: 2px solid #00ffff; border-radius: 50%; box-shadow: 0 0 5px #00ffff; }
    .frame-Fire { border: 2px solid #ff4500; border-radius: 50%; box-shadow: 0 0 10px #ff4500; }
    .frame-King { border: 3px solid #ffd700; border-radius: 50%; box-shadow: 0 0 10px #ffd700; }
    .frame-Matrix { border: 2px dotted #00ff00; border-radius: 50%; }

    .name-Glitch { color: #00ffff; text-shadow: 1px 0 #ff00ff; font-weight: bold; }
    .name-Fire { color: #ff4500; text-shadow: 0 0 3px #ff0000; font-weight: bold; }
    .name-Gold { background: linear-gradient(to right, #BF953F, #FCF6BA, #B38728); -webkit-background-clip: text; color: transparent; font-weight: 900; }
    
    .post-Cyan { color: #00ffff !important; }
    .post-Lime { color: #00ff00 !important; }
    .post-Pink { color: #ff69b4 !important; }
    .post-Gold { color: #ffd700 !important; }

    .title-badge { background: #334155; color: #94a3b8; padding: 2px 5px; border-radius: 4px; font-size: 0.6rem; margin-left: 5px; vertical-align: middle; }
    iframe { width: 100% !important; }
</style>
""", unsafe_allow_html=True)

# Veritabanı
try:
    database.create_database()
    if not database.login_user("admin", "6626"): database.add_user("admin", "6626", "admin")
except: pass
if st.session_state['logged_in']: database.update_activity(st.session_state['username'])

# --- GÖRSEL YARDIMCILAR (Düzeltildi: Tek Satır String) ---
def get_user_display_html(username, size=40):
    ava, frame, name_style, _, font_style, title = database.get_user_styles(username)
    img_src = f"data:image/jpeg;base64,{ava}" if ava else "https://via.placeholder.com/150/CCCCCC/FFFFFF?text=U"
    
    # HTML stringlerini tek satırda birleştiriyoruz (Hata önleyici)
    f_html = f'<div class="frame-overlay frame-{frame}"></div>' if frame else ""
    classes = f"{f'name-{name_style}' if name_style else ''} {f'font-{font_style}' if font_style else ''}"
    
    return f"""<div style="display:flex;align-items:center;"><div class="avatar-container"><img src="{img_src}" class="avatar-img">{f_html}</div><div class="{classes}" style="font-size:0.9rem;">{username} {f"<span class='title-badge'>{title}</span>" if title else ""}</div></div>"""

def get_post_style_css(username):
    _, _, _, post_style, font_style, _ = database.get_user_styles(username)
    return f"post-{post_style} font-{font_style}"

class SchoolServer:
    def join_or_update_student(self, c, u, p=0): 
        if p!=0: database.add_score(u, p, "Oyun")
        return database.get_total_score(u)
    def get_score(self, c, u): return database.get_total_score(u)
    def get_leaderboard(self, c):
        df = pd.DataFrame(database.get_leaderboard_data(), columns=["Öğrenci","Puan"])
        return df if not df.empty else pd.DataFrame(columns=["Öğrenci","Puan"])
    def buy_item(self, u, type, name, cost): return database.buy_item(u, type, name, cost)
    def send_gift(self, s, r, item, cost): return database.send_gift(s, r, item, cost)
server = SchoolServer()

@st.cache_data
def load_local_exams():
    if os.path.exists("exams.json"):
        try: return json.load(open("exams.json","r",encoding="utf-8"))
        except: return {}
    return {}

# --- TRANSFER ---
if "action" in st.query_params:
    try:
        act = st.query_params["action"]
        if act == "transfer":
            u, a = st.query_params["u"], int(st.query_params["a"])
            if database.get_user_role(u):
                st.session_state.update({'logged_in':True, 'username':u, 'active_menu':"🎮 Oyun"})
                if a > 0: database.add_score(u, a, "Oyun"); st.toast(f"✅ {a} Puan!", icon="💰"); time.sleep(1)
        elif act == "buy":
            u, t, v, c = st.query_params["u"], st.query_params["t"], st.query_params["v"], int(st.query_params["c"])
            if database.get_user_role(u):
                st.session_state.update({'logged_in':True, 'username':u, 'active_menu':"🛒 Mağaza"})
                ok, msg = server.buy_item(u, t, v, c)
                if ok: st.toast(f"🎉 {msg}", icon="🛍️"); time.sleep(1)
                else: st.toast(f"❌ {msg}", icon="⚠️")
        elif act == "gift":
            u, t, g, c = st.query_params["u"], st.query_params["t"], st.query_params["g"], int(st.query_params["c"])
            if database.get_user_role(u):
                st.session_state.update({'logged_in':True, 'username':u, 'active_menu':"🛒 Mağaza"})
                if t and t != "None":
                    ok, msg = server.send_gift(u, t, g, c)
                    if ok: st.toast(f"🎁 {msg}", icon="✅"); time.sleep(1)
                    else: st.toast(f"❌ {msg}", icon="⚠️")
        st.query_params.clear(); st.rerun()
    except: st.query_params.clear()

# --- JS ---
def get_transfer_js(username):
    return f"""function autoTransfer(){{let v=0;if(typeof score!=='undefined'&&score>0)v=score;else if(typeof money!=='undefined')v=Math.floor(money-startBalance);if(v<=0){{alert("Puan yok!");return;}}let b=document.getElementById('bBtn')||document.getElementById('mBtn');if(b){{b.innerText="...";b.disabled=true;}}try{{const u=new URL(window.top.location.href);u.searchParams.set('action','transfer');u.searchParams.set('u',"{username}");u.searchParams.set('a',v);u.searchParams.set('ts',Date.now());const l=document.createElement('a');l.href=u.toString();l.target="_top";document.body.appendChild(l);l.click();}}catch(e){{alert(e.message);}}}}"""

# --- OYUNLAR ---
def get_finance_game_html(start, user):
    js = get_transfer_js(user)
    return f"""<!DOCTYPE html><html><head><meta name="viewport" content="width=device-width,initial-scale=1.0"><style>body{{background:#0f172a;color:#fff;font-family:sans-serif;padding:5px;text-align:center}}.tab{{display:flex;justify-content:center;gap:10px;margin-bottom:10px}}.tab button{{background:#334155;border:none;color:#fff;padding:8px;border-radius:5px;cursor:pointer}}.active{{background:#3b82f6!important}}.grid{{display:grid;grid-template-columns:repeat(2,1fr);gap:5px}}.card{{background:#1e293b;padding:8px;border-radius:5px;border:1px solid #475569;cursor:pointer}}.btn{{background:radial-gradient(circle,#3b82f6,#1d4ed8);width:80px;height:80px;border-radius:50%;margin:10px auto;display:flex;align-items:center;justify-content:center;font-size:30px;box-shadow:0 0 15px #3b82f6;cursor:pointer}}.bank{{background:#10b981;color:white;width:100%;padding:12px;border:none;border-radius:8px;margin-top:10px;font-weight:bold}}</style></head><body><div style="font-size:20px;font-weight:bold;color:#fbbf24">💰 <span id="m">{start}</span></div><div style="font-size:12px;color:#94a3b8">Gelir: <span id="cps">0</span>/sn</div><div class="tab"><button onclick="sTab('main')" class="active" id="btn-main">İşletme</button><button onclick="sTab('mgr')" id="btn-mgr">Yöneticiler</button></div><div id="main"><div class="btn" onclick="clk()">👆</div><div class="grid" id="market"></div></div><div id="mgr" style="display:none"><div class="grid" id="managers"></div></div><button id="bBtn" class="bank" onclick="autoTransfer()">🏦 KASAYI BANKAYA AKTAR</button><script>let money={start},startBalance={start};const assets=[{{n:"Limonata",c:100,g:1,k:0}},{{n:"Simit",c:500,g:5,k:0}},{{n:"Kantin",c:2500,g:30,k:0}},{{n:"Cafe",c:10000,g:100,k:0}},{{n:"Yazılım",c:50000,g:600,k:0}},{{n:"Fabrika",c:200000,g:3000,k:0}},{{n:"Banka",c:1000000,g:15000,k:0}}];const mgrs=[{{n:"Çırak",c:5000,e:0,desc:"Limonata/Simit Oto"}},{{n:"Müdür",c:50000,e:0,desc:"Kantin/Cafe Oto"}},{{n:"CEO",c:1000000,e:0,desc:"x2 Hız"}}];function u(){{document.getElementById('m').innerText=Math.floor(money).toLocaleString();let total=assets.reduce((t,x)=>t+(x.k*x.g),0)*(mgrs[2].e?2:1);document.getElementById('cps').innerText=total.toLocaleString();let h='';assets.forEach((x,i)=>{{let p=Math.floor(x.c*Math.pow(1.15,x.k));h+=`<div class="card" onclick="b(${{i}})"><b>${{x.n}}</b> (${{x.k}})<br><span style="color:#f87171">${{p.toLocaleString()}}</span><br><span style="color:#34d399">+${{x.g}}</span></div>`}});document.getElementById('market').innerHTML=h;let m='';mgrs.forEach((x,i)=>{{m+=`<div class="card" onclick="bm(${{i}})" style="opacity:${{x.e?0.5:1}}"><b>${{x.n}}</b><br><span style="color:#fbbf24">${{x.c.toLocaleString()}}</span><br><small>${{x.desc}}</small></div>`}});document.getElementById('managers').innerHTML=m;}}function clk(){{money+=1+(assets[0].k*0.1);u()}}function b(i){{let x=assets[i],p=Math.floor(x.c*Math.pow(1.15,x.k));if(money>=p){{money-=p;x.k++;u()}}}}function bm(i){{if(!mgrs[i].e&&money>=mgrs[i].c){{money-=mgrs[i].c;mgrs[i].e=1;u()}}}}function sTab(t){{document.getElementById('main').style.display='none';document.getElementById('mgr').style.display='none';document.getElementById('btn-main').className='';document.getElementById('btn-mgr').className='';document.getElementById(t).style.display='block';document.getElementById('btn-'+t).className='active';}}setInterval(()=>{{let g=assets.reduce((t,x)=>t+(x.k*x.g),0)*(mgrs[2].e?2:1);if(mgrs[0].e)g+=(assets[0].g*assets[0].k+assets[1].g*assets[1].k)*0.5;if(mgrs[1].e)g+=(assets[2].g*assets[2].k+assets[3].g*assets[3].k)*0.5;if(g>0){{money+=g/10;u()}}}},100);u();{js}</script></body></html>"""

def get_matrix_game_html(user):
    js = get_transfer_js(user)
    return f"""<!DOCTYPE html><html><head><meta name="viewport" content="width=device-width,initial-scale=1.0,maximum-scale=1.0,user-scalable=no"><style>body{{background:#050505;color:#00ffff;margin:0;overflow:hidden;touch-action:none;text-align:center}}canvas{{background:#111;border:2px solid #333;margin-top:10px}}.btn{{position:absolute;top:10px;right:10px;background:#ff00ff;border:none;padding:5px 15px;border-radius:15px;font-weight:bold;color:white}}</style></head><body><div style="padding:10px;display:flex;justify-content:space-between"><span>PUAN: <span id="s">0</span></span><button id="mBtn" class="btn" onclick="autoTransfer()">AKTAR</button></div><canvas id="c"></canvas><script>const cvs=document.getElementById('c'),ctx=cvs.getContext('2d');const R=10,C=8;let SQ=25,grid=[],pieces=[],drag=null,score=0;const SHAPES=[[[1]],[[1,1]],[[1],[1]],[[1,1,1]],[[1,0],[1,0],[1,1]]];function rs(){{let w=window.innerWidth,h=window.innerHeight;SQ=Math.floor(Math.min((w-20)/C,(h-100)/R));SQ=Math.min(SQ,35);cvs.width=SQ*C;cvs.height=SQ*R+120;d()}}window.addEventListener('resize',rs);function init(){{grid=Array(R).fill().map(()=>Array(C).fill(0));score=0;document.getElementById('s').innerText=0;rs();sp()}}function sp(){{pieces=[];let y=R*SQ+20,w=cvs.width/3;for(let i=0;i<3;i++){{let s=SHAPES[Math.floor(Math.random()*SHAPES.length)];pieces.push({{s:s,x:w*i+5,y:y,bx:w*i+5,by:y,sc:0.6}})}}d()}}function d(){{ctx.fillStyle="#000000";ctx.fillRect(0,0,cvs.width,cvs.height);for(let r=0;r<R;r++)for(let c=0;c<C;c++){{ctx.strokeStyle="#333";ctx.lineWidth=1;ctx.strokeRect(c*SQ,r*SQ,SQ,SQ);if(grid[r][c]){{ctx.fillStyle="#00ffff";ctx.fillRect(c*SQ+3,r*SQ+3,SQ-6,SQ-6);ctx.strokeStyle="#ff00ff";ctx.strokeRect(c*SQ+3,r*SQ+3,SQ-6,SQ-6)}}}}ctx.strokeStyle="white";ctx.beginPath();ctx.moveTo(0,R*SQ);ctx.lineTo(cvs.width,R*SQ);ctx.stroke();pieces.forEach(p=>{{if(p!==drag)ds(p.s,p.x,p.y,SQ*p.sc,"#555")}});if(drag)ds(drag.s,drag.x,drag.y,SQ,"#ff00ff")}}function ds(s,x,y,z,c){{ctx.fillStyle=c;for(let r=0;r<s.length;r++)for(let k=0;k<s[r].length;k++)if(s[r][k])ctx.fillRect(x+k*z,y+r*z,z,z)}}function gp(e){{let r=cvs.getBoundingClientRect(),t=e.touches?e.touches[0]:e;return{{x:t.clientX-r.left,y:t.clientY-r.top}}}}function chk(){{for(let r=0;r<R;r++)if(grid[r].every(x=>x)){{grid[r].fill(0);score+=50}}for(let c=0;c<C;c++){{let f=true;for(let r=0;r<R;r++)if(!grid[r][c])f=false;if(f){{for(let r=0;r<R;r++)grid[r][c]=0;score+=50}}}}document.getElementById('s').innerText=score;if(pieces.length===0)sp()}}cvs.addEventListener('touchstart',e=>{{let p=gp(e);pieces.forEach(pi=>{{if(p.x>=pi.x&&p.x<=pi.x+60&&p.y>=pi.y&&p.y<=pi.y+60)drag=pi}})}},{{passive:false}});cvs.addEventListener('touchmove',e=>{{e.preventDefault();if(drag){{let p=gp(e);drag.x=p.x-20;drag.y=p.y-20;d()}}}},{{passive:false}});cvs.addEventListener('touchend',e=>{{if(drag){{let gx=Math.round(drag.x/SQ),gy=Math.round(drag.y/SQ),fit=true;for(let r=0;r<drag.s.length;r++)for(let c=0;c<drag.s[r].length;c++)if(drag.s[r][c]){{if(gx+c<0||gx+c>=C||gy+r>=R||grid[gy+r][gx+c])fit=false}}if(fit){{for(let r=0;r<drag.s.length;r++)for(let c=0;c<drag.s[r].length;c++)if(drag.s[r][c])grid[gy+r][gx+c]=1;pieces=pieces.filter(p=>p!==drag);score+=10;chk()}}else{{drag.x=drag.bx;drag.y=drag.by}}drag=null;d()}}}},{{passive:false}});init();{js}</script></body></html>"""

# --- ARAYÜZ ---
if not st.session_state['logged_in']:
    st.markdown('<div class="login-container"><h1 class="login-title">🎓 Dijital Kampüs</h1></div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        with st.form("login"):
            u = st.text_input("Kullanıcı Adı"); p = st.text_input("Şifre", type="password")
            if st.form_submit_button("Giriş"):
                user = database.login_user(u, p)
                if user:
                    st.session_state.update({'logged_in':True, 'user_role':user[3], 'username':user[1]})
                    if user[3]=="student": server.join_or_update_student("GENEL", user[1], 0)
                    st.rerun()
                else: st.error("Hatalı.")
        with st.expander("Kayıt"):
            with st.form("reg"):
                nu = st.text_input("Kullanıcı"); np = st.text_input("Şifre", type="password")
                q = st.text_input("Muhasebe ve Finansman Öğretmeninizin Adı Nedir?")
                if st.form_submit_button("Kayıt"):
                    if q.lower().strip() == TEACHER_NAME.lower():
                        success, rank = database.add_user(nu, np, "student")
                        if success:
                            if rank <= 10: 
                                st.balloons()
                                st.success(f"TEBRİKLER! {rank}. kişi olarak KURUCU ünvanı ve 50.000 Puan kazandın!")
                            else: st.success("Başarılı! Giriş yapabilirsin.")
                        else: st.error("İsim alınmış.")
                    else: st.error("Güvenlik sorusu yanlış!")
else:
    with st.sidebar:
        st.markdown(get_user_display_html(st.session_state['username'], size=70), unsafe_allow_html=True)
        uploaded_avatar = st.file_uploader("Profil Foto", type=['png', 'jpg'])
        if uploaded_avatar:
            if database.update_avatar(st.session_state['username'], uploaded_avatar): st.success("Yüklendi!"); time.sleep(1); st.rerun()
        
        with st.expander("İsim Değiştir"):
            new_name_input = st.text_input("Yeni İsim")
            change_count = database.get_user_change_count(st.session_state['username'])
            cost = 0 if change_count == 0 else 500000
            btn_label = "Ücretsiz Değiştir" if cost == 0 else f"{cost:,} Puan"
            if st.button(btn_label):
                if new_name_input:
                    ok, msg = database.change_username_logic(st.session_state['username'], new_name_input)
                    if ok: st.session_state['username'] = new_name_input; st.success(msg); time.sleep(2); st.rerun()
                    else: st.error(msg)
        
        st.divider()
        with st.expander("Arkadaş Ekle"):
            search_u = st.selectbox("Kişi Ara", database.get_searchable_users(st.session_state['username']))
            if st.button("Ekle"):
                ok, msg = database.send_friend_request(st.session_state['username'], search_u)
                if ok: st.success(msg)
                else: st.warning(msg)
        
        reqs = database.get_pending_requests(st.session_state['username'])
        if reqs:
            st.divider()
            st.write("📩 İstekler:")
            for r in reqs:
                c1, c2 = st.columns([2,1])
                c1.write(r[1])
                if c2.button("Kabul", key=f"acc_{r[0]}"):
                    database.accept_request(r[1], st.session_state['username'])
                    st.success("Oldu!"); st.rerun()

        if st.button("Çıkış"): st.session_state['logged_in']=False; st.rerun()

    st.markdown(f'<div class="top-bar"><div class="user-greeting">Merhaba, {st.session_state["username"]}</div><div class="role-badge">{st.session_state["user_role"]}</div></div>', unsafe_allow_html=True)
    
    noti_count = database.get_unread_notification_count(st.session_state['username'])
    noti_text = f"🔔 ({noti_count})" if noti_count > 0 else "🔔"
    menu_ops = ["📢 Kampüs Duvar", "💬 Mesaj", "🏆 Puan", "📚 Ders", "🎮 Oyun", "🛒 Mağaza", noti_text]
    if st.session_state['user_role'] == 'admin': menu_ops.append("⚙️ Admin")
    
    curr = st.session_state['active_menu']
    if curr.startswith("🔔") and curr != noti_text: curr = noti_text
    
    ix = 0
    if curr in menu_ops: ix = menu_ops.index(curr)
    sel = st.radio("", menu_ops, index=ix, horizontal=True, label_visibility="collapsed")
    if sel != st.session_state['active_menu']: st.session_state['active_menu'] = sel; st.rerun()

    if sel == "📢 Kampüs Duvar":
        st.subheader("Kampüs Duvar")
        
        my_score = server.get_score("GENEL", st.session_state['username'])
        POST_THRESHOLD = 1000000
        POST_COST = 100000
        
        if my_score >= POST_THRESHOLD or st.session_state['user_role'] == 'admin':
            with st.expander(f"✨ Paylaşım Yap (-{POST_COST:,} P)", expanded=False):
                with st.form("sh"):
                    def_val = st.session_state.get('draft_content', "")
                    txt = st.text_area("İçerik", value=def_val); img = st.file_uploader("Resim", type=['png','jpg'])
                    if st.form_submit_button("Paylaş"):
                        if my_score >= POST_COST:
                            database.add_score(st.session_state['username'], -POST_COST, "Post Ücreti")
                            database.add_post(st.session_state['username'], txt, img)
                            st.session_state['draft_content'] = ""
                            st.rerun()
                        else: st.error("Bakiye Yetersiz!")
        else:
            st.info(f"🔒 Paylaşım için {POST_THRESHOLD:,} Puan Gerekli. (Senin: {my_score:,})")

        for p in database.get_posts(20):
            # --- POST KARTI BAŞLANGIÇ ---
            st.markdown(f"""
            <div class="post-card-container">
                <div class="post-header">
                    {get_user_display_html(p[1], size=35)}
                    <span class="post-date">{p[4]}</span>
                </div>
                <div class="{get_post_style_css(p[1])} post-text">{p[2] if p[2] else ''}</div>
                {f'<img src="data:image/jpeg;base64,{p[3]}" class="post-img">' if p[3] else ''}
            </div>
            """, unsafe_allow_html=True)
            # --- POST KARTI BİTİŞ ---
            
            # --- BUTONLAR (KARTIN İÇİNDE GİBİ GÖRÜNEN ALT KISIM) ---
            # Kolonları dar tutuyoruz ki butonlar yan yana sıkışsın
            c1, c2, c3, c4, c5 = st.columns([1,1,1,1,6]) 
            
            with c1:
                if st.button(f"❤️ {p[5]}", key=f"l_{p[0]}"): database.like_post(p[0]); st.rerun()
            with c2:
                # Yorum ikonu sadece görsel, aşağıda expander var
                st.markdown("<div style='text-align:center; padding-top:5px;'>💬</div>", unsafe_allow_html=True)
            with c3:
                if st.button("🔄", key=f"r_{p[0]}"): 
                    st.session_state['draft_content'] = f"Alıntı (@{p[1]}): {p[2]}"
                    st.rerun()
            
            if st.session_state['username'] == p[1] or st.session_state['user_role'] == 'admin':
                with c4:
                    with st.popover("⚙️"):
                        with st.form(key=f"e_{p[0]}"):
                            new_t = st.text_area("Düzenle", p[2])
                            if st.form_submit_button("Ok"): database.update_post(p[0], new_t); st.rerun()
                        if st.button("Sil", key=f"d_{p[0]}"): database.delete_post(p[0]); st.rerun()

            comments = database.get_comments(p[0])
            if comments:
                with st.expander(f"Yorumlar ({len(comments)})"):
                    for c in comments: st.markdown(f"<div class='comment-box'>{get_user_display_html(c[0], size=20)} &nbsp; {c[1]}</div>", unsafe_allow_html=True)
            
            with st.form(f"c{p[0]}", clear_on_submit=True):
                ct = st.text_input("Yorum Yaz...", label_visibility="collapsed")
                if st.form_submit_button("Gönder"): 
                    if ct: database.add_comment(p[0], st.session_state['username'], ct); st.rerun()
            
            st.write("") # Boşluk bırak

    elif sel == "🛒 Mağaza":
        st.header("Mağaza 💎")
        st.metric("Bakiye", f"{server.get_score('GENEL', st.session_state['username']):,} P")
        
        items = {
            "🖼️ Çerçeve": [
                {"n": "Gold", "c": 50000, "t": "frame", "v": "Gold", "css": "frame-Gold"},
                {"n": "Neon", "c": 150000, "t": "frame", "v": "Neon", "css": "frame-Neon"},
                {"n": "Alev", "c": 300000, "t": "frame", "v": "Fire", "css": "frame-Fire"},
                {"n": "Matrix", "c": 500000, "t": "frame", "v": "Matrix", "css": "frame-Matrix"},
                {"n": "Kral", "c": 2000000, "t": "frame", "v": "King", "css": "frame-King"}
            ],
            "✨ İsim": [
                {"n": "Glitch", "c": 100000, "t": "name", "v": "Glitch", "css": "name-Glitch"},
                {"n": "Alevli", "c": 400000, "t": "name", "v": "Fire", "css": "name-Fire"},
                {"n": "Altın", "c": 750000, "t": "name", "v": "Gold", "css": "name-Gold"},
                {"n": "Gökkuşağı", "c": 1000000, "t": "name", "v": "Rainbow", "css": "name-Rainbow"}
            ],
            "🔤 Font": [
                {"n": "Cinzel", "c": 150000, "t": "font", "v": "Cinzel", "css": "font-Cinzel"},
                {"n": "Orbitron", "c": 250000, "t": "font", "v": "Orbitron", "css": "font-Orbitron"},
                {"n": "Rye", "c": 350000, "t": "font", "v": "Rye", "css": "font-Rye"},
                {"n": "Dans", "c": 500000, "t": "font", "v": "Dancing", "css": "font-Dancing"},
                {"n": "Metalik", "c": 1000000, "t": "font", "v": "Metallic", "css": "font-Metallic"}
            ],
            "🔰 Ünvan": [
                {"n": "Çırak", "c": 10000, "t": "title", "v": "Çırak", "css": ""},
                {"n": "Usta", "c": 100000, "t": "title", "v": "Usta", "css": ""},
                {"n": "Bilgin", "c": 500000, "t": "title", "v": "Bilgin", "css": ""},
                {"n": "LORD", "c": 5000000, "t": "title", "v": "LORD", "css": ""}
            ]
        }
        
        tabs = st.tabs(["Ürünler", "🎁 Hediye Gönder"])
        
        with tabs[0]:
            cat_tabs = st.tabs(list(items.keys()))
            for i, (cat, products) in enumerate(items.items()):
                with cat_tabs[i]:
                    html_code = '<div class="shop-grid">'
                    for p in products:
                        buy_link = f"?action=buy&u={st.session_state['username']}&t={p['t']}&v={p['v']}&c={p['c']}"
                        
                        preview = ""
                        if p['t'] == 'frame':
                            # Placeholder resim eklendi
                            preview = f'<div style="position:relative;width:40px;height:40px;"><img src="https://via.placeholder.com/40/CCCCCC/FFFFFF?text=U" style="border-radius:50%;"><div class="{p["css"]}" style="position:absolute;top:-3px;left:-3px;width:46px;height:46px;"></div></div>'
                        elif p['t'] == 'name': preview = f'<div class="{p["css"]}" style="font-size:0.7rem">İsim</div>'
                        elif p['t'] == 'font': preview = f'<div class="{p["css"]}" style="font-size:0.9rem">Aa</div>'
                        elif p['t'] == 'title': preview = f'<span class="title-badge">{p["v"]}</span>'
                        
                        html_code += f"""
                        <div class="shop-item">
                            {preview}
                            <div class="shop-name">{p['n']}</div>
                            <a href="{buy_link}" target="_top" style="text-decoration:none;width:100%;">
                                <div class="shop-price">{p['c']:,} P</div>
                            </a>
                        </div>"""
                    html_code += "</div>"
                    st.markdown(html_code, unsafe_allow_html=True)

        with tabs[1]:
            st.info("Arkadaşına hediye gönder! (Puan senden düşer)")
            target_user = st.selectbox("Kime:", database.get_searchable_users(st.session_state['username']))
            gifts = [
                {"n": "Sıcak Çay", "c": 2000, "i": "☕"}, {"n": "Kahve", "c": 5000, "i": "🧖"}, 
                {"n": "Çikolata", "c": 8000, "i": "🍫"}, {"n": "Gül", "c": 15000, "i": "🌹"}, 
                {"n": "Tost", "c": 20000, "i": "🥪"}, {"n": "Hamburger", "c": 30000, "i": "🍔"},
                {"n": "Ayıcık", "c": 60000, "i": "🧸"}, {"n": "Kupa", "c": 100000, "i": "🏆"},
                {"n": "Elmas", "c": 500000, "i": "💎"}, {"n": "Araba", "c": 2000000, "i": "🏎️"}
            ]
            html_code = '<div class="shop-grid">'
            for g in gifts:
                gift_link = f"?action=gift&u={st.session_state['username']}&t={target_user}&g={g['n']}&c={g['c']}"
                html_code += f"""
                <div class="shop-item" style="height:120px;">
                    <div class="gift-icon">{g['i']}</div>
                    <div class="shop-name">{g['n']}</div>
                    <a href="{gift_link}" target="_top" style="text-decoration:none;width:100%;">
                        <div class="shop-price">{g['c']:,}</div>
                    </a>
                </div>"""
            html_code += "</div>"
            st.markdown(html_code, unsafe_allow_html=True)

    elif sel.startswith("🔔"):
        st.header("Bildirimler")
        notis = database.get_unread_notifications(st.session_state['username'])
        if not notis: st.info("Temiz.")
        else:
            for who, comment, post_summary in notis:
                st.warning(f"**{who}**: '{comment}' (Gönderi: {post_summary[:20]}...)")
            database.mark_notifications_read(st.session_state['username'])

    elif sel == "💬 Mesaj":
        friends = database.get_friends(st.session_state['username'])
        if st.session_state['user_role'] == 'student' and "admin" not in friends: friends.insert(0, "admin")
        if st.session_state['user_role'] == 'admin': friends = [u[0] for u in database.get_all_users() if u[0]!="admin"]
        target = st.selectbox("Kişi", friends) if friends else None
        if target:
            for s, m, t in database.get_conversation(st.session_state['username'], target):
                ava_html = get_user_display_html(s, size=30)
                align = "flex-direction:row-reverse;background:#2563eb" if s == st.session_state['username'] else "flex-direction:row;background:#334155"
                st.markdown(f"""<div style='display:flex;{align};align-items:center;margin:5px;'>{ava_html} <div style='padding:10px;border-radius:10px;margin:5px;color:white;background:inherit'>{m}</div></div>""", unsafe_allow_html=True)
            if txt := st.chat_input("Yaz..."): database.send_message(st.session_state['username'], target, txt); st.rerun()
        else: st.info("Kimse yok.")

    elif sel == "🏆 Puan":
        st.metric("Puan", server.get_score("GENEL", st.session_state['username']))
        st.dataframe(server.get_leaderboard("GENEL"), use_container_width=True)

    elif sel == "📚 Ders":
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

    elif sel == "🎮 Oyun":
        gm = st.selectbox("Seç", ["Finans İmparatoru", "Asset Matrix"])
        sc = server.get_score("GENEL", st.session_state['username'])
        if gm == "Finans İmparatoru": components.html(get_finance_game_html(sc, st.session_state['username']), height=600)
        else: components.html(get_matrix_game_html(st.session_state['username']), height=750)

    elif sel == "⚙️ Admin":
        st.header("Admin")
        st.subheader("Kullanıcı Düzenle")
        all_u = [u[0] for u in database.get_all_users()]
        target_u = st.selectbox("Kullanıcı", all_u)
        new_p = st.number_input("Puan Ekle", value=0)
        if st.button("Güncelle"): database.add_score(target_u, new_p, "Admin"); st.success("Tamam!")
        st.divider()
        st.subheader("Casus Modu")
        spy_u = st.selectbox("Kimin Mesajları?", all_u, key="spu")
        spy_p = st.selectbox("Kiminle?", all_u, key="spp")
        if st.button("Oku"):
            msgs = database.get_conversation(spy_u, spy_p)
            for s, m, t in msgs: st.write(f"**{s}**: {m} ({t})")
        st.divider()
        if st.button("Sil"): database.delete_user(target_u); st.error("Silindi!"); st.rerun()
