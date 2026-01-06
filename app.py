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
# 1. SAYFA AYARLARI
# ==========================================
st.set_page_config(
    page_title="Bağarası ÇPAL - Dijital Kampüs",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="collapsed"
)

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
# 3. OYUN KODLARI
# ==========================================

# --- OYUN 1: FINANS İMPARATORU ---
FINANCE_GAME_HTML = """
<!DOCTYPE html>
<html lang="tr">
<head>
<meta charset="UTF-8">
<style>
    body { background-color: #0f172a; color: #e2e8f0; font-family: sans-serif; user-select: none; padding: 10px; text-align: center; margin: 0; }
    .dashboard { display: flex; justify-content: space-between; background: #1e293b; padding: 15px; border-radius: 12px; border: 1px solid #334155; margin-bottom: 20px; }
    .money-val { font-size: 22px; font-weight: 900; color: #34d399; }
    .clicker-btn { background: radial-gradient(circle, #3b82f6 0%, #1d4ed8 100%); border: 4px solid #1e3a8a; border-radius: 50%; width: 110px; height: 110px; font-size: 30px; cursor: pointer; margin: 0 auto 20px auto; display: flex; align-items: center; justify-content: center; box-shadow: 0 0 20px rgba(59, 130, 246, 0.4); }
    .clicker-btn:active { transform: scale(0.95); }
    .asset-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(130px, 1fr)); gap: 8px; margin-bottom: 20px; }
    .asset-card { background: #1e293b; padding: 10px; border-radius: 8px; border: 1px solid #334155; cursor: pointer; transition: 0.2s; text-align: left; }
    .asset-card:hover { border-color: #facc15; background: #253347; }
    .asset-card.locked { opacity: 0.5; filter: grayscale(1); pointer-events: none; }
    .bank-btn { background: #10b981; color: #fff; border: none; padding: 8px 20px; font-weight: bold; border-radius: 6px; cursor: pointer; margin-top: 10px; }
    .code-display { background: #fff; color: #000; padding: 5px; margin-top: 5px; font-family: monospace; font-weight: bold; display: none; border-radius: 4px; }
</style>
</head>
<body>
<div class="dashboard">
    <div>NAKİT: <div id="money" class="money-val">0 ₺</div></div>
    <div>GELİR: <div id="cps" style="color:#facc15">0.0 /sn</div></div>
</div>
<div class="clicker-btn" onclick="manualWork()">👆</div>
<div class="asset-grid" id="market"></div>
<button class="bank-btn" onclick="generateCode()">🏦 Bankaya Aktar</button>
<div id="transferCode" class="code-display"></div>
<script>
    let money = 0;
    const assets = [
        { name: "Limonata", cost: 150, gain: 0.5, count: 0 }, { name: "Simit Tezgahı", cost: 1000, gain: 3.5, count: 0 },
        { name: "Kantin", cost: 5000, gain: 15.0, count: 0 }, { name: "Kırtasiye", cost: 20000, gain: 55.0, count: 0 },
        { name: "Yazılım Ofisi", cost: 80000, gain: 200.0, count: 0 }, { name: "Fabrika", cost: 1000000, gain: 3500.0, count: 0 }
    ];
    function updateUI() {
        document.getElementById('money').innerText = Math.floor(money).toLocaleString() + ' ₺';
        let totalCps = assets.reduce((t, a) => t + (a.count * a.gain), 0);
        document.getElementById('cps').innerText = totalCps.toFixed(1) + ' /sn';
        const market = document.getElementById('market'); market.innerHTML = '';
        assets.forEach((asset, index) => {
            let currentCost = Math.floor(asset.cost * Math.pow(1.2, asset.count));
            let div = document.createElement('div');
            div.className = 'asset-card ' + (money >= currentCost ? '' : 'locked');
            div.onclick = () => buyAsset(index);
            div.innerHTML = `<b>${asset.name}</b> (${asset.count})<br><span style="color:#f87171">${currentCost.toLocaleString()} ₺</span><br><span style="color:#34d399">+${asset.gain}/sn</span>`;
            market.appendChild(div);
        });
    }
    function manualWork() { money += 1; updateUI(); }
    function buyAsset(index) {
        let asset = assets[index]; let currentCost = Math.floor(asset.cost * Math.pow(1.2, asset.count));
        if (money >= currentCost) { money -= currentCost; asset.count++; updateUI(); }
    }
    function generateCode() {
        if (money < 50) { alert("En az 50 ₺ birikmeli."); return; }
        let val = Math.floor(money); let hex = (val * 13).toString(16).toUpperCase(); 
        let rnd = Math.floor(Math.random() * 9999);
        let code = `FNK-${hex}-${rnd}`;
        let box = document.getElementById('transferCode'); box.innerText = code; box.style.display = 'block'; money = 0; updateUI();
    }
    setInterval(() => { let totalCps = assets.reduce((t, a) => t + (a.count * a.gain), 0); if (totalCps > 0) { money += totalCps; updateUI(); } }, 1000);
    updateUI();
</script>
</body>
</html>
"""

# --- OYUN 2: SOCRATIC MATRIX (HATA GİDERİLDİ) ---
ASSET_MATRIX_HTML = """
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Socratic Matrix</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@700&display=swap');
        
        body { 
            margin: 0; 
            background-color: #050505; 
            color: #FFD700; 
            font-family: 'Cinzel', serif; 
            text-align: center; 
            touch-action: pan-y; /* Dikey kaydırmaya izin ver */
            user-select: none;
            overflow-y: auto; 
        }

        #game-container { 
            position: relative; 
            width: 100%; 
            height: 100vh; 
            display: flex; 
            flex-direction: column; 
            align-items: center; 
            padding-top: 10px;
        }

        .header { 
            display: flex; 
            justify-content: space-between; 
            width: 90%; 
            max-width: 350px; 
            margin-bottom: 5px; 
            padding: 5px;
            background: #111;
            border-bottom: 1px solid #FFD700;
        }

        .score-val { font-size: 18px; color: #FFD700; font-weight: bold; }

        canvas { 
            background: #0f0f0f; 
            border: 2px solid #333; 
            border-radius: 4px; 
            box-shadow: 0 0 15px rgba(0,0,0,0.8); 
            touch-action: none; /* Sadece oyun alanı kilitli */
        }

        .bank-btn { 
            margin-top: 10px;
            background: linear-gradient(135deg, #FFD700, #B8860B); 
            color: #000; 
            border: none; 
            padding: 10px 25px; 
            font-weight: bold; 
            border-radius: 20px; 
            cursor: pointer; 
        }

        #bankCode { 
            margin-top: 10px;
            background: #222; 
            color: #fff; 
            padding: 8px; 
            display: none; 
            font-family: monospace;
        }

        /* Modal Ekranlar */
        .overlay {
            position: absolute; top: 0; left: 0; width: 100%; height: 100%;
            background: rgba(0,0,0,0.95);
            display: flex; flex-direction: column; justify-content: center; align-items: center;
            z-index: 50;
        }
        .hidden { display: none !important; }
        
        .big-btn {
            background: transparent;
            border: 2px solid #FFD700;
            color: #FFD700;
            padding: 15px 40px;
            font-size: 18px;
            font-family: 'Cinzel', serif;
            cursor: pointer;
            margin-top: 20px;
        }
    </style>
</head>
<body>

    <div id="game-container">
        <div class="header">
            <div>VARLIK: <span id="score" class="score-val">0</span></div>
            <div>SEVİYE: <span id="level" class="score-val">1</span></div>
        </div>

        <canvas id="gameCanvas"></canvas>

        <button class="bank-btn" onclick="getTransferCode()">🏦 HAZİNE AKTAR</button>
        <div id="bankCode"></div>

        <div id="startScreen" class="overlay">
            <h1 style="color:#FFD700;">SOCRATIC MATRIX</h1>
            <p style="color:#aaa;">8x10 Izgara. Blokları sürükle ve yok et.</p>
            <button class="big-btn" onclick="startGame()">BAŞLA</button>
        </div>

        <div id="gameOverScreen" class="overlay hidden">
            <h1 style="color:#ff4444">LİKİDİTE KRİZİ</h1>
            <p style="color:#fff;">Skor: <span id="finalScore">0</span></p>
            <button class="big-btn" onclick="startGame()">TEKRAR DENE</button>
        </div>
    </div>

    <script>
        const canvas = document.getElementById('gameCanvas');
        const ctx = canvas.getContext('2d');
        const scoreEl = document.getElementById('score');
        
        // --- AYARLAR ---
        const COLS = 8;
        const ROWS = 10;
        let CELL_SIZE = 30; 
        const BLOCK_COLOR = "#D500F9"; // Mor
        const PREVIEW_COLOR = "rgba(213, 0, 249, 0.3)";
        
        // --- DEĞİŞKENLER ---
        let grid = [];
        let pieces = []; 
        let draggingPiece = null;
        let score = 0;
        let dragOffset = {x:0, y:0};

        // --- ŞEKİLLER (Tetrominolar) ---
        const SHAPES = [
            [[1]], 
            [[1,1]], [[1],[1]], 
            [[1,1],[1,1]], 
            [[1,1,1]], [[1],[1],[1]],
            [[1,1,1,1]], [[1],[1],[1],[1]],
            [[1,0],[1,0],[1,1]], 
            [[0,1],[0,1],[1,1]], 
            [[1,1,0],[0,1,1]],   
            [[0,1,1],[1,1,0]]    
        ];

        // --- BOYUTLANDIRMA ---
        function resize() {
            const containerW = window.innerWidth;
            const containerH = window.innerHeight * 0.70; 
            
            CELL_SIZE = Math.max(20, Math.floor(Math.min((containerW - 20) / COLS, containerH / ROWS)));
            
            canvas.width = CELL_SIZE * COLS;
            canvas.height = (CELL_SIZE * ROWS) + (CELL_SIZE * 4); 
            
            draw();
        }
        window.addEventListener('resize', resize);

        // --- OYUN MANTIĞI ---
        function startGame() {
            grid = Array(ROWS).fill().map(() => Array(COLS).fill(0));
            score = 0;
            scoreEl.innerText = score;
            
            document.getElementById('startScreen').classList.add('hidden');
            document.getElementById('gameOverScreen').classList.add('hidden');
            document.getElementById('bankCode').style.display = 'none';
            
            resize();
            spawnPieces();
        }

        function spawnPieces() {
            pieces = [];
            const spawnZoneY = (ROWS * CELL_SIZE) + (CELL_SIZE * 0.5);
            const slotWidth = canvas.width / 3;

            for(let i=0; i<3; i++) {
                const shape = SHAPES[Math.floor(Math.random() * SHAPES.length)];
                const pW = shape[0].length * CELL_SIZE * 0.6; 
                
                pieces.push({
                    shape: shape,
                    x: (slotWidth * i) + (slotWidth/2) - (pW/2),
                    y: spawnZoneY,
                    baseX: (slotWidth * i) + (slotWidth/2) - (pW/2),
                    baseY: spawnZoneY,
                    scale: 0.6,
                    isDragging: false
                });
            }
            draw();
            checkGameOver();
        }

        // --- ÇİZİM ---
        function draw() {
            ctx.fillStyle = "#050505";
            ctx.fillRect(0, 0, canvas.width, canvas.height);

            // Izgara
            for(let r=0; r<ROWS; r++) {
                for(let c=0; c<COLS; c++) {
                    const x = c * CELL_SIZE;
                    const y = r * CELL_SIZE;
                    
                    ctx.strokeStyle = "#222";
                    ctx.strokeRect(x, y, CELL_SIZE, CELL_SIZE);

                    if (grid[r][c] === 1) {
                        drawCell(x, y, CELL_SIZE, BLOCK_COLOR);
                    }
                }
            }

            // Çizgi
            ctx.beginPath();
            ctx.moveTo(0, ROWS * CELL_SIZE);
            ctx.lineTo(canvas.width, ROWS * CELL_SIZE);
            ctx.strokeStyle = "#FFD700";
            ctx.lineWidth = 2;
            ctx.stroke();

            // Parçalar
            pieces.forEach(p => {
                if(p.isDragging) return;
                drawShape(p.shape, p.x, p.y, CELL_SIZE * p.scale, "#888");
            });

            // Sürüklenen
            if (draggingPiece) {
                // Izgara hesaplaması: Artık sürüklenen parçanın sol üst köşesini değil, parmağın bulunduğu yeri baz alacağız
                const {gx, gy} = getGridPos(draggingPiece.x, draggingPiece.y);
                
                // Önizleme (Ghost)
                if (canPlace(draggingPiece.shape, gx, gy)) {
                    drawShape(draggingPiece.shape, gx * CELL_SIZE, gy * CELL_SIZE, CELL_SIZE, PREVIEW_COLOR);
                }
                
                // Parçanın kendisi
                drawShape(draggingPiece.shape, draggingPiece.x, draggingPiece.y, CELL_SIZE, BLOCK_COLOR);
            }
        }

        function drawCell(x, y, size, color) {
            ctx.fillStyle = color;
            ctx.fillRect(x+1, y+1, size-2, size-2);
            ctx.strokeStyle = "rgba(255, 215, 0, 0.4)";
            ctx.lineWidth = 1;
            ctx.strokeRect(x+3, y+3, size-6, size-6);
        }

        function drawShape(shape, px, py, size, color) {
            for(let r=0; r<shape.length; r++) {
                for(let c=0; c<shape[r].length; c++) {
                    if(shape[r][c] === 1) {
                        drawCell(px + (c*size), py + (r*size), size, color);
                    }
                }
            }
        }

        // --- FİZİK (DÜZELTİLDİ) ---
        function getGridPos(px, py) {
            if(!draggingPiece) return {gx:-1, gy:-1};
            
            // HATA DÜZELTME: dragOffset'i tekrar eklemek yerine direkt koordinatı kullanıyoruz.
            // Çünkü px zaten offset eklenmiş hali.
            // ızgara hücresini bulurken: Math.round(konum / hücre_boyutu)
            
            const gx = Math.round(px / CELL_SIZE);
            const gy = Math.round(py / CELL_SIZE);
            return {gx, gy};
        }

        function canPlace(shape, gx, gy) {
            for(let r=0; r<shape.length; r++) {
                for(let c=0; c<shape[r].length; c++) {
                    if(shape[r][c] === 1) {
                        let tx = gx + c;
                        let ty = gy + r;
                        if(tx < 0 || tx >= COLS || ty < 0 || ty >= ROWS || grid[ty][tx] === 1) return false;
                    }
                }
            }
            return true;
        }

        function place(shape, gx, gy) {
            for(let r=0; r<shape.length; r++) {
                for(let c=0; c<shape[r].length; c++) {
                    if(shape[r][c] === 1) grid[gy+r][gx+c] = 1;
                }
            }
            score += shape.flat().filter(x=>x).length * 10;
            checkLines();
            scoreEl.innerText = score;
        }

        function checkLines() {
            let lines = 0;
            for(let r=0; r<ROWS; r++) {
                if(grid[r].every(val => val === 1)) {
                    grid[r].fill(0);
                    lines++;
                }
            }
            for(let c=0; c<COLS; c++) {
                let full = true;
                for(let r=0; r<ROWS; r++) if(grid[r][c] === 0) full = false;
                if(full) {
                    for(let r=0; r<ROWS; r++) grid[r][c] = 0;
                    lines++;
                }
            }
            if(lines > 0) score += lines * 100;
        }

        function checkGameOver() {
            let canMove = false;
            if(pieces.length === 0) return;

            for(let p of pieces) {
                for(let r=0; r<ROWS; r++) {
                    for(let c=0; c<COLS; c++) {
                        if(canPlace(p.shape, c, r)) {
                            canMove = true;
                            break;
                        }
                    }
                    if(canMove) break;
                }
                if(canMove) break;
            }

            if(!canMove) {
                document.getElementById('finalScore').innerText = score;
                document.getElementById('gameOverScreen').classList.remove('hidden');
                document.getElementById('gameOverScreen').style.display = 'flex';
            }
        }

        // --- KONTROLLER ---
        function getTouchPos(e) {
            const rect = canvas.getBoundingClientRect();
            const clientX = e.touches ? e.touches[0].clientX : e.clientX;
            const clientY = e.touches ? e.touches[0].clientY : e.clientY;
            return { x: clientX - rect.left, y: clientY - rect.top };
        }

        function onDown(e) {
            const pos = getTouchPos(e);

            for(let i=pieces.length-1; i>=0; i--) {
                const p = pieces[i];
                // Spawn alanındaki boyut (scale 0.6)
                const w = p.shape[0].length * CELL_SIZE * p.scale;
                const h = p.shape.length * CELL_SIZE * p.scale;
                
                // Çarpışma alanı (biraz genişletildi)
                if(pos.x >= p.x - 30 && pos.x <= p.x + w + 30 &&
                   pos.y >= p.y - 30 && pos.y <= p.y + h + 30) {
                    
                    if(e.cancelable) e.preventDefault(); 

                    draggingPiece = p;
                    p.isDragging = true;
                    
                    // Sürüklemeye başlarken parmağı tam ortaya alalım
                    const realW = p.shape[0].length * CELL_SIZE;
                    const realH = p.shape.length * CELL_SIZE;
                    
                    dragOffset.x = -realW / 2;
                    dragOffset.y = -realH / 2; 
                    
                    p.x = pos.x + dragOffset.x;
                    p.y = pos.y + dragOffset.y;
                    
                    draw();
                    break;
                }
            }
        }

        function onMove(e) {
            if(!draggingPiece) return;
            if(e.cancelable) e.preventDefault(); 
            
            const pos = getTouchPos(e);
            draggingPiece.x = pos.x + dragOffset.x;
            draggingPiece.y = pos.y + dragOffset.y;
            draw();
        }

        function onUp(e) {
            if(!draggingPiece) return;
            if(e.cancelable) e.preventDefault();

            const {gx, gy} = getGridPos(draggingPiece.x, draggingPiece.y);

            if(canPlace(draggingPiece.shape, gx, gy)) {
                place(draggingPiece.shape, gx, gy);
                pieces = pieces.filter(p => p !== draggingPiece);
                if(pieces.length === 0) spawnPieces();
                else checkGameOver();
            } else {
                draggingPiece.x = draggingPiece.baseX;
                draggingPiece.y = draggingPiece.baseY;
                draggingPiece.isDragging = false;
            }
            
            draggingPiece = null;
            draw();
        }

        canvas.addEventListener('mousedown', onDown);
        canvas.addEventListener('touchstart', onDown, {passive: false});
        window.addEventListener('mousemove', onMove);
        window.addEventListener('touchmove', onMove, {passive: false});
        window.addEventListener('mouseup', onUp);
        window.addEventListener('touchend', onUp, {passive: false});

        function getTransferCode() {
            if(score < 50) { alert("En az 50 puan gerekli."); return; }
            const hex = (score * 13).toString(16).toUpperCase();
            const code = `FNK-${hex}-${Math.floor(Math.random()*999)}`;
            const box = document.getElementById('bankCode');
            box.innerText = code;
            box.style.display = 'block';
            score = 0; scoreEl.innerText = 0;
            grid = Array(ROWS).fill().map(() => Array(COLS).fill(0));
            draw();
        }
        
        setTimeout(resize, 100);
    </script>
</body>
</html>
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
            with open("exams.json", "r", encoding="utf-8") as f:
                return json.load(f)
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
        
        # --- ANA MENÜYE DÖN BUTONU ---
        if st.button("🏠 Ana Menüye Dön"):
            st.rerun()

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
        try:
            conn = database.connect()
            msgs = conn.execute("SELECT sender, message, timestamp FROM global_messages ORDER BY id DESC LIMIT 50").fetchall()
            conn.close()
            for m in msgs[::-1]:
                with st.chat_message("assistant" if m[0] != st.session_state.username else "user", avatar="👤"):
                    st.markdown(f"**{m[0]}**: {m[1]}")
                    st.caption(m[2])
        except: st.warning("Sohbet yükleniyor...")

        if prompt := st.chat_input("Meydana seslen..."):
            try:
                database.send_global_message(st.session_state.username, prompt)
                st.rerun()
            except: pass

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

        # 2. SOSYAL & SOHBET
        with t2:
            st.subheader("💬 Sosyal Ağ")
            st_chat, st_req, st_add = st.tabs(["Sohbet Et", "Arkadaş İstekleri", "Öğrenci Ekle"])
            
            with st_chat:
                chat_type = st.radio("Sohbet Modu:", ["🌍 Genel Sohbet (Meydan)", "🔒 Özel Mesaj"], horizontal=True)
                if chat_type == "🌍 Genel Sohbet (Meydan)":
                    render_global_chat()
                else:
                    friends = database.get_friends(st.session_state.username)
                    if st.session_state.user_role == 'student': friends.append("admin") 
                    
                    if not friends:
                        st.info("Henüz arkadaşın yok.")
                    else:
                        target = st.selectbox("Kiminle konuşmak istersin?", friends)
                        render_chat(target)
            
            with st_req:
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
            
            with st_add:
                st.markdown("Okuldaki diğer öğrencileri bul ve ekle.")
                searchable = database.get_searchable_students(st.session_state.username)
                if searchable:
                    target_student = st.selectbox("Öğrenci Seç", searchable)
                    if st.button("Takip İsteği Gönder"):
                        res, msg = database.send_friend_request(st.session_state.username, target_student)
                        if res: st.success(msg)
                        else: st.warning(msg)
                else: st.info("Eklenebilecek kimse bulunamadı.")

        # 3. DERSLER
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
