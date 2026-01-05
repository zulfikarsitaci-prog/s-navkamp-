import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import requests
import json
import os
import time
import random
import database  # database.py dosyası yaninda olmalı
from datetime import datetime

# ==========================================
# 1. SAYFA AYARLARI (EN BAŞTA OLMALI)
# ==========================================
st.set_page_config(
    page_title="Bağarası ÇPAL - Dijital Kampüs",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Veritabanı Başlat
database.create_database()
if not database.login_user("admin", "6626"):
    database.add_user("admin", "6626", "admin")

# ==========================================
# 2. SABİTLER VE VERİ KAYNAKLARI
# ==========================================
GITHUB_BASE_URL = "https://raw.githubusercontent.com/zulfikarsitaci-prog/s-navkamp-/main"
URL_TYT_DATA = f"{GITHUB_BASE_URL}/tyt_data.json"
URL_TYT_PDF = f"{GITHUB_BASE_URL}/tytson8.pdf"
URL_MESLEK_SORULAR = f"{GITHUB_BASE_URL}/sorular.json"
URL_LIFESIM = f"{GITHUB_BASE_URL}/lifesim_data.json"

# --- OYUN HTML KODLARI (TAM VE ÇALIŞAN VERSİYONLAR) ---
FINANCE_GAME_HTML = """
<!DOCTYPE html>
<html lang="tr">
<head>
<meta charset="UTF-8">
<style>
    body { background-color: #0f172a; color: #e2e8f0; font-family: sans-serif; user-select: none; padding: 10px; text-align: center; margin: 0; }
    .dashboard { display: flex; justify-content: space-between; background: #1e293b; padding: 15px; border-radius: 12px; border: 1px solid #334155; margin-bottom: 20px; }
    .money-val { font-size: 22px; font-weight: 900; color: #34d399; }
    .clicker-btn { background: radial-gradient(circle, #3b82f6 0%, #1d4ed8 100%); border: 4px solid #1e3a8a; border-radius: 50%; width: 110px; height: 110px; font-size: 30px; cursor: pointer; margin: 0 auto 20px auto; display: flex; align-items: center; justify-content: center; box-shadow: 0 0 20px rgba(59, 130, 246, 0.4); }
    .clicker-btn:active { transform: scale(0.95); }
    .asset-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(130px, 1fr)); gap: 8px; margin-bottom: 20px; }
    .asset-card { background: #1e293b; padding: 10px; border-radius: 8px; border: 1px solid #334155; cursor: pointer; transition: 0.2s; text-align: left; }
    .asset-card:hover { border-color: #facc15; background: #253347; }
    .asset-card.locked { opacity: 0.5; filter: grayscale(1); pointer-events: none; }
    .bank-btn { background: #10b981; color: #fff; border: none; padding: 8px 20px; font-weight: bold; border-radius: 6px; cursor: pointer; margin-top: 10px; }
    .code-display { background: #fff; color: #000; padding: 5px; margin-top: 5px; font-family: monospace; font-weight: bold; display: none; border-radius: 4px; }
</style>
</head>
<body>
<div class="dashboard">
    <div>NAKİT: <div id="money" class="money-val">0 ₺</div></div>
    <div>GELİR: <div id="cps" style="color:#facc15">0.0 /sn</div></div>
</div>
<div class="clicker-btn" onclick="manualWork()">👆</div>
<div class="asset-grid" id="market"></div>
<button class="bank-btn" onclick="generateCode()">🏦 Bankaya Aktar</button>
<div id="transferCode" class="code-display"></div>
<script>
    let money = 0;
    const assets = [
        { name: "Limonata", cost: 150, gain: 0.5, count: 0 }, { name: "Simit Tezgahı", cost: 1000, gain: 3.5, count: 0 },
        { name: "Kantin", cost: 5000, gain: 15.0, count: 0 }, { name: "Kırtasiye", cost: 20000, gain: 55.0, count: 0 },
        { name: "Yazılım Ofisi", cost: 80000, gain: 200.0, count: 0 }, { name: "Fabrika", cost: 1000000, gain: 3500.0, count: 0 }
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
            div.innerHTML = `<b>${asset.name}</b> (${asset.count})<br><span style="color:#f87171">${currentCost.toLocaleString()} ₺</span><br><span style="color:#34d399">+${asset.gain}/sn</span>`;
            market.appendChild(div);
        });
    }
    function manualWork() { money += 1; updateUI(); }
    function buyAsset(index) {
        let asset = assets[index]; let currentCost = Math.floor(asset.cost * Math.pow(1.2, asset.count));
        if (money >= currentCost) { money -= currentCost; asset.count++; updateUI(); }
    }
    function generateCode() {
        if (money < 50) { alert("En az 50 ₺ birikmeli."); return; }
        let val = Math.floor(money); let hex = (val * 13).toString(16).toUpperCase(); 
        let rnd = Math.floor(Math.random() * 9999);
        let code = `FNK-${hex}-${rnd}`;
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
<style>
    body { background-color: #050505; color: white; font-family: sans-serif; text-align: center; overflow: hidden; margin: 0; }
    #gameCanvas { background: #111; border: 1px solid #333; margin-top: 10px; box-shadow: 0 0 20px rgba(255,255,255,0.1); }
    .btn { background: #333; color: white; border: 1px solid #555; padding: 10px 20px; cursor: pointer; margin-top: 10px; font-weight: bold; }
    .btn:hover { background: #555; }
    #bankCodeDisplay { background: white; color: black; padding: 5px; display: none; margin: 10px auto; width: 200px; font-weight: bold; border-radius: 4px; }
</style>
</head>
<body>
    <h3 style="margin-bottom:5px; color:#FFD700;">ASSET MATRIX</h3>
    <div id="score" style="font-size:24px; font-weight:bold;">0</div>
    <button class="btn" onclick="getTransferCode()">🏦 PUANI ÇEK</button>
    <div id="bankCodeDisplay"></div>
    <canvas id="gameCanvas" width="300" height="400"></canvas>
    <script>
        const canvas = document.getElementById('gameCanvas'); const ctx = canvas.getContext('2d');
        let score = 0; let x = 125, y = 0;
        function draw() {
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            ctx.fillStyle = '#3b82f6'; ctx.fillRect(x, y, 50, 50);
            y += 2; if(y > canvas.height) { y = 0; score += 10; document.getElementById('score').innerText = score; }
            requestAnimationFrame(draw);
        }
        function getTransferCode() {
            let val = score > 0 ? score : 50; // Demo puan
            let hex = (val * 13).toString(16).toUpperCase(); 
            let code = `FNK-${hex}-${Math.floor(Math.random()*999)}`;
            document.getElementById('bankCodeDisplay').innerText = code; 
            document.getElementById('bankCodeDisplay').style.display = 'block'; score = 0;
        }
        draw();
    </script>
</body>
</html>
"""

# ==========================================
# 3. FONKSİYONLAR (VERİ ÇEKME & SERVER)
# ==========================================
@st.cache_data
def fetch_json_data(url):
    try:
        r = requests.get(url)
        return r.json() if r.status_code == 200 else {}
    except: return {}

@st.cache_data
def load_local_exams():
    # exams.json dosyasını yerelden okur
    if os.path.exists("exams.json"):
        try:
            with open("exams.json", "r", encoding="utf-8") as f:
                return json.load(f)
        except: return {}
    return {}

@st.cache_resource
class SchoolServer:
    def __init__(self):
        self.classes = {} 
        self.used_codes = set()
        self.create_class("GENEL")
    def create_class(self, class_code):
        if class_code not in self.classes: self.classes[class_code] = {}
    def join_or_update_student(self, class_code, username, points_to_add=0):
        if class_code not in self.classes: self.create_class(class_code)
        if username not in self.classes[class_code]: self.classes[class_code][username] = 0
        self.classes[class_code][username] += points_to_add
        return self.classes[class_code][username]
    def get_score(self, class_code, username): return self.classes.get(class_code, {}).get(username, 0)
    def redeem_code(self, class_code, username, code_string):
        if code_string in self.used_codes: return False, "Kod kullanılmış!"
        try:
            parts = code_string.split('-')
            if len(parts) != 3 or parts[0] != "FNK": return False, "Geçersiz kod!"
            amount = int(int(parts[1], 16) / 13)
            self.used_codes.add(code_string)
            nb = self.join_or_update_student(class_code, username, amount)
            return True, nb
        except: return False, "Hata."
    def get_leaderboard(self, class_code):
        if class_code in self.classes:
            data = [{"Öğrenci": k, "Puan": v} for k, v in self.classes[class_code].items()]
            if data: return pd.DataFrame(data).sort_values(by="Puan", ascending=False)
        return pd.DataFrame()

server = SchoolServer()

def load_lifesim():
    try:
        r = requests.get(f"{GITHUB_BASE_URL}/game.html")
        html = r.text if r.status_code == 200 else "<h3>Yüklenemedi</h3>"
        data = requests.get(URL_LIFESIM).json()
        return html.replace("// PYTHON_DATA_HERE", f"var scenarios = {json.dumps(data)};")
    except: return "Simülasyon Yüklenemedi"

# ==========================================
# 4. ARAYÜZ MANTIĞI
# ==========================================
if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "user_role" not in st.session_state: st.session_state.user_role = None
if "username" not in st.session_state: st.session_state.username = None
if "class_code" not in st.session_state: st.session_state.class_code = "GENEL"

# --- A) GİRİŞ EKRANI ---
if not st.session_state.logged_in:
    st.markdown("<h1 style='text-align:center;'>🎓 Bağarası ÇPAL Dijital Kampüs</h1>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        tab_log, tab_reg = st.tabs(["Giriş Yap", "Kayıt Ol (Öğrenci)"])
        
        with tab_log:
            with st.form("login"):
                u = st.text_input("Kullanıcı Adı")
                p = st.text_input("Şifre", type="password")
                if st.form_submit_button("Giriş"):
                    user = database.login_user(u, p)
                    if user:
                        st.session_state.logged_in = True
                        st.session_state.user_role = user[3]
                        st.session_state.username = user[1]
                        if user[3] == "student": server.join_or_update_student("GENEL", user[1], 0)
                        st.rerun()
                    else: st.error("Hatalı bilgi.")
        
        with tab_reg:
            with st.form("reg"):
                nu = st.text_input("Kullanıcı Adı")
                np = st.text_input("Şifre", type="password")
                if st.form_submit_button("Kayıt Ol"):
                    if database.add_user(nu, np, "student"): st.success("Kayıt başarılı! Giriş yapınız.")
                    else: st.error("Bu isim kullanılıyor.")

# --- B) UYGULAMA İÇİ ---
else:
    # Sidebar
    with st.sidebar:
        st.title(st.session_state.username)
        st.caption(f"Yetki: {st.session_state.user_role}")
        if st.session_state.user_role == "student":
            code = st.text_input("Sınıf Kodu", placeholder="Örn: 1234")
            if st.button("Sınıfa Geç"):
                st.session_state.class_code = code
                server.join_or_update_student(code, st.session_state.username)
                st.success(f"Sınıf: {code}"); time.sleep(0.5); st.rerun()
        if st.button("Çıkış"): st.session_state.logged_in = False; st.rerun()

    # --- ÖĞRENCİ PANELİ ---
    if st.session_state.user_role == "student":
        st.header(f"Merhaba, {st.session_state.username}")
        
        # Sekmeler
        t1, t2, t3, t4 = st.tabs(["🏆 Kampüs", "📚 Dersler & Sınav", "🎮 Oyunlar", "💼 LifeSim"])
        
        # 1. KAMPÜS (Puan & Sıralama & Duyuru)
        with t1:
            c1, c2 = st.columns([1,2])
            with c1:
                st.metric("Puanın", f"{server.get_score(st.session_state.class_code, st.session_state.username)} ₺")
                redeem = st.text_input("Puan Kodu")
                if st.button("Yükle"):
                    res, msg = server.redeem_code(st.session_state.class_code, st.session_state.username, redeem)
                    if res: st.success(f"Yüklendi! Yeni: {msg}")
                    else: st.error(msg)
                st.divider()
                st.subheader("📢 Duyurular")
                anns = database.get_announcements()
                if anns:
                    for a in anns: st.info(f"**{a[1]}**: {a[2]}")
                else: st.write("Duyuru yok.")
            with c2:
                st.subheader("Sıralama")
                st.dataframe(server.get_leaderboard(st.session_state.class_code), use_container_width=True)

        # 2. DERSLER (TYT / MESLEK / JSON SINAVLAR)
        with t2:
            mode = st.radio("Çalışma Modu:", ["TYT Çalışma", "Meslek Soruları", "Okul Sınavları (JSON)"], horizontal=True)
            st.divider()

            # --- TYT ---
            if mode == "TYT Çalışma":
                tyt_data = fetch_json_data(URL_TYT_DATA)
                if tyt_data:
                    dersler = sorted(list(set([v.get('ders') for v in tyt_data.values() if 'ders' in v])))
                    sel_ders = st.selectbox("Ders", dersler)
                    pages = [k for k, v in tyt_data.items() if v.get('ders') == sel_ders]
                    if pages:
                        sel_page = st.selectbox("Sayfa", pages)
                        det = tyt_data[sel_page]
                        c_p, c_q = st.columns([1.5, 1])
                        with c_p: st.markdown(f'<embed src="{URL_TYT_PDF}#page={sel_page}" width="100%" height="600px">', unsafe_allow_html=True)
                        with c_q:
                            with st.form("tyt_f"):
                                ans = {}
                                for i, q in enumerate(det['sorular']):
                                    st.write(f"Soru {q}")
                                    ans[i] = st.radio(f"C{q}", ['A','B','C','D','E'], key=f"t_{i}", horizontal=True)
                                if st.form_submit_button("Kontrol"):
                                    d = sum([1 for i, q in enumerate(det['sorular']) if ans[i] == det['cevaplar'][i]])
                                    sc = d * 50
                                    st.success(f"{d} Doğru. +{sc} Puan")
                                    if sc>0: server.join_or_update_student(st.session_state.class_code, st.session_state.username, sc)

            # --- MESLEK ---
            elif mode == "Meslek Soruları":
                m_data = fetch_json_data(URL_MESLEK_SORULAR)
                if m_data:
                    root = m_data.get("KONU_TARAMA", m_data)
                    sinif = st.selectbox("Sınıf", list(root.keys()))
                    if sinif:
                        ders = st.selectbox("Ders", list(root[sinif].keys()))
                        if ders:
                            konu = st.selectbox("Konu", list(root[sinif][ders].keys()))
                            if konu:
                                qs = root[sinif][ders][konu]
                                with st.form("mes_f"):
                                    mans = {}
                                    for i, q in enumerate(qs):
                                        st.write(f"**{i+1}. {q['soru']}**")
                                        mans[i] = st.radio("Cevap", q['secenekler'], key=f"m_{i}")
                                    if st.form_submit_button("Bitir"):
                                        dm = sum([1 for i, q in enumerate(qs) if mans[i] == q['cevap']])
                                        pm = dm * 100
                                        st.success(f"{dm} Doğru. +{pm} Puan")
                                        if pm>0: server.join_or_update_student(st.session_state.class_code, st.session_state.username, pm)

            # --- JSON SINAVLAR (EXAMS.JSON) ---
            elif mode == "Okul Sınavları (JSON)":
                EXAM_DATA = load_local_exams()
                if not EXAM_DATA:
                    st.warning("exams.json dosyası bulunamadı veya boş!")
                else:
                    s_sinif = st.selectbox("Sınıf", list(EXAM_DATA.keys()))
                    if s_sinif:
                        s_ders = st.selectbox("Ders", list(EXAM_DATA[s_sinif].keys()))
                        if s_ders:
                            questions = EXAM_DATA[s_sinif][s_ders]
                            st.subheader(f"{s_ders} Sınavı")
                            with st.form("json_exam"):
                                user_ans = {}
                                for i, q in enumerate(questions):
                                    st.markdown(f"**Soru {i+1}:** {q.get('question', q.get('text', ''))}")
                                    if q['type'] == 'test':
                                        user_ans[i] = st.radio("Seçim", q['options'], key=f"jq_{i}")
                                    elif q['type'] == 'text':
                                        user_ans[i] = st.text_input("Cevap", key=f"jq_{i}")
                                    elif q['type'] == 'scenario':
                                        user_ans[i] = [st.text_input(sub['q'], key=f"jq_{i}_{j}") for j, sub in enumerate(q['sub_questions'])]
                                    elif q['type'] == 'calculation':
                                        user_ans[i] = [st.number_input(inp['label'], key=f"jq_{i}_{j}") for j, inp in enumerate(q['inputs'])]
                                    st.divider()
                                
                                if st.form_submit_button("Sınavı Tamamla"):
                                    score = 0
                                    for i, q in enumerate(questions):
                                        # Basit Puanlama Mantığı
                                        if q['type'] == 'test' and user_ans[i] == q['answer']: score += q['points']
                                        elif q['type'] == 'text' and q['answer'].lower() in user_ans[i].lower(): score += q['points']
                                        elif q['type'] == 'scenario': score += q['points'] # Demo: Direkt puan veriyor
                                        elif q['type'] == 'calculation': score += q['points']
                                    
                                    st.success(f"Sınav Tamamlandı! Puanın: {score}")
                                    if score>0: server.join_or_update_student(st.session_state.class_code, st.session_state.username, score)

        # 3. OYUNLAR
        with t3:
            gm = st.selectbox("Oyun Seç", ["Finans İmparatoru", "Asset Matrix"])
            if gm == "Finans İmparatoru": components.html(FINANCE_GAME_HTML, height=600)
            else: components.html(ASSET_MATRIX_HTML, height=600)

        # 4. LIFESIM
        with t4:
            components.html(load_lifesim(), height=800, scrolling=True)

    # --- ADMIN / TEACHER PANELİ ---
    elif st.session_state.user_role in ["admin", "teacher"]:
        st.header(f"Yönetim Paneli ({st.session_state.user_role.upper()})")
        
        # Admin Ekstraları
        if st.session_state.user_role == "admin":
            st.subheader("Kullanıcı Yönetimi")
            with st.form("add_usr"):
                nu = st.text_input("Yeni Kullanıcı")
                np = st.text_input("Şifre")
                nr = st.selectbox("Rol", ["teacher", "admin", "student"])
                if st.form_submit_button("Ekle"):
                    if database.add_user(nu, np, nr): st.success("Eklendi")
                    else: st.error("Hata")
            
            users = database.get_all_users()
            df = pd.DataFrame(users, columns=["Kullanıcı", "Rol"])
            st.dataframe(df, use_container_width=True)
            dele = st.selectbox("Silinecek Kişi", df["Kullanıcı"])
            if st.button("Sil"):
                if dele != "admin": database.delete_user(dele); st.rerun()
                else: st.error("Admin silinemez.")

        # Öğretmen Ekstraları
        if st.session_state.user_role == "teacher":
            if "created_code" not in st.session_state:
                st.session_state.created_code = str(random.randint(1000, 9999))
                server.create_class(st.session_state.created_code)
            st.info(f"Ders Kodunuz: {st.session_state.created_code}")
            st.dataframe(server.get_leaderboard(st.session_state.created_code))
            
            with st.form("ann"):
                tit = st.text_input("Duyuru Başlık")
                con = st.text_area("İçerik")
                if st.form_submit_button("Yayınla"):
                    database.add_announcement(tit, con, st.session_state.username)
                    st.success("Yayınlandı")
