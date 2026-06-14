"""
SmartAttend — Global Design System
New token set as per spec:
  Primary  #5B5FF8   Dark  #0F172A   Success  #22C55E   Background  #F8FAFC
"""
import streamlit as st

# ── Design tokens ─────────────────────────────────────────────────────────────
P      = "#5B5FF8"   # primary
P_HVR  = "#4A4EE0"   # primary hover (5% darker)
P_LITE = "#EEEFFF"   # primary tint
P_MID  = "#C7C9FD"   # primary mid
SEC    = "#7C3AED"   # secondary violet
ACC    = "#06B6D4"   # accent cyan
OK     = "#22C55E"   # success
WARN   = "#F59E0B"   # warning
ERR    = "#EF4444"   # error

G50  = "#F8FAFC"     # app background
G100 = "#F1F5F9"
G200 = "#E2E8F0"
G300 = "#CBD5E1"
G400 = "#94A3B8"
G500 = "#64748B"
G600 = "#475569"
G700 = "#334155"
G800 = "#1E293B"
G900 = "#0F172A"     # dark base
WHT  = "#FFFFFF"

D_BG      = "#0B0B14"
D_SURFACE = "#131325"
D_BORDER  = "#202040"
D_TEXT    = "#E2E8F0"
D_MUTED   = "#94A3B8"
D_INPUT   = "#18182E"


def _dark() -> bool:
    return st.session_state.get("dark_mode", False)


def render_theme_toggle(key: str = "theme_toggle"):
    if "dark_mode" not in st.session_state:
        st.session_state.dark_mode = False
    label = "☀️ Light" if st.session_state.dark_mode else "🌙 Dark"
    if st.button(label, key=key, type="tertiary"):
        st.session_state.dark_mode = not st.session_state.dark_mode
        st.rerun()


def style_background_home():
    st.markdown(f"<style>.stApp{{background:{G50}!important;}}</style>",
                unsafe_allow_html=True)


def style_background_dashboard():
    bg = D_BG if _dark() else G50
    st.markdown(f"<style>.stApp{{background:{bg}!important;}}</style>",
                unsafe_allow_html=True)


def style_base_layout():
    d      = _dark()
    bg     = D_BG      if d else G50
    surf   = D_SURFACE if d else WHT
    brd    = D_BORDER  if d else G200
    tx     = D_TEXT    if d else G900
    muted  = D_MUTED   if d else G500
    inp_bg = D_INPUT   if d else WHT

    st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

*,*::before,*::after{{box-sizing:border-box;}}
html,body,[class*="css"]{{
  font-family:'Inter',-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif!important;
  -webkit-font-smoothing:antialiased;
}}

/* ── Streamlit chrome ── */
#MainMenu,footer,header{{visibility:hidden!important;height:0!important;}}
.stDeployButton{{display:none!important;}}
[data-testid="stToolbar"]{{display:none!important;}}

/* ── App shell ── */
.stApp{{background:{bg}!important;color:{tx}!important;}}

/* ── Container ── */
.block-container{{
  padding:1.25rem 2.5rem 4rem!important;
  max-width:1340px!important;
  margin:0 auto!important;
}}
@media(max-width:900px){{.block-container{{padding:1rem 1.25rem 3rem!important;}}}}
@media(max-width:600px){{.block-container{{padding:0.75rem 0.875rem 2.5rem!important;}}}}

/* ── Typography ── */
h1{{font-family:'Inter',sans-serif!important;font-size:2.25rem!important;
    font-weight:900!important;letter-spacing:-0.045em!important;
    line-height:1.1!important;color:{tx}!important;margin-bottom:0!important;}}
h2{{font-family:'Inter',sans-serif!important;font-size:1.35rem!important;
    font-weight:700!important;letter-spacing:-0.025em!important;
    color:{tx}!important;margin-bottom:0!important;}}
h3{{font-family:'Inter',sans-serif!important;font-size:1.05rem!important;
    font-weight:600!important;color:{tx}!important;margin-bottom:0!important;}}
p,label,.stMarkdown p,.stText{{
  font-family:'Inter',sans-serif!important;
  color:{muted}!important;font-size:0.875rem!important;line-height:1.6!important;
}}
label[data-baseweb]{{
  font-family:'Inter',sans-serif!important;font-size:0.8rem!important;
  font-weight:600!important;color:{tx}!important;letter-spacing:0.01em!important;
}}

/* ── Text inputs ── */
.stTextInput>div>div>input,
.stTextArea>div>div>textarea{{
  background:{inp_bg}!important;border:1.5px solid {brd}!important;
  border-radius:9px!important;color:{tx}!important;
  font-family:'Inter',sans-serif!important;font-size:0.875rem!important;
  padding:0.65rem 0.875rem!important;
  transition:border-color 0.18s ease,box-shadow 0.18s ease!important;
}}
.stTextInput>div>div>input:focus,
.stTextArea>div>div>textarea:focus{{
  border-color:{P}!important;
  box-shadow:0 0 0 3px rgba(91,95,248,0.13)!important;outline:none!important;
}}

/* ── Selectbox ── */
.stSelectbox>div>div{{
  background:{inp_bg}!important;border:1.5px solid {brd}!important;
  border-radius:9px!important;color:{tx}!important;
  font-family:'Inter',sans-serif!important;font-size:0.875rem!important;
}}
[data-testid="stSelectbox"] label{{
  font-size:0.8rem!important;font-weight:600!important;color:{tx}!important;
}}

/* ── Buttons — primary ── */
button[kind="primaryFormSubmit"],
button[kind="primary"]{{
  background:{P}!important;color:#fff!important;border:none!important;
  border-radius:9px!important;font-family:'Inter',sans-serif!important;
  font-size:0.875rem!important;font-weight:600!important;
  padding:0.575rem 1.375rem!important;cursor:pointer!important;
  transition:background 0.18s,transform 0.15s,box-shadow 0.18s!important;
  box-shadow:0 2px 8px rgba(91,95,248,0.3)!important;
}}
button[kind="primary"]:hover{{
  background:{P_HVR}!important;transform:translateY(-1px)!important;
  box-shadow:0 6px 18px rgba(91,95,248,0.38)!important;
}}
button[kind="primary"]:active{{transform:translateY(0)!important;}}

/* ── Buttons — secondary ── */
button[kind="secondary"]{{
  background:{surf}!important;color:{tx}!important;
  border:1.5px solid {brd}!important;border-radius:9px!important;
  font-family:'Inter',sans-serif!important;font-size:0.875rem!important;
  font-weight:500!important;padding:0.575rem 1.375rem!important;
  transition:background 0.18s,border-color 0.18s,box-shadow 0.18s!important;
}}
button[kind="secondary"]:hover{{
  background:{G100}!important;border-color:{G300}!important;
  box-shadow:0 2px 8px rgba(0,0,0,0.06)!important;
}}

/* ── Buttons — tertiary ── */
button[kind="tertiary"]{{
  background:transparent!important;color:{P}!important;border:none!important;
  border-radius:9px!important;font-family:'Inter',sans-serif!important;
  font-size:0.875rem!important;font-weight:500!important;
  padding:0.5rem 1rem!important;transition:background 0.15s!important;
}}
button[kind="tertiary"]:hover{{background:rgba(91,95,248,0.07)!important;}}

/* ── Metrics ── */
[data-testid="stMetric"]{{
  background:{surf}!important;border:1px solid {brd}!important;
  border-radius:14px!important;padding:1.25rem 1.5rem!important;
  transition:box-shadow 0.2s!important;
}}
[data-testid="stMetric"]:hover{{box-shadow:0 4px 16px rgba(0,0,0,0.07)!important;}}
[data-testid="stMetricLabel"]{{
  font-size:0.7rem!important;font-weight:700!important;
  text-transform:uppercase!important;letter-spacing:0.06em!important;
  color:{muted}!important;
}}
[data-testid="stMetricValue"]{{
  font-size:1.8rem!important;font-weight:900!important;
  color:{tx}!important;letter-spacing:-0.04em!important;
}}
[data-testid="stMetricDelta"]{{font-size:0.78rem!important;}}

/* ── Dividers ── */
hr{{border:none!important;border-top:1px solid {brd}!important;margin:1.25rem 0!important;}}

/* ── Dataframe ── */
[data-testid="stDataFrame"]{{
  border-radius:12px!important;border:1px solid {brd}!important;overflow:hidden!important;
}}

/* ── Alerts ── */
[data-testid="stAlert"]{{border-radius:10px!important;font-family:'Inter',sans-serif!important;}}

/* ── Spinner ── */
.stSpinner>div{{border-top-color:{P}!important;}}

/* ── Toast ── */
[data-testid="stToast"]{{
  border-radius:10px!important;font-family:'Inter',sans-serif!important;
  font-size:0.875rem!important;
}}

/* ── Camera ── */
[data-testid="stCameraInput"]{{border-radius:12px!important;overflow:hidden!important;}}

/* ── Progress ── */
.stProgress>div>div>div{{background:{P}!important;border-radius:100px!important;}}

/* ── Bordered containers ── */
[data-testid="stVerticalBlockBorderWrapper"]{{
  border:1.5px solid {brd}!important;border-radius:14px!important;
  background:{surf}!important;padding:1.25rem!important;
}}

/* ── Charts ── */
[data-testid="stArrowVegaLiteChart"],
[data-testid="stVegaLiteChart"]{{
  border-radius:12px!important;overflow:hidden!important;
}}
</style>
""", unsafe_allow_html=True)
