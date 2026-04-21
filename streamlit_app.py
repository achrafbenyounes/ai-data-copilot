# ═══════════════════════════════════════════════════════
# AI Data Copilot — by Achraf BEN YOUNES
# ═══════════════════════════════════════════════════════

import os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import streamlit as st
import pandas as pd
import fitz
from langdetect import detect

from core.ai.context_loader import extract_file_content
from core.ai.ai_brain_with_api import query_ai
from core.router.data_router import choose_engine
from core.ai.dataset_analyzer import analyze_csv
from core.ai.ai_transformer import generate_transformations
from core.ai.data_health_score import compute_health_score   # ← AJOUT

# ───────────────────────────────────────────────────────
st.set_page_config(
    page_title="AI Data Copilot",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ───────────────────────────────────────────────────────
# ACCENT THEMES
# ───────────────────────────────────────────────────────
THEMES = {
    "Ocean":   {"a": "#38bdf8", "b": "#818cf8", "glow": "rgba(56,189,248,0.18)",  "icon": "🌊"},
    "Violet":  {"a": "#a78bfa", "b": "#f472b6", "glow": "rgba(167,139,250,0.18)", "icon": "💜"},
    "Emerald": {"a": "#34d399", "b": "#38bdf8", "glow": "rgba(52,211,153,0.18)",  "icon": "🌿"},
    "Sunset":  {"a": "#fb923c", "b": "#f472b6", "glow": "rgba(251,146,60,0.18)",  "icon": "🌅"},
    "Rose":    {"a": "#f43f5e", "b": "#fb923c", "glow": "rgba(244,63,94,0.18)",   "icon": "🌸"},
}

# ───────────────────────────────────────────────────────
# BACKGROUND THEMES
# ───────────────────────────────────────────────────────
BG_THEMES = {
    "Void":  {"base": "#050810", "card": "rgba(10,14,23,0.85)",    "icon": "🌑", "border": "rgba(255,255,255,0.05)", "dark": True},
    "Slate": {"base": "#0a0f1a", "card": "rgba(15,20,35,0.9)",     "icon": "🪨", "border": "rgba(255,255,255,0.06)", "dark": True},
    "Pearl": {"base": "#f0f4f8", "card": "rgba(255,255,255,0.9)",  "icon": "🤍", "border": "rgba(0,0,0,0.07)",       "dark": False},
    "Ivory": {"base": "#faf8f4", "card": "rgba(255,255,255,0.92)", "icon": "🪷", "border": "rgba(0,0,0,0.06)",       "dark": False},
    "Sky":   {"base": "#e8f4ff", "card": "rgba(255,255,255,0.88)", "icon": "☁️", "border": "rgba(14,165,233,0.12)",  "dark": False},
}

# ───────────────────────────────────────────────────────
# TRANSLATIONS
# ───────────────────────────────────────────────────────
T = {
    "fr": {
        "tagline1":       "Votre copilote intelligent pour l'analyse et la transformation de données.",
        "tagline2":       "Chargez un fichier — obtenez une analyse complète et du code prêt à l'emploi.",
        "author":         "by Achraf BEN YOUNES",
        "upload_label":   "Déposez votre fichier ici",
        "upload_hint":    "CSV · TXT · PDF — max 200 MB",
        "file_detected":  "Type détecté",
        "prev_csv":       "Aperçu du dataset",
        "prev_txt":       "Aperçu du texte",
        "prev_pdf":       "Aperçu du PDF",
        "unsupported":    "Format non supporté. Utilisez CSV, TXT ou PDF.",
        "engine_label":   "Moteur actif",
        "analysis":       "Analyse",
        "rows":           "Lignes",
        "cols":           "Colonnes",
        "nulls":          "Valeurs manquantes",
        "full_report":    "Rapport complet",
        "transforms":     "Transformations suggérées",
        "tr_hint":        "Générées automatiquement à partir de l'analyse réelle de vos données.",
        "why":            "Pourquoi ?",
        "no_tr":          "Vos données sont propres — aucune transformation nécessaire !",
        "ask":            "Interrogez vos données",
        "ask_hint":       "Ex : Quelles colonnes ont le plus de valeurs manquantes ?",
        "answer":         "Réponse",
        "spinner":        "Analyse en cours…",
        "custom_title":   "Personnaliser",
        "theme_label":    "Thème de couleur",
        "bg_label":       "Couleur de fond",
        "dir":            "ltr",
        "powered":        "Propulsé par IA",
        "health_title":   "Data Health Score",
        "health_detail":  "Détail des pénalités",
        "health_perfect": "Aucune pénalité — données impeccables !",
    },
    "en": {
        "tagline1":       "Your intelligent copilot for data analysis and transformation.",
        "tagline2":       "Upload a file — get a full analysis and ready-to-use code instantly.",
        "author":         "by Achraf BEN YOUNES",
        "upload_label":   "Drop your file here",
        "upload_hint":    "CSV · TXT · PDF — max 200 MB",
        "file_detected":  "Detected type",
        "prev_csv":       "Dataset preview",
        "prev_txt":       "Text preview",
        "prev_pdf":       "PDF preview",
        "unsupported":    "Unsupported format. Use CSV, TXT or PDF.",
        "engine_label":   "Active engine",
        "analysis":       "Analysis",
        "rows":           "Rows",
        "cols":           "Columns",
        "nulls":          "Missing values",
        "full_report":    "Full report",
        "transforms":     "Suggested transformations",
        "tr_hint":        "Auto-generated from the actual analysis of your data.",
        "why":            "Why?",
        "no_tr":          "Your data is clean — no transformation needed!",
        "ask":            "Query your data",
        "ask_hint":       "e.g. Which columns have the most missing values?",
        "answer":         "Answer",
        "spinner":        "Analyzing…",
        "custom_title":   "Customize",
        "theme_label":    "Color theme",
        "bg_label":       "Background",
        "dir":            "ltr",
        "powered":        "AI-Powered",
        "health_title":   "Data Health Score",
        "health_detail":  "Penalty details",
        "health_perfect": "No penalties — data is spotless!",
    },
    "ar": {
        "tagline1":       "مساعدك الذكي لتحليل البيانات وتحويلها.",
        "tagline2":       "ارفع ملفًا واحصل على تحليل شامل وكود جاهز للاستخدام فورًا.",
        "author":         "من تطوير أشرف بن يونس",
        "upload_label":   "أسقط ملفك هنا",
        "upload_hint":    "CSV · TXT · PDF — الحد الأقصى 200 MB",
        "file_detected":  "النوع المكتشف",
        "prev_csv":       "معاينة البيانات",
        "prev_txt":       "معاينة النص",
        "prev_pdf":       "معاينة PDF",
        "unsupported":    "صيغة غير مدعومة. استخدم CSV أو TXT أو PDF.",
        "engine_label":   "المحرك النشط",
        "analysis":       "التحليل",
        "rows":           "الصفوف",
        "cols":           "الأعمدة",
        "nulls":          "القيم المفقودة",
        "full_report":    "التقرير الكامل",
        "transforms":     "التحويلات المقترحة",
        "tr_hint":        "تم إنشاؤها تلقائيًا من التحليل الفعلي لبياناتك.",
        "why":            "لماذا؟",
        "no_tr":          "بياناتك نظيفة — لا حاجة لأي تحويل!",
        "ask":            "استفسر عن بياناتك",
        "ask_hint":       "مثال: ما الأعمدة التي تحتوي على أكثر القيم المفقودة؟",
        "answer":         "الإجابة",
        "spinner":        "جارٍ التحليل…",
        "custom_title":   "تخصيص",
        "theme_label":    "نسق اللون",
        "bg_label":       "لون الخلفية",
        "dir":            "rtl",
        "powered":        "مدعوم بالذكاء الاصطناعي",
        "health_title":   "نقاط جودة البيانات",
        "health_detail":  "تفاصيل النقاط المخصومة",
        "health_perfect": "لا توجد خصومات — البيانات ممتازة!",
    },
}

# ───────────────────────────────────────────────────────
# SESSION DEFAULTS
# ───────────────────────────────────────────────────────
if "lang"  not in st.session_state: st.session_state.lang  = "fr"
if "theme" not in st.session_state: st.session_state.theme = "Ocean"
if "bg"    not in st.session_state: st.session_state.bg    = "Pearl"

lang  = st.session_state.lang
theme = st.session_state.theme
bg    = st.session_state.bg
t     = T[lang]
th    = THEMES[theme]
bgt   = BG_THEMES[bg]
is_rtl = (t["dir"] == "rtl")

A    = th["a"]
B    = th["b"]
GLW  = th["glow"]
BASE = bgt["base"]
CARD = bgt["card"]
BDR  = bgt["border"]
IS_DARK = bgt.get("dark", True)

# Text / muted colors adapt to light vs dark background
TXT_MAIN   = "#1e293b"   if not IS_DARK else "#cbd5e1"
TXT_MUTED  = "#64748b"   if not IS_DARK else "#64748b"
TXT_FAINT  = "#94a3b8"   if not IS_DARK else "#334155"
TXT_GHOST  = "#cbd5e1"   if not IS_DARK else "#1e293b"
HERO_GRAD  = f"linear-gradient(135deg, #0f172a 0%, #1e293b 20%, {A} 50%, {B} 80%, #0f172a 100%)" \
             if IS_DARK else \
             f"linear-gradient(135deg, #0f172a 0%, {A} 40%, {B} 80%, #1e293b 100%)"
NAV_BORDER = "rgba(255,255,255,0.04)" if IS_DARK else "rgba(0,0,0,0.06)"
SEC_GRAD   = f"linear-gradient(90deg, {A}33, transparent)" if IS_DARK else f"linear-gradient(90deg, {A}55, transparent)"
INPUT_BDR  = "rgba(255,255,255,0.07)" if IS_DARK else "rgba(0,0,0,0.1)"
INPUT_TXT  = "#e2e8f0" if IS_DARK else "#1e293b"
INPUT_PH   = "#1e2d3d" if IS_DARK else "#94a3b8"

# ───────────────────────────────────────────────────────
# CSS
# ───────────────────────────────────────────────────────
rtl_overrides = f"""
    .stApp, .main, .block-container,
    p, div, h1, h2, h3, span, label {{ direction: rtl !important; text-align: right !important; }}
    .stTextInput input {{ text-align: right !important; direction: rtl !important; }}
    .stFileUploader label, [data-testid="stFileUploaderDropzoneInstructions"] {{
        direction: rtl !important; text-align: right !important;
    }}
    .sec-row {{ flex-direction: row-reverse !important; }}
    .sec-row::after {{ display: none !important; }}
    .sec-row::before {{
        content: '' !important;
        flex: 1 !important;
        height: 1px !important;
        background: linear-gradient(270deg, rgba({A.replace('#','')},0.15), transparent) !important;
    }}
    .tc {{ border-left: none !important; border-right: 3px solid {A} !important; }}
    .tc:hover {{ border-right-color: {B} !important; transform: translateX(-4px) !important; }}
    .t-label {{ flex-direction: row-reverse !important; }}
    .t-label::before {{ display: none !important; }}
    .t-label::after {{ content: '‹'; color: {A}; font-size: 1.2rem; font-weight: 900; }}
    .hero-badge, .author-row {{ justify-content: flex-end !important; }}
    .mgrid {{ direction: rtl; }}
    .engine-badge {{ flex-direction: row-reverse; }}
    .nav-brand {{ flex-direction: row-reverse; }}
    .lang-switcher {{ flex-direction: row-reverse; }}
""" if is_rtl else ""

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;500;600;700;800&family=Outfit:wght@300;400;500;600&family=JetBrains+Mono:wght@400;500&display=swap');

/* ═══ RESET ════════════════════════════════════════════════ */
*, *::before, *::after {{ box-sizing: border-box; }}

html, body, [class*="css"] {{
    font-family: 'Outfit', sans-serif !important;
    color: {TXT_MAIN};
}}

/* Hide ALL Streamlit chrome decorations */
#MainMenu, header, footer,
[data-testid="stToolbar"],
[data-testid="stDecoration"],
[data-testid="stStatusWidget"],
[data-testid="stDeployButton"],
.stDeployButton,
button[kind="header"],
[data-testid="manage-app-button"] {{
    display: none !important;
    visibility: hidden !important;
    height: 0 !important;
    overflow: hidden !important;
}}

/* ═══ APP BACKGROUND ═══════════════════════════════════════ */
.stApp {{
    background: {BASE} !important;
    background-image:
        radial-gradient(ellipse 1000px 700px at -10% -15%, {GLW} 0%, transparent 65%),
        radial-gradient(ellipse  800px 600px at 110%  95%, {th["glow"].replace("0.18","0.12")} 0%, transparent 65%),
        radial-gradient(ellipse  600px 400px at  55%  45%, rgba(15,23,42,0.5) 0%, transparent 70%)
        !important;
}}

/* ═══ LAYOUT ════════════════════════════════════════════════ */
.main .block-container {{
    padding: 0 3.5rem 7rem 3.5rem !important;
    max-width: 1200px !important;
}}

/* ═══ NAVBAR ════════════════════════════════════════════════ */
.topbar {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 1.8rem 0 1.5rem 0;
    border-bottom: 1px solid {NAV_BORDER};
    margin-bottom: 0;
}}
.nav-brand {{
    display: flex;
    align-items: center;
    gap: 0.65rem;
    font-family: 'Syne', sans-serif;
    font-size: 1rem;
    font-weight: 700;
    color: {TXT_MAIN};
    letter-spacing: -0.2px;
}}
.nav-dot {{
    width: 9px; height: 9px;
    background: {A};
    border-radius: 50%;
    box-shadow: 0 0 8px {A}, 0 0 20px {GLW};
    animation: breathe 3s ease-in-out infinite;
    flex-shrink: 0;
}}
@keyframes breathe {{
    0%,100% {{ box-shadow: 0 0 6px {A}; transform: scale(1); }}
    50%      {{ box-shadow: 0 0 20px {A}, 0 0 40px {GLW}; transform: scale(1.15); }}
}}
.lang-switcher {{
    display: flex;
    align-items: center;
    gap: 0.25rem;
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 50px;
    padding: 0.2rem;
}}

/* ═══ STREAMLIT BUTTON OVERRIDES ════════════════════════════ */
.stButton > button {{
    font-family: 'Outfit', sans-serif !important;
    font-size: 0.78rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.3px !important;
    padding: 0.3rem 0.9rem !important;
    border-radius: 50px !important;
    border: none !important;
    background: transparent !important;
    color: #475569 !important;
    cursor: pointer !important;
    transition: all 0.18s ease !important;
    box-shadow: none !important;
    min-height: unset !important;
    height: auto !important;
    line-height: 1.5 !important;
    width: auto !important;
}}
.stButton > button:hover {{
    background: rgba(255,255,255,0.06) !important;
    color: #94a3b8 !important;
    box-shadow: none !important;
    border: none !important;
}}
.stButton > button:focus {{
    box-shadow: none !important;
    outline: none !important;
    border: none !important;
}}
.stButton > button:active {{
    transform: scale(0.97) !important;
    box-shadow: none !important;
}}
.btn-active > button {{
    background: linear-gradient(135deg, {A}, {B}) !important;
    color: #fff !important;
    box-shadow: 0 2px 14px {GLW} !important;
}}
.btn-active > button:hover {{
    background: linear-gradient(135deg, {B}, {A}) !important;
    color: #fff !important;
    box-shadow: 0 4px 20px {GLW} !important;
}}
.btn-theme > button {{
    padding: 0.4rem 0.75rem !important;
    border-radius: 10px !important;
    font-size: 0.8rem !important;
}}
.btn-theme-active > button {{
    background: linear-gradient(135deg, {A}22, {B}22) !important;
    border: 1px solid {A}55 !important;
    color: {A} !important;
    box-shadow: 0 0 12px {GLW} !important;
}}
.btn-bg > button {{
    padding: 0.4rem 0.75rem !important;
    border-radius: 10px !important;
    font-size: 0.8rem !important;
}}
.btn-bg-active > button {{
    background: linear-gradient(135deg, {A}22, {B}22) !important;
    border: 1px solid {A}55 !important;
    color: {A} !important;
    box-shadow: 0 0 12px {GLW} !important;
}}

/* ═══ HERO ══════════════════════════════════════════════════ */
.hero-wrap {{
    padding: 3rem 0 1.8rem 0;
    position: relative;
}}
.hero-badge {{
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    font-size: 0.67rem;
    font-weight: 700;
    letter-spacing: 2.5px;
    text-transform: uppercase;
    color: {A};
    background: {GLW};
    border: 1px solid {A}44;
    border-radius: 50px;
    padding: 0.3rem 1.1rem;
    margin-bottom: 1.4rem;
}}
.badge-dot {{
    width: 5px; height: 5px;
    background: {A};
    border-radius: 50%;
    animation: breathe 2s infinite;
    flex-shrink: 0;
}}
.hero-title {{
    font-family: 'Syne', sans-serif !important;
    font-size: clamp(3rem, 5.5vw, 4.8rem) !important;
    font-weight: 800 !important;
    line-height: 1.06 !important;
    letter-spacing: -3px !important;
    margin-bottom: 1rem !important;
    background: {HERO_GRAD} !important;
    background-size: 300% 300% !important;
    -webkit-background-clip: text !important;
    -webkit-text-fill-color: transparent !important;
    background-clip: text !important;
    animation: shimmer 7s ease infinite !important;
}}
@keyframes shimmer {{
    0%   {{ background-position: 0%   50%; }}
    50%  {{ background-position: 100% 50%; }}
    100% {{ background-position: 0%   50%; }}
}}
.hero-sub {{
    max-width: 560px;
    margin-bottom: 0.5rem;
}}
.hero-sub p {{
    color: {TXT_MUTED};
    font-size: 1.05rem;
    font-weight: 300;
    line-height: 1.7;
    margin-bottom: 0.15rem;
}}
.author-row {{
    display: flex;
    align-items: center;
    gap: 0.6rem;
    font-size: 0.74rem;
    color: {TXT_GHOST};
    font-weight: 500;
    margin-top: 1.2rem;
    padding-top: 1rem;
    border-top: 1px solid {BDR};
}}
.author-star {{ color: {A}; }}
.author-name {{
    background: linear-gradient(90deg, {A}, {B});
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    font-weight: 700;
    font-size: 0.82rem;
    font-family: 'Syne', sans-serif;
}}
.contact-row {{
    display: flex;
    align-items: center;
    flex-wrap: wrap;
    gap: 0.55rem;
    margin-top: 0.9rem;
    padding-top: 0.9rem;
    border-top: 1px solid {BDR};
}}
.contact-chip {{
    display: inline-flex;
    align-items: center;
    gap: 0.45rem;
    font-size: 0.75rem;
    font-weight: 500;
    color: {TXT_MUTED};
    background: {CARD};
    border: 1px solid {BDR};
    border-radius: 50px;
    padding: 0.3rem 0.9rem;
    text-decoration: none;
    font-family: 'Outfit', sans-serif;
    white-space: nowrap;
    transition: all 0.2s cubic-bezier(.4,0,.2,1);
}}
.contact-chip:hover {{
    border-color: {A}77;
    color: {A};
    box-shadow: 0 0 0 3px {GLW};
    text-decoration: none;
    transform: translateY(-1px);
}}
.ci-svg {{
    width: 13px; height: 13px;
    flex-shrink: 0;
    opacity: 0.75;
}}
.linkedin-btn {{
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    font-size: 0.78rem;
    font-weight: 700;
    letter-spacing: 0.5px;
    color: #fff;
    background: linear-gradient(135deg, #0077b5 0%, #00a0dc 100%);
    border: none;
    border-radius: 50px;
    padding: 0.42rem 1.1rem 0.42rem 0.75rem;
    text-decoration: none;
    font-family: 'Outfit', sans-serif;
    position: relative;
    overflow: hidden;
    transition: all 0.22s cubic-bezier(.4,0,.2,1);
    box-shadow: 0 2px 12px rgba(0,119,181,0.35), 0 0 0 0 rgba(0,119,181,0);
}}
.linkedin-btn::before {{
    content: '';
    position: absolute;
    inset: 0;
    background: linear-gradient(135deg, rgba(255,255,255,0.18) 0%, transparent 60%);
    border-radius: 50px;
    pointer-events: none;
}}
.linkedin-btn:hover {{
    transform: translateY(-2px) scale(1.04);
    box-shadow: 0 6px 24px rgba(0,119,181,0.55), 0 0 0 4px rgba(0,119,181,0.12);
    text-decoration: none;
    color: #fff;
}}
.linkedin-btn:active {{
    transform: scale(0.97);
}}
.li-icon {{
    width: 15px; height: 15px;
    flex-shrink: 0;
    filter: drop-shadow(0 1px 2px rgba(0,0,0,0.2));
}}
.li-arrow {{
    font-size: 0.7rem;
    opacity: 0.8;
    margin-left: 0.1rem;
    transition: transform 0.18s ease;
}}
.linkedin-btn:hover .li-arrow {{
    transform: translate(2px, -2px);
}}

/* ═══ CUSTOMIZER PANEL ══════════════════════════════════════ */
.custom-panel {{
    background: {CARD};
    border: 1px solid {BDR};
    border-radius: 18px;
    padding: 1.4rem 1.8rem;
    margin-bottom: 2.5rem;
    backdrop-filter: blur(12px);
}}
.custom-title {{
    font-size: 0.66rem;
    font-weight: 700;
    letter-spacing: 2.5px;
    text-transform: uppercase;
    color: {TXT_MUTED};
    margin-bottom: 0.9rem;
}}

/* ═══ FILE UPLOADER ═════════════════════════════════════════ */
[data-testid="stFileUploader"] {{
    background: {CARD} !important;
    border: 1px dashed {A}55 !important;
    border-radius: 18px !important;
    transition: border-color 0.25s, background 0.25s !important;
    padding: 0.5rem !important;
}}
[data-testid="stFileUploader"]:hover {{
    border-color: {A}99 !important;
    background: {CARD} !important;
    box-shadow: 0 0 0 4px {GLW} !important;
}}
[data-testid="stFileUploaderDropzone"] {{
    background: transparent !important;
    border: none !important;
}}
[data-testid="stFileUploaderDropzoneInstructions"] {{
    color: {TXT_MUTED} !important;
}}
[data-testid="stFileUploaderDropzoneInstructions"] span,
[data-testid="stFileUploaderDropzoneInstructions"] small,
[data-testid="stFileUploader"] label,
[data-testid="stFileUploader"] span,
[data-testid="stFileUploader"] p {{
    color: {TXT_MUTED} !important;
}}
[data-testid="stFileUploader"] svg {{
    fill: {A} !important;
    color: {A} !important;
}}
[data-testid="stFileUploader"] button {{
    background: {CARD} !important;
    color: {TXT_MAIN} !important;
    border: 1px solid {BDR} !important;
    border-radius: 10px !important;
    font-family: 'Outfit', sans-serif !important;
    font-weight: 600 !important;
    transition: all 0.2s ease !important;
}}
[data-testid="stFileUploader"] button:hover {{
    border-color: {A}88 !important;
    color: {A} !important;
    box-shadow: 0 0 0 3px {GLW} !important;
}}
[data-testid="stFileUploader"] > div > div:first-child {{
    display: none !important;
}}

/* ═══ SEC LABEL ═════════════════════════════════════════════ */
.sec-row {{
    display: flex;
    align-items: center;
    gap: 0.7rem;
    font-size: 0.64rem;
    font-weight: 700;
    letter-spacing: 3px;
    text-transform: uppercase;
    color: {TXT_MUTED};
    margin: 1.8rem 0 0.9rem 0;
}}
.sec-row::after {{
    content: '';
    flex: 1;
    height: 1px;
    background: {SEC_GRAD};
}}
.sec-icon {{
    width: 30px; height: 30px;
    background: linear-gradient(135deg, {A}18, {B}18);
    border: 1px solid {A}22;
    border-radius: 9px;
    display: flex; align-items: center; justify-content: center;
    font-size: 0.9rem;
    flex-shrink: 0;
}}

/* ═══ ENGINE BADGE ══════════════════════════════════════════ */
.engine-badge {{
    display: inline-flex;
    align-items: center;
    gap: 0.55rem;
    background: rgba(16,185,129,0.07);
    border: 1px solid rgba(16,185,129,0.18);
    border-radius: 50px;
    padding: 0.4rem 1.1rem;
    font-size: 0.78rem;
    color: #34d399;
    font-family: 'JetBrains Mono', monospace;
    margin: 0.5rem 0 1.8rem 0;
}}
.e-pulse {{
    width: 7px; height: 7px;
    background: #34d399;
    border-radius: 50%;
    box-shadow: 0 0 8px rgba(52,211,153,0.6);
    animation: breathe 2s infinite;
    flex-shrink: 0;
}}

/* ═══ METRIC GRID ════════════════════════════════════════════ */
.mgrid {{
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 1.2rem;
    margin: 0.6rem 0 1.4rem 0;
}}
.mtile {{
    background: {CARD};
    border: 1px solid {BDR};
    border-radius: 20px;
    padding: 1.8rem 2rem;
    position: relative;
    overflow: hidden;
    backdrop-filter: blur(10px);
    transition: transform 0.22s ease, border-color 0.22s ease;
}}
.mtile::before {{
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 1px;
    background: linear-gradient(90deg, transparent, {A}66, {B}44, transparent);
}}
.mtile:hover {{
    transform: translateY(-3px);
    border-color: {A}22;
}}
.mtile .mv {{
    display: block;
    font-size: 3rem;
    font-weight: 800;
    font-family: 'Syne', sans-serif;
    line-height: 1;
    margin-bottom: 0.55rem;
    background: linear-gradient(135deg, #f1f5f9, {A});
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}}
.mtile .ml {{
    font-size: 0.67rem;
    font-weight: 700;
    letter-spacing: 2.5px;
    text-transform: uppercase;
    color: {TXT_MUTED};
}}
.mtile .mbg {{
    position: absolute;
    bottom: -12px; right: 10px;
    font-size: 4.5rem;
    opacity: 0.035;
    pointer-events: none;
    line-height: 1;
}}

/* ═══ HEALTH SCORE CARD ══════════════════════════════════════ */
.health-card {{
    background: {CARD};
    border: 1px solid {BDR};
    border-radius: 20px;
    padding: 1.6rem 2rem;
    margin: 0 0 1.4rem 0;
    backdrop-filter: blur(10px);
    position: relative;
    overflow: hidden;
}}
.health-card::before {{
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 1px;
    background: linear-gradient(90deg, transparent, {A}66, {B}44, transparent);
}}
.health-header {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 1rem;
}}
.health-label {{
    font-size: 0.67rem;
    font-weight: 700;
    letter-spacing: 2.5px;
    text-transform: uppercase;
    color: {TXT_MUTED};
}}
.health-score-value {{
    font-family: 'Syne', sans-serif;
    font-size: 1.6rem;
    font-weight: 800;
    line-height: 1;
}}
.health-bar-track {{
    background: rgba(255,255,255,0.06);
    border-radius: 999px;
    height: 10px;
    overflow: hidden;
}}
.health-bar-fill {{
    height: 100%;
    border-radius: 999px;
    transition: width 0.8s cubic-bezier(.4,0,.2,1);
}}
.health-penalty-item {{
    display: flex;
    align-items: flex-start;
    gap: 0.75rem;
    padding: 0.7rem 0;
    border-top: 1px solid {BDR};
}}
.health-penalty-badge {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.72rem;
    font-weight: 700;
    padding: 0.2rem 0.6rem;
    border-radius: 6px;
    white-space: nowrap;
    flex-shrink: 0;
}}
.health-penalty-text {{
    font-size: 0.82rem;
    color: {TXT_MUTED};
    line-height: 1.5;
}}

/* ═══ TRANSFORM CARDS ════════════════════════════════════════ */
.tc {{
    background: {CARD};
    border: 1px solid {BDR};
    border-left: 2px solid {A};
    border-radius: 16px;
    padding: 1.3rem 1.8rem 1rem 1.8rem;
    margin-bottom: 0.85rem;
    transition: all 0.22s cubic-bezier(.4,0,.2,1);
    backdrop-filter: blur(8px);
    position: relative;
    overflow: hidden;
}}
.tc::after {{
    content: '';
    position: absolute;
    inset: 0;
    background: linear-gradient(135deg, {A}05 0%, transparent 50%);
    opacity: 0;
    transition: opacity 0.22s;
    pointer-events: none;
    border-radius: 16px;
}}
.tc:hover {{
    border-color: rgba(255,255,255,0.09);
    border-left-color: {B};
    transform: translateX(5px);
    box-shadow: 0 4px 24px rgba(0,0,0,0.25);
}}
.tc:hover::after {{ opacity: 1; }}
.t-label {{
    font-size: 0.89rem;
    font-weight: 700;
    color: {TXT_MAIN};
    margin-bottom: 0.4rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
    font-family: 'Syne', sans-serif;
}}
.t-label::before {{
    content: '›';
    color: {A};
    font-size: 1.3rem;
    font-weight: 900;
    line-height: 1;
    flex-shrink: 0;
}}
.t-why {{
    font-size: 0.79rem;
    color: {TXT_MUTED};
    line-height: 1.65;
    margin-bottom: 0.9rem;
}}

/* ═══ INPUT ══════════════════════════════════════════════════ */
.stTextInput > div > div > input {{
    background: {CARD} !important;
    border: 1px solid {INPUT_BDR} !important;
    border-radius: 14px !important;
    color: {INPUT_TXT} !important;
    font-family: 'Outfit', sans-serif !important;
    font-size: 0.97rem !important;
    padding: 0.9rem 1.3rem !important;
    transition: all 0.2s ease !important;
    caret-color: {A} !important;
}}
.stTextInput > div > div > input:focus {{
    border-color: {A}55 !important;
    box-shadow: 0 0 0 4px {GLW} !important;
    outline: none !important;
}}
.stTextInput > div > div > input::placeholder {{ color: {INPUT_PH} !important; }}

/* ═══ AI BUBBLE ══════════════════════════════════════════════ */
.ai-bubble {{
    background: {CARD};
    border: 1px solid {A}22;
    border-radius: 20px;
    padding: 2.2rem 2.6rem;
    margin-top: 1rem;
    line-height: 1.85;
    color: {TXT_MUTED};
    font-size: 0.96rem;
    position: relative;
}}
.ai-bubble::before {{
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 1px;
    background: linear-gradient(90deg, transparent, {A}66, {B}44, transparent);
    border-radius: 20px 20px 0 0;
}}

/* ═══ EXPANDER ════════════════════════════════════════════════ */
.stExpander {{
    background: {CARD} !important;
    border: 1px solid {BDR} !important;
    border-radius: 14px !important;
    backdrop-filter: blur(8px) !important;
}}
details > summary {{
    font-size: 0.82rem !important;
    color: {TXT_MUTED} !important;
    font-family: 'Outfit', sans-serif !important;
    padding: 0.7rem 0.5rem !important;
}}

/* ═══ CODE ═══════════════════════════════════════════════════ */
.stCodeBlock {{ border-radius: 12px !important; }}
code, pre {{ font-family: 'JetBrains Mono', monospace !important; font-size: 0.8rem !important; }}

/* ═══ DATAFRAME ══════════════════════════════════════════════ */
.stDataFrame {{ border-radius: 14px !important; overflow: hidden !important; }}

/* ═══ ALERT ══════════════════════════════════════════════════ */
.stAlert {{ border-radius: 12px !important; }}

/* ═══ SCROLLBAR ══════════════════════════════════════════════ */
::-webkit-scrollbar {{ width: 4px; height: 4px; }}
::-webkit-scrollbar-track {{ background: transparent; }}
::-webkit-scrollbar-thumb {{ background: #1e293b; border-radius: 4px; }}
::-webkit-scrollbar-thumb:hover {{ background: #334155; }}

/* ═══ RESPONSIVE ═════════════════════════════════════════════ */
@media (max-width: 900px) {{
    .main .block-container {{ padding: 0 1.5rem 5rem 1.5rem !important; }}
    .hero-wrap {{ padding: 3rem 0 2rem 0; }}
    .hero-title {{ font-size: 2.6rem !important; letter-spacing: -2px !important; }}
    .mgrid {{ grid-template-columns: 1fr 1fr !important; }}
    .mgrid .mtile:last-child {{ grid-column: span 2 !important; }}
}}

/* ═══ RTL OVERRIDES ══════════════════════════════════════════ */
{rtl_overrides}
</style>
""", unsafe_allow_html=True)

# ───────────────────────────────────────────────────────
# HELPERS
# ───────────────────────────────────────────────────────
def read_csv(f):
    encodings = ["utf-8-sig", "utf-8", "latin-1", "cp1252"]
    separators = [";", ",", "\t", "|"]
    best = None
    for enc in encodings:
        for sep in separators:
            try:
                f.seek(0)
                df = pd.read_csv(f, encoding=enc, sep=sep, engine="python", on_bad_lines="skip")
                if df.shape[1] > 1:
                    if best is None or df.shape[1] > best.shape[1]:
                        best = df
            except Exception:
                pass
    if best is not None:
        return best
    # last resort: comma with utf-8-sig, keep whatever we get
    try:
        f.seek(0)
        return pd.read_csv(f, encoding="utf-8-sig", on_bad_lines="skip")
    except Exception as e:
        raise ValueError(f"Could not parse CSV file: {e}")

def read_txt(f):
    f.seek(0); return f.read().decode("utf-8")

def read_pdf(f):
    f.seek(0)
    doc = fitz.open(stream=f.read(), filetype="pdf")
    return "".join(p.get_text() for p in doc)

def sec(icon: str, label: str):
    st.markdown(
        f'<div class="sec-row">'
        f'<div class="sec-icon">{icon}</div>'
        f'<span>{label}</span>'
        f'</div>',
        unsafe_allow_html=True,
    )

def file_tag(ext: str, label: str):
    st.markdown(
        f'<p style="font-size:.72rem;color:#1e293b;margin:.4rem 0 .7rem 0;">'
        f'<code style="color:{A};background:{GLW};padding:2px 10px;border-radius:6px;'
        f'font-family:JetBrains Mono,monospace;font-size:.72rem;">.{ext}</code>'
        f'&ensp;{label}</p>',
        unsafe_allow_html=True,
    )

def process_file(f):
    ft = f.name.split(".")[-1].lower()
    file_tag(ft, t["file_detected"])
    if ft == "csv":
        try:
            df = read_csv(f)
        except ValueError as e:
            st.error(str(e))
            return None

        # ── Aperçu collapsible ─────────────────────────────────────
        with st.expander(f"📋 {t['prev_csv']}", expanded=True):
            st.dataframe(df, use_container_width=True, height=240)

        # ── Q&A — juste sous l'aperçu ─────────────────────────────
        sec("💬", t["ask"])
        user_q = st.text_input(
            label="q",
            placeholder=t["ask_hint"],
            label_visibility="collapsed",
            key="csv_user_q",
        )
        if user_q and user_q.strip():
            f.seek(0)
            ctx = extract_file_content(f)
            prompt = (
                f"You are an AI data assistant.\n"
                f"File content:\n{ctx}\n\n"
                f"IMPORTANT: Answer ONLY in {detect_lang_of_text(user_q)} language.\n"
                f"Question: {user_q}"
            )
            with st.spinner(t["spinner"]):
                answer = query_ai(prompt)
            with st.expander(f"🧠 {t['answer']}", expanded=True):
                st.markdown(f'<div class="ai-bubble">{answer}</div>', unsafe_allow_html=True)

        return df
    elif ft == "txt":
        text = read_txt(f)
        sec("📄", t["prev_txt"])
        st.text(text[:1000])
        return text
    elif ft == "pdf":
        text = read_pdf(f)
        sec("📑", t["prev_pdf"])
        st.text(text[:1000])
        return text
    else:
        st.error(t["unsupported"]); return None

def detect_lang_of_text(text):
    try:
        return {"fr":"French","en":"English","ar":"Arabic"}.get(detect(text),"English")
    except:
        return "English"

# ───────────────────────────────────────────────────────
# HELPER : rendu du Data Health Score
# ───────────────────────────────────────────────────────
def render_health_score(df: pd.DataFrame):
    """Calcule et affiche la carte Data Health Score."""
    health  = compute_health_score(df, lang=lang)
    score   = health["score"]
    niveau  = health["niveau"]
    emoji   = health["emoji"]
    details = health["details"]

    # Couleur de la barre selon le score
    if score >= 90:
        bar_color  = "#22c55e"
        text_color = "#22c55e"
        badge_bg   = "rgba(34,197,94,0.12)"
        badge_border = "rgba(34,197,94,0.25)"
    elif score >= 71:
        bar_color  = "#f59e0b"
        text_color = "#f59e0b"
        badge_bg   = "rgba(245,158,11,0.12)"
        badge_border = "rgba(245,158,11,0.25)"
    elif score >= 41:
        bar_color  = "#f97316"
        text_color = "#f97316"
        badge_bg   = "rgba(249,115,22,0.12)"
        badge_border = "rgba(249,115,22,0.25)"
    else:
        bar_color  = "#ef4444"
        text_color = "#ef4444"
        badge_bg   = "rgba(239,68,68,0.12)"
        badge_border = "rgba(239,68,68,0.25)"

    # ── Carte principale ──────────────────────────────────────
    st.markdown(f"""
    <div class="health-card">
        <div class="health-header">
            <span class="health-label">{t['health_title']}</span>
            <span class="health-score-value" style="color:{text_color};">
                {emoji}&nbsp;{score}&nbsp;<span style="font-size:0.9rem;opacity:0.5;">/ 100</span>
                &nbsp;—&nbsp;
                <span style="font-size:1rem;">{niveau}</span>
            </span>
        </div>
        <div class="health-bar-track">
            <div class="health-bar-fill" style="width:{score}%; background:{bar_color};"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Détail des pénalités ──────────────────────────────────
    if details:
        with st.expander(f"🔍 {t['health_detail']}"):
            for idx, d in enumerate(details):
                # Build the optional per-column breakdown table
                extra_html = ""
                if d.get("extra_rows"):
                    rows_html = ""
                    for row in d["extra_rows"]:
                        bar_pct = min(row["pct"], 100)
                        rows_html += f"""
                        <tr>
                            <td style="padding:5px 8px;font-size:0.78rem;color:{TXT_MAIN};
                                       border-bottom:1px solid rgba(128,128,128,0.1);
                                       max-width:160px;word-break:break-word;">
                                {row['col']}
                            </td>
                            <td style="padding:5px 8px;font-size:0.78rem;color:{TXT_MUTED};
                                       text-align:right;white-space:nowrap;
                                       border-bottom:1px solid rgba(128,128,128,0.1);">
                                {row['vides']:,}&nbsp;<span style="opacity:0.6;font-size:0.72rem;">{d['extra_of_rows']}</span>
                            </td>
                            <td style="padding:5px 8px;border-bottom:1px solid rgba(128,128,128,0.1);
                                       min-width:110px;">
                                <div style="display:flex;align-items:center;gap:6px;">
                                    <div style="flex:1;background:rgba(128,128,128,0.15);
                                                border-radius:3px;height:6px;overflow:hidden;">
                                        <div style="width:{bar_pct}%;background:{text_color};
                                                    border-radius:3px;height:6px;"></div>
                                    </div>
                                    <span style="font-size:0.75rem;color:{text_color};
                                                 min-width:40px;text-align:right;font-weight:600;">
                                        {row['pct']} %
                                    </span>
                                </div>
                            </td>
                        </tr>"""
                    ch = d["extra_col_headers"]
                    extra_html = f"""
                    <div style="margin-top:0.9rem;padding:0.65rem 0.75rem;
                                background:rgba(128,128,128,0.05);border-radius:8px;
                                border:1px solid rgba(128,128,128,0.12);">
                        <div style="font-size:0.72rem;font-weight:700;color:{TXT_MUTED};
                                    text-transform:uppercase;letter-spacing:0.06em;
                                    margin-bottom:0.5rem;">
                            📊&nbsp;{d['extra_header']}
                        </div>
                        <table style="width:100%;border-collapse:collapse;">
                            <thead>
                                <tr>
                                    <th style="padding:4px 8px;font-size:0.7rem;font-weight:600;
                                               color:{TXT_MUTED};text-align:left;
                                               border-bottom:1px solid rgba(128,128,128,0.18);">
                                        {ch[0]}
                                    </th>
                                    <th style="padding:4px 8px;font-size:0.7rem;font-weight:600;
                                               color:{TXT_MUTED};text-align:right;
                                               border-bottom:1px solid rgba(128,128,128,0.18);">
                                        {ch[1]}
                                    </th>
                                    <th style="padding:4px 8px;font-size:0.7rem;font-weight:600;
                                               color:{TXT_MUTED};
                                               border-bottom:1px solid rgba(128,128,128,0.18);">
                                        {ch[2]}
                                    </th>
                                </tr>
                            </thead>
                            <tbody>{rows_html}</tbody>
                        </table>
                    </div>"""

                divider = "" if idx == 0 else f'<div style="border-top:1px solid rgba(128,128,128,0.12);margin:0.75rem 0;"></div>'
                st.markdown(f"""
                {divider}
                <div class="health-penalty-item">
                    <span class="health-penalty-badge"
                          style="background:{badge_bg}; border:1px solid {badge_border}; color:{text_color};">
                        −{d['penalite']} pts
                    </span>
                    <div style="flex:1;">
                        <div style="font-size:0.85rem;font-weight:600;color:{TXT_MAIN};margin-bottom:0.55rem;">
                            {d['critere']}
                        </div>
                        <div class="health-penalty-text" style="margin-bottom:0.4rem;">
                            📋&nbsp;{d['explication']}
                        </div>
                        <div class="health-penalty-text" style="margin-bottom:0.4rem;">
                            ⚠️&nbsp;{d['impact']}
                        </div>
                        <div class="health-penalty-text">
                            ✅&nbsp;{d['conseil']}
                        </div>
                        {extra_html}
                    </div>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.success(f"✅ {t['health_perfect']}")


# ───────────────────────────────────────────────────────
# NAVBAR
# ───────────────────────────────────────────────────────
n1, n2 = st.columns([5, 3])

with n1:
    st.markdown(
        '<div class="topbar">'
        '<div class="nav-brand">'
        '<div class="nav-dot"></div>'
        'AI Data Copilot'
        '</div>'
        '</div>',
        unsafe_allow_html=True,
    )

with n2:
    st.markdown('<div style="height:1.4rem"></div>', unsafe_allow_html=True)
    lc1, lc2, lc3 = st.columns(3)
    for col, (lcode, flag) in zip([lc1,lc2,lc3],[("fr","🇫🇷 FR"),("en","🇬🇧 EN"),("ar","🇸🇦 AR")]):
        with col:
            active = "btn-active" if lang == lcode else ""
            st.markdown(f'<div class="stButton {active}">', unsafe_allow_html=True)
            if st.button(flag, key=f"l_{lcode}", use_container_width=True):
                st.session_state.lang = lcode
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

# Rebind
lang  = st.session_state.lang
theme = st.session_state.theme
t     = T[lang]
th    = THEMES[theme]

# ───────────────────────────────────────────────────────
# HERO
# ───────────────────────────────────────────────────────
st.markdown(f"""
<div class="hero-wrap">
    <div class="hero-badge">
        <div class="badge-dot"></div>
        {t['powered']}
    </div>
    <h1 class="hero-title">AI Data Copilot</h1>
    <div class="hero-sub">
        <p>{t['tagline1']}</p>
        <p>{t['tagline2']}</p>
    </div>
    <div class="author-row">
        <span class="author-star">✦</span>
        <span style="color:#1e293b;font-size:.74rem;">{t['author'].replace('Achraf BEN YOUNES','').replace('أشرف بن يونس','').strip()}</span>
        <span class="author-name">Achraf BEN YOUNES</span>
    </div>
    <div class="contact-row">
        <span class="contact-chip">
            <svg class="ci-svg" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect width="20" height="16" x="2" y="4" rx="2"/><path d="m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7"/></svg>
            <span>achrafbenyounes2012@gmail.com</span>
        </span>
        <span class="contact-chip">
            <svg class="ci-svg" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07A19.5 19.5 0 0 1 4.69 13a19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 3.6 2.18h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"/></svg>
            <span>07.60.93.53.71</span>
        </span>
        <a class="linkedin-btn" href="https://www.linkedin.com/in/achraf-b-601b7012/" target="_blank" rel="noopener noreferrer">
            <svg class="li-icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor"><path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433a2.062 2.062 0 0 1-2.063-2.065 2.064 2.064 0 1 1 2.063 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/></svg>
            <span>LinkedIn</span>
            <span class="li-arrow">↗</span>
        </a>
    </div>
</div>
""", unsafe_allow_html=True)

# ───────────────────────────────────────────────────────
# CUSTOMIZER
# ───────────────────────────────────────────────────────
with st.expander(f"🎨 {t['custom_title']}", expanded=False):
    st.markdown(f'<div class="custom-title">{t["theme_label"]}</div>', unsafe_allow_html=True)
    tc = st.columns(len(THEMES))
    for col, (tname, tdata) in zip(tc, THEMES.items()):
        with col:
            active_cls = "btn-theme btn-theme-active" if theme == tname else "btn-theme"
            st.markdown(f'<div class="{active_cls}">', unsafe_allow_html=True)
            if st.button(f"{tdata['icon']} {tname}", key=f"th_{tname}", use_container_width=True):
                st.session_state.theme = tname
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div style="height:.6rem"></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="custom-title">{t["bg_label"]}</div>', unsafe_allow_html=True)
    bc = st.columns(len(BG_THEMES))
    for col, (bname, bdata) in zip(bc, BG_THEMES.items()):
        with col:
            active_cls = "btn-bg btn-bg-active" if bg == bname else "btn-bg"
            st.markdown(f'<div class="{active_cls}">', unsafe_allow_html=True)
            if st.button(f"{bdata['icon']} {bname}", key=f"bg_{bname}", use_container_width=True):
                st.session_state.bg = bname
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

# ───────────────────────────────────────────────────────
# UPLOAD
# ───────────────────────────────────────────────────────
uploaded_file = st.file_uploader(
    f"📂 {t['upload_label']}",
    type=["csv", "txt", "pdf"],
    help=t["upload_hint"],
    label_visibility="visible",
)

# ───────────────────────────────────────────────────────
# MAIN FLOW
# ───────────────────────────────────────────────────────
if uploaded_file:
    mb       = uploaded_file.size / (1024 * 1024)
    content  = process_file(uploaded_file)

    engine, transformed = choose_engine(
        source_type="file",
        file_size_mb=mb,
        df=content if isinstance(content, pd.DataFrame) else None,
    )

    if isinstance(transformed, pd.DataFrame):

        # ── Metrics ───────────────────────────────────────────────
        sec("📊", t["analysis"])
        analysis    = analyze_csv(transformed)
        total_nulls = sum(int(v) for v in analysis.get("missing", {}).values())

        rows_v = analysis.get("num_rows", "—")
        cols_v = analysis.get("num_columns", "—")
        tiles  = [
            (rows_v,     t["rows"],  "▦"),
            (cols_v,     t["cols"],  "▤"),
            (total_nulls,t["nulls"], "◌"),
        ]
        html = "".join(
            f'<div class="mtile"><span class="mv">{v}</span>'
            f'<span class="ml">{l}</span>'
            f'<span class="mbg">{ic}</span></div>'
            for v, l, ic in tiles
        )
        st.markdown(f'<div class="mgrid">{html}</div>', unsafe_allow_html=True)

        # ── Data Health Score ──────────────────────────────────────
        sec("🏥", t["health_title"])
        render_health_score(transformed)                          # ← AJOUT

        with st.expander(f"🔍 {t['full_report']}"):
            st.json(analysis)

        # ── Transformations (collapsible) ─────────────────────────
        with st.expander(f"🔧 {t['transforms']}", expanded=False):
            st.markdown(
                f'<p style="font-size:.79rem;color:#1e293b;margin:-.4rem 0 1.3rem 0;">'
                f'{t["tr_hint"]}</p>',
                unsafe_allow_html=True,
            )

            suggestions = generate_transformations(transformed, engine, lang=lang)
            code_lang   = "sql" if engine == "duckdb" else "python"

            if not suggestions:
                st.success(f"✅ {t['no_tr']}")
            else:
                for item in suggestions:
                    st.markdown(
                        f'<div class="tc">'
                        f'<div class="t-label">{item["label"]}</div>'
                        f'<div class="t-why">{t["why"]} &nbsp;{item["description"]}</div>'
                        f'</div>',
                        unsafe_allow_html=True,
                    )
                    st.code(item["code"], language=code_lang)

    # ── (Q&A déplacé sous l'aperçu du dataset dans process_file) ──