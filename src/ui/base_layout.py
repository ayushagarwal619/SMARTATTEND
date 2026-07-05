"""
SmartAttend — Global Design System
Updated to Neo-Brutalism styling system.
"""
import streamlit as st

# ── Design tokens ─────────────────────────────────────────────────────────────
P      = "#5865F2"   # Primary Indigo
P_HVR  = "#4752C4"   # Primary Hover
SEC    = "#EB459E"   # Secondary Pink
ACC    = "#000000"   # Structural Black
OK     = "#22C55E"   # Success
WARN   = "#F59E0B"   # Warning
ERR    = "#EF4444"   # Error


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
    st.markdown("<style>.stApp{background:#FAFAFA!important;}</style>",
                unsafe_allow_html=True)


def style_background_dashboard():
    bg = "#1A1A1A" if _dark() else "#FAFAFA"
    st.markdown(f"<style>.stApp{{background:{bg}!important;}}</style>",
                unsafe_allow_html=True)


def style_base_layout():
    d = _dark()
    bg           = "#1A1A1A" if d else "#FAFAFA"
    surf         = "#242424" if d else "#FFFFFF"
    brd          = "#FFFFFF" if d else "#000000"
    tx           = "#FFFFFF" if d else "#000000"
    muted        = "#CCCCCC" if d else "#333333"
    inp_bg       = "#2A2A2A" if d else "#FFFFFF"
    shadow_color = "#FFFFFF" if d else "#000000"

    st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Climate+Crisis&family=Outfit:wght@300;400;500;600;700;800;900&display=swap');

*, *::before, *::after {{
  box-sizing: border-box;
}}

html, body, [class*="css"] {{
  font-family: 'Outfit', sans-serif !important;
  -webkit-font-smoothing: antialiased;
}}

/* ── Streamlit chrome ── */
#MainMenu, footer, header {{
  visibility: hidden !important;
  height: 0 !important;
}}
.stDeployButton {{
  display: none !important;
}}
[data-testid="stToolbar"] {{
  display: none !important;
}}

/* ── App shell ── */
.stApp {{
  background: {bg} !important;
  color: {tx} !important;
}}

/* ── Container ── */
.block-container {{
  padding: 1.25rem 2.5rem 4rem !important;
  max-width: 1340px !important;
  margin: 0 auto !important;
}}
@media (max-width: 900px) {{
  .block-container {{
    padding: 1rem 1.25rem 3rem !important;
  }}
}}
@media (max-width: 600px) {{
  .block-container {{
    padding: 0.75rem 0.875rem 2.5rem !important;
  }}
}}

/* ── Typography ── */
h1 {{
  font-family: 'Climate Crisis', display, sans-serif !important;
  font-size: 3.25rem !important;
  font-weight: 900 !important;
  letter-spacing: -0.04em !important;
  line-height: 1.0 !important;
  color: {tx} !important;
  margin-bottom: 0.75rem !important;
}}
h2 {{
  font-family: 'Climate Crisis', display, sans-serif !important;
  font-size: 1.85rem !important;
  font-weight: 900 !important;
  letter-spacing: -0.03em !important;
  line-height: 1.1 !important;
  color: {tx} !important;
  margin-bottom: 0.75rem !important;
}}
h3 {{
  font-family: 'Outfit', sans-serif !important;
  font-size: 1.35rem !important;
  font-weight: 800 !important;
  color: {tx} !important;
  margin-bottom: 0 !important;
}}
p, label, .stMarkdown p, .stText {{
  font-family: 'Outfit', sans-serif !important;
  color: {muted} !important;
  font-size: 0.95rem !important;
  line-height: 1.5 !important;
}}
label[data-baseweb] {{
  font-family: 'Outfit', sans-serif !important;
  font-size: 0.95rem !important;
  font-weight: 800 !important;
  color: {tx} !important;
  letter-spacing: 0.01em !important;
}}

/* ── Inputs (System) ── */
.stTextInput>div>div>input,
.stTextArea>div>div>textarea,
.stSelectbox>div>div {{
  height: 52px !important;
  border: 3px solid {brd} !important;
  border-radius: 6px !important;
  background: {inp_bg} !important;
  color: {tx} !important;
  font-family: 'Outfit', sans-serif !important;
  font-size: 0.95rem !important;
  padding: 0.65rem 0.875rem !important;
  transition: border-color 0.15s ease, box-shadow 0.15s ease !important;
}}

.stTextArea>div>div>textarea {{
  height: auto !important;
  min-height: 120px !important;
}}

.stTextInput>div>div>input:focus,
.stTextArea>div>div>textarea:focus,
.stSelectbox>div>div:focus-within {{
  outline: none !important;
  border-color: {P} !important;
  box-shadow: 4px 4px 0 {shadow_color} !important;
}}

/* ── Button System ── */
button[kind="primary"], button[kind="primaryFormSubmit"] {{
  background: {P} !important;
  color: #FFFFFF !important;
  border: 3px solid {brd} !important;
  border-radius: 6px !important;
  font-family: 'Outfit', sans-serif !important;
  font-weight: 800 !important;
  font-size: 0.95rem !important;
  padding: 0.65rem 1.5rem !important;
  box-shadow: 4px 4px 0 {shadow_color} !important;
  transition: transform 100ms ease, box-shadow 100ms ease !important;
  cursor: pointer !important;
}}

button[kind="primary"]:hover, button[kind="primaryFormSubmit"]:hover {{
  transform: translate(-2px, -2px) !important;
  box-shadow: 6px 6px 0 {shadow_color} !important;
}}

button[kind="primary"]:active, button[kind="primaryFormSubmit"]:active {{
  transform: translate(4px, 4px) !important;
  box-shadow: 0px 0px 0 {shadow_color} !important;
}}

button[kind="secondary"] {{
  background: {SEC} !important;
  color: #FFFFFF !important;
  border: 3px solid {brd} !important;
  border-radius: 6px !important;
  font-family: 'Outfit', sans-serif !important;
  font-weight: 800 !important;
  font-size: 0.95rem !important;
  padding: 0.65rem 1.5rem !important;
  box-shadow: 4px 4px 0 {shadow_color} !important;
  transition: transform 100ms ease, box-shadow 100ms ease !important;
  cursor: pointer !important;
}}

button[kind="secondary"]:hover {{
  transform: translate(-2px, -2px) !important;
  box-shadow: 6px 6px 0 {shadow_color} !important;
}}

button[kind="secondary"]:active {{
  transform: translate(4px, 4px) !important;
  box-shadow: 0px 0px 0 {shadow_color} !important;
}}

button[kind="tertiary"] {{
  background: {surf} !important;
  color: {tx} !important;
  border: 3px solid {brd} !important;
  border-radius: 6px !important;
  font-family: 'Outfit', sans-serif !important;
  font-weight: 800 !important;
  font-size: 0.95rem !important;
  padding: 0.65rem 1.5rem !important;
  box-shadow: 4px 4px 0 {shadow_color} !important;
  transition: transform 100ms ease, box-shadow 100ms ease !important;
  cursor: pointer !important;
}}

button[kind="tertiary"]:hover {{
  transform: translate(-2px, -2px) !important;
  box-shadow: 6px 6px 0 {shadow_color} !important;
}}

button[kind="tertiary"]:active {{
  transform: translate(4px, 4px) !important;
  box-shadow: 0px 0px 0 {shadow_color} !important;
}}

button:disabled, button[disabled], 
button[kind="primary"]:disabled, button[kind="primaryFormSubmit"]:disabled,
button[kind="secondary"]:disabled, button[kind="tertiary"]:disabled {{
  background: #E2E8F0 !important;
  color: #94A3B8 !important;
  border: 3px solid {brd} !important;
  box-shadow: 4px 4px 0 {shadow_color} !important;
  transform: none !important;
  cursor: not-allowed !important;
  transition: none !important;
}}

button:disabled:hover, button[disabled]:hover {{
  transform: none !important;
  box-shadow: 4px 4px 0 {shadow_color} !important;
}}

/* ── Metrics ── */
[data-testid="stMetric"] {{
  background: {surf} !important;
  border: 3px solid {brd} !important;
  border-radius: 6px !important;
  padding: 1.25rem 1.5rem !important;
  box-shadow: 4px 4px 0 {shadow_color} !important;
}}
[data-testid="stMetricLabel"] {{
  font-size: 0.8rem !important;
  font-weight: 800 !important;
  text-transform: uppercase !important;
  letter-spacing: 0.05em !important;
  color: {tx} !important;
  font-family: 'Outfit', sans-serif !important;
}}
[data-testid="stMetricValue"] {{
  font-size: 2.0rem !important;
  font-weight: 900 !important;
  color: {tx} !important;
  letter-spacing: -0.04em !important;
  font-family: 'Outfit', sans-serif !important;
}}

/* ── Dividers ── */
hr {{
  border: none !important;
  border-top: 3px solid {brd} !important;
  margin: 1.25rem 0 !important;
}}

/* ── Alerts & Toast ── */
[data-testid="stAlert"] {{
  border: 3px solid {brd} !important;
  border-radius: 6px !important;
  box-shadow: 4px 4px 0 {shadow_color} !important;
  background: {surf} !important;
  color: {tx} !important;
  font-family: 'Outfit', sans-serif !important;
}}
[data-testid="stAlert"] > div {{
  border: none !important;
  background: transparent !important;
}}
[data-testid="stToast"] {{
  border: 3px solid {brd} !important;
  border-radius: 6px !important;
  box-shadow: 4px 4px 0 {shadow_color} !important;
  background: {surf} !important;
  color: {tx} !important;
  font-family: 'Outfit', sans-serif !important;
}}

/* ── Camera ── */
[data-testid="stCameraInput"] {{
  border: 3px solid {brd} !important;
  border-radius: 6px !important;
  box-shadow: 4px 4px 0 {shadow_color} !important;
  overflow: hidden !important;
}}

/* ── Progress ── */
.stProgress>div>div {{
  background: {surf} !important;
  border: 2.5px solid {brd} !important;
  border-radius: 4px !important;
  height: 14px !important;
}}
.stProgress>div>div>div {{
  background: {P} !important;
  border-radius: 0px !important;
  border-right: 2.5px solid {brd} !important;
}}

/* ── Bordered containers ── */
[data-testid="stVerticalBlockBorderWrapper"] {{
  border: 4px solid {brd} !important;
  border-radius: 8px !important;
  background: {surf} !important;
  padding: 24px !important;
  box-shadow: 6px 6px 0 {shadow_color} !important;
}}

/* ── Charts ── */
[data-testid="stArrowVegaLiteChart"],
[data-testid="stVegaLiteChart"] {{
  border: 3px solid {brd} !important;
  border-radius: 6px !important;
  box-shadow: 4px 4px 0 {shadow_color} !important;
  background: {surf} !important;
}}
</style>
""", unsafe_allow_html=True)
