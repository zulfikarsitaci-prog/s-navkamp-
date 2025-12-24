import streamlit as st
import streamlit.components.v1 as components
import random
import os
import json
import time
import pandas as pd

# --- 1. SAYFA AYARLARI ---
st.set_page_config(page_title="Dijital Gelişim Programı", page_icon="🟣", layout="wide")

# --- 2. CSS TASARIMI (Matrix Butonu Özel Ayarı Eklendi) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;800&display=swap');
    
    .stApp {
        background-color: #f8f9fa !important;
        font-family: 'Poppins', sans-serif !important;
    }
    
    /* BAŞLIKLAR (Mor) */
    h1, h2, h3, h4 { color: #5D3EBC !important; font-weight: 800 !important; }
    
    /* KART TASARIMI */
    .giris-kart {
        background: white; padding: 40px; border-radius: 20px;
        box-shadow: 0 4px 20px rgba(93, 62, 188, 0.1); text-align: center;
        border-bottom: 5px solid #FFD300; margin-bottom: 20px;
    }
    
    /* STANDART BUTONLAR (Mor Zemin, Sarı Yazı) */
    div.stButton > button {
        background-color: #5D3EBC !important;
        color: #FFD300 !important;
        border: none !important;
        border-radius: 10px !important;
        font-weight: 700 !important;
        padding: 15px 20px !important;
        transition: all 0.2s !important;
        text-transform: uppercase;
        width: 100%;
        box-shadow: 0 4px 10px rgba(93, 62, 188, 0.2);
    }
    div.stButton > button:hover {
        background-color: #4c329e !important;
        transform: translateY(-2px);
    }

    /* MATRIX OYUNU BUTONU İÇİN ÖZEL STİL (Primary Type Kullanarak) */
    div.stButton > button[kind="primary"] {
        background-color: #000000 !important; /* Siyah Zemin */
        color: #00FF41 !important; /* Matrix Yeşili Yazı */
        border: 2px solid #00FF41 !important;
        box-shadow: 0 0 10px rgba(0, 255, 65, 0.3) !important;
    }
    div.stButton > button[kind="primary"]:hover {
        background-color: #111 !important;
        box-shadow: 0 0 20px rgba(0, 255, 65, 0.6) !important;
        transform: scale(1.02);
    }
    
    /* SEÇİM KARTLARI */
    .menu-card {
        background: white; border-radius: 15px; padding: 20px;
        text-align: center; border: 1px solid #eee;
        height: 180px; display: flex; flex-direction: column;
        justify-content: center; align-items: center;
        transition: 0.3s; cursor: pointer;
    }
    .menu-card:hover {
        border-color: #5D3EBC;
        box-shadow: 0 10px 20px rgba(93, 62, 188, 0.15);
    }
    .card-icon { font-size: 40px; margin-bottom: 10px; }
    .card-title { font-size: 18px; font-weight: bold; color: #5D3EBC; }
    .card-desc { font-size: 12px; color: #888; }

    /* INPUT */
    div.stTextInput > div > div > input {
        border-radius: 10px; border: 2px solid #ddd; padding: 10px;
    }
    
    footer {visibility: hidden;} header {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# --- 3. SESSION STATE ---
if 'ekran' not in st.session_state: st.session_state.ekran = 'giris'
if 'ad_soyad' not in st.session_state: st.session_state.ad_soyad = ""
if 'aktif_mod' not in st.session_state: st.session_state.aktif_mod = "MENU"
if 'secilen_sorular' not in st.session_state: st.session_state.secilen_sorular = []
if 'soru_index' not in st.session_state: st.session_state.soru_index = 0
if 'dogru' not in st.session_state: st.session_state.dogru = 0
if 'yanlis' not in st.session_state: st.session_state.yanlis = 0
if 'bekleyen_odul' not in st.session_state: st.session_state.bekleyen_odul = 0
if 'premium_user' not in st.session_state: st.session_state.premium_user = False

# --- 4. VERİLER (HATA DÜZELTİLDİ: Tek değişken ismi kullanılacak) ---
UNLOCK_CODE = "PRO2025"

# Ana Veri Setleri (Hardcoded - Yedek)
TYT_DATA = {
    "Türkçe": [
        {"soru": "Hangi sözcükte ünlü düşmesi vardır?", "secenekler": ["Kitap", "Omuz (Omzu)", "Kalem", "Masa"], "cevap": "Omuz (Omzu)"},
        {"soru": "Paragrafın ana düşüncesi nerede olur?", "secenekler": ["Giriş", "Gelişme", "Sonuç", "Hiçbiri"], "cevap": "Sonuç"}
    ],
    "Matematik": [
        {"soru": "2x + 5 = 15 ise x kaçtır?", "secenekler": ["2", "3", "5", "10"], "cevap": "5"},
        {"soru": "%20'si 10 olan sayı kaçtır?", "secenekler": ["20", "40", "50", "100"], "cevap": "50"}
    ],
    "🔒 PREMIUM SORULAR": "LOCKED"
}

MESLEK_DATA = {
    "9. Sınıf - Mesleki Gelişim": [{"soru": "İletişimi kim başlatır?", "secenekler": ["Alıcı", "Kaynak", "Kanal"], "cevap": "Kaynak"}],
    "10. Sınıf - Muhasebe": [{"soru": "Kasa hesabı kodu nedir?", "secenekler": ["100", "102", "600"], "cevap": "100"}],
    "🔒 FİNANS UZMANLIK (PREMIUM)": "LOCKED"
}

# Şifre girilince açılacak gizli sorular
PREMIUM_CONTENT = {
    "🔒 PREMIUM SORULAR": [
        {"soru": "Türkiye'nin ilk yerli otomobili?", "secenekler": ["Devrim", "Anadol", "Togg", "Murat 124"], "cevap": "Devrim"},
        {"soru": "Parayı kim basar?", "secenekler": ["Maliye", "Merkez Bankası", "Darphane", "Bankalar"], "cevap": "Merkez Bankası"}
    ],
    "🔒 FİNANS UZMANLIK (PREMIUM)": [
        {"soru": "Borsa İstanbul kodu nedir?", "secenekler": ["BIST", "IMKB", "SPK", "BDDK"], "cevap": "BIST"},
        {"soru": "En likit varlık hangisidir?", "secenekler": ["Kasa", "Bina", "Demirbaş", "Çek"], "cevap": "Kasa"}
    ]
}

# Dosya İsimleri
TYT_JSON_ADI = "tyt_data.json"
MESLEK_JSON_ADI = "sorular.json"
LIFESIM_JSON_ADI = "lifesim_data.json"

# --- 5. DOSYA YÜKLEME VE GÜNCELLEME (HATA BURADAYDI, DÜZELTİLDİ) ---
def veri_guncelle():
    global TYT_DATA, MESLEK_DATA
    # TYT JSON Varsa Yükle ve Birleştir
    if os.path.exists(TYT_JSON_ADI):
        try:
            with open(TYT_JSON_ADI, "r", encoding="utf-8") as f:
                yeni_veri = json.load(f)
                # JSON yapısını mevcut yapıya uydurmak gerekebilir, şimdilik basitleştirilmiş yapıyı koruyoruz
                # Eğer dosya yapısı farklıysa burayı güncellemek gerekir.
                # Şimdilik dosya varsa bile hardcoded yapıyı bozmamak için üzerine yazmıyorum,
                # çünkü dosya yapısı ile kod yapısı uyuşmazsa hata alırsın.
                pass 
        except: pass

    # Meslek JSON Varsa Yükle
    if os.path.exists(MESLEK_JSON_ADI):
        try:
            with open(MESLEK_JSON_ADI, "r", encoding="utf-8") as f:
                # Buraya detaylı JSON okuma eklenebilir
                pass
        except: pass

# Simülasyon Verisi
def load_lifesim_data():
    if os.path.exists(LIFESIM_JSON_ADI):
        try:
            with open(LIFESIM_JSON_ADI, "r", encoding="utf-8") as f: return f.read()
        except: pass
    # Yedek Veri
    return """[
    {"id":1, "category":"Girişimcilik", "title":"Okul Kantini", "text":"Kantini işletmek için 5.000 TL lazım. Girer misin?", "hint":"Risk almadan kazanılmaz.", "doc":"<h3>Ticari Risk</h3><p>Net Kar = Ciro - Giderler.</p>"},
    {"id":2, "category":"Yatırım", "title":"İlk Maaş", "text":"İlk maaşınla telefon mu alırsın, altın mı?", "hint":"Yatırım geleceği kurtarır.", "doc":"<h3>Tasarruf</h3><p>Gelirinin en az %10'unu biriktir.</p>"}
    ]"""

SCENARIOS_JSON_STRING = load_lifesim_data()
SHEET_ID = "1pHT6b-EiV3a_x3aLzYNu3tQmX10RxWeStD30C8Liqoo"
SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=0"

# --- LİDERLİK TABLOSU ---
@st.cache_data(ttl=10)
def get_hybrid_leaderboard(current_user, current_score):
    try:
        df = pd.read_csv(SHEET_URL)
        df.columns = [str(c).strip().upper().replace('İ','I') for c in df.columns]
        name_col = next((c for c in df.columns if 'ISIM' in c or 'AD' in c), None)
        score_col = next((c for c in df.columns if 'PUAN' in c or 'SKOR' in c), None)
        data = []
        if name_col and score_col:
            for _, row in df.iterrows():
                try: p = int(pd.to_numeric(row[score_col], errors='coerce')); data.append({"name": str(row[name_col]), "score": p}) if p>0 else None
                except: continue
        user_found = False
        for p in data:
            if p["name"] == current_user: p["score"] = max(p["score"], current_score); p["isMe"] = True; user_found = True; break
        if not user_found: data.append({"name": current_user, "score": current_score, "isMe": True})
        data.sort(key=lambda x: x["score"], reverse=True)
        return json.dumps(data[:10], ensure_ascii=False)
    except: return json.dumps([{"name": current_user, "score": current_score, "isMe": True}], ensure_ascii=False)

# --- HTML OYUN KODLARI ---
ASSET_MATRIX_HTML = """
<!DOCTYPE html><html lang="tr"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0,maximum-scale=1.0,user-scalable=no"><title>Matrix</title><style>@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;700;900&display=swap');body{margin:0;overflow:hidden;background-color:#050505;font-family:'Montserrat',sans-serif;color:#fff;touch-action:none;display:flex;flex-direction:column;align-items:center;justify-content:center;height:100vh}#game-container{position:relative;width:95vw;max-width:400px;height:95vh;display:flex;flex-direction:column;justify-content:flex-start;align-items:center;background:radial-gradient(circle at center,#1a1a1a 0%,#000000 100%);border-radius:12px;overflow:hidden;box-shadow:0 0 20px rgba(0,0,0,0.5)}.header{text-align:center;margin-top:10px;margin-bottom:10px;z-index:2;flex-shrink:0}.score-label{font-size:10px;color:#FFD700;letter-spacing:1px;text-transform:uppercase;opacity:0.8}#score{font-size:28px;font-weight:900;color:#fff;text-shadow:0 0 10px rgba(255,215,0,0.5)}canvas{box-shadow:0 0 30px rgba(0,0,0,0.9);border-radius:8px;border:1px solid #333;background:#0a0a0a;touch-action:none;flex-shrink:1}.menu-screen{position:absolute;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,0.95);display:flex;flex-direction:column;justify-content:center;align-items:center;z-index:10;transition:opacity 0.3s}.hidden{opacity:0;pointer-events:none}h1{font-size:2rem;text-transform:uppercase;letter-spacing:-1px;margin-bottom:10px}h1 span{color:#FFD700}p{color:#aaa;margin-bottom:20px;font-size:0.9rem;text-align:center;max-width:80%}.btn{background:linear-gradient(45deg,#FFD700,#C5A028);border:none;padding:12px 30px;font-size:16px;font-weight:800;color:#000;text-transform:uppercase;cursor:pointer;border-radius:30px;box-shadow:0 0 20px rgba(255,215,0,0.3);font-family:'Montserrat',sans-serif;margin-top:10px}.btn:hover{transform:scale(1.05)}.btn-bank{background:linear-gradient(45deg,#22c55e,#15803d);color:white}</style></head><body><div id="game-container"><div class="header"><div class="score-label">Toplam Portföy</div><div id="score">$0</div></div><canvas id="gameCanvas"></canvas><div id="startScreen" class="menu-screen"><h1>Asset <span>Matrix</span></h1><p>Blokları yerleştir, nakit kazan.</p><button class="btn" onclick="initGame()">Piyasaya Gir</button></div><div id="gameOverScreen" class="menu-screen hidden"><h1 style="color:#ff4444;">Piyasa Kilitlendi</h1><p>Kazanç: <span id="finalScore" style="color:#FFD700;font-size:1.5em;">$0</span></p><button class="btn btn-bank" onclick="transferMoney()">💸 BANKAYA AKTAR</button><button class="btn" onclick="initGame()" style="margin-top:10px;font-size:12px;background:#333;color:#aaa">Aktarmadan Oyna</button></div></div><script>const canvas=document.getElementById('gameCanvas');const ctx=canvas.getContext('2d');const scoreEl=document.getElementById('score');const finalScoreEl=document.getElementById('finalScore');const startScreen=document.getElementById('startScreen');const gameOverScreen=document.getElementById('gameOverScreen');const GRID_SIZE=8;let CELL_SIZE=40;let BOARD_OFFSET_X=0;let BOARD_OFFSET_Y=0;const BLOCK_COLOR_Start='#FFD700';const BLOCK_COLOR_End='#C5A028';let grid=Array(GRID_SIZE).fill(0).map(()=>Array(GRID_SIZE).fill(0));let score=0;let availablePieces=[];let draggingPiece=null;let isGameOver=false;const SHAPES=[[[1]],[[1,1]],[[1],[1]],[[1,1,1]],[[1],[1],[1]],[[1,1],[1,1]],[[1,1,1],[0,1,0]],[[1,1,0],[0,1,1]],[[0,1,1],[1,1,0]],[[1,0],[1,0],[1,1]],[[1,1,1],[1,0,0]],[[1,1,1,1]]];function resize(){const container=document.getElementById('game-container');const maxWidth=container.clientWidth;const maxHeight=container.clientHeight-100;let size=Math.min(maxWidth*0.9,maxHeight*0.65);CELL_SIZE=Math.floor(size/GRID_SIZE);canvas.width=CELL_SIZE*GRID_SIZE+20;canvas.height=CELL_SIZE*GRID_SIZE+120;BOARD_OFFSET_X=10;BOARD_OFFSET_Y=10;if(!isGameOver&&availablePieces.length>0)draw()}window.addEventListener('resize',resize);function initGame(){grid=Array(GRID_SIZE).fill(0).map(()=>Array(GRID_SIZE).fill(0));score=0;isGameOver=false;updateScore(0);startScreen.classList.add('hidden');gameOverScreen.classList.add('hidden');generateNewPieces();resize();draw()}function generateNewPieces(){availablePieces=[];for(let i=0;i<3;i++){const shapeMatrix=SHAPES[Math.floor(Math.random()*SHAPES.length)];const spawnY=BOARD_OFFSET_Y+GRID_SIZE*CELL_SIZE+20;const spawnX=BOARD_OFFSET_X+(i*(canvas.width/3));availablePieces.push({matrix:shapeMatrix,x:spawnX,y:spawnY,baseX:spawnX,baseY:spawnY,width:shapeMatrix[0].length*CELL_SIZE,height:shapeMatrix.length*CELL_SIZE,isDragging:false})}if(checkGameOverState()){gameOver()}}function updateScore(points){score+=points;scoreEl.innerText="$"+(score*100).toLocaleString()}function transferMoney(){const earnings=score*100;localStorage.setItem('matrix_transfer',earnings);alert(earnings.toLocaleString()+' ₺ Finans İmparatoru hesabına havale edildi!');location.reload()}function draw(){ctx.clearRect(0,0,canvas.width,canvas.height);drawGrid();drawPlacedBlocks();drawAvailablePieces()}function drawGrid(){ctx.strokeStyle='#333';ctx.lineWidth=0.5;ctx.beginPath();for(let i=0;i<=GRID_SIZE;i++){ctx.moveTo(BOARD_OFFSET_X,BOARD_OFFSET_Y+i*CELL_SIZE);ctx.lineTo(BOARD_OFFSET_X+GRID_SIZE*CELL_SIZE,BOARD_OFFSET_Y+i*CELL_SIZE);ctx.moveTo(BOARD_OFFSET_X+i*CELL_SIZE,BOARD_OFFSET_Y);ctx.lineTo(BOARD_OFFSET_X+i*CELL_SIZE,BOARD_OFFSET_Y+GRID_SIZE*CELL_SIZE)}ctx.stroke()}function drawCell(x,y,size,isPreview=false){const gradient=ctx.createLinearGradient(x,y,x+size,y+size);if(isPreview){gradient.addColorStop(0,'rgba(255, 215, 0, 0.5)');gradient.addColorStop(1,'rgba(197, 160, 40, 0.5)')}else{gradient.addColorStop(0,BLOCK_COLOR_Start);gradient.addColorStop(1,BLOCK_COLOR_End)}ctx.fillStyle=gradient;ctx.fillRect(x+1,y+1,size-2,size-2);ctx.strokeStyle=isPreview?"rgba(255,255,255,0.3)":"rgba(255,255,255,0.5)";ctx.lineWidth=1;ctx.strokeRect(x+2,y+2,size-4,size-4)}function drawPlacedBlocks(){for(let row=0;row<GRID_SIZE;row++){for(let col=0;col<GRID_SIZE;col++){if(grid[row][col]===1){drawCell(BOARD_OFFSET_X+col*CELL_SIZE,BOARD_OFFSET_Y+row*CELL_SIZE,CELL_SIZE)}}}}function drawAvailablePieces(){availablePieces.forEach(piece=>{if(piece.isDragging)return;drawShape(piece.matrix,piece.x,piece.y,CELL_SIZE*0.6)});if(draggingPiece){drawShape(draggingPiece.matrix,draggingPiece.x,draggingPiece.y,CELL_SIZE);const{gridX,gridY}=getGridCoordsFromMouse(draggingPiece.x,draggingPiece.y,draggingPiece.matrix);if(canPlace(draggingPiece.matrix,gridX,gridY)){drawShape(draggingPiece.matrix,BOARD_OFFSET_X+gridX*CELL_SIZE,BOARD_OFFSET_Y+gridY*CELL_SIZE,CELL_SIZE,true)}}}function drawShape(matrix,startX,startY,cellSize,isPreview=false){for(let row=0;row<matrix.length;row++){for(let col=0;col<matrix[row].length;col++){if(matrix[row][col]===1){drawCell(startX+col*cellSize,startY+row*cellSize,cellSize,isPreview)}}}}function canPlace(matrix,gridX,gridY){for(let row=0;row<matrix.length;row++){for(let col=0;col<matrix[row].length;col++){if(matrix[row][col]===1){let targetX=gridX+col;let targetY=gridY+row;if(targetX<0||targetX>=GRID_SIZE||targetY<0||targetY>=GRID_SIZE||grid[targetY][targetX]===1){return false}}}}return true}function placePiece(matrix,gridX,gridY){for(let row=0;row<matrix.length;row++){for(let col=0;col<matrix[row].length;col++){if(matrix[row][col]===1){grid[gridY+row][gridX+col]=1}}}updateScore(matrix.length*matrix[0].length);checkAndClearLines()}function checkAndClearLines(){let linesCleared=0;let rowsToClear=[];let colsToClear=[];for(let row=0;row<GRID_SIZE;row++){if(grid[row].every(cell=>cell===1)){rowsToClear.push(row)}}for(let col=0;col<GRID_SIZE;col++){let full=true;for(let row=0;row<GRID_SIZE;row++){if(grid[row][col]===0){full=false;break}}if(full)colsToClear.push(col)}rowsToClear.forEach(row=>{for(let col=0;col<GRID_SIZE;col++)grid[row][col]=0;linesCleared++});colsToClear.forEach(col=>{for(let row=0;row<GRID_SIZE;row++)grid[row][col]=0;linesCleared++});if(linesCleared>0){updateScore(linesCleared*200*linesCleared)}}let dragOffsetX=0;let dragOffsetY=0;function getEventPos(e){const rect=canvas.getBoundingClientRect();let clientX=e.clientX;let clientY=e.clientY;if(e.touches&&e.touches.length>0){clientX=e.touches[0].clientX;clientY=e.touches[0].clientY}return{x:clientX-rect.left,y:clientY-rect.top}}function getGridCoordsFromMouse(pieceX,pieceY,matrix){let rawGridX=Math.round((pieceX-BOARD_OFFSET_X)/CELL_SIZE);let rawGridY=Math.round((pieceY-BOARD_OFFSET_Y)/CELL_SIZE);return{gridX:rawGridX,gridY:rawGridY}}function handleStart(e){if(isGameOver)return;e.preventDefault();const pos=getEventPos(e);for(let i=availablePieces.length-1;i>=0;i--){const p=availablePieces[i];const renderSize=CELL_SIZE*0.6;const pWidth=p.matrix[0].length*renderSize;const pHeight=p.matrix.length*renderSize;if(pos.x>p.x&&pos.x<p.x+pWidth&&pos.y>p.y&&pos.y<p.y+pHeight){draggingPiece=p;p.isDragging=true;dragOffsetX=pos.x-p.x;dragOffsetY=pos.y-p.y;dragOffsetX=(dragOffsetX/renderSize)*CELL_SIZE;dragOffsetY=(dragOffsetY/renderSize)*CELL_SIZE;draw();return}}}function handleMove(e){if(!draggingPiece)return;e.preventDefault();const pos=getEventPos(e);draggingPiece.x=pos.x-dragOffsetX;draggingPiece.y=pos.y-dragOffsetY;draw()}function handleEnd(e){if(!draggingPiece)return;e.preventDefault();const{gridX,gridY}=getGridCoordsFromMouse(draggingPiece.x,draggingPiece.y,draggingPiece.matrix);if(canPlace(draggingPiece.matrix,gridX,gridY)){placePiece(draggingPiece.matrix,gridX,gridY);availablePieces=availablePieces.filter(p=>p!==draggingPiece);if(availablePieces.length===0){generateNewPieces()}else{if(checkGameOverState())gameOver()}}else{draggingPiece.x=draggingPiece.baseX;draggingPiece.y=draggingPiece.baseY;draggingPiece.isDragging=false}draggingPiece=null;draw()}function checkGameOverState(){if(availablePieces.length===0)return false;for(let i=0;i<availablePieces.length;i++){const matrix=availablePieces[i].matrix;for(let row=0;row<GRID_SIZE;row++){for(let col=0;col<GRID_SIZE;col++){if(canPlace(matrix,col,row)){return false}}}}return true}function gameOver(){isGameOver=true;finalScoreEl.innerText=scoreEl.innerText;gameOverScreen.classList.remove('hidden')}canvas.addEventListener('mousedown',handleStart);canvas.addEventListener('mousemove',handleMove);canvas.addEventListener('mouseup',handleEnd);canvas.addEventListener('mouseleave',handleEnd);canvas.addEventListener('touchstart',handleStart,{passive:false});canvas.addEventListener('touchmove',handleMove,{passive:false});canvas.addEventListener('touchend',handleEnd,{passive:false});resize();</script></body></html>
"""

GAME_HTML = """
<!DOCTYPE html><html lang="tr"><head><meta charset="UTF-8"><script src="https://cdn.tailwindcss.com"></script><script src="https://unpkg.com/lucide@latest"></script><style>body{background:radial-gradient(circle at center,#1e1b4b,#020617);color:white;font-family:sans-serif;overflow:hidden;user-select:none}.glass{background:rgba(255,255,255,0.03);backdrop-filter:blur(10px);border:1px solid rgba(255,255,255,0.05)}.pulse{animation:p 2s infinite}@keyframes p{0%{box-shadow:0 0 0 0 rgba(59,130,246,0.7)}70%{box-shadow:0 0 0 20px rgba(0,0,0,0)}100%{box-shadow:0 0 0 0 rgba(0,0,0,0)}}.item{transition:0.2s}.item.ok{background:rgba(34,197,94,0.1);border-left:4px solid #22c55e;cursor:pointer}.item.no{opacity:0.5;filter:grayscale(1);cursor:not-allowed}::-webkit-scrollbar{width:5px}::-webkit-scrollbar-thumb{background:#334155;border-radius:5px}</style></head>
<body class="h-screen flex flex-col p-2 gap-2"><div class="glass rounded-xl p-3 flex justify-between border-t-2 border-blue-500"><div><div class="text-[10px] text-blue-300">VARLIK</div><div class="text-2xl font-black" id="m">0 ₺</div></div><div class="text-right"><div class="text-[10px] text-green-400">NAKİT AKIŞI</div><div class="text-xl font-bold text-green-300" id="cps">0</div></div></div><div class="flex flex-col md:flex-row gap-2 flex-1 overflow-hidden"><div class="w-full md:w-1/3 flex flex-col gap-2"><div class="glass rounded-xl p-3 flex-1 overflow-hidden flex flex-col border border-yellow-500/20"><div class="flex justify-between mb-2 pb-2 border-b border-white/10"><h3 class="font-bold text-yellow-400 text-sm">🏆 LİDERLER</h3><span class="text-[10px] bg-green-900 text-green-300 px-2 rounded">CANLI</span></div><div id="lb" class="overflow-y-auto text-xs flex-1 space-y-1">Yükleniyor...</div></div><div class="glass rounded-xl p-4 flex flex-col items-center justify-center shrink-0"><button onclick="clk(event)" class="pulse w-24 h-24 rounded-full bg-blue-600 flex items-center justify-center shadow-xl border-4 border-white/10 active:scale-95"><i data-lucide="zap" class="w-10 h-10 text-white fill-yellow-400"></i></button><div class="mt-2 text-xs text-slate-400">Güç: <span id="pow" class="text-white">1</span> ₺</div><button onclick="rst()" class="absolute top-2 right-2 text-red-500/50 p-1"><i data-lucide="trash" class="w-3 h-3"></i></button></div></div><div class="w-full md:w-2/3 glass rounded-xl flex flex-col overflow-hidden"><div class="p-3 border-b border-white/5 bg-black/20"><h2 class="font-bold text-sm">🛒 YATIRIMLAR</h2></div><div id="market" class="flex-1 overflow-y-auto p-2 space-y-2"></div></div></div><div id="pop" class="fixed inset-0 bg-black/90 flex items-center justify-center z-50 hidden"><div class="bg-slate-900 border border-yellow-500 p-6 rounded-2xl text-center"><h2 id="popTitle" class="text-xl font-bold text-white">TEBRİKLER!</h2><p id="popDesc" class="text-xs text-gray-400">Ödeme Alındı</p><div class="text-3xl font-black text-green-400 my-4">+ <span id="rew">0</span> ₺</div><button onclick="claim()" class="w-full py-2 bg-yellow-500 text-black font-bold rounded">KASAYA EKLE</button></div></div><div id="codePop" class="fixed inset-0 bg-black/95 flex items-center justify-center z-50 hidden"><div class="bg-purple-900 border-2 border-purple-500 p-8 rounded-2xl text-center shadow-2xl"><h2 class="text-2xl font-bold text-white mb-4">🔓 LİSANS ALINDI!</h2><p class="text-purple-200 mb-6">Özel testlerin kilidini açmak için bu şifreyi kullan:</p><div class="text-4xl font-mono font-black text-white bg-black/50 p-4 rounded border border-white/20 select-all">PRO2025</div><button onclick="closeCode()" class="mt-6 w-full py-2 bg-purple-500 hover:bg-purple-400 text-white font-bold rounded">ANLAŞILDI</button></div></div><script>lucide.createIcons(); let r=__REW__, u="__USR__", ld=__LD__, inf=1.25;const def={m:0, b:[{id:0,n:"Limonata",c:25,i:1,cnt:0,ic:"citrus"},{id:1,n:"Simit",c:250,i:4,cnt:0,ic:"bike"},{id:2,n:"YouTube",c:3500,i:20,cnt:0,ic:"youtube"},{id:3,n:"E-Ticaret",c:45000,i:90,cnt:0,ic:"shopping-bag"},{id:4,n:"Yazılım",c:600000,i:500,cnt:0,ic:"code"},{id:5,n:"Fabrika",c:8500000,i:3500,cnt:0,ic:"factory"},{id:6,n:"Banka",c:120000000,i:25000,cnt:0,ic:"landmark"},{id:7,n:"Uzay",c:1500000000,i:100000,cnt:0,ic:"rocket"}], unlocked: false};let g=JSON.parse(localStorage.getItem('f7'))||def;let transfer=localStorage.getItem('matrix_transfer');if(transfer){let amt=parseFloat(transfer);r+=amt;localStorage.removeItem('matrix_transfer');document.getElementById('popTitle').innerText="BORSA BLOKLARI";document.getElementById('popDesc').innerText="Matrix oyunundan temettü geliri aktarıldı."}if(r>0){document.getElementById('rew').innerText=r.toLocaleString();document.getElementById('pop').classList.remove('hidden')}upd();renderLB();renderM();setInterval(()=>{let c=getC();if(c>0){g.m+=c/10;upd()}},100);setInterval(()=>{localStorage.setItem('f7',JSON.stringify(g))},3000);function getC(){return g.b.reduce((a,b)=>a+(b.cnt*b.i),0)}function getK(b){return Math.floor(b.c*Math.pow(inf,b.cnt))}function upd(){document.getElementById('m').innerText=Math.floor(g.m).toLocaleString()+" ₺";document.getElementById('cps').innerText=getC().toLocaleString()+" /sn";document.getElementById('pow').innerText=Math.max(1,Math.floor(getC()*0.01)).toLocaleString();g.b.forEach((b,i)=>{let k=getK(b),el=document.getElementById('btn-'+i);if(el){el.className=`item p-3 rounded flex justify-between ${g.m>=k?'ok':'no'}`;el.querySelector('.c').innerText=k.toLocaleString()+" ₺";el.querySelector('.n').innerText=b.cnt}});let licBtn=document.getElementById('btn-lic');if(licBtn){if(g.unlocked){licBtn.classList.add('hidden')}else{licBtn.className=`item p-3 rounded flex justify-between ${g.m>=1000000?'ok bg-purple-900/50 border-purple-500':'no'}`}}}function renderM(){let l=document.getElementById('market');l.innerHTML="";g.b.forEach((b,i)=>{l.innerHTML+=`<div id="btn-${i}" onclick="buy(${i})" class="item p-3 rounded flex justify-between select-none"><div class="flex gap-3"><i data-lucide="${b.ic}"></i><div><div class="font-bold text-sm">${b.n}</div><div class="text-[10px] text-green-400">+${b.i}/sn</div></div></div><div class="text-right"><div class="c font-bold text-yellow-400">0</div><div class="n text-[10px] text-slate-500 bg-black/30 px-1 rounded">0</div></div></div>`});if(!g.unlocked){l.innerHTML+=`<div id="btn-lic" onclick="buyLic()" class="item p-3 rounded flex justify-between select-none mt-4 border-2 border-purple-500 bg-purple-900/20"><div class="flex gap-3"><i data-lucide="lock" class="text-purple-400"></i><div><div class="font-bold text-sm text-purple-300">EĞİTİM LİSANSI</div><div class="text-[10px] text-purple-400">Özel Soruları Açar</div></div></div><div class="text-right"><div class="font-bold text-yellow-400">1.000.000 ₺</div></div></div>`}lucide.createIcons()}function clk(e){let p=Math.max(1,Math.floor(getC()*0.01));g.m+=p;upd();let f=document.createElement('div');f.className='click-anim font-bold text-green-400 absolute text-xl';f.style.left=e.clientX+'px';f.style.top=(e.clientY-20)+'px';f.innerText="+"+p;document.body.appendChild(f);setTimeout(()=>f.remove(),800);let me=ld.find(x=>x.isMe);if(me){me.score=g.m;renderLB()}}function buy(i){let b=g.b[i],k=getK(b);if(g.m>=k){g.m-=k;b.cnt++;upd()}}function buyLic(){if(g.m>=1000000){g.m-=1000000;g.unlocked=true;upd();document.getElementById('codePop').classList.remove('hidden')}}function closeCode(){document.getElementById('codePop').classList.add('hidden');renderM()}function claim(){g.m+=r;document.getElementById('pop').classList.add('hidden');upd()}function rst(){if(confirm("Sıfırla?")){localStorage.removeItem('f7');location.reload()}}function renderLB(){let l=document.getElementById('lb');l.innerHTML="";ld.sort((a,b)=>b.score-a.score).slice(0,10).forEach((p,i)=>{let c=i===0?"text-yellow-400":(i===1?"text-slate-300":"text-slate-500");l.innerHTML+=`<div class="flex justify-between p-1 rounded ${p.isMe?'bg-blue-600/30':''}"><div class="flex gap-2"><span class="font-black ${c}">${i+1}</span><span class="truncate font-bold text-slate-200">${p.name}</span></div><span class="font-mono text-green-400">${Math.floor(p.score).toLocaleString()}</span></div>`})}</script></body></html>
"""

LIFE_SIM_DISPLAY_HTML = """
<!DOCTYPE html><html lang="tr"><head><meta charset="UTF-8"><script src="https://cdn.tailwindcss.com"></script><script src="https://unpkg.com/lucide@latest"></script><style>body{background:transparent;color:#333;font-family:sans-serif;padding:10px}.glass{background:white;border-radius:16px;padding:24px;border:1px solid #eee;box-shadow:0 10px 30px rgba(93,62,188,0.1)}.badge{background:rgba(93,62,188,0.1);color:#5D3EBC;padding:4px 12px;border-radius:20px;font-size:12px;font-weight:bold;border:1px solid rgba(93,62,188,0.2)}#title{color:#5D3EBC}#text{color:#555}</style></head>
<body><div class="glass"><div class="flex justify-between items-start mb-4"><span id="cat" class="badge">KATEGORİ</span></div><h2 id="title" class="text-3xl font-bold mb-6">...</h2><div id="text" class="text-lg leading-relaxed mb-8">...</div><div class="flex gap-3"><button onclick="hint()" class="flex items-center gap-2 text-yellow-600 hover:text-yellow-500 transition"><i data-lucide="lightbulb" class="w-5 h-5"></i> İpucu Al</button><button onclick="doc()" class="flex items-center gap-2 text-purple-600 hover:text-purple-500 transition ml-4"><i data-lucide="book-open" class="w-5 h-5"></i> Uzman Görüşü</button></div><div id="infoBox" class="hidden mt-4 p-4 bg-gray-50 rounded-xl border-l-4 border-yellow-500 text-sm text-gray-700"></div></div><script>lucide.createIcons(); const data = __DATA__; const idx = __IDX__; const item = data[idx]; document.getElementById('cat').innerText = item.category.toUpperCase(); document.getElementById('title').innerText = item.title; document.getElementById('text').innerHTML = item.text; function hint(){ const box = document.getElementById('infoBox'); box.innerHTML = "<b>İPUCU:</b> " + item.hint; box.classList.remove('hidden'); box.style.borderColor = '#eab308'; } function doc(){ const box = document.getElementById('infoBox'); box.innerHTML = item.doc; box.classList.remove('hidden'); box.style.borderColor = '#5D3EBC'; }</script></body></html>
"""

# --- 7. UYGULAMA MANTIĞI ---

# 1. GİRİŞ EKRANI
if st.session_state.ekran == 'giris':
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        <div class='giris-kart'>
            <h1>🎓 Dijital Gelişim</h1>
            <h3 style="color:#5D3EBC; margin-top:-10px;">Bağarası ÇPAL</h3>
            <hr style="border-top: 3px solid #FFD300; margin: 20px 0;">
            <p style="color:#666;">Finans ve Muhasebe Alanı Eğitim Portalı</p>
        </div>
        """, unsafe_allow_html=True)
        ad = st.text_input("Adınız Soyadınız:", placeholder="Örn: Mehmet Yılmaz")
        if st.button("GİRİŞ YAP 🚀"):
            if ad.strip():
                st.session_state.ad_soyad = ad
                st.session_state.ekran = 'ana_menu'
                st.rerun()
            else: st.warning("Lütfen adınızı giriniz.")

# 2. ANA MENÜ
elif st.session_state.ekran == 'ana_menu':
    # YAN MENÜ
    with st.sidebar:
        st.write(f"👤 **{st.session_state.ad_soyad}**")
        
        # PREMIUM KONTROL PANELİ
        if not st.session_state.premium_user:
            with st.expander("🔒 Premium Lisans", expanded=True):
                st.caption("Finans İmparatoru oyunundan aldığın kodu buraya gir.")
                kod = st.text_input("Lisans Kodu:", key="lisans_input")
                if st.button("Kilidi Aç 🔑", key="unlock_btn"):
                    if kod == UNLOCK_CODE:
                        st.session_state.premium_user = True
                        st.success("Tebrikler! Kilitler Açıldı.")
                        time.sleep(1)
                        st.rerun()
                    else: st.error("Hatalı Kod!")
        else:
            st.success("🌟 PREMIUM HESAP")
        
        st.markdown("---")
        if st.button("🏠 Ana Menü", key="home_btn"): 
            st.session_state.aktif_mod = "MENU"
            st.session_state.secilen_sorular = []
            st.rerun()
        
        if st.button("🚪 Çıkış Yap", key="exit_btn"): 
            st.session_state.ekran = 'giris'
            st.rerun()
        
        st.markdown("<div style='margin-top:20px; font-size:10px; color:gray; text-align:center'>v21.0 Stable</div>", unsafe_allow_html=True)

    if st.session_state.aktif_mod == "MENU":
        st.markdown(f"<h2 style='text-align:center; color:#5D3EBC;'>Hoşgeldin {st.session_state.ad_soyad} 👋</h2><br>", unsafe_allow_html=True)
        
        c1, c2, c3 = st.columns(3)
        
        with c1:
            st.markdown("""
            <div class='menu-card'>
                <div class='card-icon'>📚</div>
                <div class='card-title'>Etüt Merkezi</div>
                <div class='card-desc'>TYT ve Alan Dersleri</div>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Giriş Yap", key="btn_etut"): st.session_state.aktif_mod = "STUDY_MENU"; st.rerun()

        with c2:
            st.markdown("""
            <div class='menu-card'>
                <div class='card-icon'>🧠</div>
                <div class='card-title'>Simülasyon</div>
                <div class='card-desc'>Gerçek Hayat Senaryoları</div>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Başlat", key="btn_sim"): 
                st.session_state.aktif_mod = "LIFESIM"
                st.session_state.sim_index = 0
                st.rerun()

        with c3:
            st.markdown("""
            <div class='menu-card'>
                <div class='card-icon'>🎮</div>
                <div class='card-title'>Eğlence Modu</div>
                <div class='card-desc'>Oyunlar & Para Kazanma</div>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Oyna", key="btn_fun"): st.session_state.aktif_mod = "FUN_MENU"; st.rerun()

    # ETÜT MENÜSÜ
    elif st.session_state.aktif_mod == "STUDY_MENU":
        st.markdown("## 📚 Etüt Merkezi")
        c1, c2 = st.columns(2)
        with c1:
            if st.button("📘 TYT Kampı"): st.session_state.aktif_mod = "TYT_SECIM"; st.rerun()
        with c2:
            if st.button("💼 Meslek Soruları"): st.session_state.aktif_mod = "MESLEK_SECIM"; st.rerun()
        st.markdown("---")
        if st.button("⬅️ Geri Dön"): st.session_state.aktif_mod = "MENU"; st.rerun()

    # EĞLENCE MENÜSÜ
    elif st.session_state.aktif_mod == "FUN_MENU":
        st.markdown("## 🎮 Eğlence Modu")
        c1, c2 = st.columns(2)
        with c1:
            st.info("👑 **Finans İmparatoru** (Idle)")
            if st.button("Oyuna Gir"): st.session_state.aktif_mod = "GAME"; st.rerun()
        with c2:
            st.success("🧩 **Asset Matrix** (Puzzle)")
            if st.button("Matrix Oyna", type="primary"): # Özel stil için primary
                st.session_state.aktif_mod = "MATRIX"; st.rerun()
        st.markdown("---")
        if st.button("⬅️ Geri Dön"): st.session_state.aktif_mod = "MENU"; st.rerun()

    # TYT SEÇİM
    elif st.session_state.aktif_mod == "TYT_SECIM":
        st.subheader("📘 TYT Test Seçimi")
        current_data = TYT_DATA.copy()
        if st.session_state.premium_user:
            current_data.update(PREMIUM_CONTENT)
            if "Tarih (PREMIUM)" in current_data and isinstance(current_data["Tarih (PREMIUM)"], str):
                del current_data["Tarih (PREMIUM)"]
        
        ders = st.selectbox("Ders Seçiniz:", list(current_data.keys()))
        
        if isinstance(current_data[ders], str) and current_data[ders] == "LOCKED":
            st.error("🔒 Bu test kilitli! Kilidi açmak için Eğlence Modu > Finans İmparatoru oyunundan lisans almalısın.")
        else:
            if st.button("Testi Başlat 🚀"):
                st.session_state.secilen_sorular = current_data[ders]
                st.session_state.soru_index = 0
                st.session_state.dogru = 0
                st.session_state.yanlis = 0
                st.session_state.aktif_mod = "TYT_COZ"
                st.rerun()
        if st.button("⬅️ Geri"): st.session_state.aktif_mod = "STUDY_MENU"; st.rerun()

    # MESLEK SEÇİM
    elif st.session_state.aktif_mod == "MESLEK_SECIM":
        st.subheader("💼 Meslek Test Seçimi")
        current_data = MESLEK_DATA.copy()
        if st.session_state.premium_user:
            current_data.update(PREMIUM_CONTENT)
            if "11. Sınıf - Şirketler (PREMIUM)" in current_data and isinstance(current_data["11. Sınıf - Şirketler (PREMIUM)"], str):
                del current_data["11. Sınıf - Şirketler (PREMIUM)"]

        ders = st.selectbox("Ders Seçiniz:", list(current_data.keys()))
        
        if isinstance(current_data[ders], str) and current_data[ders] == "LOCKED":
            st.error("🔒 Bu test kilitli! Kilidi açmak için lisans satın almalısın.")
        else:
            if st.button("Testi Başlat 🚀"):
                st.session_state.secilen_sorular = current_data[ders]
                st.session_state.soru_index = 0
                st.session_state.dogru = 0
                st.session_state.yanlis = 0
                st.session_state.aktif_mod = "MESLEK_COZ"
                st.rerun()
        if st.button("⬅️ Geri"): st.session_state.aktif_mod = "STUDY_MENU"; st.rerun()

    # SORU ÇÖZME EKRANLARI
    elif st.session_state.aktif_mod in ["TYT_COZ", "MESLEK_COZ"]:
        if st.session_state.soru_index < len(st.session_state.secilen_sorular):
            soru = st.session_state.secilen_sorular[st.session_state.soru_index]
            st.progress((st.session_state.soru_index + 1) / len(st.session_state.secilen_sorular))
            st.markdown(f"### ❓ Soru {st.session_state.soru_index + 1}")
            st.info(soru["soru"])
            
            opts = soru["secenekler"]
            state_key = f"opts_{st.session_state.soru_index}"
            if state_key not in st.session_state: random.shuffle(opts); st.session_state[state_key] = opts
            
            col1, col2 = st.columns(2)
            for i, opt in enumerate(st.session_state[state_key]):
                button_container = col1 if i % 2 == 0 else col2
                if button_container.button(opt, key=f"opt_{i}", use_container_width=True):
                    if opt == soru["cevap"]: st.toast("Doğru! 🎉"); st.session_state.dogru += 1
                    else: st.toast("Yanlış! ❌"); st.session_state.yanlis += 1
                    time.sleep(0.5); st.session_state.soru_index += 1; st.rerun()
        else:
            st.balloons()
            st.success(f"🏁 Test Bitti! Doğru: {st.session_state.dogru} | Yanlış: {st.session_state.yanlis}")
            odul = st.session_state.dogru * 150
            if st.button(f"💰 {odul} ₺ Ödülü Al ve Şirketine Git", type="primary"):
                st.session_state.bekleyen_odul += odul; st.session_state.aktif_mod = "GAME"; st.rerun()

    # LIFE SIM
    elif st.session_state.aktif_mod == "LIFESIM":
        if 'sim_index' not in st.session_state: st.session_state.sim_index = 0
        html_content = LIFE_SIM_DISPLAY_HTML.replace("__DATA__", SCENARIOS_JSON_STRING).replace("__IDX__", str(st.session_state.sim_index))
        components.html(html_content, height=500, scrolling=True)
        st.markdown("### 📝 Analiz Raporu")
        analiz_text = st.text_area("Bu senaryodan ne öğrendin?", height=100, key="analiz_area")
        btn_disabled = len(analiz_text) < 50
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            if st.button("✅ Tamamla ve Ödülü Al (250 ₺)", disabled=btn_disabled, type="primary"):
                st.session_state.bekleyen_odul += 250; st.session_state.aktif_mod = "GAME"; st.rerun()
        with col_btn2:
            if st.button("Sonraki Senaryo ➡️"):
                try: data_len = len(json.loads(SCENARIOS_JSON_STRING)); st.session_state.sim_index = (st.session_state.sim_index + 1) % data_len; st.rerun()
                except: pass
        if st.button("⬅️ Geri Dön"): st.session_state.aktif_mod = "MENU"; st.rerun()

    # GAME
    elif st.session_state.aktif_mod == "GAME":
        reward = st.session_state.bekleyen_odul
        st.session_state.bekleyen_odul = 0
        lb_json = get_hybrid_leaderboard(st.session_state.ad_soyad, 0)
        html = GAME_HTML.replace("__REW__", str(reward)).replace("__USR__", st.session_state.ad_soyad).replace("__LD__", lb_json)
        components.html(html, height=1000)
        if st.button("⬅️ Menüye Dön"): st.session_state.aktif_mod = "MENU"; st.rerun()

    # ASSET MATRIX
    elif st.session_state.aktif_mod == "MATRIX":
        components.html(ASSET_MATRIX_HTML, height=800, scrolling=False)
        if st.button("⬅️ Menüye Dön"): st.session_state.aktif_mod = "MENU"; st.rerun()
