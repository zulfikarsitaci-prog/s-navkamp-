import streamlit as st
import streamlit.components.v1 as components
import json
import os
import pandas as pd
import time
import urllib.parse

# --- AYARLAR ---
st.set_page_config(page_title="Finans Kampüsü", page_icon="🏛️", layout="wide")

# --- CSS (Arayüz Düzenlemeleri) ---
st.markdown("""
    <style>
    .stApp { background-color: #0a0a12; color: #e0e0e0; }
    [data-testid="stSidebar"] { background-color: #16213e; border-right: 1px solid #f1c40f; }
    h1, h2, h3 { color: #f1c40f !important; font-family: sans-serif; }
    
    /* Banka Alanı Stili */
    .bank-area { background-color: #0f3460; padding: 20px; border-radius: 12px; border: 2px dashed #27ae60; text-align: center; color: #2ecc71; }
    .html-save-btn { display: block; width: 100%; background: #27ae60; color: white; padding: 10px; text-align: center; border-radius: 8px; text-decoration: none; margin-top: 10px; }
    </style>
""", unsafe_allow_html=True)

# --- VERİTABANI FONKSİYONLARI ---
DB_FILE = "puan_veritabani.json"

def load_db():
    if not os.path.exists(DB_FILE):
        with open(DB_FILE, "w", encoding="utf-8") as f: json.dump({}, f)
    try:
        with open(DB_FILE, "r", encoding="utf-8") as f: return json.load(f)
    except: return {}

def save_db(data):
    with open(DB_FILE, "w", encoding="utf-8") as f: json.dump(data, f, ensure_ascii=False, indent=4)

def update_player_score(user_key, points, name, no):
    db = load_db()
    current_data = db.get(user_key, {"score": 0, "name": name, "no": no})
    current_data["score"] += points
    current_data["name"] = name
    db[user_key] = current_data
    save_db(db)
    return current_data["score"]

def get_player_score(user_key):
    db = load_db()
    return db.get(user_key, {}).get("score", 0)

def decode_transfer_code(code):
    try:
        parts = code.split('-')
        if len(parts) != 3 or parts[0] != "FNK": return None
        hex_val = parts[1]
        score_mult = int(hex_val, 16)
        actual_score = score_mult / 13
        if actual_score.is_integer(): return int(actual_score)
        else: return None
    except: return None

# --- SESSION STATE ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'user_info' not in st.session_state: st.session_state.user_info = {}

# --- UYGULAMA AKIŞI ---

# 1. GİRİŞ EKRANI
if not st.session_state.logged_in:
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        st.markdown("<h1 style='text-align:center;'>🏛️ FİNANS KAMPÜSÜ</h1>", unsafe_allow_html=True)
        with st.form("login"):
            ad = st.text_input("Ad Soyad")
            no = st.text_input("Okul No")
            if st.form_submit_button("GİRİŞ YAP", type="primary"):
                if ad and no:
                    key = f"{no}_{ad.strip()}"
                    st.session_state.user_info = {"name": ad, "no": no, "key": key}
                    st.session_state.logged_in = True
                    st.rerun()
                else: st.error("Eksik bilgi girdiniz.")

# 2. ANA PANEL
else:
    user = st.session_state.user_info
    user_key = user['key']
    current_score = get_player_score(user_key)
    
    # YAN MENÜ
    with st.sidebar:
        st.markdown(f"### 👤 {user['name']}")
        st.info(f"💰 Varlık: **{current_score} ₺**")
        
        # Skor Kaydetme Linki
        safe_name = urllib.parse.quote(user['name'])
        form_link = f"https://docs.google.com/forms/d/e/1FAIpQLScshsXIM91CDKu8TgaHIelXYf3M9hzoGb7mldQCDAJ-rcuJ3w/viewform?usp=pp_url&entry.1300987443={safe_name}&entry.598954691={current_score}"
        st.markdown(f"""<a href="{form_link}" target="_blank" class="html-save-btn">💾 SKORU KAYDET</a>""", unsafe_allow_html=True)
        
        if st.button("ÇIKIŞ YAP"):
            st.session_state.logged_in = False
            st.rerun()

    # SEKMELER
    t1, t2, t3, t4 = st.tabs(["🏠 PROFİL", "📚 SORU MERKEZİ", "🎮 SİMÜLASYON DÜNYASI", "🏆 LİDERLİK"])

    with t1:
        st.metric("Toplam Varlık", f"{current_score} ₺")
        st.success("Verileriniz güvende. Oyunlardan kazandığınız kodları Banka bölümüne girmeyi unutmayın.")

    with t2:
        st.subheader("Akademik Görevler")
        c1, c2 = st.columns(2)
        if c1.button("TYT Testi Çöz (+20 Puan)"):
             update_player_score(user_key, 20, user['name'], user['no'])
             st.toast("+20 Puan Eklendi!")
             time.sleep(1)
             st.rerun()
        if c2.button("Meslek Testi Çöz (+20 Puan)"):
             update_player_score(user_key, 20, user['name'], user['no'])
             st.toast("+20 Puan Eklendi!")
             time.sleep(1)
             st.rerun()

    with t3:
        # --- HTML OYUN ENTEGRASYONU ---
        st.info("Aşağıdaki menüden oynamak istediğiniz simülasyonu seçin.")
        
        # game.html dosyasını oku ve göster
        try:
            with open("game.html", "r", encoding="utf-8") as f:
                html_content = f.read()
                components.html(html_content, height=800, scrolling=False)
        except FileNotFoundError:
            st.error("game.html dosyası bulunamadı! Lütfen GitHub'a yükleyin.")

        # BANKA VEZNESİ (Transfer Kodu)
        st.markdown("---")
        c_bank, c_info = st.columns([1, 2])
        with c_bank:
            st.markdown('<div class="bank-area"><h3>🏦 MERKEZ BANKASI</h3></div>', unsafe_allow_html=True)
        with c_info:
            code = st.text_input("Transfer Kodu Giriniz (Örn: FNK-A1B-99):")
            if st.button("KODU BOZDUR VE YATIR", type="primary"):
                amount = decode_transfer_code(code)
                if amount:
                    update_player_score(user_key, amount, user['name'], user['no'])
                    st.success(f"Hesabınıza {amount} ₺ eklendi!")
                    time.sleep(2)
                    st.rerun()
                else:
                    st.error("Geçersiz Kod!")

    with t4:
        db = load_db()
        data = [{"Öğrenci": v['name'], "Puan": v['score']} for k,v in db.items()]
        if data:
            df = pd.DataFrame(data).sort_values("Puan", ascending=False).reset_index(drop=True)
            df.index += 1
            st.dataframe(df, use_container_width=True)
        else:
            st.info("Henüz veri yok.")
