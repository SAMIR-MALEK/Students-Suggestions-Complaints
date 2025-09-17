# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="منصة الاقتراحات والشكاوى", page_icon="📝", layout="centered")

st.title("📝 منصة الاقتراحات والشكاوى للطلبة")
st.write("مرحبًا بك في المنصة، يمكنك هنا إرسال شكوى أو اقتراحك بسهولة ")

# 🟢 معلومات الطالب
student_name = st.text_input("👤 الاسم الكامل")
student_email = st.text_input("📧 البريد الإلكتروني (اختياري)")

# 🟢 نوع الرسالة
type_choice = st.selectbox(
    "📌 اختر نوع الرسالة:",
    ["اقتراح", "شكوى", "استفسار"]
)

# 🟢 نص الرسالة
message = st.text_area("✍️ أكتب رسالتك هنا:")

# 🟢 زر الإرسال
if st.button("إرسال"):
    if message.strip() == "":
        st.warning("⚠️ يرجى إدخال نص قبل الإرسال.")
    else:
        # حفظ البيانات في شكل JSON للعرض
        st.success("✅ تم إرسال رسالتك بنجاح، شكراً لمساهمتك!")
        st.json({
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "type": type_choice,
            "name": student_name,
            "email": student_email,
            "message": message,
        })
