"""SmartAttend — Brand components redesigned in Neo-Brutalism."""
import streamlit as st

LOGO_SVG = """<svg width="32" height="32" viewBox="0 0 36 36" fill="none" xmlns="http://www.w3.org/2000/svg">
  <rect width="36" height="36" rx="6" fill="#5865F2" stroke="#000" stroke-width="2"/>
  <path d="M18 7L9 11v8c0 5.25 3.85 10.16 9 11.35C23.15 29.16 27 24.25 27 19v-8l-9-4z"
        fill="white" fill-opacity="0.15"/>
  <path d="M18 7L9 11v8c0 5.25 3.85 10.16 9 11.35C23.15 29.16 27 24.25 27 19v-8l-9-4z"
        stroke="white" stroke-width="1.5" stroke-linejoin="round"/>
  <path d="M14 18l2.8 2.8L22.5 15" stroke="white" stroke-width="2"
        stroke-linecap="round" stroke-linejoin="round"/>
</svg>"""

LOGO_SVG_SM = """<svg width="28" height="28" viewBox="0 0 36 36" fill="none">
  <rect width="36" height="36" rx="6" fill="#5865F2" stroke="#000" stroke-width="2"/>
  <path d="M18 7L9 11v8c0 5.25 3.85 10.16 9 11.35C23.15 29.16 27 24.25 27 19v-8l-9-4z"
        fill="white" fill-opacity="0.15"/>
  <path d="M18 7L9 11v8c0 5.25 3.85 10.16 9 11.35C23.15 29.16 27 24.25 27 19v-8l-9-4z"
        stroke="white" stroke-width="1.5" stroke-linejoin="round"/>
  <path d="M14 18l2.8 2.8L22.5 15" stroke="white" stroke-width="2"
        stroke-linecap="round" stroke-linejoin="round"/>
</svg>"""


def header_home():
    st.markdown(f"""
<style>
.sa-nav{{display:flex;align-items:center;justify-content:space-between;
  padding:1.25rem 0;border-bottom:3px solid #000000;margin-bottom:0;}}
.sa-nav-left{{display:flex;align-items:center;gap:12px;}}
.sa-nav-left .wordmark{{font-family:'Outfit',sans-serif;font-size:1.45rem;
  font-weight:900;color:#000000;letter-spacing:-0.04em;text-transform:uppercase;}}
.sa-nav-links{{display:flex;align-items:center;gap:2rem;}}
.sa-nav-links a{{font-size:0.95rem;font-weight:800;color:#000000;
  text-decoration:none;transition:color 0.15s;font-family:'Outfit',sans-serif;}}
.sa-nav-links a:hover{{color:#5865F2;text-decoration:underline;}}
</style>
<div class="sa-nav">
  <div class="sa-nav-left">
    {LOGO_SVG}
    <span class="wordmark">SmartAttend</span>
  </div>
  <div class="sa-nav-links">
    <a href="#features">Features</a>
    <a href="#how-it-works">How It Works</a>
    <a href="#about">About</a>
  </div>
</div>
""", unsafe_allow_html=True)


def header_dashboard():
    st.markdown(f"""
<style>
.sa-db-brand{{display:flex;align-items:center;gap:12px;}}
.sa-db-brand .wordmark{{font-family:'Outfit',sans-serif;font-size:1.3rem;
  font-weight:900;color:#5865F2;letter-spacing:-0.03em;text-transform:uppercase;}}
</style>
<div class="sa-db-brand">
  {LOGO_SVG_SM}
  <span class="wordmark">SmartAttend</span>
</div>
""", unsafe_allow_html=True)
