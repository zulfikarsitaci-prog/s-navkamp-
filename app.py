import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import requests
import json
import os
import time
import random
import database
import base64
import re
from datetime import datetime

# --- AYARLAR ---
st.set_page_config(page_title="Bağarası ÇPAL", page_icon="🎓", layout="wide", initial_sidebar_state="expanded")

# --- GELİŞMİŞ SINAV VERİSİ ---
def create_full_exams_json():
    data = {
      "9. Sınıf": {
        "Mesleki Gelişim Atölyesi": [
          {"type": "scenario", "text": "SENARYO 1: Mehmet Amca tarlasını telefon uygulamasıyla suluyor, akıllı saatiyle nabzını ölçüyor.", "sub_questions": [{"q": "1. Mehmet Amca'nın teknolojiyi kullanma amacını özetleyiniz (Verim, Kolaylık vb.)", "a": "Verim"}, {"q": "2. Akıllı saat hangi teknoloji türüne girer?", "a": "Giyilebilir"}], "points": 20},
          {"type": "text", "question": "3. Ofiste işlerin yürümesi için kullanılan teknolojik ürünlerden 1 tanesini yazınız.", "answer": "Bilgisayar", "keywords": ["bilgisayar", "yazıcı", "tarayıcı", "telefon", "tablet"], "points": 10},
          {"type": "text", "question": "4. E-Posta (E-Mail) ile WhatsApp arasındaki en temel fark nedir?", "answer": "Resmiyet", "keywords": ["resmi", "kurumsal", "yasal", "belge"], "points": 10},
          {"type": "text", "question": "5. Staj başvurusu e-postasının 'Konu' kısmına ne yazılmalıdır?", "answer": "Staj Başvurusu", "points": 10},
          {"type": "text", "question": "6. Güneş paneli kullanan bir işletme hangi tür enerji kaynağı kullanır?", "answer": "Yenilenebilir", "keywords": ["yenilenebilir", "tükenmez", "güneş"], "points": 10},
          {"type": "scenario", "text": "SENARYO 5: Elinizde geri dönüştürülebilir meyve suyu kutusu ve yağlı peçete var.", "sub_questions": [{"q": "7. Meyve suyu kutusu (Ambalaj) Çöp müdür, Atık mıdır?", "a": "Atık"}, {"q": "Kullanılmış yağlı peçete Çöp müdür, Atık mıdır?", "a": "Çöp"}, {"q": "8. Atık yağların lavaboya dökülmemesi neyi kirletir?", "a": "Su"}], "points": 20},
          {"type": "text", "question": "9. Sıfır Atık prensibine göre atığı çöp atmak yerine başka amaçla kullanmaya ne denir?", "answer": "İleri Dönüşüm", "keywords": ["dönüşüm", "geri kazanım"], "points": 10},
          {"type": "test", "question": "10. Bankaların web sitelerinde soruları yanıtlayan sanal asistanlar hangi teknolojidir?", "options": ["Blockchain", "Yapay Zeka", "Bulut Bilişim", "Nesnelerin İnterneti"], "answer": "Yapay Zeka", "points": 10}
        ],
        "Temel Muhasebe": [
          {"type": "calculation", "text": "SORU 1: KIDEM TAZMİNATI HESAPLAMA: 4 Yıl 5 Ay 18 Gün çalışan işçi. Brüt Maaş: 30.000 TL.", "inputs": [{"label": "4 Yıllık Tutar (30.000 x 4)", "correct": 120000}, {"label": "5 Aylık Tutar (30.000 / 12 x 5)", "correct": 12500}, {"label": "18 Günlük Tutar (30.000 / 30 x 18)", "correct": 18000}, {"label": "TOPLAM TAZMİNAT", "correct": 150500}], "points": 20},
          {"type": "scenario", "text": "SORU 2: SGK STATÜLERİ EŞLEŞTİRME", "sub_questions": [{"q": "a) Maaşlı çalışan mühendis (4a/4b/4c)?", "a": "4a"}, {"q": "b) Kendi ofisini açan mimar (Bağkur) (4a/4b/4c)?", "a": "4b"}, {"q": "c) Valilikte memur (4a/4b/4c)?", "a": "4c"}], "points": 10},
          {"type": "text", "question": "SORU 3: SGK'ya göre bordroların saklanma süresi kaç yıldır?", "answer": "10", "points": 10},
          {"type": "text", "question": "SORU 4: 25.12.2025'te işe başlayacak işçinin sigorta bildirgesi en geç ne zaman verilmeli?", "answer": "24.12.2025", "keywords": ["24.12", "bir gün önce"], "points": 10},
          {"type": "text", "question": "SORU 5: İşçi kendi isteğiyle istifa ederse ihbar tazminatı alabilir mi? (Evet/Hayır)", "answer": "Hayır", "points": 10},
          {"type": "text", "question": "SORU 6: Nakliyesi yapılan ancak henüz faturası kesilmemiş mal için şoförün taşıması gereken belge?", "answer": "Sevk İrsaliyesi", "points": 10},
          {"type": "text", "question": "SORU 7: Faturanın 'Kapalı Fatura' (imzanın altta) olması bedelin ne yapıldığını gösterir?", "answer": "Ödendiğini", "keywords": ["ödendi", "peşin"], "points": 10},
          {"type": "calculation", "text": "SORU 8: FATURA HESAPLAMA: 50 Çanta, Birim Fiyat 200 TL, İskonto %10, KDV %20.", "inputs": [{"label": "Mal Bedeli (50x200)", "correct": 10000}, {"label": "İskonto Tutarı (%10)", "correct": 1000}, {"label": "KDV Matrahı (Bedel - İskonto)", "correct": 9000}, {"label": "KDV Tutarı (%20)", "correct": 1800}, {"label": "Genel Toplam", "correct": 10800}], "points": 20}
        ]
      },
      "10. Sınıf": {
        "Ekonomi": [
          {"type": "scenario", "text": "SENARYO 1 (MEHMET BEY): Pamuğu balya olarak satmak yerine iplik atölyesi kurup ipliğe dönüştürmüştür.", "sub_questions": [{"q": "1. Bu değer kazandırma işlemine ne ad verilir?", "a": "Üretim"}, {"q": "2. Mehmet Bey üretim faktörlerinden hangisidir?", "a": "Girişimci"}], "points": 20},
          {"type": "scenario", "text": "SENARYO (AYŞE HANIM): Bahçesindeki incirlerden reçel yapıp satmak için atölye kuruyor.", "sub_questions": [{"q": "İncir (Üretim Faktörü)?", "a": "Doğal Kaynak"}, {"q": "Komşu Fatma Hanım (Üretim Faktörü)?", "a": "Emek"}, {"q": "Kazanlar ve Ocak (Üretim Faktörü)?", "a": "Sermaye"}], "points": 15},
          {"type": "text", "question": "3. Söke ve çevresinde yapılan Tarım Sektörünün alt dallarından birini yazınız.", "answer": "Pamukçuluk", "keywords": ["pamuk", "zeytin", "incir", "hayvancılık"], "points": 10},
          {"type": "text", "question": "4. Yatırımcının Söke'ye tekstil fabrikası kurmasındaki en önemli faktör?", "answer": "Hammadde", "keywords": ["hammadde", "pamuk"], "points": 10},
          {"type": "text", "question": "5. Hammaddenin fabrikada işlenerek mamul hale gelmesi süreci?", "answer": "Sanayi", "keywords": ["sanayi", "imalat"], "points": 10},
          {"type": "text", "question": "6. Kıt kaynakları kullanmak için sorulan 3 temel sorudan birini yazınız.", "answer": "Nasıl", "keywords": ["neyi", "nasıl", "kimin için"], "points": 10},
          {"type": "scenario", "text": "7-8. EKONOMİK SİSTEMLER", "sub_questions": [{"q": "Devletin belirlediği sistem?", "a": "Sosyalizm"}, {"q": "Piyasanın belirlediği sistem?", "a": "Kapitalizm"}], "points": 10},
          {"type": "text", "question": "9. Nazilli Basma Fabrikası'nın (1937) kuruluş amacı hangi ilke ile açıklanır?", "answer": "Devletçilik", "points": 15},
          {"type": "text", "question": "10. Türk denizlerinde ticaret hakkını Türk gemilerine veren kanun?", "answer": "Kabotaj", "points": 15},
          {"type": "text", "question": "KAVRAM: Kendi çıkarını maksimize eden, akılcı birey?", "answer": "Homo Economicus", "points": 10},
          {"type": "text", "question": "PİYASA: Fiyat artınca Tüketici (Talep) ne yapar? (Artar/Azalır)", "answer": "Azalır", "points": 10}
        ],
        "Temel Hukuk": [
          {"type": "scenario", "text": "SENARYO 1: Ahmet Bey tarlasını sürmek için Tariş Kooperatifi'nden traktör kiralamıştır.", "sub_questions": [{"q": "Ahmet Bey gerçek mi tüzel kişi mi?", "a": "Gerçek"}, {"q": "Tariş Kooperatifi gerçek mi tüzel kişi mi?", "a": "Tüzel"}, {"q": "Tarla taşınır mı taşınmaz mı?", "a": "Taşınmaz"}, {"q": "Traktör taşınır mı taşınmaz mı?", "a": "Taşınır"}], "points": 20},
          {"type": "text", "question": "3. Tarafların karşılıklı anlaşmasına hukukta ne ad verilir?", "answer": "Sözleşme", "points": 10},
          {"type": "text", "question": "4. Borç ilişkisinde yerine getirilmesi gereken davranışa ne denir?", "answer": "Edim", "points": 10},
          {"type": "scenario", "text": "SENARYO 3: BORCUN KAYNAKLARI (Sözleşme / Haksız Fiil / Sebepsiz Zenginleşme)", "sub_questions": [{"q": "A) Gübre almak için imza atması?", "a": "Sözleşme"}, {"q": "B) Traktörle komşunun çitini yıkması?", "a": "Haksız Fiil"}, {"q": "C) Bankanın yanlışlıkla hesaba para yatırması?", "a": "Sebepsiz Zenginleşme"}], "points": 15},
          {"type": "text", "question": "5. Kefilin borcun tamamından sorumlu olduğu kefillik türü?", "answer": "Müteselsil", "points": 10},
          {"type": "text", "question": "6. Borcun yerine getirilerek sona erdirilmesine ne denir?", "answer": "İfa", "points": 10},
          {"type": "text", "question": "7. Yazılı olmayan hukuk kaynaklarına ne denir?", "answer": "Örf ve Adet", "keywords": ["örf", "adet"], "points": 10},
          {"type": "text", "question": "8. Eşit bireyler arasındaki (örn: komşu kavgası) sorunları çözen hukuk dalı?", "answer": "Özel Hukuk", "points": 15}
        ]
      },
      "11. Sınıf": {
        "İş ve Sosyal Güvenlik Hukuku": [
          {"type": "scenario", "text": "SENARYO: Ege Tekstil A.Ş. sahibi Ali Bey, yönetimi Ayşe Hanım'a bırakmıştır. İşçi Mehmet Bey servis aracında kaza yapmıştır.", "sub_questions": [{"q": "1. Hukuken asıl İşveren kimdir?", "a": "Ege Tekstil"}, {"q": "İşveren Vekili kimdir?", "a": "Ayşe"}, {"q": "Servis aracı işyeri sayılır mı? (Evet/Hayır)", "a": "Evet"}], "points": 20},
          {"type": "scenario", "text": "2. İŞ SÖZLEŞMESİ UNSURLARI", "sub_questions": [{"q": "a) İşçi ne koyar? (Emek)", "a": "İş Görme"}, {"q": "b) Karşılığında ne alır?", "a": "Ücret"}, {"q": "c) İşveren ile ilişkisi nasıldır?", "a": "Bağımlılık"}], "points": 10},
          {"type": "text", "question": "3. Fabrika işçiliği Sürekli iş midir, Süreksiz iş midir?", "answer": "Sürekli", "points": 10},
          {"type": "text", "question": "4. İşçinin ticari sırları saklaması hangi borçtur?", "answer": "Sadakat", "points": 10},
          {"type": "text", "question": "6. İşverenin işçiyi korumak için almak zorunda olduğu önlemlerin genel adı?", "answer": "İş Sağlığı ve Güvenliği", "keywords": ["isg", "güvenlik"], "points": 10},
          {"type": "calculation", "text": "7. FAZLA ÇALIŞMA: Mehmet Bey 50 saat çalıştı (Normal: 45). Saat ücreti 200 TL. (%50 Zamlı)", "inputs": [{"label": "A) Fazla Çalışma Saati (50-45)", "correct": 5}, {"label": "B) 1 Saatlik Zamlı Ücret (200 x 1.5)", "correct": 300}, {"label": "C) Toplam Fazla Çalışma Ücreti", "correct": 1500}], "points": 30}
        ],
        "Şirketler Muhasebesi": [
          {"type": "calculation", "text": "SORU 1: KURULUŞ KAYDI (ALİ KARA LTD): Sermaye Taahhüdü 900.000 TL. (Nakit 50.000, Taşıt 700.000, Kalanı Çek ciro ederek ödüyor)", "inputs": [{"label": "500 Sermaye (Alacak)", "correct": 900000}, {"label": "100 Kasa (Borç)", "correct": 50000}, {"label": "254 Taşıtlar (Borç)", "correct": 700000}, {"label": "101 Alınan Çekler (Borç - Kalan)", "correct": 150000}], "points": 30},
          {"type": "calculation", "text": "SORU 2: SERMAYE ARTIRIMI (180.000 TL): Merve 150.000 (Yarısı Nakit, Yarısı Senet), Ayşe 30.000 (Banka).", "inputs": [{"label": "Merve - Nakit Tutarı (150bin / 2)", "correct": 75000}, {"label": "Merve - Senet Tutarı (121 Alacak Senetleri)", "correct": 75000}, {"label": "Ayşe - Banka Tutarı (102 Bankalar)", "correct": 30000}], "points": 20},
          {"type": "calculation", "text": "SORU 3: KAR DAĞITIMI (250.000 TL): Yavuz (%80), Ali (%20). Yavuz'a 50.000 Senet, kalanı Çek verilerek ödeniyor.", "inputs": [{"label": "Yavuz'un Kar Payı (%80)", "correct": 200000}, {"label": "Ali'nin Kar Payı (%20)", "correct": 50000}, {"label": "Yavuz'a Verilen Çek Tutarı (103 Verilen Çekler)", "correct": 150000}], "points": 30},
          {"type": "calculation", "text": "SORU 4: ZARAR DAĞITIMI (80.000 TL): Yusuf ve Mesut Eşit Paylaşacak.", "inputs": [{"label": "Yusuf'un Zarar Payı", "correct": 40000}, {"label": "Mesut'un Zarar Payı", "correct": 40000}], "points": 20}
        ],
        "Maliyet Muhasebesi": [
          {"type": "calculation", "text": "SORU 1: GİDER DAĞITIMI I: Yemek (20.000 -> Personel), Temizlik (30.000 -> Alan). Kesim: 60 Kişi, Dikim: 600 m2. (Toplam Personel: 200, Toplam Alan: 1500 m2).", "inputs": [{"label": "Kesim Bölümü Yemek Payı (20000/200*60)", "correct": 6000}, {"label": "Dikim Bölümü Temizlik Payı (30000/1500*600)", "correct": 12000}], "points": 20},
          {"type": "calculation", "text": "SORU 2: FIFO (İlk Giren İlk Çıkar) STOK: 01.05 Devir: 5000kg @ 30TL. | 15.05 Alış: 5500kg @ 35TL. | Üretime Sevk: 7500 kg.", "inputs": [{"label": "Kalan Stok Miktarı (10500 - 7500)", "correct": 3000}, {"label": "Kalan Stok Değeri (Hepsi son alıştan: 3000 x 35 TL)", "correct": 105000}], "points": 20},
          {"type": "calculation", "text": "SORU 3: DAĞITIM II (ABAY): Montaj Gideri 16.000 TL. Personel Sayısına göre dağıtılacak (Kesim 55, Döküm 25 kişi. Toplam 80).", "inputs": [{"label": "Birim Başına Yük (16000 / 80)", "correct": 200}, {"label": "Kesim'e Düşen Pay (55 x 200)", "correct": 11000}, {"label": "Döküm'e Düşen Pay (25 x 200)", "correct": 5000}], "points": 20},
          {"type": "calculation", "text": "SORU 4: BİRİM MALİYET: Toplam Maliyet Ekmek 75.000 (5000 adet), Poğaça 80.000 (4000 adet).", "inputs": [{"label": "Ekmek Birim Maliyet (75000/5000)", "correct": 15}, {"label": "Poğaça Birim Maliyet (80000/4000)", "correct": 20}], "points": 20}
        ]
      },
      "12. Sınıf": {
        "Bankacılık": [
          {"type": "scenario", "text": "SENARYO 1: Turist John 500 Dolar nakit bozduruyor. İthalatçı firma hesaptan 50.000 Euro gönderiyor.", "sub_questions": [{"q": "1. John'un cebindeki nakit paraya ne denir?", "a": "Efektif"}, {"q": "Hesaptan yapılan işleme ne denir?", "a": "Döviz"}, {"q": "2. Banka Dolar alıp TL veriyorsa bu işlem nedir?", "a": "Döviz Alış"}], "points": 20},
          {"type": "scenario", "text": "SENARYO 2: Ali Bey para gönderecek.", "sub_questions": [{"q": "3. Farklı bankaya para gönderme (Durum A)?", "a": "EFT"}, {"q": "Aynı bankaya para gönderme (Durum B)?", "a": "Havale"}, {"q": "4. Mesai saati dışı yapılan EFT hesaba ne zaman geçer (FAST hariç)?", "a": "Pazartesi"}], "points": 30},
          {"type": "text", "question": "5. Bankanın firmanın borcunu garanti ettiği (kefil olduğu) belgeye ne denir?", "answer": "Teminat Mektubu", "points": 10},
          {"type": "text", "question": "6. Parayı bir menkul kıymeti 'geri satma taahhüdüyle' alıp kısa vadeli değerlendirme?", "answer": "Repo", "points": 10},
          {"type": "scenario", "text": "7. KREDİ EŞLEŞTİRME", "sub_questions": [{"q": "Ev almak için?", "a": "Konut"}, {"q": "Araba almak için?", "a": "Taşıt"}, {"q": "Mobilya/Tatil için?", "a": "İhtiyaç"}], "points": 10},
          {"type": "text", "question": "8. Senet üzerine atılan kefillik imzasına ne ad verilir?", "answer": "Aval", "points": 10},
          {"type": "text", "question": "9. Tüketiciler için kredi kullanmanın bir faydasını yazınız.", "answer": "Nakit", "keywords": ["nakit", "standart", "ihtiyaç", "ödeme kolaylığı"], "points": 10}
        ]
      }
    }
    with open("exams.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

create_full_exams_json()

def init_state():
    defaults = {
        "logged_in": False, "user_role": None, "username": None, 
        "class_code": "GENEL", "active_menu": "📢 Kampüs Duvar", 
        "draft_content": "",
        "captcha_q": None, "captcha_a": None,
        "open_comments": [],
        "wall_mode": "Tüm Kampüs"
    }
    for k, v in defaults.items():
        if k not in st.session_state: st.session_state[k] = v

    if st.session_state['captcha_q'] is None:
        n1 = random.randint(1, 9); n2 = random.randint(1, 9)
        st.session_state['captcha_q'] = f"{n1} + {n2}"; st.session_state['captcha_a'] = n1 + n2

init_state()
database.create_database()

# --- YARDIMCI ---
def extract_youtube_link(text):
    if not text: return None
    match = re.search(r'(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/(watch\?v=|embed/|v/|live/|.+\?v=)?([^&=%\?]{11})', text)
    if match: return f"https://www.youtube.com/watch?v={match.group(6)}"
    return None

# --- CSS (MAĞAZA KARTLARI DÜZELTİLDİ) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@700&family=Orbitron:wght@700&family=Rye&family=Dancing+Script:wght@700&family=Metal+Mania&family=Press+Start+2P&family=Creepster&display=swap');

    .login-container { text-align: center; margin-top: 20px; }
    .login-main { font-family: 'Cinzel', serif; color: #FFD700; font-size: 2.2rem; text-shadow: 2px 2px 4px #000; font-weight: bold; }
    
    /* POST KARTI */
    .post-card { background-color: #1e293b; border: 1px solid #334155; border-radius: 12px; padding: 15px; margin-bottom: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.3); }
    .post-header { display: flex; align-items: center; border-bottom: 1px solid #334155; padding-bottom: 8px; margin-bottom: 8px; }
    .post-content { color: #e2e8f0; font-size: 0.95rem; white-space: pre-wrap; margin-bottom: 5px; }
    
    /* BUTONLAR (İKON İÇİN) */
    div.stButton > button { background-color: transparent !important; border: none !important; color: #94a3b8 !important; padding: 0px 5px !important; font-size: 1.3rem !important; margin-right: 15px !important; box-shadow: none !important;}
    div.stButton > button:hover { color: #FFD700 !important; transform: scale(1.1); }
    
    div[data-testid="column"] { padding: 0 !important; min-width: 0 !important; margin: 0 !important; flex: 0 0 auto !important; width: auto !important; }
    div[data-testid="stHorizontalBlock"] { align-items: center !important; flex-wrap: nowrap !important; }

    .comment-box { background: #0f172a; padding: 8px; border-radius: 6px; margin-top: 6px; font-size: 0.85rem; border-left: 3px solid #334155; }
    
    /* MAĞAZA GRİD (DÜZELTİLDİ - BUTONLAR SIKIŞTI) */
    .shop-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; margin-top: 10px; }
    @media only screen and (max-width: 600px) { .shop-grid { grid-template-columns: repeat(2, 1fr); } }
    
    .shop-item { 
        background: #0f172a; 
        border: 1px solid #334155; 
        border-radius: 8px; 
        padding: 5px; 
        text-align: center; 
        height: 120px; /* Küçültüldü */
        display: flex; 
        flex-direction: column; 
        align-items: center; 
        justify-content: space-between; 
        transition: transform 0.2s; 
    }
    .shop-item:hover { transform: translateY(-3px); border-color: #FFD700; }
    
    .shop-preview { 
        width: 40px; /* Küçültüldü */
        height: 40px; 
        margin-bottom: 2px; 
        display: flex; 
        align-items: center; 
        justify-content: center; 
        border-radius: 50%; 
        border: 2px solid #334155; 
    }
    .shop-name { font-size: 0.65rem; color: #cbd5e1; font-weight: bold; margin-bottom: 2px; line-height: 1.1; }
    
    /* MAĞAZA BUTONLARI İÇİN ÖZEL STİL */
    .shop-btn-container button {
        width: 100% !important;
        font-size: 0.7rem !important;
        padding: 2px !important;
        margin: 0 !important;
        border: 1px solid #10b981 !important;
        background-color: #10b981 !important;
        color: white !important;
        border-radius: 4px !important;
        height: auto !important;
    }

    /* STİLLER */
    .avatar-img { width: 40px; height: 40px; border-radius: 50%; object-fit: cover; }
    .frame-overlay { position: absolute; top: -3px; left: -3px; width: 46px; height: 46px; pointer-events: none; }
    
    .frame-Gold { border: 2px solid #FFD700; border-radius: 50%; box-shadow: 0 0 5px #FFD700; }
    .frame-Neon { border: 2px solid #00ffff; border-radius: 50%; box-shadow: 0 0 5px #00ffff; }
    .frame-Fire { border: 2px solid #ff4500; border-radius: 50%; box-shadow: 0 0 10px #ff4500; }
    .frame-King { border: 3px solid #ffd700; border-radius: 50%; box-shadow: 0 0 10px #ffd700; }
    .frame-Matrix { border: 2px dotted #00ff00; border-radius: 50%; }
    .frame-Ice { border: 2px solid #00bfff; border-radius: 50%; box-shadow: 0 0 8px #00bfff; }
    .frame-Dark { border: 2px solid #333; border-radius: 50%; box-shadow: inset 0 0 10px #000; }
    .frame-Nature { border: 2px solid #2ecc71; border-radius: 50%; }
    .frame-Cyber { border: 2px solid #ff00ff; border-radius: 50%; box-shadow: 0 0 5px #ff00ff; }
    .frame-Love { border: 2px solid #ff69b4; border-radius: 50%; box-shadow: 0 0 5px #ff69b4; }

    .name-Glitch { color: #00ffff; text-shadow: 1px 0 #ff00ff; font-weight: bold; }
    .name-Fire { color: #ff4500; text-shadow: 0 0 3px #ff0000; font-weight: bold; }
    .name-Gold { background: linear-gradient(to right, #BF953F, #FCF6BA, #B38728); -webkit-background-clip: text; color: transparent; font-weight: 900; }
    .name-Neon { color: #fff; text-shadow: 0 0 5px #fff, 0 0 10px #ff00de; font-weight: bold; }
    .name-Matrix { color: #00ff00; font-family: monospace; text-shadow: 0 0 2px #003300; }
    .name-Rainbow { background-image: linear-gradient(to left, violet, indigo, blue, green, yellow, orange, red); -webkit-background-clip: text; color: transparent; font-weight: bold; }
    .name-Ghost { color: #ffffff; opacity: 0.7; text-shadow: 0 0 10px #ffffff; }
    .name-Retro { font-family: 'Press Start 2P', cursive; color: #ffcc00; font-size: 0.7rem; }

    .font-Cinzel { font-family: 'Cinzel', serif; } .font-Orbitron { font-family: 'Orbitron', sans-serif; }
    .font-Rye { font-family: 'Rye', serif; } .font-Dancing { font-family: 'Dancing Script', cursive; }
    .font-Metallic { font-family: 'Metal Mania', cursive; color: #b0b0b0; }
    .font-Retro { font-family: 'Press Start 2P', cursive; font-size: 0.7rem; }
    .font-Horror { font-family: 'Creepster', cursive; color: #e74c3c; }

    .title-badge { background: #334155; color: #94a3b8; padding: 1px 5px; border-radius: 3px; font-size: 0.6rem; margin-left: 4px; }
</style>
""", unsafe_allow_html=True)

# --- GÖRSEL YARDIMCILAR ---
def get_user_display_html(username, size=40):
    ava, frame, name_style, _, font_style, title = database.get_user_styles(username)
    img_src = f"data:image/jpeg;base64,{ava}" if ava else "https://via.placeholder.com/150/CCCCCC/FFFFFF?text=U"
    f_html = f'<div class="frame-overlay frame-{frame}"></div>' if frame else ""
    classes = f"{f'name-{name_style}' if name_style else ''} {f'font-{font_style}' if font_style else ''}"
    return f'<div style="display:flex;align-items:center;"><div class="avatar-container"><img src="{img_src}" class="avatar-img">{f_html}</div><div style="margin-left:10px;"><div class="{classes}" style="font-size:0.9rem;">{username} {f"<span class='title-badge'>{title}</span>" if title else ""}</div></div></div>'

def get_post_style_css(username):
    _, _, _, post_style, font_style, _ = database.get_user_styles(username)
    return f"post-{post_style} font-{font_style}"

class SchoolServer:
    def join_or_update_student(self, c, u, p=0): 
        if p!=0: database.add_score(u, p, "Oyun")
        return database.get_total_score(u)
    def get_score(self, c, u): return database.get_total_score(u)
    def get_leaderboard(self, c):
        data = database.get_leaderboard_data()
        df = pd.DataFrame(data, columns=["Öğrenci","Puan"]) if data else pd.DataFrame(columns=["Öğrenci","Puan"])
        return df
    def buy_item(self, u, type, name, cost): return database.buy_item(u, type, name, cost)
    def send_gift(self, s, r, item, cost): return database.send_gift(s, r, item, cost)
server = SchoolServer()

@st.cache_data
def load_local_exams():
    if os.path.exists("exams.json"):
        try: return json.load(open("exams.json","r",encoding="utf-8"))
        except: return {}
    return {}

# --- TRANSFER JS ---
def get_transfer_js(username):
    return f"""function autoTransfer(){{let v=0;if(typeof score!=='undefined'&&score>0)v=score;else if(typeof money!=='undefined')v=Math.floor(money-startBalance);if(v<=0){{alert("Puan yok!");return;}}let b=document.getElementById('bBtn')||document.getElementById('mBtn');if(b){{b.innerText="...";b.disabled=true;}}try{{const u=new URL(window.top.location.href);u.searchParams.set('action','transfer');u.searchParams.set('u',"{username}");u.searchParams.set('a',v);u.searchParams.set('ts',Date.now());const l=document.createElement('a');l.href=u.toString();l.target="_top";document.body.appendChild(l);l.click();}}catch(e){{alert(e.message);}}}}"""

# --- OYUNLAR ---
def get_finance_game_html(start, user):
    js = get_transfer_js(user)
    return f"""<!DOCTYPE html><html><head><meta name="viewport" content="width=device-width,initial-scale=1.0"><style>body{{background:#0f172a;color:#fff;font-family:sans-serif;padding:5px;text-align:center}}.tab{{display:flex;justify-content:center;gap:10px;margin-bottom:10px}}.tab button{{background:#334155;border:none;color:#fff;padding:8px;border-radius:5px;cursor:pointer}}.active{{background:#3b82f6!important}}.grid{{display:grid;grid-template-columns:repeat(2,1fr);gap:5px}}.card{{background:#1e293b;padding:8px;border-radius:5px;border:1px solid #475569;cursor:pointer}}.btn{{background:radial-gradient(circle,#3b82f6,#1d4ed8);width:80px;height:80px;border-radius:50%;margin:10px auto;display:flex;align-items:center;justify-content:center;font-size:30px;box-shadow:0 0 15px #3b82f6;cursor:pointer}}.bank{{background:#10b981;color:white;width:100%;padding:12px;border:none;border-radius:8px;margin-top:10px;font-weight:bold}}</style></head><body><div style="font-size:20px;font-weight:bold;color:#fbbf24">💰 <span id="m">{start}</span></div><div style="font-size:12px;color:#94a3b8">Gelir: <span id="cps">0</span>/sn</div><div class="tab"><button onclick="sTab('main')" class="active" id="btn-main">İşletme</button><button onclick="sTab('mgr')" id="btn-mgr">Yöneticiler</button></div><div id="main"><div class="btn" onclick="clk()">👆</div><div class="grid" id="market"></div></div><div id="mgr" style="display:none"><div class="grid" id="managers"></div></div><button id="bBtn" class="bank" onclick="autoTransfer()">🏦 KASAYI BANKAYA AKTAR</button><script>let money={start},startBalance={start};const assets=[{{n:"Limonata",c:100,g:1,k:0}},{{n:"Simit",c:500,g:5,k:0}},{{n:"Kantin",c:2500,g:30,k:0}},{{n:"Cafe",c:10000,g:100,k:0}},{{n:"Yazılım",c:50000,g:600,k:0}},{{n:"Fabrika",c:200000,g:3000,k:0}},{{n:"Banka",c:1000000,g:15000,k:0}}];const mgrs=[{{n:"Çırak",c:5000,e:0,desc:"Limonata/Simit Oto"}},{{n:"Müdür",c:50000,e:0,desc:"Kantin/Cafe Oto"}},{{n:"CEO",c:1000000,e:0,desc:"x2 Hız"}}];function u(){{document.getElementById('m').innerText=Math.floor(money).toLocaleString();let total=assets.reduce((t,x)=>t+(x.k*x.g),0)*(mgrs[2].e?2:1);document.getElementById('cps').innerText=total.toLocaleString();let h='';assets.forEach((x,i)=>{{let p=Math.floor(x.c*Math.pow(1.15,x.k));h+=`<div class="card" onclick="b(${{i}})"><b>${{x.n}}</b> (${{x.k}})<br><span style="color:#f87171">${{p.toLocaleString()}}</span><br><span style="color:#34d399">+${{x.g}}</span></div>`}});document.getElementById('market').innerHTML=h;let m='';mgrs.forEach((x,i)=>{{m+=`<div class="card" onclick="bm(${{i}})" style="opacity:${{x.e?0.5:1}}"><b>${{x.n}}</b><br><span style="color:#fbbf24">${{x.c.toLocaleString()}}</span><br><small>${{x.desc}}</small></div>`}});document.getElementById('managers').innerHTML=m;}}function clk(){{money+=1+(assets[0].k*0.1);u()}}function b(i){{let x=assets[i],p=Math.floor(x.c*Math.pow(1.15,x.k));if(money>=p){{money-=p;x.k++;u()}}}}function bm(i){{if(!mgrs[i].e&&money>=mgrs[i].c){{money-=mgrs[i].c;mgrs[i].e=1;u()}}}}function sTab(t){{document.getElementById('main').style.display='none';document.getElementById('mgr').style.display='none';document.getElementById('btn-main').className='';document.getElementById('btn-mgr').className='';document.getElementById(t).style.display='block';document.getElementById('btn-'+t).className='active';}}setInterval(()=>{{let g=assets.reduce((t,x)=>t+(x.k*x.g),0)*(mgrs[2].e?2:1);if(mgrs[0].e)g+=(assets[0].g*assets[0].k+assets[1].g*assets[1].k)*0.5;if(mgrs[1].e)g+=(assets[2].g*assets[2].k+assets[3].g*assets[3].k)*0.5;if(g>0){{money+=g/10;u()}}}},100);u();{js}</script></body></html>"""

def get_matrix_game_html(user):
    js = get_transfer_js(user)
    return f"""<!DOCTYPE html><html><head><meta name="viewport" content="width=device-width,initial-scale=1.0,maximum-scale=1.0,user-scalable=no"><style>body{{background:#050505;color:#00ffff;margin:0;overflow:hidden;touch-action:none;text-align:center}}canvas{{background:#111;border:2px solid #333;margin-top:10px}}.btn{{position:absolute;top:10px;right:10px;background:#ff00ff;border:none;padding:5px 15px;border-radius:15px;font-weight:bold;color:white}}</style></head><body><div style="padding:10px;display:flex;justify-content:space-between"><span>PUAN: <span id="s">0</span></span><button id="mBtn" class="btn" onclick="autoTransfer()">AKTAR</button></div><canvas id="c"></canvas><script>const cvs=document.getElementById('c'),ctx=cvs.getContext('2d');const R=10,C=8;let SQ=25,grid=[],pieces=[],drag=null,score=0;const SHAPES=[[[1]],[[1,1]],[[1],[1]],[[1,1,1]],[[1,0],[1,0],[1,1]]];function rs(){{let w=window.innerWidth,h=window.innerHeight;SQ=Math.floor(Math.min((w-20)/C,(h-100)/R));SQ=Math.min(SQ,35);cvs.width=SQ*C;cvs.height=SQ*R+120;d()}}window.addEventListener('resize',rs);function init(){{grid=Array(R).fill().map(()=>Array(C).fill(0));score=0;document.getElementById('s').innerText=0;rs();sp()}}function sp(){{pieces=[];let y=R*SQ+20,w=cvs.width/3;for(let i=0;i<3;i++){{let s=SHAPES[Math.floor(Math.random()*SHAPES.length)];pieces.push({{s:s,x:w*i+5,y:y,bx:w*i+5,by:y,sc:0.6}})}}d()}}function d(){{ctx.fillStyle="#000000";ctx.fillRect(0,0,cvs.width,cvs.height);for(let r=0;r<R;r++)for(let c=0;c<C;c++){{ctx.strokeStyle="#333";ctx.lineWidth=1;ctx.strokeRect(c*SQ,r*SQ,SQ,SQ);if(grid[r][c]){{ctx.fillStyle="#00ffff";ctx.fillRect(c*SQ+3,r*SQ+3,SQ-6,SQ-6);ctx.strokeStyle="#ff00ff";ctx.strokeRect(c*SQ+3,r*SQ+3,SQ-6,SQ-6)}}}}ctx.strokeStyle="white";ctx.beginPath();ctx.moveTo(0,R*SQ);ctx.lineTo(cvs.width,R*SQ);ctx.stroke();pieces.forEach(p=>{{if(p!==drag)ds(p.s,p.x,p.y,SQ*p.sc,"#555")}});if(drag)ds(drag.s,drag.x,drag.y,SQ,"#ff00ff")}}function ds(s,x,y,z,c){{ctx.fillStyle=c;for(let r=0;r<s.length;r++)for(let k=0;k<s[r].length;k++)if(s[r][k])ctx.fillRect(x+k*z,y+r*z,z,z)}}function gp(e){{let r=cvs.getBoundingClientRect(),t=e.touches?e.touches[0]:e;return{{x:t.clientX-r.left,y:t.clientY-r.top}}}}function chk(){{for(let r=0;r<R;r++)if(grid[r].every(x=>x)){{grid[r].fill(0);score+=50}}for(let c=0;c<C;c++){{let f=true;for(let r=0;r<R;r++)if(!grid[r][c])f=false;if(f){{for(let r=0;r<R;r++)grid[r][c]=0;score+=50}}}}document.getElementById('s').innerText=score;if(pieces.length===0)sp()}}cvs.addEventListener('touchstart',e=>{{let p=gp(e);pieces.forEach(pi=>{{if(p.x>=pi.x&&p.x<=pi.x+60&&p.y>=pi.y&&p.y<=pi.y+60)drag=pi}})}},{{passive:false}});cvs.addEventListener('touchmove',e=>{{e.preventDefault();if(drag){{let p=gp(e);drag.x=p.x-20;drag.y=p.y-20;d()}}}},{{passive:false}});cvs.addEventListener('touchend',e=>{{if(drag){{let gx=Math.round(drag.x/SQ),gy=Math.round(drag.y/SQ),fit=true;for(let r=0;r<drag.s.length;r++)for(let c=0;c<drag.s[r].length;c++)if(drag.s[r][c]){{if(gx+c<0||gx+c>=C||gy+r>=R||grid[gy+r][gx+c])fit=false}}if(fit){{for(let r=0;r<drag.s.length;r++)for(let c=0;c<drag.s[r].length;c++)if(drag.s[r][c])grid[gy+r][gx+c]=1;pieces=pieces.filter(p=>p!==drag);score+=10;chk()}}else{{drag.x=drag.bx;drag.y=drag.by}}drag=null;d()}}}},{{passive:false}});init();{js}</script></body></html>"""

# --- ARAYÜZ ---
if not st.session_state['logged_in']:
    st.markdown('<div class="login-container"><div class="login-sub">Muhasebe ve Finansman Alanı</div><div class="login-main">DİJİTAL GELİŞİM PLATFORMU</div><div class="login-sub">~ Dijital Kampüs ~</div></div>', unsafe_allow_html=True)
    with st.sidebar:
        if st.button("⚠️ SİSTEMİ SIFIRLA"):
            try:
                if os.path.exists("education_platform.db"): os.remove("education_platform.db")
                st.success("Sıfırlandı! Yenile."); time.sleep(1); st.rerun()
            except: st.error("Hata.")
    with st.container():
        with st.form("login"):
            u = st.text_input("Kullanıcı Adı")
            p = st.text_input("Şifre", type="password")
            if st.form_submit_button("Giriş"):
                user = database.login_user(u, p)
                if user:
                    st.session_state.update({'logged_in':True, 'username':user[1], 'user_role':user[3]})
                    database.update_activity(user[1])
                    st.rerun()
                else: st.error("Hatalı!")
        with st.expander("Kayıt Ol"):
            with st.form("reg"):
                nu = st.text_input("Kullanıcı"); np = st.text_input("Şifre", type="password")
                st.write(f"Güvenlik: **{st.session_state['captcha_q']} = ?**")
                ans = st.number_input("Cevap", step=1)
                if st.form_submit_button("Kayıt"):
                    if ans == st.session_state['captcha_a']:
                        res, rank = database.add_user(nu, np, "student")
                        if res:
                            st.session_state['captcha_q'] = None; st.success("Kaydedildi!")
                        else: st.error("Dolu.")
                    else: st.error("Yanlış."); st.session_state['captcha_q'] = None; st.rerun()
else:
    database.update_activity(st.session_state['username'])
    
    with st.sidebar:
        st.markdown(get_user_display_html(st.session_state['username'], size=70), unsafe_allow_html=True)
        st.write("") 
        
        with st.expander("⚙️ Hesabım"):
            nname = st.text_input("Yeni İsim")
            cost = 0 if database.get_user_change_count(st.session_state['username']) == 0 else 500000
            if st.button(f"Değiştir ({cost:,} P)"):
                if nname:
                    ok, msg = database.change_username_logic(st.session_state['username'], nname)
                    if ok: st.session_state['username'] = nname; st.success(msg); time.sleep(1); st.rerun()
                    else: st.error(msg)
            
            st.divider()
            uploaded_avatar = st.file_uploader("Fotoğraf", type=['png', 'jpg'])
            if uploaded_avatar:
                if database.update_avatar(st.session_state['username'], uploaded_avatar): st.success("Yüklendi!"); time.sleep(1); st.rerun()
            
            st.divider()
            search_u = st.selectbox("Arkadaş Ara", database.get_searchable_users(st.session_state['username']))
            if st.button("Ekle"):
                ok, msg = database.send_friend_request(st.session_state['username'], search_u)
                if ok: st.success(msg)
                else: st.warning(msg)

        reqs = database.get_pending_requests(st.session_state['username'])
        if reqs:
            st.info("İstekler Var")
            for r in reqs:
                c1, c2 = st.columns([2,1])
                c1.write(r[1])
                if c2.button("Kabul", key=f"ac_{r[0]}"): database.accept_request(r[1], st.session_state['username']); st.rerun()
        
        st.write(""); 
        if st.button("🚪 Çıkış Yap"): st.session_state['logged_in']=False; st.rerun()

    st.markdown(f'<div class="top-bar"><div class="user-greeting">Merhaba, {st.session_state["username"]}</div><div class="role-badge">{st.session_state["user_role"]}</div></div>', unsafe_allow_html=True)
    
    # Bildirim
    noti_count = database.get_unread_notification_count(st.session_state['username'])
    noti_text = f"🔔 ({noti_count})" if noti_count > 0 else "🔔"
    menu = ["📢 Kampüs Duvar", "💬 Mesaj", "🏆 Puan", "📚 Ders", "🎮 Oyun", "🛒 Mağaza", noti_text]
    if st.session_state['user_role'] == 'admin': menu.append("⚙️ Admin")
    
    curr = st.session_state['active_menu']
    if curr.startswith("🔔") and curr != noti_text: curr = noti_text
    try: ix = menu.index(curr)
    except: ix = 0
    sel = st.radio("", menu, index=ix, horizontal=True, label_visibility="collapsed")
    if sel != st.session_state['active_menu']: st.session_state['active_menu'] = sel; st.rerun()

    if sel == "📢 Kampüs Duvar":
        st.subheader("Kampüs Duvar")
        st.session_state['wall_mode'] = st.selectbox("Görünüm:", ["Tüm Kampüs", "Benim Profilim"], label_visibility="collapsed")
        
        ms = database.get_total_score(st.session_state['username'])
        if ms >= 1000000 or st.session_state['user_role'] == 'admin':
            with st.expander("✨ Paylaşım (-100,000 P)", expanded=False):
                with st.form("sh"):
                    def_val = st.session_state.get('draft_content', "")
                    txt = st.text_area("İçerik", value=def_val); img = st.file_uploader("Resim", type=['png','jpg'])
                    if st.form_submit_button("Paylaş"):
                        if ms >= 100000:
                            database.add_score(st.session_state['username'], -100000, "Post")
                            database.add_post(st.session_state['username'], txt, img)
                            st.session_state['draft_content'] = ""
                            st.rerun()
                        else: st.error("Yetersiz Puan")
        
        all_posts = database.get_posts(50)
        posts = [p for p in all_posts if p[1] == st.session_state['username']] if st.session_state['wall_mode'] == "Benim Profilim" else all_posts
        
        for p in posts:
            st.markdown(f"""
            <div class="post-card">
                <div class="post-header">
                    {get_user_display_html(p[1], size=35)}
                    <span style="color:#94a3b8;font-size:0.7rem;margin-left:auto;">{p[4]}</span>
                </div>
                <div class="{get_post_style_css(p[1])} post-content">{p[2] if p[2] else ''}</div>
                {f'<img src="data:image/jpeg;base64,{p[3]}" class="post-image">' if p[3] else ''}
            </div>
            """, unsafe_allow_html=True)
            if p[2]:
                yt = extract_youtube_link(p[2])
                if yt: st.video(yt)
            
            c1, c2, c3, c4 = st.columns([0.15, 0.15, 0.15, 0.55]) 
            with c1: 
                if st.button(f"❤️ {p[5]}", key=f"l_{p[0]}"): database.like_post(p[0]); st.rerun()
            with c2: 
                if st.button("💬", key=f"c_btn_{p[0]}"):
                    if p[0] in st.session_state['open_comments']: st.session_state['open_comments'].remove(p[0])
                    else: st.session_state['open_comments'].append(p[0])
                    st.rerun()
            with c3:
                if st.button("🔄", key=f"r_{p[0]}"): st.session_state['draft_content'] = f"Alıntı (@{p[1]}): {p[2]}"; st.rerun()
            if st.session_state['username'] == p[1] or st.session_state['user_role'] == 'admin':
                with c4:
                    _, sc2 = st.columns([0.8, 0.2])
                    with sc2:
                        with st.popover("⋮"):
                            if st.button("Sil", key=f"d_{p[0]}"): database.delete_post(p[0]); st.rerun()

            if p[0] in st.session_state['open_comments']:
                comments = database.get_comments(p[0])
                if comments:
                    for c in comments: st.markdown(f"<div class='comment-box'>{get_user_display_html(c[0], size=20)} &nbsp; {c[1]}</div>", unsafe_allow_html=True)
                with st.form(f"c_form_{p[0]}", clear_on_submit=True):
                    ct = st.text_input("Yorum Yaz...", label_visibility="collapsed")
                    if st.form_submit_button("Gönder"): 
                        if ct: database.add_comment(p[0], st.session_state['username'], ct); st.rerun()
            st.write("") 

    elif sel == "🛒 Mağaza":
        st.header("Mağaza 💎")
        st.metric("Bakiye", f"{server.get_score('GENEL', st.session_state['username']):,} P")
        
        tabs = st.tabs(["Çerçeve", "İsim", "Font", "🎁 Hediye"])
        
        # ÇERÇEVELER
        with tabs[0]: 
            items = [
                {"n": "Gold", "c": 50000, "t": "frame", "v": "Gold", "css":"frame-Gold"}, 
                {"n": "Neon", "c": 150000, "t": "frame", "v": "Neon", "css":"frame-Neon"}, 
                {"n": "Alev", "c": 300000, "t": "frame", "v": "Fire", "css":"frame-Fire"}, 
                {"n": "Kral", "c": 2000000, "t": "frame", "v": "King", "css":"frame-King"},
                {"n": "Matrix", "c": 500000, "t": "frame", "v": "Matrix", "css":"frame-Matrix"},
                {"n": "Buz", "c": 750000, "t": "frame", "v": "Ice", "css":"frame-Ice"},
                {"n": "Karanlık", "c": 100000, "t": "frame", "v": "Dark", "css":"frame-Dark"},
                {"n": "Doğa", "c": 250000, "t": "frame", "v": "Nature", "css":"frame-Nature"},
                {"n": "Siber", "c": 600000, "t": "frame", "v": "Cyber", "css":"frame-Cyber"},
                {"n": "Aşk", "c": 400000, "t": "frame", "v": "Love", "css":"frame-Love"}
            ]
            rows = [items[i:i+4] for i in range(0, len(items), 4)]
            for row in rows:
                cols = st.columns(4)
                for i, it in enumerate(row):
                    with cols[i]:
                        preview = f'<div class="shop-preview"><div class="{it["css"]}" style="width:100%;height:100%;border-radius:50%;"></div></div>'
                        st.markdown(f'<div class="shop-item">{preview}<div class="shop-name">{it["n"]}</div><div class="shop-btn-container"></div></div>', unsafe_allow_html=True)
                        if st.button(f"AL ({it['c']:,})", key=f"buy_fr_{it['n']}"):
                            ok, msg = database.buy_item(st.session_state['username'], it['t'], it['v'], it['c'])
                            if ok: st.success(msg); time.sleep(1); st.rerun()
                            else: st.error(msg)

        # İSİMLER
        with tabs[1]:
            items = [
                {"n": "Glitch", "c": 100000, "t": "name", "v": "Glitch", "css":"name-Glitch"},
                {"n": "Alevli", "c": 400000, "t": "name", "v": "Fire", "css":"name-Fire"},
                {"n": "Altın", "c": 750000, "t": "name", "v": "Gold", "css":"name-Gold"},
                {"n": "Neon", "c": 500000, "t": "name", "v": "Neon", "css":"name-Neon"},
                {"n": "Matrix", "c": 300000, "t": "name", "v": "Matrix", "css":"name-Matrix"},
                {"n": "Gökkuşağı", "c": 1000000, "t": "name", "v": "Rainbow", "css":"name-Rainbow"},
                {"n": "Hayalet", "c": 250000, "t": "name", "v": "Ghost", "css":"name-Ghost"},
                {"n": "Retro", "c": 150000, "t": "name", "v": "Retro", "css":"name-Retro"}
            ]
            rows = [items[i:i+4] for i in range(0, len(items), 4)]
            for row in rows:
                cols = st.columns(4)
                for i, it in enumerate(row):
                    with cols[i]:
                        preview = f'<div class="{it["css"]}" style="font-size:0.8rem;">İSİM</div>'
                        st.markdown(f'<div class="shop-item"><div style="margin-top:20px;">{preview}</div><div class="shop-name">{it["n"]}</div></div>', unsafe_allow_html=True)
                        if st.button(f"AL ({it['c']:,})", key=f"buy_nm_{it['n']}"):
                            ok, msg = database.buy_item(st.session_state['username'], it['t'], it['v'], it['c'])
                            if ok: st.success(msg); time.sleep(1); st.rerun()
                            else: st.error(msg)

        # FONTLAR
        with tabs[2]:
            items = [
                {"n": "Cinzel", "c": 150000, "t": "font", "v": "Cinzel", "css":"font-Cinzel"},
                {"n": "Orbitron", "c": 250000, "t": "font", "v": "Orbitron", "css":"font-Orbitron"},
                {"n": "Rye", "c": 350000, "t": "font", "v": "Rye", "css":"font-Rye"},
                {"n": "Dans", "c": 500000, "t": "font", "v": "Dancing", "css":"font-Dancing"},
                {"n": "Metalik", "c": 1000000, "t": "font", "v": "Metallic", "css":"font-Metallic"},
                {"n": "Retro", "c": 600000, "t": "font", "v": "Retro", "css":"font-Retro"},
                {"n": "Korku", "c": 800000, "t": "font", "v": "Horror", "css":"font-Horror"}
            ]
            rows = [items[i:i+4] for i in range(0, len(items), 4)]
            for row in rows:
                cols = st.columns(4)
                for i, it in enumerate(row):
                    with cols[i]:
                        preview = f'<div class="{it["css"]}" style="font-size:1rem;">Aa</div>'
                        st.markdown(f'<div class="shop-item"><div style="margin-top:20px;">{preview}</div><div class="shop-name">{it["n"]}</div></div>', unsafe_allow_html=True)
                        if st.button(f"AL ({it['c']:,})", key=f"buy_fn_{it['n']}"):
                            ok, msg = database.buy_item(st.session_state['username'], it['t'], it['v'], it['c'])
                            if ok: st.success(msg); time.sleep(1); st.rerun()
                            else: st.error(msg)

        # HEDİYELER
        with tabs[3]:
            st.info("Hediye göndererek arkadaşını mutlu et!")
            all_users = database.get_all_users_list(st.session_state['username'])
            t_user = st.selectbox("Kime:", all_users)
            gifts = [("Kahve ☕", 5000), ("Çikolata 🍫", 10000), ("Gül 🌹", 25000), ("Taç 👑", 100000), ("Araba 🏎️", 500000), ("Elmas 💎", 1000000), ("Uçak ✈️", 2000000), ("Diploma 📜", 50000), ("Yat 🛥️", 3000000), ("Ev 🏠", 5000000)]
            
            rows = [gifts[i:i+4] for i in range(0, len(gifts), 4)]
            for row in rows:
                cols = st.columns(4)
                for i, (gn, gp) in enumerate(row):
                    with cols[i]:
                        st.markdown(f'<div class="shop-item"><div style="font-size:1.5rem;margin-top:10px;">{gn.split()[-1]}</div><div class="shop-name">{gn}</div></div>', unsafe_allow_html=True)
                        if st.button(f"GÖNDER ({gp:,})", key=f"gift_{gn}"):
                            ok, msg = database.send_gift(st.session_state['username'], t_user, gn, gp)
                            if ok: st.success(msg)
                            else: st.error(msg)

    elif sel.startswith("🔔"):
        st.header("Bildirimler")
        database.mark_notifications_read(st.session_state['username'])
        st.success("Tüm bildirimler okundu.")

    elif sel == "💬 Mesaj":
        st.subheader("Mesajlaşma")
        friends = database.get_friends(st.session_state['username'])
        if not friends: st.info("Henüz arkadaşın yok. Yan menüden ekleyebilirsin.")
        else:
            target = st.selectbox("Kime:", friends)
            if target:
                msgs = database.get_conversation(st.session_state['username'], target)
                for m in msgs:
                    align = "row-reverse" if m[0] == st.session_state['username'] else "row"
                    bg = "#2563eb" if m[0] == st.session_state['username'] else "#334155"
                    st.markdown(f"""<div style="display:flex;flex-direction:{align};margin-bottom:5px;"><div style="background:{bg};padding:8px;border-radius:10px;max-width:70%;">{m[1]}</div></div>""", unsafe_allow_html=True)
                with st.form("msg_form", clear_on_submit=True):
                    msg_txt = st.text_input("Mesaj")
                    if st.form_submit_button("Gönder"):
                        if msg_txt: database.send_message(st.session_state['username'], target, msg_txt); st.rerun()

    elif sel == "🏆 Puan":
        st.dataframe(server.get_leaderboard("GENEL"), use_container_width=True)

    elif sel == "📚 Ders":
        EX = load_local_exams()
        if EX:
            cls = st.selectbox("Sınıf", list(EX.keys())); lsn = st.selectbox("Ders", list(EX[cls].keys()))
            questions = EX[cls][lsn]
            
            with st.form("exam_form"):
                score = 0
                total_possible = 0
                st.info(f"{lsn} Sınavı")
                
                for i, q in enumerate(questions):
                    st.markdown(f"---")
                    
                    q_type = q.get('type', 'text')
                    
                    if q_type == 'scenario':
                        st.write(f"**SENARYO:** {q['text']}")
                        for sub_q in q['sub_questions']:
                            st.write(f"- {sub_q['q']}")
                            user_ans = st.text_input("Cevap", key=f"sc_{i}_{sub_q['q']}")
                            if user_ans and sub_q['a'].lower() in user_ans.lower(): score += (q['points'] / len(q['sub_questions']))
                        total_possible += q['points']
                    
                    elif q_type == 'calculation':
                        st.write(f"**HESAPLAMA:** {q['text']}")
                        for inp in q['inputs']:
                            val = st.number_input(inp['label'], key=f"cal_{i}_{inp['label']}")
                            if val == inp['correct']: score += (q['points'] / len(q['inputs']))
                        total_possible += q['points']
                    
                    elif q_type == 'test':
                        st.write(f"**{i+1}. {q.get('question')}**")
                        ans = st.radio("Seçiniz", q['options'], key=f"rad_{i}")
                        if ans == q['answer']: score += q['points']
                        total_possible += q['points']
                    
                    elif q_type == 'text':
                        st.write(f"**{i+1}. {q.get('question')}**")
                        ans = st.text_input("Cevap", key=f"txt_{i}")
                        if ans:
                            correct = False
                            if ans.lower() == q['answer'].lower(): correct = True
                            if 'keywords' in q:
                                for k in q['keywords']:
                                    if k.lower() in ans.lower(): correct = True
                            if correct: score += q['points']
                        total_possible += q['points']

                if st.form_submit_button("Sınavı Tamamla"):
                    database.add_score(st.session_state['username'], int(score), f"Sınav: {lsn}")
                    st.balloons()
                    st.success(f"Sınav Bitti! Puanın: {int(score)} / {total_possible}")
                    time.sleep(3)
                    st.rerun()

    elif sel == "🎮 Oyun":
        gm = st.selectbox("Seç", ["Finans İmparatoru", "Asset Matrix"])
        sc = server.get_score("GENEL", st.session_state['username'])
        if gm == "Finans İmparatoru": components.html(get_finance_game_html(sc, st.session_state['username']), height=600)
        else: components.html(get_matrix_game_html(st.session_state['username']), height=750)

    elif sel == "⚙️ Admin":
        st.header("Admin")
        st.subheader("Kullanıcı Düzenle")
        all_u = [u[0] for u in database.get_all_users()]
        target_u = st.selectbox("Kullanıcı", all_u)
        new_p = st.number_input("Puan Ekle", value=0)
        if st.button("Güncelle"): database.add_score(target_u, new_p, "Admin"); st.success("Tamam!")
        st.divider()
        if st.button("Sil"): database.delete_user(target_u); st.error("Silindi!"); st.rerun()
