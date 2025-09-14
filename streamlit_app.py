import streamlit as st
from datetime import datetime

st.set_page_config(page_title="êë­¡ ŸéŸç¢©Ÿ¥Ÿ¢ íŸé¬èŸíî", page_icon="??", layout="centered")

st.title("?? êë­¡ ŸéŸç¢©Ÿ¥Ÿ¢ íŸé¬èŸíî ééáé ¡")
st.write("šìéŸñ  è åï Ÿéêë­¡. ï©¤î è¢Ÿ ¡ Ÿç¢©Ÿ¥è ší ¬èíŸè š§ëŸì:")

type_choice = st.radio("Ÿ¦¢© Ÿéëíã:", ["Ÿç¢©Ÿ¥", "¬èíî"])
student_name = st.text_input("ŸéŸ«ê íŸééç  (Ÿ¦¢ïŸ©ï)")
student_email = st.text_input("Ÿé ©ï§ Ÿééè¢©íëï (Ÿ¦¢ïŸ©ï)")
message = st.text_area("?? šè¢  ©«Ÿé¢è ìëŸ:")

if st.button("©«Ÿé"):
    if message.strip() == "":
        st.warning("?? ï©¤î §¦Ÿé ë­ ç é Ÿé©«Ÿé.")
    else:
        st.success("? ¢ê ©«Ÿé ©«Ÿé¢è  ë¤Ÿ¥? ¬è©Ÿñ éê«Ÿìê¢è!")
        st.json({
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "type": type_choice,
            "name": student_name,
            "email": student_email,
            "message": message,
        })
