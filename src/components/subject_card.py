"""SmartAttend — Subject card component."""
import streamlit as st


# Accent colours cycle per card index (set externally via card_index param)
_ACCENTS = ["#4F46E5", "#7C3AED", "#06B6D4", "#10B981", "#F59E0B", "#EF4444"]


def subject_card(
    name: str,
    code: str,
    section: str,
    stats: list | None = None,
    footer_callback=None,
    faculty: str = "",
    card_index: int = 0,
):
    """
    Premium subject card with:
    - Colour accent stripe (cycles through palette)
    - Subject name, code badge, section, faculty
    - Stat chips
    - Attendance progress bar (auto-detected from stats)
    - Hover lift animation
    - Optional footer_callback for action buttons
    """
    accent = _ACCENTS[card_index % len(_ACCENTS)]

    # ── Extract attendance % for progress bar ──
    pct_val: int | None = None
    for (icon, label, value) in (stats or []):
        lbl_lower = label.lower()
        if lbl_lower in ("attendance", "attendance %") or (
            isinstance(value, str) and value.endswith("%")
        ):
            try:
                pct_val = int(str(value).replace("%", "").strip())
            except ValueError:
                pass

    if pct_val is not None:
        if pct_val >= 75:
            bar_clr = "#10B981"
            bar_bg  = "#D1FAE5"
        elif pct_val >= 50:
            bar_clr = "#F59E0B"
            bar_bg  = "#FEF3C7"
        else:
            bar_clr = "#EF4444"
            bar_bg  = "#FEE2E2"
        bar_w = min(pct_val, 100)
    else:
        bar_clr = bar_bg = ""
        bar_w = 0

    # ── Stat chips ──
    chips = ""
    if stats:
        chips = '<div style="display:flex;gap:6px;flex-wrap:wrap;margin-top:12px;">'
        for icon, label, value in stats:
            chips += f"""<div style="display:inline-flex;align-items:center;gap:4px;
  background:#F9FAFB;border:1px solid #E5E7EB;padding:4px 9px;border-radius:6px;
  font-size:0.76rem;font-family:'Inter',sans-serif;color:#374151;">
  <span>{icon}</span>
  <span style="font-weight:700;color:#111827;">{value}</span>
  <span style="color:#9CA3AF;">{label}</span>
</div>"""
        chips += "</div>"

    # ── Progress bar ──
    prog = ""
    if pct_val is not None:
        prog = f"""
<div style="margin-top:14px;">
  <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:5px;">
    <span style="font-size:0.68rem;font-weight:700;text-transform:uppercase;
                 letter-spacing:0.06em;color:#9CA3AF;font-family:'Inter',sans-serif;">
      Attendance
    </span>
    <span style="font-size:0.78rem;font-weight:800;color:{bar_clr};
                 font-family:'Inter',sans-serif;">{pct_val}%</span>
  </div>
  <div style="height:6px;background:{bar_bg};border-radius:100px;overflow:hidden;">
    <div style="height:100%;width:{bar_w}%;background:{bar_clr};
                border-radius:100px;transition:width 0.5s ease;"></div>
  </div>
</div>"""

    # ── Faculty tag ──
    fac_html = ""
    if faculty:
        fac_html = f"""<span style="display:inline-block;font-size:0.72rem;color:#6B7280;
  font-family:'Inter',sans-serif;margin-top:4px;">
  👤 {faculty}
</span>"""

    uid = f"sa-card-{card_index}-{code}"

    card = f"""
<style>
#{uid}{{
  background:#fff;border:1px solid #E5E7EB;border-radius:14px;
  padding:20px 22px 16px;margin-bottom:14px;position:relative;overflow:hidden;
  transition:transform 0.2s ease,box-shadow 0.2s ease;cursor:default;
}}
#{uid}::before{{
  content:'';position:absolute;left:0;top:0;bottom:0;width:4px;
  background:linear-gradient(180deg,{accent},{accent}99);
  border-radius:4px 0 0 4px;
}}
#{uid}:hover{{
  transform:translateY(-3px);
  box-shadow:0 10px 30px rgba(0,0,0,0.08);
}}
</style>
<div id="{uid}">
  <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:2px;">
    <h3 style="margin:0;font-size:0.98rem;font-weight:700;color:#111827;
               font-family:'Inter',sans-serif;letter-spacing:-0.01em;
               line-height:1.3;padding-right:10px;">{name}</h3>
    <span style="flex-shrink:0;font-size:0.7rem;font-weight:700;
                 background:{accent}15;color:{accent};
                 padding:3px 9px;border-radius:100px;
                 font-family:'Inter',sans-serif;letter-spacing:0.02em;">{code}</span>
  </div>
  <div style="display:flex;align-items:center;gap:10px;margin-top:4px;flex-wrap:wrap;">
    <span style="font-size:0.78rem;color:#6B7280;font-family:'Inter',sans-serif;">
      Section <b style="color:#374151;">{section}</b>
    </span>
    {fac_html}
  </div>
  {chips}
  {prog}
</div>
"""
    st.markdown(card, unsafe_allow_html=True)

    if footer_callback:
        footer_callback()
