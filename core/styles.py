import streamlit as st

def load_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@700&family=Orbitron:wght@700&family=Rye&family=Dancing+Script:wght@700&family=Metal+Mania&display=swap');

    .login-container { text-align: center; margin-top: 20px; margin-bottom: 30px; }
    .login-sub { color: #94a3b8; font-size: 1rem; margin-bottom: 5px; font-family: sans-serif; letter-spacing: 1px; }
    .login-main { 
        font-family: 'Cinzel', serif;
        color: #FFD700; 
        font-size: 2.2rem; 
        text-shadow: 2px 2px 4px #000; 
        line-height: 1.2; 
        margin: 10px 0;
        font-weight: bold;
    }
    .login-bottom { color: #cbd5e1; font-family: 'Orbitron', sans-serif; font-size: 0.9rem; margin-top: 5px; }

    .top-bar { background: #1e293b; padding: 10px; border-radius: 8px; display: flex; justify-content: space-between; border-bottom: 2px solid #FFD700; margin-bottom: 10px; }

    .post-card {
        background-color: #1e293b; 
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 15px;
        margin-bottom: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        position: relative;
    }
    .post-header { display: flex; align-items: center; border-bottom: 1px solid #334155; padding-bottom: 8px; margin-bottom: 8px; }
    .post-content { color: #e2e8f0; font-size: 0.95rem; line-height: 1.5; white-space: pre-wrap; margin-bottom: 10px; }
    .post-image { width: 100%; border-radius: 8px; margin-top: 5px; }

    div.stButton > button {
        background-color: transparent !important;
        border: none !important;
        color: #94a3b8 !important;
        font-size: 1.2rem !important;
        box-shadow: none !important;
    }
    div.stButton > button:hover {
        color: #FFD700 !important;
        transform: scale(1.1);
    }

    div[data-testid="stPopoverBody"] button {
        background-color: #334155 !important;
        color: white !important;
        border: 1px solid #475569 !important;
        margin-bottom: 5px !important;
        width: 100% !important;
        font-size: 0.9rem !important;
    }

    .comment-box { background: #0f172a; padding: 8px; border-radius: 6px; margin-top: 6px; font-size: 0.85rem; border-left: 3px solid #334155; }

    .shop-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 6px; margin-top: 10px; }
    @media only screen and (max-width: 600px) { .shop-grid { grid-template-columns: repeat(3, 1fr); } }
    .shop-item { background: #0f172a; border: 1px solid #334155; border-radius: 8px; padding: 5px; text-align: center; display: flex; flex-direction: column; align-items: center; justify-content: space-between; height: 110px; }
    .shop-name { font-size: 0.65rem; color: #cbd5e1; }
    .shop-price { background: #10b981; color: white; padding: 2px 8px; border-radius: 8px; font-size: 0.65rem; }

    .font-Cinzel { font-family: 'Cinzel', serif; }
    .font-Orbitron { font-family: 'Orbitron', sans-serif; }
    .font-Rye { font-family: 'Rye', serif; }
    .font-Dancing { font-family: 'Dancing Script', cursive; }
    .font-Metallic { font-family: 'Metal Mania', cursive; color: #b0b0b0; text-shadow: 2px 2px 0px #000; letter-spacing: 1px; }

    .avatar-container { position: relative; display: inline-block; margin-right: 8px; }
    .avatar-img { width: 40px; height: 40px; border-radius: 50%; object-fit: cover; }

    .frame-Gold { border: 2px solid #FFD700; border-radius: 50%; box-shadow: 0 0 5px #FFD700; }
    .frame-Neon { border: 2px solid #00ffff; border-radius: 50%; box-shadow: 0 0 5px #00ffff; }
    .frame-Fire { border: 2px solid #ff4500; border-radius: 50%; box-shadow: 0 0 10px #ff4500; }
    .frame-King { border: 3px solid #ffd700; border-radius: 50%; box-shadow: 0 0 10px #ffd700; }
    .frame-Matrix { border: 2px dotted #00ff00; border-radius: 50%; }

    .name-Glitch { color: #00ffff; text-shadow: 1px 0 #ff00ff; font-weight: bold; }
    .name-Fire { color: #ff4500; text-shadow: 0 0 3px #ff0000; font-weight: bold; }
    .name-Gold { background: linear-gradient(to right, #BF953F, #FCF6BA, #B38728); -webkit-background-clip: text; color: transparent; font-weight: 900; }

    .post-Cyan { color: #00ffff !important; }
    .post-Lime { color: #00ff00 !important; }
    .post-Pink { color: #ff69b4 !important; }
    .post-Gold { color: #ffd700 !important; }

    .title-badge { background: #334155; color: #94a3b8; padding: 1px 5px; border-radius: 3px; font-size: 0.6rem; margin-left: 4px; }

    iframe { width: 100% !important; }
    </style>
    """, unsafe_allow_html=True)