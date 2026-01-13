def render_stories():
    stories = social.get_active_stories()
    if stories:
        st.markdown("### 🔥 Hikayeler")
        
        # --- KRİTİK DEĞİŞİKLİK ---
        # Eskiden: cols = st.columns(len(stories)) -> Bu, az hikaye varsa tüm ekrana yayıyordu.
        # Şimdi: Hikaye sayısı kadar kolon açıyoruz ama CSS (styles.py) bunları 75px genişliğe zorluyor.
        # Bu yüzden Python tarafında bir şey değiştirmene gerek kalmadı, CSS işi halledecek.
        # Ancak emin olmak için yine de standart columns kullanıyoruz.
        
        cols = st.columns(len(stories))
        
        for i, story in enumerate(stories):
            sid, s_user, s_content, s_img, s_time = story
            
            with cols[i]:
                ava, _, _, _, _, _ = users.get_user_styles(s_user)
                img_src = f"data:image/jpeg;base64,{ava}" if ava else "https://via.placeholder.com/150/CCCCCC/FFFFFF?text=U"
                
                # Yuvarlak İkon
                st.markdown(f"""
                <div style="text-align:center;">
                    <div style="width: 60px; height: 60px; border-radius: 50%; padding: 2px; background: linear-gradient(45deg, #f09433 0%, #e6683c 25%, #dc2743 50%, #cc2366 75%, #bc1888 100%); display: inline-block;">
                        <img src="{img_src}" style="width: 100%; height: 100%; border-radius: 50%; border: 2px solid #0f172a; object-fit: cover;">
                    </div>
                    <div style="font-size:0.7rem; color:#cbd5e1; margin-top:2px; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">{s_user}</div>
                </div>
                """, unsafe_allow_html=True)
                
                # Görünmez Tıklama Alanı (CSS ile "story-btn" sınıfını yakalıyoruz)
                st.markdown('<div class="story-btn">', unsafe_allow_html=True)
                if st.button(s_user, key=f"story_{sid}"):
                    st.session_state['active_story_index'] = i
                    st.session_state['active_story_open'] = True
                st.markdown('</div>', unsafe_allow_html=True)

    # ... (Modal pencere kodları aynı kalabilir) ...
    # (Kodun geri kalanı aynı)
