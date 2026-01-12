import database.users as users

MAIN_CSS = """
<style>
    ... (AZ ÖNCE VERDİĞİM TAM CSS AYNI ŞEKİLDE BURADA)
</style>
"""

def get_user_display_html(username, size=40):
    ava, frame, name_style, _, font_style, title = users.get_user_styles(username)
    img_src = f"data:image/jpeg;base64,{ava}" if ava else "https://via.placeholder.com/150/CCCCCC/FFFFFF?text=U"
    f_html = f'<div class="frame-overlay frame-{frame}"></div>' if frame else ""
    classes = f"{f'name-{name_style}' if name_style else ''} {f'font-{font_style}' if font_style else ''}"

    return f"""
    <div style="display:flex;align-items:center;">
        <div class="avatar-container" style="width:{size}px;height:{size}px;">
            <img src="{img_src}" class="avatar-img" style="width:100%;height:100%;">
            {f_html}
        </div>
        <div style="margin-left:8px;">
            <div class="{classes}" style="font-size:0.9rem;">{username}</div>
        </div>
    </div>
    """

def get_post_style_css(username):
    _, _, _, post_style, font_style, _ = users.get_user_styles(username)
    return f"post-{post_style} font-{font_style}"