"""SmartAttend — Teacher Screen (Login + Dashboard)"""
import re
import streamlit as st

from src.ui.base_layout import style_background_dashboard, style_base_layout
from src.components.footer import footer_dashboard
from src.components.subject_card import subject_card
from src.database.db import (
    check_teacher_exists, create_teacher, teacher_login,
    get_teacher_subjects, get_attendance_for_teacher,
    reset_teacher_password,
)
from src.components.dialog_create_subject import create_subject_dialog
from src.components.dialog_share_subject import share_subject_dialog
from src.components.dialog_add_photo import add_photos_dialog
from src.pipelines.face_pipeline import predict_attendance
from src.components.dialog_attendance_results import attendance_result_dialog
import numpy as np
from datetime import datetime
import pandas as pd
from src.database.config import supabase
from src.components.dialog_voice_attendance import voice_attendance_dialog


# ── Shared nav ────────────────────────────────────────────────────────────────
def _topnav(name: str):
    initial = name[:1].upper() if name else "T"
    st.markdown(f"""
<style>
.sat-nav{{display:flex;align-items:center;justify-content:space-between;
  padding:0.9rem 0;border-bottom:1px solid #E5E7EB;margin-bottom:1.75rem;}}
.sat-brand{{display:flex;align-items:center;gap:10px;}}
.sat-brand .wm{{font-family:'Inter',sans-serif;font-size:0.98rem;font-weight:800;
  color:#4F46E5;letter-spacing:-0.03em;}}
.sat-right{{display:flex;align-items:center;gap:12px;}}
.sat-av{{width:36px;height:36px;border-radius:50%;
  background:linear-gradient(135deg,#4F46E5,#7C3AED);color:#fff;
  font-size:0.8rem;font-weight:800;display:flex;align-items:center;
  justify-content:center;font-family:'Inter',sans-serif;flex-shrink:0;}}
.sat-uname{{font-size:0.85rem;font-weight:600;color:#111827;
  font-family:'Inter',sans-serif;display:block;}}
.sat-urole{{font-size:0.72rem;color:#9CA3AF;font-family:'Inter',sans-serif;display:block;}}
</style>
<div class="sat-nav">
  <div class="sat-brand">
    <svg width="30" height="30" viewBox="0 0 36 36" fill="none">
      <rect width="36" height="36" rx="9" fill="#4F46E5"/>
      <path d="M18 7L9 11v8c0 5.25 3.85 10.16 9 11.35C23.15 29.16 27 24.25 27 19v-8l-9-4z"
            fill="white" fill-opacity="0.15"/>
      <path d="M18 7L9 11v8c0 5.25 3.85 10.16 9 11.35C23.15 29.16 27 24.25 27 19v-8l-9-4z"
            stroke="white" stroke-width="1.5" stroke-linejoin="round"/>
      <path d="M14 18l2.8 2.8L22.5 15" stroke="white" stroke-width="2"
            stroke-linecap="round" stroke-linejoin="round"/>
    </svg>
    <span class="wm">SmartAttend</span>
  </div>
  <div class="sat-right">
    <div class="sat-av">{initial}</div>
    <div>
      <span class="sat-uname">{name}</span>
      <span class="sat-urole">Teacher</span>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)


def _sec(title, sub=""):
    st.markdown(f"""
<div style="margin-bottom:1rem;">
  <h2 style="margin:0;font-size:1.1rem;font-weight:700;color:#111827;
             font-family:'Inter',sans-serif;letter-spacing:-0.02em;">{title}</h2>
  {'<p style="margin:4px 0 0;font-size:0.8rem;color:#6B7280;font-family:Inter,sans-serif;">'+sub+'</p>' if sub else ''}
</div>""", unsafe_allow_html=True)


def _teacher_stat_cards(n_sub, n_stu, n_sess):
    st.markdown(f"""
<style>
.tsc-grid{{display:grid;grid-template-columns:repeat(3,1fr);gap:14px;margin-bottom:1.75rem;}}
.tsc-card{{background:#fff;border:1px solid #E5E7EB;border-radius:14px;
  padding:1.25rem 1.375rem;position:relative;overflow:hidden;
  transition:box-shadow 0.2s,transform 0.2s;}}
.tsc-card:hover{{box-shadow:0 6px 20px rgba(0,0,0,0.07);transform:translateY(-2px);}}
.tsc-card::after{{content:'';position:absolute;bottom:0;left:0;right:0;height:3px;}}
.tsc-card.t1::after{{background:#4F46E5;}}
.tsc-card.t2::after{{background:#06B6D4;}}
.tsc-card.t3::after{{background:#7C3AED;}}
.tsc-icon{{font-size:1.25rem;margin-bottom:10px;display:block;}}
.tsc-lbl{{font-size:0.68rem;font-weight:700;text-transform:uppercase;letter-spacing:0.07em;
  color:#9CA3AF;font-family:'Inter',sans-serif;margin-bottom:5px;}}
.tsc-val{{font-size:1.65rem;font-weight:900;letter-spacing:-0.04em;
  font-family:'Inter',sans-serif;color:#111827;line-height:1;}}
.tsc-sub{{font-size:0.72rem;color:#9CA3AF;font-family:'Inter',sans-serif;margin-top:4px;}}
@media(max-width:600px){{.tsc-grid{{grid-template-columns:1fr 1fr;}}}}
</style>
<div class="tsc-grid">
  <div class="tsc-card t1">
    <span class="tsc-icon">📚</span>
    <div class="tsc-lbl">Subjects</div>
    <div class="tsc-val">{n_sub}</div>
    <div class="tsc-sub">managed</div>
  </div>
  <div class="tsc-card t2">
    <span class="tsc-icon">🎓</span>
    <div class="tsc-lbl">Total Students</div>
    <div class="tsc-val">{n_stu}</div>
    <div class="tsc-sub">enrolled across subjects</div>
  </div>
  <div class="tsc-card t3">
    <span class="tsc-icon">📋</span>
    <div class="tsc-lbl">Sessions</div>
    <div class="tsc-val">{n_sess}</div>
    <div class="tsc-sub">attendance sessions</div>
  </div>
</div>
""", unsafe_allow_html=True)


def _tab_nav():
    tabs = {
        "take_attendance":    ("📷", "Take Attendance"),
        "manage_subjects":    ("📚", "Subjects"),
        "attendance_records": ("📊", "Records"),
    }
    cur = st.session_state.get("current_teacher_tab", "take_attendance")
    cols = st.columns(len(tabs))
    for col, (key, (icon, lbl)) in zip(cols, tabs.items()):
        with col:
            t = "primary" if cur == key else "secondary"
            if st.button(f"{icon}  {lbl}", type=t, use_container_width=True, key=f"tt_{key}"):
                st.session_state.current_teacher_tab = key
                st.rerun()
    st.markdown('<hr style="margin:0 0 1.5rem;">', unsafe_allow_html=True)


def _empty_state(emoji, title, subtitle):
    st.markdown(f"""
<div style="background:#fff;border:2px dashed #E5E7EB;border-radius:14px;
     padding:3rem 2rem;text-align:center;">
  <div style="font-size:2rem;margin-bottom:10px;">{emoji}</div>
  <div style="font-size:0.9rem;font-weight:600;color:#374151;
       font-family:'Inter',sans-serif;margin-bottom:5px;">{title}</div>
  <div style="font-size:0.8rem;color:#9CA3AF;font-family:'Inter',sans-serif;">{subtitle}</div>
</div>""", unsafe_allow_html=True)


# ── Router ────────────────────────────────────────────────────────────────────
def teacher_screen():
    style_background_dashboard()
    style_base_layout()
    if "teacher_data" in st.session_state:
        teacher_dashboard()
    elif st.session_state.get("teacher_login_type") == "register":
        teacher_screen_register()
    elif st.session_state.get("teacher_login_type") == "forgot_password":
        teacher_screen_forgot_password()
    else:
        teacher_screen_login()


# ════════════════════════════════════════════════════════════════════════════
# DASHBOARD
# ════════════════════════════════════════════════════════════════════════════
def teacher_dashboard():
    td         = st.session_state.teacher_data
    name       = td["name"]
    teacher_id = td["teacher_id"]

    _topnav(name)

    # Action bar
    a1, a2, a3, _ = st.columns([1, 1, 1, 3])
    with a1:
        if st.button("⇄ Student Mode", type="secondary", use_container_width=True):
            st.session_state["login_type"] = "student"
            st.rerun()
    with a2:
        if st.button("Sign Out", type="secondary", use_container_width=True):
            st.session_state["is_logged_in"] = False
            del st.session_state.teacher_data
            st.rerun()

    st.markdown('<hr style="margin:0 0 1.5rem;">', unsafe_allow_html=True)

    # Stats
    all_sub    = get_teacher_subjects(teacher_id)
    n_stu      = sum(s.get("total_students", 0) for s in all_sub)
    n_sess     = sum(s.get("total_classes",  0) for s in all_sub)
    _teacher_stat_cards(len(all_sub), n_stu, n_sess)

    # Quick actions
    st.markdown("""
<div style="background:linear-gradient(135deg,#4F46E5,#7C3AED);
     border-radius:14px;padding:1.25rem 1.5rem;margin-bottom:1.75rem;
     display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:1rem;">
  <div>
    <div style="font-size:0.95rem;font-weight:700;color:#fff;font-family:'Inter',sans-serif;">
      Quick Actions
    </div>
    <div style="font-size:0.78rem;color:rgba(255,255,255,0.65);font-family:'Inter',sans-serif;margin-top:3px;">
      Most used teacher tools
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

    qc1, qc2, qc3, qc4 = st.columns(4)
    with qc1:
        if st.button("📷 Take Attendance", type="primary", use_container_width=True):
            st.session_state.current_teacher_tab = "take_attendance"
            st.rerun()
    with qc2:
        if st.button("📚 New Subject", type="secondary", use_container_width=True):
            create_subject_dialog(teacher_id)
    with qc3:
        if st.button("📊 View Records", type="secondary", use_container_width=True):
            st.session_state.current_teacher_tab = "attendance_records"
            st.rerun()
    with qc4:
        if st.button("🎙 Voice Mode", type="secondary", use_container_width=True):
            st.session_state.current_teacher_tab = "take_attendance"
            st.rerun()

    st.markdown('<div style="height:1.5rem"></div>', unsafe_allow_html=True)

    if "current_teacher_tab" not in st.session_state:
        st.session_state.current_teacher_tab = "take_attendance"

    _tab_nav()

    tab = st.session_state.current_teacher_tab
    if tab == "take_attendance":
        _tab_attendance()
    elif tab == "manage_subjects":
        _tab_subjects()
    elif tab == "attendance_records":
        _tab_records()

    footer_dashboard()


# ── Tab: Take Attendance ──────────────────────────────────────────────────────
def _tab_attendance():
    teacher_id = st.session_state.teacher_data["teacher_id"]
    _sec("Take AI Attendance",
         "Upload classroom photos or use voice to mark attendance automatically.")

    if "attendance_images" not in st.session_state:
        st.session_state.attendance_images = []

    subjects = get_teacher_subjects(teacher_id)
    if not subjects:
        _empty_state("📭", "No subjects yet", "Go to Subjects tab and create your first subject.")
        return

    subject_options = {f"{s['name']}  ·  {s['subject_code']}": s["subject_id"] for s in subjects}

    c1, c2 = st.columns([3, 1], vertical_alignment="bottom")
    with c1:
        sel_label = st.selectbox("Select Subject", options=list(subject_options.keys()))
    with c2:
        if st.button("＋ Add Photos", type="primary", use_container_width=True):
            add_photos_dialog()

    sel_id = subject_options[sel_label]

    if st.session_state.attendance_images:
        st.markdown('<div style="height:4px"></div>', unsafe_allow_html=True)
        _sec(f"Added Photos ({len(st.session_state.attendance_images)})")
        gcols = st.columns(4)
        for idx, img in enumerate(st.session_state.attendance_images):
            with gcols[idx % 4]:
                st.image(img, use_container_width=True, caption=f"Photo {idx+1}")

    st.markdown('<div style="height:6px"></div>', unsafe_allow_html=True)
    has = bool(st.session_state.attendance_images)
    b1, b2, b3 = st.columns(3)

    with b1:
        if st.button("🗑  Clear All", type="secondary", use_container_width=True, disabled=not has):
            st.session_state.attendance_images = []
            st.rerun()

    with b2:
        if st.button("🔍  Run Face Analysis", type="primary", use_container_width=True, disabled=not has):
            with st.spinner("Deep scanning with AI…"):
                detected_map = {}
                for idx, img in enumerate(st.session_state.attendance_images):
                    img_np = np.array(img.convert("RGB"))
                    det, _, _ = predict_attendance(img_np)
                    if det:
                        for sid in det.keys():
                            detected_map.setdefault(int(sid), []).append(f"Photo {idx+1}")

                enrolled_res      = supabase.table("subject_students").select("*, students(*)").eq("subject_id", sel_id).execute()
                enrolled_students = enrolled_res.data

                if not enrolled_students:
                    st.warning("No students enrolled in this subject.")
                else:
                    results, logs = [], []
                    ts = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
                    for node in enrolled_students:
                        stu     = node["students"]
                        sources = detected_map.get(int(stu["student_id"]), [])
                        present = len(sources) > 0
                        results.append({
                            "Name":   stu["name"],
                            "ID":     stu["student_id"],
                            "Source": ", ".join(sources) if present else "—",
                            "Status": "✅ Present" if present else "❌ Absent",
                        })
                        logs.append({
                            "student_id": stu["student_id"],
                            "subject_id": sel_id,
                            "timestamp":  ts,
                            "is_present": bool(present),
                        })
                    attendance_result_dialog(pd.DataFrame(results), logs)

    with b3:
        if st.button("🎙  Voice Attendance", type="secondary", use_container_width=True):
            voice_attendance_dialog(sel_id)


# ── Tab: Subjects ─────────────────────────────────────────────────────────────
def _tab_subjects():
    teacher_id = st.session_state.teacher_data["teacher_id"]
    h1, h2 = st.columns([3, 1], vertical_alignment="center")
    with h1:
        _sec("Your Subjects", "Manage subjects and share join codes with students.")
    with h2:
        if st.button("＋ New Subject", type="primary", use_container_width=True):
            create_subject_dialog(teacher_id)

    subjects = get_teacher_subjects(teacher_id)
    if not subjects:
        _empty_state("📂", "No subjects yet", 'Click "+ New Subject" to create your first subject.')
        return

    cols = st.columns(2, gap="medium")
    for i, sub in enumerate(subjects):
        def _mk_share(s):
            def _fn():
                if st.button("Share Join Code", type="tertiary",
                             use_container_width=True,
                             icon=":material/share:",
                             key=f"share_{s['subject_code']}"):
                    share_subject_dialog(s["name"], s["subject_code"])
                st.markdown('<div style="height:4px"></div>', unsafe_allow_html=True)
            return _fn

        with cols[i % 2]:
            subject_card(
                name=sub["name"],
                code=sub["subject_code"],
                section=sub["section"],
                stats=[
                    ("🎓", "Students", sub.get("total_students", 0)),
                    ("📅", "Sessions",  sub.get("total_classes",  0)),
                ],
                footer_callback=_mk_share(sub),
                card_index=i,
            )


# ── Tab: Records + Analytics ──────────────────────────────────────────────────
def _tab_records():
    _sec("Attendance Records", "Session-by-session logs with present/absent breakdown.")
    teacher_id = st.session_state.teacher_data["teacher_id"]
    records    = get_attendance_for_teacher(teacher_id)

    if not records:
        _empty_state("📋", "No records yet",
                     "Take your first attendance session to see records here.")
        return

    data = []
    for r in records:
        ts = r.get("timestamp")
        data.append({
            "ts_group":     ts.split(".")[0] if ts else None,
            "Time":         datetime.fromisoformat(ts).strftime("%d %b %Y  %I:%M %p") if ts else "N/A",
            "Subject":      r["subjects"]["name"],
            "Subject Code": r["subjects"]["subject_code"],
            "is_present":   bool(r.get("is_present", False)),
        })

    df = pd.DataFrame(data)
    summary = (
        df.groupby(["ts_group", "Time", "Subject", "Subject Code"])
        .agg(Present=("is_present", "sum"), Total=("is_present", "count"))
        .reset_index()
    )
    summary["Rate %"] = (summary["Present"] / summary["Total"] * 100).round(1)
    summary["Attendance"] = (
        "✅ " + summary["Present"].astype(str) + " / " + summary["Total"].astype(str)
    )
    display = summary.sort_values("ts_group", ascending=False)[
        ["Time", "Subject", "Subject Code", "Attendance", "Rate %"]
    ]
    st.dataframe(display, use_container_width=True, hide_index=True)

    # ── Attendance rate chart ────────────────────────────────────────────────
    st.markdown('<div style="height:1rem"></div>', unsafe_allow_html=True)
    _sec("Attendance Rate per Session")
    if len(summary) >= 2:
        chart_df = summary.sort_values("ts_group")[["Time", "Rate %"]].copy()
        chart_df = chart_df.set_index("Time")
        st.line_chart(chart_df, use_container_width=True)
    else:
        st.info("Add more sessions to see trend charts.")

    # ── Per-subject average ──────────────────────────────────────────────────
    st.markdown('<div style="height:0.5rem"></div>', unsafe_allow_html=True)
    _sec("Average Attendance by Subject")
    sub_avg = (
        summary.groupby("Subject")["Rate %"]
        .mean()
        .reset_index()
        .rename(columns={"Rate %": "Avg %"})
        .sort_values("Avg %", ascending=False)
        .set_index("Subject")
    )
    if not sub_avg.empty:
        st.bar_chart(sub_avg, use_container_width=True)


# ════════════════════════════════════════════════════════════════════════════
# AUTH SCREENS — split layout
# ════════════════════════════════════════════════════════════════════════════
_AUTH_CSS = """
<style>
.sa-ta-left{
  background:linear-gradient(145deg,#111827 0%,#1F2937 60%,#374151 100%);
  border-radius:20px;padding:3rem 2.5rem;
  display:flex;flex-direction:column;justify-content:center;min-height:500px;
}
.sa-ta-left h2{font-size:1.5rem!important;font-weight:900!important;
  color:#fff!important;letter-spacing:-0.04em!important;margin-bottom:0.75rem!important;}
.sa-ta-left p{font-size:0.85rem!important;color:rgba(255,255,255,0.65)!important;
  line-height:1.65!important;margin-bottom:1.75rem!important;}
.sa-ta-bullets{list-style:none;padding:0;margin:0;}
.sa-ta-bullets li{font-size:0.8rem;color:rgba(255,255,255,0.8);
  font-family:'Inter',sans-serif;margin-bottom:10px;
  display:flex;align-items:center;gap:10px;}
.sa-ta-check{width:20px;height:20px;border-radius:50%;
  background:rgba(79,70,229,0.4);display:flex;align-items:center;
  justify-content:center;font-size:0.65rem;color:#fff;flex-shrink:0;}
.sa-form-card2{background:#fff;border:1px solid #E5E7EB;border-radius:20px;padding:2.25rem 2rem;}
.sa-fl{display:flex;align-items:center;gap:10px;margin-bottom:1.5rem;}
.sa-fl .wm{font-family:'Inter',sans-serif;font-size:1rem;font-weight:800;
  color:#4F46E5;letter-spacing:-0.03em;}
</style>
"""

_AUTH_LOGO = """
<svg width="26" height="26" viewBox="0 0 36 36" fill="none">
  <rect width="36" height="36" rx="9" fill="#4F46E5"/>
  <path d="M18 7L9 11v8c0 5.25 3.85 10.16 9 11.35C23.15 29.16 27 24.25 27 19v-8l-9-4z"
        fill="white" fill-opacity="0.15"/>
  <path d="M18 7L9 11v8c0 5.25 3.85 10.16 9 11.35C23.15 29.16 27 24.25 27 19v-8l-9-4z"
        stroke="white" stroke-width="1.5" stroke-linejoin="round"/>
  <path d="M14 18l2.8 2.8L22.5 15" stroke="white" stroke-width="2"
        stroke-linecap="round" stroke-linejoin="round"/>
</svg>"""


# ── Login ─────────────────────────────────────────────────────────────────────
def teacher_screen_login():
    st.markdown(_AUTH_CSS, unsafe_allow_html=True)

    back, _ = st.columns([1, 4])
    with back:
        if st.button("← Home", type="secondary"):
            st.session_state["login_type"] = None
            st.rerun()
    st.markdown('<div style="height:8px"></div>', unsafe_allow_html=True)

    left, right = st.columns([1, 1.1], gap="large")

    with left:
        st.markdown("""
<div class="sa-ta-left">
  <h2>Teacher Login</h2>
  <p>Sign in to your SmartAttend account to manage subjects and take AI-powered attendance.</p>
  <ul class="sa-ta-bullets">
    <li><span class="sa-ta-check">✓</span> Take attendance with one click</li>
    <li><span class="sa-ta-check">✓</span> Track students across all subjects</li>
    <li><span class="sa-ta-check">✓</span> Generate and share QR join codes</li>
    <li><span class="sa-ta-check">✓</span> View analytics and attendance trends</li>
    <li><span class="sa-ta-check">✓</span> Low-attendance alerts</li>
  </ul>
</div>
""", unsafe_allow_html=True)

    with right:
        st.markdown(f"""
<div class="sa-form-card2">
  <div class="sa-fl">{_AUTH_LOGO}<span class="wm">SmartAttend</span></div>
  <div style="font-size:1.2rem;font-weight:800;color:#111827;letter-spacing:-0.03em;
       font-family:'Inter',sans-serif;margin-bottom:4px;">Sign in</div>
  <div style="font-size:0.82rem;color:#6B7280;font-family:'Inter',sans-serif;
       margin-bottom:1.5rem;">Enter your credentials to access your dashboard.</div>
""", unsafe_allow_html=True)

        username = st.text_input("Username", placeholder="e.g. ananya_roy")
        password = st.text_input("Password", type="password", placeholder="Your password")

        st.markdown('<div style="height:6px"></div>', unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            if st.button("Sign In →", type="primary", use_container_width=True):
                if login_teacher(username, password):
                    st.toast("Welcome back! 👋")
                    import time; time.sleep(0.6)
                    st.rerun()
                else:
                    st.error("Incorrect username or password.")
        with c2:
            if st.button("Create Account", type="secondary", use_container_width=True):
                st.session_state.teacher_login_type = "register"
                st.rerun()

        st.markdown('<div style="height:6px"></div>', unsafe_allow_html=True)
        fp, _ = st.columns([1, 2])
        with fp:
            if st.button("Forgot password?", type="tertiary"):
                st.session_state.teacher_login_type = "forgot_password"
                st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)

    footer_dashboard()


# ── Register ──────────────────────────────────────────────────────────────────
def teacher_screen_register():
    st.markdown(_AUTH_CSS, unsafe_allow_html=True)

    back, _ = st.columns([1, 4])
    with back:
        if st.button("← Login", type="secondary"):
            st.session_state.teacher_login_type = "login"
            st.rerun()
    st.markdown('<div style="height:8px"></div>', unsafe_allow_html=True)

    left, right = st.columns([1, 1.1], gap="large")

    with left:
        st.markdown("""
<div class="sa-ta-left">
  <h2>Create Account</h2>
  <p>Set up your SmartAttend teacher profile. It only takes a minute to get started.</p>
  <ul class="sa-ta-bullets">
    <li><span class="sa-ta-check">✓</span> Free to use for all teachers</li>
    <li><span class="sa-ta-check">✓</span> Create unlimited subjects</li>
    <li><span class="sa-ta-check">✓</span> No credit card required</li>
    <li><span class="sa-ta-check">✓</span> Secure bcrypt-hashed passwords</li>
  </ul>
</div>
""", unsafe_allow_html=True)

    with right:
        st.markdown(f"""
<div class="sa-form-card2">
  <div class="sa-fl">{_AUTH_LOGO}<span class="wm">SmartAttend</span></div>
  <div style="font-size:1.2rem;font-weight:800;color:#111827;letter-spacing:-0.03em;
       font-family:'Inter',sans-serif;margin-bottom:4px;">Create Teacher Account</div>
  <div style="font-size:0.82rem;color:#6B7280;font-family:'Inter',sans-serif;
       margin-bottom:1.5rem;">Fill in your details to get started.</div>
""", unsafe_allow_html=True)

        c1, c2 = st.columns(2)
        with c1:
            username = st.text_input("Username", placeholder="ananya_roy")
        with c2:
            name = st.text_input("Full Name", placeholder="Ananya Roy")
        mobile   = st.text_input("Mobile Number", placeholder="+91 9876543210")
        password = st.text_input("Password", type="password", placeholder="Min. 6 characters")
        confirm  = st.text_input("Confirm Password", type="password", placeholder="Repeat password")

        st.markdown('<div style="height:8px"></div>', unsafe_allow_html=True)
        if st.button("Create Account →", type="primary", use_container_width=True):
            ok, msg = register_teacher(username, name, mobile, password, confirm)
            if ok:
                st.success(msg)
                import time; time.sleep(1.5)
                st.session_state.teacher_login_type = "login"
                st.rerun()
            else:
                st.error(msg)

        st.markdown("</div>", unsafe_allow_html=True)

    footer_dashboard()


# ── Forgot password ───────────────────────────────────────────────────────────
def teacher_screen_forgot_password():
    st.markdown(_AUTH_CSS, unsafe_allow_html=True)

    back, _ = st.columns([1, 4])
    with back:
        if st.button("← Login", type="secondary"):
            st.session_state.teacher_login_type = "login"
            for k in ["forgot_step","fp_otp","fp_mobile_entered","fp_otp_time"]:
                st.session_state.pop(k, None)
            st.rerun()
    st.markdown('<div style="height:8px"></div>', unsafe_allow_html=True)

    _, center, __ = st.columns([1, 2, 1])
    with center:
        st.markdown(f"""
<div class="sa-form-card2">
  <div class="sa-fl">{_AUTH_LOGO}<span class="wm">SmartAttend</span></div>
  <div style="font-size:1.2rem;font-weight:800;color:#111827;letter-spacing:-0.03em;
       font-family:'Inter',sans-serif;margin-bottom:4px;">Reset Password</div>
  <div style="font-size:0.82rem;color:#6B7280;font-family:'Inter',sans-serif;
       margin-bottom:1.25rem;">We'll send an OTP to your registered mobile number.</div>
""", unsafe_allow_html=True)

        if "forgot_step" not in st.session_state:
            st.session_state.forgot_step = "enter_mobile"
        step = st.session_state.forgot_step

        # Step bar
        _steps = ["Enter Mobile", "Verify OTP", "New Password"]
        _keys  = ["enter_mobile", "verify_otp", "reset_password"]
        cur_i  = _keys.index(step) if step in _keys else 0
        bar    = '<div style="display:flex;gap:5px;margin-bottom:1.25rem;">'
        for i, s in enumerate(_steps):
            done   = i < cur_i
            active = i == cur_i
            bg  = "#4F46E5" if active else ("#10B981" if done else "#E5E7EB")
            clr = "#fff"    if (active or done) else "#9CA3AF"
            bar += f'<div style="flex:1;background:{bg};color:{clr};border-radius:6px;padding:6px;text-align:center;font-size:0.7rem;font-weight:700;font-family:Inter,sans-serif;">{"✓ " if done else ""}{s}</div>'
        bar += "</div>"
        st.markdown(bar, unsafe_allow_html=True)

        if step == "enter_mobile":
            mob = st.text_input("Registered Mobile", placeholder="+91 9876543210", key="fp_mob")
            if st.button("Send OTP →", type="primary", use_container_width=True):
                if mob:
                    import random, time as _t
                    otp = str(random.randint(100000, 999999))
                    st.session_state.fp_otp            = otp
                    st.session_state.fp_mobile_entered = mob
                    st.session_state.fp_otp_time       = _t.time()
                    st.info(f"Dev mode — OTP: **{otp}**")
                    st.session_state.forgot_step = "verify_otp"
                    st.rerun()
                else:
                    st.warning("Enter your mobile number.")

        elif step == "verify_otp":
            st.caption(f"Sent to {st.session_state.get('fp_mobile_entered','')}")
            otp_in = st.text_input("6-digit OTP", max_chars=6, key="fp_otp_in")
            v, r = st.columns(2)
            with v:
                if st.button("Verify →", type="primary", use_container_width=True):
                    import time as _t
                    if _t.time() - st.session_state.get("fp_otp_time",0) > 300:
                        st.error("OTP expired.")
                        st.session_state.forgot_step = "enter_mobile"
                    elif otp_in == st.session_state.get("fp_otp"):
                        st.session_state.forgot_step = "reset_password"
                        st.rerun()
                    else:
                        st.error("Incorrect OTP.")
            with r:
                if st.button("Resend", type="secondary", use_container_width=True):
                    st.session_state.forgot_step = "enter_mobile"
                    st.rerun()

        elif step == "reset_password":
            st.success("Identity verified.")
            np_ = st.text_input("New Password", type="password", key="fp_np")
            cp_ = st.text_input("Confirm Password", type="password", key="fp_cp")
            if st.button("Update Password →", type="primary", use_container_width=True):
                if not np_ or not cp_:
                    st.warning("Fill in both fields.")
                elif np_ != cp_:
                    st.error("Passwords do not match.")
                elif len(np_) < 6:
                    st.error("Min. 6 characters.")
                else:
                    ok = reset_teacher_password(st.session_state.get("fp_mobile_entered"), np_)
                    if ok:
                        st.success("Password updated!")
                        for k in ["forgot_step","fp_otp","fp_mobile_entered","fp_otp_time"]:
                            st.session_state.pop(k, None)
                        import time as _t; _t.sleep(1)
                        st.session_state.teacher_login_type = "login"
                        st.rerun()
                    else:
                        st.error("No account found with that mobile number.")

        st.markdown("</div>", unsafe_allow_html=True)

    footer_dashboard()


# ── Auth logic ────────────────────────────────────────────────────────────────
def login_teacher(username, password):
    if not username or not password:
        return False
    t = teacher_login(username, password)
    if t:
        st.session_state.user_role    = "teacher"
        st.session_state.teacher_data = t
        st.session_state.is_logged_in = True
        return True
    return False


def register_teacher(username, name, mobile, password, confirm):
    if not all([username, name, password]):
        return False, "All fields are required."
    if not mobile:
        return False, "Mobile number is required."
    if not re.match(r"^\+?[\d\s\-]{7,15}$", mobile):
        return False, "Enter a valid mobile number."
    if check_teacher_exists(username):
        return False, "Username already taken."
    if password != confirm:
        return False, "Passwords do not match."
    if len(password) < 6:
        return False, "Password must be at least 6 characters."
    try:
        create_teacher(username, password, name, mobile)
        return True, "Account created! You can now log in."
    except Exception as e:
        return False, f"Error: {e}"
