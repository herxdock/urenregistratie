from datetime import date
import pandas as pd
import streamlit as st

from src.auth import current_user
from src.reports import (period_bounds, load_range, aggregate,
                         shift_minutes, fmt_hm, all_users_in_range)
from src.export import to_excel_bytes, to_pdf_bytes
from src.ui import kpi_grid

st.title("📊 Rapporten")

me = current_user()
username = me.get("name", "")
is_admin = me.get("role") == "admin"

# ---------------- Periode ----------------
with st.container(border=True):
    st.markdown("#### 📅 Periode")
    mode = st.radio("Kies periode", ["Dag", "Week", "Maand", "Aangepaste range"],
                    horizontal=True, label_visibility="collapsed")
    if mode == "Aangepaste range":
        c1, c2 = st.columns(2)
        start = c1.date_input("Van", value=date.today().replace(day=1), format="DD/MM/YYYY")
        end = c2.date_input("Tot", value=date.today(), format="DD/MM/YYYY")
        if end < start:
            st.error("Einddatum moet na startdatum liggen.")
            st.stop()
        period_label = f"{start:%d/%m/%Y} t/m {end:%d/%m/%Y}"
    else:
        ref = st.date_input("Referentiedatum", value=date.today(), format="DD/MM/YYYY")
        start, end = period_bounds(mode, ref=ref)
        period_label = {
            "Dag": f"dag {start:%d/%m/%Y}",
            "Week": f"week {start:%d/%m/%Y} t/m {end:%d/%m/%Y}",
            "Maand": f"maand {start:%m/%Y}",
        }[mode]

# ---------------- Gebruikersfilter ----------------
if is_admin:
    with st.container(border=True):
        st.markdown("#### 👤 Gebruiker")
        available = all_users_in_range(start, end)
        if not available:
            available = [username] if username else []
        keuze_opties = ["Iedereen"] + available
        sel_user = st.selectbox("Toon data van", keuze_opties, index=0)
    users_filter = None if sel_user == "Iedereen" else {sel_user}
else:
    users_filter = {username}
    sel_user = username

# ---------------- Data ----------------
rows = load_range(start, end, users=users_filter)

if not rows:
    with st.container(border=True):
        st.info(f"Geen gegevens voor **{period_label}**.")
    st.stop()

# ---------------- Filters ----------------
with st.container(border=True):
    st.markdown("#### 🎛️ Filters")
    types = sorted({s.get("type", "Standaard") for _, s, _ in rows})
    sel_types = st.multiselect("Filter op type", types, default=types)
    if sel_types:
        rows = [r for r in rows if r[1].get("type", "Standaard") in sel_types]
    group_by = st.radio("Groepeer per", ["Dag", "Week", "Maand", "Type"], horizontal=True)

if not rows:
    with st.container(border=True):
        st.warning("Geen resultaten met deze filters.")
    st.stop()

# ---------------- Verwerken ----------------
summary = aggregate(rows, group_by)
total_min = sum(b["minutes"] for b in summary)
n_days = len({r[0] for r in rows})
gem_per_dag = total_min // n_days if n_days else 0

with st.container(border=True):
    st.markdown("#### 🧮 Totalen")
    kpi_grid([
        ("Totaal uren", fmt_hm(total_min)),
        ("Aantal shiften", len(rows)),
        ("Dagen met uren", n_days),
        ("Gem. per dag", fmt_hm(gem_per_dag)),
    ])

summary_df = pd.DataFrame([
    {"Periode": b["key"], "Uren": fmt_hm(b["minutes"]), "Shiften": b["count"]}
    for b in summary
])

with st.container(border=True):
    st.markdown(f"#### 📋 Samenvatting per {group_by.lower()}")
    with st.expander("Toon samenvatting", expanded=False):
        st.dataframe(summary_df, use_container_width=True, hide_index=True)

detail_rows = []
for d, s, uname in sorted(rows, key=lambda x: (x[0], x[1]["begin"])):
    item = {
        "Datum": d.strftime("%d/%m/%Y"),
        "Begin": s["begin"], "Eind": s["eind"],
        "Uren": fmt_hm(shift_minutes(s)),
        "Type": s.get("type", ""),
        "Commentaar": s.get("commentaar", ""),
    }
    if is_admin and sel_user == "Iedereen":
        item = {"Gebruiker": uname, **item}
    detail_rows.append(item)

detail_df = pd.DataFrame(detail_rows)

with st.container(border=True):
    st.markdown(f"#### 🔍 Detail per shift  ·  {len(detail_df)}")
    with st.expander("Toon alle shiften", expanded=False):
        st.dataframe(detail_df, use_container_width=True, hide_index=True)

# ---------------- Export ----------------
with st.container(border=True):
    st.markdown("#### ⬇️ Exporteren")

    scope = sel_user if is_admin else username
    excel_bytes = to_excel_bytes(detail_df, summary_df, f"Per {group_by}")
    pdf_bytes = to_pdf_bytes(
        period_label=f"Periode: {period_label}  |  Groepering: per {group_by.lower()}  |  Wie: {scope}",
        summary_title=f"Samenvatting per {group_by.lower()}",
        summary_df=summary_df,
        detail_df=detail_df,
        total_minutes=total_min,
    )
    stamp = date.today().strftime("%Y%m%d")
    c1, c2 = st.columns(2)
    c1.download_button("📊 Excel", data=excel_bytes,
                       file_name=f"urenrapport_{stamp}.xlsx",
                       mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                       use_container_width=True)
    c2.download_button("📄 PDF", data=pdf_bytes,
                       file_name=f"urenrapport_{stamp}.pdf",
                       mime="application/pdf",
                       use_container_width=True)
