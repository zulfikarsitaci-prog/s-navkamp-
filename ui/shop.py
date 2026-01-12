import streamlit as st
import time
import database.users as users
import database.score as score

def render_shop():
    st.subheader("🛒 Kampüs Mağazası")
    
    # Kullanıcının Puanı
    my_score = score.get_total_score(st.session_state['username'])
    st.info(f"💰 Mevcut Bakiyen: **{my_score:,} Puan**")

    # Sekmeler
    tab1, tab2 = st.tabs(["Standart Ürünler", "💎 Premium & Özel"])

    # --- 1. STANDART SEKME ---
    with tab1:
        items_std = [
            {"name": "Neon Çerçeve", "type": "frame", "val": "Neon", "cost": 15000, "img": "🔵"},
            {"name": "Alev Çerçeve", "type": "frame", "val": "Fire", "cost": 25000, "img": "🔥"},
            {"name": "Matriks Çerçeve", "type": "frame", "val": "Matrix", "cost": 30000, "img": "🟢"},
            {"name": "Glitch İsim", "type": "name_style", "val": "Glitch", "cost": 50000, "img": "👾"},
        ]
        render_grid(items_std, is_premium=False)

    # --- 2. PREMIUM SEKME (YENİ EKLENENLER) ---
    with tab2:
        items_prem = [
            {"name": "KRAL TACI", "type": "frame", "val": "King", "cost": 250000, "img": "👑"},
            {"name": "ALTIN İSİM", "type": "name_style", "val": "Gold", "cost": 500000, "img": "✨"},
            {"name": "HAYALET MODU", "type": "frame", "val": "Ghost", "cost": 1000000, "img": "👻"},
            {"name": "KAHİN ÜNVANI", "type": "title", "val": "Kahin", "cost": 750000, "img": "🔮"},
        ]
        render_grid(items_prem, is_premium=True)

def render_grid(items, is_premium):
    # Responsive Grid (Yan yana 3 kutu)
    cols = st.columns(3)
    
    for i, item in enumerate(items):
        with cols[i % 3]: # 3 kolona dağıt
            # CSS Sınıfı Seçimi
            card_class = "shop-card-premium" if is_premium else "shop-card"
            price_class = "shop-price-premium" if is_premium else "shop-price"
            
            # HTML Kart Görünümü
            st.markdown(f"""
            <div class="{card_class}">
                <div style="font-size:3rem;">{item['img']}</div>
                <div class="shop-title">{item['name']}</div>
                <div class="{price_class}">{item['cost']:,} P</div>
            </div>
            """, unsafe_allow_html=True)
            
            # Satın Al Butonu (Tam genişlik)
            if st.button("Satın Al", key=f"buy_{item['val']}_{item['type']}", use_container_width=True):
                ok, msg = users.buy_item(st.session_state['username'], item['type'], item['val'], item['cost'])
                if ok:
                    st.success(msg)
                    st.balloons()
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error(msg)
            
            st.write("") # Boşluk
