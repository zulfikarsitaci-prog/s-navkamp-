import streamlit as st
import random
import os
import time
import json
import fitz  # PyMuPDF

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Bağarası Hibrit Eğitim Merkezi", page_icon="🎓", layout="wide")

# --- DOSYA İSİMLERİ ---
TYT_PDF_ADI = "tytson8.pdf"
TYT_JSON_ADI = "tyt_data.json"
MESLEK_JSON_ADI = "sorular.json"

# --- TASARIM ---
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
    
    /* Meslek Sorusu Kartı */
    .soru-karti {
        background-color: white; 
        padding: 20px; 
        border-radius: 10px; 
        border-left: 5px solid #FF7043; 
        font-size: 18px;
        margin-bottom: 20px;
    }
    </style>
""", unsafe_allow_html=True)

# ==============================================================================
# FONKSİYONLAR
# ==============================================================================

# 1. PDF Sayfası Getir (TYT İçin)
def pdf_sayfa_getir(dosya_yolu, sayfa_numarasi):
    if not os.path.exists(dosya_yolu):
        st.error(f"⚠️ PDF Dosyası ({dosya_yolu}) bulunamadı!")
        return
    try:
        doc = fitz.open(dosya_yolu)
        if sayfa_numarasi > len(doc):
             st.error("Bu sayfa numarası PDF sınırları dışında.")
             return
        page = doc.load_page(sayfa_numarasi - 1)
        pix = page.get_pixmap(dpi=150)
        st.image(pix.tobytes(), caption=f"Sayfa {sayfa_numarasi}", use_container_width=True)
    except Exception as e:
        st.error(f"PDF Hatası: {e}")

# 2. TYT Verilerini Yükle (tyt_data.json)
def tyt_veri_yukle():
    if not os.path.exists(TYT_JSON_ADI):
        return {}
    try:
        with open(TYT_JSON_ADI, "r", encoding="utf-8") as f:
            ham_veri = json.load(f)
            return {int(k): v for k, v in ham_veri.items()}
    except:
        return {}

# 3. Meslek Sorularını Yükle (sorular.json)
def meslek_veri_yukle():
    if not os.path.exists(MESLEK_JSON_ADI):
        return {}
    try:
        with open(MESLEK_JSON_ADI, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}

# ==============================================================================
# EKRAN AKIŞI
# ==============================================================================
if 'ekran' not in st.session_state: st.session_state.ekran = 'giris'
if 'oturum' not in st.session_state: st.session_state.oturum = False
if 'ad_soyad' not in st.session_state: st.session_state.ad_soyad = ""
if 'mod' not in st.session_state: st.session_state.mod = "" # "PDF" veya "MESLEK"
if 'secilen_liste' not in st.session_state: st.session_state.secilen_liste = []
if 'aktif_index' not in st.session_state: st.session_state.aktif_index = 0
if 'toplam_puan' not in st.session_state: st.session_state.toplam_puan = 0

# Verileri Hafızaya Al
TYT_VERI = tyt_veri_yukle()
MESLEK_VERI = meslek_veri_yukle()

# --- 1. GİRİŞ EKRANI ---
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
        
        ad_soyad_input = st.text_input("Adınız Soyadınız:", placeholder="Örn: Ali Yılmaz")
        
        # Uyarılar (Dosya eksikse hoca görsün)
        if not TYT_VERI and not MESLEK_VERI:
            st.error("⚠️ Sistemde soru dosyaları (JSON) bulunamadı.")

        if st.button("SİSTEME GİRİŞ YAP 🚀"):
            if ad_soyad_input.strip():
                st.session_state.ad_soyad = ad_soyad_input
                st.session_state.ekran = 'sinav'
                st.rerun()
            else:
                st.error("Lütfen adınızı giriniz!")
        
        st.markdown("""
        <div class='imza-not'>Okulumuz Muh. ve Finansman alanının öğrencilerimize hediyesidir.</div>
        <div class='imza'></div>
        """, unsafe_allow_html=True)

# --- 2. SINAV EKRANI ---
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
        
        # SINAV SEÇİM MENÜSÜ
        if not st.session_state.oturum:
            st.header("Sınav Türü Seçin")
            tur_secimi = st.radio("Hangisi çözülecek?", ["TYT Deneme (PDF)", "Meslek Lisesi (Test)"])
            
            # A) TYT SEÇİMİ
            if tur_secimi == "TYT Deneme (PDF)":
                if TYT_VERI:
                    mevcut_dersler = sorted(list(set(v["ders"] for v in TYT_VERI.values())))
                    ders = st.selectbox("Ders:", ["Karışık Deneme"] + mevcut_dersler)
                    adet = st.slider("Sayfa Sayısı:", 1, 10, 3)
                    
                    if st.button("TYT Başlat"):
                        uygun = [s for s, d in TYT_VERI.items() if ders == "Karışık Deneme" or d["ders"] == ders]
                        if uygun:
                            random.shuffle(uygun)
                            st.session_state.secilen_liste = uygun[:adet]
                            st.session_state.mod = "PDF"
                            st.session_state.oturum = True
                            st.session_state.aktif_index = 0
                            st.session_state.toplam_puan = 0
                            st.rerun()
                        else:
                            st.error("Ders bulunamadı.")
                else:
                    st.warning("TYT verisi (tyt_data.json) yüklenmemiş.")

            # B) MESLEK SEÇİMİ
            else:
                if MESLEK_VERI:
                    alan = st.selectbox("Alan/Sınıf:", list(MESLEK_VERI.keys()))
                    if st.button("Meslek Sınavı Başlat"):
                        sorular = MESLEK_VERI.get(alan, [])
                        if sorular:
                            random.shuffle(sorular)
                            st.session_state.secilen_liste = sorular
                            st.session_state.mod = "MESLEK"
                            st.session_state.oturum = True
                            st.session_state.aktif_index = 0
                            st.session_state.toplam_puan = 0
                            st.rerun()
                        else:
                            st.error("Bu alanda soru yok.")
                else:
                    st.warning("Meslek verisi (sorular.json) yüklenmemiş.")

    # --- SORU ÇÖZME ALANI ---
    if st.session_state.oturum:
        
        # SINAV BİTTİ Mİ?
        if st.session_state.aktif_index >= len(st.session_state.secilen_liste):
            st.balloons()
            st.success(f"🎉 Sınav Tamamlandı! Puanınız: {st.session_state.toplam_puan}")
            if st.button("Yeni Sınav Başlat"):
                st.session_state.oturum = False
                st.rerun()
        
        else:
            # --- MOD 1: TYT (PDF) ---
            if st.session_state.mod == "PDF":
                sayfa_no = st.session_state.secilen_liste[st.session_state.aktif_index]
                veri = TYT_VERI[sayfa_no]
                
                st.subheader(f"📄 {veri['ders']} - Sayfa {sayfa_no}")
                
                tab1, tab2 = st.tabs(["📄 KİTAPÇIK", "📝 CEVAP FORMU"])
                with tab1:
                    pdf_sayfa_getir(TYT_PDF_ADI, sayfa_no)
                with tab2:
                    cevaplar = veri["cevaplar"] # "ABCDX" gibi string
                    dogru_sayisi = 0
                    
                    with st.form(f"form_{sayfa_no}"):
                        st.info(f"Bu sayfada {len(cevaplar)} soru var.")
                        for i in range(len(cevaplar)):
                            st.write(f"**Soru {i+1}**")
                            st.radio(f"S{i}", ["A","B","C","D","E"], key=f"c_{sayfa_no}_{i}", horizontal=True, index=None, label_visibility="collapsed")
                            st.divider()
                        
                        if st.form_submit_button("KONTROL ET VE GEÇ ➡️"):
                            for i in range(len(cevaplar)):
                                val = st.session_state.get(f"c_{sayfa_no}_{i}")
                                dogru_cevap = cevaplar[i]
                                
                                # Eğer cevap anahtarında X varsa (boşsa) kontrol etme
                                if dogru_cevap == "X":
                                    st.warning(f"Soru {i+1}: Cevap anahtarı girilmemiş.")
                                elif val == dogru_cevap:
                                    dogru_sayisi += 1
                                    st.toast(f"Soru {i+1}: Doğru! ✅")
                                else:
                                    st.toast(f"Soru {i+1}: Yanlış! ❌")
                            
                            st.session_state.toplam_puan += (dogru_sayisi * 5)
                            time.sleep(1.5)
                            st.session_state.aktif_index += 1
                            st.rerun()

            # --- MOD 2: MESLEK (JSON TEXT) ---
            elif st.session_state.mod == "MESLEK":
                soru = st.session_state.secilen_liste[st.session_state.aktif_index]
                
                st.subheader(f"❓ Soru {st.session_state.aktif_index + 1}")
                st.markdown(f"<div class='soru-karti'>{soru['soru']}</div>", unsafe_allow_html=True)
                
                secenekler = soru["secenekler"].copy()
                random.shuffle(secenekler)
                
                c1, c2 = st.columns(2)
                for idx, sec in enumerate(secenekler):
                    with (c1 if idx % 2 == 0 else c2):
                        if st.button(sec, key=f"btn_{st.session_state.aktif_index}_{idx}", use_container_width=True):
                            if sec == soru["cevap"]:
                                st.balloons()
                                st.success("DOĞRU! ✅")
                                st.session_state.toplam_puan += 10 # Meslek sorusu puanı
                            else:
                                st.error(f"YANLIŞ! ❌ (Doğru Cevap: {soru['cevap']})")
                            
                            time.sleep(2)
                            st.session_state.aktif_index += 1
                            st.rerun()
