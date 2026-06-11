"""SmartAttend — Student Screen (Login + Dashboard)"""
import streamlit as st
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
from src.components.dialog_enroll import enroll_dialog
from src.components.subject_card import subject_card


# ── Shared navbar ─────────────────────────────────────────────────────────────
def _topnav(name: str, role: str = "Student"):
    initial = name[:1].upper() if name else "S"
    st.markdown(f"""
<style>
.sa-nav2{{display:flex;align-items:center;justify-content:space-between;
  padding:0.9rem 0;border-bottom:1px solid #E5E7EB;margin-bottom:1.75rem;}}
.sa-nav2-brand{{display:flex;align-items:center;gap:10px;}}
.sa-nav2-brand .wm{{font-family:'Inter',sans-serif;font-size:0.98rem;
  font-weight:800;color:#4F46E5;letter-spacing:-0.03em;}}
.sa-nav2-right{{display:flex;align-items:center;gap:12px;}}
.sa-av{{width:36px;height:36px;border-radius:50%;
  background:linear-gradient(135deg,#4F46E5,#7C3AED);
  color:#fff;font-size:0.8rem;font-weight:800;
  display:flex;align-items:center;justify-content:center;
  font-family:'Inter',sans-serif;flex-shrink:0;}}
.sa-uinfo .uname{{font-size:0.85rem;font-weight:600;color:#111827;
  font-family:'Inter',sans-serif;display:block;}}
.sa-uinfo .urole{{font-size:0.72rem;color:#9CA3AF;
  font-family:'Inter',sans-serif;display:block;}}
</style>
<div class="sa-nav2">
  <div class="sa-nav2-brand">
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
  <div class="sa-nav2-right">
    <div class="sa-av">{initial}</div>
    <div class="sa-uinfo">
      <span class="uname">{name}</span>
      <span class="urole">{role}</span>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)


# ── Stat cards row ────────────────────────────────────────────────────────────
def _stat_cards(n_sub, total, attended, pct):
    missed = total - attended
    clr = "#10B981" if pct >= 75 else ("#F59E0B" if pct >= 50 else "#EF4444")
    st.markdown(f"""
<style>
.sas-grid{{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin-bottom:1.75rem;}}
.sas-card{{background:#fff;border:1px solid #E5E7EB;border-radius:14px;
  padding:1.25rem 1.375rem;position:relative;overflow:hidden;
  transition:box-shadow 0.2s,transform 0.2s;}}
.sas-card:hover{{box-shadow:0 6px 20px rgba(0,0,0,0.07);transform:translateY(-2px);}}
.sas-card::after{{content:'';position:absolute;bottom:0;left:0;right:0;height:3px;}}
.sas-card.c1::after{{background:#4F46E5;}}
.sas-card.c2::after{{background:#06B6D4;}}
.sas-card.c3::after{{background:#7C3AED;}}
.sas-card.c4::after{{background:{clr};}}
.sas-icon{{font-size:1.25rem;margin-bottom:10px;display:block;}}
.sas-lbl{{font-size:0.68rem;font-weight:700;text-transform:uppercase;
  letter-spacing:0.07em;color:#9CA3AF;font-family:'Inter',sans-serif;margin-bottom:5px;}}
.sas-val{{font-size:1.65rem;font-weight:900;letter-spacing:-0.04em;
  font-family:'Inter',sans-serif;color:#111827;line-height:1;}}
.sas-sub{{font-size:0.72rem;color:#9CA3AF;font-family:'Inter',sans-serif;margin-top:4px;}}
@media(max-width:768px){{.sas-grid{{grid-template-columns:repeat(2,1fr);}}}}
@media(max-width:420px){{.sas-grid{{grid-template-columns:1fr;}}}}
</style>
<div class="sas-grid">
  <div class="sas-card c1">
    <span class="sas-icon">📚</span>
    <div class="sas-lbl">Subjects</div>
    <div class="sas-val">{n_sub}</div>
    <div class="sas-sub">enrolled</div>
  </div>
  <div class="sas-card c2">
    <span class="sas-icon">📅</span>
    <div class="sas-lbl">Total Classes</div>
    <div class="sas-val">{total}</div>
    <div class="sas-sub">scheduled</div>
  </div>
  <div class="sas-card c3">
    <span class="sas-icon">✅</span>
    <div class="sas-lbl">Attended</div>
    <div class="sas-val">{attended}</div>
    <div class="sas-sub">{missed} missed</div>
  </div>
  <div class="sas-card c4">
    <span class="sas-icon">📊</span>
    <div class="sas-lbl">Attendance</div>
    <div class="sas-val" style="color:{clr};">{pct}%</div>
    <div class="sas-sub">{'On track ✓' if pct>=75 else 'Needs attention ⚠'}</div>
  </div>
</div>
""", unsafe_allow_html=True)


# ── Recent activity feed ──────────────────────────────────────────────────────
def _activity_feed(logs: list, subjects_map: dict):
    """Show last 5 attendance events."""
    recent = sorted(logs, key=lambda x: x.get("timestamp",""), reverse=True)[:5]
    if not recent:
        return

    items_html = ""
    for log in recent:
        present = log.get("is_present", False)
        ts_raw  = log.get("timestamp", "")
        try:
            from datetime import datetime as _dt
            ts_fmt = _dt.fromisoformat(ts_raw).strftime("%d %b  %I:%M %p")
        except Exception:
            ts_fmt = ts_raw[:16] if ts_raw else "—"

        sub_id   = log.get("subject_id")
        sub_info = subjects_map.get(sub_id, {})
        sub_name = sub_info.get("name", "Unknown Subject") if sub_info else "Unknown Subject"

        dot_bg  = "#D1FAE5" if present else "#FEE2E2"
        dot_clr = "#10B981" if present else "#EF4444"
        dot_sym = "✓" if present else "✗"
        status  = "Present" if present else "Absent"

        items_html += f"""
<div style="display:flex;align-items:center;gap:12px;padding:10px 0;
     border-bottom:1px solid #F3F4F6;">
  <div style="width:28px;height:28px;border-radius:50%;background:{dot_bg};
       display:flex;align-items:center;justify-content:center;flex-shrink:0;
       font-size:0.72rem;font-weight:700;color:{dot_clr};">{dot_sym}</div>
  <div style="flex:1;min-width:0;">
    <div style="font-size:0.85rem;font-weight:600;color:#111827;
         font-family:'Inter',sans-serif;white-space:nowrap;overflow:hidden;
         text-overflow:ellipsis;">
      Marked <span style="color:{dot_clr};">{status}</span> — {sub_name}
    </div>
    <div style="font-size:0.72rem;color:#9CA3AF;font-family:'Inter',sans-serif;
         margin-top:2px;">{ts_fmt}</div>
  </div>
</div>"""

    st.markdown(f"""
<div style="background:#fff;border:1px solid #E5E7EB;border-radius:14px;padding:18px 20px;margin-bottom:1.75rem;">
  <div style="font-size:0.8rem;font-weight:700;color:#374151;font-family:'Inter',sans-serif;
       text-transform:uppercase;letter-spacing:0.06em;margin-bottom:8px;">
    Recent Activity
  </div>
  {items_html}
</div>
""", unsafe_allow_html=True)


# ── Section label ─────────────────────────────────────────────────────────────
def _sec(title, sub=""):
    st.markdown(f"""
<div style="margin-bottom:1rem;">
  <h2 style="margin:0;font-size:1.1rem;font-weight:700;color:#111827;
             font-family:'Inter',sans-serif;letter-spacing:-0.02em;">{title}</h2>
  {'<p style="margin:4px 0 0;font-size:0.8rem;color:#6B7280;font-family:Inter,sans-serif;">'+sub+'</p>' if sub else ''}
</div>""", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════════════
# DASHBOARD
# ════════════════════════════════════════════════════════════════════════════
def student_dashboard():
    student_data = st.session_state.student_data
    student_id   = student_data["student_id"]
    student_name = student_data["name"]

    _topnav(student_name, "Student")

    # ── Action bar ──────────────────────────────────────────────────────────
    a1, a2, a3, _ = st.columns([1, 1, 1, 3])
    with a1:
        if st.button("＋ Enroll", type="primary", use_container_width=True):
            enroll_dialog()
    with a2:
        if st.button("⇄ Teacher Mode", type="secondary", use_container_width=True):
            st.session_state["login_type"] = "teacher"
            st.rerun()
    with a3:
        if st.button("Sign Out", type="secondary", use_container_width=True):
            st.session_state["is_logged_in"] = False
            del st.session_state.student_data
            st.rerun()

    st.markdown('<hr style="margin:0 0 1.5rem;">', unsafe_allow_html=True)

    # ── Data ────────────────────────────────────────────────────────────────
    with st.spinner("Loading your dashboard…"):
        subjects = get_student_subjects(student_id)
        logs     = get_student_attendance(student_id)

    # Build stats_map and subjects_map
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

    # ── Stat cards ──────────────────────────────────────────────────────────
    _stat_cards(len(subjects), total_all, attended_all, pct_all)

    # ── Two-column layout: Subjects | Activity ───────────────────────────────
    left, right = st.columns([1.6, 1], gap="large")

    with left:
        _sec("Your Subjects",
             f"{len(subjects)} subject{'s' if len(subjects) != 1 else ''} enrolled")

        if not subjects:
            st.markdown("""
<div style="background:#fff;border:2px dashed #E5E7EB;border-radius:14px;
     padding:3rem 2rem;text-align:center;">
  <div style="font-size:2rem;margin-bottom:10px;">📚</div>
  <div style="font-size:0.9rem;font-weight:600;color:#374151;
       font-family:'Inter',sans-serif;margin-bottom:5px;">No subjects yet</div>
  <div style="font-size:0.8rem;color:#9CA3AF;font-family:'Inter',sans-serif;">
    Click "+ Enroll" above and enter a subject code.
  </div>
</div>""", unsafe_allow_html=True)
        else:
            for i, sub_node in enumerate(subjects):
                sub  = sub_node.get("subjects", {})
                sid  = sub.get("subject_id")
                stat = stats_map.get(sid, {"total": 0, "attended": 0})
                att  = stat["attended"]
                tot  = stat["total"]
                pct  = int(att / tot * 100) if tot > 0 else 0

                def _make_cb(sub_ref, sid_ref):
                    def _cb():
                        if st.button(
                            "Unenroll",
                            type="tertiary",
                            use_container_width=True,
                            icon=":material/delete_forever:",
                            key=f"unenroll_{sid_ref}",
                        ):
                            unenroll_student_to_subject(student_id, sid_ref)
                            st.toast(f"Unenrolled from {sub_ref.get('name','')}")
                            st.rerun()
                    return _cb

                subject_card(
                    name=sub.get("name", "—"),
                    code=sub.get("subject_code", "—"),
                    section=sub.get("section", "—"),
                    stats=[
                        ("📅", "Classes",    tot),
                        ("✅", "Attended",   att),
                        ("📊", "Attendance", f"{pct}%"),
                    ],
                    footer_callback=_make_cb(sub, sid),
                    card_index=i,
                )

    with right:
        _sec("Recent Activity", "Your last 5 attendance events")
        _activity_feed(logs, subjects_map)

        # ── Attendance health card ──────────────────────────────────────────
        health_clr = "#10B981" if pct_all >= 75 else ("#F59E0B" if pct_all >= 50 else "#EF4444")
        health_bg  = "#F0FDF4" if pct_all >= 75 else ("#FFFBEB" if pct_all >= 50 else "#FFF5F5")
        health_msg = "Great attendance! Keep it up." if pct_all >= 75 \
                     else "Attendance needs attention." if pct_all >= 50 \
                     else "Critical — risk of shortage."
        bar_w = min(pct_all, 100)
        st.markdown(f"""
<div style="background:{health_bg};border:1px solid {health_clr}30;border-radius:14px;
     padding:18px 20px;margin-bottom:1.25rem;">
  <div style="font-size:0.7rem;font-weight:700;text-transform:uppercase;letter-spacing:0.07em;
       color:{health_clr};font-family:'Inter',sans-serif;margin-bottom:10px;">
    Overall Health
  </div>
  <div style="font-size:2rem;font-weight:900;color:{health_clr};letter-spacing:-0.04em;
       font-family:'Inter',sans-serif;line-height:1;margin-bottom:6px;">{pct_all}%</div>
  <div style="height:6px;background:rgba(0,0,0,0.08);border-radius:100px;overflow:hidden;margin-bottom:8px;">
    <div style="height:100%;width:{bar_w}%;background:{health_clr};border-radius:100px;"></div>
  </div>
  <div style="font-size:0.78rem;color:{health_clr};font-family:'Inter',sans-serif;
       font-weight:500;">{health_msg}</div>
</div>
""", unsafe_allow_html=True)

    footer_dashboard()


# ════════════════════════════════════════════════════════════════════════════
# LOGIN / REGISTER — split layout
# ════════════════════════════════════════════════════════════════════════════
def student_screen():
    style_background_dashboard()
    style_base_layout()

    if "student_data" in st.session_state:
        student_dashboard()
        return

    # ── Split layout: illustration left, form right ──────────────────────────
    st.markdown("""
<style>
.sa-auth-page{min-height:100vh;}
.sa-auth-left{
  background:linear-gradient(145deg,#4F46E5 0%,#7C3AED 60%,#06B6D4 100%);
  border-radius:20px;padding:3rem 2.5rem;
  display:flex;flex-direction:column;justify-content:center;min-height:540px;
}
.sa-auth-left h2{font-size:1.6rem!important;font-weight:900!important;
  color:#fff!important;letter-spacing:-0.04em!important;margin-bottom:0.75rem!important;}
.sa-auth-left p{font-size:0.88rem!important;color:rgba(255,255,255,0.75)!important;
  line-height:1.65!important;margin-bottom:1.75rem!important;}
.sa-auth-bullets{list-style:none;padding:0;margin:0;}
.sa-auth-bullets li{font-size:0.82rem;color:rgba(255,255,255,0.85);
  font-family:'Inter',sans-serif;margin-bottom:10px;display:flex;align-items:center;gap:10px;}
.sa-auth-check{width:20px;height:20px;border-radius:50%;background:rgba(255,255,255,0.2);
  display:flex;align-items:center;justify-content:center;font-size:0.65rem;color:#fff;flex-shrink:0;}
.sa-form-card{background:#fff;border:1px solid #E5E7EB;border-radius:20px;padding:2.25rem 2rem;}
.sa-form-logo{display:flex;align-items:center;gap:10px;margin-bottom:1.5rem;}
.sa-form-logo .wm{font-family:'Inter',sans-serif;font-size:1rem;font-weight:800;
  color:#4F46E5;letter-spacing:-0.03em;}
</style>
""", unsafe_allow_html=True)

    back_col, _ = st.columns([1, 4])
    with back_col:
        if st.button("← Home", type="secondary"):
            st.session_state["login_type"] = None
            st.rerun()

    st.markdown('<div style="height:8px"></div>', unsafe_allow_html=True)

    left, right = st.columns([1, 1.1], gap="large")

    # ── Left panel ───────────────────────────────────────────────────────────
    with left:
        st.markdown("""
<div class="sa-auth-left">
  <div style="margin-bottom:1.5rem;">
    <svg width="40" height="40" viewBox="0 0 36 36" fill="none">
      <rect width="36" height="36" rx="9" fill="rgba(255,255,255,0.2)"/>
      <path d="M18 7L9 11v8c0 5.25 3.85 10.16 9 11.35C23.15 29.16 27 24.25 27 19v-8l-9-4z"
            stroke="white" stroke-width="1.5" stroke-linejoin="round"/>
      <path d="M14 18l2.8 2.8L22.5 15" stroke="white" stroke-width="2"
            stroke-linecap="round" stroke-linejoin="round"/>
    </svg>
  </div>
  <h2>Student Login</h2>
  <p>Use Face ID to sign in instantly. No password needed — your face is your credential.</p>
  <ul class="sa-auth-bullets">
    <li><span class="sa-auth-check">✓</span> Instant face recognition login</li>
    <li><span class="sa-auth-check">✓</span> View attendance across all subjects</li>
    <li><span class="sa-auth-check">✓</span> Track attendance percentage live</li>
    <li><span class="sa-auth-check">✓</span> Join subjects via QR code</li>
    <li><span class="sa-auth-check">✓</span> Voice enrollment available</li>
  </ul>
</div>
""", unsafe_allow_html=True)

    # ── Right panel (form) ───────────────────────────────────────────────────
    with right:
        st.markdown("""
<div class="sa-form-card">
  <div class="sa-form-logo">
    <svg width="26" height="26" viewBox="0 0 36 36" fill="none">
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
  <div style="font-size:1.2rem;font-weight:800;color:#111827;letter-spacing:-0.03em;
       font-family:'Inter',sans-serif;margin-bottom:4px;">Sign in with Face ID</div>
  <div style="font-size:0.82rem;color:#6B7280;font-family:'Inter',sans-serif;
       margin-bottom:1.25rem;">Position your face in the camera frame below.</div>
""", unsafe_allow_html=True)

        show_reg = False
        photo    = st.camera_input("Look directly at the camera")

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
                        student = next((s for s in all_st if s["student_id"] == sid_key), None)
                        if student:
                            st.session_state.is_logged_in = True
                            st.session_state.user_role    = "student"
                            st.session_state.student_data = student
                            st.toast(f"Welcome back, {student['name']}! 👋")
                            time.sleep(0.8)
                            st.rerun()
                    else:
                        st.info("Face not recognised. If you are new, register below.")
                        show_reg = True

        st.markdown("</div>", unsafe_allow_html=True)

        # ── New student registration ─────────────────────────────────────────
        if show_reg:
            st.markdown("""
<div style="background:#F5F3FF;border:1px solid #DDD6FE;border-radius:14px;
     padding:1.5rem 1.75rem;margin-top:1rem;">
  <div style="font-size:0.7rem;font-weight:700;text-transform:uppercase;letter-spacing:0.08em;
       color:#7C3AED;margin-bottom:1rem;font-family:'Inter',sans-serif;">
    ✨ New Student — Create Profile
  </div>
""", unsafe_allow_html=True)
            new_name = st.text_input("Full Name", placeholder="e.g. Priya Sharma")
            st.markdown("""
<div style="background:#EFF6FF;border:1px solid #BFDBFE;border-radius:8px;
     padding:9px 13px;margin:8px 0;font-size:0.78rem;color:#1D4ED8;
     font-family:'Inter',sans-serif;">
  🎙️ <b>Optional:</b> Record your voice to enable voice-based attendance too.
</div>""", unsafe_allow_html=True)
            audio_data = None
            try:
                audio_data = st.audio_input("Record: e.g. I am present")
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
                            resp = create_student(new_name, face_embedding=face_emb, voice_embedding=voice_emb)
                            if resp:
                                train_classifier()
                                st.session_state.is_logged_in = True
                                st.session_state.user_role    = "student"
                                st.session_state.student_data = resp[0]
                                st.toast(f"Welcome, {new_name}! 🎉")
                                time.sleep(0.8)
                                st.rerun()
                        else:
                            st.error("Could not capture face features. Please retake the photo.")
                else:
                    st.warning("Please enter your full name.")
            st.markdown("</div>", unsafe_allow_html=True)

    footer_dashboard()
