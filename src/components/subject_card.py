"""SmartAttend — Subject card component redesigned in Neo-Brutalism."""
import streamlit as st

_ACCENTS = ["#5865F2", "#EB459E", "#00E676", "#FFD600", "#FF1744", "#7C3AED"]


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
            bar_clr = "#22C55E"
        elif pct_val >= 50:
            bar_clr = "#F59E0B"
        else:
            bar_clr = "#EF4444"
        bar_w = min(pct_val, 100)
    else:
        bar_clr = ""
        bar_w = 0

    chips = ""
    if stats:
        chips = '<div style="display:flex;gap:10px;flex-wrap:wrap;margin-top:16px;">'
        for icon, label, value in stats:
            chips += f"""<div style="display:inline-flex;align-items:center;gap:6px;
  background:#FFFFFF;border:2.5px solid #000000;padding:6px 12px;border-radius:4px;
  font-size:0.8rem;font-family:'Outfit',sans-serif;color:#000000;
  box-shadow: 2px 2px 0 #000000;font-weight:800;">
  <span>{icon}</span>
  <span>{value} {label}</span>
</div>"""
        chips += "</div>"

    prog = ""
    if pct_val is not None:
        prog = f"""
<div style="margin-top:18px;">
  <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px;">
    <span style="font-size:0.8rem;font-weight:800;text-transform:uppercase;
                 letter-spacing:0.04em;color:#000000;font-family:'Outfit',sans-serif;">
      Attendance
    </span>
    <span style="font-size:0.9rem;font-weight:900;color:#000000;
                 font-family:'Outfit',sans-serif;">{pct_val}%</span>
  </div>
  <div style="height:14px;background:#FFFFFF;border:2.5px solid #000000;border-radius:4px;overflow:hidden;position:relative;">
    <div style="height:100%;width:{bar_w}%;background:{bar_clr};
                border-right:2.5px solid #000000;transition:width 0.5s ease;"></div>
  </div>
</div>"""

    fac_html = ""
    if faculty:
        fac_html = (f'<span style="font-size:0.85rem;color:#000000;font-weight:600;'
                    f'font-family:\'Outfit\',sans-serif;margin-top:3px;display:inline-block;'
                    f'background:#E2E8F0;border:1.5px solid #000;padding:2px 6px;border-radius:3px;">'
                    f'👤 {faculty}</span>')

    uid = f"sc-{card_index}-{code}"

    st.markdown(f"""
<style>
#{uid} {{
  background: #FFFFFF;
  border: 4px solid #000000;
  border-radius: 8px;
  box-shadow: 6px 6px 0 #000000;
  padding: 24px;
  margin-bottom: 20px;
  position: relative;
  overflow: hidden;
  transition: transform 150ms ease, box-shadow 150ms ease;
  cursor: default;
}}

#{uid}::before {{
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 8px;
  background: {accent};
}}

#{uid}:hover {{
  transform: translate(-2px, -2px);
  box-shadow: 8px 8px 0 #000000;
}}
</style>
<div id="{uid}">
  <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:6px;">
    <h3 style="margin:0;font-size:1.25rem;font-weight:800;color:#000000;
               font-family:'Outfit',sans-serif;letter-spacing:-0.02em;
               line-height:1.2;padding-right:10px;">{name}</h3>
    <span style="flex-shrink:0;font-size:0.8rem;font-weight:800;
                 background:{accent};color:#FFFFFF;padding:4px 8px;
                 border:2px solid #000000;border-radius:4px;font-family:'Outfit',sans-serif;
                 box-shadow: 2px 2px 0 #000000;">{code}</span>
  </div>
  <div style="display:flex;align-items:center;gap:10px;margin-top:6px;flex-wrap:wrap;">
    <span style="font-size:0.85rem;color:#000000;font-family:'Outfit',sans-serif;font-weight:600;">
      Section <b style="color:#000000;font-weight:800;background:#E2E8F0;border:1.5px solid #000;padding:2px 6px;border-radius:3px;">{section}</b>
    </span>
    {fac_html}
  </div>
  {chips}
  {prog}
</div>
""", unsafe_allow_html=True)

    if footer_callback:
        footer_callback()
