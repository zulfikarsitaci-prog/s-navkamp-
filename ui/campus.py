import streamlit as st
import re
import time
import database.social as social
import database.score as score
import database.users as users
from .styles import get_user_display_html, get_post_style_css

def render_stories():
    stories = social.get_active_stories()
    
    if stories:
        st.markdown("### 🔥 Hikayeler")
        
        # Flex container oluşturmak için columns kullanıyoruz
        cols = st.columns(len(stories))
        
        for i, story in enumerate(stories):
            sid, s_user, s_content, s_img, s_time = story
            
            with cols[i]:
                # Avatar Verisi
                ava, _, _, _, _, _ = users.get_user_styles(s_user)
                img_src = f"data:image/jpeg;base64,{ava}" if ava else "https://via.placeholder.com/150/CCCCCC/FFFFFF?text=U"
                
                # HİKAYE KUTUSU (HTML)
                # 'story-container' sınıfı CSS tarafından yakalanıp yan yana dizilir.
                st.markdown(f"""
                <div class="story-container" style="display:flex; flex-direction:column; align-items:center; width:70px;">
                    <div style="width: 60px; height: 60px; border-radius: 50%; padding: 2px; background: linear-gradient(45deg, #f09433, #bc1888);">
                        <img src="{img_src}" style="width: 100%; height: 100%; border-radius: 50%; border: 2px solid #0f172a; object-fit: cover;">
                    </div>
                    <div style="font-size:0.7rem; color:#cbd5e1; margin-top:4px; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; max-width:65px; text-align:center;">
                        {s_user}
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Tıklama Butonu (Görünmez, üstüne biner)
                st.markdown('<div class="story-btn">', unsafe_allow_html=True)
                if st.button(f"view_{sid}", key=f"sbtn_{sid}"):
                    st.session_state['active_story_index'] = i
                    st.session_state['active_story_open'] = True
                st.markdown('</div>', unsafe_allow_html=True)

    # --- MODAL (Aynı Kalıyor) ---
    if st.session_state.get('active_story_open') and stories:
        idx = st.session_state.get('active_story_index', 0)
        idx = idx % len(stories) # Index hatasını önle
        
        current_story = stories[idx]
        sid, s_user, s_content, s_img, s_time = current_story
        
        @st.dialog(f"Hikaye: {s_user}")
        def show_story_modal():
            if s_img: st.image(f"data:image/jpeg;base64,{s_img}", use_container_width=True)
            if s_content: st.write(f"📝 {s_content}")
            st.caption(f"🕒 {s_time}")
            c1, c2, c3 = st.columns([1, 4, 1])
            with c1: 
                if st.button("⬅️", key="prev"): st.session_state['active_story_index'] = idx - 1; st.rerun()
            with c3: 
                if st.button("➡️", key="next"): st.session_state['active_story_index'] = idx + 1; st.rerun()
        show_story_modal()

    if stories: st.write("")

def render_campus_wall():
    render_stories()
    
    st.subheader("Kampüs Duvar")
    
    # Paylaşım Alanı
    my_score = score.get_total_score(st.session_state['username'])
    POST_COST = 100000
    if my_score >= POST_COST or st.session_state['user_role'] == 'admin':
        with st.expander(f"✨ Paylaşım (-{POST_COST:,} P)"):
            ptype = st.radio("Tip", ["Normal", "Anket"], horizontal=True, label_visibility="collapsed")
            with st.form("share"):
                txt = st.text_area("İçerik")
                if ptype=="Normal":
                    img = st.file_uploader("Görsel", type=['jpg','png'])
                    if st.form_submit_button("Paylaş"):
                        score.add_score(st.session_state['username'], -POST_COST, "Post")
                        social.add_post(st.session_state['username'], txt, img); st.rerun()
                else:
                    opts = st.text_input("Şıklar (virgülle)")
                    if st.form_submit_button("Anket"):
                        social.add_poll_post(st.session_state['username'], txt, opts.split(",")); st.rerun()

    # Akış
    posts = social.get_posts(40)
    for p in posts:
        pid, p_user, p_content, p_img, p_time, p_likes, p_poll = p
        
        st.markdown(f"""
        <div class="post-card">
            <div class="post-header">
                {get_user_display_html(p_user, size=35)}
                <span style="color:#94a3b8; font-size:0.7rem; margin-left:auto;">{p_time[-5:]}</span>
            </div>
            <div class="post-content">{p_content if p_content else ''}</div>
            {f'<img src="data:image/jpeg;base64,{p_img}" class="post-image">' if p_img else ''}
        </div>
        """, unsafe_allow_html=True)
        
        # Anket
        if p_poll:
            res, total, voted = social.get_poll_results(pid, p_poll)
            if not voted:
                for idx, (txt, cnt) in enumerate(res):
                    st.markdown('<div class="poll-marker"></div>', unsafe_allow_html=True) # CSS yakalayıcı
                    if st.button(f"⚪ {txt}", key=f"vt_{pid}_{idx}", use_container_width=True):
                        social.vote_poll(pid, st.session_state['username'], idx); st.rerun()
            else:
                for txt, cnt in res:
                    ratio = int((cnt/total)*100) if total else 0
                    st.markdown(f"""<div class="poll-bar-bg"><div class="poll-bar-fill" style="width:{ratio}%"></div><div class="poll-text"><span>{txt}</span><span>%{ratio}</span></div></div>""", unsafe_allow_html=True)
        
        # Butonlar
        c1, c2, c3 = st.columns([1, 1, 4])
        with c1: 
            if st.button(f"❤️ {p_likes}", key=f"lk_{pid}"): social.like_post(pid); st.rerun()
        with c2:
            if st.button("💬", key=f"cm_{pid}"): 
                if pid in st.session_state['open_comments']: st.session_state['open_comments'].remove(pid)
                else: st.session_state['open_comments'].append(pid)
                st.rerun()
        with c3:
             if st.session_state['username'] == p_user or st.session_state['user_role'] == 'admin':
                with st.popover("⋮"):
                    if st.button("Sil", key=f"d_{pid}"): social.delete_post(pid); st.rerun()
        
        # Yorumlar
        if pid in st.session_state['open_comments']:
            cmts = social.get_comments(pid)
            if cmts:
                for c in cmts: st.markdown(f"<div style='font-size:0.85rem; color:#cbd5e1; margin-left:10px;'><b>{c[0]}</b>: {c[1]}</div>", unsafe_allow_html=True)
            with st.form(f"cf_{pid}", clear_on_submit=True):
                if st.form_submit_button("Yolla") and (val := st.text_input("Yorum", label_visibility="collapsed")):
                    social.add_comment(pid, st.session_state['username'], val); st.rerun()
        
        st.write("")
