import streamlit as st
import database.users as users
import database.score as score
import database.social as social
import time

def render_admin_panel():
    st.header("🛡️ Yönetici Paneli")
    
    if st.session_state.get('user_role') != 'admin':
        st.error("Bu sayfaya erişim yetkiniz yok!")
        return

    tab1, tab2, tab3 = st.tabs(["👤 Kullanıcı", "📢 İçerik Düzenle", "⚙️ Sistem"])

    # --- 1. KULLANICI YÖNETİMİ ---
    with tab1:
        st.subheader("Kullanıcı İşlemleri")
        all_users_data = users.get_all_users_list() 
        usernames = [u[0] for u in all_users_data]
        selected_user = st.selectbox("Kullanıcı Seç", usernames)
        
        if selected_user:
            u_score = score.get_total_score(selected_user)
            u_role = next((u[1] for u in all_users_data if u[0] == selected_user), "student")
            
            c1, c2 = st.columns(2)
            c1.info(f"Puan: **{u_score:,}**")
            c2.info(f"Rol: **{u_role}**")
            
            st.divider()
            st.write("💰 **Puan Ekle / Sil**")
            cp1, cp2, cp3 = st.columns([2, 1, 1])
            amount = cp1.number_input("Miktar", step=1000, value=0)
            if cp2.button("➕ Ekle", use_container_width=True):
                users.admin_update_score(selected_user, amount, "Admin")
                st.success("Eklendi"); time.sleep(0.5); st.rerun()
            if cp3.button("➖ Sil", use_container_width=True):
                users.admin_update_score(selected_user, -amount, "Admin")
                st.warning("Silindi"); time.sleep(0.5); st.rerun()
            
            st.divider()
            st.write("👑 **Yetki**")
            n_role = st.selectbox("Rol", ["student", "admin"], index=0 if u_role=="student" else 1)
            if st.button("Yetkiyi Güncelle"):
                users.set_user_role(selected_user, n_role)
                st.success("Güncellendi"); time.sleep(0.5); st.rerun()

    # --- 2. İÇERİK YÖNETİMİ (DÜZENLEME EKLENDİ) ---
    with tab2:
        st.subheader("Son Gönderiler")
        last_posts = social.get_posts(50)
        
        for p in last_posts:
            # p: (id, username, content, image, time, likes, poll)
            with st.expander(f"{p[4]} - {p[1]}: {p[2][:30]}..."):
                # DÜZENLEME ALANI
                new_content = st.text_area("İçeriği Düzenle:", value=p[2], key=f"edit_txt_{p[0]}")
                
                c_edit, c_del = st.columns(2)
                
                if c_edit.button("💾 Güncelle", key=f"save_{p[0]}", use_container_width=True):
                    social.update_post(p[0], new_content)
                    st.toast("Gönderi güncellendi!", icon="✅")
                    time.sleep(0.5); st.rerun()
                    
                if c_del.button("🗑️ Sil", key=f"del_{p[0]}", use_container_width=True):
                    social.delete_post(p[0])
                    st.error("Silindi!"); time.sleep(0.5); st.rerun()

    with tab3:
        st.info("Sistem aktif.")
        st.json(st.session_state)
