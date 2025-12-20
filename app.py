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
    
    .stDeployButton {display:none;}
    footer {visibility: hidden;}
    #MainMenu {visibility: hidden;}
    
    .giris-kart {
        background-color: white;
        padding: 30px;
        border-radius: 20px;
        border: 3px solid #FF7043;
        text-align: center;
        box-shadow: 0 8px 16px rgba(0,0,0,0.1);
        margin-bottom: 20px;
    }
    
    .imza {
        margin-top: 40px;
        font-family: 'Dancing Script', cursive;
        color: #D84315;
        font-size: 28px;
        text-align: right;
        padding-right: 20px;
        transform: rotate(-2deg);
    }
    .imza-not {
        font-family: 'Courier New', monospace;
        font-size: 12px;
        color: #555;
        text-align: right;
        margin-top: -10px;
        padding-right: 20px;
    }
    
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

# --- DOSYA AYARLARI ---
PDF_DOSYA_ADI = "tytson8.pdf"  # Yüklediğiniz dosyanın tam adı
JSON_DOSYA_ADI = "tyt_data.json"

# ==============================================================================
# FONKSİYONLAR
# ==============================================================================
def pdf_sayfa_getir(dosya_yolu, sayfa_numarasi):
    if not os.path.exists(dosya_yolu):
        st.error(f"⚠️ PDF Dosyası ({dosya_yolu}) bulunamadı!")
        return
    try:
        doc = fitz.open(dosya_yolu)
        # PDF sayfa sayısı kontrolü
        if sayfa_numarasi > len(doc):
             st.error("Bu sayfa numarası PDF'te yok.")
             return

        page = doc.load_page(sayfa_numarasi - 1)
        pix = page.get_pixmap(dpi=150)
        st.image(pix.tobytes(), caption=f"Sayfa {sayfa_numarasi}", use_container_width=True)
    except Exception as e:
        st.error(f"Hata: {e}")

# JSON YÜKLEME FONKSİYONU
def veri_yukle():
    if not os.path.exists(JSON_DOSYA_ADI):
        # Dosya yoksa hata vermesin diye boş şablon döner
        return {}
    try:
        with open(JSON_DOSYA_ADI, "r", encoding="utf-8") as f:
            ham_veri = json.load(f)
            # JSON'daki string anahtarları sayıya çeviriyoruz ("13" -> 13)
            return {int(k): v for k, v in ham_veri.items()}
    except Exception as e:
        st.error(f"JSON okuma hatası: {e}")
        return {}

# ==============================================================================
# EKRAN AKIŞI
# ==============================================================================
if 'ekran' not in st.session_state: st.session_state.ekran = 'giris'
if 'oturum' not in st.session_state: st.session_state.oturum = False
if 'ad_soyad' not in st.session_state: st.session_state.ad_soyad = ""
if 'secilen_liste' not in st.session_state: st.session_state.secilen_liste = []
if 'aktif_index' not in st.session_state: st.session_state.aktif_index = 0
if 'toplam_puan' not in st.session_state: st.session_state.toplam_puan = 0

# Verileri Yükle
PDF_HARITASI = veri_yukle()

# 1. GİRİŞ EKRANI
if st.session_state.ekran == 'giris':
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        <div class='giris-kart'>
            <h1>🎓 Bağarası ÇPAL</h1>
            <h2>TYT Sınav Merkezi</h2>
            <hr>
            <p>Lütfen sınava başlamak için kimlik bilgilerinizi giriniz.</p>
        </div>
        """, unsafe_allow_html=True)
        
        ad_soyad_input = st.text_input("Adınız Soyadınız:", placeholder="Örn: Ali Yılmaz")
        
        if PDF_HARITASI == {}:
            st.warning("⚠️ Sistemde henüz soru/cevap anahtarı yüklü değil (tyt_data.json boş).")

        if st.button("SİSTEME GİRİŞ YAP 🚀"):
            if ad_soyad_input.strip():
                st.session_state.ad_soyad = ad_soyad_input
                st.session_state.ekran = 'sinav'
                st.rerun()
            else:
                st.error("Lütfen adınızı giriniz!")
        
        st.markdown("""
        <div class='imza-not'>Okulumuz muhasebe alanının okulumuza hediyesidir.</div>
        <div class='imza'>Zülfikar Sıtacı</div>
        """, unsafe_allow_html=True)

# 2. SINAV EKRANI
elif st.session_state.ekran == 'sinav':
    
    with st.sidebar:
        st.image("https://cdn-icons-png.flaticon.com/512/2997/2997321.png", width=100)
        st.write(f"👤 **{st.session_state.ad_soyad}**")
        st.divider()
        
        if st.button("🏠 Çıkış Yap"):
            st.session_state.ekran = 'giris'
            st.session_state.oturum = False
            st.rerun()
        
        st.divider()
        
        if not st.session_state.oturum:
            st.header("Sınav Oluştur")
            
            # JSON dosyasından dersleri bul
            if PDF_HARITASI:
                mevcut_dersler = sorted(list(set(v["ders"] for v in PDF_HARITASI.values())))
                ders = st.selectbox("Ders Seçiniz:", ["Karışık Deneme"] + mevcut_dersler)
                adet = st.slider("Kaç Sayfa Çözülecek?", 1, 10, 3)
                
                if st.button("Sınavı Başlat"):
                    # Uygun sayfaları seç
                    uygun_sayfalar = [s for s, d in PDF_HARITASI.items() if ders == "Karışık Deneme" or d["ders"] == ders]
                    
                    if uygun_sayfalar:
                        random.shuffle(uygun_sayfalar)
                        st.session_state.secilen_liste = uygun_sayfalar[:adet]
                        st.session_state.oturum = True
                        st.session_state.aktif_index = 0
                        st.session_state.toplam_puan = 0
                        st.rerun()
                    else:
                        st.error("Seçilen derse ait sayfa bulunamadı.")
            else:
                st.error("Lütfen 'tyt_data.json' dosyasını yükleyiniz.")

    # İçerik Alanı
    if st.session_state.oturum:
        if st.session_state.aktif_index >= len(st.session_state.secilen_liste):
            st.balloons()
            st.success(f"🎉 Sınav Bitti! Puanınız: {st.session_state.toplam_puan}")
            if st.button("Yeni Sınav"):
                st.session_state.oturum = False
                st.rerun()
        else:
            sayfa_no = st.session_state.secilen_liste[st.session_state.aktif_index]
            veri = PDF_HARITASI[sayfa_no]
            
            st.subheader(f"📄 {veri['ders']} - Sayfa {sayfa_no}")
            
            tab1, tab2 = st.tabs(["📄 KİTAPÇIK", "📝 CEVAP FORMU"])
            
            with tab1:
                pdf_sayfa_getir(PDF_DOSYA_ADI, sayfa_no)
            
            with tab2:
                cevaplar = veri["cevaplar"]
                dogru_sayisi = 0
                st.info(f"Bu sayfada {len(cevaplar)} soru var. Lütfen işaretleyiniz.")
                
                with st.form(f"form_{sayfa_no}"):
                    for i in range(len(cevaplar)):
                        st.write(f"**Soru {i+1}**")
                        st.radio(f"Soru {i+1}", ["A","B","C","D","E"], key=f"c_{sayfa_no}_{i}", horizontal=True, index=None, label_visibility="collapsed")
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
    elif PDF_HARITASI:
        st.info("👈 Sol menüden ders seçip sınavı başlatın.")
