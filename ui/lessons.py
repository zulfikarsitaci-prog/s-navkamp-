import streamlit as st
import time
import database.exams as exams
import database.score as score

def render_lessons():
    EX = exams.load_local_exams()
    if EX:
        cls = st.selectbox("Sınıf", list(EX.keys()))
        lsn = st.selectbox("Ders", list(EX[cls].keys()))
        with st.form("ex"):
            for i, q in enumerate(EX[cls][lsn]):
                st.write(f"{i+1}. {q.get('text') or q.get('question')}")
                if q['type']=='test': st.radio("Cv", q['options'], key=f"q{i}")
                else: st.text_input("Cv", key=f"q{i}")
            if st.form_submit_button("Bitir"):
                p = sum([x.get('points',0) for x in EX[cls][lsn]])
                score.add_score(st.session_state['username'], p, "Sınav")
                st.success(f"{p} Puan!")
                time.sleep(1)
                st.rerun()
