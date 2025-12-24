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

# --- LIFE-SIM HTML KODU (V4.1 - FIX: JS SYNTAX HATASI DÜZELTİLDİ) ---
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
        
        /* Ders Notu Animasyonu */
        .info-card { transform: translateX(100%); transition: transform 0.5s ease-out; }
        .info-card.show { transform: translateX(0); }
    </style>
</head>
<body>
    <div class="main-container">
        <div class="panel left-panel">
            <div class="glass p-4 rounded-xl border-l-4 border-accent shrink-0">
                <label class="text-xs text-slate-400 uppercase font-bold flex items-center gap-2"><i data-lucide="library"></i> Ders & Senaryo Seçimi</label>
                <select id="scenarioSelect" onchange="loadScenario()" class="w-full mt-2 bg-slate-900 text-white p-2 rounded border border-slate-700 outline-none focus:border-accent cursor-pointer"></select>
            </div>
            
            <div class="glass p-6 rounded-xl flex-1 flex flex-col relative group overflow-visible">
                <div class="flex justify-between items-start mb-4"><span id="categoryBadge" class="px-3 py-1 bg-blue-500/20 text-blue-400 text-xs font-bold rounded-full">YÜKLENİYOR</span></div>
                <h2 id="scenarioTitle" class="text-xl font-bold text-white mb-4 leading-snug">...</h2>
                <div class="prose prose-invert text-sm text-slate-300 overflow-y-auto pr-2 flex-1" id="scenarioText"></div>
                
                <div class="mt-4 shrink-0">
                    <button onclick="toggleHint()" id="hintBtn" class="flex items-center gap-2 text-xs text-warning hover:text-white transition-colors"><i data-lucide="lightbulb" class="w-4 h-4"></i> İpucu Göster</button>
                    <div id="hintBox" class="hidden mt-2 p-3 bg-yellow-900/30 border border-yellow-700/50 rounded-lg text-xs text-yellow-200 italic animate-pulse"></div>
                </div>
                
                <div class="mt-4 bg-slate-800/50 p-4 rounded-lg border border-slate-700 shrink-0">
                    <h3 class="text-xs font-bold text-slate-400 mb-2 flex items-center gap-2"><i data-lucide="bar-chart-4" class="w-4 h-4"></i> VERİLER</h3>
                    <ul id="scenarioData" class="space-y-1 text-xs md:text-sm font-mono text-primary"></ul>
                </div>
            </div>
        </div>

        <div class="panel right-panel relative">
            
            <div id="knowledgeCard" class="absolute inset-0 z-20 bg-slate-900/95 backdrop-blur-xl p-6 flex flex-col gap-4 info-card hidden border-l-4 border-success overflow-y-auto">
                <div class="flex justify-between items-center">
                    <h3 class="text-xl font-bold text-success flex items-center gap-2"><i data-lucide="book-open"></i> KONU ÖZETİ & KRİTİK BİLGİLER</h3>
                    <button onclick="closeKnowledgeCard()" class="p-2 hover:bg-slate-700 rounded-full"><i data-lucide="x" class="w-6 h-6 text-slate-400"></i></button>
                </div>
                <div id="knowledgeContent" class="text-slate-300 text-sm leading-relaxed space-y-4">
                    </div>
                <button onclick="downloadReport()" class="mt-auto w-full py-3 bg-primary/20 hover:bg-primary/30 text-primary border border-primary/50 rounded-lg font-bold flex items-center justify-center gap-2 transition-all">
                    <i data-lucide="download"></i> Raporu İndir ve Tamamla
                </button>
            </div>

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
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        lucide.createIcons();
        
        // --- SENARYO VERİTABANI (BACKTICK KULLANILDI - HATASIZ) ---
        const scenarios = [
            // GÜNCEL
            { 
                category: "Güncel", 
                title: "1. Taksitli Alışveriş ve Enflasyon", 
                text: `Telefonun peşin fiyatı 30.000 TL, 12 taksitli fiyatı 36.000 TL. Enflasyon %60. Hangisi daha karlı?`, 
                data: ["Enflasyon: %60", "Vade Farkı: %20"], 
                hint: `Reel faiz hesabı yap. Paranın zaman değerini düşün.`,
                doc: `📌 **DERS NOTU: Enflasyon ve Borçlanma**<br><br>• **Nominal Faiz:** Bankanın veya satıcının belirlediği faiz oranıdır.<br>• **Reel Faiz:** Enflasyondan arındırılmış gerçek kazanç/maliyet oranıdır.<br><br>💡 **Kural:** Eğer Enflasyon Oranı > Kredi/Vade Faizi ise, borçlanmak karlıdır. Çünkü paranın alım gücü düşerken, borcunuzun reel değeri de düşer. Bu durumda taksitli almak, nakit parayı başka bir yatırım aracında (altın, döviz, fon) değerlendirme fırsatı sunar.`
            },
            { 
                category: "Güncel", 
                title: "2. Gizli Enflasyon (Shrinkflation)", 
                text: `Fiyat aynı kaldı ama gramaj 100gr'dan 80gr'a düştü. Birim maliyet analizi yap.`, 
                data: ["Eski: 100gr", "Yeni: 80gr"], 
                hint: `Gramaj düşünce birim fiyat % kaç arttı?`,
                doc: `📌 **DERS NOTU: Shrinkflation (Küçülflasyon)**<br><br>• Üreticilerin maliyet artışını doğrudan fiyata yansıtmak yerine, ürünün gramajını düşürerek gizli zam yapmasıdır.<br><br>⚠ **Tüketici Dikkat:** Her zaman ürünün paket fiyatına değil, **Birim Fiyatına (TL/kg veya TL/lt)** bakılmalıdır. Bu örnekte gramaj %20 düşerse, ürüne gizlice %25 zam yapılmış demektir.`
            },
            { 
                category: "Güncel", 
                title: "3. İkinci El Araç Yanılgısı", 
                text: `500k'ya aldın, 1M'ye sattın ama yenisi 1.1M. Kar ettin mi?`, 
                data: ["Alış: 500k", "Piyasa: 1.1M"], 
                hint: `Yerine koyma maliyetini düşün.`, 
                doc: `📌 **DERS NOTU: Yerine Koyma Maliyeti**<br><br>• **Nominal Kar:** Kağıt üzerindeki kar (Satış - Alış).<br>• **Yerine Koyma Maliyeti:** Sattığınız malı tekrar almak için ödemeniz gereken bedel.<br><br>💡 Eğer sattığınız malı yerine koymak için üzerine para eklemeniz gerekiyorsa, teknik olarak **Sermaye Kaybı** yaşıyorsunuz demektir. Ticarette esas olan malın adedini korumaktır, TL değerini değil.` 
            },
            { 
                category: "Güncel", 
                title: "4. Bedelli Askerlik Maliyeti", 
                text: `Bedelli 240.000 TL. Maaşın 35.000 TL. Gitmek mi ödemek mi?`, 
                data: ["Bedelli: 240k", "Maaş: 35k"], 
                hint: `Fırsat maliyeti hesabı yap.`, 
                doc: `📌 **DERS NOTU: Fırsat Maliyeti (Opportunity Cost)**<br><br>• Bir kararı uygularken vazgeçtiğiniz en iyi ikinci alternatifin değeridir.<br><br>🧮 **Hesaplama:** (6 Ay x Maaş) + (Kariyer Kaybı/Terfi Gecikmesi) + (Sosyal Hak Kaybı). Eğer bu toplam Bedelli ücretinden yüksekse, bedelli yapmak finansal olarak mantıklıdır.` 
            },
            { 
                category: "Güncel", 
                title: "5. Öğrenci Evi Bütçesi", 
                text: `Gelirler eşit değil. Gider nasıl paylaşılır?`, 
                data: ["Gider: 19k"], 
                hint: `Oransal dağılım.`, 
                doc: `📌 **DERS NOTU: Adil Bütçe Yönetimi**<br><br>• **Eşit Paylaşım:** Herkes aynı tutarı öder. (Gelir farkı varsa adaletsiz olabilir)<br>• **Oransal Paylaşım:** Herkes gelirinin belirli bir yüzdesini (örn. %30) havuza koyar. Geliri çok olan çok, az olan az öder. Bu yöntem sosyal adalete daha uygundur.` 
            },
            
            // MUHASEBE
            { 
                category: "Muhasebe", 
                title: "6. Asgari Ücret Dengesi", 
                text: `Maliyet %40 arttı. Zam yaparsan satış düşecek. Çözüm?`, 
                data: ["Maliyet: +%40"], 
                hint: `Verimlilik artışı.`, 
                doc: `📌 **DERS NOTU: Maliyet Yönetimi**<br><br>• İşçilik maliyeti artınca sadece zam yapmak kısır döngüdür.<br>✅ **Çözüm:** Verimliliği artırmak (aynı sürede daha çok iş), israfı önlemek (yalın üretim) veya devlet teşviklerini kullanmaktır. Fiyat artışı en son çare olmalıdır.` 
            },
            { 
                category: "Muhasebe", 
                title: "7. Vergi Affı Beklentisi", 
                text: `Af çıkacak diye borcu ödememek mantıklı mı?`, 
                data: ["Borç: 500k"], 
                hint: `Risk analizi.`, 
                doc: `📌 **DERS NOTU: Vergi Ahlakı ve Risk**<br><br>• Vergi affı beklentisiyle ödeme yapmamak 'Ahlaki Riziko' (Moral Hazard) yaratır.<br>• Ancak af çıkmazsa; Gecikme Zammı + E-Haciz riski + Ticari İtibar Kaybı oluşur. Bu maliyetler, faizden elde edilecek gelirden genelde daha yüksektir.` 
            },
            { 
                category: "Muhasebe", 
                title: "8. Enflasyon Muhasebesi", 
                text: `Kağıt üzerinde kar var ama stok yerine konamıyor.`, 
                data: ["Nakit: Yok"], 
                hint: `Sermaye erimesi.`, 
                doc: `📌 **DERS NOTU: Enflasyon Muhasebesi**<br><br>• Enflasyonist ortamda mali tablolar gerçeği yansıtmaz. Düşük maliyetli eski stoklar satılınca kar yüksek görünür, bu yüzden yüksek vergi çıkar.<br>• Bu durum **'Sermaye Erimesi'ne** yol açar. İşletmeler stok değerleme yöntemlerini (LIFO/FIFO) ve vergi planlamasını buna göre yapmalıdır.` 
            },
            { 
                category: "Muhasebe", 
                title: "9. E-Fatura Cezası", 
                text: `Fatura kesilemedi. Müşteriye izah et.`, 
                data: ["Ceza: Var"], 
                hint: `Dürüstlük ve teknik raporla başvurmak.`, 
                doc: `📌 **DERS NOTU: Vergi Usul Kanunu ve Mücbir Sebep**<br><br>• E-Fatura/E-Arşiv kesilmemesi Özel Usulsüzlük cezası gerektirir.<br>• Ancak sistemsel arızalar 'Mücbir Sebep' sayılabilir. Durumu ispatlayan teknik raporla Gelir İdaresi'ne başvurulursa ceza iptal edilebilir. Müşteriye şeffaf olmak güveni korur.` 
            },
            { 
                category: "Muhasebe", 
                title: "10. Startup Batış Riski", 
                text: `200k sermaye ile iş kurarken görünmeyen giderler.`, 
                data: ["Stopaj, SGK"], 
                hint: `Sadece kirayı değil, vergileri ve resmi harçları hesapla.`, 
                doc: `📌 **DERS NOTU: Görünmeyen Giderler (Overhead)**<br><br>• Girişimciler genelde sadece Kira ve Malzeme maliyetini hesaplar.<br>• **Unutulanlar:** Stopaj (%20), SGK Primi, Damga Vergileri, Ruhsat Harçları, Muhasebe Ücreti. Bunlar bütçenin %30'unu oluşturur ve nakit akışını bozar.` 
            },

            // HUKUK
            { 
                category: "Hukuk", 
                title: "11. Kiracı Tahliyesi", 
                text: `Kira piyasanın altında. Dava uzun. Uzlaşma?`, 
                data: ["Fark: 4 Kat"], 
                hint: `Zamanın maliyeti.`, 
                doc: `📌 **DERS NOTU: Sulh ve Uzlaşma Kültürü**<br><br>• Hukukta 'En kötü sulh, en iyi davadan iyidir' sözü vardır.<br>• Dava süreçleri (3-4 yıl) hem masraflıdır hem de enflasyonist ortamda alacağın değerini eritir. Kiracıya taşınma yardımı yapıp orta yolda anlaşmak, yılları mahkemede geçirmekten daha karlı olabilir.` 
            },
            { 
                category: "Hukuk", 
                title: "12. Sosyal Medya Hakareti", 
                text: `Müdüre hakaret. TCK 125.`, 
                data: ["Suç: Hakaret"], 
                hint: `Uzlaşma.`, 
                doc: `📌 **DERS NOTU: Bilişim Suçları ve Hakaret**<br><br>• Sosyal medya 'kamuya açık alan' sayılır, bu yüzden ceza artırımı uygulanır (TCK 125/4).<br>• Hakaret suçu 'Uzlaşmaya Tabi' suçlardandır. Savcılık dava açmadan önce tarafları uzlaştırmacıya gönderir. Özür dilemek ve pişmanlık, sicilin bozulmasını engelleyebilir.` 
            },
            { 
                category: "Hukuk", 
                title: "13. Ayıplı Mal", 
                text: `Telefon bozuldu, servis reddetti. Hakem Heyeti.`, 
                data: ["Mal: Ayıplı"], 
                hint: `Bilirkişi incelemesi talep et.`, 
                doc: `📌 **DERS NOTU: Tüketici Hakları**<br><br>• Malın ayıplı çıkması durumunda tüketicinin 4 hakkı vardır: İade, Değişim, İndirim, Ücretsiz Onarım.<br>• Servis 'kullanıcı hatası' dese bile, Tüketici Hakem Heyeti'ne (E-Devlet üzerinden) başvurup bilirkişi talep edebilirsiniz. Karar mahkeme hükmündedir.` 
            },
            { 
                category: "Hukuk", 
                title: "14. Mobbing İddiası", 
                text: `Çalışanlar kavgalı. İK yöneticisi olarak karar ver.`, 
                data: ["Kanıt: ?"], 
                hint: `Eşitlik ilkesi ve somut delil.`, 
                doc: `📌 **DERS NOTU: İş Hukuku ve Mobbing**<br><br>• Mobbing (Psikolojik Taciz) ispatı zor bir durumdur.<br>• Yöneticinin görevi 'Eşit İşlem Borcu'na uymaktır. İddialar somut delile (e-posta, şahit, kamera) dayanmıyorsa, tek taraflı işlem yapmak şirketi tazminat yükü altına sokar.` 
            },
            { 
                category: "Hukuk", 
                title: "15. Miras Paylaşımı", 
                text: `Tarla satılsın mı işlensin mi? Kardeş kavgası.`, 
                data: ["Çözüm: ?"], 
                hint: `İntifa hakkı veya ortak işletme modeli.`, 
                doc: `📌 **DERS NOTU: Ortaklığın Giderilmesi (İzale-i Şuyu)**<br><br>• Mirasçılar anlaşamazsa mahkeme malı açık artırmayla satar, bu da malın değerinin altında gitmesine neden olur.<br>• **Çözüm:** 'Aile Anayasası' oluşturmak veya toprağı işleyip gelirini paylaşmak (İntifa Hakkı) hem malı korur hem de aile bağlarını.` 
            },

            // YÖNETİM
            { 
                category: "Yönetim", 
                title: "16. AI ve İşsizlik", 
                text: `AI 3 kişinin işini yapıyor. Kovmak mı?`, 
                data: ["Verim: Yüksek"], 
                hint: `Dönüştürmek.`, 
                doc: `📌 **DERS NOTU: İnsan Kaynakları Dönüşümü**<br><br>• Teknolojik işsizlik kaçınılmazdır ama çözüm kovmak değil, 'Upskilling' (Beceri Geliştirme) yapmaktır.<br>• O personelleri AI operatörü olarak eğitmek, kurumsal hafızayı korur ve şirketin teknolojiye adaptasyonunu hızlandırır.` 
            },
            { 
                category: "Yönetim", 
                title: "17. Kriz Masası", 
                text: `Müşteri otelde olay çıkardı. İtibar yönetimi.`, 
                data: ["Risk: Viral"], 
                hint: `Empati.`, 
                doc: `📌 **DERS NOTU: Kriz İletişimi**<br><br>• Kriz anında savunmaya geçmek (inkar etmek, suçlamak) yangını körükler.<br>• Doğru Strateji: 1. Kabul et, 2. Özür dile (gerekirse), 3. Telafi et. Müşterinin sesinin duyulduğunu hissetmesi öfkeyi %80 azaltır.` 
            },
            { 
                category: "Yönetim", 
                title: "18. Ofise Dönüş", 
                text: `Herkes evden çalışmak istiyor. Sen ofis diyorsun.`, 
                data: ["Kültür: Zayıf"], 
                hint: `Hibrit model (Haftada 2 gün ofis).`, 
                doc: `📌 **DERS NOTU: Kurum Kültürü ve Hibrit Çalışma**<br><br>• Tamamen uzaktan çalışma 'Kurum Aidiyetini' zayıflatır. Tamamen ofis ise verimi düşürebilir.<br>• **Altın Oran:** Hibrit modeldir. Haftanın belirli günlerini (Core Days) sosyalleşme ve beyin fırtınası için ofise ayırmak en verimli yöntemdir.` 
            },
            { 
                category: "Yönetim", 
                title: "19. Tedarik Zinciri", 
                text: `Hammadde yok. Üretim durdu. Müşteriye ne denir?`, 
                data: ["Stok: 0"], 
                hint: `Şeffaflık ve alternatif çözüm önerisi.`, 
                doc: `📌 **DERS NOTU: Tedarik Zinciri Yönetimi**<br><br>• 'Just in Time' (Tam Zamanında) üretim modeli stok maliyetini düşürür ama krizlere kırılgandır.<br>• Kriz anında müşteriye yalan söylemek (oyalamak) en büyük hatadır. Şeffaf olup, gerekirse rakip firmadan ürün temin edip müşteriyi mağdur etmemek uzun vadeli güven sağlar.` 
            },
            { 
                category: "Yönetim", 
                title: "20. Greenwashing", 
                text: `Patron yalandan 'Doğa Dostu' yazmak istiyor.`, 
                data: ["Risk: Büyük"], 
                hint: `Tüketici güveni kaybolursa marka biter.`, 
                doc: `📌 **DERS NOTU: İş Etiği ve Greenwashing**<br><br>• Tüketiciyi çevreci gibi görünerek kandırmaya 'Yeşil Aklama' (Greenwashing) denir.<br>• Bu ortaya çıktığında marka değeri sıfırlanır. Etik olmayan kar, en büyük zarardır. Dürüstlük en sürdürülebilir pazarlama stratejisidir.` 
            },

            // DEĞERLER
            { 
                category: "Değerler", 
                title: "21. Bulunan Cüzdan", 
                text: `Düşmanının cüzdanı. İçinde para var.`, 
                data: ["Vicdan"], 
                hint: `Karakter.`, 
                doc: `📌 **DERS NOTU: Etik ve Karakter**<br><br>• Etik, yasaların bittiği yerde başlar.<br>• 'Karakter, kimse izlemiyorken ne yaptığındır.' Düşmanının malını korumak, sadece ona değil, kendi onuruna duyduğun saygının göstergesidir. Bu davranış toplumsal güven sermayesini artırır.` 
            },
            { 
                category: "Değerler", 
                title: "22. Zorbalığa Sessiz Kalmak", 
                text: `Arkadaşın eziliyor. Ses çıkarırsan yanacaksın.`, 
                data: ["Cesaret"], 
                hint: `Sessiz kalmak onaylamaktır.`, 
                doc: `📌 **DERS NOTU: Aktif Vatandaşlık**<br><br>• Zorbalık karşısında sessiz kalanlar, zorbalığın devam etmesine zemin hazırlar.<br>• 'Bana dokunmayan yılan bin yaşasın' zihniyeti toplumu çürütür. Doğruyu savunmak kısa vadede riskli olsa da, uzun vadede saygınlık kazandırır.` 
            },
            { 
                category: "Değerler", 
                title: "23. Çevre Etiği", 
                text: `Fabrikanız nehri kirletiyor. İhbar eder misin?`, 
                data: ["Aile vs Toplum"], 
                hint: `Uzun vadeli toplum sağlığı.`, 
                doc: `📌 **DERS NOTU: Kurumsal Sosyal Sorumluluk**<br><br>• Kısa vadeli kar uğruna doğayı kirletmek, gelecek nesillerden çalmaktır.<br>• Gerçek vatanseverlik toprağına, suyuna sahip çıkmaktır. Aile şirketi bile olsa, yanlışa dur demek en büyük sadakattir.` 
            },
            { 
                category: "Değerler", 
                title: "24. Hasarlı Kaza", 
                text: `Arabayı çizdin, kaçma şansın var.`, 
                data: ["Dürüstlük"], 
                hint: `Empati kur.`, 
                doc: `📌 **DERS NOTU: Empati ve Sorumluluk**<br><br>• 'Kendine yapılmasını istemediğin şeyi başkasına yapma.'<br>• Kaçmak anlık olarak 5-10 bin TL kurtarabilir ama vicdan yükü ömür boyu sürer. Sorumluluk almak olgunluktur.` 
            },
            { 
                category: "Değerler", 
                title: "25. Dijital Bağımlılık", 
                text: `Kardeşin ekran bağımlısı. Nasıl yardım edersin?`, 
                data: ["İletişim"], 
                hint: `Yasak yerine alternatif sun.`, 
                doc: `📌 **DERS NOTU: Dijital Denge**<br><br>• Teknoloji iyi bir hizmetçi ama kötü bir efendidir.<br>• Bağımlılıkla mücadelede yasaklar ters teper. Çözüm, boşluğu spor, sanat veya sohbet ile doldurmaktır. İlgi göstermek, tabletten daha güçlü bir bağlayıcıdır.` 
            }
        ];
        
        // Diğer senaryolar için varsayılan not
        const defaultDoc = `📌 **DERS NOTU: Genel Analiz**<br><br>• Bu konuda karar verirken şu 3 filtreyi kullan:<br>1. **Hukuki mi?** (Yasalara uygun mu?)<br>2. **Ekonomik mi?** (Verimli ve sürdürülebilir mi?)<br>3. **Etik mi?** (Vicdana ve toplumsal değerlere uygun mu?)<br><br>💡 İyi bir yönetici bu üç dengeyi kurabilen kişidir.`;

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
                items.forEach(item => { let opt = document.createElement('option'); opt.value = item.idx; opt.innerHTML = item.title; group.appendChild(opt); });
                select.appendChild(group);
            }
            loadScenario();
            startTimer();
            setupCanvas();
        };

        function loadScenario() {
            selectedScenarioIndex = document.getElementById('scenarioSelect').value;
            const s = scenarios[selectedScenarioIndex];
            
            document.getElementById('categoryBadge').innerText = s.category.toUpperCase();
            document.getElementById('categoryBadge').className = `px-3 py-1 text-xs font-bold rounded-full w-fit mb-4 ${getCategoryColor(s.category)}`;
            document.getElementById('scenarioTitle').innerText = s.title;
            document.getElementById('scenarioText').innerText = s.text;
            
            const dataList = document.getElementById('scenarioData');
            dataList.innerHTML = "";
            if(s.data) {
                s.data.forEach(item => {
                    let parts = item.split(':');
                    dataList.innerHTML += `<li class="flex justify-between border-b border-slate-700/50 pb-1"><span class="text-slate-400">${parts[0]}:</span> <span class="text-white font-mono font-bold">${parts[1] || ''}</span></li>`;
                });
            }

            document.getElementById('inputText').value = "";
            clearCanvas();
            document.getElementById('hintBox').classList.add('hidden');
            document.getElementById('hintBtn').classList.remove('hidden');
            document.getElementById('aiFeedback').innerHTML = "Bekleniyor... Stratejini oluşturduktan sonra 'Analiz Et' butonuna bas.";
            
            // Bilgi kartını kapat
            document.getElementById('knowledgeCard').classList.remove('show');
            setTimeout(() => document.getElementById('knowledgeCard').classList.add('hidden'), 500);
            
            const btn = document.getElementById('analyzeBtn');
            btn.innerHTML = '<i data-lucide="sparkles" class="w-6 h-6"></i> ANALİZ ET';
            btn.classList.remove('bg-green-600');
        }

        function analyzeSubmission() {
            const btn = document.getElementById('analyzeBtn');
            const feedback = document.getElementById('aiFeedback');
            const text = document.getElementById('inputText').value.trim();
            const s = scenarios[selectedScenarioIndex];

            if (text.length < 10) {
                feedback.innerHTML = "<span class='text-warning font-bold'>⚠ Uyarı:</span> Cevabın çok kısa.";
                return;
            }

            btn.innerHTML = '⏳ ANALİZ EDİLİYOR...';
            feedback.innerHTML = "<span class='animate-pulse text-primary'>🧠 Yapay zeka stratejini inceliyor...</span>";

            setTimeout(() => {
                let keywords = ["risk", "maliyet", "kar", "yasa", "etik", "plan", "strateji", "verim", "analiz", "faiz", "enflasyon", "vicdan"];
                let found = keywords.filter(w => text.toLowerCase().includes(w));
                
                let responseHTML = "";
                if (found.length > 0) {
                    responseHTML = `<span class='text-success font-bold'>✔ Analiz Başarılı!</span><br>Harika noktalar yakaladın. Şimdi sağda açılan <b class='text-white'>Konu Özeti</b> kartını incele.`;
                    btn.classList.add('bg-green-600');
                } else {
                    responseHTML = `<span class='text-blue-400 font-bold'>ℹ Tamamlandı</span><br>Stratejin kaydedildi. Konunun teknik detaylarını öğrenmek için sağdaki nota bak.`;
                }

                btn.innerHTML = '<i data-lucide="check-circle" class="w-6 h-6"></i> TAMAMLANDI';
                feedback.innerHTML = responseHTML;

                // BİLGİ KARTINI AÇ (DERS NOTU)
                const card = document.getElementById('knowledgeCard');
                const content = document.getElementById('knowledgeContent');
                content.innerHTML = s.doc || defaultDoc;
                
                card.classList.remove('hidden');
                setTimeout(() => card.classList.add('show'), 50);

            }, 2000);
        }

        function closeKnowledgeCard() {
            const card = document.getElementById('knowledgeCard');
            card.classList.remove('show');
            setTimeout(() => card.classList.add('hidden'), 500);
        }

        function downloadReport() {
            const s = scenarios[selectedScenarioIndex];
            const ans = document.getElementById('inputText').value;
            const content = `LIFE-SIM RAPORU\n=================\nTARİH: ${new Date().toLocaleString('tr-TR')}\nKONU: ${s.title}\n\nÖĞRENCİ YANITI:\n${ans}\n\nDERS NOTU / GERİ BİLDİRİM:\n${(s.doc || defaultDoc).replace(/<br>/g, '\n').replace(/<b>/g, '').replace(/<\/b>/g, '')}`;
            
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
