import database.users as users

MAIN_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@700&family=Orbitron:wght@700&family=Rye&family=Dancing+Script:wght@700&family=Metal+Mania&display=swap');

    /* --- 1. SIKIŞTIRMA VE GENEL --- */
    .main .block-container { padding-top: 1rem !important; }
    div[data-testid="stVerticalBlock"] { gap: 0rem !important; }
    div.stMarkdown { margin-bottom: 0px !important; }
    
    /* --- 2. MODERN ÜST MENÜ (LACİVERT - SARI) --- */
    div[role="radiogroup"] label div:first-child { display: none !important; }
    div[role="radiogroup"] {
        flex-direction: row !important;
        overflow-x: auto !important;
        gap: 8px !important;
        padding-bottom: 5px !important;
        margin-bottom: 10px !important;
        border-bottom: 1px solid rgba(255, 215, 0, 0.3);
    }
    div[role="radiogroup"] label {
        background-color: #1e293b !important;
        border: 1px solid #FFD700 !important;
        border-radius: 20px !important;
        padding: 6px 16px !important;
        margin: 0 !important;
        transition: all 0.2s;
        min-width: auto !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
    }
    div[role="radiogroup"] label p {
        color: #FFD700 !important;
        font-weight: 700 !important;
        font-size: 0.9rem !important;
        margin: 0 !important;
        text-shadow: 0 1px 2px rgba(0,0,0,0.8);
    }
    div[role="radiogroup"] label[data-checked="true"] {
        background-color: #FFD700 !important;
        border-color: #FFD700 !important;
        box-shadow: 0 0 15px rgba(255, 215, 0, 0.4);
        transform: scale(1.05);
    }
    div[role="radiogroup"] label[data-checked="true"] p { color: #1e293b !important; }

    /* --- 3. ANKET BUTONLARI --- */
    div.poll-marker + div .stButton { margin-top: -24px !important; margin-bottom: -5px !important; padding: 0 !important; }
    div.poll-marker + div .stButton button {
        width: 100% !important; justify-content: flex-start !important; text-align: left !important;
        padding: 6px 10px !important; min-height: 30px !important; height: auto !important;
        background: rgba(15, 23, 42, 0.8) !important; border: 1px solid rgba(255, 255, 255, 0.1) !important;
        color: #e2e8f0 !important; border-radius: 6px !important; font-size: 0.85rem !important;
    }
    div.poll-marker + div .stButton button:hover { background: rgba(255, 215, 0, 0.2) !important; border-color: #FFD700 !important; color: white !important; }

    /* --- 4. POST KARTLARI --- */
    .post-card {
        background: rgba(30, 41, 59, 0.65);
        backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 12px; padding: 10px; margin-bottom: 8px !important;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2);
    }
    div[data-testid="column"] .stButton { margin-top: -12px !important; margin-bottom: -10px !important; }
    .post-header { display: flex; align-items: center; border-bottom: 1px solid rgba(255,255,255,0.05); padding-bottom: 5px; margin-bottom: 5px; }
    .post-content { color: #e2e8f0; font-size: 0.9rem; line-height: 1.3; white-space: pre-wrap; margin-bottom: 5px; }
    .post-image { width: 100%; border-radius: 6px; margin-top: 2px; }

    /* --- 5. MAĞAZA DÜZENİ (GRID) --- */
    .shop-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; margin-top: 10px; }
    .shop-card {
        background: rgba(30, 41, 59, 0.8);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px; padding: 10px; text-align: center;
        transition: transform 0.2s; display: flex; flex-direction: column;
        justify-content: space-between; align-items: center; height: 160px;
    }
    .shop-card:hover { transform: translateY(-3px); border-color: #FFD700; }
    .shop-title { font-size: 0.8rem; color: #e2e8f0; font-weight: bold; margin: 5px 0; }
    .shop-price { background: #10b981; color: white; padding: 2px 6px; border-radius: 8px; font-size: 0.7rem; }
    
    /* --- 6. ÇERÇEVELER --- */
    .avatar-container { position: relative; display: inline-block; margin-right: 8px; line-height: 0; }
    .avatar-img { border-radius: 50%; object-fit: cover; border: 2px solid rgba(255,255,255,0.1); }
    .frame-overlay { position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); width: 135%; height: 135%; pointer-events: none; z-index: 2; }

    /* Mevcutlar */
    .frame-Gold { border: 3px solid #FFD700; border-radius: 50%; box-shadow: 0 0 8px #FFD700; }
    .frame-Neon { border: 3px solid #00ffff; border-radius: 50%; box-shadow: 0 0 8px #00ffff; }
    .frame-Fire { border: 3px solid #ff4500; border-radius: 50%; box-shadow: 0 0 15px #ff4500; }
    .frame-King { border: 4px solid #ffd700; border-radius: 50%; box-shadow: 0 0 15px #ffd700; }
    .frame-Matrix { border: 3px dotted #00ff00; border-radius: 50%; }

    /* --- YENİ EKLENEN ÇERÇEVELER --- */
    /* 1. İMPARATOR (Mor/Altın Asalet) */
    .frame-Emperor {
        border: 4px double #FFD700;
        border-radius: 50%;
        box-shadow: 0 0 15px #800080, inset 0 0 10px #FFD700;
        background: linear-gradient(45deg, transparent 40%, rgba(128, 0, 128, 0.3));
    }
    /* 2. CEHENNEM (Daha yoğun ateş) */
    .frame-Inferno {
        border: 3px solid #ff4500;
        border-radius: 50%;
        box-shadow: 0 0 10px #ff0000, 0 0 20px #ff8c00;
        border-bottom: 4px solid #8b0000;
    }
    /* 3. SİBER (Neon Hacker) */
    .frame-Cyber {
        border: 3px dashed #00ff00;
        border-radius: 50%;
        box-shadow: 0 0 10px #00ff00, inset 0 0 5px #00ffff;
    }
    
    /* İsim Stilleri */
    .name-Glitch { color: #00ffff; text-shadow: 1px 0 #ff00ff; font-weight: bold; }
    .name-Fire { color: #ff4500; text-shadow: 0 0 3px #ff0000; font-weight: bold; }
    .name-Gold { background: linear-gradient(to right, #BF953F, #FCF6BA, #B38728); -webkit-background-clip: text; color: transparent; font-weight: 900; }
    .title-badge { background: #334155; color: #94a3b8; padding: 2px 6px; border-radius: 4px; font-size: 0.6rem; margin-left: 5px; border: 1px solid #475569; }
    
    .comment-box { background: rgba(15, 23, 42, 0.8); padding: 8px; border-radius: 6px; margin-top: 4px; font-size: 0.85rem; border-left: 3px solid #334155; }
    iframe { width: 100% !important; border-radius: 8px; }
    div[data-testid="stHorizontalBlock"] { flex-wrap: nowrap !important; overflow-x: auto !important; overflow-y: hidden !important; padding-bottom: 5px !important; gap: 5px !important; justify-content: flex-start !important; }
</style>
"""

def get_user_display_html(username, size=40):
    ava, frame, name_style, _, font_style, title = users.get_user_styles(username)
    img_src = f"data:image/jpeg;base64,{ava}" if ava else "https://via.placeholder.com/150/CCCCCC/FFFFFF?text=U"
    f_html = f'<div class="frame-overlay frame-{frame}"></div>' if frame else ""
    classes = f"{f'name-{name_style}' if name_style else ''} {f'font-{font_style}' if font_style else ''}"
    
    badge_html = ""
    if title:
        badges = {"Kahin":("🔮","#6366f1","0 0 10px #6366f1"),"LORD":("👑","#FFD700","0 0 10px gold"),"KURUCU":("☑️","#3b82f6","none"),"Bilgin":("🛡️","#a855f7","none"),"Usta":("⚔️","#ef4444","none"),"Çırak":("🔨","#94a3b8","none"),"Admin":("🛠️","#22c55e","none")}
        icon, color, glow = badges.get(title, ("🎓", "#cbd5e1", "none"))
        badge_html = f"""<span style="background:rgba(15,23,42,0.8);color:{color};border:1px solid {color};border-radius:12px;padding:1px 6px;font-size:0.65rem;margin-left:6px;display:inline-flex;align-items:center;gap:3px;box-shadow:{glow};vertical-align:middle;">{icon} {title}</span>"""
    
    return f"""<div style="display:flex;align-items:center;"><div class="avatar-container" style="width:{size}px; height:{size}px;"><img src="{img_src}" class="avatar-img" style="width:100%; height:100%;">{f_html}</div><div style="margin-left:12px;"><div class="{classes}" style="font-size:0.9rem; display:flex; align-items:center;">{username} {badge_html}</div></div></div>"""

def get_post_style_css(username):
    _, _, _, post_style, font_style, _ = users.get_user_styles(username)
    return f"post-{post_style} font-{font_style}"
