"""SmartAttend — Brand components."""
import streamlit as st

# Inline SVG — shield with checkmark tick (clean, professional, no graduation cap)
LOGO_SVG = """<svg width="32" height="32" viewBox="0 0 36 36" fill="none" xmlns="http://www.w3.org/2000/svg">
  <rect width="36" height="36" rx="9" fill="#4F46E5"/>
  <path d="M18 7L9 11v8c0 5.25 3.85 10.16 9 11.35C23.15 29.16 27 24.25 27 19v-8l-9-4z"
        fill="white" fill-opacity="0.15"/>
  <path d="M18 7L9 11v8c0 5.25 3.85 10.16 9 11.35C23.15 29.16 27 24.25 27 19v-8l-9-4z"
        stroke="white" stroke-width="1.5" stroke-linejoin="round"/>
  <path d="M14 18l2.8 2.8L22.5 15" stroke="white" stroke-width="2"
        stroke-linecap="round" stroke-linejoin="round"/>
</svg>"""


def header_home():
    """Top navbar for the landing page."""
    st.markdown(f"""
<style>
.sa-nav{{display:flex;align-items:center;justify-content:space-between;
         padding:1rem 0;border-bottom:1px solid #E5E7EB;margin-bottom:0;}}
.sa-nav-left{{display:flex;align-items:center;gap:10px;}}
.sa-nav-left .wordmark{{font-family:'Inter',sans-serif;font-size:1.05rem;
   font-weight:800;color:#111827;letter-spacing:-0.035em;}}
.sa-nav-beta{{font-size:0.65rem;font-weight:700;background:#EEF2FF;color:#4F46E5;
   padding:2px 8px;border-radius:100px;letter-spacing:0.04em;text-transform:uppercase;}}
.sa-nav-links{{display:flex;align-items:center;gap:1.5rem;}}
.sa-nav-links a{{font-size:0.82rem;font-weight:500;color:#6B7280;
   text-decoration:none;transition:color 0.15s;font-family:'Inter',sans-serif;}}
.sa-nav-links a:hover{{color:#4F46E5;}}
</style>
<div class="sa-nav">
  <div class="sa-nav-left">
    {LOGO_SVG}
    <span class="wordmark">SmartAttend</span>
    <span class="sa-nav-beta">Beta</span>
  </div>
  <div class="sa-nav-links">
    <a href="#">Features</a>
    <a href="#">How It Works</a>
    <a href="#">About</a>
  </div>
</div>
""", unsafe_allow_html=True)


def header_dashboard():
    """Brand mark used in the top-left of dashboard navbars."""
    st.markdown(f"""
<style>
.sa-db-brand{{display:flex;align-items:center;gap:10px;}}
.sa-db-brand .wordmark{{font-family:'Inter',sans-serif;font-size:0.95rem;
   font-weight:800;color:#4F46E5;letter-spacing:-0.03em;}}
</style>
<div class="sa-db-brand">
  {LOGO_SVG}
  <span class="wordmark">SmartAttend</span>
</div>
""", unsafe_allow_html=True)
