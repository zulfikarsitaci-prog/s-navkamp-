import database.users as users

MAIN_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@700&family=Orbitron:wght@700&family=Rye&family=Dancing+Script:wght@700&family=Metal+Mania&display=swap');

    /* --- GENEL --- */
    .login-container { text-align: center; margin-top: 20px; margin-bottom: 30px; }
    .login-sub { color: #94a3b8; font-size: 1rem; margin-bottom: 5px; font-family: sans-serif; letter-spacing: 1px; }
    
    /* Neon Başlık */
    @keyframes neonShine {
        0% { text-shadow: 0 0 5px #FFD700, 0 0 10px #FFD700; color: #FFD700; }
        50% { text-shadow: 0 0 10px #00ffff, 0 0 20px #00ffff; color: #e0f2fe; }
        100% { text-shadow: 0 0 5px #FFD700, 0 0 10px #FFD700; color: #FFD700; }
    }
    .login-main { font-family: 'Cinzel', serif; font-size: 2.2rem; line-height: 1.2; margin: 10px 0; font-weight: bold; animation: neonShine 3s infinite alternate; }
    .login-bottom { color: #cbd5e1; font-family: 'Orbitron', sans-serif; font-size: 0.9rem; margin-top: 5px; }

    /* Sticky Header */
    .top-bar { 
        position: sticky; top: 0; z-index: 999;
        background: rgba(30, 41, 59, 0.95);
        padding: 12px 15px; border-radius: 0 0 15px 15px; 
        display: flex; justify-content: space-between; align-items: center;
        border-bottom: 2px solid #FFD700; margin: -1rem -1rem 1rem -1rem; 
        box-shadow: 0 5px 20px rgba(0,0,0,0.5);
    }
    
    /* Post Kartı */
    .post-card {
        background: rgba(30, 41, 59, 0.65); backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 16px; padding: 15px;
        margin-bottom: 15px; box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3); position: relative;
    }
    .post-header { display: flex; align-items: center; border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 8px; margin-bottom: 8px; }
    .post-content { color: #e2e8f0; font-size: 0.95rem; line-height: 1.5; white-space: pre-wrap; margin-bottom: 10px; }
    .post-image { width: 100%; border-radius: 8px; margin-top: 5px; }
    
    /* Butonlar */
    div.stButton > button { background-color: transparent !important; border: none !important; color: #94a3b8 !important; font-size: 1.2rem !important; box-shadow: none !important; transition: transform 0.2s; }
    div.stButton > button:hover { color: #FFD700 !important; transform: scale(1.15); }
    div[data-testid="stPopoverBody"] button { background-color: #334155 !important; color: white !important; border: 1px solid #475569 !important; margin-bottom: 5px !important; width: 100% !important; font-size: 0.9rem !important; }
    
    /* Mağaza */
    .shop-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 8px; margin-top: 10px; }
    @media only screen and (max-width: 600px) { .shop-grid { grid-template-columns: repeat(3, 1fr); } }
    .shop-item { background: rgba(15, 23, 42, 0.8); border: 1px solid #334155; border-radius: 12px; padding: 8px; text-align: center; display: flex; flex-direction: column; align-items: center; justify-content: space-between; height: 120px; transition: transform 0.2s; }
    .shop-item:hover { transform: translateY(-3px); border-color: #FFD700; }
    .shop-name { font-size: 0.7rem; color: #cbd5e1; margin-top: 5px; }
    .shop-price { background: #10b981; color: white; padding: 3px 10px; border-radius: 12px; font-size: 0.7rem; font-weight: bold; }
    .gift-icon { font-size: 1.5rem; margin-bottom: 5px; }

    /* Fontlar */
    .font-Cinzel { font-family: 'Cinzel', serif; } .font-Orbitron { font-family: 'Orbitron', sans-serif; }
    .font-Rye { font-family: 'Rye', serif; } .font-Dancing { font-family: 'Dancing Script', cursive; }
    .font-Metallic { font-family: 'Metal Mania', cursive; color: #b0b0b0; text-shadow: 2px 2px 0px #000; letter-spacing: 1px; }

    /* --- AVATAR & ÇERÇEVE DÜZENLEMESİ --- */
    .avatar-container { position: relative; display: inline-block; margin-right: 8px; line-height: 0; }
    .avatar-img { border-radius: 50%; object-fit: cover; border: 2px solid rgba(255,255,255,0.1); }
    
    .frame-overlay { 
        position: absolute; 
        top: 50%; left: 50%; 
        transform: translate(-50%, -50%); 
        width: 135%; height: 135%;
        pointer-events: none; z-index: 2;
    }
    
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
    .comment-box { background: rgba(15, 23, 42, 0.8); padding: 8px; border-radius: 6px; margin-top: 6px; font-size: 0.85rem; border-left: 3px solid #334155; }
    iframe { width: 100% !important; border-radius: 8px; }
</style>
"""

def get_user_display_html(username, size=40):
    ava, frame, name_style, _, font_style, title = users.get_user_styles(username)
    img_src = f"data:image/jpeg;base64,{ava}" if ava else "https://via.placeholder.com/150/CCCCCC/FFFFFF?text=U"
    f_html = f'<div class="frame-overlay frame-{frame}"></div>' if frame else ""
    classes = f"{f'name-{name_style}' if name_style else ''} {f'font-{font_style}' if font_style else ''}"
    
    # HTML kodunu tek satırda veya sola yaslı veriyoruz ki kod bloğu sanılmasın
    return f"""<div style="display:flex;align-items:center;"><div class="avatar-container" style="width:{size}px; height:{size}px;"><img src="{img_src}" class="avatar-img" style="width:100%; height:100%;">{f_html}</div><div style="margin-left:12px;"><div class="{classes}" style="font-size:0.9rem;">{username} {f"<span class='title-badge'>{title}</span>" if title else ""}</div></div></div>"""

def get_post_style_css(username):
    _, _, _, post_style, font_style, _ = users.get_user_styles(username)
    return f"post-{post_style} font-{font_style}"
