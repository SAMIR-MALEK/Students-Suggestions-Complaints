st.markdown("""
<style>
/* الخط */
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Cairo', sans-serif;
}

/* خلفية الصفحة */
.stApp {
    background: linear-gradient(180deg, #031028 0%, #071a30 100%);
    color: #f5f8ff;
    min-height: 100vh;
    padding: 28px 36px;
}

/* حاوية المحتوى */
.container-wide {
    max-width: 1200px;
    margin: 0 auto;
}

/* بانر العنوان */
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
    color: #ffd966;
}
.top-banner .subtitle {
    font-size: 13px;
    color: #d6eaff;
    opacity: 0.95;
    margin-top: 4px;
}

/* البطاقة */
.card {
    background: #eef5fb;
    color: #071022;
    border-radius: 14px;
    padding: 22px;
    box-shadow: 0 12px 36px rgba(2,6,23,0.45);
    border: 1px solid rgba(7,16,37,0.06);
    margin-bottom: 24px;
}

/* عناوين البطاقة */
.card h2 {
    margin: 0 0 8px 0;
    color: #ffcc00;
    font-size: 20px;
}
.card p.lead {
    margin: 0 0 14px 0;
    color: #08304f;
    opacity: 0.95;
}

/* الحقول */
.card .stTextInput>div>div>input,
.card .stTextArea>div>div>textarea,
.card .stSelectbox>div>div>div[role="combobox"] {
    background: #ffffff !important;
    color: #071022 !important;
    border: 1px solid rgba(7,16,37,0.08) !important;
    border-radius: 10px !important;
    padding: 10px 12px !important;
}

/* الأزرار */
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

/* الأعمدة */
@media (min-width: 1000px) {
    .two-cols {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 16px;
    }
}
</style>
""", unsafe_allow_html=True)
