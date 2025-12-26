import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import requests
import json
import os
import time

# 1. SAYFA AYARLARI
st.set_page_config(
    page_title="Bağarası ÇPAL - Finans Ekosistemi",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ==========================================
# 🔗 GITHUB AYARLARI (OTOMATİK)
# ==========================================
GITHUB_USER = "zulfikarsitaci-prog"
GITHUB_REPO = "s-navkamp-"
GITHUB_BRANCH = "main"
GITHUB_BASE_URL = f"https://raw.githubusercontent.com/{GITHUB_USER}/{GITHUB_REPO}/{GITHUB_BRANCH}"

# Dosya Linkleri
URL_LIFESIM = f"{GITHUB_BASE_URL}/lifesim_data.json"
URL_TYT_DATA = f"{GITHUB_BASE_URL}/tyt_data.json"
URL_TYT_PDF = f"{GITHUB_BASE_URL}/tytson8.pdf"
URL_MESLEK_SORULAR = f"{GITHUB_BASE_URL}/sorular.json"

# TYT Ders Sayfa Haritası (PDF'teki Başlangıç Sayfaları)
TYT_DERS_SAYFA_HARITASI = {
    "Türkçe": 1,
    "Sosyal Bilimler": 21,
    "Temel Matematik": 41,
    "Fen Bilimleri": 61
}

# ==========================================
# 3. YARDIMCI FONKSİYONLAR
# ==========================================
@st.cache_data(ttl=300)
def fetch_json_data(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = json.loads(response.text)
            if isinstance(data, list): return data
    except: pass
    return []

def load_lifesim_html():
    try:
        if os.path.exists("game.html"):
            with open("game.html", "r", encoding="utf-8") as f: html = f.read()
        else:
            resp = requests.get(f"{GITHUB_BASE_URL}/game.html")
            html = resp.text if resp.status_code == 200 else "<h3>game.html bulunamadı</h3>"
        
        data = fetch_json_data(URL_LIFESIM)
        json_str = json.dumps(data)
        return html.replace("// PYTHON_DATA_HERE", f"var scenarios = {json_str};")
    except: return "<h3>Yükleme Hatası</h3>"

def decode_transfer_code(code):
    try:
        parts = code.split('-')
        if len(parts) != 3 or parts[0] != "FNK": return None
        return int(int(parts[1], 16) / 13)
    except: return None

# ==========================================
# 🎮 OYUN KODLARI (SABİT)
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
        let val = Math.floor(money); let hex = (val * 13).toString(16).toUpperCase(); let rnd = Math.floor(Math.random() * 100); let code = `FNK-${hex}-${rnd}`;
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
    <title>Asset Matrix</title>
    <style>
        body { margin: 0; background-color: #050505; color: white; font-family: monospace; display: flex; flex-direction: column; align-items: center; touch-action: none; padding: 10px; }
        canvas { background: #111; border: 2px solid #333; box-shadow: 0 0 20px rgba(0,255,255,0.1); display: block; margin-bottom: 10px; }
        .btn { background: #3b82f6; border: none; padding: 8px 20px; color: white; font-weight: bold; border-radius: 20px; cursor: pointer; margin-top: 5px; font-size: 12px; }
        .code-box { margin-top: 10px; background: white; color: black; padding: 5px; font-weight: bold; display: none; text-align: center; width: 100%; word-break: break-all; border-radius: 4px; }
        .score-board { font-size: 20px; font-weight: bold; color: #facc15; margin-bottom: 10px; }
    </style>
</head>
<body>
    <div class="score-board">SKOR: $<span id="score">0</span></div>
    <canvas id="gameCanvas"></canvas>
    <button class="btn" onclick="getTransferCode()">🏦 BANKAYA AKTAR</button>
    <div id="codeArea" class="code-box"></div>
    <script>
        const canvas = document.getElementById('gameCanvas'); const ctx = canvas.getContext('2d');
        const GRID_SIZE = 10; let CELL_SIZE = 30; let grid = [], pieces = [], dragging = null, score = 0;
        function resize() {
            const maxWidth = window.innerWidth - 20; const size = Math.min(maxWidth, 400); 
            CELL_SIZE = Math.floor(size / (GRID_SIZE + 2)); canvas.width = CELL_SIZE * GRID_SIZE + 20; canvas.height = CELL_SIZE * GRID_SIZE + 120;
            if(pieces.length > 0) draw();
        }
        const SHAPES = [[[1]], [[1,1]], [[1],[1]], [[1,1],[1,1]], [[1,1,1]], [[1],[1],[1]], [[0,1,0],[1,1,1]]];
        function init() { grid = Array(GRID_SIZE).fill(0).map(()=>Array(GRID_SIZE).fill(0)); score = 0; spawnPieces(); draw(); }
        function spawnPieces() {
            pieces = []; for(let i=0; i<3; i++) {
                const m = SHAPES[Math.floor(Math.random()*SHAPES.length)]; const w = m[0].length * CELL_SIZE; const x = 10 + i * (canvas.width/3) + (canvas.width/3 - w)/2; const y = CELL_SIZE * GRID_SIZE + 30;
                pieces.push({ m, x, y, bx: x, by: y, w, h: m.length*CELL_SIZE });
            }
        }
        function draw() {
            ctx.fillStyle = "#080808"; ctx.fillRect(0,0,canvas.width,canvas.height);
            ctx.strokeStyle = "#222"; ctx.lineWidth = 1; ctx.beginPath();
            for(let i=0; i<=GRID_SIZE; i++) { ctx.moveTo(10, 10+i*CELL_SIZE); ctx.lineTo(10+GRID_SIZE*CELL_SIZE, 10+i*CELL_SIZE); ctx.moveTo(10+i*CELL_SIZE, 10); ctx.lineTo(10+i*CELL_SIZE, 10+GRID_SIZE*CELL_SIZE); }
            ctx.stroke();
            for(let r=0; r<GRID_SIZE; r++) for(let c=0; c<GRID_SIZE; c++) if(grid[r][c]) { ctx.fillStyle = "#facc15"; ctx.fillRect(10+c*CELL_SIZE+1, 10+r*CELL_SIZE+1, CELL_SIZE-2, CELL_SIZE-2); }
            pieces.forEach(p => { ctx.fillStyle = p === dragging ? "rgba(6, 182, 212, 0.8)" : "#06b6d4"; p.m.forEach((row, r) => row.forEach((val, c) => { if(val) ctx.fillRect(p.x + c*CELL_SIZE, p.y + r*CELL_SIZE, CELL_SIZE-2, CELL_SIZE-2); })); });
            document.getElementById('score').innerText = score;
        }
        function getPos(e) {
            const r = canvas.getBoundingClientRect(); let clientX = e.changedTouches ? e.changedTouches[0].clientX : e.clientX; let clientY = e.changedTouches ? e.changedTouches[0].clientY : e.clientY;
            return { x: (x-r.left)*(canvas.width/r.width), y: (y-r.top)*(canvas.height/r.height) };
        }
        function start(e) {
            e.preventDefault(); const p_ = getPos(e);
            for(let i=pieces.length-1; i>=0; i--) { const p = pieces[i]; if(p_.x>=p.x-10 && p_.x<=p.x+p.w+10 && p_.y>=p.y-10 && p_.y<=p.y+p.h+10) { dragging = p; dragging.dx = p_.x - p.x; dragging.dy = p_.y - p.y; draw(); return; } }
        }
        function move(e) { if(!dragging) return; e.preventDefault(); const p = getPos(e); dragging.x = p.x - dragging.dx; dragging.y = p.y - dragging.dy; draw(); }
        function end(e) {
            if(!dragging) return; e.preventDefault(); const gx = Math.round((dragging.x-10)/CELL_SIZE); const gy = Math.round((dragging.y-10)/CELL_SIZE);
            if(canPlace(dragging.m, gx, gy)) { place(dragging.m, gx, gy); pieces = pieces.filter(p => p !== dragging); if(pieces.length === 0) spawnPieces(); } else { dragging.x = dragging.bx; dragging.y = dragging.by; }
            dragging = null; draw();
        }
        function canPlace(m, gx, gy) {
            return m.every((row, r) => row.every((val, c) => { if(!val) return true; const tx=gx+c, ty=gy+r; return tx>=0 && tx<GRID_SIZE && ty>=0 && ty<GRID_SIZE && !grid[ty][tx]; }));
        }
        function place(m, gx, gy) {
            m.forEach((row, r) => row.forEach((val, c) => { if(val) grid[gy+r][gx+c]=1; })); score += 10; 
            let rows=[], cols=[]; for(let r=0; r<GRID; r++) if(grid[r].every(v=>v)) rows.push(r); for(let c=0; c<GRID; c++) if(grid.map(r=>r[c]).every(v=>v)) cols.push(c);
            if(rows.length+cols.length > 0) { rows.forEach(r => grid[r].fill(0)); cols.forEach(c => grid.forEach(r => r[c]=0)); score += (rows.length+cols.length) * 50; }
        }
        function getTransferCode() {
            if(score < 50) { alert("En az 50 Puan gerekli."); return; }
            let val = score; let hex = (val * 13).toString(16).toUpperCase(); let code = `FNK-${hex}-MTX`;
            document.getElementById('codeArea').innerText = code; document.getElementById('codeArea').style.display = 'block'; score = 0; init();
        }
        canvas.addEventListener('mousedown', start); canvas.addEventListener('touchstart', start, {passive:false}); canvas.addEventListener('mousemove', move); canvas.addEventListener('touchmove', move, {passive:false}); canvas.addEventListener('mouseup', end); canvas.addEventListener('touchend', end, {passive:false});
        window.addEventListener('resize', resize); window.onload = () => { resize(); init(); };
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
    
    /* Optik Form Satır Stili */
    .optik-row { background:white; padding:5px 15px; border-bottom:1px solid #eee; display:flex; justify-content:space-between; align-items:center; }
    .optik-row:hover { background-color:#f8f9fa; }
</style>
""", unsafe_allow_html=True)

if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'user_name' not in st.session_state: st.session_state.user_name = ""
if 'user_no' not in st.session_state: st.session_state.user_no = ""
if 'bank_balance' not in st.session_state: st.session_state.bank_balance = 0

# --- EKRAN 1: GİRİŞ ---
if not st.session_state.logged_in:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown("""
        <div class="login-container">
            <h1 style="font-size: 2.5rem; margin-bottom: 0;">🎓 Bağarası ÇPAL</h1>
            <h2 style="color: #555 !important; margin-top: 0;">Finans & Eğitim Ekosistemi</h2>
            <hr style="border: 1px solid #eee; margin: 20px 0;">
            <p style="font-size:18px; font-weight:bold; color:#D84315;">
                Muhasebe ve Finansman Alanı Dijital Dönüşüm Projesi
            </p>
            <br>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        with st.form("login_form"):
            ad = st.text_input("Adı Soyadı", placeholder="Örn: Ahmet Yılmaz")
            no = st.text_input("Okul Numarası", placeholder="Örn: 1453")
            if st.form_submit_button("SİSTEME GİRİŞ YAP"):
                if ad and no:
                    st.session_state.logged_in = True
                    st.session_state.user_name = ad
                    st.session_state.user_no = no
                    st.rerun()
                else: st.error("Lütfen bilgileri giriniz.")

# --- EKRAN 2: ANA MENÜ ---
else:
    st.markdown(f"""
    <div style="display:flex; justify-content:space-between; align-items:center; padding:10px 20px; background:white; border-radius:10px; margin-bottom:20px; box-shadow: 0 2px 5px rgba(0,0,0,0.05);">
        <div style="font-family:'Cinzel'; font-weight:bold; font-size:18px; color:#2c3e50;">🎓 BAĞARASI ÇPAL</div>
        <div style="font-family:'Poppins'; font-size:14px; color:#555;">
            Hoşgeldin, <b>{st.session_state.user_name}</b> | 🏦 Banka: <span style="color:#27ae60; font-weight:bold;">{st.session_state.bank_balance} ₺</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    tab_ana, tab_profil, tab_soru, tab_eglence, tab_lifesim, tab_premium = st.tabs([
        "🏆 ANA EKRAN", "👤 PROFİL", "📚 SORU ÇÖZÜM", "🎮 EĞLENCE", "💼 LIFESIM", "💎 PREMIUM"
    ])

    with tab_ana:
        c_bank, c_score = st.columns([1, 2])
        with c_bank:
            st.markdown('<div class="bank-box"><h3>🏦 MERKEZ BANKASI VEZNESİ</h3><p>Oyunlardan aldığınız kodları buraya girin.</p></div>', unsafe_allow_html=True)
            code = st.text_input("Transfer Kodu:", key="transfer_code")
            if st.button("💰 KODU BOZDUR", use_container_width=True):
                amt = decode_transfer_code(code)
                if amt:
                    st.session_state.bank_balance += amt
                    st.success(f"✅ İŞLEM BAŞARILI! Hesabınıza {amt} ₺ eklendi.")
                    time.sleep(2)
                    st.rerun()
                else: st.error("Geçersiz kod!")
        with c_score:
            st.header("🏆 Okul Sıralaması")
            data = [{'Sıra': 1, 'Ad Soyad': 'Ayşe Y.', 'Puan': 50000}, {'Sıra': 2, 'Ad Soyad': 'Mehmet K.', 'Puan': 42000}, {'Sıra': 3, 'Ad Soyad': st.session_state.user_name + " (SİZ)", 'Puan': st.session_state.bank_balance}]
            st.table(pd.DataFrame(data))

    with tab_profil:
        st.info(f"Öğrenci: {st.session_state.user_name} ({st.session_state.user_no})")
        if st.button("Çıkış Yap"): st.session_state.logged_in = False; st.rerun()

    # --- SORU ÇÖZÜM MERKEZİ ---
    with tab_soru:
        st.header("📚 Soru Çözüm Merkezi")
        t_tyt, t_meslek = st.tabs(["📘 TYT (KİTAPÇIKLI)", "📙 MESLEK (ONLİNE)"])
        
        # 1. TYT BÖLÜMÜ
        with t_tyt:
            # ÖNCE VERİYİ ÇEK (Scope Hatasını Önlemek İçin)
            tyt_questions = fetch_json_data(URL_TYT_DATA)
            
            if not tyt_questions:
                st.warning("TYT verileri yükleniyor veya dosya bulunamadı...")
            else:
                # KATEGORİ SEÇİMİNİ ANA ALANDA YAP
                cats_tyt = list(set([q.get('category', 'Genel') for q in tyt_questions if isinstance(q, dict)]))
                sel_cat_tyt = st.selectbox("Ders Seçiniz:", cats_tyt, key="tyt_sel_cat")
                
                c_pdf, c_optik = st.columns([1.5, 1])
                
                with c_pdf:
                    start_page = TYT_DERS_SAYFA_HARITASI.get(sel_cat_tyt, 1)
                    st.markdown(f"""
                    <embed src="{URL_TYT_PDF}#page={start_page}" width="100%" height="800px" type="application/pdf">
                    """, unsafe_allow_html=True)

                with c_optik:
                    st.subheader(f"📝 {sel_cat_tyt} Optik Formu")
                    active_questions = [q for q in tyt_questions if q.get('category') == sel_cat_tyt]
                    
                    with st.form(key=f"tyt_optik_{sel_cat_tyt}"):
                        user_answers = {}
                        for i, q in enumerate(active_questions):
                            col_q, col_opt = st.columns([1, 3])
                            col_q.markdown(f"**{i+1}.**")
                            user_answers[i] = col_opt.radio(f"{i+1}", ['A', 'B', 'C', 'D', 'E'], key=f"t_{i}", horizontal=True, label_visibility="collapsed", index=None)
                        
                        if st.form_submit_button("SINAVI BİTİR"):
                            dogru, yanlis = 0, 0
                            for i, q in enumerate(active_questions):
                                if user_answers[i] == q.get('correct'):
                                    dogru += 1
                                else:
                                    yanlis += 1
                                    st.markdown(f"<small style='color:red'>Soru {i+1}: Yanlış (Sen: {user_answers[i]} - Cevap: {q.get('correct')})</small>", unsafe_allow_html=True)
                            
                            puan = dogru * 50
                            st.success(f"Sonuç: {dogru} Doğru, {yanlis} Yanlış")
                            st.info(f"Kazanılan Puan: {puan} ₺")
                            st.session_state.bank_balance += puan

        # 2. MESLEK BÖLÜMÜ
        with t_meslek:
            meslek_qs = fetch_json_data(URL_MESLEK_SORULAR)
            
            if not meslek_qs:
                st.warning("Meslek soruları yükleniyor... (sorular.json bekleniyor)")
            else:
                siniflar = sorted(list(set([str(q.get('sinif', 'Genel')) for q in meslek_qs if isinstance(q, dict)])))
                sel_sinif = st.selectbox("Sınıf Seviyesi:", siniflar)
                
                dersler = sorted(list(set([q.get('category') for q in meslek_qs if str(q.get('sinif', 'Genel')) == sel_sinif])))
                sel_ders = st.selectbox("Ders Seçiniz:", dersler)
                
                active_meslek_qs = [q for q in meslek_qs if str(q.get('sinif', 'Genel')) == sel_sinif and q.get('category') == sel_ders]
                
                st.markdown("---")
                with st.form(key=f"meslek_optik_{sel_sinif}_{sel_ders}"):
                    m_answers = {}
                    for i, q in enumerate(active_meslek_qs):
                        st.markdown(f"**{i+1}. {q.get('text')}**")
                        opts = q.get('options', ['A', 'B', 'C', 'D', 'E'])
                        m_answers[i] = st.radio("Cevap:", opts, key=f"m_q_{i}", horizontal=True, index=None, label_visibility="collapsed")
                        st.markdown("---")
                    
                    if st.form_submit_button("TESTİ BİTİR VE KONTROL ET"):
                        m_dogru = 0
                        st.markdown("### 📊 Sonuçlar")
                        for i, q in enumerate(active_meslek_qs):
                            if m_answers[i] == q.get('correct'):
                                m_dogru += 1
                            else:
                                st.markdown(f"❌ **Soru {i+1}:** Yanlış (Doğru: {q.get('correct')})")
                        
                        m_puan = m_dogru * 100
                        st.success(f"✅ Toplam Doğru: {m_dogru}")
                        st.info(f"💰 Kazanılan: {m_puan} ₺")
                        st.session_state.bank_balance += m_puan

    with tab_eglence:
        st.header("🎮 Simülasyonlar")
        game = st.selectbox("Oyun Seç:", ["Finans İmparatoru (Pasif Gelir)", "Asset Matrix (Blok)"])
        if game == "Finans İmparatoru (Pasif Gelir)": components.html(FINANCE_GAME_HTML, height=700)
        else: components.html(ASSET_MATRIX_HTML, height=750)

    with tab_lifesim:
        st.header("💼 LifeSim")
        final_code = load_lifesim_html()
        components.html(final_code, height=800, scrolling=True)

    with tab_premium:
        st.warning("Premium özellikler yapım aşamasında.")
