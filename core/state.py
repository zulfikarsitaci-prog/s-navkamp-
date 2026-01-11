import streamlit as st
import random

def init_state():
    defaults = {
        "logged_in": False,
        "user_role": None,
        "username": None,
        "class_code": "GENEL",
        "active_menu": "📢 Kampüs Duvar",
        "draft_content": "",
        "captcha_q": None,
        "captcha_a": None,
        "open_comments": []
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

    if st.session_state["captcha_q"] is None:
        a, b = random.randint(1, 9), random.randint(1, 9)
        st.session_state["captcha_q"] = f"{a} + {b}"
        st.session_state["captcha_a"] = a + b