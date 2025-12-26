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
# 🔗 GITHUB AYARLARI (BURAYI DÜZENLE)
# ==========================================
# Buraya repo ana linkini yazıyoruz. Kod diğer dosyaları (json, pdf) otomatik bulacak.
GITHUB_BASE_URL = "https://raw.githubusercontent.com/zulfikarsitaci-prog/s-navkamp-/refs/heads/main/"

# Otomatik oluşan linkler
URL_LIFESIM = f"{GITHUB_BASE_URL}/lifesim_data.json"
URL_TYT = f"{GITHUB_BASE_URL}/tyt_data.json"
URL_KONULAR = f"{GITHUB_BASE_URL}/konular.json"
URL_PDF = f"{GITHUB_BASE_URL}/tytson8.pdf"

# ==========================================
# 🎮 OYUN 1: FİNANS İMPARATORU (DÜZELTİLMİŞ & RESPONSIVE)
# ==========================================
FINANCE_GAME_HTML = """
<!DOCTYPE html>
<html lang="tr">
<head>
<meta charset="UTF-8">
<style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;700;900&display=swap');
    body { background-color: #0f172a; color: #e2e8f0; font-family: 'Montserrat', sans-serif; user-select: none; padding: 10px; text-align: center; margin: 0; }
    
    /* Container */
    .container { width: 100%; max-width: 100%; box-sizing: border-box; overflow-x: hidden; }

    /* Dashboard */
    .dashboard { display: flex; flex-wrap: wrap; justify-content: space-between; background: linear-gradient(145deg, #1e293b, #0f172a); padding: 15px; border-radius: 12px; border: 1px solid #334155; margin-bottom: 20px; gap: 10px; }
    .stat-box { text-align: left; flex: 1; min-width: 120px; }
    .stat-label { font-size: 9px; color: #94a3b8; letter-spacing: 1px; }
    .money-val { font-size: 22px; font-weight: 900; color: #34d399; }
    .income-val { font-size: 16px; font-weight: 700; color: #facc15; }

    /* Clicker Button */
    .clicker-btn {
        background: radial-gradient(circle, #3b82f6 0%, #1d4ed8 100%);
        border: 4px solid #1e3a8a; border-radius: 50%; 
        width: 120px; height: 120px;
        font-size: 35px; cursor: pointer; 
        box-shadow: 0 0 20px rgba(59, 130, 246, 0.4);
        margin: 0 auto 20px auto;
        display: flex; align-items: center; justify-content: center;
        transition: transform 0.1s;
    }
    .clicker-btn:active { transform: scale(0.95); }

    /* Market Grid (Responsive) */
    .asset-grid { 
        display: grid; 
        grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); 
        gap: 8px; 
        margin-bottom: 20px; 
    }
    
    .asset-card {
        background: #1e293b; padding: 10px; border-radius: 8px; border: 1px solid #334155;
        cursor: pointer; position: relative; transition: 0.2s; text-align: left;
    }
    .asset-card:hover { border-color: #facc15; background: #253347; }
    .asset-card.locked { opacity: 0.5; filter: grayscale(1); pointer-events: none; }
    
    .asset-name { font-weight: bold; font-size: 11px; color: #fff; display: block; margin-bottom: 2px;}
    .asset-cost { font-size: 10px; color: #f87171; font-weight: bold; }
    .asset-gain { font-size: 9px; color: #34d399; }
    .asset-count { position: absolute; top: 8px; right: 8px; background: #facc15; color: #000; font-weight: bold; font-size: 9px; padding: 1px 5px; border-radius: 4px; }

    /* Bank Section */
    .bank-area { background: #064e3b; border: 1px dashed #34d399; padding: 10px; border-radius: 8px; margin-top: 10px; }
    .bank-btn { background: #34d399; color: #064e3b; border: none; padding: 8px 15px; font-weight: bold; border-radius: 5px; cursor: pointer; width: 100%; font-size: 12px; }
    .code-display { background: #fff; color: #000; padding: 8px; margin-top: 5px; font-family: monospace; font-weight: bold; display: none; font-size: 12px; word-break: break-all; }
</style>
</head>
<body>
<div class="container">
    <div class="dashboard">
        <div class="stat-box">
            <div class="stat-label">NAKİT VARLIK</div>
            <div id="money" class="money-val">0 ₺</div>
        </div>
        <div class="stat-box" style="text-align:right;">
            <div class="stat-label">PASİF GELİR</div>
            <div id="cps" class="income-val">0.0 /sn</div>
        </div>
    </div>

    <div class="clicker-btn" onclick="manualWork()">👆</div>

    <div style="text-align:left; color:#facc15; font-size:12px; font-weight:bold; margin-bottom:5px;">PORTFÖY</div>
    <div class="asset-grid" id="market"></div>

    <div class="bank-area">
        <h4 style="margin:0 0 5px 0; color:#34d399; font-size:12px;">BANKA TRANSFERİ</h4>
        <button class="bank-btn" onclick="generateCode()">KAZANCI AKTAR & SIFIRLA</button>
        <div id="transferCode" class="code-display"></div>
    </div>
</div>

<script>
    // EKONOMİ AYARLARI
    let money = 0;
    const assets = [
        { name: "Limonata", cost: 150, gain: 0.2, count: 0 },
        { name: "Simit Arabası", cost: 900, gain: 1.5, count: 0 },
        { name: "Kantin", cost: 4500, gain: 8.0, count: 0 },
        { name: "Kırtasiye", cost: 18000, gain: 25.0, count: 0 },
        { name: "Yazılım Ofisi", cost: 75000, gain: 90.0, count: 0 },
        { name: "Holding", cost: 500000, gain: 500.0, count: 0 }
    ];

    function updateUI() {
        document.getElementById('money').innerText = Math.floor(money).toLocaleString() + ' ₺';
        let totalCps = assets.reduce((t, a) => t + (a.count * a.gain), 0);
        document.getElementById('cps').innerText = totalCps.toFixed(1) + ' /sn';

        const market = document.getElementById('market');
        market.innerHTML = '';

        assets.forEach((asset, index) => {
            let currentCost = Math.floor(asset.cost * Math.pow(1.2, asset.count));
            let div = document.createElement('div');
            div.className = 'asset-card ' + (money >= currentCost ? '' : 'locked');
            div.onclick = () => buyAsset(index);
            div.innerHTML = `
                <div class="asset-count">${asset.count}</div>
                <div class="asset-name">${asset.name}</div>
                <div class="asset-cost">${currentCost.toLocaleString()} ₺</div>
                <div class="asset-gain">+${asset.gain}/sn</div>
            `;
            market.appendChild(div);
        });
    }

    function manualWork() { money += 1; updateUI(); }

    function buyAsset(index) {
        let asset = assets[index];
        let currentCost = Math.floor(asset.cost * Math.pow(1.2, asset.count));
        if (money >= currentCost) { money -= currentCost; asset.count++; updateUI(); }
    }

    function generateCode() {
        if (money < 50) { alert("En az 50 ₺ birikmeli."); return; }
        let val = Math.floor(money);
        let hex = (val * 13).toString(16).toUpperCase();
        let rnd = Math.floor(Math.random() * 100);
        let code = `FNK-${hex}-${rnd}`;
        let box = document.getElementById('transferCode');
        box.innerText = code; box.style.display = 'block';
        money = 0; updateUI();
    }

    setInterval(() => {
        let totalCps = assets.reduce((t, a) => t + (a.count * a.gain), 0);
        if (totalCps > 0) { money += totalCps; updateUI(); }
    }, 1000);

    updateUI();
</script>
</body>
</html>
"""

# ==========================================
# 🎮 OYUN 2: ASSET MATRIX (FIXED)
# ==========================================
ASSET_MATRIX_HTML = """
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <title>Asset Matrix</title>
    <style>
        body { margin: 0; background-color: #050505; color: white; font-family: monospace; display: flex; flex-direction: column; align-items: center; touch-action: none; padding: 10px; }
        canvas { background: #111; border: 2px solid #333; box-shadow: 0 0 20px rgba(0,255,255,0.1); display: block; margin-bottom: 10px; }
        .btn { background: linear-gradient(45deg, #06b6d4, #3b82f6); border: none; padding: 10px 20px; color: white; font-weight: bold; border-radius: 8px; cursor: pointer; margin-top: 5px; }
        .code-box { margin-top: 10px; background: white; color: black; padding: 10px; font-weight: bold; display: none; text-align: center; width: 100%; word-break: break-all; }
        .score-board { font-size: 20px; font-weight: bold; color: #facc15; margin-bottom: 10px; }
    </style>
</head>
<body>
    <div class="score-board">SKOR: $<span id="score">0</span></div>
    <canvas id="gameCanvas"></canvas>
    <button class="btn" onclick="getTransferCode()">BANKAYA AKTAR</button>
    <div id="codeArea" class="code-box"></div>

    <script>
        const canvas = document.getElementById('gameCanvas');
        const ctx = canvas.getContext('2d');
        const GRID_SIZE = 10;
        let CELL_SIZE = 30;
        let grid = [], pieces = [], dragging = null, score = 0;

        function resize() {
            const maxWidth = window.innerWidth - 20;
            const size = Math.min(maxWidth, 400); 
            CELL_SIZE = Math.floor(size / (GRID_SIZE + 2));
            canvas.width = CELL_SIZE * GRID_SIZE + 20;
            canvas.height = CELL_SIZE * GRID_SIZE + 120;
            if(pieces.length > 0) draw();
        }

        const SHAPES = [[[1]], [[1,1]], [[1],[1]], [[1,1],[1,1]], [[1,1,1]], [[1],[1],[1]], [[0,1,0],[1,1,1]]];

        function init() {
            grid = Array(GRID_SIZE).fill(0).map(()=>Array(GRID_SIZE).fill(0));
            score = 0; spawnPieces(); draw();
        }

        function spawnPieces() {
            pieces = [];
            for(let i=0; i<3; i++) {
                const m = SHAPES[Math.floor(Math.random()*SHAPES.length)];
                const w = m[0].length * CELL_SIZE;
                const x = 10 + i * (canvas.width/3) + (canvas.width/3 - w)/2;
                const y = CELL_SIZE * GRID_SIZE + 30;
                pieces.push({ m, x, y, bx: x, by: y, w, h: m.length*CELL_SIZE });
            }
        }

        function draw() {
            ctx.fillStyle = "#080808"; ctx.fillRect(0,0,canvas.width,canvas.height);
            ctx.strokeStyle = "#222"; ctx.lineWidth = 1; ctx.beginPath();
            for(let i=0; i<=GRID_SIZE; i++) {
                ctx.moveTo(10, 10+i*CELL_SIZE); ctx.lineTo(10+GRID_SIZE*CELL_SIZE, 10+i*CELL_SIZE);
                ctx.moveTo(10+i*CELL_SIZE, 10); ctx.lineTo(10+i*CELL_SIZE, 10+GRID_SIZE*CELL_SIZE);
            }
            ctx.stroke();
            for(let r=0; r<GRID_SIZE; r++) for(let c=0; c<GRID_SIZE; c++) 
                if(grid[r][c]) { ctx.fillStyle = "#facc15"; ctx.fillRect(10+c*CELL_SIZE+1, 10+r*CELL_SIZE+1, CELL_SIZE-2, CELL_SIZE-2); }
            pieces.forEach(p => {
                ctx.fillStyle = p === dragging ? "rgba(6, 182, 212, 0.8)" : "#06b6d4";
                p.m.forEach((row, r) => row.forEach((val, c) => {
                    if(val) ctx.fillRect(p.x + c*CELL_SIZE, p.y + r*CELL_SIZE, CELL_SIZE-2, CELL_SIZE-2);
                }));
            });
            document.getElementById('score').innerText = score;
        }

        function getPos(e) {
            const r = canvas.getBoundingClientRect();
            const x = e.changedTouches ? e.changedTouches[0].clientX : e.clientX;
            const y = e.changedTouches ? e.changedTouches[0].clientY : e.clientY;
            return { x: (x-r.left)*(canvas.width/r.width), y: (y-r.top)*(canvas.height/r.height) };
        }
        function start(e) {
            e.preventDefault(); const p_ = getPos(e);
            for(let i=pieces.length-1; i>=0; i--) {
                const p = pieces[i];
                if(p_.x>=p.x-10 && p_.x<=p.x+p.w+10 && p_.y>=p.y-10 && p_.y<=p.y+p.h+10) {
                    dragging = p; dragging.dx = p_.x - p.x; dragging.dy = p_.y - p.y; draw(); return;
                }
            }
        }
        function move(e) {
            if(!dragging) return; e.preventDefault(); const p = getPos(e);
            dragging.x = p.x - dragging.dx; dragging.y = p.y - dragging.dy; draw();
        }
        function end(e) {
            if(!dragging) return; e.preventDefault();
            const gx = Math.round((dragging.x-10)/CELL_SIZE);
            const gy = Math.round((dragging.y-10)/CELL_SIZE);
            if(canPlace(dragging.m, gx, gy)) {
                place(dragging.m, gx, gy); pieces = pieces.filter(p => p !== dragging);
                if(pieces.length === 0) spawnPieces();
            } else { dragging.x = dragging.bx; dragging.y = dragging.by; }
            dragging = null; draw();
        }
        function canPlace(m, gx, gy) {
            return m.every((row, r) => row.every((val, c) => {
                if(!val) return true;
                const tx=gx+c, ty=gy+r;
                return tx>=0 && tx<GRID_SIZE && ty>=0 && ty<GRID_SIZE && !grid[ty][tx];
            }));
        }
        function place(m, gx, gy) {
            m.forEach((row, r) => row.forEach((val, c) => { if(val) grid[gy+r][gx+c]=1; }));
            score += 10; 
            let rows=[], cols=[];
            for(let r=0; r<GRID_SIZE; r++) if(grid[r].every(v=>v)) rows.push(r);
            for(let c=0; c<GRID_SIZE; c++) if(grid.map(r=>r[c]).every(v=>v)) cols.push(c);
            if(rows.length+cols.length > 0) {
                rows.forEach(r => grid[r].fill(0)); cols.forEach(c => grid.forEach(r => r[c]=0));
                score += (rows.length+cols.length) * 50;
            }
        }
        function getTransferCode() {
            if(score < 50) { alert("En az 50 Puan gerekli."); return; }
            let val = score; let hex = (val * 13).toString(16).toUpperCase(); let code = `FNK-${hex}-MTX`;
            document.getElementById('codeArea').innerText = code; document.getElementById('codeArea').style.display = 'block';
            score = 0; init();
        }
        canvas.addEventListener('mousedown', start); canvas.addEventListener('touchstart', start, {passive:false});
        canvas.addEventListener('mousemove', move); canvas.addEventListener('touchmove', move, {passive:false});
        canvas.addEventListener('mouseup', end); canvas.addEventListener('touchend', end, {passive:false});
        window.addEventListener('resize', resize); window.onload = () => { resize(); init(); };
    </script>
</body>
</html>
"""

# ==========================================
# 3. YARDIMCI FONKSİYONLAR
# ==========================================
@st.cache_data(ttl=300)
def fetch_json_data(url):
    """GitHub'dan veya yerelden JSON çeker."""
    if os.path.exists(url.split('/')[-1]): # Yerel kontrolü
        try:
            with open(url.split('/')[-1], "r", encoding="utf-8") as f:
                return json.load(f)
        except: pass
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return json.loads(response.text)
    except: pass
    return []

def load_lifesim_html():
    try:
        with open("game.html", "r", encoding="utf-8") as f:
            html = f.read()
        
        # Veriyi Çek
        data = fetch_json_data(URL_LIFESIM)
        json_str = json.dumps(data)
        
        return html.replace("// PYTHON_DATA_HERE", f"var scenarios = {json_str};")
    except FileNotFoundError:
        return "<h3 style='color:red'>Hata: game.html dosyası bulunamadı!</h3>"

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
    .question-card { background: white; padding: 20px; border-radius: 10px; border-left: 5px solid #3498db; box-shadow: 0 2px 10px rgba(0,0,0,0.05); margin-bottom: 20px; }
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
                else: st.error("Lütfen tüm alanları doldurunuz.")

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
            st.markdown('<div class="bank-box"><h3>🏦 MERKEZ BANKASI VEZNESİ</h3><p>Oyunlardan aldığınız transfer kodlarını buraya girin.</p></div>', unsafe_allow_html=True)
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
            data = [
                {'Sıra': 1, 'Ad Soyad': 'Ayşe Y.', 'Puan': 50000},
                {'Sıra': 2, 'Ad Soyad': 'Mehmet K.', 'Puan': 42000},
                {'Sıra': 3, 'Ad Soyad': st.session_state.user_name + " (SİZ)", 'Puan': st.session_state.bank_balance}
            ]
            df = pd.DataFrame(data).sort_values("Puan", ascending=False).reset_index(drop=True)
            st.table(df)

    with tab_profil:
        st.info(f"Öğrenci: {st.session_state.user_name} ({st.session_state.user_no})")
        if st.button("Çıkış Yap"): st.session_state.logged_in = False; st.rerun()

    with tab_soru:
        st.header("📚 Soru Çözüm Merkezi")
        st.markdown(f"""
        <a href="{URL_PDF}" target="_blank" style="text-decoration:none;">
            <div style="background:#e74c3c; color:white; padding:15px; border-radius:10px; text-align:center; margin-bottom:20px; font-weight:bold;">
                📥 TYT KONU ÖZETİNİ İNDİR (PDF)
            </div>
        </a>
        """, unsafe_allow_html=True)
        
        questions = fetch_json_data(URL_TYT)
        if not questions: st.warning("Soru yüklenemedi.")
        else:
            categories = list(set([q.get('category', 'Genel') for q in questions]))
            selected_cat = st.selectbox("Kategori Seç:", categories)
            filtered_qs = [q for q in questions if q.get('category') == selected_cat]
            for i, q in enumerate(filtered_qs):
                with st.container():
                    st.markdown(f"""<div class="question-card"><h4>Soru {i+1}</h4><p>{q.get('text')}</p></div>""", unsafe_allow_html=True)
                    options = q.get('options', [])
                    answer = st.radio(f"Cevap {i+1}:", options, key=f"q_{i}")
                    if st.button(f"Kontrol {i+1}", key=f"btn_{i}"):
                        if answer == q.get('correct'):
                            st.success("Doğru! +100 Puan")
                            st.session_state.bank_balance += 100
                        else: st.error("Yanlış.")

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
