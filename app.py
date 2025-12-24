import streamlit as st
import streamlit.components.v1 as components
import random
import os
import json
import fitz  # PyMuPDF
import time
import pandas as pd

# --- 1. SAYFA AYARLARI ---
st.set_page_config(page_title="Dijital Gelişim Programı", page_icon="🎄", layout="wide")

# --- 2. CSS TASARIMI (YILBAŞI + MODERN) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;500;800&display=swap');
    
    .stApp {
        background: radial-gradient(circle at top, #2b1055, #24243e, #000000);
        font-family: 'Outfit', sans-serif;
        color: white;
    }
    
    h1, h2, h3 { color: #fff !important; text-shadow: 0 0 10px rgba(255,255,255,0.5); }
    
    .giris-kart {
        background: rgba(255, 255, 255, 0.1); backdrop-filter: blur(10px);
        padding: 40px; border-radius: 20px; border: 1px solid rgba(255,255,255,0.2);
        text-align: center; box-shadow: 0 0 30px rgba(138, 43, 226, 0.3); margin-top: 50px;
    }
    
    div.stButton > button {
        background: linear-gradient(90deg, #FF512F 0%, #DD2476 100%) !important;
        color: white !important; border: none !important; border-radius: 12px !important;
        font-weight: 800 !important; padding: 16px 24px !important;
        transition: all 0.3s !important; text-transform: uppercase; letter-spacing: 1px;
        box-shadow: 0 5px 15px rgba(221, 36, 118, 0.4);
    }
    div.stButton > button:hover { transform: translateY(-3px) scale(1.02) !important; box-shadow: 0 10px 20px rgba(221, 36, 118, 0.6) !important; }
    
    div.stTextInput > div > div > input {
        background-color: rgba(255,255,255,0.1) !important; color: white !important;
        border: 1px solid rgba(255,255,255,0.3) !important; border-radius: 10px !important;
    }
    
    .light-rope { text-align: center; white-space: nowrap; overflow: hidden; position: absolute; z-index: 1; margin: -30px 0 0 0; padding: 0; pointer-events: none; width: 100%; left: 0; top: 0; }
    .light { display: inline-block; width: 12px; height: 12px; border-radius: 50%; margin: 20px; background: #00f7a5; box-shadow: 0px 5px 20px 2px #00f7a5; animation: flash 2s infinite alternate; }
    .light:nth-child(2n) { background: #00e6ff; box-shadow: 0px 5px 24px 3px #00e6ff; animation-delay: 0.5s; }
    .light:nth-child(3n) { background: #ff0055; box-shadow: 0px 5px 24px 3px #ff0055; animation-delay: 1s; }
    .light:nth-child(4n) { background: #ffe600; box-shadow: 0px 5px 24px 3px #ffe600; animation-delay: 1.5s; }
    @keyframes flash { 0%, 100% { opacity: 1; transform: scale(1.2); } 50% { opacity: 0.3; transform: scale(0.8); } }

    footer {visibility: hidden;} #MainMenu {visibility: hidden;} header {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

LIGHTS_HTML = """<ul class="light-rope"><li class="light"></li><li class="light"></li><li class="light"></li><li class="light"></li><li class="light"></li><li class="light"></li><li class="light"></li><li class="light"></li><li class="light"></li><li class="light"></li><li class="light"></li><li class="light"></li><li class="light"></li><li class="light"></li><li class="light"></li><li class="light"></li><li class="light"></li><li class="light"></li><li class="light"></li><li class="light"></li></ul>"""

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

# --- 4. DOSYA İSİMLERİ ---
TYT_PDF_ADI = "tytson8.pdf"
TYT_JSON_ADI = "tyt_data.json"
MESLEK_JSON_ADI = "sorular.json"
LIFESIM_JSON_ADI = "lifesim_data.json"
SHEET_ID = "1pHT6b-EiV3a_x3aLzYNu3tQmX10RxWeStD30C8Liqoo"
SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=0"

# --- 5. YEDEK VERİLER (Sadece dosya yoksa devreye girer) ---
YEDEK_TYT = {
    1: {"ders": "Yedek Türkçe", "cevaplar": ["A","B","C","D","E"]},
    2: {"ders": "Yedek Matematik", "cevaplar": ["E","D","C","B","A"]}
}
YEDEK_MESLEK = {
    "KONU_TARAMA": {
        "9. Sınıf": {
            "Yedek Ders": {
                "Yedek Test": [{"soru": "Dosya okunamadı. Bu yedek sorudur.", "secenekler": ["A", "B"], "cevap": "A"}]
            }
        }
    }
}
YEDEK_LIFESIM = """[{"id":1, "category":"HATA", "title":"Dosya Bulunamadı", "text":"lifesim_data.json dosyası yüklenmemiş.", "hint":"GitHub'ı kontrol et.", "doc":"Dosya eksik."}]"""

UNLOCK_CODE = "PRO2025"
PREMIUM_CONTENT = {
    "Tarih (PREMIUM)": [{"soru": "İstanbul'un fethi?", "secenekler": ["1453", "1071", "1299", "1923"], "cevap": "1453"}],
    "11. Sınıf - Şirketler (PREMIUM)": [{"soru": "A.Ş. en az sermaye?", "secenekler": ["10.000", "50.000", "100.000"], "cevap": "50.000"}]
}

# --- 6. FONKSİYONLAR ---
def dosya_yukle(dosya_adi):
    if not os.path.exists(dosya_adi):
        # Dosya yoksa yedek dön, ama kullanıcıya da söyle
        return YEDEK_TYT if dosya_adi == TYT_JSON_ADI else YEDEK_MESLEK
    try:
        with open(dosya_adi, "r", encoding="utf-8") as f:
            data = json.load(f)
            if dosya_adi == TYT_JSON_ADI: return {int(k): v for k, v in data.items()}
            return data
    except: return YEDEK_TYT if dosya_adi == TYT_JSON_ADI else YEDEK_MESLEK

def load_lifesim_data():
    if os.path.exists(LIFESIM_JSON_ADI):
        try:
            with open(LIFESIM_JSON_ADI, "r", encoding="utf-8") as f: return f.read()
        except: pass
    return YEDEK_LIFESIM

def pdf_sayfa_getir(yol, sayfa):
    if not os.path.exists(yol): st.warning("PDF Dosyası Bulunamadı"); return
    try:
        doc = fitz.open(yol)
        if sayfa > len(doc): return
        pix = doc.load_page(sayfa - 1).get_pixmap(dpi=150)
        st.image(pix.tobytes(), use_container_width=True)
    except: pass

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

# VERİLERİ YÜKLE
TYT_VERI = dosya_yukle(TYT_JSON_ADI)
MESLEK_VERI = dosya_yukle(MESLEK_JSON_ADI)
SCENARIOS_JSON_STRING = load_lifesim_data()

# --- HTML ŞABLONLARI ---

# ASSET MATRIX (DÜZELTİLMİŞ)
ASSET_MATRIX_HTML = """
<!DOCTYPE html><html lang="tr"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0,maximum-scale=1.0,user-scalable=no"><title>Matrix</title><style>@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;700;900&display=swap');body{margin:0;overflow:hidden;background-color:#050505;font-family:'Montserrat',sans-serif;color:#fff;touch-action:none;display:flex;flex-direction:column;align-items:center;justify-content:center;height:100vh}#game-container{position:relative;width:95vw;max-width:400px;height:95vh;display:flex;flex-direction:column;justify-content:flex-start;align-items:center;background:radial-gradient(circle at center,#1a1a1a 0%,#000000 100%);border-radius:12px;overflow:hidden;box-shadow:0 0 20px rgba(0,0,0,0.5)}.header{text-align:center;margin-top:10px;margin-bottom:10px;z-index:2;flex-shrink:0}.score-label{font-size:10px;color:#FFD700;letter-spacing:1px;text-transform:uppercase;opacity:0.8}#score{font-size:28px;font-weight:900;color:#fff;text-shadow:0 0 10px rgba(255,215,0,0.5)}canvas{box-shadow:0 0 30px rgba(0,0,0,0.9);border-radius:8px;border:1px solid #333;background:#0a0a0a;touch-action:none;flex-shrink:1}.menu-screen{position:absolute;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,0.95);display:flex;flex-direction:column;justify-content:center;align-items:center;z-index:10;transition:opacity 0.3s}.hidden{opacity:0;pointer-events:none}h1{font-size:2rem;text-transform:uppercase;letter-spacing:-1px;margin-bottom:10px}h1 span{color:#FFD700}p{color:#aaa;margin-bottom:20px;font-size:0.9rem;text-align:center;max-width:80%}.btn{background:linear-gradient(45deg,#FFD700,#C5A028);border:none;padding:12px 30px;font-size:16px;font-weight:800;color:#000;text-transform:uppercase;cursor:pointer;border-radius:30px;box-shadow:0 0 20px rgba(255,215,0,0.3);font-family:'Montserrat',sans-serif;margin-top:10px}.btn:hover{transform:scale(1.05)}.btn-bank{background:linear-gradient(45deg,#22c55e,#15803d);color:white}</style></head><body><div id="game-container"><div class="header"><div class="score-label">Toplam Portföy</div><div id="score">$0</div></div><canvas id="gameCanvas"></canvas><div id="startScreen" class="menu-screen"><h1>Asset <span>Matrix</span></h1><p>Blokları yerleştir, nakit kazan.</p><button class="btn" onclick="initGame()">Piyasaya Gir</button></div><div id="gameOverScreen" class="menu-screen hidden"><h1 style="color:#ff4444;">Piyasa Kilitlendi</h1><p>Kazanç: <span id="finalScore" style="color:#FFD700;font-size:1.5em;">$0</span></p><button class="btn btn-bank" onclick="transferMoney()">💸 BANKAYA AKTAR</button><button class="btn" onclick="initGame()" style="margin-top:10px;font-size:12px;background:#333;color:#aaa">Aktarmadan Oyna</button></div></div><script>const canvas=document.getElementById('gameCanvas');const ctx=canvas.getContext('2d');const scoreEl=document.getElementById('score');const finalScoreEl=document.getElementById('finalScore');const startScreen=document.getElementById('startScreen');const gameOverScreen=document.getElementById('gameOverScreen');const GRID_SIZE=8;let CELL_SIZE=40;let BOARD_OFFSET_X=0;let BOARD_OFFSET_Y=0;const BLOCK_COLOR_Start='#FFD700';const BLOCK_COLOR_End='#C5A028';let grid=Array(GRID_SIZE).fill(0).map(()=>Array(GRID_SIZE).fill(0));let score=0;let availablePieces=[];let draggingPiece=null;let isGameOver=false;const SHAPES=[[[1]],[[1,1]],[[1],[1]],[[1,1,1]],[[1],[1],[1]],[[1,1],[1,1]],[[1,1,1],[0,1,0]],[[1,1,0],[0,1,1]],[[0,1,1],[1,1,0]],[[1,0],[1,0],[1,1]],[[1,1,1],[1,0,0]],[[1,1,1,1]]];function resize(){const container=document.getElementById('game-container');const maxWidth=container.clientWidth;const maxHeight=container.clientHeight-100;let size=Math.min(maxWidth*0.9,maxHeight*0.65);CELL_SIZE=Math.floor(size/GRID_SIZE);canvas.width=CELL_SIZE*GRID_SIZE+20;canvas.height=CELL_SIZE*GRID_SIZE+120;BOARD_OFFSET_X=10;BOARD_OFFSET_Y=10;if(!isGameOver&&availablePieces.length>0)draw()}window.addEventListener('resize',resize);function initGame(){grid=Array(GRID_SIZE).fill(0).map(()=>Array(GRID_SIZE).fill(0));score=0;isGameOver=false;updateScore(0);startScreen.classList.add('hidden');gameOverScreen.classList.add('hidden');generateNewPieces();resize();draw()}function generateNewPieces(){availablePieces=[];for(let i=0;i<3;i++){const shapeMatrix=SHAPES[Math.floor(Math.random()*SHAPES.length)];const spawnY=BOARD_OFFSET_Y+GRID_SIZE*CELL_SIZE+20;const spawnX=BOARD_OFFSET_X+(i*(canvas.width/3));availablePieces.push({matrix:shapeMatrix,x:spawnX,y:spawnY,baseX:spawnX,baseY:spawnY,width:shapeMatrix[0].length*CELL_SIZE,height:shapeMatrix.length*CELL_SIZE,isDragging:false})}if(checkGameOverState()){gameOver()}}function updateScore(points){score+=points;scoreEl.innerText="$"+(score*100).toLocaleString()}function transferMoney(){const earnings=score*100;localStorage.setItem('matrix_transfer',earnings);alert(earnings.toLocaleString()+' ₺ Finans İmparatoru hesabına havale edildi!');location.reload()}function draw(){ctx.clearRect(0,0,canvas.width,canvas.height);drawGrid();drawPlacedBlocks();drawAvailablePieces()}function drawGrid(){ctx.strokeStyle='#333';ctx.lineWidth=0.5;ctx.beginPath();for(let i=0;i<=GRID_SIZE;i++){ctx.moveTo(BOARD_OFFSET_X,BOARD_OFFSET_Y+i*CELL_SIZE);ctx.lineTo(BOARD_OFFSET_X+GRID_SIZE*CELL_SIZE,BOARD_OFFSET_Y+i*CELL_SIZE);ctx.moveTo(BOARD_OFFSET_X+i*CELL_SIZE,BOARD_OFFSET_Y);ctx.lineTo(BOARD_OFFSET_X+i*CELL_SIZE,BOARD_OFFSET_Y+GRID_SIZE*CELL_SIZE)}ctx.stroke()}function drawCell(x,y,size,isPreview=false){const gradient=ctx.createLinearGradient(x,y,x+size,y+size);if(isPreview){gradient.addColorStop(0,'rgba(255, 215, 0, 0.5)');gradient.addColorStop(1,'rgba(197, 160, 40, 0.5)')}else{gradient.addColorStop(0,BLOCK_COLOR_Start);gradient.addColorStop(1,BLOCK_COLOR_End)}ctx.fillStyle=gradient;ctx.fillRect(x+1,y+1,size-2,size-2);ctx.strokeStyle=isPreview?"rgba(255,255,255,0.3)":"rgba(255,255,255,0.5)";ctx.lineWidth=1;ctx.strokeRect(x+2,y+2,size-4,size-4)}function drawPlacedBlocks(){for(let row=0;row<GRID_SIZE;row++){for(let col=0;col<GRID_SIZE;col++){if(grid[row][col]===1){drawCell(BOARD_OFFSET_X+col*CELL_SIZE,BOARD_OFFSET_Y+row*CELL_SIZE,CELL_SIZE)}}}}function drawAvailablePieces(){availablePieces.forEach(piece=>{if(piece.isDragging)return;drawShape(piece.matrix,piece.x,piece.y,CELL_SIZE*0.6)});if(draggingPiece){drawShape(draggingPiece.matrix,draggingPiece.x,draggingPiece.y,CELL_SIZE);const{gridX,gridY}=getGridCoordsFromMouse(draggingPiece.x,draggingPiece.y,draggingPiece.matrix);if(canPlace(draggingPiece.matrix,gridX,gridY)){drawShape(draggingPiece.matrix,BOARD_OFFSET_X+gridX*CELL_SIZE,BOARD_OFFSET_Y+gridY*CELL_SIZE,CELL_SIZE,true)}}}function drawShape(matrix,startX,startY,cellSize,isPreview=false){for(let row=0;row<matrix.length;row++){for(let col=0;col<matrix[row].length;col++){if(matrix[row][col]===1){drawCell(startX+col*cellSize,startY+row*cellSize,cellSize,isPreview)}}}}function canPlace(matrix,gridX,gridY){for(let row=0;row<matrix.length;row++){for(let col=0;col<matrix[row].length;col++){if(matrix[row][col]===1){let targetX=gridX+col;let targetY=gridY+row;if(targetX<0||targetX>=GRID_SIZE||targetY<0||targetY>=GRID_SIZE||grid[targetY][targetX]===1){return false}}}}return true}function placePiece(matrix,gridX,gridY){for(let row=0;row<matrix.length;row++){for(let col=0;col<matrix[row].length;col++){if(matrix[row][col]===1){grid[gridY+row][gridX+col]=1}}}updateScore(matrix.length*matrix[0].length);checkAndClearLines()}function checkAndClearLines(){let linesCleared=0;let rowsToClear=[];let colsToClear=[];for(let row=0;row<GRID_SIZE;row++){if(grid[row].every(cell=>cell===1)){rowsToClear.push(row)}}for(let col=0;col<GRID_SIZE;col++){let full=true;for(let row=0;row<GRID_SIZE;row++){if(grid[row][col]===0){full=false;break}}if(full)colsToClear.push(col)}rowsToClear.forEach(row=>{for(let col=0;col<GRID_SIZE;col++)grid[row][col]=0;linesCleared++});colsToClear.forEach(col=>{for(let row=0;row<GRID_SIZE;row++)grid[row][col]=0;linesCleared++});if(linesCleared>0){updateScore(linesCleared*200*linesCleared)}}let dragOffsetX=0;let dragOffsetY=0;function getEventPos(e){const rect=canvas.getBoundingClientRect();let clientX=e.clientX;let clientY=e.clientY;if(e.touches&&e.touches.length>0){clientX=e.touches[0].clientX;clientY=e.touches[0].clientY}return{x:clientX-rect.left,y:clientY-rect.top}}function getGridCoordsFromMouse(pieceX,pieceY,matrix){let rawGridX=Math.round((pieceX-BOARD_OFFSET_X)/CELL_SIZE);let rawGridY=Math.round((pieceY-BOARD_OFFSET_Y)/CELL_SIZE);return{gridX:rawGridX,gridY:rawGridY}}function handleStart(e){if(isGameOver)return;e.preventDefault();const pos=getEventPos(e);for(let i=availablePieces.length-1;i>=0;i--){const p=availablePieces[i];const renderSize=CELL_SIZE*0.6;const pWidth=p.matrix[0].length*renderSize;const pHeight=p.matrix.length*renderSize;if(pos.x>p.x&&pos.x<p.x+pWidth&&pos.y>p.y&&pos.y<p.y+pHeight){draggingPiece=p;p.isDragging=true;dragOffsetX=pos.x-p.x;dragOffsetY=pos.y-p.y;dragOffsetX=(dragOffsetX/renderSize)*CELL_SIZE;dragOffsetY=(dragOffsetY/renderSize)*CELL_SIZE;draw();return}}}function handleMove(e){if(!draggingPiece)return;e.preventDefault();const pos=getEventPos(e);draggingPiece.x=pos.x-dragOffsetX;draggingPiece.y=pos.y-dragOffsetY;draw()}function handleEnd(e){if(!draggingPiece)return;e.preventDefault();const{gridX,gridY}=getGridCoordsFromMouse(draggingPiece.x,draggingPiece.y,draggingPiece.matrix);if(canPlace(draggingPiece.matrix,gridX,gridY)){placePiece(draggingPiece.matrix,gridX,gridY);availablePieces=availablePieces.filter(p=>p!==draggingPiece);if(availablePieces.length===0){generateNewPieces()}else{if(checkGameOverState())gameOver()}}else{draggingPiece.x=draggingPiece.baseX;draggingPiece.y=draggingPiece.baseY;draggingPiece.isDragging=false}draggingPiece=null;draw()}function checkGameOverState(){if(availablePieces.length===0)return false;for(let i=0;i<availablePieces.length;i++){const matrix=availablePieces[i].matrix;for(let row=0;row<GRID_SIZE;row++){for(let col=0;col<GRID_SIZE;col++){if(canPlace(matrix,col,row)){return false}}}}return true}function gameOver(){isGameOver=true;finalScoreEl.innerText=scoreEl.innerText;gameOverScreen.classList.remove('hidden')}canvas.addEventListener('mousedown',handleStart);canvas.addEventListener('mousemove',handleMove);canvas.addEventListener('mouseup',handleEnd);canvas.addEventListener('mouseleave',handleEnd);canvas.addEventListener('touchstart',handleStart,{passive:false});canvas.addEventListener('touchmove',handleMove,{passive:false});canvas.addEventListener('touchend',handleEnd,{passive:false});resize();</script></body></html>
"""

# FİNANS İMPARATORU
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
    st.markdown(LIGHTS_HTML, unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        <div class='giris-kart'>
            <h1>🎓 Bağarası ÇPAL</h1>
            <h2>Finans & Eğitim Ekosistemi</h2>
            <hr style='border-color:rgba(255,255,255,0.2)'><br>
            <p style="font-size:18px; font-weight:bold; color:#fff;">Muhasebe ve Finansman Dijital Gelişim Programı</p>
        </div>
        """, unsafe_allow_html=True)
        ad = st.text_input("Adınız Soyadınız:", placeholder="Örn: Mehmet")
        if st.button("SİSTEME GİRİŞ YAP 🚀", use_container_width=True):
            if ad:
                st.session_state.ad_soyad = ad
                st.session_state.ekran = 'ana_menu'
                st.rerun()
            else: st.error("Lütfen isim giriniz.")
        st.markdown("<div class='footer-text'>Geliştirici: Zülfikar SITACI</div>", unsafe_allow_html=True)

# 2. ANA MENÜ
elif st.session_state.ekran == 'ana_menu':
    st.markdown(LIGHTS_HTML, unsafe_allow_html=True)
    with st.sidebar:
        st.write(f"👤 **{st.session_state.ad_soyad}**")
        if not st.session_state.premium_user:
            st.caption("🔒 Kilitli İçerik")
            kod = st.text_input("Lisans Kodu:", placeholder="Kodu buraya gir")
            if st.button("Kilidi Aç 🔓"):
                if kod == UNLOCK_CODE:
                    st.session_state.premium_user = True
                    st.success("Kilit Açıldı!")
                    time.sleep(1)
                    st.rerun()
                else: st.error("Hatalı Kod!")
        else: st.success("🌟 PREMIUM ÜYE")
        st.markdown("---")
        if st.button("🏠 Ana Menü"): st.session_state.aktif_mod = "MENU"; st.session_state.secilen_sorular = []; st.rerun()
        if st.button("🎮 Stres At (Para Kazan)"): st.session_state.aktif_mod = "FUN"; st.rerun()
        if st.button("🚪 Çıkış"): st.session_state.ekran = 'giris'; st.rerun()
        st.markdown("<div style='margin-top:50px; font-size:10px; color:gray; text-align:center'>Zülfikar SITACI</div>", unsafe_allow_html=True)

    if st.session_state.aktif_mod == "MENU":
        st.title(f"Hoşgeldin {st.session_state.ad_soyad} 👋")
        
        c1, c2 = st.columns(2)
        with c1:
            st.info("📘 **TYT Kampı**")
            if st.button("TYT Başlat 🚀", key="b1"): st.session_state.aktif_mod = "TYT_SECIM"; st.rerun()
        with c2:
            st.info("💼 **Meslek Lisesi**")
            if st.button("Meslek Çöz 🚀", key="b2"): st.session_state.aktif_mod = "MESLEK_SECIM"; st.rerun()
        
        st.markdown("---")
        
        c3, c4 = st.columns(2)
        with c3:
            st.info("🧠 **Life-Sim (Simülasyon)**")
            if st.button("Simülasyonu Aç", key="b3"): 
                if 'sim_index' not in st.session_state: st.session_state.sim_index = 0
                st.session_state.aktif_mod = "LIFESIM"
                st.rerun()
        with c4:
            st.info("👑 **Finans İmparatoru**")
            if st.button("Oyuna Gir", key="b4"): st.session_state.aktif_mod = "GAME"; st.rerun()

    # TYT SEÇİM
    elif st.session_state.aktif_mod == "TYT_SECIM":
        st.subheader("📘 TYT Test Seçimi")
        current_data = TYT_VERI.copy()
        if st.session_state.premium_user:
            current_data.update(PREMIUM_CONTENT)
            if "Tarih (PREMIUM)" in current_data and isinstance(current_data["Tarih (PREMIUM)"], str): del current_data["Tarih (PREMIUM)"]
        
        ders = st.selectbox("Ders Seçiniz:", list(current_data.keys()))
        if current_data[ders] == "LOCKED": st.error("🔒 Kilitli! Finans İmparatoru'nda 1M ₺ biriktirip lisans al.")
        else:
            if st.button("Testi Başlat 🚀"):
                st.session_state.secilen_sorular = current_data[ders]
                st.session_state.soru_index = 0; st.session_state.dogru = 0; st.session_state.yanlis = 0; st.session_state.aktif_mod = "TYT_COZ"; st.rerun()
        if st.button("⬅️ Menüye Dön"): st.session_state.aktif_mod = "MENU"; st.rerun()

    # MESLEK SEÇİM
    elif st.session_state.aktif_mod == "MESLEK_SECIM":
        st.subheader("💼 Meslek Test Seçimi")
        
        # Konu tarama yapısına ulaş (JSON yapısına göre)
        konu_data = MESLEK_VERI.get("KONU_TARAMA", {})
        
        if konu_data:
            sinif = st.selectbox("Sınıf Seç:", list(konu_data.keys()))
            ders = st.selectbox("Ders Seç:", list(konu_data[sinif].keys()))
            test = st.selectbox("Test Seç:", list(konu_data[sinif][ders].keys()))
            
            if st.button("Testi Başlat 🚀"):
                st.session_state.secilen_sorular = konu_data[sinif][ders][test]
                st.session_state.soru_index = 0
                st.session_state.dogru = 0
                st.session_state.yanlis = 0
                st.session_state.aktif_mod = "MESLEK_COZ"
                st.rerun()
        else:
            st.error("Meslek verisi bulunamadı!")
            
        if st.button("⬅️ Menüye Dön"): st.session_state.aktif_mod = "MENU"; st.rerun()

    # SORU ÇÖZME EKRANI (ORTAK)
    elif st.session_state.aktif_mod in ["TYT_COZ", "MESLEK_COZ"]:
        if st.session_state.soru_index < len(st.session_state.secilen_sorular):
            if st.session_state.aktif_mod == "TYT_COZ":
                # TYT için farklı mantık (Sadece optik form gibi)
                test_id = st.session_state.secilen_sorular[0] # Test ID'si listede tek eleman
                test_data = TYT_VERI[test_id]
                st.subheader(f"📄 {test_data['ders']}")
                c1, c2 = st.columns([1, 1])
                with c1: pdf_sayfa_getir(TYT_PDF_ADI, test_id)
                with c2:
                    with st.form("tyt_form"):
                        st.write("Cevaplarınızı İşaretleyiniz:")
                        for i in range(len(test_data["cevaplar"])):
                            st.radio(f"Soru {i+1}", ["A", "B", "C", "D", "E"], key=f"q_{i}", horizontal=True, index=None)
                        if st.form_submit_button("Testi Bitir"):
                            d, y, b = 0, 0, 0
                            for i, dogru in enumerate(test_data["cevaplar"]):
                                secim = st.session_state.get(f"q_{i}")
                                if secim == dogru: d += 1
                                elif secim: y += 1
                                else: b += 1
                            st.session_state.dogru = d
                            st.session_state.yanlis = y
                            st.session_state.bos = b
                            st.session_state.aktif_mod = "SONUC_TYT"
                            st.rerun()
            else:
                # MESLEK İÇİN İNTERAKTİF
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
            # MESLEK BİTİŞİ
            st.balloons()
            st.success(f"🏁 Test Bitti! Doğru: {st.session_state.dogru} | Yanlış: {st.session_state.yanlis}")
            odul = st.session_state.dogru * 150
            if st.button(f"💰 {odul} ₺ Ödülü Al ve Şirketine Git", type="primary"):
                st.session_state.bekleyen_odul += odul; st.session_state.aktif_mod = "GAME"; st.rerun()

    # TYT SONUÇ
    elif st.session_state.aktif_mod == "SONUC_TYT":
        st.balloons()
        st.success(f"🏁 Sonuçlar: {st.session_state.dogru} Doğru | {st.session_state.yanlis} Yanlış")
        odul = st.session_state.dogru * 150
        if st.button(f"💰 {odul} ₺ Ödülü Al ve Şirketine Git", type="primary"):
            st.session_state.bekleyen_odul += odul; st.session_state.aktif_mod = "GAME"; st.rerun()

    # LIFE SIM
    elif st.session_state.aktif_mod == "LIFESIM":
        if 'sim_index' not in st.session_state: st.session_state.sim_index = 0
        html_content = LIFE_SIM_DISPLAY_HTML.replace("__DATA__", SCENARIOS_JSON_STRING).replace("__IDX__", str(st.session_state.sim_index))
        components.html(html_content, height=500, scrolling=True)
        st.markdown("### 📝 Analiz Raporu")
        st.info("💡 Ödül butonunun aktif olması için en az **50 karakterlik** bir analiz yazmalısın.")
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
        if btn_disabled: st.caption(f"Kalan karakter: {50 - len(analiz_text)}")
        if st.button("⬅️ Menüye Dön"): st.session_state.aktif_mod = "MENU"; st.rerun()

    # GAME
    elif st.session_state.aktif_mod == "GAME":
        reward = st.session_state.bekleyen_odul
        st.session_state.bekleyen_odul = 0
        lb_json = get_hybrid_leaderboard(st.session_state.ad_soyad, 0)
        html = GAME_HTML.replace("__REW__", str(reward)).replace("__USR__", st.session_state.ad_soyad).replace("__LD__", lb_json)
        components.html(html, height=1000)
        if st.button("⬅️ Menüye Dön"): st.session_state.aktif_mod = "MENU"; st.rerun()

    # ASSET MATRIX
    elif st.session_state.aktif_mod == "FUN":
        components.html(ASSET_MATRIX_HTML, height=800, scrolling=False)
        if st.button("⬅️ Menüye Dön"): st.session_state.aktif_mod = "MENU"; st.rerun()
