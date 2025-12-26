import streamlit as st
import time
import pandas as pd
import random
import json
import os

# --- 1. AYARLAR & CSS (CINZEL FONT) ---
st.set_page_config(page_title="Finans Kampüsü", page_icon="🏛️", layout="wide")

st.markdown("""
    <style>
    /* Google Font: Cinzel Import */
    @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;700;900&family=Poppins:wght@300;400;600&display=swap');
    
    .stApp { background-color: #f4f4f8; }
    
    /* TÜM BAŞLIKLAR VE MENÜLER CINZEL OLACAK */
    h1, h2, h3, h4, .stTabs button { font-family: 'Cinzel', serif !important; font-weight: 700 !important; }
    p, div, span, button { font-family: 'Poppins', sans-serif; }
    
    /* Sekme Tasarımı */
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] {
        height: 50px; background-color: #fff; border-radius: 8px 8px 0 0;
        border: 1px solid #ddd; border-bottom: none; font-size: 16px; color: #555;
    }
    .stTabs [aria-selected="true"] { background-color: #2c3e50; color: #f1c40f !important; border: 1px solid #2c3e50; }
    
    /* Skor Kartları */
    .info-card { background: linear-gradient(135deg, #2c3e50 0%, #000000 100%); padding: 25px; border-radius: 15px; color: #f1c40f; text-align: center; box-shadow: 0 10px 20px rgba(0,0,0,0.2); border: 2px solid #f1c40f; }
    .score-val { font-family: 'Cinzel', serif; font-size: 42px; font-weight: 900; }
    
    /* Butonlar */
    div.stButton > button { border-radius: 8px; height: 45px; font-weight: bold; border: 1px solid #ccc; transition: 0.3s; text-transform: uppercase; letter-spacing: 1px; }
    div.stButton > button:hover { border-color: #f1c40f; color: #f1c40f; background-color: #2c3e50; }
    
    /* Matrix Grid Stili */
    .matrix-grid { display: grid; grid-template-columns: repeat(10, 1fr); gap: 2px; background: #000; padding: 5px; border-radius: 10px; border: 4px solid #333; }
    .matrix-cell { width: 100%; aspect-ratio: 1; background-color: #111; border-radius: 2px; transition: 0.2s; }
    .matrix-cell.active { box-shadow: 0 0 5px currentColor; }
    </style>
""", unsafe_allow_html=True)

# --- 2. DOSYA VE VERİ YÖNETİMİ (ESKİ JSON YAPISI) ---
TYT_JSON_ADI = "tyt_data.json"
MESLEK_JSON_ADI = "sorular.json"

# Dosyalar yoksa oluştur (Hata vermemesi için)
if not os.path.exists(TYT_JSON_ADI):
    dummy_tyt = {"1": {"ders": "Temel Kavramlar", "cevaplar": ["A", "B", "C", "D", "E"]}}
    with open(TYT_JSON_ADI, "w", encoding="utf-8") as f: json.dump(dummy_tyt, f)

if not os.path.exists(MESLEK_JSON_ADI):
    dummy_meslek = {"KONU_TARAMA": {"9. Sınıf": {"Muhasebe": {"Test 1": [{"soru": "Varlık nedir?", "secenekler": ["Para", "Borç"], "cevap": "Para"}]}}}}
    with open(MESLEK_JSON_ADI, "w", encoding="utf-8") as f: json.dump(dummy_meslek, f)

def load_jsons():
    try:
        with open(TYT_JSON_ADI, "r", encoding="utf-8") as f: tyt = json.load(f)
        with open(MESLEK_JSON_ADI, "r", encoding="utf-8") as f: meslek = json.load(f)
        return tyt, meslek
    except: return {}, {}

TYT_DATA, MESLEK_DATA = load_jsons()

# --- 3. SESSION STATE ---
if 'db' not in st.session_state: st.session_state.db = {} # {user_key: score}
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'user_info' not in st.session_state: st.session_state.user_info = {}
if 'active_app' not in st.session_state: st.session_state.active_app = "MAIN" # MAIN, GAME_FIN, GAME_MTX, QUIZ
if 'temp_game_score' not in st.session_state: st.session_state.temp_game_score = 0
if 'premium_unlocked' not in st.session_state: st.session_state.premium_unlocked = False
if 'finance_assets' not in st.session_state: st.session_state.finance_assets = {"Limon": 0, "Simit": 0, "Büfe": 0}

# Matrix Renkleri: Gold, Rose Gold, Gri (Gümüş), Mor
MATRIX_COLORS = ["#FFD700", "#B76E79", "#C0C0C0", "#800080", "#FFD700"] 

def get_total_score(key): return st.session_state.db.get(key, 0)
def save_score(key, points): st.session_state.db[key] = st.session_state.db.get(key, 0) + points

# --- EKRAN: GİRİŞ ---
if not st.session_state.logged_in:
    c1, c2, c3 = st.columns([1, 1, 1])
    with c2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown("<div style='text-align:center'><h1>🏛️ FİNANS KAMPÜSÜ</h1><p>Giriş Yap</p></div>", unsafe_allow_html=True)
        with st.form("login"):
            ad = st.text_input("Ad Soyad")
            no = st.text_input("Okul No")
            if st.form_submit_button("SİSTEME GİR", type="primary"):
                if ad and no:
                    key = f"{no}_{ad.strip()}"
                    st.session_state.user_info = {"name": ad, "no": no, "key": key}
                    st.session_state.logged_in = True
                    if key not in st.session_state.db: st.session_state.db[key] = 0
                    st.rerun()
                else: st.error("Bilgileri giriniz.")

# --- EKRAN: ANA UYGULAMA ---
else:
    user = st.session_state.user_info
    user_key = user['key']
    main_score = get_total_score(user_key)

    # OYUNLARIN İÇİNE GİRİLDİYSE MENÜYÜ GİZLE
    if st.session_state.active_app == "MAIN":
        with st.sidebar:
            st.write(f"👤 **{user['name']}**")
            st.write(f"🎓 No: {user['no']}")
            if st.button("Çıkış Yap"): st.session_state.logged_in = False; st.rerun()

        # SEKMELER
        tab1, tab2, tab3, tab4, tab5 = st.tabs(["🏠 PROFİL", "📚 DERSLER", "🎮 OYUNLAR", "💎 PREMIUM", "🏆 SIRALAMA"])

        # TAB 1: PROFİL
        with tab1:
            st.markdown(f"### HOŞGELDİN, {user['name'].upper()}")
            st.markdown(f"""
                <div class="info-card">
                    <div style="font-size:14px; letter-spacing:2px;">TOPLAM VARLIK</div>
                    <div class="score-val">{main_score} ₺</div>
                </div>
            """, unsafe_allow_html=True)

        # TAB 2: DERSLER (JSON Parsing)
        with tab2:
            st.subheader("SORU ÇÖZÜM MERKEZİ")
            col_a, col_b = st.columns(2)
            
            with col_a:
                with st.container(border=True):
                    st.markdown("#### 📘 TYT KAMPI")
                    # JSON'dan TYT derslerini listele
                    tyt_options = [f"Test {k} - {v['ders']}" for k, v in TYT_DATA.items()]
                    sel_tyt = st.selectbox("Test Seç:", tyt_options)
                    if st.button("TYT BAŞLA", key="btn_tyt"):
                        st.session_state.active_app = "QUIZ"
                        st.session_state.quiz_data = TYT_DATA[sel_tyt.split(" ")[1]]["cevaplar"] # Basit mantık
                        st.session_state.quiz_type = "TYT"
                        st.rerun()

            with col_b:
                with st.container(border=True):
                    st.markdown("#### 💼 MESLEKİ GELİŞİM")
                    # Meslek JSON yapısını düzleştirme (Flatten)
                    meslek_tests = []
                    if "KONU_TARAMA" in MESLEK_DATA:
                        for sinif, dersler in MESLEK_DATA["KONU_TARAMA"].items():
                            for ders, testler in dersler.items():
                                for test_adi, sorular in testler.items():
                                    meslek_tests.append(f"{sinif} - {ders} - {test_adi}")
                    
                    sel_meslek = st.selectbox("Konu Seç:", meslek_tests)
                    if st.button("MESLEK BAŞLA", key="btn_meslek"):
                        # Seçilen testi bul ve başlat
                        # (Not: Burada tam eşleşme kodu uzun olacağı için simüle ediyoruz, gerçekte parse edilir)
                        st.session_state.active_app = "QUIZ"
                        st.session_state.quiz_data = [{"soru": "Örnek Soru?", "cevap": "A", "secenekler":["A","B"]}] # Örnek
                        st.session_state.quiz_type = "MESLEK"
                        st.rerun()

        # TAB 3: OYUNLAR
        with tab3:
            st.subheader("EKONOMİ SİMÜLASYONU")
            c1, c2 = st.columns(2)
            with c1:
                with st.container(border=True):
                    st.markdown("### 💰 FİNANS İMPARATORU")
                    st.caption("Şirket kur, 1 Milyon yap, Premium ol.")
                    if st.button("OYNA (FİNANS)", use_container_width=True):
                        st.session_state.active_app = "GAME_FIN"
                        st.session_state.temp_game_score = 0
                        st.rerun()
            with c2:
                with st.container(border=True):
                    st.markdown("### 🧩 ASSET MATRIX")
                    st.caption("10x12 Grid. Renkleri topla.")
                    if st.button("OYNA (MATRIX)", use_container_width=True):
                        st.session_state.active_app = "GAME_MTX"
                        st.session_state.temp_game_score = 0
                        st.rerun()

        # TAB 4: PREMIUM
        with tab4:
            st.subheader("💎 PREMIUM LOUNGE")
            if st.session_state.premium_unlocked:
                st.success("Premium Üye Girişi Başarılı")
                st.markdown("### 🤖 YAPAY ZEKA ÖZEL SORULARI")
                st.info("Soru 1: Bir startup'ın değerlemesi (Valuation) nasıl hesaplanır?")
                st.info("Soru 2: Blockchain teknolojisinin muhasebe denetimine etkisi nedir?")
                st.button("Cevapları Analiz Et (AI)")
            else:
                st.warning("Bu alana girmek için Finans İmparatoru oyununda 1.000.000 ₺ biriktirip kodu almalısın.")
                kod_gir = st.text_input("Premium Kodun Var mı?")
                if st.button("KODU ONAYLA"):
                    if kod_gir == "MILLIONAIRE":
                        st.session_state.premium_unlocked = True
                        st.balloons()
                        st.rerun()
                    else:
                        st.error("Hatalı Kod!")

        # TAB 5: SIRALAMA
        with tab5:
            st.subheader("🏆 LİDERLER")
            data = [{"Öğrenci": k.split('_')[1], "Puan": v} for k, v in st.session_state.db.items()]
            df = pd.DataFrame(data).sort_values("Puan", ascending=False).reset_index(drop=True)
            df.index += 1
            st.dataframe(df, use_container_width=True)

    # --- OYUN EKRANLARI (MODÜLER) ---
    
    # 1. FİNANS OYUNU
    elif st.session_state.active_app == "GAME_FIN":
        st.markdown("<h2 style='text-align:center; color:#f1c40f;'>💰 FİNANS İMPARATORU</h2>", unsafe_allow_html=True)
        
        # Üst Bilgi Barı
        c1, c2, c3 = st.columns([1, 2, 1])
        with c1: 
            if st.button("⬅️ MENÜYE DÖN"):
                st.session_state.active_app = "MAIN"
                st.rerun()
        with c2:
            st.markdown(f"<div style='text-align:center; font-size:24px; font-weight:bold;'>KASA: {st.session_state.temp_game_score} ₺</div>", unsafe_allow_html=True)
        with c3:
            if st.button("🏦 BANKAYA AKTAR"):
                save_score(user_key, st.session_state.temp_game_score)
                st.session_state.temp_game_score = 0
                st.toast("Para ana hesabına aktarıldı!")
                st.rerun()

        st.divider()
        
        # Cimri Oyun Alanı
        col1, col2 = st.columns(2)
        
        with col1:
            st.info("🔨 İŞ GÜCÜ")
            if st.button("🍋 LİMON SAT (+1 ₺)", use_container_width=True):
                st.session_state.temp_game_score += 1
                st.rerun()
            
            st.write("")
            if st.button("🥨 SİMİT SAT (+3 ₺)", use_container_width=True):
                # Biraz zorluk
                time.sleep(0.5) 
                st.session_state.temp_game_score += 3
                st.rerun()

        with col2:
            st.warning("📈 YATIRIMLAR")
            # Premium Kontrolü
            if st.session_state.temp_game_score >= 1000000:
                st.success("🎉 TEBRİKLER! 1 MİLYON OLDUN!")
                st.markdown("### PREMIUM KODUN: **MILLIONAIRE**")
                st.caption("Bu kodu Premium sekmesine gir.")
            else:
                st.progress(min(st.session_state.temp_game_score / 1000000, 1.0))
                st.caption(f"Premium Hedef: {st.session_state.temp_game_score} / 1.000.000")

    # 2. MATRIX OYUNU
    elif st.session_state.active_app == "GAME_MTX":
        st.markdown("<h2 style='text-align:center; color:#B76E79;'>🧩 ASSET MATRIX (10x12)</h2>", unsafe_allow_html=True)
        
        score = st.session_state.temp_game_score
        
        # Renk Belirleme (Her 50 puanda bir değişir)
        level_idx = min((score // 50), len(MATRIX_COLORS)-1)
        current_color = MATRIX_COLORS[level_idx]
        
        c1, c2, c3 = st.columns([1, 2, 1])
        with c1:
            if st.button("⬅️ ÇIKIŞ"):
                st.session_state.active_app = "MAIN"
                st.rerun()
        with c2:
            st.markdown(f"<div style='text-align:center; color:{current_color}; font-size:24px; font-weight:bold;'>DEĞER: {score}</div>", unsafe_allow_html=True)
        with c3:
            if st.button("🏦 AKTAR"):
                save_score(user_key, score)
                st.session_state.temp_game_score = 0
                st.toast("Değerler nakite çevrildi!")
                st.rerun()

        # Matrix Grid Simülasyonu (HTML ile görselleştirme çünkü 120 buton yavaşlatır)
        # Doluluk oranı puana göre değişsin
        filled_cells = min(score % 50 * 2.4, 120) # 50 puanda 120 hücre dolsun (görsel)
        
        grid_html = f"""
        <div style="display: grid; grid-template-columns: repeat(10, 1fr); gap: 4px; max-width: 400px; margin: auto; background: #222; padding: 10px; border: 4px solid {current_color}; border-radius: 10px;">
        """
        for i in range(120): # 10x12 = 120 hücre
            bg = current_color if i < filled_cells else "#333"
            shadow = f"box-shadow: 0 0 5px {current_color};" if i < filled_cells else ""
            grid_html += f'<div style="width: 100%; aspect-ratio: 1; background-color: {bg}; border-radius: 2px; {shadow}"></div>'
        grid_html += "</div>"
        
        st.markdown(grid_html, unsafe_allow_html=True)
        
        st.write("")
        # Aksiyon Butonu
        if st.button("⛏️ BLOK KAZ (+1)", use_container_width=True, type="primary"):
            st.session_state.temp_game_score += 1
            st.rerun()

    # 3. QUIZ EKRANI
    elif st.session_state.active_app == "QUIZ":
        st.markdown(f"## 📝 {st.session_state.quiz_type} TESTİ")
        
        # Burası örnek olarak sadece bir soru gösteriyor. Gerçek JSON yapısı entegre edilecek.
        # Şimdilik kullanıcıya 5 puan verip çıkalım (Cimri)
        
        st.info("Soru: Aşağıdakilerden hangisi bir finansal tablodur?")
        c1, c2 = st.columns(2)
        if c1.button("A) Bilanço"):
            st.success("Doğru! +5 Puan")
            save_score(user_key, 5)
            time.sleep(1)
            st.session_state.active_app = "MAIN"
            st.rerun()
        if c2.button("B) Tcetveli"):
            st.error("Yanlış.")
            time.sleep(1)
            st.session_state.active_app = "MAIN"
            st.rerun()
            
        if st.button("Vazgeç"):
            st.session_state.active_app = "MAIN"
            st.rerun()
