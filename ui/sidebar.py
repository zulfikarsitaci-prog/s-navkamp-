import streamlit as st
import time
import database.users as users
import database.social as social
import database.score as score
from .styles import get_user_display_html

def render_xp_bar(current_score):
    ranks = [(0,"Başlangıç"),(10000,"Çırak"),(100000,"Usta"),(500000,"Bilgin"),(5000000,"LORD")]
    current_rank = ranks[0]
    next_rank = ranks[1]
    for i in range(len(ranks)-1):
        if current_score >= ranks[i][0]:
            current_rank = ranks[i]; next_rank = ranks[i+1]
        else: break
    if current_score >= ranks[-1][0]: progress = 100; label = "MAX SEVİYE"
    else:
        range_diff = next_rank[0] - current_rank[0]
        score_diff = current_score - current_rank[0]
        progress = min(100, int((score_diff / range_diff) * 100))
        label = f"{next_rank[1]} için {next_rank[0] - current_score:,} Puan"

    bar_html = f"""<div style="margin: 10px 0;"><div style="display:flex;justify-content:space-between;font-size:0.7rem;color:#94a3b8;margin-bottom:3px;"><span>{current_rank[1]}</span><span>{progress}%</span></div><div style="background:#334155;border-radius:10px;height:12px;width:100%;overflow:hidden;border:1px solid #475569;"><div style="background:linear-gradient(90deg, #3b82f6, #00ffff);width:{progress}%;height:100%;border-radius:10px;box-shadow:0 0 10px #00ffff;"></div></div><div style="text-align:center;font-size:0.6rem;color:#64748b;margin-top:2px;">{label}</div></div>"""
    st.markdown(bar_html, unsafe_allow_html=True)

def render_sidebar():
    if not st.session_state['logged_in']: return False 
    
    with st.sidebar:
        st.markdown(get_user_display_html(st.session_state['username'], size=70), unsafe_allow_html=True)
        user_score = score.get_total_score(st.session_state['username'])
        render_xp_bar(user_score)
        st.write("") 

        # --- YENİ: HİKAYE YÖNETİMİ ---
        with st.expander("📸 Hikaye Paylaş / Sil"):
            # 1. Hikaye Ekleme
            st.caption("Yeni Hikaye Ekle")
            with st.form("sidebar_story_form", clear_on_submit=True):
                st_img = st.file_uploader("Görsel", type=['png', 'jpg', 'jpeg'], label_visibility="collapsed")
                st_txt = st.text_input("Not", placeholder="Kısa bir not...")
                if st.form_submit_button("Paylaş"):
                    if st_img:
                        social.add_story(st.session_state['username'], st_img, st_txt)
                        st.toast("Hikaye paylaşıldı!", icon="✅")
                        time.sleep(1)
                        st.rerun()
                    else: st.error("Resim seçmelisin!")
            
            st.divider()
            
            # 2. Hikaye Silme
            st.caption("Hikayelerim")
            my_stories = social.get_my_stories(st.session_state['username'])
            if my_stories:
                for s in my_stories:
                    c1, c2 = st.columns([3, 1])
                    c1.text(f"{s[2][5:]} - {s[1][:10]}...") # Tarih ve içerik özeti
                    if c2.button("Sil", key=f"del_st_{s[0]}"):
                        social.delete_story(s[0])
                        st.rerun()
            else:
                st.caption("Hiç hikayen yok.")
        # -----------------------------
        
        with st.expander("⚙️ Hesabım"):
            new_name_input = st.text_input("Yeni İsim")
            cost = 500000 if users.get_user_change_count(st.session_state['username']) > 0 else 0
            if st.button(f"Değiştir ({cost} P)"):
                ok, msg = users.change_username_logic(st.session_state['username'], new_name_input)
                if ok: st.session_state['username'] = new_name_input; st.success(msg); time.sleep(2); st.rerun()
                else: st.error(msg)
            
            uploaded_avatar = st.file_uploader("Fotoğraf", type=['png', 'jpg'])
            if uploaded_avatar:
                if users.update_avatar(st.session_state['username'], uploaded_avatar): st.success("Yüklendi!"); time.sleep(1); st.rerun()
            
            search_u = st.selectbox("Arkadaş Ara", social.get_searchable_users(st.session_state['username']))
            if st.button("Ekle"):
                ok, msg = social.send_friend_request(st.session_state['username'], search_u)
                if ok: st.success(msg)
                else: st.warning(msg)

        reqs = social.get_pending_requests(st.session_state['username'])
        if reqs:
            st.info("📩 İstekler")
            for r in reqs:
                if st.button(f"Kabul: {r[1]}", key=f"acc_{r[0]}"):
                    social.accept_request(r[1], st.session_state['username']); st.rerun()

        st.write("")
        if st.button("🚪 Çıkış Yap"): st.session_state['logged_in']=False; st.rerun()
    return True

def render_login_page():
    # Login sayfası kodları aynı kalıyor
    st.markdown("""<div class="login-container"><div class="login-sub">Muhasebe ve Finansman Alanı</div><div class="login-main">DİJİTAL GELİŞİM PLATFORMU</div><div class="login-bottom">~ Dijital Kampüs ~</div></div>""", unsafe_allow_html=True)
    with st.container():
        with st.form("login"):
            u = st.text_input("Kullanıcı Adı"); p = st.text_input("Şifre", type="password")
            if st.form_submit_button("Giriş"):
                user = users.login_user(u, p)
                if user: st.session_state.update({'logged_in':True, 'user_role':user[3], 'username':user[1]}); st.rerun()
                else: st.error("Hatalı.")
        with st.expander("Kayıt Ol"):
            with st.form("reg"):
                nu = st.text_input("Kullanıcı"); np = st.text_input("Şifre", type="password")
                st.write(f"Güvenlik: **{st.session_state['captcha_q']} = ?**")
                ans = st.number_input("Cevap", step=1)
                if st.form_submit_button("Kayıt"):
                    if ans == st.session_state['captcha_a']:
                        s, r = users.add_user(nu, np, "student")
                        if s: st.session_state['captcha_q']=None; st.success("Başarılı!"); st.rerun()
                        else: st.error("İsim alınmış.")
                    else: st.error("Yanlış cevap!"); time.sleep(1); st.rerun()
