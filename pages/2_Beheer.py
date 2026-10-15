from datetime import date, timedelta
import streamlit as st

from src.auth import require_login
from src.ui import inject_mobile_css
from src.settings_store import load_settings, save_settings
from src.github_store import load_month, delete_shift
from src.reports import shift_minutes, fmt_hm

st.set_page_config(page_title="Beheer", page_icon="⚙️", layout="centered")
require_login()
inject_mobile_css()

st.title("⚙️ Beheer")
st.caption("Beheer de opties die in de dropdown bij een shift verschijnen.")

settings = load_settings()
types = list(settings.get("shift_types", ["Standaard"]))
if "Standaard" not in types:
    types.insert(0, "Standaard")

st.subheader("Types")

changed = False
for i, t in enumerate(types):
    c1, c2, c3 = st.columns([5, 1, 1])
    new_val = c1.text_input(f"Type {i+1}", value=t, key=f"t_{i}",
                            label_visibility="collapsed")
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

st.divider()
st.subheader("Nieuw type toevoegen")
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

st.info("Verwijderen van een type beïnvloedt bestaande data niet — "
        "reeds opgeslagen shiften met dat type blijven bestaan en blijven "
        "filterbaar in rapporten.")

# ---------- Shiften verwijderen ----------
st.divider()
st.subheader("Shiften verwijderen")
st.caption(
    "Bekijk shiften in een periode en verwijder ze (uit scherm én uit de opslag). "
    "Dubbele bevestiging nodig."
)

c1, c2 = st.columns(2)
start = c1.date_input("Van", value=date.today().replace(day=1),
                     format="DD/MM/YYYY", key="del_start")
end = c2.date_input("Tot", value=date.today(),
                    format="DD/MM/YYYY", key="del_end")

if end < start:
    st.error("Einddatum moet na startdatum liggen.")
    st.stop()

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
    st.stop()

total_shifts = sum(len(v) for v in days_with_shifts.values())
st.write(f"**{total_shifts} shift(s)** in deze periode.")

confirm_id = st.session_state.get("confirm_del")

for day in sorted(days_with_shifts):
    shifts = days_with_shifts[day]
    shifts_sorted = sorted(shifts, key=lambda s: s.get("begin", "00:00"))
    day_min = sum(shift_minutes(s) for s in shifts)

    with st.expander(
        f"📅 {day:%d/%m/%Y} — {len(shifts)} shift(s), totaal {fmt_hm(day_min)}"
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
                        "✅ Ja, definitief verwijderen",
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
