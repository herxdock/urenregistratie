from datetime import date, timedelta
import streamlit as st

from src.settings_store import load_settings, save_settings
from src.github_store import load_month, delete_shift
from src.reports import shift_minutes, fmt_hm
from src.ui import kpi_grid

st.title("⚙️ Beheer")
st.caption("Beheer de types en verwijder shiften.")

# ============================================================
# BLOK 1 — Types
# ============================================================
settings = load_settings()
types = list(settings.get("shift_types", ["Standaard"]))
if "Standaard" not in types:
    types.insert(0, "Standaard")

changed = False

with st.container(border=True):
    st.markdown("#### 🏷️ Types")
    st.caption("Dit zijn de opties in de dropdown bij een shift.")

    for i, t in enumerate(types):
        c1, c2, c3 = st.columns([5, 1, 1])
        new_val = c1.text_input(
            f"Type {i+1}",
            value=t,
            key=f"t_{i}",
            label_visibility="collapsed",
        )
        if c2.button("💾", key=f"sv_{i}", help="Opslaan"):
            if new_val.strip() and new_val.strip() != t:
                types[i] = new_val.strip()
                changed = True
        if t == "Standaard":
            c3.button("🔒", key=f"del_{i}", disabled=True, help="Standaard kan niet weg")
        else:
            if c3.button("🗑️", key=f"del_{i}", help="Verwijderen"):
                types.pop(i)
                changed = True
                st.rerun()

# ============================================================
# BLOK 2 — Nieuw type
# ============================================================
with st.container(border=True):
    st.markdown("#### ➕ Nieuw type toevoegen")

    with st.form("add_type", clear_on_submit=True):
        new = st.text_input("Naam", placeholder="bv. Klant X")
        ok = st.form_submit_button("➕ Toevoegen", use_container_width=True, type="primary")
        if ok:
            n = new.strip()
            if n and n not in types:
                types.append(n)
                changed = True

if changed:
    save_settings({"shift_types": types})
    st.success("Aangepast ✅")
    st.rerun()

# ============================================================
# BLOK 3 — Shiften verwijderen
# ============================================================
with st.container(border=True):
    st.markdown("#### 🗑️ Shiften verwijderen")
    st.caption("Kies een periode, klap een dag open en verwijder een shift. "
               "Dubbele bevestiging nodig.")

    c1, c2 = st.columns(2)
    start = c1.date_input(
        "Van",
        value=date.today().replace(day=1),
        format="DD/MM/YYYY",
        key="del_start",
    )
    end = c2.date_input(
        "Tot",
        value=date.today(),
        format="DD/MM/YYYY",
        key="del_end",
    )

    if end < start:
        st.error("Einddatum moet na startdatum liggen.")
        st.stop()

    # ----- Data ophalen -----
    days_with_shifts: dict = {}
    cache = {}
    d = start
    while d <= end:
        key = (d.year, d.month)
        if key not in cache:
            cache[key] = load_month(d)
        day_data = cache[key].get(d.isoformat())
        if day_data and day_data.get("shifts"):
            days_with_shifts[d] = day_data["shifts"]
        d += timedelta(days=1)

    if not days_with_shifts:
        st.info("Geen shiften in deze periode.")
    else:
        total_shifts = sum(len(v) for v in days_with_shifts.values())
        total_min = sum(
            shift_minutes(s) for shifts in days_with_shifts.values() for s in shifts
        )

        # KPI-grid bovenaan dit blok
        kpi_grid([
            ("Shiften",      total_shifts),
            ("Totaal uren",  fmt_hm(total_min)),
        ])

        st.markdown("---")

        confirm_id = st.session_state.get("confirm_del")

        for day in sorted(days_with_shifts):
            shifts = days_with_shifts[day]
            shifts_sorted = sorted(shifts, key=lambda s: s.get("begin", "00:00"))
            day_min = sum(shift_minutes(s) for s in shifts)

            with st.expander(
                f"📅 {day:%d/%m/%Y} — {len(shifts)} shift(s), {fmt_hm(day_min)}"
            ):
                for s in shifts_sorted:
                    sid = s.get("id", "")
                    with st.container(border=True):
                        st.markdown(
                            f"**{s.get('begin','?')} – {s.get('eind','?')}**  "
                            f"· {fmt_hm(shift_minutes(s))}  \n"
                            f"Type: `{s.get('type','')}`"
                        )
                        if s.get("commentaar"):
                            st.caption(f"💬 {s['commentaar']}")

                        if confirm_id == sid:
                            st.warning("⚠️ Zeker dat je deze shift definitief wil verwijderen?")
                            c_yes, c_no = st.columns(2)
                            if c_yes.button(
                                "✅ Ja, verwijderen",
                                key=f"yes_{sid}",
                                type="primary",
                                use_container_width=True,
                            ):
                                try:
                                    ok = delete_shift(day, sid)
                                    st.session_state.pop("confirm_del", None)
                                    if ok:
                                        st.success("Shift verwijderd ✅")
                                    else:
                                        st.warning("Shift was al verwijderd.")
                                    st.rerun()
                                except Exception as ex:
                                    st.error(f"Verwijderen mislukt: {ex}")

                            if c_no.button(
                                "↩️ Annuleren",
                                key=f"no_{sid}",
                                use_container_width=True,
                            ):
                                st.session_state.pop("confirm_del", None)
                                st.rerun()
                        else:
                            if st.button(
                                "🗑️ Verwijder deze shift",
                                key=f"ask_{sid}",
                                use_container_width=True,
                            ):
                                st.session_state["confirm_del"] = sid
                                st.rerun()
