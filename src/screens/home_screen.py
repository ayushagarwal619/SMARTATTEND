"""SmartAttend — Landing Page"""
import streamlit as st
from src.components.header import header_home
from src.components.footer import footer_home
from src.ui.base_layout import style_base_layout, style_background_home


# ── Inline dashboard mockup SVG ───────────────────────────────────────────────
_DASHBOARD_PREVIEW = """
<svg viewBox="0 0 520 340" xmlns="http://www.w3.org/2000/svg" style="width:100%;max-width:520px;border-radius:16px;box-shadow:0 24px 60px rgba(79,70,229,0.18);">
  <!-- background -->
  <rect width="520" height="340" rx="14" fill="#F9FAFB"/>
  <!-- topbar -->
  <rect width="520" height="44" rx="0" fill="#4F46E5"/>
  <rect x="14" y="13" width="18" height="18" rx="5" fill="white" opacity="0.9"/>
  <rect x="38" y="17" width="72" height="10" rx="5" fill="white" opacity="0.7"/>
  <!-- avatar -->
  <circle cx="494" cy="22" r="13" fill="white" opacity="0.15"/>
  <text x="494" y="27" text-anchor="middle" font-size="10" fill="white" font-family="Inter,sans-serif" font-weight="700">AK</text>
  <!-- stat cards row -->
  <rect x="14" y="60" width="108" height="60" rx="10" fill="white" stroke="#E5E7EB" stroke-width="1"/>
  <rect x="14" y="114" width="108" height="4" rx="2" fill="#4F46E5" opacity="0.6"/>
  <text x="24" y="79" font-size="8" fill="#9CA3AF" font-family="Inter,sans-serif" font-weight="600" letter-spacing="0.5">SUBJECTS</text>
  <text x="24" y="99" font-size="22" fill="#111827" font-family="Inter,sans-serif" font-weight="900">6</text>

  <rect x="132" y="60" width="108" height="60" rx="10" fill="white" stroke="#E5E7EB" stroke-width="1"/>
  <rect x="132" y="114" width="108" height="4" rx="2" fill="#06B6D4" opacity="0.6"/>
  <text x="142" y="79" font-size="8" fill="#9CA3AF" font-family="Inter,sans-serif" font-weight="600" letter-spacing="0.5">CLASSES</text>
  <text x="142" y="99" font-size="22" fill="#111827" font-family="Inter,sans-serif" font-weight="900">48</text>

  <rect x="250" y="60" width="108" height="60" rx="10" fill="white" stroke="#E5E7EB" stroke-width="1"/>
  <rect x="250" y="114" width="108" height="4" rx="2" fill="#7C3AED" opacity="0.6"/>
  <text x="260" y="79" font-size="8" fill="#9CA3AF" font-family="Inter,sans-serif" font-weight="600" letter-spacing="0.5">ATTENDED</text>
  <text x="260" y="99" font-size="22" fill="#111827" font-family="Inter,sans-serif" font-weight="900">42</text>

  <rect x="368" y="60" width="138" height="60" rx="10" fill="#EEF2FF" stroke="#C7D2FE" stroke-width="1"/>
  <rect x="368" y="114" width="138" height="4" rx="2" fill="#10B981" opacity="0.8"/>
  <text x="378" y="79" font-size="8" fill="#6B7280" font-family="Inter,sans-serif" font-weight="600" letter-spacing="0.5">ATTENDANCE</text>
  <text x="378" y="99" font-size="22" fill="#4F46E5" font-family="Inter,sans-serif" font-weight="900">87%</text>

  <!-- subject cards -->
  <rect x="14" y="136" width="236" height="68" rx="10" fill="white" stroke="#E5E7EB" stroke-width="1"/>
  <rect x="14" y="136" width="4" height="68" rx="2" fill="#4F46E5"/>
  <text x="26" y="154" font-size="9" fill="#111827" font-family="Inter,sans-serif" font-weight="700">Data Structures &amp; Algorithms</text>
  <rect x="26" y="160" width="40" height="10" rx="100" fill="#EEF2FF"/>
  <text x="46" y="168" text-anchor="middle" font-size="7" fill="#4F46E5" font-family="Inter,sans-serif" font-weight="600">CS301</text>
  <text x="26" y="180" font-size="7" fill="#9CA3AF" font-family="Inter,sans-serif">Section A</text>
  <!-- progress bar -->
  <rect x="26" y="191" width="212" height="5" rx="100" fill="#F3F4F6"/>
  <rect x="26" y="191" width="175" height="5" rx="100" fill="#10B981"/>

  <rect x="264" y="136" width="242" height="68" rx="10" fill="white" stroke="#E5E7EB" stroke-width="1"/>
  <rect x="264" y="136" width="4" height="68" rx="2" fill="#7C3AED"/>
  <text x="276" y="154" font-size="9" fill="#111827" font-family="Inter,sans-serif" font-weight="700">Database Management Systems</text>
  <rect x="276" y="160" width="40" height="10" rx="100" fill="#F5F3FF"/>
  <text x="296" y="168" text-anchor="middle" font-size="7" fill="#7C3AED" font-family="Inter,sans-serif" font-weight="600">CS405</text>
  <text x="276" y="180" font-size="7" fill="#9CA3AF" font-family="Inter,sans-serif">Section B</text>
  <rect x="276" y="191" width="218" height="5" rx="100" fill="#F3F4F6"/>
  <rect x="276" y="191" width="130" height="5" rx="100" fill="#F59E0B"/>

  <!-- activity feed -->
  <rect x="14" y="218" width="492" height="108" rx="10" fill="white" stroke="#E5E7EB" stroke-width="1"/>
  <text x="24" y="236" font-size="8" fill="#111827" font-family="Inter,sans-serif" font-weight="700">Recent Activity</text>
  <!-- item 1 -->
  <circle cx="28" cy="254" r="6" fill="#D1FAE5"/>
  <text x="28" y="257" text-anchor="middle" font-size="6" fill="#10B981">✓</text>
  <text x="40" y="257" font-size="7.5" fill="#374151" font-family="Inter,sans-serif" font-weight="500">Marked present — DSA  ·  Today 09:15 AM</text>
  <!-- item 2 -->
  <circle cx="28" cy="272" r="6" fill="#D1FAE5"/>
  <text x="28" y="275" text-anchor="middle" font-size="6" fill="#10B981">✓</text>
  <text x="40" y="275" font-size="7.5" fill="#374151" font-family="Inter,sans-serif" font-weight="500">Marked present — DBMS  ·  Yesterday 11:00 AM</text>
  <!-- item 3 -->
  <circle cx="28" cy="290" r="6" fill="#FEE2E2"/>
  <text x="28" y="293" text-anchor="middle" font-size="6" fill="#EF4444">✗</text>
  <text x="40" y="293" font-size="7.5" fill="#374151" font-family="Inter,sans-serif" font-weight="500">Marked absent — CN  ·  Yesterday 02:00 PM</text>
  <!-- item 4 -->
  <circle cx="28" cy="308" r="6" fill="#D1FAE5"/>
  <text x="28" y="311" text-anchor="middle" font-size="6" fill="#10B981">✓</text>
  <text x="40" y="311" font-size="7.5" fill="#374151" font-family="Inter,sans-serif" font-weight="500">Enrolled in Operating Systems  ·  2 days ago</text>
</svg>
"""


def home_screen():
    style_background_home()
    style_base_layout()
    header_home()

    # ════════════════════════════════════════════════════════════════════════
    # HERO — split layout
    # ════════════════════════════════════════════════════════════════════════
    st.markdown("""
<style>
.sa-hero-wrap{padding:3.5rem 0 1rem;}
.sa-hero-badge{display:inline-flex;align-items:center;gap:7px;
  background:#EEF2FF;color:#4F46E5;border:1px solid #C7D2FE;
  padding:5px 14px;border-radius:100px;font-size:0.75rem;font-weight:700;
  letter-spacing:0.03em;font-family:'Inter',sans-serif;margin-bottom:1.5rem;}
.sa-badge-dot{width:7px;height:7px;background:#4F46E5;border-radius:50%;
  animation:pulse 2s infinite;}
@keyframes pulse{0%,100%{opacity:1;}50%{opacity:0.4;}}
.sa-hero-h1{font-size:clamp(2.2rem,4.5vw,3.6rem)!important;font-weight:900!important;
  letter-spacing:-0.05em!important;line-height:1.05!important;
  color:#111827!important;margin-bottom:1.25rem!important;}
.sa-hero-accent{
  background:linear-gradient(135deg,#4F46E5,#7C3AED);
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;
  background-clip:text;}
.sa-hero-sub{font-size:1.05rem!important;color:#4B5563!important;
  line-height:1.65!important;max-width:480px;margin-bottom:2rem!important;}
.sa-hero-cta{display:flex;gap:12px;flex-wrap:wrap;margin-bottom:2.5rem;}
.sa-trust{display:flex;align-items:center;gap:10px;margin-top:0.5rem;}
.sa-trust-avatars{display:flex;}
.sa-trust-avatar{width:28px;height:28px;border-radius:50%;border:2px solid #fff;
  margin-left:-8px;font-size:0.65rem;font-weight:700;font-family:'Inter',sans-serif;
  display:flex;align-items:center;justify-content:center;color:#fff;}
.sa-trust-text{font-size:0.78rem;color:#6B7280;font-family:'Inter',sans-serif;}
.sa-trust-text b{color:#374151;}
</style>
<div class="sa-hero-wrap">
  <div class="sa-hero-badge">
    <span class="sa-badge-dot"></span>
    AI-Powered &nbsp;·&nbsp; Face Recognition &nbsp;·&nbsp; QR Attendance
  </div>
  <h1 class="sa-hero-h1">
    Attendance in<br/><span class="sa-hero-accent">Seconds.</span>
  </h1>
  <p class="sa-hero-sub">
    SmartAttend automates college attendance using facial recognition and QR codes.
    No paper. No manual roll call. Just instant, accurate results.
  </p>
</div>
""", unsafe_allow_html=True)

    # Hero: two columns — CTAs left, dashboard preview right
    left_col, right_col = st.columns([1.05, 1.2], gap="large")

    with left_col:
        cta1, cta2 = st.columns(2, gap="small")
        with cta1:
            if st.button("Student Portal →", type="primary", use_container_width=True):
                st.session_state["login_type"] = "student"
                st.rerun()
        with cta2:
            if st.button("Teacher Login →", type="secondary", use_container_width=True):
                st.session_state["login_type"] = "teacher"
                st.rerun()

        st.markdown("""
<div class="sa-trust" style="margin-top:1.25rem;">
  <div class="sa-trust-avatars">
    <div class="sa-trust-avatar" style="background:#4F46E5;margin-left:0;">RK</div>
    <div class="sa-trust-avatar" style="background:#7C3AED;">PS</div>
    <div class="sa-trust-avatar" style="background:#06B6D4;">AM</div>
    <div class="sa-trust-avatar" style="background:#10B981;">VJ</div>
  </div>
  <span class="sa-trust-text"><b>10,000+</b> students already using SmartAttend</span>
</div>
""", unsafe_allow_html=True)

    with right_col:
        st.markdown(_DASHBOARD_PREVIEW, unsafe_allow_html=True)

    # ── Statistics band ──────────────────────────────────────────────────────
    st.markdown("""
<style>
.sa-stats-band{
  background:linear-gradient(135deg,#4F46E5 0%,#7C3AED 100%);
  border-radius:18px;padding:2.25rem 2.5rem;margin:3.5rem 0 2rem;
  display:grid;grid-template-columns:repeat(4,1fr);gap:1rem;
}
.sa-band-item{text-align:center;}
.sa-band-val{font-size:2rem;font-weight:900;color:#fff;
  letter-spacing:-0.04em;display:block;font-family:'Inter',sans-serif;}
.sa-band-lbl{font-size:0.72rem;color:rgba(255,255,255,0.65);font-weight:500;
  font-family:'Inter',sans-serif;letter-spacing:0.03em;margin-top:2px;}
@media(max-width:600px){.sa-stats-band{grid-template-columns:repeat(2,1fr);}}
</style>
<div class="sa-stats-band">
  <div class="sa-band-item">
    <span class="sa-band-val">10K+</span>
    <span class="sa-band-lbl">Students Registered</span>
  </div>
  <div class="sa-band-item">
    <span class="sa-band-val">500+</span>
    <span class="sa-band-lbl">Classes Daily</span>
  </div>
  <div class="sa-band-item">
    <span class="sa-band-val">98%</span>
    <span class="sa-band-lbl">Recognition Accuracy</span>
  </div>
  <div class="sa-band-item">
    <span class="sa-band-val">&lt;3s</span>
    <span class="sa-band-lbl">Average Scan Time</span>
  </div>
</div>
""", unsafe_allow_html=True)

    # ════════════════════════════════════════════════════════════════════════
    # FEATURES
    # ════════════════════════════════════════════════════════════════════════
    st.markdown("""
<style>
.sa-sec-eyebrow{font-size:0.7rem;font-weight:700;text-transform:uppercase;
  letter-spacing:0.1em;color:#4F46E5;text-align:center;
  font-family:'Inter',sans-serif;margin-bottom:8px;margin-top:4rem;}
.sa-sec-title{font-size:clamp(1.6rem,3vw,2.1rem);font-weight:900;
  letter-spacing:-0.04em;color:#111827;text-align:center;
  margin-bottom:0.6rem;font-family:'Inter',sans-serif;}
.sa-sec-sub{font-size:0.9rem;color:#6B7280;text-align:center;
  max-width:500px;margin:0 auto 2.5rem;line-height:1.6;
  font-family:'Inter',sans-serif;}
.sa-feat-grid{
  display:grid;grid-template-columns:repeat(3,1fr);
  gap:16px;margin-bottom:1rem;
}
@media(max-width:800px){.sa-feat-grid{grid-template-columns:repeat(2,1fr);}}
@media(max-width:500px){.sa-feat-grid{grid-template-columns:1fr;}}
.sa-feat-card{
  background:#fff;border:1px solid #E5E7EB;border-radius:16px;
  padding:24px 22px;
  transition:box-shadow 0.22s ease,transform 0.22s ease;
}
.sa-feat-card:hover{
  box-shadow:0 12px 36px rgba(79,70,229,0.11);
  transform:translateY(-3px);
}
.sa-feat-icon{
  width:46px;height:46px;border-radius:12px;
  display:flex;align-items:center;justify-content:center;
  font-size:1.25rem;margin-bottom:14px;
}
.sa-feat-card h4{
  font-size:0.95rem;font-weight:700;color:#111827;
  margin-bottom:7px;font-family:'Inter',sans-serif;
}
.sa-feat-card p{
  font-size:0.82rem;color:#6B7280;line-height:1.6;
  font-family:'Inter',sans-serif;margin:0;
}
</style>
<div class="sa-sec-eyebrow">Features</div>
<div class="sa-sec-title">Everything You Need</div>
<div class="sa-sec-sub">
  Built for real classrooms. Designed to replace clipboards, manual registers, and proxy attendance.
</div>
<div class="sa-feat-grid">
  <div class="sa-feat-card">
    <div class="sa-feat-icon" style="background:#EEF2FF;">🤖</div>
    <h4>Face Recognition</h4>
    <p>Upload a classroom photo and AI instantly identifies and marks all recognised students present.</p>
  </div>
  <div class="sa-feat-card">
    <div class="sa-feat-icon" style="background:#F0FDF4;">📱</div>
    <h4>QR Code Joining</h4>
    <p>Students scan once to enroll in a subject permanently. Share via WhatsApp, email, or on-screen.</p>
  </div>
  <div class="sa-feat-card">
    <div class="sa-feat-icon" style="background:#FFF7ED;">📊</div>
    <h4>Live Analytics</h4>
    <p>Real-time attendance charts, subject-wise breakdowns, and low-attendance alerts for teachers.</p>
  </div>
  <div class="sa-feat-card">
    <div class="sa-feat-icon" style="background:#F0F9FF;">🎙️</div>
    <h4>Voice Attendance</h4>
    <p>Record classroom audio — AI identifies students by voice as a second verification method.</p>
  </div>
  <div class="sa-feat-card">
    <div class="sa-feat-icon" style="background:#FFF1F2;">📋</div>
    <h4>Instant Reports</h4>
    <p>Session-by-session logs, present/absent counts, downloadable records — all in one dashboard.</p>
  </div>
  <div class="sa-feat-card">
    <div class="sa-feat-icon" style="background:#F5F3FF;">🔒</div>
    <h4>Secure by Design</h4>
    <p>Biometric data is encrypted. Role-based access ensures teachers and students see only what's theirs.</p>
  </div>
</div>
""", unsafe_allow_html=True)

    # ════════════════════════════════════════════════════════════════════════
    # HOW IT WORKS — horizontal stepper
    # ════════════════════════════════════════════════════════════════════════
    st.markdown("""
<style>
.sa-steps-wrap{
  background:#fff;border:1px solid #E5E7EB;border-radius:20px;
  padding:2.5rem 2rem;margin:3rem 0;
}
.sa-steps-grid{
  display:grid;grid-template-columns:repeat(4,1fr);
  gap:0;position:relative;
}
.sa-steps-grid::before{
  content:'';position:absolute;top:24px;left:12.5%;right:12.5%;
  height:2px;background:linear-gradient(90deg,#C7D2FE,#DDD6FE);
  z-index:0;
}
@media(max-width:700px){
  .sa-steps-grid{grid-template-columns:1fr 1fr;}
  .sa-steps-grid::before{display:none;}
}
.sa-step{text-align:center;padding:0 1rem;position:relative;z-index:1;}
.sa-step-num{
  width:48px;height:48px;border-radius:50%;
  background:linear-gradient(135deg,#4F46E5,#7C3AED);
  color:#fff;font-size:0.95rem;font-weight:800;
  display:flex;align-items:center;justify-content:center;
  margin:0 auto 14px;font-family:'Inter',sans-serif;
  box-shadow:0 4px 16px rgba(79,70,229,0.35);
}
.sa-step h4{font-size:0.9rem;font-weight:700;color:#111827;
  margin-bottom:6px;font-family:'Inter',sans-serif;}
.sa-step p{font-size:0.78rem;color:#6B7280;
  font-family:'Inter',sans-serif;line-height:1.5;margin:0;}
</style>
<div class="sa-sec-eyebrow">How It Works</div>
<div class="sa-sec-title">Up and Running in 4 Steps</div>
<div class="sa-sec-sub">From account creation to your first AI-powered attendance session in under 5 minutes.</div>
<div class="sa-steps-wrap">
  <div class="sa-steps-grid">
    <div class="sa-step">
      <div class="sa-step-num">1</div>
      <h4>Create Subject</h4>
      <p>Teacher creates a subject with a unique code and section identifier.</p>
    </div>
    <div class="sa-step">
      <div class="sa-step-num">2</div>
      <h4>Generate QR</h4>
      <p>A shareable QR code and join link are auto-generated for the subject.</p>
    </div>
    <div class="sa-step">
      <div class="sa-step-num">3</div>
      <h4>Students Join</h4>
      <p>Students scan the QR once and are permanently enrolled in the subject.</p>
    </div>
    <div class="sa-step">
      <div class="sa-step-num">4</div>
      <h4>Track Attendance</h4>
      <p>Upload a classroom photo — AI scans, marks, and logs attendance instantly.</p>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

    # ════════════════════════════════════════════════════════════════════════
    # SOCIAL PROOF BANNER
    # ════════════════════════════════════════════════════════════════════════
    st.markdown("""
<div style="background:linear-gradient(135deg,#111827 0%,#1F2937 100%);
     border-radius:18px;padding:3rem 2.5rem;text-align:center;margin:1rem 0 2rem;">
  <div style="font-size:clamp(1.2rem,2.5vw,1.65rem);font-weight:900;color:#fff;
       letter-spacing:-0.035em;margin-bottom:0.75rem;font-family:'Inter',sans-serif;">
    Trusted by 50+ Educational Institutions
  </div>
  <div style="font-size:0.88rem;color:rgba(255,255,255,0.6);max-width:500px;
       margin:0 auto;font-family:'Inter',sans-serif;line-height:1.65;">
    "SmartAttend replaced our paper registers completely. Attendance is done before the
    lecture even starts. Our faculty love it."
  </div>
  <div style="margin-top:1.25rem;font-size:0.78rem;color:rgba(255,255,255,0.4);
       font-family:'Inter',sans-serif;">
    — Head of Department, Computer Science, XYZ Engineering College
  </div>
</div>
""", unsafe_allow_html=True)

    footer_home()
