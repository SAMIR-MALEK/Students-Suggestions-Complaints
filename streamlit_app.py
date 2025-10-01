# -*- coding: utf-8 -*-
import streamlit as st
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials
import json

st.set_page_config(page_title="منصة الاقتراحات والشكاوى", page_icon="📝", layout="centered")
st.title("📝 منصة الاقتراحات والشكاوى للطلبة")
st.write("مرحبًا بك — الرجاء إدخال سنة البكالوريا ورقم التسجيل للتحقق ثم متابعة إرسال الشكوى/الاقتراح.")

# --------- ثوابت (ID الجداول) ----------
STUDENTS_SHEET_ID = "1qDdqUC6TA6gNNVSbauLg_Un22vcgjjPB8kJitXa6qBo"   # قائمة الطلبة
SUGGESTIONS_SHEET_ID = "1z_OgVfrJQew28gf41Hck0uG1syH2mttJcOf6JodqdIU"  # شكاوى واقتراحات

STUDENTS_SHEET_NAME = "قائمة الطلبة"
SUGGESTIONS_SHEET_NAME = "شكاوى واقتراحات"

# --------- دالة الاتصال بـ Google Sheets (مرنة في قراءة الأسرار) ----------
@st.cache_resource
def get_gspread_client():
    """
    يحاول الحصول على بيانات اعتماد Service Account بطريقتين:
    1) st.secrets['google_service_account'] (مساحة Streamlit secrets بصيغة TOML)
    2) st.secrets['GOOGLE_CREDENTIALS'] (مفتاح JSON مخزّن كقيمة نصية)
    """
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]

    # حالة (1): st.secrets["google_service_account"] متوقع كـ dict (streamlit secrets standard)
    try:
        info = st.secrets["google_service_account"]
        creds = Credentials.from_service_account_info(info, scopes=scopes)
        client = gspread.authorize(creds)
        return client
    except Exception:
        pass

    # حالة (2): st.secrets["GOOGLE_CREDENTIALS"] متوقع كنص JSON
    try:
        raw = st.secrets["GOOGLE_CREDENTIALS"]
        # إذا كانت القيمة مخزّنة بالفعل كـ dict في st.secrets فهي تمر بالطريقة السابقة
        if isinstance(raw, str):
            info = json.loads(raw)
        else:
            info = raw
        creds = Credentials.from_service_account_info(info, scopes=scopes)
        client = gspread.authorize(creds)
        return client
    except Exception as e:
        # نرفع خطأ واضح ليظهر في الواجهة
        raise RuntimeError("خطأ في قراءة بيانات الاعتماد من st.secrets. تأكد من إضافة google_service_account أو GOOGLE_CREDENTIALS.") from e

# --------- واجهة التحقق (الخطوة الأولى) ----------
with st.form("verify_form"):
    col1, col2 = st.columns(2)
    with col1:
        année_bac = st.text_input("سنة البكالوريا (AnnéeBAC)", placeholder="مثال: 2023")
    with col2:
        mat_bac = st.text_input("رقم التسجيل (MatBAC)", placeholder="مثال: 123456789")
    verify_clicked = st.form_submit_button("🔎 تحقق")

student_found = None
student_record = None

if verify_clicked:
    if (not année_bac) or (not mat_bac):
        st.warning("⚠️ الرجاء ملء سنة البكالوريا ورقم التسجيل قبل التحقق.")
    else:
        try:
            client = get_gspread_client()
            sheet = client.open_by_key(STUDENTS_SHEET_ID)
            worksheet = sheet.worksheet(STUDENTS_SHEET_NAME)

            # قراءة كل البيانات (كمصفوفة)
            all_values = worksheet.get_all_records()  # list of dicts keyed by header
            # البحث بمطابقة AnnéeBAC و MatBAC (مراعاة النصوص)
            for row in all_values:
                # بعض الخانات قد تكون أرقامًا؛ نحوّل إلى str للمقارنة الآمنة
                if str(row.get("AnnéeBAC", "")).strip() == str(année_bac).strip() and str(row.get("MatBAC", "")).strip() == str(mat_bac).strip():
                    student_found = True
                    student_record = row
                    break

            if student_found:
                st.success(f"✅ مرحبًا {student_record.get('Nom','')} {student_record.get('Prénom','')} — تم التحقق من وجودك.")
            else:
                st.error("⚠️ لم يتم العثور على بياناتك في قائمة الطلبة. تأكد من سنة البكالوريا ورقم التسجيل.")
        except Exception as e:
            st.error(f"❌ خطأ أثناء التحقق: {e}")

# --------- إذا وُجد الطالب: اظهار نموذج الشكوى والاقتراح ----------
if student_found:
    st.markdown("---")
    st.subheader("استمارة الشكاوى والاقتراحات")

    # نملأ بعض الحقول مسبقًا من سجل الطالب
    nom = student_record.get("Nom", "")
    prenom = student_record.get("Prénom", "")
    annee = student_record.get("Année", "")
    specialite = student_record.get("specialité", "")

    # الاستمارة
    with st.form("msg_form"):
        st.text_input("اللقب (Nom)", value=nom, key="nom")
        st.text_input("الاسم (Prénom)", value=prenom, key="prenom")
        st.text_input("السنة (Année)", value=annee, key="annee")
        st.text_input("التخصص (specialité)", value=specialite, key="specialite")
        email = st.text_input("📧 البريد الإلكتروني (اختياري)")
        type_choice = st.selectbox("📌 نوع الرسالة:", ["اقتراح", "شكوى", "استفسار"])
        message = st.text_area("✍️ نص الرسالة:")
        send_clicked = st.form_submit_button("📤 إرسال")

    if send_clicked:
        if not message.strip():
            st.warning("⚠️ الرجاء كتابة نص الرسالة قبل الإرسال.")
        else:
            try:
                client = get_gspread_client()
                sheet = client.open_by_key(SUGGESTIONS_SHEET_ID)
                worksheet = sheet.worksheet(SUGGESTIONS_SHEET_NAME)

                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                # ترتيب الأعمدة كما طلبت
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
                st.success("✅ تم إرسال رسالتك وحفظها بنجاح في Google Sheets.")
            except Exception as e:
                st.error(f"❌ حدث خطأ أثناء حفظ الرسالة: {e}")
