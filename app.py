import streamlit as st
import streamlit.components.v1 as components
import json
import os
import pandas as pd
import time

# --- 1. AYARLAR & CSS ---
st.set_page_config(page_title="Finans Kampüsü", page_icon="🏛️", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;700;900&family=Poppins:wght@300;400;600&display=swap');
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
    </style>
""", unsafe_allow_html=True)

# --- 2. GÜVENLİ VERİTABANI & ŞİFRELEME ---
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

# --- 3. ŞİFRE ÇÖZÜCÜ (GÜVENLİK MERKEZİ) ---
def decode_transfer_code(code):
    """
    Şifre Formatı: FNK-[HEX_PUAN]-[CHECKSUM]
    Örn: 100 Puan -> 100 * 13 = 1300 -> Hex(514)
    Kod: FNK-514-X9
    """
    try:
        parts = code.split('-')
        if len(parts) != 3 or parts[0] != "FNK":
            return None
        
        hex_val = parts[1]
        score_mult = int(hex_val, 16) # Hex'ten onluğa çevir
        actual_score = score_mult / 13 # Şifreleme katsayısına böl
        
        if actual_score.is_integer():
            return int(actual_score)
        else:
            return None
    except:
        return None

# --- 4. SESSION STATE ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'user_info' not in st.session_state: st.session_state.user_info = {}

# --- 5. OYUN KODLARI (JS ŞİFRELEME DAHİL) ---

FINANCE_GAME_HTML = """
<!DOCTYPE html>
<html>
<head>
<style>
body { background: #1a1a2e; color: white; font-family: 'Poppins', sans-serif; padding: 20px; text-align: center; }
.top-bar { display: flex; justify-content: space-between; background: #16213e; padding: 15px; border-radius: 10px; border-bottom: 3px solid #f1c40f; margin-bottom: 20px; }
.money { font-size: 24px; font-weight: bold; color: #2ecc71; }
.grid { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 10px; }
.item { background: #0f3460; padding: 10px; border-radius: 8px; cursor: pointer; transition: 0.2s; border: 1px solid #16213e; }
.item:hover { border-color: #f1c40f; transform: translateY(-3px); }
.item.locked { opacity: 0.4; pointer-events: none; }
.name { font-weight: bold; color: #f1c40f; }
.cost { color: #e74c3c; font-size: 12px; }
.btn-save { background: #27ae60; color: white; border: none; padding: 15px; width: 100%; border-radius: 8px; font-weight: bold; font-size: 16px; cursor: pointer; margin-top: 20px; }
.code-display { background: white; color: #333; padding: 15px; border-radius: 10px; margin-top: 10px; font-family: monospace; font-size: 18px; border: 2px dashed #333; display: none; }
</style>
</head>
<body>
<div class="top-bar">
    <div>KASA: <span id="money" class="money">0</span> ₺</div>
    <div style="font-size:12px; color:#aaa;">Her saniye gelir</div>
</div>

<div style="margin-bottom:20px;">
    <button onclick="clickCoin()" style="width:80px; height:80px; border-radius:50%; background:#f1c40f; border:none; font-size:30px; cursor:pointer; box-shadow:0 0 15px #f1c40f;">👆</button>
</div>

<div class="grid" id="market"></div>

<button class="btn-save" onclick="generateCode()">🏦 BANKAYA TRANSFER KODU AL</button>
<div id="codeArea" class="code-display">KODUNUZ: <span id="codeVal" style="font-weight:bold; color:#d35400;"></span></div>
<p id="info" style="font-size:12px; color:#aaa; margin-top:5px; display:none;">Bu kodu kopyala ve aşağıdaki 'Banka Veznesi' kutusuna yapıştır.</p>

<script>
let money = 0;
// Cimri Mod
let assets = [
    {n: "Limon", c: 50, i: 1, cnt: 0},
    {n: "Simit", c: 250, i: 4, cnt: 0},
    {n: "Çay", c: 1000, i: 15, cnt: 0},
    {n: "Tost", c: 5000, i: 60, cnt: 0},
    {n: "Döner", c: 20000, i: 200, cnt: 0},
    {n: "AVM", c: 1000000, i: 5000, cnt: 0}
];

function updateUI() {
    document.getElementById('money').innerText = Math.floor(money).toLocaleString();
    let m = document.getElementById('market');
    m.innerHTML = "";
    assets.forEach((a, i) => {
        let cost = Math.floor(a.c * Math.pow(1.2, a.cnt));
        let div = document.createElement('div');
        div.className = "item " + (money >= cost ? "" : "locked");
        div.onclick = () => buy(i);
        div.innerHTML = `<div class="name">${a.n} (${a.cnt})</div><div class="cost">${cost.toLocaleString()} ₺</div><div style="font-size:10px; color:#2ecc71;">+${a.i}/sn</div>`;
        m.appendChild(div);
    });
}

function clickCoin() { money += 1; updateUI(); }

function buy(i) {
    let a = assets[i];
    let cost = Math.floor(a.c * Math.pow(1.2, a.cnt));
    if(money >= cost) { money -= cost; a.cnt++; updateUI(); }
}

setInterval(() => {
    let income = assets.reduce((t, a) => t + (a.cnt * a.i), 0);
    if(income > 0) { money += income; updateUI(); }
}, 1000);

// ŞİFRELEME ALGORİTMASI (GÜVENLİK)
function generateCode() {
    if(money < 1) { alert("Aktaracak paranız yok!"); return; }
    let score = Math.floor(money);
    
    // Basit ama etkili şifreleme: Puan * 13 -> Hex Çevir
    let secureVal = (score * 13).toString(16).toUpperCase();
    let randomPart = Math.floor(Math.random() * 90 + 10); // 2 basamaklı rastgele
    let finalCode = "FNK-" + secureVal + "-" + randomPart;
    
    document.getElementById('codeVal').innerText = finalCode;
    document.getElementById('codeArea').style.display = "block";
    document.getElementById('info').style.display = "block";
    
    // Parayı sıfırla (Kod alındı artık)
    money = 0;
    assets.forEach(a => a.cnt = 0); // Oyunu sıfırla
    updateUI();
}
updateUI();
</script>
</body>
</html>
"""

MATRIX_GAME_HTML = """
<!DOCTYPE html>
<html>
<head>
<style>
body { background: #000; color: white; display: flex; flex-direction: column; align-items: center; justify-content: center; height: 95vh; font-family: monospace; }
canvas { border: 4px solid #333; background: #111; }
.btn { background: #8e44ad; color: white; border: none; padding: 10px 20px; font-size: 16px; font-weight: bold; border-radius: 5px; cursor: pointer; margin-top: 10px; }
.code-box { background: #fff; color: black; padding: 10px; margin-top: 10px; font-weight: bold; border: 2px dashed #8e44ad; display: none; }
</style>
</head>
<body>
<div style="color:#f1c40f; font-size:20px; margin-bottom:5px;">PUAN: <span id="score">0</span></div>
<canvas id="tetris" width="240" height="400"></canvas>
<button class="btn" onclick="getCode()">🏦 TRANSFER KODU AL</button>
<div id="codeDisplay" class="code-box"></div>

<script>
const cvs = document.getElementById("tetris");
const ctx = cvs.getContext("2d");
const ROW = 20; const COL = 12; const SQ = 20;
const VACANT = "#111";

let board = [];
for(r = 0; r < ROW; r++){
    board[r] = [];
    for(c = 0; c < COL; c++){
        board[r][c] = VACANT;
    }
}

function drawSquare(x,y,color){
    ctx.fillStyle = color;
    ctx.fillRect(x*SQ,y*SQ,SQ,SQ);
    ctx.strokeStyle = "#000";
    ctx.strokeRect(x*SQ,y*SQ,SQ,SQ);
}

function drawBoard(){
    for(r = 0; r < ROW; r++){
        for(c = 0; c < COL; c++){
            drawSquare(c,r,board[r][c]);
        }
    }
}
drawBoard();

let score = 0;
// BASİT MANTIK: Tıklayınca rastgele blok koyar (Cimri Puan)
cvs.addEventListener("click", function(evt){
    let rect = cvs.getBoundingClientRect();
    let x = Math.floor((evt.clientX - rect.left)/SQ);
    let y = Math.floor((evt.clientY - rect.top)/SQ);
    if(board[y][x] == VACANT){
        // Renk döngüsü: 50 puanda bir
        let colors = ["gold", "pink", "silver", "purple"];
        let color = colors[Math.floor(score/50) % 4];
        board[y][x] = color;
        score += 2; // Çok cimri
        document.getElementById("score").innerText = score;
        drawBoard();
    }
});

function getCode(){
    if(score < 2) { alert("En az 2 puan yap!"); return; }
    
    // ŞİFRELEME: Puan * 13 -> Hex
    let secureVal = (score * 13).toString(16).toUpperCase();
    let code = "FNK-" + secureVal + "-MX";
    
    document.getElementById("codeDisplay").innerText = code;
    document.getElementById("codeDisplay").style.display = "block";
    
    // Sıfırla
    score = 0;
    document.getElementById("score").innerText = score;
    for(r=0; r<ROW; r++) for(c=0; c<COL; c++) board[r][c] = VACANT;
    drawBoard();
}
</script>
</body>
</html>
"""

# --- 6. UYGULAMA AKIŞI ---

# EKRAN 1: GİRİŞ
if not st.session_state.logged_in:
    c1, c2, c3 = st.columns([1, 1, 1])
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
        st.info("Bilgilerin yerel veritabanında güvenle saklanıyor.")

    # TAB 2: DERSLER
    with t2:
        st.subheader("SORU ÇÖZÜM MERKEZİ")
        c1, c2 = st.columns(2)
        if c1.button("📘 TYT TESTİ (+10 Puan)"):
            update_player_score(user_key, 10, user['name'], user['no'])
            st.toast("Doğru! +10 Puan")
            time.sleep(0.5); st.rerun()
        if c2.button("💼 MESLEK TESTİ (+10 Puan)"):
            update_player_score(user_key, 10, user['name'], user['no'])
            st.toast("Doğru! +10 Puan")
            time.sleep(0.5); st.rerun()

    # TAB 3: OYUNLAR & BANKA (GÜVENLİ TRANSFER)
    with t3:
        col_game, col_bank = st.columns([2, 1])
        
        with col_game:
            st.subheader("🎮 OYUN ALANI")
            oyun = st.selectbox("Oyun Seç:", ["Finans İmparatoru", "Asset Matrix"])
            
            if oyun == "Finans İmparatoru":
                components.html(FINANCE_GAME_HTML, height=600)
            else:
                components.html(MATRIX_GAME_HTML, height=500)
        
        with col_bank:
            st.markdown("<div style='height: 50px;'></div>", unsafe_allow_html=True) # Boşluk
            st.markdown("""
                <div class="bank-area">
                    <h3 style="color:#27ae60;">🏦 BANKA VEZNESİ</h3>
                    <p style="font-size:12px;">Oyundan aldığın 'FNK' ile başlayan kodu buraya gir.</p>
                </div>
            """, unsafe_allow_html=True)
            
            # TRANSFER İŞLEMİ
            transfer_code = st.text_input("Transfer Kodu:", placeholder="Örn: FNK-1A4-99")
            
            if st.button("PARA YATIR", type="primary"):
                amount = decode_transfer_code(transfer_code)
                
                if amount:
                    update_player_score(user_key, amount, user['name'], user['no'])
                    st.success(f"✅ ONAYLANDI! Hesabına {amount} ₺ yatırıldı.")
                    st.balloons()
                    time.sleep(2)
                    st.rerun()
                else:
                    st.error("⛔ GEÇERSİZ VEYA HATALI KOD!")

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
