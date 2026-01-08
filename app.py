import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import requests
import json
import os
import time
import random
import database
from datetime import datetime

# ==========================================
# 1. SAYFA VE STİL AYARLARI
# ==========================================
st.set_page_config(
    page_title="Bağarası ÇPAL - Dijital Kampüs",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- ÖZEL CSS (Görsel Düzenlemeler) ---
st.markdown("""
<style>
    /* Giriş Ekranı */
    .login-container { display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center; margin-top: 50px; }
    .login-title { font-family: 'Helvetica', sans-serif; font-size: 2.5rem; font-weight: 700; color: #FFD700; text-shadow: 0 0 15px rgba(0,0,0,0.8); margin-bottom: 20px;}
    
    /* Sol Menü Özelleştirme */
    section[data-testid="stSidebar"] {
        background-color: #0f172a;
    }
    div[data-testid="stSidebarUserContent"] {
        padding-top: 20px;
    }
    
    /* Menü Butonları */
    .menu-btn-home { 
        width: 100%; background-color: #2563eb; color: white; padding: 12px; 
        border-radius: 8px; text-align: center; font-weight: bold; margin-bottom: 10px; cursor: pointer; border: 1px solid #3b82f6;
    }
    .menu-btn-home:hover { background-color: #1d4ed8; }
    
    .menu-btn-exit { 
        width: 100%; background-color: #dc2626; color: white; padding: 12px; 
        border-radius: 8px; text-align: center; font-weight: bold; margin-top: auto; cursor: pointer; border: 1px solid #ef4444;
    }
    .menu-btn-exit:hover { background-color: #b91c1c; }

    /* Üst Bar (Karşılama) - Daha kompakt */
    .top-bar {
        background-color: #1e293b; padding: 8px 15px; border-radius: 0 0 8px 8px; 
        display: flex; justify-content: space-between; align-items: center;
        margin-bottom: 10px; border-bottom: 2px solid #FFD700; font-size: 0.85rem;
    }
    .user-greeting { font-weight: bold; color: #e2e8f0; }
    .role-badge { background: #FFD700; color: #000; padding: 2px 8px; border-radius: 4px; font-weight: 900; font-size: 0.7rem; }
</style>
""", unsafe_allow_html=True)

# Veritabanı Başlat
database.create_database()
if not database.login_user("admin", "6626"):
    database.add_user("admin", "6626", "admin")

# Aktivite Güncelleme
if "logged_in" in st.session_state and st.session_state.logged_in:
    database.update_activity(st.session_state.username)

# ==========================================
# 2. SABİTLER
# ==========================================
GITHUB_BASE_URL = "https://raw.githubusercontent.com/zulfikarsitaci-prog/s-navkamp-/main"
URL_TYT_DATA = f"{GITHUB_BASE_URL}/tyt_data.json"
URL_TYT_PDF = f"{GITHUB_BASE_URL}/tytson8.pdf"
URL_MESLEK_SORULAR = f"{GITHUB_BASE_URL}/sorular.json"
URL_LIFESIM = f"{GITHUB_BASE_URL}/lifesim_data.json"

# ==========================================
# 3. OYUN KODLARI (GÜNCEL)
# ==========================================

def get_finance_game_html(start_money):
    return f"""<!DOCTYPE html><html lang="tr"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><style>body{{background:#0f172a;color:#fff;font-family:sans-serif;text-align:center;padding:10px;margin:0;}}.dash{{display:flex;justify-content:space-between;background:#1e293b;padding:10px;border-radius:10px;margin-bottom:10px;}}.val{{font-size:18px;font-weight:bold;color:#34d399;}}.btn{{background:radial-gradient(circle,#3b82f6,#1d4ed8);width:80px;height:80px;border-radius:50%;margin:0 auto 15px;display:flex;align-items:center;justify-content:center;font-size:30px;cursor:pointer;box-shadow:0 0 15px #3b82f6;}}.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(100px,1fr));gap:5px;}}.card{{background:#1e293b;padding:5px;border-radius:5px;border:1px solid #334155;cursor:pointer;font-size:10px;}}.card:hover{{border-color:#facc15;}}.bank{{width:100%;padding:10px;background:#10b981;border:none;color:white;border-radius:5px;margin-top:10px;font-weight:bold;}}.code{{background:#fff;color:#000;padding:5px;margin-top:5px;display:none;font-family:monospace;}}</style></head><body><div class="dash"><div>SERMAYE<br><div id="m" class="val">{start_money}</div></div><div>GELİR<br><div id="c" style="color:#facc15">0.0</div></div></div><div class="btn" onclick="clk()">👆</div><div class="grid" id="g"></div><button class="bank" onclick="bank()">🏦 BANKAYA AKTAR</button><div id="code" class="code"></div><script>let m={start_money},s={start_money},a=[{{n:"Limonata",c:150,g:0.5,k:0}},{{n:"Simit",c:1000,g:3.5,k:0}},{{n:"Kantin",c:5000,g:15,k:0}},{{n:"Kırtasiye",c:20000,g:55,k:0}},{{n:"Yazılım",c:80000,g:200,k:0}},{{n:"Fabrika",c:1000000,g:3500,k:0}}];function u(){{document.getElementById('m').innerText=Math.floor(m).toLocaleString();let t=a.reduce((x,y)=>x+(y.k*y.g),0);document.getElementById('c').innerText=t.toFixed(1);let h=document.getElementById('g');h.innerHTML='';a.forEach((x,i)=>{{let p=Math.floor(x.c*Math.pow(1.2,x.k));let d=document.createElement('div');d.className='card';d.onclick=()=>b(i);d.innerHTML=`<b>${{x.n}}</b> (${{x.k}})<br><span style="color:#f87171">${{p.toLocaleString()}}</span><br><span style="color:#34d399">+${{x.g}}</span>`;h.appendChild(d)}})}}function clk(){{m+=1;u()}}function b(i){{let x=a[i],p=Math.floor(x.c*Math.pow(1.2,x.k));if(m>=p){{m-=p;x.k++;u()}}}}function bank(){{let p=m-s;if(p<50){{alert("En az 50 TL kar etmelisin.");return}}let c=`FNK-${{Math.floor(p).toString(16).toUpperCase()}}-${{Math.floor(Math.random()*999)}}`;document.getElementById('code').innerText=c;document.getElementById('code').style.display='block';s=m;}}setInterval(()=>{{let t=a.reduce((x,y)=>x+(y.k*y.g),0);if(t>0){{m+=t;u()}}}},1000);u();</script></body></html>"""

ASSET_MATRIX_HTML = """
<!DOCTYPE html>
<html lang="tr">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
<style>
@import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@700&display=swap');
body { margin:0; background:#050505; color:#FFD700; font-family:'Cinzel',serif; text-align:center; touch-action:none; user-select:none; overflow:hidden; }
#game { position:absolute; top:0; left:0; width:100%; height:100%; display:flex; flex-direction:column; align-items:center; }
.head { width:90%; display:flex; justify-content:space-between; padding:10px; background:#111; border-bottom:1px solid #FFD700; margin-bottom:5px; font-size:14px; }
canvas { background:#0f0f0f; border:2px solid #333; touch-action:none; }
.btn { margin-top:10px; background:linear-gradient(135deg,#FFD700,#B8860B); border:none; padding:10px 20px; font-weight:bold; border-radius:20px; cursor:pointer; z-index:100; }
#code { margin-top:5px; background:#222; color:#fff; padding:5px; display:none; font-family:monospace; border:1px dashed #FFD700; z-index:100; }
.ovl { position:absolute; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.95); display:flex; flex-direction:column; justify-content:center; align-items:center; z-index:200; }
.hid { display:none !important; }
.bbtn { background:transparent; border:2px solid #FFD700; color:#FFD700; padding:15px 40px; font-size:18px; font-family:'Cinzel',serif; cursor:pointer; margin-top:20px; }
</style>
</head>
<body>
<div id="game">
    <div class="head"><div>VARLIK: <span id="s">0</span></div><div>SEVİYE: <span id="l">1</span></div></div>
    <canvas id="c"></canvas>
    <button class="btn" onclick="get()">🏦 BANKA</button>
    <div id="code"></div>
    <div id="start" class="ovl"><h1 style="color:#FFD700">SOCRATIC 8x10</h1><p style="color:#aaa">Blokları Yerleştir</p><button class="bbtn" onclick="init()">BAŞLA</button></div>
    <div id="end" class="ovl hid"><h1 style="color:#ff4444">İFLAS</h1><p style="color:#fff">Skor: <span id="fs">0</span></p><button class="bbtn" onclick="init()">TEKRAR</button></div>
</div>
<script>
const cvs=document.getElementById('c'), ctx=cvs.getContext('2d'), scoreEl=document.getElementById('s');
const COLS=8, ROWS=10; let SQ=30, grid=[], pieces=[], dragP=null, score=0, dragOff={x:0,y:0};
const SHAPES=[[[1]],[[1,1]],[[1],[1]],[[1,1],[1,1]],[[1,1,1]],[[1],[1],[1]],[[1,1,1,1]],[[1],[1],[1],[1]],[[1,0],[1,0],[1,1]],[[0,1],[0,1],[1,1]],[[1,1,0],[0,1,1]],[[0,1,1],[1,1,0]]];
function sz(){ 
    let w=window.innerWidth, h=window.innerHeight; 
    SQ = Math.floor(Math.min((w-20)/COLS, (h-150)/ROWS)); 
    cvs.width=SQ*COLS; cvs.height=(SQ*ROWS)+(SQ*3.5); d(); 
}
window.addEventListener('resize',sz);
function init(){ 
    grid=Array(ROWS).fill().map(()=>Array(COLS).fill(0)); score=0; scoreEl.innerText=0;
    document.getElementById('start').classList.add('hid'); document.getElementById('end').classList.add('hid'); document.getElementById('code').style.display='none';
    sz(); spawn(); 
}
function spawn(){
    pieces=[]; let y=(ROWS*SQ)+20, w=cvs.width/3;
    for(let i=0;i<3;i++){
        let s=SHAPES[Math.floor(Math.random()*SHAPES.length)];
        pieces.push({s:s, x:(w*i)+(w/2)-((s[0].length*SQ*0.6)/2), y:y, bx:(w*i)+(w/2)-((s[0].length*SQ*0.6)/2), by:y, sc:0.6, drag:false});
    }
    d(); check();
}
function d(){
    ctx.fillStyle="#050505"; ctx.fillRect(0,0,cvs.width,cvs.height);
    for(let r=0;r<ROWS;r++) for(let c=0;c<COLS;c++) {
        ctx.strokeStyle="#222"; ctx.strokeRect(c*SQ,r*SQ,SQ,SQ);
        if(grid[r][c]) dc(c*SQ,r*SQ,SQ,"#D500F9");
    }
    ctx.beginPath(); ctx.moveTo(0,ROWS*SQ); ctx.lineTo(cvs.width,ROWS*SQ); ctx.strokeStyle="#FFD700"; ctx.lineWidth=2; ctx.stroke();
    pieces.forEach(p=>{ if(!p.drag) ds(p.s,p.x,p.y,SQ*p.sc,"#888"); });
    if(dragP) {
        let {gx,gy} = gp(dragP.x, dragP.y);
        if(cp(dragP.s,gx,gy)) ds(dragP.s,gx*SQ,gy*SQ,SQ,"rgba(213,0,249,0.4)");
        ds(dragP.s,dragP.x,dragP.y,SQ,"#D500F9");
    }
}
function dc(x,y,s,c){ ctx.fillStyle=c; ctx.fillRect(x+1,y+1,s-2,s-2); ctx.strokeStyle="rgba(255,215,0,0.5)"; ctx.strokeRect(x+4,y+4,s-8,s-8); }
function ds(s,x,y,z,c){ for(let r=0;r<s.length;r++) for(let k=0;k<s[r].length;k++) if(s[r][k]) dc(x+(k*z),y+(r*z),z,c); }
function gp(x,y){ return {gx:Math.round(x/SQ), gy:Math.round(y/SQ)}; }
function cp(s,x,y){ for(let r=0;r<s.length;r++) for(let k=0;k<s[r].length;k++) if(s[r][k]){ let tx=x+k, ty=y+r; if(tx<0||tx>=COLS||ty<0||ty>=ROWS||grid[ty][tx]) return false; } return true; }
function pl(s,x,y){ for(let r=0;r<s.length;r++) for(let k=0;k<s[r].length;k++) if(s[r][k]) grid[y+r][x+k]=1; score+=10; cl(); scoreEl.innerText=score; }
function cl(){ 
    for(let r=0;r<ROWS;r++) if(grid[r].every(v=>v)) { grid[r].fill(0); score+=50; }
    for(let c=0;c<COLS;c++) { let f=true; for(let r=0;r<ROWS;r++) if(!grid[r][c]) f=false; if(f){ for(let r=0;r<ROWS;r++) grid[r][c]=0; score+=50; }}
}
function check(){
    if(!pieces.length) return; let move=false;
    pieces.forEach(p=>{ for(let r=0;r<ROWS;r++) for(let c=0;c<COLS;c++) if(cp(p.s,c,r)) move=true; });
    if(!move){ document.getElementById('fs').innerText=score; document.getElementById('end').classList.remove('hid'); }
}
function getPos(e){ let r=cvs.getBoundingClientRect(), t=e.touches?e.touches[0]:e; return {x:t.clientX-r.left, y:t.clientY-r.top}; }
function down(e){
    let p=getPos(e);
    for(let i=pieces.length-1;i>=0;i--){
        let pi=pieces[i], w=pi.s[0].length*SQ*pi.sc, h=pi.s.length*SQ*pi.sc;
        if(p.x>=pi.x-20 && p.x<=pi.x+w+20 && p.y>=pi.y-20 && p.y<=pi.y+h+20){
            if(e.cancelable) e.preventDefault(); dragP=pi; pi.drag=true;
            dragOff.x=-(pi.s[0].length*SQ)/2; dragOff.y=-(pi.s.length*SQ)/2;
            pi.x=p.x+dragOff.x; pi.y=p.y+dragOff.y; d(); break;
        }
    }
}
function move(e){ if(dragP){ if(e.cancelable) e.preventDefault(); let p=getPos(e); dragP.x=p.x+dragOff.x; dragP.y=p.y+dragOff.y; d(); } }
function up(e){
    if(dragP){
        if(e.cancelable) e.preventDefault(); let {gx,gy}=gp(dragP.x,dragP.y);
        if(cp(dragP.s,gx,gy)){ pl(dragP.s,gx,gy); pieces=pieces.filter(p=>p!==dragP); if(!pieces.length) spawn(); else check(); }
        else { dragP.x=dragP.bx; dragP.y=dragP.by; dragP.drag=false; }
        dragP=null; d();
    }
}
cvs.addEventListener('mousedown',down); cvs.addEventListener('touchstart',down,{passive:false});
window.addEventListener('mousemove',move); window.addEventListener('touchmove',move,{passive:false});
window.addEventListener('mouseup',up); window.addEventListener('touchend',up,{passive:false});
function get(){ if(score<50){alert("50 Lazım");return} let c=`FNK-${(score*13).toString(16).toUpperCase()}-${Math.floor(Math.random()*999)}`; document.getElementById('code').innerText=c; document.getElementById('code').style.display='block'; score=0; scoreEl.innerText=0; grid=Array(ROWS).fill().map(()=>Array(COLS).fill(0)); d(); }
sz();
</script></body></html>
"""

# ==========================================
# 4. ARAYÜZ MANTIĞI
# ==========================================
if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "user_role" not in st.session_state: st.session_state.user_role = None
if "username" not in st.session_state: st.session_state.username = None
if "class_code" not in st.session_state: st.session_state.class_code = "GENEL"

# --- A) GİRİŞ EKRANI (ORTALANMIŞ) ---
if not st.session_state.logged_in:
    st.markdown('<div class="login-container"><h1 class="login-title">🎓 Bağarası ÇPAL Dijital Kampüs</h1></div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        tab_log, tab_reg = st.tabs(["Giriş Yap", "Kayıt Ol (Öğrenci)"])
        with tab_log:
            with st.form("login"):
                u = st.text_input("Kullanıcı Adı")
                p = st.text_input("Şifre", type="password")
                if st.form_submit_button("Giriş"):
                    user = database.login_user(u, p)
                    if user:
                        st.session_state.logged_in = True
                        st.session_state.user_role = user[3]
                        st.session_state.username = user[1]
                        if user[3] == "student": server.join_or_update_student("GENEL", user[1], 0)
                        st.rerun()
                    else: st.error("Hatalı bilgi.")
        with tab_reg:
            with st.form("reg"):
                nu = st.text_input("Kullanıcı Adı")
                np = st.text_input("Şifre", type="password")
                if st.form_submit_button("Kayıt Ol"):
                    if database.add_user(nu, np, "student"): st.success("Kayıt başarılı! Giriş yapınız.")
                    else: st.error("Bu isim kullanılıyor.")

# --- B) UYGULAMA İÇİ ---
else:
    unread_msgs = database.get_unread_messages(st.session_state.username)
    if unread_msgs:
        for m in unread_msgs:
            st.toast(f"📩 {m[1]}: {m[2]}", icon="🔔")
            database.mark_as_read(m[0])

    # --- SOL MENÜ (DÜZENLENDİ) ---
    with st.sidebar:
        # 1. ANA MENÜYE DÖN (EN ÜSTTE)
        if st.button("🏠 Ana Menüye Dön"): st.rerun()
        
        st.divider()
        st.title(st.session_state.username)
        st.caption(f"Yetki: {st.session_state.user_role}")
        
        with st.expander("📬 Mesaj Kutusu"):
            msgs = database.get_my_messages(st.session_state.username)
            if msgs:
                for m in msgs: st.info(f"**{m[1]}**: {m[2]}\n\n*{m[3]}*")
            else: st.caption("Kutunuz boş.")

        if st.session_state.user_role == "student":
            code = st.text_input("Sınıf Kodu", placeholder="Örn: 1234")
            if st.button("Sınıfa Geç"):
                st.session_state.class_code = code
                server.join_or_update_student(code, st.session_state.username)
                st.success(f"Sınıf: {code}"); time.sleep(0.5); st.rerun()
        
        # 2. ÇIKIŞ YAP (EN ALTTA)
        st.markdown("<div style='margin-top: 50px;'></div>", unsafe_allow_html=True)
        if st.button("🚪 Çıkış Yap"): 
            st.session_state.logged_in = False; st.rerun()

    # --- ÜST BAR ---
    role_tr = "Öğrenci" if st.session_state.user_role == "student" else "Öğretmen/Yönetici"
    st.markdown(f'<div class="top-bar"><div class="user-greeting">Merhaba, {st.session_state.username}</div><div class="role-badge">{role_tr}</div></div>', unsafe_allow_html=True)

    # --- SOHBET FONKSİYONLARI ---
    def render_chat(other_user):
        if not other_user: return
        st.markdown(f"### 💬 {other_user} ile Sohbet")
        messages = database.get_conversation(st.session_state.username, other_user)
        for sender, msg, timestamp in messages:
            with st.chat_message("user" if sender == st.session_state.username else "assistant"):
                st.write(msg)
                st.caption(f"{sender} - {timestamp}")
        if prompt := st.chat_input("Mesaj yaz..."):
            database.send_message(st.session_state.username, other_user, prompt)
            st.rerun()
        database.mark_messages_as_read(st.session_state.username, other_user)

    def render_global_chat():
        st.markdown("### 🌍 Kampüs Meydanı")
        try:
            msgs = database.get_global_messages(50)
            for m in msgs:
                with st.chat_message("assistant" if m[0] != st.session_state.username else "user", avatar="👤"):
                    st.markdown(f"**{m[0]}**: {m[1]}")
                    st.caption(m[2])
        except: st.warning("Sohbet yükleniyor...")
        if prompt := st.chat_input("Meydana seslen..."):
            try: database.send_global_message(st.session_state.username, prompt); st.rerun()
            except: pass

    # --- İÇERİK ---
    if st.session_state.user_role == "admin":
        st.header("⚙️ Yönetim Paneli")
        col_on, col_chat = st.columns([1, 2])
        with col_on:
            st.subheader("🟢 Online")
            online = database.get_online_users(5)
            if online: st.dataframe(pd.DataFrame(online), use_container_width=True)
            else: st.info("Kimse yok.")
            if st.button("Yenile"): st.rerun()
        with col_chat:
            st.subheader("💬 Canlı Destek")
            all_users = [u[0] for u in database.get_all_users() if u[0] != "admin"]
            target_user = st.selectbox("Sohbet Başlat:", all_users)
            render_chat(target_user)
        st.divider()
        t1, t2 = st.tabs(["Kullanıcı Ekle", "Kullanıcı Sil"])
        with t1:
            with st.form("admin_add"):
                nu = st.text_input("Kullanıcı"); np = st.text_input("Şifre"); nr = st.selectbox("Rol", ["teacher", "student", "admin"])
                if st.form_submit_button("Ekle"):
                    if database.add_user(nu, np, nr): st.success("Eklendi")
                    else: st.error("Hata")
        with t2:
            all_u = database.get_all_users()
            tod = st.selectbox("Silinecek", [u[0] for u in all_u])
            if st.button("Sil"):
                if tod!="admin": database.delete_user(tod); st.rerun()

    elif st.session_state.user_role in ["student", "teacher"]:
        if st.session_state.user_role == "teacher":
            st.success("👨‍🏫 ÖĞRETMEN MODU")
            if "created_code" not in st.session_state:
                st.session_state.created_code = str(random.randint(1000, 9999))
                server.create_class(st.session_state.created_code)
                st.session_state.class_code = st.session_state.created_code
            c1, c2 = st.columns(2)
            with c1: st.info(f"Ders Kodu: {st.session_state.created_code}")
            with c2: st.write(f"Aktif: {server.get_active_students_in_class(st.session_state.created_code)}")
            st.divider()

        t1, t2, t3, t4, t5 = st.tabs(["🏆 Kampüs", "💬 Sosyal", "📚 Dersler", "🎮 Oyunlar", "💼 LifeSim"])
        
        with t1:
            c1, c2 = st.columns([1,2])
            with c1:
                st.metric("Puan", f"{server.get_score(st.session_state.class_code, st.session_state.username)} ₺")
                if st.session_state.user_role == "student":
                    kod = st.text_input("Puan Kodu")
                    if st.button("Yükle"):
                        res, msg = server.redeem_code(st.session_state.class_code, st.session_state.username, kod)
                        if res: st.success("Yüklendi"); time.sleep(1); st.rerun()
                        else: st.error(msg)
                if st.session_state.user_role == "teacher":
                    with st.form("ann"):
                        t = st.text_input("Başlık"); c = st.text_area("İçerik")
                        if st.form_submit_button("Yayınla"): database.add_announcement(t, c, st.session_state.username); st.success("Yayınlandı")
            with c2:
                st.subheader("Duyurular")
                anns = database.get_announcements()
                for a in anns: st.info(f"**{a[1]}**: {a[2]}")
                st.subheader("Sıralama")
                st.dataframe(server.get_leaderboard(st.session_state.class_code), use_container_width=True)

        with t2:
            chat_type = st.radio("Sohbet Modu:", ["🌍 Genel Sohbet", "🔒 Özel Mesaj"], horizontal=True)
            if chat_type == "🌍 Genel Sohbet": render_global_chat()
            else:
                friends = database.get_friends(st.session_state.username)
                if st.session_state.user_role == 'student': friends.append("admin") 
                if not friends: st.info("Arkadaşın yok.")
                else: target = st.selectbox("Kiminle?", friends); render_chat(target)
            with st.expander("Arkadaş Ekle / İstekler"):
                pending = database.get_pending_requests(st.session_state.username)
                if pending:
                    for req_id, sender in pending:
                        c1, c2 = st.columns([3, 1])
                        c1.write(f"**{sender}** seni ekledi."); 
                        if c2.button("Kabul", key=f"acc_{req_id}"): database.accept_request(sender, st.session_state.username); st.success("Oldu!"); st.rerun()
                st.divider()
                searchable = database.get_searchable_students(st.session_state.username)
                if searchable:
                    target_s = st.selectbox("Öğrenci Seç", searchable)
                    if st.button("İstek Gönder"): res, msg = database.send_friend_request(st.session_state.username, target_s); st.success(msg)

        with t3:
            ders_modu = st.radio("Seç:", ["TYT Çalışma", "Meslek Soruları", "Okul Yazılıları (JSON)"], horizontal=True)
            st.divider()
            if ders_modu == "TYT Çalışma":
                tyt_data = fetch_json_data(URL_TYT_DATA)
                if tyt_data:
                    dersler = sorted(list(set([v.get('ders') for v in tyt_data.values() if 'ders' in v])))
                    sel = st.selectbox("Ders", dersler)
                    pages = [k for k, v in tyt_data.items() if v.get('ders') == sel]
                    if pages:
                        pg = st.selectbox("Sayfa", pages); det = tyt_data[pg]
                        c_p, c_q = st.columns([1.5, 1])
                        with c_p: st.markdown(f'<embed src="{URL_TYT_PDF}#page={pg}" width="100%" height="600px">', unsafe_allow_html=True)
                        with c_q:
                            with st.form("tyt"):
                                ans = {}
                                for i, q in enumerate(det['sorular']): st.write(f"Soru {q}"); ans[i] = st.radio("Cevap", ['A','B','C','D','E'], key=f"t{i}", horizontal=True)
                                if st.form_submit_button("Kontrol"):
                                    d = sum([1 for i, q in enumerate(det['sorular']) if ans[i] == det['cevaplar'][i]])
                                    sc = d*50; st.success(f"Puan: {sc}"); 
                                    if sc>0: server.join_or_update_student(st.session_state.class_code, st.session_state.username, sc)
            elif ders_modu == "Meslek Soruları":
                m_data = fetch_json_data(URL_MESLEK_SORULAR)
                if m_data:
                    root = m_data.get("KONU_TARAMA", m_data)
                    sinif = st.selectbox("Sınıf", list(root.keys()))
                    if sinif:
                        ders = st.selectbox("Ders", list(root[sinif].keys()))
                        if ders:
                            konu = st.selectbox("Konu", list(root[sinif][ders].keys()))
                            if konu:
                                qs = root[sinif][ders][konu]
                                with st.form("mes"):
                                    mans = {}
                                    for i, q in enumerate(qs): st.write(f"**{i+1}. {q['soru']}**"); mans[i] = st.radio("Cevap", q['secenekler'], key=f"m{i}")
                                    if st.form_submit_button("Bitir"):
                                        dm = sum([1 for i, q in enumerate(qs) if mans[i] == q['cevap']])
                                        pm = dm*100; st.success(f"Puan: {pm}");
                                        if pm>0: server.join_or_update_student(st.session_state.class_code, st.session_state.username, pm)
            elif ders_modu == "Okul Yazılıları (JSON)":
                EXAM_DATA = load_local_exams()
                if not EXAM_DATA: st.warning("Sınav yok.")
                else:
                    eg = st.selectbox("Sınıf", list(EXAM_DATA.keys()))
                    if eg:
                        el = st.selectbox("Ders", list(EXAM_DATA[eg].keys()))
                        if el:
                            qs = EXAM_DATA[eg][el]; st.subheader(f"{el}")
                            with st.form("js_ex"):
                                for i, q in enumerate(qs):
                                    st.markdown(f"**{i+1}:** {q.get('text') or q.get('question')}")
                                    if q['type']=='test': st.radio("Seçim", q['options'], key=f"j{i}")
                                    elif q['type']=='text': st.text_input("Cevap", key=f"j{i}")
                                    elif q['type']=='scenario': 
                                        for j, sub in enumerate(q['sub_questions']): st.text_input(sub['q'], key=f"j{i}_{j}")
                                    elif q['type']=='calculation': 
                                        for j, inp in enumerate(q['inputs']): st.number_input(inp['label'], key=f"j{i}_{j}")
                                    st.divider()
                                if st.form_submit_button("Bitir"):
                                    score = sum([q.get('points',0) for q in qs]); st.success(f"Puan: {score}")
                                    server.join_or_update_student(st.session_state.class_code, st.session_state.username, score)

        with t4:
            gm = st.selectbox("Oyun", ["Finans İmparatoru", "Asset Matrix"])
            current_balance = server.get_score(st.session_state.class_code, st.session_state.username)
            if gm == "Finans İmparatoru": components.html(get_finance_game_html(current_balance), height=600)
            else: components.html(ASSET_MATRIX_HTML, height=750)

        with t5: components.html(load_lifesim(), height=800, scrolling=True)
