import streamlit as st
import streamlit.components.v1 as components
import json
import os

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Finans İmparatoru", layout="wide")

# --- CSS İLE GÖRÜNÜMÜ GÜZELLEŞTİR ---
st.markdown("""
<style>
    [data-testid="stSidebar"] { background-color: #0f172a; }
    .stButton>button { width: 100%; border-radius: 8px; font-weight: bold; }
    h1, h2, h3 { color: #fff; }
    .stat-box { background: #1e293b; padding: 15px; border-radius: 10px; border: 1px solid #334155; text-align: center; }
    .stat-val { font-size: 24px; font-weight: bold; color: #34d399; }
</style>
""", unsafe_allow_html=True)

# --- VERİ YÜKLEME FONKSİYONU ---
def load_data():
    if not os.path.exists('lifesim_data.json'):
        return []
    with open('lifesim_data.json', 'r', encoding='utf-8') as f:
        return json.load(f)

scenarios = load_data()

# --- SESSION STATE (GEÇİCİ HAFIZA) ---
if 'balance' not in st.session_state: st.session_state.balance = 0
if 'bank' not in st.session_state: st.session_state.bank = 0

# --- YAN MENÜ (SIDEBAR) ---
with st.sidebar:
    st.title("🏛️ FİNANS İMPARATORU")
    st.markdown("---")
    
    # Menü Seçenekleri
    menu = st.radio("MENÜ", [
        "👤 Profil", 
        "🎓 Soru Çözüm Merkezi", 
        "💼 LifeSim (Kariyer)", 
        "🎮 Eğlence (Oyunlar)", 
        "💎 Premium", 
        "🏆 Skor Tablosu"
    ])
    
    st.markdown("---")
    st.write(f"💰 **Cüzdan:** {st.session_state.balance} TL")
    st.write(f"🏦 **Banka:** {st.session_state.bank} TL")

# ================= MENÜ İÇERİKLERİ =================

# --- 1. PROFIL SAYFASI ---
if menu == "👤 Profil":
    st.header("👤 Oyuncu Profili")
    col1, col2 = st.columns(2)
    with col1:
        st.info(f"**Kullanıcı Adı:** Yatırımcı Adayı")
        st.info(f"**Unvan:** Başlangıç Seviyesi")
    with col2:
        toplam_varlik = st.session_state.balance + st.session_state.bank
        st.success(f"**Toplam Varlık:** {toplam_varlik} TL")
        st.warning(f"**Çözülen Soru:** 0")

# --- 2. SORU ÇÖZÜM MERKEZİ (TYT-MESLEK) ---
elif menu == "🎓 Soru Çözüm Merkezi":
    st.header("🎓 TYT & Meslek Senaryoları")
    
    if not scenarios:
        st.error("lifesim_data.json dosyası bulunamadı! Lütfen GitHub'a yükleyin.")
    else:
        # Senaryo Seçimi
        secilen_baslik = st.selectbox("Bir Görev Seçin:", [s['title'] for s in scenarios])
        # Seçilen senaryo verisini bul
        secilen_senaryo = next(s for s in scenarios if s['title'] == secilen_baslik)
        
        # İçerik Gösterimi
        with st.container():
            st.subheader(f"📌 {secilen_senaryo['category']}")
            st.write(secilen_senaryo['text'])
            st.markdown(f"**Ödül:** :green[{secilen_senaryo.get('money_reward', 1000)} TL]")
            
            # Veri Parametreleri (Varsa)
            if 'data' in secilen_senaryo:
                st.code("\n".join(secilen_senaryo['data']), language="yaml")
            
            # Cevap Alanı
            cevap = st.text_area("Çözüm stratejinizi yazın:", height=100)
            
            if st.button("Analiz Et ⚡"):
                puan = 0
                keywords = secilen_senaryo.get('keywords', {})
                
                # Basit kelime eşleştirme analizi
                for k in keywords:
                    if k in cevap.lower(): puan += 1
                
                # Başarı kriteri: Anahtar kelimelerin yarısını bilmek
                basari = len(keywords) == 0 or (puan / len(keywords) >= 0.5)
                
                if basari:
                    odul = secilen_senaryo.get('money_reward', 1000)
                    st.session_state.balance += odul
                    st.balloons()
                    st.success(f"✅ BAŞARILI! Analiziniz doğru. **+{odul} TL** kazandınız.")
                    st.info(f"💡 **Hap Bilgi:** {secilen_senaryo['hapBilgi']}")
                else:
                    st.warning("⚠️ Eksikler var. Biraz daha detaylandır.")

# --- 3. LIFESIM (BANKA & KARİYER) ---
elif menu == "💼 LifeSim (Kariyer)":
    st.header("💼 Kariyer ve Varlık Yönetimi")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### 🏦 Banka İşlemleri")
        miktar = st.number_input("Tutar Girin:", min_value=0, step=100)
        
        c1, c2 = st.columns(2)
        if c1.button("Para Yatır (Faiz Başlar)"):
            if miktar <= st.session_state.balance:
                st.session_state.balance -= miktar
                st.session_state.bank += miktar
                st.success(f"{miktar} TL Bankaya Yatırıldı!")
                st.rerun()
            else:
                st.error("Yetersiz Nakit Bakiye")
                
        if c2.button("Para Çek"):
            if miktar <= st.session_state.bank:
                st.session_state.bank -= miktar
                st.session_state.balance += miktar
                st.success(f"{miktar} TL Çekildi!")
                st.rerun()
            else:
                st.error("Yetersiz Banka Bakiyesi")
                
    with col2:
        st.markdown("### 📊 Varlık Özeti")
        st.write(f"Cüzdan: {st.session_state.balance} TL")
        st.write(f"Banka: {st.session_state.bank} TL")
        st.metric(label="Net Varlık", value=f"{st.session_state.balance + st.session_state.bank} TL")

# --- 4. EĞLENCE (BLOK OYUNU) ---
elif menu == "🎮 Eğlence (Oyunlar)":
    st.header("🎮 Blok Simülasyonu")
    st.caption("Blokları yerleştir, satırları sil ve para kazan!")
    
    # HTML DOSYASINI OKU VE GÖM
    try:
        with open("game.html", "r", encoding="utf-8") as f:
            html_code = f.read()
            # HTML'i iFrame içinde göster
            components.html(html_code, height=700, scrolling=False)
    except FileNotFoundError:
        st.error("game.html dosyası bulunamadı! Lütfen Blok Oyunu kodlarını game.html olarak kaydedin.")

# --- 5. PREMIUM ---
elif menu == "💎 Premium":
    st.header("💎 Premium Üyelik")
    st.warning("Bu özellik yakında aktif olacak!")
    st.info("Avantajlar: 2x Pasif Gelir, Özel Sorular, Reklamsız Deneyim")

# --- 6. SKOR TABLOSU ---
elif menu == "🏆 Skor Tablosu":
    st.header("🏆 Liderlik Tablosu")
    st.table([
        {"Sıra": 1, "Oyuncu": "Elon M.", "Varlık": "₺999,000,000"},
        {"Sıra": 2, "Oyuncu": "Jeff B.", "Varlık": "₺500,000,000"},
        {"Sıra": 3, "Oyuncu": "SİZ", "Varlık": f"₺{st.session_state.balance + st.session_state.bank}"},
    ])
