import calendar
from datetime import date, timedelta
import streamlit as st

from src.github_store import load_month
from src.reports import shift_minutes, fmt_hm

st.title("📅 Kalender")
st.caption("Maandoverzicht: ingevulde dagen en notities.")

c1, c2 = st.columns(2)
month = c1.number_input("Maand", min_value=1, max_value=12,
                        value=date.today().month, step=1, key="cal_m")
year = c2.number_input("Jaar", min_value=2020, max_value=2100,
                       value=date.today().year, step=1, key="cal_y")

# Data van de maand ophalen
first = date(int(year), int(month), 1)
month_data = load_month(first)

cal = calendar.Calendar(firstweekday=0)   # maandag eerst
weeks = cal.monthdatescalendar(int(year), int(month))

# HTML-grid opbouwen
html = ['<div style="display:grid;grid-template-columns:repeat(7,1fr);gap:6px;">']

for d in ["Ma", "Di", "Wo", "Do", "Vr", "Za", "Zo"]:
    html.append(
        f'<div style="text-align:center;font-weight:700;font-size:.9rem;'
        f'color:#64748b;padding:6px 0;">{d}</div>'
    )

today = date.today()
for week in weeks:
    for d in week:
        in_month = (d.month == int(month) and d.year == int(year))
        if not in_month:
            html.append(
                '<div style="background:transparent;color:#cbd5e1;'
                'border-radius:10px;padding:8px 6px;text-align:center;'
                f'min-height:64px;font-size:.95rem;">{d.day}</div>'
            )
            continue

        entry = month_data.get(d.isoformat(), {})
        shifts = entry.get("shifts", [])
        note = entry.get("note", "")
        total = sum(shift_minutes(s) for s in shifts)

        if total > 0:
            bg = "#dcefe3"; bd = "#b7dcc6"; fg = "#1f5136"
            extra = f'<div style="font-size:.78rem;margin-top:2px;">{fmt_hm(total)}</div>'
        else:
            bg = "#f8fafc"; bd = "#e2e8f0"; fg = "#94a3b8"
            extra = ""

        note_icon = '<div style="font-size:.75rem;">📝</div>' if note else ""
        outline = "outline:2px solid #6b8dab;" if d == today else ""

        html.append(
            f'<div style="background:{bg};border:1px solid {bd};color:{fg};'
            f'border-radius:10px;padding:8px 6px;text-align:center;'
            f'min-height:64px;font-size:.95rem;font-weight:600;'
            f'display:flex;flex-direction:column;align-items:center;'
            f'justify-content:center;{outline}">'
            f'{d.day}{extra}{note_icon}</div>'
        )

html.append("</div>")
st.markdown("".join(html), unsafe_allow_html=True)

st.caption("🟩 ingevuld  ·  ⬜ geen uren  ·  📝 met notitie  ·  blauwe rand = vandaag")

# Maandtotaal
all_shifts = [s for entry in month_data.values() for s in entry.get("shifts", [])]
if all_shifts:
    total_min = sum(shift_minutes(s) for s in all_shifts)
    n_days = sum(1 for entry in month_data.values() if entry.get("shifts"))
    st.divider()
    c1, c2 = st.columns(2)
    c1.metric("Totaal maand", fmt_hm(total_min))
    c2.metric("Dagen met uren", n_days)
