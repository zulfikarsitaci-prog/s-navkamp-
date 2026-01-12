import database.users as users

MAIN_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@700&family=Orbitron:wght@700&family=Rye&family=Dancing+Script:wght@700&family=Metal+Mania&display=swap');

    /* --- 1. GENEL SIKIŞTIRMA (BOŞLUKLARI YOK ET) --- */
    .main .block-container {
        padding-top: 1rem !important; /* Üstteki devasa boşluğu al */
        padding-left: 0.5rem !important;
        padding-right: 0.5rem !important;
    }
    div[data-testid="stVerticalBlock"] { gap: 0rem !important; }
    div.stMarkdown { margin-bottom: 0px !important; }
    h3 { margin-top: 0px !important; padding-top: 0px !important; font-size: 1.2rem !important; }

    /* --- 2. GÖRÜNÜR & BÜYÜK MENÜ (LACİVERT-SARI) --- */
    
    /* Yuvarlak radyo butonlarını gizle */
    div[role="radiogroup"] label div:first-child { display: none !important; }
    
    /* Menü Kapsayıcısı */
    div[role="radiogroup"] {
        flex-direction: row !important;
        overflow-x: auto !important; /* Yan kaydırma */
        gap: 10px !important;
        padding: 5px 0 10px 0 !important;
        border-bottom: 2px solid #FFD700; /* Altına sarı çizgi */
        margin-bottom: 10px !important;
        -webkit-overflow-scrolling: touch;
    }
    
    /* Menü Butonları (Kapsül) */
    div[role="radiogroup"] label {
        background-color: #1e293b !important; /* Koyu Lacivert */
        border: 2px solid #FFD700 !important; /* Altın Sarı Kenarlık */
        border-radius: 12px !important;
        padding: 10px 20px !important; /* İÇ BOŞLUĞU ARTIRDIM (DAHA BÜYÜK) */
        min-width: auto !important;
        margin: 0 !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
    
    /* Menü Yazıları (BÜYÜK VE OKUNAKLI) */
    div[role="radiogroup"] label p {
        color: #FFD700 !important; /* SARI YAZI */
        font-weight: 800 !important; /* EKSTRA KALIN */
        font-size: 1.1rem !important; /* YAZI BOYUTUNU BÜYÜTTÜM */
        margin: 0 !important;
        letter-spacing: 0.5px;
    }
    
    /* Seçili Menü Öğesi */
    div[role="radiogroup"] label[data-checked="true"] {
        background-color: #FFD700 !important; /* Sarı Zemin */
        border-color: #ffffff !important;
        transform: scale(1.05);
    }
    div[role="radiogroup"] label[data-checked="true"] p {
        color: #0f172a !important; /* Siyah/Lacivert Yazı */
    }

    /* --- 3. ANKET & BUTON DÜZENİ (BİTİŞİK LİSTE) --- */
    
    /* İşaretçiden sonraki buton */
    div.poll-marker + div .stButton {
        margin-top: -22px !important; /* Yukarı çek */
        margin-bottom: -8px !important; /* Aşağıyı çek */
        padding: 0 !important;
        width: 100% !important;
    }

    /* Anket Butonunun İçi */
    div.poll-marker + div .stButton button {
        width: 100% !important; /* EKRANI KAPLA */
        justify-content: flex-start !important; /* SOLA YASLA */
        text-align: left !important;
        padding: 12px 15px !important; /* Tıklaması kolay olsun */
        background: rgba(30, 41, 59, 0.9) !important; /* Koyu zemin */
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-bottom: 1px solid rgba(255, 255, 255, 0.05) !important;
        color: #e2e8f0 !important;
        border-radius: 4px !important; /* Köşeli liste yapısı */
        font-size: 1rem !important;
        font-weight: 500 !important;
    }

    /* Hover Efekti */
    div.poll-marker + div .stButton button:hover {
        background: rgba(255, 215, 0, 0.2) !important;
        border-left: 4px solid #FFD700 !important; /* Soldan sarı çizgi */
        color: white !important;
    }

    /* --- 4. POST AKSİYONLARI (KALP VB.) --- */
    div[data-testid="column"] .stButton {
        margin-top: -15px !important;
        margin-bottom: -15px !important;
    }
    
    /* --- 5. HİKAYELER --- */
    div[data-testid="stHorizontalBlock"] {
        padding-bottom: 5px !important;
        gap: 5px !important;
    }
    /* Hikaye isimleri (küçük butonlar) */
    .story-btn button {
        font-size: 0.7rem !important;
        margin-top: -8px !important;
        color: #94a3b8 !important;
    }

    /* --- DİĞER CSS --- */
    .post-card {
        background: rgba(30, 41, 59, 0.65);
        backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 12px;
        margin-bottom: 15px !important;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2);
    }
    .post-header { display: flex; align-items: center; border-bottom: 1px solid rgba(255,255,255,0.05); padding-bottom: 8px; margin-bottom: 8px; }
    .post-content { color: #e2e8f0; font-size: 0.95rem; line-height: 1.4; white-space: pre-wrap; margin-bottom: 10px; }
    .post-image { width: 100%; border-radius: 8px; margin-top: 5px; }
    
    .poll-bar-bg { background: rgba(255,255,255,0.05); border-radius: 4px; margin-bottom: 3px; height: 28px; line-height: 28px; position:relative; }
    .poll-bar-fill { background: linear-gradient(90deg, #3b82f6, #60a5fa); height: 100%; position: absolute; top: 0; left: 0; }
    .poll-text { position: relative; z-index: 2; padding: 0 10px; font-size: 0.8rem; color: white; display: flex; justify-content: space-between; font-weight: 600; }

    .login-container { text-align: center; margin-top: 20px; margin-bottom: 30px; }
    .login-main { font-family: 'Cinzel', serif; font-size: 2.2rem; margin: 10px 0; font-weight: bold; animation: neonShine 3s infinite alternate; }
    @keyframes neonShine { 0% { text-shadow: 0 0 5px #FFD700; color: #FFD700; } 50% { text-shadow: 0 0 20px #00ffff; color: #e0f2fe; } 100% { text-shadow: 0 0 5px #FFD700; color: #FFD700; } }
    
    /* Buton Genel */
    div.stButton > button { background-color: transparent !important; border: none !important; color: #94a3b8 !important; font-size: 1.1rem !important; padding: 0.2rem 0.5rem !important; }
    div.stButton > button:hover { color: #FFD700 !important; transform: scale(1.1); }
    div[data-testid="stPopoverBody"] button { background-color: #334155 !important; color: white !important; border: 1px solid #475569 !important; margin-bottom: 5px !important; width: 100% !important; font-size: 0.9rem !important; }
    
    /* Avatar & Frame */
    .avatar-container { position: relative; display: inline-block; margin-right: 8px; line-height: 0; }
    .avatar-img { border-radius: 50%; object-fit: cover; border: 2px solid rgba(255,255,255,0.1); }
    .frame-overlay { position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); width: 135%; height: 135%; pointer-events: none; z-index: 2; }
    
    .frame-Gold { border: 3px solid #FFD700; border-radius: 50%; box-shadow: 0 0 8px #FFD700; }
    .frame-Neon { border: 3px solid #00ffff; border-radius: 50%; box-shadow: 0 0 8px #00ffff; }
    .frame-Fire { border: 3px solid #ff4500; border-radius: 50%; box-shadow: 0 0 15px #ff4500; }
    .frame-King { border: 4px solid #ffd700; border-radius: 50%; box-shadow: 0 0 15px #ffd700; }
    .frame-Matrix { border: 3px dotted #00ff00; border-radius: 50%; }
    .name-Glitch { color: #00ffff; text-shadow: 1px 0 #ff00ff; font-weight: bold; }
    .name-Fire { color: #ff4500; text-shadow: 0 0 3px #ff0000; font-weight: bold; }
    .name-Gold { background: linear-gradient(to right, #BF953F, #FCF6BA, #B38728); -webkit-background-clip: text; color: transparent; font-weight: 900; }
    .post-Cyan { color: #00ffff !important; } .post-Lime { color: #00ff00 !important; } .post-Pink { color: #ff69b4 !important; } .post-Gold { color: #ffd700 !important; }
    .title-badge { background: #334155; color: #94a3b8; padding: 2px 6px; border-radius: 4px; font-size: 0.6rem; margin-left: 5px; border: 1px solid #475569; }
    .comment-box { background: rgba(15, 23, 42, 0.8); padding: 8px; border-radius: 6px; margin-top: 4px; font-size: 0.85rem; border-left: 3px solid #334155; }
    .shop-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 8px; margin-top: 10px; }
    @media only screen and (max-width: 600px) { .shop-grid { grid-template-columns: repeat(3, 1fr); } }
    .shop-item { background: rgba(15, 23, 42, 0.8); border: 1px solid #334155; border-radius: 12px; padding: 8px; text-align: center; display: flex; flex-direction: column; align-items: center; justify-content: space-between; height: 120px; transition: transform 0.2s; }
    .shop-name { font-size: 0.7rem; color: #cbd5e1; margin-top: 5px; }
    .shop-price { background: #10b981; color: white; padding: 3px 10px; border-radius: 12px; font-size: 0.7rem; font-weight: bold; }
    
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
        badges = {"Kahin":("🔮","#6366f1","0 0 10px #6366f1"),"LORD":("👑","#FFD700","0 0 10px gold"),"KURUCU":("☑️","#3b82f6","none"),"Bilgin":("🛡️","#a855f7","none"),"Usta":("⚔️","#ef4444","none"),"Çırak":("🔨","#94a3b8","none"),"Admin":("🛠️","#22c55e","none")}
        icon, color, glow = badges.get(title, ("🎓", "#cbd5e1", "none"))
        badge_html = f"""<span style="background:rgba(15,23,42,0.8);color:{color};border:1px solid {color};border-radius:12px;padding:1px 6px;font-size:0.65rem;margin-left:6px;display:inline-flex;align-items:center;gap:3px;box-shadow:{glow};vertical-align:middle;">{icon} {title}</span>"""
    return f"""<div style="display:flex;align-items:center;"><div class="avatar-container" style="width:{size}px; height:{size}px;"><img src="{img_src}" class="avatar-img" style="width:100%; height:100%;">{f_html}</div><div style="margin-left:12px;"><div class="{classes}" style="font-size:0.9rem; display:flex; align-items:center;">{username} {badge_html}</div></div></div>"""

def get_post_style_css(username):
    _, _, _, post_style, font_style, _ = users.get_user_styles(username)
    return f"post-{post_style} font-{font_style}"
