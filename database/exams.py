import os
import json
import streamlit as st

@st.cache_data
def load_local_exams():
    # exams.json dosyasının ana dizinde olduğunu varsayıyoruz
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    EXAM_PATH = os.path.join(BASE_DIR, "exams.json")
    
    if os.path.exists(EXAM_PATH):
        try: return json.load(open(EXAM_PATH, "r", encoding="utf-8"))
        except: return {}
    return {}
