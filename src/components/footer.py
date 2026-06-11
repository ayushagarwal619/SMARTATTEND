"""SmartAttend — Footer components."""
import streamlit as st


def footer_home():
    st.markdown("""
<style>
.sa-footer{border-top:1px solid #E5E7EB;padding:3rem 0 1.75rem;margin-top:5rem;}
.sa-footer-grid{display:flex;justify-content:space-between;flex-wrap:wrap;
  gap:2.5rem;margin-bottom:2.5rem;}
.sa-footer-brand .name{font-family:'Inter',sans-serif;font-size:1rem;font-weight:800;
  color:#111827;letter-spacing:-0.03em;display:block;margin-bottom:8px;}
.sa-footer-brand p{font-size:0.8rem;color:#6B7280;max-width:240px;
  line-height:1.55;font-family:'Inter',sans-serif;margin:0;}
.sa-footer-col h5{font-size:0.72rem;font-weight:700;text-transform:uppercase;
  letter-spacing:0.09em;color:#374151;margin-bottom:14px;
  font-family:'Inter',sans-serif;}
.sa-footer-col a{display:block;font-size:0.82rem;color:#6B7280;
  text-decoration:none;margin-bottom:9px;font-family:'Inter',sans-serif;
  transition:color 0.15s;}
.sa-footer-col a:hover{color:#4F46E5;}
.sa-footer-bottom{display:flex;justify-content:space-between;align-items:center;
  border-top:1px solid #F3F4F6;padding-top:1.25rem;flex-wrap:wrap;gap:0.5rem;}
.sa-footer-bottom span{font-size:0.78rem;color:#9CA3AF;font-family:'Inter',sans-serif;}
.sa-badge{background:#EEF2FF;color:#4F46E5;padding:3px 11px;
  border-radius:100px;font-size:0.7rem;font-weight:700;letter-spacing:0.03em;}
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
<div style="margin-top:3rem;padding-top:1.25rem;border-top:1px solid #E5E7EB;
     display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:0.5rem;">
  <span style="font-size:0.75rem;color:#9CA3AF;font-family:'Inter',sans-serif;">
    &copy; 2024 SmartAttend &mdash; AI-Powered Attendance
  </span>
  <span style="font-size:0.75rem;color:#9CA3AF;font-family:'Inter',sans-serif;">
    Built for Colleges &amp; Universities
  </span>
</div>
""", unsafe_allow_html=True)
