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

# --- SENARYO VERİTABANI (GÜNLÜK HAYAT ODAKLI & UZUN) ---
SCENARIOS_DATA = [
    # --- GÜNCEL EKONOMİ ---
    {
        "category": "Güncel Ekonomi",
        "title": "1. Teknoloji Alışverişi ve Enflasyon Çıkmazı",
        "text": "Mevcut telefonun aniden bozuldu ve tamir edilemez durumda. İşlerin ve derslerin için acilen yeni bir telefona ihtiyacın var. İstediğin modelin piyasa fiyatı 40.000 TL. <br><br><b>Mevcut Durumun:</b><br>• Banka hesabında tam 40.000 TL nakit paran var (tüm birikimin bu).<br>• Kredi kartınla 12 taksit yapabilirsin ama banka aylık %4,5 vade farkı koyuyor (Toplam geri ödeme: ~58.000 TL).<br>• Ülkedeki yıllık enflasyon beklentisi %65.<br><br><b>Karar Anı:</b> Tüm nakdini verip 'borçsuz' ama 'parasız' kalmak mı? Yoksa vade farkı ödeyip nakdini 'altın/döviz/fon' gibi araçlarda tutmak mı? Hangi yolu seçersin ve neden?",
        "data": ["Nakit: 40.000 TL", "Taksitli Tutar: 58.000 TL", "Enflasyon: %65"],
        "hint": "Paranın Zaman Değeri kavramını düşün. Bugünün 40.000 TL'si ile 1 yıl sonraki 40.000 TL aynı mı?",
        "doc": "📌 **HAP BİLGİ: Enflasyonist Ortamda Borçlanma**<br><br>• **Nominal vs Reel Maliyet:** Banka size %40 faizle kredi veriyorsa ama ülkede enflasyon %65 ise, aslında reel olarak 'eksi faizle' borçlanıyorsunuz demektir. Yani borcunuz zamanla erir.<br>• **Nakit Kraldır (Cash is King):** Belirsizlik dönemlerinde tüm nakdi bir mala bağlamak risklidir. Acil durumlar için likidite (nakit) bırakmak, vade farkı ödemekten daha değerli olabilir.<br>• **Karar:** Eğer elindeki nakdi, bankanın vade farkından (%45) daha yüksek getiri getirecek bir araca (Örn: Altın, Fon, Döviz - Beklenti %65) yatırabiliyorsan, taksitli almak matematiksel olarak daha karlıdır."
    },
    {
        "category": "Güncel Ekonomi",
        "title": "2. Kira Artışı ve Ev Sahibi Baskısı",
        "text": "3 yıldır oturduğun evde kiran 5.000 TL. Bölgedeki emsal kiralar 20.000 TL'ye çıktı. Ev sahibin aradı ve 'Ya kirayı 15.000 TL yap ya da oğlum gelecek evi boşalt' dedi. <br><br>Yasal olarak %25 (veya TÜFE) oranında zam yapma hakkın var. Mahkemeye gitsen tahliye davası en az 3 yıl sürer ve kazanırsın. Ancak ev sahibi kapına gelip huzursuzluk çıkarabilir, apartmanda dedikodu yayabilir.<br><br><b>Karar Anı:</b> Yasaların sana verdiği hakkı sonuna kadar kullanıp (düşük kira) psikolojik baskıyı mı göze alırsın? Yoksa bütçeni zorlayıp 'huzur parası' diyerek orta yolda (12-13 bin) anlaşır mısın?",
        "data": ["Mevcut Kira: 5.000", "Talep: 15.000", "Yasal Hak: ~8.000"],
        "hint": "Bu sadece bir hukuk sorusu değil, bir 'Stres Yönetimi' ve 'Maliyet/Fayda' sorusudur.",
        "doc": "📌 **HAP BİLGİ: Sulh ve Zaman Maliyeti**<br><br>• **Hukuki Hak:** Kiracı, sözleşme süresi bitmeden ve haklı bir neden (ihtiyaç, tadilat, 10 yıl dolumu) ispatlanmadan çıkarılamaz.<br>• **Görünmeyen Maliyet:** Dava süreci masraflıdır (Avukat, Dosya). Daha önemlisi 'Psikolojik Maliyet'tir. Huzursuz bir evde yaşamanın, sürekli gergin olmanın iş ve okul hayatına etkisi, aradaki 3-4 bin TL farktan daha büyük olabilir.<br>• **Strateji:** Genellikle 'Kötü bir sulh, iyi bir davadan iyidir'. Orta yolda anlaşmak (örneğin 10-12 bin TL), hem taşınma masrafından kurtarır hem de huzuru satın alır."
    },
    {
        "category": "Kariyer & Yönetim",
        "title": "3. Maaş mı, Özgürlük mü? (Freelance İkilemi)",
        "text": "Üniversiteden yeni mezun oldun. İki yerden teklif aldın:<br><br><b>A Şirketi (Kurumsal):</b> Sabah 9 - Akşam 6 mesai. İstanbul'da plazada. Maaş: 45.000 TL + Yemek + Sigorta. Ancak her gün 3 saat trafikte geçecek ve kıyafet zorunluluğu var.<br><b>B Şirketi (Startup - Uzaktan):</b> Evden çalışma (Home Office). Maaş: 30.000 TL. Sigorta var ama yemek yok. İstediğin şehirden çalışabilirsin.<br><br>İstanbul'da kira ve yaşam maliyeti çok yüksek. Anadolu'da ailenin yanında veya daha ucuz bir şehirde yaşama şansın var. Geleceğini ve yaşam kaliteni düşünerek hangisini seçersin?",
        "data": ["Kurumsal: 45k (Ofis)", "Startup: 30k (Remote)", "Kira: İstanbul Pahalı"],
        "hint": "Sadece maaşa bakma. 'Net Ele Geçen' ve 'Yaşam Maliyeti' (Cost of Living) hesabını yap.",
        "doc": "📌 **HAP BİLGİ: Reel Gelir ve Yaşam Kalitesi**<br><br>• **Nominal Gelir:** Bordroda yazan rakamdır (45.000 TL).<br>• **Reel (Kullanılabilir) Gelir:** Zorunlu giderler düştükten sonra cebe kalan paradır.<br><br>💡 **Hesap:** İstanbul'da kira (20k) + yol + giyim + dışarıda yeme içme düştüğünde cebine 5.000 TL kalıyorsa; Anadolu'da kirasız evde 30.000 TL alıp 20.000 TL biriktirmek finansal olarak daha mantıklıdır. Ayrıca günde 3 saat trafik, haftada 15 saat (yılda neredeyse 1 ay) kayıp demektir. Zaman en değerli sermayedir."
    },
    
    # --- ETİK & DEĞERLER ---
    {
        "category": "Etik Değerler",
        "title": "4. Rakibinin Kayıp Cüzdanı",
        "text": "Okul birinciliği için yarıştığın ve hiç sevmediğin bir sınıf arkadaşın var. Sürekli seni ezikliyor. Okul çıkışı yerde bir cüzdan buldun. İçinde yüklü miktarda para ve o çocuğun kimliği var. Etrafta kamera yok, kimse seni görmedi.<br><br>Ailennin maddi durumu şu an sıkışık, o para evdeki büyük bir deliği kapatabilir. Cüzdanı çöpe atıp parayı alsan kimse bilmeyecek. Arkadaşın ise o parayı kaybederse çok üzülecek ama hayatı kaymayacak.<br><br>Vicdanınla baş başasın. Ne yaparsın? Dürüstçe anlat.",
        "data": ["Miktar: Yüksek", "Risk: Sıfır", "Vicdan: ?"],
        "hint": "Karakter, kimse seni izlemiyorken ne yaptığındır.",
        "doc": "📌 **HAP BİLGİ: Etik Liderlik ve Karakter**<br><br>• **Dürüstlük Testi:** İnsanlar genellikle 'Yakalanma riski varsa' dürüst davranır. Gerçek erdem, ceza korkusu olmadan doğruyu seçmektir.<br>• **Sevgi vs Adalet:** Birine adil davranmak için onu sevmek zorunda değilsiniz. Düşmanınızın bile hakkını korumak, sizi ondan üstün ve güçlü kılar. O parayı harcamak, ömür boyu sürecek bir vicdan yükü (manevi borç) yaratır."
    },
    {
        "category": "Güncel Ekonomi",
        "title": "5. 'Yalancı İndirim' Tuzağı",
        "text": "Bir e-ticaret sitesinde aylardır takip ettiğin spor ayakkabı 3.000 TL idi. 'Efsane Cuma' indirimlerinde fiyatın üzerinin çizilip '5.000 TL'den 3.500 TL'ye düştü' yazıldığını gördün. Yani aslında eski fiyattan daha pahalıya satıyorlar ama 'Büyük İndirim' algısı var.<br><br>Ayakkabıya ihtiyacın var ve stoklar tükeniyor görünüyor (FOMO - Kaçırma Korkusu). Bu pazarlama tuzağına düşüp alır mısın, yoksa prensip gereği protesto mu edersin?",
        "data": ["Gerçek Fiyat: 3.000", "Kampanya: 3.500", "Algı: İndirim Var"],
        "hint": "Çapalama Etkisi (Anchoring Effect) denilen psikolojik tuzağı düşün.",
        "doc": "📌 **HAP BİLGİ: Davranışsal Ekonomi ve Fiyat Algısı**<br><br>• **Çapalama (Anchoring):** Beynimiz ilk gördüğü sayıya (5.000 TL) odaklanır ve sonraki fiyatı (3.500 TL) buna göre 'ucuz' algılar. Oysa gerçek referans 3.000 TL'dir.<br>• **FOMO (Fear of Missing Out):** 'Son 3 ürün', 'İndirim bitiyor' sayaçları panik yaptırıp mantıklı düşünmeyi engellemek içindir. <br>• **Tavsiye:** Fiyat takip grafikleri kullanın ve ihtiyacınız yoksa 'ucuz' diye hiçbir şeyi almayın. En büyük tasarruf, almamaktır."
    }
]

SCENARIOS_JSON = json.dumps(SCENARIOS_DATA, ensure_ascii=False)

# --- LIFE-SIM HTML KODU (V5.0 - SORGULAYICI GERİ BİLDİRİM & GİZLİ BİLGİ KARTI) ---
LIFE_SIM_HTML = f"""
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Life-Sim</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://unpkg.com/lucide@latest"></script>
    <script>
        tailwind.config = {{ theme: {{ extend: {{ colors: {{ bg: '#0f172a', surface: '#1e293b', primary: '#38bdf8', accent: '#f472b6', success: '#34d399', warning: '#fbbf24' }} }} }} }}
    </script>
    <style>
        body {{ background-color: #0f172a; color: #e2e8f0; font-family: 'Segoe UI', sans-serif; overflow: hidden; }}
        .glass {{ background: rgba(30, 41, 59, 0.8); backdrop-filter: blur(12px); border: 1px solid rgba(255,255,255,0.08); }}
        .glow-border:focus-within {{ box-shadow: 0 0 20px rgba(56, 189, 248, 0.2); border-color: #38bdf8; }}
        
        /* Scrollbar */
        ::-webkit-scrollbar {{ width: 6px; }}
        ::-webkit-scrollbar-track {{ background: #0f172a; }}
        ::-webkit-scrollbar-thumb {{ background: #334155; border-radius: 4px; }}
        
        /* Layout */
        .main-container {{ height: 100vh; display: flex; flex-direction: column; gap: 1rem; padding: 0.5rem; }}
        @media (min-width: 768px) {{ .main-container {{ flex-direction: row; }} }}
        .panel {{ display: flex; flex-direction: column; gap: 1rem; height: 100%; overflow-y: auto; }}
        .left-panel {{ flex: 4; }}
        .right-panel {{ flex: 5; position: relative; }}
        
        /* Bilgi Kartı Animasyonu */
        .info-card {{ 
            position: absolute; top: 0; right: 0; bottom: 0; left: 0; 
            background: rgba(15, 23, 42, 0.98); 
            z-index: 50; 
            transform: translateX(100%); 
            transition: transform 0.4s cubic-bezier(0.16, 1, 0.3, 1);
            display: flex; flex-direction: column;
        }}
        .info-card.show {{ transform: translateX(0); }}
        
        /* Buton Efektleri */
        .btn-analyze {{ background: linear-gradient(135deg, #38bdf8 0%, #2563eb 100%); }}
        .btn-analyze:hover {{ filter: brightness(1.1); }}
    </style>
</head>
<body>
    <div class="main-container">
        <div class="panel left-panel">
            <div class="glass p-4 rounded-xl border-l-4 border-accent shrink-0">
                <label class="text-xs text-slate-400 uppercase font-bold flex items-center gap-2">
                    <i data-lucide="map"></i> Hayat Senaryosu Seç
                </label>
                <select id="scenarioSelect" onchange="loadScenario()" class="w-full mt-2 bg-slate-900 text-white p-3 rounded border border-slate-700 outline-none focus:border-accent cursor-pointer hover:bg-slate-800 transition"></select>
            </div>
            
            <div class="glass p-6 rounded-xl flex-1 flex flex-col relative overflow-hidden">
                <div class="flex justify-between items-start mb-4">
                    <span id="categoryBadge" class="px-3 py-1 bg-blue-500/20 text-blue-400 text-xs font-bold rounded-full">YÜKLENİYOR</span>
                </div>
                <h2 id="scenarioTitle" class="text-2xl font-bold text-white mb-4 leading-tight">...</h2>
                <div class="prose prose-invert text-base text-slate-300 overflow-y-auto pr-3 flex-1 leading-relaxed" id="scenarioText"></div>
                
                <div class="mt-6 pt-4 border-t border-slate-700/50">
                    <button onclick="toggleHint()" id="hintBtn" class="text-xs text-warning hover:text-white transition-colors flex items-center gap-1">
                        <i data-lucide="key"></i> Ufak bir ipucu ister misin?
                    </button>
                    <div id="hintBox" class="hidden p-3 bg-yellow-900/20 border border-yellow-600/30 rounded-lg text-sm text-yellow-200/90 italic"></div>
                </div>
                
                <div class="mt-4 flex flex-wrap gap-2" id="scenarioDataTags"></div>
            </div>
        </div>

        <div class="panel right-panel">
            
            <div id="knowledgeCard" class="info-card border-l-4 border-success shadow-2xl">
                <div class="p-6 border-b border-slate-700 flex justify-between items-center bg-slate-800/50">
                    <h3 class="text-xl font-bold text-success flex items-center gap-2">
                        <i data-lucide="book-open-check"></i> UZMAN GÖRÜŞÜ & DERS NOTU
                    </h3>
                    <button onclick="closeKnowledgeCard()" class="p-2 hover:bg-slate-700 rounded-full transition">
                        <i data-lucide="x" class="w-6 h-6 text-slate-400"></i>
                    </button>
                </div>
                <div id="knowledgeContent" class="p-8 text-slate-200 text-base leading-7 space-y-4 overflow-y-auto flex-1">
                    </div>
                <div class="p-4 bg-slate-800/50 border-t border-slate-700 text-center">
                    <button onclick="downloadReport()" class="px-6 py-3 bg-success/20 hover:bg-success/30 text-success border border-success/50 rounded-lg font-bold flex items-center justify-center gap-2 mx-auto transition-all w-full md:w-auto">
                        <i data-lucide="download"></i> Bu Analizi Rapor Olarak İndir
                    </button>
                </div>
            </div>

            <div class="glass p-1 rounded-xl flex-1 flex flex-col relative border border-slate-700 glow-border">
                <div class="bg-slate-800/50 p-2 rounded-t-xl flex justify-between items-center px-4">
                    <span class="text-xs font-bold text-slate-400 uppercase">Senin Stratejin</span>
                    <span id="timer" class="font-mono text-primary text-sm">00:00</span>
                </div>
                <textarea id="inputText" class="w-full h-full bg-transparent p-6 text-lg text-slate-200 resize-none outline-none font-light leading-relaxed placeholder-slate-600" 
                placeholder="Bu durumda ne yaparsın? Kararının arkasındaki mantığı, riskleri ve fırsatları detaylıca anlat..."></textarea>
            </div>
            
            <div class="glass p-0 rounded-xl overflow-hidden flex flex-col md:flex-row shrink-0 min-h-[120px]">
                <button id="analyzeBtn" onclick="analyzeSubmission()" class="btn-analyze text-white font-bold p-6 flex flex-col items-center justify-center gap-2 md:w-1/4 transition-all active:scale-95">
                    <i data-lucide="sparkles" class="w-8 h-8"></i>
                    <span>ANALİZ ET</span>
                </button>
                
                <div class="p-6 flex-1 bg-slate-800/80 flex items-center relative">
                    <div id="aiFeedback" class="text-sm text-slate-300 leading-relaxed w-full">
                        <div class="flex items-center gap-3 text-slate-500">
                            <i data-lucide="bot" class="w-8 h-8"></i>
                            <p>Senaryoyu oku, kararını ver ve 'Analiz Et' butonuna bas. Yapay zeka yaklaşımını değerlendirecek.</p>
                        </div>
                    </div>
                    
                    <button id="showDocBtn" onclick="openKnowledgeCard()" class="hidden absolute right-4 top-1/2 -translate-y-1/2 bg-purple-600 hover:bg-purple-500 text-white px-4 py-2 rounded-lg shadow-lg flex items-center gap-2 text-xs font-bold transition-all animate-bounce">
                        <i data-lucide="lightbulb"></i>
                        UZMAN GÖRÜŞÜNÜ GÖR
                    </button>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        lucide.createIcons();
        const scenarios = {SCENARIOS_JSON};
        let selectedScenarioIndex = 0;
        let startTime = Date.now();

        window.onload = function() {{
            const select = document.getElementById('scenarioSelect');
            const categories = {{}};
            scenarios.forEach((s, index) => {{
                if(!categories[s.category]) categories[s.category] = [];
                categories[s.category].push({{ ...s, idx: index }});
            }});
            for (const [cat, items] of Object.entries(categories)) {{
                let group = document.createElement('optgroup'); group.label = cat.toUpperCase();
                items.forEach(item => {{ let opt = document.createElement('option'); opt.value = item.idx; opt.innerHTML = item.title; group.appendChild(opt); }});
                select.appendChild(group);
            }}
            loadScenario();
            setInterval(() => {{ 
                const d = Math.floor((Date.now() - startTime)/1000); 
                document.getElementById('timer').innerText = `${{Math.floor(d/60).toString().padStart(2,'0')}}:${{(d%60).toString().padStart(2,'0')}}`; 
            }}, 1000);
        }};

        function loadScenario() {{
            selectedScenarioIndex = document.getElementById('scenarioSelect').value;
            const s = scenarios[selectedScenarioIndex];
            
            document.getElementById('categoryBadge').innerText = s.category;
            document.getElementById('scenarioTitle').innerText = s.title;
            document.getElementById('scenarioText').innerHTML = s.text;
            
            const tags = document.getElementById('scenarioDataTags');
            tags.innerHTML = "";
            s.data.forEach(d => {{
                tags.innerHTML += `<span class="px-2 py-1 bg-slate-700 rounded text-xs text-primary border border-slate-600">${{d}}</span>`;
            }});

            // Reset
            document.getElementById('inputText').value = "";
            document.getElementById('hintBox').classList.add('hidden');
            document.getElementById('hintBtn').classList.remove('hidden');
            document.getElementById('aiFeedback').innerHTML = `<div class="flex items-center gap-3 text-slate-500"><i data-lucide="bot" class="w-8 h-8"></i><p>Bekleniyor...</p></div>`;
            document.getElementById('showDocBtn').classList.add('hidden');
            document.getElementById('knowledgeCard').classList.remove('show');
            
            const btn = document.getElementById('analyzeBtn');
            btn.innerHTML = '<i data-lucide="sparkles" class="w-8 h-8"></i><span>ANALİZ ET</span>';
            btn.disabled = false;
            btn.classList.remove('opacity-50');
        }}

        function analyzeSubmission() {{
            const text = document.getElementById('inputText').value.trim().toLowerCase();
            const btn = document.getElementById('analyzeBtn');
            const feedback = document.getElementById('aiFeedback');
            
            if (text.length < 15) {{
                feedback.innerHTML = "<span class='text-warning font-bold flex items-center gap-2'><i data-lucide='alert-triangle'></i> Çok kısa yazdın. Biraz daha detaylandır.</span>";
                lucide.createIcons();
                return;
            }}

            btn.innerHTML = '⏳';
            btn.disabled = true;
            btn.classList.add('opacity-50');
            
            feedback.innerHTML = "<span class='text-primary animate-pulse'>Yapay zeka stratejini inceliyor... Riskler hesaplanıyor...</span>";

            setTimeout(() => {{
                // SORGULAYICI GERİ BİLDİRİM MANTIĞI
                let msg = "";
                
                // Anahtar kelime yakalama (Basit Mantık)
                if (text.includes("nakit") || text.includes("peşin")) {{
                    msg = "<span class='text-white font-bold'>🤔 Nakit tercih ettin.</span><br>Peki acil durum fonunu tamamen tüketmek, bu belirsiz ekonomide seni savunmasız bırakmaz mı?";
                }} else if (text.includes("taksit") || text.includes("kredi") || text.includes("borç")) {{
                    msg = "<span class='text-white font-bold'>🤔 Borçlanmayı seçtin.</span><br>Peki aylık ödeme yükü, gelecekteki nakit akışını kilitlerse ne yapacaksın? Reel faiz hesabını yaptın mı?";
                }} else if (text.includes("dava") || text.includes("mahkeme")) {{
                    msg = "<span class='text-white font-bold'>⚖ Hukuki yolu seçtin.</span><br>Haklısın ama davanın yıllarca süreceğini ve bu süreçteki stres maliyetini hesaba kattın mı?";
                }} else if (text.includes("uzlaş") || text.includes("anlaş")) {{
                    msg = "<span class='text-success font-bold'>🤝 Uzlaşmayı seçtin.</span><br>Bazen haktan feragat etmek, huzuru satın almaktır. Bu pragmatik bir yaklaşım.";
                }} else {{
                    msg = "<span class='text-white font-bold'>Analiz Tamamlandı.</span><br>Yaklaşımın ilginç. Kararın finansal ve etik boyutlarını tam olarak görmek ister misin?";
                }}

                feedback.innerHTML = msg;
                btn.innerHTML = '<i data-lucide="check" class="w-8 h-8"></i><span>BİTTİ</span>';
                
                // Hap Bilgi Butonunu Göster
                document.getElementById('showDocBtn').classList.remove('hidden');
                lucide.createIcons();

            }}, 1500);
        }}

        function openKnowledgeCard() {{
            const s = scenarios[selectedScenarioIndex];
            document.getElementById('knowledgeContent').innerHTML = s.doc;
            document.getElementById('knowledgeCard').classList.remove('hidden');
            // Animasyon için frame atlat
            requestAnimationFrame(() => document.getElementById('knowledgeCard').classList.add('show'));
        }}

        function closeKnowledgeCard() {{
            document.getElementById('knowledgeCard').classList.remove('show');
            setTimeout(() => document.getElementById('knowledgeCard').classList.add('hidden'), 400);
        }}

        function toggleHint() {{
            const s = scenarios[selectedScenarioIndex];
            document.getElementById('hintBox').innerHTML = `💡 ${{s.hint}}`;
            document.getElementById('hintBox').classList.remove('hidden');
            document.getElementById('hintBtn').classList.add('hidden');
        }}
        
        function downloadReport() {{
            const s = scenarios[selectedScenarioIndex];
            const ans = document.getElementById('inputText').value;
            const txt = `KONU: ${{s.title}}\\nCEVAP: ${{ans}}\\n\\nUZMAN NOTU:\\n${{s.doc.replace(/<[^>]*>/g, '')}}`;
            const blob = new Blob([txt], {{type: 'text/plain'}});
            const a = document.createElement('a');
            a.href = URL.createObjectURL(blob);
            a.download = 'Analiz_Raporu.txt';
            a.click();
        }}
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
    
    .stSelectbox div[data-baseweb="select"] > div {
        background-color: #FFFFFF !important;
        color: #000000 !important;
        border: 2px solid #FF7043;
    }
    
    .stDeployButton {display:none;}
    footer {visibility: hidden;}
    #MainMenu {visibility: hidden;}
    
    .giris-kart {
        background-color: white;
        padding: 40px;
        border-radius: 20px;
        border: 3px solid #FF7043;
        text-align: center;
        box-shadow: 0 10px 20px rgba(0,0,0,0.1);
        margin-bottom: 20px;
    }

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
    
    .konu-karti { background-color: white; padding: 20px; border-radius: 10px; border-left: 6px solid #2196F3; margin-bottom: 15px; box-shadow: 0 2px 5px rgba(0,0,0,0.05); }
    .soru-karti { background-color: white; padding: 20px; border-radius: 10px; border-left: 5px solid #FF7043; font-size: 18px; margin-bottom: 20px; color: #000 !important; }
    .hata-karti { background-color: #FFEBEE; border-left: 5px solid #D32F2F; padding: 15px; margin-bottom: 15px; border-radius: 5px; color: #000; }
    .stat-card { background-color: white; padding: 15px; border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); text-align: center; border: 2px solid #FF7043; }
    .stat-number { font-size: 32px; font-weight: bold; color: #D84315; }
    
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
