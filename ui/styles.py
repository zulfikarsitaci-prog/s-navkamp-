import database.users as users

MAIN_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@700&family=Orbitron:wght@700&family=Rye&family=Dancing+Script:wght@700&family=Metal+Mania&display=swap');

    /* --- 1. SIKIŞTIRMA VE GENEL AYARLAR --- */
    .main .block-container { 
        padding-top: 1rem !important; 
        padding-left: 0.5rem !important; 
        padding-right: 0.5rem !important; 
        max-width: 100% !important;
    }
    div[data-testid="stVerticalBlock"] { gap: 0rem !important; }
    div.stMarkdown { margin-bottom: 0px !important; }
    
    /* --- 2. HİKAYE ŞERİDİ (SOLA YASLI & YAN YANA) --- */
    div[data-testid="stHorizontalBlock"] {
        flex-wrap: nowrap !important;
        overflow-x: auto !important;
        overflow-y: hidden !important;
        justify-content: flex-start !important;
        gap: 8px !important;
        padding-bottom: 10px !important;
        -webkit-overflow-scrolling: touch;
    }
    
    div[data-testid="column"] {
        flex: 0 0 auto !important; 
        width: 72px !important; 
        min-width: 72px !important;
        margin: 0 !important;
        padding: 0 !important;
        display: flex;
        flex-direction: column;
        align-items: center;
    }

    .story-btn button {
        font-size: 0.7rem !important;
        margin-top: -5px !important;
        color: #94a3b8 !important;
        border: none !important;
        background: transparent !important;
        width: 72px !important;
        white-space: nowrap !important;
        overflow: hidden !important;
        text-overflow: ellipsis !important;
    }

    /* --- 3. MODERN KAPSÜL MENÜ (HAP TASARIM) --- */
    div[role="radiogroup"] label div:first-child { display: none !important; }
    
    div[role="radiogroup"] {
        flex-direction: row !important; 
        overflow-x: auto !important; 
        gap: 10px !important; /* Boşluk arttı */
        padding: 5px 5px 10px 5px !important; 
        border-bottom: 2px solid #FFD700; 
        margin-bottom: 10px !important;
    }
    
    /* KAPSÜL KUTU */
    div[role="radiogroup"] label {
        background-color: #1e293b !important; 
        border: 2px solid #FFD700 !important;
        border-radius: 50px !important; /* TAM OVAL (KAPSÜL) */
        padding: 8px 20px !important;   /* Geniş iç boşluk */
        min-width: auto !important;
        margin: 0 !important; 
        display: flex !important; 
        align-items: center !important; 
        justify-content: center !important;
        transition: transform 0.2s;
    }
    
    div[role="radiogroup"] label p {
        color: #FFD700 !important; 
        font-weight: 800 !important; 
        font-size: 1rem !important; 
        margin: 0 !important;
        white-space: nowrap !important;
    }
    
    /* SEÇİLİ KAPSÜL */
    div[role="radiogroup"] label[data-checked="true"] {
        background-color: #FFD700 !important; 
        border-color: #ffffff !important; 
        transform: scale(1.05);
        box-shadow: 0 0 10px rgba(255, 215, 0, 0.5);
    }
    div[role="radiogroup"] label[data-checked="true"] p { 
        color: #0f172a !important; 
    }

    /* --- 4. GİRİŞ EKRANI (ORTALAMA & NEON) --- */
    .login-container { 
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        text-align: center;
        margin-top: 40px; 
        margin-bottom: 30px; 
        width: 100%;
    }
    
    .login-main { 
        font-family: 'Cinzel', serif; 
        font-size: 2.2rem; 
        margin: 10px 0; 
        font-weight: bold; 
        animation: neonShine 3s infinite alternate; 
    }
    @keyframes neonShine { 
        0% { text-shadow: 0 0 5px #FFD700; color: #FFD700; } 
        50% { text-shadow: 0 0 20px #00ffff; color: #e0f2fe; } 
        100% { text-shadow: 0 0 5px #FFD700; color: #FFD700; } 
    }

    /* --- 5. ANKET & POST (BUZLU CAM) --- */
    div.poll-marker + div .stButton { margin-top: -22px !important; margin-bottom: -8px !important; padding: 0 !important; width: 100% !important; }
    div.poll-marker + div .stButton button {
        width: 100% !important; justify-content: flex-start !important; text-align: left !important;
        padding: 12px 15px !important; background: rgba(30, 41, 59, 0.9) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important; color: #e2e8f0 !important;
        border-radius: 4px !important; font-size: 1rem !important;
    }
    div.poll-marker + div .stButton button:hover { background: rgba(255, 215, 0, 0.2) !important; border-left: 4px solid #FFD700 !important; color: white !important; }

    .post-card {
        background: rgba(30, 41, 59, 0.65); 
        backdrop-filter: blur(12px); 
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.08); 
        border-radius: 16px; 
        padding: 12px; 
        margin-bottom: 15px !important;
    }
    .post-header { display: flex; align-items: center; border-bottom: 1px solid rgba(255,255,255,0.05); padding-bottom: 8px; margin-bottom: 8px; }
    .post-content { color: #e2e8f0; font-size: 0.95rem; line-height: 1.4; white-space: pre-wrap; margin-bottom: 10px; }
    .post-image { width: 100%; border-radius: 8px; margin-top: 5px; }
    
    .poll-bar-bg { background: rgba(255,255,255,0.05); border-radius: 4px; margin-bottom: 3px; height: 28px; line-height: 28px; position:relative; }
    .poll-bar-fill { background: linear-gradient(90deg, #3b82f6, #60a5fa); height: 100%; position: absolute; top: 0; left: 0; }
    .poll-text { position: relative; z-index: 2; padding: 0 10px; font-size: 0.8rem; color: white; display: flex; justify-content: space-between; font-weight: 600; }

    /* --- 6. DİĞER --- */
    .avatar-container { position: relative; display: inline-block; margin-right: 8px; line-height: 0; }
    .avatar-img { border-radius: 50%; object-fit: cover; border: 2px solid rgba(255,255,255,0.1); }
    .frame-overlay { position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); width: 135%; height: 135%; pointer-events: none; z-index: 2; }
    
    /* Çerçeveler */
    .frame-Gold { border: 3px solid #FFD700; border-radius: 50%; box-shadow: 0 0 8px #FFD700; }
    .frame-Neon { border: 3px solid #00ffff; border-radius: 50%; box-shadow: 0 0 8px #00ffff; }
    .frame-Fire { border: 3px solid #ff4500; border-radius: 50%; box-shadow: 0 0 15px #ff4500; }
    .frame-King { border: 4px solid #ffd700; border-radius: 50%; box-shadow: 0 0 15px #ffd700; }
    .frame-Matrix { border: 3px dotted #00ff00; border-radius: 50%; }
    .frame-Nature { border: 3px solid #22c55e; border-radius: 50%; border-style: double; box-shadow: 0 0 8px #166534; }
    .frame-Ice { border: 3px solid #a5f3fc; border-radius: 50%; box-shadow: 0 0 10px #0891b2, inset 0 0 5px #a5f3fc; }
    .frame-Cyber { border: 3px dashed #00ff00; border-radius: 50%; box-shadow: 0 0 10px #00ff00, inset 0 0 5px #00ffff; }
    .frame-Inferno { border: 3px solid #ff4500; border-radius: 50%; box-shadow: 0 0 10px #ff0000, 0 0 20px #ff8c00; border-bottom: 4px solid #8b0000; }
    .frame-Emperor { border: 4px double #FFD700; border-radius: 50%; box-shadow: 0 0 15px #800080, inset 0 0 10px #FFD700; background: linear-gradient(45deg, transparent 40%, rgba(128, 0, 128, 0.3)); }
    
    /* Takım Çerçeveleri */
    .frame-GS { border: 4px solid transparent; border-radius: 50%; background-image: linear-gradient(#1e293b, #1e293b), linear-gradient(to right, #facc15, #ef4444); background-origin: border-box; background-clip: content-box, border-box; box-shadow: 0 0 10px #ef4444; }
    .frame-FB { border: 4px solid transparent; border-radius: 50%; background-image: linear-gradient(#1e293b, #1e293b), linear-gradient(to right, #facc15, #1e3a8a); background-origin: border-box; background-clip: content-box, border-box; box-shadow: 0 0 10px #1e3a8a; }
    .frame-BJK { border: 4px solid transparent; border-radius: 50%; background-image: linear-gradient(#1e293b, #1e293b), linear-gradient(to right, #ffffff, #000000); background-origin: border-box; background-clip: content-box, border-box; box-shadow: 0 0 10px #ffffff; }
    .frame-TS { border: 4px solid transparent; border-radius: 50%; background-image: linear-gradient(#1e293b, #1e293b), linear-gradient(to right, #800000, #3b82f6); background-origin: border-box; background-clip: content-box, border-box; box-shadow: 0 0 10px #3b82f6; }
    .frame-TR { border: 4px solid #ef4444; border-radius: 50%; box-shadow: 0 0 15px #ef4444, inset 0 0 5px #ffffff; }

    .name-Glitch { color: #00ffff; text-shadow: 1px 0 #ff00ff; font-weight: bold; }
    .name-Fire { color: #ff4500; text-shadow: 0 0 3px #ff0000; font-weight: bold; }
    .name-Gold { background: linear-gradient(to right, #BF953F, #FCF6BA, #B38728); -webkit-background-clip: text; color: transparent; font-weight: 900; }
    .name-Ice { color: #a5f3fc; text-shadow: 0 0 5px #0891b2; font-weight: bold; }
    
    .title-badge { background: #334155; color: #94a3b8; padding: 2px 6px; border-radius: 4px; font-size: 0.6rem; margin-left: 5px; border: 1px solid #475569; }
    .shop-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; margin-top: 10px; }
    .shop-card { background: rgba(30, 41, 59, 0.8); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 12px; padding: 10px; text-align: center; height: 160px; display: flex; flex-direction: column; justify-content: space-between; align-items: center; }
    .shop-title { font-size: 0.8rem; color: #e2e8f0; font-weight: bold; margin: 5px 0; }
    .shop-price { background: #10b981; color: white; padding: 2px 6px; border-radius: 8px; font-size: 0.7rem; }
    
    .font-Cinzel { font-family: 'Cinzel', serif; } .font-Orbitron { font-family: 'Orbitron', sans-serif; }
    .font-Rye { font-family: 'Rye', serif; } .font-Dancing { font-family: 'Dancing Script', cursive; }
    .font-Metallic { font-family: 'Metal Mania', cursive; color: #b0b0b0; text-shadow: 2px 2px 0px #000; letter-spacing: 1px; }
    iframe { width: 100% !important; border-radius: 8px; }
</style>
"""

def get_user_display_html(username, size=40):
    ava, frame, name_style, _, font_style, title = users.get_user_styles(username)
    img_src = f"data:image/jpeg;base64,{ava}" if ava else "https://via.placeholder.com/150/CCCCCC/FFFFFF?text=U"
    f_html = f'<div class="frame-overlay frame-{frame}"></div>' if frame else ""
    classes = f"{f'name-{name_style}' if name_style else ''} {f'font-{font_style}' if font_style else ''}"
    badge_html = ""
    if title:
        badges = {"Kahin":("🔮","#6366f1","0 0 10px #6366f1"),"Efsane":("🌟","#F59E0B","0 0 10px #F59E0B"),"LORD":("👑","#FFD700","0 0 10px gold"),"Bilgin":("🛡️","#a855f7","none"),"Usta":("⚔️","#ef4444","none"),"Çırak":("🔨","#94a3b8","none")}
        icon, color, glow = badges.get(title, ("🎓", "#cbd5e1", "none"))
        badge_html = f"""<span style="background:rgba(15,23,42,0.8);color:{color};border:1px solid {color};border-radius:12px;padding:1px 6px;font-size:0.65rem;margin-left:6px;display:inline-flex;align-items:center;gap:3px;box-shadow:{glow};vertical-align:middle;">{icon} {title}</span>"""
    return f"""<div style="display:flex;align-items:center;"><div class="avatar-container" style="width:{size}px; height:{size}px;"><img src="{img_src}" class="avatar-img" style="width:100%; height:100%;">{f_html}</div><div style="margin-left:12px;"><div class="{classes}" style="font-size:0.9rem; display:flex; align-items:center;">{username} {badge_html}</div></div></div>"""

def get_post_style_css(username):
    _, _, _, post_style, font_style, _ = users.get_user_styles(username)
    return f"post-{post_style} font-{font_style}"
