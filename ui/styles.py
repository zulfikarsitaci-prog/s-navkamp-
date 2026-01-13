import database.users as users

MAIN_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@700&family=Orbitron:wght@700&family=Rye&family=Dancing+Script:wght@700&family=Metal+Mania&display=swap');

    /* --- 1. SIKIŞTIRMA VE GENEL --- */
    .main .block-container { 
        padding-top: 1rem !important; 
        padding-left: 0.5rem !important; 
        padding-right: 0.5rem !important; 
        max-width: 100% !important;
    }
    div[data-testid="stVerticalBlock"] { gap: 0rem !important; }
    div.stMarkdown { margin-bottom: 0px !important; }

    /* --- 2. MEGA GOLD MENÜ (HIZLI & BÜYÜK) --- */
    
    div[role="radiogroup"] {
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: nowrap !important;
        overflow-x: auto !important;
        gap: 12px !important;
        padding: 10px 5px 15px 5px !important;
        border-bottom: 3px solid #B8860B; /* Altına Koyu Gold Çizgi */
        margin-bottom: 15px !important;
        -webkit-overflow-scrolling: touch;
        justify-content: flex-start !important;
    }
    
    /* Radyo yuvarlağını gizle */
    div[role="radiogroup"] label div:first-child { display: none !important; }
    
    /* Menü Kutuları */
    div[role="radiogroup"] label {
        background-color: #0f172a !important; /* LACİVERT ARKA PLAN (KORUNDU) */
        border: 3px solid #B8860B !important; /* KOYU GOLD KALIN ÇERÇEVE */
        border-radius: 16px !important;
        padding: 12px 25px !important; /* İÇ BOŞLUK BÜYÜTÜLDÜ */
        min-width: fit-content !important;
        margin: 0 !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        height: 55px !important; /* YÜKSEKLİK ARTTI */
        transition: transform 0.1s;
    }
    
    /* Menü Yazıları */
    div[role="radiogroup"] label p {
        color: #FFD700 !important; /* PARLAK GOLD YAZI */
        font-weight: 800 !important;
        font-size: 1.2rem !important; /* YAZI BOYUTU BÜYÜDÜ */
        text-transform: uppercase !important; /* Hepsi BÜYÜK HARF olsun */
        letter-spacing: 1px !important;
        margin: 0 !important;
        white-space: nowrap !important;
        text-shadow: 0px 2px 2px rgba(0,0,0,0.8); /* Okunurluk gölgesi */
    }
    
    /* Seçili Menü */
    div[role="radiogroup"] label[data-checked="true"] {
        background-color: #B8860B !important; /* Seçilince Koyu Gold Zemin */
        border-color: #FFD700 !important;     /* Çerçeve Parlak Gold */
        transform: scale(1.05);
        box-shadow: 0 0 20px rgba(255, 215, 0, 0.4);
    }
    div[role="radiogroup"] label[data-checked="true"] p {
        color: #ffffff !important; /* Seçilince BEYAZ yazı */
    }

    /* --- 3. HİKAYELER (Instagram Modu) --- */
    div[data-testid="column"]:has(.story-btn) {
        flex: 0 0 auto !important; width: 80px !important; min-width: 80px !important; max-width: 80px !important; margin-right: 0px !important;
    }
    div[data-testid="stHorizontalBlock"]:has(.story-btn) {
        display: flex !important; flex-wrap: nowrap !important; overflow-x: auto !important; justify-content: flex-start !important; gap: 0px !important;
    }
    .story-btn button {
        font-size: 0.7rem !important; margin-top: -5px !important; color: #94a3b8 !important; border: none !important; background: transparent !important; width: 100% !important; white-space: nowrap !important; overflow: hidden !important; text-overflow: ellipsis !important; padding: 0 !important;
    }

    /* --- 4. DİĞER BİLEŞENLER --- */
    /* Popover (+ Butonu) */
    div[data-testid="stPopover"] { display: inline-block !important; margin-top: -16px !important; margin-bottom: -15px !important; }
    div[data-testid="stPopover"] button { border: 1px solid rgba(255,255,255,0.2) !important; height: 2em !important; }
    
    /* Kalp Butonu */
    div[data-testid="column"] .stButton { margin-top: -15px !important; margin-bottom: -15px !important; }

    .post-card { background: rgba(30, 41, 59, 0.75); backdrop-filter: blur(10px); -webkit-backdrop-filter: blur(10px); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 12px; padding: 10px; margin-bottom: 12px !important; box-shadow: 0 4px 10px rgba(0, 0, 0, 0.3); }
    .post-header { display: flex; align-items: center; border-bottom: 1px solid rgba(255,255,255,0.05); padding-bottom: 6px; margin-bottom: 6px; }
    .post-content { color: #e2e8f0; font-size: 0.95rem; line-height: 1.4; white-space: pre-wrap; margin-bottom: 8px; }
    .post-image { width: 100%; border-radius: 6px; margin-top: 4px; }
    
    /* Anket */
    div.poll-marker + div .stButton button { text-align: left !important; padding: 8px 12px !important; background: rgba(15, 23, 42, 0.8) !important; border: 1px solid rgba(255, 255, 255, 0.1) !important; }
    div.poll-marker + div .stButton { margin-top: -20px !important; margin-bottom: -5px !important; }
    .poll-bar-bg { background: rgba(255,255,255,0.05); border-radius: 4px; margin-bottom: 3px; height: 24px; line-height: 24px; position:relative; }
    .poll-bar-fill { background: linear-gradient(90deg, #3b82f6, #60a5fa); height: 100%; position: absolute; top: 0; left: 0; }
    .poll-text { position: relative; z-index: 2; padding: 0 8px; font-size: 0.75rem; color: white; display: flex; justify-content: space-between; font-weight: 600; }

    /* Çerçeveler */
    .avatar-container { position: relative; display: inline-block; margin-right: 8px; line-height: 0; }
    .avatar-img { border-radius: 50%; object-fit: cover; border: 2px solid rgba(255,255,255,0.1); }
    .frame-overlay { position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); width: 135%; height: 135%; pointer-events: none; z-index: 2; }
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
    
    .shop-card { background: rgba(30, 41, 59, 0.8); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 12px; padding: 10px; text-align: center; height: 160px; display: flex; flex-direction: column; justify-content: space-between; align-items: center; }
    .shop-title { font-size: 0.8rem; color: #e2e8f0; font-weight: bold; margin: 5px 0; }
    .shop-price { background: #10b981; color: white; padding: 2px 6px; border-radius: 8px; font-size: 0.7rem; }
    .shop-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; margin-top: 10px; }
    
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
        badges = {"Kahin":("🔮","#6366f1","0 0 10px #6366f1"),"Efsane":("🌟","#F59E0B","0 0 10px #F59E0B"),"LORD":("👑","#FFD700","0 0 10px gold"),"Bilgin":("🛡️","#a855f7","none"),"Usta":("⚔️","#ef4444","none"),"Çırak":("🔨","#94a3b8","none"),"Admin":("🛠️","#22c55e","none")}
        icon, color, glow = badges.get(title, ("🎓", "#cbd5e1", "none"))
        badge_html = f"""<span style="background:rgba(15,23,42,0.8);color:{color};border:1px solid {color};border-radius:12px;padding:1px 6px;font-size:0.65rem;margin-left:6px;display:inline-flex;align-items:center;gap:3px;box-shadow:{glow};vertical-align:middle;">{icon} {title}</span>"""
    return f"""<div style="display:flex;align-items:center;"><div class="avatar-container" style="width:{size}px; height:{size}px;"><img src="{img_src}" class="avatar-img" style="width:100%; height:100%;">{f_html}</div><div style="margin-left:12px;"><div class="{classes}" style="font-size:0.9rem; display:flex; align-items:center;">{username} {badge_html}</div></div></div>"""

def get_post_style_css(username):
    _, _, _, post_style, font_style, _ = users.get_user_styles(username)
    return f"post-{post_style} font-{font_style}"
