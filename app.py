import streamlit as st
import streamlit.components.v1 as components
import json
import os

# 1. SAYFA AYARLARI
st.set_page_config(
    page_title="Finans İmparatoru & Kampüs",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. CSS STİLLERİ (Görünüm)
st.markdown("""
<style>
    [data-testid="stSidebar"] { background-color: #0f172a; border-right: 1px solid #334155; }
    .stApp { background-color: #0a0a12; color: white; }
    h1, h2, h3 { color: #f1c40f !important; font-family: 'Segoe UI', sans-serif; }
    .stButton>button { width: 100%; border-radius: 8px; font-weight: bold; background: #1e293b; color: white; border: 1px solid #334155; }
    .stButton>button:hover { border-color: #f1c40f; color: #f1c40f; }
    .info-box { padding: 15px; background: #16213e; border-radius: 10px; border-left: 5px solid #f1c40f; margin-bottom: 20px; }
</style>
""", unsafe_allow_html=True)

# 3. OTURUM VE PUAN YÖNETİMİ (Session State)
if 'balance' not in st.session_state: st.session_state.balance = 0
if 'bank' not in st.session_state: st.session_state.bank = 0
if 'inventory' not in st.session_state: st.session_state.inventory = []

# 4. YARDIMCI FONKSİYON: HTML OYUN YÜKLEME
def load_html_game(filename, height=700):
    """HTML dosyasını okur ve ekrana basar. Dosya yoksa uyarı verir."""
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as f:
            html_content = f.read()
            # LifeSim verisi için özel durum: JSON verisini enjekte etme yeri
            if filename == "game_lifesim.html" and os.path.exists("lifesim_data.json"):
                with open("lifesim_data.json", 'r', encoding='utf-8') as jf:
                    json_data = jf.read()
                    # HTML içindeki placeholder'ı gerçek veriyle değiştir
                    html_content = html_content.replace("// PYTHON_DATA_HERE", f"let scenarios = {json_data};")
            
            components.html(html_content, height=height, scrolling=False)
    else:
        st.warning(f"⚠️ {filename} dosyası henüz yüklenmedi. Lütfen GitHub'a yükleyin.")

# 5. YAN MENÜ (SIDEBAR)
with st.sidebar:
    st.title("🏛️ FİNANS KAMPÜSÜ")
    st.markdown("---")
    
    menu = st.radio("MENÜ", [
        "👤 Profil",
        "🎓 Soru Çözüm (TYT/Meslek)",
        "💼 LifeSim (Kariyer)",
        "📈 Finans İmparatoru",
        "🧩 Asset Matrix (Blok)",
        "🏆 Skor Tablosu"
    ])
    
    st.markdown("---")
    # Mini Cüzdan Görünümü
    c1, c2 = st.columns(2)
    c1.metric("Cüzdan", f"{st.session_state.balance} ₺")
    c2.metric("Banka", f"{st.session_state.bank} ₺")

# 6. SAYFA İÇERİKLERİ

# --- PROFİL ---
if menu == "👤 Profil":
    st.header("👤 Oyuncu Profili")
    st.info("Hoş geldin, Yatırımcı Adayı.")
    st.write(f"Toplam Net Varlık: **{st.session_state.balance + st.session_state.bank} ₺**")

# --- SORU ÇÖZÜM ---
elif menu == "🎓 Soru Çözüm (TYT/Meslek)":
    st.header("🎓 Soru Çözüm Merkezi")
    st.write("Burada TYT ve Meslek dersleri testleri olacak.")
    # İleride buraya soru kodları eklenecek

# --- LIFESIM ---
elif menu == "💼 LifeSim (Kariyer)":
    st.header("💼 LifeSim: Kariyer Yönetimi")
    # game_lifesim.html dosyasını çağırır
    load_html_game("game_lifesim.html", height=800)

# --- FİNANS İMPARATORU ---
elif menu == "📈 Finans İmparatoru":
    st.header("📈 Finans İmparatoru (Pasif Gelir)")
    # game_finance.html dosyasını çağırır
    load_html_game("game_finance.html", height=650)

# --- ASSET MATRIX ---
elif menu == "🧩 Asset Matrix (Blok)":
    st.header("🧩 Asset Matrix: Blok Oyunu")
    # game_matrix.html dosyasını çağırır
    load_html_game("game_matrix.html", height=700)

# --- SKOR TABLOSU ---
elif menu == "🏆 Skor Tablosu":
    st.header("🏆 Liderlik Tablosu")
    st.table([
        {"Sıra": 1, "Oyuncu": "Elon M.", "Puan": "999M"},
        {"Sıra": 2, "Oyuncu": "Jeff B.", "Puan": "500M"},
        {"Sıra": 3, "Oyuncu": "SİZ", "Puan": f"{st.session_state.balance}"}
    ])
