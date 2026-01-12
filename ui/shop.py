import streamlit as st
import time
import database.users as users
import database.score as score

# --- ÜRÜN KATALOĞU ---
# Bu listenin fonksiyonun DIŞINDA ve ÜSTÜNDE olması şarttır.
Items = {
    "🖼️ Çerçeve": [
        {"n": "Gold", "c": 50000, "t": "frame", "v": "Gold", "css": "frame-Gold"},
        {"n": "Doğa", "c": 75000, "t": "frame", "v": "Nature", "css": "frame-Nature"},
        {"n": "Buz", "c": 100000, "t": "frame", "v": "Ice", "css": "frame-Ice"},
        {"n": "Neon", "c": 150000, "t": "frame", "v": "Neon", "css": "frame-Neon"},
        {"n": "Alev", "c": 300000, "t": "frame", "v": "Fire", "css": "frame-Fire"},
        {"n": "Matrix", "c": 500000, "t": "frame", "v": "Matrix", "css": "frame-Matrix"},
        {"n": "Siber", "c": 1500000, "t": "frame", "v": "Cyber", "css": "frame-Cyber"},
        {"n": "Kral", "c": 2000000, "t": "frame", "v": "King", "css": "frame-King"},
        {"n": "Cehennem", "c": 3500000, "t": "frame", "v": "Inferno", "css": "frame-Inferno"},
        {"n": "İmparator", "c": 5000000, "t": "frame", "v": "Emperor", "css": "frame-Emperor"}
    ],
    "⚽ Takımlar": [
        {"n": "Galatasaray", "c": 500000, "t": "frame", "v": "GS", "css": "frame-GS"},
        {"n": "Fenerbahçe", "c": 500000, "t": "frame", "v": "FB", "css": "frame-FB"},
        {"n": "Beşiktaş", "c": 500000, "t": "frame", "v": "BJK", "css": "frame-BJK"},
        {"n": "Trabzonspor", "c": 500000, "t": "frame", "v": "TS", "css": "frame-TS"},
        {"n": "Milli Takım", "c": 1000000, "t": "frame", "v": "TR", "css": "frame-TR"}
    ],
    "✨ İsim": [
        {"n": "Glitch", "c": 100000, "t": "name_style", "v": "Glitch", "css": "name-Glitch"},
        {"n": "Alevli", "c": 400000, "t": "name_style", "v": "Fire", "css": "name-Fire"},
        {"n": "Buzlu", "c": 600000, "t": "name_style", "v": "Ice", "css": "name-Ice"},
        {"n": "Altın", "c": 750000, "t": "name_style", "v": "Gold", "css": "name-Gold"},
        {"n": "Gökkuşağı", "c": 1000000, "t": "name_style", "v": "Rainbow", "css": "name-Rainbow"}
    ],
    "🔤 Font": [
        {"n": "Cinzel", "c": 150000, "t": "font_style", "v": "Cinzel", "css": "font-Cinzel"},
        {"n": "Orbitron", "c": 250000, "t": "font_style", "v": "Orbitron", "css": "font-Orbitron"},
        {"n": "Rye", "c": 350000, "t": "font_style", "v": "Rye", "css": "font-Rye"},
        {"n": "Dans", "c": 500000, "t": "font_style", "v": "Dancing", "css": "font-Dancing"},
        {"n": "Metalik", "c": 1000000, "t": "font_style", "v": "Metallic", "css": "font-Metallic"}
    ],
    "🔰 Ünvan": [
        {"n": "Çırak", "c": 10000, "t": "title", "v": "Çırak", "css": ""},
        {"n": "Usta", "c": 100000, "t": "title", "v": "Usta", "css": ""},
        {"n": "Bilgin", "c": 500000, "t": "title", "v": "Bilgin", "css": ""},
        {"n": "Kahin", "c": 1000000, "t": "title", "v": "Kahin", "css": ""},
        {"n": "Efsane", "c": 2500000, "t": "title", "v": "Efsane", "css": ""},
        {"n": "LORD", "c": 5000000, "t": "title", "v": "LORD", "css": ""}
    ]
}

def render_shop():
    st.subheader("🛒 Kampüs Mağazası")
    
    # Kullanıcı Puanını Çek
    my_score = score.get_total_score(st.session_state['username'])
    st.info(f"💰 Mevcut Bakiyen: **{my_score:,} Puan**")

    # Kategorileri (Sekmeleri) oluştur
    categories = list(Items.keys())
    tabs = st.tabs(categories)

    for idx, category in enumerate(categories):
        with tabs[idx]:
            items_list = Items[category]
            
            # Responsive Grid (3 kolonlu)
            cols = st.columns(3)
            
            for i, item in enumerate(items_list):
                with cols[i % 3]:
                    # --- ÖNİZLEME HTML OLUŞTURMA ---
                    preview_html = ""
                    
                    if item['t'] == 'frame':
                        # Çerçeve: Boş bir div üzerinde çerçeve CSS'ini göster
                        preview_html = f"""<div class="{item['css']}" style="width:50px; height:50px; margin:0 auto; background:rgba(255,255,255,0.1);"></div>"""
                    
                    elif item['t'] == 'name_style': # Veritabanında sütun adı 'name_style'
                        # İsim Stili: Kullanıcı adını o stilde yaz
                        preview_html = f"""<div class="{item['css']}" style="font-size:0.9rem;">{st.session_state['username']}</div>"""
                    
                    elif item['t'] == 'font_style': # Veritabanında sütun adı 'font_style'
                         # Font: 'Abc' yazısını o fontta yaz
                        preview_html = f"""<div class="{item['css']}" style="font-size:1.1rem;">Abc</div>"""
                    
                    else: # Title (Ünvan)
                        # Düz yazı olarak ünvanı göster
                        preview_html = f"""<div style="font-size:0.8rem; color:#94a3b8; font-weight:bold;">{item['v']}</div>"""

                    # --- KART HTML ---
                    st.markdown(f"""
                    <div class="shop-card">
                        <div style="margin-bottom:10px; height:50px; display:flex; align-items:center; justify-content:center;">
                            {preview_html}
                        </div>
                        <div class="shop-title">{item['n']}</div>
                        <div class="shop-price">{item['c']:,} P</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # --- SATIN AL BUTONU ---
                    if st.button("Al", key=f"buy_{category}_{i}", use_container_width=True):
                        # Veritabanı sütun isimleri ile item['t'] eşleşmeli
                        # name -> name_style, font -> font_style olarak düzelttim yukarıdaki sözlükte.
                        ok, msg = users.buy_item(st.session_state['username'], item['t'], item['v'], item['c'])
                        if ok:
                            st.success("Hayırlı olsun!")
                            st.balloons()
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error(msg)
            
            st.write("") # Alt boşluk
