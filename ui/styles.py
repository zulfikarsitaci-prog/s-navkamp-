import database.users as users

MAIN_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700&family=Cinzel:wght@700&display=swap');

    /* --- 1. GENEL DÜZEN --- */
    .main .block-container { 
        padding-top: 1rem !important; 
        padding-left: 0.5rem !important; 
        padding-right: 0.5rem !important; 
        max-width: 100% !important;
    }
    div[data-testid="stVerticalBlock"] { gap: 0.5rem !important; }
    
    /* --- 2. MENÜ (SENİN BEĞENDİĞİN KAPSÜL TASARIM) --- */
    div[role="radiogroup"] {
        flex-direction: row !important;
        display: flex !important;
        overflow-x: auto !important;
        gap: 10px !important;
        padding: 5px 2px 10px 2px !important;
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

    /* --- 3. BUZLU CAM EFEKTİ (GERİ GELDİ) --- */
    .post-card {
        background: rgba(30, 41, 59, 0.65) !important; /* Yarı saydam */
        backdrop-filter: blur(12px) !important;        /* Buzlanma */
        -webkit-backdrop-filter: blur(12px) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 16px !important;
        padding: 15px;
        margin-bottom: 15px !important;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3) !important;
    }

    /* --- 4. GİRİŞ EKRANI (ORTALAMA) --- */
    .login-container { 
        display: flex; 
        flex-direction: column; 
        align-items: center; 
        justify-content: center; 
        text-align: center; 
        margin-top: 20px; 
        margin-bottom: 30px; 
        width: 100%;
    }
    .login-main { 
        font-family: 'Cinzel', serif; 
        font-size: 2.2rem; 
        margin: 10px 0; 
        font-weight: bold; 
        color: #e0f2fe;
        text-shadow: 0 0 5px #FFD700;
        animation: neonShine 2s infinite alternate; 
    }
    @keyframes neonShine { 
        0% { text-shadow: 0 0 5px #FFD700; color: #FFD700; } 
        100% { text-shadow: 0 0 20px #00ffff; color: #e0f2fe; } 
    }

    /* --- 5. HİKAYELER (DÜZELTME) --- */
    /* Butonu tamamen gizle ve kutunun üstüne yay */
    .story-btn button {
        height: 70px !important;
        width: 60px !important;
        opacity: 0 !important;
        position: absolute !important;
        top: -10px !important; 
        left: 0 !important;
        z-index: 10 !important;
    }
    
    div[data-testid="column"]:has(.story-container) {
        width: 65px !important; min-width: 65px !important; max-width: 65px !important;
        padding: 0 !important; margin: 0 !important; flex: 0 0 auto !important;
    }
    
    div[data-testid="stHorizontalBlock"]:has(.story-container) {
        flex-wrap: nowrap !important; overflow-x: auto !important; gap: 5px !important;
    }

    /* --- DİĞER DETAYLAR --- */
    .post-header { display: flex; align-items: center; border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 8px; margin-bottom: 8px; }
    .post-content { color: #e2e8f0; font-size: 0.95rem; line-height: 1.5; margin-bottom: 10px; }
    .post-image { width: 100%; border-radius: 8px; margin-top: 5px; }

    /* Buton hizalamaları */
    div[data-testid="column"] .stButton { margin-top: -10px !important; margin-bottom: -10px !important; }
    div[data-testid="stPopover"] { display: inline-block !important; margin-top: -10px !important; }

    /* Çerçeveler */
    .avatar-container { position: relative; width: 40px; height: 40px; display:inline-block; }
    .frame-overlay { position: absolute; top: -15%; left: -15%; width: 130%; height: 130%; pointer-events: none; z-index: 2; }
    
    .frame-Gold { border: 2px solid #FFD700; box-shadow: 0 0 5px #FFD700; border-radius: 50%; }
    .frame-Neon { border: 2px solid #00ffff; box-shadow: 0 0 5px #00ffff; border-radius: 50%; }
    .frame-King { border: 3px solid #ffd700; border-radius: 50%; }
</style>
"""

def get_user_display_html(username, size=40):
    ava, frame, name_style, _, font_style, title = users.get_user_styles(username)
    img_src = f"data:image/jpeg;base64,{ava}" if ava else "https://via.placeholder.com/150/CCCCCC/FFFFFF?text=U"
    frame_class = f"frame-{frame}" if frame else ""
    
    # HTML hatasını önlemek için temiz yapı
    return f"""
    <div style="display:flex; align-items:center; gap:10px;">
        <div class="avatar-container {frame_class}" style="width:{size}px; height:{size}px;">
            <img src="{img_src}" style="width:100%; height:100%; border-radius:50%; object-fit:cover;">
        </div>
        <div style="display:flex; flex-direction:column;">
            <span style="font-weight:bold; color:#e2e8f0; font-size:0.9rem;">{username}</span>
            <span style="font-size:0.65rem; color:#94a3b8;">{title}</span>
        </div>
    </div>
    """

def get_post_style_css(username):
    return ""
