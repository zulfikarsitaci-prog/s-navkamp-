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

st.set_page_config(page_title="Bağarası ÇPAL - Dijital Kampüs", page_icon="🎓", layout="wide", initial_sidebar_state="collapsed")

database.create_database()
if not database.login_user("admin", "6626"): database.add_user("admin", "6626", "admin")
if "logged_in" in st.session_state and st.session_state.logged_in: database.update_activity(st.session_state.username)

GITHUB_BASE_URL = "https://raw.githubusercontent.com/zulfikarsitaci-prog/s-navkamp-/main"
URL_TYT_DATA = f"{GITHUB_BASE_URL}/tyt_data.json"
URL_TYT_PDF = f"{GITHUB_BASE_URL}/tytson8.pdf"
URL_MESLEK_SORULAR = f"{GITHUB_BASE_URL}/sorular.json"
URL_LIFESIM = f"{GITHUB_BASE_URL}/lifesim_data.json"

# --- OYUN KODLARI ---
FINANCE_GAME_HTML = """<!DOCTYPE html><html lang="tr"><head><meta charset="UTF-8"><style>body{background-color:#0f172a;color:#e2e8f0;font-family:sans-serif;text-align:center;margin:0;}.dashboard{display:flex;justify-content:space-between;background:#1e293b;padding:15px;border-radius:12px;margin-bottom:20px;}.clicker-btn{background:radial-gradient(circle,#3b82f6 0%,#1d4ed8 100%);width:110px;height:110px;border-radius:50%;margin:0 auto 20px;display:flex;align-items:center;justify-content:center;font-size:30px;cursor:pointer;}.asset-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(130px,1fr));gap:8px;}.asset-card{background:#1e293b;padding:10px;border-radius:8px;border:1px solid #334155;cursor:pointer;}.asset-card:hover{border-color:#facc15;}</style></head><body><div class="dashboard"><div>NAKİT: <span id="money" style="color:#34d399;font-weight:bold;">0</span> ₺</div><div>GELİR: <span id="cps" style="color:#facc15">0.0</span> /sn</div></div><div class="clicker-btn" onclick="manualWork()">👆</div><div class="asset-grid" id="market"></div><button onclick="generateCode()" style="margin-top:10px;padding:10px;background:#10b981;border:none;color:white;border-radius:5px;cursor:pointer;">🏦 BANKA</button><div id="transferCode" style="margin-top:10px;background:white;color:black;padding:5px;display:none;"></div><script>let money=0;const assets=[{name:"Limonata",cost:150,gain:0.5,count:0},{name:"Simit",cost:1000,gain:3.5,count:0},{name:"Kantin",cost:5000,gain:15,count:0},{name:"Kırtasiye",cost:20000,gain:55,count:0},{name:"Fabrika",cost:1000000,gain:3500,count:0}];function updateUI(){document.getElementById('money').innerText=Math.floor(money).toLocaleString();let t=assets.reduce((a,b)=>a+(b.count*b.gain),0);document.getElementById('cps').innerText=t.toFixed(1);const m=document.getElementById('market');m.innerHTML='';assets.forEach((a,i)=>{let c=Math.floor(a.cost*Math.pow(1.2,a.count));let d=document.createElement('div');d.className='asset-card';d.onclick=()=>buy(i);d.innerHTML=`<b>${a.name}</b> (${a.count})<br><span style="color:#f87171">${c}</span><br><span style="color:#34d399">+${a.gain}</span>`;m.appendChild(d)})}function manualWork(){money+=1;updateUI()}function buy(i){let a=assets[i];let c=Math.floor(a.cost*Math.pow(1.2,a.count));if(money>=c){money-=c;a.count++;updateUI()}}function generateCode(){if(money<50){alert("50 TL lazim");return}let val=Math.floor(money);let c=`FNK-${(val*13).toString(16).toUpperCase()}-${Math.floor(Math.random()*999)}`;document.getElementById('transferCode').innerText=c;document.getElementById('transferCode').style.display='block';money=0;updateUI()}setInterval(()=>{let t=assets.reduce((a,b)=>a+(b.count*b.gain),0);if(t>0){money+=t;updateUI()}},1000);updateUI();</script></body></html>"""

# --- ASSET MATRIX (8x8 Düzeltilmiş) ---
ASSET_MATRIX_HTML = """
<!DOCTYPE html>
<html>
<head>
<style>
body { background: #000; color: #FFD700; font-family: sans-serif; text-align: center; overflow: hidden; }
canvas { background: #111; border: 2px solid #FFD700; display: block; margin: 10px auto; }
button { background: #333; color: #FFD700; border: 1px solid #FFD700; padding: 10px 20px; font-size: 18px; margin: 5px; cursor: pointer; border-radius: 5px; }
button:active { background: #555; }
#ui { display: flex; justify-content: space-between; width: 320px; margin: 0 auto; font-weight: bold; }
#bankCode { background: white; color: black; padding: 5px; display: none; margin: 5px auto; width: 200px; }
</style>
</head>
<body>
<div id="ui"><span>VARLIK: <span id="score">0</span></span><span>SEVİYE: <span id="level">1</span></span></div>
<canvas id="gameCanvas" width="320" height="320"></canvas>
<div>
  <button onmousedown="move(-1)">⬅️</button>
  <button onmousedown="rotate()">🔄</button>
  <button onmousedown="move(1)">➡️</button>
  <button onmousedown="drop()">⬇️</button>
</div>
<button onclick="getTransferCode()" style="background:#FFD700; color:#000;">🏦 HAZİNE</button>
<div id="bankCode"></div>

<script>
const cvs = document.getElementById("gameCanvas");
const ctx = cvs.getContext("2d");
const ROW = 8, COL = 8, SQ = 40, VACANT = "#111";
let board = [], score = 0;

for(let r=0; r<ROW; r++){ board[r] = []; for(let c=0; c<COL; c++){ board[r][c] = VACANT; } }

function drawSquare(x,y,color){
    ctx.fillStyle = color; ctx.fillRect(x*SQ, y*SQ, SQ, SQ);
    ctx.strokeStyle = "#000"; ctx.strokeRect(x*SQ, y*SQ, SQ, SQ);
    if(color !== VACANT) { ctx.strokeStyle = "rgba(255,215,0,0.5)"; ctx.strokeRect(x*SQ+4, y*SQ+4, SQ-8, SQ-8); }
}

function drawBoard(){ for(let r=0; r<ROW; r++){ for(let c=0; c<COL; c++){ drawSquare(c, r, board[r][c]); } } }
drawBoard();

const PIECES = [ [Z,"#FF4444"], [S,"#44FF44"], [T,"#FFFF44"], [O,"#44FFFF"], [L,"#FF44FF"], [I,"#4444FF"], [J,"#FFAA44"] ];
const Z=[[[1,1,0],[0,1,1],[0,0,0]],[[0,0,1],[0,1,1],[0,1,0]],[[0,0,0],[1,1,0],[0,1,1]],[[0,1,0],[1,1,0],[1,0,0]]];
const S=[[[0,1,1],[1,1,0],[0,0,0]],[[0,1,0],[0,1,1],[0,0,1]],[[0,0,0],[0,1,1],[1,1,0]],[[1,0,0],[1,1,0],[0,1,0]]];
const T=[[[0,1,0],[1,1,1],[0,0,0]],[[0,1,0],[0,1,1],[0,1,0]],[[0,0,0],[1,1,1],[0,1,0]],[[0,1,0],[1,1,0],[0,1,0]]];
const O=[[[0,0,0,0],[0,1,1,0],[0,1,1,0],[0,0,0,0]],[[0,0,0,0],[0,1,1,0],[0,1,1,0],[0,0,0,0]],[[0,0,0,0],[0,1,1,0],[0,1,1,0],[0,0,0,0]],[[0,0,0,0],[0,1,1,0],[0,1,1,0],[0,0,0,0]]];
const L=[[[0,0,1],[1,1,1],[0,0,0]],[[0,1,0],[0,1,0],[0,1,1]],[[0,0,0],[1,1,1],[1,0,0]],[[1,1,0],[0,1,0],[0,1,0]]];
const I=[[[0,1,0,0],[0,1,0,0],[0,1,0,0],[0,1,0,0]],[[0,0,0,0],[1,1,1,1],[0,0,0,0],[0,0,0,0]],[[0,0,1,0],[0,0,1,0],[0,0,1,0],[0,0,1,0]],[[0,0,0,0],[0,0,0,0],[1,1,1,1],[0,0,0,0]]];
const J=[[[1,0,0],[1,1,1],[0,0,0]],[[0,1,1],[0,1,0],[0,1,0]],[[0,0,0],[1,1,1],[0,0,1]],[[0,1,0],[0,1,0],[1,1,0]]];

let p = randomPiece();

function randomPiece(){
    let r = Math.floor(Math.random() * PIECES.length);
    return new Piece(PIECES[r][0], PIECES[r][1]);
}

function Piece(tetromino, color){
    this.tetromino = tetromino; this.color = color;
    this.tetrominoN = 0; this.activeTetromino = this.tetromino[this.tetrominoN];
    this.x = 2; this.y = -2;
}

Piece.prototype.fill = function(color){
    for(let r=0; r<this.activeTetromino.length; r++){
        for(let c=0; c<this.activeTetromino.length; c++){
            if(this.activeTetromino[r][c]){ drawSquare(this.x+c, this.y+r, color); }
        }
    }
}

Piece.prototype.draw = function(){ this.fill(this.color); }
Piece.prototype.unDraw = function(){ this.fill(VACANT); }

Piece.prototype.moveDown = function(){
    if(!this.collision(0,1,this.activeTetromino)){
        this.unDraw(); this.y++; this.draw();
    } else {
        this.lock(); p = randomPiece();
    }
}
Piece.prototype.moveRight = function(){ if(!this.collision(1,0,this.activeTetromino)){ this.unDraw(); this.x++; this.draw(); } }
Piece.prototype.moveLeft = function(){ if(!this.collision(-1,0,this.activeTetromino)){ this.unDraw(); this.x--; this.draw(); } }
Piece.prototype.rotate = function(){
    let next = this.tetromino[(this.tetrominoN + 1) % this.tetromino.length];
    let kick = 0;
    if(this.collision(0,0,next)){ kick = this.x > COL/2 ? -1 : 1; }
    if(!this.collision(kick,0,next)){
        this.unDraw(); this.x += kick;
        this.tetrominoN = (this.tetrominoN + 1) % this.tetromino.length;
        this.activeTetromino = this.tetromino[this.tetrominoN];
        this.draw();
    }
}

Piece.prototype.collision = function(x,y,piece){
    for(let r=0; r<piece.length; r++){
        for(let c=0; c<piece.length; c++){
            if(!piece[r][c]) continue;
            let nX = this.x + c + x; let nY = this.y + r + y;
            if(nX < 0 || nX >= COL || nY >= ROW) return true;
            if(nY < 0) continue;
            if(board[nY][nX] != VACANT) return true;
        }
    }
    return false;
}

Piece.prototype.lock = function(){
    for(let r=0; r<this.activeTetromino.length; r++){
        for(let c=0; c<this.activeTetromino.length; c++){
            if(!this.activeTetromino[r][c]) continue;
            if(this.y + r < 0){ alert("Oyun Bitti"); board=[]; for(let r=0;r<ROW;r++){board[r]=[];for(let c=0;c<COL;c++) board[r][c]=VACANT;} score=0; }
            board[this.y+r][this.x+c] = this.color;
        }
    }
    for(let r=0; r<ROW; r++){
        let isFull = true;
        for(let c=0; c<COL; c++) isFull = isFull && (board[r][c] != VACANT);
        if(isFull){
            for(let y=r; y>1; y--){ for(let c=0; c<COL; c++) board[y][c] = board[y-1][c]; }
            for(let c=0; c<COL; c++) board[0][c] = VACANT;
            score += 50;
        }
    }
    document.getElementById("score").innerHTML = score;
    drawBoard();
}

function drop(){ p.moveDown(); drawBoard(); }
let dropStart = Date.now();
function gameLoop(){
    let now = Date.now();
    if(now - dropStart > 1000){ p.moveDown(); dropStart = Date.now(); }
    requestAnimationFrame(gameLoop);
}
gameLoop();

function move(dir){ if(dir===1) p.moveRight(); else p.moveLeft(); }
function rotate(){ p.rotate(); }
function getTransferCode(){
    if(score<50){ alert("En az 50 puan gerekli"); return; }
    let c = `FNK-${(score*13).toString(16).toUpperCase()}-${Math.floor(Math.random()*999)}`;
    document.getElementById('bankCode').innerText = c;
    document.getElementById('bankCode').style.display='block';
    score=0; document.getElementById("score").innerHTML = 0;
}
</script></body></html>
"""

# ==========================================
# 4. YARDIMCI FONKSİYONLAR
# ==========================================
@st.cache_data
def fetch_json_data(url):
    try:
        r = requests.get(url)
        return r.json() if r.status_code == 200 else {}
    except: return {}

@st.cache_data
def load_local_exams():
    if os.path.exists("exams.json"):
        try:
            with open("exams.json", "r", encoding="utf-8") as f: return json.load(f)
        except: return {}
    return {}

@st.cache_resource
class SchoolServer:
    def __init__(self):
        self.classes = {} 
        self.used_codes = set()
        self.create_class("GENEL")
    def create_class(self, class_code):
        if class_code not in self.classes: self.classes[class_code] = {}
    def join_or_update_student(self, class_code, username, points_to_add=0):
        if class_code not in self.classes: self.create_class(class_code)
        if username not in self.classes[class_code]: self.classes[class_code][username] = 0
        self.classes[class_code][username] += points_to_add
        return self.classes[class_code][username]
    def get_score(self, class_code, username): return self.classes.get(class_code, {}).get(username, 0)
    def redeem_code(self, class_code, username, code_string):
        if code_string in self.used_codes: return False, "Kod kullanılmış!"
        try:
            parts = code_string.split('-')
            if len(parts) != 3 or parts[0] != "FNK": return False, "Geçersiz kod!"
            amount = int(int(parts[1], 16) / 13)
            self.used_codes.add(code_string)
            nb = self.join_or_update_student(class_code, username, amount)
            return True, nb
        except: return False, "Hata."
    def get_leaderboard(self, class_code):
        if class_code in self.classes:
            data = [{"Öğrenci": k, "Puan": v} for k, v in self.classes[class_code].items()]
            if data: return pd.DataFrame(data).sort_values(by="Puan", ascending=False)
        return pd.DataFrame()
    def get_active_students_in_class(self, class_code):
        return list(self.classes.get(class_code, {}).keys())

server = SchoolServer()

def load_lifesim():
    try:
        r = requests.get(f"{GITHUB_BASE_URL}/game.html")
        html = r.text if r.status_code == 200 else "<h3>Yüklenemedi</h3>"
        data = requests.get(URL_LIFESIM).json()
        return html.replace("// PYTHON_DATA_HERE", f"var scenarios = {json.dumps(data)};")
    except: return "Simülasyon Yüklenemedi"

# ==========================================
# 5. ARAYÜZ MANTIĞI
# ==========================================
if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "user_role" not in st.session_state: st.session_state.user_role = None
if "username" not in st.session_state: st.session_state.username = None
if "class_code" not in st.session_state: st.session_state.class_code = "GENEL"

# --- A) GİRİŞ EKRANI ---
if not st.session_state.logged_in:
    st.markdown("<h1 style='text-align:center;'>🎓 Bağarası ÇPAL Dijital Kampüs</h1>", unsafe_allow_html=True)
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
    # --- YENİ MESAJ KONTROLÜ (TOAST) ---
    unread_msgs = database.get_unread_messages(st.session_state.username)
    if unread_msgs:
        for m in unread_msgs:
            st.toast(f"📩 {m[1]}: {m[2]}", icon="🔔")
            database.mark_as_read(m[0])

    # Sidebar
    with st.sidebar:
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
        if st.button("Çıkış"): st.session_state.logged_in = False; st.rerun()

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
        st.markdown("### 🌍 Kampüs Meydanı (Genel Sohbet)")
        msgs = database.get_global_messages(30) # Son 30 mesaj
        for m in msgs:
            with st.chat_message("assistant" if m[0] != st.session_state.username else "user", avatar="👤"):
                st.markdown(f"**{m[0]}**: {m[1]}")
                st.caption(m[2])
        if prompt := st.chat_input("Meydana seslen..."):
            database.send_global_message(st.session_state.username, prompt)
            st.rerun()

    # --- ADMIN PANELİ ---
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
                nu = st.text_input("Kullanıcı")
                np = st.text_input("Şifre")
                nr = st.selectbox("Rol", ["teacher", "student", "admin"])
                if st.form_submit_button("Ekle"):
                    if database.add_user(nu, np, nr): st.success("Eklendi")
                    else: st.error("Hata")
        with t2:
            all_u = database.get_all_users()
            tod = st.selectbox("Silinecek", [u[0] for u in all_u])
            if st.button("Sil"):
                if tod!="admin": database.delete_user(tod); st.rerun()

    # --- ÖĞRETMEN / ÖĞRENCİ ---
    elif st.session_state.user_role in ["student", "teacher"]:
        
        if st.session_state.user_role == "teacher":
            st.success("👨‍🏫 ÖĞRETMEN MODU")
            if "created_code" not in st.session_state:
                st.session_state.created_code = str(random.randint(1000, 9999))
                server.create_class(st.session_state.created_code)
                st.session_state.class_code = st.session_state.created_code
            
            c1, c2 = st.columns(2)
            with c1: st.info(f"Ders Kodu: {st.session_state.created_code}")
            with c2: st.write(f"Aktif Öğrenciler: {server.get_active_students_in_class(st.session_state.created_code)}")
            st.divider()

        st.header(f"Merhaba, {st.session_state.username}")
        t1, t2, t3, t4, t5 = st.tabs(["🏆 Kampüs", "💬 Sosyal & Sohbet", "📚 Dersler", "🎮 Oyunlar", "💼 LifeSim"])
        
        # 1. KAMPÜS
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
                        t = st.text_input("Başlık")
                        c = st.text_area("İçerik")
                        if st.form_submit_button("Yayınla"):
                            database.add_announcement(t, c, st.session_state.username)
                            st.success("Yayınlandı")

            with c2:
                st.subheader("Duyurular")
                anns = database.get_announcements()
                for a in anns: st.info(f"**{a[1]}**: {a[2]}")
                st.subheader("Sıralama")
                st.dataframe(server.get_leaderboard(st.session_state.class_code), use_container_width=True)

        # 2. İLETİŞİM (GENEL VE ÖZEL)
        with t2:
            sub_global, sub_private, sub_req, sub_add = st.tabs(["🌍 Genel Sohbet", "🔒 Özel Mesajlar", "Arkadaş İstekleri", "Öğrenci Ekle"])
            
            with sub_global:
                render_global_chat()

            with sub_private:
                friends = database.get_friends(st.session_state.username)
                if st.session_state.user_role == 'student': friends.append("admin") 
                
                if not friends:
                    st.info("Henüz arkadaşın yok. 'Öğrenci Ekle' sekmesinden arkadaş ekle!")
                else:
                    target = st.selectbox("Kiminle konuşmak istersin?", friends)
                    render_chat(target)
            
            with sub_req:
                pending = database.get_pending_requests(st.session_state.username)
                if pending:
                    for req_id, sender in pending:
                        c1, c2 = st.columns([3, 1])
                        c1.write(f"**{sender}** seni takip etmek istiyor.")
                        if c2.button("Kabul Et", key=f"acc_{req_id}"):
                            database.accept_request(sender, st.session_state.username)
                            st.success(f"{sender} ile artık arkadaşsınız!")
                            st.rerun()
                else: st.caption("Bekleyen istek yok.")
            
            with sub_add:
                st.markdown("Okuldaki diğer öğrencileri bul ve ekle.")
                searchable = database.get_searchable_students(st.session_state.username)
                if searchable:
                    target_student = st.selectbox("Öğrenci Seç", searchable)
                    if st.button("Takip İsteği Gönder"):
                        res, msg = database.send_friend_request(st.session_state.username, target_student)
                        if res: st.success(msg)
                        else: st.warning(msg)
                else: st.info("Eklenebilecek kimse bulunamadı.")

        # 3. DERSLER (TYT / MESLEK / JSON)
        with t3:
            ders_modu = st.radio("Çalışma Alanı Seçiniz:", ["TYT Çalışma", "Meslek Soruları", "Okul Yazılıları (JSON)"], horizontal=True)
            st.divider()

            if ders_modu == "TYT Çalışma":
                tyt_data = fetch_json_data(URL_TYT_DATA)
                if tyt_data:
                    dersler = sorted(list(set([v.get('ders') for v in tyt_data.values() if 'ders' in v])))
                    sel = st.selectbox("Ders", dersler)
                    pages = [k for k, v in tyt_data.items() if v.get('ders') == sel]
                    if pages:
                        pg = st.selectbox("Sayfa", pages)
                        det = tyt_data[pg]
                        c_p, c_q = st.columns([1.5, 1])
                        with c_p: st.markdown(f'<embed src="{URL_TYT_PDF}#page={pg}" width="100%" height="600px">', unsafe_allow_html=True)
                        with c_q:
                            with st.form("tyt"):
                                ans = {}
                                for i, q in enumerate(det['sorular']):
                                    st.write(f"Soru {q}")
                                    ans[i] = st.radio("Cevap", ['A','B','C','D','E'], key=f"t{i}", horizontal=True)
                                if st.form_submit_button("Kontrol"):
                                    d = sum([1 for i, q in enumerate(det['sorular']) if ans[i] == det['cevaplar'][i]])
                                    sc = d*50
                                    st.success(f"Puan: {sc}")
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
                                    for i, q in enumerate(qs):
                                        st.write(f"**{i+1}. {q['soru']}**")
                                        mans[i] = st.radio("Cevap", q['secenekler'], key=f"m{i}")
                                    if st.form_submit_button("Bitir"):
                                        dm = sum([1 for i, q in enumerate(qs) if mans[i] == q['cevap']])
                                        pm = dm*100
                                        st.success(f"Puan: {pm}")
                                        if pm>0: server.join_or_update_student(st.session_state.class_code, st.session_state.username, pm)

            elif ders_modu == "Okul Yazılıları (JSON)":
                EXAM_DATA = load_local_exams()
                if not EXAM_DATA: st.warning("exams.json yok!")
                else:
                    eg = st.selectbox("Sınıf Seviyesi", list(EXAM_DATA.keys()))
                    if eg:
                        el = st.selectbox("Ders Adı", list(EXAM_DATA[eg].keys()))
                        if el:
                            qs = EXAM_DATA[eg][el]
                            st.subheader(f"{el}")
                            with st.form("js_ex"):
                                ua = {}
                                for i, q in enumerate(qs):
                                    st.markdown(f"**Soru {i+1}:** {q.get('text') or q.get('question')}")
                                    if q['type']=='test': ua[i] = st.radio("Seçim", q['options'], key=f"j{i}")
                                    elif q['type']=='text': ua[i] = st.text_input("Cevap", key=f"j{i}")
                                    elif q['type']=='scenario': ua[i] = [st.text_input(sub['q'], key=f"j{i}_{j}") for j, sub in enumerate(q['sub_questions'])]
                                    elif q['type']=='calculation': ua[i] = [st.number_input(inp['label'], key=f"j{i}_{j}") for j, inp in enumerate(q['inputs'])]
                                    st.divider()
                                if st.form_submit_button("Bitir"):
                                    score = 0
                                    for i, q in enumerate(qs):
                                        score += q.get('points', 0) 
                                    st.success(f"Sınav Bitti. Puan: {score}")
                                    server.join_or_update_student(st.session_state.class_code, st.session_state.username, score)

        # 4. OYUNLAR
        with t4:
            gm = st.selectbox("Oyun", ["Finans İmparatoru", "Asset Matrix"])
            if gm == "Finans İmparatoru": components.html(FINANCE_GAME_HTML, height=600)
            else: components.html(ASSET_MATRIX_HTML, height=750)

        # 5. LIFESIM
        with t5:
            components.html(load_lifesim(), height=800, scrolling=True)
