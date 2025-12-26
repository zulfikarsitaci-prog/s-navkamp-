import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import requests # İnternetten veri çekmek için gerekli
import json

# 1. SAYFA AYARLARI
st.set_page_config(
    page_title="Bağarası ÇPAL - Finans Ekosistemi",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ==========================================
# 🔗 GITHUB AYARLARI (BURAYI DÜZENLE)
# ==========================================
# Buraya lifesim_data.json dosyanın RAW linkini yapıştıracaksın.
# Örnek: "https://raw.githubusercontent.com/KULLANICI_ADI/REPO_ADI/main/lifesim_data.json"
GITHUB_JSON_URL = "https://raw.githubusercontent.com/zulfikarsitaci-prog/s-navkamp-/refs/heads/main/lifesim_data.json" 

# 2. LIFESIM HTML ŞABLONU (Değişmedi, aynı kalacak)
LIFESIM_HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Life-Sim v4.0</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://unpkg.com/lucide@latest"></script>
    <script>
        tailwind.config = {
            theme: {
                extend: {
                    colors: { bg: '#0f172a', surface: '#1e293b', primary: '#38bdf8', accent: '#818cf8', success: '#34d399', warning: '#fbbf24', danger: '#f87171' },
                    animation: { 'pulse-fast': 'pulse 1.5s cubic-bezier(0.4, 0, 0.6, 1) infinite' }
                }
            }
        }
    </script>
    <style>
        body { background-color: #f8f9fa; color: #1e293b; font-family: 'Segoe UI', sans-serif; }
        .glass { background: #ffffff; border: 1px solid #e2e8f0; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1); }
        .dark-glass { background: #1e293b; color: white; }
        .typing::after { content: '|'; animation: blink 1s step-start infinite; }
        @keyframes blink { 50% { opacity: 0; } }
        ::-webkit-scrollbar { width: 6px; }
        ::-webkit-scrollbar-track { background: #f1f5f9; }
        ::-webkit-scrollbar-thumb { background: #cbd5e1; border-radius: 3px; }
    </style>
</head>
<body class="min-h-screen p-2 md:p-4 flex flex-col md:flex-row gap-6 bg-slate-50">

    <div class="w-full md:w-1/3 flex flex-col gap-4">
        <div class="flex items-center gap-3 mb-1">
            <div class="bg-blue-100 p-2 rounded-lg relative">
                <i data-lucide="cpu" class="text-blue-600 w-8 h-8"></i>
            </div>
            <div>
                <h1 class="text-xl font-bold tracking-wider text-slate-800">SOCRATES-AI</h1>
                <p class="text-xs text-slate-500 font-mono">Maieutics Learning Protocol</p>
            </div>
        </div>

        <div class="glass p-4 rounded-xl border-l-4 border-blue-500">
            <label class="text-xs text-slate-500 uppercase font-bold flex items-center gap-2">
                <i data-lucide="database"></i> Simülasyon Veri Tabanı
            </label>
            <select id="scenarioSelect" onchange="loadScenario()" class="w-full mt-2 bg-slate-100 text-slate-800 p-2 rounded border border-slate-300 outline-none focus:border-blue-500 transition-colors cursor-pointer font-mono text-sm">
            </select>
        </div>

        <div class="glass p-6 rounded-xl flex-1 flex flex-col relative overflow-hidden group">
            <div class="flex justify-between items-start mb-4">
                <span id="categoryBadge" class="px-3 py-1 bg-blue-100 text-blue-600 text-xs font-bold rounded-full font-mono">BEKLENİYOR</span>
            </div>
            <h2 id="scenarioTitle" class="text-lg font-bold text-slate-800 mb-4 leading-snug">...</h2>
            <div class="prose text-sm text-slate-600 flex-1 overflow-y-auto pr-2 font-light" id="scenarioText"></div>
            <div class="mt-4 bg-slate-100 p-4 rounded-lg border border-slate-200">
                <h3 class="text-xs font-bold text-slate-500 mb-2 flex items-center gap-2 font-mono">
                    <i data-lucide="binary" class="w-4 h-4"></i> GİRDİ PARAMETRELERİ
                </h3>
                <ul id="scenarioData" class="space-y-1 text-xs md:text-sm font-mono text-blue-600"></ul>
            </div>
        </div>
    </div>

    <div class="w-full md:w-2/3 flex flex-col gap-4">
        <div id="aiInteractionArea" class="dark-glass p-5 rounded-xl min-h-[140px] flex gap-4 transition-all duration-500 shadow-lg">
            <div class="bg-slate-700 p-3 rounded-full shrink-0 h-12 w-12 flex items-center justify-center">
                <i data-lucide="bot" class="text-blue-400 w-6 h-6 animate-pulse-fast"></i>
            </div>
            <div class="flex-1">
                <h4 class="text-blue-400 text-xs font-bold mb-1 uppercase tracking-widest font-mono flex justify-between">
                    <span>SİSTEM DURUMU: <span id="systemState" class="text-white">BEKLEMEDE</span></span>
                    <span id="scoreDisplay" class="text-white hidden">Analiz Skoru: %0</span>
                </h4>
                <div id="aiFeedback" class="text-sm text-slate-200 leading-relaxed font-mono mt-2">
                    <span class="typing">Sisteme hoş geldin. Veri tabanından bir senaryo seç.</span>
                </div>
                <div id="hapBilgiBox" class="hidden mt-4 p-4 rounded-lg bg-emerald-600 border border-emerald-400 shadow-lg transform transition-all duration-500">
                    <div class="flex items-center gap-2 mb-2 text-white font-bold border-b border-emerald-400/30 pb-1">
                        <i data-lucide="gem" class="w-4 h-4"></i><span>KRİTİK HAP BİLGİ</span>
                    </div>
                    <p id="hapBilgiText" class="text-xs md:text-sm text-white font-semibold italic"></p>
                </div>
            </div>
        </div>

        <div class="glass p-1 rounded-xl flex-1 relative min-h-[300px] border border-slate-300 flex flex-col bg-white">
            <textarea id="inputText" class="w-full h-full bg-transparent p-6 text-base text-slate-700 resize-none outline-none font-light leading-relaxed font-mono" 
            placeholder="// Çözüm algoritmanı buraya yaz..."></textarea>
            
            <div class="absolute bottom-4 right-4 flex gap-2">
                <button onclick="analyzeSubmission()" id="actionBtn" class="bg-blue-600 hover:bg-blue-500 text-white font-bold px-6 py-2 rounded-lg shadow-lg flex items-center gap-2 transition-all active:scale-95 group">
                    <i data-lucide="zap" class="w-4 h-4 group-hover:fill-current"></i> ANALİZİ BAŞLAT
                </button>
            </div>
        </div>
    </div>

    <script>
        lucide.createIcons();

        // --- PYTHON'DAN VERİ ENJEKSİYONU ---
        // PYTHON_DATA_HERE
        
        if (typeof scenarios === 'undefined') {
            var scenarios = [{ title: "Veri Yükleniyor...", text: "Lütfen bekleyin veya sayfayı yenileyin.", category: "Sistem", data:[], keywords:{} }];
        }

        let currentScenario = null;

        window.onload = function() {
            loadScenarioDropdown();
            loadScenario(0);
        };

        function loadScenarioDropdown() {
            const select = document.getElementById('scenarioSelect');
            select.innerHTML = ""; // Temizle
            scenarios.forEach((s, idx) => {
                let opt = document.createElement('option');
                opt.value = idx;
                opt.innerText = `[${s.category.toUpperCase()}] ${s.title}`;
                select.appendChild(opt);
            });
        }

        function loadScenario(index = null) {
            if(index === null) index = document.getElementById('scenarioSelect').value;
            if(!scenarios[index]) return;
            
            currentScenario = scenarios[index];
            document.getElementById('categoryBadge').innerText = currentScenario.category.toUpperCase();
            document.getElementById('scenarioTitle').innerText = currentScenario.title;
            document.getElementById('scenarioText').innerText = currentScenario.text;
            
            const dataList = document.getElementById('scenarioData');
            dataList.innerHTML = "";
            if(currentScenario.data) {
                currentScenario.data.forEach(item => {
                    dataList.innerHTML += `<li class="border-b border-blue-100 pb-1">> ${item}</li>`;
                });
            }

            document.getElementById('inputText').value = "";
            document.getElementById('hapBilgiBox').classList.add('hidden');
            document.getElementById('scoreDisplay').classList.add('hidden');
            document.getElementById('aiFeedback').innerHTML = `<span class="typing text-blue-300">Yeni senaryo yüklendi. Stratejini bekliyorum...</span>`;
            
            const btn = document.getElementById('actionBtn');
            btn.innerHTML = 'ANALİZİ BAŞLAT';
            btn.disabled = false;
            btn.className = "bg-blue-600 hover:bg-blue-500 text-white font-bold px-6 py-2 rounded-lg shadow-lg flex items-center gap-2 transition-all active:scale-95 group";
            
            updateSystemState("HAZIR");
        }

        function analyzeSubmission() {
            const text = document.getElementById('inputText').value.toLowerCase();
            const feedbackArea = document.getElementById('aiFeedback');
            const btn = document.getElementById('actionBtn');

            if (text.length < 10) {
                feedbackArea.innerHTML = "<span class='text-yellow-400'>Girdi çok kısa. Lütfen detaylandır.</span>";
                return;
            }

            updateSystemState("İŞLENİYOR...");
            btn.innerHTML = 'HESAPLANIYOR...';
            btn.disabled = true;

            setTimeout(() => {
                let score = 0;
                let missing = [];
                const keys = currentScenario.keywords || {};
                const totalKeys = Object.keys(keys).length;

                for (const [key, question] of Object.entries(keys)) {
                    if (text.includes(key)) score++;
                    else missing.push({ key, question });
                }

                const finalScore = totalKeys === 0 ? 100 : Math.floor((score / totalKeys) * 100);
                
                document.getElementById('scoreDisplay').innerText = `Skor: %${finalScore}`;
                document.getElementById('scoreDisplay').classList.remove('hidden');

                if (finalScore > 60) {
                    feedbackArea.innerHTML = `<span class="text-emerald-400 font-bold">>> ANALİZ BAŞARILI.</span><br>Harika bir yaklaşım.`;
                    document.getElementById('hapBilgiText').innerText = currentScenario.hapBilgi;
                    document.getElementById('hapBilgiBox').classList.remove('hidden');
                    btn.innerHTML = 'TAMAMLANDI';
                    btn.className = "bg-emerald-600 text-white font-bold px-6 py-2 rounded-lg cursor-default";
                    updateSystemState("SONUÇLANDI");
                } else {
                    const randomMissing = missing.length > 0 ? missing[Math.floor(Math.random() * missing.length)] : {question: "Daha detaylı açıkla."};
                    feedbackArea.innerHTML = `<span class="text-yellow-400 font-bold">>> EKSİK TESPİT EDİLDİ.</span><br>Şunu düşündün mü: ${randomMissing.question}`;
                    btn.innerHTML = 'TEKRAR DENE';
                    btn.className = "bg-blue-600 hover:bg-blue-500 text-white font-bold px-6 py-2 rounded-lg shadow-lg flex items-center gap-2 transition-all active:scale-95 group";
                    btn.disabled = false;
                    updateSystemState("BEKLENİYOR");
                }
            }, 1000);
        }

        function updateSystemState(msg) {
            document.getElementById('systemState').innerText = msg;
        }
    </script>
</body>
</html>
"""

# 3. CSS TASARIM
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
</style>
""", unsafe_allow_html=True)

# 4. OTURUM YÖNETİMİ
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'user_name' not in st.session_state: st.session_state.user_name = ""
if 'user_no' not in st.session_state: st.session_state.user_no = ""

# --- FONKSİYON: VERİ ÇEKME (GÜNCELLENDİ) ---
@st.cache_data(ttl=300)
def fetch_lifesim_data():
    # 1. Önce yerel dosyaya bak (En garantisi)
    if os.path.exists("lifesim_data.json"):
        try:
            with open("lifesim_data.json", "r", encoding="utf-8") as f:
                return f.read()
        except:
            pass # Okuyamazsa interneti dene

    # 2. Yerelde yoksa GitHub'dan çekmeyi dene
    try:
        if "githubusercontent" in GITHUB_JSON_URL:
            response = requests.get(GITHUB_JSON_URL)
            if response.status_code == 200:
                return response.text
    except:
        pass
        
    # 3. Hiçbiri olmazsa boş liste dön (Hata vermemesi için)
    return "[]"

# --- EKRAN 1: GİRİŞ EKRANI ---
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

# --- EKRAN 2: ANA MENÜ VE İÇERİK ---
else:
    # Üst Bilgi Çubuğu
    st.markdown(f"""
    <div style="display:flex; justify-content:space-between; align-items:center; padding:10px 20px; background:white; border-radius:10px; margin-bottom:20px; box-shadow: 0 2px 5px rgba(0,0,0,0.05);">
        <div style="font-family:'Cinzel'; font-weight:bold; font-size:18px; color:#2c3e50;">🎓 BAĞARASI ÇPAL</div>
        <div style="font-family:'Poppins'; font-size:14px; color:#555;">Hoşgeldin, <b>{st.session_state.user_name}</b> ({st.session_state.user_no})</div>
    </div>
    """, unsafe_allow_html=True)

    # SEKMELER
    tab_ana, tab_profil, tab_soru, tab_eglence, tab_lifesim, tab_premium = st.tabs([
        "🏆 ANA EKRAN", "👤 PROFİL", "📚 SORU ÇÖZÜM", "🎮 EĞLENCE", "💼 LIFESIM", "💎 PREMIUM"
    ])

    # 1. ANA EKRAN
    with tab_ana:
        st.header("🏆 Liderlik Tablosu")
        data = {'Sıra': [1, 2, 3], 'Ad Soyad': ['Ayşe Y.', 'Mehmet K.', st.session_state.user_name], 'Toplam Puan': [15000, 12500, 0]}
        st.table(pd.DataFrame(data))

    # 2. PROFİL
    with tab_profil:
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("### Öğrenci Kartı")
            st.write(f"**Ad Soyad:** {st.session_state.user_name}")
            st.write("**Sınıf:** 11/A")
        with c2:
            st.markdown("### Varlık Durumu")
            st.metric("Toplam Varlık", "0 ₺")
        if st.button("Çıkış Yap"):
            st.session_state.logged_in = False
            st.rerun()

    # 3. SORU ÇÖZÜM
    with tab_soru:
        st.header("📚 Soru Çözüm Merkezi")
        st.info("Sınavlar yakında yüklenecektir.")

    # 4. EĞLENCE
    with tab_eglence:
        st.header("🎮 Eğlence Alanı")
        st.info("Finans İmparatoru ve Asset Matrix yakında eklenecek.")

    # 5. LIFESIM (Entegre Edilen Kısım)
    with tab_lifesim:
        st.header("💼 LifeSim: Kariyer Simülasyonu")
        
        # GitHub'dan Veri Çek
        json_data = fetch_lifesim_data()
        
        if json_data == "[]":
            st.warning("Veriler GitHub'dan çekilemedi. Lütfen 'GITHUB_JSON_URL' satırını kontrol edin veya repo'nun public olduğundan emin olun.")
        
        # HTML Şablonuna Veriyi Göm
        # Javascript değişkeni 'const scenarios = ...' kısmını oluşturuyoruz
        final_html = LIFESIM_HTML_TEMPLATE.replace(
            "// PYTHON_DATA_HERE", 
            f"var scenarios = {json_data};"
        )
        
        # Ekrana Bas
        components.html(final_html, height=800, scrolling=True)

    # 6. PREMIUM
    with tab_premium:
        st.header("💎 Premium Özellikler")
        st.warning("Yapım aşamasında.")
