import streamlit as st
import streamlit.components.v1 as components
import json
import os

st.set_page_config(page_title="Finans İmparatoru", layout="wide")

# --- 1. OYUN KODLARI (HTML STRINGS) ---

# FİNANS İMPARATORU (Python İçinde Gömülü)
FINANCE_GAME = """
<style>
 body { background: #0a0a12; color: white; font-family: sans-serif; text-align: center; }
 .box { background: #16213e; padding: 20px; border: 1px solid #f1c40f; border-radius: 10px; margin: 10px auto; max-width: 400px; }
 .btn { background: linear-gradient(45deg, #f1c40f, #d35400); border: none; padding: 15px; width: 100%; color: black; font-weight: bold; cursor: pointer; border-radius: 5px; margin-top: 5px; }
</style>
<div class="box">
  <h2>FİNANS İMPARATORU</h2>
  <h1 id="money" style="color:#2ecc71">0 ₺</h1>
  <button class="btn" onclick="earn()">TIKLA KAZAN (+100 ₺)</button>
  <button class="btn" style="background:#3498db; color:white" onclick="invest()">YATIRIM YAP (Maliyet: 1000 ₺)</button>
  <p id="status" style="font-size:12px; color:#aaa; margin-top:10px;">Pasif Gelir: 0 ₺/sn</p>
</div>
<script>
  let money = 0;
  let income = 0;
  function update() { 
    document.getElementById('money').innerText = money + ' ₺'; 
    document.getElementById('status').innerText = 'Pasif Gelir: ' + income + ' ₺/sn';
  }
  function earn() { money += 100; update(); }
  function invest() {
    if(money >= 1000) { money -= 1000; income += 50; update(); }
  }
  setInterval(() => { money += income; update(); }, 1000);
</script>
"""

# ASSET MATRIX (Python İçinde Gömülü)
MATRIX_GAME = """
<style>
 body { background: #000; display: flex; flex-direction: column; align-items: center; color: white; font-family: monospace; }
 canvas { border: 1px solid #333; box-shadow: 0 0 20px rgba(0,255,255,0.2); margin-top: 20px; }
 button { background: #00e5ff; border: none; padding: 10px 30px; font-weight: bold; cursor: pointer; margin-top: 10px; }
</style>
<h2>ASSET MATRIX</h2>
<canvas id="c" width="300" height="400"></canvas>
<button onclick="reset()">YENİ OYUN</button>
<script>
 const c = document.getElementById('c'), ctx = c.getContext('2d');
 let pieces = [];
 function reset() {
    pieces = [{x:50,y:350,w:30},{x:130,y:350,w:60},{x:220,y:350,w:30}];
    draw();
 }
 function draw() {
    ctx.fillStyle = '#111'; ctx.fillRect(0,0,300,400);
    // Basit Grid
    ctx.strokeStyle='#222'; ctx.beginPath();
    for(let i=0;i<300;i+=30) { ctx.moveTo(i,0); ctx.lineTo(i,300); ctx.moveTo(0,i); ctx.lineTo(300,i); }
    ctx.stroke();
    
    // Parçalar (Basit Temsil)
    ctx.fillStyle = '#00e5ff';
    pieces.forEach(p => ctx.fillRect(p.x, p.y, p.w, 30));
 }
 reset();
</script>
"""

# --- 2. VERİ YÜKLEME VE HTML BİRLEŞTİRME ---
def load_lifesim_game():
    # JSON verisini oku
    try:
        with open('lifesim_data.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            json_str = json.dumps(data)
    except FileNotFoundError:
        json_str = "[]" # Hata durumunda boş veri

    # HTML dosyasını oku
    try:
        with open('game.html', 'r', encoding='utf-8') as f:
            html = f.read()
    except FileNotFoundError:
        return "<h1>Hata: game.html bulunamadı!</h1>"

    # Veriyi HTML içine enjekte et
    # "PYTHON_DATA_HERE" yazan yeri silip yerine "scenarios = [....];" yazıyoruz.
    injected_html = html.replace(
        "// PYTHON_DATA_HERE", 
        f"scenarios = {json_str};"
    )
    return injected_html

# --- 3. STREAMLIT ARAYÜZÜ ---

st.sidebar.title("MENÜ")
menu = st.sidebar.radio("Seçim Yapınız:", ["💼 LifeSim (Kariyer)", "📈 Finans İmparatoru", "🧩 Asset Matrix"])

if menu == "💼 LifeSim (Kariyer)":
    st.header("💼 LifeSim: Kariyer Yönetimi")
    # LifeSim HTML'ini dinamik oluşturup gösteriyoruz
    game_code = load_lifesim_game()
    components.html(game_code, height=700, scrolling=True)

elif menu == "📈 Finans İmparatoru":
    st.header("📈 Finans İmparatoru")
    # Python içindeki stringi gösteriyoruz
    components.html(FINANCE_GAME, height=600)

elif menu == "🧩 Asset Matrix":
    st.header("🧩 Asset Matrix")
    # Python içindeki stringi gösteriyoruz
    components.html(MATRIX_GAME, height=600)
