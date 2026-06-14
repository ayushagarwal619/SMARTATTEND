"""SmartAttend — Teacher Screen.
Added: Low Attendance Alerts panel, per-subject analytics, updated #5B5FF8 colour tokens.
All attendance logic, face recognition, QR logic unchanged.
"""
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

# ── Inline logo ───────────────────────────────────────────────────────────────
_LOGO = """<svg width="30" height="30" viewBox="0 0 36 36" fill="none">
  <rect width="36" height="36" rx="9" fill="#5B5FF8"/>
  <path d="M18 7L9 11v8c0 5.25 3.85 10.16 9 11.35C23.15 29.16 27 24.25 27 19v-8l-9-4z"
        fill="white" fill-opacity="0.15"/>
  <path d="M18 7L9 11v8c0 5.25 3.85 10.16 9 11.35C23.15 29.16 27 24.25 27 19v-8l-9-4z"
        stroke="white" stroke-width="1.5" stroke-linejoin="round"/>
  <path d="M14 18l2.8 2.8L22.5 15" stroke="white" stroke-width="2"
        stroke-linecap="round" stroke-linejoin="round"/>
</svg>"""

_AUTH_LOGO = """<svg width="26" height="26" viewBox="0 0 36 36" fill="none">
  <rect width="36" height="36" rx="9" fill="#5B5FF8"/>
  <path d="M18 7L9 11v8c0 5.25 3.85 10.16 9 11.35C23.15 29.16 27 24.25 27 19v-8l-9-4z"
        fill="white" fill-opacity="0.15"/>
  <path d="M18 7L9 11v8c0 5.25 3.85 10.16 9 11.35C23.15 29.16 27 24.25 27 19v-8l-9-4z"
        stroke="white" stroke-width="1.5" stroke-linejoin="round"/>
  <path d="M14 18l2.8 2.8L22.5 15" stroke="white" stroke-width="2"
        stroke-linecap="round" stroke-linejoin="round"/>
</svg>"""


# ── Shared helpers ────────────────────────────────────────────────────────────
def _topnav(name):
    initial = name[:1].upper() if name else "T"
    st.markdown(f"""
<style>
.ttn{{display:flex;align-items:center;justify-content:space-between;
  padding:0.9rem 0;border-bottom:1px solid #E2E8F0;margin-bottom:1.75rem;}}
.ttn-brand{{display:flex;align-items:center;gap:10px;}}
.ttn-brand .wm{{font-family:'Inter',sans-serif;font-size:0.97rem;font-weight:800;
  color:#5B5FF8;letter-spacing:-0.03em;}}
.ttn-right{{display:flex;align-items:center;gap:12px;}}
.ttn-av{{width:36px;height:36px;border-radius:50%;
  background:linear-gradient(135deg,#5B5FF8,#7C3AED);color:#fff;font-size:0.8rem;
  font-weight:800;display:flex;align-items:center;justify-content:center;
  font-family:'Inter',sans-serif;flex-shrink:0;}}
.ttn-uname{{font-size:0.85rem;font-weight:600;color:#0F172A;
  font-family:'Inter',sans-serif;display:block;}}
.ttn-urole{{font-size:0.72rem;color:#94A3B8;font-family:'Inter',sans-serif;display:block;}}
</style>
<div class="ttn">
  <div class="ttn-brand">{_LOGO}<span class="wm">SmartAttend</span></div>
  <div class="ttn-right">
    <div class="ttn-av">{initial}</div>
    <div><span class="ttn-uname">{name}</span><span class="ttn-urole">Teacher</span></div>
  </div>
</div>
""", unsafe_allow_html=True)


def _sec(title, sub=""):
    sub_html = (f'<p style="margin:4px 0 0;font-size:0.8rem;color:#64748B;'
                f'font-family:Inter,sans-serif;">{sub}</p>') if sub else ""
    st.markdown(
        f'<div style="margin-bottom:1rem;">'
        f'<h2 style="margin:0;font-size:1.08rem;font-weight:700;color:#0F172A;'
        f'font-family:Inter,sans-serif;letter-spacing:-0.02em;">{title}</h2>'
        f'{sub_html}</div>',
        unsafe_allow_html=True,
    )


def _empty(emoji, title, subtitle):
    st.markdown(f"""
<div style="background:#fff;border:2px dashed #E2E8F0;border-radius:14px;
     padding:3rem 2rem;text-align:center;">
  <div style="font-size:2rem;margin-bottom:10px;">{emoji}</div>
  <div style="font-size:0.9rem;font-weight:600;color:#334155;
       font-family:'Inter',sans-serif;margin-bottom:5px;">{title}</div>
  <div style="font-size:0.8rem;color:#94A3B8;font-family:'Inter',sans-serif;">{subtitle}</div>
</div>""", unsafe_allow_html=True)


def _stat_cards(n_sub, n_stu, n_sess):
    st.markdown(f"""
<style>
.ttsc{{display:grid;grid-template-columns:repeat(3,1fr);gap:14px;margin-bottom:1.75rem;}}
.ttsc-card{{background:#fff;border:1px solid #E2E8F0;border-radius:14px;
  padding:1.2rem 1.35rem;position:relative;overflow:hidden;
  transition:box-shadow 0.2s,transform 0.2s;}}
.ttsc-card:hover{{box-shadow:0 6px 20px rgba(0,0,0,0.06);transform:translateY(-2px);}}
.ttsc-card::after{{content:'';position:absolute;bottom:0;left:0;right:0;height:3px;}}
.ttsc-card.t1::after{{background:#5B5FF8;}}
.ttsc-card.t2::after{{background:#06B6D4;}}
.ttsc-card.t3::after{{background:#7C3AED;}}
.ttsc-icon{{font-size:1.2rem;margin-bottom:10px;display:block;}}
.ttsc-lbl{{font-size:0.67rem;font-weight:700;text-transform:uppercase;
  letter-spacing:0.07em;color:#94A3B8;font-family:'Inter',sans-serif;margin-bottom:5px;}}
.ttsc-val{{font-size:1.6rem;font-weight:900;letter-spacing:-0.04em;
  font-family:'Inter',sans-serif;color:#0F172A;line-height:1;}}
.ttsc-sub{{font-size:0.7rem;color:#94A3B8;font-family:'Inter',sans-serif;margin-top:4px;}}
@media(max-width:600px){{.ttsc{{grid-template-columns:1fr 1fr;}}}}
</style>
<div class="ttsc">
  <div class="ttsc-card t1">
    <span class="ttsc-icon">📚</span>
    <div class="ttsc-lbl">Subjects</div>
    <div class="ttsc-val">{n_sub}</div>
    <div class="ttsc-sub">managed</div>
  </div>
  <div class="ttsc-card t2">
    <span class="ttsc-icon">🎓</span>
    <div class="ttsc-lbl">Total Students</div>
    <div class="ttsc-val">{n_stu}</div>
    <div class="ttsc-sub">enrolled across subjects</div>
  </div>
  <div class="ttsc-card t3">
    <span class="ttsc-icon">📋</span>
    <div class="ttsc-lbl">Attendance Sessions</div>
    <div class="ttsc-val">{n_sess}</div>
    <div class="ttsc-sub">recorded</div>
  </div>
</div>
""", unsafe_allow_html=True)


def _tab_nav():
    tabs = {
        "take_attendance":    ("📷", "Take Attendance"),
        "manage_subjects":    ("📚", "Subjects"),
        "attendance_records": ("📊", "Analytics & Records"),
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

    # Action row
    a1, a2, _ = st.columns([1, 1, 4])
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

    all_sub    = get_teacher_subjects(teacher_id)
    n_stu      = sum(s.get("total_students", 0) for s in all_sub)
    n_sess     = sum(s.get("total_classes",  0) for s in all_sub)
    _stat_cards(len(all_sub), n_stu, n_sess)

    # Quick actions band
    st.markdown("""
<div style="background:linear-gradient(135deg,#5B5FF8 0%,#7C3AED 100%);
     border-radius:14px;padding:1.25rem 1.5rem;margin-bottom:1rem;">
  <div style="font-size:0.9rem;font-weight:700;color:#fff;
       font-family:'Inter',sans-serif;margin-bottom:3px;">Quick Actions</div>
  <div style="font-size:0.76rem;color:rgba(255,255,255,0.62);
       font-family:'Inter',sans-serif;">Most-used tools</div>
</div>""", unsafe_allow_html=True)

    q1, q2, q3, q4 = st.columns(4)
    with q1:
        if st.button("📷  Take Attendance", type="primary", use_container_width=True):
            st.session_state.current_teacher_tab = "take_attendance"
            st.rerun()
    with q2:
        if st.button("📚  New Subject", type="secondary", use_container_width=True):
            create_subject_dialog(teacher_id)
    with q3:
        if st.button("📊  Analytics", type="secondary", use_container_width=True):
            st.session_state.current_teacher_tab = "attendance_records"
            st.rerun()
    with q4:
        if st.button("🎙  Voice Mode", type="secondary", use_container_width=True):
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
        _tab_analytics()

    footer_dashboard()


# ── Tab: Take Attendance ──────────────────────────────────────────────────────
def _tab_attendance():
    teacher_id = st.session_state.teacher_data["teacher_id"]
    _sec("Take AI Attendance",
         "Upload classroom photos to automatically mark attendance using facial recognition.")

    if "attendance_images" not in st.session_state:
        st.session_state.attendance_images = []

    subjects = get_teacher_subjects(teacher_id)
    if not subjects:
        _empty("📭", "No subjects yet", "Go to Subjects tab and create your first subject.")
        return

    subject_options = {f"{s['name']}  ·  {s['subject_code']}": s["subject_id"]
                       for s in subjects}

    c1, c2 = st.columns([3, 1], vertical_alignment="bottom")
    with c1:
        sel = st.selectbox("Select Subject", options=list(subject_options.keys()))
    with c2:
        if st.button("＋ Add Photos", type="primary", use_container_width=True):
            add_photos_dialog()

    sel_id = subject_options[sel]

    if st.session_state.attendance_images:
        _sec(f"Uploaded Photos ({len(st.session_state.attendance_images)})")
        gcols = st.columns(4)
        for idx, img in enumerate(st.session_state.attendance_images):
            with gcols[idx % 4]:
                st.image(img, use_container_width=True, caption=f"Photo {idx+1}")

    st.markdown('<div style="height:6px"></div>', unsafe_allow_html=True)
    has = bool(st.session_state.attendance_images)
    b1, b2, b3 = st.columns(3)

    with b1:
        if st.button("🗑  Clear All", type="secondary", use_container_width=True,
                     disabled=not has):
            st.session_state.attendance_images = []
            st.rerun()
    with b2:
        if st.button("🔍  Run Face Analysis", type="primary", use_container_width=True,
                     disabled=not has):
            with st.spinner("Scanning classroom photos with AI…"):
                det_map = {}
                for idx, img in enumerate(st.session_state.attendance_images):
                    img_np = np.array(img.convert("RGB"))
                    det, _, _ = predict_attendance(img_np)
                    if det:
                        for sid in det.keys():
                            det_map.setdefault(int(sid), []).append(f"Photo {idx+1}")

                enr = supabase.table("subject_students").select("*, students(*)").eq(
                    "subject_id", sel_id).execute()
                enrolled = enr.data
                if not enrolled:
                    st.warning("No students enrolled in this subject.")
                else:
                    results, logs = [], []
                    ts = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
                    for node in enrolled:
                        stu     = node["students"]
                        sources = det_map.get(int(stu["student_id"]), [])
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
        if st.button("🎙  Voice Attendance", type="secondary",
                     use_container_width=True):
            voice_attendance_dialog(sel_id)


# ── Tab: Subjects ─────────────────────────────────────────────────────────────
def _tab_subjects():
    teacher_id = st.session_state.teacher_data["teacher_id"]
    h1, h2 = st.columns([3, 1], vertical_alignment="center")
    with h1:
        _sec("Your Subjects", "Manage subjects and share QR join codes with students.")
    with h2:
        if st.button("＋ New Subject", type="primary", use_container_width=True):
            create_subject_dialog(teacher_id)

    subjects = get_teacher_subjects(teacher_id)
    if not subjects:
        _empty("📂", "No subjects yet", 'Click "+ New Subject" to create your first subject.')
        return

    cols = st.columns(2, gap="medium")
    for i, sub in enumerate(subjects):
        def _mk(s):
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
                footer_callback=_mk(sub),
                card_index=i,
            )


# ── Tab: Analytics & Records (with Low Attendance Alerts) ────────────────────
def _tab_analytics():
    teacher_id = st.session_state.teacher_data["teacher_id"]
    records    = get_attendance_for_teacher(teacher_id)

    if not records:
        _empty("📋", "No records yet",
               "Take your first attendance session to see analytics here.")
        return

    data = []
    for r in records:
        ts = r.get("timestamp")
        data.append({
            "ts_group":     ts.split(".")[0] if ts else None,
            "Time":         datetime.fromisoformat(ts).strftime("%d %b %Y  %I:%M %p") if ts else "N/A",
            "Subject":      r["subjects"]["name"],
            "Subject Code": r["subjects"]["subject_code"],
            "student_id":   r.get("student_id"),
            "is_present":   bool(r.get("is_present", False)),
        })

    df = pd.DataFrame(data)

    summary = (
        df.groupby(["ts_group", "Time", "Subject", "Subject Code"])
        .agg(Present=("is_present", "sum"), Total=("is_present", "count"))
        .reset_index()
    )
    summary["Rate %"]    = (summary["Present"] / summary["Total"] * 100).round(1)
    summary["Attendance"]= ("✅ " + summary["Present"].astype(str)
                             + " / " + summary["Total"].astype(str))

    # ── Low attendance alerts ──────────────────────────────────────────────
    all_sub = get_teacher_subjects(teacher_id)
    sub_names = {s["subject_id"]: s["name"] for s in all_sub}

    # Per-student per-subject attendance
    stu_sub = (
        df.groupby(["student_id", "Subject"])
        .agg(Present=("is_present", "sum"), Total=("is_present", "count"))
        .reset_index()
    )
    stu_sub["Rate %"] = (stu_sub["Present"] / stu_sub["Total"] * 100).round(1)
    low = stu_sub[stu_sub["Rate %"] < 75].copy()

    if not low.empty:
        # Fetch student names from DB
        try:
            all_stu_res = supabase.table("students").select("student_id, name").execute()
            stu_name_map = {r["student_id"]: r["name"] for r in (all_stu_res.data or [])}
        except Exception:
            stu_name_map = {}

        low["Student"] = low["student_id"].apply(
            lambda x: stu_name_map.get(x, f"ID {x}")
        )

        alert_count = len(low)
        st.markdown(f"""
<div style="background:#FFF5F5;border:1px solid #FECACA;border-radius:14px;
     padding:1.25rem 1.5rem;margin-bottom:1.75rem;">
  <div style="display:flex;align-items:center;gap:10px;margin-bottom:10px;">
    <div style="width:32px;height:32px;border-radius:50%;background:#FEE2E2;
         display:flex;align-items:center;justify-content:center;
         font-size:0.9rem;flex-shrink:0;">⚠️</div>
    <div>
      <div style="font-size:0.88rem;font-weight:700;color:#991B1B;
           font-family:'Inter',sans-serif;">
        {alert_count} Low-Attendance Student{'s' if alert_count!=1 else ''} Detected
      </div>
      <div style="font-size:0.75rem;color:#B91C1C;font-family:'Inter',sans-serif;
           margin-top:2px;">
        Students with attendance below 75% — action required
      </div>
    </div>
  </div>
""", unsafe_allow_html=True)

        display_low = low[["Student", "Subject", "Present", "Total", "Rate %"]].copy()
        display_low = display_low.rename(columns={"Present": "Attended", "Total": "Classes"})
        st.dataframe(display_low.sort_values("Rate %"),
                     use_container_width=True, hide_index=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # ── Session records table ──────────────────────────────────────────────
    _sec("Attendance Records", "Session-by-session logs sorted by most recent.")
    display = summary.sort_values("ts_group", ascending=False)[
        ["Time", "Subject", "Subject Code", "Attendance", "Rate %"]
    ]
    st.dataframe(display, use_container_width=True, hide_index=True)

    # ── Attendance rate trend ──────────────────────────────────────────────
    st.markdown('<div style="height:1rem"></div>', unsafe_allow_html=True)
    _sec("Attendance Rate Trend", "Per-session attendance % over time")
    if len(summary) >= 2:
        chart_df = (summary.sort_values("ts_group")[["Time", "Rate %"]]
                    .set_index("Time"))
        st.line_chart(chart_df, use_container_width=True, height=220)
    else:
        st.info("Run more sessions to see the trend chart.")

    # ── Per-subject average ──────────────────────────────────────────────
    st.markdown('<div style="height:0.5rem"></div>', unsafe_allow_html=True)
    _sec("Average Attendance by Subject")
    sub_avg = (
        summary.groupby("Subject")["Rate %"]
        .mean()
        .reset_index()
        .rename(columns={"Rate %": "Avg Attendance %"})
        .sort_values("Avg Attendance %", ascending=False)
        .set_index("Subject")
    )
    if not sub_avg.empty:
        st.bar_chart(sub_avg, use_container_width=True, height=220)


# ════════════════════════════════════════════════════════════════════════════
# AUTH SCREENS
# ════════════════════════════════════════════════════════════════════════════
_AUTH_CSS = """
<style>
.tal{{background:linear-gradient(145deg,#0F172A 0%,#1E293B 60%,#334155 100%);
  border-radius:20px;padding:3rem 2.5rem;display:flex;flex-direction:column;
  justify-content:center;min-height:500px;}}
.tal h2{{font-size:1.5rem!important;font-weight:900!important;color:#fff!important;
  letter-spacing:-0.04em!important;margin-bottom:0.75rem!important;}}
.tal p{{font-size:0.85rem!important;color:rgba(255,255,255,0.62)!important;
  line-height:1.65!important;margin-bottom:1.75rem!important;}}
.tal ul{{list-style:none;padding:0;margin:0;}}
.tal li{{font-size:0.8rem;color:rgba(255,255,255,0.8);font-family:'Inter',sans-serif;
  margin-bottom:10px;display:flex;align-items:center;gap:10px;}}
.tal-ck{{width:20px;height:20px;border-radius:50%;background:rgba(91,95,248,0.4);
  display:flex;align-items:center;justify-content:center;font-size:0.62rem;
  color:#fff;flex-shrink:0;}}
.tar{{background:#fff;border:1px solid #E2E8F0;border-radius:20px;padding:2.25rem 2rem;}}
.tar-logo{{display:flex;align-items:center;gap:10px;margin-bottom:1.5rem;}}
.tar-logo .wm{{font-family:'Inter',sans-serif;font-size:1rem;font-weight:800;
  color:#5B5FF8;letter-spacing:-0.03em;}}
</style>"""


def teacher_screen_login():
    st.markdown(_AUTH_CSS, unsafe_allow_html=True)
    bc, _ = st.columns([1, 4])
    with bc:
        if st.button("← Home", type="secondary"):
            st.session_state["login_type"] = None
            st.rerun()
    st.markdown('<div style="height:8px"></div>', unsafe_allow_html=True)

    lc, rc = st.columns([1, 1.1], gap="large")
    with lc:
        st.markdown("""
<div class="tal">
  <h2>Teacher Login</h2>
  <p>Sign in to manage subjects, take AI-powered attendance, and view analytics.</p>
  <ul>
    <li><span class="tal-ck">✓</span> AI face recognition attendance</li>
    <li><span class="tal-ck">✓</span> Track all students across subjects</li>
    <li><span class="tal-ck">✓</span> Generate and share QR join codes</li>
    <li><span class="tal-ck">✓</span> Analytics and attendance trend charts</li>
    <li><span class="tal-ck">✓</span> Low-attendance student alerts</li>
  </ul>
</div>""", unsafe_allow_html=True)

    with rc:
        st.markdown(f"""
<div class="tar">
  <div class="tar-logo">{_AUTH_LOGO}<span class="wm">SmartAttend</span></div>
  <div style="font-size:1.2rem;font-weight:800;color:#0F172A;letter-spacing:-0.03em;
       font-family:'Inter',sans-serif;margin-bottom:4px;">Sign in</div>
  <div style="font-size:0.82rem;color:#64748B;font-family:'Inter',sans-serif;
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


def teacher_screen_register():
    st.markdown(_AUTH_CSS, unsafe_allow_html=True)
    bc, _ = st.columns([1, 4])
    with bc:
        if st.button("← Login", type="secondary"):
            st.session_state.teacher_login_type = "login"
            st.rerun()
    st.markdown('<div style="height:8px"></div>', unsafe_allow_html=True)

    lc, rc = st.columns([1, 1.1], gap="large")
    with lc:
        st.markdown("""
<div class="tal">
  <h2>Create Account</h2>
  <p>Set up your SmartAttend teacher profile in under a minute.</p>
  <ul>
    <li><span class="tal-ck">✓</span> Free to use for all teachers</li>
    <li><span class="tal-ck">✓</span> Create unlimited subjects</li>
    <li><span class="tal-ck">✓</span> No credit card required</li>
    <li><span class="tal-ck">✓</span> Secure password hashing</li>
  </ul>
</div>""", unsafe_allow_html=True)

    with rc:
        st.markdown(f"""
<div class="tar">
  <div class="tar-logo">{_AUTH_LOGO}<span class="wm">SmartAttend</span></div>
  <div style="font-size:1.2rem;font-weight:800;color:#0F172A;letter-spacing:-0.03em;
       font-family:'Inter',sans-serif;margin-bottom:4px;">Create Teacher Account</div>
  <div style="font-size:0.82rem;color:#64748B;font-family:'Inter',sans-serif;
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


def teacher_screen_forgot_password():
    st.markdown(_AUTH_CSS, unsafe_allow_html=True)
    bc, _ = st.columns([1, 4])
    with bc:
        if st.button("← Login", type="secondary"):
            st.session_state.teacher_login_type = "login"
            for k in ["forgot_step","fp_otp","fp_mobile_entered","fp_otp_time"]:
                st.session_state.pop(k, None)
            st.rerun()
    st.markdown('<div style="height:8px"></div>', unsafe_allow_html=True)

    _, ctr, __ = st.columns([1, 2, 1])
    with ctr:
        st.markdown(f"""
<div class="tar">
  <div class="tar-logo">{_AUTH_LOGO}<span class="wm">SmartAttend</span></div>
  <div style="font-size:1.2rem;font-weight:800;color:#0F172A;letter-spacing:-0.03em;
       font-family:'Inter',sans-serif;margin-bottom:4px;">Reset Password</div>
  <div style="font-size:0.82rem;color:#64748B;font-family:'Inter',sans-serif;
       margin-bottom:1.25rem;">We'll send an OTP to your registered mobile number.</div>
""", unsafe_allow_html=True)

        if "forgot_step" not in st.session_state:
            st.session_state.forgot_step = "enter_mobile"
        step = st.session_state.forgot_step
        _steps = ["Enter Mobile", "Verify OTP", "New Password"]
        _keys  = ["enter_mobile", "verify_otp", "reset_password"]
        cur_i  = _keys.index(step) if step in _keys else 0
        bar    = '<div style="display:flex;gap:5px;margin-bottom:1.25rem;">'
        for i, s in enumerate(_steps):
            done   = i < cur_i
            active = i == cur_i
            bg  = "#5B5FF8" if active else ("#22C55E" if done else "#E2E8F0")
            clr = "#fff"    if (active or done) else "#94A3B8"
            bar += (f'<div style="flex:1;background:{bg};color:{clr};border-radius:6px;'
                    f'padding:6px;text-align:center;font-size:0.7rem;font-weight:700;'
                    f'font-family:Inter,sans-serif;">{"✓ " if done else ""}{s}</div>')
        bar += "</div>"
        st.markdown(bar, unsafe_allow_html=True)

        if step == "enter_mobile":
            mob = st.text_input("Registered Mobile", placeholder="+91 9876543210",
                                key="fp_mob")
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
                    ok = reset_teacher_password(
                        st.session_state.get("fp_mobile_entered"), np_
                    )
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


# ── Auth helpers ──────────────────────────────────────────────────────────────
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
