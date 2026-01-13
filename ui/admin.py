import streamlit as st
import database.users as users
import database.score as score
import database.social as social
import time

def render_admin_panel():
    st.header("🛡️ Yönetici Paneli")
    
    # Yetki Kontrolü (Güvenlik)
    if st.session_state.get('user_role') != 'admin':
        st.error("Bu sayfaya erişim yetkiniz yok!")
        return

    # Sekmeler
    tab1, tab2, tab3 = st.tabs(["👤 Kullanıcı Yönetimi", "📢 İçerik Yönetimi", "⚙️ Sistem"])

    # --- 1. KULLANICI & PUAN YÖNETİMİ ---
    with tab1:
        st.subheader("Kullanıcı İşlemleri")
        
        # Tüm kullanıcıları çek
        all_users_data = users.get_all_users_list() # [(kadi, rol, unvan), ...]
        usernames = [u[0] for u in all_users_data]
        
        selected_user = st.selectbox("Kullanıcı Seç", usernames)
        
        if selected_user:
            # Seçilen kullanıcının mevcut durumu
            u_score = score.get_total_score(selected_user)
            u_role = next((u[1] for u in all_users_data if u[0] == selected_user), "student")
            
            c1, c2, c3 = st.columns(3)
            c1.info(f"Puan: **{u_score:,}**")
            c2.info(f"Rol: **{u_role}**")
            
            st.divider()
            
            # Puan İşlemi
            st.write("💰 **Puan Ekle / Sil**")
            col_p1, col_p2, col_p3 = st.columns([2, 1, 1])
            amount = col_p1.number_input("Miktar", step=1000, value=0)
            
            if col_p2.button("➕ Ekle", use_container_width=True):
                users.admin_update_score(selected_user, amount, "Admin Hediyesi")
                st.success(f"{selected_user} kişisine {amount} puan eklendi.")
                time.sleep(1); st.rerun()
                
            if col_p3.button("➖ Sil", use_container_width=True):
                users.admin_update_score(selected_user, -amount, "Admin Cezası")
                st.warning(f"{selected_user} kişisinden {amount} puan silindi.")
                time.sleep(1); st.rerun()
            
            st.divider()
            
            # Yetki İşlemi
            st.write("👑 **Yetki Durumu**")
            new_role_select = st.selectbox("Yeni Rol", ["student", "admin"], index=0 if u_role=="student" else 1)
            if st.button("Yetkiyi Güncelle"):
                users.set_user_role(selected_user, new_role_select)
                st.success("Yetki güncellendi!")
                time.sleep(1); st.rerun()

    # --- 2. İÇERİK YÖNETİMİ (SİLME) ---
    with tab2:
        st.subheader("Son Gönderiler")
        last_posts = social.get_posts(50) # Son 50 post
        
        for p in last_posts:
            # p: (id, username, content, image, time, likes, poll)
            with st.expander(f"{p[4]} - {p[1]}: {p[2][:30]}..."):
                st.write(f"**Tam İçerik:** {p[2]}")
                st.caption(f"Beğeni: {p[5]}")
                if st.button("🗑️ Bu Gönderiyi Sil", key=f"adm_del_{p[0]}"):
                    social.delete_post(p[0])
                    st.error("Gönderi silindi.")
                    time.sleep(1); st.rerun()

    # --- 3. SİSTEM (LOGLAR VS.) ---
    with tab3:
        st.info("Sistem şu an aktif.")
        st.json(st.session_state)
