from datetime import date
import pandas as pd
import streamlit as st

from src.reports import period_bounds, load_range, aggregate, shift_minutes, fmt_hm
from src.export import to_excel_bytes, to_pdf_bytes

st.title("📊 Rapporten")

# ---------------- Periode ----------------
mode = st.radio(
    "Periode",
    ["Dag", "Week", "Maand", "Aangepaste range"],
    horizontal=True,
)

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

# ---------------- Data ----------------
rows = load_range(start, end)

if not rows:
    st.info("Geen gegevens in deze periode.")
    st.stop()

# ---------------- Filters ----------------
types = sorted({s.get("type", "Standaard") for _, s in rows})
sel_types = st.multiselect("Filter op type", types, default=types)
if sel_types:
    rows = [(d, s) for d, s in rows if s.get("type", "Standaard") in sel_types]

if not rows:
    st.warning("Geen resultaten met deze filters.")
    st.stop()

# ---------------- Groepering ----------------
group_by = st.radio("Groepeer per", ["Dag", "Week", "Maand", "Type"], horizontal=True)

summary = aggregate(rows, group_by)
total_min = sum(b["minutes"] for b in summary)
n_days = len({d for d, _ in rows})
gem_per_dag = total_min // n_days if n_days else 0

# ---------------- KPI's ----------------
c1, c2 = st.columns(2)
c1.metric("Totaal", fmt_hm(total_min))
c2.metric("Shiften", len(rows))
c3, c4 = st.columns(2)
c3.metric("Dagen met uren", n_days)
c4.metric("Gem. per dag", fmt_hm(gem_per_dag))

# ---------------- Samenvatting ----------------
summary_df = pd.DataFrame([
    {"Periode": b["key"], "Uren": fmt_hm(b["minutes"]), "Shiften": b["count"]}
    for b in summary
])
st.subheader(f"Samenvatting per {group_by.lower()}")
st.dataframe(summary_df, use_container_width=True, hide_index=True)

# ---------------- Detail ----------------
detail_df = pd.DataFrame([
    {
        "Datum": d.strftime("%d/%m/%Y"),
        "Begin": s["begin"],
        "Eind": s["eind"],
        "Uren": fmt_hm(shift_minutes(s)),
        "Type": s.get("type", ""),
        "Commentaar": s.get("commentaar", ""),
    }
    for d, s in sorted(rows, key=lambda x: (x[0], x[1]["begin"]))
])
with st.expander(f"Detail per shift ({len(detail_df)})"):
    st.dataframe(detail_df, use_container_width=True, hide_index=True)

# ---------------- Export ----------------
st.divider()
st.subheader("Exporteren")

excel_bytes = to_excel_bytes(detail_df, summary_df, f"Per {group_by}")
pdf_bytes = to_pdf_bytes(
    period_label=f"Periode: {period_label}  |  Groepering: per {group_by.lower()}",
    summary_title=f"Samenvatting per {group_by.lower()}",
    summary_df=summary_df,
    detail_df=detail_df,
    total_minutes=total_min,
)

stamp = date.today().strftime("%Y%m%d")
c1, c2 = st.columns(2)
c1.download_button(
    "⬇️ Excel",
    data=excel_bytes,
    file_name=f"urenrapport_{stamp}.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    use_container_width=True,
)
c2.download_button(
    "⬇️ PDF",
    data=pdf_bytes,
    file_name=f"urenrapport_{stamp}.pdf",
    mime="application/pdf",
    use_container_width=True,
)
