# -*- coding: utf-8 -*-
import streamlit as st
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials
import json

st.set_page_config(page_title="منصة الاقتراحات والشكاوى", page_icon="📝", layout="centered")
st.title("📝 منصة الاقتراحات والشكاوى للطلبة")
st.write("مرحبًا بك — الرجاء إدخال سنة البكالوريا ورقم التسجيل للتحقق ثم متابعة إرسال الشكوى/الاقتراح.")

# --------- معرفات Google Sheets ----------
STUDENTS_SHEET_ID = "1qDdqUC6TA6gNNVSbauLg_Un22vcgjjPB8kJitXa6qBo"   # قائمة الطلبة
SUGGESTIONS_SHEET_ID = "1z_OgVfrJQew28gf41Hck0uG1syH2mttJcOf6JodqdIU"  # شكاوى واقتراحات

STUDENTS_SHEET_NAME = "قائمة الطلبة"
SUGGESTIONS_SHEET_NAME = "شكاوى واقتراحات"

# --------- الاتصال بـ Google Sheets ----------
@st.cache_resource
def get_gspread_client():
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]
    try:
        info = st.secrets["google_service_account"]
        creds = Credentials.from_service_account_info(info, scopes=scopes)
        return gspread.authorize(creds)
    except Exception:
        pass

    try:
        raw = st.secrets["GOOGLE_CREDENTIALS"]
        if isinstance(raw, str):
            info = json.loads(raw)
        else:
            info = raw
        creds = Credentials.from_service_account_info(info, scopes=scopes)
        return gspread.authorize(creds)
    except Exception as e:
        raise RuntimeError("❌ لم أستطع قراءة بيانات الاعتماد. تأكد من إعداد GOOGLE_CREDENTIALS في Secrets.") from e


# --------- خطوة التحقق من الطالب ----------
if "student_found" not in st.session_state:
    st.session_state["student_found"] = False

if not st.session_state["student_found"]:
    with st.form("verify_form"):
        col1, col2 = st.columns(2)
        with col1:
            année_bac = st.text_input("📅 سنة البكالوريا (AnnéeBAC)", placeholder="مثال: 2023")
        with col2:
            mat_bac = st.text_input("🔢 رقم التسجيل (MatBAC)", placeholder="مثال: 123456789")
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
                    st.rerun()  # ← هذا الآن هو الدالة الصحيحة في Streamlit
                else:
                    st.error("⚠️ لم يتم العثور على بياناتك. تأكد من صحة المعلومات.")
            except Exception as e:
                st.error(f"❌ حدث خطأ أثناء التحقق: {e}")

# --------- إذا تم التحقق، عرض نموذج الشكوى ----------
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
        st.text_input("👤 اللقب (Nom)", value=nom, key="nom")
        st.text_input("👤 الاسم (Prénom)", value=prenom, key="prenom")
        st.text_input("📚 السنة (Année)", value=annee, key="annee")
        st.text_input("🏷️ التخصص (specialité)", value=specialite, key="specialite")
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
                st.success("✅ تم إرسال رسالتك وحفظها بنجاح 🎉")

                # إعادة تعيين الحالة بعد الإرسال
                for key in ["student_found", "student_record", "année_bac", "mat_bac"]:
                    if key in st.session_state:
                        del st.session_state[key]
                st.rerun()
            except Exception as e:
                st.error(f"❌ حدث خطأ أثناء حفظ الرسالة: {e}")
