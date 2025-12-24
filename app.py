import streamlit as st
import streamlit.components.v1 as components
import random
import os
import time
import json
import fitz  # PyMuPDF

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Bağarası Hibrit Yaşam Merkezi", page_icon="🎓", layout="wide")

# --- DOSYA İSİMLERİ ---
TYT_PDF_ADI = "tytson8.pdf"
TYT_JSON_ADI = "tyt_data.json"
MESLEK_JSON_ADI = "sorular.json"
KONU_JSON_ADI = "konular.json"
LIFESIM_JSON_ADI = "lifesim_data.json"

# ==============================================================================
# VERİ YÜKLEME FONKSİYONLARI
# ==============================================================================

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
        .glass { background: rgba(30, 41, 59, 0.9); backdrop-filter: blur(12px); border: 1px solid rgba(255,255,255,0.08); }
        .glow-border:focus-within { box-shadow: 0 0 20px rgba(56, 189, 248, 0.2); border-color: #38bdf8; }
        ::-webkit-scrollbar { width: 6px; }
        ::-webkit-scrollbar-track { background: #0f172a; }
        ::-webkit-scrollbar-thumb { background: #334155; border-radius: 4px; }
        .tab-btn { transition: all 0.3s ease; border-bottom: 3px solid transparent; opacity: 0.6; }
        .tab-btn.active { border-bottom-color: #38bdf8; opacity: 1; color: white; background: rgba(56, 189, 248, 0.1); }
        .tab-content { display: none; height: 100%; animation: fadeIn 0.4s ease; }
        .tab-content.active { display: flex; flex-direction: column; gap: 1rem; }
        @keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
        .info-card { 
            position: absolute; top: 0; right: 0; bottom: 0; left: 0; 
            background: rgba(15, 23, 42, 0.98); 
            z-index: 50; 
            transform: translateX(100%); 
            transition: transform 0.4s cubic-bezier(0.16, 1, 0.3, 1);
            display: flex; flex-direction: column;
        }
        .info-card.show { transform: translateX(0); }
        .btn-analyze { background: linear-gradient(135deg, #38bdf8 0%, #2563eb 100%); }
        .btn-analyze:hover { filter: brightness(1.1); }
    </style>
</head>
<body>
    <div class="flex gap-4 mb-2 shrink-0">
        <button onclick="switchTab('scenario')" id="tab-btn-scenario" class="tab-btn active flex-1 py-3 glass rounded-lg font-bold text-lg flex items-center justify-center gap-2">
            <i data-lucide="book-open"></i> GÖREV & SENARYO
        </button>
        <button onclick="switchTab('answer')" id="tab-btn-answer" class="tab-btn flex-1 py-3 glass rounded-lg font-bold text-lg flex items-center justify-center gap-2">
            <i data-lucide="edit-3"></i> ÇÖZÜM & ANALİZ
        </button>
    </div>

    <div class="flex-1 overflow-hidden relative">
        <div id="tab-scenario" class="tab-content active">
            <div class="glass p-4 rounded-xl border-l-4 border-accent shrink-0">
                <label class="text-xs text-slate-400 uppercase font-bold flex items-center gap-2">
                    <i data-lucide="map"></i> Hayat Senaryosu Seç
                </label>
                <select id="scenarioSelect" onchange="loadScenario()" class="w-full mt-2 bg-slate-900 text-white p-3 rounded border border-slate-700 outline-none focus:border-accent cursor-pointer hover:bg-slate-800 transition"></select>
            </div>
            
            <div class="glass p-8 rounded-xl flex-1 flex flex-col relative overflow-hidden">
                <div class="flex justify-between items-start mb-6">
                    <span id="categoryBadge" class="px-4 py-1 bg-blue-500/20 text-blue-400 text-sm font-bold rounded-full border border-blue-500/30">YÜKLENİYOR</span>
                </div>
                <h2 id="scenarioTitle" class="text-3xl font-bold text-white mb-6 leading-tight">...</h2>
                <div class="prose prose-invert text-lg text-slate-300 overflow-y-auto pr-3 flex-1 leading-relaxed" id="scenarioText"></div>
                
                <div class="mt-8 grid grid-cols-1 md:grid-cols-2 gap-4 border-t border-slate-700/50 pt-6">
                    <div>
                        <button onclick="toggleHint()" id="hintBtn" class="text-sm text-warning hover:text-white transition-colors flex items-center gap-2 bg-yellow-900/20 px-4 py-2 rounded-lg border border-yellow-700/30 w-full justify-center">
                            <i data-lucide="key"></i> İpucu Göster
                        </button>
                        <div id="hintBox" class="hidden p-4 bg-yellow-900/20 border border-yellow-600/30 rounded-lg text-base text-yellow-200/90 italic"></div>
                    </div>
                    <div class="flex flex-wrap gap-2 justify-end items-center" id="scenarioDataTags"></div>
                </div>
                <button onclick="switchTab('answer')" class="mt-4 w-full py-4 bg-slate-700 hover:bg-slate-600 text-white rounded-xl font-bold flex items-center justify-center gap-2 transition md:hidden">
                    Çözüme Başla <i data-lucide="arrow-right"></i>
                </button>
            </div>
        </div>

        <div id="tab-answer" class="tab-content relative">
            <div id="knowledgeCard" class="info-card border-l-4 border-success shadow-2xl rounded-xl">
                <div class="p-6 border-b border-slate-700 flex justify-between items-center bg-slate-800/50">
                    <h3 class="text-xl font-bold text-success flex items-center gap-2">
                        <i data-lucide="book-open-check"></i> UZMAN GÖRÜŞÜ & DERS NOTU
                    </h3>
                    <button onclick="closeKnowledgeCard()" class="p-2 hover:bg-slate-700 rounded-full transition">
                        <i data-lucide="x" class="w-6 h-6 text-slate-400"></i>
                    </button>
                </div>
                <div id="knowledgeContent" class="p-8 text-slate-200 text-lg leading-8 space-y-6 overflow-y-auto flex-1"></div>
                <div class="p-4 bg-slate-800/50 border-t border-slate-700 text-center">
                    <button onclick="downloadReport()" class="px-6 py-3 bg-success/20 hover:bg-success/30 text-success border border-success/50 rounded-lg font-bold flex items-center justify-center gap-2 mx-auto transition-all w-full md:w-auto">
                        <i data-lucide="download"></i> Analiz Raporunu İndir
                    </button>
                </div>
            </div>

            <div class="glass p-2 rounded-lg flex items-center justify-between shrink-0">
                <div class="flex gap-2">
                    <button onclick="setMode('text')" id="btn-text" class="flex items-center gap-2 px-4 py-2 rounded-lg bg-primary text-slate-900 font-bold text-sm transition-all"><i data-lucide="file-edit" class="w-4 h-4"></i> Yazı</button>
                    <button onclick="setMode('draw')" id="btn-draw" class="flex items-center gap-2 px-4 py-2 rounded-lg text-slate-400 hover:text-white hover:bg-slate-700 text-sm transition-all"><i data-lucide="pencil" class="w-4 h-4"></i> Çizim</button>
                </div>
                <div class="text-right px-4 flex items-center gap-2"><i data-lucide="timer" class="w-4 h-4 text-slate-500"></i><span id="timer" class="text-xl font-mono text-white font-bold">00:00</span></div>
            </div>

            <div class="glass p-1 rounded-xl flex-1 flex flex-col relative border border-slate-700 glow-border">
                <textarea id="inputText" class="w-full h-full bg-transparent p-6 text-xl text-slate-200 resize-none outline-none font-light leading-relaxed placeholder-slate-600" 
                placeholder="Bu durumda ne yaparsın? Kararının arkasındaki mantığı, riskleri ve fırsatları buraya yaz..."></textarea>
                <div id="drawContainer" class="hidden w-full h-full bg-slate-900 relative rounded-lg overflow-hidden">
                    <canvas id="drawingCanvas" class="w-full h-full block"></canvas>
                    <button onclick="clearCanvas()" class="absolute top-4 right-4 bg-slate-700 p-2 rounded hover:bg-red-500 transition text-white z-10" title="Temizle"><i data-lucide="trash" class="w-4 h-4"></i></button>
                </div>
            </div>
            
            <div class="glass p-0 rounded-xl overflow-hidden flex flex-col md:flex-row shrink-0 min-h-[140px]">
                <button id="analyzeBtn" onclick="analyzeSubmission()" class="btn-analyze text-white font-bold p-6 flex flex-col items-center justify-center gap-2 md:w-1/4 transition-all active:scale-95">
                    <i data-lucide="sparkles" class="w-8 h-8"></i>
                    <span class="text-lg">ANALİZ ET</span>
                </button>
                
                <div class="p-6 flex-1 bg-slate-800/80 flex items-center relative">
                    <div id="aiFeedback" class="text-base text-slate-300 leading-relaxed w-full">
                        <div class="flex items-center gap-3 text-slate-500">
                            <i data-lucide="bot" class="w-8 h-8"></i>
                            <p>Senaryoyu okuduktan sonra kararını yaz ve 'Analiz Et' butonuna bas.</p>
                        </div>
                    </div>
                    <button id="showDocBtn" onclick="openKnowledgeCard()" class="hidden absolute right-6 top-1/2 -translate-y-1/2 bg-purple-600 hover:bg-purple-500 text-white px-6 py-3 rounded-lg shadow-lg flex items-center gap-2 text-sm font-bold transition-all animate-bounce">
                        <i data-lucide="lightbulb" class="w-5 h-5"></i> UZMAN GÖRÜŞÜNÜ GÖR
                    </button>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        lucide.createIcons();
        const scenarios = __SCENARIOS_PLACEHOLDER__;
        let selectedScenarioIndex = 0;
        let startTime = Date.now();

        window.onload = function() {
            const select = document.getElementById('scenarioSelect');
            const categories = {};
            scenarios.forEach((s, index) => {
                if(!categories[s.category]) categories[s.category] = [];
                categories[s.category].push({ ...s, idx: index });
            });
            for (const [cat, items] of Object.entries(categories)) {
                let group = document.createElement('optgroup'); group.label = cat.toUpperCase();
                items.forEach(item => { 
                    let opt = document.createElement('option'); 
                    opt.value = item.idx; 
                    opt.innerHTML = item.title; 
                    group.appendChild(opt); 
                });
                select.appendChild(group);
            }
            loadScenario();
            setInterval(() => { 
                const d = Math.floor((Date.now() - startTime)/1000); 
                document.getElementById('timer').innerText = `${Math.floor(d/60).toString().padStart(2,'0')}:${(d%60).toString().padStart(2,'0')}`; 
            }, 1000);
            
            setupCanvas();
        };

        function switchTab(tabName) {
            document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
            document.getElementById('tab-btn-' + tabName).classList.add('active');
            document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
            document.getElementById('tab-' + tabName).classList.add('active');
            if(tabName === 'answer') resizeCanvas();
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
            s.data.forEach(d => {
                tags.innerHTML += `<span class="px-3 py-1 bg-slate-700 rounded-full text-sm text-primary border border-slate-600 font-mono">${d}</span>`;
            });

            document.getElementById('inputText').value = "";
            document.getElementById('hintBox').classList.add('hidden');
            document.getElementById('hintBtn').classList.remove('hidden');
            document.getElementById('aiFeedback').innerHTML = `<div class="flex items-center gap-3 text-slate-500"><i data-lucide="bot" class="w-8 h-8"></i><p>Bekleniyor...</p></div>`;
            document.getElementById('showDocBtn').classList.add('hidden');
            document.getElementById('knowledgeCard').classList.remove('show');
            
            const btn = document.getElementById('analyzeBtn');
            btn.innerHTML = '<i data-lucide="sparkles" class="w-8 h-8"></i><span class="text-lg">ANALİZ ET</span>';
            btn.disabled = false;
            btn.classList.remove('opacity-50');
        }

        function analyzeSubmission() {
            const text = document.getElementById('inputText').value.trim().toLowerCase();
            const btn = document.getElementById('analyzeBtn');
            const feedback = document.getElementById('aiFeedback');
            
            if (text.length < 15) {
                feedback.innerHTML = "<span class='text-warning font-bold flex items-center gap-2'><i data-lucide='alert-triangle'></i> Çok kısa yazdın. Biraz daha detaylandır.</span>";
                lucide.createIcons();
                return;
            }

            btn.innerHTML = '⏳';
            btn.disabled = true;
            btn.classList.add('opacity-50');
            feedback.innerHTML = "<span class='text-primary animate-pulse'>Yapay zeka stratejini inceliyor... Riskler hesaplanıyor...</span>";

            setTimeout(() => {
                let msg = "";
                if (text.includes("nakit") || text.includes("peşin")) {
                    msg = "<span class='text-white font-bold'>🤔 Nakit tercih ettin.</span><br>Peki acil durum fonunu tamamen tüketmek, bu belirsiz ekonomide seni savunmasız bırakmaz mı?";
                } else if (text.includes("taksit") || text.includes("kredi")) {
                    msg = "<span class='text-white font-bold'>🤔 Borçlanmayı seçtin.</span><br>Peki aylık ödeme yükü, gelecekteki nakit akışını kilitlerse ne yapacaksın?";
                } else if (text.includes("dava") || text.includes("mahkeme")) {
                    msg = "<span class='text-white font-bold'>⚖ Hukuki yolu seçtin.</span><br>Haklısın ama davanın yıllarca süreceğini ve bu süreçteki stres maliyetini hesaba kattın mı?";
                } else if (text.includes("uzlaş")) {
                    msg = "<span class='text-success font-bold'>🤝 Uzlaşmayı seçtin.</span><br>Bazen haktan feragat etmek, huzuru satın almaktır. Bu pragmatik bir yaklaşım.";
                } else {
                    msg = "<span class='text-white font-bold'>Analiz Tamamlandı.</span><br>Yaklaşımın ilginç. Kararın finansal ve etik boyutlarını tam olarak görmek ister misin?";
                }

                feedback.innerHTML = msg;
                btn.innerHTML = '<i data-lucide="check" class="w-8 h-8"></i><span>BİTTİ</span>';
                document.getElementById('showDocBtn').classList.remove('hidden');
                lucide.createIcons();
            }, 1500);
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
            const ans = document.getElementById('inputText').value;
            const txt = `KONU: ${s.title}\\nCEVAP: ${ans}\\n\\nUZMAN NOTU:\\n${s.doc.replace(/<[^>]*>/g, '')}`;
            const blob = new Blob([txt], {type: 'text/plain'});
            const a = document.createElement('a');
            a.href = URL.createObjectURL(blob);
            a.download = 'Analiz_Raporu.txt';
            a.click();
        }

        function setMode(mode) {
            if(mode === 'text') {
                document.getElementById('inputText').style.display = 'block';
                document.getElementById('drawContainer').classList.add('hidden');
            } else {
                document.getElementById('inputText').style.display = 'none';
                document.getElementById('drawContainer').classList.remove('hidden');
                resizeCanvas();
            }
        }

        let isDrawing = false; let ctx;
        function setupCanvas() { 
            const c = document.getElementById('drawingCanvas'); 
            ctx = c.getContext('2d'); 
            ['mousedown','touchstart'].forEach(e=>c.addEventListener(e,ev=>{ev.preventDefault();startDraw(ev.touches?ev.touches[0]:ev)})); 
            ['mousemove','touchmove'].forEach(e=>c.addEventListener(e,ev=>{ev.preventDefault();draw(ev.touches?ev.touches[0]:ev)})); 
            ['mouseup','touchend'].forEach(e=>c.addEventListener(e,()=>isDrawing=false)); 
        }
        function resizeCanvas() { 
            const c=document.getElementById('drawingCanvas'); 
            const p=document.getElementById('drawContainer'); 
            if(c.width!==p.offsetWidth){c.width=p.offsetWidth;c.height=p.offsetHeight;ctx.strokeStyle='#38bdf8';ctx.lineWidth=2;} 
        }
        function startDraw(e) { isDrawing=true; const r=e.target.getBoundingClientRect(); ctx.beginPath(); ctx.moveTo(e.clientX-r.left, e.clientY-r.top); }
        function draw(e) { if(!isDrawing)return; const r=e.target.getBoundingClientRect(); ctx.lineTo(e.clientX-r.left, e.clientY-r.top); ctx.stroke(); }
        function clearCanvas() { ctx.clearRect(0,0,document.getElementById('drawingCanvas').width, document.getElementById('drawingCanvas').height); }
        
        window.addEventListener('resize', () => { resizeCanvas(); });
    </script>
</body>
</html>
"""

# ENJEKSİYON YAPILIYOR
LIFE_SIM_HTML = HTML_TEMPLATE.replace("__SCENARIOS_PLACEHOLDER__", SCENARIOS_JSON_STRING)

# --- TASARIM VE CSS ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Dancing+Script:wght@700&display=swap');
    
    .stApp { background-color: #F0F4C3 !important; }
    h1, h2, h3, h4, .stMarkdown, p, label { color: #212121 !important; }
    
    /* DROPDOWN DÜZELTMESİ */
    .stSelectbox div[data-baseweb="select"] > div {
        background-color: #FFFFFF !important;
        color: #000000 !important;
        border: 2px solid #FF7043;
    }
    
    .stDeployButton {display:none;}
    footer {visibility: hidden;}
    #MainMenu {visibility: hidden;}
    
    /* GİRİŞ KARTI */
    .giris-kart {
        background-color: white;
        padding: 40px;
        border-radius: 20px;
        border: 3px solid #FF7043;
        text-align: center;
        box-shadow: 0 10px 20px rgba(0,0,0,0.1);
        margin-bottom: 20px;
    }

    /* SEÇİM KARTLARI */
    .secim-karti {
        background-color: white;
        padding: 20px;
        border-radius: 15px;
        border: 2px solid #FF7043;
        text-align: center;
        transition: transform 0.2s;
        height: 150px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        cursor: pointer;
    }
    .secim-karti:hover {
        transform: scale(1.02);
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
    }
    
    /* BUTONLAR */
    .stButton>button {
        background-color: #FF7043 !important;
        color: white !important;
        border-radius: 8px;
        font-weight: bold;
        width: 100%;
        border: 2px solid #D84315 !important;
        min-height: 50px;
        font-size: 16px !important;
    }
    .stButton>button:hover {
        background-color: #E64A19 !important;
    }
    
    /* KARTLAR */
    .konu-karti { background-color: white; padding: 20px; border-radius: 10px; border-left: 6px solid #2196F3; margin-bottom: 15px; box-shadow: 0 2px 5px rgba(0,0,0,0.05); }
    .soru-karti { background-color: white; padding: 20px; border-radius: 10px; border-left: 5px solid #FF7043; font-size: 18px; margin-bottom: 20px; color: #000 !important; }
    .hata-karti { background-color: #FFEBEE; border-left: 5px solid #D32F2F; padding: 15px; margin-bottom: 15px; border-radius: 5px; color: #000; }
    .stat-card { background-color: white; padding: 15px; border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); text-align: center; border: 2px solid #FF7043; }
    .stat-number { font-size: 32px; font-weight: bold; color: #D84315; }
    
    /* İMZA */
    .imza-container { margin-top: 40px; text-align: right; padding-right: 20px; opacity: 0.9; }
    .imza { font-family: 'Dancing Script', cursive; color: #D84315; font-size: 24px; margin-bottom: 5px; }
    </style>
""", unsafe_allow_html=True)

# ==============================================================================
# EKRAN VE DEĞİŞKENLER
# ==============================================================================
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

# --- 1. GİRİŞ EKRANI ---
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
                st.session_state.karne = []
                st.session_state.dogru_sayisi = 0
                st.session_state.yanlis_sayisi = 0
                st.session_state.bos_sayisi = 0
                st.session_state.secim_turu = None 
                st.rerun()
            else:
                st.error("Lütfen adınızı giriniz!")
        
        st.markdown("""
        <div class='imza-container'>
            <div class='imza'>Zülfikar SITACI & Mustafa BAĞCIK</div>
        </div>
        """, unsafe_allow_html=True)

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

    # --- ANA MENÜ (SEÇİM EKRANI) ---
    if not st.session_state.oturum and st.session_state.secim_turu != "LIFESIM":
        
        st.markdown(f"<h2 style='text-align:center;'>Hoşgeldin {st.session_state.ad_soyad}, Bugün Ne Yapmak İstersin? 👇</h2><br>", unsafe_allow_html=True)
        
        # --- 1. GRUP: SORU ÇÖZÜM MERKEZİ ---
        st.header("1. Bölüm: 📝 Soru Çözüm Merkezi")
        col_a, col_b = st.columns(2)
        
        with col_a:
            st.markdown("""<div class='secim-karti'><h3>📘 TYT Kampı</h3><p>Çıkmış Sorular & Denemeler</p></div>""", unsafe_allow_html=True)
            if st.button("TYT Başlat ➡️", key="btn_tyt"): st.session_state.secim_turu = "TYT"
        
        with col_b:
            st.markdown("""<div class='secim-karti'><h3>💼 Meslek Lisesi</h3><p>Alan Dersleri & Konu Testleri</p></div>""", unsafe_allow_html=True)
            if st.button("Meslek Çöz ➡️", key="btn_meslek"): st.session_state.secim_turu = "MESLEK"

        st.markdown("---")

        # --- 2. GRUP: SİMÜLASYON ---
        st.header("2. Bölüm: 🎮 Gerçek Hayat Simülasyonu")
        st.markdown("""<div class='secim-karti' style='border-color:#38bdf8; height:120px;'><h3>🧠 Life-Sim</h3><p>Ekonomi, Hukuk ve Yönetim Senaryoları ile Kendini Dene!</p></div>""", unsafe_allow_html=True)
        if st.button("Simülasyonu Başlat 🚀", key="btn_life", use_container_width=True): 
            st.session_state.secim_turu = "LIFESIM"
            st.rerun()
        
        st.divider()
        
        # --- TYT AYARLARI ---
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
                
        # --- MESLEK AYARLARI ---
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

    # --- 3. MODÜL: LIFE-SIM (HTML ENTEGRASYONU) ---
    elif st.session_state.secim_turu == "LIFESIM":
        # Yüksekliği 1000px yaptık ki taşma olmasın ve scroll rahat çalışsın
        components.html(LIFE_SIM_HTML, height=1000, scrolling=True)

    # --- 4. MODÜL: KLASİK SINAV MOTORU ---
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
