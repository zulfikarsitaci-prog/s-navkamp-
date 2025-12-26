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
    
    /* GEREKSİZ SİMGELERİ VE YAZILARI GİZLE */
    .stDeployButton, footer, header { display: none !important; }
    [data-testid="stToolbar"] { display: none !important; }
    .viewerBadge_container__1QSob { display: none !important; }
    
    .stApp { background-color: #f4f4f9; }
    h1, h2, h3, h4, .stTabs button { font-family: 'Cinzel', serif !important; font-weight: 700 !important; }
    p, div, span, button, input { font-family: 'Poppins', sans-serif !important; }
    
    /* Sekmeler */
    .stTabs [data-baseweb="tab-list"] { gap: 8px; background: white; padding: 10px; border-radius: 12px; box-shadow: 0 2px 10px rgba(0,0,0,0.05); }
    .stTabs [data-baseweb="tab"] { height: 45px; border-radius: 8px; border: none; font-weight: 600; font-size: 16px; }
    .stTabs [aria-selected="true"] { background-color: #2c3e50; color: #f1c40f !important; }
    
    /* Kartlar */
    .score-box { background: linear-gradient(135deg, #2c3e50 0%, #000000 100%); padding: 25px; border-radius: 15px; color: #f1c40f; text-align: center; border: 2px solid #f1c40f; box-shadow: 0 10px 30px rgba(0,0,0,0.2); }
    .big-num { font-family: 'Cinzel', serif; font-size: 48px; font-weight: 900; }
    
    /* Banka Veznesi */
    .bank-area { background-color: #e8f5e9; padding: 20px; border-radius: 12px; border: 2px dashed #27ae60; text-align: center; margin-top: 20px; }
    
    div.stButton > button { border-radius: 8px; height: 50px; font-weight: bold; border: 1px solid #ddd; transition: 0.3s; width: 100%; text-transform: uppercase; letter-spacing: 1px; }
    div.stButton > button:hover { border-color: #f1c40f; color: #f1c40f; background-color: #2c3e50; }
    
    /* HTML SAVE BUTTON */
    .html-save-btn { display: block; width: 100%; background-color: #27ae60; color: white !important; padding: 15px; text-align: center; border-radius: 12px; font-weight: 800; font-size: 18px; text-decoration: none; box-shadow: 0 4px 15px rgba(39, 174, 96, 0.4); margin-top: 10px; transition: transform 0.2s; border: 2px solid white; }
    .html-save-btn:hover { transform: scale(1.02); background-color: #219150; box-shadow: 0 6px 20px rgba(39, 174, 96, 0.6); }
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

# Şifre Çözücü
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

# Finans Oyunu: Gelişmiş Ekonomi
FINANCE_GAME_HTML = """
<!DOCTYPE html>
<html>
<head>
<style>
body { background: #1a1a2e; color: white; font-family: 'Poppins', sans-serif; padding: 10px; text-align: center; user-select:none; }
.top-bar { display: flex; justify-content: space-between; background: #16213e; padding: 15px; border-radius: 10px; border-bottom: 3px solid #f1c40f; margin-bottom: 20px; }
.money { font-size: 24px; font-weight: bold; color: #2ecc71; }
.grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 8px; }
.item { background: #0f3460; padding: 10px; border-radius: 8px; cursor: pointer; transition: 0.1s; border: 1px solid #16213e; position: relative; }
.item:active { transform: scale(0.95); }
.item.locked { opacity: 0.5; filter: grayscale(1); pointer-events: none; }
.name { font-weight: bold; color: #f1c40f; font-size: 14px; }
.cost { color: #e74c3c; font-size: 11px; }
.count { position: absolute; top: 5px; right: 5px; background: #e94560; padding: 2px 6px; border-radius: 10px; font-size: 10px; font-weight: bold; }
.btn-save { background: #27ae60; color: white; border: none; padding: 12px; width: 100%; border-radius: 8px; font-weight: bold; font-size: 16px; cursor: pointer; margin-top: 20px; }
.code-display { background: white; color: #333; padding: 10px; border-radius: 10px; margin-top: 10px; font-family: monospace; font-size: 16px; border: 2px dashed #333; display: none; }
</style>
</head>
<body>
<div class="top-bar">
    <div>KASA: <span id="money" class="money">0</span> ₺</div>
    <div style="font-size:11px; color:#aaa;">GELİR: <span id="cps">0</span>/sn</div>
</div>

<div style="margin-bottom:15px;">
    <button onclick="clickCoin()" style="width:80px; height:80px; border-radius:50%; background:radial-gradient(circle, #f1c40f 0%, #f39c12 100%); border:4px solid #fff; font-size:30px; cursor:pointer; box-shadow:0 0 15px rgba(241,196,15,0.5);">👆</button>
</div>

<div class="grid" id="market"></div>

<button class="btn-save" onclick="generateCode()">🏦 BANKAYA TRANSFER KODU</button>
<div id="codeArea" class="code-display"><span id="codeVal" style="font-weight:bold; color:#d35400;"></span></div>
<p id="info" style="font-size:10px; color:#aaa; margin-top:5px; display:none;">Kodu kopyala ve uygulamadaki kutuya yapıştır.</p>

<script>
let money = 0;
// GELİŞMİŞ VE CİMRİ EKONOMİ
let assets = [
    {n: "Limonata", c: 50, i: 0.5, cnt: 0},
    {n: "Simit", c: 350, i: 2, cnt: 0},
    {n: "Kırtasiye", c: 1500, i: 8, cnt: 0},
    {n: "Okul Kantini", c: 7500, i: 35, cnt: 0},
    {n: "Servis Filosu", c: 35000, i: 150, cnt: 0},
    {n: "Yazılım Şirketi", c: 150000, i: 600, cnt: 0},
    {n: "Holding", c: 1000000, i: 4500, cnt: 0}
];

function updateUI() {
    document.getElementById('money').innerText = Math.floor(money).toLocaleString();
    let totalCps = assets.reduce((t, a) => t + (a.cnt * a.i), 0);
    document.getElementById('cps').innerText = totalCps.toFixed(1);
    
    let m = document.getElementById('market');
    m.innerHTML = "";
    assets.forEach((a, i) => {
        let cost = Math.floor(a.c * Math.pow(1.25, a.cnt)); // %25 Enflasyon
        let div = document.createElement('div');
        div.className = "item " + (money >= cost ? "" : "locked");
        div.onclick = () => buy(i);
        div.innerHTML = `
            <span class="count">${a.cnt}</span>
            <div class="name">${a.n}</div>
            <div class="cost">${cost.toLocaleString()} ₺</div>
            <div style="font-size:10px; color:#2ecc71;">+${a.i}/sn</div>
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
}, 100); // 100ms'de bir güncelleme (akıcı olması için)

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

# Matrix Oyunu: Block Blast (Tıklayıp Yerleştirme)
MATRIX_GAME_HTML = """
<!DOCTYPE html>
<html>
<head>
<style>
body { background: #000; color: white; display: flex; flex-direction: column; align-items: center; justify-content: center; height: 95vh; font-family: monospace; user-select: none; }
.board { display: grid; grid-template-columns: repeat(10, 25px); grid-template-rows: repeat(10, 25px); gap: 2px; border: 4px solid #333; padding: 5px; border-radius: 5px; }
.cell { width: 25px; height: 25px; background: #111; border-radius: 3px; cursor: pointer; transition: 0.1s; }
.cell:hover { border: 1px solid #555; }
.score-display { color: #FFD700; font-size: 24px; margin-bottom: 10px; font-weight: bold; }
.next-piece { margin-top: 15px; text-align: center; height: 60px; }
.btn { background: #8e44ad; color: white; border: none; padding: 10px 20px; font-size: 16px; font-weight: bold; border-radius: 5px; cursor: pointer; margin-top: 10px; }
.code-box { background: #fff; color: black; padding: 5px; margin-top: 5px; font-weight: bold; border: 2px dashed #8e44ad; display: none; font-size:14px; }
</style>
</head>
<body>
<div class="score-display">SKOR: <span id="score">0</span></div>
<div class="board" id="board"></div>
<div class="next-piece" id="nextPiece" style="color:#aaa; font-size:12px;">ŞEKİL: <span id="shapeName" style="color:white; font-weight:bold;"></span> (Tıkla Yerleştir)</div>

<button class="btn" onclick="getCode()">🏦 TRANSFER KODU</button>
<div id="codeDisplay" class="code-box"></div>

<script>
const BOARD_SIZE = 10;
let grid = Array(BOARD_SIZE).fill().map(() => Array(BOARD_SIZE).fill(0));
let score = 0;
// Renkler: Gold, Rose, Gümüş, Mor
const COLORS = ["#FFD700", "#B76E79", "#C0C0C0", "#800080"];

// Şekiller (Block Blast tarzı)
const SHAPES = [
    {n: "TEKLİ", m: [[1]]}, 
    {n: "İKİLİ", m: [[1, 1]]},
    {n: "DİK İKİ", m: [[1], [1]]},
    {n: "KÖŞE", m: [[1, 0], [1, 1]]},
    {n: "KARE", m: [[1, 1], [1, 1]]}
];
let currentShape = SHAPES[0];

function initBoard() {
    const boardDiv = document.getElementById("board");
    boardDiv.innerHTML = "";
    for(let r=0; r<BOARD_SIZE; r++) {
        for(let c=0; c<BOARD_SIZE; c++) {
            let cell = document.createElement("div");
            cell.className = "cell";
            cell.id = `c-${r}-${c}`;
            cell.onclick = () => placeShape(r, c);
            boardDiv.appendChild(cell);
        }
    }
    newShape();
}

function newShape() {
    currentShape = SHAPES[Math.floor(Math.random() * SHAPES.length)];
    document.getElementById("shapeName").innerText = currentShape.n;
}

function getColor() {
    return COLORS[Math.floor(score / 50) % COLORS.length];
}

function updateBoard() {
    for(let r=0; r<BOARD_SIZE; r++) {
        for(let c=0; c<BOARD_SIZE; c++) {
            let cell = document.getElementById(`c-${r}-${c}`);
            cell.style.background = grid[r][c] ? getColor() : "#111";
            cell.style.boxShadow = grid[r][c] ? "0 0 5px " + getColor() : "none";
        }
    }
    document.getElementById("score").innerText = score;
}

function placeShape(r, c) {
    let shape = currentShape.m;
    let h = shape.length;
    let w = shape[0].length;
    
    // Sığar mı kontrolü
    if (r + h > BOARD_SIZE || c + w > BOARD_SIZE) return;
    
    for(let i=0; i<h; i++) {
        for(let j=0; j<w; j++) {
            if(shape[i][j] && grid[r+i][c+j]) return; // Çakışma var
        }
    }
    
    // Yerleştir
    for(let i=0; i<h; i++) {
        for(let j=0; j<w; j++) {
            if(shape[i][j]) grid[r+i][c+j] = 1;
        }
    }
    
    score += 5; // Yerleştirme puanı
    checkLines();
    updateBoard();
    newShape();
}

function checkLines() {
    // Satır Kontrolü
    for(let r=0; r<BOARD_SIZE; r++) {
        if(grid[r].every(v => v === 1)) {
            grid[r].fill(0); // Satırı sil
            score += 20; // Patlatma puanı
        }
    }
    // Sütun Kontrolü
    for(let c=0; c<BOARD_SIZE; c++) {
        let full = true;
        for(let r=0; r<BOARD_SIZE; r++) if(grid[r][c] === 0) full = false;
        if(full) {
            for(let r=0; r<BOARD_SIZE; r++) grid[r][c] = 0; // Sütunu sil
            score += 20;
        }
    }
}

function getCode(){
    if(score < 5) { alert("En az 5 puan yap!"); return; }
    let secureVal = (score * 13).toString(16).toUpperCase();
    let code = "FNK-" + secureVal + "-BL";
    document.getElementById("codeDisplay").innerText = code;
    document.getElementById("codeDisplay").style.display = "block";
    
    // Reset
    score = 0; grid = Array(BOARD_SIZE).fill().map(() => Array(BOARD_SIZE).fill(0));
    updateBoard();
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
        st.markdown("<div style='text-align:center'><h1>🏛️ FİNANS KAMPÜSÜ</h1><p>Güvenli Giriş Sistemi</p></div>", unsafe_allow_html=True)
        with st.form("login"):
            ad = st.text_input("Ad Soyad")
            no = st.text_input("Okul No")
            if st.form_submit_button("GİRİŞ YAP", type="primary"):
                if ad and no:
                    key = f"{no}_{ad.strip()}"
                    st.session_state.user_info = {"name": ad, "no": no, "key": key}
                    st.session_state.logged_in = True
                    st.rerun()
                else: st.error("Bilgileri giriniz.")

# EKRAN 2: ANA PANEL
else:
    user = st.session_state.user_info
    user_key = user['key']
    current_score = get_player_score(user_key)
    
    # Yan Menü
    with st.sidebar:
        st.write(f"👤 **{user['name']}**")
        st.write(f"🎓 {user['no']}")
        st.markdown("---")
        
        # OTO KAYIT BUTONU
        safe_name = urllib.parse.quote(user['name'])
        safe_score = str(current_score)
        final_form_link = FORM_LINK_TASLAK.replace("AD_YOK", safe_name).replace("9999", safe_score)
        st.markdown(f"""<a href="{final_form_link}" target="_blank" class="html-save-btn">💾 LİSTEYE KAYDET</a>""", unsafe_allow_html=True)
        
        if st.button("ÇIKIŞ YAP"):
            st.session_state.logged_in = False
            st.rerun()

    # Sekmeler
    t1, t2, t3, t4 = st.tabs(["🏠 PROFİL", "📚 DERSLER", "🎮 OYUNLAR & BANKA", "🏆 SIRALAMA"])

    # TAB 1: PROFİL
    with t1:
        st.markdown(f"### Merhaba, {user['name'].upper()}")
        st.markdown(f"""
            <div class="score-box">
                <div style="font-size:14px; letter-spacing:2px; margin-bottom:10px;">TOPLAM VARLIK</div>
                <div class="big-num">{current_score} ₺</div>
            </div>
        """, unsafe_allow_html=True)
        st.info("Puanların yerel hafızada saklanıyor. Listede görünmek için yandaki 'LİSTEYE KAYDET' butonuna bas.")

    # TAB 2: DERSLER
    with t2:
        st.subheader("SORU ÇÖZÜM MERKEZİ")
        c1, c2 = st.columns(2)
        if c1.button("📘 TYT TESTİ (+20 Puan)"):
            update_player_score(user_key, 20, user['name'], user['no'])
            st.toast("Doğru! +20 Puan")
            time.sleep(0.5); st.rerun()
        if c2.button("💼 MESLEK TESTİ (+20 Puan)"):
            update_player_score(user_key, 20, user['name'], user['no'])
            st.toast("Doğru! +20 Puan")
            time.sleep(0.5); st.rerun()

    # TAB 3: OYUNLAR & BANKA
    with t3:
        col_game, col_bank = st.columns([2, 1])
        
        with col_game:
            st.subheader("🎮 OYUN ALANI")
            oyun = st.selectbox("Oyun Seç:", ["Finans İmparatoru", "Asset Matrix (Block Blast)"])
            
            if oyun == "Finans İmparatoru":
                components.html(FINANCE_GAME_HTML, height=600)
            else:
                components.html(MATRIX_GAME_HTML, height=600)
        
        with col_bank:
            st.markdown("<div style='height: 50px;'></div>", unsafe_allow_html=True)
            st.markdown("""
                <div class="bank-area">
                    <h3 style="color:#27ae60;">🏦 BANKA VEZNESİ</h3>
                    <p style="font-size:12px;">Oyundan aldığın 'FNK' kodunu gir.</p>
                </div>
            """, unsafe_allow_html=True)
            
            transfer_code = st.text_input("Transfer Kodu:", placeholder="Örn: FNK-1A4-99")
            
            if st.button("PARA YATIR", type="primary"):
                amount = decode_transfer_code(transfer_code)
                if amount:
                    update_player_score(user_key, amount, user['name'], user['no'])
                    st.success(f"✅ Hesabına {amount} ₺ yatırıldı.")
                    st.balloons()
                    time.sleep(2)
                    st.rerun()
                else:
                    st.error("⛔ GEÇERSİZ KOD!")

    # TAB 4: SIRALAMA
    with t4:
        st.subheader("🏆 LİDERLİK TABLOSU")
        db = load_db()
        data = [{"Öğrenci": v['name'], "Puan": v['score']} for k,v in db.items()]
        if data:
            df = pd.DataFrame(data).sort_values("Puan", ascending=False).reset_index(drop=True)
            df.index += 1
            st.dataframe(df, use_container_width=True)
        else:
            st.write("Henüz veri yok.")
