from src.auth import current_user

me = current_user()
if me.get("role") != "admin":
    st.error("🔒 Geen toegang. Deze pagina is enkel voor beheerders.")
    st.stop()
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
    start = c1.date_input("Van", value=date.today().replace(day=1),
                          format="DD/MM/YYYY", key="del_start")
    end = c2.date_input("Tot", value=date.today(),
                        format="DD/MM/YYYY", key="del_end")

    if end < start:
        st.error("Einddatum moet na startdatum liggen.")
        st.stop()

    days_data: dict = {}
    cache = {}
    d = start
    while d <= end:
        k = (d.year, d.month)
        if k not in cache:
            cache[k] = load_month(d)
        entry = cache[k].get(d.isoformat(), {})
        if "users" in entry:
            for uname, udata in entry["users"].items():
                if udata.get("shifts"):
                    days_data.setdefault(d, []).append((uname, udata["shifts"]))
        elif entry.get("shifts"):
            # oud formaat
            days_data.setdefault(d, []).append((None, entry["shifts"]))
        d += timedelta(days=1)

    if not days_data:
        st.info("Geen shiften in deze periode.")
    else:
        total_shifts = sum(len(shifts) for rows in days_data.values() for _, shifts in rows)
        total_min = sum(
            shift_minutes(s)
            for rows in days_data.values()
            for _, shifts in rows
            for s in shifts
        )
        kpi_grid([
            ("Shiften", total_shifts),
            ("Totaal uren", fmt_hm(total_min)),
        ])

        st.markdown("---")
        confirm_key = st.session_state.get("confirm_del")

        for day in sorted(days_data):
            for uname, shifts in days_data[day]:
                label_uname = uname or "onbekend"
                day_min = sum(shift_minutes(s) for s in shifts)
                with st.expander(
                    f"📅 {day:%d/%m/%Y} · 👤 {label_uname} — "
                    f"{len(shifts)} shift(s), {fmt_hm(day_min)}"
                ):
                    for s in sorted(shifts, key=lambda x: x.get("begin", "00:00")):
                        sid = s.get("id", "")
                        key_base = f"{sid}_{label_uname}"
                        with st.container(border=True):
                            st.markdown(
                                f"**{s.get('begin','?')} – {s.get('eind','?')}**  "
                                f"· {fmt_hm(shift_minutes(s))}  \n"
                                f"Type: `{s.get('type','')}`"
                            )
                            if s.get("commentaar"):
                                st.caption(f"💬 {s['commentaar']}")

                            if confirm_key == key_base:
                                st.warning("⚠️ Zeker dat je deze shift definitief wil verwijderen?")
                                c_yes, c_no = st.columns(2)
                                if c_yes.button("✅ Ja, verwijderen",
                                                key=f"yes_{key_base}",
                                                type="primary", use_container_width=True):
                                    try:
                                        if uname is None:
                                            st.error("Oude data zonder gebruiker — kan niet via Beheer verwijderd worden.")
                                        else:
                                            ok = delete_shift(day, uname, sid)
                                            st.session_state.pop("confirm_del", None)
                                            if ok:
                                                st.success("Shift verwijderd ✅")
                                                st.rerun()
                                            else:
                                                st.warning("Shift niet gevonden.")
                                    except Exception as ex:
                                        st.error(f"Verwijderen mislukt: {ex}")
                                if c_no.button("↩️ Annuleren", key=f"no_{key_base}",
                                               use_container_width=True):
                                    st.session_state.pop("confirm_del", None)
                                    st.rerun()
                            else:
                                if st.button("🗑️ Verwijder deze shift",
                                             key=f"ask_{key_base}",
                                             use_container_width=True):
                                    st.session_state["confirm_del"] = key_base
                                    st.rerun()
