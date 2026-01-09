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
    defaults = {"logged_in": False, "user_role": None, "username": None, "class_code": "GENEL", "active_menu": "📢 Kampüs Duvar"}
    for k, v in defaults.items():
        if k not in st.session_state: st.session_state[k] = v
init_state()

# --- CSS ---
st.markdown("""
<style>
    .login-container { text-align: center; margin-top: 50px; }
    .login-title { font-family: 'Helvetica', sans-serif; font-size: 2.2rem; font-weight: 700; color: #FFD700; text-shadow: 0 0 10px rgba(0,0,0,0.5); }
    .top-bar { background: #1e293b; padding: 10px; border-radius: 8px; display: flex; justify-content: space-between; border-bottom: 2px solid #FFD700; margin-bottom: 10px; }
    .user-greeting { font-weight: bold; color: #e2e8f0; }
    .comment-sec { background: #0f172a; padding: 10px; margin-top: 10px; border-radius: 5px; font-size: 0.9rem; }
    div[data-testid="stRadio"] > div { flex-direction: row; justify-content: center; gap: 20px; flex-wrap: wrap; }
    
    /* MAĞAZA KARTLARI */
    .shop-card {
        background-color: #0f172a; border: 1px solid #334155; border-radius: 15px; padding: 20px;
        text-align: center; transition: transform 0.2s; height: 100%; display: flex; flex-direction: column;
        align-items: center; justify-content: space-between;
    }
    .shop-card:hover { transform: scale(1.02); border-color: #FFD700; }
    .price-tag { background: #10b981; color: white; padding: 5px 10px; border-radius: 15px; font-weight: bold; margin-top: 10px; font-size: 0.9rem; }
    
    /* AVATAR VE ÇERÇEVELER */
    .avatar-container { position: relative; display: inline-block; vertical-align: middle; }
    .avatar-img { width: 100%; height: 100%; border-radius: 50%; object-fit: cover; }
    .frame-overlay { position: absolute; pointer-events: none; z-index: 2; border-radius: 50%; }
    
    /* --- ÇERÇEVE STİLLERİ --- */
    .frame-bronze { border: 3px solid #cd7f32; }
    .frame-silver { border: 3px solid #c0c0c0; box-shadow: 0 0 8px #c0c0c0; }
    .frame-gold { border: 3px solid #FFD700; box-shadow: 0 0 12px #FFD700; }
    .frame-neon { border: 3px solid #00ffff; box-shadow: 0 0 10px #00ffff, inset 0 0 5px #00ffff; }
    .frame-cyber { border: 3px dashed #ff00ff; box-shadow: 0 0 8px #ff00ff; }
    .frame-fire { border: 3px solid #ff4500; box-shadow: 0 0 15px #ff4500; animation: pulse 1.5s infinite; }
    .frame-ice { border: 3px solid #e0f7fa; box-shadow: 0 0 15px #00bfff; }
    .frame-rainbow { 
        border: 4px solid transparent; 
        background-image: linear-gradient(white, white), linear-gradient(to right, red, orange, yellow, green, blue, indigo, violet); 
        background-origin: border-box; background-clip: content-box, border-box;
    }
    .frame-matrix { border: 3px dotted #00ff00; box-shadow: 0 0 10px #00ff00; }
    .frame-king { 
        border: 4px solid #ffd700; 
        box-shadow: 0 0 25px #ffd700, inset 0 0 10px #ff0000;
        background-image: linear-gradient(45deg, transparent 95%, #ffd700 100%);
    }

    @keyframes pulse { 0% { box-shadow: 0 0 5px #ff4500; } 50% { box-shadow: 0 0 20px #ff4500; } 100% { box-shadow: 0 0 5px #ff4500; } }
    iframe { width: 100% !important; }
</style>
""", unsafe_allow_html=True)

# Veritabanı
try:
    database.create_database()
    if not database.login_user("admin", "6626"): database.add_user("admin", "6626", "admin")
except: pass
if st.session_state['logged_in']: database.update_activity(st.session_state['username'])

# --- AVATAR HTML (DÜZELTİLDİ) ---
def get_avatar_html(username, size=50):
    ava_data, frame_type = database.get_avatar_and_frame(username)
    img_src = f"data:image/jpeg;base64,{ava_data}" if ava_data else "https://via.placeholder.com/150?text=U"
    
    frame_html = ""
    if frame_type:
        # HATA DÜZELTİLDİ: Artık 'frame-' eklemiyoruz, veritabanından geleni direkt kullanıyoruz.
        f_size = size + 10
        f_offset = -5
        frame_html = f'<div class="frame-overlay {frame_type}" style="width:{f_size}px;height:{f_size}px;top:{f_offset}px;left:{f_offset}px;"></div>'

    return f"""
    <div class="avatar-container" style="width:{size}px;height:{size}px;">
        <img src="{img_src}" class="avatar-img">
        {frame_html}
    </div>
    """

class SchoolServer:
    def join_or_update_student(self, c, u, p=0): 
        if p!=0: database.add_score(u, p, "Oyun")
        return database.get_total_score(u)
    def get_score(self, c, u): return database.get_total_score(u)
    def get_leaderboard(self, c):
        df = pd.DataFrame(database.get_leaderboard_data(), columns=["Öğrenci","Puan"])
        return df if not df.empty else pd.DataFrame(columns=["Öğrenci","Puan"])
    def buy_item(self, username, item_type, item_name, cost):
        if item_type == "frame":
            success, msg = database.buy_frame(username, item_name, cost)
            return success, msg
        return False, "Hata."

server = SchoolServer()

@st.cache_data
def load_local_exams():
    if os.path.exists("exams.json"):
        try:
            with open("exams.json", "r", encoding="utf-8") as f: return json.load(f)
        except: return {}
    return {}

# --- TRANSFER JS ---
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

def get_finance_game_html(start, user):
    js = get_transfer_js(user)
    return f"""<!DOCTYPE html><html><head><meta name="viewport" content="width=device-width, initial-scale=1.0"><style>body{{background:#0f172a;color:white;font-family:sans-serif;text-align:center;padding:10px}} .grid{{display:grid;grid-template-columns:repeat(3,1fr);gap:5px}} .card{{background:#1e293b;padding:5px;border-radius:5px;font-size:10px;cursor:pointer}} .btn{{background:#3b82f6;width:80px;height:80px;border-radius:50%;margin:15px auto;display:flex;align-items:center;justify-content:center;font-size:30px;cursor:pointer}} .bank{{background:#10b981;color:white;width:100%;padding:10px;border:none;border-radius:5px;margin-top:10px;font-weight:bold}}</style></head><body><div>💰 <span id="m">{start}</span></div><div class="btn" onclick="c()">👆</div><div class="grid" id="g"></div><button id="bBtn" class="bank" onclick="autoTransfer()">🏦 AKTAR</button><script>let money={start}, startBalance={start}; const a=[{{n:"Limonata",c:100,g:1,k:0}},{{n:"Simit",c:500,g:5,k:0}},{{n:"Kantin",c:2000,g:25,k:0}},{{n:"Yazılım",c:10000,g:150,k:0}},{{n:"Fabrika",c:50000,g:800,k:0}},{{n:"Banka",c:200000,g:5000,k:0}}]; function u(){{document.getElementById('m').innerText=Math.floor(money).toLocaleString(); let h=''; a.forEach((x,i)=>{{let p=Math.floor(x.c*Math.pow(1.2,x.k)); h+=`<div class="card" onclick="b(${{i}})"><b>${{x.n}}</b> (${{x.k}})<br><span style="color:#f87171">${{p}}</span><br><span style="color:#34d399">+${{x.g}}</span></div>`}}); document.getElementById('g').innerHTML=h;}} function c(){{money++;u()}} function b(i){{let x=a[i],p=Math.floor(x.c*Math.pow(1.2,x.k)); if(money>=p){{money-=p;x.k++;u()}}}} setInterval(()=>{{let g=a.reduce((t,x)=>t+(x.k*x.g),0); if(g>0){{money+=g;u()}}}},1000); u(); {js} </script></body></html>"""

def get_matrix_game_html(user):
    js = get_transfer_js(user)
    return f"""<!DOCTYPE html><html><head><meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no"><style>body{{background:#050505;color:#00ffff;margin:0;overflow:hidden;touch-action:none;text-align:center}} canvas{{background:#111;border:2px solid #333;margin-top:10px}} .btn{{position:absolute;top:10px;right:10px;background:#ff00ff;border:none;padding:5px 15px;border-radius:15px;font-weight:bold;color:white}}</style></head><body><div style="padding:10px;display:flex;justify-content:space-between"><span>PUAN: <span id="s">0</span></span><button id="mBtn" class="btn" onclick="autoTransfer()">AKTAR</button></div><canvas id="c"></canvas><script>const cvs=document.getElementById('c'), ctx=cvs.getContext('2d'); const R=10, C=8; let SQ=25, grid=[], pieces=[], drag=null, score=0; const SHAPES=[[[1]],[[1,1]],[[1],[1]],[[1,1,1]],[[1,0],[1,0],[1,1]]]; function rs(){{let w=window.innerWidth, h=window.innerHeight; SQ=Math.floor(Math.min((w-20)/C,(h-100)/R)); SQ=Math.min(SQ,35); cvs.width=SQ*C; cvs.height=SQ*R+120; d();}} window.addEventListener('resize',rs); function init(){{grid=Array(R).fill().map(()=>Array(C).fill(0)); score=0; document.getElementById('s').innerText=0; rs(); sp();}} function sp(){{pieces=[]; let y=R*SQ+20, w=cvs.width/3; for(let i=0;i<3;i++){{let s=SHAPES[Math.floor(Math.random()*SHAPES.length)]; pieces.push({{s:s,x:w*i+5,y:y,bx:w*i+5,by:y,sc:0.6}});}} d();}} function d(){{ctx.fillStyle="#000000"; ctx.fillRect(0,0,cvs.width,cvs.height); for(let r=0;r<R;r++) for(let c=0;c<C;c++) {{ctx.strokeStyle="#333"; ctx.lineWidth=1; ctx.strokeRect(c*SQ,r*SQ,SQ,SQ); if(grid[r][c]) {{ctx.fillStyle="#00ffff"; ctx.fillRect(c*SQ+3,r*SQ+3,SQ-6,SQ-6); ctx.strokeStyle="#ff00ff"; ctx.strokeRect(c*SQ+3,r*SQ+3,SQ-6,SQ-6);}}}} ctx.strokeStyle="white"; ctx.beginPath(); ctx.moveTo(0,R*SQ); ctx.lineTo(cvs.width,R*SQ); ctx.stroke(); pieces.forEach(p=>{{if(p!==drag) ds(p.s,p.x,p.y,SQ*p.sc,"#555")}}); if(drag) ds(drag.s,drag.x,drag.y,SQ,"#ff00ff");}} function ds(s,x,y,z,c){{ctx.fillStyle=c; for(let r=0;r<s.length;r++) for(let k=0;k<s[r].length;k++) if(s[r][k]) ctx.fillRect(x+k*z,y+r*z,z,z);}} function gp(e){{let r=cvs.getBoundingClientRect(),t=e.touches?e.touches[0]:e; return {{x:t.clientX-r.left,y:t.clientY-r.top}}}} function chk(){{for(let r=0;r<R;r++) if(grid[r].every(x=>x)) {{grid[r].fill(0); score+=50;}} for(let c=0;c<C;c++) {{let f=true; for(let r=0;r<R;r++) if(!grid[r][c]) f=false; if(f) {{for(let r=0;r<R;r++) grid[r][c]=0; score+=50;}}}} document.getElementById('s').innerText=score; if(pieces.length===0) sp();}} cvs.addEventListener('touchstart',e=>{{let p=gp(e); pieces.forEach(pi=>{{if(p.x>=pi.x&&p.x<=pi.x+60&&p.y>=pi.y&&p.y<=pi.y+60) drag=pi;}});}},{{passive:false}}); cvs.addEventListener('touchmove',e=>{{e.preventDefault(); if(drag){{let p=gp(e); drag.x=p.x-20; drag.y=p.y-20; d();}}}},{{passive:false}}); cvs.addEventListener('touchend',e=>{{if(drag){{let gx=Math.round(drag.x/SQ), gy=Math.round(drag.y/SQ), fit=true; for(let r=0;r<drag.s.length;r++) for(let c=0;c<drag.s[r].length;c++) if(drag.s[r][c]) {{if(gx+c<0||gx+c>=C||gy+r>=R||grid[gy+r][gx+c]) fit=false;}} if(fit){{for(let r=0;r<drag.s.length;r++) for(let c=0;c<drag.s[r].length;c++) if(drag.s[r][c]) grid[gy+r][gx+c]=1; pieces=pieces.filter(p=>p!==drag); score+=10; chk();}} else {{drag.x=drag.bx; drag.y=drag.by;}} drag=null; d();}}}},{{passive:false}}); init(); {js} </script></body></html>"""

if "t_user" in st.query_params and "t_amt" in st.query_params:
    try:
        u, a = st.query_params["t_user"], int(st.query_params["t_amt"])
        role = database.get_user_role(u)
        if role:
            st.session_state['logged_in'], st.session_state['username'], st.session_state['user_role'] = True, u, role
            st.session_state['active_menu'] = "🎮 Oyun"
            if a > 0: database.add_score(u, a, "Oyun"); st.toast(f"✅ {a} Puan Eklendi!", icon="💰"); time.sleep(1)
            st.query_params.clear(); st.rerun()
    except: st.query_params.clear()

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
                else: st.error("Hatalı bilgi.")
        with st.expander("Kayıt Ol"):
            with st.form("reg"):
                nu = st.text_input("Yeni Kullanıcı"); np = st.text_input("Şifre", type="password")
                if st.form_submit_button("Kayıt"):
                    if database.add_user(nu, np, "student"): st.success("Başarılı!"); st.rerun()
                    else: st.error("Dolu.")
else:
    with st.sidebar:
        st.markdown(get_avatar_html(st.session_state['username'], size=80), unsafe_allow_html=True)
        st.title(st.session_state['username'])
        uploaded_avatar = st.file_uploader("Profil", type=['png', 'jpg', 'jpeg'])
        if uploaded_avatar:
            if database.update_avatar(st.session_state['username'], uploaded_avatar):
                st.success("Yüklendi!"); time.sleep(1); st.rerun()
        if st.button("Çıkış"): st.session_state['logged_in']=False; st.rerun()

    st.markdown(f'<div class="top-bar"><div class="user-greeting">Merhaba, {st.session_state["username"]}</div><div class="role-badge">{st.session_state["user_role"]}</div></div>', unsafe_allow_html=True)
    
    noti_count = database.get_unread_notification_count(st.session_state['username'])
    noti_text = f"🔔 ({noti_count})" if noti_count > 0 else "🔔"
    
    menu_ops = ["📢 Kampüs Duvar", "💬 Mesaj", "🏆 Puan", "📚 Ders", "🎮 Oyun", "🛒 Mağaza", noti_text]
    if st.session_state['user_role'] == 'admin': menu_ops.append("⚙️ Admin")
    
    current_sel = st.session_state['active_menu']
    if current_sel.startswith("🔔") and current_sel != noti_text: current_sel = noti_text
    
    ix = 0
    if current_sel in menu_ops: ix = menu_ops.index(current_sel)
    sel = st.radio("", menu_ops, index=ix, horizontal=True, label_visibility="collapsed")
    if sel != st.session_state['active_menu']: st.session_state['active_menu'] = sel; st.rerun()

    if sel == "📢 Kampüs Duvar":
        st.subheader("Kampüs Duvar")
        with st.expander("Paylaş", expanded=False):
            with st.form("sh"):
                txt = st.text_area("İçerik"); img = st.file_uploader("Resim", type=['png','jpg','jpeg'])
                if st.form_submit_button("Paylaş"):
                    if txt or img: database.add_post(st.session_state['username'], txt, img); st.rerun()
        
        for p in database.get_posts(20):
            with st.container():
                # --- YENİ DÜZEN: Avatar+İsim SOLDA, Buton SAĞDA ---
                col_header, col_action = st.columns([5, 1])
                
                with col_header:
                    ava_html = get_avatar_html(p[1], size=40)
                    st.markdown(f"""<div style="display:flex;align-items:center;margin-bottom:5px;">{ava_html} <div style="margin-left:10px;"><b>{p[1]}</b><br><small style="color:#aaa">{p[4]}</small></div></div>""", unsafe_allow_html=True)
                
                with col_action:
                    # Yetki Kontrolü
                    if st.session_state['username'] == p[1] or st.session_state['user_role'] == 'admin':
                        with st.popover("⋮"):
                            new_txt = st.text_area("Düzenle", value=p[2], key=f"e{p[0]}")
                            if st.button("Kaydet", key=f"s{p[0]}"): database.update_post(p[0], new_txt); st.rerun()
                            if st.button("Sil", key=f"d{p[0]}"): database.delete_post(p[0]); st.rerun()

                if p[2]: st.write(p[2])
                if p[3]: st.markdown(f'<img src="data:image/jpeg;base64,{p[3]}" style="max-width:100%;border-radius:10px">', unsafe_allow_html=True)
                
                c1, c2 = st.columns([1,4])
                if c1.button(f"❤️ {p[5]}", key=f"l{p[0]}"): database.like_post(p[0]); st.rerun()
                comments = database.get_comments(p[0])
                if comments:
                    with st.expander(f"💬 Yorumlar ({len(comments)})"):
                        for c in comments: 
                            c_ava_html = get_avatar_html(c[0], size=25)
                            st.markdown(f"""<div class='comment-sec' style="display:flex;align-items:center;">{c_ava_html} <div style="margin-left:5px;"><b>{c[0]}</b>: {c[1]}</div></div>""", unsafe_allow_html=True)
                with st.popover("Yorum"):
                    with st.form(f"c{p[0]}"):
                        ct = st.text_input("Yorum")
                        if st.form_submit_button("Yolla"): database.add_comment(p[0], st.session_state['username'], ct); st.rerun()
                st.divider()

    elif sel == "🛒 Mağaza":
        st.header("Puan Mağazası 💎")
        my_score = server.get_score("GENEL", st.session_state['username'])
        st.metric("Puanın", f"{my_score:,} ₺".replace(",", "."))
        
        products = [
            {"name": "Bronz", "cost": 10000, "css": "frame-bronze", "desc": "Başlangıç seviyesi."},
            {"name": "Gümüş", "cost": 50000, "css": "frame-silver", "desc": "Parlak gümüş."},
            {"name": "Altın", "cost": 100000, "css": "frame-gold", "desc": "Zenginlik göstergesi."},
            {"name": "Alev", "cost": 250000, "css": "frame-fire", "desc": "Yanıyor!"},
            {"name": "Buz", "cost": 250000, "css": "frame-ice", "desc": "Buz gibi serin."},
            {"name": "Neon", "cost": 300000, "css": "frame-neon", "desc": "Geceleri parlar."},
            {"name": "Gökkuşağı", "cost": 500000, "css": "frame-rainbow", "desc": "Tüm renkler senin."},
            {"name": "Siber", "cost": 750000, "css": "frame-cyber", "desc": "Gelecekten geldi."},
            {"name": "Matrix", "cost": 1000000, "css": "frame-matrix", "desc": "Kodun kendisi ol."},
            {"name": "KRAL TACI", "cost": 2500000, "css": "frame-king", "desc": "Sadece efsaneler için."}
        ]
        
        rows = [products[i:i+3] for i in range(0, len(products), 3)]
        for row in rows:
            cols = st.columns(3)
            for i, p in enumerate(row):
                with cols[i]:
                    with st.container():
                        st.markdown(f"""
                        <div class="shop-card">
                            <div style="position:relative;width:60px;height:60px;margin:0 auto;">
                                <img src="https://via.placeholder.com/60/1e293b/ffffff?text=U" style="border-radius:50%;">
                                <div class="{p['css']}" style="position:absolute;top:-5px;left:-5px;width:70px;height:70px;"></div>
                            </div>
                            <h3 style="margin:10px 0 5px 0;">{p['name']}</h3>
                            <small style="color:#94a3b8;min-height:40px;display:block;">{p['desc']}</small>
                            <div class="price-tag">{p['cost']:,} P</div>
                        </div>
                        """, unsafe_allow_html=True)
                        if st.button("SATIN AL", key=f"buy_{p['name']}"):
                            ok, msg = server.buy_item(st.session_state['username'], "frame", p["css"], p["cost"])
                            if ok: st.success(msg); time.sleep(1); st.rerun()
                            else: st.error(msg)
            st.write("")

    elif sel.startswith("🔔"):
        st.header("Bildirimler")
        notis = database.get_unread_notifications(st.session_state['username'])
        if not notis: st.info("Yeni bildirim yok.")
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
                ava_html = get_avatar_html(s, size=30)
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
