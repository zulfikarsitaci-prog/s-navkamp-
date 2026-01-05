import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import requests
import json
import os
import time
import random
import database  # Veritabanı modülümüz
from datetime import datetime

# ==========================================
# 1. SAYFA VE GENEL AYARLAR
# ==========================================
st.set_page_config(
    page_title="Bağarası ÇPAL - Dijital Kampüs",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Veritabanını başlat
database.create_database()
if not database.login_user("admin", "6626"):
    database.add_user("admin", "6626", "admin")

# ==========================================
# 2. SABİTLER VE OYUN HTML KODLARI
# ==========================================
GITHUB_USER = "zulfikarsitaci-prog"
GITHUB_REPO = "s-navkamp-"
GITHUB_BRANCH = "main"
GITHUB_BASE_URL = f"https://raw.githubusercontent.com/{GITHUB_USER}/{GITHUB_REPO}/{GITHUB_BRANCH}"

URL_LIFESIM = f"{GITHUB_BASE_URL}/lifesim_data.json"

# --- HTML OYUN KODLARI (Öncekiyle Aynı - Yer Kaplamaması İçin Kısaltıldı) ---
# (Buraya önceki kodundaki FINANCE_GAME_HTML ve ASSET_MATRIX_HTML değişkenlerini aynen yapıştırın.
# Kodun çalışması için bu değişkenlerin tanımlı olması şarttır. Ben örnek olarak kısa tutuyorum.)

FINANCE_GAME_HTML = """
<!DOCTYPE html>
<html><head><style>body{background:#0f172a;color:white;text-align:center;font-family:sans-serif;}</style></head>
<body><h2>Finans İmparatoru</h2><p>Oyun yüklendi...</p></body></html>
"""
ASSET_MATRIX_HTML = """
<!DOCTYPE html>
<html><head><style>body{background:#000;color:white;text-align:center;font-family:sans-serif;}</style></head>
<body><h2>Asset Matrix</h2><p>Oyun yüklendi...</p></body></html>
"""

# ==========================================
# 3. SERVER VE YARDIMCI FONKSİYONLAR
# ==========================================
@st.cache_resource
class SchoolServer:
    def __init__(self):
        self.classes = {} 
        self.used_codes = set()
        self.create_class("GENEL")

    def create_class(self, class_code):
        if class_code not in self.classes:
            self.classes[class_code] = {}
        return True

    def join_or_update_student(self, class_code, username, points_to_add=0):
        if class_code not in self.classes: self.create_class(class_code)
        if username not in self.classes[class_code]: self.classes[class_code][username] = 0
        self.classes[class_code][username] += points_to_add
        return self.classes[class_code][username]

    def get_score(self, class_code, username):
        return self.classes.get(class_code, {}).get(username, 0)

    def redeem_code(self, class_code, username, code_string):
        if code_string in self.used_codes: return False, "Kod kullanılmış!"
        try:
            parts = code_string.split('-')
            if len(parts) != 3 or parts[0] != "FNK": return False, "Geçersiz kod!"
            amount = int(int(parts[1], 16) / 13)
            self.used_codes.add(code_string)
            nb = self.join_or_update_student(class_code, username, amount)
            return True, nb
        except: return False, "Hata."

    def get_leaderboard(self, class_code):
        if class_code in self.classes:
            data = [{"Öğrenci": k, "Puan": v} for k, v in self.classes[class_code].items()]
            if data: return pd.DataFrame(data).sort_values(by="Puan", ascending=False)
        return pd.DataFrame()

server = SchoolServer()

def load_lifesim():
    try:
        r = requests.get(f"{GITHUB_BASE_URL}/game.html")
        html = r.text if r.status_code == 200 else "<h3>Yüklenemedi</h3>"
        data = requests.get(URL_LIFESIM).json()
        return html.replace("// PYTHON_DATA_HERE", f"var scenarios = {json.dumps(data)};")
    except: return "Simülasyon Yüklenemedi"

# ==========================================
# 4. ARAYÜZ MANTIĞI
# ==========================================
if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "user_role" not in st.session_state: st.session_state.user_role = None
if "username" not in st.session_state: st.session_state.username = None
if "class_code" not in st.session_state: st.session_state.class_code = "GENEL"

# --- GİRİŞ VE KAYIT EKRANI ---
if not st.session_state.logged_in:
    st.markdown("<h1 style='text-align:center;'>🎓 Bağarası ÇPAL Dijital Kampüs</h1>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        tab_log, tab_reg = st.tabs(["Giriş Yap", "Kayıt Ol"])
        with tab_log:
            with st.form("login_form"):
                u = st.text_input("Kullanıcı Adı")
                p = st.text_input("Şifre", type="password")
                if st.form_submit_button("Giriş"):
                    user = database.login_user(u, p)
                    if user:
                        st.session_state.logged_in = True
                        st.session_state.user_role = user[3]
                        st.session_state.username = user[1]
                        if user[3] == "student": server.join_or_update_student("GENEL", user[1], 0)
                        st.rerun()
                    else: st.error("Hatalı bilgi.")
        with tab_reg:
            with st.form("reg_form"):
                nu = st.text_input("Kullanıcı Adı")
                np = st.text_input("Şifre", type="password")
                if st.form_submit_button("Kayıt Ol"):
                    if database.add_user(nu, np, "student"): st.success("Kayıt başarılı! Giriş yapınız.")
                    else: st.error("Kullanıcı adı dolu.")

# --- ANA UYGULAMA ---
else:
    with st.sidebar:
        st.title(st.session_state.username)
        st.write(f"Rol: {st.session_state.user_role}")
        if st.button("Çıkış"): st.session_state.logged_in = False; st.rerun()

    # --- ÖĞRENCİ PANELİ ---
    if st.session_state.user_role == "student":
        st.header(f"Merhaba, {st.session_state.username}")
        
        tabs = st.tabs(["🏆 Kampüs", "📚 Dersler & Test", "🎮 Oyunlar", "💼 LifeSim"])
        
        with tabs[0]: # KAMPÜS
            c1, c2 = st.columns([1,2])
            with c1:
                st.metric("Puanın", f"{server.get_score(st.session_state.class_code, st.session_state.username)} ₺")
                kod = st.text_input("Puan Kodu")
                if st.button("Yükle"):
                    res, msg = server.redeem_code(st.session_state.class_code, st.session_state.username, kod)
                    if res: st.success(f"Yüklendi! Yeni: {msg}")
                    else: st.error(msg)
            with c2:
                st.dataframe(server.get_leaderboard(st.session_state.class_code), use_container_width=True)

        with tabs[1]: # DERSLER VE TESTLER (YENİLENEN KISIM)
            ders_secimi = st.selectbox("Ders Seçiniz", ["Seçiniz...", "İş ve Sosyal Güvenlik Hukuku", "Maliyet Muhasebesi"])
            
            # --- DERS 1: İŞ HUKUKU ---
            if ders_secimi == "İş ve Sosyal Güvenlik Hukuku":
                st.subheader("📝 11. Sınıf İş Hukuku - 1. Dönem 2. Yazılı Hazırlık")
                st.info("Senaryo: Söke OSB'de 'Ege Tekstil A.Ş.' sahibi Ali Bey, yönetimi Ayşe Hanım'a bırakmıştır. İşçi Mehmet Bey servise binerken yaralanmıştır.")

                with st.expander("BÖLÜM A: Kavramlar ve Senaryo Analizi", expanded=True):
                    with st.form("hukuk_a"):
                        q1_a = st.text_input("1. Hukuken asıl İşveren kimdir?")
                        q1_b = st.text_input("2. İşveren Vekili kimdir?")
                        q1_c = st.radio("3. Servis aracı işyeri sınırına dahil midir?", ["Evet", "Hayır"])
                        
                        st.markdown("**İş Sözleşmesi Unsurları:**")
                        c1, c2, c3 = st.columns(3)
                        q2_a = c1.text_input("Unsur 1 (Emek)")
                        q2_b = c2.text_input("Unsur 2 (Para)")
                        q2_c = c3.text_input("Unsur 3 (Bağımlılık)")
                        
                        if st.form_submit_button("A Bölümünü Kontrol Et"):
                            score = 0
                            if "Ege Tekstil" in q1_a or "Tüzel Kişilik" in q1_a: score += 5
                            if "Ayşe" in q1_b: score += 5
                            if q1_c == "Evet": score += 10
                            if q2_a and q2_b and q2_c: score += 10
                            st.info(f"Tahmini Puan: {score}/30. (Not: Tam eşleşme gerekmez, anahtar kelimeler yeterli.)")
                            st.write("Doğru Cevaplar: Ege Tekstil A.Ş., Ayşe Hanım, Evet (Eklenti), İş Görme, Ücret, Bağımlılık.")

                with st.expander("BÖLÜM C: Fazla Çalışma Hesaplaması"):
                    st.write("Veri: Haftalık normal süre 45 saat. Mehmet Bey 50 saat çalıştı. Saatlik ücreti 200 TL.")
                    with st.form("hukuk_c"):
                        fc_saat = st.number_input("Kaç saat fazla çalışma?", min_value=0)
                        fc_ucret = st.number_input("1 Saatlik Zamlı (%50) Ücret (TL)?", min_value=0)
                        fc_toplam = st.number_input("Toplam Fazla Çalışma Ücreti (TL)?", min_value=0)
                        
                        if st.form_submit_button("Hesapla ve Kontrol Et"):
                            if fc_saat == 5 and fc_ucret == 300 and fc_toplam == 1500:
                                st.balloons()
                                st.success("TEBRİKLER! Hepsi Doğru. (5 Saat * 300 TL = 1500 TL)")
                                server.join_or_update_student(st.session_state.class_code, st.session_state.username, 30)
                            else:
                                st.error(f"Hatalı. Doğrusu: 5 Saat, 300 TL, 1500 TL olmalıydı.")

            # --- DERS 2: MALİYET MUHASEBESİ ---
            elif ders_secimi == "Maliyet Muhasebesi":
                st.subheader("📊 11. Sınıf Maliyet Muhasebesi Uygulamaları")
                
                # SORU 1: DAĞITIM
                st.markdown("### SORU 1: Gider Dağıtımı (I. Dağıtım)")
                data_dagitim = {
                    "Gider Yerleri": ["Kesim", "Dikim", "Ütü", "Paketleme"],
                    "Personel Sayısı": [60, 70, 40, 30],
                    "Alan (m2)": [500, 600, 200, 200],
                    "Makine Sayısı": [80, 90, 100, 30]
                }
                df_dagitim = pd.DataFrame(data_dagitim)
                st.dataframe(df_dagitim, hide_index=True)
                st.info("Toplam Yemek Gideri: 20.000 TL (Personele göre) | Toplam Temizlik: 30.000 TL (Alana göre)")

                with st.form("muh_s1"):
                    c1, c2 = st.columns(2)
                    ans_yemek_kesim = c1.number_input("Kesim Bölümü Yemek Gideri Payı (TL)?", step=100)
                    ans_temizlik_dikim = c2.number_input("Dikim Bölümü Temizlik Gideri Payı (TL)?", step=100)
                    
                    if st.form_submit_button("Dağıtımı Kontrol Et"):
                        # Hesaplama: Yemek (20000/200=100 TL/kişi) -> Kesim(60*100=6000)
                        # Hesaplama: Temizlik (30000/1500=20 TL/m2) -> Dikim(600*20=12000)
                        dogru = True
                        if ans_yemek_kesim != 6000:
                            st.error("Kesim Yemek Payı Yanlış! (İpucu: 20.000 / 200 * 60)")
                            dogru = False
                        if ans_temizlik_dikim != 12000:
                            st.error("Dikim Temizlik Payı Yanlış! (İpucu: 30.000 / 1500 * 600)")
                            dogru = False
                        
                        if dogru:
                            st.success("Harika! Dağıtım anahtarlarını doğru kullandın.")
                            server.join_or_update_student(st.session_state.class_code, st.session_state.username, 20)

                st.divider()

                # SORU 2: FIFO
                st.markdown("### SORU 2: FIFO (İlk Giren İlk Çıkar)")
                st.code("""
                01.05: Devir 5000 kg @ 30 TL
                10.05: Çıkan 3500 kg
                15.05: Giren 5500 kg @ 35 TL
                21.05: Çıkan 4000 kg
                """)
                with st.form("muh_s2"):
                    kalan_stok_degeri = st.number_input("Ay sonu eldeki stoğun TL değeri nedir?", step=100)
                    if st.form_submit_button("FIFO Kontrol"):
                        # Mantık: 
                        # 10.05 Kalan: 1500 kg @ 30 TL
                        # 21.05 Çıkan 4000 kg -> (1500 @ 30 bitti) + (2500 @ 35 çıktı)
                        # Kalan: (5500 - 2500) = 3000 kg @ 35 TL
                        # Değer: 3000 * 35 = 105.000 TL
                        if kalan_stok_degeri == 105000:
                            st.success("Doğru! (Kalan 3000 kg * 35 TL = 105.000 TL)")
                            server.join_or_update_student(st.session_state.class_code, st.session_state.username, 20)
                        else:
                            st.error("Yanlış. İpucu: En son giren partiden 3000 kg kaldı.")

                st.divider()

                # SORU 4: BİRİM MALİYET
                st.markdown("### SORU 4: Birim Maliyet Hesaplama")
                df_birim = pd.DataFrame({
                    "Gider Türü": ["Direkt İşçilik", "DİMMG", "GÜG", "TOPLAM"],
                    "Ekmek (5000 Adet)": [20000, 35000, 20000, 75000],
                    "Poğaça (4000 Adet)": [15000, 40000, 25000, 80000]
                })
                st.dataframe(df_birim, hide_index=True)
                
                with st.form("muh_s4"):
                    c1, c2 = st.columns(2)
                    br_ekmek = c1.number_input("1 Adet Ekmek Maliyeti (TL)", step=0.5)
                    br_pogaca = c2.number_input("1 Adet Poğaça Maliyeti (TL)", step=0.5)
                    
                    if st.form_submit_button("Maliyet Kontrol"):
                        # Ekmek: 75000 / 5000 = 15
                        # Poğaça: 80000 / 4000 = 20
                        if br_ekmek == 15 and br_pogaca == 20:
                            st.success("Tebrikler! Muhasebe dehasısın.")
                            server.join_or_update_student(st.session_state.class_code, st.session_state.username, 20)
                        else:
                            st.warning("Hesaplamada hata var. Toplam Maliyet / Miktar formülünü hatırla.")

        with tabs[2]: # OYUNLAR
            secim = st.selectbox("Oyun Seç", ["Finans İmparatoru", "Asset Matrix"])
            if secim == "Finans İmparatoru": components.html(FINANCE_GAME_HTML, height=600)
            else: components.html(ASSET_MATRIX_HTML, height=600)

        with tabs[3]: # LIFESIM
            components.html(load_lifesim(), height=800, scrolling=True)

    # --- ÖĞRETMEN VE ADMİN (KISA TUTULDU) ---
    elif st.session_state.user_role in ["admin", "teacher"]:
        st.info("Yönetim Paneli Aktif.")
        # ... (Yönetim kodları buraya gelir, önceki kodla aynı kalabilir) ...
