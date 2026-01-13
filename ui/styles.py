import database.users as users

MAIN_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@700&family=Cinzel:wght@700&display=swap');

    /* --- 1. PERFORMANS VE GENEL AYARLAR --- */
    .main .block-container { 
        padding-top: 1rem !important; 
        padding-left: 0.2rem !important; 
        padding-right: 0.2rem !important; 
        max-width: 100% !important;
    }
    div[data-testid="stVerticalBlock"] { gap: 0rem !important; }
    div.stMarkdown { margin-bottom: 0px !important; }

    /* --- 2. MENÜ (KESİN GÖRÜNÜRLÜK ÇÖZÜMÜ) --- */
    
    div[role="radiogroup"] {
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: nowrap !important;
        overflow-x: auto !important;
        gap: 8px !important;
        padding: 5px 2px 10px 2px !important;
        border-bottom: 2px solid #B8860B;
        margin-bottom: 10px !important;
        background: transparent !important; /* Arka plan çakışmasını önle */
    }
    
    div[role="radiogroup"] label div:first-child { display: none !important; }
    
    /* BUTON KUTUSU */
    div[role="radiogroup"] label {
        background-color: #0f172a !important; /* Koyu Lacivert (Zorunlu) */
        border: 2px solid #B8860B !important;
        border-radius: 10px !important;
        padding: 8px 12px !important;
        margin: 0 !important;
        height: 40px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        min-width: auto !important;
    }
    
    /* YAZILAR (HER DURUMDA GOLD) */
    div[role="radiogroup"] label p {
        color: #FFD700 !important; /* Altın Sarısı */
        font-family: 'Orbitron', sans-serif !important;
        font-weight: 700 !important;
        font-size: 0.9rem !important; /* Mobilde taşmasın diye bir tık küçülttüm */
        margin: 0 !important;
        padding: 0 !important;
        white-space: nowrap !important;
        text-shadow: none !important; /* Performans için gölgeyi kaldırdım */
    }
    
    /* SEÇİLİ OLAN */
    div[role="radiogroup"] label[data-checked="true"] {
        background-color: #FFD700 !important; /* Sarı Zemin */
        border-color: #ffffff !important;
    }
    div[role="radiogroup"] label[data-checked="true"] p {
        color: #000000 !important; /* Siyah Yazı */
    }

    /* --- 3. KOMPAKT HİKAYELER (KÜÇÜLTÜLDÜ) --- */
    
    /* Hikaye kapsayıcısını daralt */
    div[data-testid="column"]:has(.story-btn) {
        flex: 0 0 auto !important; 
        width: 60px !important; /* Genişlik 80'den 60'a düştü */
        min-width: 60px !important;
        max-width: 60px !important;
        margin-right: 2px !important;
        padding: 0 !important;
    }

    div[data-testid="stHorizontalBlock"]:has(.story-btn) {
        gap: 0px !important;
        overflow-x: auto !important;
        padding-bottom: 5px !important;
    }

    .story-btn button {
        font-size: 0.6rem !important;
        margin-top: -3px !important;
        color: #cbd5e1 !important;
        border: none !important;
        background: transparent !important;
        width: 60px !important;
        white-space: nowrap !important;
        overflow: hidden !important;
        text-overflow: ellipsis !important;
        padding: 0 !important;
    }

    /* --- 4. OPTİMİZE EDİLMİŞ POST KARTLARI (HIZ İÇİN) --- */
    
    .post-card {
        background: rgba(15, 23, 42, 0.9) !important; /* Blur yerine düz renk (Daha hızlı) */
        border: 1px solid rgba(255, 215, 0, 0.2) !important;
        border-radius: 12px;
        padding: 10px;
        margin-bottom: 10px !important;
    }
    
    /* Admin Düzenle Alanı */
    textarea {
        background: #1e293b !important;
        color: white !important;
        border: 1px solid #475569 !important;
    }

    /* --- 5. DİĞERLERİ --- */
    div[data-testid="stPopover"] { display: inline-block !important; margin-top: -15px !important; }
    div[data-testid="stPopover"] button { border: 1px solid #475569 !important; height: 35px !important; }
    div[data-testid="column"] .stButton { margin-top: -10px !important; margin-bottom: -10px !important; }

    .post-header { display: flex; align-items: center; border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 5px; margin-bottom: 5px; }
    .post-content { color: #e2e8f0; font-size: 0.9rem; line-height: 1.3; margin-bottom: 5px; }
    .post-image { width: 100%; border-radius: 6px; margin-top: 4px; }
    
    /* Anket */
    div.poll-marker + div .stButton button { padding: 6px 10px !important; background: #1e293b !important; border: 1px solid #334155 !important; font-size: 0.85rem !important; }
    div.poll-marker + div .stButton { margin-top: -15px !important; }
    .poll-bar-bg { background: #334155; border-radius: 4px; margin-bottom: 2px; height: 20px; line-height: 20px; position:relative; }
    .poll-bar-fill { background: #3b82f6; height: 100%; position: absolute; top: 0; left: 0; }
    .poll-text { position: relative; z-index: 2; padding: 0 5px; font-size: 0.7rem; color: white; display: flex; justify-content: space-between; }

    /* Çerçeveler */
    .avatar-container { position: relative; display: inline-block; margin-right: 8px; line-height: 0; }
    .avatar-img { border-radius: 50%; object-fit: cover; border: 2px solid rgba(255,255,255,0.1); }
    .frame-overlay { position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); width: 135%; height: 135%; pointer-events: none; z-index: 2; }
    
    /* Basitleştirilmiş Çerçeve CSS'leri (Hız için gölgeleri azalttım) */
    .frame-Gold { border: 2px solid #FFD700; border-radius: 50%; }
    .frame-Neon { border: 2px solid #00ffff; border-radius: 50%; box-shadow: 0 0 5px #00ffff; }
    .frame-Fire { border: 2px solid #ff4500; border-radius: 50%; }
    .frame-King { border: 3px solid #ffd700; border-radius: 50%; }
    .frame-Matrix { border: 2px dotted #00ff00; border-radius: 50%; }
    .frame-Nature { border: 2px solid #22c55e; border-radius: 50%; }
    .frame-Ice { border: 2px solid #a5f3fc; border-radius: 50%; }
    .frame-Cyber { border: 2px dashed #00ff00; border-radius: 50%; }
    .frame-Inferno { border: 2px solid #ff4500; border-radius: 50%; border-bottom: 3px solid #8b0000; }
    .frame-Emperor { border: 3px double #FFD700; border-radius: 50%; box-shadow: 0 0 10px #800080; }
    .frame-GS { border: 3px solid #ef4444; border-radius: 50%; border-left-color: #facc15; }
    .frame-FB { border: 3px solid #1e3a8a; border-radius: 50%; border-left-color: #facc15; }
    .frame-BJK { border: 3px solid #000000; border-radius: 50%; border-left-color: #ffffff; }
    .frame-TS { border: 3px solid #800000; border-radius: 50%; border-left-color: #3b82f6; }
    .frame-TR { border: 3px solid #ef4444; border-radius: 50%; border-top-color: #ffffff; }

    .shop-title { font-size: 0.75rem; color: #e2e8f0; font-weight: bold; margin: 3px 0; }
    .shop-price { background: #10b981; color: white; padding: 2px 5px; border-radius: 6px; font-size: 0.65rem; }
    .shop-card { background: #1e293b; border: 1px solid #334155; border-radius: 10px; padding: 8px; text-align: center; height: 140px; display: flex; flex-direction: column; justify-content: space-between; align-items: center; }
    .shop-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px; margin-top: 5px; }
    
    .login-main { font-family: 'Cinzel', serif; font-size: 2rem; margin: 10px 0; font-weight: bold; color: #FFD700; text-shadow: 0 0 5px #FFD700; }
</style>
"""

def get_user_display_html(username, size=40):
    ava, frame, name_style, _, font_style, title = users.get_user_styles(username)
    img_src = f"data:image/jpeg;base64,{ava}" if ava else "https://via.placeholder.com/150/CCCCCC/FFFFFF?text=U"
    f_html = f'<div class="frame-overlay frame-{frame}"></div>' if frame else ""
    # İsim ve unvan HTML'ini basitleştirip hızlandırıyoruz
    return f"""<div style="display:flex;align-items:center;"><div class="avatar-container" style="width:{size}px; height:{size}px;"><img src="{img_src}" class="avatar-img" style="width:100%; height:100%;">{f_html}</div><div style="margin-left:10px;font-weight:bold;color:#e2e8f0;font-size:0.9rem;">{username}</div></div>"""

def get_post_style_css(username):
    # Performans için stil getirme fonksiyonunu boş geçiyoruz (yazılar standart olsun, hız artsın)
    return "" 
