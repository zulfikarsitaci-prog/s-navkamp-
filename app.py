import streamlit as st
import streamlit.components.v1 as components
import random
import os
import time
import json
import fitz  # PyMuPDF

# --- 1. SAYFA AYARLARI ---
st.set_page_config(page_title="Bağarası Hibrit Yaşam Merkezi", page_icon="🎓", layout="wide")

# --- 2. SESSION STATE BAŞLATMA (EN ÜSTTE) ---
if 'ekran' not in st.session_state: st.session_state.ekran = 'giris'
if 'oturum' not in st.session_state: st.session_state.oturum = False
if 'ad_soyad' not in st.session_state: st.session_state.ad_soyad = ""
if 'mod' not in st.session_state: st.session_state.mod = "" 
if 'secilen_liste' not in st.session_state: st.session_state.secilen_liste = []
if 'aktif_index' not in st.session_state: st.session_state.aktif_index = 0
if 'secim_turu' not in st.session_state: st.session_state.secim_turu = None 
if 'karne' not in st.session_state: st.session_state.karne = []
if 'dogru_sayisi' not in st.session_state: st.session_state.dogru_sayisi = 0
if 'yanlis_sayisi' not in st.session_state: st.session_state.yanlis_sayisi = 0
if 'bos_sayisi' not in st.session_state: st.session_state.bos_sayisi = 0

# --- 3. DOSYA İSİMLERİ ---
TYT_PDF_ADI = "tytson8.pdf"
TYT_JSON_ADI = "tyt_data.json"
MESLEK_JSON_ADI = "sorular.json"
KONU_JSON_ADI = "konular.json"
LIFESIM_JSON_ADI = "lifesim_data.json"

# --- 4. VERİ YÜKLEME FONKSİYONLARI ---
def dosya_yukle(dosya_adi):
    if not os.path.exists(dosya_adi): return {}
    try:
        with open(dosya_adi, "r", encoding="utf-8") as f:
            data = json.load(f)
            if dosya_adi == TYT_JSON_ADI:
                return {int(k): v for k, v in data.items()}
            return data
    except Exception as e:
        st.error(f"Dosya okuma hatası ({dosya_adi}): {e}")
        return {}

def load_lifesim_data():
    """LifeSim senaryolarını JSON dosyasından okur ve JS stringi olarak döndürür"""
    if os.path.exists(LIFESIM_JSON_ADI):
        try:
            with open(LIFESIM_JSON_ADI, "r", encoding="utf-8") as f:
                raw_data = f.read()
                json.loads(raw_data) # Validasyon
                return raw_data
        except Exception as e:
            st.error(f"Senaryo dosyası hatası: {e}")
            return "[]"
    else:
        return "[]"

def pdf_sayfa_getir(dosya_yolu, sayfa_numarasi):
    if not os.path.exists(dosya_yolu):
        st.error(f"⚠️ PDF Dosyası ({dosya_yolu}) bulunamadı!")
        return
    try:
        doc = fitz.open(dosya_yolu)
        if sayfa_numarasi > len(doc): return
        page = doc.load_page(sayfa_numarasi - 1)
        pix = page.get_pixmap(dpi=150)
        st.image(pix.tobytes(), caption=f"Sayfa {sayfa_numarasi}", use_container_width=True)
    except Exception as e:
        st.error(f"PDF Hatası: {e}")

# VERİLERİ YÜKLE
TYT_VERI = dosya_yukle(TYT_JSON_ADI)
MESLEK_VERI = dosya_yukle(MESLEK_JSON_ADI)
KONU_VERI = dosya_yukle(KONU_JSON_ADI)
SCENARIOS_JSON_STRING = load_lifesim_data()

# --- LIFE-SIM HTML ŞABLONU ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Life-Sim</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://unpkg.com/lucide@latest"></script>
    <script>
        tailwind.config = { theme: { extend: { colors: { bg: '#0f172a', surface: '#1e293b', primary: '#38bdf8', accent: '#f472b6', success: '#34d399', warning: '#fbbf24' } } } }
    </script>
    <style>
        body { background-color: #0f172a; color: #e2e8f0; font-family: 'Segoe UI', sans-serif; overflow: hidden; display: flex; flex-direction: column; height: 100vh; padding: 10px; }
        .glass { background: rgba(30, 41, 59, 0.95); backdrop-filter: blur(12px); border: 1px solid rgba(255,255,255,0.08); }
        .glow-border:focus-within { box-shadow: 0 0 20px rgba(56, 189, 248, 0.2); border-color: #38bdf8; }
        ::-webkit-scrollbar { width: 6px; }
        ::-webkit-scrollbar-track { background: #0f172a; }
        ::-webkit-scrollbar-thumb { background: #334155; border-radius: 4px; }
        .main-container { height: 95vh; display: flex; flex-direction: column; gap: 1rem; padding: 0.5rem; }
        @media (min-width: 768px) { .main-container { flex-direction: row; } }
        .panel { display: flex; flex-direction: column; gap: 1rem; height: 100%; overflow-y: auto; }
        .left-panel { flex: 4; }
        .right-panel { flex: 5; position: relative; }
        .msg-container { display: flex; flex-direction: column; gap: 10px; padding: 10px; overflow-y: auto; flex: 1; }
        .msg { padding: 12px 16px; border-radius: 12px; max-width: 85%; font-size: 0.95rem; line-height: 1.5; animation: popIn 0.3s ease; }
        .msg-ai { background: rgba(56, 189, 248, 0.15); border-left: 4px solid #38bdf8; align-self: flex-start; color: #e0f2fe; }
        .msg-user { background: rgba(30, 41, 59, 0.8); border: 1px solid rgba(255,255,255,0.1); align-self: flex-end; color: #cbd5e1; }
        @keyframes popIn { from { opacity: 0; transform: translateY(5px); } to { opacity: 1; transform: translateY(0); } }
        .info-card { position: absolute; top: 0; right: 0; bottom: 0; left: 0; background: rgba(15, 23, 42, 0.98); z-index: 50; transform: translateX(100%); transition: transform 0.4s cubic-bezier(0.16, 1, 0.3, 1); display: flex; flex-direction: column; }
        .info-card.show { transform: translateX(0); }
        .btn-analyze { background: linear-gradient(135deg, #38bdf8 0%, #2563eb 100%); transition: all 0.3s; }
        .btn-analyze:hover { filter: brightness(1.1); transform: translateY(-1px); }
        .btn-finish { background: linear-gradient(135deg, #34d399 0%, #059669 100%); }
        .tab-btn { transition: all 0.3s ease; border-bottom: 3px solid transparent; opacity: 0.6; }
        .tab-btn.active { border-bottom-color: #38bdf8; opacity: 1; color: white; background: rgba(56, 189, 248, 0.1); }
    </style>
</head>
<body>
    <div class="flex gap-4 mb-2 shrink-0">
        <button onclick="switchTab('scenario')" id="tab-btn-scenario" class="tab-btn active flex-1 py-3 glass rounded-lg font-bold text-lg flex items-center justify-center gap-2"><i data-lucide="book-open"></i> GÖREV</button>
        <button onclick="switchTab('answer')" id="tab-btn-answer" class="tab-btn flex-1 py-3 glass rounded-lg font-bold text-lg flex items-center justify-center gap-2"><i data-lucide="message-circle"></i> İNTERAKTİF ANALİZ</button>
    </div>
    <div class="flex-1 overflow-hidden relative">
        <div id="tab-scenario" class="panel hidden">
            <div class="glass p-4 rounded-xl border-l-4 border-accent shrink-0">
                <label class="text-xs text-slate-400 uppercase font-bold flex items-center gap-2"><i data-lucide="map"></i> Senaryo Seçimi</label>
                <select id="scenarioSelect" onchange="loadScenario()" class="w-full mt-2 bg-slate-900 text-white p-3 rounded border border-slate-700 outline-none focus:border-accent cursor-pointer hover:bg-slate-800 transition"></select>
            </div>
            <div class="glass p-8 rounded-xl flex-1 flex flex-col relative overflow-hidden mt-4">
                <div class="flex justify-between items-start mb-6"><span id="categoryBadge" class="px-4 py-1 bg-blue-500/20 text-blue-400 text-sm font-bold rounded-full border border-blue-500/30">YÜKLENİYOR</span></div>
                <h2 id="scenarioTitle" class="text-3xl font-bold text-white mb-6 leading-tight">...</h2>
                <div class="prose prose-invert text-lg text-slate-300 overflow-y-auto pr-3 flex-1 leading-relaxed" id="scenarioText"></div>
                <div class="mt-8 grid grid-cols-1 md:grid-cols-2 gap-4 border-t border-slate-700/50 pt-6">
                    <div>
                        <button onclick="toggleHint()" id="hintBtn" class="text-sm text-warning hover:text-white transition-colors flex items-center gap-2 bg-yellow-900/20 px-4 py-2 rounded-lg border border-yellow-700/30 w-full justify-center"><i data-lucide="key"></i> İpucu Göster</button>
                        <div id="hintBox" class="hidden p-4 bg-yellow-900/20 border border-yellow-600/30 rounded-lg text-base text-yellow-200/90 italic"></div>
                    </div>
                    <div class="flex flex-wrap gap-2 justify-end items-center" id="scenarioDataTags"></div>
                </div>
                <button onclick="switchTab('answer')" class="mt-4 w-full py-4 bg-slate-700 hover:bg-slate-600 text-white rounded-xl font-bold flex items-center justify-center gap-2 transition md:hidden">Analize Başla <i data-lucide="arrow-right"></i></button>
            </div>
        </div>
        <div id="tab-answer" class="panel right-panel relative flex flex-col">
            <div id="knowledgeCard" class="info-card border-l-4 border-success shadow-2xl rounded-xl">
                <div class="p-6 border-b border-slate-700 flex justify-between items-center bg-slate-800/50">
                    <h3 class="text-xl font-bold text-success flex items-center gap-2"><i data-lucide="check-circle-2"></i> UZMAN GÖRÜŞÜ & DOĞRU CEVAP</h3>
                    <button onclick="closeKnowledgeCard()" class="p-2 hover:bg-slate-700 rounded-full transition"><i data-lucide="x" class="w-6 h-6 text-slate-400"></i></button>
                </div>
                <div id="knowledgeContent" class="p-8 text-slate-200 text-lg leading-8 space-y-6 overflow-y-auto flex-1"></div>
                <div class="p-4 bg-slate-800/50 border-t border-slate-700 text-center">
                    <button onclick="downloadReport()" class="px-6 py-3 bg-success/20 hover:bg-success/30 text-success border border-success/50 rounded-lg font-bold flex items-center justify-center gap-2 mx-auto transition-all w-full md:w-auto"><i data-lucide="download"></i> Simülasyon Raporunu İndir</button>
                </div>
            </div>
            <div id="chatContainer" class="msg-container glass rounded-xl mb-2">
                <div class="msg msg-ai"><i data-lucide="bot" class="inline w-4 h-4 mr-2"></i>Merhaba! Bu senaryoyu dikkatlice okuduysan, ilk kararını ve gerekçeni aşağıya yaz. Finansal, hukuki ve etik açılardan değerlendireceğim.</div>
            </div>
            <div class="glass p-1 rounded-xl shrink-0 border border-slate-700 glow-border flex flex-col">
                <textarea id="inputText" class="w-full h-24 bg-transparent p-4 text-lg text-slate-200 resize-none outline-none font-light placeholder-slate-600" placeholder="Stratejini buraya yaz..."></textarea>
                <div class="flex justify-between items-center bg-slate-800/50 p-2 rounded-b-xl">
                    <span class="text-xs text-slate-500 ml-2" id="stepIndicator">Aşama 1/3</span>
                    <button id="analyzeBtn" onclick="analyzeSubmission()" class="btn-analyze text-white font-bold py-2 px-6 rounded-lg flex items-center gap-2 shadow-lg"><span>GÖNDER</span> <i data-lucide="send" class="w-4 h-4"></i></button>
                </div>
            </div>
            <div id="expertBtnContainer" class="hidden absolute top-4 right-4 z-40">
                <button onclick="openKnowledgeCard()" class="bg-purple-600 hover:bg-purple-500 text-white px-4 py-2 rounded-full shadow-lg flex items-center gap-2 text-sm font-bold transition-all animate-bounce"><i data-lucide="lightbulb" class="w-4 h-4"></i> UZMAN GÖRÜŞÜNÜ GÖR</button>
            </div>
        </div>
    </div>
    <script>
        lucide.createIcons();
        const scenarios = __SCENARIOS_PLACEHOLDER__;
        let selectedScenarioIndex = 0;
        let currentStep = 1;
        window.onload = function() {
            const select = document.getElementById('scenarioSelect');
            const categories = {};
            scenarios.forEach((s, index) => { if(!categories[s.category]) categories[s.category] = []; categories[s.category].push({ ...s, idx: index }); });
            for (const [cat, items] of Object.entries(categories)) {
                let group = document.createElement('optgroup'); group.label = cat.toUpperCase();
                items.forEach(item => { let opt = document.createElement('option'); opt.value = item.idx; opt.innerHTML = item.title; group.appendChild(opt); });
                select.appendChild(group);
            }
            loadScenario();
        };
        function switchTab(tabName) {
            document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
            document.getElementById('tab-btn-' + tabName).classList.add('active');
            if(tabName === 'scenario') {
                document.getElementById('tab-scenario').classList.remove('hidden');
                document.getElementById('tab-answer').classList.add('hidden');
            } else {
                document.getElementById('tab-scenario').classList.add('hidden');
                document.getElementById('tab-answer').classList.remove('hidden');
                document.getElementById('tab-answer').style.display = 'flex';
            }
        }
        function loadScenario() {
            selectedScenarioIndex = document.getElementById('scenarioSelect').value;
            const s = scenarios[selectedScenarioIndex];
            switchTab('scenario');
            document.getElementById('categoryBadge').innerText = s.category;
            document.getElementById('scenarioTitle').innerText = s.title;
            document.getElementById('scenarioText').innerHTML = s.text;
            const tags = document.getElementById('scenarioDataTags');
            tags.innerHTML = "";
            s.data.forEach(d => { tags.innerHTML += `<span class="px-3 py-1 bg-slate-700 rounded-full text-sm text-primary border border-slate-600 font-mono">${d}</span>`; });
            currentStep = 1;
            document.getElementById('inputText').value = "";
            document.getElementById('inputText').disabled = false;
            document.getElementById('hintBox').classList.add('hidden');
            document.getElementById('hintBtn').classList.remove('hidden');
            document.getElementById('expertBtnContainer').classList.add('hidden');
            document.getElementById('knowledgeCard').classList.remove('show');
            document.getElementById('stepIndicator').innerText = "Aşama 1/3";
            const chat = document.getElementById('chatContainer');
            chat.innerHTML = `<div class="msg msg-ai"><i data-lucide="bot" class="inline w-4 h-4 mr-2"></i>Bu senaryo için ilk stratejin nedir? Kararını ve nedenini yaz.</div>`;
            lucide.createIcons();
            const btn = document.getElementById('analyzeBtn');
            btn.innerHTML = '<span>GÖNDER</span> <i data-lucide="send" class="w-4 h-4"></i>';
            btn.className = "btn-analyze text-white font-bold py-2 px-6 rounded-lg flex items-center gap-2 shadow-lg";
            btn.disabled = false;
        }
        function addMessage(text, type) {
            const chat = document.getElementById('chatContainer');
            const div = document.createElement('div');
            div.className = `msg ${type === 'user' ? 'msg-user' : 'msg-ai'}`;
            div.innerHTML = text;
            chat.appendChild(div);
            chat.scrollTop = chat.scrollHeight;
            lucide.createIcons();
        }
        function analyzeSubmission() {
            const input = document.getElementById('inputText');
            const text = input.value.trim();
            const s = scenarios[selectedScenarioIndex];
            const btn = document.getElementById('analyzeBtn');
            if (text.length < 10) { addMessage("⚠ Lütfen biraz daha detaylı bir cevap yaz.", "msg-ai"); return; }
            addMessage(text, "msg-user");
            input.value = "";
            btn.disabled = true;
            btn.innerHTML = '⏳ Düşünüyor...';
            setTimeout(() => {
                let aiResponse = "";
                const lowerText = text.toLowerCase();
                if (currentStep === 1) {
                    if(lowerText.length < 50) { aiResponse = "Kararın net, ancak gerekçelerin biraz zayıf görünüyor. Bu kararın finansal veya hukuki uzun vadeli sonuçlarını hesaba kattın mı? Riskleri biraz daha açabilir misin?"; } 
                    else { aiResponse = "Güzel bir başlangıç. Peki bu kararı verirken senaryodaki verileri (Örn: " + s.data[0] + ") nasıl değerlendirdin? Alternatif maliyeti düşündün mü? Biraz daha detaylandır."; }
                    currentStep++;
                    document.getElementById('stepIndicator').innerText = "Aşama 2/3: Derinleşme";
                    btn.disabled = false;
                    btn.innerHTML = '<span>DEVAM ET</span> <i data-lucide="arrow-up" class="w-4 h-4"></i>';
                } else if (currentStep === 2) {
                    aiResponse = "Analizlerin kayda alındı. Yaklaşımın mantıklı temellere oturuyor. Şimdi bu konuda uzman görüşünü ve ideal stratejiyi görerek kendi cevabınla kıyaslayabilirsin. Sağ üstteki butona tıkla.";
                    currentStep++;
                    document.getElementById('stepIndicator').innerText = "Tamamlandı";
                    input.disabled = true;
                    input.placeholder = "Simülasyon tamamlandı.";
                    btn.className = "btn-finish text-white font-bold py-2 px-6 rounded-lg flex items-center gap-2 shadow-lg opacity-50 cursor-not-allowed";
                    btn.innerHTML = '<span>BİTTİ</span> <i data-lucide="check" class="w-4 h-4"></i>';
                    document.getElementById('expertBtnContainer').classList.remove('hidden');
                }
                addMessage(aiResponse, "msg-ai");
            }, 1000);
        }
        function openKnowledgeCard() {
            const s = scenarios[selectedScenarioIndex];
            document.getElementById('knowledgeContent').innerHTML = s.doc;
            document.getElementById('knowledgeCard').classList.remove('hidden');
            requestAnimationFrame(() => document.getElementById('knowledgeCard').classList.add('show'));
        }
        function closeKnowledgeCard() {
            document.getElementById('knowledgeCard').classList.remove('show');
            setTimeout(() => document.getElementById('knowledgeCard').classList.add('hidden'), 400);
        }
        function toggleHint() {
            const s = scenarios[selectedScenarioIndex];
            document.getElementById('hintBox').innerHTML = `💡 ${s.hint}`;
            document.getElementById('hintBox').classList.remove('hidden');
            document.getElementById('hintBtn').classList.add('hidden');
        }
        function downloadReport() {
            const s = scenarios[selectedScenarioIndex];
            let history = "";
            document.querySelectorAll('.msg').forEach(m => {
                history += m.classList.contains('msg-user') ? "ÖĞRENCİ: " : "SİSTEM: ";
                history += m.innerText + "\\n\\n";
            });
            const txt = `SİMÜLASYON RAPORU\\nKONU: ${s.title}\\n\\n--- DİYALOG GEÇMİŞİ ---\\n${history}\\n--- UZMAN NOTU ---\\n${s.doc.replace(/<[^>]*>/g, '')}`;
            const blob = new Blob([txt], {type: 'text/plain'});
            const a = document.createElement('a');
            a.href = URL.createObjectURL(blob);
            a.download = 'Simulasyon_Raporu.txt';
            a.click();
        }
    </script>
</body>
</html>
"""

LIFE_SIM_HTML = HTML_TEMPLATE.replace("__SCENARIOS_PLACEHOLDER__", SCENARIOS_JSON_STRING)

# --- TASARIM VE CSS ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Dancing+Script:wght@700&display=swap');
    .stApp { background-color: #F0F4C3 !important; }
    h1, h2, h3, h4, .stMarkdown, p, label { color: #212121 !important; }
    .stSelectbox div[data-baseweb="select"] > div { background-color: #FFFFFF !important; color: #000000 !important; border: 2px solid #FF7043; }
    .stDeployButton {display:none;}
    footer {visibility: hidden;}
    #MainMenu {visibility: hidden;}
    .giris-kart { background-color: white; padding: 40px; border-radius: 20px; border: 3px solid #FF7043; text-align: center; box-shadow: 0 10px 20px rgba(0,0,0,0.1); margin-bottom: 20px; }
    .secim-karti { background-color: white; padding: 20px; border-radius: 15px; border: 2px solid #FF7043; text-align: center; transition: transform 0.2s; height: 150px; display: flex; flex-direction: column; justify-content: center; align-items: center; cursor: pointer; }
    .secim-karti:hover { transform: scale(1.02); box-shadow: 0 5px 15px rgba(0,0,0,0.2); }
    .stButton>button { background-color: #FF7043 !important; color: white !important; border-radius: 8px; font-weight: bold; width: 100%; border: 2px solid #D84315 !important; min-height: 50px; font-size: 16px !important; }
    .stButton>button:hover { background-color: #E64A19 !important; }
    .konu-karti { background-color: white; padding: 20px; border-radius: 10px; border-left: 6px solid #2196F3; margin-bottom: 15px; box-shadow: 0 2px 5px rgba(0,0,0,0.05); }
    .soru-karti { background-color: white; padding: 20px; border-radius: 10px; border-left: 5px solid #FF7043; font-size: 18px; margin-bottom: 20px; color: #000 !important; }
    .hata-karti { background-color: #FFEBEE; border-left: 5px solid #D32F2F; padding: 15px; margin-bottom: 15px; border-radius: 5px; color: #000; }
    .stat-card { background-color: white; padding: 15px; border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); text-align: center; border: 2px solid #FF7043; }
    .stat-number { font-size: 32px; font-weight: bold; color: #D84315; }
    .imza-container { margin-top: 40px; text-align: right; padding-right: 20px; opacity: 0.9; }
    .imza { font-family: 'Dancing Script', cursive; color: #D84315; font-size: 24px; margin-bottom: 5px; }
    </style>
""", unsafe_allow_html=True)

# --- 1. GİRİŞ EKRANI ---
if st.session_state.ekran == 'giris':
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""<div class='giris-kart'><h1>🎓 Bağarası ÇPAL</h1><h2>Hibrit Yaşam & Eğitim Merkezi</h2><hr><p style="font-size:18px; font-weight:bold; color:#D84315;">Muhasebe ve Finansman Alanı Digital Dönüşüm Projesi </p><br><p>Lütfen sisteme giriş yapmak için bilgilerinizi giriniz.</p></div>""", unsafe_allow_html=True)
        ad_soyad_input = st.text_input("Adınız Soyadınız:", placeholder="Örn: Mehmet Karaduman")
        st.write("")
        if st.button("SİSTEME GİRİŞ YAP ➡️"):
            if ad_soyad_input.strip():
                st.session_state.ad_soyad = ad_soyad_input
                st.session_state.ekran = 'sinav'
                st.session_state.karne = []
                st.session_state.dogru_sayisi = 0
                st.session_state.yanlis_sayisi = 0
                st.session_state.bos_sayisi = 0
                st.session_state.secim_turu = None 
                st.rerun()
            else: st.error("Lütfen adınızı giriniz!")
        st.markdown("""<div class='imza-container'><div class='imza'>Zülfikar SITACI </div></div>""", unsafe_allow_html=True)

# --- 2. ANA KUMANDA MERKEZİ ---
elif st.session_state.ekran == 'sinav':
    with st.sidebar:
        st.image("https://cdn-icons-png.flaticon.com/512/2997/2997321.png", width=100)
        st.write(f"👤 **{st.session_state.ad_soyad}**")
        if st.button("🏠 Ana Ekrana Dön"):
             st.session_state.oturum = False
             st.session_state.secim_turu = None
             st.rerun()
        st.divider()
        if st.button("🚪 Çıkış Yap"):
            st.session_state.ekran = 'giris'
            st.session_state.oturum = False
            st.rerun()

    if not st.session_state.oturum and st.session_state.secim_turu != "LIFESIM":
        st.markdown(f"<h2 style='text-align:center;'>Hoşgeldin {st.session_state.ad_soyad}, Bugün Ne Yapmak İstersin? 👇</h2><br>", unsafe_allow_html=True)
        
        # 2 GRUPLU YENİ MENÜ DÜZENİ
        st.header(" 📝 Soru Çözüm Merkezi")
        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown("""<div class='secim-karti'><h3>📘 TYT Kampı</h3><p>Çıkmış Sorular & Denemeler</p></div>""", unsafe_allow_html=True)
            if st.button("TYT Başlat ➡️", key="btn_tyt"): st.session_state.secim_turu = "TYT"
        with col_b:
            st.markdown("""<div class='secim-karti'><h3>💼 Meslek Lisesi</h3><p>Alan Dersleri & Konu Testleri</p></div>""", unsafe_allow_html=True)
            if st.button("Meslek Çöz ➡️", key="btn_meslek"): st.session_state.secim_turu = "MESLEK"
        
        st.markdown("---")
        
        st.header(" 🎮 Gerçek Hayat Simülasyonu")
        st.markdown("""<div class='secim-karti' style='border-color:#38bdf8; height:120px;'><h3>🧠 Life-Sim</h3><p>Sokratik Yöntemle İnteraktif Yaşam Koçluğu</p></div>""", unsafe_allow_html=True)
        if st.button("Simülasyonu Başlat 🚀", key="btn_life", use_container_width=True): 
            st.session_state.secim_turu = "LIFESIM"
            st.rerun()
        
        st.divider()
        
        if st.session_state.secim_turu == "TYT":
            st.subheader("📘 TYT Ayarları")
            if TYT_VERI:
                dersler = sorted(list(set(v["ders"] for v in TYT_VERI.values())))
                ders = st.selectbox("Ders Seçiniz:", ["Karışık Deneme"] + dersler)
                adet = st.slider("Kaç Sayfa Çözmek İstersiniz?", 1, 10, 3)
                if st.button("SINAVI BAŞLAT 🚀"):
                    uygun = [s for s, d in TYT_VERI.items() if ders == "Karışık Deneme" or d["ders"] == ders]
                    if uygun:
                        random.shuffle(uygun)
                        st.session_state.secilen_liste = uygun[:adet]
                        st.session_state.mod = "PDF"
                        st.session_state.oturum = True
                        st.session_state.karne = [] 
                        st.session_state.aktif_index = 0
                        st.rerun()
                    else: st.error("Soru yok.")
            else: st.warning("TYT verisi yok.")
                
        elif st.session_state.secim_turu == "MESLEK":
            st.subheader("💼 Meslek Alanı")
            tab1, tab2 = st.tabs(["📝 TEST ÇÖZ", "📚 DERS NOTLARI"])
            with tab1:
                konu_verisi = MESLEK_VERI.get("KONU_TARAMA", {})
                if konu_verisi:
                    sinif = st.selectbox("Sınıf Seçiniz:", list(konu_verisi.keys()), key="s_konu")
                    sinif_dersleri = konu_verisi.get(sinif, {})
                    if sinif_dersleri:
                        ders = st.selectbox("Ders Seçiniz:", list(sinif_dersleri.keys()), key="d_konu")
                        testler = sinif_dersleri.get(ders, {})
                        if testler:
                            test = st.selectbox("Test Seçiniz:", list(testler.keys()), key="t_konu")
                            if st.button("TESTİ BAŞLAT 🚀", key="btn_konu"):
                                st.session_state.secilen_liste = testler[test]
                                st.session_state.mod = "MESLEK"
                                st.session_state.oturum = True
                                st.session_state.karne = [] 
                                st.session_state.aktif_index = 0
                                st.rerun()
                        else: st.warning("Test yok.")
                    else: st.warning("Ders yok.")
                else: st.warning("Veri yok.")
            with tab2:
                if KONU_VERI:
                    k_sinif = st.selectbox("Sınıf Seçiniz:", list(KONU_VERI.keys()), key="k_s")
                    k_dersler = KONU_VERI.get(k_sinif, {})
                    if k_dersler:
                        k_ders = st.selectbox("Ders Seçiniz:", list(k_dersler.keys()), key="k_d")
                        notlar = k_dersler.get(k_ders, [])
                        for not_maddesi in notlar:
                            st.markdown(f"<div class='konu-karti'><div class='konu-baslik'>{not_maddesi['baslik']}</div><div class='konu-icerik'>{not_maddesi['icerik']}</div></div>", unsafe_allow_html=True)

    elif st.session_state.secim_turu == "LIFESIM":
        components.html(LIFE_SIM_HTML, height=1000, scrolling=True)

    elif st.session_state.oturum:
        if st.session_state.aktif_index >= len(st.session_state.secilen_liste):
            st.balloons()
            st.markdown(f"<h2 style='text-align:center;'>🏁 Sınav Sonucu: {st.session_state.ad_soyad}</h2>", unsafe_allow_html=True)
            c1, c2, c3 = st.columns(3)
            c1.markdown(f"<div class='stat-card'><div class='stat-number'>{st.session_state.dogru_sayisi}</div><div class='stat-label'>Doğru</div></div>", unsafe_allow_html=True)
            c2.markdown(f"<div class='stat-card'><div class='stat-number'>{st.session_state.yanlis_sayisi}</div><div class='stat-label'>Yanlış</div></div>", unsafe_allow_html=True)
            c3.markdown(f"<div class='stat-card'><div class='stat-number'>{st.session_state.bos_sayisi}</div><div class='stat-label'>Boş</div></div>", unsafe_allow_html=True)
            if st.button("Ana Menüye Dön"): 
                st.session_state.oturum = False
                st.session_state.secim_turu = None
                st.rerun()
        
        elif st.session_state.mod == "MESLEK":
            soru = st.session_state.secilen_liste[st.session_state.aktif_index]
            st.subheader(f"❓ Soru {st.session_state.aktif_index + 1}")
            st.markdown(f"<div class='soru-karti'>{soru['soru']}</div>", unsafe_allow_html=True)
            if "secenekler_mix" not in st.session_state:
                s = soru["secenekler"].copy(); random.shuffle(s); st.session_state.secenekler_mix = s
            c1, c2 = st.columns(2)
            for idx, sec in enumerate(st.session_state.secenekler_mix):
                with (c1 if idx % 2 == 0 else c2):
                    if st.button(sec, key=f"btn_{idx}", use_container_width=True):
                        if sec.strip() == soru["cevap"].strip():
                            st.toast("Doğru! ✅"); st.session_state.dogru_sayisi += 1
                        else:
                            st.toast("Yanlış! ❌"); st.session_state.yanlis_sayisi += 1
                        del st.session_state.secenekler_mix; time.sleep(0.5); st.session_state.aktif_index += 1; st.rerun()

        elif st.session_state.mod == "PDF":
            sayfa = st.session_state.secilen_liste[st.session_state.aktif_index]
            st.subheader(f"📄 {TYT_VERI[sayfa]['ders']} - Sayfa {sayfa}")
            t1, t2 = st.tabs(["📄 KİTAPÇIK", "📝 CEVAP FORMU"])
            with t1: pdf_sayfa_getir(TYT_PDF_ADI, sayfa)
            with t2:
                with st.form(f"f_{sayfa}"):
                    cevaplar = TYT_VERI[sayfa]["cevaplar"]
                    for i in range(len(cevaplar)): st.radio(f"Soru {i+1}", ["A","B","C","D","E"], key=f"c_{i}", horizontal=True, index=None)
                    if st.form_submit_button("KONTROL ET ➡️"):
                        for i, dogru in enumerate(cevaplar):
                            secilen = st.session_state.get(f"c_{i}")
                            if dogru != "X":
                                if not secilen: st.session_state.bos_sayisi += 1
                                elif secilen == dogru: st.session_state.dogru_sayisi += 1
                                else: st.session_state.yanlis_sayisi += 1
                        st.session_state.aktif_index += 1; st.rerun()
