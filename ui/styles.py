import database.users as users

MAIN_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700&display=swap');

    /* --- 1. GENEL DÜZEN --- */
    .main .block-container { 
        padding-top: 1rem !important; 
        padding-left: 0.5rem !important; 
        padding-right: 0.5rem !important; 
        max-width: 100% !important;
    }
    div[data-testid="stVerticalBlock"] { gap: 0.5rem !important; }
    
    /* --- 2. MENÜ (KAPSÜL BUTONLAR) --- */
    /* Radyo grubunu yatay yap ve kaydırılabilir olsun */
    div[role="radiogroup"] {
        flex-direction: row !important;
        display: flex !important;
        overflow-x: auto !important;
        gap: 10px !important;
        padding: 5px 2px 10px 2px !important;
        border-bottom: 2px solid #B8860B;
        margin-bottom: 10px !important;
    }

    /* Yuvarlak radyo işaretini GİZLE */
    div[role="radiogroup"] label > div:first-child {
        display: none !important;
    }

    /* Menü Kutusunun Kendisi */
    div[role="radiogroup"] label {
        background-color: #0f172a !important; /* Lacivert */
        border: 2px solid #B8860B !important; /* Gold */
        border-radius: 20px !important;       /* Oval Köşeler */
        padding: 8px 16px !important;
        margin: 0 !important;
        min-width: auto !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        transition: all 0.2s;
    }

    /* Menü Yazısı */
    div[role="radiogroup"] label p {
        color: #FFD700 !important; /* Gold Yazı */
        font-weight: 700 !important;
        font-size: 0.9rem !important;
        margin: 0 !important;
        white-space: nowrap !important;
    }

    /* Seçili Buton Efekti */
    div[role="radiogroup"] label[data-checked="true"] {
        background-color: #FFD700 !important; /* Sarı Zemin */
        transform: scale(1.05);
        box-shadow: 0 0 10px rgba(255, 215, 0, 0.5);
    }
    div[role="radiogroup"] label[data-checked="true"] p {
        color: #000000 !important; /* Siyah Yazı */
    }

    /* --- 3. HİKAYELER (DÜZELTİLDİ) --- */
    /* Hikaye butonunu gizle ve kutuyu boyutlandır */
    .story-btn button {
        height: 60px !important;
        width: 60px !important;
        opacity: 0 !important; /* Tamamen görünmez */
        position: absolute !important;
        top: 0 !important;
        left: 0 !important;
        z-index: 5 !important;
    }
    
    /* Hikaye kapsayıcısı */
    div[data-testid="column"]:has(.story-container) {
        width: 65px !important;
        min-width: 65px !important;
        max-width: 65px !important;
        padding: 0 !important;
        margin: 0 !important;
        flex: 0 0 auto !important;
    }
    
    /* Yatay hizalama */
    div[data-testid="stHorizontalBlock"]:has(.story-container) {
        flex-wrap: nowrap !important;
        overflow-x: auto !important;
        gap: 5px !important;
    }

    /* --- 4. POST KARTI (HTML HATASI GİDERİLDİ) --- */
    .post-card {
        background-color: #1e293b;
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 12px;
        margin-bottom: 10px;
    }
    .post-header {
        display: flex;
        align-items: center;
        margin-bottom: 8px;
        border-bottom: 1px solid rgba(255,255,255,0.1);
        padding-bottom: 5px;
    }
    .post-content {
        color: #e2e8f0;
        font-size: 0.95rem;
        line-height: 1.4;
        margin-bottom: 8px;
    }
    .post-image {
        width: 100%;
        border-radius: 8px;
        margin-top: 5px;
    }

    /* --- 5. DİĞER --- */
    /* Avatar Çerçeveleri */
    .avatar-container { position: relative; width: 40px; height: 40px; display:inline-block; }
    .avatar-img { width: 100%; height: 100%; object-fit: cover; border-radius: 50%; }
    
    .frame-Gold { border: 2px solid #FFD700; box-shadow: 0 0 5px #FFD700; border-radius: 50%; }
    .frame-Neon { border: 2px solid #00ffff; box-shadow: 0 0 5px #00ffff; border-radius: 50%; }
    .frame-King { border: 3px solid #ffd700; border-radius: 50%; }
    
    /* Buton Boşlukları */
    div[data-testid="column"] .stButton { margin-top: -10px !important; }
</style>
"""

def get_user_display_html(username, size=40):
    ava, frame, name_style, _, font_style, title = users.get_user_styles(username)
    img_src = f"data:image/jpeg;base64,{ava}" if ava else "https://via.placeholder.com/150/CCCCCC/FFFFFF?text=U"
    
    frame_class = f"frame-{frame}" if frame else ""
    
    # Çok basit HTML yapısı (Hata riskini azaltır)
    return f"""
    <div style="display:flex; align-items:center; gap:8px;">
        <div class="avatar-container {frame_class}" style="width:{size}px; height:{size}px;">
            <img src="{img_src}" style="width:100%; height:100%; border-radius:50%; object-fit:cover;">
        </div>
        <div style="display:flex; flex-direction:column; justify-content:center;">
            <span style="font-weight:bold; color:#e2e8f0; font-size:0.9rem; line-height:1;">{username}</span>
            <span style="font-size:0.7rem; color:#94a3b8;">{title}</span>
        </div>
    </div>
    """

def get_post_style_css(username):
    return ""
