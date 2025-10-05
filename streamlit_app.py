# -*- coding: utf-8 -*-
import streamlit as st
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials
import json
import time

# --------- إعداد الصفحة ----------
st.set_page_config(page_title="📝 منصة الاقتراحات والشكاوى", page_icon="📝", layout="centered")

# 🎨 CSS لتخصيص التصميم
st.markdown("""
<style>
/* الخلفية */
.stApp {
    background: linear-gradient(135deg, #0b1a3a 0%, #0d234d 100%);
    color: #ffffff;
}

/* العناوين */
h1, h2, h3, h4 {
    color: #ffcc00 !important;
    text-align: center;
    font-weight: 800;
}

/* مربعات الإدخال */
input, textarea, select {
    background-color: #162447 !important;
    color: #ffffff !important;
    border: 1px solid #ffcc00 !important;
    border-radius: 8px !important;
}

/* أزرار */
div.stButton > button {
    background-color: #ffcc00 !important;
    color: #0b1a3a !important;
    font-weight: bold !important;
    border-radius: 10px !important;
    width: 100% !important;
    transition: 0.3s;
}
div.stButton > button:hover {
    background-color: #ffaa00 !important;
    color: #ffffff !important;
    transform: scale(1.02);
}

/* رسائل النجاح والتحذير */
.stSuccess, .stWarning, .stInfo, .stError {
    background-color: #162447 !important;
    border: 1px solid #ffcc00 !important;
    color: #ffffff !important;
    border-radius: 8px !important;
}

/* نص الترحيب */
p, label {
    color: #dcdcdc !important;
    font-size: 16px !important;
}

/* فصل النماذج */
hr {
    border: 1px solid #ffcc00;
}
</style>
""", unsafe_allow_html=True)

# --------- واجهة المستخدم ----------
st.title("📝 منصة الاقتراحات والشكاوى للطلبة")
st.write("مرحبًا بك — الرجاء إدخال سنة البكالوريا ورقم التسجيل للتحقق ثم متابعة إرسال الشكوى أو الاقتراح 📩")

# --------- معرفات Google Sheets ----------
STUDENTS_SHEET_ID = "1qDdqUC6TA6gNNVSbauLg_Un22vcgjjPB8kJitXa6qBo"
SUGGESTIONS_SHEET_ID = "1z_OgVfrJQew28gf41Hck0uG1syH2mttJcOf6JodqdIU"
STUDENTS_SHEET_NAME = "قائمة الطلبة"
SUGGESTIONS_SHEET_NAME = "شكاوى واقتراحات"

# --------- الاتصال بـ Google Sheets ----------
@st.cache_resource
def get_gspread_client():
    scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    try:
        info = st.secrets["google_service_account"]
        creds = Credentials.from_service_account_info(info, scopes=scopes)
        return gspread.authorize(creds)
    except Exception:
        pass
    try:
        raw = st.secrets["GOOGLE_CREDENTIALS"]
        info = json.loads(raw) if isinstance(raw, str) else raw
        creds = Credentials.from_service_account_info(info, scopes=scopes)
        return gspread.authorize(creds)
    except Exception as e:
        raise RuntimeError("❌ لم أستطع قراءة بيانات الاعتماد.") from e

# --------- التحقق من الطالب ----------
if "student_found" not in st.session_state:
    st.session_state["student_found"] = False

if not st.session_state["student_found"]:
    with st.form("verify_form"):
        col1, col2 = st.columns(2)
        with col1:
            année_bac = st.text_input("📅 سنة البكالوريا", placeholder="مثال: 2023")
        with col2:
            mat_bac = st.text_input("🔢 رقم التسجيل", placeholder="مثال: 123456789")
        verify_clicked = st.form_submit_button("🔎 تحقق")

    if verify_clicked:
        if not année_bac or not mat_bac:
            st.warning("⚠️ الرجاء إدخال سنة البكالوريا ورقم التسجيل.")
        else:
            try:
                client = get_gspread_client()
                sheet = client.open_by_key(STUDENTS_SHEET_ID)
                worksheet = sheet.worksheet(STUDENTS_SHEET_NAME)
                all_values = worksheet.get_all_records()

                student_record = next(
                    (row for row in all_values if str(row.get("AnnéeBAC", "")).strip() == str(année_bac).strip() 
                     and str(row.get("MatBAC", "")).strip() == str(mat_bac).strip()), 
                    None
                )

                if student_record:
                    st.session_state["student_found"] = True
                    st.session_state["student_record"] = student_record
                    st.session_state["année_bac"] = année_bac
                    st.session_state["mat_bac"] = mat_bac
                    st.success(f"✅ مرحبًا {student_record.get('Nom','')} {student_record.get('Prénom','')} — تم التحقق بنجاح.")
                    st.rerun()
                else:
                    st.error("⚠️ لم يتم العثور على بياناتك. تأكد من صحة المعلومات.")
            except Exception as e:
                st.error(f"❌ حدث خطأ أثناء التحقق: {e}")

# --------- نموذج الشكوى ----------
if st.session_state["student_found"]:
    student_record = st.session_state["student_record"]
    année_bac = st.session_state["année_bac"]
    mat_bac = st.session_state["mat_bac"]

    st.markdown("---")
    st.subheader("📨 استمارة الشكاوى والاقتراحات")

    nom = student_record.get("Nom", "")
    prenom = student_record.get("Prénom", "")
    annee = student_record.get("Année", "")
    specialite = student_record.get("specialité", "")

    with st.form("msg_form"):
        st.text_input("👤 اللقب", value=nom, key="nom")
        st.text_input("👤 الاسم", value=prenom, key="prenom")
        st.text_input("📚 السنة", value=annee, key="annee")
        st.text_input("🏷️ التخصص", value=specialite, key="specialite")
        email = st.text_input("📧 البريد الإلكتروني (اختياري)")
        type_choice = st.selectbox("📌 نوع الرسالة:", ["اقتراح", "شكوى", "استفسار"])
        message = st.text_area("✍️ نص الرسالة:")
        send_clicked = st.form_submit_button("📤 إرسال")

    if send_clicked:
        if not message.strip():
            st.warning("⚠️ الرجاء كتابة نص الرسالة.")
        else:
            try:
                client = get_gspread_client()
                sheet = client.open_by_key(SUGGESTIONS_SHEET_ID)
                worksheet = sheet.worksheet(SUGGESTIONS_SHEET_NAME)

                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                row_values = [
                    année_bac,
                    mat_bac,
                    st.session_state.get("nom", nom),
                    st.session_state.get("prenom", prenom),
                    st.session_state.get("annee", annee),
                    st.session_state.get("specialite", specialite),
                    now,
                    email,
                    type_choice,
                    message
                ]

                worksheet.append_row(row_values, value_input_option="RAW")
                st.success("✅ شكرا لك! تم إرسال انشغالك وسيتم الاطلاع عليه قريبًا.")
                st.info("🔄 سيتم إعادتك إلى صفحة التحقق خلال 4 ثوانٍ...")
                time.sleep(4)

                for key in ["student_found", "student_record", "année_bac", "mat_bac"]:
                    if key in st.session_state:
                        del st.session_state[key]
                st.rerun()

            except Exception as e:
                st.error(f"❌ حدث خطأ أثناء حفظ الرسالة: {e}")
