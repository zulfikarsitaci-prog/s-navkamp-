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

# 2. GITHUB AYARLARI (LifeSim İçin)
# Buraya kendi raw linkini koymalısın yoksa boş çalışır.
GITHUB_JSON_URL = "https://raw.githubusercontent.com/KULLANICI_ADI/REPO_ADI/main/lifesim_data.json"

# ==========================================
# 🔐 TRANSFER KODU SİSTEMİ (Backend)
# ==========================================
def decode_code(code):
    """
    Oyunlardan gelen şifreli kodu çözer.
    Format: FNK-{HEX_DEGER}-{RASTGELE}
    Hex Değer = (Gerçek Tutar * 13)
    """
    try:
        parts = code.split('-')
        if len(parts) != 3 or parts[0] != "FNK":
            return None
        
        hex_val = parts[1]
        # Hex'i sayıya çevir
        num_val = int(hex_val, 16)
        
        # Güvenlik katsayısına (13) böl
        actual_amount = num_val / 13
        
        if actual_amount.is_integer():
            return int(actual_amount)
        else:
            return None
    except:
        return None

# ==========================================
# 🎮 GELİŞMİŞ FİNANS İMPARATORU (HTML)
# ==========================================
FINANCE_GAME_HTML = """
<!DOCTYPE html>
<html>
<head>
<style>
 body { background: #f8f9fa; color: #2c3e50; font-family: 'Segoe UI', sans-serif; user-select: none; padding: 10px; }
 .container { max-width: 600px; margin: 0 auto; }
 
 /* Üst Bilgi Kartı */
 .header-card { background: #fff; padding: 15px; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); border-bottom: 3px solid #D84315; display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
 .money-area { font-size: 24px; font-weight: 800; color: #27ae60; }
 .income-area { font-size: 14px; color: #7f8c8d; font-weight: 600; }
 
 /* Tıklama Alanı */
 .clicker-btn { width: 100%; background: linear-gradient(135deg, #2c3e50, #34495e); color: white; padding: 20px; border-radius: 12px; font-size: 18px; font-weight: bold; border: none; cursor: pointer; box-shadow: 0 4px 0 #1a252f; transition: transform 0.1s; margin-bottom: 20px; }
 .clicker-btn:active { transform: translateY(4px); box-shadow: none; }

 /* Market Grid */
 .market-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
 .asset-card { background: #fff; padding: 10px; border-radius: 8px; border: 1px solid #eee; cursor: pointer; transition: 0.2s; position: relative; }
 .asset-card:hover { border-color: #D84315; transform: translateY(-2px); }
 .asset-card.locked { opacity: 0.5; filter: grayscale(1); pointer-events: none; }
 .asset-name { font-weight: bold; font-size: 14px; color: #D84315; }
 .asset-cost { font-size: 12px; color: #e74c3c; font-weight: bold; }
 .asset-income { font-size: 11px; color: #27ae60; }
 .asset-count { position: absolute; top: 5px; right: 5px; background: #2c3e50; color: white; padding: 2px 6px; border-radius: 4px; font-size: 10px; }

 /* Banka Transfer */
 .bank-section { margin-top: 30px; background: #e8f5e9; padding: 15px; border-radius: 10px; border: 1px dashed #27ae60; text-align: center; }
 .transfer-btn { background: #27ae60; color: white; border: none; padding: 10px 20px; border-radius: 6px; font-weight: bold; cursor: pointer; }
 .code-display { margin-top: 10px; font-family: monospace; font-size: 18px; color: #333; background: #fff; padding: 5px; border-radius: 4px; display: none; border: 1px solid #ccc; }
</style>
</head>
<body>
<div class="container">
    <div class="header-card">
        <div>
            <div class="money-area"><span id="money">0</span> ₺</div>
            <div style="font-size:10px; color:#aaa;">NAKİT VARLIK</div>
        </div>
        <div style="text-align:right;">
            <div class="income-area">+<span id="cps">0.0</span> ₺/sn</div>
            <div style="font-size:10px; color:#aaa;">PASİF GELİR</div>
        </div>
    </div>

    <button class="clicker-btn" onclick="manualClick()">👆 ÇALIŞ (+1 ₺)</button>

    <h4 style="color:#2c3e50; margin-bottom:10px;">YATIRIM FIRSATLARI</h4>
    <div class="market-grid" id="market">
        </div>

    <div class="bank-section">
        <h4 style="margin:0 0 10px 0; color:#27ae60;">BANKA TRANSFERİ</h4>
        <p style="font-size:12px; color:#555;">Biriken nakit paranı ana hesabına aktarmak için kod üret.</p>
        <button class="transfer-btn" onclick="generateTransferCode()">KOD ÜRET & PARAYI SIFIRLA</button>
        <div id="transferCode" class="code-display"></div>
    </div>
</div>

<script>
    // --- CİMRİ EKONOMİ AYARLARI ---
    let money = 0;
    let assets = [
        { name: "Limonata Standı", cost: 100, income: 0.5, count: 0 },
        { name: "Simit Arabası", cost: 750, income: 2.5, count: 0 },
        { name: "Kırtasiye", cost: 3000, income: 8.0, count: 0 },
        { name: "Kantin İşletmesi", cost: 12000, income: 25.0, count: 0 },
        { name: "Yazılım Şirketi", cost: 50000, income: 85.0, count: 0 }
    ];

    function updateUI() {
        document.getElementById('money').innerText = Math.floor(money).toLocaleString();
        
        let totalCps = 0;
        assets.forEach(a => totalCps += a.count * a.income);
        document.getElementById('cps').innerText = totalCps.toFixed(1);

        const market = document.getElementById('market');
        market.innerHTML = '';

        assets.forEach((asset, index) => {
            let currentCost = Math.floor(asset.cost * Math.pow(1.15, asset.count));
            
            let div = document.createElement('div');
            div.className = 'asset-card ' + (money >= currentCost ? '' : 'locked');
            div.onclick = () => buyAsset(index);
            
            div.innerHTML = `
                <div class="asset-name">${asset.name}</div>
                <div class="asset-cost">${currentCost.toLocaleString()} ₺</div>
                <div class="asset-income">+${asset.income} ₺/sn</div>
                <div class="asset-count">${asset.count}</div>
            `;
            market.appendChild(div);
        });
    }

    function manualClick() {
        money += 1; // Cimri tıklama
        updateUI();
    }

    function buyAsset(index) {
        let asset = assets[index];
        let currentCost = Math.floor(asset.cost * Math.pow(1.15, asset.count));
        
        if (money >= currentCost) {
            money -= currentCost;
            asset.count++;
            updateUI();
        }
    }

    // Pasif Gelir Döngüsü (Her 1 saniyede)
    setInterval(() => {
        let totalCps = 0;
        assets.forEach(a => totalCps += a.count * a.income);
        if(totalCps > 0) {
            money += totalCps;
            updateUI();
        }
    }, 1000);

    // KOD ÜRETME (GÜVENLİK ALGORİTMASI)
    function generateTransferCode() {
        if(money < 50) {
            alert("Transfer için en az 50 ₺ birikmelidir!");
            return;
        }

        let amountToTransfer = Math.floor(money);
        
        // Basit Şifreleme: (Tutar * 13) -> Hex Çevir
        let encryptedVal = (amountToTransfer * 13).toString(16).toUpperCase();
        let randomPart = Math.floor(Math.random() * 100);
        let code = "FNK-" + encryptedVal + "-" + randomPart;

        document.getElementById("transferCode").innerText = code;
        document.getElementById("transferCode").style.display = "block";

        // Parayı sıfırla (Varlıklar kalır)
        money = 0;
        updateUI();
    }

    updateUI();
</script>
</body>
</html>
"""

# ==========================================
# 🧩 ASSET MATRIX (HTML - Cimri Puan)
# ==========================================
ASSET_MATRIX_HTML = """
<!DOCTYPE html>
<html>
<head>
<style>
 body { background: #050505; color: white; font-family: 'Segoe UI', monospace; display: flex; flex-direction: column; align-items: center; padding: 20px; }
 canvas { background: #111; border: 2px solid #333; margin-bottom: 20px; }
 .btn { background: #38bdf8; border: none; padding: 10px 20px; font-weight: bold; cursor: pointer; color: #000; border-radius: 5px; }
 .code-box { margin-top: 15px; padding: 10px; background: white; color: black; font-weight: bold; display: none; }
</style>
</head>
<body>
 <h3>ASSET MATRIX</h3>
 <div style="margin-bottom:10px">PUAN: <span id="score">0</span></div>
 <canvas id="c" width="300" height="400"></canvas>
 <button class="btn" onclick="getCode()">KAZANCI BANKAYA AKTAR</button>
 <div id="code" class="code-box"></div>

 <script>
  const c = document.getElementById('c'), ctx = c.getContext('2d');
  let score = 0;
  
  // Basit Görselleştirme (Tam oyun yerine demo mantığı)
  function draw() {
    ctx.fillStyle = '#111'; ctx.fillRect(0,0,300,400);
    ctx.strokeStyle = '#222'; ctx.beginPath();
    for(let i=0;i<300;i+=30) { ctx.moveTo(i,0); ctx.lineTo(i,400); }
    for(let i=0;i<400;i+=30) { ctx.moveTo(0,i); ctx.lineTo(300,i); }
    ctx.stroke();
    
    ctx.fillStyle = '#38bdf8';
    ctx.fillText("Blokları Yerleştir (Demo)", 80, 200);
  }
  
  // Tıklayınca Puan Artır (Oyun mantığını simüle eder)
  c.addEventListener('click', () => {
      score += 10; // Cimri puan
      document.getElementById('score').innerText = score;
      draw();
      ctx.fillStyle = '#f1c40f';
      ctx.fillRect(Math.random()*270, Math.random()*370, 30, 30);
  });

  function getCode() {
      if(score < 50) { alert("En az 50 puan gerekli!"); return; }
      
      // Şifreleme Algoritması (Python ile aynı olmalı)
      let val = (score * 13).toString(16).toUpperCase();
      let code = "FNK-" + val + "-MTX";
      
      document.getElementById('code').innerText = code;
      document.getElementById('code').style.display = 'block';
      score = 0; 
      document.getElementById('score').innerText = 0;
      draw();
  }
  draw();
 </script>
</body>
</html>
"""

# ==========================================
# 3. YARDIMCI FONKSİYONLAR
# ==========================================
@st.cache_data(ttl=300)
def fetch_lifesim_data():
    if os.path.exists("lifesim_data.json"):
        try:
            with open("lifesim_data.json", "r", encoding="utf-8") as f:
                return f.read()
        except: pass
    try:
        if "githubusercontent" in GITHUB_JSON_URL:
            response = requests.get(GITHUB_JSON_URL)
            if response.status_code == 200:
                return response.text
    except: pass
    return "[]"

def load_lifesim_html():
    try:
        with open("game.html", "r", encoding="utf-8") as f:
            html = f.read()
        json_data = fetch_lifesim_data()
        return html.replace("// PYTHON_DATA_HERE", f"var scenarios = {json_data};")
    except FileNotFoundError:
        return "<h3 style='color:red'>Hata: game.html dosyası bulunamadı!</h3>"

# ==========================================
# 4. TASARIM VE OTURUM
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
    
    /* Banka Vezne Alanı */
    .bank-area { background: #e8f5e9; padding: 20px; border-radius: 15px; border: 2px dashed #27ae60; text-align: center; margin-bottom: 20px; }
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
    # Üst Bilgi
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

    # 1. ANA EKRAN (Skor & Banka)
    with tab_ana:
        c_bank, c_lead = st.columns([1, 2])
        
        with c_bank:
            st.markdown('<div class="bank-area"><h3>🏦 MERKEZ BANKASI VEZNESİ</h3><p>Oyunlardan kazandığın transfer kodunu buraya gir.</p></div>', unsafe_allow_html=True)
            
            code_input = st.text_input("Transfer Kodu (Örn: FNK-3A-99)", key="bank_code")
            
            if st.button("💰 KODU BOZDUR VE YATIR", use_container_width=True):
                amount = decode_code(code_input)
                if amount:
                    st.session_state.bank_balance += amount
                    st.success(f"✅ İŞLEM BAŞARILI! Hesabınıza {amount} ₺ eklendi.")
                    time.sleep(2)
                    st.rerun()
                else:
                    st.error("⛔ HATA: Geçersiz veya kullanılmış kod!")

        with c_lead:
            st.header("🏆 Okul Sıralaması")
            # Demo Veri + Kendi Skorun
            data = [
                {'Sıra': 1, 'Ad Soyad': 'Ayşe Y.', 'Puan': 50000},
                {'Sıra': 2, 'Ad Soyad': 'Mehmet K.', 'Puan': 42000},
                {'Sıra': 3, 'Ad Soyad': st.session_state.user_name + " (SİZ)", 'Puan': st.session_state.bank_balance},
                {'Sıra': 4, 'Ad Soyad': 'Ali V.', 'Puan': 1500}
            ]
            df = pd.DataFrame(data).sort_values("Puan", ascending=False).reset_index(drop=True)
            df['Sıra'] = df.index + 1
            st.table(df)

    # 2. PROFİL
    with tab_profil:
        st.info(f"Öğrenci: {st.session_state.user_name} ({st.session_state.user_no})")
        if st.button("Çıkış Yap"):
            st.session_state.logged_in = False
            st.rerun()

    # 3. SORU ÇÖZÜM
    with tab_soru:
        st.header("📚 Soru Çözüm Merkezi")
        st.info("Testler yakında eklenecek.")

    # 4. EĞLENCE (Gelişmiş & Entegre Oyunlar)
    with tab_eglence:
        st.header("🎮 Eğlence & Finans Alanı")
        game_choice = st.selectbox("Oyun Seç:", ["Finans İmparatoru (Pasif Gelir)", "Asset Matrix (Blok Oyunu)"])
        
        if game_choice == "Finans İmparatoru (Pasif Gelir)":
            components.html(FINANCE_GAME_HTML, height=700, scrolling=True)
        else:
            components.html(ASSET_MATRIX_HTML, height=750, scrolling=False)

    # 5. LIFESIM (Game.html + JSON)
    with tab_lifesim:
        st.header("💼 LifeSim: Kariyer Simülasyonu")
        final_code = load_lifesim_html()
        components.html(final_code, height=800, scrolling=True)

    # 6. PREMIUM
    with tab_premium:
        st.warning("Premium özellikler yapım aşamasında.")
