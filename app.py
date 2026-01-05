import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import requests
import json
import os
import time
import random
import database  # Veritabanı modülünün (database.py) yanına olduğundan emin ol
from datetime import datetime

# ==========================================
# 1. SAYFA VE GENEL AYARLAR
# ==========================================
st.set_page_config(
    page_title="Bağarası ÇPAL - Dijital Kampüs",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Veritabanını başlat
database.create_database()
if not database.login_user("admin", "6626"):
    database.add_user("admin", "6626", "admin")

# ==========================================
# 2. SABİTLER (GITHUB & DATA)
# ==========================================
GITHUB_USER = "zulfikarsitaci-prog"
GITHUB_REPO = "s-navkamp-"
GITHUB_BRANCH = "main"
GITHUB_BASE_URL = f"https://raw.githubusercontent.com/{GITHUB_USER}/{GITHUB_REPO}/{GITHUB_BRANCH}"

URL_LIFESIM = f"{GITHUB_BASE_URL}/lifesim_data.json"
URL_TYT_DATA = f"{GITHUB_BASE_URL}/tyt_data.json"
URL_TYT_PDF = f"{GITHUB_BASE_URL}/tytson8.pdf"
URL_MESLEK_SORULAR = f"{GITHUB_BASE_URL}/sorular.json"

# ==========================================
# 3. OYUN HTML KODLARI (TAM VERSİYONLAR)
# ==========================================

FINANCE_GAME_HTML = """
<!DOCTYPE html>
<html lang="tr">
<head>
<meta charset="UTF-8">
<style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;700;900&display=swap');
    body { background-color: #0f172a; color: #e2e8f0; font-family: 'Montserrat', sans-serif; user-select: none; padding: 10px; text-align: center; margin: 0; }
    .container { width: 100%; max-width: 100%; box-sizing: border-box; overflow-x: hidden; }
    .dashboard { display: flex; flex-wrap: wrap; justify-content: space-between; background: linear-gradient(145deg, #1e293b, #0f172a); padding: 15px; border-radius: 12px; border: 1px solid #334155; margin-bottom: 20px; gap: 10px; }
    .stat-box { text-align: left; flex: 1; min-width: 120px; }
    .stat-label { font-size: 9px; color: #94a3b8; letter-spacing: 1px; }
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
    .bank-btn:hover { background: #059669; }
    .code-display { background: #fff; color: #000; padding: 5px; margin-top: 5px; font-family: monospace; font-weight: bold; display: none; font-size: 12px; border-radius: 4px; width: 100%; box-sizing: border-box;}
</style>
</head>
<body>
<div class="container">
    <div class="dashboard">
        <div class="stat-box"><div class="stat-label">NAKİT VARLIK</div><div id="money" class="money-val">0 ₺</div></div>
        <div class="stat-box" style="text-align:right;"><div class="stat-label">PASİF GELİR</div><div id="cps" class="income-val">0.0 /sn</div></div>
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
        { name: "Fabrika", cost: 1000000, gain: 3500.0, count: 0 }, { name: "Kripto Madeni", cost: 5000000, gain: 15000.0, count: 0 },
        { name: "Uzay İstasyonu", cost: 50000000, gain: 200000.0, count: 0 }
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
        if (money < 100) { alert("En az 100 ₺ birikmeli."); return; }
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
        .quiz-box { background: #111; border: 1px solid #333; padding: 30px; border-radius: 8px; max-width: 500px; box-shadow: 0 0 50px rgba(255, 215, 0, 0.1); }
        .quiz-question { font-size: 1.2rem; color: #fff; margin-bottom: 20px; font-weight: 700; }
        .quiz-option { display: block; width: 100%; padding: 15px; margin: 10px 0; background: #222; border: 1px solid #333; color: #ccc; cursor: pointer; transition: 0.3s; text-align: left; border-radius: 4px; }
        .quiz-option:hover { background: #333; border-color: #666; }
        .feedback-msg { margin-top: 15px; font-style: italic; color: #FFD700; min-height: 40px; }
        .hap-bilgi-list { text-align: left; background: #111; padding: 20px; border-radius: 8px; border-left: 4px solid #FFD700; margin-bottom: 20px; font-size: 0.85rem; color: #ddd; }
        .hap-bilgi-list li { margin-bottom: 8px; }
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
        <div id="quizScreen" class="menu-screen hidden">
            <div class="quiz-box">
                <div id="quizQuestion" class="quiz-question">Soru</div>
                <div id="quizOptions"></div>
                <div id="quizFeedback" class="feedback-msg"></div>
            </div>
        </div>
        <div id="gameOverScreen" class="menu-screen hidden">
            <h1 style="color: #ff4444;">LİKİDİTE KRİZİ</h1>
            <p>Piyasa kilitlendi.</p>
            <div class="hap-bilgi-list"><strong style="display:block; margin-bottom:10px; color:#FFD700;">GÜNÜN HAP BİLGİLERİ:</strong><ul id="takeawayList"></ul></div>
            <p>Son Değer: <span id="finalScore" style="color:#fff; font-weight:bold;">$0</span></p>
            <button class="btn" onclick="initGame()">Yeniden Dene</button>
        </div>
    </div>
    <script>
        const canvas = document.getElementById('gameCanvas'); const ctx = canvas.getContext('2d');
        const scoreEl = document.getElementById('score'); const finalScoreEl = document.getElementById('finalScore');
        const levelEl = document.getElementById('level-indicator'); const startScreen = document.getElementById('startScreen');
        const gameOverScreen = document.getElementById('gameOverScreen'); const quizScreen = document.getElementById('quizScreen');
        const quizQuestionEl = document.getElementById('quizQuestion'); const quizOptionsEl = document.getElementById('quizOptions');
        const quizFeedbackEl = document.getElementById('quizFeedback'); const takeawayListEl = document.getElementById('takeawayList');
        const GRID_SIZE = 8; let CELL_SIZE = 30; let BOARD_OFFSET_X = 0; let BOARD_OFFSET_Y = 0;
        const THEMES = [{ name: "GOLD (Birikim)", start: '#FFD700', end: '#C5A028' }, { name: "PURPLE (Kaldıraç)", start: '#D500F9', end: '#7B1FA2' }, { name: "ROSE (Volatilite)", start: '#E0BFB8', end: '#B76E79' }];
        let currentLevel = 0; let levelThreshold = 30; 
        const QUESTIONS = [
            { q: "Varlığını nakde çevirme yeteneğine ne denir?", opts: ["A) Pasif Yatırım", "B) Likidite", "C) Enflasyon"], correct: 1, wrongFeedback: ["Yanlış.", "", "Yanlış."], successMsg: "Doğru! Likidite hayattır." },
            { q: "Tek büyük blok risklidir. Neden?", opts: ["A) Konsantrasyon Riski", "B) Piyasa Hızı", "C) Blok Rengi"], correct: 0, wrongFeedback: ["", "Değil.", "Değil."], successMsg: "Doğru! Çeşitlendirme yapmalısın." },
            { q: "Küçük yatırımların katlanarak büyümesi nedir?", opts: ["A) Devalüasyon", "B) Bileşik Getiri", "C) Arbitraj"], correct: 1, wrongFeedback: ["Değil.", "", "Değil."], successMsg: "Doğru! Dünyanın 8. harikası." }
        ];
        const TAKEAWAYS = ["LİKİDİTE HAYATTIR.", "ÇEŞİTLENDİRME RİSKİ AZALTIR.", "ZAMANLAMA HER ŞEYDİR."];
        let grid = [], score = 0, availablePieces = [], draggingPiece = null, isGameOver = false, isPaused = false, questionIndex = 0;
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
            score = 0; currentLevel = 0; questionIndex = 0; isGameOver = false; isPaused = false;
            updateScore(0); updateTheme();
            startScreen.classList.add('hidden'); gameOverScreen.classList.add('hidden'); quizScreen.classList.add('hidden');
            generateNewPieces(); resize(); draw();
        }
        function triggerQuiz() {
            if (questionIndex >= QUESTIONS.length) return;
            isPaused = true; quizScreen.classList.remove('hidden');
            const qData = QUESTIONS[questionIndex];
            quizQuestionEl.innerText = qData.q; quizFeedbackEl.innerText = ""; quizOptionsEl.innerHTML = "";
            qData.opts.forEach((opt, idx) => {
                const btn = document.createElement('div'); btn.className = 'quiz-option'; btn.innerText = opt;
                btn.onclick = () => handleQuizAnswer(idx, qData); quizOptionsEl.appendChild(btn);
            });
        }
        function handleQuizAnswer(idx, qData) {
            if (idx === qData.correct) {
                quizFeedbackEl.style.color = "#44ff44"; quizFeedbackEl.innerText = qData.successMsg;
                setTimeout(() => { quizScreen.classList.add('hidden'); isPaused = false; questionIndex++; draw(); }, 2000);
            } else { quizFeedbackEl.style.color = "#ffaa44"; quizFeedbackEl.innerText = qData.wrongFeedback[idx]; }
        }
        const SHAPES = [[[1]], [[1, 1]], [[1], [1]], [[1, 1, 1]], [[1], [1], [1]], [[1, 1], [1, 1]], [[1, 1, 1], [0, 1, 0]], [[1, 0], [1, 0], [1, 1]], [[1, 1, 1, 1]]];
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
            let oldScore = score; score += points; scoreEl.innerText = "$" + score; 
            let oldLevel = Math.floor(oldScore / levelThreshold); let newLevel = Math.floor(score / levelThreshold);
            if (newLevel > oldLevel) { currentLevel = newLevel; updateTheme(); triggerQuiz(); }
        }
        function updateTheme() {
            const theme = THEMES[currentLevel % THEMES.length];
            levelEl.innerText = "SEVİYE: " + theme.name; levelEl.style.color = theme.start; scoreEl.style.color = theme.start;
            if(!isGameOver) draw();
        }
        function draw() {
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            drawGrid(); drawPlacedBlocks(); drawAvailablePieces();
        }
        function drawGrid() {
            ctx.lineWidth = 2; ctx.strokeStyle = '#666'; ctx.beginPath();
            for (let i = 0; i <= GRID_SIZE; i++) {
                ctx.moveTo(BOARD_OFFSET_X, BOARD_OFFSET_Y + i * CELL_SIZE); ctx.lineTo(BOARD_OFFSET_X + GRID_SIZE * CELL_SIZE, BOARD_OFFSET_Y + i * CELL_SIZE);
                ctx.moveTo(BOARD_OFFSET_X + i * CELL_SIZE, BOARD_OFFSET_Y); ctx.lineTo(BOARD_OFFSET_X + i * CELL_SIZE, BOARD_OFFSET_Y + GRID_SIZE * CELL_SIZE);
            }
            ctx.stroke();
        }
        function drawCell(x, y, size, isPreview = false) {
             const theme = THEMES[currentLevel % THEMES.length];
             const gradient = ctx.createLinearGradient(x, y, x + size, y + size);
             if(isPreview) { gradient.addColorStop(0, hexToRgbA(theme.start, 0.4)); gradient.addColorStop(1, hexToRgbA(theme.end, 0.4)); } 
             else { gradient.addColorStop(0, theme.start); gradient.addColorStop(1, theme.end); }
            ctx.fillStyle = gradient; ctx.fillRect(x + 1, y + 1, size - 2, size - 2);
            ctx.strokeStyle = "rgba(255,255,255,0.7)"; ctx.lineWidth = 2; ctx.strokeRect(x + 1, y + 1, size - 2, size - 2);
        }
        function hexToRgbA(hex, alpha){
            let c; if(/^#([A-Fa-f0-9]{3}){1,2}$/.test(hex)){ c= hex.substring(1).split(''); if(c.length== 3){ c= [c[0], c[0], c[1], c[1], c[2], c[2]]; } c= '0x'+c.join(''); return 'rgba('+[(c>>16)&255, (c>>8)&255, c&255].join(',')+','+alpha+')'; } return hex;
        }
        function drawPlacedBlocks() {
            for (let row = 0; row < GRID_SIZE; row++) for (let col = 0; col < GRID_SIZE; col++) if (grid[row][col] === 1) drawCell(BOARD_OFFSET_X + col * CELL_SIZE, BOARD_OFFSET_Y + row * CELL_SIZE, CELL_SIZE);
        }
        function drawAvailablePieces() {
            availablePieces.forEach(piece => { if (piece.isDragging) return; drawShape(piece.matrix, piece.x, piece.y, CELL_SIZE * 0.5); });
            if (draggingPiece) {
                drawShape(draggingPiece.matrix, draggingPiece.x, draggingPiece.y, CELL_SIZE);
                const { gridX, gridY } = getGridCoordsFromMouse(draggingPiece.x, draggingPiece.y);
                if (canPlace(draggingPiece.matrix, gridX, gridY)) drawShape(draggingPiece.matrix, BOARD_OFFSET_X + gridX * CELL_SIZE, BOARD_OFFSET_Y + gridY * CELL_SIZE, CELL_SIZE, true);
            }
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
            takeawayListEl.innerHTML = "";
            TAKEAWAYS.forEach(item => { let li = document.createElement('li'); li.innerText = item; takeawayListEl.appendChild(li); });
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
            if(isGameOver || isPaused) return; e.preventDefault(); const pos = getEventPos(e);
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
# 4. SERVER VE YARDIMCI FONKSİYONLAR
# ==========================================
@st.cache_resource
class SchoolServer:
    def __init__(self):
        self.classes = {} 
        self.used_codes = set()
        self.create_class("GENEL")

    def create_class(self, class_code):
        if class_code not in self.classes:
            self.classes[class_code] = {}
        return True

    def join_or_update_student(self, class_code, username, points_to_add=0):
        if class_code not in self.classes: self.create_class(class_code)
        if username not in self.classes[class_code]: self.classes[class_code][username] = 0
        self.classes[class_code][username] += points_to_add
        return self.classes[class_code][username]

    def get_score(self, class_code, username):
        return self.classes.get(class_code, {}).get(username, 0)

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

server = SchoolServer()

@st.cache_data(ttl=300)
def fetch_json_data(url):
    try:
        r = requests.get(url)
        return r.json() if r.status_code == 200 else {}
    except: return {}

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

# --- GİRİŞ VE KAYIT EKRANI ---
if not st.session_state.logged_in:
    st.markdown("<h1 style='text-align:center;'>🎓 Bağarası ÇPAL Dijital Kampüs</h1>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        tab_log, tab_reg = st.tabs(["Giriş Yap", "Kayıt Ol (Öğrenci)"])
        with tab_log:
            with st.form("login_form"):
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
            with st.form("reg_form"):
                nu = st.text_input("Kullanıcı Adı")
                np = st.text_input("Şifre", type="password")
                if st.form_submit_button("Kayıt Ol"):
                    if database.add_user(nu, np, "student"): st.success("Kayıt başarılı! Giriş yapınız.")
                    else: st.error("Kullanıcı adı dolu.")

# --- ANA UYGULAMA ---
else:
    with st.sidebar:
        st.title(st.session_state.username)
        st.write(f"Rol: {st.session_state.user_role}")
        
        if st.session_state.user_role == "student":
            st.divider()
            code_input = st.text_input("Sınıf Kodu Gir", placeholder="Örn: 1234")
            if st.button("Sınıfa Geç"):
                st.session_state.class_code = code_input
                server.join_or_update_student(code_input, st.session_state.username)
                st.success(f"Sınıf: {code_input}")
                st.rerun()
        
        st.divider()
        if st.button("Çıkış"):
            st.session_state.logged_in = False
            st.rerun()

    # --- ÖĞRENCİ PANELİ (GÜNCELLENDİ: TYT/MESLEK + YENİ SINAV) ---
    if st.session_state.user_role == "student":
        st.header(f"Merhaba, {st.session_state.username}")
        
        tabs = st.tabs(["🏆 Kampüs", "📚 Dersler & Test", "🎮 Oyunlar", "💼 LifeSim"])
        
        with tabs[0]: # KAMPÜS
            c1, c2 = st.columns([1,2])
            with c1:
                st.metric("Puanın", f"{server.get_score(st.session_state.class_code, st.session_state.username)} ₺")
                kod = st.text_input("Puan Kodu")
                if st.button("Yükle"):
                    res, msg = server.redeem_code(st.session_state.class_code, st.session_state.username, kod)
                    if res: st.success(f"Yüklendi! Yeni: {msg}")
                    else: st.error(msg)
                
                st.divider()
                st.subheader("📢 Duyurular")
                anns = database.get_announcements()
                if anns:
                    for a in anns:
                        st.info(f"{a[1]}: {a[2]}")
                else: st.write("Duyuru yok.")

            with c2:
                st.subheader("Sıralama")
                st.dataframe(server.get_leaderboard(st.session_state.class_code), use_container_width=True)

        with tabs[1]: # DERSLER (TYT + MESLEK + YAZILI)
            ders_modu = st.radio("Çalışma Modu Seçiniz:", ["TYT Çalışma", "Meslek Soruları", "11. Sınıf Yazılı Hazırlık (İnteraktif)"], horizontal=True)
            st.divider()
            
            # --- 1. TYT MODU ---
            if ders_modu == "TYT Çalışma":
                tyt_data = fetch_json_data(URL_TYT_DATA)
                if tyt_data:
                    dersler = sorted(list(set([v.get('ders') for v in tyt_data.values() if 'ders' in v])))
                    s_ders = st.selectbox("Ders Seçiniz:", dersler)
                    s_pages = []
                    for k, v in tyt_data.items():
                        if v.get('ders') == s_ders: s_pages.append((k, v))
                    s_pages.sort(key=lambda x: int(x[0]) if x[0].isdigit() else 999)
                    
                    if s_pages:
                        sel = st.selectbox("Sayfa Seçiniz:", s_pages, format_func=lambda x: f"Sayfa {x[0]}")
                        p_no, det = sel
                        
                        c_p, c_o = st.columns([1.5, 1])
                        with c_p:
                            st.markdown(f'<embed src="{URL_TYT_PDF}#page={p_no}" width="100%" height="800px" type="application/pdf">', unsafe_allow_html=True)
                        with c_o:
                            with st.form(f"tyt_{p_no}"):
                                ans = {}
                                for i, q in enumerate(det['sorular']):
                                    st.write(f"**Soru {q}**")
                                    ans[i] = st.radio(f"C{q}", ['A','B','C','D','E'], horizontal=True, key=f"rad_{p_no}_{q}", index=None)
                                if st.form_submit_button("KONTROL ET"):
                                    d = 0
                                    for i, q in enumerate(det['sorular']):
                                        if ans[i] == det['cevaplar'][i]: d += 1
                                    sc = d * 50
                                    st.success(f"{d} Doğru. +{sc} Puan")
                                    if sc > 0:
                                        server.join_or_update_student(st.session_state.class_code, st.session_state.username, sc)
            
            # --- 2. MESLEK MODU ---
            elif ders_modu == "Meslek Soruları":
                m_data = fetch_json_data(URL_MESLEK_SORULAR)
                if m_data:
                    root = m_data.get("KONU_TARAMA", m_data)
                    sinif = st.selectbox("Sınıf Düzeyi:", list(root.keys()))
                    if sinif:
                        ders = st.selectbox("Ders Adı:", list(root[sinif].keys()))
                        if ders:
                            test = st.selectbox("Konu:", list(root[sinif][ders].keys()))
                            if test:
                                qs = root[sinif][ders][test]
                                with st.form(f"meslek_{test}"):
                                    mans = {}
                                    for i, q in enumerate(qs):
                                        st.write(f"**{i+1}. {q['soru']}**")
                                        mans[i] = st.radio("Cevap:", q['secenekler'], key=f"mrad_{i}", index=None)
                                    if st.form_submit_button("TESTİ BİTİR"):
                                        dm = 0
                                        for i, q in enumerate(qs):
                                            if mans[i] == q['cevap']: dm += 1
                                        pm = dm * 100
                                        st.success(f"{dm} Doğru. +{pm} Puan")
                                        if pm > 0:
                                            server.join_or_update_student(st.session_state.class_code, st.session_state.username, pm)

            # --- 3. YAZILI HAZIRLIK MODU (Yeni Eklenen) ---
            elif ders_modu == "11. Sınıf Yazılı Hazırlık (İnteraktif)":
                ders_secimi = st.selectbox("Yazılı Seçiniz", ["İş ve Sosyal Güvenlik Hukuku", "Maliyet Muhasebesi"])
                
                if ders_secimi == "İş ve Sosyal Güvenlik Hukuku":
                    st.subheader("📝 11. Sınıf İş Hukuku - 1. Dönem 2. Yazılı Hazırlık")
                    st.info("Senaryo: Söke OSB'de 'Ege Tekstil A.Ş.' sahibi Ali Bey, yönetimi Ayşe Hanım'a bırakmıştır. İşçi Mehmet Bey servise binerken yaralanmıştır.")

                    with st.expander("BÖLÜM A: Kavramlar ve Senaryo Analizi", expanded=True):
                        with st.form("hukuk_a"):
                            q1_a = st.text_input("1. Hukuken asıl İşveren kimdir?")
                            q1_b = st.text_input("2. İşveren Vekili kimdir?")
                            q1_c = st.radio("3. Servis aracı işyeri sınırına dahil midir?", ["Evet", "Hayır"])
                            st.markdown("**İş Sözleşmesi Unsurları:**")
                            c1, c2, c3 = st.columns(3)
                            q2_a = c1.text_input("Unsur 1 (Emek)")
                            q2_b = c2.text_input("Unsur 2 (Para)")
                            q2_c = c3.text_input("Unsur 3 (Bağımlılık)")
                            
                            if st.form_submit_button("A Bölümünü Kontrol Et"):
                                score = 0
                                if "Ege Tekstil" in q1_a or "Tüzel" in q1_a: score += 5
                                if "Ayşe" in q1_b: score += 5
                                if q1_c == "Evet": score += 10
                                if q2_a and q2_b and q2_c: score += 10
                                st.info(f"Puan: {score}/30. (Doğru: Ege Tekstil, Ayşe Hanım, Evet, İş Görme, Ücret, Bağımlılık)")

                    with st.expander("BÖLÜM C: Fazla Çalışma Hesaplaması"):
                        st.write("Veri: Haftalık normal süre 45 saat. Mehmet Bey 50 saat çalıştı. Saatlik ücreti 200 TL.")
                        with st.form("hukuk_c"):
                            fc_saat = st.number_input("Kaç saat fazla çalışma?", min_value=0)
                            fc_ucret = st.number_input("1 Saatlik Zamlı (%50) Ücret (TL)?", min_value=0)
                            fc_toplam = st.number_input("Toplam Fazla Çalışma Ücreti (TL)?", min_value=0)
                            
                            if st.form_submit_button("Hesapla ve Kontrol Et"):
                                if fc_saat == 5 and fc_ucret == 300 and fc_toplam == 1500:
                                    st.balloons()
                                    st.success("TEBRİKLER! Hepsi Doğru. (5 Saat * 300 TL = 1500 TL)")
                                    server.join_or_update_student(st.session_state.class_code, st.session_state.username, 30)
                                else:
                                    st.error(f"Hatalı. Doğrusu: 5 Saat, 300 TL, 1500 TL olmalıydı.")

                elif ders_secimi == "Maliyet Muhasebesi":
                    st.subheader("📊 11. Sınıf Maliyet Muhasebesi Uygulamaları")
                    st.markdown("### SORU 1: Gider Dağıtımı (I. Dağıtım)")
                    data_dagitim = {"Gider Yerleri": ["Kesim", "Dikim", "Ütü", "Paketleme"], "Personel": [60, 70, 40, 30], "Alan (m2)": [500, 600, 200, 200]}
                    st.dataframe(pd.DataFrame(data_dagitim), hide_index=True)
                    st.info("Yemek: 20.000 TL (Personele göre) | Temizlik: 30.000 TL (Alana göre)")

                    with st.form("muh_s1"):
                        c1, c2 = st.columns(2)
                        ans_yemek_kesim = c1.number_input("Kesim Yemek Payı (TL)?", step=100)
                        ans_temizlik_dikim = c2.number_input("Dikim Temizlik Payı (TL)?", step=100)
                        if st.form_submit_button("Kontrol Et"):
                            if ans_yemek_kesim == 6000 and ans_temizlik_dikim == 12000:
                                st.success("Doğru Hesaplama!")
                                server.join_or_update_student(st.session_state.class_code, st.session_state.username, 20)
                            else: st.error("Hatalı. (Yemek Katsayı: 100, Temizlik Katsayı: 20)")
                    
                    st.divider()
                    st.markdown("### SORU 2: FIFO")
                    st.code("01.05: Devir 5000 kg @ 30 TL\n10.05: Çıkan 3500 kg\n15.05: Giren 5500 kg @ 35 TL\n21.05: Çıkan 4000 kg")
                    with st.form("muh_s2"):
                        kalan = st.number_input("Kalan Stok Değeri (TL)?", step=100)
                        if st.form_submit_button("FIFO Kontrol"):
                            if kalan == 105000:
                                st.success("Doğru! (3000 kg * 35 TL)")
                                server.join_or_update_student(st.session_state.class_code, st.session_state.username, 20)
                            else: st.error("Yanlış.")

        with tabs[2]: # OYUNLAR (DÜZELTİLDİ)
            secim = st.selectbox("Oyun Seç", ["Finans İmparatoru", "Asset Matrix"])
            if secim == "Finans İmparatoru": components.html(FINANCE_GAME_HTML, height=600)
            else: components.html(ASSET_MATRIX_HTML, height=600)

        with tabs[3]: # LIFESIM
            components.html(load_lifesim(), height=800, scrolling=True)

    # --- ADMIN VE ÖĞRETMEN PANELLERİ (GERİ GETİRİLDİ) ---
    elif st.session_state.user_role == "admin":
        st.header("⚙️ Yönetici Paneli")
        tab1, tab2 = st.tabs(["Kullanıcı Ekle", "Kullanıcı Listesi"])
        with tab1:
            with st.form("add_user_admin"):
                u_name = st.text_input("Kullanıcı Adı")
                u_pass = st.text_input("Şifre")
                u_role = st.selectbox("Rol", ["teacher", "admin", "student"])
                if st.form_submit_button("Kaydet"):
                    if database.add_user(u_name, u_pass, u_role): st.success("Eklendi.")
                    else: st.error("Kullanıcı var.")
        with tab2:
            users = database.get_all_users()
            df = pd.DataFrame(users, columns=["Kullanıcı", "Rol"])
            st.dataframe(df, use_container_width=True)
            to_del = st.selectbox("Silinecek", df["Kullanıcı"])
            if st.button("Sil"):
                if to_del != "admin": database.delete_user(to_del); st.rerun()
                else: st.error("Admin silinemez.")

    elif st.session_state.user_role == "teacher":
        st.header("👨‍🏫 Öğretmen Paneli")
        if "created_code" not in st.session_state:
            st.session_state.created_code = str(random.randint(1000, 9999))
            server.create_class(st.session_state.created_code)
        
        st.info(f"Ders Kodunuz: {st.session_state.created_code}")
        
        tab1, tab2 = st.tabs(["Liderlik", "Duyuru"])
        with tab1:
            st.dataframe(server.get_leaderboard(st.session_state.created_code), use_container_width=True)
        with tab2:
            with st.form("ann_form"):
                baslik = st.text_input("Başlık")
                icerik = st.text_area("İçerik")
                if st.form_submit_button("Yayınla"):
                    database.add_announcement(baslik, icerik, st.session_state.username)
                    st.success("Yayınlandı.")
