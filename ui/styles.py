import database.users as users

MAIN_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@700&family=Orbitron:wght@700&display=swap');

/* =====================================================
   1. GENEL SIKIŞTIRMA (GLOBAL BOŞLUK KONTROLÜ)
===================================================== */
.main .block-container {
    padding-top: 0.5rem !important;
    padding-left: 0.5rem !important;
    padding-right: 0.5rem !important;
}

div[data-testid="stVerticalBlock"] {
    gap: 0.2rem !important;
}

div.stMarkdown {
    margin-bottom: 0px !important;
}

/* =====================================================
   2. ÜST MENÜ – OKUNURLUK VE KONTRAST DÜZELTİLDİ
===================================================== */

/* Radyo yuvarlaklarını gizle */
div[role="radiogroup"] label div:first-child {
    display: none !important;
}

/* Menü kapsayıcı */
div[role="radiogroup"] {
    display: flex !important;
    flex-direction: row !important;
    gap: 6px !important;
    padding: 4px 0 6px 0 !important;
    border-bottom: 2px solid #FFD700;
    overflow-x: auto !important;
}

/* Menü butonları */
div[role="radiogroup"] label {
    background: #0f172a !important; /* DAHA KOYU */
    border: 1px solid #FFD700 !important;
    border-radius: 10px !important;
    padding: 6px 14px !important; /* DAHA SIKI */
    box-shadow: none !important;
}

/* Menü yazısı */
div[role="radiogroup"] label p {
    color: #FFD700 !important;
    font-size: 0.95rem !important;
    font-weight: 700 !important;
    letter-spacing: 0.2px !important;
    margin: 0 !important;
}

/* Seçili menü */
div[role="radiogroup"] label[data-checked="true"] {
    background: #FFD700 !important;
}

div[role="radiogroup"] label[data-checked="true"] p {
    color: #0f172a !important;
}

/* =====================================================
   3. ANKET ŞIKLARI – BİTİŞİK LİSTE HALİ
===================================================== */

/* Anket buton kapsayıcı */
div.poll-marker + div .stButton {
    margin: 0 !important;
    padding: 0 !important;
}

/* Anket butonu */
div.poll-marker + div .stButton button {
    width: 100% !important;
    padding: 8px 12px !important;
    background: rgba(30,41,59,0.85) !important;
    border: none !important;
    border-bottom: 1px solid rgba(255,255,255,0.08) !important;
    border-radius: 0 !important;
    text-align: left !important;
    font-size: 0.95rem !important;
    color: #e5e7eb !important;
}

/* Hover */
div.poll-marker + div .stButton button:hover {
    background: rgba(255,215,0,0.15) !important;
    color: #fff !important;
}

/* =====================================================
   4. GÖNDERİLER ARASI MESAFE AZALTILDI
===================================================== */

.post-card {
    background: rgba(30,41,59,0.65);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 14px;
    padding: 10px;
    margin-bottom: 6px !important; /* ESKİ: 15px */
}

/* Post header */
.post-header {
    padding-bottom: 6px;
    margin-bottom: 6px;
}

/* =====================================================
   5. ANKET SONUÇ BARLARI (DAHA SIKI)
===================================================== */

.poll-bar-bg {
    height: 22px;
    margin-bottom: 3px;
}

.poll-text {
    font-size: 0.75rem;
}

/* =====================================================
   6. GENEL BUTON (ANKET HARİÇ)
===================================================== */

div.stButton > button {
    background: transparent !important;
    border: none !important;
    padding: 0.15rem 0.4rem !important;
    font-size: 1rem !important;
    color: #94a3b8 !important;
}

div.stButton > button:hover {
    color: #FFD700 !important;
}
</style>
"""

def get_user_display_html(username, size=40):
    ava, frame, name_style, _, font_style, title = users.get_user_styles(username)
    img_src = f"data:image/jpeg;base64,{ava}" if ava else "https://via.placeholder.com/150"
    f_html = f'<div class="frame-overlay frame-{frame}"></div>' if frame else ""
    classes = f"{f'name-{name_style}' if name_style else ''} {f'font-{font_style}' if font_style else ''}"
    return f"""
    <div style="display:flex;align-items:center;">
        <div class="avatar-container" style="width:{size}px;height:{size}px;">
            <img src="{img_src}" class="avatar-img" style="width:100%;height:100%;">
            {f_html}
        </div>
        <div style="margin-left:8px;">
            <div class="{classes}" style="font-size:0.85rem;">{username}</div>
        </div>
    </div>
    """

def get_post_style_css(username):
    _, _, _, post_style, font_style, _ = users.get_user_styles(username)
    return f"post-{post_style} font-{font_style}"