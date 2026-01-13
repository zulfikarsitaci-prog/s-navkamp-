import database.users as users

MAIN_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&family=Cinzel:wght@700&family=Orbitron:wght@700&display=swap');

    /* --- 1. GENEL AYARLAR --- */
    .main .block-container { 
        padding-top: 1rem !important; 
        max-width: 100% !important;
    }
    div[data-testid="stVerticalBlock"] { gap: 0.5rem !important; }
    
    /* --- 2. MENÜ (KAPSÜL TASARIM - OKUNAKLI) --- */
    div[role="radiogroup"] {
        flex-direction: row !important;
        display: flex !important;
        overflow-x: auto !important;
        gap: 10px !important;
        padding: 5px 5px 15px 5px !important;
        border-bottom: 2px solid #B8860B;
        margin-bottom: 15px !important;
    }
    div[role="radiogroup"] label > div:first-child { display: none !important; }

    div[role="radiogroup"] label {
        background-color: #0f172a !important; 
        border: 2px solid #B8860B !important; 
        border-radius: 20px !important;       
        padding: 8px 16px !important;
        margin: 0 !important;
        min-width: auto !important;
        display: flex !important; align-items: center !important; justify-content: center !important;
        transition: all 0.2s;
    }

    div[role="radiogroup"] label p {
        color: #FFD700 !important; 
        font-weight: 700 !important;
        font-size: 0.9rem !important;
        margin: 0 !important;
        white-space: nowrap !important;
    }

    div[role="radiogroup"] label[data-checked="true"] {
        background-color: #FFD700 !important; 
        transform: scale(1.05);
        box-shadow: 0 0 10px rgba(255, 215, 0, 0.5);
    }
    div[role="radiogroup"] label[data-checked="true"] p {
        color: #000000 !important; 
    }

    /* --- 3. BUZLU CAM EFEKTİ (GLASSMORPHISM) --- */
    .post-card, .shop-card {
        background: rgba(30, 41, 59, 0.70) !important; /* Yarı saydam lacivert */
        backdrop-filter: blur(12px) !important;        /* Buzlama */
        -webkit-backdrop-filter: blur(12px) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 16px !important;
        padding: 15px;
        margin-bottom: 15px !important;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3) !important;
    }

    /* --- 4. HİKAYELER (DÜZELTİLDİ) --- */
    .story-btn button {
        height: 60px !important; width: 60px !important;
        opacity: 0 !important; position: absolute !important; top: 0 !important; left: 0 !important; z-index: 10 !important;
    }
    div[data-testid="column"]:has(.story-container) {
        width: 65px !important; min-width: 65px !important; max-width: 65px !important;
        padding: 0 !important; margin: 0 !important; flex: 0 0 auto !important;
    }
    div[data-testid="stHorizontalBlock"]:has(.story-container) {
        flex-wrap: nowrap !important; overflow-x: auto !important; gap: 5px !important;
    }

    /* --- 5. ÇERÇEVE STİLLERİ (TAKIMLAR DAHİL) --- */
    .avatar-container { position: relative; width: 40px; height: 40px; display:inline-block; }
    .avatar-img { width: 100%; height: 100%; object-fit: cover; border-radius: 50%; }
    .frame-overlay { position: absolute; top: -15%; left: -15%; width: 130%; height: 130%; pointer-events: none; z-index: 2; }
    
    /* Premium */
    .frame-Gold { border: 2px solid #FFD700; box-shadow: 0 0 5px #FFD700; border-radius: 50%; }
    .frame-Neon { border: 2px solid #00ffff; box-shadow: 0 0 5px #00ffff; border-radius: 50%; }
    .frame-Fire { border: 2px solid #ff4500; border-radius: 50%; box-shadow: 0 0 5px #ff4500; }
    .frame-King { border: 3px solid #ffd700; border-radius: 50%; box-shadow: 0 0 10px #ffd700; }
    .frame-Matrix { border: 2px dotted #00ff00; border-radius: 50%; }
    .frame-Nature { border: 2px solid #22c55e; border-radius: 50%; }
    .frame-Ice { border: 2px solid #a5f3fc; border-radius: 50%; box-shadow: 0 0 5px #a5f3fc; }
    .frame-Cyber { border: 2px dashed #00ff00; border-radius: 50%; }
    .frame-Inferno { border: 2px solid #ff4500; border-radius: 50%; border-bottom: 4px solid #8b0000; }
    .frame-Emperor { border: 3px double #FFD700; border-radius: 50%; box-shadow: 0 0 10px #800080; }

    /* Takımlar */
    .frame-GS { border: 3px solid #ef4444; border-radius: 50%; border-left-color: #facc15; box-shadow: 0 0 5px #ef4444; }
    .frame-FB { border: 3px solid #1e3a8a; border-radius: 50%; border-left-color: #facc15; box-shadow: 0 0 5px #1e3a8a; }
    .frame-BJK { border: 3px solid #000000; border-radius: 50%; border-left-color: #ffffff; box-shadow: 0 0 5px #ffffff; }
    .frame-TS { border: 3px solid #800000; border-radius: 50%; border-left-color: #3b82f6; box-shadow: 0 0 5px #3b82f6; }
    .frame-TR { border: 3px solid #ef4444; border-radius: 50%; border-top-color: #ffffff; box-shadow: 0 0 5px #ef4444; }

    /* İsim Stilleri */
    .name-Glitch { color: #00ffff; text-shadow: 2px 0 #ff00ff; font-weight: bold; }
    .name-Fire { color: #ff4500; text-shadow: 0 0 5px #ff0000; font-weight: bold; }
    .name-Gold { background: linear-gradient(to right, #BF953F, #FCF6BA, #B38728); -webkit-background-clip: text; color: transparent; font-weight: 900; }
    .name-Ice { color: #a5f3fc; text-shadow: 0 0 5px #0891b2; font-weight: bold; }

    /* Fontlar */
    .font-Cinzel { font-family: 'Cinzel', serif; } 
    .font-Orbitron { font-family: 'Orbitron', sans-serif; }
    .font-Rye { font-family: 'Rye', serif; } 
    .font-Dancing { font-family: 'Dancing Script', cursive; }
    .font-Metallic { font-family: 'Metal Mania', cursive; letter-spacing: 1px; }

    /* Diğer */
    .post-header { display: flex; align-items: center; border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 8px; margin-bottom: 8px; }
    .post-content { color: #e2e8f0; font-size: 0.95rem; line-height: 1.5; margin-bottom: 10px; }
    .post-image { width: 100%; border-radius: 8px; margin-top: 5px; }
    div[data-testid="column"] .stButton { margin-top: -10px !important; margin-bottom: -10px !important; }
    div[data-testid="stPopover"] { display: inline-block !important; margin-top: -10px !important; }
    
    .shop-title { font-size: 0.8rem; color: #e2e8f0; font-weight: bold; margin: 5px 0; }
    .shop-price { background: #10b981; color: white; padding: 2px 6px; border-radius: 8px; font-size: 0.7rem; }
</style>
"""

def get_user_display_html(username, size=40):
    ava, frame, name_style, _, font_style, title = users.get_user_styles(username)
    img_src = f"data:image/jpeg;base64,{ava}" if ava else "https://via.placeholder.com/150/CCCCCC/FFFFFF?text=U"
    
    frame_class = f"frame-{frame}" if frame else ""
    name_class = f"name-{name_style}" if name_style else ""
    font_class = f"font-{font_style}" if font_style else ""
    
    return f"""
    <div style="display:flex; align-items:center; gap:10px;">
        <div class="avatar-container {frame_class}" style="width:{size}px; height:{size}px;">
            <img src="{img_src}" style="width:100%; height:100%; border-radius:50%; object-fit:cover;">
        </div>
        <div style="display:flex; flex-direction:column;">
            <span class="{name_class} {font_class}" style="font-weight:bold; color:#e2e8f0; font-size:0.9rem;">{username}</span>
            <span style="font-size:0.65rem; color:#94a3b8;">{title}</span>
        </div>
    </div>
    """

def get_post_style_css(username):
    _, _, _, post_style, font_style, _ = users.get_user_styles(username)
    return f"post-{post_style} font-{font_style}"
