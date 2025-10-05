# -*- coding: utf-8 -*-
import streamlit as st
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials
import json
import time

st.set_page_config(page_title="منصة الاقتراحات والشكاوى", page_icon="📝", layout="wide")

LOGO_URL = ""  # ضع رابط الشعـار هنا إن وُجد

# ---- CSS نظيف ومغلق بشكل صحيح ----
css = """
<link href="https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap" rel="stylesheet">
<style>
/* الخط العام */
html, body, [class*="css"]  {
    font-family: 'Cairo', sans-serif;
}

/* الخلفية العامة - أزرق ليلي */
.stApp {
    background: linear-gradient(180deg, #061028 0%, #081631 100%);
    color: #f5f5f5;
    min-height: 100vh;
    padding: 30px 40px;
}

/* الحاوية الرئيسية بعرض كامل */
.container-wide {
    max-width: 1200px;
    margin: 0 auto;
}

/* بانر الشعار */
.top-banner {
    display: flex;
    align-items: center;
    gap: 18px;
    padding: 18px 22px;
    border-radius: 14px;
    background: linear-gradient(90deg, rgba(255,204,0,0.06), rgba(255,204,0,0.03));
    border: 1px solid rgba(255,204,0,0.08);
    margin-bottom: 22px;
}
.top-banner img {
    height: 56px;
    width: 56px;
    object-fit: contain;
    border-radius: 8px;
    background: rgba(255,255,255,0.04);
    padding: 6px;
}
.top-banner .title {
    font-size: 20px;
    font-weight: 700;
    color: #ffdb4d; /* أصفر فاتح للعناوين */
}
.top-banner .subtitle {
    font-size: 13px;
    color: #d8e6ff;
    opacity: 0.9;
}

/* البطاقة الرئيسية (تمتد بعرض المساحة المتاحة) */
.card {
    background: #e9eef6; /* بطاقة رمادية فاتحة */
    color: #071025;
    border-radius: 14px;
    padding: 22px;
    box-shadow: 0 8px 30px rgba(2,6,23,0.45);
    border: 1px solid rgba(7,16,37,0.06);
    margin-bottom: 18px;
}

/* عناوين داخل البطاقة */
.card h2 {
    margin: 0 0 6px 0;
    color: #ffcc00; /* أصفر للعناوين */
}
.card p.lead {
    margin: 0 0 12px 0;
    color: #0b2540;
    opacity: 0.9;
}

/* تحكمات الإدخال داخل البطاقة */
.card input, .card textarea, .card select {
    background: #ffffff !important;
    color: #071025 !important;
    border: 1px solid rgba(7,16,37,0.08) !important;
    border-radius: 8px !important;
    padding: 10px 12px !important;
}

/* زر الإرسال */
.stButton > button {
    background: linear-gradient(180deg, #ffcc00 0%, #ffb400 100%) !important;
    color: #071025 !important;
    font-weight: 700 !important;
    border: none !important;
    padding: 10px 18px !important;
    border-radius: 10px !important;
    box-shadow: 0 6px 18px rgba(255,188,51,0.18) !important;
}
.stButton > button:hover {
    transform: translateY(-1px);
}

/* رسائل الحالة داخل التصميم */
.stAlert {
    border-radius: 10px;
    padding: 10px 12px;
}

/* تنسيق الأعمدة في شاشات كبيرة */
@media (min-width: 1000px) {
    .two-cols {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 16px;
    }
}
</style>
"""
# حقن الـ CSS داخل الصفحة (هنا المفتاح: unsafe_allow_html=True)
st.markdown(css, unsafe_allow_html=True)

# ---- رأس الصفحة (بانر مع الشعار أو أيقونة بديلة) ----
st.markdown('<div class="container-wide">', unsafe_allow_html=True)
if LOGO_URL:
    st.markdown(f'''
        <div class="top-banner">
            <img src="{LOGO_URL}" alt="logo" />
            <div>
                <div class="title">📨 منصة الاقتراحات والشكاوى</div>
                <div class="subtitle">منصة لطلبة كلية الحقوق والعلوم السياسية — أدخل بياناتك ثم أرسل شكواك أو اقتراحك</div>
            </div>
        </div>
    ''', unsafe_allow_html=True)
else:
    st.markdown('''
        <div class="top-banner">
            <div style="height:56px;width:56px;border-radius:8px;background:#071025;display:flex;align-items:center;justify-content:center;font-size:22px;color:#ffcc00">📝</div>
            <div>
                <div class="title">📨 منصة الاقتراحات والشكاوى</div>
                <div class="subtitle">منصة لطلبة كلية الحقوق والعلوم السياسية — أدخل بياناتك ثم أرسل شكواك أو اقتراحك</div>
            </div>
        </div>
    ''', unsafe_allow_html=True)

# ---- معرفات Google Sheets ----
STUDENTS_SHEET_ID = "1qDdqUC6TA6gNNVSbauLg_Un22vcgjjPB8kJitXa6qBo"
SUGGESTIONS_SHEET_ID = "1z_OgVfrJQew28gf41Hck0uG1syH2mttJcOf6JodqdIU"
STUDENTS_SHEET_NAME = "قائمة الطلبة"
SUGGESTIONS_SHEET_NAME = "شكاوى واقتراحات"

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
        raise RuntimeError("❌ لم أستطع قراءة بيانات الاعتماد. تأكد من إعداد GOOGLE_CREDENTIALS في Secrets.") from e

# ---- حالة الجلسة ----
if "student_found" not in st.session_state:
    st.session_state["student_found"] = False

# ----- البطاقة الرئيسية (يمتد بعرض الصفحة) -----
st.markdown('<div class="card">', unsafe_allow_html=True)

if not st.session_state["student_found"]:
    st.markdown("<h2>🔎 تحقق من بياناتك</h2>", unsafe_allow_html=True)
    st.markdown('<p class="lead">الرجاء إدخال سنة البكالوريا ورقم التسجيل للتحقق ثم متابعة إرسال الشكوى أو الاقتراح.</p>', unsafe_allow_html=True)

    with st.form("verify_form"):
        col1, col2 = st.columns([1,1])
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
                all_values = worksheet.get_all_records()  # جيد للقوائم الصغيرة
                student_record = next(
                    (row for row in all_values
                     if str(row.get("AnnéeBAC","")).strip() == str(année_bac).strip()
                     and str(row.get("MatBAC","")).strip() == str(mat_bac).strip()),
                    None
                )
                if student_record:
                    st.session_state["student_found"] = True
                    st.session_state["student_record"] = student_record
                    st.session_state["année_bac"] = année_bac
                    st.session_state["mat_bac"] = mat_bac
                    st.success(f"✅ مرحبًا {student_record.get('Nom','')} {student_record.get('Prénom','')} — تم التحقق بنجاح.")
                    time.sleep(0.6)
                    st.experimental_rerun()
                else:
                    st.error("⚠️ لم يتم العثور على بياناتك. تأكد من صحة المعلومات.")
            except Exception as e:
                st.error(f"❌ حدث خطأ أثناء التحقق: {e}")

if st.session_state["student_found"]:
    student_record = st.session_state["student_record"]
    année_bac = st.session_state["année_bac"]
    mat_bac = st.session_state["mat_bac"]

    st.markdown("<h2>📨 استمارة الشكاوى والاقتراحات</h2>", unsafe_allow_html=True)
    st.markdown('<p class="lead">املأ الحقول التالية وسيتم حفظ الشكوى في قاعدة بيانات المنصة.</p>', unsafe_allow_html=True)

    with st.form("msg_form"):
        nom = st.text_input("👤 اللقب (Nom)", value=student_record.get("Nom",""), key="nom")
        prenom = st.text_input("👤 الاسم (Prénom)", value=student_record.get("Prénom",""), key="prenom")
        annee = st.text_input("📚 السنة (Année)", value=student_record.get("Année",""), key="annee")
        specialite = st.text_input("🏷️ التخصص (specialité)", value=student_record.get("specialité",""), key="specialite")
        email = st.text_input("📧 البريد الإلكتروني (اختياري)", placeholder="example@mail.com")
        type_choice = st.selectbox("📌 نوع الرسالة:", ["اقتراح","شكوى","استفسار"])
        message = st.text_area("✍️ نص الرسالة:")
        send_clicked = st.form_submit_button("📤 إرسال")

    if send_clicked:
        if not message or not message.strip():
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
                st.success("✅ شكراً! تم إرسال انشغالك بنجاح.")
                st.info("🔄 ستعود لصفحة التحقق آلياً...")
                time.sleep(1.2)
                for key in ["student_found","student_record","année_bac","mat_bac"]:
                    if key in st.session_state:
                        del st.session_state[key]
                st.experimental_rerun()
            except Exception as e:
                st.error(f"❌ حدث خطأ أثناء حفظ الرسالة: {e}")

# غلق البطاقة والحاوية
st.markdown("</div>", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)
