import streamlit as st
import streamlit.components.v1 as components
import random
import os
import time
import json
import fitz  # PyMuPDF

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Bağarası Hibrit Eğitim Ekosistemi", page_icon="🎓", layout="wide")

# --- DOSYA İSİMLERİ ---
TYT_PDF_ADI = "tytson8.pdf"
TYT_JSON_ADI = "tyt_data.json"
MESLEK_JSON_ADI = "sorular.json"
KONU_JSON_ADI = "konular.json"

# --- LIFE-SIM HTML KODU (V3.2 - FINAL / DÜZELTİLMİŞ ANALİZ MOTORU) ---
LIFE_SIM_HTML = """
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
        body { background-color: #0f172a; color: #e2e8f0; font-family: 'Segoe UI', sans-serif; overflow: hidden; }
        .glass { background: rgba(30, 41, 59, 0.7); backdrop-filter: blur(12px); border: 1px solid rgba(255,255,255,0.08); }
        .glow-border:focus-within { box-shadow: 0 0 20px rgba(56, 189, 248, 0.2); border-color: #38bdf8; }
        canvas { cursor: crosshair; touch-action: none; }
        ::-webkit-scrollbar { width: 8px; }
        ::-webkit-scrollbar-track { background: #0f172a; }
        ::-webkit-scrollbar-thumb { background: #334155; border-radius: 4px; }
        .main-container { height: 95vh; display: flex; flex-direction: column; gap: 1rem; padding: 0.5rem; }
        @media (min-width: 768px) { .main-container { flex-direction: row; } }
        .panel { display: flex; flex-direction: column; gap: 1rem; height: 100%; overflow-y: auto; }
        .left-panel { flex: 1; }
        .right-panel { flex: 2; }
    </style>
</head>
<body>
    <div class="main-container">
        <div class="panel left-panel">
            <div class="glass p-4 rounded-xl border-l-4 border-accent shrink-0">
                <label class="text-xs text-slate-400 uppercase font-bold flex items-center gap-2"><i data-lucide="list"></i> Görev Seçimi</label>
                <select id="scenarioSelect" onchange="loadScenario()" class="w-full mt-2 bg-slate-900 text-white p-2 rounded border border-slate-700 outline-none focus:border-accent cursor-pointer"></select>
            </div>
            
            <div class="glass p-6 rounded-xl flex-1 flex flex-col relative group overflow-visible">
                <div class="flex justify-between items-start mb-4"><span id="categoryBadge" class="px-3 py-1 bg-blue-500/20 text-blue-400 text-xs font-bold rounded-full">YÜKLENİYOR</span></div>
                <h2 id="scenarioTitle" class="text-xl font-bold text-white mb-4 leading-snug">...</h2>
                <div class="prose prose-invert text-sm text-slate-300 overflow-y-auto pr-2 flex-1" id="scenarioText"></div>
                
                <div class="mt-4 shrink-0">
                    <button onclick="toggleHint()" id="hintBtn" class="flex items-center gap-2 text-xs text-warning hover:text-white transition-colors"><i data-lucide="lightbulb" class="w-4 h-4"></i> Bir İpucu Ver (-5 Puan)</button>
                    <div id="hintBox" class="hidden mt-2 p-3 bg-yellow-900/30 border border-yellow-700/50 rounded-lg text-xs text-yellow-200 italic animate-pulse"></div>
                </div>
                
                <div class="mt-4 bg-slate-800/50 p-4 rounded-lg border border-slate-700 shrink-0">
                    <h3 class="text-xs font-bold text-slate-400 mb-2 flex items-center gap-2"><i data-lucide="bar-chart-4" class="w-4 h-4"></i> VERİLER</h3>
                    <ul id="scenarioData" class="space-y-1 text-xs md:text-sm font-mono text-primary"></ul>
                </div>
            </div>
        </div>

        <div class="panel right-panel">
            <div class="glass p-2 rounded-lg flex items-center justify-between shrink-0">
                <div class="flex gap-2">
                    <button onclick="setTab('text')" id="btn-text" class="flex items-center gap-2 px-3 py-2 rounded-lg bg-primary text-slate-900 font-bold text-sm transition-all"><i data-lucide="file-edit" class="w-4 h-4"></i> Analiz Yaz</button>
                    <button onclick="setTab('draw')" id="btn-draw" class="flex items-center gap-2 px-3 py-2 rounded-lg text-slate-400 hover:text-white hover:bg-slate-700 text-sm transition-all"><i data-lucide="pencil" class="w-4 h-4"></i> Şema Çiz</button>
                </div>
                <div class="text-right px-4 flex items-center gap-2"><i data-lucide="timer" class="w-4 h-4 text-slate-500"></i><span id="timer" class="text-xl font-mono text-white font-bold">00:00</span></div>
            </div>
            
            <div class="glass p-1 rounded-xl flex-1 relative min-h-[300px] border border-slate-700 glow-border">
                <textarea id="inputText" class="w-full h-full bg-transparent p-6 text-base text-slate-200 resize-none outline-none font-light leading-relaxed" placeholder="Bu krizi nasıl yöneteceksin? Finansal, hukuki ve etik gerekçelerini detaylandır..."></textarea>
                <div id="drawContainer" class="hidden w-full h-full bg-slate-900 relative rounded-lg overflow-hidden">
                    <canvas id="drawingCanvas" class="w-full h-full block"></canvas>
                    <button onclick="clearCanvas()" class="absolute top-4 right-4 bg-slate-700 p-2 rounded hover:bg-red-500 transition text-white z-10" title="Temizle"><i data-lucide="trash" class="w-4 h-4"></i></button>
                </div>
            </div>
            
            <div class="grid grid-cols-1 md:grid-cols-4 gap-4 shrink-0">
                <button id="analyzeBtn" onclick="analyzeSubmission()" class="md:col-span-1 bg-gradient-to-br from-primary to-blue-600 hover:from-blue-400 hover:to-blue-500 text-slate-900 font-bold py-4 rounded-xl shadow-lg flex flex-col items-center justify-center gap-1 transition-all active:scale-95 group"><i data-lucide="sparkles" class="w-6 h-6 group-hover:animate-spin"></i> ANALİZ ET</button>
                <div class="md:col-span-3 glass p-4 rounded-xl flex items-start gap-4 border border-slate-700/50 min-h-[100px]">
                    <div class="bg-slate-800 p-3 rounded-full shrink-0"><i data-lucide="bot" class="text-accent w-6 h-6"></i></div>
                    <div class="flex-1">
                        <h4 class="text-accent text-xs font-bold mb-1 uppercase tracking-widest">Sistem Geri Bildirimi</h4>
                        <div id="aiFeedback" class="text-sm text-slate-300 leading-relaxed">Bekleniyor... Stratejini oluşturduktan sonra 'Analiz Et' butonuna bas.</div>
                        <button id="downloadBtn" onclick="downloadReport()" class="hidden mt-3 px-4 py-1.5 bg-success/20 hover:bg-success/30 text-success border border-success/30 rounded text-xs font-bold flex items-center gap-2 transition-all"><i data-lucide="download" class="w-3 h-3"></i> Raporu İndir</button>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        lucide.createIcons();
        
        // --- SENARYO VERİTABANI (TAM LİSTE) ---
        const scenarios = [
            { category: "Güncel", title: "1. Taksitli Alışveriş ve Enflasyon", text: "Telefonun peşin fiyatı 30.000 TL, 12 taksitli fiyatı 36.000 TL. Enflasyon %60. Hangisi daha karlı?", data: ["Enflasyon: %60", "Vade Farkı: %20"], hint: "Reel faiz hesabı yap. Paranın zaman değerini düşün." },
            { category: "Güncel", title: "2. Gizli Enflasyon (Shrinkflation)", text: "Fiyat aynı kaldı ama gramaj düştü. Birim maliyet analizi yap.", data: ["Eski: 100gr", "Yeni: 80gr"], hint: "Gramaj düşünce birim fiyat % kaç arttı?" },
            { category: "Güncel", title: "3. İkinci El Araç Yanılgısı", text: "500k'ya aldın, 1M'ye sattın ama yenisi 1.1M. Kar ettin mi?", data: ["Alış: 500k", "Piyasa: 1.1M"], hint: "Yerine koyma maliyetini (Replacement Cost) düşün." },
            { category: "Güncel", title: "4. Bedelli Askerlik Maliyeti", text: "Bedelli 240.000 TL. Maaşın 35.000 TL. Gitmek mi ödemek mi?", data: ["Bedelli: 240k", "Maaş: 35k"], hint: "6 aylık maaş kaybı + kariyer kaybı vs Bedelli ücreti." },
            { category: "Güncel", title: "5. Öğrenci Evi Bütçesi", text: "3 arkadaş eve çıkıyorsunuz. Gelirler eşit değil. Gider nasıl paylaşılır?", data: ["Gider: 19k"], hint: "Adil paylaşım için gelire oranlı bir model kur." },
            { category: "Güncel", title: "6. Kuryelik ve Net Kar", text: "Ciro 60.000 TL ama masraflar sana ait. Gerçek maaşın ne?", data: ["Ciro: 60k", "Masraf: ~20k"], hint: "Amortismanı ve sosyal güvence giderlerini düş." },
            { category: "Güncel", title: "7. Abonelik Ekonomisi", text: "Küçük aboneliklerin yıllık maliyeti ve fırsat maliyeti.", data: ["Aylık: 700 TL"], hint: "Yıllık toplam tutarı ve bununla alabileceğin bir varlığı düşün." },
            { category: "Güncel", title: "8. Düğün Borcu", text: "500k kredi ile düğün mü, sade nikah ve ev peşinatı mı?", data: ["Faiz: Yüksek"], hint: "Gelecekteki finansal özgürlüğün mü, bir günlük gösteriş mi?" },
            { category: "Güncel", title: "9. Kripto Risk Yönetimi", text: "Tüm paranı tek coine yatırmak mantıklı mı?", data: ["Risk: %100"], hint: "Yumurtaları aynı sepete koymamak ilkesi." },
            { category: "Güncel", title: "10. Güneş Enerjisi ROI", text: "100k yatırım, aylık 2k tasarruf. Ne zaman amorti eder?", data: ["Yatırım: 100k"], hint: "Yatırım / Aylık Tasarruf = Ay sayısı." },
            
            { category: "Muhasebe", title: "11. Asgari Ücret Dengesi", text: "Maliyet arttı. Zam yaparsan satış düşecek. Çözüm?", data: ["Maliyet: +%40"], hint: "Verimlilik artışı veya yan haklarda düzenleme olabilir mi?" },
            { category: "Muhasebe", title: "12. Vergi Affı Beklentisi", text: "Borcu ödeme af çıkacak diyorlar. Risk alır mısın?", data: ["Borç: 500k"], hint: "Gecikme faizi ve ticari itibar kaybını hesapla." },
            { category: "Muhasebe", title: "13. Enflasyon Muhasebesi", text: "Kağıt üzerinde kar var ama stok yerine konamıyor.", data: ["Nakit: Yok"], hint: "Vergi, gerçekleşmemiş kardan ödenirse sermaye erir." },
            { category: "Muhasebe", title: "14. E-Fatura Cezası", text: "Fatura kesilemedi. Müşteriye izah et.", data: ["Ceza: Var"], hint: "Dürüstlük ve teknik raporla başvurmak." },
            { category: "Muhasebe", title: "15. Startup Batış Riski", text: "200k sermaye ile iş kurarken görünmeyen giderler.", data: ["Stopaj, SGK"], hint: "Sadece kirayı değil, vergileri ve resmi harçları hesapla." },
            
            { category: "Hukuk", title: "16. Kiracı Tahliyesi", text: "Kira piyasanın altında. Dava uzun. Uzlaşma?", data: ["Fark: 4 Kat"], hint: "Dava sürecindeki enflasyon kaybı vs Uzlaşma." },
            { category: "Hukuk", title: "17. Sosyal Medya Hakareti", text: "Müdüre hakaret ettin. Savunma stratejin ne?", data: ["Suç: Hakaret"], hint: "Haksız tahrik indirimi veya uzlaşma." },
            { category: "Hukuk", title: "18. Ayıplı Mal", text: "Telefon bozuldu, servis reddetti. Hakem Heyeti.", data: ["Mal: Ayıplı"], hint: "Bilirkişi incelemesi talep et." },
            { category: "Hukuk", title: "19. Mobbing İddiası", text: "Çalışanlar kavgalı. İK yöneticisi olarak karar ver.", data: ["Kanıt: ?"], hint: "Eşitlik ilkesi ve somut delil." },
            { category: "Hukuk", title: "20. Miras Paylaşımı", text: "Tarla satılsın mı işlensin mi? Kardeş kavgası.", data: ["Çözüm: ?"], hint: "İntifa hakkı veya ortak işletme modeli." },
            
            { category: "Yönetim", title: "21. AI ve İşsizlik", text: "AI 3 kişinin işini yapıyor. Kovmak mı dönüştürmek mi?", data: ["Verim: Yüksek"], hint: "Personeli AI operatörü olarak eğitmek." },
            { category: "Yönetim", title: "22. Ofise Dönüş", text: "Herkes evden çalışmak istiyor. Sen ofis diyorsun.", data: ["Kültür: Zayıf"], hint: "Hibrit model (Haftada 2 gün ofis)." },
            { category: "Yönetim", title: "23. Kriz Masası", text: "Müşteri otelde olay çıkardı. Sosyal medya riski.", data: ["İtibar"], hint: "Empati ve anında telafi." },
            { category: "Yönetim", title: "24. Tedarik Zinciri", text: "Hammadde yok. Üretim durdu. Müşteriye ne denir?", data: ["Stok: 0"], hint: "Şeffaflık ve alternatif çözüm önerisi." },
            { category: "Yönetim", title: "25. Greenwashing", text: "Patron yalandan 'Doğa Dostu' yazmak istiyor.", data: ["Risk: Büyük"], hint: "Tüketici güveni kaybolursa marka biter." },
            
            { category: "Değerler", title: "26. Bulunan Cüzdan", text: "Düşmanının cüzdanı. İçinde para var.", data: ["Vicdan"], hint: "Karakter sınavı." },
            { category: "Değerler", title: "27. Zorbalığa Sessiz Kalmak", text: "Arkadaşın eziliyor. Ses çıkarırsan yanacaksın.", data: ["Cesaret"], hint: "Sessiz kalmak onaylamaktır." },
            { category: "Değerler", title: "28. Çevre Etiği", text: "Fabrikanız nehri kirletiyor. İhbar eder misin?", data: ["Aile vs Toplum"], hint: "Uzun vadeli toplum sağlığı." },
            { category: "Değerler", title: "29. Hasarlı Kaza", text: "Arabayı çizdin, kaçma şansın var.", data: ["Dürüstlük"], hint: "Empati kur." },
            { category: "Değerler", title: "30. Dijital Bağımlılık", text: "Kardeşin ekran bağımlısı. Nasıl yardım edersin?", data: ["İletişim"], hint: "Yasak yerine alternatif sun." }
        ];

        let selectedScenarioIndex = 0;
        let startTime = Date.now();

        window.onload = function() {
            const select = document.getElementById('scenarioSelect');
            scenarios.forEach((s, index) => {
                let opt = document.createElement('option');
                opt.value = index;
                opt.innerHTML = s.title;
                select.appendChild(opt);
            });
            loadScenario();
            startTimer();
            setupCanvas();
        };

        function loadScenario() {
            selectedScenarioIndex = document.getElementById('scenarioSelect').value;
            const s = scenarios[selectedScenarioIndex];
            
            // Badge ve Metinleri Güncelle
            document.getElementById('categoryBadge').innerText = s.category.toUpperCase();
            document.getElementById('categoryBadge').className = `px-3 py-1 text-xs font-bold rounded-full w-fit mb-4 ${getCategoryColor(s.category)}`;
            document.getElementById('scenarioTitle').innerText = s.title;
            document.getElementById('scenarioText').innerText = s.text;
            
            // Verileri Listele
            const dataList = document.getElementById('scenarioData');
            dataList.innerHTML = "";
            if(s.data) {
                s.data.forEach(item => {
                    let parts = item.split(':');
                    let key = parts[0];
                    let val = parts[1] || '';
                    dataList.innerHTML += `<li class="flex justify-between border-b border-slate-700/50 pb-1"><span class="text-slate-400">${key}:</span> <span class="text-white font-mono font-bold">${val}</span></li>`;
                });
            }

            // Sıfırlama
            document.getElementById('inputText').value = "";
            clearCanvas();
            document.getElementById('hintBox').classList.add('hidden');
            document.getElementById('hintBtn').classList.remove('hidden');
            
            // AI Mesajını Sıfırla
            document.getElementById('aiFeedback').innerHTML = "Bekleniyor... Stratejini oluşturduktan sonra 'Analiz Et' butonuna bas.";
            document.getElementById('downloadBtn').classList.add('hidden');
            
            // Buton Rengini Sıfırla
            const btn = document.getElementById('analyzeBtn');
            btn.innerHTML = '<i data-lucide="sparkles" class="w-6 h-6"></i> ANALİZ ET';
            btn.classList.remove('bg-green-600', 'bg-red-600');
        }

        // --- DÜZELTİLMİŞ ANALİZ FONKSİYONU ---
        function analyzeSubmission() {
            const btn = document.getElementById('analyzeBtn');
            const feedback = document.getElementById('aiFeedback');
            const text = document.getElementById('inputText').value.trim();
            const s = scenarios[selectedScenarioIndex];

            // 1. Boş Cevap Kontrolü
            if (text.length < 10) {
                feedback.innerHTML = "<span class='text-warning font-bold'>⚠ Uyarı:</span> Cevabın çok kısa. Bir yönetici gibi detaylı gerekçeler yazmalısın.";
                return;
            }

            // 2. İşleniyor Animasyonu
            btn.innerHTML = '⏳ SİSTEM ANALİZ EDİYOR...';
            feedback.innerHTML = "<span class='animate-pulse text-primary'>🧠 Yapay zeka anahtar kelimeleri tarıyor... Hukuki ve Mali riskler hesaplanıyor...</span>";

            // 3. Simülasyon Gecikmesi (2 saniye)
            setTimeout(() => {
                // Basit Anahtar Kelime Analizi
                let keywords = ["risk", "maliyet", "kar", "yasa", "etik", "plan", "strateji", "verim", "analiz", "faiz", "enflasyon", "uzlaşma", "itibar"];
                let found = keywords.filter(w => text.toLowerCase().includes(w));
                
                let responseHTML = "";
                
                if (found.length > 0) {
                    responseHTML = `<span class='text-success font-bold'>✔ Analiz Başarılı!</span><br>
                    Harika, yanıtında <b>${found.length}</b> kritik finansal/yönetimsel kavrama değinmişsin. Stratejin sistem tarafından onaylandı.<br>
                    <span class='text-slate-400 text-xs'>Sonraki Adım: Raporunu indirip eğitmenine sunabilirsin.</span>`;
                    btn.classList.add('bg-green-600');
                } else {
                    responseHTML = `<span class='text-blue-400 font-bold'>ℹ Geliştirilebilir</span><br>
                    Stratejin mantıklı görünüyor ancak daha fazla teknik terim (Örn: Maliyet, Risk, Yasa) kullanman puanını artırır.<br>
                    <span class='text-slate-400 text-xs'>Yine de raporunu oluşturduk.</span>`;
                }

                // Sonuçları Göster
                btn.innerHTML = '<i data-lucide="check-circle" class="w-6 h-6"></i> ANALİZ TAMAMLANDI';
                feedback.innerHTML = responseHTML;
                document.getElementById('downloadBtn').classList.remove('hidden');

            }, 2000);
        }

        function downloadReport() {
            const s = scenarios[selectedScenarioIndex];
            const ans = document.getElementById('inputText').value;
            const content = `LIFE-SIM RAPORU\n=================\nTARİH: ${new Date().toLocaleString('tr-TR')}\nKONU: ${s.title}\nKATEGORİ: ${s.category}\n\nÖĞRENCİ YANITI:\n${ans}\n\nSİSTEM DEĞERLENDİRMESİ:\nOtomatik analiz tamamlandı. Strateji veritabanına işlendi.\n\nONAY KODU: ${Math.random().toString(36).substr(2, 9).toUpperCase()}`;
            
            const blob = new Blob([content], { type: 'text/plain' });
            const a = document.createElement('a');
            a.href = window.URL.createObjectURL(blob);
            a.download = `LifeSim_Rapor_${Date.now()}.txt`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
        }

        function toggleHint() {
            const s = scenarios[selectedScenarioIndex];
            document.getElementById('hintBox').innerHTML = `<span class="font-bold">💡 İPUCU:</span> ${s.hint}`;
            document.getElementById('hintBox').classList.remove('hidden');
            document.getElementById('hintBtn').classList.add('hidden');
        }

        function getCategoryColor(cat) {
            const c = { 'Muhasebe': 'bg-green-900/50 text-green-400', 'Hukuk': 'bg-red-900/50 text-red-400', 'Yönetim': 'bg-blue-900/50 text-blue-400', 'Güncel': 'bg-purple-900/50 text-purple-400', 'Değerler': 'bg-orange-900/50 text-orange-400' };
            return c[cat] || 'bg-slate-700 text-slate-300';
        }

        // Sekme ve Çizim İşlemleri
        function setTab(mode) {
            if(mode === 'text') {
                document.getElementById('inputText').style.display = 'block';
                document.getElementById('drawContainer').classList.add('hidden');
            } else {
                document.getElementById('inputText').style.display = 'none';
                document.getElementById('drawContainer').classList.remove('hidden');
                resizeCanvas();
            }
        }

        // Canvas Kodları
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
        
        function startTimer() { setInterval(() => { const d = Math.floor((Date.now() - startTime)/1000); document.getElementById('timer').innerText = `${Math.floor(d/60).toString().padStart(2,'0')}:${(d%60).toString().padStart(2,'0')}`; }, 1000); }
        window.addEventListener('resize', () => { resizeCanvas(); });
    </script>
</body>
</html>
"""

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
# FONKSİYONLAR
# ==============================================================================

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

def dosya_yukle(dosya_adi):
    if not os.path.exists(dosya_adi): return {}
    try:
        with open(dosya_adi, "r", encoding="utf-8") as f:
            data = json.load(f)
            if dosya_adi == TYT_JSON_ADI:
                return {int(k): v for k, v in data.items()}
            return data
    except: return {}

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

# VERİLERİ YÜKLE
TYT_VERI = dosya_yukle(TYT_JSON_ADI)
MESLEK_VERI = dosya_yukle(MESLEK_JSON_ADI)
KONU_VERI = dosya_yukle(KONU_JSON_ADI)

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
        
        col_a, col_b, col_c = st.columns(3)
        with col_a:
            st.markdown("""<div class='secim-karti'><h3>📘 TYT Kampı</h3><p>Çıkmış Sorular & Denemeler</p></div>""", unsafe_allow_html=True)
            if st.button("TYT Başlat ➡️", key="btn_tyt"): st.session_state.secim_turu = "TYT"
        
        with col_b:
            st.markdown("""<div class='secim-karti'><h3>💼 Meslek Lisesi</h3><p>Alan Dersleri & Konu Testleri</p></div>""", unsafe_allow_html=True)
            if st.button("Meslek Çöz ➡️", key="btn_meslek"): st.session_state.secim_turu = "MESLEK"

        with col_c:
            st.markdown("""<div class='secim-karti' style='border-color:#38bdf8;'><h3>🧠 Life-Sim</h3><p>Finans & Kriz Yönetim Senaryoları</p></div>""", unsafe_allow_html=True)
            if st.button("Simülasyonu Aç 🚀", key="btn_life"): 
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
