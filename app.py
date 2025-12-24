import streamlit as st
import streamlit.components.v1 as components
import random
import os
import json
import fitz  # PyMuPDF
import time
import pandas as pd # Veri okumak için gerekli

# --- 1. SAYFA AYARLARI ---
st.set_page_config(page_title="Bağarası Hibrit Yaşam Merkezi", page_icon="🎓", layout="wide")

# --- 2. SESSION STATE BAŞLATMA ---
if 'ekran' not in st.session_state: st.session_state.ekran = 'giris'
if 'oturum' not in st.session_state: st.session_state.oturum = False
if 'ad_soyad' not in st.session_state: st.session_state.ad_soyad = ""
if 'secim_turu' not in st.session_state: st.session_state.secim_turu = None 
if 'secilen_liste' not in st.session_state: st.session_state.secilen_liste = []
if 'aktif_index' not in st.session_state: st.session_state.aktif_index = 0
if 'karne' not in st.session_state: st.session_state.karne = []
if 'dogru_sayisi' not in st.session_state: st.session_state.dogru_sayisi = 0
if 'yanlis_sayisi' not in st.session_state: st.session_state.yanlis_sayisi = 0
if 'bos_sayisi' not in st.session_state: st.session_state.bos_sayisi = 0
if 'mod' not in st.session_state: st.session_state.mod = ""
if 'bekleyen_odul' not in st.session_state: st.session_state.bekleyen_odul = 0

# --- 3. DOSYA VE LİNK AYARLARI ---
TYT_PDF_ADI = "tytson8.pdf"
TYT_JSON_ADI = "tyt_data.json"
MESLEK_JSON_ADI = "sorular.json"
KONU_JSON_ADI = "konular.json"
LIFESIM_JSON_ADI = "lifesim_data.json"

# SENİN GOOGLE SHEETS LİNKİN (Canlı Liderlik Tablosu)
SHEET_ID = "1pHT6b-EiV3a_x3aLzYNu3tQmX10RxWeStD30C8Liqoo"
SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=0"

# --- 4. VERİ YÜKLEME FONKSİYONLARI ---
def dosya_yukle(dosya_adi):
    if not os.path.exists(dosya_adi): return {}
    try:
        with open(dosya_adi, "r", encoding="utf-8") as f:
            data = json.load(f)
            if dosya_adi == TYT_JSON_ADI:
                return {int(k): v for k, v in data.items()}
            return data
    except: return {}

def load_lifesim_data():
    if os.path.exists(LIFESIM_JSON_ADI):
        try:
            with open(LIFESIM_JSON_ADI, "r", encoding="utf-8") as f:
                raw = f.read()
                json.loads(raw); return raw 
        except: return "[]"
    return "[]"

def pdf_sayfa_getir(yol, sayfa):
    if not os.path.exists(yol): st.error("PDF yok"); return
    try:
        doc = fitz.open(yol)
        if sayfa > len(doc): return
        pix = doc.load_page(sayfa - 1).get_pixmap(dpi=150)
        st.image(pix.tobytes(), use_container_width=True)
    except: pass

@st.cache_data(ttl=60) # 60 saniyede bir veriyi yeniler (API kotasını korumak için)
def get_leaderboard_data():
    """Google Sheets'ten veriyi çeker ve JSON formatına çevirir"""
    try:
        df = pd.read_csv(SHEET_URL)
        # Sütun isimlerini kontrol et ve temizle
        if 'Isim' in df.columns and 'Puan' in df.columns:
            # Puana göre sırala (Büyükten küçüğe)
            df = df.sort_values(by='Puan', ascending=False).head(10)
            
            # JSON formatına çevir: [{'name': 'Ali', 'score': 5000}, ...]
            leaderboard_data = []
            for _, row in df.iterrows():
                leaderboard_data.append({
                    "name": str(row['Isim']),
                    "score": int(row['Puan']) if pd.notnull(row['Puan']) else 0
                })
            return json.dumps(leaderboard_data, ensure_ascii=False)
        else:
            return "[]" # Sütunlar yoksa boş dön
    except Exception as e:
        print(f"Liderlik tablosu hatası: {e}")
        return "[]" # Hata varsa boş dön

# Verileri Yükle
TYT_VERI = dosya_yukle(TYT_JSON_ADI)
MESLEK_VERI = dosya_yukle(MESLEK_JSON_ADI)
KONU_VERI = dosya_yukle(KONU_JSON_ADI)
SCENARIOS_JSON_STRING = load_lifesim_data()

# --- 5. HTML ŞABLONLARI ---

# A) LIFE-SIM ŞABLONU
LIFE_SIM_TEMPLATE = """
<!DOCTYPE html>
<html lang="tr">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<script src="https://cdn.tailwindcss.com"></script><script src="https://unpkg.com/lucide@latest"></script>
<script>tailwind.config = { theme: { extend: { colors: { bg: '#0f172a', surface: '#1e293b', primary: '#38bdf8', accent: '#f472b6', success: '#34d399', warning: '#fbbf24' } } } }</script>
<style>
body { background-color: #0f172a; color: #e2e8f0; font-family: 'Segoe UI', sans-serif; overflow: hidden; display: flex; flex-direction: column; height: 100vh; padding: 10px; }
.glass { background: rgba(30, 41, 59, 0.95); backdrop-filter: blur(12px); border: 1px solid rgba(255,255,255,0.08); }
::-webkit-scrollbar { width: 6px; } ::-webkit-scrollbar-track { background: #0f172a; } ::-webkit-scrollbar-thumb { background: #334155; border-radius: 4px; }
.tab-btn { transition: all 0.3s ease; border-bottom: 3px solid transparent; opacity: 0.6; } .tab-btn.active { border-bottom-color: #38bdf8; opacity: 1; color: white; background: rgba(56, 189, 248, 0.1); }
.tab-content { display: none; height: 100%; animation: fadeIn 0.4s ease; } .tab-content.active { display: flex; flex-direction: column; gap: 1rem; }
@keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
.info-card { position: absolute; top: 0; right: 0; bottom: 0; left: 0; background: rgba(15, 23, 42, 0.98); z-index: 50; transform: translateX(100%); transition: transform 0.4s cubic-bezier(0.16, 1, 0.3, 1); display: flex; flex-direction: column; } .info-card.show { transform: translateX(0); }
.btn-analyze { background: linear-gradient(135deg, #38bdf8 0%, #2563eb 100%); transition: all 0.3s; } .btn-analyze:hover { filter: brightness(1.1); transform: translateY(-1px); }
.btn-finish { background: linear-gradient(135deg, #34d399 0%, #059669 100%); }
.msg { padding: 12px 16px; border-radius: 12px; max-width: 85%; margin-bottom: 10px; } .msg-ai { background: rgba(56, 189, 248, 0.15); border-left: 4px solid #38bdf8; align-self: flex-start; color: #e0f2fe; } .msg-user { background: rgba(30, 41, 59, 0.8); border: 1px solid rgba(255,255,255,0.1); align-self: flex-end; color: #cbd5e1; }
</style>
</head>
<body>
<div class="flex gap-4 mb-2 shrink-0">
<button onclick="switchTab('scenario')" id="tab-btn-scenario" class="tab-btn active flex-1 py-3 glass rounded-lg font-bold text-lg flex items-center justify-center gap-2"><i data-lucide="book-open"></i> GÖREV</button>
<button onclick="switchTab('answer')" id="tab-btn-answer" class="tab-btn flex-1 py-3 glass rounded-lg font-bold text-lg flex items-center justify-center gap-2"><i data-lucide="message-circle"></i> İNTERAKTİF ANALİZ</button>
</div>
<div class="flex-1 overflow-hidden relative">
<div id="tab-scenario" class="tab-content active"><div class="glass p-4 rounded-xl border-l-4 border-accent shrink-0"><select id="scenarioSelect" onchange="loadScenario()" class="w-full bg-slate-900 text-white p-3 rounded border border-slate-700 outline-none"></select></div><div class="glass p-8 rounded-xl flex-1 flex flex-col relative overflow-hidden"><div class="flex justify-between items-start mb-6"><span id="categoryBadge" class="px-4 py-1 bg-blue-500/20 text-blue-400 text-sm font-bold rounded-full border border-blue-500/30">...</span></div><h2 id="scenarioTitle" class="text-3xl font-bold text-white mb-6 leading-tight">...</h2><div class="prose prose-invert text-lg text-slate-300 overflow-y-auto pr-3 flex-1 leading-relaxed" id="scenarioText"></div><div class="mt-8 flex justify-between"><button onclick="toggleHint()" class="text-sm text-warning hover:text-white transition-colors bg-yellow-900/20 px-4 py-2 rounded-lg border border-yellow-700/30">İpucu</button><div id="hintBox" class="hidden p-2 bg-yellow-900/20 text-yellow-200/90 italic"></div><button onclick="switchTab('answer')" class="bg-slate-700 hover:bg-slate-600 text-white rounded-xl px-6 py-3 font-bold">Analize Başla</button></div></div></div>
<div id="tab-answer" class="tab-content relative"><div id="knowledgeCard" class="info-card border-l-4 border-success shadow-2xl rounded-xl"><div class="p-6 border-b border-slate-700 flex justify-between items-center bg-slate-800/50"><h3 class="text-xl font-bold text-success flex items-center gap-2">UZMAN GÖRÜŞÜ</h3><button onclick="closeKnowledgeCard()" class="p-2 hover:bg-slate-700 rounded-full"><i data-lucide="x"></i></button></div><div id="knowledgeContent" class="p-8 text-slate-200 text-lg leading-8 space-y-6 overflow-y-auto flex-1"></div></div><div id="chatContainer" class="flex flex-col flex-1 overflow-y-auto glass rounded-xl p-4 mb-2"></div><div class="glass p-1 rounded-xl shrink-0 border border-slate-700 glow-border flex flex-col"><textarea id="inputText" class="w-full h-24 bg-transparent p-4 text-lg text-slate-200 resize-none outline-none font-light placeholder-slate-600" placeholder="Stratejini buraya yaz..."></textarea><div class="flex justify-between items-center bg-slate-800/50 p-2 rounded-b-xl"><span class="text-xs text-slate-500 ml-2" id="stepIndicator">Aşama 1/3</span><button id="analyzeBtn" onclick="analyzeSubmission()" class="btn-analyze text-white font-bold py-2 px-6 rounded-lg flex items-center gap-2 shadow-lg"><span>GÖNDER</span> <i data-lucide="send" class="w-4 h-4"></i></button></div></div><div id="expertBtnContainer" class="hidden absolute top-4 right-4 z-40"><button onclick="openKnowledgeCard()" class="bg-purple-600 hover:bg-purple-500 text-white px-4 py-2 rounded-full shadow-lg flex items-center gap-2 text-sm font-bold animate-bounce">UZMAN GÖRÜŞÜNÜ GÖR</button></div></div>
</div>
<script>
lucide.createIcons(); const scenarios = __SCENARIOS_PLACEHOLDER__; let selectedScenarioIndex = 0; let currentStep = 1;
window.onload = function() {
    const select = document.getElementById('scenarioSelect'); const categories = {};
    scenarios.forEach((s, index) => { if(!categories[s.category]) categories[s.category] = []; categories[s.category].push({ ...s, idx: index }); });
    for (const [cat, items] of Object.entries(categories)) { let group = document.createElement('optgroup'); group.label = cat.toUpperCase(); items.forEach(item => { let opt = document.createElement('option'); opt.value = item.idx; opt.innerHTML = item.title; group.appendChild(opt); }); select.appendChild(group); }
    loadScenario();
};
function switchTab(tabName) { document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active')); document.getElementById('tab-btn-' + tabName).classList.add('active'); document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active')); document.getElementById('tab-' + tabName).classList.add('active'); }
function loadScenario() {
    selectedScenarioIndex = document.getElementById('scenarioSelect').value; const s = scenarios[selectedScenarioIndex];
    switchTab('scenario'); document.getElementById('categoryBadge').innerText = s.category; document.getElementById('scenarioTitle').innerText = s.title; document.getElementById('scenarioText').innerHTML = s.text;
    currentStep = 1; document.getElementById('inputText').value = ""; document.getElementById('inputText').disabled = false; document.getElementById('hintBox').classList.add('hidden'); document.getElementById('expertBtnContainer').classList.add('hidden'); document.getElementById('knowledgeCard').classList.remove('show'); document.getElementById('stepIndicator').innerText = "Aşama 1/3";
    document.getElementById('chatContainer').innerHTML = `<div class="msg msg-ai">Merhaba! Bu senaryoyu dikkatlice okuduysan, ilk kararını ve gerekçeni aşağıya yaz.</div>`;
    const btn = document.getElementById('analyzeBtn'); btn.innerHTML = '<span>GÖNDER</span>'; btn.className = "btn-analyze text-white font-bold py-2 px-6 rounded-lg flex items-center gap-2 shadow-lg"; btn.disabled = false;
}
function addMessage(text, type) { const chat = document.getElementById('chatContainer'); const div = document.createElement('div'); div.className = `msg ${type === 'user' ? 'msg-user' : 'msg-ai'}`; div.innerHTML = text; chat.appendChild(div); chat.scrollTop = chat.scrollHeight; }
function analyzeSubmission() {
    const input = document.getElementById('inputText'); const text = input.value.trim(); const btn = document.getElementById('analyzeBtn');
    if (text.length < 10) { addMessage("Lütfen biraz daha detaylı yaz.", "msg-ai"); return; }
    addMessage(text, "msg-user"); input.value = ""; btn.disabled = true; btn.innerHTML = '⏳...';
    setTimeout(() => {
        let aiResponse = "";
        if (currentStep === 1) { aiResponse = "Güzel bir başlangıç. Peki riskleri ve alternatif maliyetleri düşündün mü? Biraz daha detaylandır."; currentStep++; document.getElementById('stepIndicator').innerText = "Aşama 2/3"; btn.disabled = false; btn.innerHTML = 'DEVAM ET'; }
        else if (currentStep === 2) { aiResponse = "Analizlerin kayda alındı. Şimdi uzman görüşünü inceleyip raporunu alabilirsin."; currentStep++; document.getElementById('stepIndicator').innerText = "Tamamlandı"; input.disabled = true; input.placeholder = "Bitti."; btn.className = "btn-finish text-white font-bold py-2 px-6 rounded-lg opacity-50"; btn.innerHTML = 'BİTTİ'; document.getElementById('expertBtnContainer').classList.remove('hidden'); }
        addMessage(aiResponse, "msg-ai");
    }, 800);
}
function openKnowledgeCard() { document.getElementById('knowledgeContent').innerHTML = scenarios[selectedScenarioIndex].doc; document.getElementById('knowledgeCard').classList.remove('hidden'); requestAnimationFrame(() => document.getElementById('knowledgeCard').classList.add('show')); }
function closeKnowledgeCard() { document.getElementById('knowledgeCard').classList.remove('show'); setTimeout(() => document.getElementById('knowledgeCard').classList.add('hidden'), 400); }
function toggleHint() { document.getElementById('hintBox').innerHTML = scenarios[selectedScenarioIndex].hint; document.getElementById('hintBox').classList.remove('hidden'); }
</script></body></html>
"""
LIFE_SIM_HTML = LIFE_SIM_TEMPLATE.replace("__SCENARIOS_PLACEHOLDER__", SCENARIOS_JSON_STRING)

# B) OYUN HTML (V4.0 - GERÇEK LİDERLİK TABLOSU ENTEGRASYONLU)
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
        .click-anim { position: absolute; animation: floatUp 0.8s ease-out forwards; pointer-events: none; font-weight: 800; color: #4ade80; z-index: 100; }
        @keyframes floatUp { 0% { transform: translateY(0) scale(1); opacity: 1; } 100% { transform: translateY(-100px) scale(1.5); opacity: 0; } }
        .pulse-btn { animation: pulse-glow 2s infinite; }
        @keyframes pulse-glow { 0% { box-shadow: 0 0 0 0 rgba(59, 130, 246, 0.7); } 70% { box-shadow: 0 0 0 20px rgba(59, 130, 246, 0); } 100% { box-shadow: 0 0 0 0 rgba(59, 130, 246, 0); } }
        .market-item { transition: all 0.2s; border-left: 4px solid transparent; }
        .market-item.can-buy { background: rgba(34, 197, 94, 0.1); border-left-color: #22c55e; cursor: pointer; }
        .market-item.can-buy:hover { transform: translateX(5px); background: rgba(34, 197, 94, 0.2); }
        .market-item.locked { opacity: 0.6; filter: grayscale(0.8); cursor: not-allowed; }
        .leader-item { transition: all 0.2s; }
        .leader-item:hover { background: rgba(255,255,255,0.1); transform: scale(1.02); }
        ::-webkit-scrollbar { width: 5px; } ::-webkit-scrollbar-track { background: #0f172a; } ::-webkit-scrollbar-thumb { background: #334155; border-radius: 5px; }
    </style>
</head>
<body class="h-screen flex flex-col p-2 md:p-4 gap-4 max-w-7xl mx-auto">
    <div class="glass rounded-2xl p-4 flex justify-between items-center shrink-0 border-t-4 border-blue-500">
        <div><span class="text-xs text-blue-300 font-bold tracking-widest uppercase">Toplam Servet</span><div class="flex items-center gap-2"><span class="text-3xl md:text-5xl font-black text-white" id="moneyDisplay">0</span><span class="text-xl text-yellow-400 font-bold">₺</span></div></div>
        <div class="text-right"><span class="text-xs text-green-400 font-bold tracking-widest uppercase">Saniyelik Kazanç</span><div class="flex items-center justify-end gap-1"><span class="text-2xl font-bold text-green-300">+</span><span class="text-2xl font-bold text-green-300" id="cpsDisplay">0</span></div></div>
    </div>
    <div class="flex flex-col md:flex-row gap-4 flex-1 overflow-hidden">
        <div class="w-full md:w-1/3 flex flex-col gap-4">
            <div class="glass rounded-2xl p-4 flex-1 overflow-hidden flex flex-col border border-yellow-500/20 relative">
                <div class="flex items-center justify-between mb-3 shrink-0">
                    <h3 class="font-bold text-yellow-400 flex items-center gap-2"><i data-lucide="trophy" class="w-5 h-5"></i> TOP 10 LİDER</h3>
                    <span class="text-xs bg-yellow-500/20 text-yellow-200 px-2 py-1 rounded animate-pulse">Canlı</span>
                </div>
                <div id="leaderboardList" class="overflow-y-auto space-y-2 pr-1 text-sm flex-1">
                    <div class="text-center text-slate-500 text-xs py-10">Veriler yükleniyor...</div>
                </div>
            </div>
            <div class="glass rounded-2xl p-4 flex flex-col items-center justify-center relative shrink-0">
                <button id="mainBtn" onclick="handleClick(event)" class="pulse-btn w-32 h-32 rounded-full bg-gradient-to-br from-blue-500 to-indigo-700 flex flex-col items-center justify-center shadow-2xl border-4 border-white/10 active:scale-95 transition-transform z-10"><i data-lucide="zap" class="w-12 h-12 text-white fill-yellow-400 stroke-none"></i></button>
                <p class="mt-2 text-center text-slate-400 text-xs">Tık Gücü: <strong class="text-white" id="clickPowerDisplay">1</strong> ₺</p>
                <div class="text-xs font-mono text-white/50 mt-1" id="playTimeDisplay">00:00</div>
                <button onclick="hardReset()" class="absolute top-2 right-2 p-1 text-red-400/50 hover:text-red-400"><i data-lucide="trash-2" class="w-4 h-4"></i></button>
            </div>
        </div>
        <div class="w-full md:w-2/3 glass rounded-2xl flex flex-col overflow-hidden">
            <div class="p-4 border-b border-white/5 bg-black/20 flex justify-between items-center shrink-0"><h2 class="font-bold text-lg flex items-center gap-2"><i data-lucide="shopping-cart" class="text-purple-400"></i> YATIRIMLAR</h2></div>
            <div id="marketList" class="flex-1 overflow-y-auto p-4 space-y-3"></div>
        </div>
    </div>
    <div id="rewardPopup" class="fixed inset-0 bg-black/80 flex items-center justify-center z-50 hidden">
        <div class="bg-gray-900 border-2 border-yellow-500 p-8 rounded-2xl text-center max-w-md mx-4 shadow-2xl shadow-yellow-500/20">
            <i data-lucide="gift" class="w-16 h-16 text-yellow-400 mx-auto mb-4"></i><h2 class="text-2xl font-bold text-white mb-2">TEBRİKLER!</h2><p class="text-gray-300 mb-6">Eğitim çalışmalarından bonus kazandın:</p><div class="text-4xl font-black text-green-400 mb-8">+ <span id="rewardAmountDisplay">0</span> ₺</div><button onclick="claimReward()" class="w-full py-3 bg-yellow-500 hover:bg-yellow-400 text-black font-bold rounded-xl transition transform hover:scale-105">HARİKA!</button>
        </div>
    </div>
    <script>
        let incomingReward = __REWARD_AMOUNT__;
        let playerName = "__USER_NAME__";
        // PYTHON'DAN GELEN CANLI LİDERLİK VERİSİ
        let cloudLeaderboard = __LEADERBOARD_JSON__; 
        const INFLATION_RATE = 1.15; 
        
        const defaultData = {
            money: 0, startTime: Date.now(),
            buildings: [
                { id: 0, name: "Limonata Tezgahı", baseCost: 15, income: 1, count: 0, icon: "citrus", color: "text-yellow-400", bg: "bg-yellow-400/20" },
                { id: 1, name: "Simit Arabası", baseCost: 100, income: 5, count: 0, icon: "bike", color: "text-orange-400", bg: "bg-orange-400/20" },
                { id: 2, name: "YouTube Kanalı", baseCost: 1100, income: 32, count: 0, icon: "youtube", color: "text-red-500", bg: "bg-red-500/20" },
                { id: 3, name: "E-Ticaret Sitesi", baseCost: 12000, income: 150, count: 0, icon: "shopping-bag", color: "text-blue-400", bg: "bg-blue-400/20" },
                { id: 4, name: "Yazılım Şirketi", baseCost: 130000, income: 800, count: 0, icon: "code", color: "text-cyan-400", bg: "bg-cyan-400/20" },
                { id: 5, name: "Fabrika", baseCost: 1400000, income: 5000, count: 0, icon: "factory", color: "text-slate-400", bg: "bg-slate-400/20" },
                { id: 6, name: "Kripto Borsası", baseCost: 20000000, income: 45000, count: 0, icon: "bitcoin", color: "text-yellow-500", bg: "bg-yellow-500/20" },
                { id: 7, name: "Uzay Madenciliği", baseCost: 330000000, income: 150000, count: 0, icon: "rocket", color: "text-purple-500", bg: "bg-purple-500/20" }
            ]
        };
        let game = { ...defaultData };

        window.onload = function() {
            lucide.createIcons(); loadGame();
            if (incomingReward > 0) { document.getElementById('rewardAmountDisplay').innerText = formatNumber(incomingReward); document.getElementById('rewardPopup').classList.remove('hidden'); }
            setInterval(passiveIncomeLoop, 1000); setInterval(uiLoop, 100); setInterval(saveGame, 5000);
            renderLeaderboard();
        };

        function renderLeaderboard() {
            // Cloud verisi boşsa veya hata varsa varsayılan göster
            let dataToShow = cloudLeaderboard;
            if(!dataToShow || dataToShow.length === 0) {
                // Eğer cloud boşsa oyuncunun kendisini göster
                dataToShow = [{name: playerName, score: game.money}];
            } else {
                // Oyuncuyu da listeye ekle (eğer listede yoksa görsel olarak ekle)
                // Not: Gerçek kaydetme için veritabanı yazma işlemi gerekir. Bu sadece görsel.
                let meFound = false;
                dataToShow.forEach(p => { if(p.name === playerName) { p.score = Math.max(p.score, game.money); p.isMe = true; meFound = true; }});
                if(!meFound) dataToShow.push({name: playerName, score: game.money, isMe: true});
            }
            
            // Sırala
            dataToShow.sort((a, b) => b.score - a.score);
            let top10 = dataToShow.slice(0, 10);
            
            const listEl = document.getElementById('leaderboardList');
            listEl.innerHTML = "";
            top10.forEach((p, idx) => {
                let rankColor = idx === 0 ? "text-yellow-400" : (idx === 1 ? "text-slate-300" : (idx === 2 ? "text-orange-400" : "text-slate-500"));
                let bgClass = p.isMe ? "bg-blue-600/30 border border-blue-500/50" : "bg-white/5 border border-transparent";
                let html = `<div class="leader-item flex items-center justify-between p-2 rounded-lg ${bgClass}"><div class="flex items-center gap-3 overflow-hidden"><span class="font-black ${rankColor} w-4 text-center">${idx + 1}</span><div class="flex flex-col min-w-0"><span class="font-bold text-white truncate text-xs">${p.name}</span></div></div><span class="font-mono text-xs text-green-400 font-bold">${formatNumber(p.score)} ₺</span></div>`;
                listEl.innerHTML += html;
            });
        }

        function claimReward() { game.money += incomingReward; incomingReward = 0; document.getElementById('rewardPopup').classList.add('hidden'); updateUI(); saveGame(); }
        function handleClick(e) { const cps = calculateCPS(); const power = Math.max(1, Math.floor(cps * 0.05)); game.money += power; showFloatingText(e.clientX, e.clientY, `+${formatNumber(power)}`); animateButton(); updateUI(); renderLeaderboard(); } // Tıklandıkça sıralamayı güncelle
        function buyItem(id) { const item = game.buildings[id]; const currentCost = calculateCost(item.baseCost, item.count); if (game.money >= currentCost) { game.money -= currentCost; item.count++; updateUI(); saveGame(); } }
        function passiveIncomeLoop() { const cps = calculateCPS(); if (cps > 0) game.money += cps; }
        function uiLoop() {
            updateUI();
            const diff = Math.floor((Date.now() - game.startTime) / 1000);
            const m = Math.floor(diff / 60).toString().padStart(2, '0'); const s = (diff % 60).toString().padStart(2, '0');
            document.getElementById('playTimeDisplay').innerText = `${m}:${s}`;
        }
        function calculateCost(base, count) { return Math.floor(base * Math.pow(INFLATION_RATE, count)); }
        function calculateCPS() { return game.buildings.reduce((total, item) => total + (item.count * item.income), 0); }
        function updateUI() {
            document.getElementById('moneyDisplay').innerText = formatNumber(game.money);
            const cps = calculateCPS();
            document.getElementById('cpsDisplay').innerText = formatNumber(cps);
            document.getElementById('clickPowerDisplay').innerText = formatNumber(Math.max(1, Math.floor(cps * 0.05)));
            const list = document.getElementById('marketList');
            if (list.children.length === 0) {
                game.buildings.forEach((item, index) => {
                    const div = document.createElement('div'); div.id = `item-${index}`; div.onclick = () => buyItem(index);
                    div.innerHTML = `<div class="flex items-center gap-4 relative z-10"><div class="w-14 h-14 rounded-xl ${item.bg} flex items-center justify-center text-2xl shadow-inner shrink-0"><i data-lucide="${item.icon}" class="${item.color}"></i></div><div class="flex-1 min-w-0"><div class="flex justify-between items-center"><h4 class="font-bold text-white text-lg truncate">${item.name}</h4><span class="text-xs bg-white/10 px-2 py-1 rounded text-white/70 count-badge">0</span></div><div class="flex justify-between items-center mt-1"><div class="text-xs text-green-400 font-mono">+${formatNumber(item.income)}/sn</div><div class="text-sm font-bold price-tag text-slate-400">0 ₺</div></div></div></div><div class="absolute bottom-0 left-0 h-1 bg-green-500/50 transition-all duration-300 progress-bar" style="width: 0%"></div>`;
                    list.appendChild(div);
                });
                lucide.createIcons();
            }
            game.buildings.forEach((item, index) => {
                const el = document.getElementById(`item-${index}`); const currentCost = calculateCost(item.baseCost, item.count); const canBuy = game.money >= currentCost;
                el.className = `market-item glass p-4 rounded-xl relative overflow-hidden group select-none ${canBuy ? 'can-buy' : 'locked'}`;
                el.querySelector('.count-badge').innerText = item.count;
                el.querySelector('.price-tag').innerText = formatNumber(currentCost) + " ₺";
                el.querySelector('.price-tag').className = `text-sm font-bold price-tag ${canBuy ? 'text-yellow-400' : 'text-red-400'}`;
                let progress = Math.min(100, (game.money / currentCost) * 100);
                el.querySelector('.progress-bar').style.width = `${progress}%`;
            });
        }
        function showFloatingText(x, y, text) { const el = document.createElement('div'); el.className = 'click-anim text-2xl'; el.style.left = `${x}px`; el.style.top = `${y - 20}px`; el.innerText = text; document.body.appendChild(el); setTimeout(() => el.remove(), 800); }
        function animateButton() { const btn = document.getElementById('mainBtn'); btn.style.transform = "scale(0.95)"; setTimeout(() => btn.style.transform = "scale(1)", 50); }
        function formatNumber(num) { if (num >= 1000000000) return (num / 1000000000).toFixed(2) + " Mr"; if (num >= 1000000) return (num / 1000000).toFixed(2) + " M"; if (num >= 1000) return (num / 1000).toFixed(1) + " k"; return Math.floor(num).toLocaleString('tr-TR'); }
        function saveGame() { const saveData = { money: game.money, startTime: game.startTime, buildings: game.buildings.map(b => ({ id: b.id, count: b.count })) }; localStorage.setItem('finansV3Save', JSON.stringify(saveData)); }
        function loadGame() { const saved = localStorage.getItem('finansV3Save'); if (saved) { try { const parsed = JSON.parse(saved); game.money = parsed.money || 0; game.startTime = parsed.startTime || Date.now(); if (parsed.buildings) { parsed.buildings.forEach(b => { if (game.buildings[b.id]) { game.buildings[b.id].count = b.count; } }); } } catch (e) {} } }
        function hardReset() { if(confirm("TÜM İLERLEMEN SİLİNECEK! Emin misin?")) { localStorage.removeItem('finansV3Save'); location.reload(); } }
    </script>
</body>
</html>
"""

# --- EKRAN YÖNETİMİ ---
if st.session_state.ekran == 'giris':
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""<div class='giris-kart'><h1>🎓 Bağarası ÇPAL</h1><h2>Hibrit Yaşam & Eğitim Merkezi</h2><hr><p style="font-size:18px; font-weight:bold; color:#D84315;">Geleceğe Hazırlık Simülasyonu</p><br><p>Lütfen sisteme giriş yapmak için bilgilerinizi giriniz.</p></div>""", unsafe_allow_html=True)
        ad_soyad_input = st.text_input("Adınız Soyadınız:", placeholder="Örn: Mehmet Karaduman")
        st.write("")
        if st.button("SİSTEME GİRİŞ YAP ➡️"):
            if ad_soyad_input.strip():
                st.session_state.ad_soyad = ad_soyad_input
                st.session_state.ekran = 'sinav'
                st.rerun()
            else: st.error("Lütfen adınızı giriniz!")
        st.markdown("""<div class='imza-container'><div class='imza'>Zülfikar SITACI & Mustafa BAĞCIK</div></div>""", unsafe_allow_html=True)

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

    # ANA MENÜ
    if not st.session_state.oturum and st.session_state.secim_turu not in ["LIFESIM", "GAME"]:
        st.markdown(f"<h2 style='text-align:center;'>Hoşgeldin {st.session_state.ad_soyad}, Bugün Ne Yapmak İstersin? 👇</h2><br>", unsafe_allow_html=True)
        
        st.header("1. Bölüm: 📝 Soru Çözüm Merkezi")
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("""<div class='secim-karti'><h3>📘 TYT Kampı</h3><p>Çıkmış Sorular</p></div>""", unsafe_allow_html=True)
            if st.button("TYT Başlat ➡️", key="btn_tyt"): st.session_state.secim_turu = "TYT"
        with c2:
            st.markdown("""<div class='secim-karti'><h3>💼 Meslek Lisesi</h3><p>Alan Dersleri</p></div>""", unsafe_allow_html=True)
            if st.button("Meslek Çöz ➡️", key="btn_meslek"): st.session_state.secim_turu = "MESLEK"
        
        st.markdown("---")
        
        st.header("2. Bölüm: 🎮 Simülasyon & Oyun")
        c3, c4 = st.columns(2)
        with c3:
            st.markdown("""<div class='secim-karti' style='border-color:#38bdf8;'><h3>🧠 Life-Sim</h3><p>Yaşam Senaryoları</p></div>""", unsafe_allow_html=True)
            if st.button("Simülasyonu Başlat 🚀", key="btn_life", use_container_width=True): 
                st.session_state.secim_turu = "LIFESIM"
                st.rerun()
        with c4:
            st.markdown("""<div class='secim-karti' style='border-color:#fbbf24;'><h3>👑 Finans İmparatoru</h3><p>Kendi Şirketini Kur!</p></div>""", unsafe_allow_html=True)
            if st.button("Oyunu Başlat 🎮", key="btn_game", use_container_width=True): 
                st.session_state.secim_turu = "GAME"
                st.rerun()

        st.divider()

    # OYUN SAYFASI (ÖDÜL VE LİDERLİK TABLOSU ENTEGRASYONLU)
    if st.session_state.secim_turu == "GAME":
        reward_val = st.session_state.bekleyen_odul
        st.session_state.bekleyen_odul = 0 
        
        # Google Sheet'ten gelen veriyi al
        leaderboard_json = get_leaderboard_data()
        
        # Kullanıcı adını, ödülü ve liderlik verisini JS'e gönder
        final_game_html = GAME_HTML_TEMPLATE.replace("__REWARD_AMOUNT__", str(reward_val))
        final_game_html = final_game_html.replace("__USER_NAME__", st.session_state.ad_soyad)
        final_game_html = final_game_html.replace("__LEADERBOARD_JSON__", leaderboard_json)
        
        components.html(final_game_html, height=1000, scrolling=True)

    # LIFE-SIM SAYFASI
    elif st.session_state.secim_turu == "LIFESIM":
        col_ls_1, col_ls_2 = st.columns([3, 1])
        with col_ls_1:
            components.html(LIFE_SIM_HTML, height=800, scrolling=True)
        with col_ls_2:
            st.info("Senaryoyu tamamladıysan ödülünü al!")
            if st.button("✅ Senaryoyu Bitirdim (+250 ₺)", use_container_width=True):
                st.session_state.bekleyen_odul += 250
                st.session_state.secim_turu = "GAME"
                st.rerun()

    # SINAV MOTORU
    elif st.session_state.oturum:
        if st.session_state.aktif_index >= len(st.session_state.secilen_liste):
            st.balloons()
            st.markdown(f"<h2 style='text-align:center;'>🏁 Sınav Tamamlandı!</h2>", unsafe_allow_html=True)
            
            c1, c2, c3 = st.columns(3)
            c1.markdown(f"<div class='stat-card'><div class='stat-number' style='color:#4caf50'>{st.session_state.dogru_sayisi}</div><div class='stat-label'>Doğru</div></div>", unsafe_allow_html=True)
            c2.markdown(f"<div class='stat-card'><div class='stat-number' style='color:#f44336'>{st.session_state.yanlis_sayisi}</div><div class='stat-label'>Yanlış</div></div>", unsafe_allow_html=True)
            c3.markdown(f"<div class='stat-card'><div class='stat-number' style='color:#ff9800'>{st.session_state.bos_sayisi}</div><div class='stat-label'>Boş</div></div>", unsafe_allow_html=True)
            
            st.markdown("---")
            
            kazanc = st.session_state.dogru_sayisi * 150
            
            if kazanc > 0:
                st.success(f"🎉 TEBRİKLER! Bu testten şirket sermayen için **{kazanc} ₺** kazandın!")
                
                if st.button(f"💰 {kazanc} ₺ Ödülü Al ve Şirketine Git 🚀", type="primary", use_container_width=True): 
                    st.session_state.bekleyen_odul += kazanc
                    st.session_state.oturum = False
                    st.session_state.secim_turu = "GAME"
                    st.rerun()
            else:
                st.warning("Maalesef hiç doğru yapamadığın için para kazanamadın. Tekrar dene!")
                if st.button("Ana Menüye Dön", use_container_width=True): 
                    st.session_state.oturum = False
                    st.rerun()
        
        elif st.session_state.mod == "MESLEK":
            soru = st.session_state.secilen_liste[st.session_state.aktif_index]
            st.subheader(f"❓ Soru {st.session_state.aktif_index + 1}")
            st.markdown(f"<div class='soru-karti'>{soru['soru']}</div>", unsafe_allow_html=True)
            
            if "secenekler_mix" not in st.session_state:
                s = soru["secenekler"].copy()
                random.shuffle(s)
                st.session_state.secenekler_mix = s
            
            for idx, sec in enumerate(st.session_state.secenekler_mix):
                if st.button(sec, key=f"btn_{idx}", use_container_width=True):
                    if sec.strip() == soru["cevap"].strip():
                        st.toast("Doğru! ✅", icon="✅")
                        st.session_state.dogru_sayisi += 1
                    else:
                        st.toast("Yanlış! ❌", icon="❌")
                        st.session_state.yanlis_sayisi += 1
                    
                    if "secenekler_mix" in st.session_state:
                        del st.session_state.secenekler_mix
                    time.sleep(0.5)
                    st.session_state.aktif_index += 1
                    st.rerun()

        elif st.session_state.mod == "PDF":
            s = st.session_state.secilen_liste[st.session_state.aktif_index]
            st.subheader(f"📄 {TYT_VERI[s]['ders']} - Sayfa {s}")
            
            c1, c2 = st.columns([1, 1])
            with c1: 
                pdf_sayfa_getir(TYT_PDF_ADI, s)
            with c2:
                with st.form(f"f_{s}"):
                    cevaplar = TYT_VERI[s]["cevaplar"]
                    st.write("Cevapları İşaretle:")
                    for i in range(len(cevaplar)): 
                        st.radio(f"Soru {i+1}", ["A","B","C","D","E"], key=f"c_{i}", horizontal=True, index=None)
                    
                    if st.form_submit_button("Sayfayı Kontrol Et ➡️"):
                        for i, dogru in enumerate(cevaplar):
                            secilen = st.session_state.get(f"c_{i}")
                            if dogru != "X":
                                if not secilen: st.session_state.bos_sayisi += 1
                                elif secilen == dogru: st.session_state.dogru_sayisi += 1
                                else: st.session_state.yanlis_sayisi += 1
                        st.session_state.aktif_index += 1
                        st.rerun()
