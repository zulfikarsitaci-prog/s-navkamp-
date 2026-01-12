import streamlit as st
import database.score as score
import database.social as social

def render_shop():
    st.subheader("🛒 Kampüs Mağazası")
    my_score = score.get_total_score(st.session_state['username'])
    st.info(f"💰 Mevcut Bakiyen: **{my_score:,} Puan**")

    # Kategorileri (Sekmeleri) oluştur
    categories = list(Items.keys())
    tabs = st.tabs(categories)

    for idx, category in enumerate(categories):
        with tabs[idx]:
            items_list = Items[category]
            cols = st.columns(3)
            
            for i, item in enumerate(items_list):
                with cols[i % 3]:
                    # Önizleme HTML'i
                    preview_html = ""
                    if item['t'] == 'frame':
                        # Çerçeve önizlemesi (Boş bir yuvarlak)
                        preview_html = f"""<div class="{item['css']}" style="width:50px; height:50px; margin:0 auto; background:rgba(255,255,255,0.1);"></div>"""
                    elif item['t'] == 'name':
                        # İsim önizlemesi
                        preview_html = f"""<div class="{item['css']}" style="font-size:0.9rem;">{st.session_state['username']}</div>"""
                    elif item['t'] == 'font':
                         # Font önizlemesi
                        preview_html = f"""<div class="{item['css']}" style="font-size:1.1rem;">Abc</div>"""
                    else:
                        # Ünvan
                        preview_html = f"""<div style="font-size:0.9rem; color:#94a3b8;">{item['v']}</div>"""

                    # Kart Yapısı
                    st.markdown(f"""
                    <div class="shop-card">
                        <div style="margin-bottom:10px; height:50px; display:flex; align-items:center; justify-content:center;">{preview_html}</div>
                        <div class="shop-title">{item['n']}</div>
                        <div class="shop-price">{item['c']:,} P</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if st.button("Al", key=f"buy_{category}_{i}", use_container_width=True):
                        # Not: buy_item fonksiyonunda 't' parametresi 'item_type' a denk gelir
                        # 'v' parametresi de 'item_value' ya denk gelir.
                        ok, msg = users.buy_item(st.session_state['username'], item['t'], item['v'], item['c'])
                        if ok:
                            st.success("Hayırlı olsun!")
                            st.balloons()
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error(msg)
            st.write("")

    Items = {
    "🖼️ Çerçeve": [
        {"n": "Gold", "c": 50000, "t": "frame", "v": "Gold", "css": "frame-Gold"},
        {"n": "Doğa", "c": 75000, "t": "frame", "v": "Nature", "css": "frame-Nature"}, # YENİ
        {"n": "Buz", "c": 100000, "t": "frame", "v": "Ice", "css": "frame-Ice"},       # YENİ
        {"n": "Neon", "c": 150000, "t": "frame", "v": "Neon", "css": "frame-Neon"},
        {"n": "Alev", "c": 300000, "t": "frame", "v": "Fire", "css": "frame-Fire"},
        {"n": "Matrix", "c": 500000, "t": "frame", "v": "Matrix", "css": "frame-Matrix"},
        {"n": "Siber", "c": 1500000, "t": "frame", "v": "Cyber", "css": "frame-Cyber"},   # YENİ
        {"n": "Kral", "c": 2000000, "t": "frame", "v": "King", "css": "frame-King"},
        {"n": "Cehennem", "c": 3500000, "t": "frame", "v": "Inferno", "css": "frame-Inferno"}, # YENİ
        {"n": "İmparator", "c": 5000000, "t": "frame", "v": "Emperor", "css": "frame-Emperor"} # YENİ
    ],
    "⚽ Takımlar": [ # YENİ KATEGORİ
        {"n": "Galatasaray", "c": 500000, "t": "frame", "v": "GS", "css": "frame-GS"},
        {"n": "Fenerbahçe", "c": 500000, "t": "frame", "v": "FB", "css": "frame-FB"},
        {"n": "Beşiktaş", "c": 500000, "t": "frame", "v": "BJK", "css": "frame-BJK"},
        {"n": "Trabzonspor", "c": 500000, "t": "frame", "v": "TS", "css": "frame-TS"},
        {"n": "Milli Takım", "c": 1000000, "t": "frame", "v": "TR", "css": "frame-TR"}
    ],
    "✨ İsim": [
        {"n": "Glitch", "c": 100000, "t": "name", "v": "Glitch", "css": "name-Glitch"},
        {"n": "Alevli", "c": 400000, "t": "name", "v": "Fire", "css": "name-Fire"},
        {"n": "Buzlu", "c": 600000, "t": "name", "v": "Ice", "css": "name-Ice"}, # YENİ
        {"n": "Altın", "c": 750000, "t": "name", "v": "Gold", "css": "name-Gold"},
        {"n": "Gökkuşağı", "c": 1000000, "t": "name", "v": "Rainbow", "css": "name-Rainbow"}
    ],
    "🔤 Font": [
        {"n": "Cinzel", "c": 150000, "t": "font", "v": "Cinzel", "css": "font-Cinzel"},
        {"n": "Orbitron", "c": 250000, "t": "font", "v": "Orbitron", "css": "font-Orbitron"},
        {"n": "Rye", "c": 350000, "t": "font", "v": "Rye", "css": "font-Rye"},
        {"n": "Dans", "c": 500000, "t": "font", "v": "Dancing", "css": "font-Dancing"},
        {"n": "Metalik", "c": 1000000, "t": "font", "v": "Metallic", "css": "font-Metallic"}
    ],
    "🔰 Ünvan": [
        {"n": "Çırak", "c": 10000, "t": "title", "v": "Çırak", "css": ""},
        {"n": "Usta", "c": 100000, "t": "title", "v": "Usta", "css": ""},
        {"n": "Bilgin", "c": 500000, "t": "title", "v": "Bilgin", "css": ""},
        {"n": "Kahin", "c": 1000000, "t": "title", "v": "Kahin", "css": ""}, # YENİ
        {"n": "Efsane", "c": 2500000, "t": "title", "v": "Efsane", "css": ""}, # YENİ
        {"n": "LORD", "c": 5000000, "t": "title", "v": "LORD", "css": ""}
    ]
}

    
    tabs = st.tabs(["Ürünler", "🎁 Hediye Gönder"])
    
    with tabs[0]:
        cat_tabs = st.tabs(list(items.keys()))
        for i, (cat, products) in enumerate(items.items()):
            with cat_tabs[i]:
                html_code = '<div class="shop-grid">'
                for p in products:
                    buy_link = f"?action=buy&u={st.session_state['username']}&t={p['t']}&v={p['v']}&c={p['c']}"
                    preview = ""
                    if p['t'] == 'frame': preview = f'<div style="position:relative;width:40px;height:40px;"><img src="https://via.placeholder.com/40/CCCCCC/FFFFFF?text=U" style="border-radius:50%;"><div class="{p["css"]}" style="position:absolute;top:-3px;left:-3px;width:46px;height:46px;"></div></div>'
                    elif p['t'] == 'name': preview = f'<div class="{p["css"]}" style="font-size:0.7rem">İsim</div>'
                    elif p['t'] == 'font': preview = f'<div class="{p["css"]}" style="font-size:0.9rem">Aa</div>'
                    elif p['t'] == 'title': preview = f'<span class="title-badge">{p["v"]}</span>'
                    
                    html_code += f"""<div class="shop-item">{preview}<div class="shop-name">{p['n']}</div><a href="{buy_link}" target="_top" style="text-decoration:none;width:100%;"><div class="shop-price">{p['c']:,} P</div></a></div>"""
                html_code += "</div>"
                st.markdown(html_code, unsafe_allow_html=True)

    with tabs[1]:
        st.info("Arkadaşına hediye gönder! (Puan senden düşer)")
        target_user = st.selectbox("Kime:", social.get_searchable_users(st.session_state['username']))
        gifts = [
            {"n": "Sıcak Çay", "c": 2000, "i": "☕"}, {"n": "Kahve", "c": 5000, "i": "🧖"}, {"n": "Çikolata", "c": 8000, "i": "🍫"}, 
            {"n": "Gül", "c": 15000, "i": "🌹"}, {"n": "Tost", "c": 20000, "i": "🥪"}, {"n": "Hamburger", "c": 30000, "i": "🍔"},
            {"n": "Ayıcık", "c": 60000, "i": "🧸"}, {"n": "Kupa", "c": 100000, "i": "🏆"}, {"n": "Elmas", "c": 500000, "i": "💎"}, {"n": "Araba", "c": 2000000, "i": "🏎️"}
        ]
        html_code = '<div class="shop-grid">'
        for g in gifts:
            gift_link = f"?action=gift&u={st.session_state['username']}&t={target_user}&g={g['n']}&c={g['c']}"
            html_code += f"""<div class="shop-item" style="height:120px;"><div class="gift-icon">{g['i']}</div><div class="shop-name">{g['n']}</div><a href="{gift_link}" target="_top" style="text-decoration:none;width:100%;"><div class="shop-price">{g['c']:,}</div></a></div>"""
        html_code += "</div>"
        st.markdown(html_code, unsafe_allow_html=True)
