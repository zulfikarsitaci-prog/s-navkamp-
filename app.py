import streamlit as st
import pandas as pd

# 1. SAYFA AYARLARI
st.set_page_config(
    page_title="Finans Kampüsü",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="collapsed" # Yan menüyü kapalı başlatıyoruz
)

# 2. CSS TASARIMI (Üst Menü ve Görünüm İçin)
st.markdown("""
<style>
    /* Yan Menüyü Tamamen Gizle (İsteğe bağlı, üst menü kullanacağımız için) */
    [data-testid="stSidebar"] { display: none; }
    
    /* Genel Arka Plan */
    .stApp { background-color: #0a0a12; color: white; }
    
    /* Giriş Kutusu Stili */
    .login-container {
        background-color: #16213e;
        padding: 40px;
        border-radius: 15px;
        border: 2px solid #f1c40f;
        text-align: center;
        max-width: 500px;
        margin: 100px auto;
    }
    
    /* Tab (Sekme) Stilleri */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        background-color: #16213e;
        padding: 10px;
        border-radius: 10px;
        border-bottom: 2px solid #f1c40f;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        background-color: transparent;
        color: #aaa;
        font-weight: bold;
        font-size: 16px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #f1c40f !important;
        color: #000 !important;
        border-radius: 5px;
    }
    
    /* Skor Tablosu Stili */
    .score-card {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        padding: 20px;
        border-radius: 10px;
        border: 1px solid #334155;
        text-align: center;
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

# 3. OTURUM YÖNETİMİ (Session State)
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'user_name' not in st.session_state: st.session_state.user_name = ""
if 'user_no' not in st.session_state: st.session_state.user_no = ""
if 'balance' not in st.session_state: st.session_state.balance = 0

# ==========================================
# EKRAN 1: GİRİŞ EKRANI
# ==========================================
if not st.session_state.logged_in:
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        # Basit bir kutu görünümü için container
        with st.container(border=True):
            st.markdown("<h1 style='text-align:center; color:#f1c40f;'>🏛️ FİNANS KAMPÜSÜ</h1>", unsafe_allow_html=True)
            st.markdown("<p style='text-align:center; color:#aaa;'>Öğrenci Giriş Portalı</p>", unsafe_allow_html=True)
            
            with st.form("login_form"):
                ad_soyad = st.text_input("Ad Soyad")
                okul_no = st.text_input("Okul Numarası")
                
                submitted = st.form_submit_button("SİSTEME GİRİŞ YAP", use_container_width=True, type="primary")
                
                if submitted:
                    if ad_soyad and okul_no:
                        st.session_state.user_name = ad_soyad
                        st.session_state.user_no = okul_no
                        st.session_state.logged_in = True
                        st.rerun() # Sayfayı yenile ve içeri al
                    else:
                        st.error("Lütfen bilgileri eksiksiz giriniz.")

# ==========================================
# EKRAN 2: ANA MENÜ VE İÇERİK
# ==========================================
else:
    # Üst Bilgi Çubuğu (Kullanıcı Adı ve Bakiye)
    col_user, col_empty, col_bal = st.columns([2, 4, 2])
    with col_user:
        st.markdown(f"👤 **{st.session_state.user_name}** ({st.session_state.user_no})")
    with col_bal:
        st.markdown(f"💰 Bakiye: **{st.session_state.balance} ₺**")
    
    st.markdown("---")

    # ÜST MENÜ (TABS)
    tab_profil, tab_soru, tab_eglence, tab_lifesim, tab_premium = st.tabs([
        "👤 PROFİL", 
        "📚 SORU ÇÖZÜM", 
        "🎮 EĞLENCE", 
        "💼 LIFESIM", 
        "💎 PREMIUM"
    ])

    # --- 1. PROFİL & SKOR TABELASI ---
    with tab_profil:
        st.header("🏆 Skor Tabelası")
        
        # Örnek Skor Verisi
        data = {
            "Sıra": [1, 2, 3, 4, 5],
            "Öğrenci Adı": ["Ahmet Y.", "Ayşe K.", "Mehmet T.", st.session_state.user_name, "Zeynep B."],
            "Toplam Varlık": ["1.500.000 ₺", "1.200.000 ₺", "900.000 ₺", f"{st.session_state.balance} ₺", "50.000 ₺"]
        }
        df = pd.DataFrame(data)
        st.table(df)
        
        if st.button("Çıkış Yap", type="secondary"):
            st.session_state.logged_in = False
            st.rerun()

    # --- 2. SORU ÇÖZÜM ---
    with tab_soru:
        st.header("📚 TYT ve Meslek Soruları")
        st.info("Buraya TYT ve Mesleki soru modülleri gelecek.")
        # İleride buraya soru kodlarını ekleyeceğiz

    # --- 3. EĞLENCE (Finans & Matrix) ---
    with tab_eglence:
        st.header("🎮 Oyun Bölümü")
        st.info("Buraya Finans İmparatoru ve Asset Matrix oyunları gelecek.")
        # İleride buraya oyun HTML'lerini gömeceğiz

    # --- 4. LIFESIM ---
    with tab_lifesim:
        st.header("💼 LifeSim Kariyer Simülasyonu")
        st.info("Buraya LifeSim simülasyonu gelecek.")
        # İleride buraya LifeSim HTML'ini gömeceğiz

    # --- 5. PREMIUM ---
    with tab_premium:
        st.header("💎 Premium Üyelik")
        st.warning("Bu alan yapım aşamasındadır.")
