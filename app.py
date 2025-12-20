import streamlit as st
import random
import os
import time
import json
import fitz  # PyMuPDF

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Bağarası Hibrit Eğitim Merkezi", page_icon="🎓", layout="wide")

# --- TASARIM VE GİZLİLİK ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Dancing+Script:wght@700&display=swap');
    
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
    
    /* Zülfikar SITACI İmzası (El Yazısı Fontu) */
    .imza {
        margin-top: 40px;
        font-family: 'Dancing Script', cursive; /* El yazısı fontu */
        color: #D84315;
        font-size: 28px; /* Yazı boyutu büyütüldü */
        text-align: right;
        padding-right: 20px;
        transform: rotate(-2deg); /* Hafif eğiklik */
    }
    .imza-not {
        font-family: 'Courier New', monospace;
        font-size: 12px;
        color: #555;
        text-align: right;
        margin-top: -10px;
        padding-right: 20px;
    }
    
    /* Kullanım Kılavuzu */
    .kilavuz {
        background-color: #FFF3E0;
        border-left: 5px solid #FF9800;
        padding: 15px;
        margin-top: 20px;
        text-align: left;
        font-size: 14px;
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
# FONKSİYONLAR
# ==============================================================================
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

# DOSYADAN SORU ÇEKME FONKSİYONU
def dosya_sorularini_yukle():
    if not os.path.exists("sorular.json"):
        st.warning("⚠️ 'sorular.json' dosyası bulunamadı! Lütfen GitHub'a yükleyiniz.")
        return {}
    try:
        with open("sorular.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        st.error(f"Soru dosyası okuma hatası: {e}")
        return {}

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
        
        # Kullanım Kılavuzu (Yeni Eklenen)
        with st.expander("ℹ️ KULLANIM KILAVUZU (Okumak İçin Tıkla)"):
            st.markdown("""
            **1. TYT Kampı:** Gerçek çıkmış sorularla PDF üzerinden deneme sınavı olursunuz.
            **2. Meslek Sınavları:** Kendi alanınızla ilgili (Muhasebe vb.) çoktan seçmeli test çözersiniz.
            **3. Puanlama:** Her soru anında kontrol edilir, sınav sonunda toplam puanınız görünür.
            **4. Önemli:** Sınav bitmeden sayfayı yenilemeyiniz.
            """)

        if st.button("SİSTEME GİRİŞ YAP 🚀"):
            if ad_soyad_input.strip():
                st.session_state.ad_soyad = ad_soyad_input
                st.session_state.ekran = 'sinav'
                st.rerun()
            else:
                st.error("Lütfen adınızı ve soyadınızı giriniz!")
        
        # İMZA ALANI (El Yazısı)
        st.markdown("""
        <div class='imza-not'>Okulumuz muhasebe alanının okulumuza hediyesidir.</div>
        <div class='imza'>Zülfikar SITACI
        Mustafa BAĞCIK </div>
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
            
            else: # Meslek Lisesi Modu (JSON'dan Okuma)
                soru_havuzu = dosya_sorularini_yukle()
                if soru_havuzu:
                    # Sınıf Seviyelerini Listele
                    ders = st.selectbox("Sınıf Seviyesi / Alan:", list(soru_havuzu.keys()))
                    if st.button("Meslek Sınavını Başlat"):
                        sorular = soru_havuzu.get(ders, [])
                        if sorular:
                            random.shuffle(sorular) # Soruları Karıştır
                            st.session_state.secilen_liste = sorular
                            st.session_state.mod = "MESLEK"
                            st.session_state.oturum = True
                            st.session_state.aktif_index = 0
                            st.session_state.toplam_puan = 0
                            st.rerun()
                        else:
                            st.error("Bu kategori boş görünüyor.")
                else:
                    st.error("Lütfen 'sorular.json' dosyasını yükleyiniz.")

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

            # 2. MOD: MESLEK LİSESİ (JSON Dosyasından)
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
                random.shuffle(secenekler) # Şıkları Karıştır
                
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
