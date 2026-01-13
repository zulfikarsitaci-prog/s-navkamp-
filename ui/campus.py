import streamlit as st
import re
import time
import database.social as social
import database.score as score
import database.users as users
from .styles import get_user_display_html, get_post_style_css

def extract_youtube_link(text):
    if not text: return None
    match = re.search(r'(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/(watch\?v=|embed/|v/|live/|.+\?v=)?([^&=%\?]{11})', text)
    if match: return f"https://www.youtube.com/watch?v={match.group(6)}"
    return None

def render_stories():
    # 1. Hikayeleri Çek (Cache'li fonksiyon kullanıyoruz, hızlıdır)
    stories = social.get_active_stories()
    
    if stories:
        st.markdown("### 🔥 Hikayeler")
        
        # CSS ile 60px'e zorlanmış kolonlar oluşturuyoruz
        cols = st.columns(len(stories))
        
        for i, story in enumerate(stories):
            sid, s_user, s_content, s_img, s_time = story
            
            with cols[i]:
                # Avatarı al (Cache'den gelir)
                ava, _, _, _, _, _ = users.get_user_styles(s_user)
                img_src = f"data:image/jpeg;base64,{ava}" if ava else "https://via.placeholder.com/150/CCCCCC/FFFFFF?text=U"
                
                # HTML: Yuvarlak İkon (50px) ve İsim
                # CSS dosyasındaki .story-btn sınıfı bu yapıyı yakalar
                st.markdown(f"""
                <div style="text-align:center;">
                    <div style="width: 50px; height: 50px; border-radius: 50%; padding: 2px; background: linear-gradient(45deg, #f09433, #bc1888); display: inline-block; cursor: pointer;">
                        <img src="{img_src}" style="width: 100%; height: 100%; border-radius: 50%; border: 2px solid #0f172a; object-fit: cover;">
                    </div>
                    <div style="font-size:0.65rem; color:#cbd5e1; margin-top:2px; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; max-width:55px;">{s_user}</div>
                </div>
                """, unsafe_allow_html=True)
                
                # Görünmez Buton (Tıklama yakalamak için)
                st.markdown('<div class="story-btn">', unsafe_allow_html=True)
                if st.button(f"s_{sid}", key=f"btn_story_{sid}"):
                    st.session_state['active_story_index'] = i
                    st.session_state['active_story_open'] = True
                st.markdown('</div>', unsafe_allow_html=True)

    # --- HİKAYE GÖSTERİM PENCERESİ (MODAL) ---
    if st.session_state.get('active_story_open') and stories:
        idx = st.session_state.get('active_story_index', 0)
        
        # İndeks hatasını önle
        if idx >= len(stories): idx = 0
        if idx < 0: idx = len(stories) - 1
        
        current_story = stories[idx]
        sid, s_user, s_content, s_img, s_time = current_story
        
        @st.dialog(f"Hikaye: {s_user}")
        def show_story_modal():
            if s_img:
                st.image(f"data:image/jpeg;base64,{s_img}", use_container_width=True)
            if s_content:
                st.write(f"📝 {s_content}")
            st.caption(f"🕒 {s_time}")
            
            # İleri / Geri
            c1, c2, c3 = st.columns([1, 4, 1])
            with c1:
                if st.button("⬅️", key="prev_story"):
                    st.session_state['active_story_index'] = idx - 1
                    st.rerun()
            with c3:
                if st.button("➡️", key="next_story"):
                    st.session_state['active_story_index'] = idx + 1
                    st.rerun()
                    
        show_story_modal()
        
    if stories: st.write("") # Alt boşluk

def render_campus_wall():
    # Önce hikayeleri bas
    render_stories()
    
    st.subheader("Kampüs Duvar")
    
    # --- PAYLAŞIM ALANI ---
    my_score = score.get_total_score(st.session_state['username'])
    POST_COST = 100000
    
    # Sadece Admin veya puanı yetenler paylaşım yapabilir (Gürültüyü önlemek için)
    # Eşik değerini düşürebilirsin.
    CAN_POST = (my_score >= POST_COST) or (st.session_state['user_role'] == 'admin')
    
    if CAN_POST:
        with st.expander(f"✨ Yeni Paylaşım / Anket (-{POST_COST:,} P)", expanded=False):
            ptype = st.radio("Tip", ["Normal Post", "Anket"], horizontal=True, label_visibility="collapsed")
            with st.form("share_form"):
                txt = st.text_area("Ne düşünüyorsun?", height=80)
                
                if ptype == "Normal Post":
                    img = st.file_uploader("Resim Ekle", type=['png','jpg','jpeg'])
                    if st.form_submit_button("Paylaş"):
                        if my_score >= POST_COST:
                            score.add_score(st.session_state['username'], -POST_COST, "Post")
                            social.add_post(st.session_state['username'], txt, img)
                            st.rerun()
                        else: st.error("Yetersiz Puan!")
                else: 
                    st.info("Şıkları virgülle ayır (Örn: Evet, Hayır)")
                    opts = st.text_input("Şıklar")
                    if st.form_submit_button("Anket Başlat"):
                        op_list = opts.split(",")
                        if len(op_list) >= 2 and my_score >= POST_COST:
                            score.add_score(st.session_state['username'], -POST_COST, "Anket")
                            social.add_poll_post(st.session_state['username'], txt, op_list)
                            st.rerun()
                        else: st.error("Eksik bilgi veya yetersiz puan.")
    
    # --- GÖNDERİ AKIŞI (FEED) ---
    posts = social.get_posts(30) # Son 30 gönderi (Hız için limitli)
    
    for p in posts:
        pid, p_user, p_content, p_img, p_time, p_likes, p_poll = p
        is_poll = True if p_poll else False
        
        # HTML Kartı Oluştur (Solid Arka Plan - Hızlı Render)
        post_html = f"""
        <div class="post-card">
            <div class="post-header">
                {get_user_display_html(p_user, size=35)}
                <span style="color:#64748b;font-size:0.65rem;margin-left:auto;">{p_time[-5:]}</span>
            </div>
            <div class="post-content">{p_content if p_content else ''}</div>
            {f'<img src="data:image/jpeg;base64,{p_img}" class="post-image">' if p_img else ''}
        </div>
        """
        st.markdown(post_html, unsafe_allow_html=True)
        
        # --- ANKET MANTIĞI ---
        if is_poll:
            poll_res, total_votes, has_voted = social.get_poll_results(pid, p_poll)
            
            if not has_voted:
                st.caption("Oylamak için tıkla:")
                for idx, (opt_text, cnt) in enumerate(poll_res):
                    # CSS ile .poll-marker + div yakalanıp sıkıştırılıyor
                    st.markdown('<div class="poll-marker"></div>', unsafe_allow_html=True)
                    if st.button(f"🗳️ {opt_text}", key=f"vote_{pid}_{idx}", use_container_width=True):
                        social.vote_poll(pid, st.session_state['username'], idx)
                        st.rerun()
            else:
                st.caption(f"Sonuçlar ({total_votes} Oy):")
                for opt_text, cnt in poll_res:
                    ratio = int((cnt / total_votes) * 100) if total_votes > 0 else 0
                    # HTML Progress Bar (CSS ile optimize edildi)
                    st.markdown(f"""
                    <div class="poll-bar-bg">
                        <div class="poll-bar-fill" style="width:{ratio}%;"></div>
                        <div class="poll-text"><span>{opt_text}</span><span>%{ratio}</span></div>
                    </div>""", unsafe_allow_html=True)
            st.write("") # Boşluk
            
        # --- BUTONLAR (BEĞEN / YORUM / SİL) ---
        c1, c2, c3 = st.columns([1, 1, 3])
        
        # Beğeni
        with c1:
            if st.button(f"❤️ {p_likes}", key=f"like_{pid}"):
                social.like_post(pid)
                st.rerun() # Sleep yok, direkt yenile
        
        # Yorum Aç/Kapa
        with c2:
            if st.button("💬", key=f"cmt_tog_{pid}"):
                if pid in st.session_state['open_comments']:
                    st.session_state['open_comments'].remove(pid)
                else:
                    st.session_state['open_comments'].append(pid)
                st.rerun()
                
        # Silme (Sadece sahibi veya admin)
        with c3:
            if st.session_state['username'] == p_user or st.session_state['user_role'] == 'admin':
                with st.popover("⋮"): # Üç nokta menüsü
                    if st.button("🗑️ Sil", key=f"del_p_{pid}"):
                        social.delete_post(pid)
                        st.rerun()

        # --- YORUMLAR KISMI ---
        if pid in st.session_state['open_comments']:
            comments = social.get_comments(pid)
            if comments:
                for c in comments:
                    st.markdown(f"""
                    <div style="background:rgba(0,0,0,0.2); padding:5px 10px; border-radius:8px; margin-top:2px; border-left:2px solid #334155;">
                        <span style="color:#FFD700; font-weight:bold; font-size:0.8rem;">{c[0]}</span>: 
                        <span style="color:#e2e8f0; font-size:0.85rem;">{c[1]}</span>
                    </div>""", unsafe_allow_html=True)
            else:
                st.caption("Henüz yorum yok.")
            
            # Hızlı Yorum Formu
            with st.form(f"c_form_{pid}", clear_on_submit=True):
                ct = st.text_input("Yorum...", label_visibility="collapsed")
                if st.form_submit_button("Gönder"): 
                    if ct: 
                        social.add_comment(pid, st.session_state['username'], ct)
                        st.rerun()
        
        # Ayırıcı çizgi yerine boşluk (Performans için)
        st.write("") 
