import streamlit as st
import streamlit.components.v1 as components
import json
import os

st.set_page_config(page_title="Finans İmparatoru", layout="wide", initial_sidebar_state="expanded")

# CSS DÜZENLEMELERİ
st.markdown("""
<style>
    [data-testid="stSidebar"] { background-color: #0f172a; border-right: 1px solid #334155; }
    h1, h2, h3 { color: white; }
    .stRadio > label { color: white; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# ================= 1. GÖMÜLÜ OYUN KODLARI =================

# FİNANS İMPARATORU (HTML/JS String)
FINANCE_GAME_HTML = """
<!DOCTYPE html>
<html>
<head>
<style>
 body { background: #0a0a12; color: white; font-family: 'Segoe UI', sans-serif; text-align: center; user-select: none; }
 .box { background: #16213e; padding: 20px; border-radius: 15px; border: 2px solid #f1c40f; max-width: 400px; margin: 20px auto; box-shadow: 0 0 20px rgba(241,196,15,0.2); }
 h2 { color: #f1c40f; margin: 0 0 15px 0; letter-spacing: 2px; }
 .money { font-size: 36px; font-weight: bold; color: #2ecc71; margin: 10px 0; text-shadow: 0 0 10px rgba(46,204,113,0.4); }
 .btn { background: linear-gradient(45deg, #f1c40f, #d35400); border: none; padding: 15px; width: 100%; color: #000; font-weight: bold; font-size: 16px; cursor: pointer; border-radius: 8px; margin-top: 10px; transition: transform 0.1s; }
 .btn:active { transform: scale(0.98); }
 .btn-invest { background: linear-gradient(45deg, #3498db, #2980b9); color: white; }
 .stats { display: flex; justify-content: space-between; margin-top: 15px; font-size: 12px; color: #aaa; }
</style>
</head>
<body>
<div class="box">
  <h2>FİNANS İMPARATORU</h2>
  <div class="money" id="money">0 ₺</div>
  <div style="color: #aaa; font-size: 14px; margin-bottom: 20px;">Pasif Gelir: <span id="income" style="color: #fff">0</span> ₺/sn</div>
  
  <button class="btn" onclick="earn()">👆 TIKLA KAZAN (+100 ₺)</button>
  <button class="btn btn-invest" onclick="invest()">🏢 DÜKKAN AL (Maliyet: <span id="cost">1000</span> ₺)</button>
  
  <div class="stats">
     <span>Dükkan Sayısı: <span id="shops">0</span></span>
     <span>Seviye: Başlangıç</span>
  </div>
</div>
<script>
  let money = 0;
  let income = 0;
  let shops = 0;
  let cost = 1000;

  function update() { 
    document.getElementById('money').innerText = Math.floor(money).toLocaleString() + ' ₺'; 
    document.getElementById('income').innerText = income.toLocaleString();
    document.getElementById('cost').innerText = cost.toLocaleString();
    document.getElementById('shops').innerText = shops;
  }

  function earn() { 
    money += 100; 
    update(); 
  }

  function invest() {
    if(money >= cost) { 
      money -= cost; 
      income += 50; 
      shops++;
      cost = Math.floor(cost * 1.2); // Maliyet artışı
      update(); 
    }
  }

  // Pasif Gelir Döngüsü
  setInterval(() => { 
    money += income; 
    update(); 
  }, 1000);
</script>
</body>
</html>
"""

# ASSET MATRIX (HTML/JS String)
MATRIX_GAME_HTML = """
<!DOCTYPE html>
<html>
<head>
<style>
 body { background: #050505; color: white; display: flex; flex-direction: column; align-items: center; font-family: monospace; margin: 0; padding: 20px; }
 canvas { background: #111; border: 2px solid #333; border-radius: 4px; box-shadow: 0 0 30px rgba(0,255,255,0.1); }
 h2 { color: #00e5ff; letter-spacing: 3px; margin-bottom: 10px; }
 button { background: #00e5ff; color: #000; border: none; padding: 10px 30px; font-weight: bold; cursor: pointer; margin-top: 15px; border-radius: 4px; }
 button:hover { background: #00b8cc; }
 #score { font-size: 24px; font-weight: bold; margin-bottom: 10px; color: #fff; }
</style>
</head>
<body>
<h2>ASSET MATRIX</h2>
<div id="score">SKOR: 0</div>
<canvas id="c" width="320" height="400"></canvas>
<button onclick="init()">YENİ OYUN</button>

<script>
 const c = document.getElementById('c'), ctx = c.getContext('2d');
 let pieces = [], score = 0;

 function init() {
    score = 0;
    document.getElementById('score').innerText = "SKOR: " + score;
    spawnPieces();
    draw();
 }

 function spawnPieces() {
    pieces = [
        {x: 30, y: 320, w: 30, h: 30, c: '#FFD700'}, // Altın
        {x: 110, y: 320, w: 60, h: 30, c: '#00e5ff'}, // Neon Mavi
        {x: 220, y: 320, w: 30, h: 60, c: '#ff0055'}  // Neon Pembe
    ];
 }

 function draw() {
    ctx.fillStyle = '#080808'; ctx.fillRect(0,0,320,400);
    
    // Grid Çizgileri
    ctx.strokeStyle='#222'; ctx.lineWidth=1; ctx.beginPath();
    for(let i=0;i<=320;i+=32) { ctx.moveTo(i,0); ctx.lineTo(i,300); } // Dikey
    for(let i=0;i<=300;i+=30) { ctx.moveTo(0,i); ctx.lineTo(320,i); } // Yatay
    ctx.stroke();
    
    // Alt Çizgi (Spawn Alanı Ayracı)
    ctx.strokeStyle='#444'; ctx.beginPath(); ctx.moveTo(0,300); ctx.lineTo(320,300); ctx.stroke();

    // Parçaları Çiz
    pieces.forEach(p => {
        ctx.fillStyle = p.c;
        ctx.fillRect(p.x, p.y, p.w, p.h);
        ctx.strokeStyle = 'rgba(255,255,255,0.5)';
        ctx.strokeRect(p.x, p.y, p.w, p.h);
    });
 }
 
 // Basit Etkileşim (Görsel Demo)
 c.addEventListener('mousedown', () => {
    score += 10;
    document.getElementById('score').innerText = "SKOR: " + score;
    // Parçaların rengini rastgele değiştir (Canlılık için)
    pieces.forEach(p => p.c = `hsl(${Math.random()*360}, 70%, 50%)`);
    draw();
 });

 init();
</script>
</body>
</html>
"""

# ================= 2. LIFESIM YÜKLEME FONKSİYONU =================
def load_lifesim_game():
    # 1. JSON Verisini Oku
    try:
        with open('lifesim_data.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            json_str = json.dumps(data) # JSON verisini String'e çevir
    except FileNotFoundError:
        # Dosya yoksa boş liste gönder, oyun bozulmasın
        json_str = "[]" 

    # 2. HTML Dosyasını Oku
    try:
        with open('game.html', 'r', encoding='utf-8') as f:
            html = f.read()
    except FileNotFoundError:
        return "<h2 style='color:red'>Hata: game.html bulunamadı!</h2>"

    # 3. Veriyi HTML içine yapıştır (Inject)
    # game.html içindeki "// PYTHON_DATA_HERE" yazısını bulup gerçek veriyle değiştirir.
    injected_html = html.replace(
        "// PYTHON_DATA_HERE", 
        f"scenarios = {json_str};"
    )
    return injected_html

# ================= 3. STREAMLIT ARAYÜZÜ =================

# Yan Menü
st.sidebar.title("MENÜ")
st.sidebar.info("Aşağıdan oynamak istediğiniz simülasyonu seçin.")
menu = st.sidebar.radio("Seçim Yapınız:", ["💼 LifeSim (Kariyer)", "📈 Finans İmparatoru", "🧩 Asset Matrix"])

# Menü Mantığı
if menu == "💼 LifeSim (Kariyer)":
    st.header("💼 LifeSim: Kariyer Yönetimi")
    # LifeSim'i dinamik olarak yükle ve göster
    game_code = load_lifesim_game()
    components.html(game_code, height=700, scrolling=False)

elif menu == "📈 Finans İmparatoru":
    st.header("📈 Finans İmparatoru")
    # Python içindeki HTML stringi göster
    components.html(FINANCE_GAME_HTML, height=600)

elif menu == "🧩 Asset Matrix":
    st.header("🧩 Asset Matrix")
    # Python içindeki HTML stringi göster
    components.html(MATRIX_GAME_HTML, height=600)
