from datetime import date
import pandas as pd
import streamlit as st

from src.reports import period_bounds, load_range, aggregate, shift_minutes, fmt_hm
from src.export import to_excel_bytes, to_pdf_bytes

st.title("📊 Rapporten")

# ============================================================
# BLOK 1 — Periode
# ============================================================
with st.container(border=True):
    st.markdown("#### 📅 Periode")

    mode = st.radio(
        "Kies periode",
        ["Dag", "Week", "Maand", "Aangepaste range"],
        horizontal=True,
        label_visibility="collapsed",
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

# ============================================================
# Data laden
# ============================================================
rows = load_range(start, end)

if not rows:
    with st.container(border=True):
        st.info(f"Geen gegevens voor **{period_label}**.")
    st.stop()

# ============================================================
# BLOK 2 — Filters en groepering
# ============================================================
with st.container(border=True):
    st.markdown("#### 🎛️ Filters")

    types = sorted({s.get("type", "Standaard") for _, s in rows})
    sel_types = st.multiselect("Filter op type", types, default=types)

    if sel_types:
        rows = [(d, s) for d, s in rows if s.get("type", "Standaard") in sel_types]

    group_by = st.radio(
        "Groepeer per",
        ["Dag", "Week", "Maand", "Type"],
        horizontal=True,
    )

if not rows:
    with st.container(border=True):
        st.warning("Geen resultaten met deze filters.")
    st.stop()

# ============================================================
# Data verwerken
# ============================================================
summary = aggregate(rows, group_by)
total_min = sum(b["minutes"] for b in summary)
n_days = len({d for d, _ in rows})
gem_per_dag = total_min // n_days if n_days else 0

# ============================================================
# BLOK 3 — Totalen
# ============================================================
with st.container(border=True):
    st.markdown("#### 🧮 Totalen")

    c1, c2 = st.columns(2)
    c1.metric("Totaal uren", fmt_hm(total_min))
    c2.metric("Aantal shiften", len(rows))
    c3, c4 = st.columns(2)
    c3.metric("Dagen met uren", n_days)
    c4.metric("Gem. per dag", fmt_hm(gem_per_dag))

# ============================================================
# BLOK 4 — Samenvatting
# ============================================================
summary_df = pd.DataFrame([
    {"Periode": b["key"], "Uren": fmt_hm(b["minutes"]), "Shiften": b["count"]}
    for b in summary
])

with st.container(border=True):
    st.markdown(f"#### 📋 Samenvatting per {group_by.lower()}")
    st.dataframe(summary_df, use_container_width=True, hide_index=True)

# ============================================================
# BLOK 5 — Detail per shift
# ============================================================
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

with st.container(border=True):
    st.markdown(f"#### 🔍 Detail per shift  ·  {len(detail_df)}")
    with st.expander("Toon alle shiften", expanded=False):
        st.dataframe(detail_df, use_container_width=True, hide_index=True)

# ============================================================
# BLOK 6 — Export
# ============================================================
with st.container(border=True):
    st.markdown("#### ⬇️ Exporteren")

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
        "📊 Excel",
        data=excel_bytes,
        file_name=f"urenrapport_{stamp}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True,
    )
    c2.download_button(
        "📄 PDF",
        data=pdf_bytes,
        file_name=f"urenrapport_{stamp}.pdf",
        mime="application/pdf",
        use_container_width=True,
    )
