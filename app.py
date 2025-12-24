import streamlit as st
import streamlit.components.v1 as components
import random
import time
import pandas as pd
import json

# --- 1. SAYFA AYARLARI ---
st.set_page_config(page_title="Dijital Gelişim Programı", page_icon="🎓", layout="wide")

# --- 2. GÖMÜLÜ VERİLER (DOSYA HATASINI BİTİREN KISIM) ---
# Artık json dosyası aramaz, direkt buradaki veriyi kullanır.

TYT_DATA_EMBEDDED = {
    1: {"ders": "Türkçe (Paragraf)", "cevaplar": ["A", "C", "B", "D", "E"]},
    2: {"ders": "Matematik (Temel)", "cevaplar": ["E", "E", "A", "C", "B"]},
    3: {"ders": "Tarih (İlk Çağ)", "cevaplar": ["B", "A", "D", "C", "E"]},
    4: {"ders": "Coğrafya (İklim)", "cevaplar": ["C", "B", "A", "E", "D"]},
    5: {"ders": "Felsefe", "cevaplar": ["A", "D", "E", "B", "C"]}
}

MESLEK_DATA_EMBEDDED = {
    "9. Sınıf": {
        "Mesleki Gelişim": {
            "İletişim": [
                {"soru": "İletişimde en önemli unsur nedir?", "secenekler": ["Kaynak", "Alıcı", "Geri Bildirim", "Kanal"], "cevap": "Geri Bildirim"},
                {"soru": "Sözsüz iletişim hangisini kapsar?", "secenekler": ["Mektup", "Beden Dili", "Telefon", "E-Mail"], "cevap": "Beden Dili"},
                {"soru": "Empati nedir?", "secenekler": ["Sempati duymak", "Kendini başkasının yerine koymak", "Öğüt vermek", "Eleştirmek"], "cevap": "Kendini başkasının yerine koymak"}
            ]
        }
    },
    "10. Sınıf": {
        "Muhasebe 1": {
            "Bilanço": [
                {"soru": "Kasa hesabı hangi kod ile başlar?", "secenekler": ["100", "102", "300", "600"], "cevap": "100"},
                {"soru": "Varlık hesapları nasıl çalışır?", "secenekler": ["Borçtan artar", "Alacaktan artar", "Pasiften artar", "Hiçbiri"], "cevap": "Borçtan artar"},
                {"soru": "Aşağıdakilerden hangisi dönen varlıktır?", "secenekler": ["Binalar", "Demirbaşlar", "Ticari Mallar", "Taşıtlar"], "cevap": "Ticari Mallar"}
            ]
        }
    },
    "11. Sınıf": {
        "Şirketler Muhasebesi": {
            "Şirket Kuruluşu": [
                {"soru": "Anonim şirket en az kaç kişiyle kurulur?", "secenekler": ["1", "2", "5", "50"], "cevap": "1"},
                {"soru": "Limited şirket en az sermaye ne kadardır?", "secenekler": ["10.000", "50.000", "100.000", "5.000"], "cevap": "10.000"}
            ]
        }
    }
}

# --- 3. SESSION STATE ---
if 'ekran' not in st.session_state: st.session_state.ekran = 'giris'
if 'oturum' not in st.session_state: st.session_state.oturum = False
if 'ad_soyad' not in st.session_state: st.session_state.ad_soyad = ""
if 'secim_turu' not in st.session_state: st.session_state.secim_turu = None 
if 'secilen_liste' not in st.session_state: st.session_state.secilen_liste = []
if 'aktif_index' not in st.session_state: st.session_state.aktif_index = 0
if 'dogru_sayisi' not in st.session_state: st.session_state.dogru_sayisi = 0
if 'yanlis_sayisi' not in st.session_state: st.session_state.yanlis_sayisi = 0
if 'bos_sayisi' not in st.session_state: st.session_state.bos_sayisi = 0
if 'mod' not in st.session_state: st.session_state.mod = ""
if 'bekleyen_odul' not in st.session_state: st.session_state.bekleyen_odul = 0

# GOOGLE SHEETS AYARLARI
SHEET_ID = "1pHT6b-EiV3a_x3aLzYNu3tQmX10RxWeStD30C8Liqoo"
SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=0"

# --- 4. TASARIM (CSS) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;500;700&display=swap');
    .stApp { background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%); font-family: 'Roboto', sans-serif; }
    h1, h2, h3 { color: #1e3a8a !important; }
    p, label { color: #374151 !important; font-size: 16px; }
    .giris-kart { background-color: white; padding: 40px; border-radius: 20px; box-shadow: 0 20px 25px -5px rgba(0,0,0,0.1); text-align: center; border-top: 6px solid #FF7043; margin-top: 30px; margin-bottom: 20px; }
    .secim-karti { background-color: white; padding: 25px; border-radius: 15px; border: 2px solid #e5e7eb; text-align: center; transition: all 0.3s ease; height: 160px; display: flex; flex-direction: column; justify-content: center; align-items: center; cursor: pointer; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); }
    .secim-karti:hover { transform: translateY(-5px); box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1); border-color: #FF7043; }
    .stButton>button { background-color: #FF7043 !important; color: white !important; border-radius: 10px; font-weight: bold; border: none !important; padding: 10px 20px; transition: all 0.2s; box-shadow: 0 4px 6px rgba(255, 112, 67, 0.3); }
    .stButton>button:hover { background-color: #F4511E !important; transform: scale(1.02); }
    .stTextInput>div>div>input { border-radius: 10px; border: 2px solid #e5e7eb; padding: 10px; }
    .footer-text { text-align: center; font-size: 10px; color: #9ca3af; margin-top: 50px; font-family: monospace; opacity: 0.7; }
    .konu-karti { background-color: white; padding: 20px; border-radius: 10px; border-left: 6px solid #2196F3; margin-bottom: 15px; box-shadow: 0 2px 5px rgba(0,0,0,0.05); }
    .soru-karti { background-color: white; padding: 20px; border-radius: 10px; border-left: 5px solid #FF7043; font-size: 18px; margin-bottom: 20px; color: #000 !important; }
    .stat-card { background-color: white; padding: 15px; border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); text-align: center; border: 2px solid #FF7043; }
    .stat-number { font-size: 32px; font-weight: bold; color: #D84315; }
    footer {visibility: hidden;} #MainMenu {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# --- 5. LİDERLİK TABLOSU MANTIĞI (HİBRİD SİSTEM) ---
@st.cache_data(ttl=5) # 5 saniyede bir yenile
def get_hybrid_leaderboard(current_user, current_score):
    try:
        # 1. Google Sheets'ten veriyi çek (Sadece Okuma)
        df = pd.read_csv(SHEET_URL)
        df.columns = [str(c).strip().upper() for c in df.columns] # Başlıkları büyük harfe çevirip temizle
        
        # Sütunları bul (Esnek arama)
        name_col = next((c for c in df.columns if c in ['ISIM', 'AD', 'AD SOYAD', 'NAME']), None)
        score_col = next((c for c in df.columns if c in ['PUAN', 'SKOR', 'SCORE', 'MONEY']), None)
        
        data = []
        if name_col and score_col:
            # Mevcut veriyi al
            for _, row in df.iterrows():
                try:
                    puan = int(pd.to_numeric(row[score_col], errors='coerce'))
                    data.append({"name": str(row[name_col]), "score": puan})
                except: continue
        
        # 2. ŞU ANKİ KULLANICIYI LİSTEYE EKLE (HİBRİD KISIM)
        # Bu kısım sayesinde, Google Sheets'e yazamasak bile kullanıcı kendini listede görür.
        # Eğer kullanıcı zaten listede varsa güncelle, yoksa ekle.
        user_exists = False
        for p in data:
            if p["name"] == current_user:
                p["score"] = max(p["score"], current_score) # En yüksek skoru tut
                p["isMe"] = True
                user_exists = True
                break
        
        if not user_exists:
            data.append({"name": current_user, "score": current_score, "isMe": True})
            
        # 3. Sırala ve İlk 10'u döndür
        data.sort(key=lambda x: x["score"], reverse=True)
        return json.dumps(data[:10], ensure_ascii=False)

    except Exception as e:
        # Hata olursa sadece kullanıcıyı döndür
        return json.dumps([{"name": current_user, "score": current_score, "isMe": True}], ensure_ascii=False)

# --- 6. HTML ŞABLONLARI ---

# LIFE-SIM HTML
LIFE_SIM_DATA = """[
    {"id":1, "category":"Girişimcilik", "title":"Okul Kantini İhalesi", "text":"Okulun kantin ihalesi açıldı. İhaleye girmek için 5.000 TL teminat yatırman gerekiyor. İhaleyi kazanırsan günlük cirodan %20 kar elde edeceksin ama kantin kirası ve personel giderleri var.", "hint":"Nakit akışını hesapla. Sabit giderler bazen kardan yüksek olabilir.", "doc":"<h3>Ticari Risk Analizi</h3><p>Bir işletmeye yatırım yaparken sadece ciroya (kasaya giren paraya) bakılmaz. <b>Net Kar = Ciro - (Kira + Personel + Malzeme)</b> formülü kullanılır. Eğer sabit giderler çok yüksekse, yüksek ciro bile zarar getirebilir.</p>"},
    {"id":2, "category":"Borsa", "title":"Halka Arz Fırsatı", "text":"Yeni bir teknoloji şirketi halka arz oluyor. Elindeki tüm parayı bu hisseye yatırmayı düşünüyorsun. Arkadaşların 'kesin 2 katına çıkacak' diyor.", "hint":"Tüm yumurtaları aynı sepete koyma.", "doc":"<h3>Portföy Çeşitlendirmesi</h3><p>Yatırımda en temel kural <b>çeşitlendirmedir</b>. Tüm sermayeyi tek bir hisseye yatırmak kumardır. Profesyoneller paralarını Hisse, Altın ve Nakit arasında bölerler.</p>"}
]"""

LIFE_SIM_HTML = """
<!DOCTYPE html><html lang="tr"><head><meta charset="UTF-8"><script src="https://cdn.tailwindcss.com"></script><script src="https://unpkg.com/lucide@latest"></script><style>body{background-color:#0f172a;color:#e2e8f0;font-family:sans-serif;padding:20px}.glass{background:rgba(30,41,59,0.9);border-radius:12px;padding:20px;border:1px solid #334155}</style></head>
<body>
<div class="glass">
    <h2 id="title" class="text-2xl font-bold text-white mb-4">Senaryo Yükleniyor...</h2>
    <p id="text" class="text-gray-300 mb-6 leading-relaxed">...</p>
    <div class="flex gap-4">
        <button onclick="nextScenario()" class="bg-blue-600 hover:bg-blue-500 text-white px-6 py-2 rounded font-bold transition">Yeni Senaryo</button>
        <button onclick="showDoc()" class="bg-purple-600 hover:bg-purple-500 text-white px-6 py-2 rounded font-bold transition">Uzman Görüşü</button>
    </div>
    <div id="docBox" class="hidden mt-4 p-4 bg-slate-800 rounded border-l-4 border-green-500 text-sm"></div>
</div>
<script>
    lucide.createIcons();
    const data = __DATA__;
    let currentIdx = 0;
    function load() {
        const item = data[currentIdx];
        document.getElementById('title').innerText = item.title;
        document.getElementById('text').innerText = item.text;
        document.getElementById('docBox').innerHTML = item.doc;
        document.getElementById('docBox').classList.add('hidden');
    }
    function nextScenario() {
        currentIdx = (currentIdx + 1) % data.length;
        load();
    }
    function showDoc() {
        document.getElementById('docBox').classList.remove('hidden');
    }
    load();
</script>
</body></html>
""".replace("__DATA__", LIFE_SIM_DATA)

# OYUN HTML
GAME_HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
    <script src="https://cdn.tailwindcss.com"></script><script src="https://unpkg.com/lucide@latest"></script>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;500;800&family=Press+Start+2P&display=swap');
        body { background: radial-gradient(circle at center, #1e1b4b, #020617); color: white; font-family: 'Outfit', sans-serif; overflow: hidden; user-select: none; }
        .glass { background: rgba(255, 255, 255, 0.03); backdrop-filter: blur(10px); border: 1px solid rgba(255, 255, 255, 0.05); }
        .click-anim { position: absolute; animation: fly 0.8s ease-out forwards; pointer-events: none; font-weight: 800; color: #4ade80; z-index: 100; }
        @keyframes fly { 0% { transform: translateY(0); opacity: 1; } 100% { transform: translateY(-100px); opacity: 0; } }
        .pulse-btn { animation: pulse 2s infinite; }
        @keyframes pulse { 0% { box-shadow: 0 0 0 0 rgba(59, 130, 246, 0.7); } 70% { box-shadow: 0 0 0 20px rgba(59, 130, 246, 0); } 100% { box-shadow: 0 0 0 0 rgba(59, 130, 246, 0); } }
        .market-item { transition: all 0.2s; border-left: 4px solid transparent; }
        .market-item.can-buy { background: rgba(34, 197, 94, 0.1); border-left-color: #22c55e; cursor: pointer; }
        .market-item.locked { opacity: 0.5; cursor: not-allowed; filter: grayscale(1); }
        .leader-item.me { background: rgba(59, 130, 246, 0.3); border: 1px solid #3b82f6; }
        ::-webkit-scrollbar { width: 5px; } ::-webkit-scrollbar-track { background: #0f172a; } ::-webkit-scrollbar-thumb { background: #334155; border-radius: 5px; }
    </style>
</head>
<body class="h-screen flex flex-col p-2 gap-2">
    <div class="glass rounded-xl p-3 flex justify-between items-center shrink-0 border-t-2 border-blue-500">
        <div><div class="text-[10px] text-blue-300 uppercase tracking-widest">TOPLAM VARLIK</div><div class="text-2xl font-black text-white tracking-tighter" id="moneyDisplay">0 ₺</div></div>
        <div class="text-right"><div class="text-[10px] text-green-400 uppercase tracking-widest">GELİR / SN</div><div class="text-xl font-bold text-green-300" id="cpsDisplay">0</div></div>
    </div>

    <div class="flex flex-col md:flex-row gap-2 flex-1 overflow-hidden">
        <div class="w-full md:w-1/3 flex flex-col gap-2">
            <div class="glass rounded-xl p-3 flex-1 overflow-hidden flex flex-col relative border border-yellow-500/20">
                <div class="flex justify-between items-center mb-2 border-b border-white/10 pb-2">
                    <h3 class="font-bold text-yellow-400 text-sm flex gap-2"><i data-lucide="trophy" class="w-4 h-4"></i> LİDERLİK TABLOSU</h3>
                    <span class="text-[10px] bg-green-500/20 text-green-300 px-2 py-0.5 rounded animate-pulse">CANLI</span>
                </div>
                <div id="leaderboardList" class="overflow-y-auto space-y-1 text-xs flex-1 pr-1">
                    <div class="text-center text-slate-500 py-4">Sıralama yükleniyor...</div>
                </div>
            </div>
            
            <div class="glass rounded-xl p-4 flex flex-col items-center justify-center shrink-0 relative">
                <button id="mainBtn" onclick="handleClick(event)" class="pulse-btn w-24 h-24 rounded-full bg-gradient-to-br from-blue-600 to-indigo-800 flex items-center justify-center shadow-xl border-4 border-white/10 active:scale-95 transition-transform"><i data-lucide="zap" class="w-10 h-10 text-white fill-yellow-400"></i></button>
                <div class="mt-2 text-center text-xs text-slate-400">Tık Gücü: <strong class="text-white" id="clickPower">1</strong> ₺</div>
                <button onclick="resetGame()" class="absolute top-2 right-2 text-red-500/50 hover:text-red-500 p-1"><i data-lucide="trash" class="w-3 h-3"></i></button>
            </div>
        </div>

        <div class="w-full md:w-2/3 glass rounded-xl flex flex-col overflow-hidden">
            <div class="p-3 border-b border-white/5 bg-black/20 flex justify-between items-center shrink-0">
                <h2 class="font-bold text-sm flex gap-2"><i data-lucide="shopping-cart" class="w-4 h-4 text-purple-400"></i> YATIRIMLAR</h2>
            </div>
            <div id="marketList" class="flex-1 overflow-y-auto p-2 space-y-2"></div>
        </div>
    </div>

    <div id="rewardPopup" class="fixed inset-0 bg-black/90 flex items-center justify-center z-50 hidden">
        <div class="bg-slate-900 border border-yellow-500 p-6 rounded-2xl text-center max-w-sm mx-4 shadow-2xl relative">
            <div class="absolute -top-10 left-1/2 -translate-x-1/2 bg-yellow-500 p-3 rounded-full shadow-lg border-4 border-slate-900"><i data-lucide="gift" class="w-8 h-8 text-black"></i></div>
            <h2 class="text-xl font-bold text-white mt-4 mb-1">TEBRİKLER!</h2>
            <p class="text-sm text-gray-400 mb-4">Eğitim görevini tamamladın.</p>
            <div class="text-3xl font-black text-green-400 mb-6">+ <span id="rewardAmt">0</span> ₺</div>
            <button onclick="claim()" class="w-full py-2 bg-yellow-500 hover:bg-yellow-400 text-black font-bold rounded-lg transition">KASAYA EKLE</button>
        </div>
    </div>

    <script>
        lucide.createIcons();
        let reward = __REWARD__;
        let user = "__USER__";
        let leaderboardData = __LB_DATA__;
        const INFLATION = 1.25;

        // INIT DATA
        const defaultGame = {
            money: 0, 
            buildings: [
                {id:0, name:"Limonata Tezgahı", cost:25, inc:1, count:0, icon:"citrus", color:"text-yellow-400"},
                {id:1, name:"Simit Arabası", cost:250, inc:4, count:0, icon:"bike", color:"text-orange-400"},
                {id:2, name:"YouTube Kanalı", cost:3500, inc:20, count:0, icon:"youtube", color:"text-red-500"},
                {id:3, name:"E-Ticaret", cost:45000, inc:90, count:0, icon:"shopping-bag", color:"text-blue-400"},
                {id:4, name:"Yazılım Ofisi", cost:600000, inc:500, count:0, icon:"code", color:"text-cyan-400"},
                {id:5, name:"Fabrika", cost:8500000, inc:3500, count:0, icon:"factory", color:"text-slate-400"},
                {id:6, name:"Banka", cost:120000000, inc:25000, count:0, icon:"landmark", color:"text-green-400"},
                {id:7, name:"Uzay İstasyonu", cost:1500000000, inc:100000, count:0, icon:"rocket", color:"text-purple-500"}
            ]
        };
        let game = JSON.parse(localStorage.getItem('finansSaveV7')) || defaultGame;

        // ONLOAD
        if(reward > 0) {
            document.getElementById('rewardAmt').innerText = reward.toLocaleString();
            document.getElementById('rewardPopup').classList.remove('hidden');
        }
        renderLB();
        renderMarket();
        updateUI();
        setInterval(() => {
            let cps = getCPS();
            if(cps > 0) { game.money += cps / 10; updateUI(); }
        }, 100);
        setInterval(() => { localStorage.setItem('finansSaveV7', JSON.stringify(game)); }, 3000);

        // FUNCTIONS
        function getCPS() { return game.buildings.reduce((a,b) => a + (b.count * b.inc), 0); }
        function getCost(b) { return Math.floor(b.cost * Math.pow(INFLATION, b.count)); }
        
        function updateUI() {
            document.getElementById('moneyDisplay').innerText = Math.floor(game.money).toLocaleString() + " ₺";
            document.getElementById('cpsDisplay').innerText = getCPS().toLocaleString();
            let power = Math.max(1, Math.floor(getCPS() * 0.01));
            document.getElementById('clickPower').innerText = power.toLocaleString();
            
            // Market Buttons
            game.buildings.forEach((b, i) => {
                let cost = getCost(b);
                let el = document.getElementById('btn-'+i);
                if(el) {
                    el.className = `market-item p-3 rounded-lg flex items-center justify-between cursor-pointer select-none ${game.money >= cost ? 'can-buy bg-slate-800' : 'locked bg-slate-900'}`;
                    el.querySelector('.cost').innerText = cost.toLocaleString() + " ₺";
                    el.querySelector('.count').innerText = b.count;
                }
            });
        }

        function renderMarket() {
            const list = document.getElementById('marketList');
            list.innerHTML = "";
            game.buildings.forEach((b, i) => {
                let div = document.createElement('div');
                div.id = 'btn-'+i;
                div.onclick = () => buy(i);
                div.innerHTML = `
                    <div class="flex items-center gap-3">
                        <div class="w-10 h-10 rounded bg-slate-700 flex items-center justify-center"><i data-lucide="${b.icon}" class="${b.color} w-5 h-5"></i></div>
                        <div><div class="font-bold text-sm text-white">${b.name}</div><div class="text-[10px] text-green-400">+${b.inc}/sn</div></div>
                    </div>
                    <div class="text-right"><div class="cost font-bold text-xs text-yellow-400">0</div><div class="count text-[10px] text-slate-500 bg-black/30 px-1 rounded inline-block">0</div></div>
                `;
                list.appendChild(div);
            });
            lucide.createIcons();
        }

        function handleClick(e) {
            let power = Math.max(1, Math.floor(getCPS() * 0.01));
            game.money += power;
            
            // Anim
            let el = document.createElement('div');
            el.className = 'click-anim font-bold text-green-400 text-xl';
            el.style.left = e.clientX + 'px';
            el.style.top = (e.clientY - 20) + 'px';
            el.innerText = "+" + power;
            document.body.appendChild(el);
            setTimeout(() => el.remove(), 800);
            
            updateUI();
            
            // Update LB locally for fun
            let me = leaderboardData.find(x => x.isMe);
            if(me) { me.score = game.money; renderLB(); }
        }

        function buy(id) {
            let b = game.buildings[id];
            let cost = getCost(b);
            if(game.money >= cost) {
                game.money -= cost;
                b.count++;
                updateUI();
            }
        }

        function claim() {
            game.money += reward;
            document.getElementById('rewardPopup').classList.add('hidden');
            updateUI();
        }

        function resetGame() {
            if(confirm("Her şeyi silip sıfırdan başlamak istiyor musun?")) {
                localStorage.removeItem('finansSaveV7');
                location.reload();
            }
        }

        function renderLB() {
            const list = document.getElementById('leaderboardList');
            list.innerHTML = "";
            leaderboardData.sort((a,b) => b.score - a.score);
            leaderboardData.slice(0, 10).forEach((p, i) => {
                let color = i===0 ? "text-yellow-400" : (i===1 ? "text-slate-300" : (i===2 ? "text-orange-400" : "text-slate-500"));
                let row = document.createElement('div');
                row.className = `flex justify-between items-center p-2 rounded ${p.isMe ? 'leader-item me' : 'leader-item hover:bg-white/5'}`;
                row.innerHTML = `
                    <div class="flex items-center gap-2 overflow-hidden">
                        <span class="font-black ${color} w-4 text-center">${i+1}</span>
                        <span class="truncate font-bold text-slate-200">${p.name}</span>
                    </div>
                    <span class="font-mono text-green-400">${Math.floor(p.score).toLocaleString()}</span>
                `;
                list.appendChild(row);
            });
        }
    </script>
</body>
</html>
"""

# --- EKRAN YÖNETİMİ ---
if st.session_state.ekran == 'giris':
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        <div class='giris-kart'>
            <h1>🎓 Bağarası ÇPAL</h1>
            <h2>Finans & Eğitim Ekosistemi</h2>
            <hr>
            <p style="font-size:18px; font-weight:bold; color:#D84315;">
                Muhasebe ve Finansman Alanı Dijital Dönüşüm Projesi
            </p>
            <br>
            <p>Lütfen sisteme giriş yapmak için bilgilerinizi giriniz.</p>
        </div>
        """, unsafe_allow_html=True)
        
        ad_soyad_input = st.text_input("Adınız Soyadınız:", placeholder="Örn: Mehmet Karaduman")
        st.write("")
        if st.button("SİSTEME GİRİŞ YAP ➡️"):
            if ad_soyad_input.strip():
                st.session_state.ad_soyad = ad_soyad_input
                st.session_state.ekran = 'sinav'
                st.rerun()
            else:
                st.error("Lütfen adınızı giriniz!")
        
        st.markdown("<div class='footer-text'>Geliştirici: Zülfikar SITACI</div>", unsafe_allow_html=True)

elif st.session_state.ekran == 'sinav':
    with st.sidebar:
        st.image("https://cdn-icons-png.flaticon.com/512/2997/2997321.png", width=100)
        st.write(f"👤 **{st.session_state.ad_soyad}**")
        if st.button("🏠 Ana Menü"):
             st.session_state.oturum = False
             st.session_state.secim_turu = None
             st.rerun()
        st.divider()
        if st.button("🚪 Çıkış"):
            st.session_state.ekran = 'giris'
            st.session_state.oturum = False
            st.rerun()
        st.markdown("<div class='footer-text'>Geliştirici: Zülfikar SITACI</div>", unsafe_allow_html=True)

    # ANA MENÜ
    if not st.session_state.oturum and st.session_state.secim_turu not in ["LIFESIM", "GAME"]:
        st.markdown(f"<h2 style='text-align:center;'>Hoşgeldin {st.session_state.ad_soyad}, Bugün Ne Yapmak İstersin? 👇</h2><br>", unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("""<div class='secim-karti'><h3>📘 TYT Kampı</h3><p>Çıkmış Sorular</p></div>""", unsafe_allow_html=True)
            if st.button("TYT Başlat ➡️", key="btn_tyt"): st.session_state.secim_turu = "TYT"
        with col2:
            st.markdown("""<div class='secim-karti'><h3>💼 Meslek Lisesi</h3><p>Alan Dersleri</p></div>""", unsafe_allow_html=True)
            if st.button("Meslek Çöz ➡️", key="btn_meslek"): st.session_state.secim_turu = "MESLEK"
        
        st.markdown("---")
        
        col3, col4 = st.columns(2)
        with col3:
            st.markdown("""<div class='secim-karti' style='border-color:#38bdf8;'><h3>🧠 Life-Sim</h3><p>Yaşam Senaryoları</p></div>""", unsafe_allow_html=True)
            if st.button("Simülasyonu Başlat 🚀", key="btn_life", use_container_width=True): 
                st.session_state.secim_turu = "LIFESIM"
                st.rerun()
        with col4:
            st.markdown("""<div class='secim-karti' style='border-color:#fbbf24;'><h3>👑 Finans İmparatoru</h3><p>Kendi Şirketini Kur!</p></div>""", unsafe_allow_html=True)
            if st.button("Oyunu Başlat 🎮", key="btn_game", use_container_width=True): 
                st.session_state.secim_turu = "GAME"
                st.rerun()

    # OYUN
    elif st.session_state.secim_turu == "GAME":
        reward = st.session_state.bekleyen_odul
        st.session_state.bekleyen_odul = 0
        # Hibrid Leaderboard'u Getir
        lb_json = get_hybrid_leaderboard(st.session_state.ad_soyad, 0)
        
        html = GAME_HTML_TEMPLATE.replace("__REWARD__", str(reward))
        html = html.replace("__USER__", st.session_state.ad_soyad)
        html = html.replace("__LB_DATA__", lb_json)
        components.html(html, height=1000, scrolling=True)

    # SİMÜLASYON
    elif st.session_state.secim_turu == "LIFESIM":
        components.html(LIFE_SIM_HTML, height=600, scrolling=True)
        st.markdown("### 📝 Analiz Raporu")
        analiz_text = st.text_area("Bu senaryodan ne öğrendin? (En az 3 cümle yazmalısın)", height=100)
        
        if len(analiz_text) > 20: # 20 karakterden azsa buton çıkmaz
            if st.button("✅ Analizi Tamamla ve Ödülü Al (+250 ₺)", type="primary"):
                st.session_state.bekleyen_odul += 250
                st.session_state.secim_turu = "GAME"
                st.rerun()
        else:
            st.info("Ödül butonunun aktif olması için yukarıya mantıklı bir analiz yazmalısın.")

    # SORU ÇÖZÜMÜ
    elif st.session_state.oturum:
        # TYT SEÇİM EKRANI
        if st.session_state.secim_turu == "TYT" and not st.session_state.secilen_liste:
            test_id = st.selectbox("Hangi Testi Çözmek İstersin?", list(TYT_DATA_EMBEDDED.keys()), format_func=lambda x: TYT_DATA_EMBEDDED[x]["ders"])
            if st.button("Başlat"):
                st.session_state.secilen_liste = [test_id]
                st.session_state.mod = "TYT"
                st.rerun()
        
        # MESLEK SEÇİM EKRANI
        elif st.session_state.secim_turu == "MESLEK" and not st.session_state.secilen_liste:
            sinif = st.selectbox("Sınıf", list(MESLEK_DATA_EMBEDDED.keys()))
            ders = st.selectbox("Ders", list(MESLEK_DATA_EMBEDDED[sinif].keys()))
            konu = st.selectbox("Konu", list(MESLEK_DATA_EMBEDDED[sinif][ders].keys()))
            if st.button("Başlat"):
                st.session_state.secilen_liste = MESLEK_DATA_EMBEDDED[sinif][ders][konu]
                st.session_state.mod = "MESLEK"
                st.rerun()

        # TEST BİTİŞ EKRANI
        elif st.session_state.aktif_index >= len(st.session_state.secilen_liste):
            st.balloons()
            st.success(f"Tebrikler! Doğru: {st.session_state.dogru_sayisi} | Yanlış: {st.session_state.yanlis_sayisi}")
            odul = st.session_state.dogru_sayisi * 150
            if st.button(f"💰 {odul} ₺ Ödülü Al ve Şirketine Git"):
                st.session_state.bekleyen_odul += odul
                st.session_state.secim_turu = "GAME"
                st.session_state.oturum = False
                st.session_state.secilen_liste = []
                st.session_state.aktif_index = 0
                st.rerun()

        # SORU EKRANI (MESLEK)
        elif st.session_state.mod == "MESLEK":
            soru = st.session_state.secilen_liste[st.session_state.aktif_index]
            st.markdown(f"### Soru {st.session_state.aktif_index + 1}")
            st.info(soru["soru"])
            
            opts = soru["secenekler"]
            if "shuffled_opts" not in st.session_state:
                random.shuffle(opts)
                st.session_state.shuffled_opts = opts
            
            for opt in st.session_state.shuffled_opts:
                if st.button(opt, use_container_width=True):
                    if opt == soru["cevap"]:
                        st.toast("Doğru! 🎉")
                        st.session_state.dogru_sayisi += 1
                    else:
                        st.toast("Yanlış! ❌")
                        st.session_state.yanlis_sayisi += 1
                    del st.session_state.shuffled_opts
                    st.session_state.aktif_index += 1
                    time.sleep(0.5)
                    st.rerun()

        # SORU EKRANI (TYT)
        elif st.session_state.mod == "TYT":
            test_id = st.session_state.secilen_liste[0]
            data = TYT_DATA_EMBEDDED[test_id]
            st.markdown(f"### 📄 {data['ders']}")
            st.warning("TYT soruları için PDF kitapçığına bakınız.")
            
            with st.form("tyt_form"):
                for i in range(len(data["cevaplar"])):
                    st.radio(f"Soru {i+1}", ["A", "B", "C", "D", "E"], key=f"q{i}", horizontal=True, index=None)
                
                if st.form_submit_button("Testi Bitir"):
                    for i, dogru in enumerate(data["cevaplar"]):
                        secim = st.session_state.get(f"q{i}")
                        if secim == dogru: st.session_state.dogru_sayisi += 1
                        elif secim: st.session_state.yanlis_sayisi += 1
                        else: st.session_state.bos_sayisi += 1
                    st.session_state.aktif_index = 999 # Bitir
                    st.rerun()
