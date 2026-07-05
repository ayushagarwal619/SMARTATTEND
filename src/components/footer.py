"""SmartAttend — Footer components redesigned in Neo-Brutalism."""
import streamlit as st


def footer_home():
    st.markdown("""
<style>
.sa-footer{border-top:3px solid #000000;padding:3rem 0 1.75rem;margin-top:5rem;}
.sa-footer-grid{display:flex;justify-content:space-between;flex-wrap:wrap;
  gap:2.5rem;margin-bottom:2.5rem;}
.sa-footer-brand .name{font-family:'Outfit',sans-serif;font-size:1.25rem;font-weight:900;
  color:#000000;letter-spacing:-0.03em;display:block;margin-bottom:8px;text-transform:uppercase;}
.sa-footer-brand p{font-size:0.9rem;color:#333333;max-width:240px;
  line-height:1.55;font-family:'Outfit',sans-serif;margin:0;font-weight:600;}
.sa-footer-col h5{font-size:0.85rem;font-weight:800;text-transform:uppercase;
  letter-spacing:0.06em;color:#000000;margin-bottom:14px;
  font-family:'Outfit',sans-serif;}
.sa-footer-col a{display:block;font-size:0.9rem;color:#333333;
  text-decoration:none;margin-bottom:9px;font-family:'Outfit',sans-serif;
  transition:color 0.15s;font-weight:600;}
.sa-footer-col a:hover{color:#5865F2;text-decoration:underline;}
.sa-footer-bottom{display:flex;justify-content:space-between;align-items:center;
  border-top:2px solid #000000;padding-top:1.25rem;flex-wrap:wrap;gap:0.5rem;}
.sa-footer-bottom span{font-size:0.85rem;color:#000000;font-family:'Outfit',sans-serif;font-weight:700;}
.sa-badge{background:#FFD600;color:#000000;padding:4px 12px;
  border:2px solid #000000;border-radius:4px;font-size:0.8rem;font-weight:800;
  letter-spacing:0.03em;box-shadow: 2px 2px 0 #000;}
</style>
<div class="sa-footer">
  <div class="sa-footer-grid">
    <div class="sa-footer-brand">
      <span class="name">SmartAttend</span>
      <p>AI-powered attendance management built for colleges and universities.</p>
    </div>
    <div class="sa-footer-col">
      <h5>Product</h5>
      <a href="#">Features</a>
      <a href="#">How It Works</a>
      <a href="#">Changelog</a>
    </div>
    <div class="sa-footer-col">
      <h5>Resources</h5>
      <a href="#">Documentation</a>
      <a href="#">API Reference</a>
      <a href="#">Status</a>
    </div>
    <div class="sa-footer-col">
      <h5>Company</h5>
      <a href="#">About</a>
      <a href="#">Contact</a>
      <a href="#">Privacy Policy</a>
      <a href="#">Terms of Service</a>
    </div>
  </div>
  <div class="sa-footer-bottom">
    <span>&copy; 2024 SmartAttend. All rights reserved.</span>
    <span class="sa-badge">v2.0</span>
  </div>
</div>
""", unsafe_allow_html=True)


def footer_dashboard():
    st.markdown("""
<div style="margin-top:3rem;padding-top:1.25rem;border-top:3px solid #000000;
     display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:0.5rem;">
  <span style="font-size:0.85rem;color:#000000;font-family:'Outfit',sans-serif;font-weight:700;">
    &copy; 2024 SmartAttend &mdash; AI-Powered Attendance
  </span>
  <span style="font-size:0.85rem;color:#000000;font-family:'Outfit',sans-serif;font-weight:700;">
    Built for Colleges &amp; Universities
  </span>
</div>
""", unsafe_allow_html=True)
