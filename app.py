import streamlit as st
import time
import pandas as pd
import random
import json
import os

# --- 1. AYARLAR & CSS ---
st.set_page_config(page_title="Finans Kampüsü", page_icon="🎓", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #f8f9fa; }
    
    /* Sekme Tasarımı */
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] {
        height: 50px; background-color: #fff; border-radius: 10px 10px 0 0;
        box-shadow: 0 -2px 5px rgba(0,0,0,0.05); border: none; font-weight: 600;
    }
    .stTabs [aria-selected="true"] { background-color: #6c5ce7; color: white !important; }
    
    /* Kartlar */
    .info-card { background: white; padding: 20px; border-radius: 15px; box-shadow: 0 4px 10px rgba(0,0,0,0.05); text-align: center; }
    .score-val { color: #6c5ce7; font-size: 36px; font-weight: 900; }
    
    /* Özel Butonlar */
    div.stButton > button { border-radius: 12px; height: 50px; font-weight: bold; transition: 0.3s; }
    div.stButton > button:hover { transform: scale(1.02); }
    .game-btn { border: 2px solid #6c5ce7 !important; color: #6c5ce7 !important; background: white !important; }
    .game-btn:hover { background: #6c5ce7 !important; color: white !important; }
    </style>
""", unsafe_allow_html=True)

# --- 2. VERİ YÖNETİMİ ---
if 'db' not in st.session_state:
    st.session_state.db = {"101_Örnek Öğrenci": 500} # Simülasyon Verisi

def get_score(key): return st.session_state.db.get(key, 0)
def add_score(key, points): 
    st.session_state.db[key] = st.session_state.db.get(key, 0) + points

# --- 3. SORU VERİLERİ (ÖRNEK) ---
SORULAR = {
    "TYT": [
        {"q": "Aşağıdakilerden hangisi bir noktalama işaretidir?", "opts": ["A) Virgül", "B) Harf", "C) Kelime"], "a": "A) Virgül"},
        {"q": "3 + 5 x 2 işleminin sonucu kaçtır?", "opts": ["A) 16", "B) 13", "C) 10"], "a": "B) 13"},
        {"q": "Türkiye'nin başkenti neresidir?", "opts": ["A) İstanbul", "B) İzmir", "C) Ankara"], "a": "C) Ankara"}
    ],
    "MESLEK": [
        {"q": "İşletmenin kasasındaki nakit para hangi hesapta izlenir?", "opts": ["A) 100 Kasa", "B) 102 Bankalar", "C) 103 Çekler"], "a": "A) 100 Kasa"},
        {"q": "Bilanço eşitliği hangisidir?", "opts": ["A) Varlık = Kaynak", "B) Gelir = Gider", "C) Borç = Alacak"], "a": "A) Varlık = Kaynak"}
    ]
}

# --- 4. OTURUM STATE ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'user_info' not in st.session_state: st.session_state.user_info = {}
if 'active_screen' not in st.session_state: st.session_state.active_screen = "TABS" # TABS, GAME_FINANCE, QUIZ_TYT, QUIZ_MESLEK
if 'quiz_idx' not in st.session_state: st.session_state.quiz_idx = 0

# ==============================================================================
# EKRAN 1: GİRİŞ YAP
# ==============================================================================
if not st.session_state.logged_in:
    c1, c2, c3 = st.columns([1, 1, 1])
    with c2:
        st.markdown("<br><br><h1 style='text-align:center; color:#6c5ce7;'>🎓 Finans Kampüsü</h1>", unsafe_allow_html=True)
        st.info("👋 Hoşgeldin! Puanlarının kaybolmaması için bilgilerini gir.")
        with st.form("login"):
            ad = st.text_input("Ad Soyad")
            no = st.text_input("Okul No")
            if st.form_submit_button("BAŞLA 🚀", type="primary"):
                if ad and no:
                    key = f"{no}_{ad.strip()}"
                    st.session_state.user_info = {"name": ad, "no": no, "key": key}
                    st.session_state.logged_in = True
                    if key not in st.session_state.db: st.session_state.db[key] = 0
                    st.rerun()
                else: st.error("Eksik bilgi!")

# ==============================================================================
# EKRAN 2: ANA PANEL (SEKMELER)
# ==============================================================================
elif st.session_state.active_screen == "TABS":
    user = st.session_state.user_info
    score = get_score(user['key'])
    
    with st.sidebar:
        st.write(f"👤 **{user['name']}**")
        st.write(f"🏫 **{user['no']}**")
        if st.button("Çıkış"): st.session_state.logged_in = False; st.rerun()

    tab1, tab2, tab3, tab4 = st.tabs(["🏠 Profil", "📚 Dersler", "🎮 Oyunlar", "🏆 Sıralama"])

    with tab1:
        st.markdown(f"### Merhaba, {user['name']}!")
        st.markdown(f"""
            <div class="info-card">
                <div style="color:#888;">TOPLAM VARLIK</div>
                <div class="score-val">{score} ₺</div>
            </div>
        """, unsafe_allow_html=True)
        st.success("Verilerin otomatik olarak kaydediliyor. ✅")

    with tab2:
        col1, col2 = st.columns(2)
        with col1:
            st.info("📘 **TYT Kampı**")
            if st.button("Testi Başlat (TYT)"):
                st.session_state.active_screen = "QUIZ_TYT"
                st.session_state.quiz_idx = 0
                st.rerun()
        with col2:
            st.warning("💼 **Meslek Alanı**")
            if st.button("Testi Başlat (Meslek)"):
                st.session_state.active_screen = "QUIZ_MESLEK"
                st.session_state.quiz_idx = 0
                st.rerun()

    with tab3:
        col1, col2 = st.columns(2)
        with col1:
            st.success("💰 **Finans İmparatoru**")
            st.caption("Şirket kur, para yönet.")
            if st.button("Oyuna Gir"):
                st.session_state.active_screen = "GAME_FINANCE"
                st.rerun()
        with col2:
            st.error("🧩 **Asset Matrix**")
            st.caption("Yatırım bloklarını yerleştir.")
            st.button("Yakında...", disabled=True)

    with tab4:
        st.subheader("🏆 Liderlik Tablosu")
        data = [{"Öğrenci": k.split('_')[1], "Puan": v} for k, v in st.session_state.db.items()]
        df = pd.DataFrame(data).sort_values("Puan", ascending=False).reset_index(drop=True)
        df.index += 1
        st.dataframe(df, use_container_width=True)

# ==============================================================================
# EKRAN 3: OYUN - FİNANS İMPARATORU (NATIVE PYTHON)
# ==============================================================================
elif st.session_state.active_screen == "GAME_FINANCE":
    user_key = st.session_state.user_info['key']
    
    c1, c2 = st.columns([3, 1])
    with c1: st.header("💰 Finans İmparatoru")
    with c2: 
        if st.button("🔙 Menüye Dön"):
            st.session_state.active_screen = "TABS"
            st.rerun()
            
    # Basit Tıklama Oyunu Mantığı
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("### 🍋 Limonata Standı")
        st.caption("Gelir: 50 ₺ / Tık")
        if st.button("SATIŞ YAP 🍋", use_container_width=True):
            add_score(user_key, 50)
            st.toast("+50 ₺ Kazanıldı!")
            st.rerun()
            
    with col2:
        st.markdown("### 🌭 Sosisli Arabası")
        st.caption("Maliyet: 1000 ₺ | Gelir: 250 ₺")
        if st.button("YATIRIM YAP (-1000)", use_container_width=True):
            if get_score(user_key) >= 1000:
                add_score(user_key, -1000 + 250) # Yatırım düş, ilk geliri ver
                st.toast("Yatırım Yapıldı! +250 ₺")
                st.rerun()
            else:
                st.error("Yetersiz Bakiye!")

    with col3:
        st.markdown(f"""
            <div style="background:#6c5ce7; color:white; padding:20px; border-radius:10px; text-align:center;">
                <h3>KASA</h3>
                <h1>{get_score(user_key)} ₺</h1>
            </div>
        """, unsafe_allow_html=True)

# ==============================================================================
# EKRAN 4: SORU ÇÖZÜM (TYT & MESLEK)
# ==============================================================================
elif st.session_state.active_screen in ["QUIZ_TYT", "QUIZ_MESLEK"]:
    tur = "TYT" if st.session_state.active_screen == "QUIZ_TYT" else "MESLEK"
    sorular = SORULAR[tur]
    idx = st.session_state.quiz_idx
    user_key = st.session_state.user_info['key']
    
    # Üst Bar
    c1, c2 = st.columns([3, 1])
    with c1: st.subheader(f"📝 {tur} Testi - Soru {idx + 1}/{len(sorular)}")
    with c2: 
        if st.button("Testi Bitir"):
            st.session_state.active_screen = "TABS"
            st.rerun()
            
    if idx < len(sorular):
        q_data = sorular[idx]
        st.markdown(f"**{q_data['q']}**")
        
        cols = st.columns(len(q_data['opts']))
        for i, opt in enumerate(q_data['opts']):
            if cols[i].button(opt, use_container_width=True):
                if opt == q_data['a']:
                    st.success("DOĞRU! 🎉 +100 Puan")
                    add_score(user_key, 100)
                    time.sleep(1)
                else:
                    st.error(f"YANLIŞ! Doğru cevap: {q_data['a']}")
                    time.sleep(2)
                
                st.session_state.quiz_idx += 1
                st.rerun()
    else:
        st.success("Test Bitti! 🎈")
        if st.button("Sonuçları Kaydet ve Çık"):
            st.session_state.active_screen = "TABS"
            st.rerun()
