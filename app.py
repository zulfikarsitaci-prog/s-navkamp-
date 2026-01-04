import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import requests
import json
import os
import time
import random

# 1. SAYFA AYARLARI
st.set_page_config(
    page_title="Bağarası ÇPAL - Dijital Kampüs",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ==========================================
# 🧠 CANLI HAFIZA SİSTEMİ (SUNUCU & GÜVENLİK)
# ==========================================
@st.cache_resource
class SchoolServer:
    def __init__(self):
        # Sınıflar: { "DERS_KODU": { "OKUL_NO": {"ad": "Ali", "puan": 0} } }
        self.classes = {} 
        # Kullanılan Kodlar Havuzu: ["FNK-A1-99", "FNK-B2-101"]
        self.used_codes = set() 

    def create_class(self, class_code):
        if class_code not in self.classes:
            self.classes[class_code] = {}
        return True

    def join_student(self, class_code, name, school_no):
        if class_code in self.classes:
            if str(school_no) not in self.classes[class_code]:
                self.classes[class_code][str(school_no)] = {"ad": name, "puan": 0}
            return True
        return False

    def update_score(self, class_code, school_no, points):
        """Puanı doğrudan günceller (Soru çözümleri için)"""
        if class_code in self.classes and str(school_no) in self.classes[class_code]:
            self.classes[class_code][str(school_no)]["puan"] += points
            return self.classes[class_code][str(school_no)]["puan"]
        return 0

    def redeem_code(self, class_code, school_no, code_string):
        """
        Kod bozdurma işlemi (Oyunlar için).
        Aynı kodun tekrar kullanılmasını engeller.
        """
        # 1. Kod daha önce kullanıldı mı?
        if code_string in self.used_codes:
            return False, "Bu kod daha önce kullanıldı!"

        # 2. Kod Formatı ve Değer Çözme
        try:
            parts = code_string.split('-')
            # Format: FNK-{HEX}-{RND}
            if len(parts) != 3 or parts[0] != "FNK":
                return False, "Geçersiz kod formatı!"
            
            # Puanı hesapla (Hex -> Int / 13)
            hex_val = parts[1]
            amount = int(int(hex_val, 16) / 13)
            
            if amount <= 0:
                return False, "Geçersiz tutar!"

            # 3. İşlemi Gerçekleştir
            self.used_codes.add(code_string) # Kodu kullanılanlara ekle
            new_balance = self.update_score(class_code, school_no, amount)
            
            return True, new_balance

        except Exception as e:
            return False, "Kod çözülemedi."

    def get_leaderboard(self, class_code):
        if class_code in self.classes:
            data = []
            for no, info in self.classes[class_code].items():
                data.append({"Okul No": no, "Ad Soyad": info["ad"], "Puan": info["puan"]})
            if data:
                df = pd.DataFrame(data)
                return df.sort_values(by="Puan", ascending=False).reset_index(drop=True)
        return pd.DataFrame(columns=["Sıra", "Okul No", "Ad Soyad", "Puan"])

server = SchoolServer()

# ==========================================
# 🔗 GITHUB AYARLARI
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
# 3. YARDIMCI FONKSİYONLAR
# ==========================================
@st.cache_data(ttl=300)
def fetch_json_data(url):
    try:
        response = requests.get(url)
        if response.status_code == 200: return json.loads(response.text)
    except: pass
    return {}

def load_lifesim_html():
    try:
        if os.path.exists("game.html"):
            with open("game.html", "r", encoding="utf-8") as f: html = f.read()
        else:
            resp = requests.get(f"{GITHUB_BASE_URL}/game.html")
            html = resp.text if resp.status_code == 200 else "<h3>game.html bulunamadı</h3>"
        
        data = fetch_json_data(URL_LIFESIM)
        if not data: data = []
        json_str = json.dumps(data)
        return html.replace("// PYTHON_DATA_HERE", f"var scenarios = {json_str};")
    except: return "<h3>Yükleme Hatası</h3>"

# ==========================================
# 🎮 OYUN KODLARI
# ==========================================

# 1. FİNANS İMPARATORU (Aynı kalıyor)
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
        let val = Math.floor(money); 
        let hex = (val * 13).toString(16).toUpperCase(); 
        // RASTGELE SAYI EKLENDİ (Anti-Cheat)
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

# 2. ASSET MATRIX (8x8 GÜNCELLENMİŞ SÜRÜM)
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
        
        /* EK: Banka Butonu Stili */
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
        <div class="bank-btn-overlay">
            <button class="mini-btn" onclick="getTransferCode()">🏦 BANKAYA AKTAR</button>
        </div>
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
            <div class="hap-bilgi-list">
                <strong style="display:block; margin-bottom:10px; color:#FFD700;">GÜNÜN HAP BİLGİLERİ:</strong>
                <ul id="takeawayList"></ul>
            </div>
            <p>Son Değer: <span id="finalScore" style="color:#fff; font-weight:bold;">$0</span></p>
            <button class="btn" onclick="initGame()">Yeniden Dene</button>
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
        const quizScreen = document.getElementById('quizScreen');
        const quizQuestionEl = document.getElementById('quizQuestion');
        const quizOptionsEl = document.getElementById('quizOptions');
        const quizFeedbackEl = document.getElementById('quizFeedback');
        const takeawayListEl = document.getElementById('takeawayList');

        const GRID_SIZE = 8; // GÜNCELLENDİ: 8x8
        let CELL_SIZE = 30; 
        let BOARD_OFFSET_X = 0;
        let BOARD_OFFSET_Y = 0;
        
        const THEMES = [
            { name: "GOLD (Birikim)", start: '#FFD700', end: '#C5A028' },
            { name: "PURPLE (Kaldıraç)", start: '#D500F9', end: '#7B1FA2' },
            { name: "ROSE (Volatilite)", start: '#E0BFB8', end: '#B76E79' }
        ];
        
        let currentLevel = 0;
        let levelThreshold = 30; 

        const QUESTIONS = [
            { q: "Varlığını nakde çevirme yeteneğine ne denir?", opts: ["A) Pasif Yatırım", "B) Likidite", "C) Enflasyon"], correct: 1, wrongFeedback: ["Yanlış.", "", "Yanlış."], successMsg: "Doğru! Likidite hayattır." },
            { q: "Tek büyük blok risklidir. Neden?", opts: ["A) Konsantrasyon Riski", "B) Piyasa Hızı", "C) Blok Rengi"], correct: 0, wrongFeedback: ["", "Değil.", "Değil."], successMsg: "Doğru! Çeşitlendirme yapmalısın." },
            { q: "Küçük yatırımların katlanarak büyümesi?", opts: ["A) Devalüasyon", "B) Bileşik Getiri", "C) Arbitraj"], correct: 1, wrongFeedback: ["Değer kaybıdır.", "", "Fiyat farkıdır."], successMsg: "Doğru! Dünyanın 8. harikası." }
        ];

        const TAKEAWAYS = ["LİKİDİTE HAYATTIR.", "ÇEŞİTLENDİRME RİSKİ AZALTIR.", "ZAMANLAMA HER ŞEYDİR."];

        let grid = [], score = 0, availablePieces = [], draggingPiece = null, isGameOver = false, isPaused = false, questionIndex = 0;

        function resize() {
            const maxWidth = window.innerWidth * 0.95;
            const maxHeight = window.innerHeight * 0.85; 
            let size = Math.min(maxWidth, maxHeight * 0.75); 
            CELL_SIZE = Math.floor(size / GRID_SIZE);
            canvas.width = CELL_SIZE * GRID_SIZE + 20; 
            canvas.height = CELL_SIZE * GRID_SIZE + 130; 
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
                const btn = document.createElement('div');
                btn.className = 'quiz-option'; btn.innerText = opt;
                btn.onclick = () => handleQuizAnswer(idx, qData);
                quizOptionsEl.appendChild(btn);
            });
        }

        function handleQuizAnswer(idx, qData) {
            if (idx === qData.correct) {
                quizFeedbackEl.style.color = "#44ff44"; quizFeedbackEl.innerText = qData.successMsg;
                setTimeout(() => { quizScreen.classList.add('hidden'); isPaused = false; questionIndex++; draw(); }, 2000);
            } else {
                quizFeedbackEl.style.color = "#ffaa44"; quizFeedbackEl.innerText = qData.wrongFeedback[idx];
            }
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
            ctx.lineWidth = 2; // KALINLIK
            ctx.strokeStyle = '#666'; // RENK (DAHA BELİRGİN)
            ctx.beginPath();
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
            } else {
                draggingPiece.x = draggingPiece.baseX; draggingPiece.y = draggingPiece.baseY; draggingPiece.isDragging = false;
            }
            draggingPiece = null; draw();
        }
        
        function getTransferCode() {
            if(score < 50) { alert("En az 50 puan gerekli."); return; }
            let val = score; 
            let hex = (val * 13).toString(16).toUpperCase(); 
            // RANDOM EKLE (Anti-Cheat)
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
# 4. ARAYÜZ (Bağarası ÇPAL Teması)
# ==========================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;700;900&family=Poppins:wght@300;400;600&display=swap');
    .stApp { background-color: #f8f9fa; color: #2c3e50; font-family: 'Poppins', sans-serif; }
    [data-testid="stSidebar"] { display: none; }
    h1, h2, h3, .stTabs button { font-family: 'Cinzel', serif !important; color: #2c3e50 !important; }
    .stTabs [data-baseweb="tab-list"] { gap: 10px; background-color: #ffffff; padding: 10px 20px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); border-bottom: 2px solid #D84315; }
    .stTabs [data-baseweb="tab"] { height: 50px; border: none; font-size: 16px; font-weight: 700; color: #555; background-color: transparent; }
    .stTabs [aria-selected="true"] { color: #D84315 !important; border-bottom: 3px solid #D84315 !important; }
    .stButton>button { background-color: #2c3e50; color: white; border-radius: 8px; border: none; padding: 10px 20px; font-weight: bold; transition: 0.3s; }
    .stButton>button:hover { background-color: #D84315; color: white; }
    .login-container { background: white; padding: 40px; border-radius: 20px; box-shadow: 0 10px 25px rgba(0,0,0,0.1); text-align: center; border-top: 5px solid #D84315; }
    .bank-box { background: #e8f5e9; border: 2px dashed #27ae60; padding: 20px; border-radius: 15px; text-align: center; margin-bottom: 20px; }
    .optik-box { background:white; padding:15px; border-radius:10px; margin-bottom:10px; border-left:4px solid #D84315; box-shadow: 0 2px 5px rgba(0,0,0,0.05); }
    .leader-table { width: 100%; border-collapse: collapse; font-family: 'Poppins', sans-serif; }
    .leader-table th { background: #2c3e50; color: white; padding: 10px; text-align: left; }
    .leader-table td { border-bottom: 1px solid #ddd; padding: 10px; }
    .leader-table tr:nth-child(even) { background-color: #f2f2f2; }
</style>
""", unsafe_allow_html=True)

if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'user_role' not in st.session_state: st.session_state.user_role = "" # "student" or "teacher"
if 'user_name' not in st.session_state: st.session_state.user_name = ""
if 'user_no' not in st.session_state: st.session_state.user_no = ""
if 'class_code' not in st.session_state: st.session_state.class_code = ""
if 'bank_balance' not in st.session_state: st.session_state.bank_balance = 0

# --- EKRAN 1: GİRİŞ EKRANI (TABLI) ---
if not st.session_state.logged_in:
    st.markdown("<br><br>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        st.markdown("""
        <div class="login-container">
            <h1 style="font-size: 2.2rem; margin-bottom: 0;">🎓 Bağarası ÇPAL</h1>
            <h2 style="color: #555 !important; margin-top: 0;">Dijital Eğitim Kampüsü</h2>
            <hr style="border: 1px solid #eee; margin: 20px 0;">
        </div>
        """, unsafe_allow_html=True)
        
        tab_student, tab_teacher = st.tabs(["ÖĞRENCİ GİRİŞİ", "ÖĞRETMEN GİRİŞİ"])
        
        with tab_student:
            with st.form("student_login"):
                ad = st.text_input("Adı Soyadı")
                no = st.text_input("Okul Numarası")
                code = st.text_input("Ders Kodu (Öğretmeninizden Alın)")
                if st.form_submit_button("Sınıfa Katıl"):
                    if ad and no and code:
                        if server.join_student(code, ad, no):
                            st.session_state.logged_in = True
                            st.session_state.user_role = "student"
                            st.session_state.user_name = ad
                            st.session_state.user_no = no
                            st.session_state.class_code = code
                            st.rerun()
                        else:
                            st.error("Ders kodu bulunamadı veya ders aktif değil!")
                    else:
                        st.error("Lütfen tüm alanları doldurun.")

        with tab_teacher:
            with st.form("teacher_login"):
                t_pass = st.text_input("Yönetici Şifresi", type="password")
                if st.form_submit_button("Ders Başlat"):
                    if t_pass == "1234": # Basit şifre (Değiştirilebilir)
                        # Rastgele 4 haneli kod üret
                        new_code = str(random.randint(1000, 9999))
                        server.create_class(new_code)
                        st.session_state.logged_in = True
                        st.session_state.user_role = "teacher"
                        st.session_state.class_code = new_code
                        st.rerun()
                    else:
                        st.error("Hatalı şifre!")

# --- EKRAN 2: UYGULAMA İÇİ ---
else:
    # ---------------- ÖĞRETMEN PANELİ ----------------
    if st.session_state.user_role == "teacher":
        st.markdown(f"""
        <div style="background:#2c3e50; padding:20px; border-radius:10px; color:white; text-align:center; margin-bottom:20px;">
            <h2>👨‍🏫 ÖĞRETMEN PANELİ</h2>
            <p style="font-size:18px;">DERS KODU: <span style="font-size:32px; font-weight:bold; color:#f1c40f; background:rgba(255,255,255,0.1); padding:5px 15px; border-radius:5px;">{st.session_state.class_code}</span></p>
            <small>Öğrenciler bu kodu girerek sisteme dahil olabilirler.</small>
        </div>
        """, unsafe_allow_html=True)
        
        c_refresh, c_data = st.columns([1, 4])
        with c_refresh:
            if st.button("🔄 LİSTEYİ YENİLE", use_container_width=True):
                st.rerun()
                
        with c_data:
            df = server.get_leaderboard(st.session_state.class_code)
            if not df.empty:
                # Özel HTML Tablo (Daha şık görünüm)
                table_html = df.to_html(index=False, classes="leader-table")
                st.markdown(table_html, unsafe_allow_html=True)
            else:
                st.info("Henüz derse katılan öğrenci yok.")

        if st.button("🚪 Dersi Bitir / Çıkış"):
            st.session_state.logged_in = False
            st.rerun()

    # ---------------- ÖĞRENCİ PANELİ ----------------
    elif st.session_state.user_role == "student":
        # Üst Bilgi
        st.markdown(f"""
        <div style="display:flex; justify-content:space-between; align-items:center; padding:10px 20px; background:white; border-radius:10px; margin-bottom:20px; box-shadow: 0 2px 5px rgba(0,0,0,0.05);">
            <div style="font-family:'Cinzel'; font-weight:bold; font-size:18px; color:#2c3e50;">🎓 Bağarası ÇPAL</div>
            <div style="font-family:'Poppins'; font-size:14px; color:#555;">
                {st.session_state.user_name} | 🏦 Cüzdan: <span style="color:#27ae60; font-weight:bold;">{st.session_state.bank_balance} ₺</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        tab_ana, tab_soru, tab_eglence, tab_lifesim = st.tabs(["🏆 ANA EKRAN", "📚 SORU ÇÖZÜM", "🎮 OYUN ALANI", "💼 LIFESIM"])

        # 1. ANA EKRAN (Banka & Sıralama)
        with tab_ana:
            c_bank, c_score = st.columns([1, 2])
            with c_bank:
                st.markdown('<div class="bank-box"><h3>🏦 BANKA VEZNESİ</h3><p>Oyunlardan kazandığın kodu buraya gir.</p></div>', unsafe_allow_html=True)
                code = st.text_input("Transfer Kodu:", key="transfer_code")
                if st.button("💰 KODU BOZDUR", use_container_width=True):
                    # KOD BOZDURMA VE GÜVENLİK
                    success, result = server.redeem_code(st.session_state.class_code, st.session_state.user_no, code)
                    if success:
                        st.session_state.bank_balance = result # Yeni bakiyeyi al
                        st.success(f"✅ İşlem Başarılı! Yeni Bakiyeniz: {result} ₺")
                        time.sleep(2)
                        st.rerun()
                    else:
                        st.error(f"⛔ {result}")
            
            with c_score:
                st.header("🏆 Canlı Sıralama")
                df = server.get_leaderboard(st.session_state.class_code)
                if not df.empty:
                    st.dataframe(df, use_container_width=True, hide_index=True)
                else:
                    st.info("Sıralama verisi yok.")

        # 2. SORU ÇÖZÜM
        with tab_soru:
            t_tyt, t_meslek = st.tabs(["📘 TYT (KİTAPÇIK)", "📙 MESLEK"])
            
            # TYT KISMI
            with t_tyt:
                tyt_data = fetch_json_data(URL_TYT_DATA)
                if tyt_data:
                    # Ders Seçimi
                    dersler = sorted(list(set([detay.get('ders') for detay in tyt_data.values() if 'ders' in detay])))
                    secilen_ders = st.selectbox("Ders Seç:", dersler)
                    
                    # Sayfa Filtreleme
                    ilgili_sayfalar = []
                    for k, v in tyt_data.items():
                        if v.get('ders') == secilen_ders:
                            s = v.get('sorular', [])
                            if s: ilgili_sayfalar.append((k, f"{min(s)}-{max(s)}", v))
                    
                    # Sayfa Numarasına Göre Sırala
                    ilgili_sayfalar.sort(key=lambda x: int(x[0]) if x[0].isdigit() else 999)

                    if ilgili_sayfalar:
                        secim = st.selectbox("Sayfa Seç:", ilgili_sayfalar, format_func=lambda x: f"Sayfa {x[0]} (Soru: {x[1]})")
                        sayfa_no, aralik, detay = secim
                        
                        c_pdf, c_optik = st.columns([1.5, 1])
                        with c_pdf:
                            st.markdown(f'<embed src="{URL_TYT_PDF}#page={sayfa_no}" width="100%" height="800px" type="application/pdf">', unsafe_allow_html=True)
                        
                        with c_optik:
                            st.subheader("📝 Optik Form")
                            with st.form(key=f"tyt_{sayfa_no}"):
                                answers = {}
                                for i, s_no in enumerate(detay['sorular']):
                                    st.write(f"**Soru {s_no}**")
                                    answers[i] = st.radio(f"S{s_no}", ['A','B','C','D','E'], horizontal=True, key=f"q_{sayfa_no}_{s_no}", label_visibility="collapsed", index=None)
                                
                                if st.form_submit_button("KONTROL ET"):
                                    d, y = 0, 0
                                    for i, s_no in enumerate(detay['sorular']):
                                        try: dogru_cevap = detay['cevaplar'][i]
                                        except: dogru_cevap = "?"
                                        if answers[i] == dogru_cevap: d += 1
                                        else: y += 1
                                    
                                    puan = d * 50
                                    st.success(f"{d} Doğru, {y} Yanlış")
                                    if puan > 0:
                                        new_b = server.update_score(st.session_state.class_code, st.session_state.user_no, puan)
                                        st.session_state.bank_balance = new_b
                                        st.info(f"Kazanılan: {puan} ₺ (Hesaba eklendi)")

            # MESLEK KISMI
            with t_meslek:
                meslek_data = fetch_json_data(URL_MESLEK_SORULAR)
                if meslek_data:
                    root = meslek_data.get("KONU_TARAMA", meslek_data)
                    sinif = st.selectbox("Sınıf:", list(root.keys()))
                    if sinif:
                        ders = st.selectbox("Ders:", list(root[sinif].keys()))
                        if ders:
                            test = st.selectbox("Konu:", list(root[sinif][ders].keys()))
                            if test:
                                sorular = root[sinif][ders][test]
                                with st.form(f"m_{sinif}_{ders}_{test}"):
                                    m_ans = {}
                                    for i, q in enumerate(sorular):
                                        st.write(f"**{i+1}. {q['soru']}**")
                                        m_ans[i] = st.radio("Cevap:", q['secenekler'], key=f"mq_{i}", index=None)
                                        st.divider()
                                    if st.form_submit_button("BİTİR"):
                                        d_m = 0
                                        for i, q in enumerate(sorular):
                                            if m_ans[i] == q['cevap']: d_m += 1
                                        p_m = d_m * 100
                                        st.success(f"{d_m} Doğru")
                                        if p_m > 0:
                                            nb = server.update_score(st.session_state.class_code, st.session_state.user_no, p_m)
                                            st.session_state.bank_balance = nb
                                            st.info(f"{p_m} ₺ eklendi.")

        # 3. OYUNLAR
        with tab_eglence:
            game = st.selectbox("Oyun Seç:", ["Finans İmparatoru", "Asset Matrix"])
            if game == "Finans İmparatoru": components.html(FINANCE_GAME_HTML, height=700)
            else: components.html(ASSET_MATRIX_HTML, height=750)

        # 4. LIFESIM
        with tab_lifesim:
            final_code = load_lifesim_html()
            components.html(final_code, height=800, scrolling=True)
