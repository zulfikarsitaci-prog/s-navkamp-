import streamlit as st
import re
import database.social as social
import database.score as score
from .styles import get_user_display_html, get_post_style_css

def extract_youtube_link(text):
    if not text: return None
    match = re.search(r'(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/(watch\?v=|embed/|v/|live/|.+\?v=)?([^&=%\?]{11})', text)
    if match: return f"https://www.youtube.com/watch?v={match.group(6)}"
    return None

def render_campus_wall():
    st.subheader("Kampüs Duvar")
    
    my_score = score.get_total_score(st.session_state['username'])
    POST_THRESHOLD = 1000000
    POST_COST = 100000
    
    if my_score >= POST_THRESHOLD or st.session_state['user_role'] == 'admin':
        with st.expander(f"✨ Paylaşım (-{POST_COST:,} P)", expanded=False):
            with st.form("sh"):
                def_val = st.session_state.get('draft_content', "")
                txt = st.text_area("İçerik", value=def_val); img = st.file_uploader("Resim", type=['png','jpg'])
                if st.form_submit_button("Paylaş"):
                    if my_score >= POST_COST:
                        score.add_score(st.session_state['username'], -POST_COST, "Post")
                        social.add_post(st.session_state['username'], txt, img)
                        st.session_state['draft_content'] = ""
                        st.rerun()
                    else: st.error("Bakiye Yetersiz!")
    else:
        st.info(f"🔒 Paylaşım için {POST_THRESHOLD:,} P gerekli.")

    for p in social.get_posts(20):
        # HTML Render
        st.markdown(f"""
        <div class="post-card">
            <div class="post-header">
                {get_user_display_html(p[1], size=35)}
                <span style="color:#94a3b8;font-size:0.7rem;margin-left:auto;">{p[4]}</span>
            </div>
            <div class="{get_post_style_css(p[1])} post-content">{p[2] if p[2] else ''}</div>
            {f'<img src="data:image/jpeg;base64,{p[3]}" class="post-image">' if p[3] else ''}
        </div>
        """, unsafe_allow_html=True)
        
        if p[2]:
            yt = extract_youtube_link(p[2])
            if yt: st.video(yt)

        c1, c2 = st.columns([1, 4]) 
        with c1:
            if st.button(f"❤️ {p[5]}", key=f"l_{p[0]}"): 
                social.like_post(p[0]); st.rerun()
        with c2:
            with st.popover("➕", use_container_width=False):
                if st.button("💬 Yorum Yap", key=f"c_btn_{p[0]}"):
                    if p[0] in st.session_state['open_comments']: st.session_state['open_comments'].remove(p[0])
                    else: st.session_state['open_comments'].append(p[0])
                    st.rerun()
                if st.button("🔄 Paylaş", key=f"r_{p[0]}"):
                    st.session_state['draft_content'] = f"Alıntı (@{p[1]}): {p[2]}"; st.rerun()
                if st.session_state['username'] == p[1] or st.session_state['user_role'] == 'admin':
                    if st.button("🗑️ Sil", key=f"d_{p[0]}"): social.delete_post(p[0]); st.rerun()

        if p[0] in st.session_state['open_comments']:
            comments = social.get_comments(p[0])
            if comments:
                for c in comments: st.markdown(f"<div class='comment-box'>{get_user_display_html(c[0], size=20)} &nbsp; {c[1]}</div>", unsafe_allow_html=True)
            else: st.caption("Henüz yorum yok.")
            
            with st.form(f"c_form_{p[0]}", clear_on_submit=True):
                ct = st.text_input("Yorum Yaz...", label_visibility="collapsed")
                if st.form_submit_button("Gönder"): 
                    if ct: social.add_comment(p[0], st.session_state['username'], ct); st.rerun()
        st.write("") 
