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
KONU_JSON_ADI = "konular.json"

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
    }
    .secim-karti:hover {
        transform: scale(1.02);
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
    }
    
    /* İMZA */
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
    
    /* KONU ANLATIM KARTI */
    .konu-karti {
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        border-left: 6px solid #2196F3;
        margin-bottom: 15px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }
    .konu-baslik {
        color: #1565C0;
        font-size: 20px;
        font-weight: bold;
        margin-bottom: 10px;
    }
    .konu-icerik {
        font-size: 16px;
        line-height: 1.6;
        color: #333;
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
    
    /* HATA VE İSTATİSTİK */
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

def dosya_yukle(dosya_adi):
    if not os.path.exists(dosya_adi): return {}
    try:
        with open(dosya_adi, "r", encoding="utf-8") as f:
            data = json.load(f)
            if dosya_adi == TYT_JSON_ADI:
                return {int(k): v for k, v in data.items()}
            return data
    except json.JSONDecodeError:
        st.error(f"⚠️ {dosya_adi} dosyasında format hatası var! (Parantez veya virgül eksik)")
        return {}
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

# KARNE DEĞİŞKENLERİ
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
            <div class='imza-baslik'>Muhasebe ve Finansman Öğretmenleri</div>
            <div class='imza'>Z. SITACI & M. BAĞCIK</div>
        </div>
        """, unsafe_allow_html=True)

# --- 2. SINAV VE MENÜ EKRANI ---
elif st.session_state.ekran == 'sinav':
    
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
        
        st.markdown("<h2 style='text-align:center;'>Sınav Türünü Seçiniz 👇</h2><br>", unsafe_allow_html=True)
        
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
                <p>Konu Testleri ve Ders Notları</p>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Meslek Çöz ➡️", key="btn_meslek"):
                st.session_state.secim_turu = "MESLEK"
        
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
                        st.session_state.dogru_sayisi = 0
                        st.session_state.yanlis_sayisi = 0
                        st.session_state.bos_sayisi = 0
                        st.rerun()
                    else: st.error("Bu derste soru bulunamadı.")
            else:
                st.warning("TYT verileri yüklenmemiş.")
                
        # --- MESLEK AYARLARI (2 SEKME: TEST VE NOTLAR) ---
        elif st.session_state.secim_turu == "MESLEK":
            st.subheader("💼 Meslek Alanı")
            
            tab1, tab2 = st.tabs(["📝 TEST ÇÖZ (Konu & Zor)", "📚 DERS NOTLARI"])
            
            # SEKME 1: KONU TESTLERİ
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
                            st.info(f"Bu testte {len(testler[test])} soru bulunmaktadır.")
                            if st.button("TESTİ BAŞLAT 🚀", key="btn_konu"):
                                st.session_state.secilen_liste = testler[test]
                                st.session_state.mod = "MESLEK"
                                st.session_state.oturum = True
                                st.session_state.karne = [] 
                                st.session_state.aktif_index = 0
                                st.session_state.dogru_sayisi = 0
                                st.session_state.yanlis_sayisi = 0
                                st.session_state.bos_sayisi = 0
                                st.rerun()
                        else: st.warning("Bu derse ait test bulunamadı.")
                    else: st.warning("Bu sınıfa ait ders bulunamadı.")
                else: 
                    st.warning("Veri bulunamadı. Lütfen sorular.json dosyasını kontrol edin.")

            # SEKME 2: KONU ANLATIMI
            with tab2:
                if KONU_VERI:
                    k_sinif = st.selectbox("Sınıf Seçiniz:", list(KONU_VERI.keys()), key="k_s")
                    k_dersler = KONU_VERI.get(k_sinif, {})
                    if k_dersler:
                        k_ders = st.selectbox("Ders Seçiniz:", list(k_dersler.keys()), key="k_d")
                        st.info(f"📖 {k_sinif} - {k_ders} Ders Notları")
                        notlar = k_dersler.get(k_ders, [])
                        
                        for not_maddesi in notlar:
                            st.markdown(f"""
                            <div class='konu-karti'>
                                <div class='konu-baslik'>{not_maddesi['baslik']}</div>
                                <div class='konu-icerik'>{not_maddesi['icerik']}</div>
                            </div>
                            """, unsafe_allow_html=True)
                    else: st.warning("Bu sınıfa ait not bulunamadı.")
                else:
                    st.warning("Konu anlatımı verisi (konular.json) yüklenmemiş.")

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
            # PDF MODU
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

            # MESLEK MODU
            elif st.session_state.mod == "MESLEK":
                soru = st.session_state.secilen_liste[st.session_state.aktif_index]
                st.subheader(f"❓ Soru {st.session_state.aktif_index + 1}")
                st.markdown(f"<div class='soru-karti'>{soru['soru']}</div>", unsafe_allow_html=True)
                
                # Şıkları karıştır ama kaybetme (Session State kullanarak)
                if "secenekler_mix" not in st.session_state:
                     secenekler = soru["secenekler"].copy()
                     random.shuffle(secenekler)
                     st.session_state.secenekler_mix = secenekler
                
                c1, c2 = st.columns(2)
                for idx, sec in enumerate(st.session_state.secenekler_mix):
                    with (c1 if idx % 2 == 0 else c2):
                        if st.button(sec, key=f"btn_{idx}", use_container_width=True):
                            if sec.strip() == soru["cevap"].strip():
                                st.toast("Doğru! ✅")
                                st.session_state.dogru_sayisi += 1
                            else:
                                st.toast("Yanlış! ❌")
                                st.session_state.yanlis_sayisi += 1
                                st.session_state.karne.append({"tip": "MESLEK", "durum": "Yanlış", "soru_metni": soru['soru'], "secilen": sec, "dogru": soru['cevap']})
                            
                            # Sonraki soruya geç
                            del st.session_state.secenekler_mix
                            time.sleep(0.5)
                            st.session_state.aktif_index += 1
                            st.rerun()
