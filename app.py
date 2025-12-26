import streamlit as st
import pandas as pd

# 1. SAYFA AYARLARI
st.set_page_config(
    page_title="Bağarası ÇPAL - Finans Ekosistemi",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="collapsed" # Sidebar kapalı başlar
)

# 2. CSS TASARIM (AÇIK TEMA, CINZEL FONT, MENÜ DÜZENİ)
st.markdown("""
<style>
    /* Font İçe Aktarma */
    @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;700;900&family=Poppins:wght@300;400;600&display=swap');

    /* Genel Sayfa Yapısı (Açık Renk) */
    .stApp {
        background-color: #f8f9fa; /* Çok açık gri/beyaz */
        color: #2c3e50; /* Koyu lacivert/siyah yazı */
        font-family: 'Poppins', sans-serif;
    }

    /* Sidebar'ı Tamamen Gizle (İstenirse) */
    [data-testid="stSidebar"] { display: none; }
    
    /* Başlıklar ve Menüler İçin Cinzel Fontu */
    h1, h2, h3, .stTabs button {
        font-family: 'Cinzel', serif !important;
        color: #2c3e50 !important;
    }

    /* Üst Menü (Tabs) Tasarımı */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        background-color: #ffffff;
        padding: 10px 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        border-bottom: 2px solid #D84315;
    }

    .stTabs [data-baseweb="tab"] {
        height: 50px;
        border: none;
        font-size: 16px;
        font-weight: 700;
        color: #555;
        background-color: transparent;
    }

    .stTabs [aria-selected="true"] {
        color: #D84315 !important; /* Seçili sekme rengi */
        border-bottom: 3px solid #D84315 !important;
    }

    /* Buton Tasarımları */
    .stButton>button {
        background-color: #2c3e50;
        color: white;
        border-radius: 8px;
        border: none;
        padding: 10px 20px;
        font-weight: bold;
        transition: 0.3s;
    }
    .stButton>button:hover {
        background-color: #D84315; /* Hover rengi */
        color: white;
    }

    /* Giriş Ekranı Kartı */
    .login-container {
        background: white;
        padding: 40px;
        border-radius: 20px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.1);
        text-align: center;
        border-top: 5px solid #D84315;
    }
    
    /* Skor Tablosu */
    .dataframe {
        font-family: 'Poppins', sans-serif;
        font-size: 14px;
        width: 100%;
    }
</style>
""", unsafe_allow_html=True)

# 3. OTURUM YÖNETİMİ
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'user_name' not in st.session_state: st.session_state.user_name = ""
if 'user_no' not in st.session_state: st.session_state.user_no = ""

# --- EKRAN 1: GİRİŞ EKRANI ---
if not st.session_state.logged_in:
    # Sayfayı ortalamak için kolonlar
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        # İSTEDİĞİN GİRİŞ HTML'İ BURADA
        st.markdown("""
        <div class="login-container">
            <h1 style="font-size: 2.5rem; margin-bottom: 0;">🎓 Bağarası ÇPAL</h1>
            <h2 style="color: #555 !important; margin-top: 0;">Finans & Eğitim Ekosistemi</h2>
            <hr style="border: 1px solid #eee; margin: 20px 0;">
            <p style="font-size:18px; font-weight:bold; color:#D84315;">
                Muhasebe ve Finansman Alanı Dijital Dönüşüm Projesi
            </p>
            <br>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        with st.form("login_form"):
            ad = st.text_input("Adı Soyadı", placeholder="Örn: Ahmet Yılmaz")
            no = st.text_input("Okul Numarası", placeholder="Örn: 1453")
            
            submitted = st.form_submit_button("SİSTEME GİRİŞ YAP")
            
            if submitted:
                if ad and no:
                    st.session_state.logged_in = True
                    st.session_state.user_name = ad
                    st.session_state.user_no = no
                    st.rerun()
                else:
                    st.error("Lütfen tüm alanları doldurunuz.")

# --- EKRAN 2: ANA MENÜ VE İÇERİK ---
else:
    # Üst Bilgi Çubuğu (Basit karşılama)
    st.markdown(f"""
    <div style="display:flex; justify-content:space-between; align-items:center; padding:10px 20px; background:white; border-radius:10px; margin-bottom:20px; box-shadow: 0 2px 5px rgba(0,0,0,0.05);">
        <div style="font-family:'Cinzel'; font-weight:bold; font-size:18px; color:#2c3e50;">
            🎓 BAĞARASI ÇPAL
        </div>
        <div style="font-family:'Poppins'; font-size:14px; color:#555;">
            Hoşgeldin, <b>{st.session_state.user_name}</b> ({st.session_state.user_no})
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ANA MENÜLER (ÜSTTE - TABS)
    tab_ana, tab_profil, tab_soru, tab_eglence, tab_lifesim, tab_premium = st.tabs([
        "🏆 ANA EKRAN (SKOR)", 
        "👤 PROFİL", 
        "📚 SORU ÇÖZÜM", 
        "🎮 EĞLENCE", 
        "💼 LIFESIM", 
        "💎 PREMIUM"
    ])

    # --- 1. ANA EKRAN (SKOR TABLOSU) ---
    with tab_ana:
        st.header("🏆 Liderlik Tablosu")
        st.info("Okul genelindeki sıralama aşağıdadır.")
        
        # Örnek Veri (Daha sonra veritabanından gelecek)
        data = {
            'Sıra': [1, 2, 3, 4, 5],
            'Ad Soyad': ['Ayşe Y.', 'Mehmet K.', st.session_state.user_name, 'Fatma D.', 'Ali V.'],
            'Okul No': [102, 305, st.session_state.user_no, 440, 120],
            'Toplam Puan': [15000, 12500, 0, 9000, 8500]
        }
        df = pd.DataFrame(data)
        st.table(df)

    # --- 2. PROFİL ---
    with tab_profil:
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### Öğrenci Kartı")
            st.write(f"**Ad Soyad:** {st.session_state.user_name}")
            st.write(f"**Okul No:** {st.session_state.user_no}")
            st.write("**Sınıf:** 11/A (Muhasebe)")
        with col2:
            st.markdown("### Varlık Durumu")
            st.metric("Toplam Cüzdan", "0 ₺")
            st.metric("Banka Hesabı", "0 ₺")
        
        if st.button("Çıkış Yap"):
            st.session_state.logged_in = False
            st.rerun()

    # --- 3. SORU ÇÖZÜM ---
    with tab_soru:
        st.header("📚 Soru Çözüm Merkezi")
        st.write("TYT ve Meslek dersleri testleri burada yer alacak.")
        # Buraya soru modülleri gelecek

    # --- 4. EĞLENCE ---
    with tab_eglence:
        st.header("🎮 Eğlence Alanı")
        st.write("Burada Finans İmparatoru ve Asset Matrix oyunları olacak.")
        # Buraya finans ve blok oyunu gelecek

    # --- 5. LIFESIM ---
    with tab_lifesim:
        st.header("💼 LifeSim: Kariyer Simülasyonu")
        st.write("Gerçek hayat senaryoları burada çalışacak.")
        # Buraya LifeSim HTML gelecek

    # --- 6. PREMIUM ---
    with tab_premium:
        st.header("💎 Premium Özellikler")
        st.warning("Bu alan şu an yapım aşamasındadır.")
        st.markdown("""
        * 🚀 2x Puan Kazanımı
        * 🎨 Özel Temalar
        * 📈 Gelişmiş İstatistikler
        """)
