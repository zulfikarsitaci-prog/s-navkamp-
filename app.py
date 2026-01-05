import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import requests
import json
import os
import time
import random
import database
from datetime import datetime

# ==========================================
# 1. SAYFA VE GENEL AYARLAR
# ==========================================
st.set_page_config(page_title="Bağarası ÇPAL - Dijital Kampüs", page_icon="🎓", layout="wide", initial_sidebar_state="collapsed")

database.create_database()
if not database.login_user("admin", "6626"):
    database.add_user("admin", "6626", "admin")

# ==========================================
# 2. VERİ YÜKLEME (JSON'DAN SORULARI ÇEK)
# ==========================================
@st.cache_data
def load_exams():
    try:
        # Eğer dosya varsa yerelden oku
        if os.path.exists("exams.json"):
            with open("exams.json", "r", encoding="utf-8") as f:
                return json.load(f)
        else:
            return {} # Dosya yoksa boş dön
    except Exception as e:
        st.error(f"Soru bankası yüklenirken hata: {e}")
        return {}

EXAM_DATA = load_exams()

# ==========================================
# 3. SABİTLER VE OYUN KODLARI
# ==========================================
GITHUB_BASE_URL = "https://raw.githubusercontent.com/zulfikarsitaci-prog/s-navkamp-/main"
URL_LIFESIM = f"{GITHUB_BASE_URL}/lifesim_data.json"

FINANCE_GAME_HTML = """<!DOCTYPE html><html><head><style>body{background:#0f172a;color:white;text-align:center;font-family:sans-serif;}</style></head><body><h2>Finans İmparatoru</h2><p>Oyun dosyası yükleniyor...</p></body></html>"""
ASSET_MATRIX_HTML = """<!DOCTYPE html><html><head><style>body{background:#000;color:white;text-align:center;font-family:sans-serif;}</style></head><body><h2>Asset Matrix</h2><p>Oyun dosyası yükleniyor...</p></body></html>"""

# ==========================================
# 4. SERVER VE YARDIMCI FONKSİYONLAR
# ==========================================
@st.cache_resource
class SchoolServer:
    def __init__(self):
        self.classes = {} 
        self.used_codes = set()
        self.create_class("GENEL")
    def create_class(self, class_code):
        if class_code not in self.classes: self.classes[class_code] = {}
    def join_or_update_student(self, class_code, username, points_to_add=0):
        if class_code not in self.classes: self.create_class(class_code)
        if username not in self.classes[class_code]: self.classes[class_code][username] = 0
        self.classes[class_code][username] += points_to_add
        return self.classes[class_code][username]
    def get_score(self, class_code, username): return self.classes.get(class_code, {}).get(username, 0)
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
# 5. ARAYÜZ MANTIĞI
# ==========================================
if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "user_role" not in st.session_state: st.session_state.user_role = None
if "username" not in st.session_state: st.session_state.username = None
if "class_code" not in st.session_state: st.session_state.class_code = "GENEL"

# --- GİRİŞ VE KAYIT ---
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
else:
    with st.sidebar:
        st.title(st.session_state.username)
        st.caption(f"Rol: {st.session_state.user_role}")
        if st.session_state.user_role == "student":
            code_input = st.text_input("Sınıf Kodu", placeholder="Örn: 1234")
            if st.button("Sınıfa Geç"):
                st.session_state.class_code = code_input
                server.join_or_update_student(code_input, st.session_state.username)
                st.success(f"Sınıf: {code_input}"); st.rerun()
        if st.button("Çıkış"): st.session_state.logged_in = False; st.rerun()

    if st.session_state.user_role == "student":
        st.header(f"Merhaba, {st.session_state.username}")
        tabs = st.tabs(["🏆 Kampüs", "📝 Sınavlar & Hazırlık", "🎮 Oyunlar", "💼 LifeSim"])
        
        with tabs[0]:
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

        # --- DİNAMİK SINAV MODÜLÜ (JSON'DAN ÇEKER) ---
        with tabs[1]:
            st.subheader("📚 Yazılıya Hazırlık ve Testler")
            
            if not EXAM_DATA:
                st.warning("Soru bankası (exams.json) bulunamadı veya boş!")
            else:
                col_sinif, col_ders = st.columns(2)
                selected_grade = col_sinif.selectbox("Sınıf Seçiniz", list(EXAM_DATA.keys()))
                
                if selected_grade:
                    lessons = list(EXAM_DATA[selected_grade].keys())
                    selected_lesson = col_ders.selectbox("Ders Seçiniz", lessons)
                    
                    if selected_lesson:
                        st.divider()
                        st.markdown(f"### {selected_grade} - {selected_lesson} Sınavı")
                        questions = EXAM_DATA[selected_grade][selected_lesson]
                        
                        with st.form(f"exam_{selected_grade}_{selected_lesson}"):
                            total_score = 0
                            possible_score = 0
                            user_answers = {}
                            
                            for i, q in enumerate(questions):
                                possible_score += q.get("points", 0)
                                st.markdown(f"**Soru {i+1}:** {q.get('question', '') if 'question' in q else ''}")
                                
                                # Tip 1: Çoktan Seçmeli (Test)
                                if q["type"] == "test":
                                    user_answers[i] = st.radio("Seçiniz:", q["options"], key=f"q_{i}", index=None, label_visibility="collapsed")
                                
                                # Tip 2: Klasik (Text)
                                elif q["type"] == "text":
                                    user_answers[i] = st.text_input("Cevabınız:", key=f"q_{i}")
                                
                                # Tip 3: Senaryo (Alt Sorulu)
                                elif q["type"] == "scenario":
                                    st.info(q["text"])
                                    sub_answers = []
                                    for j, sub in enumerate(q["sub_questions"]):
                                        sub_answers.append(st.text_input(f"{sub['q']}", key=f"q_{i}_sub_{j}"))
                                    user_answers[i] = sub_answers
                                    
                                # Tip 4: Hesaplama (Sayısal)
                                elif q["type"] == "calculation":
                                    st.info(q["text"])
                                    calc_answers = []
                                    for j, inp in enumerate(q["inputs"]):
                                        calc_answers.append(st.number_input(inp["label"], key=f"q_{i}_calc_{j}", step=1))
                                    user_answers[i] = calc_answers
                                    
                                st.divider()

                            if st.form_submit_button("Sınavı Bitir ve Puanla"):
                                earned_score = 0
                                st.markdown("### Sonuçlar")
                                
                                for i, q in enumerate(questions):
                                    is_correct = False
                                    
                                    if q["type"] == "test":
                                        if user_answers[i] == q["answer"]: is_correct = True
                                    
                                    elif q["type"] == "text":
                                        # Basit bir "içeriyor mu" kontrolü (büyük/küçük harf duyarsız)
                                        if q.get("keywords"):
                                            if any(k.lower() in str(user_answers[i]).lower() for k in q["keywords"]): is_correct = True
                                        elif str(user_answers[i]).lower() == q["answer"].lower():
                                            is_correct = True
                                            
                                    elif q["type"] == "scenario":
                                        # Alt soruların hepsi kabaca doğru mu? (Basit kontrol)
                                        correct_count = 0
                                        for j, sub in enumerate(q["sub_questions"]):
                                            if sub["a"].lower() in str(user_answers[i][j]).lower():
                                                correct_count += 1
                                        if correct_count >= len(q["sub_questions"]) / 2: # Yarısı doğruysa puan ver
                                            is_correct = True
                                            
                                    elif q["type"] == "calculation":
                                        correct_count = 0
                                        for j, inp in enumerate(q["inputs"]):
                                            if user_answers[i][j] == inp["correct"]:
                                                correct_count += 1
                                        if correct_count == len(q["inputs"]): is_correct = True
                                    
                                    if is_correct:
                                        earned_score += q["points"]
                                        st.success(f"Soru {i+1}: Doğru (+{q['points']} Puan)")
                                    else:
                                        ans_display = q.get("answer", "Bakınız: Cevap Anahtarı")
                                        st.error(f"Soru {i+1}: Yanlış / Eksik. (Doğru Cevap: {ans_display})")
                                
                                st.metric("Toplam Puan", f"{earned_score} / {possible_score}")
                                if earned_score > 0:
                                    server.join_or_update_student(st.session_state.class_code, st.session_state.username, earned_score)
                                    st.toast(f"{earned_score} Puan bakiyene eklendi!")

        with tabs[2]: # OYUNLAR
            secim = st.selectbox("Oyun Seç", ["Finans İmparatoru", "Asset Matrix"])
            if secim == "Finans İmparatoru": components.html(FINANCE_GAME_HTML, height=600)
            else: components.html(ASSET_MATRIX_HTML, height=600)
        with tabs[3]: # LIFESIM
            components.html(load_lifesim(), height=800, scrolling=True)

    # --- YÖNETİM (Admin/Teacher) ---
    elif st.session_state.user_role in ["admin", "teacher"]:
        st.info("Yönetim Paneli.")
        # ... (Önceki yönetim kodları buraya eklenebilir) ...
