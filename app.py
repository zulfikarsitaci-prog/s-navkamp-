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

def init_state():
    defaults = {
        "logged_in": False, "user_role": None, "username": None, 
        "class_code": "GENEL", "active_menu": "📢 Kampüs Duvar", 
        "draft_content": "",
        "captcha_q": None, "captcha_a": None,
        "open_comments": [] 
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

# --- CSS ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@700&family=Orbitron:wght@700&family=Rye&family=Dancing+Script:wght@700&family=Metal+Mania&display=swap');

    .login-container { text-align: center; margin-top: 20px; margin-bottom: 30px; }
    .login-sub { color: #94a3b8; font-size: 1rem; margin-bottom: 5px; font-family: sans-serif; letter-spacing: 1px; }
    .login-main { font-family: 'Cinzel', serif; color: #FFD700; font-size: 2.2rem; text-shadow: 2px 2px 4px #000; line-height: 1.2; margin: 10px 0; font-weight: bold; }
    .login-bottom { color: #cbd5e1; font-family: 'Orbitron', sans-serif; font-size: 0.9rem; margin-top: 5px; }

    .top-bar { background: #1e293b; padding: 10px; border-radius: 8px; display: flex; justify-content: space-between; border-bottom: 2px solid #FFD700; margin-bottom: 10px; }
    
    .post-card {
        background-color: #1e293b; 
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 15px;
        margin-bottom: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
    .post-header { display: flex; align-items: center; border-bottom: 1px solid #334155; padding-bottom: 8px; margin-bottom: 8px; }
    .post-content { color: #e2e8f0; font-size: 0.95rem; line-height: 1.5; white-space: pre-wrap; margin-bottom: 5px; }
    
    div.stButton > button {
        background-color: transparent !important;
        border: none !important;
        color: #94a3b8 !important;
        padding: 0px 5px !important;
        font-size: 1.3rem !important;
        box-shadow: none !important;
        margin-right: 15px !important;
    }
    div.stButton > button:hover { color: #FFD700 !important; transform: scale(1.1); }
    
    div[data-testid="column"] { padding: 0 !important; min-width: 0 !important; margin: 0 !important; flex: 0 0 auto !important; width: auto !important; }
    div[data-testid="stHorizontalBlock"] { align-items: center !important; flex-wrap: nowrap !important; }

    .comment-box { background: #0f172a; padding: 8px; border-radius: 6px; margin-top: 6px; font-size: 0.85rem; border-left: 3px solid #334155; }
    div[data-testid="stRadio"] > div { flex-direction: row; justify-content: center; gap: 8px; flex-wrap: wrap; }
    
    .shop-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 6px; margin-top: 10px; }
    .shop-item { background: #0f172a; border: 1px solid #334155; border-radius: 8px; padding: 5px; text-align: center; display: flex; flex-direction: column; align-items: center; justify-content: space-between; height: 110px; }
    .shop-name { font-size: 0.65rem; color: #cbd5e1; }
    .shop-price { background: #10b981; color: white; padding: 2px 8px; border-radius: 8px; font-size: 0.65rem; }

    .font-Cinzel { font-family: 'Cinzel', serif; } .font-Orbitron { font-family: 'Orbitron', sans-serif; }
    .font-Rye { font-family: 'Rye', serif; } .font-Dancing { font-family: 'Dancing Script', cursive; }
    .font-Metallic { font-family: 'Metal Mania', cursive; color: #b0b0b0; text-shadow: 2px 2px 0px #000; }

    .avatar-container { position: relative; display: inline-block; margin-right: 8px; }
    .avatar-img { width: 40px; height: 40px; border-radius: 50%; object-fit: cover; }
    .frame-overlay { position: absolute; top: -3px; left: -3px; width: 46px; height: 46px; pointer-events: none; }
    
    .frame-Gold { border: 2px solid #FFD700; border-radius: 50%; box-shadow: 0 0 5px #FFD700; }
    .frame-Neon { border: 2px solid #00ffff; border-radius: 50%; box-shadow: 0 0 5px #00ffff; }
    .frame-Fire { border: 2px solid #ff4500; border-radius: 50%; box-shadow: 0 0 10px #ff4500; }
    .frame-King { border: 3px solid #ffd700; border-radius: 50%; box-shadow: 0 0 10px #ffd700; }
    .frame-Matrix { border: 2px dotted #00ff00; border-radius: 50%; }
    .name-Glitch { color: #00ffff; text-shadow: 1px 0 #ff00ff; font-weight: bold; }
    .name-Fire { color: #ff4500; text-shadow: 0 0 3px #ff0000; font-weight: bold; }
    .name-Gold { background: linear-gradient(to right, #BF953F, #FCF6BA, #B38728); -webkit-background-clip: text; color: transparent; font-weight: 900; }
    .post-Cyan { color: #00ffff !important; } .post-Lime { color: #00ff00 !important; } .post-Pink { color: #ff69b4 !important; } .post-Gold { color: #ffd700 !important; }
    .title-badge { background: #334155; color: #94a3b8; padding: 1px 5px; border-radius: 3px; font-size: 0.6rem; margin-left: 4px; }
</style>
""", unsafe_allow_html=True)

# --- GÖRSEL YARDIMCILAR ---
def get_user_display_html(username, size=40):
    ava, frame, name_style, _, font_style, title = database.get_user_styles(username)
    img_src = f"data:image/jpeg;base64,{ava}" if ava else "https://via.placeholder.com/150/CCCCCC/FFFFFF?text=U"
    f_html = f'<div class="frame-overlay frame-{frame}"></div>' if frame else ""
    classes = f"{f'name-{name_style}' if name_style else ''} {f'font-{font_style}' if font_style else ''}"
    return f'<div style="display:flex;align-items:center;"><div class="avatar-container"><img src="{img_src}" class="avatar-img">{f_html}</div><div style="margin-left:10px;"><div class="{classes}" style="font-size:0.9rem;">{username} {f"<span class='title-badge'>{title}</span>" if title else ""}</div></div></div>'

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
    def send_gift(self, s, r, item, cost): return database.send_gift(s, r, item, cost) # Bu fonksiyon database'de yoksa diye kontrol edin, aşağıda ekledim.
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
            if database.get_total_score(u) >= 0: # Basit kontrol
                st.session_state.update({'logged_in':True, 'username':u, 'active_menu':"🎮 Oyun"})
                if a > 0: database.add_score(u, a, "Oyun"); st.toast(f"✅ {a} Puan!", icon="💰"); time.sleep(1)
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
    st.markdown('<div class="login-container"><div class="login-sub">Muhasebe ve Finansman Alanı</div><div class="login-main">DİJİTAL GELİŞİM PLATFORMU</div><div class="login-sub">~ Dijital Kampüs ~</div></div>', unsafe_allow_html=True)
    
    with st.sidebar:
        # --- ACİL SIFIRLAMA BUTONU ---
        if st.button("⚠️ SİSTEMİ SIFIRLA"):
            try:
                if os.path.exists("education_platform.db"):
                    os.remove("education_platform.db")
                    st.success("Sistem temizlendi! Sayfayı yenile.")
                    time.sleep(1)
                    st.rerun()
            except: st.error("Silinemedi.")

    with st.container():
        with st.form("login"):
            u = st.text_input("Kullanıcı Adı")
            p = st.text_input("Şifre", type="password")
            if st.form_submit_button("Giriş"):
                user = database.login_user(u, p)
                if user:
                    st.session_state.update({'logged_in':True, 'username':user[1], 'user_role':user[3]})
                    # ACTIVITY LOG EKLENDİ
                    database.update_activity(user[1])
                    st.rerun()
                else: st.error("Hatalı!")
        
        with st.expander("Kayıt Ol"):
            with st.form("reg"):
                nu = st.text_input("Kullanıcı"); np = st.text_input("Şifre", type="password")
                st.write(f"Güvenlik: **{st.session_state['captcha_q']} = ?**")
                ans = st.number_input("Cevap", step=1)
                
                if st.form_submit_button("Kayıt"):
                    if ans == st.session_state['captcha_a']:
                        success, rank = database.add_user(nu, np, "student")
                        if success:
                            st.session_state['captcha_q'] = None 
                            if rank <= 10: 
                                st.balloons()
                                st.success(f"TEBRİKLER! {rank}. kişi olarak KURUCU ünvanı kazandın!")
                            else: st.success("Başarılı! Giriş yapabilirsin.")
                        else: st.error("İsim alınmış.")
                    else:
                        st.error("Yanlış cevap!")
                        st.session_state['captcha_q'] = None
                        time.sleep(1)
                        st.rerun()
else:
    # --- ACTIVITY UPDATE ---
    database.update_activity(st.session_state['username'])

    with st.sidebar:
        st.markdown(get_user_display_html(st.session_state['username'], size=70), unsafe_allow_html=True)
        st.write("") 
        
        with st.expander("⚙️ Hesabım"):
            new_name_input = st.text_input("Yeni İsim")
            change_count = database.get_user_change_count(st.session_state['username'])
            cost = 0 if change_count == 0 else 500000
            btn_label = "Değiştir (Ücretsiz)" if cost == 0 else f"Değiştir ({cost:,} P)"
            if st.button(btn_label):
                if new_name_input:
                    ok, msg = database.change_username_logic(st.session_state['username'], new_name_input)
                    if ok: st.session_state['username'] = new_name_input; st.success(msg); time.sleep(2); st.rerun()
                    else: st.error(msg)
            
            st.divider()
            uploaded_avatar = st.file_uploader("Fotoğraf", type=['png', 'jpg'])
            if uploaded_avatar:
                if database.update_avatar(st.session_state['username'], uploaded_avatar): st.success("Yüklendi!"); time.sleep(1); st.rerun()
            
            st.divider()
            search_u = st.selectbox("Arkadaş Ara", database.get_searchable_users(st.session_state['username']))
            if st.button("Ekle"):
                ok, msg = database.send_friend_request(st.session_state['username'], search_u)
                if ok: st.success(msg)
                else: st.warning(msg)

        reqs = database.get_pending_requests(st.session_state['username'])
        if reqs:
            st.info("📩 İstekler")
            for r in reqs:
                c1, c2 = st.columns([2,1])
                c1.write(r[1])
                if c2.button("Kabul", key=f"acc_{r[0]}"):
                    database.accept_request(r[1], st.session_state['username'])
                    st.success("Oldu!"); st.rerun()

        st.write("")
        if st.button("🚪 Çıkış Yap"): st.session_state['logged_in']=False; st.rerun()

    st.markdown(f'<div class="top-bar"><div class="user-greeting">Merhaba, {st.session_state["username"]}</div><div class="role-badge">{st.session_state["user_role"]}</div></div>', unsafe_allow_html=True)
    
    database.mark_notifications_read(st.session_state['username'])
    menu = ["📢 Kampüs Duvar", "💬 Mesaj", "🏆 Puan", "📚 Ders", "🎮 Oyun", "🛒 Mağaza"]
    if st.session_state['user_role'] == 'admin': menu.append("⚙️ Admin")
    sel = st.radio("", menu, horizontal=True, label_visibility="collapsed")

    if sel == "📢 Kampüs Duvar":
        st.subheader("Kampüs Duvar")
        
        my_score = server.get_score("GENEL", st.session_state['username'])
        POST_THRESHOLD = 1000000
        POST_COST = 100000
        
        if my_score >= POST_THRESHOLD or st.session_state['user_role'] == 'admin':
            with st.expander(f"✨ Paylaşım (-{POST_COST:,} P)", expanded=False):
                with st.form("sh"):
                    def_val = st.session_state.get('draft_content', "")
                    txt = st.text_area("İçerik", value=def_val); img = st.file_uploader("Resim", type=['png','jpg'])
                    if st.form_submit_button("Paylaş"):
                        if my_score >= POST_COST:
                            database.add_score(st.session_state['username'], -POST_COST, "Post")
                            database.add_post(st.session_state['username'], txt, img)
                            st.session_state['draft_content'] = ""
                            st.rerun()
                        else: st.error("Bakiye Yetersiz!")
        else:
            st.info(f"🔒 Paylaşım için {POST_THRESHOLD:,} P gerekli.")

        for p in database.get_posts(20):
            st.markdown(f"""
            <div class="post-card">
                <div class="post-header">
                    {get_user_display_html(p[1], size=35)}
                    <span style="color:#94a3b8;font-size:0.7rem;margin-left:auto;">{p[4]}</span>
                </div>
                <div class="{get_post_style_css(p[1])} post-content">{p[2] if p[2] else ''}</div>
                {f'<img src="data:image/jpeg;base64,{p[3]}" class="post-image">' if p[3] else ''}
            </div>
            """, unsafe_allow_html=True)
            
            if p[2]:
                yt = extract_youtube_link(p[2])
                if yt: st.video(yt)

            # --- DÜZGÜN, SAĞLAM İKON YAPISI ---
            c1, c2, c3, c4 = st.columns([0.15, 0.15, 0.15, 0.55]) 
            
            with c1: 
                if st.button(f"❤️ {p[5]}", key=f"l_{p[0]}"): database.like_post(p[0]); st.rerun()
            with c2: 
                if st.button("💬", key=f"c_btn_{p[0]}"):
                    if p[0] in st.session_state['open_comments']: st.session_state['open_comments'].remove(p[0])
                    else: st.session_state['open_comments'].append(p[0])
                    st.rerun()
            with c3:
                if st.button("🔄", key=f"r_{p[0]}"): st.session_state['draft_content'] = f"Alıntı (@{p[1]}): {p[2]}"; st.rerun()
            
            if st.session_state['username'] == p[1] or st.session_state['user_role'] == 'admin':
                with c4:
                    _, sc2 = st.columns([0.8, 0.2])
                    with sc2:
                        with st.popover("⋮"):
                            with st.form(key=f"e_{p[0]}"):
                                new_t = st.text_area("Düzenle", p[2])
                                if st.form_submit_button("Ok"): database.update_post(p[0], new_t); st.rerun()
                            if st.button("Sil", key=f"d_{p[0]}"): database.delete_post(p[0]); st.rerun()

            if p[0] in st.session_state['open_comments']:
                comments = database.get_comments(p[0])
                if comments:
                    for c in comments: st.markdown(f"<div class='comment-box'>{get_user_display_html(c[0], size=20)} &nbsp; {c[1]}</div>", unsafe_allow_html=True)
                
                with st.form(f"c_form_{p[0]}", clear_on_submit=True):
                    ct = st.text_input("Yorum Yaz...", label_visibility="collapsed")
                    if st.form_submit_button("Gönder"): 
                        if ct: database.add_comment(p[0], st.session_state['username'], ct); st.rerun()
            st.write("") 

    elif sel == "🛒 Mağaza":
        st.header("Mağaza 💎")
        st.metric("Bakiye", f"{server.get_score('GENEL', st.session_state['username']):,} P")
        
        tabs = st.tabs(["Çerçeve", "İsim", "Font"])
        
        with tabs[0]: 
            items = [{"n": "Gold", "c": 50000, "t": "frame", "v": "Gold"}, {"n": "Neon", "c": 150000, "t": "frame", "v": "Neon"}, {"n": "Alev", "c": 300000, "t": "frame", "v": "Fire"}, {"n": "Kral", "c": 2000000, "t": "frame", "v": "King"}]
            cols = st.columns(4)
            for i, it in enumerate(items):
                with cols[i]:
                    st.markdown(f"<div class='shop-item'><div class='shop-name'>{it['n']}</div><div class='shop-price'>{it['c']:,}</div></div>", unsafe_allow_html=True)
                    if st.button("Al", key=f"bi_{i}"):
                        ok, msg = database.buy_item(st.session_state['username'], it['t'], it['v'], it['c'])
                        if ok: st.success(msg); time.sleep(1); st.rerun()
                        else: st.error(msg)

    elif sel == "💬 Mesaj":
        st.subheader("Mesajlaşma")
        all_u = database.get_all_users_list(st.session_state['username'])
        friends = database.get_friends(st.session_state['username'])
        target = st.selectbox("Kime:", friends) if friends else None
        
        if target:
            msgs = database.get_conversation(st.session_state['username'], target)
            for m in msgs:
                align = "row-reverse" if m[0] == st.session_state['username'] else "row"
                bg = "#2563eb" if m[0] == st.session_state['username'] else "#334155"
                st.markdown(f"""<div style="display:flex;flex-direction:{align};margin-bottom:5px;">
                    <div style="background:{bg};padding:8px;border-radius:10px;max-width:70%;">{m[1]}</div>
                </div>""", unsafe_allow_html=True)
            
            with st.form("msg_form", clear_on_submit=True):
                msg_txt = st.text_input("Mesaj")
                if st.form_submit_button("Gönder"):
                    if msg_txt:
                        database.send_message(st.session_state['username'], target, msg_txt)
                        st.rerun()
        else: st.info("Henüz arkadaşın yok.")

    elif sel == "🏆 Puan":
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
        if st.button("Sil"): database.delete_user(target_u); st.error("Silindi!"); st.rerun()
