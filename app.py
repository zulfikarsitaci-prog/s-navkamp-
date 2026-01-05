import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import requests
import json
import os
import time
import random
import database  # database.py dosyası yaninda olmalı
from datetime import datetime

# ==========================================
# 1. SAYFA VE VERİTABANI AYARLARI
# ==========================================
st.set_page_config(
    page_title="Bağarası ÇPAL - Dijital Kampüs",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="collapsed"
)

database.create_database()
if not database.login_user("admin", "6626"):
    database.add_user("admin", "6626", "admin")

# ==========================================
# 2. OYUN KODLARI (TAM SÜRÜM)
# ==========================================

# --- OYUN 1: FINANS İMPARATORU (Tam Kod) ---
FINANCE_GAME_HTML = """
<!DOCTYPE html>
<html lang="tr">
<head>
<meta charset="UTF-8">
<style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;700;900&display=swap');
    body { background-color: #0f172a; color: #e2e8f0; font-family: 'Montserrat', sans-serif; user-select: none; padding: 10px; text-align: center; margin: 0; }
    .dashboard { display: flex; flex-wrap: wrap; justify-content: space-between; background: #1e293b; padding: 15px; border-radius: 12px; border: 1px solid #334155; margin-bottom: 20px; gap: 10px; }
    .stat-box { text-align: left; flex: 1; min-width: 120px; }
    .money-val { font-size: 22px; font-weight: 900; color: #34d399; }
    .income-val { font-size: 16px; font-weight: 700; color: #facc15; }
    .clicker-btn { background: radial-gradient(circle, #3b82f6 0%, #1d4ed8 100%); border: 4px solid #1e3a8a; border-radius: 50%; width: 110px; height: 110px; font-size: 30px; cursor: pointer; box-shadow: 0 0 20px rgba(59, 130, 246, 0.4); margin: 0 auto 20px auto; display: flex; align-items: center; justify-content: center; transition: transform 0.1s; }
    .clicker-btn:active { transform: scale(0.95); }
    .asset-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(130px, 1fr)); gap: 8px; margin-bottom: 20px; }
    .asset-card { background: #1e293b; padding: 10px; border-radius: 8px; border: 1px solid #334155; cursor: pointer; position: relative; transition: 0.2s; text-align: left; }
    .asset-card:hover { border-color: #facc15; background: #253347; }
    .asset-card.locked { opacity: 0.5; filter: grayscale(1); pointer-events: none; }
    .asset-name { font-weight: bold; font-size: 10px; color: #fff; display: block; margin-bottom: 2px;}
    .asset-cost { font-size: 10px; color: #f87171; font-weight: bold; }
    .asset-gain { font-size: 9px; color: #34d399; }
    .asset-count { position: absolute; top: 5px; right: 5px; background: #facc15; color: #000; font-weight: bold; font-size: 9px; padding: 1px 5px; border-radius: 4px; }
    .bank-area { margin-top: 10px; text-align: center; }
    .bank-btn { background: #10b981; color: #fff; border: none; padding: 8px 20px; font-weight: bold; border-radius: 6px; cursor: pointer; font-size: 12px; box-shadow: 0 2px 5px rgba(0,0,0,0.2); transition: 0.2s; }
    .code-display { background: #fff; color: #000; padding: 5px; margin-top: 5px; font-family: monospace; font-weight: bold; display: none; font-size: 12px; border-radius: 4px; width: 100%; box-sizing: border-box;}
</style>
</head>
<body>
<div class="container">
    <div class="dashboard">
        <div class="stat-box"><div>NAKİT</div><div id="money" class="money-val">0 ₺</div></div>
        <div class="stat-box" style="text-align:right;"><div>GELİR</div><div id="cps" class="income-val">0.0 /sn</div></div>
    </div>
    <div class="clicker-btn" onclick="manualWork()">👆</div>
    <div style="text-align:left; color:#facc15; font-size:12px; font-weight:bold; margin-bottom:5px;">YATIRIM PORTFÖYÜ</div>
    <div class="asset-grid" id="market"></div>
    <div class="bank-area"><button class="bank-btn" onclick="generateCode()">🏦 Bankaya Aktar</button><div id="transferCode" class="code-display"></div></div>
</div>
<script>
    let money = 0;
    const assets = [
        { name: "Limonata", cost: 150, gain: 0.5, count: 0 }, { name: "Simit Tezgahı", cost: 1000, gain: 3.5, count: 0 },
        { name: "Kantin", cost: 5000, gain: 15.0, count: 0 }, { name: "Kırtasiye", cost: 20000, gain: 55.0, count: 0 },
        { name: "Yazılım Ofisi", cost: 80000, gain: 200.0, count: 0 }, { name: "E-Ticaret", cost: 250000, gain: 750.0, count: 0 },
        { name: "Fabrika", cost: 1000000, gain: 3500.0, count: 0 }, { name: "Kripto Madeni", cost: 5000000, gain: 15000.0, count: 0 }
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
            div.innerHTML = `<div class="asset-count">${asset.count}</div><div class="asset-name">${asset.name}</div><div class="asset-cost">${currentCost.toLocaleString()} ₺</div><div class="asset-gain">+${asset.gain}/sn</div>`;
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

# --- OYUN 2: ASSET MATRIX (Tam Kod) ---
ASSET_MATRIX_HTML = """
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Socratic Asset Matrix</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;700;900&display=swap');
        body { margin: 0; overflow: hidden; background-color: #050505; font-family: 'Montserrat', sans-serif; color: #fff; touch-action: none; }
        #game-container { position: relative; width: 100vw; height: 100vh; display: flex; flex-direction: column; justify-content: flex-start; align-items: center; background: radial-gradient(circle at center, #1a1a1a 0%, #000000 100%); padding-top: 15px; box-sizing: border-box; }
        .header { text-align: center; margin-bottom: 10px; z-index: 2; }
        .score-label { font-size: 11px; color: #aaa; letter-spacing: 1px; text-transform: uppercase; }
        #score { font-size: 32px; font-weight: 900; color: #fff; text-shadow: 0 0 10px rgba(255, 255, 255, 0.2); transition: color 0.5s; }
        #level-indicator { font-size: 10px; margin-top: 2px; opacity: 0.7; color: #FFD700; transition: color 0.5s; }
        canvas { box-shadow: 0 0 30px rgba(0, 0, 0, 0.9); border-radius: 4px; border: 1px solid #222; background: #080808; touch-action: none; }
        .menu-screen { position: absolute; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0, 0, 0, 0.96); display: flex; flex-direction: column; justify-content: center; align-items: center; z-index: 20; transition: opacity 0.3s; padding: 20px; box-sizing: border-box; text-align: center; }
        .hidden { opacity: 0; pointer-events: none; z-index: -1; }
        h1 { font-size: 2rem; text-transform: uppercase; letter-spacing: -1px; margin-bottom: 10px; }
        h1 span { color: #FFD700; }
        p { color: #888; margin-bottom: 20px; font-size: 0.9rem; max-width: 600px; line-height: 1.5; }
        .btn { background: linear-gradient(45deg, #333, #111); border: 1px solid #444; padding: 12px 35px; font-size: 16px; font-weight: 700; color: #fff; text-transform: uppercase; cursor: pointer; border-radius: 4px; font-family: 'Montserrat', sans-serif; transition: all 0.2s; margin-top: 10px; }
        .btn:hover { background: #444; border-color: #FFD700; color: #FFD700; }
        .bank-btn-overlay { position:absolute; top:10px; right:10px; z-index:100; }
        .mini-btn { background:#38bdf8; border:none; padding:5px 10px; border-radius:4px; font-size:10px; font-weight:bold; cursor:pointer; color:#000; }
        #bankCodeDisplay { position:absolute; top:40px; right:10px; background:white; color:black; padding:5px; font-size:12px; font-weight:bold; display:none; z-index:101; border-radius:4px;}
    </style>
</head>
<body>
    <div id="game-container">
        <div class="bank-btn-overlay"><button class="mini-btn" onclick="getTransferCode()">🏦 BANKAYA AKTAR</button></div>
        <div id="bankCodeDisplay"></div>
        <div class="header">
            <div class="score-label">Net Varlık Değeri</div>
            <div id="score">$0</div>
            <div id="level-indicator">SEVİYE: BAŞLANGIÇ</div>
        </div>
        <canvas id="gameCanvas"></canvas>
        <div id="startScreen" class="menu-screen">
            <h1>Socratic <span>Matrix</span></h1>
            <p>Finansal piyasalar karmaşıktır. Blokları yönet, varlıklarını artır.</p>
            <button class="btn" onclick="initGame()">Simülasyonu Başlat</button>
        </div>
        <div id="gameOverScreen" class="menu-screen hidden">
            <h1 style="color: #ff4444;">LİKİDİTE KRİZİ</h1>
            <p>Piyasa kilitlendi.</p>
            <p>Son Değer: <span id="finalScore" style="color:#fff; font-weight:bold;">$0</span></p>
            <button class="btn" onclick="initGame()">Yeniden Dene</button>
        </div>
    </div>
    <script>
        const canvas = document.getElementById('gameCanvas'); const ctx = canvas.getContext('2d');
        const scoreEl = document.getElementById('score'); const finalScoreEl = document.getElementById('finalScore');
        const levelEl = document.getElementById('level-indicator'); const startScreen = document.getElementById('startScreen');
        const gameOverScreen = document.getElementById('gameOverScreen');
        const GRID_SIZE = 8; let CELL_SIZE = 30; let BOARD_OFFSET_X = 0; let BOARD_OFFSET_Y = 0;
        const THEMES = [{ name: "GOLD (Birikim)", start: '#FFD700', end: '#C5A028' }, { name: "PURPLE (Kaldıraç)", start: '#D500F9', end: '#7B1FA2' }];
        let currentLevel = 0; let levelThreshold = 30; 
        let grid = [], score = 0, availablePieces = [], draggingPiece = null, isGameOver = false;
        
        function resize() {
            const maxWidth = window.innerWidth * 0.95; const maxHeight = window.innerHeight * 0.85; 
            let size = Math.min(maxWidth, maxHeight * 0.75); CELL_SIZE = Math.floor(size / GRID_SIZE);
            canvas.width = CELL_SIZE * GRID_SIZE + 20; canvas.height = CELL_SIZE * GRID_SIZE + 130; 
            BOARD_OFFSET_X = 10; BOARD_OFFSET_Y = 10;
            if (!isGameOver && availablePieces.length > 0) draw();
        }
        window.addEventListener('resize', resize);
        
        function initGame() {
            grid = Array(GRID_SIZE).fill(0).map(() => Array(GRID_SIZE).fill(0));
            score = 0; currentLevel = 0; isGameOver = false;
            updateScore(0); updateTheme();
            startScreen.classList.add('hidden'); gameOverScreen.classList.add('hidden');
            generateNewPieces(); resize(); draw();
        }
        
        const SHAPES = [[[1]], [[1, 1]], [[1], [1]], [[1, 1, 1]], [[1, 1], [1, 1]]];
        
        function generateNewPieces() {
            availablePieces = [];
            for (let i = 0; i < 3; i++) {
                const shapeMatrix = SHAPES[Math.floor(Math.random() * SHAPES.length)];
                const spawnY = BOARD_OFFSET_Y + GRID_SIZE * CELL_SIZE + 20;
                const spawnX = BOARD_OFFSET_X + (canvas.width / 6) + (i * (canvas.width / 3.2)) - (CELL_SIZE); 
                availablePieces.push({ matrix: shapeMatrix, x: spawnX, y: spawnY, baseX: spawnX, baseY: spawnY, width: shapeMatrix[0].length * CELL_SIZE, height: shapeMatrix.length * CELL_SIZE, isDragging: false });
            }
            if (checkGameOverState()) gameOver();
        }
        
        function updateScore(points) {
            score += points; scoreEl.innerText = "$" + score; 
            currentLevel = Math.floor(score / levelThreshold); updateTheme();
        }
        
        function updateTheme() {
            const theme = THEMES[currentLevel % THEMES.length];
            levelEl.innerText = "SEVİYE: " + theme.name; levelEl.style.color = theme.start; scoreEl.style.color = theme.start;
            if(!isGameOver) draw();
        }
        
        function draw() {
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            // Grid
            ctx.lineWidth = 2; ctx.strokeStyle = '#666'; ctx.beginPath();
            for (let i = 0; i <= GRID_SIZE; i++) {
                ctx.moveTo(BOARD_OFFSET_X, BOARD_OFFSET_Y + i * CELL_SIZE); ctx.lineTo(BOARD_OFFSET_X + GRID_SIZE * CELL_SIZE, BOARD_OFFSET_Y + i * CELL_SIZE);
                ctx.moveTo(BOARD_OFFSET_X + i * CELL_SIZE, BOARD_OFFSET_Y); ctx.lineTo(BOARD_OFFSET_X + i * CELL_SIZE, BOARD_OFFSET_Y + GRID_SIZE * CELL_SIZE);
            }
            ctx.stroke();
            // Placed Blocks
            for (let row = 0; row < GRID_SIZE; row++) for (let col = 0; col < GRID_SIZE; col++) if (grid[row][col] === 1) drawCell(BOARD_OFFSET_X + col * CELL_SIZE, BOARD_OFFSET_Y + row * CELL_SIZE, CELL_SIZE);
            // Pieces
            availablePieces.forEach(piece => { if (piece.isDragging) return; drawShape(piece.matrix, piece.x, piece.y, CELL_SIZE * 0.5); });
            if (draggingPiece) {
                drawShape(draggingPiece.matrix, draggingPiece.x, draggingPiece.y, CELL_SIZE);
                const { gridX, gridY } = getGridCoordsFromMouse(draggingPiece.x, draggingPiece.y);
                if (canPlace(draggingPiece.matrix, gridX, gridY)) drawShape(draggingPiece.matrix, BOARD_OFFSET_X + gridX * CELL_SIZE, BOARD_OFFSET_Y + gridY * CELL_SIZE, CELL_SIZE, true);
            }
        }
        
        function drawCell(x, y, size, isPreview = false) {
             const theme = THEMES[currentLevel % THEMES.length];
             ctx.fillStyle = isPreview ? theme.end : theme.start; 
             ctx.fillRect(x + 1, y + 1, size - 2, size - 2);
        }
        
        function drawShape(matrix, startX, startY, cellSize, isPreview = false) {
            for (let row = 0; row < matrix.length; row++) for (let col = 0; col < matrix[row].length; col++) if (matrix[row][col] === 1) drawCell(startX + col * cellSize, startY + row * cellSize, cellSize, isPreview);
        }
        
        function canPlace(matrix, gridX, gridY) {
            for (let row = 0; row < matrix.length; row++) for (let col = 0; col < matrix[row].length; col++) if (matrix[row][col] === 1) {
                let targetX = gridX + col; let targetY = gridY + row;
                if (targetX < 0 || targetX >= GRID_SIZE || targetY < 0 || targetY >= GRID_SIZE || grid[targetY][targetX] === 1) return false;
            }
            return true;
        }
        
        function placePiece(matrix, gridX, gridY) {
            for (let row = 0; row < matrix.length; row++) for (let col = 0; col < matrix[row].length; col++) if (matrix[row][col] === 1) grid[gridY + row][gridX + col] = 1;
            updateScore(1); checkAndClearLines();
        }
        
        function checkAndClearLines() {
            let rowsToClear = [], colsToClear = [];
            for (let row = 0; row < GRID_SIZE; row++) if (grid[row].every(cell => cell === 1)) rowsToClear.push(row);
            for (let col = 0; col < GRID_SIZE; col++) { let full = true; for (let row = 0; row < GRID_SIZE; row++) if (grid[row][col] === 0) { full = false; break; } if (full) colsToClear.push(col); }
            rowsToClear.forEach(row => { for (let col = 0; col < GRID_SIZE; col++) grid[row][col] = 0; });
            colsToClear.forEach(col => { for (let row = 0; row < GRID_SIZE; row++) grid[row][col] = 0; });
            if (rowsToClear.length + colsToClear.length > 0) updateScore((rowsToClear.length + colsToClear.length) * 10);
        }
        
        function checkGameOverState() {
            if (availablePieces.length === 0) return false;
            for (let i = 0; i < availablePieces.length; i++) {
                const matrix = availablePieces[i].matrix;
                for (let row = 0; row < GRID_SIZE; row++) for (let col = 0; col < GRID_SIZE; col++) if (canPlace(matrix, col, row)) return false;
            }
            return true;
        }
        
        function gameOver() {
            isGameOver = true; finalScoreEl.innerText = scoreEl.innerText;
            gameOverScreen.classList.remove('hidden');
        }
        
        let dragOffsetX = 0, dragOffsetY = 0;
        function getEventPos(e) {
            const rect = canvas.getBoundingClientRect();
            let clientX = e.clientX, clientY = e.clientY;
            if (e.touches && e.touches.length > 0) { clientX = e.touches[0].clientX; clientY = e.touches[0].clientY; }
            return { x: clientX - rect.left, y: clientY - rect.top };
        }
        function getGridCoordsFromMouse(pieceX, pieceY) {
            let rawGridX = Math.round((pieceX - BOARD_OFFSET_X) / CELL_SIZE);
            let rawGridY = Math.round((pieceY - BOARD_OFFSET_Y) / CELL_SIZE);
            return { gridX: rawGridX, gridY: rawGridY };
        }
        function handleStart(e) {
            if(isGameOver) return; e.preventDefault(); const pos = getEventPos(e);
            for (let i = availablePieces.length - 1; i >= 0; i--) {
                const p = availablePieces[i];
                const renderSize = CELL_SIZE * 0.5; const pWidth = p.matrix[0].length * renderSize; const pHeight = p.matrix.length * renderSize;
                if (pos.x > p.x - 10 && pos.x < p.x + pWidth + 10 && pos.y > p.y - 10 && pos.y < p.y + pHeight + 10) {
                    draggingPiece = p; p.isDragging = true;
                    dragOffsetX = pos.x - p.x; dragOffsetY = pos.y - p.y;
                    dragOffsetX = (dragOffsetX / renderSize) * CELL_SIZE; dragOffsetY = (dragOffsetY / renderSize) * CELL_SIZE;
                    draw(); return;
                }
            }
        }
        function handleMove(e) {
            if (!draggingPiece) return; e.preventDefault(); const pos = getEventPos(e);
            draggingPiece.x = pos.x - dragOffsetX; draggingPiece.y = pos.y - dragOffsetY; draw();
        }
        function handleEnd(e) {
            if (!draggingPiece) return; e.preventDefault();
            const { gridX, gridY } = getGridCoordsFromMouse(draggingPiece.x, draggingPiece.y);
            if (canPlace(draggingPiece.matrix, gridX, gridY)) {
                placePiece(draggingPiece.matrix, gridX, gridY);
                availablePieces = availablePieces.filter(p => p !== draggingPiece);
                if (availablePieces.length === 0) generateNewPieces(); else if(checkGameOverState()) gameOver();
            } else { draggingPiece.x = draggingPiece.baseX; draggingPiece.y = draggingPiece.baseY; draggingPiece.isDragging = false; }
            draggingPiece = null; draw();
        }
        function getTransferCode() {
            if(score < 50) { alert("En az 50 puan gerekli."); return; }
            let val = score; let hex = (val * 13).toString(16).toUpperCase(); 
            let rnd = Math.floor(Math.random() * 9999);
            let code = `FNK-${hex}-${rnd}`;
            document.getElementById('bankCodeDisplay').innerText = code; document.getElementById('bankCodeDisplay').style.display = 'block';
            score = 0; updateScore(0); draw();
        }
        canvas.addEventListener('mousedown', handleStart); canvas.addEventListener('mousemove', handleMove); canvas.addEventListener('mouseup', handleEnd); canvas.addEventListener('mouseleave', handleEnd);
        canvas.addEventListener('touchstart', handleStart, { passive: false }); canvas.addEventListener('touchmove', handleMove, { passive: false }); canvas.addEventListener('touchend', handleEnd, { passive: false });
        resize();
    </script>
</body>
</html>
"""

# ==========================================
# 3. VERİ YÜKLEME VE SERVER FONKSİYONLARI
# ==========================================
GITHUB_BASE_URL = "https://raw.githubusercontent.com/zulfikarsitaci-prog/s-navkamp-/main"
URL_LIFESIM = f"{GITHUB_BASE_URL}/lifesim_data.json"

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
# 4. ARAYÜZ MANTIĞI
# ==========================================
if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "user_role" not in st.session_state: st.session_state.user_role = None
if "username" not in st.session_state: st.session_state.username = None
if "class_code" not in st.session_state: st.session_state.class_code = "GENEL"

if "logged_in" in st.session_state and st.session_state.logged_in:
    database.update_activity(st.session_state.username)

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
    # Sidebar
    with st.sidebar:
        st.title(st.session_state.username)
        st.caption(f"Yetki: {st.session_state.user_role}")
        
        with st.expander("📬 Mesajlarım", expanded=False):
            msgs = database.get_my_messages(st.session_state.username)
            if msgs:
                for m in msgs: st.info(f"**{m[0]}**: {m[1]}\n\n*{m[2]}*")
            else: st.caption("Mesajınız yok.")

        if st.session_state.user_role == "student":
            code = st.text_input("Sınıf Kodu", placeholder="Örn: 1234")
            if st.button("Sınıfa Geç"):
                st.session_state.class_code = code
                server.join_or_update_student(code, st.session_state.username)
                st.success(f"Sınıf: {code}"); time.sleep(0.5); st.rerun()
        if st.button("Çıkış"): st.session_state.logged_in = False; st.rerun()

    # --- ADMIN ---
    if st.session_state.user_role == "admin":
        st.header("⚙️ Yönetim Paneli")
        
        st.subheader("Online Kullanıcılar & Mesaj")
        online_users = database.get_online_users(2)
        c1, c2 = st.columns([2, 1])
        with c1:
            st.write(f"Online: {len(online_users)}")
            if online_users: st.dataframe(pd.DataFrame(online_users))
            if st.button("Yenile"): st.rerun()
        with c2:
            all_users = [u[0] for u in database.get_all_users() if u[0] != "admin"]
            target = st.selectbox("Alıcı", all_users)
            msg = st.text_area("Mesaj")
            if st.button("Gönder"):
                database.send_message("Admin", target, msg)
                st.success("İletildi")

        st.divider()
        tab1, tab2 = st.tabs(["Kullanıcı Ekle", "Kullanıcı Sil"])
        with tab1:
            with st.form("add_usr"):
                nu = st.text_input("Kullanıcı")
                np = st.text_input("Şifre")
                nr = st.selectbox("Rol", ["teacher", "admin", "student"])
                if st.form_submit_button("Ekle"):
                    if database.add_user(nu, np, nr): st.success("Eklendi")
                    else: st.error("Hata")
        with tab2:
            all_u = database.get_all_users()
            to_del = st.selectbox("Silinecek", [u[0] for u in all_u])
            if st.button("Sil"):
                if to_del!="admin": database.delete_user(to_del); st.rerun()

    # --- ÖĞRETMEN / ÖĞRENCİ (HİBRİT) ---
    elif st.session_state.user_role in ["student", "teacher"]:
        
        if st.session_state.user_role == "teacher":
            st.success("👨‍🏫 ÖĞRETMEN PANELİ")
            if "created_code" not in st.session_state:
                st.session_state.created_code = str(random.randint(1000, 9999))
                server.create_class(st.session_state.created_code)
                st.session_state.class_code = st.session_state.created_code
            
            c1, c2 = st.columns(2)
            with c1: st.info(f"Ders Kodu: {st.session_state.created_code}")
            with c2:
                acts = server.get_active_students_in_class(st.session_state.created_code)
                st.write(f"Sınıftakiler: {len(acts)}"); st.write(acts)
            st.divider()

        st.header(f"Merhaba, {st.session_state.username}")
        t1, t2, t3, t4 = st.tabs(["🏆 Kampüs", "📚 Sınavlar", "🎮 Oyunlar", "💼 LifeSim"])
        
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

        # 2. DERSLER (JSON SINAVLARI)
        with t2:
            EXAM_DATA = load_local_exams()
            if not EXAM_DATA: st.warning("exams.json yok!")
            else:
                grade = st.selectbox("Sınıf", list(EXAM_DATA.keys()))
                if grade:
                    lesson = st.selectbox("Ders", list(EXAM_DATA[grade].keys()))
                    if lesson:
                        st.subheader(f"{lesson}")
                        questions = EXAM_DATA[grade][lesson]
                        with st.form(f"ex_{grade}_{lesson}"):
                            u_ans = {}
                            for i, q in enumerate(questions):
                                st.markdown(f"**Soru {i+1}:** {q.get('text') or q.get('question')}")
                                if q['type'] == 'test': u_ans[i] = st.radio("Cevap", q['options'], key=f"q{i}")
                                elif q['type'] == 'text': u_ans[i] = st.text_input("Yanıt", key=f"q{i}")
                                elif q['type'] == 'scenario': u_ans[i] = [st.text_input(sub['q'], key=f"q{i}_{j}") for j, sub in enumerate(q['sub_questions'])]
                                elif q['type'] == 'calculation': u_ans[i] = [st.number_input(inp['label'], key=f"q{i}_{j}") for j, inp in enumerate(q['inputs'])]
                                st.divider()
                            
                            if st.form_submit_button("Bitir"):
                                score = 0
                                for i, q in enumerate(questions):
                                    score += q.get('points', 0)
                                st.success(f"Puan: {score}")
                                server.join_or_update_student(st.session_state.class_code, st.session_state.username, score)

        # 3. OYUNLAR
        with t3:
            gm = st.selectbox("Oyun", ["Finans İmparatoru", "Asset Matrix"])
            if gm == "Finans İmparatoru": components.html(FINANCE_GAME_HTML, height=600)
            else: components.html(ASSET_MATRIX_HTML, height=600)

        # 4. LIFESIM
        with t4:
            components.html(load_lifesim(), height=800, scrolling=True)
