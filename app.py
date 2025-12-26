import streamlit as st
import streamlit.components.v1 as components
import json
import os
import pandas as pd
import time
import urllib.parse

# --- 1. AYARLAR & CSS (TEMİZLİK VE FONT) ---
st.set_page_config(page_title="Finans Kampüsü", page_icon="🏛️", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;700;900&family=Poppins:wght@300;400;600&display=swap');
    .stDeployButton, footer, header { display: none !important; }
    [data-testid="stToolbar"] { display: none !important; }
    .viewerBadge_container__1QSob { display: none !important; }
    
    .stApp { background-color: #0a0a12; color: #e0e0e0; }
    h1, h2, h3, h4, .stTabs button { font-family: 'Cinzel', serif !important; font-weight: 700 !important; color: #f1c40f !important; }
    p, div, span, button, input { font-family: 'Poppins', sans-serif !important; }
    
    /* Sekmeler */
    .stTabs [data-baseweb="tab-list"] { gap: 8px; background: #16213e; padding: 10px; border-radius: 12px; border: 1px solid #f1c40f; box-shadow: 0 0 15px rgba(241, 196, 15, 0.1); }
    .stTabs [data-baseweb="tab"] { height: 45px; border-radius: 8px; border: none; font-weight: 600; font-size: 16px; color: #aaa; background: #0f3460; }
    .stTabs [aria-selected="true"] { background: linear-gradient(135deg, #f1c40f 0%, #d35400 100%) !important; color: #000 !important; font-weight: bold; }
    
    /* Kartlar */
    .score-box { background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); padding: 25px; border-radius: 15px; color: #f1c40f; text-align: center; border: 2px solid #f1c40f; box-shadow: 0 0 25px rgba(241, 196, 15, 0.2); }
    .big-num { font-family: 'Cinzel', serif; font-size: 48px; font-weight: 900; text-shadow: 0 0 10px rgba(241, 196, 15, 0.5); }
    
    /* Banka Veznesi */
    .bank-area { background-color: #0f3460; padding: 20px; border-radius: 12px; border: 2px dashed #27ae60; text-align: center; margin-top: 20px; color: #2ecc71; }
    
    /* Yan Menü */
    [data-testid="stSidebar"] { background-color: #16213e; border-right: 1px solid #f1c40f; }
    
    div.stButton > button { border-radius: 8px; height: 50px; font-weight: bold; border: 1px solid #f1c40f; transition: 0.3s; width: 100%; text-transform: uppercase; letter-spacing: 1px; background: #0f3460; color: #f1c40f; }
    div.stButton > button:hover { background: #f1c40f; color: #000; box-shadow: 0 0 15px #f1c40f; }
    
    .html-save-btn { display: block; width: 100%; background: linear-gradient(45deg, #27ae60, #2ecc71); color: white !important; padding: 15px; text-align: center; border-radius: 12px; font-weight: 800; font-size: 18px; text-decoration: none; box-shadow: 0 4px 15px rgba(39, 174, 96, 0.4); margin-top: 10px; transition: transform 0.2s; border: none; }
    .html-save-btn:hover { transform: scale(1.05); box-shadow: 0 0 20px rgba(39, 174, 96, 0.8); }
    </style>
""", unsafe_allow_html=True)

# --- 2. GÜVENLİ VERİTABANI & ŞİFRELEME ---
FORM_LINK_TASLAK = "https://docs.google.com/forms/d/e/1FAIpQLScshsXIM91CDKu8TgaHIelXYf3M9hzoGb7mldQCDAJ-rcuJ3w/viewform?usp=pp_url&entry.1300987443=AD_YOK&entry.598954691=9999"
DB_FILE = "puan_veritabani.json"

def load_db():
    if not os.path.exists(DB_FILE):
        with open(DB_FILE, "w", encoding="utf-8") as f: json.dump({}, f)
    try:
        with open(DB_FILE, "r", encoding="utf-8") as f: return json.load(f)
    except: return {}

def save_db(data):
    with open(DB_FILE, "w", encoding="utf-8") as f: json.dump(data, f, ensure_ascii=False, indent=4)

def update_player_score(user_key, points, name, no):
    db = load_db()
    current_data = db.get(user_key, {"score": 0, "name": name, "no": no})
    current_data["score"] += points
    current_data["name"] = name
    db[user_key] = current_data
    save_db(db)
    return current_data["score"]

def get_player_score(user_key):
    db = load_db()
    return db.get(user_key, {}).get("score", 0)

def decode_transfer_code(code):
    try:
        parts = code.split('-')
        if len(parts) != 3 or parts[0] != "FNK": return None
        hex_val = parts[1]
        score_mult = int(hex_val, 16)
        actual_score = score_mult / 13
        if actual_score.is_integer(): return int(actual_score)
        else: return None
    except: return None

# --- 3. SESSION STATE ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'user_info' not in st.session_state: st.session_state.user_info = {}

# --- 4. OYUN KODLARI (HTML/JS) ---

# Finans Oyunu: Premium Dark Tema
FINANCE_GAME_HTML = """
<!DOCTYPE html>
<html>
<head>
<style>
body { background: #0a0a12; color: #e0e0e0; font-family: 'Poppins', sans-serif; padding: 10px; text-align: center; user-select:none; }
.top-bar { display: flex; justify-content: space-between; background: #16213e; padding: 15px; border-radius: 12px; border: 2px solid #f1c40f; margin-bottom: 20px; box-shadow: 0 0 15px rgba(241, 196, 15, 0.1); }
.money { font-size: 24px; font-weight: bold; color: #f1c40f; text-shadow: 0 0 5px rgba(241, 196, 15, 0.5); }
.grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px; }
.item { background: linear-gradient(145deg, #0f3460, #16213e); padding: 12px; border-radius: 10px; cursor: pointer; transition: 0.2s; border: 1px solid #1a1a2e; position: relative; box-shadow: 0 4px 6px rgba(0,0,0,0.2); }
.item:hover { border-color: #f1c40f; transform: translateY(-3px); box-shadow: 0 0 10px rgba(241, 196, 15, 0.3); }
.item:active { transform: scale(0.98); }
.item.locked { opacity: 0.4; filter: grayscale(1); pointer-events: none; }
.name { font-weight: bold; color: #fff; font-size: 13px; margin-bottom: 5px; }
.cost { color: #e74c3c; font-size: 11px; }
.income { color: #2ecc71; font-size: 11px; font-weight: bold; }
.count { position: absolute; top: -5px; right: -5px; background: #f1c40f; color: black; padding: 2px 8px; border-radius: 10px; font-size: 11px; font-weight: bold; box-shadow: 0 0 5px #f1c40f; }
.btn-save { background: linear-gradient(45deg, #27ae60, #2ecc71); color: white; border: none; padding: 12px; width: 100%; border-radius: 8px; font-weight: bold; font-size: 16px; cursor: pointer; margin-top: 20px; box-shadow: 0 0 10px rgba(39, 174, 96, 0.5); }
.btn-save:hover { box-shadow: 0 0 20px rgba(39, 174, 96, 0.8); }
.code-display { background: #16213e; color: #f1c40f; padding: 10px; border-radius: 10px; margin-top: 10px; font-family: monospace; font-size: 16px; border: 2px dashed #f1c40f; display: none; }
.clicker-btn { width:90px; height:90px; border-radius:50%; background:radial-gradient(circle, #f1c40f 0%, #d35400 100%); border:3px solid #fff; font-size:35px; cursor:pointer; box-shadow:0 0 25px rgba(241,196,15,0.6); transition: 0.1s; }
.clicker-btn:active { transform: scale(0.95); box-shadow:0 0 15px rgba(241,196,15,0.8); }
</style>
</head>
<body>
<div class="top-bar">
    <div>KASA: <span id="money" class="money">0</span> ₺</div>
    <div style="font-size:11px; color:#aaa; margin-top:5px;">GELİR: <span id="cps" style="color:#2ecc71;">0</span>/sn</div>
</div>

<div style="margin-bottom:20px;">
    <button onclick="clickCoin()" class="clicker-btn">👆</button>
</div>

<div class="grid" id="market"></div>

<button class="btn-save" onclick="generateCode()">🏦 BANKAYA TRANSFER KODU AL</button>
<div id="codeArea" class="code-display"><span id="codeVal" style="font-weight:bold;"></span></div>
<p id="info" style="font-size:10px; color:#aaa; margin-top:5px; display:none;">Kodu kopyala ve uygulamadaki 'Banka Veznesi' kutusuna yapıştır.</p>

<script>
let money = 0;
let assets = [
    {n: "Limonata Standı", c: 50, i: 0.5, cnt: 0},
    {n: "Simit Tezgahı", c: 350, i: 2, cnt: 0},
    {n: "Kırtasiye Dükkanı", c: 1500, i: 8, cnt: 0},
    {n: "Okul Kantini Işletmesi", c: 7500, i: 35, cnt: 0},
    {n: "Öğrenci Servis Filosu", c: 35000, i: 150, cnt: 0},
    {n: "Yazılım & Teknoloji A.Ş.", c: 150000, i: 600, cnt: 0},
    {n: "Uluslararası Holding", c: 1000000, i: 4500, cnt: 0}
];

function updateUI() {
    document.getElementById('money').innerText = Math.floor(money).toLocaleString();
    let totalCps = assets.reduce((t, a) => t + (a.cnt * a.i), 0);
    document.getElementById('cps').innerText = totalCps.toFixed(1);
    
    let m = document.getElementById('market');
    m.innerHTML = "";
    assets.forEach((a, i) => {
        let cost = Math.floor(a.c * Math.pow(1.25, a.cnt));
        let div = document.createElement('div');
        div.className = "item " + (money >= cost ? "" : "locked");
        div.onclick = () => buy(i);
        div.innerHTML = `
            <span class="count">${a.cnt}</span>
            <div class="name">${a.n}</div>
            <div class="cost">Maliyet: ${cost.toLocaleString()} ₺</div>
            <div class="income">+${a.i}/sn</div>
        `;
        m.appendChild(div);
    });
}

function clickCoin() { money += 1; updateUI(); }

function buy(i) {
    let a = assets[i];
    let cost = Math.floor(a.c * Math.pow(1.25, a.cnt));
    if(money >= cost) { money -= cost; a.cnt++; updateUI(); }
}

setInterval(() => {
    let income = assets.reduce((t, a) => t + (a.cnt * a.i), 0);
    if(income > 0) { money += income / 10; updateUI(); }
}, 100);

function generateCode() {
    if(money < 10) { alert("En az 10 TL birikmeli!"); return; }
    let score = Math.floor(money);
    let secureVal = (score * 13).toString(16).toUpperCase();
    let randomPart = Math.floor(Math.random() * 90 + 10);
    let finalCode = "FNK-" + secureVal + "-" + randomPart;
    
    document.getElementById('codeVal').innerText = finalCode;
    document.getElementById('codeArea').style.display = "block";
    document.getElementById('info').style.display = "block";
    money = 0; assets.forEach(a => a.cnt = 0); updateUI();
}
updateUI();
</script>
</body>
</html>
"""

# Matrix Oyunu: Gönderdiğin HTML Kodu Entegre Edildi
MATRIX_GAME_HTML = """
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Black Asset Matrix 10x12</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;700;900&display=swap');

        body {
            margin: 0;
            overflow: hidden;
            background-color: #050505;
            font-family: 'Montserrat', sans-serif;
            color: #fff;
            touch-action: none;
        }

        #game-container {
            position: relative;
            width: 100vw;
            height: 100vh;
            display: flex;
            flex-direction: column;
            justify-content: flex-start;
            align-items: center;
            background: radial-gradient(circle at center, #1a1a1a 0%, #000000 100%);
            padding-top: 15px;
            box-sizing: border-box;
        }

        .header {
            text-align: center;
            margin-bottom: 10px;
            z-index: 2;
        }

        .score-label {
            font-size: 11px;
            color: #aaa;
            letter-spacing: 1px;
            text-transform: uppercase;
        }

        #score {
            font-size: 32px;
            font-weight: 900;
            color: #fff;
            text-shadow: 0 0 10px rgba(255, 255, 255, 0.2);
            transition: color 0.5s;
        }

        #level-indicator {
            font-size: 10px;
            margin-top: 2px;
            opacity: 0.7;
            color: #FFD700; /* Başlangıç rengi */
            transition: color 0.5s;
        }

        canvas {
            box-shadow: 0 0 30px rgba(0, 0, 0, 0.9);
            border-radius: 4px;
            border: 1px solid #222;
            background: #080808;
            touch-action: none;
        }

        .menu-screen {
            position: absolute;
            top: 0; left: 0; width: 100%; height: 100%;
            background: rgba(0, 0, 0, 0.95);
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            z-index: 10;
            transition: opacity 0.3s;
        }

        .hidden { opacity: 0; pointer-events: none; }

        h1 { font-size: 2rem; text-transform: uppercase; letter-spacing: -1px; margin-bottom: 10px; text-align: center;}
        h1 span { color: #FFD700; }
        p { color: #888; margin-bottom: 30px; font-size: 0.9rem; text-align: center; max-width: 80%; }

        .btn {
            background: linear-gradient(45deg, #333, #111);
            border: 1px solid #444;
            padding: 12px 35px;
            font-size: 16px;
            font-weight: 700;
            color: #fff;
            text-transform: uppercase;
            cursor: pointer;
            border-radius: 4px;
            font-family: 'Montserrat', sans-serif;
            transition: all 0.2s;
        }
        .btn:hover { background: #444; border-color: #666; }
        
        /* EK TRANSFER BUTONU STİLİ */
        .btn-transfer {
            background: linear-gradient(45deg, #27ae60, #2ecc71);
            border: 1px solid #2ecc71;
            padding: 8px 20px;
            font-size: 14px;
            margin-top: 10px;
            color: white;
            font-weight: bold;
            border-radius: 5px;
            cursor: pointer;
        }
        .code-box {
            background: #fff;
            color: #000;
            padding: 10px;
            margin-top: 10px;
            border-radius: 5px;
            font-weight: bold;
            font-family: monospace;
            display: none;
        }
    </style>
</head>
<body>

    <div id="game-container">
        <div class="header">
            <div class="score-label">Net Varlık Değeri</div>
            <div id="score">$0</div>
            <div id="level-indicator">SEVİYE: GOLD</div>
        </div>
        
        <canvas id="gameCanvas"></canvas>
        
        <button class="btn-transfer" onclick="getTransferCode()">🏦 TRANSFER KODU AL</button>
        <div id="codeDisplay" class="code-box"></div>

        <div id="startScreen" class="menu-screen">
            <h1>Asset Matrix <span>10x12</span></h1>
            <p>Piyasa zorlaştı. Puanlar kısıtlı.<br>12x12 matriste hayatta kal.</p>
            <button class="btn" onclick="initGame()">Analize Başla</button>
        </div>

        <div id="gameOverScreen" class="menu-screen hidden">
            <h1 style="color: #ff3333;">İFLAS</h1>
            <p>Likidite Sağlanamadı.<br>Son Değer: <span id="finalScore" style="color:#fff;">$0</span></p>
            <button class="btn" onclick="initGame()">Yeniden Yapılandır</button>
        </div>
    </div>

    <script>
        const canvas = document.getElementById('gameCanvas');
        const ctx = canvas.getContext('2d');
        const scoreEl = document.getElementById('score');
        const finalScoreEl = document.getElementById('finalScore');
        const levelEl = document.getElementById('level-indicator');
        const startScreen = document.getElementById('startScreen');
        const gameOverScreen = document.getElementById('gameOverScreen');

        // --- AYARLAR ---
        const GRID_SIZE = 10; // 10x12 İSTEĞİ - KARE TABANLI 10x10, YÜKSEKLİK İÇİN AYARLANABİLİR AMA BASİT OLSUN
        let CELL_SIZE = 30; 
        let BOARD_OFFSET_X = 0;
        let BOARD_OFFSET_Y = 0;
        
        // RENK TEMALARI (Gold, Purple, Rose Gold)
        const THEMES = [
            { name: "GOLD", start: '#FFD700', end: '#C5A028' },       // Klasik Altın
            { name: "NEON PURPLE", start: '#D500F9', end: '#7B1FA2' }, // Neon Mor
            { name: "ROSE GOLD", start: '#E0BFB8', end: '#B76E79' }    // Rose Gold
        ];
        
        let currentLevel = 0;
        let levelThreshold = 50; // Her 50 puanda renk değişir (Cimri puanlama için uygun)

        const GRID_LINE_COLOR = '#222';

        // --- OYUN DURUMU ---
        let grid = Array(GRID_SIZE).fill(0).map(() => Array(GRID_SIZE).fill(0));
        let score = 0;
        let availablePieces = [];
        let draggingPiece = null;
        let isGameOver = false;

        // --- ŞEKİLLER ---
        const SHAPES = [
            [[1]], 
            [[1, 1]], [[1], [1]], 
            [[1, 1, 1]], [[1], [1], [1]], 
            [[1, 1], [1, 1]], 
            [[1, 1, 1], [0, 1, 0]], 
            [[1, 1, 0], [0, 1, 1]], 
            [[0, 1, 1], [1, 1, 0]], 
            [[1, 0], [1, 0], [1, 1]], 
            [[1, 1, 1], [1, 0, 0]], 
            [[1, 1, 1, 1]], [[1],[1],[1],[1]]
        ];

        // --- TEMEL FONKSİYONLAR ---

        function resize() {
            const maxWidth = window.innerWidth * 0.95;
            const maxHeight = window.innerHeight * 0.85; 
            
            // 12x12 olduğu için hücreler daha küçük olmalı
            let size = Math.min(maxWidth, maxHeight * 0.75); 
            
            CELL_SIZE = Math.floor(size / GRID_SIZE);
            
            canvas.width = CELL_SIZE * GRID_SIZE + 20; 
            canvas.height = CELL_SIZE * GRID_SIZE + 130; // Alt panel için yer

            BOARD_OFFSET_X = 10;
            BOARD_OFFSET_Y = 10;
            
            if (!isGameOver && availablePieces.length > 0) draw();
        }
        window.addEventListener('resize', resize);

        function initGame() {
            grid = Array(GRID_SIZE).fill(0).map(() => Array(GRID_SIZE).fill(0));
            score = 0;
            currentLevel = 0;
            isGameOver = false;
            updateScore(0);
            updateTheme();
            
            startScreen.classList.add('hidden');
            gameOverScreen.classList.add('hidden');
            document.getElementById('codeDisplay').style.display = "none";
            
            generateNewPieces();
            resize();
            draw();
        }

        function generateNewPieces() {
            availablePieces = [];
            for (let i = 0; i < 3; i++) {
                const shapeMatrix = SHAPES[Math.floor(Math.random() * SHAPES.length)];
                
                const spawnY = BOARD_OFFSET_Y + GRID_SIZE * CELL_SIZE + 20;
                // 3 parça için eşit dağılım
                const spawnX = BOARD_OFFSET_X + (canvas.width / 6) + (i * (canvas.width / 3.2)) - (CELL_SIZE); 
                
                availablePieces.push({
                    matrix: shapeMatrix,
                    x: spawnX,
                    y: spawnY,
                    baseX: spawnX,
                    baseY: spawnY,
                    width: shapeMatrix[0].length * CELL_SIZE,
                    height: shapeMatrix.length * CELL_SIZE,
                    isDragging: false
                });
            }
            if (checkGameOverState()) gameOver();
        }

        // CİMRİ PUANLAMA & LEVEL SİSTEMİ
        function updateScore(points) {
            score += points;
            scoreEl.innerText = "$" + score; // Sadece sayı, binlik ayraç yok
            
            // Level Kontrolü
            let calculatedLevel = Math.floor(score / levelThreshold);
            if (calculatedLevel !== currentLevel) {
                currentLevel = calculatedLevel;
                updateTheme();
            }
        }

        function updateTheme() {
            const themeIndex = currentLevel % THEMES.length;
            const theme = THEMES[themeIndex];
            
            levelEl.innerText = "SEVİYE: " + theme.name;
            levelEl.style.color = theme.start;
            scoreEl.style.color = theme.start; // Skor rengi de değişsin
            
            // Canvas'ı yeniden çiz ki renkler değişsin
            if(!isGameOver) draw();
        }

        // --- ÇİZİM ---

        function draw() {
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            drawGrid();
            drawPlacedBlocks();
            drawAvailablePieces();
        }

        function drawGrid() {
            ctx.strokeStyle = GRID_LINE_COLOR;
            ctx.lineWidth = 0.5;
            ctx.beginPath();
            for (let i = 0; i <= GRID_SIZE; i++) {
                ctx.moveTo(BOARD_OFFSET_X, BOARD_OFFSET_Y + i * CELL_SIZE);
                ctx.lineTo(BOARD_OFFSET_X + GRID_SIZE * CELL_SIZE, BOARD_OFFSET_Y + i * CELL_SIZE);
                ctx.moveTo(BOARD_OFFSET_X + i * CELL_SIZE, BOARD_OFFSET_Y);
                ctx.lineTo(BOARD_OFFSET_X + i * CELL_SIZE, BOARD_OFFSET_Y + GRID_SIZE * CELL_SIZE);
            }
            ctx.stroke();
        }

        function drawCell(x, y, size, isPreview = false) {
             const themeIndex = currentLevel % THEMES.length;
             const theme = THEMES[themeIndex];

             const gradient = ctx.createLinearGradient(x, y, x + size, y + size);
             if(isPreview) {
                 gradient.addColorStop(0, hexToRgbA(theme.start, 0.4));
                 gradient.addColorStop(1, hexToRgbA(theme.end, 0.4));
             } else {
                 gradient.addColorStop(0, theme.start);
                 gradient.addColorStop(1, theme.end);
             }

            ctx.fillStyle = gradient;
            ctx.fillRect(x + 1, y + 1, size - 2, size - 2);
            
            ctx.strokeStyle = isPreview ? "rgba(255,255,255,0.2)" : "rgba(255,255,255,0.4)";
            ctx.lineWidth = 1;
            ctx.strokeRect(x + 1, y + 1, size - 2, size - 2);
        }

        // Yardımcı fonksiyon: Hex'i şeffaf RGB'ye çevir
        function hexToRgbA(hex, alpha){
            let c;
            if(/^#([A-Fa-f0-9]{3}){1,2}$/.test(hex)){
                c= hex.substring(1).split('');
                if(c.length== 3){
                    c= [c[0], c[0], c[1], c[1], c[2], c[2]];
                }
                c= '0x'+c.join('');
                return 'rgba('+[(c>>16)&255, (c>>8)&255, c&255].join(',')+','+alpha+')';
            }
            return hex;
        }

        function drawPlacedBlocks() {
            for (let row = 0; row < GRID_SIZE; row++) {
                for (let col = 0; col < GRID_SIZE; col++) {
                    if (grid[row][col] === 1) {
                        drawCell(BOARD_OFFSET_X + col * CELL_SIZE, BOARD_OFFSET_Y + row * CELL_SIZE, CELL_SIZE);
                    }
                }
            }
        }

        function drawAvailablePieces() {
            availablePieces.forEach(piece => {
                if (piece.isDragging) return;
                // Aşağıdaki parçaları %50 boyutta çiz (12x12 olduğu için yer dar)
                drawShape(piece.matrix, piece.x, piece.y, CELL_SIZE * 0.5); 
            });

            if (draggingPiece) {
                drawShape(draggingPiece.matrix, draggingPiece.x, draggingPiece.y, CELL_SIZE);
                
                const { gridX, gridY } = getGridCoordsFromMouse(draggingPiece.x, draggingPiece.y);
                if (canPlace(draggingPiece.matrix, gridX, gridY)) {
                     drawShape(draggingPiece.matrix, BOARD_OFFSET_X + gridX * CELL_SIZE, BOARD_OFFSET_Y + gridY * CELL_SIZE, CELL_SIZE, true);
                }
            }
        }

        function drawShape(matrix, startX, startY, cellSize, isPreview = false) {
            for (let row = 0; row < matrix.length; row++) {
                for (let col = 0; col < matrix[row].length; col++) {
                    if (matrix[row][col] === 1) {
                        drawCell(startX + col * cellSize, startY + row * cellSize, cellSize, isPreview);
                    }
                }
            }
        }

        // --- OYUN MANTIĞI ---

        function canPlace(matrix, gridX, gridY) {
            for (let row = 0; row < matrix.length; row++) {
                for (let col = 0; col < matrix[row].length; col++) {
                    if (matrix[row][col] === 1) {
                        let targetX = gridX + col;
                        let targetY = gridY + row;
                        if (targetX < 0 || targetX >= GRID_SIZE || targetY < 0 || targetY >= GRID_SIZE || grid[targetY][targetX] === 1) {
                            return false;
                        }
                    }
                }
            }
            return true;
        }

        function placePiece(matrix, gridX, gridY) {
            for (let row = 0; row < matrix.length; row++) {
                for (let col = 0; col < matrix[row].length; col++) {
                    if (matrix[row][col] === 1) {
                        grid[gridY + row][gridX + col] = 1;
                    }
                }
            }
            // CİMRİ PUAN: Blok yerleştirme sadece +1 puan
            updateScore(1); 
            checkAndClearLines();
        }

        function checkAndClearLines() {
            let linesCleared = 0;
            let rowsToClear = [];
            let colsToClear = [];

            for (let row = 0; row < GRID_SIZE; row++) {
                if (grid[row].every(cell => cell === 1)) rowsToClear.push(row);
            }
            for (let col = 0; col < GRID_SIZE; col++) {
                let full = true;
                for (let row = 0; row < GRID_SIZE; row++) {
                    if (grid[row][col] === 0) { full = false; break; }
                }
                if (full) colsToClear.push(col);
            }

            rowsToClear.forEach(row => {
                for (let col = 0; col < GRID_SIZE; col++) grid[row][col] = 0;
                linesCleared++;
            });
            colsToClear.forEach(col => {
                for (let row = 0; row < GRID_SIZE; row++) grid[row][col] = 0;
                linesCleared++;
            });

            if (linesCleared > 0) {
                // CİMRİ PUAN: Satır başına sadece 10 puan + (satır sayısı * 5 bonus)
                let bonus = linesCleared * 10 + (linesCleared > 1 ? linesCleared * 5 : 0);
                updateScore(bonus);
                
                // Efekt
                canvas.style.transform = 'scale(1.01)';
                setTimeout(() => canvas.style.transform = 'scale(1)', 100);
            }
        }

        // --- DRAG & DROP ---

        let dragOffsetX = 0;
        let dragOffsetY = 0;

        function getEventPos(e) {
            const rect = canvas.getBoundingClientRect();
            let clientX = e.clientX;
            let clientY = e.clientY;
            if (e.touches && e.touches.length > 0) {
                clientX = e.touches[0].clientX;
                clientY = e.touches[0].clientY;
            }
            return { x: clientX - rect.left, y: clientY - rect.top };
        }
        
        function getGridCoordsFromMouse(pieceX, pieceY) {
            let rawGridX = Math.round((pieceX - BOARD_OFFSET_X) / CELL_SIZE);
            let rawGridY = Math.round((pieceY - BOARD_OFFSET_Y) / CELL_SIZE);
            return { gridX: rawGridX, gridY: rawGridY };
        }

        function handleStart(e) {
            if(isGameOver) return;
            e.preventDefault();
            const pos = getEventPos(e);

            for (let i = availablePieces.length - 1; i >= 0; i--) {
                const p = availablePieces[i];
                const renderSize = CELL_SIZE * 0.5; // Aşağıdaki parçalar küçük
                const pWidth = p.matrix[0].length * renderSize;
                const pHeight = p.matrix.length * renderSize;

                // Tıklama toleransı (parmaklar için biraz genişlet)
                if (pos.x > p.x - 10 && pos.x < p.x + pWidth + 10 &&
                    pos.y > p.y - 10 && pos.y < p.y + pHeight + 10) {
                    
                    draggingPiece = p;
                    p.isDragging = true;
                    dragOffsetX = pos.x - p.x;
                    dragOffsetY = pos.y - p.y;
                    
                    // Sürüklerken tam boyuta (CELL_SIZE) ölçekle
                    dragOffsetX = (dragOffsetX / renderSize) * CELL_SIZE;
                    dragOffsetY = (dragOffsetY / renderSize) * CELL_SIZE;
                    
                    draw();
                    return;
                }
            }
        }

        function handleMove(e) {
            if (!draggingPiece) return;
            e.preventDefault();
            const pos = getEventPos(e);
            draggingPiece.x = pos.x - dragOffsetX;
            draggingPiece.y = pos.y - dragOffsetY;
            draw();
        }

        function handleEnd(e) {
            if (!draggingPiece) return;
            e.preventDefault();

            const { gridX, gridY } = getGridCoordsFromMouse(draggingPiece.x, draggingPiece.y);

            if (canPlace(draggingPiece.matrix, gridX, gridY)) {
                placePiece(draggingPiece.matrix, gridX, gridY);
                availablePieces = availablePieces.filter(p => p !== draggingPiece);
                
                if (availablePieces.length === 0) {
                    generateNewPieces();
                } else {
                    if(checkGameOverState()) gameOver();
                }
            } else {
                draggingPiece.x = draggingPiece.baseX;
                draggingPiece.y = draggingPiece.baseY;
                draggingPiece.isDragging = false;
            }

            draggingPiece = null;
            draw();
        }

        function checkGameOverState() {
            if (availablePieces.length === 0) return false;
            for (let i = 0; i < availablePieces.length; i++) {
                const matrix = availablePieces[i].matrix;
                for (let row = 0; row < GRID_SIZE; row++) {
                    for (let col = 0; col < GRID_SIZE; col++) {
                        if (canPlace(matrix, col, row)) return false;
                    }
                }
            }
            return true;
        }

        function gameOver() {
            isGameOver = true;
            finalScoreEl.innerText = scoreEl.innerText;
            gameOverScreen.classList.remove('hidden');
        }
        
        // --- TRANSFER KODU ÜRETME ---
        function getTransferCode() {
            if (score < 5) { alert("Transfer için en az $5 değer üretmelisin!"); return; }
            
            // ŞİFRELEME: (Puan * 13) -> Hex
            let secureVal = (score * 13).toString(16).toUpperCase();
            let code = "FNK-" + secureVal + "-MTX";
            
            document.getElementById('codeDisplay').innerText = "KODUN: " + code;
            document.getElementById('codeDisplay').style.display = "block";
            
            // Oyunu Sıfırla (Kod alındıktan sonra)
            score = 0;
            grid = Array(GRID_SIZE).fill(0).map(() => Array(GRID_SIZE).fill(0));
            updateScore(0);
            generateNewPieces();
            draw();
        }

        canvas.addEventListener('mousedown', handleStart);
        canvas.addEventListener('mousemove', handleMove);
        canvas.addEventListener('mouseup', handleEnd);
        canvas.addEventListener('mouseleave', handleEnd);
        canvas.addEventListener('touchstart', handleStart, { passive: false });
        canvas.addEventListener('touchmove', handleMove, { passive: false });
        canvas.addEventListener('touchend', handleEnd, { passive: false });

        resize();
    </script>
</body>
</html>
"""

# --- 5. UYGULAMA AKIŞI ---

# EKRAN 1: GİRİŞ
if not st.session_state.logged_in:
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown("<div style='text-align:center'><h1>🏛️ FİNANS KAMPÜSÜ</h1><p>Premium Öğrenci Portalı</p></div>", unsafe_allow_html=True)
        with st.form("login"):
            ad = st.text_input("Ad Soyad")
            no = st.text_input("Okul No")
            if st.form_submit_button("SİSTEME GİRİŞ YAP", type="primary"):
                if ad and no:
                    key = f"{no}_{ad.strip()}"
                    st.session_state.user_info = {"name": ad, "no": no, "key": key}
                    st.session_state.logged_in = True
                    st.rerun()
                else: st.error("Lütfen bilgileri eksiksiz giriniz.")

# EKRAN 2: ANA PANEL
else:
    user = st.session_state.user_info
    user_key = user['key']
    current_score = get_player_score(user_key)
    
    with st.sidebar:
        st.markdown(f"### 👤 {user['name'].upper()}")
        st.markdown(f"**🎓 Okul No:** {user['no']}")
        st.markdown("---")
        # OTO KAYIT BUTONU
        safe_name = urllib.parse.quote(user['name'])
        safe_score = str(current_score)
        final_form_link = FORM_LINK_TASLAK.replace("AD_YOK", safe_name).replace("9999", safe_score)
        st.markdown(f"""<a href="{final_form_link}" target="_blank" class="html-save-btn">💾 SKORU LİSTEYE KAYDET</a>""", unsafe_allow_html=True)
        st.markdown("---")
        if st.button("GÜVENLİ ÇIKIŞ"):
            st.session_state.logged_in = False
            st.rerun()

    # Sekmeler
    t1, t2, t3, t4 = st.tabs(["🏠 PROFİL ÖZETİ", "📚 SORU MERKEZİ", "🎮 OYUN & BANKA", "🏆 LİDERLİK TABLOSU"])

    # TAB 1: PROFİL
    with t1:
        st.markdown(f"## HOŞGELDİNİZ, SAYIN {user['name'].split(' ')[0].upper()}")
        st.markdown(f"""
            <div class="score-box">
                <div style="font-size:16px; letter-spacing:3px; margin-bottom:15px; opacity:0.8;">TOPLAM NET VARLIK</div>
                <div class="big-num">{current_score} ₺</div>
            </div>
        """, unsafe_allow_html=True)
        st.success("✅ Verileriniz yerel veritabanında şifreli olarak saklanmaktadır. Skor tablosunda görünmek için yan menüdeki 'Listeye Kaydet' butonunu kullanınız.")

    # TAB 2: DERSLER
    with t2:
        st.subheader("AKADEMİK GELİŞİM")
        c1, c2 = st.columns(2)
        with c1.container(border=True):
            st.markdown("### 📘 TYT HAZIRLIK")
            st.caption("Temel Yeterlilik Testi Denemeleri")
            if st.button("TESTİ BAŞLAT (+20 Puan)", key="btn_tyt"): # KEY EKLENDİ (HATA FİX)
                update_player_score(user_key, 20, user['name'], user['no'])
                st.toast("🎉 Tebrikler! +20 Puan eklendi.")
                time.sleep(0.5); st.rerun()
                
        with c2.container(border=True):
            st.markdown("### 💼 MESLEKİ ALAN")
            st.caption("Muhasebe ve Finansman Soruları")
            if st.button("TESTİ BAŞLAT (+20 Puan)", key="btn_meslek"): # KEY EKLENDİ (HATA FİX)
                update_player_score(user_key, 20, user['name'], user['no'])
                st.toast("🎉 Tebrikler! +20 Puan eklendi.")
                time.sleep(0.5); st.rerun()

    # TAB 3: OYUNLAR & BANKA
    with t3:
        col_game, col_bank = st.columns([2, 1])
        
        with col_game:
            st.subheader("EKONOMİ SİMÜLASYONLARI")
            oyun = st.selectbox("Simülasyon Seçiniz:", ["Finans İmparatoru (Pasif Gelir)", "Asset Matrix (Block Blast)"])
            
            if oyun == "Finans İmparatoru (Pasif Gelir)":
                components.html(FINANCE_GAME_HTML, height=650)
            else:
                components.html(MATRIX_GAME_HTML, height=650)
        
        with col_bank:
            st.markdown("<div style='height: 80px;'></div>", unsafe_allow_html=True)
            st.markdown("""
                <div class="bank-area">
                    <h3 style="color:#2ecc71; margin:0;">🏦 MERKEZ BANKASI</h3>
                    <p style="font-size:13px; color:#aaa;">Güvenli Transfer Noktası</p>
                </div>
            """, unsafe_allow_html=True)
            
            st.info("Oyunlardan elde ettiğiniz 'FNK' kodunu aşağıya girerek varlıklarınızı ana hesabınıza aktarabilirsiniz.")
            transfer_code = st.text_input("Transfer Kodu (FNK-...):", placeholder="Örn: FNK-1A4-BL")
            
            if st.button("KODU ONAYLA VE YATIR", type="primary"):
                amount = decode_transfer_code(transfer_code)
                if amount:
                    update_player_score(user_key, amount, user['name'], user['no'])
                    st.success(f"✅ İŞLEM BAŞARILI! Hesabınıza {amount} ₺ tanımlandı.")
                    st.balloons()
                    time.sleep(2)
                    st.rerun()
                else:
                    st.error("⛔ HATA: Geçersiz veya hatalı transfer kodu!")

    # TAB 4: SIRALAMA
    with t4:
        st.subheader("🏆 LİDERLİK KÜRSÜSÜ")
        db = load_db()
        data = [{"Öğrenci Adı": v['name'], "Okul No": v['no'], "Toplam Varlık (₺)": v['score']} for k,v in db.items()]
        if data:
            df = pd.DataFrame(data).sort_values("Toplam Varlık (₺)", ascending=False).reset_index(drop=True)
            df.index += 1
            st.dataframe(df, use_container_width=True, height=500)
        else:
            st.info("Henüz kayıtlı veri bulunmamaktadır.")
