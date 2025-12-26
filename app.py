import streamlit as st
import streamlit.components.v1 as components
import json
import os

# Sayfa Ayarları
st.set_page_config(
    page_title="Finans İmparatoru & Blok Oyunu",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Başlık ve Açıklama (İstersen kaldırabilirsin)
# st.title("Finans İmparatoru") 

def load_game():
    # 1. JSON Verisini Oku (Python Tarafında)
    try:
        with open('lifesim_data.json', 'r', encoding='utf-8') as f:
            game_data = json.load(f)
        # JSON'ı string formatına çevir (HTML içine gömmek için)
        json_str = json.dumps(game_data)
    except FileNotFoundError:
        st.error("lifesim_data.json bulunamadı!")
        return

    # 2. HTML Dosyasını Oku
    try:
        with open('game.html', 'r', encoding='utf-8') as f:
            html_content = f.read()
    except FileNotFoundError:
        st.error("game.html bulunamadı!")
        return

    # 3. Python'daki Veriyi HTML'in İçine Enjekte Et
    # HTML kodunda '// PYTHON_DATA_HERE' yazan yeri bulup gerçek veriyle değiştiriyoruz.
    # Bu sayede 'fetch' hatası almazsın, veri garanti yüklenir.
    injected_html = html_content.replace(
        '// PYTHON_DATA_HERE', 
        f'let scenarios = {json_str}; console.log("Veri Python üzerinden yüklendi");'
    )

    # 4. Oyunu Ekrana Bas (Tam Ekran gibi)
    components.html(injected_html, height=800, scrolling=False)

if __name__ == "__main__":
    load_game()
