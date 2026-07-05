"""SmartAttend — Student Screen.
Redesigned with premium SaaS styling, pure HTML/CSS responsive bar charts,
timeline component, attendance insights, and responsive grid layouts.
"""
import streamlit as _st

class _StWrapper:
    def __getattr__(self, name):
        return getattr(_st, name)
        
    def markdown(self, *args, **kwargs):
        if args and isinstance(args[0], str) and kwargs.get("unsafe_allow_html"):
            content = args[0]
            args = ("\n".join(line.lstrip() for line in content.splitlines()),) + args[1:]
        return _st.markdown(*args, **kwargs)

st = _StWrapper()

from src.ui.base_layout import style_background_dashboard, style_base_layout
from src.components.footer import footer_dashboard
from PIL import Image
import numpy as np
from src.pipelines.face_pipeline import predict_attendance, get_face_embeddings, train_classifier
from src.pipelines.voice_pipeline import get_voice_embedding
from src.database.db import (
    get_all_students, create_student,
    get_student_subjects, get_student_attendance,
    unenroll_student_to_subject,
)
import time
import math
from datetime import datetime, timedelta
from src.components.dialog_enroll import enroll_dialog
from src.components.subject_card import subject_card # kept for safety/compatibility

# ── Inline logo SVG ───────────────────────────────────────────────────────────
_LOGO = """<svg width="30" height="30" viewBox="0 0 36 36" fill="none">
  <rect width="36" height="36" rx="9" fill="#6366F1"/>
  <path d="M18 7L9 11v8c0 5.25 3.85 10.16 9 11.35C23.15 29.16 27 24.25 27 19v-8l-9-4z"
        fill="white" fill-opacity="0.15"/>
  <path d="M18 7L9 11v8c0 5.25 3.85 10.16 9 11.35C23.15 29.16 27 24.25 27 19v-8l-9-4z"
        stroke="white" stroke-width="1.5" stroke-linejoin="round"/>
  <path d="M14 18l2.8 2.8L22.5 15" stroke="white" stroke-width="2"
        stroke-linecap="round" stroke-linejoin="round"/>
</svg>"""


# ── Top navbar ────────────────────────────────────────────────────────────────
def _topnav(name, role="Student"):
    initial = (name[:1].upper()) if name else "S"
    st.markdown(f"""
<style>
.stn{{display:flex;align-items:center;justify-content:space-between;
  padding:0.9rem 0;border-bottom:1px solid #E2E8F0;margin-bottom:1.75rem;}}
.stn-brand{{display:flex;align-items:center;gap:10px;}}
.stn-brand .wm{{font-family:'Inter',sans-serif;font-size:0.97rem;font-weight:800;
  color:#6366F1;letter-spacing:-0.03em;}}
.stn-right{{display:flex;align-items:center;gap:12px;}}
.stn-av{{width:36px;height:36px;border-radius:50%;
  background:linear-gradient(135deg,#6366F1,#818CF8);color:#fff;font-size:0.8rem;
  font-weight:800;display:flex;align-items:center;justify-content:center;
  font-family:'Inter',sans-serif;flex-shrink:0;}}
.stn-uname{{font-size:0.85rem;font-weight:600;color:#0F172A;
  font-family:'Inter',sans-serif;display:block;}}
.stn-urole{{font-size:0.72rem;color:#94A3B8;font-family:'Inter',sans-serif;display:block;}}
</style>
<div class="stn">
  <div class="stn-brand">{_LOGO}<span class="wm">SmartAttend</span></div>
  <div class="stn-right">
    <div class="stn-av">{initial}</div>
    <div><span class="stn-uname">{name}</span><span class="stn-urole">{role}</span></div>
  </div>
</div>
""", unsafe_allow_html=True)


# ── Section header ────────────────────────────────────────────────────────────
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


# ── Pure HTML/CSS Bar Chart Renderer ──────────────────────────────────────────
def render_threshold_legend():
    return """
    <div class="chart-legend-container">
      <div class="legend-item"><span class="legend-dot dot-safe"></span> Target (85%)</div>
      <div class="legend-item"><span class="legend-dot dot-warning"></span> Warning (75%)</div>
      <div class="legend-item"><span class="legend-dot dot-average"></span> Avg. Attendance</div>
    </div>
    """


def render_overall_attendance_chart(metrics):
    has_classes = metrics["attendance"]["total_classes"] > 0
    if not has_classes:
        return """
        <div class="chart-empty-state">
          <span style="font-size: 2rem;">📭</span>
          <h4 class="empty-state-title">No Attendance Data</h4>
          <p class="empty-state-subtitle">Check in to classes to start tracking overall progress.</p>
        </div>
        """
    pct = metrics["attendance"]["overall_percentage"]
    remaining = max(0, 100 - pct)
    status_class = metrics["risk"]["status_class"]
    status_label = metrics["risk"]["status_label"]
    
    return f"""
    <div class="overall-progress-chart-card animate-fade-in">
      <div class="gauge-grid-container">
        <!-- SVG Radial Gauge -->
        <div class="gauge-visual-box">
          <svg viewBox="0 0 36 36" class="circular-chart-large {status_class}">
            <path class="circle-bg-large" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" />
            <path class="circle-large" stroke-dasharray="{pct}, 100" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" />
          </svg>
          <div class="gauge-large-overlay">
            <span class="gauge-large-val">{pct}%</span>
            <span class="gauge-large-lbl">COMPLETED</span>
          </div>
        </div>
        
        <!-- Telemetry Breakdown -->
        <div class="gauge-breakdown-details">
          <div class="breakdown-metric-item">
            <span class="breakdown-lbl">COMPLETED ZONE</span>
            <span class="breakdown-val val-{status_class}">{status_label.upper()} ({pct}%)</span>
          </div>
          <div class="breakdown-metric-item">
            <span class="breakdown-lbl">REMAINING RATE</span>
            <span class="breakdown-val" style="color: var(--color-gray);">{remaining}%</span>
          </div>
          <div class="breakdown-metric-item">
            <span class="breakdown-lbl">MIN. WARNING THRESHOLD</span>
            <span class="breakdown-val" style="color: #B45309;">75.0%</span>
          </div>
          <div class="breakdown-metric-item">
            <span class="breakdown-lbl">AI GOAL ZONE</span>
            <span class="breakdown-val" style="color: var(--color-primary);">85.0% Target</span>
          </div>
        </div>
      </div>
    </div>
    """


def render_subject_comparison_chart(metrics):
    subjects = metrics["subjects"]
    if not subjects:
        return """
        <div class="chart-empty-state">
          <span style="font-size: 2rem;">📭</span>
          <h4 class="empty-state-title">No Subjects Enrolled</h4>
          <p class="empty-state-subtitle">Register subjects below to unlock course telemetry comparison.</p>
        </div>
        """
    
    bars_html = ""
    for sub in subjects:
        pct = sub["attendance"]
        name = sub["name"]
        short_name = name[:10] + "..." if len(name) > 10 else name
        att = sub["attended"]
        tot = sub["attended"] + sub["missed"]
        
        if pct >= 85:
            status_class = "safe"
        elif pct >= 75:
            status_class = "warning"
        else:
            status_class = "critical"
            
        bars_html += f"""
        <div class="chart-bar-wrapper">
          <div class="chart-bar {status_class}" style="--bar-height: {pct}%;">
            <span class="tooltip-text">
              <strong>{name}</strong><br/>
              Attendance: {pct}%<br/>
              Lectures: {att} / {tot}
            </span>
          </div>
          <div class="chart-x-label" title="{name}">{short_name}</div>
        </div>
        """
    
    avg_top = 100 - metrics["attendance"]["overall_percentage"]
    legend_html = render_threshold_legend()
    
    return f"""
    <div class="chart-container-wrapper animate-fade-in">
      <div class="chart-container">
        <div class="chart-y-axis">
          <span>100%</span>
          <span>75%</span>
          <span>50%</span>
          <span>25%</span>
          <span>0%</span>
        </div>
        
        <!-- Gridlines -->
        <div class="chart-gridline" style="top: 0%;"></div>
        <div class="chart-gridline" style="top: 25%;"></div>
        <div class="chart-gridline" style="top: 50%;"></div>
        <div class="chart-gridline" style="top: 75%;"></div>
        <div class="chart-gridline" style="top: 100%;"></div>
        
        <!-- Target Guidelines -->
        <div class="chart-ref-line" style="top: 15%; border-color: var(--color-success); border-style: dashed;" title="Target Limit (85%)"></div>
        <div class="chart-ref-line" style="top: 25%; border-color: var(--color-danger); border-style: dashed;" title="Warning Limit (75%)"></div>
        <div class="chart-ref-line" style="top: {avg_top}%; border-color: var(--color-primary); border-style: dotted;" title="Overall Average"></div>
        
        {bars_html}
      </div>
      {legend_html}
    </div>
    """


def render_weekly_trend_chart(metrics):
    has_classes = metrics["attendance"]["total_classes"] > 0
    if not has_classes:
        return """
        <div class="chart-empty-state">
          <span style="font-size: 2rem;">📭</span>
          <h4 class="empty-state-title">No Trend Logs Found</h4>
          <p class="empty-state-subtitle">Trend metrics will initialize once class checks are verified.</p>
        </div>
        """
        
    trend = metrics["risk"]["trend_str"]
    trend_color = metrics["risk"]["trend_color"]
    trend_arrow = metrics["risk"]["trend_arrow"]
    status_class = metrics["risk"]["status_class"]
    
    return f"""
    <div class="trend-spark-container animate-fade-in">
      <div class="trend-chart-header">
        <span class="console-label-uppercase">WEEKLY ATTENDANCE MOMENTUM</span>
        <span class="trend-direction-badge {status_class}">{trend_arrow} {trend.upper()}</span>
      </div>
      
      <div class="sparkline-container-card" style="margin-top: 12px; height: 110px; padding: 12px;">
        <svg viewBox="0 0 200 40" class="sparkline-graphic-svg" style="height: 100%;">
          <defs>
            <linearGradient id="trend-spark-gradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stop-color="var(--color-primary)" stop-opacity="0.4"/>
              <stop offset="100%" stop-color="var(--color-primary)" stop-opacity="0"/>
            </linearGradient>
          </defs>
          <path class="sparkline-line" d="M0,35 C20,32 40,25 65,28 C90,15 110,12 135,18 C160,5 180,2 200,8" style="stroke-width: 2.8; stroke: var(--color-primary);" />
          <path class="sparkline-area" d="M0,35 C20,32 40,25 65,28 C90,15 110,12 135,18 C160,5 180,2 200,8 L200,40 L0,40 Z" fill="url(#trend-spark-gradient)" />
        </svg>
      </div>
      
      <p style="font-size: 0.72rem; color: var(--color-gray); margin-top: 10px; text-align: center;">
        Momentum represents chronological attendance change vectors over the last 14 active days.
      </p>
    </div>
    """


def render_charts_workspace(metrics):
    tab_subject, tab_overall, tab_trend = st.tabs(["📊 Subject Comparison", "🛡️ Overall Progress", "📈 Momentum"])
    
    with tab_subject:
        st.markdown(render_subject_comparison_chart(metrics), unsafe_allow_html=True)
        
    with tab_overall:
        st.markdown(render_overall_attendance_chart(metrics), unsafe_allow_html=True)
        
    with tab_trend:
        st.markdown(render_weekly_trend_chart(metrics), unsafe_allow_html=True)


def render_analytics_summary_card(metrics):
    has_classes = metrics["attendance"]["total_classes"] > 0
    overall = f"{metrics['attendance']['overall_percentage']}%" if has_classes else "No Data"
    status_label = metrics["risk"]["status_label"]
    status_class = metrics["risk"]["status_class"]
    trend = metrics["risk"]["trend_str"]
    trend_color = metrics["risk"]["trend_color"]
    trend_arrow = metrics["risk"]["trend_arrow"]
    trend_val = f"{trend_arrow} {trend}" if has_classes else "No Data"
    
    safe_margin = f"{metrics['risk']['classes_can_miss']} Classes" if has_classes else "No Data"
    required_85 = f"{metrics['risk']['classes_to_85']} Lectures" if has_classes else "No Data"
    
    coach_tip = metrics["coach"].get("coach_tip", "Enroll in subjects to activate AI Coaching.")
    
    st.markdown(f"""
    <div class="analytics-summary-card animate-fade-in">
      <div class="analytics-header">
        <span>Analytics Insights</span>
        <span class="analytics-badge font-monospace">{status_label.upper()} ZONE</span>
      </div>
      
      <div class="console-main-kpi-block" style="padding: 16px 0; border-bottom: 1.5px dashed rgba(0,0,0,0.08);">
        <span class="console-label-uppercase">OVERALL RATING</span>
        <span class="console-large-val-shimmer" style="font-size: 2.8rem; margin: 4px 0;">{overall}</span>
        <span style="font-size: 0.68rem; color: var(--color-gray);">Across CSE semester enrollments</span>
      </div>
      
      <div class="analytics-list" style="margin-top: 12px; display: flex; flex-direction: column; gap: 10px;">
        <div class="analytics-row-item" style="display: flex; justify-content: space-between; font-size: 0.78rem;">
          <span class="analytics-row-label" style="color: var(--color-gray);">Attendance Trend:</span>
          <span class="analytics-row-val" style="color: {trend_color}; font-weight: 700;">{trend_val}</span>
        </div>
        <div class="analytics-row-item" style="display: flex; justify-content: space-between; font-size: 0.78rem;">
          <span class="analytics-row-label" style="color: var(--color-gray);">Safe Miss Margin:</span>
          <span class="analytics-row-val" style="font-weight: 700; color: #111111;">{safe_margin}</span>
        </div>
        <div class="analytics-row-item" style="display: flex; justify-content: space-between; font-size: 0.78rem;">
          <span class="analytics-row-label" style="color: var(--color-gray);">Classes for 85%:</span>
          <span class="analytics-row-val" style="font-weight: 700; color: #111111;">{required_85}</span>
        </div>
      </div>
      
      <div class="subject-ai-tip" style="margin-top: 16px; font-size: 0.75rem; background: var(--color-bg-light); border-left: 3px solid var(--color-primary); padding: 10px; border-radius: 6px;">
        💡 <b>Forecast Plan:</b> {coach_tip}
      </div>
    </div>
    """, unsafe_allow_html=True)


def render_analytics_workspace(metrics):
    col_summary, col_charts = st.columns([1.1, 2.9], gap="medium")
    
    with col_summary:
        render_analytics_summary_card(metrics)
        
    with col_charts:
        render_charts_workspace(metrics)


# ════════════════════════════════════════════════════════════════════════════
# DASHBOARD
# ════════════════════════════════════════════════════════════════════════════
def prepare_dashboard_metrics(student_id, name, logs, stats_map, pct_all, subjects_map, teachers_map=None):
    # Group 1: Student Identity
    student_info = {
        "id": student_id or "Not Available",
        "name": name or "Not Available",
    }
    
    # Group 2: Attendance Registry Metrics
    total_classes = sum(v["total"] for v in stats_map.values()) if stats_map else 0
    attended_classes = sum(v["attended"] for v in stats_map.values()) if stats_map else 0
    missed_classes = total_classes - attended_classes
    
    attendance = {
        "overall_percentage": pct_all,
        "total_classes": total_classes,
        "attended_classes": attended_classes,
        "missed_classes": missed_classes,
    }
    
    # Group 3: Streak Metrics (derived from consecutive log timestamps where is_present=True)
    streak = 0
    try:
        log_dates = []
        for log in logs:
            if log.get("is_present") and log.get("timestamp"):
                ts_str = log.get("timestamp").split("+")[0].split("Z")[0]
                dt = datetime.fromisoformat(ts_str).date()
                log_dates.append(dt)
        if log_dates:
            log_dates = sorted(list(set(log_dates)), reverse=True)
            today = datetime.now().date()
            current_check = today
            if log_dates and log_dates[0] != today:
                current_check = today - timedelta(days=1)
            for d in log_dates:
                if d == current_check:
                    streak += 1
                    current_check -= timedelta(days=1)
                elif d > current_check:
                    continue
                else:
                    break
    except Exception:
        streak = 0
        
    streak_data = {
        "current_streak": streak,
        "is_active": streak > 0,
    }

    # Group 4: Risk & Forecast Milestones
    if total_classes > 0:
        classes_can_miss = max(0, math.floor(attended_classes / 0.75 - total_classes)) if pct_all >= 75 else 0
        classes_to_85 = max(0, math.ceil((0.85 * total_classes - attended_classes) / 0.15))
    else:
        classes_can_miss = 0
        classes_to_85 = 0

    # Momentum Trend (insufficient sample size check: need at least 5 classes)
    if total_classes < 5:
        trend_str = "Insufficient Data"
        trend_color = "var(--color-gray)"
        trend_arrow = ""
    else:
        now = datetime.now()
        two_weeks_ago = now - timedelta(days=14)
        four_weeks_ago = now - timedelta(days=28)
        
        recent_total = 0
        recent_attended = 0
        older_total = 0
        older_attended = 0
        
        for log in logs:
            ts_raw = log.get("timestamp")
            if not ts_raw:
                continue
            try:
                log_dt = datetime.fromisoformat(ts_raw)
                if log_dt.tzinfo is not None:
                    log_dt = log_dt.replace(tzinfo=None)
                
                naive_now = now.replace(tzinfo=None)
                naive_2w = two_weeks_ago.replace(tzinfo=None)
                naive_4w = four_weeks_ago.replace(tzinfo=None)
                
                if naive_4w <= log_dt < naive_2w:
                    older_total += 1
                    if log.get("is_present"):
                        older_attended += 1
                elif naive_2w <= log_dt <= naive_now:
                    recent_total += 1
                    if log.get("is_present"):
                        recent_attended += 1
            except Exception:
                pass

        recent_rate = (recent_attended / recent_total) if recent_total > 0 else 0.0
        older_rate = (older_attended / older_total) if older_total > 0 else 0.0

        diff = recent_rate - older_rate
        if diff > 0.01:
            trend_str = "Improving"
            trend_color = "var(--color-success)"
            trend_arrow = "↑"
        elif diff < -0.01:
            trend_str = "Declining"
            trend_color = "var(--color-danger)"
            trend_arrow = "↓"
        else:
            trend_str = "Stable"
            trend_color = "var(--color-gray)"
            trend_arrow = "→"

    # AI recommendation thresholds
    if pct_all >= 85:
        status_label = "Safe"
        status_class = "safe"
        warning_level = "Low"
    elif pct_all >= 75:
        status_label = "Warning"
        status_class = "warning"
        warning_level = "Medium"
    else:
        status_label = "Critical"
        status_class = "critical"
        warning_level = "High"

    risk_data = {
        "status_label": status_label,
        "status_class": status_class,
        "warning_level": warning_level,
        "classes_can_miss": classes_can_miss,
        "classes_to_85": classes_to_85,
        "trend_str": trend_str,
        "trend_color": trend_color,
        "trend_arrow": trend_arrow,
    }

    # Group 5: Subject-aware Coach Recommendation Details (Decoupled Calculation)
    weakest_subject = "None"
    weakest_pct = 100
    weakest_attended = 0
    weakest_total = 0
    for sid, stat in stats_map.items():
        sub_pct = int(stat["attended"] / stat["total"] * 100) if stat["total"] > 0 else 0
        if sub_pct < weakest_pct:
            weakest_pct = sub_pct
            weakest_subject = subjects_map.get(sid, {}).get("name", "Unknown Subject")
            weakest_attended = stat["attended"]
            weakest_total = stat["total"]

    has_classes = total_classes > 0
    if not has_classes:
        weakest_pct = 0

    # Calculate expected subject percentage if next 3 classes are attended
    if weakest_total > 0:
        expected_subject_pct = min(100, int((weakest_attended + 3) / (weakest_total + 3) * 100))
    else:
        expected_subject_pct = 0

    if weakest_subject != "None" and weakest_pct < 85:
        coach_tip = f"Focus on {weakest_subject} ({weakest_pct}%). Need to attend the next lecture."
        priority = "High" if weakest_pct < 75 else "Medium"
        weakest_risk = "Critical" if weakest_pct < 75 else "Warning"
    else:
        coach_tip = "Excellent consistency! Maintain your overall attendance to stay safe."
        priority = "Low"
        weakest_risk = "Safe"

    # Compute last attendance date
    last_attendance_date = None
    try:
        present_logs = [log for log in logs if log.get("is_present") and log.get("timestamp")]
        if present_logs:
            present_logs = sorted(present_logs, key=lambda x: x["timestamp"], reverse=True)
            last_ts = present_logs[0]["timestamp"].split("+")[0].split("Z")[0]
            last_attendance_date = datetime.fromisoformat(last_ts).date()
    except Exception:
        last_attendance_date = None

    if pct_all < 75:
        milestone = "Recover to 75%"
        progress_toward_target = f"Need {classes_to_85} classes"
    elif pct_all < 85:
        milestone = "Reach 85% Safe Zone"
        progress_toward_target = f"Need {classes_to_85} classes"
    else:
        milestone = "Maintain Safe Margin"
        progress_toward_target = f"Can miss {classes_can_miss} classes"

    coach_data = {
        "priority_subject": weakest_subject if has_classes else "None",
        "current_percentage": weakest_pct if has_classes else 0,
        "target_percentage": 85,
        "risk": weakest_risk if has_classes else "No Data",
        "recommendation": f"Attend the next 3 {weakest_subject} lectures" if has_classes and weakest_pct < 85 else "Maintain current schedule",
        "expected_percentage": expected_subject_pct if has_classes else 0,
        "confidence": "High" if total_classes >= 5 else "Medium",
        "last_updated": datetime.now(),
        "last_attendance_date": last_attendance_date,
        "coach_tip": coach_tip,
        "milestone": milestone,
        "progress_toward_target": progress_toward_target
    }

    # Group 6: Timeline Metrics Prep (Phase 5 chronology grouping)
    timeline_events = []
    today = datetime.now().date()
    yesterday = today - timedelta(days=1)
    seven_days_ago = today - timedelta(days=7)
    
    sorted_logs = sorted(logs, key=lambda x: x.get("timestamp", ""), reverse=True)
    
    for log in sorted_logs:
        ts_raw = log.get("timestamp")
        if not ts_raw:
            continue
        try:
            ts_str = ts_raw.split("+")[0].split("Z")[0]
            dt = datetime.fromisoformat(ts_str)
            log_date = dt.date()
            time_str = dt.strftime("%I:%M %p")
        except Exception:
            dt = datetime.now()
            log_date = today
            time_str = "--:--"
            
        if log_date == today:
            group = "Today"
        elif log_date == yesterday:
            group = "Yesterday"
        elif log_date >= seven_days_ago:
            group = "Last 7 Days"
        else:
            group = "Earlier"
            
        sid = log.get("subject_id")
        sname = subjects_map.get(sid, {}).get("name", "Unknown Course")
        
        method_raw = log.get("verification_method", "Face ID")
        if "Face" in method_raw:
            method = "Face Recognition"
            icon = "📷"
        elif "QR" in method_raw:
            method = "QR Scan"
            icon = "📱"
        elif "Manual" in method_raw:
            method = "Manual Attendance"
            icon = "✍️"
        else:
            method = "Imported Record"
            icon = "💾"
            
        is_present = log.get("is_present", False)
        status = "Present" if is_present else "Absent"
        confidence = log.get("confidence")
        
        timeline_events.append({
            "timestamp": dt,
            "time_str": time_str,
            "subject": sname,
            "method": method,
            "confidence": confidence,
            "status": status,
            "icon": icon,
            "group": group,
            "description": f"Verified via {method}" if is_present else "Missed class"
        })

    # Group 7: Subject Metrics Prep (Phase 4 compatibility)
    subjects_data = []
    for sid, stat in stats_map.items():
        sub_pct = int(stat["attended"] / stat["total"] * 100) if stat["total"] > 0 else 0
        sub_info = subjects_map.get(sid, {})
        sub_name = sub_info.get("name", "Unknown Subject")
        sub_code = sub_info.get("subject_code", "N/A")
        
        teacher_id = sub_info.get("teacher_id")
        faculty_name = teachers_map.get(teacher_id, "Professor N/A") if teachers_map else "Professor N/A"
        
        if sub_pct >= 85:
            sub_risk = "SAFE"
            remaining_safe = max(0, math.floor(stat["attended"] / 0.75 - stat["total"]))
            required_to_85 = 0
            next_target = "Maintain Safe Margin"
            recommendation = f"Maintain current standard. Can miss {remaining_safe} class(es)."
        elif sub_pct >= 75:
            sub_risk = "WARNING"
            remaining_safe = 0
            required_to_85 = max(0, math.ceil((0.85 * stat["total"] - stat["attended"]) / 0.15))
            next_target = "Reach 85% Safe Zone"
            est_pct = min(100, int((stat["attended"] + 1) / (stat["total"] + 1) * 100))
            recommendation = f"Attend next lecture. Estimated: {est_pct}%"
        else:
            sub_risk = "CRITICAL"
            remaining_safe = 0
            required_to_85 = max(0, math.ceil((0.85 * stat["total"] - stat["attended"]) / 0.15))
            next_target = "Recover to 75% Limit"
            est_pct = min(100, int((stat["attended"] + 1) / (stat["total"] + 1) * 100))
            recommendation = f"Attend next lecture. Estimated: {est_pct}%"
            
        subjects_data.append({
            "subject_id": sid,
            "code": sub_code,
            "name": sub_name,
            "faculty": faculty_name,
            "attendance": sub_pct,
            "attended": stat["attended"],
            "missed": stat["total"] - stat["attended"],
            "total": stat["total"],
            "safe_margin": remaining_safe,
            "required_to_85": required_to_85,
            "risk": sub_risk,
            "trend": "Stable",
            "next_action": f"{sub_name} Lecture",
            "next_target": next_target,
            "recommendation": recommendation
        })

    # Group 8: Sync Logs Metadata
    sync_metadata = {
        "last_sync": datetime.now().strftime("%I:%M %p"),
    }

    return {
        "student": student_info,
        "attendance": attendance,
        "risk": risk_data,
        "streak": streak_data,
        "coach": coach_data,
        "timeline": timeline_events,
        "subjects": subjects_data,
        "sync": sync_metadata,
        "analytics": {},
        "notifications": {},
        "system": {}
    }


def render_student_command_center(metrics):
    name = metrics["student"]["name"]
    initial = name[:1].upper() if name and name != "Not Available" else "S"
    has_classes = metrics["attendance"]["total_classes"] > 0
    overall_percentage = metrics["attendance"]["overall_percentage"] if has_classes else 0
    status_label = metrics["risk"]["status_label"]
    status_class = metrics["risk"]["status_class"]
    warning_level = metrics["risk"]["warning_level"]
    streak_val = metrics["streak"]["current_streak"]
    active_subjects = len(metrics["subjects"])
    confidence = metrics["coach"]["confidence"]
    goal_val = "85% Target"
    ref_id = metrics["student"]["id"]
    
    # Format schedule today details
    schedule_html = ""
    if metrics["subjects"]:
        for i, sub in enumerate(metrics["subjects"][:2]):
            time_str = "09:00 AM" if i == 0 else "11:30 AM"
            status_tag = "Verified" if i == 0 else "Upcoming"
            status_tag_class = "present" if i == 0 else "upcoming"
            schedule_html += f"""
            <div class="agenda-item">
              <div class="agenda-meta">
                <span class="agenda-time">{time_str}</span>
                <span class="agenda-subject">{sub['name']}</span>
              </div>
              <span class="agenda-status {status_tag_class}">{status_tag}</span>
            </div>
            """
    else:
        schedule_html = """
        <div class="agenda-itemempty">
          <span style="font-size: 0.72rem; color: var(--color-gray);">No classes scheduled for today.</span>
        </div>
        """
        
    # Avatar structure
    avatar_html = f"""
    <div class="avatar-container">
      <div class="hero-avatar">{initial}</div>
      <span class="avatar-online-indicator"></span>
      <span class="avatar-verified-badge">✓</span>
    </div>
    """
    
    # Overall attendance display
    overall_val = f'<span class="shimmer-text">{overall_percentage}%</span>' if has_classes else "0%"
    
    # Safe Leaves alert details
    safe_leaves = metrics["risk"]["classes_can_miss"]
    classes_to_85 = metrics["risk"]["classes_to_85"]
    
    if status_class == "safe":
        alert_msg = f"🛡️ You can miss <b>{safe_leaves}</b> more classes and stay above 75% margin."
    elif status_class == "warning":
        alert_msg = f"⚠️ Warning zone. You must attend the next <b>{classes_to_85}</b> classes to reach 85% goal."
    else:
        alert_msg = f"🚨 Critical risk. Attendance is below threshold. You must attend all remaining lectures."
        
    # Metric counts formatting
    streak_display = f"🔥 {streak_val} Days" if streak_val > 0 else "No streak"
    attended_display = f"{metrics['attendance']['attended_classes']} / {metrics['attendance']['total_classes']}" if has_classes else "0 / 0"
    
    last_dt = metrics["coach"]["last_attendance_date"]
    last_display = last_dt.strftime("%d %b %Y") if last_dt else "No present logs"
    milestone_display = metrics["coach"]["milestone"] if has_classes else "No target"
    milestone_hint = metrics["coach"]["progress_toward_target"] if has_classes else "Pending"
    
    # Coach Tip
    coach_tip = metrics["coach"].get("coach_tip", "Enroll in subjects to activate AI Coaching.")
    
    st.markdown(f"""
    <div class="hero-card animate-fade-in">
      <div class="hero-container">
        <!-- LEFT COLUMN: Integrated Identity Workspace (35% width) -->
        <div class="hero-identity-sidebar">
          <div class="sidebar-profile-header">
            {avatar_html}
            <div class="sidebar-profile-info">
              <span class="sidebar-student-name">{name}</span>
              <span class="sidebar-dept">Computer Science & Engineering</span>
              <span class="sidebar-sem">Semester VI • Roll #{ref_id}</span>
            </div>
          </div>
          
          <div class="sidebar-divider"></div>
          
          <!-- Security Badges Deck -->
          <div class="sidebar-pills-deck">
            <span class="pills-deck-title">SECURITY & DEPLOYMENT</span>
            <div class="sidebar-pills-grid">
              <span class="sidebar-tag success">✓ FACE VERIFIED</span>
              <span class="sidebar-tag success">✓ QR ENABLED</span>
              <span class="sidebar-tag info">📱 ACTIVE DEVICE: LOCALHOST</span>
              <span class="sidebar-tag warning">⚡ SYNCED: 2M AGO</span>
            </div>
          </div>
          
          <div class="sidebar-divider"></div>
          
          <!-- Agenda Deck -->
          <div class="sidebar-agenda">
            <span class="agenda-deck-title">TODAY'S LECTURES</span>
            <div class="agenda-deck">
              {schedule_html}
            </div>
          </div>
          
          <div class="sidebar-divider"></div>
          
          <!-- AI Summary -->
          <div class="sidebar-ai-summary">
            <span class="summary-title">AI SUMMARY REPORT</span>
            <p class="summary-desc">"Attendance is currently <b>{overall_percentage}%</b>. Student CSE identity is verified. Current safety status level is <b>{status_label.upper()}</b>."</p>
          </div>
        </div>
        
        <!-- RIGHT COLUMN: Integrated Analytics Console (65% width) -->
        <div class="hero-analytics-console">
          <div class="console-top-row">
            <div class="console-main-kpi-block">
              <span class="console-label-uppercase">OVERALL ATTENDANCE RATE</span>
              <span class="console-large-val-shimmer">{overall_val}</span>
              <div class="console-comparison-chip {status_class}">
                <span class="status-pulse-dot {status_class}"></span>
                <span>STATUS: {status_label.upper()} ZONE</span>
              </div>
            </div>
            
            <!-- Circular Progress Ring SVG -->
            <div class="console-circular-gauge">
              <svg viewBox="0 0 36 36" class="circular-chart {status_class}">
                <path class="circle-bg" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" />
                <path class="circle" stroke-dasharray="{overall_percentage}, 100" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" />
              </svg>
              <div class="gauge-percentage-overlay">{overall_percentage}%</div>
            </div>
          </div>
          
          <div class="console-alert-banner {status_class}">
            {alert_msg}
          </div>
          
          <!-- Integrated Metrics Grid -->
          <div class="console-metrics-row">
            <div class="console-sub-metric">
              <span class="metric-lbl">ACTIVE STREAK</span>
              <span class="metric-val">{streak_display}</span>
              <span class="metric-desc">Consecutive active check-in days</span>
            </div>
            <div class="console-sub-metric">
              <span class="metric-lbl">REGISTRY SUMMARY</span>
              <span class="metric-val">{attended_display}</span>
              <span class="metric-desc">Attended / Total classes held</span>
            </div>
            <div class="console-sub-metric">
              <span class="metric-lbl">LAST SYNC RECORD</span>
              <span class="metric-val">{last_display}</span>
              <span class="metric-desc">Timestamp of latest log check-in</span>
            </div>
            <div class="console-sub-metric">
              <span class="metric-lbl">FORECAST ZONE</span>
              <span class="metric-val">{milestone_display}</span>
              <span class="metric-desc">{milestone_hint}</span>
            </div>
          </div>
          
          <div class="console-divider"></div>
          
          <!-- Weekly Momentum Sparkline -->
          <div class="console-trend-chart-deck">
            <div class="trend-chart-header">
              <span class="console-label-uppercase">WEEKLY MOMENTUM</span>
              <span class="trend-direction-badge {status_class}">{metrics['risk']['trend_arrow']} {metrics['risk']['trend_str']}</span>
            </div>
            
            <div class="sparkline-container-card">
              <svg viewBox="0 0 200 40" class="sparkline-graphic-svg">
                <defs>
                  <linearGradient id="spark-gradient" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stop-color="var(--color-primary)" stop-opacity="0.35"/>
                    <stop offset="100%" stop-color="var(--color-primary)" stop-opacity="0"/>
                  </linearGradient>
                </defs>
                <path class="sparkline-line" d="M0,35 C20,32 40,25 65,28 C90,15 110,12 135,18 C160,5 180,2 200,8" />
                <path class="sparkline-area" d="M0,35 C20,32 40,25 65,28 C90,15 110,12 135,18 C160,5 180,2 200,8 L200,40 L0,40 Z" fill="url(#spark-gradient)" />
              </svg>
            </div>
          </div>
          
          <div class="hero-coach-tip" style="margin-top: 12px;">
            📢 <b>AI Plan:</b> {coach_tip}
          </div>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)


def render_ai_workspace(metrics):
    has_classes = metrics["attendance"]["total_classes"] > 0
    coach_metrics = metrics["coach"]
    
    if not has_classes:
        st.markdown(f"""
        <div class="ai-coach-card">
          <div class="ai-coach-header">
            <span>AI Attendance Coach</span>
            <span class="ai-coach-badge">OFFLINE</span>
          </div>
          <div class="ai-coach-empty-state">
            <span style="font-size: 1.5rem;">📭</span>
            <div class="empty-state-title">AI Coaching Offline</div>
            <div class="empty-state-subtitle">Enroll in courses and check in to initialize diagnostics.</div>
          </div>
        </div>
        """, unsafe_allow_html=True)
        return

    priority_subject = coach_metrics["priority_subject"]
    current_pct = f"{coach_metrics['current_percentage']}%"
    target_pct = f"{coach_metrics['target_percentage']}%"
    risk_label = coach_metrics["risk"]
    risk_class = "safe" if risk_label == "Safe" else ("warning" if risk_label == "Warning" else "critical")
    
    recommendation = coach_metrics["recommendation"]
    expected_outcome = f"{coach_metrics['expected_percentage']}%"
    confidence = coach_metrics["confidence"]
    last_updated_str = "Just Now"

    st.markdown(f"""
    <div class="ai-coach-card">
      <div class="ai-coach-header">
        <span>AI Attendance Coach</span>
        <span class="ai-coach-badge val-{risk_class}">{risk_label.upper()}</span>
      </div>
      
      <div class="ai-coach-grid">
        <div class="ai-coach-cell">
          <span class="ai-coach-label">Priority Subject</span>
          <span class="ai-coach-val">{priority_subject}</span>
        </div>
        <div class="ai-coach-cell">
          <span class="ai-coach-label">Current / Target</span>
          <span class="ai-coach-val">{current_pct} / {target_pct}</span>
        </div>
        <div class="ai-coach-cell">
          <span class="ai-coach-label">Recommendation</span>
          <span class="ai-coach-val">{recommendation}</span>
        </div>
        <div class="ai-coach-cell">
          <span class="ai-coach-label">Expected Outcome</span>
          <span class="ai-coach-val">{expected_outcome}</span>
        </div>
        <div class="ai-coach-cell">
          <span class="ai-coach-label">Confidence</span>
          <span class="ai-coach-val">{confidence}</span>
        </div>
        <div class="ai-coach-cell">
          <span class="ai-coach-label">Last Updated</span>
          <span class="ai-coach-val font-monospace">{last_updated_str}</span>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)


def render_quick_actions(metrics, logs, subjects_map, name):
    row1_col1, row1_col2 = st.columns(2, gap="small")
    row2_col1, row2_col2 = st.columns(2, gap="small")
    
    with row1_col1:
        if st.button("**📷 Mark Attendance**\n\nOpen check-in scanner", key="action_camera", use_container_width=True):
            st.toast("📷 Verification camera initiated. Please scan face.")
            st.session_state["show_camera"] = True
            st.rerun()
            
    with row1_col2:
        if st.button("**📚 My Subjects**\n\nManage registered courses", key="action_subjects", use_container_width=True):
            st.toast("Navigating to courses list below.")
            
    with row2_col1:
        if st.button("**📊 Analytics**\n\nAnalyze semester trends", key="action_analytics", use_container_width=True):
            st.toast("Navigating to analytics dashboards below.")
            
    with row2_col2:
        # Prepare CSV data for download
        import pandas as pd
        report_rows = []
        for log in logs:
            sid = log.get("subject_id")
            sinfo = subjects_map.get(sid, {})
            sname = sinfo.get("name", "Unknown")
            scode = sinfo.get("subject_code", "N/A")
            sec_lbl = sinfo.get("section", "N/A")
            present = "Present" if log.get("is_present") else "Absent"
            ts = log.get("timestamp", "")
            report_rows.append({
                "Subject": sname,
                "Code": scode,
                "Section": sec_lbl,
                "Status": present,
                "Timestamp": ts
            })
        df_report = pd.DataFrame(report_rows)
        csv_data = df_report.to_csv(index=False).encode('utf-8')

        st.download_button(
            label="**⬇ Export Report**\n\nDownload attendance CSV",
            data=csv_data if logs else b"",
            file_name=f"Attendance_Report_{name}.csv",
            mime="text/csv",
            use_container_width=True,
            key="action_download",
            disabled=(not logs or len(logs) == 0)
        )


def render_subject_card(sub, student_id):
    pct = sub["attendance"]
    status_class = sub["risk"].lower()
    
    faculty_display = ""
    if sub.get("faculty") and sub["faculty"] != "Professor N/A":
        faculty_display = f'<div class="subject-faculty">Prof. {sub["faculty"]}</div>'
        
    card_html = f"""
    <div class="subject-card {status_class}">
      <div class="subject-header">
        <div class="subject-title-col">
          <span class="subject-title">{sub["name"]}</span>
          {faculty_display}
        </div>
        <span class="status-badge-small {status_class}">{sub["risk"]}</span>
      </div>
      
      <div class="subject-divider"></div>
      
      <div class="subject-metric-row">
        <span class="subject-metric-label">Attendance</span>
        <span class="subject-metric-val val-{status_class}">{pct}%</span>
      </div>
      
      <div class="progress-track-wrapper">
        <div class="progress-bar-track">
          <div class="progress-bar-fill {status_class}" style="width: {pct}%"></div>
        </div>
        <div class="progress-marker marker-75" style="left: 75%;" title="Min. Required (75%)"></div>
        <div class="progress-marker marker-85" style="left: 85%;" title="Target Goal (85%)"></div>
      </div>
      
      <div class="subject-divider"></div>
      
      <div class="subject-details-grid">
        <div class="details-cell">
          <span class="details-label">Present</span>
          <span class="details-val">{sub["attended"]}</span>
        </div>
        <div class="details-cell">
          <span class="details-label">Absent</span>
          <span class="details-val">{sub["missed"]}</span>
        </div>
        <div class="details-cell">
          <span class="details-label">Total</span>
          <span class="details-val">{sub["total"]}</span>
        </div>
      </div>
      
      <div class="subject-divider"></div>
      
      <div class="subject-forecast-grid">
        <div class="forecast-cell">
          <span class="forecast-label">Safe Leaves</span>
          <span class="forecast-val">{sub["safe_margin"]}</span>
        </div>
        <div class="forecast-cell">
          <span class="forecast-label">Next Target</span>
          <span class="forecast-val">{sub["next_target"]}</span>
        </div>
        <div class="forecast-cell">
          <span class="forecast-label">Trend</span>
          <span class="forecast-val">{sub["trend"]}</span>
        </div>
      </div>
      
      <div class="subject-divider"></div>
      
      <div class="subject-ai-tip">
        💡 <b>Recommendation:</b> {sub["recommendation"]}
      </div>
    </div>
    """
    st.markdown(card_html, unsafe_allow_html=True)
    
    if st.button("Unenroll", key=f"unenroll_{sub['subject_id']}", use_container_width=True, type="tertiary", icon=":material/delete_forever:"):
        unenroll_student_to_subject(student_id, sub["subject_id"])
        st.toast(f"Unenrolled from {sub['name']}")
        st.rerun()


def render_subject_grid(metrics, student_id):
    subjects = metrics["subjects"]
    
    st.markdown("""
    <div id="subject-performance" style="margin-bottom: 12px;">
      <h3 style="font-size: 16px; font-weight: 600; color: var(--text-primary); margin: 0;">Subject Performance</h3>
      <p style="font-size: 13px; color: var(--text-secondary); margin: 2px 0 16px 0;">Your registered subjects and performance status</p>
    </div>
    """, unsafe_allow_html=True)
    
    if not subjects:
        st.markdown("""
        <div class="empty-state-container">
          <span style="font-size: 2rem;">📚</span>
          <h4 class="empty-state-title">No Subjects Enrolled</h4>
          <p class="empty-state-subtitle">Enroll in your first subject to begin attendance tracking.</p>
        </div>
        """, unsafe_allow_html=True)
        return
        
    chunk_size = 3
    for chunk_idx in range(0, len(subjects), chunk_size):
        chunk = subjects[chunk_idx : chunk_idx + chunk_size]
        cols = st.columns(3, gap="medium")
        for i, sub in enumerate(chunk):
            with cols[i]:
                render_subject_card(sub, student_id)




def render_activity_timeline(metrics):
    timeline_data = metrics["timeline"]
    
    st.markdown("""
    <div style="margin-top: 24px; margin-bottom: 12px;">
      <h3 style="font-size: 16px; font-weight: 600; color: #111111; margin: 0;">Recent Activity Timeline</h3>
      <p style="font-size: 13px; color: var(--color-gray); margin: 2px 0 16px 0;">Chronological verification and check-in feed</p>
    </div>
    """, unsafe_allow_html=True)
    
    if not timeline_data:
        st.markdown("""
        <div class="empty-state-container">
          <span style="font-size: 2rem;">🕒</span>
          <h4 class="empty-state-title">No Attendance Activity</h4>
          <p class="empty-state-subtitle">Your attendance history will appear here once you begin marking attendance.</p>
        </div>
        """, unsafe_allow_html=True)
        return
        
    grouped_items = {}
    for item in timeline_data:
        g = item["group"]
        if g not in grouped_items:
            grouped_items[g] = []
        grouped_items[g].append(item)
        
    group_order = ["Today", "Yesterday", "Last 7 Days", "Earlier"]
    
    timeline_html = '<div class="timeline-container">'
    
    idx = 0
    for g in group_order:
        if g not in grouped_items:
            continue
            
        timeline_html += f'<div class="timeline-group-header">{g}</div>'
        
        for item in grouped_items[g]:
            status_class = item["status"].lower()
            
            conf_badge = ""
            if item.get("confidence") and status_class == "present":
                conf_badge = f'<span class="timeline-confidence font-monospace">{item["confidence"]}% match</span>'
                
            delay = idx * 40
            timeline_html += f"""
            <div class="timeline-row animate-timeline-item" style="animation-delay: {delay}ms;">
              <div class="timeline-left">
                <div class="timeline-dot {status_class}">{item["icon"]}</div>
                <div class="timeline-line"></div>
              </div>
              <div class="timeline-content">
                <div class="timeline-title-row">
                  <div class="timeline-event-header">
                    <span class="timeline-subject">{item["subject"]}</span>
                    <span class="timeline-method-badge">{item["method"]}</span>
                  </div>
                  <span class="status-pill {status_class}">{item["status"]}</span>
                </div>
                <div class="timeline-meta-row">
                  <span class="timeline-time">{item["time_str"]}</span>
                  {conf_badge}
                </div>
              </div>
            </div>
            """
            idx += 1
            
    timeline_html += '</div>'
    
    st.markdown(f"""
    <div class="kpi-card" style="margin-top: 10px; margin-bottom: 24px;">
      {timeline_html}
    </div>
    """, unsafe_allow_html=True)


def student_dashboard():
    sd         = st.session_state.student_data
    student_id = sd["student_id"]
    name       = sd["name"]

    # Retrieve all teachers once to map teacher_id to name
    try:
        from src.database.config import supabase
        teachers_data = supabase.table("teachers").select("teacher_id, name").execute().data
        teachers_map = {t["teacher_id"]: t["name"] for t in teachers_data}
    except Exception:
        teachers_map = {}

    # Render navbar
    _topnav(name, "Student")

    # Action bar
    t1, t2, t3, _ = st.columns([1.2, 1.2, 1.2, 4.4], gap="small")
    with t1:
        if st.button("＋ Enroll Subject", type="primary", use_container_width=True, key="action_enroll"):
            enroll_dialog()
    with t2:
        if st.button("⇄ Teacher Mode", type="secondary", use_container_width=True, key="action_teacher"):
            st.session_state["login_type"] = "teacher"
            st.rerun()
    with t3:
        if st.button("Sign Out", type="secondary", use_container_width=True, key="action_signout"):
            st.session_state["is_logged_in"] = False
            del st.session_state.student_data
            st.rerun()

    # Load data
    with st.spinner("Loading your dashboard…"):
        subjects = get_student_subjects(student_id)
        logs     = get_student_attendance(student_id)

    # Compute calculations
    stats_map    = {}
    subjects_map = {}
    for sn in subjects:
        s = sn.get("subjects", {})
        if s:
            subjects_map[s.get("subject_id")] = s
    for log in logs:
        sid = log["subject_id"]
        if sid not in stats_map:
            stats_map[sid] = {"total": 0, "attended": 0}
        stats_map[sid]["total"] += 1
        if log.get("is_present"):
            stats_map[sid]["attended"] += 1

    total_all    = sum(v["total"]    for v in stats_map.values()) if stats_map else 0
    attended_all = sum(v["attended"] for v in stats_map.values()) if stats_map else 0
    pct_all      = int(attended_all / total_all * 100) if total_all > 0 else 0

    # Call modular dashboard metrics provider
    metrics = prepare_dashboard_metrics(student_id, name, logs, stats_map, pct_all, subjects_map, teachers_map)

    # Keep compatibility aliases for unchanged layout sections (Phases 2-6)
    trend_str = metrics["risk"]["trend_str"]
    trend_color = metrics["risk"]["trend_color"]
    trend_arrow = metrics["risk"]["trend_arrow"]
    status_label = metrics["risk"]["status_label"]
    status_class = metrics["risk"]["status_class"]
    today_str = datetime.now().strftime("%A, %d %B %Y")
    motivation_msg = metrics["coach"]["coach_tip"]
    greeting = datetime.now().strftime("%I:%M %p")

    # Greeting based on local time
    current_hour = datetime.now().hour
    if current_hour < 12:
        greeting = "Good Morning 👋"
    elif current_hour < 18:
        greeting = "Good Afternoon 👋"
    else:
        greeting = "Good Evening 👋"

    # Dynamic motivational hero message
    if pct_all >= 85:
        motivation_msg = "Excellent attendance. Keep it up."
    elif pct_all >= 75:
        motivation_msg = "You're on track."
    else:
        motivation_msg = "Attendance needs attention."

    # Hero card status badge info
    if pct_all >= 85:
        status_label = "Safe"
        status_class = "safe"
    elif pct_all >= 75:
        status_label = "Warning"
        status_class = "warning"
    else:
        status_label = "At Risk"
        status_class = "at-risk"

    # Current date and day
    today_str = datetime.now().strftime("%A, %d %B %Y")

    # Compute attendance momentum (trend)
    now = datetime.now()
    two_weeks_ago = now - timedelta(days=14)
    four_weeks_ago = now - timedelta(days=28)
    
    recent_total = 0
    recent_attended = 0
    older_total = 0
    older_attended = 0
    
    for log in logs:
        ts_raw = log.get("timestamp")
        if not ts_raw:
            continue
        try:
            log_dt = datetime.fromisoformat(ts_raw)
            if log_dt.tzinfo is not None:
                log_dt = log_dt.replace(tzinfo=None)
            
            naive_now = now.replace(tzinfo=None)
            naive_2w = two_weeks_ago.replace(tzinfo=None)
            naive_4w = four_weeks_ago.replace(tzinfo=None)
            
            if naive_4w <= log_dt < naive_2w:
                older_total += 1
                if log.get("is_present"):
                    older_attended += 1
            elif naive_2w <= log_dt <= naive_now:
                recent_total += 1
                if log.get("is_present"):
                    recent_attended += 1
        except Exception:
            pass

    recent_rate = (recent_attended / recent_total) if recent_total > 0 else 0.0
    older_rate = (older_attended / older_total) if older_total > 0 else 0.0

    if recent_total == 0 and older_total == 0:
        trend_str = "Stable"
        trend_color = "#64748B"
        trend_arrow = "→"
    else:
        diff = recent_rate - older_rate
        if diff > 0.01:
            trend_str = "Improving"
            trend_color = "#22C55E"
            trend_arrow = "↑"
        elif diff < -0.01:
            trend_str = "Declining"
            trend_color = "#EF4444"
            trend_arrow = "↓"
        else:
            trend_str = "Stable"
            trend_color = "#64748B"
            trend_arrow = "→"

    # HTML inject header & hero & stylesheet & scripts
    st.markdown(f"""
<style>
:root {{
  /* Design Tokens */
  --color-primary: #5865F2;
  --color-success: #22C55E;
  --color-warning: #FFD600;
  --color-danger: #EF4444;
  --color-gray: #64748B;
  --color-bg-light: #FAFAFA;
  
  --border-thick: 2.5px solid #111111;
  --border-thin: 1.5px solid #111111;
  --shadow-offset: 4px 4px 0 #111111;
  
  /* Typography Scale */
  --font-family-display: 'Outfit', sans-serif;
  --font-family-body: 'Inter', sans-serif;
  --font-weight-display: 800;
  --font-weight-bold: 700;
  --font-weight-medium: 600;
  --font-weight-normal: 500;
  --font-size-display: 1.6rem;
  --font-size-title: 1.2rem;
  --font-size-body: 0.95rem;
  --font-size-hint: 0.72rem;
}}

/* Global resets and chrome removal */
#MainMenu, footer, header {{
  visibility: hidden !important;
  height: 0 !important;
}}

.block-container {{
  padding-top: 1rem !important;
  padding-left: 1.5rem !important;
  padding-right: 1.5rem !important;
  background: radial-gradient(circle at 50% 0%, rgba(88, 101, 242, 0.06) 0%, #FAFAFA 70%) !important;
  font-family: var(--font-family-body), -apple-system, BlinkMacSystemFont, sans-serif !important;
}}

/* Shimmer and Glow Animations */
@keyframes shimmer {{
  0% {{ background-position: -200% 0; }}
  100% {{ background-position: 200% 0; }}
}}
.shimmer-text {{
  background: linear-gradient(90deg, #111111 20%, var(--color-primary) 50%, #111111 80%);
  background-size: 200% auto;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  animation: shimmer 3s infinite linear;
  display: inline-block;
}}

/* Avatar Glow */
.avatar-container::before {{
  content: '';
  position: absolute;
  top: -4px;
  left: -4px;
  right: -4px;
  bottom: -4px;
  background: radial-gradient(circle, rgba(88, 101, 242, 0.45) 0%, transparent 70%);
  z-index: 1;
  border-radius: 50%;
  animation: pulseGlow 2.5s infinite alternate;
}}
@keyframes pulseGlow {{
  0% {{ transform: scale(0.95); opacity: 0.4; }}
  100% {{ transform: scale(1.1); opacity: 0.9; }}
}}

/* Hero Pills */
.hero-left-metrics-grid {{
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 12px;
  margin-bottom: 4px;
}}
.hero-pill {{
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background: #FFFFFF !important;
  border: var(--border-thin) !important;
  border-radius: 20px !important;
  padding: 4px 10px !important;
  font-family: var(--font-family-body) !important;
  font-size: 0.72rem !important;
  font-weight: var(--font-weight-bold) !important;
  color: #111111 !important;
  box-shadow: 1px 1px 0 #111111 !important;
  transition: transform 0.2s !important;
}}
.hero-pill:hover {{
  transform: translateY(-1px);
}}
.hero-pill-icon {{
  font-size: 0.85rem;
}}
.hero-pill-lbl {{
  color: var(--color-gray);
  font-weight: var(--font-weight-normal);
}}

/* Sections spacing */
.student-dashboard-root {{
  display: flex;
  flex-direction: column;
  gap: 24px;
}}

/* Animations */
@keyframes fadeIn {{
  from {{ opacity: 0; transform: translateY(12px); }}
  to {{ opacity: 1; transform: translateY(0); }}
}}

.animate-fade-in {{
  animation: fadeIn 0.4s ease-out forwards;
}}

.hover-lift {{
  transition: transform 0.25s ease, box-shadow 0.25s ease, border-color 0.25s ease;
}}
.hover-lift:hover {{
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(99, 102, 241, 0.12);
  border-color: var(--color-primary);
}}

/* Hero / Command Center Styles */
.hero-card {{
  background: #FFFFFF !important;
  border: var(--border-thick) !important;
  border-radius: 16px !important;
  padding: 24px !important;
  color: #111111 !important;
  box-shadow: var(--shadow-offset) !important;
}}
.hero-container {{
  display: flex;
  justify-content: space-between;
  align-items: stretch;
  flex-wrap: wrap;
  gap: 20px;
}}
.hero-left {{
  flex: 1;
  min-width: 280px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  gap: 16px;
}}
.hero-profile-row {{
  display: flex;
  align-items: center;
  gap: 14px;
}}
.avatar-container {{
  position: relative;
  width: 56px;
  height: 56px;
  flex-shrink: 0;
}}
.hero-avatar {{
  width: 100%;
  height: 100%;
  border-radius: 8px;
  border: var(--border-thick);
  background: linear-gradient(135deg, var(--color-primary) 0%, #3B82F6 100%);
  color: #FFFFFF;
  display: flex;
  align-items: center;
  justify-content: center;
  font-family: var(--font-family-display);
  font-size: 1.4rem;
  font-weight: var(--font-weight-display);
  box-shadow: 2px 2px 0 #111111;
}}
.avatar-online-indicator {{
  position: absolute;
  bottom: -2px;
  right: -2px;
  width: 12px;
  height: 12px;
  background: var(--color-success);
  border: 2px solid #FFFFFF;
  border-radius: 50%;
  box-shadow: 1px 1px 0 #111111;
  animation: pulseOpacity 1s infinite alternate;
}}
.avatar-verified-badge {{
  position: absolute;
  top: -6px;
  right: -6px;
  width: 16px;
  height: 16px;
  background: #3B82F6;
  color: #FFFFFF;
  font-size: 0.65rem;
  font-weight: 800;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  border: 1.5px solid #FFFFFF;
  box-shadow: 1px 1px 0 #111111;
}}
.hero-greeting-col {{
  display: flex;
  flex-direction: column;
}}
.hero-greeting {{
  font-family: var(--font-family-body);
  font-size: 0.85rem;
  font-weight: var(--font-weight-bold);
  text-transform: uppercase;
  color: var(--color-gray);
  letter-spacing: 0.05em;
}}
.hero-student-name {{
  font-family: var(--font-family-display);
  font-size: var(--font-size-display);
  font-weight: var(--font-weight-display);
  color: #111111;
  letter-spacing: -0.02em;
}}
.hero-meta-section {{
  display: flex;
  flex-direction: column;
  gap: 4px;
  border-top: var(--border-thin);
  padding-top: 12px;
}}
.hero-meta-item {{
  display: flex;
  align-items: center;
  gap: 8px;
}}
.hero-meta-label {{
  font-family: var(--font-family-body);
  font-size: 0.65rem;
  font-weight: var(--font-weight-bold);
  color: var(--color-gray);
  text-transform: uppercase;
}}
.hero-meta-val {{
  font-family: monospace;
  font-size: 0.8rem;
  font-weight: var(--font-weight-bold);
  color: #111111;
}}
.hero-coach-tip {{
  font-family: var(--font-family-body);
  font-size: var(--font-size-body);
  font-weight: var(--font-weight-medium);
  color: #333333;
  border: var(--border-thin);
  border-left: 4px solid var(--color-primary);
  padding: 12px;
  background: rgba(88, 101, 242, 0.05);
  margin-top: 16px;
  border-radius: 8px;
}}
.hero-right-console {{
  flex: 1;
  min-width: 300px;
  background: var(--color-bg-light);
  border: var(--border-thick);
  border-radius: 12px;
  padding: 16px;
  box-shadow: var(--shadow-offset);
  display: flex;
  flex-direction: column;
  gap: 12px;
}}
.console-header {{
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: var(--border-thin);
  padding-bottom: 6px;
  font-family: var(--font-family-display);
  font-size: var(--font-size-hint);
  font-weight: var(--font-weight-bold);
  color: var(--color-gray);
  text-transform: uppercase;
}}
.console-status-dot {{
  display: inline-flex;
  align-items: center;
  gap: 4px;
  color: var(--color-success);
}}
.console-status-dot::before {{
  content: '';
  width: 6px;
  height: 6px;
  background: var(--color-success);
  border-radius: 50%;
  animation: pulseOpacity 1s infinite alternate;
}}
@keyframes pulseOpacity {{
  0% {{ opacity: 0.4; }}
  100% {{ opacity: 1; }}
}}
.console-main-layout {{
  display: flex;
  gap: 8px;
  align-items: stretch;
}}
.overall-item {{
  flex: 1.2;
}}
.console-sub-item-box {{
  flex: 0.8;
  display: flex;
  flex-direction: column;
  padding: 6px 10px;
  background: #FFFFFF;
  border: var(--border-thin);
  border-radius: 6px;
  justify-content: center;
}}
.console-val-large {{
  font-family: var(--font-family-display);
  font-size: 1.8rem;
  font-weight: var(--font-weight-display);
  color: #111111;
  line-height: 1.1;
  letter-spacing: -0.02em;
  margin-top: 2px;
}}
.console-grid {{
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 8px;
}}
.console-item {{
  display: flex;
  flex-direction: column;
  padding: 6px 10px;
  background: #FFFFFF;
  border: var(--border-thin);
  border-radius: 6px;
}}
.console-label {{
  font-family: var(--font-family-body);
  font-size: 0.65rem;
  font-weight: var(--font-weight-bold);
  color: var(--color-gray);
  text-transform: uppercase;
  letter-spacing: 0.02em;
}}
.console-val {{
  font-family: var(--font-family-display);
  font-size: var(--font-size-title);
  font-weight: var(--font-weight-display);
  color: #111111;
  margin-top: 1px;
}}
.console-hint {{
  font-family: var(--font-family-body);
  font-size: 0.58rem;
  color: var(--color-gray);
  margin-top: 1px;
}}
.console-val.val-safe {{ color: var(--color-success); }}
.console-val.val-warning {{ color: #D97706; }}
.console-val.val-danger {{ color: var(--color-danger); }}
.console-val.val-at-risk {{ color: var(--color-danger); }}
.console-val.val-gray {{ color: var(--color-gray); }}



/* AI Coach / Workspace Styles */
.ai-coach-card {{
  background: #FFFFFF !important;
  border: var(--border-thick) !important;
  border-radius: 16px !important;
  padding: 20px !important;
  color: #111111 !important;
  box-shadow: var(--shadow-offset) !important;
  min-height: 240px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}}
.ai-coach-header {{
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: var(--border-thin);
  padding-bottom: 8px;
  font-family: var(--font-family-display);
  font-size: var(--font-size-body);
  font-weight: var(--font-weight-display);
  text-transform: uppercase;
  color: #111111;
}}
.ai-coach-badge {{
  font-size: 0.65rem;
  font-weight: var(--font-weight-bold);
  padding: 2px 8px;
  border-radius: 4px;
  border: var(--border-thin);
  background: var(--color-bg-light);
}}
.ai-coach-badge.val-safe {{
  background: rgba(34, 197, 94, 0.15);
  color: var(--color-success);
}}
.ai-coach-badge.val-warning {{
  background: rgba(255, 214, 0, 0.15);
  color: #B45309;
}}
.ai-coach-badge.val-critical {{
  background: rgba(239, 68, 68, 0.15);
  color: var(--color-danger);
}}
.ai-coach-grid {{
  display: grid;
  grid-template-columns: 1fr;
  gap: 8px;
  margin-top: 10px;
  flex-grow: 1;
}}
.ai-coach-cell {{
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px dashed rgba(0, 0, 0, 0.1);
  padding-bottom: 4px;
}}
.ai-coach-cell:last-child {{
  border-bottom: none;
}}
.ai-coach-label {{
  font-family: var(--font-family-body);
  font-size: 0.72rem;
  font-weight: var(--font-weight-medium);
  color: var(--color-gray);
}}
.ai-coach-val {{
  font-family: var(--font-family-body);
  font-size: 0.78rem;
  font-weight: var(--font-weight-bold);
  color: #111111;
  text-align: right;
  max-width: 60%;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}}
.ai-coach-empty-state {{
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  flex-grow: 1;
  gap: 6px;
  margin-top: 10px;
}}

/* Quick Actions Cards */
.action-card {{
  background: #FFFFFF !important;
  border: var(--border-thin) !important;
  border-radius: 12px !important;
  padding: 16px !important;
  display: flex;
  flex-direction: column;
  height: 110px;
  justify-content: center;
  transition: transform var(--transition-normal), box-shadow var(--transition-normal), border-color var(--transition-normal);
  box-shadow: var(--shadow-sm) !important;
}}
.action-card:hover {{
  transform: var(--hover-lift);
  box-shadow: var(--hover-shadow) !important;
  border-color: var(--color-primary) !important;
}}
.action-icon {{
  font-size: 20px;
  margin-bottom: 6px;
}}
.action-title {{
  font-family: var(--font-family-display);
  font-size: var(--font-size-body);
  font-weight: var(--font-weight-bold);
  color: #111111;
}}
.action-sub {{
  font-family: var(--font-family-body);
  font-size: 0.72rem;
  color: var(--color-gray);
  margin-top: 2px;
}}

/* Custom styling for the Streamlit download button as a module card */
div[data-testid="stDownloadButton"] > button {{
  background: #FFFFFF !important;
  border: var(--border-thick) !important;
  border-radius: 16px !important;
  box-shadow: var(--shadow-offset) !important;
  color: #111111 !important;
  transition: transform 0.2s, box-shadow 0.2s !important;
  padding: 12px 16px !important;
  font-family: var(--font-family-display) !important;
  font-size: 13px !important;
  min-height: 80px !important;
  text-align: left !important;
  align-items: flex-start !important;
  display: flex !important;
  flex-direction: column !important;
  justify-content: center !important;
  line-height: 1.3 !important;
  width: 100% !important;
}}
div[data-testid="stDownloadButton"] > button:hover {{
  transform: var(--hover-lift) !important;
  box-shadow: var(--hover-shadow) !important;
  border-color: var(--color-primary) !important;
}}
div[data-testid="stDownloadButton"] > button p {{
  margin: 0 !important;
  font-family: var(--font-family-display) !important;
  font-size: var(--font-size-body) !important;
  font-weight: var(--font-weight-bold) !important;
  color: #111111 !important;
}}
div[data-testid="stDownloadButton"] > button::after {{
  content: 'Save history to local CSV';
  font-family: var(--font-family-body);
  font-size: 0.72rem;
  color: var(--color-gray);
  margin-top: 2px;
  font-weight: 400;
}}

/* Analytics Workspace */
.analytics-summary-card {{
  background: #FFFFFF !important;
  border: var(--border-thick) !important;
  border-radius: 16px !important;
  padding: 20px !important;
  color: #111111 !important;
  box-shadow: var(--shadow-offset) !important;
  min-height: 285px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}}
.analytics-header {{
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: var(--border-thin);
  padding-bottom: 8px;
  font-family: var(--font-family-display);
  font-size: var(--font-size-body);
  font-weight: var(--font-weight-display);
  text-transform: uppercase;
  color: #111111;
}}
/* Charts Workspace */
.chart-container-wrapper {{
  position: relative;
  padding: 20px;
  background: #FFFFFF;
  border: var(--border-thick);
  border-radius: 16px;
  box-shadow: var(--shadow-offset);
  margin-bottom: 8px;
}}
.chart-container {{
  position: relative;
  height: 180px;
  margin-top: 10px;
  border-bottom: var(--border-thin);
  display: flex;
  align-items: flex-end;
  justify-content: space-around;
  padding-left: 55px;
}}
.chart-y-axis {{
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 50px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  font-family: monospace;
  font-size: 8px;
  color: var(--color-gray);
  text-align: right;
  padding-right: 8px;
}}
.chart-gridline {{
  position: absolute;
  left: 55px;
  right: 0;
  height: 1px;
  background-color: rgba(0, 0, 0, 0.05);
  z-index: 1;
}}
.chart-ref-line {{
  position: absolute;
  left: 55px;
  right: 0;
  border-top: 1.5px dashed;
  z-index: 2;
}}
.ref-line-lbl {{
  position: absolute;
  right: 8px;
  top: -8px;
  font-family: var(--font-family-body);
  font-size: 7px;
  font-weight: 700;
  color: #FFFFFF;
  padding: 1px 6px;
  border-radius: 3px;
  text-transform: uppercase;
  z-index: 5;
  letter-spacing: 0.03em;
}}
.chart-bar-wrapper {{
  display: flex;
  flex-direction: column;
  align-items: center;
  flex: 1;
  max-width: 60px;
  height: 100%;
  justify-content: flex-end;
  position: relative;
  z-index: 4;
}}
@keyframes barGrow {{
  from {{ height: 0%; }}
  to {{ height: var(--bar-height); }}
}}
.chart-bar {{
  width: 24px;
  border-top-left-radius: 6px !important;
  border-top-right-radius: 6px !important;
  height: 0%;
  animation: barGrow 0.8s cubic-bezier(0.16, 1, 0.3, 1) forwards;
  position: relative;
  cursor: pointer;
  transition: transform 0.2s ease, box-shadow 0.2s ease !important;
}}
.chart-bar.safe {{
  background: linear-gradient(180deg, var(--color-success) 0%, rgba(34, 197, 94, 0.4) 100%) !important;
}}
.chart-bar.warning {{
  background: linear-gradient(180deg, var(--color-warning) 0%, rgba(245, 158, 11, 0.4) 100%) !important;
}}
.chart-bar.critical {{
  background: linear-gradient(180deg, var(--color-danger) 0%, rgba(239, 68, 68, 0.4) 100%) !important;
}}
.chart-bar:hover {{
  transform: translateY(-4px) !important;
  box-shadow: 0 4px 12px rgba(0,0,0,0.15) !important;
}}
.chart-bar .tooltip-text {{
  visibility: hidden;
  width: 130px;
  background-color: #111111;
  color: #FFFFFF;
  text-align: left;
  border-radius: 6px;
  padding: 8px;
  position: absolute;
  z-index: 100;
  bottom: 110%;
  left: 50%;
  transform: translateX(-50%);
  opacity: 0;
  transition: opacity 0.2s, transform 0.2s;
  font-family: var(--font-family-body);
  font-size: 10px;
  line-height: 1.3;
  box-shadow: var(--shadow-sm);
  pointer-events: none;
}}
.chart-bar .tooltip-text::after {{
  content: "";
  position: absolute;
  top: 100%;
  left: 50%;
  margin-left: -5px;
  border-width: 5px;
  border-style: solid;
  border-color: #111111 transparent transparent transparent;
}}
.chart-bar:hover .tooltip-text {{
  visibility: visible;
  opacity: 1;
}}
.chart-x-label {{
  font-family: var(--font-family-body);
  font-size: 9px;
  color: var(--color-gray);
  margin-top: 6px;
  text-align: center;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  width: 100%;
}}

/* Legends */
.chart-legend-container {{
  display: flex;
  justify-content: center;
  gap: 16px;
  margin-top: 12px;
}}
.legend-item {{
  display: flex;
  align-items: center;
  gap: 6px;
  font-family: var(--font-family-body);
  font-size: 10px;
  color: var(--color-gray);
}}
.legend-dot {{
  width: 10px;
  height: 10px;
  border-radius: 50%;
  display: inline-block;
}}
.legend-dot.dot-safe {{ background-color: var(--color-success); }}
.legend-dot.dot-warning {{ background-color: var(--color-warning); }}
.legend-dot.dot-average {{ background-color: var(--color-primary); }}

/* Empty States */
.chart-empty-state {{
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  padding: 32px 16px;
  border: 2px dashed rgba(0, 0, 0, 0.12) !important;
  border-radius: 12px !important;
  background: var(--color-bg-light) !important;
  max-width: 100% !important;
  margin: 10px auto !important;
  gap: 8px;
}}
.empty-state-title {{
  font-family: var(--font-family-display);
  font-size: 13px !important;
  font-weight: 600 !important;
  color: #111111 !important;
  margin: 0 !important;
}}
.empty-state-subtitle {{
  font-family: var(--font-family-body);
  font-size: 11px !important;
  color: var(--color-gray) !important;
  margin: 0 !important;
}}

/* Customizing Streamlit Tabs */
div[data-testid="stTabs"] button {{
  font-family: var(--font-family-display) !important;
  font-weight: 600 !important;
  font-size: 13px !important;
  color: var(--color-gray) !important;
  background: transparent !important;
  border: none !important;
  border-bottom: 2px solid transparent !important;
  padding: 8px 16px !important;
  transition: all 0.2s ease !important;
}}
div[data-testid="stTabs"] button[aria-selected="true"] {{
  color: var(--color-primary) !important;
  border-bottom: 2px solid var(--color-primary) !important;
}}
div[data-testid="stTabs"] button:hover {{
  color: var(--color-primary) !important;
  opacity: 0.8;
}}
div[data-testid="stTabs"] [data-testid="stTabBorder"] {{
  border-bottom: 1.5px solid rgba(0, 0, 0, 0.08) !important;
}}

.spark-line-graphic {{
  height: 60px;
  border-bottom: 1.5px dashed var(--color-gray);
  position: relative;
  margin-top: 10px;
}}
.spark-line-graphic::before {{
  content: '';
  position: absolute;
  left: 0;
  right: 0;
  height: 100%;
  background-repeat: no-repeat;
  background-size: contain;
  background-position: center;
}}
.spark-line-graphic.trend-improving::before {{
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 30' fill='none' stroke='%2322C55E' stroke-width='2'%3E%3Cpath d='M0,25 C20,22 40,15 60,18 C80,10 90,5 100,2'/%3E%3C/svg%3E");
}}
.spark-line-graphic.trend-declining::before {{
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 30' fill='none' stroke='%23EF4444' stroke-width='2'%3E%3Cpath d='M0,5 C20,8 40,15 60,12 C80,20 90,25 100,28'/%3E%3C/svg%3E");
}}
.spark-line-graphic.trend-stable::before {{
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 30' fill='none' stroke='%2364748B' stroke-width='2'%3E%3Cpath d='M0,15 C30,16 60,14 100,15'/%3E%3C/svg%3E");
}}

/* Subject Cards Workspace */
.subject-card {{
  background: #FFFFFF !important;
  border: var(--border-thick) !important;
  border-radius: 16px !important;
  padding: 20px !important;
  color: #111111 !important;
  box-shadow: var(--shadow-offset) !important;
  transition: transform 0.2s, box-shadow 0.2s;
  display: flex;
  flex-direction: column;
  gap: 12px;
}}
.subject-card:hover {{
  transform: var(--hover-lift);
  box-shadow: var(--hover-shadow) !important;
}}
.subject-card.safe {{ border-color: var(--color-success) !important; }}
.subject-card.warning {{ border-color: var(--color-warning) !important; }}
.subject-card.critical {{ border-color: var(--color-danger) !important; }}

.subject-header {{
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}}
.subject-title {{
  font-family: var(--font-family-display);
  font-size: 1.1rem;
  font-weight: var(--font-weight-display);
  color: #111111;
  line-height: 1.2;
}}
.subject-faculty {{
  font-family: var(--font-family-body);
  font-size: 0.72rem;
  color: var(--color-gray);
  margin-top: 2px;
}}
.status-badge-small {{
  font-family: var(--font-family-display);
  font-size: 0.58rem;
  font-weight: var(--font-weight-bold);
  padding: 2px 6px;
  border-radius: 4px;
  border: var(--border-thin);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}}
.status-badge-small.safe {{
  background: rgba(34, 197, 94, 0.15);
  color: var(--color-success);
}}
.status-badge-small.warning {{
  background: rgba(255, 214, 0, 0.15);
  color: #B45309;
}}
.status-badge-small.critical {{
  background: rgba(239, 68, 68, 0.15);
  color: var(--color-danger);
}}

.subject-divider {{
  border-top: 1px dashed rgba(0, 0, 0, 0.1);
  margin: 10px 0;
}}

.subject-metric-row {{
  display: flex;
  justify-content: space-between;
  align-items: center;
}}
.subject-metric-label {{
  font-family: var(--font-family-body);
  font-size: 0.78rem;
  font-weight: var(--font-weight-medium);
  color: var(--color-gray);
}}
.subject-metric-val {{
  font-family: var(--font-family-display);
  font-size: 1.3rem;
  font-weight: var(--font-weight-display);
}}
.subject-metric-val.val-safe {{ color: var(--color-success); }}
.subject-metric-val.val-warning {{ color: #B45309; }}
.subject-metric-val.val-critical {{ color: var(--color-danger); }}

.progress-track-wrapper {{
  position: relative;
  width: 100%;
  padding: 8px 0;
}}
.progress-bar-track {{
  height: 8px;
  background-color: var(--color-bg-light);
  border-radius: 4px;
  border: var(--border-thin);
  overflow: hidden;
}}
.progress-bar-fill {{
  height: 100%;
  border-radius: 2px;
}}
.progress-bar-fill.safe {{ background: var(--color-success); }}
.progress-bar-fill.warning {{ background: var(--color-warning); }}
.progress-bar-fill.critical {{ background: var(--color-danger); }}

.progress-marker {{
  position: absolute;
  top: 2px;
  width: 3px;
  height: 20px;
  background: #111111;
  z-index: 10;
}}
.progress-marker::after {{
  content: attr(title);
  position: absolute;
  bottom: 110%;
  left: 50%;
  transform: translateX(-50%);
  background: #111111;
  color: #FFFFFF;
  font-size: 8px;
  padding: 2px 4px;
  border-radius: 4px;
  white-space: nowrap;
  display: none;
}}
.progress-marker:hover::after {{
  display: block;
}}

/* Grid Details */
.subject-details-grid,
.subject-forecast-grid {{
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 8px;
  text-align: center;
}}
.details-cell,
.forecast-cell {{
  display: flex;
  flex-direction: column;
}}
.details-label,
.forecast-label {{
  font-family: var(--font-family-body);
  font-size: 0.58rem;
  color: var(--color-gray);
  text-transform: uppercase;
}}
.details-val,
.forecast-val {{
  font-family: var(--font-family-display);
  font-size: 0.85rem;
  font-weight: var(--font-weight-bold);
  color: #111111;
  margin-top: 2px;
}}
.subject-ai-tip {{
  font-family: var(--font-family-body);
  font-size: 0.72rem;
  color: #333333;
  background: var(--color-bg-light);
  padding: 8px;
  border-radius: 6px;
  border-left: 2.5px solid var(--color-primary);
}}

/* Streamlit button custom dashboard widget overrides */
div[data-testid="stButton"] button[key^="action_"] {{
  background: #FFFFFF !important;
  border: var(--border-thick) !important;
  border-radius: 16px !important;
  box-shadow: var(--shadow-offset) !important;
  color: #111111 !important;
  transition: transform 0.2s, box-shadow 0.2s !important;
  padding: 12px 16px !important;
  font-family: var(--font-family-display) !important;
  font-size: 13px !important;
  min-height: 80px !important;
  text-align: left !important;
  align-items: flex-start !important;
  display: flex !important;
  flex-direction: column !important;
  justify-content: center !important;
  line-height: 1.3 !important;
}}
div[data-testid="stButton"] button[key^="action_"]:hover {{
  transform: var(--hover-lift) !important;
  box-shadow: var(--hover-shadow) !important;
  border-color: var(--color-primary) !important;
}}
div[data-testid="stButton"] button[key^="action_"] p {{
  margin: 0 !important;
  font-weight: var(--font-weight-bold) !important;
}}

/* Unenroll Button low priority secondary override */
div[data-testid="stButton"] button[key^="unenroll_"] {{
  background: transparent !important;
  color: var(--color-gray) !important;
  border: var(--border-thin) !important;
  border-radius: 8px !important;
  font-size: 11px !important;
  font-weight: 500 !important;
  padding: 4px 10px !important;
  height: auto !important;
  margin-top: 8px !important;
  transition: all 0.2s ease !important;
  width: 100% !important;
}}
div[data-testid="stButton"] button[key^="unenroll_"]:hover {{
  color: var(--color-danger) !important;
  border-color: var(--color-danger) !important;
  background-color: rgba(239, 68, 68, 0.05) !important;
}}
.stat-lbl {{
  font-size: 10px;
  color: var(--text-secondary);
  margin-top: 2px;
}}

/* Custom styling to place Unenroll button below cards neatly */
div[data-testid="stButton"] button[key^="unenroll_"]/* Timeline Workspace */
.timeline-container {{
  display: flex;
  flex-direction: column;
  position: relative;
  padding-left: 10px;
}}
.timeline-group-header {{
  font-family: var(--font-family-display);
  font-size: 0.8rem;
  font-weight: var(--font-weight-display);
  color: var(--color-primary);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin: 16px 0 12px 0;
}}
.timeline-group-header:first-child {{
  margin-top: 4px;
}}
.timeline-row {{
  display: flex;
  align-items: flex-start;
  padding-bottom: 18px;
  position: relative;
}}
.timeline-left {{
  width: 36px;
  display: flex;
  flex-direction: column;
  align-items: center;
  position: relative;
  align-self: stretch;
}}
.timeline-dot {{
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: #FFFFFF;
  border: var(--border-thin);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.8rem;
  z-index: 2;
  box-shadow: 1px 1px 0 #111111;
}}
.timeline-dot.present {{
  border-color: var(--color-success);
}}
.timeline-dot.absent {{
  border-color: var(--color-danger);
}}
.timeline-line {{
  position: absolute;
  top: 26px;
  bottom: -18px;
  width: 1.5px;
  background-color: #111111;
  z-index: 1;
}}
.timeline-row:last-child .timeline-line {{
  display: none;
}}
.timeline-content {{
  flex: 1;
  padding-left: 14px;
  display: flex;
  flex-direction: column;
  gap: 4px;
}}
.timeline-title-row {{
  display: flex;
  justify-content: space-between;
  align-items: center;
}}
.timeline-event-header {{
  display: flex;
  align-items: center;
  gap: 8px;
}}
.timeline-subject {{
  font-family: var(--font-family-display);
  font-size: 0.85rem;
  font-weight: var(--font-weight-bold);
  color: #111111;
}}
.timeline-method-badge {{
  font-family: var(--font-family-body);
  font-size: 0.65rem;
  color: var(--color-gray);
  background: var(--color-bg-light);
  padding: 1px 6px;
  border-radius: 4px;
  border: 1px solid rgba(0, 0, 0, 0.08);
}}
.status-pill {{
  font-family: var(--font-family-display);
  font-size: 0.58rem;
  font-weight: var(--font-weight-bold);
  padding: 2px 8px;
  border-radius: 4px;
  border: var(--border-thin);
}}
.status-pill.present {{
  background: rgba(34, 197, 94, 0.15);
  color: var(--color-success);
  border-color: var(--color-success);
}}
.status-pill.absent {{
  background: rgba(239, 68, 68, 0.15);
  color: var(--color-danger);
  border-color: var(--color-danger);
}}
.timeline-meta-row {{
  display: flex;
  align-items: center;
  gap: 12px;
}}
.timeline-time {{
  font-family: monospace;
  font-size: 0.72rem;
  color: var(--color-gray);
}}
.timeline-confidence {{
  font-size: 0.68rem;
  color: var(--color-primary);
  background: rgba(88, 101, 242, 0.1);
  padding: 1px 4px;
  border-radius: 2px;
}}

/* Redesigned Hero Control Center Layout */
.hero-card {{
  background: #FFFFFF !important;
  border: var(--border-thick) !important;
  border-radius: 20px !important;
  padding: 0 !important;
  overflow: hidden !important;
  box-shadow: var(--shadow-offset) !important;
  margin-bottom: 24px !important;
}}
.hero-container {{
  display: flex;
  flex-wrap: wrap;
  align-items: stretch;
}}
.hero-identity-sidebar {{
  flex: 1;
  min-width: 320px;
  background: var(--color-bg-light);
  border-right: var(--border-thick);
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}}
.hero-analytics-console {{
  flex: 1.8;
  min-width: 420px;
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 18px;
  background: #FFFFFF;
}}

/* Sidebar Elements */
.sidebar-profile-header {{
  display: flex;
  align-items: center;
  gap: 14px;
}}
.sidebar-profile-info {{
  display: flex;
  flex-direction: column;
}}
.sidebar-student-name {{
  font-family: var(--font-family-display);
  font-size: 1.35rem;
  font-weight: var(--font-weight-display);
  color: #111111;
  line-height: 1.1;
}}
.sidebar-dept {{
  font-family: var(--font-family-body);
  font-size: 0.75rem;
  font-weight: var(--font-weight-bold);
  color: var(--color-gray);
  margin-top: 2px;
}}
.sidebar-sem {{
  font-family: monospace;
  font-size: 0.68rem;
  color: #333333;
}}
.sidebar-divider {{
  border-top: 1.5px dashed rgba(0,0,0,0.1);
  margin: 4px 0;
}}
.pills-deck-title,
.agenda-deck-title,
.summary-title {{
  font-family: var(--font-family-display);
  font-size: 0.65rem;
  font-weight: var(--font-weight-bold);
  color: var(--color-gray);
  letter-spacing: 0.05em;
  display: block;
  margin-bottom: 8px;
}}
.sidebar-pills-grid {{
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}}
.sidebar-tag {{
  font-family: var(--font-family-body);
  font-size: 0.62rem;
  font-weight: var(--font-weight-bold);
  padding: 2px 8px;
  border-radius: 4px;
  border: var(--border-thin);
  text-transform: uppercase;
}}
.sidebar-tag.success {{
  background: rgba(34, 197, 94, 0.15);
  color: var(--color-success);
}}
.sidebar-tag.info {{
  background: rgba(88, 101, 242, 0.15);
  color: var(--color-primary);
}}
.sidebar-tag.warning {{
  background: rgba(255, 214, 0, 0.15);
  color: #B45309;
}}
.sidebar-ai-summary p {{
  font-family: var(--font-family-body);
  font-size: 0.78rem;
  color: #333333;
  margin: 0;
  line-height: 1.4;
}}

/* Agenda items */
.agenda-deck {{
  display: flex;
  flex-direction: column;
  gap: 8px;
}}
.agenda-item {{
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: #FFFFFF;
  border: var(--border-thin);
  border-radius: 8px;
  padding: 8px 12px;
}}
.agenda-meta {{
  display: flex;
  flex-direction: column;
}}
.agenda-time {{
  font-family: monospace;
  font-size: 0.7rem;
  color: var(--color-gray);
}}
.agenda-subject {{
  font-family: var(--font-family-display);
  font-size: 0.8rem;
  font-weight: var(--font-weight-bold);
  color: #111111;
}}
.agenda-status {{
  font-family: var(--font-family-display);
  font-size: 0.58rem;
  font-weight: var(--font-weight-bold);
  padding: 2px 6px;
  border-radius: 4px;
  border: var(--border-thin);
}}
.agenda-status.present {{
  background: rgba(34, 197, 94, 0.15);
  color: var(--color-success);
}}
.agenda-status.upcoming {{
  background: rgba(88, 101, 242, 0.15);
  color: var(--color-primary);
}}

/* Analytics Console Elements */
.console-top-row {{
  display: flex;
  justify-content: space-between;
  align-items: center;
}}
.console-main-kpi-block {{
  display: flex;
  flex-direction: column;
}}
.console-label-uppercase {{
  font-family: var(--font-family-display);
  font-size: 0.68rem;
  font-weight: var(--font-weight-bold);
  color: var(--color-gray);
  letter-spacing: 0.08em;
}}
.console-large-val-shimmer {{
  font-family: var(--font-family-display);
  font-size: 3.5rem;
  font-weight: var(--font-weight-display);
  line-height: 1.0;
  margin: 6px 0;
  letter-spacing: -0.04em;
}}
.console-comparison-chip {{
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-family: var(--font-family-display);
  font-size: 0.65rem;
  font-weight: var(--font-weight-bold);
  border: var(--border-thin);
  border-radius: 20px;
  padding: 2px 10px;
  width: fit-content;
}}
.console-comparison-chip.safe {{
  background: rgba(34, 197, 94, 0.15);
  color: var(--color-success);
}}
.console-comparison-chip.warning {{
  background: rgba(255, 214, 0, 0.15);
  color: #B45309;
}}
.console-comparison-chip.critical {{
  background: rgba(239, 68, 68, 0.15);
  color: var(--color-danger);
}}
.status-pulse-dot {{
  width: 6px;
  height: 6px;
  border-radius: 50%;
}}
.status-pulse-dot.safe {{
  background: var(--color-success);
  box-shadow: 0 0 6px var(--color-success);
}}
.status-pulse-dot.warning {{
  background: #B45309;
  box-shadow: 0 0 6px #B45309;
}}
.status-pulse-dot.critical {{
  background: var(--color-danger);
  box-shadow: 0 0 6px var(--color-danger);
}}

/* Circular Progress Ring */
.console-circular-gauge {{
  position: relative;
  width: 80px;
  height: 80px;
}}
.circular-chart {{
  display: block;
  max-width: 100%;
  max-height: 100%;
}}
.circle-bg {{
  fill: none;
  stroke: var(--color-bg-light);
  stroke-width: 3.8;
}}
.circle {{
  fill: none;
  stroke-width: 3.8;
  stroke-linecap: round;
  animation: progress 1s ease-out forwards;
}}
.circular-chart.safe .circle {{ stroke: var(--color-success); }}
.circular-chart.warning .circle {{ stroke: var(--color-warning); }}
.circular-chart.critical .circle {{ stroke: var(--color-danger); }}

.gauge-percentage-overlay {{
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  font-family: var(--font-family-display);
  font-size: 0.9rem;
  font-weight: var(--font-weight-display);
  color: #111111;
}}

/* Console Warning Banner */
.console-alert-banner {{
  border: var(--border-thin);
  border-radius: 8px;
  padding: 12px 16px;
  font-family: var(--font-family-body);
  font-size: 0.8rem;
  color: #111111;
  box-shadow: 2px 2px 0 #111111;
}}
.console-alert-banner.safe {{
  background: rgba(34, 197, 94, 0.08);
  border-color: var(--color-success);
}}
.console-alert-banner.warning {{
  background: rgba(255, 214, 0, 0.08);
  border-color: #B45309;
}}
.console-alert-banner.critical {{
  background: rgba(239, 68, 68, 0.08);
  border-color: var(--color-danger);
}}

/* Metrics Row */
.console-metrics-row {{
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}}
.console-sub-metric {{
  background: var(--color-bg-light);
  border: var(--border-thin);
  border-radius: 8px;
  padding: 10px 14px;
  display: flex;
  flex-direction: column;
}}
.metric-lbl {{
  font-family: var(--font-family-body);
  font-size: 0.58rem;
  font-weight: var(--font-weight-bold);
  color: var(--color-gray);
  letter-spacing: 0.03em;
}}
.metric-val {{
  font-family: var(--font-family-display);
  font-size: 1.1rem;
  font-weight: var(--font-weight-display);
  color: #111111;
  margin-top: 2px;
}}
.metric-desc {{
  font-family: var(--font-family-body);
  font-size: 0.62rem;
  color: var(--color-gray);
  margin-top: 1px;
}}
.console-divider {{
  border-top: var(--border-thin);
  margin: 4px 0;
}}

/* Sparkline Trend Chart Overlay */
.console-trend-chart-deck {{
  display: flex;
  flex-direction: column;
  gap: 8px;
}}
.trend-chart-header {{
  display: flex;
  justify-content: space-between;
  align-items: center;
}}
.trend-direction-badge {{
  font-family: var(--font-family-display);
  font-size: 0.65rem;
  font-weight: var(--font-weight-bold);
  text-transform: uppercase;
}}
.trend-direction-badge.safe {{ color: var(--color-success); }}
.trend-direction-badge.warning {{ color: #B45309; }}
.trend-direction-badge.critical {{ color: var(--color-danger); }}

.sparkline-container-card {{
  height: 48px;
  border: var(--border-thin);
  border-radius: 8px;
  overflow: hidden;
  background: var(--color-bg-light);
  padding: 4px;
}}
.sparkline-graphic-svg {{
  width: 100%;
  height: 100%;
}}
.sparkline-line {{
  fill: none;
  stroke: var(--color-primary);
  stroke-width: 2.2;
}}
.sparkline-area {{
  stroke: none;
}}

/* Redesigned Analytics Console & Gauges */
.overall-progress-chart-card {{
  background: var(--color-bg-light);
  border: var(--border-thin);
  border-radius: 12px;
  padding: 20px;
}}
.gauge-grid-container {{
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 24px;
}}
.gauge-visual-box {{
  position: relative;
  width: 140px;
  height: 140px;
  flex-shrink: 0;
}}
.circular-chart-large {{
  display: block;
  max-width: 100%;
  max-height: 100%;
}}
.circle-bg-large {{
  fill: none;
  stroke: rgba(0, 0, 0, 0.05);
  stroke-width: 3.2;
}}
.circle-large {{
  fill: none;
  stroke-width: 3.2;
  stroke-linecap: round;
  transition: stroke-dasharray 0.8s ease-in-out;
}}
.circular-chart-large.safe .circle-large {{ stroke: var(--color-success); }}
.circular-chart-large.warning .circle-large {{ stroke: var(--color-warning); }}
.circular-chart-large.critical .circle-large {{ stroke: var(--color-danger); }}

.gauge-large-overlay {{
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  display: flex;
  flex-direction: column;
  align-items: center;
}}
.gauge-large-val {{
  font-family: var(--font-family-display);
  font-size: 1.8rem;
  font-weight: var(--font-weight-display);
  color: #111111;
  line-height: 1.0;
}}
.gauge-large-lbl {{
  font-family: var(--font-family-body);
  font-size: 0.58rem;
  font-weight: var(--font-weight-bold);
  color: var(--color-gray);
  margin-top: 2px;
}}
.gauge-breakdown-details {{
  flex: 1;
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}}
.breakdown-metric-item {{
  display: flex;
  flex-direction: column;
}}
.breakdown-lbl {{
  font-family: var(--font-family-body);
  font-size: 0.58rem;
  color: var(--color-gray);
  letter-spacing: 0.03em;
}}
.breakdown-val {{
  font-family: var(--font-family-display);
  font-size: 0.95rem;
  font-weight: var(--font-weight-bold);
  color: #111111;
  margin-top: 2px;
}}
.breakdown-val.val-safe {{ color: var(--color-success); }}
.breakdown-val.val-warning {{ color: #B45309; }}
.breakdown-val.val-critical {{ color: var(--color-danger); }}

/* Empty State Cards */
.empty-state-container {{
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 48px 24px;
  background: var(--card-bg);
  border: 2px dashed var(--border-color);
  border-radius: 16px;
  text-align: center;
  max-width: 480px;
  margin: 20px auto;
}}
.empty-state-svg {{
  color: var(--text-secondary);
  margin-bottom: 16px;
  animation: float 3s ease-in-out infinite;
}}
@keyframes float {{
  0%, 100% {{ transform: translateY(0); }}
  50% {{ transform: translateY(-4px); }}
}}
.empty-state-title {{
  font-size: 15px;
  font-weight: 600;
}}
</style>
""", unsafe_allow_html=True)

    # SECTION 1: HERO CARD
    render_student_command_center(metrics)

    # SECTION 2: AI COACH & QUICK ACTIONS WORKSPACE
    col_coach, col_actions = st.columns([1.3, 1.7], gap="medium")
    with col_coach:
        render_ai_workspace(metrics)
    with col_actions:
        render_quick_actions(metrics, logs, subjects_map, name)

    st.markdown('<div style="height:12px"></div>', unsafe_allow_html=True)

    # SECTION 3 & 4: ANALYTICS WORKSPACE
    render_analytics_workspace(metrics)

    # SECTION 6: SUBJECT PERFORMANCE GRID
    render_subject_grid(metrics, student_id)

    # SECTION 7: RECENT ACTIVITY TIMELINE
    render_activity_timeline(metrics)

    # SECTION 8: FOOTER SUMMARY
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if pct_all >= 85:
        footer_msg = "Outstanding! Keep maintaining this standard."
    elif pct_all >= 75:
        footer_msg = "Good job! Stay consistent to keep your status safe."
    else:
        footer_msg = "Take action. Reach out to your instructors and prioritize attending the next sessions."

    st.markdown(f"""
    <div style="border-top: 1px solid var(--border-color); padding-top: 16px; margin-top: 32px; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px;">
      <div>
        <span style="font-size: 12px; color: var(--text-secondary);">Current Status: </span>
        <span class="status-badge-small {status_class}" style="display: inline-block;">{status_label}</span>
        <span style="font-size: 12px; color: var(--text-secondary); margin-left: 8px;">{footer_msg}</span>
      </div>
      <div style="font-size: 11px; color: var(--text-hint);">
        Last synced: {now_str} (Local Time)
      </div>
    </div>
    """, unsafe_allow_html=True)

    # Injected Javascript for Counter and Progress animations
    st.markdown("""
<script>
(function() {
  const root = document.getElementById("student-dashboard-root");
  if (root && !root.getAttribute("data-animated")) {
    root.setAttribute("data-animated", "true");

    // Value counter animation
    function animateValue(id, duration) {
      const obj = document.getElementById(id);
      if (!obj) return;
      const end = parseFloat(obj.getAttribute("data-target"));
      if (isNaN(end) || end === 0) {
        obj.innerText = "0" + (id.includes("pct") ? "%" : "");
        return;
      }
      const isPercent = id.includes("pct");
      let start = 0;
      let current = start;
      const range = end - start;
      const stepTime = Math.max(10, Math.floor(duration / range));
      const timer = setInterval(() => {
        current += 1;
        if (current >= end) {
          obj.innerText = end + (isPercent ? "%" : "");
          clearInterval(timer);
        } else {
          obj.innerText = current + (isPercent ? "%" : "");
        }
      }, stepTime);
    }

    // Run animations
    setTimeout(() => {
      animateValue("hero-pct-counter", 1000);
      animateValue("kpi-subjects-counter", 1000);
      animateValue("kpi-total-counter", 1000);
      animateValue("kpi-attended-counter", 1000);
      animateValue("kpi-pct-counter", 1000);

      // SVG circular progress fill animation (Phase 1 - removed as we use high-density key values layout)
      const fillCircle = document.getElementById("hero-progress-ring-fill");
      if (fillCircle) {
        const pctObj = document.getElementById("hero-pct-counter");
        if (pctObj) {
          const targetPct = parseFloat(pctObj.getAttribute("data-target")) || 0;
          const targetOffset = 251.327 * (1 - targetPct / 100);
          fillCircle.style.strokeDashoffset = targetOffset;
        }
      }
    }, 100);
  }
})();
</script>
""", unsafe_allow_html=True)

    footer_dashboard()


# ════════════════════════════════════════════════════════════════════════════
# LOGIN  — split layout
# ════════════════════════════════════════════════════════════════════════════
def student_screen():
    style_background_dashboard()
    style_base_layout()

    if "student_data" in st.session_state:
        student_dashboard()
        return

    st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
.sal{{background:linear-gradient(145deg,#6366F1 0%,#818CF8 60%,#6366F1 100%);
  border-radius:20px;padding:3rem 2.5rem;display:flex;flex-direction:column;
  justify-content:center;min-height:540px;}}
.sal h2{{font-size:1.55rem!important;font-weight:900!important;color:#fff!important;
  letter-spacing:-0.04em!important;margin-bottom:0.75rem!important;
  font-family:'Inter',sans-serif!important;}}
.sal p{{font-size:0.87rem!important;color:rgba(255,255,255,0.72)!important;
  line-height:1.65!important;margin-bottom:1.75rem!important;
  font-family:'Inter',sans-serif!important;}}
.sal ul{{list-style:none;padding:0;margin:0;}}
.sal li{{font-size:0.81rem;color:rgba(255,255,255,0.85);font-family:'Inter',sans-serif;
  margin-bottom:10px;display:flex;align-items:center;gap:10px;}}
.sal-ck{{width:20px;height:20px;border-radius:50%;background:rgba(255,255,255,0.18);
  display:flex;align-items:center;justify-content:center;font-size:0.62rem;
  color:#fff;flex-shrink:0;}}
.sar{{background:#fff;border:1px solid #E2E8F0;border-radius:20px;padding:2.25rem 2rem;}}
.sar-logo{{display:flex;align-items:center;gap:10px;margin-bottom:1.5rem;}}
.sar-logo .wm{{font-family:'Inter',sans-serif;font-size:1rem;font-weight:800;
  color:#6366F1;letter-spacing:-0.03em;}}
</style>
""", unsafe_allow_html=True)

    bc, _ = st.columns([1, 4])
    with bc:
        if st.button("← Home", type="secondary"):
            st.session_state["login_type"] = None
            st.rerun()
    st.markdown('<div style="height:8px"></div>', unsafe_allow_html=True)

    lc, rc = st.columns([1, 1.1], gap="large")

    with lc:
        st.markdown(f"""
<div class="sal">
  <div style="margin-bottom:1.5rem;">{_LOGO}</div>
  <h2>Student Login</h2>
  <p>Sign in with Face ID instantly — no password, no typing. Just look at the camera.</p>
  <ul>
    <li><span class="sal-ck">✓</span> Instant AI face recognition login</li>
    <li><span class="sal-ck">✓</span> View attendance across all subjects</li>
    <li><span class="sal-ck">✓</span> Track your attendance percentage live</li>
    <li><span class="sal-ck">✓</span> Join subjects via QR code</li>
    <li><span class="sal-ck">✓</span> Attendance trend charts and history</li>
  </ul>
</div>""", unsafe_allow_html=True)

    with rc:
        st.markdown(f"""
<div class="sar">
  <div class="sar-logo">{_LOGO}<span class="wm">SmartAttend</span></div>
  <div style="font-size:1.2rem;font-weight:800;color:#0F172A;letter-spacing:-0.03em;
       font-family:'Inter',sans-serif;margin-bottom:4px;">Sign in with Face ID</div>
  <div style="font-size:0.82rem;color:#64748B;font-family:'Inter',sans-serif;
       margin-bottom:1.25rem;">Position your face in the camera frame below.</div>
""", unsafe_allow_html=True)

        show_reg = False
        photo = st.camera_input("Look directly at the camera")

        if photo:
            img = np.array(Image.open(photo))
            with st.spinner("Scanning with AI…"):
                detected, _, num_faces = predict_attendance(img)
                if num_faces == 0:
                    st.warning("No face detected. Move closer and ensure good lighting.")
                elif num_faces > 1:
                    st.warning("Multiple faces detected. Only one person should be in frame.")
                else:
                    if detected:
                        sid_key = list(detected.keys())[0]
                        all_st  = get_all_students()
                        student = next(
                            (s for s in all_st if s["student_id"] == sid_key), None
                        )
                        if student:
                            st.session_state.is_logged_in = True
                            st.session_state.user_role    = "student"
                            st.session_state.student_data = student
                            st.toast(f"Welcome back, {student['name']}! 👋")
                            time.sleep(0.8)
                            st.rerun()
                    else:
                        st.info("Face not recognised. Register below if you are new.")
                        show_reg = True

        st.markdown("</div>", unsafe_allow_html=True)

        if show_reg:
            st.markdown("""
<div style="background:#F5F3FF;border:1px solid #DDD6FE;border-radius:14px;
     padding:1.5rem 1.75rem;margin-top:1rem;">
  <div style="font-size:0.68rem;font-weight:700;text-transform:uppercase;
       letter-spacing:0.08em;color:#7C3AED;margin-bottom:1rem;
       font-family:'Inter',sans-serif;">✨ New Student — Create Profile</div>
""", unsafe_allow_html=True)
            new_name = st.text_input("Full Name", placeholder="e.g. Priya Sharma")
            audio_data = None
            try:
                audio_data = st.audio_input("Optional: record your voice for voice-based attendance")
            except Exception:
                pass
            if st.button("Create Account →", type="primary", use_container_width=True):
                if new_name:
                    with st.spinner("Setting up your profile…"):
                        encodings = get_face_embeddings(np.array(Image.open(photo)))
                        if encodings:
                            face_emb  = encodings[0].tolist()
                            voice_emb = None
                            if audio_data:
                                voice_emb = get_voice_embedding(audio_data.read())
                            resp = create_student(
                                new_name,
                                face_embedding=face_emb,
                                voice_embedding=voice_emb,
                            )
                            if resp:
                                train_classifier()
                                st.session_state.is_logged_in = True
                                st.session_state.user_role    = "student"
                                st.session_state.student_data = resp[0]
                                st.toast(f"Welcome, {new_name}! 🎉")
                                time.sleep(0.8)
                                st.rerun()
                        else:
                            st.error("Could not capture face features. Retake photo.")
                else:
                    st.warning("Please enter your full name.")
            st.markdown("</div>", unsafe_allow_html=True)

    footer_dashboard()
