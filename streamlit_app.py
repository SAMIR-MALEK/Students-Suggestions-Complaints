import streamlit as st
from datetime import datetime

st.set_page_config(page_title="�뭡 ��碩���� �����", page_icon="??", layout="centered")

st.title("?? �뭡 ��碩���� ����� ���頡")
st.write("���� �� �� ���뭡. 賓� 袟�� �碩��� �� ���� ����:")

type_choice = st.radio("���� �����:", ["�碩��", "����"])
student_name = st.text_input("�韫� ���� (����)")
student_email = st.text_input("�頩� ���袩��� (����)")
message = st.text_area("?? �袠 ����� ��:")

if st.button("�����"):
    if message.strip() == "":
        st.warning("?? 賓� ����� � �� �革���.")
    else:
        st.success("? �� ����� ����� �뤟�? �詟� �꫟���!")
        st.json({
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "type": type_choice,
            "name": student_name,
            "email": student_email,
            "message": message,
        })
