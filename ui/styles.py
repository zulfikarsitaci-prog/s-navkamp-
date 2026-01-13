import database.users as users

MAIN_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@700&family=Cinzel:wght@700&family=Inter:wght@400;600&display=swap');

    /* --- 1. GENEL AYARLAR --- */
    .main .block-container { 
        padding-top: 1rem !important; 
        padding-left: 0.5rem !important; 
        padding-right: 0.5rem !important; 
        max-width: 100% !important;
    }
    div[data-testid="stVerticalBlock"] { gap: 0rem !important; }
    div.stMarkdown { margin-bottom: 0px !important; }

    /* --- 2. MENÜ (TAB SİSTEMİ - %100 OKUNURLUK) --- */
    
    div[role="radiogroup"] {
        display: flex !important;
        flex-direction: row !important;
        overflow-x: auto !important; /* Yan kaydırma */
        gap: 15px !important;
        padding: 5px 5px 10px 5px !important;
        border-bottom: 1px solid rgba(255, 215, 0, 0.3); /* İnce Gold Çizgi */
        margin-bottom: 10px !important;
        -webkit-overflow-scrolling: touch;
    }
    
    /* Yuvarlak radyo butonunu tamamen GİZLE */
    div[role="radiogroup"] label div:first-child { display: none !important; }
    
    /* Menü Öğesi (Kutucuk DEĞİL, Yazı Alanı) */
    div[role="radiogroup"] label {
        background-color: transparent !important; /* Arka plan yok! */
        border: none !important;
        padding: 5px 10px !important;
        margin: 0 !important;
        min-width: auto !important;
        transition: all 0.2s;
    }
    
    /* Menü Yazıları (NET GOLD) */
    div[role="radiogroup"] label p {
        color: #94a3b8 !important; /* Pasifken Gri/Mavi */
        font-weight: 600 !important;
        font-size: 1rem !important;
        margin: 0 !important;
        white-space: nowrap !important;
    }
    
    /* SEÇİLİ OLAN MENÜ (ALTIN PARLAMA) */
    div[role="radiogroup"] label[data-checked="true"] {
        border-bottom: 3px solid #FFD700 !important; /* Altı Çizili */
        background: rgba(255, 215, 0, 0.1) !important; /* Hafif sarı zemin */
        border-radius: 5px 5px 0 0 !important;
    }
    div[role="radiogroup"] label[data-checked="true"] p {
        color: #FFD700 !important; /* Parlak Gold Yazı */
        font-weight: 800 !important;
        text-shadow: 0 0 8px rgba(255, 215, 0, 0.5) !important;
    }

    /* --- 3. HİKAYELER (INSTAGRAM MODU - YAN YANA) --- */
    
    /* Hikayelerin olduğu satırı yakala */
    div[data-testid="stHorizontalBlock"]:has(.story-container) {
        display: flex !important;
        flex-wrap: nowrap !important; /* Asla alt satıra geçme */
        overflow-x: auto !important;   /* Kaydır */
        overflow-y: hidden !important;
        gap: 12px !important;          /* Aralarındaki boşluk */
        padding: 10px 0 !important;
        align-items: flex-start !important;
        justify-content: flex-start !important;
    }

    /* Tekil Hikaye Kutusu */
    div[data-testid="column"]:has(.story-container) {
        flex: 0 0 auto !important; /* Genişleme, Sabit Kal */
        width: 70px !important;    /* Sabit Genişlik */
        min-width: 70px !important;
        max-width: 70px !important;
        padding: 0 !important;
        margin: 0 !important;
    }
    
    /* Hikaye Görünmez Buton */
    .story-btn button {
        height: 70px !important;
        width: 70px !important;
        position: absolute !important;
        top: -70px !important; /* Görselin üstüne çıkar */
        left: 0 !important;
        opacity: 0 !important;
        z-index: 10 !important;
    }

    /* --- 4. POST KARTLARI (BUZLU CAM GERİ GELDİ) --- */
    
    .post-card {
        background: rgba(30, 41, 59, 0.70) !important; /* Yarı saydam lacivert */
        backdrop-filter: blur(10px) !important;        /* Buzlu cam */
        -webkit-backdrop-filter: blur(10px) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 12px;
        padding: 12px;
        margin-bottom: 12px !important;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.2);
    }
    
    .post-header { display: flex; align-items: center; padding-bottom: 8px; border-bottom: 1px solid rgba(255,255,255,0.05); margin-bottom: 8px; }
    .post-content { color: #e2e8f0; font-size: 0.95rem; line-height: 1.4; margin-bottom: 8px; }
    .post-image { width: 100%; border-radius: 8px; margin-top: 5px; border: 1px solid rgba(255,255,255,0.1); }

    /* Buton Düzenlemeleri */
    div[data-testid="stPopover"] { display: inline-block !important; margin-top: -10px !important; }
    div[data-testid="column"] .stButton { margin-top: -10px !important; margin-bottom: -10px !important; }
    
    /* Anket Çubukları */
    .poll-bar-bg { background: rgba(255,255,255,0.1); border-radius: 5px; height: 25px; position:relative; margin-bottom:5px; }
    .poll-bar-fill { background: linear-gradient(90deg, #eab308, #ca8a04); height: 100%; border-radius: 5px; position: absolute; top: 0; left: 0; }
    .poll-text { position: relative; z-index: 2; padding: 0 8px; line-height: 25px; font-size: 0.8rem; color: white; display: flex; justify-content: space-between; font-weight: bold; text-shadow: 0 1px 2px black; }

    /* Çerçeveler */
    .avatar-container { position: relative; display: inline-block; width: 40px; height: 40px; }
    .avatar-img { width: 100%; height: 100%; border-radius: 50%; object-fit: cover; border: 2px solid rgba(255,255,255,0.1); }
    .frame-overlay { position: absolute; top: -15%; left: -15%; width: 130%; height: 130%; pointer-events: none; z-index: 2; background-size: contain; background-repeat: no-repeat; background-position: center; }
    
    /* Çerçeve Stilleri (Basitleştirilmiş) */
    .frame-Gold { border: 2px solid #FFD700; box-shadow: 0 0 5px #FFD700; border-radius: 50%; }
    .frame-Neon { border: 2px solid #00ffff; box-shadow: 0 0 5px #00ffff; border-radius: 50%; }
    .frame-Fire { border: 2px solid #ff4500; border-radius: 50%; }
    .frame-King { border: 3px solid #ffd700; border-radius: 50%; }
    /* ... Diğer çerçeveler varsayılan border alır ... */

    /* Login Neon */
    .login-main { font-family: 'Cinzel', serif; font-size: 2rem; color: #FFD700; text-shadow: 0 0 10px #FFD700; margin: 10px 0; animation: neon 2s infinite alternate; }
    @keyframes neon { from { text-shadow: 0 0 5px #FFD700; } to { text-shadow: 0 0 20px #FFD700, 0 0 30px #FF8C00; } }
</style>
"""

def get_user_display_html(username, size=40):
    ava, frame, name_style, _, font_style, title = users.get_user_styles(username)
    img_src = f"data:image/jpeg;base64,{ava}" if ava else "https://via.placeholder.com/150/CCCCCC/FFFFFF?text=U"
    
    # Çerçeve HTML (CSS Class yerine inline style veya basit class)
    frame_class = f"frame-{frame}" if frame else ""
    
    # Basit ve Hızlı HTML Yapısı
    return f"""
    <div style="display:flex; align-items:center; gap:10px;">
        <div class="avatar-container {frame_class}" style="width:{size}px; height:{size}px;">
            <img src="{img_src}" style="width:100%; height:100%; border-radius:50%; object-fit:cover;">
        </div>
        <div style="font-weight:bold; color:#e2e8f0; font-size:0.9rem;">
            {username} 
            {f'<span style="background:#334155; padding:1px 4px; border-radius:4px; font-size:0.6rem; color:#FFD700; border:1px solid #FFD700; margin-left:4px;">{title}</span>' if title and title != 'Çırak' else ''}
        </div>
    </div>
    """

def get_post_style_css(username):
    return "" # Performans için boş
