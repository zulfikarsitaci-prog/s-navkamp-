import streamlit as st
import streamlit.components.v1 as components
import random
import os
import json
import fitz  # PyMuPDF
import time
import pandas as pd

# --- 1. SAYFA AYARLARI ---
st.set_page_config(page_title="Dijital Gelişim Programı", page_icon="🎓", layout="wide")

# --- 2. CSS TASARIMI ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;500;700&display=swap');
    .stApp { background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%); font-family: 'Roboto', sans-serif; }
    h1, h2, h3 { color: #1e3a8a !important; }
    
    .giris-kart { background-color: white; padding: 40px; border-radius: 20px; box-shadow: 0 10px 25px rgba(0,0,0,0.1); text-align: center; border-top: 6px solid #FF7043; margin-top: 30px; }
    
    .stButton>button { background-color: #FF7043 !important; color: white !important; border-radius: 10px; font-weight: bold; border: none !important; padding: 10px 20px; width: 100%; transition: all 0.2s; box-shadow: 0 4px 6px rgba(255, 112, 67, 0.3); }
    .stButton>button:hover { background-color: #F4511E !important; transform: scale(1.02); }
    
    .stTextInput>div>div>input { border-radius: 10px; border: 2px solid #e5e7eb; padding: 10px; }
    
    .secim-karti { background-color: white; padding: 25px; border-radius: 15px; border: 2px solid #e5e7eb; text-align: center; transition: all 0.3s ease; height: 160px; display: flex; flex-direction: column; justify-content: center; align-items: center; cursor: pointer; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); }
    .secim-karti:hover { transform: translateY(-5px); box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1); border-color: #FF7043; }
    
    .footer-text { text-align: center; font-size: 10px; color: #9ca3af; margin-top: 50px; font-family: monospace; opacity: 0.7; }
    
    /* GİZLEMELER */
    footer {visibility: hidden;} #MainMenu {visibility: hidden;}
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

# --- 4. DOSYA VE LİNKLER ---
TYT_PDF_ADI = "tytson8.pdf"
TYT_JSON_ADI = "tyt_data.json"
MESLEK_JSON_ADI = "sorular.json"
LIFESIM_JSON_ADI = "lifesim_data.json"

SHEET_ID = "1pHT6b-EiV3a_x3aLzYNu3tQmX10RxWeStD30C8Liqoo"
SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=0"

# --- 5. VERİ YÜKLEME ---
def dosya_yukle(dosya_adi):
    if not os.path.exists(dosya_adi): return {}
    try:
        with open(dosya_adi, "r", encoding="utf-8") as f:
            data = json.load(f)
            if dosya_adi == TYT_JSON_ADI: return {int(k): v for k, v in data.items()}
            return data
    except: return {}

def load_lifesim_data():
    if os.path.exists(LIFESIM_JSON_ADI):
        try:
            with open(LIFESIM_JSON_ADI, "r", encoding="utf-8") as f: return f.read()
        except: pass
    return """[
    {"id":1, "category":"Girişimcilik", "title":"Okul Kantini İhalesi", "text":"Okulun kantin ihalesi açıldı. İhaleye girmek için 5.000 TL teminat yatırman gerekiyor. İhaleyi kazanırsan günlük cirodan %20 kar elde edeceksin ama kira ve personel giderleri var.<br><br><b>Karar:</b> Risk alıp ihaleye girecek misin?", "hint":"Sabit giderleri hesapla.", "doc":"<h3>Ticari Risk Analizi</h3><p>Net Kar = Ciro - (Kira + Personel + Malzeme).</p>"},
    {"id":2, "category":"Yatırım", "title":"Staj Maaşı", "text":"Stajdan kazandığın 10.000 TL ile ne yapacaksın? Telefon mu alırsın yoksa yatırım mı yaparsın?", "hint":"Aktif ve Pasif farkını hatırla.", "doc":"<h3>Aktif vs Pasif</h3><p>Cebine para koyan şey aktiftir, cebinden para alan şey pasiftir.</p>"}
    ]"""

def pdf_sayfa_getir(yol, sayfa):
    if not os.path.exists(yol): st.warning("PDF Bulunamadı"); return
    try:
        doc = fitz.open(yol)
        if sayfa > len(doc): return
        pix = doc.load_page(sayfa - 1).get_pixmap(dpi=150)
        st.image(pix.tobytes(), use_container_width=True)
    except: pass

@st.cache_data(ttl=5)
def get_hybrid_leaderboard(current_user, current_score):
    try:
        df = pd.read_csv(SHEET_URL)
        df.columns = [str(c).strip().upper().replace('İ','I') for c in df.columns]
        name_col = next((c for c in df.columns if 'ISIM' in c or 'AD' in c), None)
        score_col = next((c for c in df.columns if 'PUAN' in c or 'SKOR' in c), None)
        data = []
        if name_col and score_col:
            for _, row in df.iterrows():
                try: 
                    p = int(pd.to_numeric(row[score_col], errors='coerce'))
                    if p > 0: data.append({"name": str(row[name_col]), "score": p})
                except: continue
        user_found = False
        for p in data:
            if p["name"].strip().lower() == current_user.strip().lower():
                p["score"] = max(p["score"], current_score)
                p["isMe"] = True
                user_found = True
                break
        if not user_found: data.append({"name": current_user, "score": current_score, "isMe": True})
        data.sort(key=lambda x: x["score"], reverse=True)
        return json.dumps(data[:15], ensure_ascii=False)
    except:
        return json.dumps([{"name": current_user, "score": current_score, "isMe": True}], ensure_ascii=False)

# VERİLERİ YÜKLE
TYT_VERI = dosya_yukle(TYT_JSON_ADI)
MESLEK_VERI = dosya_yukle(MESLEK_JSON_ADI)
SCENARIOS_JSON_STRING = load_lifesim_data()

# --- 6. HTML ŞABLONLARI ---

LIFE_SIM_DISPLAY_HTML = """
<!DOCTYPE html><html lang="tr"><head><meta charset="UTF-8"><script src="https://cdn.tailwindcss.com"></script><script src="https://unpkg.com/lucide@latest"></script><style>body{background:transparent;color:#e2e8f0;font-family:sans-serif;padding:10px}.glass{background:rgba(30,41,59,0.95);border-radius:16px;padding:24px;border:1px solid rgba(255,255,255,0.1);box-shadow:0 10px 30px rgba(0,0,0,0.2)}.badge{background:rgba(56,189,248,0.2);color:#38bdf8;padding:4px 12px;border-radius:20px;font-size:12px;font-weight:bold;border:1px solid rgba(56,189,248,0.3)}</style></head>
<body><div class="glass"><div class="flex justify-between items-start mb-4"><span id="cat" class="badge">KATEGORİ</span></div><h2 id="title" class="text-3xl font-bold text-white mb-6">...</h2><div id="text" class="text-gray-300 text-lg leading-relaxed mb-8">...</div><div class="flex gap-3"><button onclick="hint()" class="flex items-center gap-2 text-yellow-400 hover:text-yellow-300 transition"><i data-lucide="lightbulb" class="w-5 h-5"></i> İpucu Al</button><button onclick="doc()" class="flex items-center gap-2 text-purple-400 hover:text-purple-300 transition ml-4"><i data-lucide="book-open" class="w-5 h-5"></i> Uzman Görüşü</button></div><div id="infoBox" class="hidden mt-4 p-4 bg-slate-800/50 rounded-xl border-l-4 border-yellow-500 text-sm text-yellow-100"></div></div><script>lucide.createIcons(); const data = __DATA__; const idx = __IDX__; const item = data[idx]; document.getElementById('cat').innerText = item.category.toUpperCase(); document.getElementById('title').innerText = item.title; document.getElementById('text').innerHTML = item.text; function hint(){ const box = document.getElementById('infoBox'); box.innerHTML = "<b>İPUCU:</b> " + item.hint; box.classList.remove('hidden'); box.style.borderColor = '#eab308'; } function doc(){ const box = document.getElementById('infoBox'); box.innerHTML = item.doc; box.classList.remove('hidden'); box.style.borderColor = '#a855f7'; }</script></body></html>
"""

GAME_HTML = """
<!DOCTYPE html><html lang="tr"><head><meta charset="UTF-8"><script src="https://cdn.tailwindcss.com"></script><script src="https://unpkg.com/lucide@latest"></script><style>body{background:radial-gradient(circle at center,#1e1b4b,#020617);color:white;font-family:sans-serif;overflow:hidden;user-select:none}.glass{background:rgba(255,255,255,0.03);backdrop-filter:blur(10px);border:1px solid rgba(255,255,255,0.05)}.pulse{animation:p 2s infinite}@keyframes p{0%{box-shadow:0 0 0 0 rgba(59,130,246,0.7)}70%{box-shadow:0 0 0 20px rgba(0,0,0,0)}100%{box-shadow:0 0 0 0 rgba(0,0,0,0)}}.item{transition:0.2s}.item.ok{background:rgba(34,197,94,0.1);border-left:4px solid #22c55e;cursor:pointer}.item.no{opacity:0.5;filter:grayscale(1);cursor:not-allowed}::-webkit-scrollbar{width:5px}::-webkit-scrollbar-thumb{background:#334155;border-radius:5px}</style></head>
<body class="h-screen flex flex-col p-2 gap-2"><div class="glass rounded-xl p-3 flex justify-between border-t-2 border-blue-500"><div><div class="text-[10px] text-blue-300">VARLIK</div><div class="text-2xl font-black" id="m">0 ₺</div></div><div class="text-right"><div class="text-[10px] text-green-400">GELİR/SN</div><div class="text-xl font-bold text-green-300" id="cps">0</div></div></div><div class="flex flex-col md:flex-row gap-2 flex-1 overflow-hidden"><div class="w-full md:w-1/3 flex flex-col gap-2"><div class="glass rounded-xl p-3 flex-1 overflow-hidden flex flex-col border border-yellow-500/20"><div class="flex justify-between mb-2 pb-2 border-b border-white/10"><h3 class="font-bold text-yellow-400 text-sm">🏆 LİDERLER</h3><span class="text-[10px] bg-green-900 text-green-300 px-2 rounded">CANLI</span></div><div id="lb" class="overflow-y-auto text-xs flex-1 space-y-1">Yükleniyor...</div></div><div class="glass rounded-xl p-4 flex flex-col items-center justify-center shrink-0"><button onclick="clk(event)" class="pulse w-24 h-24 rounded-full bg-blue-600 flex items-center justify-center shadow-xl border-4 border-white/10 active:scale-95"><i data-lucide="zap" class="w-10 h-10 text-white fill-yellow-400"></i></button><div class="mt-2 text-xs text-slate-400">Güç: <span id="pow" class="text-white">1</span> ₺</div><button onclick="rst()" class="absolute top-2 right-2 text-red-500/50 p-1"><i data-lucide="trash" class="w-3 h-3"></i></button></div></div><div class="w-full md:w-2/3 glass rounded-xl flex flex-col overflow-hidden"><div class="p-3 border-b border-white/5 bg-black/20"><h2 class="font-bold text-sm">🛒 YATIRIMLAR</h2></div><div id="market" class="flex-1 overflow-y-auto p-2 space-y-2"></div></div></div><div id="pop" class="fixed inset-0 bg-black/90 flex items-center justify-center z-50 hidden"><div class="bg-slate-900 border border-yellow-500 p-6 rounded-2xl text-center"><h2 class="text-xl font-bold text-white">TEBRİKLER!</h2><div class="text-3xl font-black text-green-400 my-4">+ <span id="rew">0</span> ₺</div><button onclick="claim()" class="w-full py-2 bg-yellow-500 text-black font-bold rounded">AL</button></div></div>
<script>
lucide.createIcons(); let r=__REW__, u="__USR__", ld=__LD__, inf=1.25;
const def={m:0, b:[{id:0,n:"Limonata",c:25,i:1,cnt:0,ic:"citrus"},{id:1,n:"Simit",c:250,i:4,cnt:0,ic:"bike"},{id:2,n:"YouTube",c:3500,i:20,cnt:0,ic:"youtube"},{id:3,n:"E-Ticaret",c:45000,i:90,cnt:0,ic:"shopping-bag"},{id:4,n:"Yazılım",c:600000,i:500,cnt:0,ic:"code"},{id:5,n:"Fabrika",c:8500000,i:3500,cnt:0,ic:"factory"},{id:6,n:"Banka",c:120000000,i:25000,cnt:0,ic:"landmark"},{id:7,n:"Uzay",c:1500000000,i:100000,cnt:0,ic:"rocket"}]};
let g=JSON.parse(localStorage.getItem('f7'))||def;
if(r>0){document.getElementById('rew').innerText=r.toLocaleString();document.getElementById('pop').classList.remove('hidden');}
upd(); renderLB(); renderM();
setInterval(()=>{let c=getC(); if(c>0){g.m+=c/10; upd();}},100);
setInterval(()=>{localStorage.setItem('f7',JSON.stringify(g))},3000);
function getC(){return g.b.reduce((a,b)=>a+(b.cnt*b.i),0);}
function getK(b){return Math.floor(b.c*Math.pow(inf,b.cnt));}
function upd(){document.getElementById('m').innerText=Math.floor(g.m).toLocaleString()+" ₺"; document.getElementById('cps').innerText=getC().toLocaleString(); document.getElementById('pow').innerText=Math.max(1,Math.floor(getC()*0.01)).toLocaleString(); g.b.forEach((b,i)=>{let k=getK(b), el=document.getElementById('btn-'+i); if(el){el.className=`item p-3 rounded flex justify-between ${g.m>=k?'ok':'no'}`; el.querySelector('.c').innerText=k.toLocaleString()+" ₺"; el.querySelector('.n').innerText=b.cnt;}});}
function renderM(){let l=document.getElementById('market'); l.innerHTML=""; g.b.forEach((b,i)=>{l.innerHTML+=`<div id="btn-${i}" onclick="buy(${i})" class="item p-3 rounded flex justify-between select-none"><div class="flex gap-3"><i data-lucide="${b.ic}"></i><div><div class="font-bold text-sm">${b.n}</div><div class="text-[10px] text-green-400">+${b.i}/sn</div></div></div><div class="text-right"><div class="c font-bold text-yellow-400">0</div><div class="n text-[10px] text-slate-500 bg-black/30 px-1 rounded">0</div></div></div>`;}); lucide.createIcons();}
function clk(e){let p=Math.max(1,Math.floor(getC()*0.01)); g.m+=p; upd(); let f=document.createElement('div'); f.className='click-anim font-bold text-green-400 absolute text-xl'; f.style.left=e.clientX+'px'; f.style.top=(e.clientY-20)+'px'; f.innerText="+"+p; document.body.appendChild(f); setTimeout(()=>f.remove(),800); let me=ld.find(x=>x.isMe); if(me){me.score=g.m; renderLB();}}
function buy(i){let b=g.b[i],k=getK(b); if(g.m>=k){g.m-=k; b.cnt++; upd();}}
function claim(){g.m+=r; document.getElementById('pop').classList.add('hidden'); upd();}
function rst(){if(confirm("Sıfırla?")){localStorage.removeItem('f7'); location.reload();}}
function renderLB(){let l=document.getElementById('lb'); l.innerHTML=""; ld.sort((a,b)=>b.score-a.score).slice(0,10).forEach((p,i)=>{let c=i===0?"text-yellow-400":(i===1?"text-slate-300":"text-slate-500"); l.innerHTML+=`<div class="flex justify-between p-1 rounded ${p.isMe?'bg-blue-600/30':''}"><div class="flex gap-2"><span class="font-black ${c}">${i+1}</span><span class="truncate font-bold text-slate-200">${p.name}</span></div><span class="font-mono text-green-400">${Math.floor(p.score).toLocaleString()}</span></div>`;});}
</script></body></html>
"""

# --- BLOCK BLAST HTML (FİNANS TEMALI) ---
BLOCK_BLAST_HTML = """
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<style>
body { background: #0f172a; color: white; font-family: sans-serif; display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100vh; margin: 0; touch-action: none; overflow: hidden; }
#game-container { width: 95vw; max-width: 400px; display: flex; flex-direction: column; gap: 10px; }
#stats { display: flex; justify-content: space-between; background: rgba(255,255,255,0.05); padding: 15px; border-radius: 12px; border: 1px solid rgba(255,255,255,0.1); }
.stat-box { text-align: center; }
.stat-label { font-size: 10px; color: #94a3b8; letter-spacing: 1px; }
.stat-val { font-size: 20px; font-weight: bold; color: #4ade80; }
#grid { display: grid; grid-template-columns: repeat(8, 1fr); gap: 4px; background: rgba(255,255,255,0.05); padding: 8px; border-radius: 12px; aspect-ratio: 1; }
.cell { background: rgba(255,255,255,0.05); border-radius: 4px; transition: background 0.2s; }
.cell.filled { box-shadow: inset 0 0 10px rgba(0,0,0,0.3); border: 1px solid rgba(255,255,255,0.2); }
#pieces { display: flex; justify-content: space-around; height: 100px; align-items: center; margin-top: 10px; }
.piece-container { width: 80px; height: 80px; display: flex; align-items: center; justify-content: center; }
.piece-preview { display: grid; gap: 2px; transform: scale(0.6); touch-action: none; }
.block { width: 20px; height: 20px; border-radius: 2px; border: 1px solid rgba(255,255,255,0.3); }
.dragging { position: fixed; pointer-events: none; z-index: 1000; transform: scale(1.0); opacity: 0.9; }
.color-1 { background: #22c55e; } /* Dolar Yeşili */
.color-2 { background: #eab308; } /* Altın */
.color-3 { background: #3b82f6; } /* Borsa Mavisi */
.color-4 { background: #a855f7; } /* Kripto Moru */
#msg { position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%); background: rgba(0,0,0,0.9); padding: 30px; border-radius: 16px; text-align: center; display: none; border: 2px solid #eab308; z-index: 2000; }
</style>
</head>
<body>
<div id="game-container">
    <div id="stats">
        <div class="stat-box"><div class="stat-label">TEMETTÜ</div><div class="stat-val" id="score">0 ₺</div></div>
        <div class="stat-box"><div class="stat-label">PORTFÖY</div><div class="stat-val" id="best">0 ₺</div></div>
    </div>
    <div id="grid"></div>
    <div id="pieces"></div>
</div>
<div id="msg">
    <h2 style="color:#eab308; margin-bottom:10px">PİYASA ÇÖKTÜ!</h2>
    <p style="color:#cbd5e1; margin-bottom:20px">Hamle yapacak yer kalmadı.</p>
    <button onclick="resetGame()" style="background:#eab308; border:none; padding:12px 24px; border-radius:8px; font-weight:bold; cursor:pointer">YENİDEN BAŞLA</button>
</div>

<script>
const G=8; let grid=[], score=0, best=localStorage.getItem('bb_best')||0;
const SHAPES=[
    [[1]], [[1,1]], [[1,1,1]], [[1,1,1,1]], // Lines
    [[1,1],[1,1]], // Square
    [[1,0],[1,1]], [[0,1],[1,1]], // L small
    [[1,1,1],[0,1,0]], [[0,1,0],[1,1,1]], // T
    [[1,1,0],[0,1,1]], [[0,1,1],[1,1,0]] // Z
];
const COLORS=['color-1','color-2','color-3','color-4'];

function init(){
    grid=Array(G).fill().map(()=>Array(G).fill(0));
    document.getElementById('grid').innerHTML = '';
    for(let i=0; i<G*G; i++) {
        let d=document.createElement('div'); d.className='cell'; d.id='c-'+i;
        document.getElementById('grid').appendChild(d);
    }
    updateStats(); spawnPieces();
    document.getElementById('msg').style.display='none';
}

function updateStats(){
    document.getElementById('score').innerText=score+" ₺";
    document.getElementById('best').innerText=best+" ₺";
}

function spawnPieces(){
    let p=document.getElementById('pieces'); p.innerHTML='';
    for(let i=0; i<3; i++){
        let sh=SHAPES[Math.floor(Math.random()*SHAPES.length)];
        let cl=COLORS[Math.floor(Math.random()*COLORS.length)];
        let c=document.createElement('div'); c.className='piece-container';
        let pre=createPreview(sh, cl);
        c.appendChild(pre); p.appendChild(c);
        
        // Touch/Mouse Logic
        pre.onmousedown = pre.ontouchstart = startDrag;
    }
}

function createPreview(shape, color){
    let d=document.createElement('div'); d.className='piece-preview';
    d.style.gridTemplateColumns=`repeat(${shape[0].length}, 20px)`;
    d.dataset.shape=JSON.stringify(shape); d.dataset.color=color;
    shape.forEach(row=>{
        row.forEach(cell=>{
            let b=document.createElement('div');
            if(cell) b.className='block '+color;
            d.appendChild(b);
        });
    });
    return d;
}

let dragEl=null, startX, startY, currentShape, currentColor;

function startDrag(e){
    e.preventDefault();
    let touch = e.touches ? e.touches[0] : e;
    let target = e.target.closest('.piece-preview');
    if(!target) return;

    currentShape = JSON.parse(target.dataset.shape);
    currentColor = target.dataset.color;
    
    dragEl = target.cloneNode(true);
    dragEl.className += ' dragging';
    dragEl.style.width = target.offsetWidth + 'px';
    document.body.appendChild(dragEl);
    
    moveDrag(touch);
    
    document.addEventListener('mousemove', onMove);
    document.addEventListener('touchmove', onMove, {passive: false});
    document.addEventListener('mouseup', onEnd);
    document.addEventListener('touchend', onEnd);
    
    target.style.opacity = '0'; // Hide original
}

function onMove(e){
    e.preventDefault();
    let touch = e.touches ? e.touches[0] : e;
    moveDrag(touch);
    highlightGrid(touch.clientX, touch.clientY);
}

function moveDrag(touch){
    if(dragEl){
        dragEl.style.left = (touch.clientX - dragEl.offsetWidth/2) + 'px';
        dragEl.style.top = (touch.clientY - dragEl.offsetHeight) + 'px'; // Offset above finger
    }
}

function onEnd(e){
    document.removeEventListener('mousemove', onMove);
    document.removeEventListener('touchmove', onMove);
    document.removeEventListener('mouseup', onEnd);
    document.removeEventListener('touchend', onEnd);
    
    let touch = e.changedTouches ? e.changedTouches[0] : e;
    let placed = tryPlace(touch.clientX, touch.clientY);
    
    if(placed){
        // Remove from container
        let originals = document.querySelectorAll('.piece-preview');
        for(let o of originals){
            if(o.style.opacity === '0') o.parentElement.remove();
        }
        score += currentShape.flat().reduce((a,b)=>a+b,0) * 10;
        checkLines();
        if(document.getElementById('pieces').children.length === 0) spawnPieces();
        checkGameOver();
    } else {
        // Return animation could go here
        let originals = document.querySelectorAll('.piece-preview');
        for(let o of originals) o.style.opacity = '1';
    }
    
    if(dragEl) dragEl.remove();
    dragEl = null; clearHighlight(); updateStats();
}

function getGridPos(x, y){
    // Offset because user drags from above finger
    y = y - 50; 
    let els = document.elementsFromPoint(x, y);
    let cell = els.find(e => e.classList.contains('cell'));
    if(cell){
        let id = parseInt(cell.id.split('-')[1]);
        return {r: Math.floor(id/G), c: id%G};
    }
    return null;
}

function tryPlace(x, y){
    let pos = getGridPos(x, y);
    if(!pos) return false;
    
    // Check boundaries and collision
    let r = pos.r, c = pos.c;
    // Adjust logic to center/corner? Let's assume top-left of shape drops on cell
    
    for(let i=0; i<currentShape.length; i++){
        for(let j=0; j<currentShape[0].length; j++){
            if(currentShape[i][j]){
                if(r+i >= G || c+j >= G || grid[r+i][c+j]) return false;
            }
        }
    }
    
    // Place
    for(let i=0; i<currentShape.length; i++){
        for(let j=0; j<currentShape[0].length; j++){
            if(currentShape[i][j]){
                grid[r+i][c+j] = 1;
                let cell = document.getElementById(`c-${(r+i)*G + (c+j)}`);
                cell.className = 'cell filled ' + currentColor;
            }
        }
    }
    return true;
}

function highlightGrid(x, y){
    clearHighlight();
    let pos = getGridPos(x, y);
    if(!pos) return;
    
    let r = pos.r, c = pos.c;
    let valid = true;
    
    for(let i=0; i<currentShape.length; i++){
        for(let j=0; j<currentShape[0].length; j++){
            if(currentShape[i][j]){
                if(r+i >= G || c+j >= G || grid[r+i][c+j]) valid = false;
            }
        }
    }
    
    if(valid){
        for(let i=0; i<currentShape.length; i++){
            for(let j=0; j<currentShape[0].length; j++){
                if(currentShape[i][j]){
                    let cell = document.getElementById(`c-${(r+i)*G + (c+j)}`);
                    if(cell) cell.style.background = 'rgba(255,255,255,0.2)';
                }
            }
        }
    }
}

function clearHighlight(){
    document.querySelectorAll('.cell').forEach(c => {
        if(!c.classList.contains('filled')) c.style.background = '';
    });
}

function checkLines(){
    let rows=[], cols=[];
    // Check rows
    for(let r=0; r<G; r++){
        if(grid[r].every(v=>v===1)) rows.push(r);
    }
    // Check cols
    for(let c=0; c<G; c++){
        let full=true;
        for(let r=0; r<G; r++) if(grid[r][c]===0) full=false;
        if(full) cols.push(c);
    }
    
    if(rows.length + cols.length > 0){
        // Clear logic
        rows.forEach(r => {
            grid[r].fill(0);
            for(let c=0; c<G; c++) animateClear(r,c);
        });
        cols.forEach(c => {
            for(let r=0; r<G; r++) { grid[r][c]=0; animateClear(r,c); }
        });
        score += (rows.length + cols.length) * 100;
        if(score > best) { best = score; localStorage.setItem('bb_best', best); }
    }
}

function animateClear(r, c){
    let cell = document.getElementById(`c-${r*G + c}`);
    cell.className = 'cell'; // Reset class
    cell.style.transform = 'scale(0)';
    setTimeout(()=>cell.style.transform='scale(1)', 200);
}

function checkGameOver(){
    // Simple check: can any piece fit?
    // This is computationally expensive, simplified here:
    // If board is very full, maybe check. For this demo, we assume loose check.
}

function resetGame(){
    score = 0;
    init();
}

init();
</script>
</body>
</html>
"""

# --- 7. UYGULAMA MANTIĞI ---

# 1. GİRİŞ EKRANI
if st.session_state.ekran == 'giris':
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        <div class='giris-kart'>
            <h1>🎓 Bağarası ÇPAL</h1>
            <h2>Finans & Eğitim Ekosistemi</h2>
            <hr><br>
            <p style="font-size:18px; font-weight:bold; color:#D84315;">Muhasebe ve Finansman Dijital Gelişim Programı</p>
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

# 2. ANA MENÜ VE İÇERİK
elif st.session_state.ekran == 'ana_menu':
    # YAN MENÜ
    with st.sidebar:
        st.write(f"👤 **{st.session_state.ad_soyad}**")
        if st.button("🏠 Ana Menü"):
            st.session_state.aktif_mod = "MENU"
            st.session_state.secilen_sorular = []
            st.rerun()
        if st.button("🎮 Stres At"):
            st.session_state.aktif_mod = "FUN"
            st.rerun()
        if st.button("🚪 Çıkış"):
            st.session_state.ekran = 'giris'
            st.rerun()
        st.markdown("<div style='margin-top:50px; font-size:10px; color:gray; text-align:center'>Zülfikar SITACI</div>", unsafe_allow_html=True)

    # İÇERİK YÖNETİMİ
    if st.session_state.aktif_mod == "MENU":
        st.title("Hoşgeldin! Bugün ne yapmak istersin?")
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("<div class='secim-karti'><h3>📘 TYT Kampı</h3><p>Temel Yeterlilik Testi</p></div>", unsafe_allow_html=True)
            if st.button("TYT Başlat", key="b1"): st.session_state.aktif_mod = "TYT_SECIM"; st.rerun()
        with c2:
            st.markdown("<div class='secim-karti'><h3>💼 Meslek Lisesi</h3><p>Alan Dersleri</p></div>", unsafe_allow_html=True)
            if st.button("Meslek Çöz", key="b2"): st.session_state.aktif_mod = "MESLEK_SECIM"; st.rerun()
        
        st.markdown("---")
        
        c3, c4 = st.columns(2)
        with c3:
            st.markdown("<div class='secim-karti' style='border-color:#38bdf8'><h3>🧠 Life-Sim</h3><p>Yaşam Senaryoları</p></div>", unsafe_allow_html=True)
            if st.button("Simülasyon", key="b3"): 
                # Simülasyon indexini sıfırla
                if 'sim_index' not in st.session_state: st.session_state.sim_index = 0
                st.session_state.aktif_mod = "LIFESIM"
                st.rerun()
        with c4:
            st.markdown("<div class='secim-karti' style='border-color:#fbbf24'><h3>👑 Finans İmparatoru</h3><p>Şirketini Kur!</p></div>", unsafe_allow_html=True)
            if st.button("Oyuna Gir", key="b4"): st.session_state.aktif_mod = "GAME"; st.rerun()

    # TYT SEÇİM EKRANI
    elif st.session_state.aktif_mod == "TYT_SECIM":
        st.subheader("📘 TYT Test Seçimi")
        if TYT_VERI:
            test_listesi = list(TYT_VERI.keys())
            secilen_test_id = st.selectbox("Bir Test Seçiniz:", test_listesi, format_func=lambda x: f"Test {x} - {TYT_VERI[x]['ders']}")
            if st.button("Testi Başlat 🚀"):
                st.session_state.secilen_sorular = [secilen_test_id]
                st.session_state.soru_index = 0
                st.session_state.dogru = 0
                st.session_state.yanlis = 0
                st.session_state.bos = 0
                st.session_state.aktif_mod = "TYT_COZ"
                st.rerun()
        else:
            st.error("TYT Verisi Yüklenemedi! (tyt_data.json eksik)")

    # MESLEK SEÇİM EKRANI
    elif st.session_state.aktif_mod == "MESLEK_SECIM":
        st.subheader("💼 Meslek Test Seçimi")
        konu_data = MESLEK_VERI.get("KONU_TARAMA", {})
        
        if konu_data:
            sinif = st.selectbox("Sınıf Seç:", list(konu_data.keys()))
            if sinif:
                ders = st.selectbox("Ders Seç:", list(konu_data[sinif].keys()))
                if ders:
                    test = st.selectbox("Test Seç:", list(konu_data[sinif][ders].keys()))
                    
                    if st.button("Testi Başlat 🚀"):
                        st.session_state.secilen_sorular = konu_data[sinif][ders][test]
                        st.session_state.soru_index = 0
                        st.session_state.dogru = 0
                        st.session_state.yanlis = 0
                        st.session_state.aktif_mod = "MESLEK_COZ"
                        st.rerun()
        else:
            st.error("Meslek Verisi Yüklenemedi! (sorular.json eksik)")

    # TYT ÇÖZME EKRANI
    elif st.session_state.aktif_mod == "TYT_COZ":
        test_id = st.session_state.secilen_sorular[0]
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
                    st.session_state.aktif_mod = "SONUC"
                    st.rerun()

    # MESLEK ÇÖZME EKRANI
    elif st.session_state.aktif_mod == "MESLEK_COZ":
        if st.session_state.soru_index < len(st.session_state.secilen_sorular):
            soru = st.session_state.secilen_sorular[st.session_state.soru_index]
            
            st.progress((st.session_state.soru_index) / len(st.session_state.secilen_sorular))
            st.markdown(f"### ❓ Soru {st.session_state.soru_index + 1}")
            st.info(soru["soru"])
            
            opts = soru["secenekler"]
            state_key = f"opts_{st.session_state.soru_index}"
            if state_key not in st.session_state:
                random.shuffle(opts)
                st.session_state[state_key] = opts
            
            col1, col2 = st.columns(2)
            for i, opt in enumerate(st.session_state[state_key]):
                button_container = col1 if i % 2 == 0 else col2
                if button_container.button(opt, key=f"opt_{i}", use_container_width=True):
                    if opt == soru["cevap"]:
                        st.toast("Doğru! 🎉")
                        st.session_state.dogru += 1
                    else:
                        st.toast("Yanlış! ❌")
                        st.session_state.yanlis += 1
                    time.sleep(0.5)
                    st.session_state.soru_index += 1
                    st.rerun()
        else:
            st.session_state.aktif_mod = "SONUC"
            st.rerun()

    # SONUÇ EKRANI
    elif st.session_state.aktif_mod == "SONUC":
        st.balloons()
        st.success(f"🏁 Test Bitti! Doğru: {st.session_state.dogru} | Yanlış: {st.session_state.yanlis}")
        odul = st.session_state.dogru * 150
        if st.button(f"💰 {odul} ₺ Ödülü Al ve Şirketine Git", type="primary"):
            st.session_state.bekleyen_odul += odul
            st.session_state.aktif_mod = "GAME"
            st.rerun()

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
            if st.button("✅ Analizi Tamamla ve Ödülü Al (250 ₺)", disabled=btn_disabled, type="primary"):
                st.session_state.bekleyen_odul += 250
                st.session_state.aktif_mod = "GAME"
                st.rerun()
        with col_btn2:
            if st.button("Sonraki Senaryo ➡️"):
                try:
                    data_len = len(json.loads(SCENARIOS_JSON_STRING))
                    st.session_state.sim_index = (st.session_state.sim_index + 1) % data_len
                    st.rerun()
                except: pass
        if btn_disabled: st.caption(f"Kalan karakter: {50 - len(analiz_text)}")

    # GAME (IDLE)
    elif st.session_state.aktif_mod == "GAME":
        reward = st.session_state.bekleyen_odul
        st.session_state.bekleyen_odul = 0
        lb_json = get_hybrid_leaderboard(st.session_state.ad_soyad, 0)
        html = GAME_HTML.replace("__REW__", str(reward)).replace("__USR__", st.session_state.ad_soyad).replace("__LD__", lb_json)
        components.html(html, height=1000)

    # BLOCK BLAST EĞLENCE MODU
    elif st.session_state.aktif_mod == "FUN":
        components.html(BLOCK_BLAST_HTML, height=800, scrolling=False)
