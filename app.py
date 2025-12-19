import streamlit as st
import random
import os
import time
import fitz  # PyMuPDF

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Bağarası Hibrit Eğitim Merkezi", page_icon="🎓", layout="wide")

# --- TASARIM VE GİZLİLİK ---
st.markdown("""
    <style>
    .stApp { background-color: #F0F4C3 !important; }
    h1, h2, h3, h4, .stMarkdown, p { color: #212121 !important; }
    
    /* Gereksiz Menüleri Gizle */
    .stDeployButton {display:none;}
    footer {visibility: hidden;}
    #MainMenu {visibility: hidden;}
    
    /* Giriş Kartı Tasarımı */
    .giris-kart {
        background-color: white;
        padding: 30px;
        border-radius: 20px;
        border: 3px solid #FF7043;
        text-align: center;
        box-shadow: 0 8px 16px rgba(0,0,0,0.1);
        margin-bottom: 20px;
    }
    
    /* İmza Alanı */
    .imza {
        margin-top: 50px;
        font-family: 'Courier New', monospace;
        color: #555;
        font-size: 14px;
        text-align: center;
        border-top: 1px solid #aaa;
        padding-top: 10px;
    }
    
    /* Butonlar */
    .stButton>button {
        background-color: #FF7043 !important;
        color: white !important;
        border-radius: 8px;
        font-weight: bold;
        width: 100%;
        border: 2px solid #D84315 !important;
        min-height: 45px;
    }
    .stButton>button:hover {
        background-color: #E64A19 !important;
    }
    </style>
""", unsafe_allow_html=True)

# ==============================================================================
# 1. VERİ HAVUZU: PDF HARİTASI (TYT)
# ==============================================================================
PDF_HARITASI = {
    # TÜRKÇE
    13: {"ders": "Türkçe", "cevaplar": "ECE"}, 14: {"ders": "Türkçe", "cevaplar": "BAC"},
    15: {"ders": "Türkçe", "cevaplar": "BEA"}, 16: {"ders": "Türkçe", "cevaplar": "CBCD"},
    17: {"ders": "Türkçe", "cevaplar": "AABA"}, 18: {"ders": "Türkçe", "cevaplar": "CEA"},
    19: {"ders": "Türkçe", "cevaplar": "EBA"}, 20: {"ders": "Türkçe", "cevaplar": "ADB"},
    21: {"ders": "Türkçe", "cevaplar": "CBBE"}, 22: {"ders": "Türkçe", "cevaplar": "BB"},
    23: {"ders": "Türkçe", "cevaplar": "BEA"}, 24: {"ders": "Türkçe", "cevaplar": "ADE"},
    25: {"ders": "Türkçe", "cevaplar": "EAB"}, 26: {"ders": "Türkçe", "cevaplar": "CD"},
    27: {"ders": "Türkçe", "cevaplar": "CDA"}, 28: {"ders": "Türkçe", "cevaplar": "DD"},
    29: {"ders": "Türkçe", "cevaplar": "BD"}, 30: {"ders": "Türkçe", "cevaplar": "BDA"},
    31: {"ders": "Türkçe", "cevaplar": "EAD"}, 32: {"ders": "Türkçe", "cevaplar": "AB"},
    33: {"ders": "Türkçe", "cevaplar": "BAA"}, 34: {"ders": "Türkçe", "cevaplar": "DCB"},
    35: {"ders": "Türkçe", "cevaplar": "CAD"}, 36: {"ders": "Türkçe", "cevaplar": "DDB"},
    37: {"ders": "Türkçe", "cevaplar": "CBD"}, 38: {"ders": "Türkçe", "cevaplar": "AA"},
    39: {"ders": "Türkçe", "cevaplar": "EBE"}, 40: {"ders": "Türkçe", "cevaplar": "BDE"},
    41: {"ders": "Türkçe", "cevaplar": "ADA"}, 42: {"ders": "Türkçe", "cevaplar": "CDB"},
    43: {"ders": "Türkçe", "cevaplar": "AC"}, 44: {"ders": "Türkçe", "cevaplar": "DEA"},
    88: {"ders": "Türkçe", "cevaplar": "CD"}, 89: {"ders": "Türkçe", "cevaplar": "EE"},
    90: {"ders": "Türkçe", "cevaplar": "AB"}, 91: {"ders": "Türkçe", "cevaplar": "DC"},
    92: {"ders": "Türkçe", "cevaplar": "BAA"}, 93: {"ders": "Türkçe", "cevaplar": "CB"},
    97: {"ders": "Türkçe", "cevaplar": "DC"}, 98: {"ders": "Türkçe", "cevaplar": "EB"},
    99: {"ders": "Türkçe", "cevaplar": "EA"}, 100: {"ders": "Türkçe", "cevaplar": "BB"},
    101: {"ders": "Türkçe", "cevaplar": "ED"}, 102: {"ders": "Türkçe", "cevaplar": "CEC"},
    103: {"ders": "Türkçe", "cevaplar": "AA"}, 107: {"ders": "Türkçe", "cevaplar": "BC"},
    108: {"ders": "Türkçe", "cevaplar": "AC"}, 109: {"ders": "Türkçe", "cevaplar": "EDD"},
    110: {"ders": "Türkçe", "cevaplar": "BC"}, 111: {"ders": "Türkçe", "cevaplar": "EC"},
    112: {"ders": "Türkçe", "cevaplar": "DA"}, 121: {"ders": "Türkçe", "cevaplar": "DCED"},
    122: {"ders": "Türkçe", "cevaplar": "DEDB"}, 123: {"ders": "Türkçe", "cevaplar": "ABA"},
    124: {"ders": "Türkçe", "cevaplar": "EEDA"}, 125: {"ders": "Türkçe", "cevaplar": "DAC"},
    126: {"ders": "Türkçe", "cevaplar": "CBAE"}, 127: {"ders": "Türkçe", "cevaplar": "DEB"},
    128: {"ders": "Türkçe", "cevaplar": "BDDB"}, 129: {"ders": "Türkçe", "cevaplar": "CBCE"},
    130: {"ders": "Türkçe", "cevaplar": "CCCC"}, 131: {"ders": "Türkçe", "cevaplar": "DEDD"},
    132: {"ders": "Türkçe", "cevaplar": "BCCC"}, 133: {"ders": "Türkçe", "cevaplar": "C"},
    # TARİH
    138: {"ders": "Tarih", "cevaplar": "BDEE"}, 139: {"ders": "Tarih", "cevaplar": "CEDA"},
    140: {"ders": "Tarih", "cevaplar": "CADC"}, 141: {"ders": "Tarih", "cevaplar": "CEEE"},
    142: {"ders": "Tarih", "cevaplar": "DED"}, 143: {"ders": "Tarih", "cevaplar": "AE"},
    144: {"ders": "Tarih", "cevaplar": "BABC"}, 145: {"ders": "Tarih", "cevaplar": "ADCE"},
    146: {"ders": "Tarih", "cevaplar": "BCBD"}, 147: {"ders": "Tarih", "cevaplar": "CBCE"},
    148: {"ders": "Tarih", "cevaplar": "ACE"},
    # COĞRAFYA
    151: {"ders": "Coğrafya", "cevaplar": "CACE"}, 152: {"ders": "Coğrafya", "cevaplar": "AAB"},
    153: {"ders": "Coğrafya", "cevaplar": "BBB"}, 154: {"ders": "Coğrafya", "cevaplar": "BBAA"},
    155: {"ders": "Coğrafya", "cevaplar": "CBC"}, 156: {"ders": "Coğrafya", "cevaplar": "ECA"},
    157: {"ders": "Coğrafya", "cevaplar": "CD"}, 158: {"ders": "Coğrafya", "cevaplar": "EC"},
    159: {"ders": "Coğrafya", "cevaplar": "AC"}, 160: {"ders": "Coğrafya", "cevaplar": "EEDE"},
    161: {"ders": "Coğrafya", "cevaplar": "DCBD"}, 162: {"ders": "Coğrafya", "cevaplar": "CDDD"},
    163: {"ders": "Coğrafya", "cevaplar": "CD"},
    # FELSEFE
    168: {"ders": "Felsefe", "cevaplar": "CD"}, 169: {"ders": "Felsefe", "cevaplar": "BD"},
    170: {"ders": "Felsefe", "cevaplar": "EB"}, 171: {"ders": "Felsefe", "cevaplar": "BE"},
    172: {"ders": "Felsefe", "cevaplar": "BB"}, 173: {"ders": "Felsefe", "cevaplar": "BAA"},
    174: {"ders": "Felsefe", "cevaplar": "BDD"}, 175: {"ders": "Felsefe", "cevaplar": "AAB"},
    176: {"ders": "Felsefe", "cevaplar": "DA"},
    # MATEMATİK
    213: {"ders": "Matematik", "cevaplar": "AEB"}, 214: {"ders": "Matematik", "cevaplar": "ECA"},
    215: {"ders": "Matematik", "cevaplar": "CDCE"}, 216: {"ders": "Matematik", "cevaplar": "DDCD"},
    217: {"ders": "Matematik", "cevaplar": "AEC"}, 218: {"ders": "Matematik", "cevaplar": "CAA"},
    219: {"ders": "Matematik", "cevaplar": "BEAB"}, 221: {"ders": "Matematik", "cevaplar": "DEAA"},
    222: {"ders": "Matematik", "cevaplar": "BBC"}, 226: {"ders": "Matematik", "cevaplar": "ABAE"},
    227: {"ders": "Matematik", "cevaplar": "CBB"}, 230: {"ders": "Matematik", "cevaplar": "BCCD"},
    231: {"ders": "Matematik", "cevaplar": "DADB"}, 232: {"ders": "Matematik", "cevaplar": "EE"},
    246: {"ders": "Matematik", "cevaplar": "CCB"}, 247: {"ders": "Matematik", "cevaplar": "EACE"},
    249: {"ders": "Matematik", "cevaplar": "DAAC"}, 250: {"ders": "Matematik", "cevaplar": "BE"},
    # FİZİK
    312: {"ders": "Fizik", "cevaplar": "EBC"}, 313: {"ders": "Fizik", "cevaplar": "BA"},
    314: {"ders": "Fizik", "cevaplar": "EDE"}, 316: {"ders": "Fizik", "cevaplar": "DAE"},
    317: {"ders": "Fizik", "cevaplar": "BDEA"}, 318: {"ders": "Fizik", "cevaplar": "DDD"},
    320: {"ders": "Fizik", "cevaplar": "ABE"}, 321: {"ders": "Fizik", "cevaplar": "ADA"},
    # KİMYA
    339: {"ders": "Kimya", "cevaplar": "ACAE"}, 340: {"ders": "Kimya", "cevaplar": "BC"},
    344: {"ders": "Kimya", "cevaplar": "DAAD"}, 345: {"ders": "Kimya", "cevaplar": "ADC"},
    346: {"ders": "Kimya", "cevaplar": "CCD"}, 348: {"ders": "Kimya", "cevaplar": "CAC"},
    349: {"ders": "Kimya", "cevaplar": "AEC"}, 350: {"ders": "Kimya", "cevaplar": "BDEB"},
    351: {"ders": "Kimya", "cevaplar": "AAB"},
    # BİYOLOJİ
    359: {"ders": "Biyoloji", "cevaplar": "CBEE"}, 360: {"ders": "Biyoloji", "cevaplar": "DADC"},
    361: {"ders": "Biyoloji", "cevaplar": "BBD"}, 362: {"ders": "Biyoloji", "cevaplar": "AEDB"},
    363: {"ders": "Biyoloji", "cevaplar": "ECB"}, 365: {"ders": "Biyoloji", "cevaplar": "AEC"},
    373: {"ders": "Biyoloji", "cevaplar": "DE"}, 374: {"ders": "Biyoloji", "cevaplar": "EEE"}
}
PDF_DOSYA_ADI = "tytson8.pdf"

# ==============================================================================
# 2. VERİ HAVUZU: MESLEK LİSESİ SORULARI (YILLIK PLAN - SABİT)
# ==============================================================================
# Not: Buraya yıllık plana uygun daha fazla soru ekleyebilirsiniz.

MESLEK_SORULARI = {
    "9. Sınıf Meslek": [
        {"soru": "İşletmenin sahip olduğu varlıkların kaynaklarını gösteren tabloya ne denir?", "secenekler": ["Bilanço", "Gelir Tablosu", "Mizan", "Yevmiye Defteri"], "cevap": "Bilanço"},
        {"soru": "Aşağıdakilerden hangisi bir 'Varlık' hesabıdır?", "secenekler": ["Kasa", "Satıcılar", "Borç Senetleri", "Sermaye"], "cevap": "Kasa"},
        {"soru": "Excel programında 'Toplama' işlemi için kullanılan fonksiyon hangisidir?", "secenekler": ["=TOPLA()", "=EĞER()", "=MAK()", "=MİN()"], "cevap": "=TOPLA()"},
        {"soru": "Klavye kullanırken 'Enter' tuşunun temel görevi nedir?", "secenekler": ["Onaylamak / Alt satıra geçmek", "Silmek", "Boşluk bırakmak", "Büyük harf yapmak"], "cevap": "Onaylamak / Alt satıra geçmek"},
        {"soru": "Tek düzen hesap planında '100 Kasa Hesabı' hangi grup içinde yer alır?", "secenekler": ["Dönen Varlıklar", "Duran Varlıklar", "Kısa Vadeli Yabancı Kaynaklar", "Öz Kaynaklar"], "cevap": "Dönen Varlıklar"}
    ],
    "10. Sınıf Meslek": [
        {"soru": "Hukukun temel kaynaklarından biri olan 'Anayasa' hiyerarşide nerede bulunur?", "secenekler": ["En üstte", "Kanunların altında", "Yönetmeliklerin altında", "Genelgelerle eşit"], "cevap": "En üstte"},
        {"soru": "Tacir kime denir?", "secenekler": ["Bir ticari işletmeyi kısmen dahi olsa kendi adına işleten kimseye", "Devlet memuruna", "Sadece şirketi olanlara", "Çiftçilere"], "cevap": "Bir ticari işletmeyi kısmen dahi olsa kendi adına işleten kimseye"},
        {"soru": "F klavyede temel sıra harfleri aşağıdakilerden hangisidir?", "secenekler": ["U, İ, E, A, K, T, M, L, Y, Ş", "A, S, D, F, G, H, J, K, L, Ş", "Q, W, E, R, T, Y, U, I, O, P", "Z, X, C, V, B, N, M, Ö, Ç"], "cevap": "U, İ, E, A, K, T, M, L, Y, Ş"},
        {"soru": "Genel muhasebede açılış kaydı hangi deftere yapılır?", "secenekler": ["Yevmiye Defteri", "Büyük Defter", "Envanter Defteri", "Karar Defteri"], "cevap": "Yevmiye Defteri"},
        {"soru": "Satıcıya olan senetsiz borçlar hangi hesapta izlenir?", "secenekler": ["320 Satıcılar", "120 Alıcılar", "100 Kasa", "600 Yurtiçi Satışlar"], "cevap": "320 Satıcılar"}
    ],
    "11. Sınıf Meslek": [
        {"soru": "Şirketler muhasebesine göre, en az sermaye ile kurulabilen sermaye şirketi hangisidir?", "secenekler": ["Limited Şirket", "Anonim Şirket", "Kollektif Şirket", "Komandit Şirket"], "cevap": "Limited Şirket"},
        {"soru": "Maliyet muhasebesinin temel amacı nedir?", "secenekler": ["Üretilen mamulün birim maliyetini saptamak", "Vergi hesaplamak", "Personel maaşı ödemek", "Reklam yapmak"], "cevap": "Üretilen mamulün birim maliyetini saptamak"},
        {"soru": "Anonim şirketlerde genel kurul toplantısı ne zaman yapılır?", "secenekler": ["Her hesap dönemi sonundan itibaren 3 ay içinde", "Her ay", "6 ayda bir", "İki yılda bir"], "cevap": "Her hesap dönemi sonundan itibaren 3 ay içinde"},
        {"soru": "Vergi hukukunda vergiyi doğuran olayın gerçekleşmesi ile ne başlar?", "secenekler": ["Vergi Ödevi", "Vergi Cezası", "Vergi İndirimi", "Vergi Affı"], "cevap": "Vergi Ödevi"},
        {"soru": "Aşağıdakilerden hangisi doğrudan gider çeşididir?", "secenekler": ["Direkt İlk Madde ve Malzeme", "Genel Yönetim Gideri", "Pazarlama Gideri", "Finansman Gideri"], "cevap": "Direkt İlk Madde ve Malzeme"}
    ],
    "12. Sınıf Meslek": [
        {"soru": "Girişimcinin bir iş fikrini hayata geçirmeden önce hazırladığı plana ne denir?", "secenekler": ["İş Planı", "Ders Planı", "Tatil Planı", "Bütçe Planı"], "cevap": "İş Planı"},
        {"soru": "SWOT analizinde 'W' harfi neyi temsil eder?", "secenekler": ["Zayıf Yönler (Weaknesses)", "Güçlü Yönler", "Fırsatlar", "Tehditler"], "cevap": "Zayıf Yönler (Weaknesses)"},
        {"soru": "Finansal okuryazarlıkta 'Gelir - Gider' farkı pozitif ise buna ne denir?", "secenekler": ["Tasarruf / Kar", "Zarar", "Borç", "Kredi"], "cevap": "Tasarruf / Kar"},
        {"soru": "İşletmenin kısa vadeli borç ödeme gücünü gösteren oran hangisidir?", "secenekler": ["Likidite Oranları", "Karlılık Oranları", "Faaliyet Oranları", "Mali Yapı Oranları"], "cevap": "Likidite Oranları"},
        {"soru": "KOSGEB'in temel amacı nedir?", "secenekler": ["KOBİ'leri desteklemek ve geliştirmek", "Büyük şirketlere kredi vermek", "Vergi toplamak", "İthalatı artırmak"], "cevap": "KOBİ'leri desteklemek ve geliştirmek"}
    ]
}

# --- FONKSİYON: PDF GÖSTERİCİ ---
def pdf_sayfa_getir(dosya_yolu, sayfa_numarasi):
    if not os.path.exists(dosya_yolu):
        st.error(f"⚠️ PDF Dosyası ({dosya_yolu}) bulunamadı!")
        return
    try:
        doc = fitz.open(dosya_yolu)
        page = doc.load_page(sayfa_numarasi - 1)
        pix = page.get_pixmap(dpi=150)
        st.image(pix.tobytes(), caption=f"Sayfa {sayfa_numarasi}", use_container_width=True)
    except Exception as e:
        st.error(f"Hata: {e}")

# ==============================================================================
# EKRAN AKIŞI KONTROLÜ
# ==============================================================================
if 'ekran' not in st.session_state: st.session_state.ekran = 'giris'
if 'oturum' not in st.session_state: st.session_state.oturum = False
if 'ad_soyad' not in st.session_state: st.session_state.ad_soyad = ""
if 'mod' not in st.session_state: st.session_state.mod = ""
if 'secilen_liste' not in st.session_state: st.session_state.secilen_liste = []
if 'aktif_index' not in st.session_state: st.session_state.aktif_index = 0
if 'toplam_puan' not in st.session_state: st.session_state.toplam_puan = 0

# ------------------------------------------------------------------------------
# 1. GİRİŞ EKRANI (AD SOYAD ZORUNLU)
# ------------------------------------------------------------------------------
if st.session_state.ekran == 'giris':
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        <div class='giris-kart'>
            <h1>🎓 Bağarası ÇPAL</h1>
            <h2>Dijital Sınav Merkezi</h2>
            <hr>
            <p>Lütfen sınava başlamak için kimlik bilgilerinizi giriniz.</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Ad Soyad Girişi
        ad_soyad_input = st.text_input("Adınız Soyadınız:", placeholder="Örn: Ali Yılmaz")
        
        if st.button("SİSTEME GİRİŞ YAP 🚀"):
            if ad_soyad_input.strip():
                st.session_state.ad_soyad = ad_soyad_input
                st.session_state.ekran = 'sinav'
                st.rerun()
            else:
                st.error("Lütfen adınızı ve soyadınızı giriniz!")
        
        # İMZA ALANI (En Altta)
        st.markdown("""
        <div class='imza'>
            Okulumuz muhasebe alanının okulumuza hediyesidir.<br>
            <b>Zülfikar Sıtacı</b>
        </div>
        """, unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# 2. SINAV ARAYÜZÜ
# ------------------------------------------------------------------------------
elif st.session_state.ekran == 'sinav':
    
    # --- Sidebar (Sol Menü) ---
    with st.sidebar:
        st.image("https://cdn-icons-png.flaticon.com/512/2997/2997321.png", width=100)
        st.write(f"👤 **Öğrenci:** {st.session_state.ad_soyad}")
        st.divider()
        
        if st.button("🏠 Çıkış Yap"):
            st.session_state.ekran = 'giris'
            st.session_state.oturum = False
            st.rerun()
        
        st.divider()
        
        if not st.session_state.oturum:
            st.header("Sınav Ayarları")
            mod_secimi = st.radio("Sınav Türü:", ["TYT Kampı (PDF)", "Meslek Lisesi Sınavları"])
            
            if mod_secimi == "TYT Kampı (PDF)":
                mevcut = sorted(list(set(v["ders"] for v in PDF_HARITASI.values())))
                ders = st.selectbox("Ders:", ["Karışık Deneme"] + mevcut)
                adet = st.slider("Sayfa Sayısı:", 1, 10, 3)
                
                if st.button("TYT Başlat"):
                    uygun = [s for s, d in PDF_HARITASI.items() if ders == "Karışık Deneme" or d["ders"] == ders]
                    if uygun:
                        random.shuffle(uygun)
                        st.session_state.secilen_liste = uygun[:adet]
                        st.session_state.mod = "PDF"
                        st.session_state.oturum = True
                        st.session_state.aktif_index = 0
                        st.session_state.toplam_puan = 0
                        st.rerun()
                    else:
                        st.error("Bu ders için soru bulunamadı.")
            
            else: # Meslek Lisesi Modu
                # Sabit sorulardan seç
                ders = st.selectbox("Sınıf Seviyesi / Alan:", list(MESLEK_SORULARI.keys()))
                if st.button("Meslek Sınavını Başlat"):
                    sorular = MESLEK_SORULARI.get(ders, [])
                    if sorular:
                        # SORULARI KARIŞTIR (SHUFFLE)
                        random.shuffle(sorular)
                        st.session_state.secilen_liste = sorular
                        st.session_state.mod = "MESLEK"
                        st.session_state.oturum = True
                        st.session_state.aktif_index = 0
                        st.session_state.toplam_puan = 0
                        st.rerun()
                    else:
                        st.error("Bu alan için henüz soru girişi yapılmamış.")

    # --- Ana İçerik ---
    if st.session_state.oturum:
        
        # Bitiş Kontrolü
        if st.session_state.aktif_index >= len(st.session_state.secilen_liste):
            st.balloons()
            st.success(f"🎉 Tebrikler {st.session_state.ad_soyad}!")
            st.info(f"Sınav Tamamlandı. Toplam Puanınız: {st.session_state.toplam_puan}")
            if st.button("Yeni Sınav Başlat"):
                st.session_state.oturum = False
                st.rerun()
        
        else:
            # 1. MOD: PDF (TYT)
            if st.session_state.mod == "PDF":
                sayfa_no = st.session_state.secilen_liste[st.session_state.aktif_index]
                veri = PDF_HARITASI[sayfa_no]
                
                st.subheader(f"📄 {veri['ders']} - Sayfa {sayfa_no}")
                
                tab1, tab2 = st.tabs(["📄 KİTAPÇIK", "📝 CEVAP KAĞIDI"])
                
                with tab1:
                    pdf_sayfa_getir(PDF_DOSYA_ADI, sayfa_no)
                    
                with tab2:
                    st.info("Cevaplarınızı işaretleyiniz.")
                    dogru_sayisi = 0
                    cevaplar = veri["cevaplar"]
                    with st.form(f"form_{sayfa_no}"):
                        for i in range(len(cevaplar)):
                            st.write(f"**Soru {i+1}**")
                            st.radio(f"S_{i}", ["A","B","C","D","E"], key=f"c_{sayfa_no}_{i}", horizontal=True, index=None)
                            st.divider()
                        
                        if st.form_submit_button("KONTROL ET VE İLERLE ➡️"):
                            for i in range(len(cevaplar)):
                                val = st.session_state.get(f"c_{sayfa_no}_{i}")
                                if val == cevaplar[i]:
                                    dogru_sayisi += 1
                                    st.toast(f"Soru {i+1}: Doğru! ✅")
                                else:
                                    st.toast(f"Soru {i+1}: Yanlış! ❌")
                            
                            st.session_state.toplam_puan += (dogru_sayisi * 5)
                            time.sleep(1.5)
                            st.session_state.aktif_index += 1
                            st.rerun()

            # 2. MOD: MESLEK LİSESİ (Sabit Sorular)
            else:
                soru = st.session_state.secilen_liste[st.session_state.aktif_index]
                st.subheader(f"❓ Soru {st.session_state.aktif_index + 1}")
                
                # Soru Kartı
                st.markdown(f"""
                <div style="background-color:white; padding:20px; border-radius:10px; border-left:5px solid #FF7043; font-size:18px;">
                    {soru['soru']}
                </div>
                """, unsafe_allow_html=True)
                st.write("")
                
                # Seçenekleri Karıştırarak Göster
                secenekler = soru["secenekler"].copy()
                # random.shuffle(secenekler) # İsteğe bağlı seçenekleri de karıştırır
                
                cols = st.columns(2)
                for idx, sec in enumerate(secenekler):
                    with cols[idx % 2]:
                        if st.button(sec, key=f"btn_{st.session_state.aktif_index}_{idx}", use_container_width=True):
                            if sec == soru["cevap"]:
                                st.balloons()
                                st.success("DOĞRU! ✅")
                                st.session_state.toplam_puan += 20
                            else:
                                st.error(f"YANLIŞ! ❌ (Doğru Cevap: {soru['cevap']})")
                            
                            time.sleep(2)
                            st.session_state.aktif_index += 1
                            st.rerun()

    else:
        st.info("👈 Sol menüden seçim yapınız.")
