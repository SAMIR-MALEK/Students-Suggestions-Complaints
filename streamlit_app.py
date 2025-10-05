# -*- coding: utf-8 -*-
"""
streamlit_app.py
منصة انشغالاتي - نسخة بواجهة احترافية بعرض كامل
"""

import streamlit as st
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials
import json
import time

# ---------------- إعداد الصفحة ----------------
st.set_page_config(
    page_title="منصة انشغالاتي",
    page_icon="📝",
    layout="wide",
)

# رابط الشعار (ضع رابط الصورة هنا إن رغبت، اتركه فارغاً لعرض أيقونة بديلة)
LOGO_URL = ""

# ----------- CSS + خط عربي (Cairo) -----------
css = """
<link href="https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700&display=swap" rel="stylesheet">
<style>
/* استخدام خط Cairo */
html, body, [class*="css"]  {
    font-family: 'Cairo', sans-serif;
}

/* الخلفية العامة - أزرق ليلي */
.stApp {
    background: linear-gradient(180deg, #031028 0%, #071a30 100%);
    color: #f5f8ff;
    min-height: 100vh;
    padding: 28px 36px;
}

/* حاوية المحتوى بعرض محدود ومركزي داخل العرض الكامل */
.container-wide {
    max-width: 1200px;
    margin: 0 auto;
}

/* بانر الشعار */
.top-banner {
    display: flex;
    align-items: center;
    gap: 16px;
    padding: 14px 18px;
    border-radius: 12px;
    background: linear-gradient(90deg, rgba(255,204,0,0.05), rgba(255,204,0,0.02));
    border: 1px solid rgba(255,204,0,0.06);
    margin-bottom: 18px;
}
.top-banner img {
    height: 56px;
    width: 56px;
    object-fit: contain;
    border-radius: 10px;
    background: rgba(255,255,255,0.04);
    padding: 6px;
}
.top-banner .title {
    font-size: 20px;
    font-weight: 700;
    color: #ffd966; /* أصفر فاتح */
}
.top-banner .subtitle {
    font-size: 13px;
    color: #d6eaff;
    opacity: 0.95;
    margin-top: 4px;
}

/* البطاقة الرئيسية (تمتد بعرض المساحة المتاحة داخل container-wide) */
.card {
    background: #eef5fb; /* بطاقة رمادية فاتحة / مائلة للزرق */
    color: #071022;
    border-radius: 14px;
    padding: 22px;
    box-shadow: 0 12px 36px rgba(2,6,23,0.45);
    border: 1px solid rgba(7,16,37,0.06);
    margin-bottom: 24px;
}

/* عناوين داخل البطاقة */
.card h2 {
    margin: 0 0 8px 0;
    color: #ffcc00; /* أصفر للعناوين */
    font-size: 20px;
}
.card p.lead {
    margin: 0 0 14px 0;
    color: #08304f;
    opacity: 0.95;
}

/* تنسيق الحقول داخل البطاقة */
.card .stTextInput>div>div>input,
.card .stTextArea>div>div>textarea,
.card .stSelectbox>div>div>div[role="combobox"] {
    background: #ffffff !important;
    color: #071022 !important;
    border: 1px solid rgba(7,16,37,0.08) !important;
    border-radius: 10px !important;
    padding: 10px 12px !important;
}

/* أزرار */
.stButton > button {
    background: linear-gradient(180deg, #ffd24d 0%, #ffb400 100%) !important;
    color: #071022 !important;
    font-weight: 700 !important;
    border: none !important;
    padding: 10px 18px !important;
    border-radius: 10px !important;
    box-shadow: 0 8px 20px rgba(255,180,40,0.12) !important;
}
.stButton > button:hover {
    transform: translateY(-2px);
}

/* رسائل الحالة */
.stAlert {
    border-radius: 10px;
    padding: 10px 12px;
}

/* تخطيط أعمدة حكيم للشاشات الكبيرة */
@media (min-width: 1000px) {
    .two-cols {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 16px;
    }
}

/* تحسين الهوامش على الأجهزة الصغيرة */
@media (max-width: 999px) {
    .container-wide { padding: 0 12px; }
    .top-banner { padding: 12px; }
    .card { padding: 16px; }
}
</style>
"""

st.markdown(css, unsafe_allow_html=True)

# ---------------- معرفات Google Sheets ----------------
# ضع هذه القيم كما في ملفك أو st.secrets
STUDENTS_SHEET_ID = "1qDdqUC6TA6gNNVSbauLg_Un22vcgjjPB8kJitXa6qBo"   # قائمة الطلبة
SUGGESTIONS_SHEET_ID = "1z_OgVfrJQew28gf41Hck0uG1syH2mttJcOf6JodqdIU"  # شكاوى واقتراحات

STUDENTS_SHEET_NAME = "قائمة الطلبة"
SUGGESTIONS_SHEET_NAME = "شكاوى واقتراحات"

# ---------------- دالة الاتصال بـ Google Sheets ----------------
@st.cache_resource
def get_gspread_client():
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]
    # المحاولة الأولى: استخدام secret باسم google_service_account
    try:
        info = st.secrets["google_service_account"]
        creds = Credentials.from_service_account_info(info, scopes=scopes)
        return gspread.authorize(creds)
    except Exception:
        pass

    # المحاولة الثانية: استخدام GOOGLE_CREDENTIALS كسلسلة JSON
    try:
        raw = st.secrets["GOOGLE_CREDENTIALS"]
        if isinstance(raw, str):
            info = json.loads(raw)
        else:
            info = raw
        creds = Credentials.from_service_account_info(info, scopes=scopes)
        return gspread.authorize(creds)
    except Exception as e:
        raise RuntimeError("❌ لم أستطع قراءة بيانات الاعتماد. تأكد من إعداد GOOGLE_CREDENTIALS أو google_service_account في st.secrets.") from e

# ---------------- حالة الجلسة ----------------
if "student_found" not in st.session_state:
    st.session_state["student_found"] = False

# ---------------- رأس الصفحة (بانر مع الشعار أو أيقونة بديلة) ----------------
st.markdown('<div class="container-wide">', unsafe_allow_html=True)

if LOGO_URL:
    st.markdown(
        f'''
        <div class="top-banner">
            <img src="{LOGO_URL}" alt="logo" />
            <div>
                <div class="title">📨 منصة انشغالاتي</div>
                <div class="subtitle">منصة رقمية لاستقبال انشغالات، شكاوى الطلبة واقتراحاتهم ومعالجتها في أقرب الآجال</div>
            </div>
        </div>
        ''',
        unsafe_allow_html=True,
    )
else:
    # بانر نصي بديل
    st.markdown(
        '''
        <div class="top-banner">
            <div style="height:56px;width:56px;border-radius:10px;background:#071022;display:flex;align-items:center;justify-content:center;font-size:22px;color:#ffd966">📝</div>
            <div>
                <div class="title">📨 منصة انشغالاتي</div>
                <div class="subtitle">منصة رقمية لاستقبال انشغالات، شكاوى الطلبة واقتراحاتهم ومعالجتها في أقرب الآجال</div>
            </div>
        </div>
        ''',
        unsafe_allow_html=True,
    )

# ---------------- البطاقة الرئيسية (يمتد داخل container-wide) ----------------
st.markdown('<div class="card">', unsafe_allow_html=True)

# ---------- خطوة التحقق من الطالب (نموذج) ----------
if not st.session_state["student_found"]:
    st.markdown("<h2>🔎 تحقق من بياناتك</h2>", unsafe_allow_html=True)
    st.markdown('<p class="lead">الرجاء إدخال سنة البكالوريا ورقم التسجيل للتحقق ثم متابعة إرسال الشكوى أو الاقتراح.</p>', unsafe_allow_html=True)

    with st.form("verify_form"):
        col1, col2 = st.columns([1, 1])
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

                # ملاحظة: get_all_records() مناسب لقوائم صغيرة؛ إذا كانت الجدول كبيراً،
                # فكر باستخدام worksheet.find() لتحسين الأداء.
                all_values = worksheet.get_all_records()

                student_record = next(
                    (row for row in all_values
                     if str(row.get("AnnéeBAC", "")).strip() == str(année_bac).strip()
                     and str(row.get("MatBAC", "")).strip() == str(mat_bac).strip()),
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

# ---------- استمارة الشكوى والاقتراح ----------
if st.session_state["student_found"]:
    student_record = st.session_state["student_record"]
    année_bac = st.session_state["année_bac"]
    mat_bac = st.session_state["mat_bac"]

    st.markdown("<h2>📨 استمارة الشكاوى والاقتراحات</h2>", unsafe_allow_html=True)
    st.markdown('<p class="lead">املأ الحقول التالية وسيتم حفظ الشكوى في قاعدة بيانات المنصة.</p>', unsafe_allow_html=True)

    with st.form("msg_form"):
        nom = st.text_input("👤 اللقب (Nom)", value=student_record.get("Nom", ""), key="nom")
        prenom = st.text_input("👤 الاسم (Prénom)", value=student_record.get("Prénom", ""), key="prenom")
        annee = st.text_input("📚 السنة (Année)", value=student_record.get("Année", ""), key="annee")
        specialite = st.text_input("🏷️ التخصص (specialité)", value=student_record.get("specialité", ""), key="specialite")
        email = st.text_input("📧 البريد الإلكتروني (اختياري)", placeholder="example@mail.com")
        type_choice = st.selectbox("📌 نوع الرسالة:", ["اقتراح", "شكوى", "استفسار"])
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

                # رسالة نجاح ثم العودة لصفحة التحقق (كما أردت)
                st.success("✅ شكراً! تم إرسال انشغالك بنجاح وسيتم الاطلاع عليه ومعالجته في أقرب الآجال.")
                st.info("🔄 ستعاد للصفحة الرئيسية تلقائياً خلال لحظات...")

                time.sleep(1.2)
                for key in ["student_found", "student_record", "année_bac", "mat_bac"]:
                    if key in st.session_state:
                        del st.session_state[key]
                st.experimental_rerun()

            except Exception as e:
                st.error(f"❌ حدث خطأ أثناء حفظ الرسالة: {e}")

# إغلاق البطاقة والحاوية
st.markdown("</div>", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

# ---------------- ملاحظة المراجع (عرض خفيف في أسفل الصفحة) ----------------
st.markdown(
    """
    <div style="margin-top:8px;color:#d6eaff;opacity:0.9">
    ملاحظات: تم استخدام مكتبة <strong>gspread</strong> للتعامل مع Google Sheets، و<strong>Streamlit</strong> لواجهة الويب.
    تأكد من إعداد بيانات الاعتماد في <code>st.secrets</code> (مفتاح خدمة Google Service Account أو GOOGLE_CREDENTIALS JSON).
    </div>
    """,
    unsafe_allow_html=True,
)






