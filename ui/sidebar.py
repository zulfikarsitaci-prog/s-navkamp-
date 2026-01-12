import streamlit as st
import time
import database.users as users
import database.social as social
import database.score as score # Puan çekmek için eklendi
from .styles import get_user_display_html

def render_xp_bar(current_score):
    # Seviye Eşikleri
    ranks = [
        (0, "Başlangıç"),
        (10000, "Çırak"),
        (100000, "Usta"),
        (500000, "Bilgin"),
        (5000000, "LORD")
    ]
    
    # Mevcut ve Sonraki Seviyeyi Bul
    current_rank = ranks[0]
    next_rank = ranks[1]
    
    for i in range(len(ranks)-1):
        if current_score >= ranks[i][0]:
            current_rank = ranks[i]
            next_rank = ranks[i+1]
        else:
            break
            
    # Son seviyedeyse
    if current_score >= ranks[-1][0]:
        progress = 100
        label = "MAX SEVİYE"
    else:
        # Yüzde Hesapla: (Şu anki Puan - Şimdiki Seviye Alt Sınırı) / (Hedef - Şimdiki Seviye Alt Sınırı)
        range_diff = next_rank[0] - current_rank[0]
        score_diff = current_score - current_rank[0]
        progress = min(100, int((score_diff / range_diff) * 100))
        label = f"{next_rank[1]} için {next_rank[0] - current_score:,} Puan"

    # HTML Çubuğu
    bar_html = f"""
    <div style="margin: 10px 0;">
        <div style="display:flex;justify-content:space-between;font-size:0.7rem;color:#94a3b8;margin-bottom:3px;">
            <span>{current_rank[1]}</span>
            <span>{progress}%</span>
        </div>
        <div style="background:#334155;border-radius:10px;height:12px;width:100%;overflow:hidden;border:1px solid #475569;">
            <div style="background:linear-gradient(90deg, #3b82f6, #00ffff);width:{progress}%;height:100%;border-radius:10px;box-shadow:0 0 10px #00ffff;"></div>
        </div>
        <div style="text-align:center;font-size:0.6rem;color:#64748b;margin-top:2px;">{label}</div>
    </div>
    """
    st.markdown(bar_html, unsafe_allow_html=True)

def render_sidebar():
    if not st.session_state['logged_in']:
        # Giriş / Kayıt Ekranı (Sidebar yerine ana ekranı kaplar)
        return False 
    
    with st.sidebar:
        # Profil Resmi ve İsim
        st.markdown(get_user_display_html(st.session_state['username'], size=70), unsafe_allow_html=True)
        
        # --- YENİ: XP ÇUBUĞU ---
        user_score = score.get_total_score(st.session_state['username'])
        render_xp_bar(user_score)
        # -----------------------

        st.write("") 
        
        with st.expander("⚙️ Hesabım"):
            new_name_input = st.text_input("Yeni İsim")
            change_count = users.get_user_change_count(st.session_state['username'])
            cost = 0 if change_count == 0 else 500000
            btn_label = "Değiştir (Ücretsiz)" if cost == 0 else f"Değiştir ({cost:,} P)"
            if st.button(btn_label):
                if new_name_input:
                    ok, msg = users.change_username_logic(st.session_state['username'], new_name_input)
                    if ok: st.session_state['username'] = new_name_input; st.success(msg); time.sleep(2); st.rerun()
                    else: st.error(msg)
            
            st.divider()
            uploaded_avatar = st.file_uploader("Fotoğraf", type=['png', 'jpg'])
            if uploaded_avatar:
                if users.update_avatar(st.session_state['username'], uploaded_avatar): st.success("Yüklendi!"); time.sleep(1); st.rerun()
            
            st.divider()
            search_u = st.selectbox("Arkadaş Ara", social.get_searchable_users(st.session_state['username']))
            if st.button("Ekle"):
                ok, msg = social.send_friend_request(st.session_state['username'], search_u)
                if ok: st.success(msg)
                else: st.warning(msg)

        reqs = social.get_pending_requests(st.session_state['username'])
        if reqs:
            st.info("📩 İstekler")
            for r in reqs:
                c1, c2 = st.columns([2,1])
                c1.write(r[1])
                if c2.button("Kabul", key=f"acc_{r[0]}"):
                    social.accept_request(r[1], st.session_state['username'])
                    st.success("Oldu!"); st.rerun()

        st.write("")
        if st.button("🚪 Çıkış Yap"): st.session_state['logged_in']=False; st.rerun()
    return True

def render_login_page():
    st.markdown("""
        <div class="login-container">
            <div class="login-sub">Muhasebe ve Finansman Alanı</div>
            <div class="login-main">DİJİTAL GELİŞİM PLATFORMU</div>
            <div class="login-bottom">~ Dijital Kampüs ~</div>
        </div>
    """, unsafe_allow_html=True)
    
    with st.container():
        with st.form("login"):
            u = st.text_input("Kullanıcı Adı")
            p = st.text_input("Şifre", type="password")
            if st.form_submit_button("Giriş"):
                user = users.login_user(u, p)
                if user:
                    st.session_state.update({'logged_in':True, 'user_role':user[3], 'username':user[1]})
                    st.rerun()
                else: st.error("Hatalı.")
        
        with st.expander("Kayıt Ol"):
            with st.form("reg"):
                nu = st.text_input("Kullanıcı"); np = st.text_input("Şifre", type="password")
                st.write(f"Güvenlik: **{st.session_state['captcha_q']} = ?**")
                captcha_ans = st.number_input("Cevap", step=1)
                
                if st.form_submit_button("Kayıt"):
                    if captcha_ans == st.session_state['captcha_a']:
                        success, rank = users.add_user(nu, np, "student")
                        if success:
                            st.session_state['captcha_q'] = None 
                            if rank <= 10: 
                                st.balloons()
                                st.success(f"TEBRİKLER! {rank}. kişi olarak KURUCU ünvanı kazandın!")
                            else: st.success("Başarılı! Giriş yapabilirsin.")
                        else: st.error("İsim alınmış.")
                    else:
                        st.error("Yanlış cevap! Soru değişiyor...")
                        st.session_state['captcha_q'] = None
                        time.sleep(1)
                        st.rerun()
