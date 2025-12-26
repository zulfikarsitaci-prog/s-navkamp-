import streamlit as st
import time
import pandas as pd

# --- 1. AYARLAR & CSS TASARIMI ---
st.set_page_config(page_title="Finans Kampüsü", page_icon="🎓", layout="wide")

st.markdown("""
    <style>
    /* Genel Sayfa Stili */
    .stApp { background-color: #f8f9fa; }
    
    /* Sekme (Tab) Tasarımı */
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] {
        height: 50px; white-space: pre-wrap; background-color: #fff; border-radius: 10px 10px 0 0;
        box-shadow: 0 -2px 5px rgba(0,0,0,0.05); border: none; font-weight: 600;
    }
    .stTabs [aria-selected="true"] { background-color: #6c5ce7; color: white !important; }
    
    /* Kart Tasarımları */
    .info-card { background: white; padding: 20px; border-radius: 15px; box-shadow: 0 4px 10px rgba(0,0,0,0.05); margin-bottom: 20px; text-align: center; }
    .score-title { color: #888; font-size: 14px; text-transform: uppercase; letter-spacing: 1px; }
    .score-val { color: #6c5ce7; font-size: 42px; font-weight: 900; }
    
    /* Butonlar */
    div.stButton > button { border-radius: 12px; height: 50px; font-weight: bold; border: none; transition: 0.3s; }
    div.stButton > button:hover { transform: scale(1.02); }
    </style>
""", unsafe_allow_html=True)

# --- 2. VERİTABANI SİMÜLASYONU (Şimdilik Yerel) ---
# Gerçekte burası Google Sheets'e bağlanacak.
if 'db' not in st.session_state:
    st.session_state.db = {
        "101_Ahmet Yılmaz": 1250, # OkulNo_AdSoyad formatı benzersizlik sağlar
        "102_Ayşe Demir": 3400
    }

def get_player_score(user_key):
    """Veritabanından puanı çeker"""
    return st.session_state.db.get(user_key, 0)

def update_score(user_key, points):
    """Puanı artırır ve kaydeder (AUTO-SAVE)"""
    current = st.session_state.db.get(user_key, 0)
    st.session_state.db[user_key] = current + points
    return st.session_state.db[user_key]

# --- 3. OTURUM YÖNETİMİ ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'user_info' not in st.session_state: st.session_state.user_info = {} # {"name": "", "no": "", "key": ""}

# --- EKRAN: GİRİŞ YAP ---
if not st.session_state.logged_in:
    c1, c2, c3 = st.columns([1, 1, 1])
    with c2:
        st.markdown("<div style='text-align:center; margin-top:50px;'><h1 style='color:#6c5ce7;'>🎓 Finans Kampüsü</h1><p>Öğrenci Giriş Paneli</p></div>", unsafe_allow_html=True)
        with st.form("login_form"):
            ad = st.text_input("Adınız Soyadınız")
            no = st.text_input("Okul Numaranız")
            submit = st.form_submit_button("GİRİŞ YAP", type="primary")
            
            if submit:
                if ad and no:
                    unique_key = f"{no}_{ad.strip()}" # Benzersiz Anahtar
                    st.session_state.user_info = {"name": ad, "no": no, "key": unique_key}
                    st.session_state.logged_in = True
                    
                    # Eğer yeni kullanıcıysa veritabanına 0 puanla ekle
                    if unique_key not in st.session_state.db:
                        st.session_state.db[unique_key] = 0
                        
                    st.rerun()
                else:
                    st.error("Lütfen bilgileri eksiksiz girin.")

# --- EKRAN: ANA PANEL (SEKMELİ YAPI) ---
else:
    # Kullanıcı verilerini çek
    user = st.session_state.user_info
    current_score = get_player_score(user['key'])
    
    # Üst Menü (Profil Özeti - Küçük)
    with st.sidebar:
        st.write(f"👤 **{user['name']}**")
        st.write(f"🏫 No: {user['no']}")
        st.write(f"🏆 Puan: {current_score}")
        if st.button("Çıkış Yap"):
            st.session_state.logged_in = False
            st.rerun()

    # --- SEKMELER (TABS) ---
    tab1, tab2, tab3, tab4 = st.tabs(["🏠 Profil", "📚 Dersler", "🎮 Oyunlar", "🏆 Sıralama"])

    # 1. TAB: PROFİL (ANA EKRAN)
    with tab1:
        st.markdown(f"### Hoşgeldin, {user['name']} 👋")
        
        # Puan Kartı
        st.markdown(f"""
            <div class="info-card">
                <div class="score-title">GÜNCEL VARLIK</div>
                <div class="score-val">{current_score} ₺</div>
                <p style="color:#999; font-size:12px;">Tüm oyunlardan ve testlerden kazandığın toplam puan.</p>
            </div>
        """, unsafe_allow_html=True)
        
        st.info("💡 **İpucu:** Puanların yaptığın her işlemde otomatik kaydedilir.")

    # 2. TAB: DERSLER (TYT & MESLEK)
    with tab2:
        st.subheader("📚 Soru Çözüm Merkezi")
        col_a, col_b = st.columns(2)
        
        with col_a:
            with st.container(border=True):
                st.markdown("### 📘 TYT Kampı")
                st.caption("Matematik, Türkçe, Sosyal")
                if st.button("Başla (TYT)", use_container_width=True):
                    # Buraya TYT modülünü bağlayacağız
                    st.toast("TYT Modülü Yükleniyor...")
        
        with col_b:
            with st.container(border=True):
                st.markdown("### 💼 Meslek Dersleri")
                st.caption("Muhasebe, Finans, Ekonomi")
                if st.button("Başla (Meslek)", use_container_width=True):
                    # Buraya Meslek modülünü bağlayacağız
                    st.toast("Meslek Modülü Yükleniyor...")
                    
        # TEST İÇİN GEÇİCİ SORU ALANI (Auto-Save Testi)
        st.divider()
        st.write("📝 **Hızlı Soru (Test):** Aşağıdakilerden hangisi bir varlıktır?")
        if st.button("A) Kasa Hesabı"):
            update_score(user['key'], 10) # 10 Puan ekle ve kaydet
            st.success("Doğru! +10 Puan eklendi.")
            time.sleep(1)
            st.rerun()
        st.button("B) Borçlar")

    # 3. TAB: OYUNLAR (FİNANS & MATRIX)
    with tab3:
        st.subheader("🎮 Oyun Alanı")
        
        col_x, col_y = st.columns(2)
        
        with col_x:
            with st.container(border=True):
                st.markdown("### 💰 Finans İmparatoru")
                st.caption("Şirketini kur, büyüt, yönet.")
                if st.button("Oyna (Finans)", type="primary", use_container_width=True):
                    # Buraya Finans oyununu bağlayacağız
                    st.toast("Oyun Başlatılıyor...")
        
        with col_y:
            with st.container(border=True):
                st.markdown("### 🧩 Asset Matrix")
                st.caption("Yatırım bloklarını yerleştir.")
                if st.button("Oyna (Matrix)", use_container_width=True):
                    # Buraya Matrix oyununu bağlayacağız
                    st.toast("Matrix Açılıyor...")

    # 4. TAB: SIRALAMA
    with tab4:
        st.subheader("🏆 Liderlik Tablosu")
        # Veritabanını DataFrame'e çevirip gösterelim
        leader_data = [{"Öğrenci": k.split('_')[1], "Puan": v} for k, v in st.session_state.db.items()]
        df = pd.DataFrame(leader_data).sort_values(by="Puan", ascending=False).reset_index(drop=True)
        df.index += 1 # Sıralama 1'den başlasın
        st.dataframe(df, use_container_width=True)
