"""SmartAttend — Student Screen.
Added: attendance trend bar chart, updated colour tokens to #5B5FF8 palette.
Removed: voice enrollment mention from login panel (spec says Face Recognition only).
"""
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

# ── Inline logo SVG ───────────────────────────────────────────────────────────
_LOGO = """<svg width="30" height="30" viewBox="0 0 36 36" fill="none">
  <rect width="36" height="36" rx="9" fill="#5B5FF8"/>
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
  color:#5B5FF8;letter-spacing:-0.03em;}}
.stn-right{{display:flex;align-items:center;gap:12px;}}
.stn-av{{width:36px;height:36px;border-radius:50%;
  background:linear-gradient(135deg,#5B5FF8,#7C3AED);color:#fff;font-size:0.8rem;
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


# ── Stat cards ────────────────────────────────────────────────────────────────
def _stat_cards(n_sub, total, attended, pct):
    missed = total - attended
    clr = "#22C55E" if pct >= 75 else ("#F59E0B" if pct >= 50 else "#EF4444")
    st.markdown(f"""
<style>
.ssc-grid{{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin-bottom:1.75rem;}}
.ssc{{background:#fff;border:1px solid #E2E8F0;border-radius:14px;
  padding:1.2rem 1.35rem;position:relative;overflow:hidden;
  transition:box-shadow 0.2s,transform 0.2s;}}
.ssc:hover{{box-shadow:0 6px 20px rgba(0,0,0,0.06);transform:translateY(-2px);}}
.ssc::after{{content:'';position:absolute;bottom:0;left:0;right:0;height:3px;}}
.ssc.c1::after{{background:#5B5FF8;}}
.ssc.c2::after{{background:#06B6D4;}}
.ssc.c3::after{{background:#7C3AED;}}
.ssc.c4::after{{background:{clr};}}
.ssc-icon{{font-size:1.2rem;margin-bottom:10px;display:block;}}
.ssc-lbl{{font-size:0.67rem;font-weight:700;text-transform:uppercase;letter-spacing:0.07em;
  color:#94A3B8;font-family:'Inter',sans-serif;margin-bottom:5px;}}
.ssc-val{{font-size:1.6rem;font-weight:900;letter-spacing:-0.04em;
  font-family:'Inter',sans-serif;color:#0F172A;line-height:1;}}
.ssc-sub{{font-size:0.7rem;color:#94A3B8;font-family:'Inter',sans-serif;margin-top:4px;}}
@media(max-width:768px){{.ssc-grid{{grid-template-columns:repeat(2,1fr);}}}}
@media(max-width:420px){{.ssc-grid{{grid-template-columns:1fr;}}}}
</style>
<div class="ssc-grid">
  <div class="ssc c1">
    <span class="ssc-icon">📚</span>
    <div class="ssc-lbl">Subjects</div>
    <div class="ssc-val">{n_sub}</div>
    <div class="ssc-sub">enrolled</div>
  </div>
  <div class="ssc c2">
    <span class="ssc-icon">📅</span>
    <div class="ssc-lbl">Total Classes</div>
    <div class="ssc-val">{total}</div>
    <div class="ssc-sub">scheduled</div>
  </div>
  <div class="ssc c3">
    <span class="ssc-icon">✅</span>
    <div class="ssc-lbl">Attended</div>
    <div class="ssc-val">{attended}</div>
    <div class="ssc-sub">{missed} missed</div>
  </div>
  <div class="ssc c4">
    <span class="ssc-icon">📊</span>
    <div class="ssc-lbl">Attendance</div>
    <div class="ssc-val" style="color:{clr};">{pct}%</div>
    <div class="ssc-sub">{'On track ✓' if pct>=75 else 'Needs attention ⚠'}</div>
  </div>
</div>
""", unsafe_allow_html=True)


# ── Attendance trend chart ────────────────────────────────────────────────────
def _attendance_chart(stats_map, subjects_map):
    """Bar chart of attendance % per subject using st.bar_chart."""
    if not stats_map:
        return
    import pandas as pd
    rows = []
    for sid, v in stats_map.items():
        pct = int(v["attended"] / v["total"] * 100) if v["total"] > 0 else 0
        name = subjects_map.get(sid, {}).get("name", str(sid)) if subjects_map.get(sid) else str(sid)
        # Shorten long names for chart axis
        short = name[:22] + "…" if len(name) > 22 else name
        rows.append({"Subject": short, "Attendance %": pct})
    if not rows:
        return
    df = pd.DataFrame(rows).set_index("Subject")
    _sec("Attendance by Subject", "Percentage of classes attended per subject")
    st.bar_chart(df, use_container_width=True, height=220)


# ── Recent activity feed ──────────────────────────────────────────────────────
def _activity_feed(logs, subjects_map):
    recent = sorted(logs, key=lambda x: x.get("timestamp", ""), reverse=True)[:6]
    if not recent:
        return
    items = ""
    for log in recent:
        present  = log.get("is_present", False)
        ts_raw   = log.get("timestamp", "")
        try:
            from datetime import datetime as _dt
            ts = _dt.fromisoformat(ts_raw).strftime("%d %b  %I:%M %p")
        except Exception:
            ts = ts_raw[:16] if ts_raw else "—"
        sid      = log.get("subject_id")
        sinfo    = subjects_map.get(sid, {})
        sname    = sinfo.get("name", "Unknown") if sinfo else "Unknown"
        bg_dot   = "#DCFCE7" if present else "#FEE2E2"
        clr_dot  = "#22C55E" if present else "#EF4444"
        sym      = "✓" if present else "✗"
        label    = "Present" if present else "Absent"
        items += f"""
<div style="display:flex;align-items:center;gap:12px;padding:9px 0;
     border-bottom:1px solid #F1F5F9;">
  <div style="width:26px;height:26px;border-radius:50%;background:{bg_dot};
       display:flex;align-items:center;justify-content:center;flex-shrink:0;
       font-size:0.7rem;font-weight:700;color:{clr_dot};">{sym}</div>
  <div style="flex:1;min-width:0;">
    <div style="font-size:0.83rem;font-weight:600;color:#0F172A;
         font-family:'Inter',sans-serif;overflow:hidden;text-overflow:ellipsis;
         white-space:nowrap;">
      <span style="color:{clr_dot};">{label}</span> — {sname}
    </div>
    <div style="font-size:0.7rem;color:#94A3B8;font-family:'Inter',sans-serif;
         margin-top:1px;">{ts}</div>
  </div>
</div>"""
    st.markdown(f"""
<div style="background:#fff;border:1px solid #E2E8F0;border-radius:14px;
     padding:16px 20px;margin-bottom:1.5rem;">
  <div style="font-size:0.7rem;font-weight:700;text-transform:uppercase;
       letter-spacing:0.07em;color:#334155;font-family:'Inter',sans-serif;
       margin-bottom:8px;">Recent Activity</div>
  {items}
</div>""", unsafe_allow_html=True)


# ── Overall health card ───────────────────────────────────────────────────────
def _health_card(pct):
    clr = "#22C55E" if pct >= 75 else ("#F59E0B" if pct >= 50 else "#EF4444")
    bg  = "#F0FDF4" if pct >= 75 else ("#FFFBEB" if pct >= 50 else "#FFF5F5")
    msg = "Great attendance! Keep it up." if pct >= 75 \
          else "Attendance needs attention." if pct >= 50 \
          else "Critical — risk of shortage."
    st.markdown(f"""
<div style="background:{bg};border:1px solid {clr}30;border-radius:14px;
     padding:18px 20px;margin-bottom:1.25rem;">
  <div style="font-size:0.68rem;font-weight:700;text-transform:uppercase;
       letter-spacing:0.07em;color:{clr};font-family:'Inter',sans-serif;margin-bottom:10px;">
    Overall Health
  </div>
  <div style="font-size:2rem;font-weight:900;color:{clr};letter-spacing:-0.04em;
       font-family:'Inter',sans-serif;line-height:1;margin-bottom:6px;">{pct}%</div>
  <div style="height:6px;background:rgba(0,0,0,0.07);border-radius:100px;
       overflow:hidden;margin-bottom:8px;">
    <div style="height:100%;width:{min(pct,100)}%;background:{clr};
         border-radius:100px;"></div>
  </div>
  <div style="font-size:0.77rem;color:{clr};font-family:'Inter',sans-serif;
       font-weight:500;">{msg}</div>
</div>""", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════════════
# DASHBOARD
# ════════════════════════════════════════════════════════════════════════════
def student_dashboard():
    sd         = st.session_state.student_data
    student_id = sd["student_id"]
    name       = sd["name"]

    _topnav(name, "Student")

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

    with st.spinner("Loading your dashboard…"):
        subjects = get_student_subjects(student_id)
        logs     = get_student_attendance(student_id)

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

    _stat_cards(len(subjects), total_all, attended_all, pct_all)

    # Attendance trend chart (full width)
    _attendance_chart(stats_map, subjects_map)

    st.markdown('<div style="height:0.5rem"></div>', unsafe_allow_html=True)

    left, right = st.columns([1.6, 1], gap="large")

    with left:
        _sec("Your Subjects",
             f"{len(subjects)} subject{'s' if len(subjects)!=1 else ''} enrolled")

        if not subjects:
            st.markdown("""
<div style="background:#fff;border:2px dashed #E2E8F0;border-radius:14px;
     padding:3rem 2rem;text-align:center;">
  <div style="font-size:2rem;margin-bottom:10px;">📚</div>
  <div style="font-size:0.9rem;font-weight:600;color:#334155;
       font-family:'Inter',sans-serif;margin-bottom:5px;">No subjects yet</div>
  <div style="font-size:0.8rem;color:#94A3B8;font-family:'Inter',sans-serif;">
    Click "+ Enroll" and enter a subject code.
  </div>
</div>""", unsafe_allow_html=True)
        else:
            for i, sn in enumerate(subjects):
                sub  = sn.get("subjects", {})
                sid  = sub.get("subject_id")
                stat = stats_map.get(sid, {"total": 0, "attended": 0})
                att  = stat["attended"]
                tot  = stat["total"]
                pct  = int(att / tot * 100) if tot > 0 else 0

                def _make_cb(sub_ref, sid_ref):
                    def _cb():
                        if st.button("Unenroll", type="tertiary",
                                     use_container_width=True,
                                     icon=":material/delete_forever:",
                                     key=f"unenroll_{sid_ref}"):
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
        _health_card(pct_all)
        _sec("Recent Activity", "Last 6 attendance events")
        _activity_feed(logs, subjects_map)

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
.sal{{background:linear-gradient(145deg,#5B5FF8 0%,#7C3AED 60%,#06B6D4 100%);
  border-radius:20px;padding:3rem 2.5rem;display:flex;flex-direction:column;
  justify-content:center;min-height:540px;}}
.sal h2{{font-size:1.55rem!important;font-weight:900!important;color:#fff!important;
  letter-spacing:-0.04em!important;margin-bottom:0.75rem!important;}}
.sal p{{font-size:0.87rem!important;color:rgba(255,255,255,0.72)!important;
  line-height:1.65!important;margin-bottom:1.75rem!important;}}
.sal ul{{list-style:none;padding:0;margin:0;}}
.sal li{{font-size:0.81rem;color:rgba(255,255,255,0.85);font-family:'Inter',sans-serif;
  margin-bottom:10px;display:flex;align-items:center;gap:10px;}}
.sal-ck{{width:20px;height:20px;border-radius:50%;background:rgba(255,255,255,0.18);
  display:flex;align-items:center;justify-content:center;font-size:0.62rem;
  color:#fff;flex-shrink:0;}}
.sar{{background:#fff;border:1px solid #E2E8F0;border-radius:20px;padding:2.25rem 2rem;}}
.sar-logo{{display:flex;align-items:center;gap:10px;margin-bottom:1.5rem;}}
.sar-logo .wm{{font-family:'Inter',sans-serif;font-size:1rem;font-weight:800;
  color:#5B5FF8;letter-spacing:-0.03em;}}
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
