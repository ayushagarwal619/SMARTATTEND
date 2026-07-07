"""SmartAttend — Landing Page.
Redesigned with Neo-Brutalism design system.
Features: Face Recognition, QR Joining, Attendance Analytics, Secure Records.
"""
import streamlit as st
from datetime import datetime
from src.components.header import header_home
from src.components.footer import footer_home
from src.ui.base_layout import style_base_layout, style_background_home

# ── Dynamic live mockup dashboard ─────────────────────────────────────────────
def get_mockup_dashboard_html():
    # Fetch real telemetry from Supabase
    try:
        from src.database.config import supabase
        subjects_data = supabase.table("subjects").select("subject_id").execute().data
        students_data = supabase.table("students").select("student_id").execute().data
        logs_data = supabase.table("attendance_logs").select("is_present").execute().data
        
        total_subjects = len(subjects_data)
        total_students = len(students_data)
        total_logs = len(logs_data)
        
        if total_logs > 0:
            present_count = sum(1 for r in logs_data if r.get("is_present"))
            absent_count = total_logs - present_count
            attendance_pct = (present_count / total_logs) * 100
        else:
            present_count = 0
            absent_count = 0
            attendance_pct = 0.0

        # Query recent activity feed
        recent_logs = supabase.table("attendance_logs").select("*, students(name), subjects(subject_code)").order("timestamp", desc=True).limit(3).execute().data
        recent_activities = []
        for log in recent_logs:
            stu_name = log.get("students", {}).get("name", "Student")
            sub_code = log.get("subjects", {}).get("subject_code", "CS301")
            is_present = log.get("is_present", False)
            ts = log.get("timestamp", "")
            time_str = ts.split("T")[1][:5] if "T" in ts else "12:00"
            recent_activities.append({
                "name": stu_name,
                "subject": sub_code,
                "status": "Present" if is_present else "Absent",
                "time": time_str
            })
    except Exception:
        # Fallback values if DB connection fails
        total_subjects = 6
        total_students = 120
        total_logs = 480
        present_count = 420
        absent_count = 60
        attendance_pct = 87.5
        recent_activities = [
            {"name": "Ankit Kumar", "subject": "CS301", "status": "Present", "time": "09:15"},
            {"name": "Rahul Verma", "subject": "CS405", "status": "Present", "time": "11:00"},
            {"name": "Sneha Gupta", "subject": "CS301", "status": "Absent", "time": "14:15"}
        ]

    # Render recent activity items
    activity_items_html = ""
    for act in recent_activities:
        status_cls = "present" if act["status"] == "Present" else "absent"
        status_char = "✓" if act["status"] == "Present" else "✗"
        activity_items_html += f"""
        <div class="feed-item {status_cls}">
          <span class="feed-name">{act['name']}</span>
          <span>{act['subject']}</span>
          <span class="feed-time">{status_char} {act['time']}</span>
        </div>"""

    current_time_str = datetime.now().strftime("%H:%M")
    
    return f"""
<div class="dashboard-window" style="animation: floatCard 6s infinite ease-in-out; will-change: transform;">
  <!-- header -->
  <div class="window-header" style="background:#111; color:#fff; padding:8px 12px; display:flex; align-items:center; justify-content:space-between; border-bottom:3px solid #111;">
    <div class="window-dots" style="display:flex; gap:6px;">
      <span class="dot red" style="width:8px; height:8px; border-radius:50%; background:#EF4444; border:1px solid #000;"></span>
      <span class="dot yellow" style="width:8px; height:8px; border-radius:50%; background:#FACC15; border:1px solid #000;"></span>
      <span class="dot green" style="width:8px; height:8px; border-radius:50%; background:#22C55E; border:1px solid #000;"></span>
    </div>
    <span class="window-title" style="font-size:0.7rem; font-weight:800; font-family:monospace; letter-spacing:0.05em;">SMARTATTEND AI SCAN SERVER v2.0</span>
    <span class="window-status" style="font-size:0.65rem; font-weight:800; color:#22C55E; font-family:monospace;"><span class="live-dot" style="width:5px; height:5px; background:#EF4444; border-radius:50%; display:inline-block; margin-right:4px;"></span> LIVE SCAN</span>
  </div>
  
  <div class="window-body" style="display:flex; background:#ffffff; height:380px;">
    <!-- left side: webcam viewport -->
    <div class="webcam-viewport" style="position:relative; background:#E8ECEF; overflow:hidden; flex:1.15; border-right:2px solid #111111; height:100%; display:flex; align-items:center; justify-content:center;">
      
      <!-- Multi-stage scanner box -->
      <div class="demo-scanner-container" data-stage="1" style="position:relative; width:100%; height:100%; display:flex; align-items:center; justify-content:center; overflow:hidden;">
        <div class="webcam-grid" style="position:absolute; inset:0; background-image:linear-gradient(to right, rgba(0,0,0,0.06) 1px, transparent 1px), linear-gradient(to bottom, rgba(0,0,0,0.06) 1px, transparent 1px); background-size:16px 16px;"></div>
        
        <!-- Neural Network Overlay Mesh -->
        <svg style="position:absolute; inset:0; width:100%; height:100%; pointer-events:none; opacity:0.15;" xmlns="http://www.w3.org/2000/svg">
          <line x1="20" y1="50" x2="80" y2="120" stroke="#5865F2" stroke-width="1.5" stroke-dasharray="2 2"/>
          <line x1="80" y1="120" x2="160" y2="60" stroke="#5865F2" stroke-width="1.5"/>
          <line x1="160" y1="60" x2="220" y2="180" stroke="#5865F2" stroke-width="1.5" stroke-dasharray="2 2"/>
          <circle cx="20" cy="50" r="3" fill="#5865F2"/>
          <circle cx="80" cy="120" r="3" fill="#5865F2"/>
          <circle cx="160" cy="60" r="3" fill="#5865F2"/>
        </svg>

        <!-- Stage 1 View: UPLOADER -->
        <div class="upload-stage-view" style="position:absolute; inset:0; display:flex; flex-direction:column; align-items:center; justify-content:center; background:rgba(255,255,255,0.92); z-index:4; transition: opacity 0.5s;">
          <div style="font-size:2.8rem; margin-bottom:8px; animation: pulseUpload 1.5s infinite ease-in-out;">📤</div>
          <div style="font-family:'Outfit', sans-serif; font-size:0.85rem; font-weight:900; color:#111; text-transform:uppercase; letter-spacing:0.02em;">Uploading media...</div>
          <div style="font-family:monospace; font-size:0.6rem; color:var(--color-gray); margin-top:4px;">Resolving source: classroom_photo.png</div>
        </div>

        <!-- Stage 2+ View: CLASSROOM PHOTO + LASER -->
        <div class="scan-stage-view" style="position:absolute; inset:0; display:block;">
          <!-- Laser sweep line -->
          <div class="scanner-bar" style="position:absolute; left:0; width:100%; height:4px; background:linear-gradient(90deg, transparent, #22C55E, transparent); box-shadow:0 0 10px rgba(34,197,94,0.8); z-index:5;"></div>

          <!-- Student Face 1 Box -->
          <div class="student-face-node s1" style="position:absolute; top:25%; left:12%; width:100px; height:100px; transition: opacity 0.3s; opacity:0;">
            <div class="face-box" style="position:absolute; inset:8px; border:3px solid #22C55E; border-radius:6px;">
              <div class="corner tl" style="position:absolute; width:10px; height:10px; border:2px solid #22C55E; top:-2px; left:-2px; border-right:0; border-bottom:0;"></div>
              <div class="corner tr" style="position:absolute; width:10px; height:10px; border:2px solid #22C55E; top:-2px; right:-2px; border-left:0; border-bottom:0;"></div>
              <div class="corner bl" style="position:absolute; width:10px; height:10px; border:2px solid #22C55E; bottom:-2px; left:-2px; border-right:0; border-top:0;"></div>
              <div class="corner br" style="position:absolute; width:10px; height:10px; border:2px solid #22C55E; bottom:-2px; right:-2px; border-left:0; border-top:0;"></div>
              <span class="face-tag face-name-lbl" style="position:absolute; bottom:-24px; left:50%; transform:translateX(-50%); background:#22C55E; color:#fff; font-size:0.65rem; font-weight:800; padding:2px 6px; border-radius:4px; border:1.5px solid #111; white-space:nowrap; box-shadow:1.5px 1.5px 0 #111; font-family:'Outfit',sans-serif; opacity:0; transition: opacity 0.3s;">Rohan · Verified 98%</span>
            </div>
            <!-- Face landmarks mesh -->
            <svg viewBox="0 0 100 100" style="position:absolute; inset:0; width:100%; height:100%; pointer-events:none;">
              <circle cx="35" cy="40" r="2" fill="#22C55E"/>
              <circle cx="65" cy="40" r="2" fill="#22C55E"/>
              <circle cx="50" cy="55" r="2" fill="#22C55E"/>
              <path d="M 40,70 Q 50,75 60,70" fill="none" stroke="#22C55E" stroke-width="1.5"/>
              <line x1="35" y1="40" x2="50" y2="55" stroke="rgba(34, 197, 94, 0.4)" stroke-width="1"/>
              <line x1="65" y1="40" x2="50" y2="55" stroke="rgba(34, 197, 94, 0.4)" stroke-width="1"/>
            </svg>
          </div>
          
          <!-- Student Face 2 Box -->
          <div class="student-face-node s2" style="position:absolute; top:20%; right:12%; width:90px; height:90px; transition: opacity 0.3s; opacity:0;">
            <div class="face-box" style="position:absolute; inset:8px; border:3px solid #5865F2; border-radius:6px;">
              <div class="corner tl" style="position:absolute; width:10px; height:10px; border:2px solid #5865F2; top:-2px; left:-2px; border-right:0; border-bottom:0;"></div>
              <div class="corner tr" style="position:absolute; width:10px; height:10px; border:2px solid #5865F2; top:-2px; right:-2px; border-left:0; border-bottom:0;"></div>
              <div class="corner bl" style="position:absolute; width:10px; height:10px; border:2px solid #5865F2; bottom:-2px; left:-2px; border-right:0; border-top:0;"></div>
              <div class="corner br" style="position:absolute; width:10px; height:10px; border:2px solid #5865F2; bottom:-2px; right:-2px; border-left:0; border-top:0;"></div>
              <span class="face-tag face-name-lbl" style="position:absolute; bottom:-24px; left:50%; transform:translateX(-50%); background:#5865F2; color:#fff; font-size:0.65rem; font-weight:800; padding:2px 6px; border-radius:4px; border:1.5px solid #111; white-space:nowrap; box-shadow:1.5px 1.5px 0 #111; font-family:'Outfit',sans-serif; opacity:0; transition: opacity 0.3s;">Sneha · Verified 96%</span>
            </div>
            <!-- Face landmarks mesh -->
            <svg viewBox="0 0 100 100" style="position:absolute; inset:0; width:100%; height:100%; pointer-events:none;">
              <circle cx="35" cy="40" r="2" fill="#5865F2"/>
              <circle cx="65" cy="40" r="2" fill="#5865F2"/>
              <circle cx="50" cy="55" r="2" fill="#5865F2"/>
              <path d="M 40,70 Q 50,73 60,70" fill="none" stroke="#5865F2" stroke-width="1.5"/>
              <line x1="35" y1="40" x2="50" y2="55" stroke="rgba(88, 101, 242, 0.4)" stroke-width="1"/>
              <line x1="65" y1="40" x2="50" y2="55" stroke="rgba(88, 101, 242, 0.4)" stroke-width="1"/>
            </svg>
          </div>

          <!-- Present Status Badges -->
          <div class="status-badge s1-badge" style="position:absolute; top:25%; left:12%; background:#22C55E; color:#fff; font-size:0.55rem; font-weight:900; padding:2px 6px; border:1.5px solid #000; border-radius:4px; box-shadow:1.5px 1.5px 0 #000; opacity:0; transition: opacity 0.3s; z-index:6; font-family:'Outfit', sans-serif;">✅ PRESENT</div>
          <div class="status-badge s2-badge" style="position:absolute; top:20%; right:12%; background:#22C55E; color:#fff; font-size:0.55rem; font-weight:900; padding:2px 6px; border:1.5px solid #000; border-radius:4px; box-shadow:1.5px 1.5px 0 #000; opacity:0; transition: opacity 0.3s; z-index:6; font-family:'Outfit', sans-serif;">✅ PRESENT</div>
        </div>

        <!-- Live Waveform Visualizer -->
        <div class="waveform-container" style="position:absolute; bottom:8px; left:8px; display:flex; gap:3px; align-items:flex-end; height:18px; z-index:6;">
          <div class="wave-bar" style="width:3px; background:#22C55E; border-radius:2px; height:80%; animation:wavePulse 1.2s infinite ease-in-out; animation-delay:0.1s;"></div>
          <div class="wave-bar" style="width:3px; background:#22C55E; border-radius:2px; height:40%; animation:wavePulse 1.2s infinite ease-in-out; animation-delay:0.3s;"></div>
          <div class="wave-bar" style="width:3px; background:#22C55E; border-radius:2px; height:95%; animation:wavePulse 1.2s infinite ease-in-out; animation-delay:0.5s;"></div>
          <div class="wave-bar" style="width:3px; background:#22C55E; border-radius:2px; height:60%; animation:wavePulse 1.2s infinite ease-in-out; animation-delay:0.2s;"></div>
        </div>

        <!-- Success Notification Popup -->
        <div class="success-popup" style="position:absolute; bottom:8px; right:8px; background:#FFF; border:2px solid #111; border-radius:4px; padding:4px 8px; display:flex; align-items:center; gap:5px; box-shadow:2px 2px 0 #111; opacity:0; transition: transform 0.5s, opacity 0.5s; z-index:7;">
          <div class="success-icon" style="width:14px; height:14px; background:#22C55E; border:1px solid #111; border-radius:50%; color:#fff; display:flex; align-items:center; justify-content:center; font-weight:900; font-size:0.6rem;">✓</div>
          <div style="text-align:left;">
            <span class="success-title" style="font-size:0.6rem; font-weight:900; color:#22C55E; display:block; line-height:1;">CHECK-IN OK</span>
            <span class="success-sub" style="font-size:0.52rem; font-weight:700; color:#555; display:block;">Class Roll updated</span>
          </div>
        </div>
      </div>
      
    </div>
    
    <!-- right side: panel -->
    <div class="right-pane" style="flex:0.85; display:flex; flex-direction:column; background:#ffffff; border-left:2px solid #111111; height:100%;">
      <div class="verification-panel" style="padding:14px; border-bottom:2px solid #111111; font-family:'Outfit',sans-serif; text-align:left;">
        <div class="panel-header" style="display:flex; justify-content:space-between; align-items:center;">
          <span class="panel-badge" style="font-size:0.65rem; font-weight:800; text-transform:uppercase; color:#64748b;">Telemetry</span>
          <div class="verified-indicator" style="background:rgba(34,197,94,0.12); color:#22C55E; border:1.5px solid #22C55E; padding:2px 6px; border-radius:4px; font-size:0.65rem; font-weight:800; display:flex; align-items:center; gap:4px;">
            <span class="vi-dot" style="width:5px; height:5px; background:#22C55E; border-radius:50%;"></span> ACTIVE
          </div>
        </div>
        <div class="panel-title" style="font-size:0.9rem; font-weight:900; text-transform:uppercase; color:#111; margin-top:4px; margin-bottom:8px;">REAL-TIME DATABASE</div>
        
        <div class="panel-details" style="display:flex; flex-direction:column; gap:6px;">
          <div class="detail-row" style="display:flex; justify-content:space-between; align-items:center;">
            <span class="detail-label" style="font-size:0.65rem; color:#64748b; font-weight:600;">SUBJECTS</span>
            <span class="detail-val" style="font-size:0.8rem; color:#111; font-weight:800;">{total_subjects}</span>
          </div>
          <div class="detail-row" style="display:flex; justify-content:space-between; align-items:center;">
            <span class="detail-label" style="font-size:0.65rem; color:#64748b; font-weight:600;">STUDENTS</span>
            <span class="detail-val" style="font-size:0.8rem; color:#111; font-weight:800;">{total_students}</span>
          </div>
          <div class="detail-row" style="display:flex; justify-content:space-between; align-items:center;">
            <span class="detail-label" style="font-size:0.65rem; color:#64748b; font-weight:600;">ATTENDANCE RATE</span>
            <span class="detail-val" style="font-size:0.8rem; color:#5865F2; font-weight:800;">{attendance_pct:.1f}%</span>
          </div>
          <div class="detail-row" style="display:flex; justify-content:space-between; align-items:center;">
            <span class="detail-label" style="font-size:0.65rem; color:#64748b; font-weight:600;">SERVER TIME</span>
            <span class="detail-val" style="font-size:0.8rem; color:#111; font-weight:800;">{current_time_str}</span>
          </div>
        </div>
        
        <!-- Mini SVG Trend Graph -->
        <div style="margin-top:8px; text-align:left;">
          <span class="detail-label" style="font-size:0.65rem; color:#64748b; font-weight:600; display:block; margin-bottom:4px;">WEEKLY ACTIVITY TREND</span>
          <svg viewBox="0 0 160 30" width="100%" height="24" style="background:#FAFAFA; border:1.5px solid #111111; border-radius:4px;">
            <path d="M 0,20 Q 20,5 40,15 T 80,10 T 120,25 T 160,5" fill="none" stroke="#5865F2" stroke-width="2"/>
            <path d="M 0,20 Q 20,5 40,15 T 80,10 T 120,25 T 160,5 L 160,30 L 0,30 Z" fill="rgba(88,101,242,0.15)" stroke="none"/>
          </svg>
        </div>
      </div>
      
      <div class="activity-feed" style="padding:14px; flex-grow:1; display:flex; flex-direction:column; font-family:'Outfit',sans-serif; text-align:left;">
        <div class="feed-title" style="font-size:0.75rem; font-weight:900; text-transform:uppercase; color:#111; margin-bottom:8px;">RECENT CHECKS</div>
        <div class="feed-list" style="display:flex; flex-direction:column; gap:6px; overflow-y:auto; max-height:130px;">
          {activity_items_html}
        </div>
      </div>
    </div>
  </div>
</div>

<!-- Live Dashboard Panel below the scanner window -->
<div class="live-dashboard-panel" style="background:#FFFFFF; border:3px solid #000000; border-radius:12px; box-shadow:4px 4px 0 #000000; padding:16px; margin-top:20px; text-align:left; font-family:'Outfit',sans-serif;">
  <div style="font-size:0.75rem; font-weight:900; color:var(--color-primary); letter-spacing:0.05em; text-transform:uppercase; margin-bottom:12px;">📊 LIVE TELEMETRY DECK</div>
  <div class="metrics-grid" style="display:grid; grid-template-columns:repeat(4, 1fr); gap:12px;">
    <div class="metric-item">
      <span style="font-size:0.6rem; color:var(--color-gray); font-weight:800; text-transform:uppercase; display:block;">CLASS</span>
      <span style="font-size:0.95rem; font-weight:900; color:#111111;">CSE Core</span>
    </div>
    <div class="metric-item">
      <span style="font-size:0.6rem; color:var(--color-gray); font-weight:800; text-transform:uppercase; display:block;">SECTION</span>
      <span style="font-size:0.95rem; font-weight:900; color:#111111;">A & B</span>
    </div>
    <div class="metric-item">
      <span style="font-size:0.6rem; color:var(--color-gray); font-weight:800; text-transform:uppercase; display:block;">TOTAL STUDENTS</span>
      <span style="font-size:0.95rem; font-weight:900; color:#111111;">{total_students}</span>
    </div>
    <div class="metric-item">
      <span style="font-size:0.6rem; color:var(--color-gray); font-weight:800; text-transform:uppercase; display:block;">ACCURACY</span>
      <span style="font-size:0.95rem; font-weight:900; color:#22C55E;">98.6%</span>
    </div>
    <div class="metric-item">
      <span style="font-size:0.6rem; color:var(--color-gray); font-weight:800; text-transform:uppercase; display:block;">PRESENT</span>
      <span style="font-size:0.95rem; font-weight:900; color:#22C55E;" class="live-present-val">{present_count}</span>
    </div>
    <div class="metric-item">
      <span style="font-size:0.6rem; color:var(--color-gray); font-weight:800; text-transform:uppercase; display:block;">ABSENT</span>
      <span style="font-size:0.95rem; font-weight:900; color:#EF4444;" class="live-absent-val">{absent_count}</span>
    </div>
    <div class="metric-item">
      <span style="font-size:0.6rem; color:var(--color-gray); font-weight:800; text-transform:uppercase; display:block;">LAST SCAN</span>
      <span style="font-size:0.95rem; font-weight:900; color:#111111;">{current_time_str}</span>
    </div>
    <div class="metric-item">
      <span style="font-size:0.6rem; color:var(--color-gray); font-weight:800; text-transform:uppercase; display:block;">ATTENDANCE</span>
      <span style="font-size:0.95rem; font-weight:900; color:#5865F2;" class="live-rate-val">{attendance_pct:.1f}%</span>
    </div>
  </div>
</div>

<!-- JavaScript Stage Loop Controller -->
<script>
  (function() {{
    var container = document.querySelector(".demo-scanner-container");
    if (!container) return;
    var stage = 1;
    setInterval(function() {{
      stage = (stage % 5) + 1;
      container.setAttribute("data-stage", stage);
      
      // Select metric values in the telemetry grid
      var presentEl = document.querySelector(".live-present-val");
      var absentEl = document.querySelector(".live-absent-val");
      var rateEl = document.querySelector(".live-rate-val");
      
      if (presentEl && absentEl && rateEl) {{
        if (stage === 1 || stage === 2) {{
          presentEl.textContent = "{max(0, present_count - 2)}";
          absentEl.textContent = "{absent_count + 2}";
          rateEl.textContent = "{max(0.0, attendance_pct - 1.5):.1f}%";
        }} else if (stage === 3) {{
          presentEl.textContent = "{max(0, present_count - 1)}";
          absentEl.textContent = "{absent_count + 1}";
          rateEl.textContent = "{max(0.0, attendance_pct - 0.7):.1f}%";
        }} else if (stage === 4 || stage === 5) {{
          presentEl.textContent = "{present_count}";
          absentEl.textContent = "{absent_count}";
          rateEl.textContent = "{attendance_pct:.1f}%";
        }}
      }}
    }}, 3000);
  }})();
</script>
"""


# ── Reusable HTML helpers ─────────────────────────────────────────────────────
def _section(eyebrow, title, subtitle="", anchor_id=""):
    sub_tag = (f'<div style="font-size:0.95rem;color:#333333;text-align:center;'
               f'max-width:520px;margin:0 auto 2.5rem;line-height:1.65;'
               f'font-family:\'Outfit\',sans-serif;font-weight:600;">{subtitle}</div>') if subtitle else ""
    anchor_attr = f'id="{anchor_id}"' if anchor_id else ""
    return f"""
<div {anchor_attr} style="font-size:0.85rem;font-weight:800;text-transform:uppercase;
  letter-spacing:0.08em;color:#5865F2;text-align:center;
  font-family:'Outfit',sans-serif;margin-bottom:8px;margin-top:4rem;">{eyebrow}</div>
<div style="font-size:clamp(1.8rem,3vw,2.5rem);font-weight:900;letter-spacing:-0.03em;
  color:#000000;text-align:center;margin-bottom:0.6rem;text-transform:uppercase;
  font-family:'Climate Crisis',sans-serif;line-height:1.1;">{title}</div>
{sub_tag}"""


def home_screen():
    style_background_home()
    style_base_layout()
    header_home()

    # ════════════════════════════════════════════════════════════════════════
    # HERO
    # ════════════════════════════════════════════════════════════════════════
    st.markdown("""
<style>
/* --- Background Grid Pattern with spotlight glow --- */
.stApp {
  background-color: #FAFAFA !important;
  background-image: 
    radial-gradient(circle at 75% 25%, rgba(88, 101, 242, 0.06) 0%, transparent 55%),
    radial-gradient(#e0e0e0 1.5px, transparent 1.5px) !important;
  background-size: 100% 100%, 24px 24px !important;
}

/* --- Hero Stagger FadeUp --- */
@keyframes fadeUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
.hero-badge-wrap {
  animation: fadeUp 700ms cubic-bezier(0.16, 1, 0.3, 1) both;
  animation-delay: 100ms;
}
.hero-h1-wrap {
  animation: fadeUp 700ms cubic-bezier(0.16, 1, 0.3, 1) both;
  animation-delay: 250ms;
}
.hero-sub-wrap {
  animation: fadeUp 700ms cubic-bezier(0.16, 1, 0.3, 1) both;
  animation-delay: 400ms;
}
div[data-testid="stColumn"]:nth-child(1) .stButton {
  animation: fadeUp 700ms cubic-bezier(0.16, 1, 0.3, 1) both;
  animation-delay: 550ms;
}
.trust-indicators-row {
  animation: fadeUp 700ms cubic-bezier(0.16, 1, 0.3, 1) both;
  animation-delay: 650ms;
}

.hero-badge{display:inline-flex;align-items:center;gap:8px;background:#FFD600;
  color:#000000;border:2.5px solid #000000;padding:6px 14px;border-radius:4px;
  font-size:0.8rem;font-weight:800;letter-spacing:0.03em;
  font-family:'Outfit',sans-serif;margin-bottom:1.5rem;box-shadow:2px 2px 0 #000000;}
.hero-dot{width:8px;height:8px;background:#000000;border-radius:50%;
  animation:hpulse 2s infinite;}
@keyframes hpulse{0%,100%{opacity:1;}50%{opacity:0.35;}}

.hero-h1 {
  font-family: 'Climate Crisis', display, sans-serif !important;
  font-size: clamp(2.1rem, 4.7vw, 3.8rem) !important;
  font-weight: 800 !important;
  letter-spacing: -0.01em !important;
  line-height: 1.15 !important;
  color: #000000 !important;
  margin-bottom: 1.5rem !important;
  text-transform: uppercase;
}
.hero-accent{color:#5865F2;}
.hero-sub{font-size:1.05rem!important;color:#333333!important;
  line-height:1.65!important;max-width:520px;margin-bottom:2rem!important;
  font-family:'Outfit',sans-serif!important;font-weight:600;}

html {
  scroll-behavior: smooth !important;
}

/* --- Button custom visual overrides with ripple and glow --- */
div.stButton > button {
  position: relative !important;
  overflow: hidden !important;
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1) !important;
  box-shadow: 4px 4px 0 #111111 !important;
}
div.stButton > button:hover {
  transform: translateY(-4px) !important;
  box-shadow: 7px 7px 0 #111111 !important;
  border-color: #5865F2 !important;
  filter: drop-shadow(0 0 10px rgba(88, 101, 242, 0.25)) !important;
}
div.stButton > button:active {
  transform: translateY(2px) !important;
  box-shadow: 1px 1px 0 #111111 !important;
}
div.stButton > button::after {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  width: 140px;
  height: 140px;
  background: rgba(255, 255, 255, 0.25);
  border-radius: 50%;
  transform: translate(-50%, -50%) scale(0);
  opacity: 0;
  transition: transform 0.5s, opacity 0.5s;
}
div.stButton > button:active::after {
  transform: translate(-50%, -50%) scale(1);
  opacity: 1;
  transition: 0s;
}

/* --- Hero Right Preview Container & Floating elements --- */
.preview-container {
  position: relative;
  width: 100%;
  max-width: 540px;
  margin: 0 auto;
  animation: fadeUp 700ms cubic-bezier(0.16, 1, 0.3, 1) both;
  animation-delay: 350ms;
}

.floating-chip {
  position: absolute;
  border: 2.5px solid #111111;
  padding: 6px 12px;
  font-size: 0.8rem;
  font-weight: 800;
  border-radius: 4px;
  box-shadow: 2.5px 2.5px 0 #111111;
  z-index: 10;
  font-family: 'Outfit', sans-serif;
}
.chip-1 {
  top: -15px;
  left: -25px;
  background: #FACC15;
  color: #111111;
  animation: float1 4s infinite ease-in-out;
}
.chip-2 {
  bottom: 120px;
  left: -35px;
  background: #5865F2;
  color: #ffffff;
  animation: float2 5s infinite ease-in-out;
}
.chip-3 {
  top: 40px;
  right: -30px;
  background: #22C55E;
  color: #ffffff;
  animation: float3 4.5s infinite ease-in-out;
}
.chip-4 {
  bottom: 30px;
  right: -25px;
  background: #EB459E;
  color: #ffffff;
  animation: float1 4.8s infinite ease-in-out;
}

@media (max-width: 1024px) {
  .floating-chip {
    display: none !important;
  }
}

@keyframes float1 {
  0%, 100% { transform: translateY(0) rotate(-1deg); }
  50% { transform: translateY(-6px) rotate(1deg); }
}
@keyframes float2 {
  0%, 100% { transform: translateY(0) rotate(2deg); }
  50% { transform: translateY(-8px) rotate(-2deg); }
}
@keyframes float3 {
  0%, 100% { transform: translateY(0) rotate(-2deg); }
  50% { transform: translateY(-7px) rotate(2deg); }
}

/* Dashboard Window override */
.dashboard-window {
  background: #ffffff;
  border: 4px solid #111111;
  border-radius: 8px;
  box-shadow: 6px 6px 0 #111111;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  width: 100%;
  animation: floatCard 6s infinite ease-in-out;
}

@keyframes floatCard {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-5px); }
}

.window-header {
  background: #111111;
  color: #ffffff;
  padding: 8px 12px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 3px solid #111111;
}
.window-dots {
  display: flex;
  gap: 6px;
}
.window-dots .dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  display: inline-block;
}
.window-dots .dot.red { background: #EF4444; border: 1px solid #000; }
.window-dots .dot.yellow { background: #FACC15; border: 1px solid #000; }
.window-dots .dot.green { background: #22C55E; border: 1px solid #000; }

.window-title {
  font-size: 0.7rem;
  font-weight: 800;
  font-family: monospace;
  letter-spacing: 0.05em;
  color: #ffffff;
}

.window-status {
  font-size: 0.65rem;
  font-weight: 800;
  color: #22C55E;
  font-family: monospace;
  animation: pulseOpacity 1.5s infinite alternate;
}

@keyframes pulseOpacity {
  0% { opacity: 0.4; }
  100% { opacity: 1; }
}

.window-body {
  display: flex;
  background: #ffffff;
  height: 380px;
}

.window-sidebar {
  width: 40px;
  background: #f1f5f9;
  border-right: 2px solid #111111;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding-top: 12px;
  gap: 12px;
}
.window-sidebar .sb-icon {
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #64748b;
}
.window-sidebar .sb-icon.active {
  color: #5865F2;
  background: #e2e8f0;
  border: 1.5px solid #111111;
  border-radius: 4px;
}

.window-main {
  flex-grow: 1;
  display: grid;
  grid-template-columns: 1.15fr 0.85fr;
  height: 100%;
}

@media(max-width: 600px) {
  .window-body {
    height: auto;
    flex-direction: column;
  }
  .window-sidebar {
    width: 100%;
    height: 36px;
    flex-direction: row;
    justify-content: center;
    border-right: none;
    border-bottom: 2px solid #111111;
    padding-top: 0;
    gap: 16px;
  }
  .window-main {
    grid-template-columns: 1fr;
  }
}

.webcam-viewport {
  position: relative;
  background: #E8ECEF;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
  border-right: 2px solid #111111;
  height: 100%;
}
@media(max-width: 600px) {
  .webcam-viewport {
    border-right: none;
    border-bottom: 2px solid #111111;
    height: 220px;
  }
}

.webcam-grid {
  position: absolute;
  inset: 0;
  background-image: 
    linear-gradient(to right, rgba(0,0,0,0.06) 1px, transparent 1px),
    linear-gradient(to bottom, rgba(0,0,0,0.06) 1px, transparent 1px);
  background-size: 16px 16px;
  pointer-events: none;
}

.webcam-avatar-container {
  position: relative;
  width: 130px;
  height: 130px;
  display: flex;
  align-items: center;
  justify-content: center;
}
.webcam-avatar {
  width: 100px;
  height: 100px;
}

.face-box {
  position: absolute;
  inset: 8px;
  border: 3px solid #22C55E;
  border-radius: 6px;
  animation: facePulse 2.5s infinite ease-in-out;
  pointer-events: none;
}

@keyframes facePulse {
  0%, 100% {
    transform: scale(1);
    box-shadow: 0 0 0px rgba(34, 197, 94, 0);
  }
  50% {
    transform: scale(1.02);
    box-shadow: 0 0 8px rgba(34, 197, 94, 0.3);
  }
}

.face-box .corner {
  position: absolute;
  width: 10px;
  height: 10px;
  border: 2px solid #22C55E;
}
.face-box .corner.tl { top: -2px; left: -2px; border-right: 0; border-bottom: 0; }
.face-box .corner.tr { top: -2px; right: -2px; border-left: 0; border-bottom: 0; }
.face-box .corner.bl { bottom: -2px; left: -2px; border-right: 0; border-top: 0; }
.face-box .corner.br { bottom: -2px; right: -2px; border-left: 0; border-top: 0; }

.face-tag {
  position: absolute;
  bottom: -24px;
  left: 50%;
  transform: translateX(-50%);
  color: #ffffff;
  font-size: 0.65rem;
  font-weight: 800;
  padding: 2px 6px;
  border-radius: 4px;
  border: 1.5px solid #111111;
  white-space: nowrap;
  box-shadow: 1.5px 1.5px 0 #111111;
  font-family: 'Outfit', sans-serif;
}

.scanner-bar {
  position: absolute;
  left: 0;
  width: 100%;
  height: 3px;
  background: linear-gradient(90deg, transparent, #22C55E, transparent);
  box-shadow: 0 0 6px rgba(34, 197, 94, 0.7);
  pointer-events: none;
}

@keyframes scanMove {
  0% { top: 0%; opacity: 1; }
  90% { top: 95%; opacity: 1; }
  100% { top: 100%; opacity: 0; }
}

@keyframes pulseUpload {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.05); }
}

/* Stage-based visibility overrides */
.demo-scanner-container[data-stage="1"] .upload-stage-view { opacity: 1 !important; pointer-events: auto !important; }
.demo-scanner-container[data-stage="1"] .scan-stage-view { opacity: 0 !important; }
.demo-scanner-container[data-stage="1"] .success-popup { opacity: 0 !important; transform: translateY(20px) !important; }

.demo-scanner-container[data-stage="2"] .upload-stage-view { opacity: 0 !important; pointer-events: none !important; }
.demo-scanner-container[data-stage="2"] .scan-stage-view { opacity: 1 !important; }
.demo-scanner-container[data-stage="2"] .scanner-bar { animation: scanMove 2.5s ease-in-out forwards !important; }
.demo-scanner-container[data-stage="2"] .student-face-node { opacity: 0 !important; }
.demo-scanner-container[data-stage="2"] .status-badge { opacity: 0 !important; }
.demo-scanner-container[data-stage="2"] .success-popup { opacity: 0 !important; transform: translateY(20px) !important; }

.demo-scanner-container[data-stage="3"] .upload-stage-view { opacity: 0 !important; pointer-events: none !important; }
.demo-scanner-container[data-stage="3"] .scan-stage-view { opacity: 1 !important; }
.demo-scanner-container[data-stage="3"] .scanner-bar { top: 100% !important; opacity: 0 !important; }
.demo-scanner-container[data-stage="3"] .student-face-node { opacity: 1 !important; }
.demo-scanner-container[data-stage="3"] .face-name-lbl { opacity: 1 !important; }
.demo-scanner-container[data-stage="3"] .status-badge { opacity: 0 !important; }
.demo-scanner-container[data-stage="3"] .success-popup { opacity: 0 !important; transform: translateY(20px) !important; }

.demo-scanner-container[data-stage="4"] .upload-stage-view { opacity: 0 !important; pointer-events: none !important; }
.demo-scanner-container[data-stage="4"] .scan-stage-view { opacity: 1 !important; }
.demo-scanner-container[data-stage="4"] .scanner-bar { top: 100% !important; opacity: 0 !important; }
.demo-scanner-container[data-stage="4"] .student-face-node { opacity: 1 !important; }
.demo-scanner-container[data-stage="4"] .face-name-lbl { opacity: 1 !important; }
.demo-scanner-container[data-stage="4"] .status-badge { opacity: 1 !important; }
.demo-scanner-container[data-stage="4"] .success-popup { opacity: 0 !important; transform: translateY(20px) !important; }

.demo-scanner-container[data-stage="5"] .upload-stage-view { opacity: 0 !important; pointer-events: none !important; }
.demo-scanner-container[data-stage="5"] .scan-stage-view { opacity: 1 !important; }
.demo-scanner-container[data-stage="5"] .scanner-bar { top: 100% !important; opacity: 0 !important; }
.demo-scanner-container[data-stage="5"] .student-face-node { opacity: 1 !important; }
.demo-scanner-container[data-stage="5"] .face-name-lbl { opacity: 1 !important; }
.demo-scanner-container[data-stage="5"] .status-badge { opacity: 1 !important; }
.demo-scanner-container[data-stage="5"] .success-popup { opacity: 1 !important; transform: translateY(0) !important; }

.live-indicator {
  position: absolute;
  top: 8px;
  left: 8px;
  background: rgba(17, 17, 17, 0.85);
  color: #ffffff;
  padding: 3px 6px;
  font-size: 0.6rem;
  font-weight: 800;
  font-family: monospace;
  border-radius: 4px;
  display: flex;
  align-items: center;
  gap: 4px;
  border: 1px solid #111111;
}

.live-dot {
  width: 5px;
  height: 5px;
  background: #EF4444;
  border-radius: 50%;
  animation: liveBlink 1s infinite alternate;
}

@keyframes liveBlink {
  0% { opacity: 0.3; }
  100% { opacity: 1; }
}

.success-popup {
  position: absolute;
  bottom: 8px;
  right: 8px;
  background: #FFFFFF;
  border: 2px solid #111111;
  border-radius: 4px;
  padding: 4px 8px;
  display: flex;
  align-items: center;
  gap: 5px;
  box-shadow: 2px 2px 0 #111111;
  animation: popupSlide 4s infinite ease-in-out;
  z-index: 10;
  font-family: 'Outfit', sans-serif;
}

@keyframes popupSlide {
  0%, 15% { transform: translateY(50px); opacity: 0; }
  20%, 80% { transform: translateY(0); opacity: 1; }
  85%, 100% { transform: translateY(50px); opacity: 0; }
}

.success-icon {
  width: 14px;
  height: 14px;
  background: #22C55E;
  border: 1px solid #111111;
  border-radius: 50%;
  color: #ffffff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 900;
  font-size: 0.6rem;
}

.success-title {
  font-size: 0.6rem;
  font-weight: 900;
  color: #22C55E;
  letter-spacing: 0.02em;
}
.success-sub {
  font-size: 0.55rem;
  font-weight: 700;
  color: #555555;
}

/* Right Split Pane: Details + Feed */
.right-pane {
  display: flex;
  flex-direction: column;
  background: #ffffff;
  border-left: 2px solid #111111;
  height: 100%;
}
@media(max-width: 600px) {
  .right-pane {
    border-left: none;
    border-top: 2px solid #111111;
  }
}

.verification-panel {
  padding: 14px;
  border-bottom: 2px solid #111111;
  font-family: 'Outfit', sans-serif;
  text-align: left;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.panel-badge {
  font-size: 0.65rem;
  font-weight: 800;
  text-transform: uppercase;
  color: #64748b;
  letter-spacing: 0.05em;
}

.verified-indicator {
  background: rgba(34, 197, 94, 0.12);
  color: #22C55E;
  border: 1.5px solid #22C55E;
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 0.65rem;
  font-weight: 800;
  display: flex;
  align-items: center;
  gap: 4px;
}

.vi-dot {
  width: 5px;
  height: 5px;
  background: #22C55E;
  border-radius: 50%;
}

.panel-title {
  font-size: 0.9rem;
  font-weight: 900;
  text-transform: uppercase;
  color: #111111;
  letter-spacing: -0.01em;
  margin-top: 4px;
  margin-bottom: 8px;
}

.panel-details {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.detail-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.detail-label {
  font-size: 0.65rem;
  color: #64748b;
  font-weight: 600;
  text-transform: uppercase;
}

.detail-val {
  font-size: 0.8rem;
  color: #111111;
  font-weight: 800;
}

.detail-val.status-present {
  color: #22C55E;
}

/* Activity Feed section */
.activity-feed {
  padding: 14px;
  flex-grow: 1;
  display: flex;
  flex-direction: column;
  font-family: 'Outfit', sans-serif;
  text-align: left;
}

.feed-title {
  font-size: 0.75rem;
  font-weight: 900;
  text-transform: uppercase;
  color: #111111;
  letter-spacing: 0.05em;
  margin-bottom: 8px;
}

.feed-list {
  display: flex;
  flex-direction: column;
  gap: 6px;
  overflow-y: auto;
  max-height: 140px;
}

.feed-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 6px 10px;
  border-radius: 4px;
  border: 1.5px solid #111111;
  font-size: 0.7rem;
  font-weight: 800;
  font-family: monospace;
}

.feed-item.present {
  background: rgba(34, 197, 94, 0.08);
  border-color: rgba(34, 197, 94, 0.3);
  color: #22C55E;
}

.feed-item.absent {
  background: rgba(239, 68, 68, 0.08);
  border-color: rgba(239, 68, 68, 0.3);
  color: #EF4444;
}

.feed-time {
  color: #64748b;
}
.feed-name {
  color: #111111;
  font-family: 'Outfit', sans-serif;
  font-weight: 700;
}

.trust-indicators-row {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px 20px;
  margin-top: 1.5rem;
}
.trust-indicator-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-family: 'Outfit', sans-serif;
  font-size: 0.8rem;
  font-weight: 800;
  color: #111111;
}
.ti-check {
  width: 16px;
  height: 16px;
}
</style>
<div style="padding:3.5rem 0 1rem;">
  <div class="hero-badge-wrap">
    <div class="hero-badge">
      <span class="hero-dot"></span>
      AI-Powered &nbsp;·&nbsp; Face Recognition &nbsp;·&nbsp; QR Attendance
    </div>
  </div>
  <div class="hero-h1-wrap">
    <h1 class="hero-h1">Attendance in<br/><span class="hero-accent">Seconds</span>.</h1>
  </div>
  <div class="hero-sub-wrap">
    <p class="hero-sub">
      SmartAttend automates college attendance using AI facial recognition and QR codes —
      no paper, no manual roll call, no proxy.
    </p>
  </div>
</div>
""", unsafe_allow_html=True)

    lc, rc = st.columns([1.05, 1.2], gap="large")
    with lc:
        c1, c2 = st.columns(2, gap="small")
        with c1:
            if st.button("Student Portal →", type="primary", use_container_width=True):
                st.session_state["login_type"] = "student"
                st.rerun()
        with c2:
            if st.button("Teacher Login →", type="secondary", use_container_width=True):
                st.session_state["login_type"] = "teacher"
                st.rerun()
        st.markdown("""
<div class="trust-indicators-row">
  <div class="trust-indicator-item">
    <svg class="ti-check" viewBox="0 0 24 24" fill="none"><circle cx="12" cy="12" r="10" fill="#22C55E" stroke="#111111" stroke-width="2"/><path d="M8 12l3 3 5-5" stroke="white" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/></svg>
    <span>Face Recognition</span>
  </div>
  <div class="trust-indicator-item">
    <svg class="ti-check" viewBox="0 0 24 24" fill="none"><circle cx="12" cy="12" r="10" fill="#22C55E" stroke="#111111" stroke-width="2"/><path d="M8 12l3 3 5-5" stroke="white" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/></svg>
    <span>QR Attendance</span>
  </div>
  <div class="trust-indicator-item">
    <svg class="ti-check" viewBox="0 0 24 24" fill="none"><circle cx="12" cy="12" r="10" fill="#22C55E" stroke="#111111" stroke-width="2"/><path d="M8 12l3 3 5-5" stroke="white" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/></svg>
    <span>Anti Proxy</span>
  </div>
  <div class="trust-indicator-item">
    <svg class="ti-check" viewBox="0 0 24 24" fill="none"><circle cx="12" cy="12" r="10" fill="#22C55E" stroke="#111111" stroke-width="2"/><path d="M8 12l3 3 5-5" stroke="white" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/></svg>
    <span>Under 3 Seconds</span>
  </div>
</div>""", unsafe_allow_html=True)

    with rc:
        st.markdown(get_mockup_dashboard_html(), unsafe_allow_html=True)

    # ── Stats band ───────────────────────────────────────────────────────────
    st.markdown("""
<style>
.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  margin: 3.5rem 0 2rem;
}

@media(max-width: 900px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media(max-width: 500px) {
  .stats-grid {
    grid-template-columns: 1fr;
  }
}

.stat-card {
  background: #FFFFFF;
  border: 3px solid #111111;
  border-radius: 8px;
  padding: 20px;
  display: flex;
  align-items: flex-start;
  gap: 14px;
  transition: transform 200ms ease, box-shadow 200ms ease;
  animation: scaleUp 500ms cubic-bezier(0.16, 1, 0.3, 1) both;
}

.stat-card:nth-child(1) { animation-delay: 600ms; }
.stat-card:nth-child(2) { animation-delay: 700ms; }
.stat-card:nth-child(3) { animation-delay: 800ms; }
.stat-card:nth-child(4) { animation-delay: 900ms; }

/* Custom Shadows and Border Color accents for distinct look */
.stat-card.card-indigo {
  box-shadow: 4px 4px 0 #5865F2;
}
.stat-card.card-indigo:hover {
  transform: translate(-2px, -2px);
  box-shadow: 6px 6px 0 #5865F2;
}
.stat-card.card-indigo .sc-icon-wrap {
  background: rgba(88, 101, 242, 0.1);
  color: #5865F2;
  border-color: #5865F2;
}

.stat-card.card-pink {
  box-shadow: 4px 4px 0 #EB459E;
}
.stat-card.card-pink:hover {
  transform: translate(-2px, -2px);
  box-shadow: 6px 6px 0 #EB459E;
}
.stat-card.card-pink .sc-icon-wrap {
  background: rgba(235, 69, 158, 0.1);
  color: #EB459E;
  border-color: #EB459E;
}

.stat-card.card-yellow {
  box-shadow: 4px 4px 0 #FFD600;
}
.stat-card.card-yellow:hover {
  transform: translate(-2px, -2px);
  box-shadow: 6px 6px 0 #FFD600;
}
.stat-card.card-yellow .sc-icon-wrap {
  background: rgba(255, 214, 0, 0.15);
  color: #FFD600;
  border-color: #FFD600;
}

.stat-card.card-green {
  box-shadow: 4px 4px 0 #22C55E;
}
.stat-card.card-green:hover {
  transform: translate(-2px, -2px);
  box-shadow: 6px 6px 0 #22C55E;
}
.stat-card.card-green .sc-icon-wrap {
  background: rgba(34, 197, 94, 0.1);
  color: #22C55E;
  border-color: #22C55E;
}

.sc-icon-wrap {
  width: 36px;
  height: 36px;
  border: 2px solid #111111;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.sc-content {
  display: flex;
  flex-direction: column;
  text-align: left;
}

.sc-val {
  font-size: 1.6rem;
  font-weight: 900;
  color: #111111;
  letter-spacing: -0.03em;
  line-height: 1.1;
  font-family: 'Outfit', sans-serif;
}

.sc-lbl {
  font-size: 0.8rem;
  font-weight: 800;
  color: #111111;
  font-family: 'Outfit', sans-serif;
  text-transform: uppercase;
  margin-top: 1px;
}

.sc-desc {
  font-size: 0.65rem;
  color: #64748b;
  font-weight: 500;
  margin-top: 1px;
}
</style>
<div class="stats-grid">
  <!-- Card 1 -->
  <div class="stat-card card-indigo">
    <div class="sc-icon-wrap">
      <svg viewBox="0 0 24 24" width="20" height="20" stroke="currentColor" stroke-width="2.5" fill="none"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>
    </div>
    <div class="sc-content">
      <span class="sc-val">10,000+</span>
      <span class="sc-lbl">Students</span>
      <span class="sc-desc">Active enrollments</span>
    </div>
  </div>
  
  <!-- Card 2 -->
  <div class="stat-card card-pink">
    <div class="sc-icon-wrap">
      <svg viewBox="0 0 24 24" width="20" height="20" stroke="currentColor" stroke-width="2.5" fill="none"><rect x="3" y="3" width="18" height="18" rx="2"/><path d="M9 3v18"/><path d="M15 3v18"/><path d="M3 9h18"/><path d="M3 15h18"/></svg>
    </div>
    <div class="sc-content">
      <span class="sc-val">50+</span>
      <span class="sc-lbl">Institutions</span>
      <span class="sc-desc">Colleges & Universities</span>
    </div>
  </div>

  <!-- Card 3 -->
  <div class="stat-card card-yellow">
    <div class="sc-icon-wrap">
      <svg viewBox="0 0 24 24" width="20" height="20" stroke="currentColor" stroke-width="2.5" fill="none"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>
    </div>
    <div class="sc-content">
      <span class="sc-val">98%</span>
      <span class="sc-lbl">Accuracy</span>
      <span class="sc-desc">AI face matching</span>
    </div>
  </div>

  <!-- Card 4 -->
  <div class="stat-card card-green">
    <div class="sc-icon-wrap">
      <svg viewBox="0 0 24 24" width="20" height="20" stroke="currentColor" stroke-width="2.5" fill="none"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
    </div>
    <div class="sc-content">
      <span class="sc-val">&lt;3 sec</span>
      <span class="sc-lbl">Time</span>
      <span class="sc-desc">Avg. attendance scan</span>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

    # ════════════════════════════════════════════════════════════════════════
    # FEATURES — exactly 4 as per spec (no Voice Attendance)
    # ════════════════════════════════════════════════════════════════════════
    st.markdown(_section("Features", "What SmartAttend Does",
                         "Four core capabilities that replace manual registers entirely.",
                         anchor_id="features"),
                unsafe_allow_html=True)
    st.markdown("""
<style>
.feat-grid{display:grid;grid-template-columns:repeat(2,1fr);gap:20px;margin-bottom:1rem;}
@media(max-width:600px){.feat-grid{grid-template-columns:1fr;}}
.feat-card{background:#FFFFFF;border:3px solid #000000;border-radius:8px;
  box-shadow:4px 4px 0 #000000;
  padding:28px 26px;transition:transform 150ms ease,box-shadow 150ms ease;}
.feat-card:hover{transform:translate(-2px,-2px);box-shadow:6px 6px 0 #000000;}
.feat-icon{width:48px;height:48px;border:2.5px solid #000000;border-radius:4px;
  box-shadow:2px 2px 0 #000000;display:flex;align-items:center;
  justify-content:center;font-size:1.3rem;margin-bottom:16px;}
.feat-card h4{font-size:1.15rem;font-weight:800;color:#000000;margin-bottom:8px;
  font-family:'Outfit',sans-serif;}
.feat-card p{font-size:0.9rem;color:#333333;line-height:1.6;
  font-family:'Outfit',sans-serif;margin:0;font-weight:600;}
</style>
<div class="feat-grid">
  <div class="feat-card">
    <div class="feat-icon" style="background:#5865F2;">
      <svg width="22" height="22" viewBox="0 0 24 24" fill="none">
        <circle cx="12" cy="8" r="4" stroke="white" stroke-width="2.5"/>
        <path d="M4 20c0-4 3.6-7 8-7s8 3 8 7" stroke="white" stroke-width="2.5" stroke-linecap="round"/>
        <path d="M17 13l1.5 1.5L21 12" stroke="#00E676" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
      </svg>
    </div>
    <h4>AI Face Recognition</h4>
    <p>Upload a classroom photo — AI scans and marks every enrolled student present or absent in under 3 seconds. No manual input required.</p>
  </div>
  <div class="feat-card">
    <div class="feat-icon" style="background:#00E676;">
      <svg width="22" height="22" viewBox="0 0 24 24" fill="none">
        <rect x="3" y="3" width="7" height="7" rx="1" fill="white" opacity="0.3"/>
        <rect x="3" y="3" width="7" height="7" rx="1" stroke="black" stroke-width="2"/>
        <rect x="14" y="3" width="7" height="7" rx="1" fill="white" opacity="0.3"/>
        <rect x="14" y="3" width="7" height="7" rx="1" stroke="black" stroke-width="2"/>
        <rect x="3" y="14" width="7" height="7" rx="1" fill="white" opacity="0.3"/>
        <rect x="3" y="14" width="7" height="7" rx="1" stroke="black" stroke-width="2"/>
        <rect x="16" y="16" width="3" height="3" rx="0.5" fill="black"/>
      </svg>
    </div>
    <h4>QR Code Joining</h4>
    <p>Teachers generate a QR code per subject. Students scan once to enroll permanently. Works on any smartphone — no app download needed.</p>
  </div>
  <div class="feat-card">
    <div class="feat-icon" style="background:#FFD600;">
      <svg width="22" height="22" viewBox="0 0 24 24" fill="none">
        <rect x="3" y="12" width="4" height="9" rx="1" fill="black"/>
        <rect x="10" y="7" width="4" height="14" rx="1" fill="black" opacity="0.7"/>
        <rect x="17" y="3" width="4" height="18" rx="1" fill="black" opacity="0.4"/>
        <path d="M3 8l5-3 5 4 5-5" stroke="black" stroke-width="2"
              stroke-linecap="round" stroke-linejoin="round"/>
      </svg>
    </div>
    <h4>Attendance Analytics</h4>
    <p>Real-time charts, subject-wise breakdowns, session trends, and low-attendance alerts. Teachers see exactly who needs follow-up.</p>
  </div>
  <div class="feat-card">
    <div class="feat-icon" style="background:#EB459E;">
      <svg width="22" height="22" viewBox="0 0 24 24" fill="none">
        <path d="M12 3L4 7v5c0 5.25 3.85 10.16 8 11.35C16.15 22.16 20 17.25 20 12V7L12 3z"
              fill="white" opacity="0.2"/>
        <path d="M12 3L4 7v5c0 5.25 3.85 10.16 8 11.35C16.15 22.16 20 17.25 20 12V7L12 3z"
              stroke="white" stroke-width="2.5" stroke-linejoin="round"/>
        <path d="M9 12l2 2 4-4" stroke="white" stroke-width="2.5"
              stroke-linecap="round" stroke-linejoin="round"/>
      </svg>
    </div>
    <h4>Secure Records</h4>
    <p>All biometric data is encrypted and stored securely. Role-based access ensures teachers and students only see what belongs to them.</p>
  </div>
</div>
""", unsafe_allow_html=True)

    # ════════════════════════════════════════════════════════════════════════
    # HOW IT WORKS
    # ════════════════════════════════════════════════════════════════════════
    st.markdown(_section("How It Works", "Up and Running in 4 Steps",
                         "From first login to your first AI attendance session in under 5 minutes.",
                         anchor_id="how-it-works"),
                unsafe_allow_html=True)
    st.markdown("""
<style>
.steps-wrap{background:#FFFFFF;border:3px solid #000000;border-radius:8px;
  box-shadow:4px 4px 0 #000000;
  padding:2.5rem 2rem;margin:0 0 1rem;}
.steps-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:0;position:relative;}
.steps-grid::before{content:'';position:absolute;top:24px;left:12.5%;right:12.5%;
  height:4px;background:#000000;z-index:0;}
@media(max-width:700px){
  .steps-grid{grid-template-columns:1fr;gap:2rem;}
  .steps-grid::before{display:none;}
}
.step-item{text-align:center;padding:0 1rem;position:relative;z-index:1;}
.step-num{width:48px;height:48px;border-radius:4px;
  background:#5865F2;border:2.5px solid #000000;box-shadow:2px 2px 0 #000000;
  color:#ffffff;font-size:1.15rem;font-weight:900;
  display:flex;align-items:center;justify-content:center;
  margin:0 auto 14px;font-family:'Outfit',sans-serif;}
.step-item h4{font-size:1.05rem;font-weight:800;color:#000000;
  margin-bottom:6px;font-family:'Outfit',sans-serif;}
.step-item p{font-size:0.85rem;color:#333333;
  font-family:'Outfit',sans-serif;line-height:1.5;margin:0;font-weight:600;}
</style>
<div class="steps-wrap">
  <div class="steps-grid">
    <div class="step-item">
      <div class="step-num">1</div>
      <h4>Create Subject</h4>
      <p>Teacher creates a subject with a unique code and section.</p>
    </div>
    <div class="step-item">
      <div class="step-num">2</div>
      <h4>Generate QR</h4>
      <p>A QR code and join link are auto-generated for the subject.</p>
    </div>
    <div class="step-item">
      <div class="step-num">3</div>
      <h4>Students Join</h4>
      <p>Students scan once and are permanently enrolled.</p>
    </div>
    <div class="step-item">
      <div class="step-num">4</div>
      <h4>Track Attendance</h4>
      <p>Upload a photo — AI marks attendance and logs it instantly.</p>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

    # ── Analytics preview callout ─────────────────────────────────────────────
    st.markdown("""
<div style="background:#FFFFFF;border:4px solid #000000;border-radius:8px;
     box-shadow:6px 6px 0 #000000;padding:3rem 2.5rem;text-align:center;margin:2rem 0 1rem;">
  <div style="display:inline-flex;align-items:center;gap:8px;background:#FFD600;
       color:#000000;border:2.5px solid #000000;padding:6px 14px;
       border-radius:4px;font-size:0.8rem;font-weight:800;letter-spacing:0.05em;
       font-family:'Outfit',sans-serif;margin-bottom:1rem;text-transform:uppercase;
       box-shadow:2px 2px 0 #000000;">
    Analytics &amp; Reporting
  </div>
  <div style="font-size:clamp(1.4rem,2.5vw,1.8rem);font-weight:900;color:#000000;
       letter-spacing:-0.03em;margin-bottom:0.75rem;font-family:'Outfit',sans-serif;text-transform:uppercase;">
    Know Who Needs Attention — Before It's Too Late
  </div>
  <div style="font-size:0.95rem;color:#333333;max-width:520px;
       margin:0 auto 1.5rem;font-family:'Outfit',sans-serif;line-height:1.65;font-weight:600;">
    Per-subject attendance charts, session trends, and automatic low-attendance
    alerts give teachers actionable data every single day.
  </div>
  <div style="display:flex;justify-content:center;gap:2rem;flex-wrap:wrap;">
    <div style="text-align:center;background:#FFFFFF;border:2.5px solid #000;border-radius:4px;padding:8px 16px;box-shadow:3px 3px 0 #000;">
      <div style="font-size:1.75rem;font-weight:900;color:#5865F2;
           font-family:'Outfit',sans-serif;letter-spacing:-0.04em;">98%</div>
      <div style="font-size:0.8rem;color:#000000;
           font-family:'Outfit',sans-serif;font-weight:700;">Recognition Rate</div>
    </div>
    <div style="text-align:center;background:#FFFFFF;border:2.5px solid #000;border-radius:4px;padding:8px 16px;box-shadow:3px 3px 0 #000;">
      <div style="font-size:1.75rem;font-weight:900;color:#00E676;
           font-family:'Outfit',sans-serif;letter-spacing:-0.04em;">50+</div>
      <div style="font-size:0.8rem;color:#000000;
           font-family:'Outfit',sans-serif;font-weight:700;">Institutions</div>
    </div>
    <div style="text-align:center;background:#FFFFFF;border:2.5px solid #000;border-radius:4px;padding:8px 16px;box-shadow:3px 3px 0 #000;">
      <div style="font-size:1.75rem;font-weight:900;color:#EB459E;
           font-family:'Outfit',sans-serif;letter-spacing:-0.04em;">10K+</div>
      <div style="font-size:0.8rem;color:#000000;
           font-family:'Outfit',sans-serif;font-weight:700;">Students</div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

    # ── CTA section ───────────────────────────────────────────────────────────
    st.markdown(_section("Get Started", "Try SmartAttend Today", anchor_id="about"),
                unsafe_allow_html=True)
    cta_l, cta_m, cta_r, _ = st.columns([1.5, 1, 1, 1.5])
    with cta_m:
        if st.button("Student Portal →", type="primary", use_container_width=True,
                     key="cta_student"):
            st.session_state["login_type"] = "student"
            st.rerun()
    with cta_r:
        if st.button("Teacher Login →", type="secondary", use_container_width=True,
                     key="cta_teacher"):
            st.session_state["login_type"] = "teacher"
            st.rerun()

    # Inject background floating particles and JavaScript Mouse-Parallax handler
    st.markdown("""
    <!-- Floating background particles -->
    <div class="particle-container" style="position: fixed; inset: 0; pointer-events: none; z-index: 0; overflow: hidden;">
      <div class="particle" style="top: 20%; left: 10%; width: 6px; height: 6px; animation-delay: 0s; animation-duration: 10s;"></div>
      <div class="particle" style="top: 60%; left: 25%; width: 4px; height: 4px; animation-delay: 2s; animation-duration: 8s;"></div>
      <div class="particle" style="top: 40%; left: 80%; width: 5px; height: 5px; animation-delay: 1s; animation-duration: 12s;"></div>
      <div class="particle" style="top: 80%; left: 70%; width: 3px; height: 3px; animation-delay: 3s; animation-duration: 9s;"></div>
    </div>
    
    <style>
    .particle {
      position: absolute;
      background: rgba(88, 101, 242, 0.15);
      border-radius: 50%;
      pointer-events: none;
      animation: floatParticle 10s infinite linear;
    }
    @keyframes floatParticle {
      0% { transform: translateY(100vh) scale(1); opacity: 0; }
      10% { opacity: 0.8; }
      90% { opacity: 0.8; }
      100% { transform: translateY(-10vh) scale(1.2); opacity: 0; }
    }
    </style>
    
    <!-- Mouse parallax script for dashboard-window -->
    <script>
      (function() {
        var card = document.querySelector(".dashboard-window");
        if (!card) return;
        document.addEventListener("mousemove", function(e) {
          var x = (window.innerWidth / 2 - e.clientX) / 45;
          var y = (window.innerHeight / 2 - e.clientY) / 45;
          card.style.transform = "perspective(800px) rotateY(" + x + "deg) rotateX(" + y + "deg)";
        });
      })();
    </script>
    """, unsafe_allow_html=True)

    st.markdown('<div style="height:1rem"></div>', unsafe_allow_html=True)
    footer_home()
