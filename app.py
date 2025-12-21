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

# --- TASARIM ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Dancing+Script:wght@700&display=swap');
    .stApp { background-color: #F0F4C3 !important; }
    h1, h2, h3, h4, .stMarkdown, p, label { color: #212121 !important; }
    .stSelectbox div[data-baseweb="select"] > div { background-color: #FFFFFF !important; color: #000000 !important; border: 2px solid #FF7043; }
    .stDeployButton {display:none;}
    footer {visibility: hidden;}
    #MainMenu {visibility: hidden;}
    .giris-kart { background-color: white; padding: 40px; border-radius: 20px; border: 3px solid #FF7043; text-align: center; box-shadow: 0 10px 20px rgba(0,0,0,0.1); margin-bottom: 20px; }
    .secim-karti { background-color: white; padding: 20px; border-radius: 15px; border: 2px solid #FF7043; text-align: center; transition: transform 0.2s; }
    .secim-karti:hover { transform: scale(1.02); box-shadow: 0 5px 15px rgba(0,0,0,0.2); }
    .imza-container { margin-top: 50px; text-align: right; padding-right: 20px; opacity: 0.8; }
    .imza-baslik { font-family: 'Courier New', monospace; font-size: 14px; color: #555; font-weight: bold; margin-bottom: 5px; }
    .imza { font-family: 'Dancing Script', cursive; color: #D84315; font-size: 22px; }
    .stButton>button { background-color: #FF7043 !important; color: white !important; border-radius: 8px; font-weight: bold; width: 100%; border: 2px solid #D84315 !important; min-height: 50px; font-size: 16px !important; }
    .stButton>button:hover { background-color: #E64A19 !important; }
    .konu-karti { background-color: white; padding: 20px; border-radius: 10px; border-left: 6px solid #2196F3; margin-bottom: 15px; box-shadow: 0 2px 5px rgba(0,0,0,0.05); }
    .konu-baslik { color: #1565C0; font-size: 20px; font-weight: bold; margin-bottom: 10px; }
    .konu-icerik { font-size: 16px; line-height: 1.6; color: #333; }
    .soru-karti { background-color: white; padding: 20px; border-radius: 10px; border-left: 5px solid #FF7043; font-size: 18px; margin-bottom: 20px; color: #000 !important; }
    .hata-karti { background-color: #FFEBEE; border-left: 5px solid #D32F2F; padding: 15px; margin-bottom: 15px; border-radius: 5px; color: #000; }
    .stat-card { background-color: white; padding: 15px; border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); text-align: center; border: 2px solid #FF7043; }
    .stat-number { font-size: 32px; font-weight: bold; color: #D84315; }
    .stat-label { font-size: 16px; color: #555; }
    </style>
""", unsafe_allow_html=True)

def pdf_sayfa_getir(dosya_yolu, sayfa_numarasi):
    if not os.path.exists(dosya_yolu): st.error(f"⚠️ PDF ({dosya_yolu}) yok!"); return
    try:
        doc = fitz.open(dosya_yolu)
        if sayfa_numarasi > len(doc): return
        page = doc.load_page(sayfa_numarasi - 1)
        pix = page.get_pixmap(dpi=150)
        st.image(pix.tobytes(), caption=f"Sayfa {sayfa_numarasi}", use_container_width=True)
    except: pass

def dosya_yukle(dosya_adi):
    if not os.path.exists(dosya_adi): return {}
    try:
        with open(dosya_adi, "r", encoding="utf-8") as f:
            data = json.load(f)
            if dosya_adi == TYT_JSON_ADI: return {int(k): v for k, v in data.items()}
            return data
    except: return {}

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

TYT_VERI = dosya_yukle(TYT_JSON_ADI)
MESLEK_VERI = dosya_yukle(MESLEK_JSON_ADI)
KONU_VERI = dosya_yukle(KONU_JSON_ADI)

if st.session_state.ekran == 'giris':
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        st.markdown("<div class='giris-kart'><h1>🎓 Bağarası ÇPAL</h1><h2>Dijital Sınav Merkezi</h2><hr><p style='font-size:18px; font-weight:bold; color:#D84315;'>Okulumuz Muhasebe ve Finansman Alanının öğrencilerimize hediyesidir.</p><br><p>Lütfen adınızı giriniz.</p></div>", unsafe_allow_html=True)
        ad = st.text_input("Adınız Soyadınız:")
        st.write("")
        if st.button("SİSTEME GİRİŞ YAP ➡️"):
            if ad.strip():
                st.session_state.ad_soyad = ad
                st.session_state.ekran = 'sinav'
                st.rerun()
            else: st.error("İsim giriniz.")
        st.markdown("<div class='imza-container'><div class='imza-baslik'>Muhasebe ve Finansman Öğretmenleri</div><div class='imza'>Zülfikar Sıtacı & Mustafa Bağcık</div></div>", unsafe_allow_html=True)

elif st.session_state.ekran == 'sinav':
    with st.sidebar:
        st.image("https://cdn-icons-png.flaticon.com/512/2997/2997321.png", width=100)
        st.write(f"👤 **{st.session_state.ad_soyad}**")
        st.divider()
        if st.button("🏠 Çıkış Yap"):
            st.session_state.ekran, st.session_state.oturum = 'giris', False
            st.rerun()

    if not st.session_state.oturum:
        st.markdown("<h2 style='text-align:center;'>Sınav Türünü Seçiniz 👇</h2><br>", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("<div class='secim-karti'><h3>📘 TYT Kampı</h3><p>Gerçek çıkmış sorulardan oluşan denemeler.</p></div>", unsafe_allow_html=True)
            if st.button("TYT Çöz ➡️"): st.session_state.secim_turu = "TYT"
        with c2:
            st.markdown("<div class='secim-karti'><h3>💼 Meslek Lisesi</h3><p>Konu Testleri, Denemeler ve Ders Notları</p></div>", unsafe_allow_html=True)
            if st.button("Meslek Çöz ➡️"): st.session_state.secim_turu = "MESLEK"
        
        st.divider()
        
        if st.session_state.secim_turu == "TYT":
            if TYT_VERI:
                ders = st.selectbox("Ders:", ["Karışık Deneme"] + sorted(list(set(v["ders"] for v in TYT_VERI.values()))))
                adet = st.slider("Sayfa:", 1, 10, 3)
                if st.button("BAŞLAT 🚀"):
                    uygun = [s for s, d in TYT_VERI.items() if ders == "Karışık Deneme" or d["ders"] == ders]
                    if uygun:
                        random.shuffle(uygun)
                        st.session_state.secilen_liste = uygun[:adet]
                        st.session_state.mod, st.session_state.oturum = "PDF", True
                        st.session_state.karne, st.session_state.aktif_index = [], 0
                        st.session_state.dogru_sayisi = st.session_state.yanlis_sayisi = st.session_state.bos_sayisi = 0
                        st.rerun()
                    else: st.error("Soru yok.")
            else: st.warning("TYT verisi yok.")

        elif st.session_state.secim_turu == "MESLEK":
            t1, t2, t3 = st.tabs(["📝 KONU TARAMA", "🏆 GENEL DENEME", "📚 KONU ANLATIMI"])
            
            # --- TAB 1: KONU TARAMA (Sınıf -> Ders -> Test) ---
            with t1:
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
                                st.session_state.mod, st.session_state.oturum = "MESLEK", True
                                st.session_state.karne, st.session_state.aktif_index = [], 0
                                st.session_state.dogru_sayisi = st.session_state.yanlis_sayisi = st.session_state.bos_sayisi = 0
                                st.rerun()
                        else: st.warning("Bu derse ait test bulunamadı.")
                    else: st.warning("Bu sınıfa ait ders bulunamadı.")
                else: st.warning("Veri yok.")

            # --- TAB 2: GENEL DENEME (Sınıf -> Deneme) ---
            with t2:
                deneme_verisi = MESLEK_VERI.get("DENEME_SINAVLARI", {})
                if deneme_verisi:
                    sinif_d = st.selectbox("Sınıf Seçiniz:", list(deneme_verisi.keys()), key="s_deneme")
                    denemeler = deneme_verisi.get(sinif_d, {})
                    
                    if denemeler:
                        deneme = st.selectbox("Deneme Sınavı Seçiniz:", list(denemeler.keys()), key="t_deneme")
                        if st.button("DENEMEYİ BAŞLAT 🚀", key="btn_deneme"):
                            st.session_state.secilen_liste = denemeler[deneme]
                            st.session_state.mod, st.session_state.oturum = "MESLEK", True
                            st.session_state.karne, st.session_state.aktif_index = [], 0
                            st.session_state.dogru_sayisi = st.session_state.yanlis_sayisi = st.session_state.bos_sayisi = 0
                            st.rerun()
                    else: st.warning("Bu sınıfa ait deneme yok.")
                else: st.warning("Veri yok.")

            # --- TAB 3: KONU ANLATIMI ---
            with t3:
                if KONU_VERI:
                    s = st.selectbox("Sınıf:", list(KONU_VERI.keys()), key="k_s")
                    d = st.selectbox("Ders:", list(KONU_VERI[s].keys()), key="k_d")
                    for n in KONU_VERI[s][d]:
                        st.markdown(f"<div class='konu-karti'><div class='konu-baslik'>{n['baslik']}</div><div class='konu-icerik'>{n['icerik']}</div></div>", unsafe_allow_html=True)

    else:
        if st.session_state.aktif_index >= len(st.session_state.secilen_liste):
            st.balloons()
            st.markdown(f"<h2 style='text-align:center;'>🏁 Sonuçlar: {st.session_state.ad_soyad}</h2>", unsafe_allow_html=True)
            c1, c2, c3 = st.columns(3)
            c1.markdown(f"<div class='stat-card'><div class='stat-number'>{st.session_state.dogru_sayisi}</div><div class='stat-label'>Doğru</div></div>", unsafe_allow_html=True)
            c2.markdown(f"<div class='stat-card'><div class='stat-number'>{st.session_state.yanlis_sayisi}</div><div class='stat-label'>Yanlış</div></div>", unsafe_allow_html=True)
            c3.markdown(f"<div class='stat-card'><div class='stat-number'>{st.session_state.bos_sayisi}</div><div class='stat-label'>Boş</div></div>", unsafe_allow_html=True)
            st.divider()
            st.subheader("🔍 Hatalı Sorular")
            for h in [k for k in st.session_state.karne if k["durum"] == "Yanlış"]:
                if h["tip"] == "MESLEK": st.markdown(f"<div class='hata-karti'><b>SORU:</b> {h['soru']}<br>❌ <b>Sizin Cevabınız:</b> {h['secilen']}<br>✅ <b>Doğru Cevap:</b> {h['dogru']}</div>", unsafe_allow_html=True)
                elif h["tip"] == "PDF":
                    with st.expander(f"📄 Sayfa {h['sayfa']} (Hataları Gör)"):
                        c1, c2 = st.columns(2)
                        with c1: pdf_sayfa_getir(TYT_PDF_ADI, h['sayfa'])
                        with c2: 
                            for yanlis in h['hatalar']: st.markdown(f"<div class='hata-karti'><b>Soru {yanlis['soru']}</b><br>❌ {yanlis['secilen']} | ✅ {yanlis['dogru']}</div>", unsafe_allow_html=True)
            if st.button("Yeni Sınav"): st.session_state.oturum = False; st.rerun()
        
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
                            st.session_state.karne.append({"tip": "MESLEK", "durum": "Yanlış", "soru": soru['soru'], "secilen": sec, "dogru": soru['cevap']})
                        del st.session_state.secenekler_mix; st.session_state.aktif_index += 1; time.sleep(0.3); st.rerun()

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
                        hatalar = []
                        for i, dogru in enumerate(cevaplar):
                            secilen = st.session_state.get(f"c_{i}")
                            if dogru == "X": continue
                            if not secilen: st.session_state.bos_sayisi += 1
                            elif secilen == dogru: st.session_state.dogru_sayisi += 1
                            else:
                                st.session_state.yanlis_sayisi += 1
                                hatalar.append({"soru": i+1, "secilen": secilen, "dogru": dogru})
                        if hatalar: st.session_state.karne.append({"tip": "PDF", "durum": "Yanlış", "sayfa": sayfa, "hatalar": hatalar})
                        st.session_state.aktif_index += 1; st.rerun()
