import database.users as users

MAIN_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@700&family=Orbitron:wght@700&family=Rye&family=Dancing+Script:wght@700&family=Metal+Mania&display=swap');

    /* --- 1. BOŞLUKLARI SIFIRLAMA (KOMPAKT MOD) --- */
    
    /* Tüm dikey blokların arasındaki varsayılan 1rem boşluğu azalt */
    div[data-testid="stVerticalBlock"] {
        gap: 0.2rem !important; /* Normalde 1rem'dir, 0.2'ye çektik */
    }
    
    /* Markdown elementlerinin alt boşluğunu al */
    div.stMarkdown {
        margin-bottom: 0px !important;
    }

    /* --- 2. ANKET BUTONLARI (BİTİŞİK LİSTE) --- */
    
    /* İşaretçi div */
    .poll-marker {
        display: none; /* Görünmez yap, sadece yer tutsun */
    }

    /* İşaretçiden sonraki butonun kapsayıcısı (Wrapper) */
    div:has(> .poll-marker) + div .stButton,
    div.poll-marker + div .stButton {
        margin-top: -15px !important; /* Yukarı çek */
        padding-bottom: 0px !important;
    }

    /* Butonun Kendisi */
    div:has(> .poll-marker) + div .stButton button {
        width: 100% !important;
        display: flex !important;
        justify-content: flex-start !important; /* İkon ve yazıyı sola yasla */
        text-align: left !important;
        padding: 8px 12px !important;
        background: rgba(30, 41, 59, 0.6) !important;
        border: 1px solid rgba(255, 255, 255, 0.05) !important;
        color: #cbd5e1 !important;
        border-radius: 4px !important; /* Daha köşeli, liste gibi */
        margin: 0 !important;
        font-size: 0.85rem !important;
        height: auto !important;
        min-height: 0px !important;
        line-height: 1.2 !important;
    }

    /* Hover */
    div.poll-marker + div .stButton button:hover {
        background: rgba(59, 130, 246, 0.2) !important;
        border-color: #3b82f6 !important;
        color: white !important;
        padding-left: 15px !important; /* Kayma efekti */
    }

    /* --- 3. POST KARTI DÜZENİ --- */
    .post-card {
        background: rgba(30, 41, 59, 0.65);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 12px;
        padding: 12px;
        margin-bottom: 10px !important; /* Kartlar arası sadece 10px boşluk */
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2);
    }

    .post-header { display: flex; align-items: center; border-bottom: 1px solid rgba(255,255,255,0.05); padding-bottom: 6px; margin-bottom: 6px; }
    .post-content { color: #e2e8f0; font-size: 0.9rem; line-height: 1.4; white-space: pre-wrap; margin-bottom: 8px; }
    .post-image { width: 100%; border-radius: 6px; margin-top: 4px; }
    
    /* Post altı butonları (Kalp vb.) yukarı çekme */
    div[data-testid="column"] .stButton {
        margin-top: -10px !important;
        margin-bottom: -10px !important;
    }

    /* --- DİĞER CSS --- */
    .poll-bar-bg { background: rgba(255,255,255,0.05); border-radius: 4px; margin-bottom: 4px; position: relative; overflow: hidden; height: 28px; line-height: 28px; }
    .poll-bar-fill { background: linear-gradient(90deg, #3b82f6, #60a5fa); height: 100%; position: absolute; top: 0; left: 0; z-index: 1; }
    .poll-text { position: relative; z-index: 2; padding: 0 10px; font-size: 0.8rem; color: white; display: flex; justify-content: space-between; font-weight: 500; }

    div[data-testid="stHorizontalBlock"] { flex-wrap: nowrap !important; overflow-x: auto !important; overflow-y: hidden !important; padding-bottom: 5px !important; gap: 8px !important; justify-content: flex-start !important; }
    div[data-testid="column"] { flex: 0 0 65px !important; width: 65px !important; min-width: 65px !important; margin: 0 !important; padding: 0 !important; }
    
    .login-container { text-align: center; margin-top: 20px; margin-bottom: 30px; }
    .login-main { font-family: 'Cinzel', serif; font-size: 2.2rem; margin: 10px 0; font-weight: bold; animation: neonShine 3s infinite alternate; }
    @keyframes neonShine { 0% { text-shadow: 0 0 5px #FFD700; color: #FFD700; } 50% { text-shadow: 0 0 20px #00ffff; color: #e0f2fe; } 100% { text-shadow: 0 0 5px #FFD700; color: #FFD700; } }
    
    .top-bar { position: sticky; top: 0; z-index: 999; background: rgba(30, 41, 59, 0.98); padding: 10px 15px; border-radius: 0 0 15px 15px; display: flex; justify-content: space-between; align-items: center; border-bottom: 2px solid #FFD700; margin: -1rem -1rem 0.5rem -1rem; box-shadow: 0 5px 15px rgba(0,0,0,0.4); }
    
    /* Butonlar Genel */
    div.stButton > button { background-color: transparent !important; border: none !important; color: #94a3b8 !important; font-size: 1.1rem !important; box-shadow: none !important; transition: transform 0.2s; padding: 0.2rem 0.5rem !important; }
    div.stButton > button:hover { color: #FFD700 !important; transform: scale(1.1); }
    
    .avatar-container { position: relative; display: inline-block; margin-right: 8px; line-height: 0; }
    .avatar-img { border-radius: 50%; object-fit: cover; border: 2px solid rgba(255,255,255,0.1); }
    .frame-overlay { position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); width: 135%; height: 135%; pointer-events: none; z-index: 2; }
    
    /* Çerçeve ve Renkler */
    .frame-Gold { border: 3px solid #FFD700; border-radius: 50%; box-shadow: 0 0 8px #FFD700; }
    .frame-Neon { border: 3px solid #00ffff; border-radius: 50%; box-shadow: 0 0 8px #00ffff; }
    .frame-Fire { border: 3px solid #ff4500; border-radius: 50%; box-shadow: 0 0 15px #ff4500; }
    .frame-King { border: 4px solid #ffd700; border-radius: 50%; box-shadow: 0 0 15px #ffd700; }
    .frame-Matrix { border: 3px dotted #00ff00; border-radius: 50%; }
        /* --- YENİ EKLENEN ÇERÇEVELER --- */
    
    /* 1. Doğa (Yeşil Yapraklar) */
    .frame-Nature { border: 3px solid #22c55e; border-radius: 50%; border-style: double; box-shadow: 0 0 8px #166534; }
    
    /* 2. Buz (Mavi Soğuk) */
    .frame-Ice { border: 3px solid #a5f3fc; border-radius: 50%; box-shadow: 0 0 10px #0891b2, inset 0 0 5px #a5f3fc; }
    
    /* 3. Siber (Neon Hacker) */
    .frame-Cyber { border: 3px dashed #00ff00; border-radius: 50%; box-shadow: 0 0 10px #00ff00, inset 0 0 5px #00ffff; }
    
    /* 4. Cehennem (Yanık Kırmızı) */
    .frame-Inferno { border: 3px solid #ff4500; border-radius: 50%; box-shadow: 0 0 10px #ff0000, 0 0 20px #ff8c00; border-bottom: 4px solid #8b0000; }
    
    /* 5. İmparator (Mor ve Altın) */
    .frame-Emperor { border: 4px double #FFD700; border-radius: 50%; box-shadow: 0 0 15px #800080, inset 0 0 10px #FFD700; background: linear-gradient(45deg, transparent 40%, rgba(128, 0, 128, 0.3)); }

    /* --- FUTBOL TAKIMLARI (GRADIENT ÇERÇEVELER) --- */
    
    /* Galatasaray (Sarı-Kırmızı) */
    .frame-GS {
        border: 4px solid transparent;
        border-radius: 50%;
        background-image: linear-gradient(#1e293b, #1e293b), linear-gradient(to right, #facc15, #ef4444);
        background-origin: border-box;
        background-clip: content-box, border-box;
        box-shadow: 0 0 10px #ef4444;
    }

    /* Fenerbahçe (Sarı-Lacivert) */
    .frame-FB {
        border: 4px solid transparent;
        border-radius: 50%;
        background-image: linear-gradient(#1e293b, #1e293b), linear-gradient(to right, #facc15, #1e3a8a);
        background-origin: border-box;
        background-clip: content-box, border-box;
        box-shadow: 0 0 10px #1e3a8a;
    }

    /* Beşiktaş (Siyah-Beyaz) */
    .frame-BJK {
        border: 4px solid transparent;
        border-radius: 50%;
        background-image: linear-gradient(#1e293b, #1e293b), linear-gradient(to right, #ffffff, #000000);
        background-origin: border-box;
        background-clip: content-box, border-box;
        box-shadow: 0 0 10px #ffffff;
    }

    /* Trabzonspor (Bordo-Mavi) */
    .frame-TS {
        border: 4px solid transparent;
        border-radius: 50%;
        background-image: linear-gradient(#1e293b, #1e293b), linear-gradient(to right, #800000, #3b82f6);
        background-origin: border-box;
        background-clip: content-box, border-box;
        box-shadow: 0 0 10px #3b82f6;
    }

    /* Milli Takım (Kırmızı-Beyaz) */
    .frame-TR {
        border: 4px solid #ef4444;
        border-radius: 50%;
        box-shadow: 0 0 15px #ef4444, inset 0 0 5px #ffffff;
    }

    /* --- YENİ İSİM STİLİ --- */
    .name-Ice { color: #a5f3fc; text-shadow: 0 0 5px #0891b2; font-weight: bold; }

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
    iframe { width: 100% !important; border-radius:     /* --- MAĞAZA DÜZENİ --- */
    /* Standart Ürün */
    .shop-card {
        background: rgba(30, 41, 59, 0.8);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 15px;
        text-align: center;
        transition: transform 0.2s;
        height: 180px; /* Sabit yükseklik */
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        align-items: center;
    }
    .shop-card:hover { transform: translateY(-5px); border-color: #94a3b8; }

    /* PREMIUM Ürün (Altın Parlama) */
    .shop-card-premium {
        background: linear-gradient(145deg, rgba(30, 41, 59, 0.9), rgba(0, 0, 0, 0.8));
        border: 1px solid #FFD700;
        border-radius: 12px;
        padding: 15px;
        text-align: center;
        transition: transform 0.2s;
        height: 180px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        align-items: center;
        box-shadow: 0 0 10px rgba(255, 215, 0, 0.2); /* Altın Gölge */
    }
    .shop-card-premium:hover {
        transform: translateY(-5px);
        box-shadow: 0 0 20px rgba(255, 215, 0, 0.6);
    }

    .shop-img { width: 60px; height: 60px; object-fit: cover; border-radius: 50%; margin-bottom: 5px; }
    .shop-title { font-size: 0.9rem; color: #e2e8f0; font-weight: bold; margin-bottom: 5px; }
    .shop-price { background: #10b981; color: white; padding: 2px 8px; border-radius: 10px; font-size: 0.75rem; }
    .shop-price-premium { background: #FFD700; color: #000; padding: 2px 8px; border-radius: 10px; font-size: 0.75rem; font-weight: bold; }

    
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