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
    
    .stApp { background-color: #0a0a12; color: #e0e0e0; } /* Daha koyu premium arka plan */
    h1, h2, h3, h4, .stTabs button { font-family: 'Cinzel', serif !important; font-weight: 700 !important; color: #f1c40f !important; }
    p, div, span, button, input { font-family: 'Poppins', sans-serif !important; }
    
    /* Sekmeler - Premium Dark */
    .stTabs [data-baseweb="tab-list"] { gap: 8px; background: #16213e; padding: 10px; border-radius: 12px; border: 1px solid #f1c40f; box-shadow: 0 0 15px rgba(241, 196, 15, 0.1); }
    .stTabs [data-baseweb="tab"] { height: 45px; border-radius: 8px; border: none; font-weight: 600; font-size: 16px; color: #aaa; background: #0f3460; }
    .stTabs [aria-selected="true"] { background: linear-gradient(135deg, #f1c40f 0%, #d35400 100%) !important; color: #000 !important; font-weight: bold; }
    
    /* Kartlar - Premium Glow */
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

# Matrix Oyunu: Premium Drag & Drop Block Blast
MATRIX_GAME_HTML = """
<!DOCTYPE html>
<html>
<head>
<style>
body { background: #0a0a12; color: #e0e0e0; display: flex; flex-direction: column; align-items: center; justify-content: flex-start; height: 98vh; font-family: 'Poppins', sans-serif; user-select: none; overflow: hidden; padding-top: 10px; }
/* Premium Board Styling */
.board-container { padding: 5px; background: linear-gradient(145deg, #16213e, #0f3460); border-radius: 10px; box-shadow: 0 0 20px rgba(0,0,0,0.5); border: 2px solid #333; }
.board { display: grid; grid-template-columns: repeat(10, 28px); grid-template-rows: repeat(10, 28px); gap: 3px; }
.cell { width: 28px; height: 28px; background: #0a0a12; border-radius: 4px; border: 1px solid #222; transition: background 0.2s, box-shadow 0.2s; }
.cell.filled { border: none; }
.cell.highlight { background: rgba(255, 255, 255, 0.2); border: 1px dashed #aaa; }
.cell.invalid { background: rgba(231, 76, 60, 0.3); border: 1px dashed #e74c3c; }

/* Score & UI */
.top-ui { display: flex; justify-content: space-between; width: 320px; margin-bottom: 15px; align-items: center; }
.score-box { background: #16213e; padding: 5px 15px; border-radius: 20px; border: 2px solid #f1c40f; font-weight: bold; color: #f1c40f; box-shadow: 0 0 10px rgba(241, 196, 15, 0.2); }
.btn-bank { background: linear-gradient(45deg, #8e44ad, #9b59b6); color: white; border: none; padding: 8px 15px; font-weight: bold; border-radius: 20px; cursor: pointer; font-size: 12px; box-shadow: 0 0 10px rgba(142, 68, 173, 0.4); }
.btn-bank:hover { box-shadow: 0 0 15px rgba(142, 68, 173, 0.7); }

/* Dock (El) Styling */
.dock { display: flex; justify-content: center; gap: 20px; margin-top: 25px; height: 80px; align-items: center; background: rgba(255,255,255,0.05); padding: 10px; border-radius: 15px; width: 320px; }
.shape-preview { display: grid; gap: 2px; cursor: grab; transition: transform 0.1s; }
.shape-preview:active { cursor: grabbing; transform: scale(1.1); }
.preview-cell { width: 20px; height: 20px; border-radius: 3px; }

/* Floating Drag Element */
#drag-ghost { position: fixed; pointer-events: none; z-index: 100; display: none; opacity: 0.8; filter: drop-shadow(0 5px 15px rgba(0,0,0,0.5)); }

/* Code Box */
.code-box { background: #16213e; color: #f1c40f; padding: 10px; margin-top: 10px; font-weight: bold; border: 2px dashed #f1c40f; display: none; font-size:14px; font-family: monospace; border-radius: 8px; text-align: center; width: 300px; }
</style>
</head>
<body>

<div class="top-ui">
    <div class="score-box">SKOR: <span id="score">0</span></div>
    <button class="btn-bank" onclick="getCode()">🏦 KOD AL</button>
</div>

<div class="board-container">
    <div class="board" id="board"></div>
</div>

<div class="dock" id="dock"></div>

<div id="drag-ghost"></div>
<div id="codeDisplay" class="code-box"></div>

<script>
const BOARD_SIZE = 10;
let grid = Array(BOARD_SIZE).fill().map(() => Array(BOARD_SIZE).fill(0));
let score = 0;
let dockShapes = [];
let isDragging = false;
let draggedShape = null;
let dragOriginIndex = -1;

// PREMIUM RENK PALETLERİ (Gradyanlar için)
const THEMES = [
    { name: "Gold", bg: "linear-gradient(135deg, #f1c40f, #f39c12)", shadow: "#f39c12" },
    { name: "Rose", bg: "linear-gradient(135deg, #e94560, #c0392b)", shadow: "#c0392b" },
    { name: "Silver", bg: "linear-gradient(135deg, #bdc3c7, #7f8c8d)", shadow: "#7f8c8d" },
    { name: "Purple", bg: "linear-gradient(135deg, #8e44ad, #9b59b6)", shadow: "#9b59b6" },
    { name: "Cyan", bg: "linear-gradient(135deg, #00d2d3, #00cec9)", shadow: "#00cec9" },
    { name: "Emerald", bg: "linear-gradient(135deg, #2ecc71, #27ae60)", shadow: "#27ae60" }
];

// 8 FARKLI BLOK TİPİ
const SHAPES = [
    [[1]], // Tekli
    [[1, 1]], // İkili Yatay
    [[1], [1]], // İkili Dikey
    [[1, 1, 1]], // Üçlü Yatay
    [[1], [1], [1]], // Üçlü Dikey
    [[1, 1], [1, 1]], // Kare (2x2)
    [[1, 0], [1, 0], [1, 1]], // L Büyük
    [[1, 1, 1], [0, 1, 0]], // T Şekli
    [[1, 1, 0], [0, 1, 1]] // Z Şekli
];

function getTheme() { return THEMES[Math.floor(score / 50) % THEMES.length]; }

function initBoard() {
    const boardDiv = document.getElementById("board");
    boardDiv.innerHTML = "";
    for(let r=0; r<BOARD_SIZE; r++) {
        for(let c=0; c<BOARD_SIZE; c++) {
            let cell = document.createElement("div");
            cell.className = "cell";
            cell.id = `c-${r}-${c}`;
            boardDiv.appendChild(cell);
        }
    }
    updateBoardView();
    refillDock();
}

function updateBoardView() {
    for(let r=0; r<BOARD_SIZE; r++) {
        for(let c=0; c<BOARD_SIZE; c++) {
            let cell = document.getElementById(`c-${r}-${c}`);
            cell.classList.remove("filled", "highlight", "invalid");
            cell.style.background = ""; cell.style.boxShadow = "";
            
            if(grid[r][c]) {
                let theme = getTheme();
                cell.classList.add("filled");
                cell.style.background = theme.bg;
                cell.style.boxShadow = `0 0 10px ${theme.shadow}`;
            }
        }
    }
    document.getElementById("score").innerText = score;
}

function renderDock() {
    const dockDiv = document.getElementById("dock");
    dockDiv.innerHTML = "";
    dockShapes.forEach((shapeMatrix, index) => {
        if(shapeMatrix === null) { dockDiv.appendChild(document.createElement("div")); return; } // Boş slot
        
        let preview = document.createElement("div");
        preview.className = "shape-preview";
        preview.style.gridTemplateColumns = `repeat(${shapeMatrix[0].length}, 20px)`;
        
        shapeMatrix.forEach(row => {
            row.forEach(cellVal => {
                let pCell = document.createElement("div");
                pCell.className = "preview-cell";
                if(cellVal) {
                    pCell.style.background = getTheme().bg;
                    pCell.style.boxShadow = `0 0 5px ${getTheme().shadow}`;
                } else {
                    pCell.style.background = "transparent";
                }
                preview.appendChild(pCell);
            });
        });
        
        // DRAG BAŞLATMA
        preview.onmousedown = (e) => startDrag(e, shapeMatrix, index);
        dockDiv.appendChild(preview);
    });
}

function refillDock() {
    if(dockShapes.every(s => s === null) || dockShapes.length === 0) {
        dockShapes = [];
        for(let i=0; i<3; i++) dockShapes.push(SHAPES[Math.floor(Math.random() * SHAPES.length)]);
    }
    renderDock();
}

// --- DRAG & DROP MANTIĞI ---
let ghost = document.getElementById("drag-ghost");

function startDrag(e, shape, index) {
    isDragging = true; draggedShape = shape; dragOriginIndex = index;
    
    // Ghost'u hazırla
    ghost.innerHTML = "";
    ghost.style.display = "grid";
    ghost.style.gridTemplateColumns = `repeat(${shape[0].length}, 28px)`;
    ghost.style.gap = "3px";
    shape.forEach(row => {
        row.forEach(cellVal => {
            let gCell = document.createElement("div");
            gCell.style.width = "28px"; gCell.style.height = "28px"; gCell.style.borderRadius = "4px";
            if(cellVal) { gCell.style.background = getTheme().bg; } 
            else { gCell.style.background = "transparent"; }
            ghost.appendChild(gCell);
        });
    });
    moveGhost(e);
}

document.onmousemove = (e) => {
    if(!isDragging) return;
    moveGhost(e);
    highlightGrid(e);
}

document.onmouseup = (e) => {
    if(!isDragging) return;
    isDragging = false; ghost.style.display = "none";
    
    let target = getHoveredGridCoord(e);
    if(target && canPlace(draggedShape, target.r, target.c)) {
        placeShape(draggedShape, target.r, target.c);
        dockShapes[dragOriginIndex] = null; // Dock'tan sil
        score += draggedShape.flat().reduce((a,b)=>a+b, 0) * 2; // Puan ver
        checkLines();
        updateBoardView();
        refillDock();
    }
    draggedShape = null;
    updateBoardView(); // Highlightları temizle
}

function moveGhost(e) {
    ghost.style.left = e.clientX - (ghost.offsetWidth / 2) + "px";
    ghost.style.top = e.clientY - (ghost.offsetHeight / 2) + "px";
}

function getHoveredGridCoord(e) {
    let boardRect = document.getElementById("board").getBoundingClientRect();
    if(e.clientX < boardRect.left || e.clientX > boardRect.right || e.clientY < boardRect.top || e.clientY > boardRect.bottom) return null;
    
    // Mouse'un grid üzerindeki yaklaşık hücresini bul. Ghost'un ortasını baz al.
    let mouseRelX = e.clientX - boardRect.left;
    let mouseRelY = e.clientY - boardRect.top;
    
    // Ghost'un boyutlarının yarısını çıkararak şeklin merkezini bulmaya çalışalım
    let ghostRect = ghost.getBoundingClientRect();
    let centerX = mouseRelX - (ghostRect.width / 2) + 14; // +14 bir hücrenin yarısı
    let centerY = mouseRelY - (ghostRect.height / 2) + 14;

    let c = Math.floor(centerX / (28 + 3)); // 28px hücre + 3px boşluk
    let r = Math.floor(centerY / (28 + 3));
    
    // Şeklin sol üst köşesinin denk geleceği tahmini hücre
    let shapeH = draggedShape.length; let shapeW = draggedShape[0].length;
    // Deneme yanılma ile en iyi hissettiren ofsetleme
    r = Math.round(r - (shapeH/2) + 0.5);
    c = Math.round(c - (shapeW/2) + 0.5);
    
    return {r, c};
}

function highlightGrid(e) {
    updateBoardView(); // Önce temizle
    let target = getHoveredGridCoord(e);
    if(!target) return;
    
    let valid = canPlace(draggedShape, target.r, target.c);
    for(let i=0; i<draggedShape.length; i++) {
        for(let j=0; j<draggedShape[0].length; j++) {
            if(draggedShape[i][j]) {
                let cell = document.getElementById(`c-${target.r+i}-${target.c+j}`);
                if(cell) cell.classList.add(valid ? "highlight" : "invalid");
            }
        }
    }
}

function canPlace(shape, r, c) {
    if(r < 0 || c < 0 || r + shape.length > BOARD_SIZE || c + shape[0].length > BOARD_SIZE) return false;
    for(let i=0; i<shape.length; i++) {
        for(let j=0; j<shape[0].length; j++) {
            if(shape[i][j] && grid[r+i][c+j]) return false;
        }
    }
    return true;
}

function placeShape(shape, r, c) {
    for(let i=0; i<shape.length; i++) {
        for(let j=0; j<shape[0].length; j++) {
            if(shape[i][j]) grid[r+i][c+j] = 1;
        }
    }
}

function checkLines() {
    let linesCleared = 0;
    // Satır
    for(let r=0; r<BOARD_SIZE; r++) {
        if(grid[r].every(v => v === 1)) {
            grid[r].fill(0); linesCleared++;
            animateClear(r, "row");
        }
    }
    // Sütun
    for(let c=0; c<BOARD_SIZE; c++) {
        let full = true;
        for(let r=0; r<BOARD_SIZE; r++) if(grid[r][c] === 0) full = false;
        if(full) {
            for(let r=0; r<BOARD_SIZE; r++) grid[r][c] = 0;
            linesCleared++;
            animateClear(c, "col");
        }
    }
    if(linesCleared > 0) score += linesCleared * 50 * linesCleared; // Kombo puanı
}

function animateClear(idx, type) {
    // Basit bir görsel efekt (Geliştirilebilir)
    let cells = [];
    if(type == "row") for(let c=0; c<BOARD_SIZE; c++) cells.push(document.getElementById(`c-${idx}-${c}`));
    else for(let r=0; r<BOARD_SIZE; r++) cells.push(document.getElementById(`c-${r}-${idx}`));
    
    cells.forEach(cell => {
        cell.style.transition = "transform 0.2s, opacity 0.2s";
        cell.style.transform = "scale(1.5)"; cell.style.opacity = "0";
    });
    setTimeout(() => updateBoardView(), 200);
}

function getCode(){
    if(score < 10) { alert("En az 10 puan yap!"); return; }
    let secureVal = (score * 13).toString(16).toUpperCase();
    let code = "FNK-" + secureVal + "-BL";
    document.getElementById("codeDisplay").innerText = code;
    document.getElementById("codeDisplay").style.display = "block";
    score = 0; grid = Array(BOARD_SIZE).fill().map(() => Array(BOARD_SIZE).fill(0));
    dockShapes = []; refillDock(); updateBoardView();
}

initBoard();
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
            if st.button("TESTİ BAŞLAT (+20 Puan)"):
                update_player_score(user_key, 20, user['name'], user['no'])
                st.toast("🎉 Tebrikler! +20 Puan eklendi.")
                time.sleep(0.5); st.rerun()
                
        with c2.container(border=True):
            st.markdown("### 💼 MESLEKİ ALAN")
            st.caption("Muhasebe ve Finansman Soruları")
            if st.button("TESTİ BAŞLAT (+20 Puan)"):
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
