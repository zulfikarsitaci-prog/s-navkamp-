import streamlit as st
import streamlit.components.v1 as components
import json
import os
import pandas as pd
import time
import urllib.parse

# --- 1. AYARLAR & CSS (FERAH TEMA) ---
st.set_page_config(page_title="Finans Kampüsü", page_icon="🏛️", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;700;900&family=Poppins:wght@300;400;600&display=swap');
    
    /* GEREKSİZLERİ GİZLE */
    .stDeployButton, footer, header { display: none !important; }
    [data-testid="stToolbar"] { display: none !important; }
    
    /* GENEL SAYFA (FERAH AÇIK RENK) */
    .stApp { background-color: #f4f6f9; color: #2c3e50; }
    
    /* FONTLAR */
    h1, h2, h3, h4 { font-family: 'Cinzel', serif !important; font-weight: 700 !important; color: #2c3e50 !important; }
    .stTabs button { font-family: 'Cinzel', serif !important; font-weight: 700 !important; }
    p, div, span, button, input { font-family: 'Poppins', sans-serif !important; }
    
    /* SEKMELER (TABS) - MODERN BEYAZ */
    .stTabs [data-baseweb="tab-list"] { 
        gap: 10px; background: #ffffff; padding: 10px; 
        border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); 
    }
    .stTabs [data-baseweb="tab"] { 
        height: 45px; border-radius: 8px; border: none; 
        font-weight: 600; font-size: 15px; color: #7f8c8d; 
    }
    .stTabs [aria-selected="true"] { 
        background-color: #2c3e50 !important; color: #f1c40f !important; 
        box-shadow: 0 4px 10px rgba(44, 62, 80, 0.3);
    }
    
    /* SKOR KARTI - PREMIUM GOLD */
    .score-box { 
        background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%); 
        padding: 25px; border-radius: 15px; text-align: center; 
        border-left: 5px solid #f1c40f; 
        box-shadow: 0 10px 30px rgba(0,0,0,0.08); 
    }
    .big-num { 
        font-family: 'Cinzel', serif; font-size: 48px; font-weight: 900; 
        color: #2c3e50; 
        text-shadow: 2px 2px 0px rgba(241, 196, 15, 0.2);
    }
    
    /* BANKA VEZNESİ */
    .bank-area { 
        background-color: #ffffff; padding: 20px; border-radius: 12px; 
        border: 2px dashed #27ae60; text-align: center; margin-top: 20px; 
        color: #27ae60; box-shadow: 0 5px 15px rgba(0,0,0,0.03);
    }
    
    /* YAN MENÜ */
    [data-testid="stSidebar"] { 
        background-color: #ffffff; border-right: 1px solid #eee; 
    }
    
    /* BUTONLAR */
    div.stButton > button { 
        border-radius: 8px; height: 50px; font-weight: bold; 
        border: 1px solid #ddd; transition: 0.3s; width: 100%; 
        background: white; color: #2c3e50;
    }
    div.stButton > button:hover { 
        border-color: #f1c40f; background-color: #f1c40f; color: white; 
        box-shadow: 0 5px 15px rgba(241, 196, 15, 0.3);
    }
    
    /* ÖZEL HTML BUTON (YEŞİL) */
    .html-save-btn { 
        display: block; width: 100%; background: #27ae60; 
        color: white !important; padding: 15px; text-align: center; 
        border-radius: 12px; font-weight: 800; font-size: 18px; 
        text-decoration: none; margin-top: 10px; transition: transform 0.2s; 
        box-shadow: 0 4px 10px rgba(39, 174, 96, 0.3);
    }
    .html-save-btn:hover { transform: scale(1.02); background: #219150; }
    </style>
""", unsafe_allow_html=True)

# --- 2. GÜVENLİ VERİTABANI ---
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

# --- 4. OYUN KODLARI (HTML/JS) - Arka planlar güncellendi ---

# Finans Oyunu (Lacivert Dashboard Teması)
FINANCE_GAME_HTML = """
<!DOCTYPE html>
<html>
<head>
<style>
body { background: #2c3e50; color: #ecf0f1; font-family: 'Poppins', sans-serif; padding: 10px; text-align: center; user-select:none; }
.top-bar { display: flex; justify-content: space-between; background: #34495e; padding: 15px; border-radius: 12px; border-bottom: 3px solid #f1c40f; margin-bottom: 20px; box-shadow: 0 5px 15px rgba(0,0,0,0.2); }
.money { font-size: 24px; font-weight: bold; color: #f1c40f; }
.grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px; }
.item { background: #34495e; padding: 12px; border-radius: 10px; cursor: pointer; transition: 0.1s; border: 1px solid #465c71; position: relative; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
.item:hover { border-color: #f1c40f; transform: translateY(-2px); background: #3e5871; }
.item:active { transform: scale(0.98); }
.item.locked { opacity: 0.5; filter: grayscale(1); pointer-events: none; }
.name { font-weight: bold; color: #fff; font-size: 13px; margin-bottom: 5px; }
.cost { color: #e74c3c; font-size: 11px; }
.income { color: #2ecc71; font-size: 11px; font-weight: bold; }
.count { position: absolute; top: -5px; right: -5px; background: #f1c40f; color: #2c3e50; padding: 2px 8px; border-radius: 10px; font-size: 11px; font-weight: bold; box-shadow: 0 2px 5px rgba(0,0,0,0.2); }
.btn-save { background: #27ae60; color: white; border: none; padding: 12px; width: 100%; border-radius: 8px; font-weight: bold; font-size: 16px; cursor: pointer; margin-top: 20px; box-shadow: 0 4px 0 #219150; }
.btn-save:active { transform: translateY(4px); box-shadow: none; }
.code-display { background: white; color: #2c3e50; padding: 10px; border-radius: 10px; margin-top: 10px; font-family: monospace; font-size: 16px; border: 2px dashed #f1c40f; display: none; }
.clicker-btn { width:90px; height:90px; border-radius:50%; background:radial-gradient(circle, #f1c40f 0%, #f39c12 100%); border:4px solid #fff; font-size:35px; cursor:pointer; box-shadow:0 5px 15px rgba(0,0,0,0.2); transition: 0.1s; }
.clicker-btn:active { transform: scale(0.95); }
</style>
</head>
<body>
<div class="top-bar">
    <div>KASA: <span id="money" class="money">0</span> ₺</div>
    <div style="font-size:11px; color:#bdc3c7; margin-top:5px;">GELİR: <span id="cps" style="color:#2ecc71;">0</span>/sn</div>
</div>
<div style="margin-bottom:20px;"><button onclick="clickCoin()" class="clicker-btn">👆</button></div>
<div class="grid" id="market"></div>
<button class="btn-save" onclick="generateCode()">🏦 BANKAYA TRANSFER KODU AL</button>
<div id="codeArea" class="code-display"><span id="codeVal" style="font-weight:bold;"></span></div>
<p id="info" style="font-size:10px; color:#bdc3c7; margin-top:5px; display:none;">Kodu kopyala ve uygulamadaki 'Banka Veznesi' kutusuna yapıştır.</p>
<script>
let money = 0;
let assets = [{n: "Limonata Standı", c: 50, i: 0.5, cnt: 0}, {n: "Simit Tezgahı", c: 350, i: 2, cnt: 0}, {n: "Kırtasiye Dükkanı", c: 1500, i: 8, cnt: 0}, {n: "Okul Kantini", c: 7500, i: 35, cnt: 0}, {n: "Servis Filosu", c: 35000, i: 150, cnt: 0}, {n: "Yazılım A.Ş.", c: 150000, i: 600, cnt: 0}, {n: "Uluslararası Holding", c: 1000000, i: 4500, cnt: 0}];
function updateUI() {
    document.getElementById('money').innerText = Math.floor(money).toLocaleString();
    let totalCps = assets.reduce((t, a) => t + (a.cnt * a.i), 0);
    document.getElementById('cps').innerText = totalCps.toFixed(1);
    let m = document.getElementById('market'); m.innerHTML = "";
    assets.forEach((a, i) => {
        let cost = Math.floor(a.c * Math.pow(1.25, a.cnt));
        let div = document.createElement('div'); div.className = "item " + (money >= cost ? "" : "locked"); div.onclick = () => buy(i);
        div.innerHTML = `<span class="count">${a.cnt}</span><div class="name">${a.n}</div><div class="cost">Maliyet: ${cost.toLocaleString()} ₺</div><div class="income">+${a.i}/sn</div>`;
        m.appendChild(div);
    });
}
function clickCoin() { money += 1; updateUI(); }
function buy(i) {
    let a = assets[i]; let cost = Math.floor(a.c * Math.pow(1.25, a.cnt));
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
</script></body></html>
"""

# Matrix Oyunu (Block Blast - Koyu Lacivert Tema)
MATRIX_GAME_HTML = """
<!DOCTYPE html>
<html>
<head>
<style>
body { background: #2c3e50; color: #ecf0f1; display: flex; flex-direction: column; align-items: center; justify-content: flex-start; height: 98vh; font-family: 'Poppins', sans-serif; user-select: none; overflow: hidden; padding-top: 10px; }
.board-container { padding: 5px; background: #34495e; border-radius: 10px; box-shadow: 0 10px 20px rgba(0,0,0,0.2); border: 2px solid #2c3e50; }
.board { display: grid; grid-template-columns: repeat(10, 28px); grid-template-rows: repeat(10, 28px); gap: 3px; }
.cell { width: 28px; height: 28px; background: #2c3e50; border-radius: 4px; border: 1px solid #1a252f; transition: background 0.2s; }
.cell.filled { border: none; }
.cell.highlight { background: rgba(255, 255, 255, 0.3); border: 1px dashed #fff; }
.cell.invalid { background: rgba(231, 76, 60, 0.4); border: 1px dashed #c0392b; }
.top-ui { display: flex; justify-content: space-between; width: 320px; margin-bottom: 15px; align-items: center; }
.score-box { background: #34495e; padding: 5px 15px; border-radius: 20px; border: 2px solid #f1c40f; font-weight: bold; color: #f1c40f; }
.btn-bank { background: #8e44ad; color: white; border: none; padding: 8px 15px; font-weight: bold; border-radius: 20px; cursor: pointer; font-size: 12px; }
.dock { display: flex; justify-content: center; gap: 20px; margin-top: 25px; height: 80px; align-items: center; background: rgba(0,0,0,0.1); padding: 10px; border-radius: 15px; width: 320px; }
.shape-preview { display: grid; gap: 2px; cursor: grab; transition: transform 0.1s; }
.shape-preview:active { cursor: grabbing; transform: scale(1.1); }
.preview-cell { width: 20px; height: 20px; border-radius: 3px; }
#drag-ghost { position: fixed; pointer-events: none; z-index: 100; display: none; opacity: 0.8; }
.code-box { background: white; color: #2c3e50; padding: 10px; margin-top: 10px; font-weight: bold; border: 2px dashed #f1c40f; display: none; font-size:14px; font-family: monospace; border-radius: 8px; text-align: center; width: 300px; }
</style>
</head>
<body>
<div class="top-ui">
    <div class="score-box">SKOR: <span id="score">0</span></div>
    <button class="btn-bank" onclick="getCode()">🏦 KOD AL</button>
</div>
<div class="board-container"><div class="board" id="board"></div></div>
<div class="dock" id="dock"></div>
<div id="drag-ghost"></div>
<div id="codeDisplay" class="code-box"></div>
<script>
const BOARD_SIZE = 10;
let grid = Array(BOARD_SIZE).fill().map(() => Array(BOARD_SIZE).fill(0));
let score = 0; let dockShapes = []; let isDragging = false; let draggedShape = null; let dragOriginIndex = -1;
const THEMES = [{ name: "Gold", bg: "#f1c40f", shadow: "#f39c12" }, { name: "Rose", bg: "#e94560", shadow: "#c0392b" }, { name: "Silver", bg: "#bdc3c7", shadow: "#7f8c8d" }, { name: "Purple", bg: "#9b59b6", shadow: "#8e44ad" }, { name: "Cyan", bg: "#00cec9", shadow: "#00b894" }];
const SHAPES = [[[1]], [[1, 1]], [[1], [1]], [[1, 1, 1]], [[1], [1], [1]], [[1, 1], [1, 1]], [[1, 0], [1, 0], [1, 1]], [[1, 1, 1], [0, 1, 0]], [[1, 1, 0], [0, 1, 1]]];
function getTheme() { return THEMES[Math.floor(score / 50) % THEMES.length]; }
function initBoard() {
    const boardDiv = document.getElementById("board"); boardDiv.innerHTML = "";
    for(let r=0; r<BOARD_SIZE; r++) { for(let c=0; c<BOARD_SIZE; c++) { let cell = document.createElement("div"); cell.className = "cell"; cell.id = `c-${r}-${c}`; boardDiv.appendChild(cell); } }
    updateBoardView(); refillDock();
}
function updateBoardView() {
    for(let r=0; r<BOARD_SIZE; r++) {
        for(let c=0; c<BOARD_SIZE; c++) {
            let cell = document.getElementById(`c-${r}-${c}`);
            cell.className = "cell"; cell.style.background = ""; cell.style.boxShadow = "";
            if(grid[r][c]) { let theme = getTheme(); cell.classList.add("filled"); cell.style.background = theme.bg; cell.style.boxShadow = `0 0 5px ${theme.shadow}`; }
        }
    }
    document.getElementById("score").innerText = score;
}
function renderDock() {
    const dockDiv = document.getElementById("dock"); dockDiv.innerHTML = "";
    dockShapes.forEach((shapeMatrix, index) => {
        if(shapeMatrix === null) { dockDiv.appendChild(document.createElement("div")); return; }
        let preview = document.createElement("div"); preview.className = "shape-preview";
        preview.style.gridTemplateColumns = `repeat(${shapeMatrix[0].length}, 20px)`;
        shapeMatrix.forEach(row => { row.forEach(cellVal => { let pCell = document.createElement("div"); pCell.className = "preview-cell"; if(cellVal) { pCell.style.background = getTheme().bg; } else { pCell.style.background = "transparent"; } preview.appendChild(pCell); }); });
        preview.onmousedown = (e) => startDrag(e, shapeMatrix, index);
        dockDiv.appendChild(preview);
    });
}
function refillDock() {
    if(dockShapes.every(s => s === null) || dockShapes.length === 0) { dockShapes = []; for(let i=0; i<3; i++) dockShapes.push(SHAPES[Math.floor(Math.random() * SHAPES.length)]); }
    renderDock();
}
let ghost = document.getElementById("drag-ghost");
function startDrag(e, shape, index) {
    isDragging = true; draggedShape = shape; dragOriginIndex = index;
    ghost.innerHTML = ""; ghost.style.display = "grid";
    ghost.style.gridTemplateColumns = `repeat(${shape[0].length}, 28px)`; ghost.style.gap = "3px";
    shape.forEach(row => { row.forEach(cellVal => { let gCell = document.createElement("div"); gCell.style.width = "28px"; gCell.style.height = "28px"; gCell.style.borderRadius = "4px"; if(cellVal) { gCell.style.background = getTheme().bg; } else { gCell.style.background = "transparent"; } ghost.appendChild(gCell); }); });
    moveGhost(e);
}
document.onmousemove = (e) => { if(!isDragging) return; moveGhost(e); highlightGrid(e); }
document.onmouseup = (e) => {
    if(!isDragging) return; isDragging = false; ghost.style.display = "none";
    let target = getHoveredGridCoord(e);
    if(target && canPlace(draggedShape, target.r, target.c)) {
        placeShape(draggedShape, target.r, target.c); dockShapes[dragOriginIndex] = null;
        score += draggedShape.flat().reduce((a,b)=>a+b, 0) * 2;
        checkLines(); updateBoardView(); refillDock();
    }
    draggedShape = null; updateBoardView();
}
function moveGhost(e) { ghost.style.left = e.clientX - (ghost.offsetWidth / 2) + "px"; ghost.style.top = e.clientY - (ghost.offsetHeight / 2) + "px"; }
function getHoveredGridCoord(e) {
    let boardRect = document.getElementById("board").getBoundingClientRect();
    if(e.clientX < boardRect.left || e.clientX > boardRect.right || e.clientY < boardRect.top || e.clientY > boardRect.bottom) return null;
    let mouseRelX = e.clientX - boardRect.left; let mouseRelY = e.clientY - boardRect.top;
    let ghostRect = ghost.getBoundingClientRect();
    let centerX = mouseRelX - (ghostRect.width / 2) + 14; let centerY = mouseRelY - (ghostRect.height / 2) + 14;
    let c = Math.floor(centerX / (28 + 3)); let r = Math.floor(centerY / (28 + 3));
    let shapeH = draggedShape.length; let shapeW = draggedShape[0].length;
    r = Math.round(r - (shapeH/2) + 0.5); c = Math.round(c - (shapeW/2) + 0.5);
    return {r, c};
}
function highlightGrid(e) {
    updateBoardView(); let target = getHoveredGridCoord(e); if(!target) return;
    let valid = canPlace(draggedShape, target.r, target.c);
    for(let i=0; i<draggedShape.length; i++) { for(let j=0; j<draggedShape[0].length; j++) { if(draggedShape[i][j]) { let cell = document.getElementById(`c-${target.r+i}-${target.c+j}`); if(cell) cell.classList.add(valid ? "highlight" : "invalid"); } } }
}
function canPlace(shape, r, c) {
    if(r < 0 || c < 0 || r + shape.length > BOARD_SIZE || c + shape[0].length > BOARD_SIZE) return false;
    for(let i=0; i<shape.length; i++) { for(let j=0; j<shape[0].length; j++) { if(shape[i][j] && grid[r+i][c+j]) return false; } } return true;
}
function placeShape(shape, r, c) { for(let i=0; i<shape.length; i++) { for(let j=0; j<shape[0].length; j++) { if(shape[i][j]) grid[r+i][c+j] = 1; } } }
function checkLines() {
    let linesCleared = 0;
    for(let r=0; r<BOARD_SIZE; r++) { if(grid[r].every(v => v === 1)) { grid[r].fill(0); linesCleared++; } }
    for(let c=0; c<BOARD_SIZE; c++) { let full = true; for(let r=0; r<BOARD_SIZE; r++) if(grid[r][c] === 0) full = false; if(full) { for(let r=0; r<BOARD_SIZE; r++) grid[r][c] = 0; linesCleared++; } }
    if(linesCleared > 0) score += linesCleared * 50 * linesCleared;
}
function getCode(){
    if(score < 10) { alert("En az 10 puan yap!"); return; }
    let secureVal = (score * 13).toString(16).toUpperCase();
    let code = "FNK-" + secureVal + "-BL";
    document.getElementById("codeDisplay").innerText = code; document.getElementById("codeDisplay").style.display = "block";
    score = 0; grid = Array(BOARD_SIZE).fill().map(() => Array(BOARD_SIZE).fill(0)); dockShapes = []; refillDock(); updateBoardView();
}
initBoard();
</script></body></html>
"""

# --- 5. UYGULAMA AKIŞI ---

# EKRAN 1: GİRİŞ
if not st.session_state.logged_in:
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown("<div style='text-align:center'><h1>🏛️ FİNANS KAMPÜSÜ</h1><p>Öğrenci Giriş Portalı</p></div>", unsafe_allow_html=True)
        with st.form("login"):
            ad = st.text_input("Ad Soyad")
            no = st.text_input("Okul No")
            if st.form_submit_button("SİSTEME GİRİŞ", type="primary"):
                if ad and no:
                    key = f"{no}_{ad.strip()}"
                    st.session_state.user_info = {"name": ad, "no": no, "key": key}
                    st.session_state.logged_in = True
                    st.rerun()
                else: st.error("Lütfen bilgileri giriniz.")

# EKRAN 2: ANA PANEL
else:
    user = st.session_state.user_info
    user_key = user['key']
    current_score = get_player_score(user_key)
    
    with st.sidebar:
        st.markdown(f"### 👤 {user['name'].upper()}")
        st.markdown(f"**🎓 No:** {user['no']}")
        st.markdown("---")
        # OTO KAYIT BUTONU
        safe_name = urllib.parse.quote(user['name'])
        safe_score = str(current_score)
        final_form_link = FORM_LINK_TASLAK.replace("AD_YOK", safe_name).replace("9999", safe_score)
        st.markdown(f"""<a href="{final_form_link}" target="_blank" class="html-save-btn">💾 SKORU LİSTEYE KAYDET</a>""", unsafe_allow_html=True)
        st.markdown("---")
        if st.button("ÇIKIŞ YAP", key="logout_btn"): # KEY EKLENDİ
            st.session_state.logged_in = False
            st.rerun()

    # Sekmeler
    t1, t2, t3, t4 = st.tabs(["🏠 PROFİL", "📚 DERSLER", "🎮 OYUN & BANKA", "🏆 SIRALAMA"])

    # TAB 1: PROFİL
    with t1:
        st.markdown(f"## HOŞGELDİN, {user['name'].split(' ')[0].upper()}")
        st.markdown(f"""
            <div class="score-box">
                <div style="font-size:16px; letter-spacing:3px; margin-bottom:15px; opacity:0.8; color:#2c3e50;">TOPLAM VARLIK</div>
                <div class="big-num">{current_score} ₺</div>
            </div>
        """, unsafe_allow_html=True)
        st.success("Bilgileriniz yerel veritabanında güvende.")

    # TAB 2: DERSLER
    with t2:
        st.subheader("SORU ÇÖZÜM MERKEZİ")
        c1, c2 = st.columns(2)
        with c1.container(border=True):
            st.markdown("### 📘 TYT HAZIRLIK")
            st.caption("Genel Yetenek Soruları")
            # --- KRİTİK DÜZELTME: UNIQUE KEY ---
            if st.button("TESTİ BAŞLAT (+20 Puan)", key="btn_tyt_start_fixed"): 
                update_player_score(user_key, 20, user['name'], user['no'])
                st.toast("Tebrikler! +20 Puan eklendi.")
                time.sleep(0.5); st.rerun()
                
        with c2.container(border=True):
            st.markdown("### 💼 MESLEKİ ALAN")
            st.caption("Muhasebe Soruları")
            # --- KRİTİK DÜZELTME: UNIQUE KEY ---
            if st.button("TESTİ BAŞLAT (+20 Puan)", key="btn_meslek_start_fixed"): 
                update_player_score(user_key, 20, user['name'], user['no'])
                st.toast("Tebrikler! +20 Puan eklendi.")
                time.sleep(0.5); st.rerun()

    # TAB 3: OYUNLAR & BANKA
    with t3:
        col_game, col_bank = st.columns([2, 1])
        
        with col_game:
            st.subheader("SİMÜLASYONLAR")
            oyun = st.selectbox("Oyun Seç:", ["Finans İmparatoru", "Asset Matrix (Block Blast)"])
            
            if oyun == "Finans İmparatoru":
                components.html(FINANCE_GAME_HTML, height=650)
            else:
                components.html(MATRIX_GAME_HTML, height=650)
        
        with col_bank:
            st.markdown("<div style='height: 80px;'></div>", unsafe_allow_html=True)
            st.markdown("""
                <div class="bank-area">
                    <h3 style="color:#2ecc71; margin:0;">🏦 BANKA VEZNESİ</h3>
                    <p style="font-size:13px; color:#aaa;">Güvenli Transfer</p>
                </div>
            """, unsafe_allow_html=True)
            
            transfer_code = st.text_input("Transfer Kodu:", placeholder="Örn: FNK-...")
            
            if st.button("PARA YATIR", type="primary", key="btn_deposit_fixed"): # KEY EKLENDİ
                amount = decode_transfer_code(transfer_code)
                if amount:
                    update_player_score(user_key, amount, user['name'], user['no'])
                    st.success(f"✅ Hesabına {amount} ₺ eklendi.")
                    st.balloons()
                    time.sleep(2)
                    st.rerun()
                else:
                    st.error("⛔ Geçersiz Kod!")

    # TAB 4: SIRALAMA
    with t4:
        st.subheader("🏆 LİDERLİK KÜRSÜSÜ")
        db = load_db()
        data = [{"Öğrenci": v['name'], "Puan": v['score']} for k,v in db.items()]
        if data:
            df = pd.DataFrame(data).sort_values("Puan", ascending=False).reset_index(drop=True)
            df.index += 1
            st.dataframe(df, use_container_width=True, height=500)
        else:
            st.info("Veri yok.")
