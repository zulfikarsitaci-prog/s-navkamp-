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

# --- TASARIM VE CSS ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Dancing+Script:wght@700&display=swap');
    
    .stApp { background-color: #F0F4C3 !important; }
    h1, h2, h3, h4, .stMarkdown, p, label { color: #212121 !important; }
    
    /* DROPDOWN (Açılır Liste) DÜZELTMESİ - Beyaz Arka Plan */
    .stSelectbox div[data-baseweb="select"] > div {
        background-color: #FFFFFF !important;
        color: #000000 !important;
        border: 2px solid #FF7043;
    }
    
    /* GİZLİLİK */
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

    /* SEÇİM KARTLARI (ORTA EKRAN) */
    .secim-karti {
        background-color: white;
        padding: 20px;
        border-radius: 15px;
        border: 2px solid #FF7043;
        text-align: center;
        transition: transform 0.2s;
    }
    .secim-karti:hover {
        transform: scale(1.02);
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
    }
    
    /* İMZA ALANI */
    .imza-container {
        margin-top: 50px;
        text-align: right;
        padding-right: 20px;
        opacity: 0.8; 
    }
    .imza-baslik {
        font-family: 'Courier New', monospace;
        font-size: 14px;
        color: #555;
        font-weight: bold;
        margin-bottom: 5px;
    }
    .imza {
        font-family: 'Dancing Script', cursive;
        color: #D84315;
        font-size: 22px; 
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
    
    /* SORU KARTI */
    .soru-karti {
        background-color: white; 
        padding: 20px; 
        border-radius: 10px; 
        border-left: 5px solid #FF7043; 
        font-size: 18px;
        margin-bottom: 20px;
        color: #000 !important;
    }
    
    /* HATA VE İSTATİSTİK KARTLARI */
    .hata-karti {
        background-color: #FFEBEE;
        border-left: 5px solid #D32F2F;
        padding: 15px;
        margin-bottom: 15px;
        border-radius: 5px;
        color: #000;
    }
    .stat-card {
        background-color: white;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        text-align: center;
        border: 2px solid #FF7043;
    }
    .stat-number { font-size: 32px; font-weight: bold; color: #D84315; }
    .stat-label { font-size: 16px; color: #555; }
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

def tyt_veri_yukle():
    if not os.path.exists(TYT_JSON_ADI): return {}
    try:
        with open(TYT_JSON_ADI, "r", encoding="utf-8") as f:
            ham_veri = json.load(f)
            return {int(k): v for k, v in ham_veri.items()}
    except: return {}

def meslek_veri_yukle():
    if not os.path.exists(MESLEK_JSON_ADI): return {}
    try:
        with open(MESLEK_JSON_ADI, "r", encoding="utf-8") as f:
            return json.load(f)
    except: return {}

# ==============================================================================
# EKRAN AKIŞI
# ==============================================================================
if 'ekran' not in st.session_state: st.session_state.ekran = 'giris'
if 'oturum' not in st.session_state: st.session_state.oturum = False
if 'ad_soyad' not in st.session_state: st.session_state.ad_soyad = ""
if 'mod' not in st.session_state: st.session_state.mod = "" 
if 'secilen_liste' not in st.session_state: st.session_state.secilen_liste = []
if 'aktif_index' not in st.session_state: st.session_state.aktif_index = 0
if 'secim_turu' not in st.session_state: st.session_state.secim_turu = None 

# KARNE DEĞİŞKENLERİ
if 'karne' not in st.session_state: st.session_state.karne = []
if 'dogru_sayisi' not in st.session_state: st.session_state.dogru_sayisi = 0
if 'yanlis_sayisi' not in st.session_state: st.session_state.yanlis_sayisi = 0
if 'bos_sayisi' not in st.session_state: st.session_state.bos_sayisi = 0

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
            <p style="font-size:18px; font-weight:bold; color:#D84315;">
                Okulumuz Muhasebe ve Finansman Alanının öğrencilerimize hediyesidir.
            </p>
            <br>
            <p>Lütfen sınava başlamak için kimlik bilgilerinizi giriniz.</p>
        </div>
        """, unsafe_allow_html=True)
        
        ad_soyad_input = st.text_input("Adınız Soyadınız:", placeholder="Örn: Ali Yılmaz")
        
        st.write("")
        if st.button("Sınav Türünü Seçmek İçin Giriş Yapınız ➡️"):
            if ad_soyad_input.strip():
                st.session_state.ad_soyad = ad_soyad_input
                st.session_state.ekran = 'sinav'
                # Sıfırla
                st.session_state.karne = []
                st.session_state.dogru_sayisi = 0
                st.session_state.yanlis_sayisi = 0
                st.session_state.bos_sayisi = 0
                st.session_state.secim_turu = None 
                st.rerun()
            else:
                st.error("Lütfen adınızı giriniz!")
        
        # GÜNCELLENEN İMZA ALANI
        st.markdown("""
        <div class='imza-container'>
            <div class='imza-baslik'>Muhasebe ve Finansman Öğretmenleri</div>
            <div class='imza'>Zülfikar Sıtacı & Mustafa Bağcık</div>
        </div>
        """, unsafe_allow_html=True)

# --- 2. SINAV EKRANI ---
elif st.session_state.ekran == 'sinav':
    
    # --- SOL MENÜ ---
    with st.sidebar:
        st.image("https://cdn-icons-png.flaticon.com/512/2997/2997321.png", width=100)
        st.write(f"👤 **{st.session_state.ad_soyad}**")
        st.divider()
        if st.button("🏠 Çıkış Yap"):
            st.session_state.ekran = 'giris'
            st.session_state.oturum = False
            st.rerun()

    # --- ANA EKRAN (SEÇİM ALANI) ---
    if not st.session_state.oturum:
        
        st.markdown("<h2 style='text-align:center;'>Lütfen Sınav Türünü Seçiniz 👇</h2>", unsafe_allow_html=True)
        st.write("")
        
        col_a, col_b = st.columns(2)
        
        with col_a:
            st.markdown("""
            <div class='secim-karti'>
                <h3>📘 TYT Kampı</h3>
                <p>Gerçek çıkmış sorulardan oluşan PDF denemeleri.</p>
            </div>
            """, unsafe_allow_html=True)
            if st.button("TYT Çöz ➡️", key="btn_tyt"):
                st.session_state.secim_turu = "TYT"
        
        with col_b:
            st.markdown("""
            <div class='secim-karti'>
                <h3>💼 Meslek Lisesi</h3>
                <p>10, 11 ve 12. Sınıf Alan Testleri</p>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Meslek Çöz ➡️", key="btn_meslek"):
                st.session_state.secim_turu = "MESLEK"
        
        st.divider()
        
        # --- SEÇİME GÖRE AÇILAN AYARLAR ---
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
                    else: st.error("Bu derste soru bulunamadı.")
            else:
                st.warning("TYT verileri yüklenmemiş.")
                
        elif st.session_state.secim_turu == "MESLEK":
            st.subheader("💼 Meslek Alanı Ayarları")
            if MESLEK_VERI:
                # 1. Aşama: SINIF SEÇİMİ
                secilen_sinif = st.selectbox("Sınıf / Alan Seçiniz:", list(MESLEK_VERI.keys()))
                
                # 2. Aşama: TEST SEÇİMİ (O sınıfa ait testleri getir)
                secilen_sinif_testleri = MESLEK_VERI.get(secilen_sinif, {})
                if secilen_sinif_testleri:
                    secilen_test_adi = st.selectbox("Çözülecek Testi Seçiniz:", list(secilen_sinif_testleri.keys()))
                    
                    if st.button("SINAVI BAŞLAT 🚀"):
                        sorular = secilen_sinif_testleri.get(secilen_test_adi, [])
                        if sorular:
                            st.session_state.secilen_liste = sorular
                            st.session_state.mod = "MESLEK"
                            st.session_state.oturum = True
                            st.session_state.karne = [] 
                            st.session_state.aktif_index = 0
                            st.rerun()
                        else: st.error("Bu testte soru yok.")
                else:
                    st.error("Bu sınıfa ait test bulunamadı.")
            else:
                st.warning("Meslek verileri yüklenmemiş.")

    # --- SORU ÇÖZME EKRANI ---
    else:
        
        # KARNE EKRANI (SINAV BİTİNCE)
        if st.session_state.aktif_index >= len(st.session_state.secilen_liste):
            st.balloons()
            st.markdown(f"<h2 style='text-align:center;'>🏁 Sınav Sonucu: {st.session_state.ad_soyad}</h2>", unsafe_allow_html=True)
            
            c1, c2, c3 = st.columns(3)
            c1.markdown(f"<div class='stat-card'><div class='stat-number'>{st.session_state.dogru_sayisi}</div><div class='stat-label'>Doğru</div></div>", unsafe_allow_html=True)
            c2.markdown(f"<div class='stat-card'><div class='stat-number'>{st.session_state.yanlis_sayisi}</div><div class='stat-label'>Yanlış</div></div>", unsafe_allow_html=True)
            c3.markdown(f"<div class='stat-card'><div class='stat-number'>{st.session_state.bos_sayisi}</div><div class='stat-label'>Boş</div></div>", unsafe_allow_html=True)
            
            st.divider()
            
            st.subheader("🔍 Hatalı Yaptığınız Soruların Analizi")
            yanlislar = [k for k in st.session_state.karne if k["durum"] == "Yanlış"]
            
            if not yanlislar:
                st.success("Tebrikler! Hiç yanlışınız yok. Harika iş çıkardınız. 🌟")
            else:
                for hata in yanlislar:
                    if hata["tip"] == "MESLEK":
                        st.markdown(f"<div class='hata-karti'><b>SORU:</b> {hata['soru_metni']}<br><br>❌ <b>Sizin Cevabınız:</b> {hata['secilen']}<br>✅ <b>Doğru Cevap:</b> {hata['dogru']}</div>", unsafe_allow_html=True)
                    elif hata["tip"] == "PDF":
                        with st.expander(f"📄 Sayfa {hata['sayfa_no']} - {hata['ders']} (Hataları Gör)"):
                            c_pdf, c_detay = st.columns([1, 1])
                            with c_pdf: pdf_sayfa_getir(TYT_PDF_ADI, hata['sayfa_no'])
                            with c_detay:
                                for yanlis_detay in hata['hatali_sorular']:
                                    st.markdown(f"<div class='hata-karti'><b>Soru {yanlis_detay['soru_no']}</b><br>❌ Sizin Cevabınız: {yanlis_detay['secilen']}<br>✅ Doğru Cevap: {yanlis_detay['dogru']}</div>", unsafe_allow_html=True)

            if st.button("Yeni Sınav Başlat"):
                st.session_state.oturum = False
                st.rerun()
        
        else:
            # SORU GÖSTERİMİ
            if st.session_state.mod == "PDF":
                sayfa_no = st.session_state.secilen_liste[st.session_state.aktif_index]
                veri = TYT_VERI[sayfa_no]
                st.subheader(f"📄 {veri['ders']} - Sayfa {sayfa_no}")
                tab1, tab2 = st.tabs(["📄 KİTAPÇIK", "📝 CEVAP FORMU"])
                with tab1: pdf_sayfa_getir(TYT_PDF_ADI, sayfa_no)
                with tab2:
                    cevaplar = veri["cevaplar"]
                    with st.form(f"form_{sayfa_no}"):
                        st.info(f"Bu sayfada {len(cevaplar)} soru var.")
                        for i in range(len(cevaplar)):
                            st.radio(f"Soru {i+1}", ["A","B","C","D","E"], key=f"c_{sayfa_no}_{i}", horizontal=True, index=None)
                            st.divider()
                        if st.form_submit_button("KONTROL ET VE GEÇ ➡️"):
                            sayfa_hatalari = []
                            for i in range(len(cevaplar)):
                                val = st.session_state.get(f"c_{sayfa_no}_{i}")
                                dogru_cevap = cevaplar[i]
                                if dogru_cevap == "X": continue
                                if val is None: st.session_state.bos_sayisi += 1
                                elif val == dogru_cevap: st.session_state.dogru_sayisi += 1
                                else:
                                    st.session_state.yanlis_sayisi += 1
                                    sayfa_hatalari.append({"soru_no": i+1, "secilen": val, "dogru": dogru_cevap})
                            if sayfa_hatalari:
                                st.session_state.karne.append({"tip": "PDF", "durum": "Yanlış", "sayfa_no": sayfa_no, "ders": veri['ders'], "hatali_sorular": sayfa_hatalari})
                            st.toast("Cevaplar Kaydedildi...")
                            time.sleep(1)
                            st.session_state.aktif_index += 1
                            st.rerun()

            elif st.session_state.mod == "MESLEK":
                soru = st.session_state.secilen_liste[st.session_state.aktif_index]
                st.subheader(f"❓ Soru {st.session_state.aktif_index + 1}")
                st.markdown(f"<div class='soru-karti'>{soru['soru']}</div>", unsafe_allow_html=True)
                
                if "karisik_secenekler" not in st.session_state:
                     secenekler = soru["secenekler"].copy()
                     random.shuffle(secenekler)
                     st.session_state.karisik_secenekler = secenekler
                else: secenekler = st.session_state.karisik_secenekler
                
                c1, c2 = st.columns(2)
                for idx, sec in enumerate(secenekler):
                    with (c1 if idx % 2 == 0 else c2):
                        if st.button(sec, key=f"btn_{st.session_state.aktif_index}_{idx}", use_container_width=True):
                            if sec.strip() == soru["cevap"].strip():
                                st.toast("Doğru! ✅")
                                st.session_state.dogru_sayisi += 1
                            else:
                                st.toast("Yanlış! ❌")
                                st.session_state.yanlis_sayisi += 1
                                st.session_state.karne.append({"tip": "MESLEK", "durum": "Yanlış", "soru_metni": soru['soru'], "secilen": sec, "dogru": soru['cevap']})
                            if "karisik_secenekler" in st.session_state: del st.session_state.karisik_secenekler
                            time.sleep(0.5)
                            st.session_state.aktif_index += 1
                            st.rerun()
