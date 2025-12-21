import streamlit as st
import random
import os
import time
import json
import fitz  # PyMuPDF

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Bağarası Hibrit Eğitim Merkezi", page_icon="🎓", layout="wide")

# --- DOSYA İSİMLERİ ---
TYT_PDF_ADI = "tytson8.pdf"  # İsim Güncellendi
TYT_JSON_ADI = "tyt_data.json"
MESLEK_JSON_ADI = "sorular.json"

# --- TASARIM VE CSS ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Dancing+Script:wght@700&display=swap');
    
    /* Arka Planı Zorla Açık Renk Yap */
    .stApp { background-color: #F0F4C3 !important; }
    
    /* Tüm Yazıları Koyu Renk Yap (Gece Modunda Görünmesi İçin) */
    h1, h2, h3, h4, .stMarkdown, p, label { color: #212121 !important; }
    
    /* MENU VE DROPDOWN DÜZELTMESİ (Ders İsimleri Görünsün Diye) */
    .stSelectbox div[data-baseweb="select"] > div {
        background-color: #FFFFFF !important;
        color: #000000 !important;
        border: 2px solid #FF7043;
    }
    .stSelectbox div[data-baseweb="select"] span {
        color: #000000 !important;
    }
    /* Açılan Listenin Rengi */
    ul[data-baseweb="menu"] {
        background-color: #FFFFFF !important;
    }
    ul[data-baseweb="menu"] li span {
        color: #000000 !important;
    }

    /* Gereksiz Şeyleri Gizle */
    .stDeployButton {display:none;}
    footer {visibility: hidden;}
    #MainMenu {visibility: hidden;}
    
    /* Giriş Kartı */
    .giris-kart {
        background-color: white;
        padding: 40px;
        border-radius: 20px;
        border: 3px solid #FF7043;
        text-align: center;
        box-shadow: 0 10px 20px rgba(0,0,0,0.1);
        margin-bottom: 20px;
    }
    
    /* Zarif Alt İmza */
    .imza-container {
        margin-top: 50px;
        text-align: right;
        padding-right: 20px;
        opacity: 0.7; /* Hafif silik */
    }
    .imza {
        font-family: 'Dancing Script', cursive;
        color: #D84315;
        font-size: 18px; /* Daha küçük */
    }
    .imza-unvan {
        font-family: sans-serif;
        font-size: 10px;
        color: #555;
    }
    
    /* Butonlar */
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
    
    /* Soru Kartı */
    .soru-karti {
        background-color: white; 
        padding: 20px; 
        border-radius: 10px; 
        border-left: 5px solid #FF7043; 
        font-size: 18px;
        margin-bottom: 20px;
        color: #000 !important;
    }
    
    /* Hata Kartı */
    .hata-karti {
        background-color: #FFEBEE;
        border-left: 5px solid #D32F2F;
        padding: 15px;
        margin-bottom: 15px;
        border-radius: 5px;
        color: #000;
    }
    
    /* İstatistik Kartları */
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
if 'toplam_puan' not in st.session_state: st.session_state.toplam_puan = 0

# KARNE DEĞİŞKENLERİ
if 'karne' not in st.session_state: st.session_state.karne = []
if 'dogru_sayisi_toplam' not in st.session_state: st.session_state.dogru_sayisi_toplam = 0
if 'yanlis_sayisi_toplam' not in st.session_state: st.session_state.yanlis_sayisi_toplam = 0
if 'bos_sayisi_toplam' not in st.session_state: st.session_state.bos_sayisi_toplam = 0

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
        # İSTENİLEN BUTON METNİ GÜNCELLENDİ
        if st.button("Sınav Türünü Seçmek İçin Giriş Yapınız ➡️"):
            if ad_soyad_input.strip():
                st.session_state.ad_soyad = ad_soyad_input
                st.session_state.ekran = 'sinav'
                # Değişkenleri sıfırla
                st.session_state.karne = []
                st.session_state.dogru_sayisi_toplam = 0
                st.session_state.yanlis_sayisi_toplam = 0
                st.rerun()
            else:
                st.error("Lütfen adınızı giriniz!")
        
        # GÜNCELLENMİŞ İMZA ALANI (SAĞ ALT KÖŞE)
        st.markdown("""
        <div class='imza-container'>
            <div class='imza'>Zülfikar Sıtacı</div>
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
        st.divider()
        
        # SINAV SEÇİMİ
        if not st.session_state.oturum:
            st.header("Sınav Türü Seçin")
            tur_secimi = st.radio("Hangisi çözülecek?", ["TYT Deneme (PDF)", "Meslek Lisesi (Test)"])
            
            if tur_secimi == "TYT Deneme (PDF)":
                if TYT_VERI:
                    dersler = sorted(list(set(v["ders"] for v in TYT_VERI.values())))
                    # Renk sorunu CSS ile çözüldü
                    ders = st.selectbox("Ders:", ["Karışık Deneme"] + dersler)
                    adet = st.slider("Sayfa Sayısı:", 1, 10, 3)
                    if st.button("TYT Başlat"):
                        uygun = [s for s, d in TYT_VERI.items() if ders == "Karışık Deneme" or d["ders"] == ders]
                        if uygun:
                            random.shuffle(uygun)
                            st.session_state.secilen_liste = uygun[:adet]
                            st.session_state.mod = "PDF"
                            st.session_state.oturum = True
                            st.session_state.karne = [] 
                            st.session_state.aktif_index = 0
                            st.rerun()
                        else: st.error("Ders bulunamadı.")
            else:
                if MESLEK_VERI:
                    # Renk sorunu CSS ile çözüldü
                    alan = st.selectbox("Alan/Sınıf:", list(MESLEK_VERI.keys()))
                    if st.button("Meslek Sınavı Başlat"):
                        sorular = MESLEK_VERI.get(alan, [])
                        if sorular:
                            random.shuffle(sorular)
                            st.session_state.secilen_liste = sorular
                            st.session_state.mod = "MESLEK"
                            st.session_state.oturum = True
                            st.session_state.karne = [] 
                            st.session_state.aktif_index = 0
                            st.rerun()
                        else: st.error("Soru yok.")

    # --- SORU ÇÖZME VEYA SONUÇ EKRANI ---
    if st.session_state.oturum:
        
        # --- SONUÇ EKRANI (KARNE) ---
        if st.session_state.aktif_index >= len(st.session_state.secilen_liste):
            st.balloons()
            
            st.markdown(f"<h2 style='text-align:center;'>🏁 Sınav Sonucu: {st.session_state.ad_soyad}</h2>", unsafe_allow_html=True)
            
            c1, c2, c3, c4 = st.columns(4)
            c1.markdown(f"<div class='stat-card'><div class='stat-number'>{st.session_state.dogru_sayisi_toplam}</div><div class='stat-label'>Doğru</div></div>", unsafe_allow_html=True)
            c2.markdown(f"<div class='stat-card'><div class='stat-number'>{st.session_state.yanlis_sayisi_toplam}</div><div class='stat-label'>Yanlış</div></div>", unsafe_allow_html=True)
            c3.markdown(f"<div class='stat-card'><div class='stat-number'>{st.session_state.bos_sayisi_toplam}</div><div class='stat-label'>Boş</div></div>", unsafe_allow_html=True)
            
            toplam_puan = st.session_state.dogru_sayisi_toplam * (5 if st.session_state.mod == "PDF" else 10)
            c4.markdown(f"<div class='stat-card'><div class='stat-number'>{toplam_puan}</div><div class='stat-label'>Puan</div></div>", unsafe_allow_html=True)
            
            st.divider()
            
            st.subheader("🔍 Hatalı Yaptığınız Soruların Analizi")
            
            yanlislar = [k for k in st.session_state.karne if k["durum"] == "Yanlış"]
            
            if not yanlislar:
                st.success("Tebrikler! Hiç yanlışınız yok. Harika iş çıkardınız. 🌟")
            else:
                st.info("Aşağıda yanlış yaptığınız soruları ve doğru cevaplarını inceleyebilirsiniz.")
                
                for hata in yanlislar:
                    if hata["tip"] == "MESLEK":
                        st.markdown(f"""
                        <div class='hata-karti'>
                            <b>SORU:</b> {hata['soru_metni']}<br><br>
                            ❌ <b>Sizin Cevabınız:</b> {hata['secilen']}<br>
                            ✅ <b>Doğru Cevap:</b> {hata['dogru']}
                        </div>
                        """, unsafe_allow_html=True)
                    
                    elif hata["tip"] == "PDF":
                        with st.expander(f"📄 Sayfa {hata['sayfa_no']} - {hata['ders']} (Hataları Gör)"):
                            c_pdf, c_detay = st.columns([1, 1])
                            with c_pdf:
                                pdf_sayfa_getir(TYT_PDF_ADI, hata['sayfa_no'])
                            with c_detay:
                                for yanlis_detay in hata['hatali_sorular']:
                                    st.markdown(f"""
                                    <div class='hata-karti'>
                                        <b>Soru {yanlis_detay['soru_no']}</b><br>
                                        ❌ Sizin Cevabınız: {yanlis_detay['secilen']}<br>
                                        ✅ Doğru Cevap: {yanlis_detay['dogru']}
                                    </div>
                                    """, unsafe_allow_html=True)

            if st.button("Yeni Sınav Başlat"):
                st.session_state.oturum = False
                st.rerun()
        
        else:
            # --- SINAV DEVAM EDİYOR ---
            
            # MOD 1: TYT (PDF)
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
                                
                                if val is None:
                                    st.session_state.bos_sayisi_toplam += 1
                                elif val == dogru_cevap:
                                    st.session_state.dogru_sayisi_toplam += 1
                                else:
                                    st.session_state.yanlis_sayisi_toplam += 1
                                    sayfa_hatalari.append({
                                        "soru_no": i+1,
                                        "secilen": val,
                                        "dogru": dogru_cevap
                                    })
                            
                            if sayfa_hatalari:
                                st.session_state.karne.append({
                                    "tip": "PDF",
                                    "durum": "Yanlış",
                                    "sayfa_no": sayfa_no,
                                    "ders": veri['ders'],
                                    "hatali_sorular": sayfa_hatalari
                                })
                            
                            st.toast("Cevaplar Kaydedildi...")
                            time.sleep(1)
                            st.session_state.aktif_index += 1
                            st.rerun()

            # MOD 2: MESLEK
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
                                st.session_state.dogru_sayisi_toplam += 1
                            else:
                                st.toast("Yanlış! ❌")
                                st.session_state.yanlis_sayisi_toplam += 1
                                st.session_state.karne.append({
                                    "tip": "MESLEK",
                                    "durum": "Yanlış",
                                    "soru_metni": soru['soru'],
                                    "secilen": sec,
                                    "dogru": soru['cevap']
                                })
                            
                            if "karisik_secenekler" in st.session_state: del st.session_state.karisik_secenekler
                            time.sleep(0.5)
                            st.session_state.aktif_index += 1
                            st.rerun()
