import streamlit as st
import random
import os
import time
import json
import fitz  # PyMuPDF
import google.generativeai as genai

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Bağarası Hibrit Eğitim Merkezi", page_icon="🎓", layout="wide")

# --- API KEY KONTROLÜ (Meslek Soruları İçin) ---
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

# --- TASARIM ---
st.markdown("""
    <style>
    .stApp { background-color: #F0F4C3 !important; }
    h1, h2, h3, h4, .stMarkdown { color: #212121 !important; }
    
    .optik-alan {
        background-color: white;
        padding: 15px;
        border-radius: 15px;
        border: 2px solid #FF7043;
        margin-bottom: 20px;
    }
    .stButton>button {
        background-color: #FF7043 !important;
        color: white !important;
        border-radius: 8px;
        font-weight: bold;
        width: 100%;
        border: 2px solid #D84315 !important;
        min-height: 50px;
    }
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] {
        background-color: #FFFFFF;
        border-radius: 5px;
        padding: 10px 20px;
        border: 1px solid #FF7043;
    }
    .stTabs [aria-selected="true"] {
        background-color: #FF7043 !important;
        color: white !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- KONU VE PDF AYARLARI ---
MESLEK_KONULARI = {
    "9. Sınıf Meslek": "Temel Muhasebe, Mesleki Matematik",
    "10. Sınıf Meslek": "Genel Muhasebe, Klavye Teknikleri",
    "11. Sınıf Meslek": "Şirketler Muhasebesi, Maliyet",
    "12. Sınıf Meslek": "Girişimcilik, Finans"
}

# --- PDF CEVAP HARİTASI (Örnek Kısa Liste) ---
PDF_HARITASI = {
    13: {"ders": "Türkçe", "cevaplar": "ECE"},
    14: {"ders": "Türkçe", "cevaplar": "BAC"},
    15: {"ders": "Türkçe", "cevaplar": "BEA"},
    # ... (Diğer sayfaları buraya ekleyebilirsiniz) ...
    374: {"ders": "Biyoloji", "cevaplar": "EEE"}
}

PDF_DOSYA_ADI = "tytson8.pdf"

# --- FONKSİYONLAR ---
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

def ai_soru_uret(ders_adi):
    if "GOOGLE_API_KEY" not in st.secrets:
        return [{"soru": "API Key Eksik!", "secenekler": ["A"], "cevap": "A"}]
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = f"""Rol: Öğretmen. Ders: {ders_adi}. 5 adet çoktan seçmeli soru hazırla. JSON formatında: [ {{"soru": "...", "secenekler": ["A", "B"], "cevap": "A"}} ]"""
        resp = model.generate_content(prompt)
        text = resp.text.strip().replace("```json", "").replace("```", "")
        return json.loads(text)
    except:
        return []

# --- EKRAN AKIŞI ---
if 'oturum' not in st.session_state: st.session_state.oturum = False
if 'mod' not in st.session_state: st.session_state.mod = ""
if 'secilen_liste' not in st.session_state: st.session_state.secilen_liste = []
if 'aktif_index' not in st.session_state: st.session_state.aktif_index = 0
if 'toplam_puan' not in st.session_state: st.session_state.toplam_puan = 0

if not st.session_state.oturum:
    with st.sidebar:
        st.title("Sınav Modu")
        mod_secimi = st.radio("Seçim:", ["TYT Kampı (PDF)", "Meslek Lisesi"])
        
        if mod_secimi == "TYT Kampı (PDF)":
            mevcut = sorted(list(set(v["ders"] for v in PDF_HARITASI.values())))
            ders = st.selectbox("Ders:", ["Karışık Deneme"] + mevcut)
            adet = st.slider("Sayfa Sayısı:", 1, 10, 3)
            if st.button("Başlat 🚀"):
                uygun = [s for s, d in PDF_HARITASI.items() if ders == "Karışık Deneme" or d["ders"] == ders]
                if uygun:
                    random.shuffle(uygun)
                    st.session_state.secilen_liste = uygun[:adet]
                    st.session_state.mod = "PDF"
                    st.session_state.oturum = True
                    st.rerun()
                else:
                    st.error("Sayfa bulunamadı.")
        else:
            ders = st.selectbox("Alan:", list(MESLEK_KONULARI.keys()))
            if st.button("Başlat 🤖"):
                sorular = ai_soru_uret(MESLEK_KONULARI[ders])
                st.session_state.secilen_liste = sorular
                st.session_state.mod = "AI"
                st.session_state.oturum = True
                st.rerun()
else:
    if st.session_state.aktif_index < len(st.session_state.secilen_liste):
        if st.session_state.mod == "PDF":
            sayfa_no = st.session_state.secilen_liste[st.session_state.aktif_index]
            veri = PDF_HARITASI[sayfa_no]
            st.subheader(f"📄 {veri['ders']} - Sayfa {sayfa_no}")
            tab1, tab2 = st.tabs(["📄 KİTAPÇIK", "📝 CEVAP KAĞIDI"])
            with tab1: pdf_sayfa_getir(PDF_DOSYA_ADI, sayfa_no)
            with tab2:
                dogru_sayisi = 0
                with st.form(f"f_{sayfa_no}"):
                    for i in range(len(veri["cevaplar"])):
                        st.write(f"Soru {i+1}")
                        st.radio(f"S_{i}", ["A","B","C","D","E"], key=f"c_{sayfa_no}_{i}", horizontal=True)
                        st.divider()
                    if st.form_submit_button("KONTROL ET ➡️"):
                        for i in range(len(veri["cevaplar"])):
                            if st.session_state.get(f"c_{sayfa_no}_{i}") == veri["cevaplar"][i]:
                                dogru_sayisi += 1
                        st.session_state.toplam_puan += (dogru_sayisi * 5)
                        st.session_state.aktif_index += 1
                        st.rerun()
        else: # AI MODU
            soru = st.session_state.secilen_liste[st.session_state.aktif_index]
            st.info(soru["soru"])
            for sec in soru["secenekler"]:
                if st.button(sec, key=sec):
                    if sec == soru["cevap"]: st.toast("Doğru!"); st.session_state.toplam_puan+=10
                    st.session_state.aktif_index += 1; st.rerun()
    else:
        st.balloons()
        st.success(f"Bitti! Puan: {st.session_state.toplam_puan}")
        if st.button("Başa Dön"): st.session_state.oturum = False; st.rerun()