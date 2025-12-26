import streamlit as st
import time
import pandas as pd
from datetime import datetime

# --- 1. AYARLAR & TASARIM ---
st.set_page_config(page_title="Finans Kampüsü", page_icon="🎓", layout="centered")

# Renk Paleti ve CSS
st.markdown("""
    <style>
    .stApp { background-color: #f0f2f6; }
    .main-header { 
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
        padding: 30px; border-radius: 20px; color: white; text-align: center; 
        margin-bottom: 30px; box-shadow: 0 10px 20px rgba(0,0,0,0.1);
    }
    .score-card {
        background: white; padding: 20px; border-radius: 15px; 
        text-align: center; border-left: 5px solid #764ba2;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05); margin-bottom: 20px;
    }
    .big-score { font-size: 32px; font-weight: bold; color: #764ba2; }
    .game-btn { 
        width: 100%; padding: 20px; border-radius: 15px; border: none; 
        background: white; color: #444; font-weight: bold; font-size: 18px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1); transition: 0.3s; margin-bottom: 15px;
    }
    .game-btn:hover { transform: translateY(-5px); background: #764ba2; color: white; }
    </style>
""", unsafe_allow_html=True)

# --- 2. VERİTABANI SİMÜLASYONU (Şimdilik Yerel) ---
# Gerçek sistemde burası Google Sheets API olacak.
if 'db' not in st.session_state:
    st.session_state.db = {
        "Ahmet Yılmaz": 1250,
        "Ayşe Demir": 3400,
        "Mehmet Kaya": 0
    }

def get_player_data(username):
    """Veritabanından öğrenciyi bulur veya oluşturur"""
    # Burada Google Sheets'e bağlanacağız
    name = username.strip().title()
    if name in st.session_state.db:
        return st.session_state.db[name]
    else:
        # Yeni kayıt oluştur
        st.session_state.db[name] = 0
        return 0

def update_player_score(username, points):
    """Puanı veritabanına yazar (OTO-KAYIT)"""
    name = username.strip().title()
    current = st.session_state.db.get(name, 0)
    new_score = current + points
    st.session_state.db[name] = new_score
    # Burada Google Sheets'e update komutu gidecek
    return new_score

# --- 3. UYGULAMA AKIŞI (SESSION STATE) ---
if 'user' not in st.session_state: st.session_state.user = None
if 'score' not in st.session_state: st.session_state.score = 0
if 'page' not in st.session_state: st.session_state.page = 'login'

# --- EKRAN 1: GİRİŞ (LOGIN) ---
if st.session_state.page == 'login':
    st.markdown("<div class='main-header'><h1>🎓 Finans Kampüsü</h1><p>Giriş Yap ve Puanlarını Koru</p></div>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        with st.form("login_form"):
            ad = st.text_input("Adın Soyadın:", placeholder="Örn: Ali Veli")
            # İstersen buraya numara veya basit bir şifre de ekleriz
            # sifre = st.text_input("Okul No:", type="password") 
            
            submit = st.form_submit_button("GİRİŞ YAP 🚀")
            
            if submit:
                if len(ad) > 3:
                    st.session_state.user = ad
                    # Veritabanından puanı çek
                    puan = get_player_data(ad)
                    st.session_state.score = puan
                    st.session_state.page = 'dashboard'
                    st.rerun()
                else:
                    st.error("Lütfen geçerli bir isim gir.")

# --- EKRAN 2: ÖĞRENCİ PANELİ (DASHBOARD) ---
elif st.session_state.page == 'dashboard':
    # Üst Bilgi
    st.markdown(f"""
        <div class='main-header'>
            <h2>Merhaba, {st.session_state.user} 👋</h2>
        </div>
    """, unsafe_allow_html=True)
    
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"""
            <div class='score-card'>
                <p>🏆 TOPLAM PUANIN</p>
                <div class='big-score'>{st.session_state.score}</div>
            </div>
        """, unsafe_allow_html=True)
    with c2:
        st.info("💡 **Bilgi:** Puanların her işlemden sonra otomatik olarak sisteme kaydedilir. Kaydet butonuna basmana gerek yoktur.")

    st.markdown("### 🎮 Oyunlar ve Dersler")
    
    col_a, col_b = st.columns(2)
    
    with col_a:
        if st.button("📘 TYT Kampı", key="go_tyt", use_container_width=True):
            st.session_state.page = 'tyt'
            st.rerun()
            
    with col_b:
        if st.button("💰 Finans İmparatoru", key="go_game", use_container_width=True):
            st.session_state.page = 'game'
            st.rerun()
            
    if st.button("🚪 Çıkış Yap"):
        st.session_state.user = None
        st.session_state.page = 'login'
        st.rerun()

# --- EKRAN 3: ÖRNEK OYUN (AUTO-SAVE TESTİ) ---
elif st.session_state.page == 'game':
    st.header("💰 Finans İmparatoru")
    st.write(f"Mevcut Puan: **{st.session_state.score}**")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🍋 Limonata Sat (+50 Puan)"):
            # --- İŞTE SİHİR BURADA ---
            # Öğrenci butona basıyor, puan artıyor ve ARKA PLANDA KAYDEDİLİYOR
            update_player_score(st.session_state.user, 50)
            st.session_state.score += 50
            st.toast("50 Puan Eklendi ve Kaydedildi! ✅")
            time.sleep(0.5)
            st.rerun()
            
    with col2:
        if st.button("🔙 Panele Dön"):
            st.session_state.page = 'dashboard'
            st.rerun()

# --- EKRAN 4: TYT (SADECE GÖRSEL) ---
elif st.session_state.page == 'tyt':
    st.header("📘 TYT Çalışma")
    st.write("Burası soru çözüm ekranı olacak.")
    if st.button("🔙 Panele Dön"):
        st.session_state.page = 'dashboard'
        st.rerun()
