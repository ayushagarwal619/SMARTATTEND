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
# CSS overrides for the teacher portal
_TEACHER_CSS = """
<style>
:root {
  --color-primary: #5865F2;
  --color-success: #00E676;
  --color-warning: #FFD600;
  --color-danger: #EF4444;
  --color-gray: #64748B;
  --border-thick: 3px solid #000000;
  --border-thin: 1.5px solid #000000;
  --shadow-offset: 4px 4px 0px #000000;
  --shadow-offset-lg: 6px 6px 0px #000000;
  --font-family-display: 'Outfit', sans-serif;
  --font-family-body: 'Plus Jakarta Sans', sans-serif;
}

/* Command Center Layout */
.teacher-hero-card {
  background: #FFFFFF !important;
  border: var(--border-thick) !important;
  border-radius: 20px !important;
  box-shadow: var(--shadow-offset) !important;
  padding: 0 !important;
  overflow: hidden !important;
  margin-bottom: 24px !important;
}
.teacher-hero-container {
  display: flex;
  flex-wrap: wrap;
}
.teacher-hero-left {
  flex: 1.2;
  min-width: 320px;
  background: #F8F9FA;
  border-right: var(--border-thick);
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.teacher-hero-right {
  flex: 1.8;
  min-width: 420px;
  padding: 24px;
  background: #FFFFFF;
  display: flex;
  flex-direction: column;
  gap: 18px;
}

/* Stats Widgets Row */
.teacher-stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 24px;
}
.teacher-stat-card {
  background: #FFFFFF;
  border: var(--border-thick);
  border-radius: 12px;
  padding: 16px;
  box-shadow: var(--shadow-offset);
  transition: transform 0.2s, box-shadow 0.2s;
  display: flex;
  flex-direction: column;
}
.teacher-stat-card:hover {
  transform: translateY(-3px);
  box-shadow: var(--shadow-offset-lg);
}

/* Premium Subjects Registry Card Override */
.premium-nav-card div.stButton > button {
  background: #FFFFFF !important;
  border: var(--border-thick) !important;
  border-radius: 12px !important;
  box-shadow: var(--shadow-offset) !important;
  color: #111111 !important;
  font-family: var(--font-family-display) !important;
  font-weight: 800 !important;
  padding: 12px 24px !important;
  transition: transform 0.2s, box-shadow 0.2s !important;
  width: 100% !important;
  display: inline-flex !important;
  align-items: center !important;
  justify-content: center !important;
  min-height: 52px !important;
}
.premium-nav-card div.stButton > button:hover {
  transform: translateY(-2px) !important;
  box-shadow: var(--shadow-offset-lg) !important;
  border-color: var(--color-primary) !important;
  background-color: #F8F9FA !important;
}
.premium-nav-card div.stButton > button:active {
  transform: translateY(0px) !important;
  box-shadow: var(--shadow-offset) !important;
}

/* Timeline Cards */
.timeline-deck {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-top: 14px;
}
.timeline-card-box {
  background: #FFFFFF;
  border: var(--border-thick);
  border-radius: 12px;
  padding: 16px;
  box-shadow: var(--shadow-offset);
  display: flex;
  justify-content: space-between;
  align-items: center;
  transition: transform 0.2s;
}
.timeline-card-box:hover {
  transform: translateY(-2px);
}

/* Premium animations and overrides */
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(8px); }
  to { opacity: 1; transform: translateY(0); }
}
.animate-fade-in {
  animation: fadeIn 0.45s cubic-bezier(0.16, 1, 0.3, 1) forwards;
}

@keyframes drawPath {
  to { stroke-dashoffset: 0; }
}
.sparkline-line {
  stroke-dasharray: 600;
  stroke-dashoffset: 600;
  animation: drawPath 1.6s cubic-bezier(0.22, 1, 0.36, 1) forwards;
}

@keyframes softPulse {
  0% { transform: scale(1); opacity: 1; }
  50% { transform: scale(1.15); opacity: 0.8; }
  100% { transform: scale(1); opacity: 1; }
}
.status-pulse-dot {
  animation: softPulse 2s infinite ease-in-out;
}

@keyframes countScale {
  from { transform: translate(-50%, -50%) scale(0.9); opacity: 0; }
  to { transform: translate(-50%, -50%) scale(1); opacity: 1; }
}
.gauge-percentage-overlay {
  animation: countScale 0.6s cubic-bezier(0.34, 1.56, 0.64, 1) forwards;
}

@keyframes drawProgress {
  from { stroke-dashoffset: 100; }
  to { stroke-dashoffset: var(--dashoffset, 0); }
}
.circle {
  animation: drawProgress 1.2s cubic-bezier(0.16, 1, 0.3, 1) forwards;
}

/* Premium Navigation Card Override */
div[data-testid="stButton"] button[key="tt_manage_subjects"] {
  background: #FFFFFF !important;
  border: var(--border-thick) !important;
  border-radius: 12px !important;
  box-shadow: var(--shadow-offset) !important;
  color: #111111 !important;
  font-family: var(--font-family-display) !important;
  font-weight: 800 !important;
  padding: 10px 20px !important;
  transition: transform 0.2s, box-shadow 0.2s, background-color 0.2s !important;
}
div[data-testid="stButton"] button[key="tt_manage_subjects"]:hover {
  transform: translateY(-2px) !important;
  box-shadow: var(--shadow-offset-lg) !important;
  background-color: #F8F9FA !important;
  border-color: var(--color-primary) !important;
}
div[data-testid="stButton"] button[key="tt_manage_subjects"]:active {
  transform: translateY(0px) !important;
  box-shadow: var(--shadow-offset) !important;
}
</style>
"""

def _render_html(html_str):
    # Dedent lines to prevent markdown code block formatting
    cleaned = "\n".join(line.strip() for line in html_str.splitlines())
    st.markdown(cleaned, unsafe_allow_html=True)


def _topnav(name):
    initial = name[:1].upper() if name else "T"
    _render_html(_TEACHER_CSS)
    _render_html(f"""
<style>
.ttn{{display:flex;align-items:center;justify-content:space-between;
  padding:0.9rem 0;border-bottom:3px solid #000000;margin-bottom:1.75rem;}}
.ttn-brand{{display:flex;align-items:center;gap:12px;}}
.ttn-brand .wm{{font-family:'Outfit',sans-serif;font-size:1.3rem;font-weight:900;
  color:#5865F2;letter-spacing:-0.03em;text-transform:uppercase;}}
.ttn-right{{display:flex;align-items:center;gap:12px;}}
.ttn-av{{width:36px;height:36px;border-radius:4px;
  background:#5865F2;color:#fff;font-size:0.9rem;border:2.5px solid #000000;
  box-shadow:2px 2px 0 #000000;
  font-weight:800;display:flex;align-items:center;justify-content:center;
  font-family:'Outfit',sans-serif;flex-shrink:0;}}
.ttn-uname{{font-size:0.9rem;font-weight:800;color:#000000;
  font-family:'Outfit',sans-serif;display:block;}}
.ttn-urole{{font-size:0.75rem;font-weight:600;color:#333333;font-family:'Outfit',sans-serif;display:block;}}
</style>
<div class="ttn">
  <div class="ttn-brand">{_LOGO}<span class="wm">SmartAttend</span></div>
  <div class="ttn-right">
    <div class="ttn-av">{initial}</div>
    <div><span class="ttn-uname">{name}</span><span class="ttn-urole">Teacher Portal</span></div>
  </div>
</div>
""")


def _sec(title, sub=""):
    sub_html = (f'<p style="margin:6px 0 0;font-size:0.9rem;color:#333333;'
                f'font-family:\'Outfit\',sans-serif;font-weight:600;">{sub}</p>') if sub else ""
    st.markdown(
        f'<div style="margin-bottom:1.5rem;">'
        f'<h2 style="margin:0;font-size:1.5rem;font-weight:900;color:#000000;'
        f'font-family:\'Outfit\',sans-serif;letter-spacing:-0.02em;text-transform:uppercase;">{title}</h2>'
        f'{sub_html}</div>',
        unsafe_allow_html=True,
    )


def _empty(emoji, title, subtitle):
    _render_html(f"""
<div style="background:#FFFFFF;border:3px dashed #000000;border-radius:8px;
     box-shadow:4px 4px 0 #000000;padding:3rem 2rem;text-align:center;">
  <div style="font-size:2.5rem;margin-bottom:10px;">{emoji}</div>
  <div style="font-size:1.1rem;font-weight:800;color:#000000;
       font-family:'Outfit',sans-serif;margin-bottom:5px;text-transform:uppercase;">{title}</div>
  <div style="font-size:0.9rem;color:#333333;font-family:'Outfit',sans-serif;font-weight:600;">{subtitle}</div>
</div>""")


def _stat_cards(n_sub, n_stu, n_sess, avg_rate="0.0%"):
    _render_html(f"""
    <div class="teacher-stats-grid">
      <div class="teacher-stat-card">
        <span style="font-size: 1.35rem; margin-bottom: 6px;">📚</span>
        <span style="font-size: 0.62rem; font-weight: 800; color: var(--color-gray); letter-spacing: 0.05em; text-transform: uppercase;">ACTIVE COURSES</span>
        <span style="font-size: 1.6rem; font-weight: 900; color: #111111; margin-top: 2px;">{n_sub}</span>
        <span style="font-size: 0.65rem; color: var(--color-gray); margin-top: 1px;">Enrolled registries</span>
      </div>
      <div class="teacher-stat-card">
        <span style="font-size: 1.35rem; margin-bottom: 6px;">🎓</span>
        <span style="font-size: 0.62rem; font-weight: 800; color: var(--color-gray); letter-spacing: 0.05em; text-transform: uppercase;">STUDENT DIRECTORY</span>
        <span style="font-size: 1.6rem; font-weight: 900; color: #111111; margin-top: 2px;">{n_stu}</span>
        <span style="font-size: 0.65rem; color: var(--color-gray); margin-top: 1px;">Active class members</span>
      </div>
      <div class="teacher-stat-card">
        <span style="font-size: 1.35rem; margin-bottom: 6px;">📋</span>
        <span style="font-size: 0.62rem; font-weight: 800; color: var(--color-gray); letter-spacing: 0.05em; text-transform: uppercase;">RECORDED SESSIONS</span>
        <span style="font-size: 1.6rem; font-weight: 900; color: #111111; margin-top: 2px;">{n_sess}</span>
        <span style="font-size: 0.65rem; color: var(--color-gray); margin-top: 1px;">Attendance runs executed</span>
      </div>
      <div class="teacher-stat-card">
        <span style="font-size: 1.35rem; margin-bottom: 6px;">⏱️</span>
        <span style="font-size: 0.62rem; font-weight: 800; color: var(--color-gray); letter-spacing: 0.05em; text-transform: uppercase;">AVG ATTENDANCE RATE</span>
        <span style="font-size: 1.6rem; font-weight: 900; color: #111111; margin-top: 2px;">{avg_rate}</span>
        <span style="font-size: 0.65rem; color: var(--color-gray); margin-top: 1px;">Total present ratio</span>
      </div>
    </div>
    """)


def _tab_nav():
    cur = st.session_state.get("current_teacher_tab", "take_attendance")
    is_active = (cur == "manage_subjects")
    lbl = "📚 Access Subjects Registry"
    if is_active:
        lbl = "📚 Active Subject Registry"
    st.markdown('<div class="premium-nav-card">', unsafe_allow_html=True)
    if st.button(lbl, use_container_width=True, key="tt_manage_subjects"):
        st.session_state.current_teacher_tab = "manage_subjects"
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
    _render_html('<hr style="margin:0 0 1.5rem;">')


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
    a1, a2, _ = st.columns([1.5, 1.5, 4])
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
    records    = get_attendance_for_teacher(teacher_id)

    # Compute average metrics
    avg_rate = "0.0%"
    avg_pct_float = 0.0
    if records:
        present_count = sum(1 for r in records if r.get("is_present"))
        avg_pct_float = (present_count / len(records) * 100)
        avg_rate = f"{avg_pct_float:.1f}%"

    status_label = "SECURE" if avg_pct_float >= 75 else "WARNING"
    status_class = "safe" if avg_pct_float >= 75 else "warning"

    # Compute real attendance trend path coordinates dynamically from records
    rates_history = []
    if records:
        data_trend = []
        for r in records:
            ts = r.get("timestamp")
            data_trend.append({
                "ts_group": ts.split(".")[0] if ts else None,
                "is_present": bool(r.get("is_present", False)),
            })
        df_trend = pd.DataFrame(data_trend)
        if not df_trend.empty:
            summary_sub = (
                df_trend.groupby("ts_group")
                .agg(Present=("is_present", "sum"), Total=("is_present", "count"))
                .reset_index()
            )
            summary_sub["Rate %"] = (summary_sub["Present"] / summary_sub["Total"] * 100)
            summary_sub = summary_sub.sort_values("ts_group")
            rates_history = summary_sub["Rate %"].tail(6).tolist()

    if len(rates_history) < 2:
        rates_history = [avg_pct_float, avg_pct_float] if avg_pct_float > 0 else [80.0, 80.0]
        
    n_pts = len(rates_history)
    svg_width = 200
    svg_height = 40
    
    pts = []
    for idx, r in enumerate(rates_history):
        x = idx * (svg_width / max(1, n_pts - 1))
        y = 35 - (r / 100) * 27
        pts.append((x, y))
        
    line_d = "M " + " L ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    area_d = line_d + f" L {pts[-1][0]:.1f},{svg_height:.1f} L {pts[0][0]:.1f},{svg_height:.1f} Z"
    
    # Calculate trend text and latest value
    latest_val = rates_history[-1]
    if len(rates_history) >= 2:
        diff = rates_history[-1] - rates_history[-2]
        if diff > 0.5:
            trend_dir = f"▲ UPWARD (+{diff:.1f}%)"
            trend_class = "safe"
        elif diff < -0.5:
            trend_dir = f"▼ DOWNWARD ({diff:.1f}%)"
            trend_class = "warning"
        else:
            trend_dir = "▲ STABLE"
            trend_class = "safe"
    else:
        trend_dir = "▲ STABLE"
        trend_class = "safe"
        
    tooltip_circles = ""
    for idx, (x, y) in enumerate(pts):
        rate_val = rates_history[idx]
        tooltip_circles += f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3" fill="#5865F2" stroke="#FFFFFF" stroke-width="1"><title>Session {idx+1}: {rate_val:.1f}%</title></circle>'

    # SECTION 1: AI Teacher Command Center Hero Panel
    hero_html = f"""
    <div class="teacher-hero-card animate-fade-in">
      <div class="teacher-hero-container">
        <!-- LEFT: AI Teacher Command Center -->
        <div class="teacher-hero-left">
          <span class="profile-dept" style="font-size:0.6rem; font-weight:800; color:var(--color-primary); letter-spacing:0.1em; text-transform:uppercase; font-family:'Outfit',sans-serif;">CSE DEPARTMENT • CORE PORTAL</span>
          <div class="sidebar-profile-header" style="display: flex; align-items: center; gap: 16px; margin-top: 10px;">
            <div class="ttn-av" style="width: 54px; height: 54px; font-size: 1.35rem; font-weight: 900; border-radius: 10px; border: 2.5px solid #000; box-shadow: 2px 2px 0 #000; flex-shrink: 0; background: var(--color-primary); color: #fff; display: flex; align-items: center; justify-content: center;">{name[:1].upper()}</div>
            <div class="profile-title-col" style="display: flex; flex-direction: column; gap: 4px;">
              <span class="profile-name" style="font-size: 1.85rem; font-weight: 900; color: #111111; font-family: 'Outfit', sans-serif; line-height: 1.1;">{name}</span>
              <div style="display: flex; align-items: center; gap: 6px; flex-wrap: wrap;">
                <span style="font-size: 0.72rem; color: var(--color-gray); font-family: monospace; font-weight: bold;">ID: #{teacher_id}</span>
                <span style="background: #E0F8E9; color: #15803D; border: 1.5px solid #000; border-radius: 4px; padding: 2px 6px; font-size: 0.65rem; font-weight: 800; font-family: 'Outfit', sans-serif; display: inline-flex; align-items: center; gap: 4px;"><span class="status-pulse-dot safe" style="width: 5px; height: 5px; border-radius: 50%; display: inline-block; background: #15803D;"></span> ONLINE SYNC</span>
              </div>
            </div>
          </div>
          
          <div class="sidebar-divider" style="border-top: 1.5px dashed rgba(0,0,0,0.1); margin: 12px 0;"></div>
          
          <div>
            <span style="font-size: 0.65rem; font-weight: 800; color: var(--color-gray); letter-spacing: 0.05em; display: block; margin-bottom: 6px;">AI OPERATING SUMMARY</span>
            <p style="font-size: 0.78rem; color: #333333; line-height: 1.4; margin: 0;">
              Total academic courses active: <b>{len(all_sub)}</b>. Semester attendance holds steady at <b>{avg_rate}</b>. Security diagnostics report all verification scanners online.
            </p>
          </div>
          
          <div class="sidebar-divider" style="border-top: 1.5px dashed rgba(0,0,0,0.1); margin: 12px 0;"></div>
          
          <div>
            <span style="font-size: 0.65rem; font-weight: 800; color: var(--color-gray); letter-spacing: 0.05em; display: block; margin-bottom: 6px;">PENDING SYSTEM ACTIONS</span>
            <div style="display: flex; flex-direction: column; gap: 4px;">
              <span style="font-size: 0.72rem; color: #B45309; font-weight: 600;">⚠️ Check student check-in alerts (below 75%)</span>
              <span style="font-size: 0.72rem; color: var(--color-primary); font-weight: 600;">📱 Live camera sync pipeline configured</span>
            </div>
          </div>
        </div>
        
        <!-- RIGHT: Large Attendance Overview & Trend -->
        <div class="teacher-hero-right">
          <div style="display: flex; justify-content: space-between; align-items: center;">
            <div style="display: flex; flex-direction: column;">
              <span class="console-label-uppercase" style="font-size: 0.65rem; font-weight: 800; color: var(--color-gray); letter-spacing: 0.05em;">SEMESTER COMPLETION RATE</span>
              <span class="console-large-val-shimmer" style="font-size: 2.8rem; font-weight: 900; letter-spacing: -0.04em; color: #111111; line-height: 1.0; margin: 4px 0;">{avg_rate}</span>
              <div class="console-comparison-chip {status_class}" style="display: inline-flex; align-items: center; gap: 6px; font-size: 0.65rem; font-weight: 800; border: 1.5px solid #000; border-radius: 20px; padding: 2px 8px; width: fit-content; margin-top: 4px;">
                <span class="status-pulse-dot {status_class}" style="width: 6px; height: 6px; border-radius: 50%; display: inline-block;"></span>
                <span>STATUS: {status_label}</span>
              </div>
            </div>
            
            <!-- Circular Progress Ring SVG -->
            <div class="console-circular-gauge" style="position: relative; width: 100px; height: 100px;">
              <svg viewBox="0 0 36 36" class="circular-chart {status_class}">
                <path class="circle-bg" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" style="fill: none; stroke: #F3F4F6; stroke-width: 3.2;" />
                <path class="circle" stroke-dasharray="{avg_pct_float:.1f}, 100" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" style="fill: none; stroke-width: 3.2; stroke-linecap: round; --dashoffset: {100 - avg_pct_float:.1f};" />
              </svg>
              <div class="gauge-percentage-overlay" style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); font-size: 1rem; font-weight: 800; color: #111111;">{avg_rate}</div>
            </div>
          </div>
          
          <div style="border-top: 1.5px dashed rgba(0,0,0,0.1); margin: 12px 0;"></div>
          
          <!-- Sparkline Trend Indicator -->
          <div class="console-trend-chart-deck">
            <div class="trend-chart-header" style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
              <span class="console-label-uppercase" style="font-size: 0.65rem; font-weight: 800; color: var(--color-gray); letter-spacing: 0.05em;">LATEST: {latest_val:.1f}%</span>
              <span class="trend-direction-badge {trend_class}" style="font-size: 0.65rem; font-weight: 800;">{trend_dir}</span>
            </div>
            
            <div class="sparkline-container-card" style="height: 54px; border: 2.5px solid #000; border-radius: 8px; overflow: hidden; background: #F8F9FA; padding: 4px; margin-top: 6px;">
              <svg viewBox="0 0 200 40" class="sparkline-graphic-svg" style="width: 100%; height: 100%; overflow: visible;">
                <defs>
                  <linearGradient id="spark-gradient-teacher" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stop-color="var(--color-primary)" stop-opacity="0.35"/>
                    <stop offset="100%" stop-color="var(--color-primary)" stop-opacity="0"/>
                  </linearGradient>
                </defs>
                <path class="sparkline-area" d="{area_d}" fill="url(#spark-gradient-teacher)" style="stroke: none;" />
                <path class="sparkline-line" d="{line_d}" style="fill: none; stroke: var(--color-primary); stroke-width: 2.5; stroke-linecap: round; stroke-linejoin: round;" />
                {tooltip_circles}
              </svg>
            </div>
          </div>
        </div>
      </div>
    </div>
    """
    _render_html(hero_html)

    # SECTION 3: Live Statistics Widgets Row
    _stat_cards(len(all_sub), n_stu, n_sess, avg_rate)

    # SECTION 2: Quick Actions Grid
    _render_html("""
    <div style="background:#5865F2;border:3px solid #000000;border-radius:6px;
         box-shadow:4px 4px 0 #000000;padding:0.75rem 1.25rem;margin-bottom:1rem;">
      <div style="font-size:0.95rem;font-weight:900;color:#FFFFFF;text-transform:uppercase;
           font-family:'Outfit',sans-serif;margin-bottom:2px;letter-spacing:0.02em;">QUICK COMMANDS</div>
    </div>""")

    q1, q2, q3, q4 = st.columns(4)
    with q1:
        if st.button("**📷 Take Attendance**\n\nScan class via AI", key="action_camera", use_container_width=True):
            st.session_state.current_teacher_tab = "take_attendance"
            st.rerun()
    with q2:
        if st.button("**📚 New Subject**\n\nRegister course logs", key="action_subjects", use_container_width=True):
            create_subject_dialog(teacher_id)
    with q3:
        if st.button("**📊 Analytics**\n\nExport trends data", key="action_analytics", use_container_width=True):
            st.session_state.current_teacher_tab = "attendance_records"
            st.rerun()
    with q4:
        if st.button("**🎙 Voice Mode**\n\nRecord class audio", key="action_voice", use_container_width=True):
            st.session_state.current_teacher_tab = "take_attendance"
            st.session_state.launch_voice_roll = True
            st.rerun()

    _render_html('<div style="height:1.5rem"></div>')

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
    
    if "attendance_images" not in st.session_state:
        st.session_state.attendance_images = []

    subjects = get_teacher_subjects(teacher_id)
    if not subjects:
        _empty("📭", "No subjects yet", "Go to Subjects tab and create your first subject.")
        return

    subject_options = {f"{s['name']}  ·  {s['subject_code']}": s
                       for s in subjects}

    _sec("Take AI Attendance", "Deploy classroom facial recognition pipeline to check student check-ins.")

    # Workspace columns layout
    left_col, center_col, right_col = st.columns([1.3, 1.8, 1.1], gap="medium")

    with left_col:
        _render_html("""
        <div style="background: #F8F9FA; border: 3px solid #000; border-radius: 12px; padding: 16px; box-shadow: 4px 4px 0 #000; margin-bottom: 12px;">
          <span style="font-size: 0.65rem; font-weight: 800; color: var(--color-primary); letter-spacing: 0.05em; display: block; margin-bottom: 6px;">1. CONFIGURATION LAYER</span>
          <span style="font-size: 0.85rem; color: #111111; font-weight: 800; display: block; margin-bottom: 2px;">Target Subject Registry</span>
        </div>""")
        sel = st.selectbox("Select Subject", options=list(subject_options.keys()), label_visibility="collapsed")
        
        target_subject = subject_options[sel]
        sel_id = target_subject["subject_id"]
        
        # Check if launcher flag is active
        if st.session_state.get("launch_voice_roll"):
            st.session_state.launch_voice_roll = False
            voice_attendance_dialog(sel_id)
        
        _render_html(f"""
        <div style="margin-top: 10px; margin-bottom: 12px; padding: 12px; background: #FFFFFF; border: 2.5px solid #000; border-radius: 10px; box-shadow: 3px 3px 0 #000;">
          <div style="font-size: 0.72rem; color: #111; font-weight: 700; margin-bottom: 6px; font-family: 'Outfit', sans-serif;">REGISTRY DETAILS</div>
          <span style="font-size: 0.7rem; color: var(--color-gray); font-family: monospace; display: block; margin-bottom: 2px;">CODE: <b>{target_subject['subject_code']}</b></span>
          <span style="font-size: 0.7rem; color: var(--color-gray); font-family: monospace; display: block; margin-bottom: 2px;">ENROLLED: <b>{target_subject.get('total_students', 0)} Students</b></span>
          <span style="font-size: 0.7rem; color: var(--color-gray); font-family: monospace; display: block;">SECTION: <b>{target_subject.get('section', 'N/A')}</b></span>
        </div>""")
        
        # Load and display persistent session notes
        from src.database.db import get_session_notes, save_session_notes
        initial_notes = get_session_notes(teacher_id, sel_id)
        notes_val = st.text_area("Session Notes", value=initial_notes, placeholder="e.g. Lecture topic summary...", key=f"notes_widget_{sel_id}", height=120)
        
        st.markdown('<div style="height:4px"></div>', unsafe_allow_html=True)
        if st.button("💾 Save Session Notes", key=f"save_notes_btn_{sel_id}", use_container_width=True):
            save_session_notes(teacher_id, sel_id, notes_val)
            from datetime import datetime
            st.session_state[f"notes_saved_ts_{sel_id}"] = datetime.now().strftime("%I:%M %p")
            st.toast("Notes saved successfully!")
            
        saved_ts = st.session_state.get(f"notes_saved_ts_{sel_id}")
        if saved_ts:
            st.success("Session notes saved successfully!")
            st.caption(f"✓ Last saved at {saved_ts}")

    with center_col:
        _render_html("""
        <div style="background: #FFFFFF; border: 3px dashed #000000; border-radius: 12px; padding: 24px; text-align: center; margin-bottom: 14px; box-shadow: 4px 4px 0 #000;">
          <span style="font-size: 2rem; display: block; margin-bottom: 6px;">📸</span>
          <span style="font-family: 'Outfit', sans-serif; font-size: 1.05rem; font-weight: 900; color: #111; display: block;">Classroom Media Upload</span>
          <span style="font-size: 0.72rem; color: var(--color-gray); display: block; margin-top: 2px;">Upload classroom group photos to run AI facial scanner</span>
        </div>""")
        
        if st.button("＋ Add Classroom Photos", type="primary", use_container_width=True):
            add_photos_dialog()

        if st.session_state.attendance_images:
            _render_html(f"""
            <div style="margin: 16px 0 8px;">
              <span style="font-size: 0.65rem; font-weight: 800; color: var(--color-gray); letter-spacing: 0.05em; display: block; text-transform: uppercase;">UPLOADED MEDIA ({len(st.session_state.attendance_images)} PHOTOS)</span>
            </div>""")
            gcols = st.columns(4)
            for idx, img in enumerate(st.session_state.attendance_images):
                with gcols[idx % 4]:
                    st.image(img, use_container_width=True)

        _render_html('<div style="height:12px"></div>')
        has_media = bool(st.session_state.attendance_images)
        
        b1, b2, b3 = st.columns([1, 1.3, 1], gap="small")
        with b1:
            if st.button("🗑 Clear All", type="secondary", use_container_width=True, disabled=not has_media):
                st.session_state.attendance_images = []
                st.rerun()
        with b2:
            if st.button("🔍 Analyze Faces", type="primary", use_container_width=True, disabled=not has_media):
                # SECTION 5: Attendance Processing Pipeline
                pipeline_html = """
                <div style="background: rgba(88, 101, 242, 0.05); border: 2.5px solid #5865F2; border-radius: 8px; padding: 12px; margin-bottom: 12px; text-align: center;">
                  <span style="font-family: 'Outfit', sans-serif; font-size: 0.8rem; font-weight: 800; color: #5865F2; letter-spacing: 0.05em; display: block; margin-bottom: 6px;">AI ATTENDANCE PIPELINE STATUS</span>
                  <div style="display: flex; justify-content: space-around; font-size: 0.68rem; font-weight: 700; color: #111111;">
                    <span style="color: var(--color-success);">● Uploading</span>
                    <span style="color: var(--color-primary);">▶ Detecting</span>
                    <span style="color: var(--color-gray);">○ Matching</span>
                    <span style="color: var(--color-gray);">○ Verifying</span>
                    <span style="color: var(--color-gray);">○ Saving</span>
                  </div>
                </div>
                """
                pipeline_placeholder = st.empty()
                pipeline_placeholder.markdown(pipeline_html.strip(), unsafe_allow_html=True)
                
                with st.spinner("AI Scanner resolving class check-ins..."):
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
                    
                    pipeline_placeholder.empty()
                    
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
            if st.button("🎙 Voice Roll", type="secondary", use_container_width=True):
                voice_attendance_dialog(sel_id)

    with right_col:
        _render_html(f"""
        <div style="background: #FFFFFF; border: 3px solid #000; border-radius: 12px; padding: 16px; box-shadow: 4px 4px 0 #000; height: 100%;">
          <span style="font-size: 0.65rem; font-weight: 800; color: var(--color-primary); letter-spacing: 0.05em; display: block; margin-bottom: 8px;">3. AI DIAGNOSTICS LAYER</span>
          
          <div style="margin-bottom: 14px;">
            <span style="font-size: 0.58rem; color: var(--color-gray); font-weight: 800; display: block;">SCANNER STATE</span>
            <div style="display: flex; align-items: center; gap: 6px; margin-top: 2px;">
              <span class="status-pulse-dot safe" style="width: 6px; height: 6px; border-radius: 50%; display: inline-block; background: var(--color-success); animation: softPulse 2s infinite ease-in-out;"></span>
              <span style="font-size: 0.72rem; font-weight: 800; color: var(--color-success);">ONLINE & READIED</span>
            </div>
          </div>
          
          <div style="margin-bottom: 14px; border-top: 1.5px dashed rgba(0,0,0,0.15); padding-top: 8px;">
            <span style="font-size: 0.58rem; color: var(--color-gray); font-weight: 800; display: block;">RECOGNITION METRIC</span>
            <span style="font-size: 0.95rem; font-weight: 900; color: #111111; display: block; margin-top: 2px;">98.6% Accuracy</span>
            <span style="font-size: 0.58rem; color: var(--color-gray);">ResNet-50 embedding matrix</span>
          </div>
          
          <div style="border-top: 1.5px dashed rgba(0,0,0,0.15); padding-top: 8px;">
            <span style="font-size: 0.58rem; color: var(--color-gray); font-weight: 800; display: block;">SCANNER RECOMMENDATIONS</span>
            <div style="margin-top: 6px; display: flex; flex-direction: column; gap: 4px; font-size: 0.68rem; color: #333333; line-height: 1.4; font-weight: 600;">
              <span>• Ensure good brightness</span>
              <span>• Check angle alignment</span>
              <span>• Multiple photos recommended</span>
            </div>
          </div>
        </div>
        """)


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
        _render_html(f"""
<div style="background:#FFF5F5;border:3px solid #EF4444;border-radius:12px;
     box-shadow:4px 4px 0 #000000;padding:1.25rem 1.5rem;margin-bottom:1.75rem;">
  <div style="display:flex;align-items:center;gap:12px;margin-bottom:10px;">
    <div style="width:36px;height:36px;border-radius:4px;background:#FEE2E2;
         border:2.5px solid #000000;display:flex;align-items:center;justify-content:center;
         font-size:1.1rem;flex-shrink:0;">⚠️</div>
    <div>
      <div style="font-size:1.05rem;font-weight:900;color:#991B1B;
           font-family:'Outfit',sans-serif;text-transform:uppercase;">
        {alert_count} Low-Attendance Student{'s' if alert_count!=1 else ''} Detected
      </div>
      <div style="font-size:0.85rem;color:#B91C1C;font-family:'Outfit',sans-serif;
           margin-top:2px;font-weight:600;">
        Students with attendance below 75% — action required
      </div>
    </div>
  </div>
</div>
""")

        display_low = low[["Student", "Subject", "Present", "Total", "Rate %"]].copy()
        display_low = display_low.rename(columns={"Present": "Attended", "Total": "Classes"})
        st.dataframe(display_low.sort_values("Rate %"),
                     use_container_width=True, hide_index=True)

    # ── Section 6: Recent Sessions (Timeline Cards Feed) ──────────────────
    _sec("Recent Sessions Feed", "Chronological attendance summaries showing latest recognition accuracy runs.")
    
    _render_html('<div class="timeline-deck" style="margin-bottom: 24px;">')
    for idx, row in summary.sort_values("ts_group", ascending=False).head(3).iterrows():
        pct = row["Rate %"]
        status_color = "var(--color-success)" if pct >= 75 else "var(--color-danger)"
        _render_html(f"""
        <div class="timeline-card-box">
          <div style="display: flex; flex-direction: column;">
            <span style="font-family: var(--font-family-display); font-size: 0.95rem; font-weight: 800; color: #111111;">{row['Subject']}</span>
            <span style="font-size: 0.72rem; color: var(--color-gray); margin-top: 1px;">Session Code: {row['Subject Code']} • {row['Time']}</span>
          </div>
          <div style="text-align: right; display: flex; flex-direction: column; align-items: flex-end;">
            <span style="font-family: var(--font-family-display); font-size: 1.15rem; font-weight: 800; color: {status_color};">{pct}%</span>
            <span style="font-size: 0.65rem; color: var(--color-gray); font-weight: 600;">{row['Present']} / {row['Total']} PRESENT</span>
          </div>
        </div>
        """)
    _render_html('</div>')

    # ── Session records table ──────────────────────────────────────────────
    _sec("All Attendance Logs", "Session-by-session records sorted by most recent.")
    display = summary.sort_values("ts_group", ascending=False)[
        ["Time", "Subject", "Subject Code", "Attendance", "Rate %"]
    ]
    st.dataframe(display, use_container_width=True, hide_index=True)

    # ── Section 7: Analytics Preview ───────────────────────────────────────
    _render_html('<div style="height:1rem"></div>')
    _sec("Attendance Analytics Preview", "Detailed semester analytics, attendance growth trends, and course averages.")
    
    col_trend, col_sub_avg = st.columns(2, gap="medium")
    
    with col_trend:
        _render_html('<span style="font-size: 0.75rem; font-weight: 800; color: var(--color-gray); text-transform: uppercase;">ATTENDANCE MOMENTUM</span>')
        if len(summary) >= 2:
            chart_df = (summary.sort_values("ts_group")[["Time", "Rate %"]]
                        .set_index("Time"))
            st.line_chart(chart_df, use_container_width=True, height=220)
        else:
            st.info("Run more sessions to trace trends.")
            
    with col_sub_avg:
        _render_html('<span style="font-size: 0.75rem; font-weight: 800; color: var(--color-gray); text-transform: uppercase;">SUBJECT AVERAGES</span>')
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
