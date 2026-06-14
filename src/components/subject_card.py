"""SmartAttend — Subject card component. Updated colours to #5B5FF8 palette."""
import streamlit as st

_ACCENTS = ["#5B5FF8", "#7C3AED", "#06B6D4", "#22C55E", "#F59E0B", "#EF4444"]


def subject_card(
    name,
    code,
    section,
    stats=None,
    footer_callback=None,
    faculty="",
    card_index=0,
):
    accent = _ACCENTS[card_index % len(_ACCENTS)]

    pct_val = None
    for (icon, label, value) in (stats or []):
        if label.lower() in ("attendance", "attendance %") or (
            isinstance(value, str) and value.endswith("%")
        ):
            try:
                pct_val = int(str(value).replace("%", "").strip())
            except ValueError:
                pass

    if pct_val is not None:
        if pct_val >= 75:
            bar_clr, bar_bg = "#22C55E", "#DCFCE7"
        elif pct_val >= 50:
            bar_clr, bar_bg = "#F59E0B", "#FEF3C7"
        else:
            bar_clr, bar_bg = "#EF4444", "#FEE2E2"
        bar_w = min(pct_val, 100)
    else:
        bar_clr = bar_bg = ""
        bar_w = 0

    chips = ""
    if stats:
        chips = '<div style="display:flex;gap:5px;flex-wrap:wrap;margin-top:12px;">'
        for icon, label, value in stats:
            chips += f"""<div style="display:inline-flex;align-items:center;gap:4px;
  background:#F8FAFC;border:1px solid #E2E8F0;padding:4px 9px;border-radius:6px;
  font-size:0.75rem;font-family:'Inter',sans-serif;color:#334155;">
  <span>{icon}</span>
  <span style="font-weight:700;color:#0F172A;">{value}</span>
  <span style="color:#94A3B8;">{label}</span>
</div>"""
        chips += "</div>"

    prog = ""
    if pct_val is not None:
        prog = f"""
<div style="margin-top:14px;">
  <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:5px;">
    <span style="font-size:0.68rem;font-weight:700;text-transform:uppercase;
                 letter-spacing:0.06em;color:#94A3B8;font-family:'Inter',sans-serif;">
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

    fac_html = ""
    if faculty:
        fac_html = (f'<span style="font-size:0.72rem;color:#64748B;'
                    f'font-family:Inter,sans-serif;margin-top:3px;display:inline-block;">'
                    f'👤 {faculty}</span>')

    uid = f"sc-{card_index}-{code}"

    st.markdown(f"""
<style>
#{uid}{{background:#fff;border:1px solid #E2E8F0;border-radius:14px;
  padding:20px 22px 16px;margin-bottom:14px;position:relative;overflow:hidden;
  transition:transform 0.2s ease,box-shadow 0.2s ease;cursor:default;}}
#{uid}::before{{content:'';position:absolute;left:0;top:0;bottom:0;width:4px;
  background:linear-gradient(180deg,{accent},{accent}99);
  border-radius:4px 0 0 4px;}}
#{uid}:hover{{transform:translateY(-3px);box-shadow:0 10px 28px rgba(0,0,0,0.08);}}
</style>
<div id="{uid}">
  <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:2px;">
    <h3 style="margin:0;font-size:0.97rem;font-weight:700;color:#0F172A;
               font-family:'Inter',sans-serif;letter-spacing:-0.01em;
               line-height:1.3;padding-right:10px;">{name}</h3>
    <span style="flex-shrink:0;font-size:0.7rem;font-weight:700;
                 background:{accent}18;color:{accent};padding:3px 9px;
                 border-radius:100px;font-family:'Inter',sans-serif;
                 letter-spacing:0.02em;">{code}</span>
  </div>
  <div style="display:flex;align-items:center;gap:10px;margin-top:4px;flex-wrap:wrap;">
    <span style="font-size:0.78rem;color:#64748B;font-family:'Inter',sans-serif;">
      Section <b style="color:#334155;">{section}</b>
    </span>
    {fac_html}
  </div>
  {chips}
  {prog}
</div>
""", unsafe_allow_html=True)

    if footer_callback:
        footer_callback()
