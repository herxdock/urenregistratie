from datetime import date, time, datetime
import uuid
import streamlit as st

from src.auth import require_login
from src.ui import inject_mobile_css
from src.github_store import load_day, save_day
from src.settings_store import load_settings



st.title("📝 Uren invullen")

DEFAULT_BEGIN = time(8, 0)
DEFAULT_EIND = time(17, 0)


def parse_time(s):
    if not s:
        return DEFAULT_BEGIN
    try:
        h, m = s.split(":")
        return time(int(h), int(m))
    except Exception:
        return DEFAULT_BEGIN


def fmt(t: time) -> str:
    return t.strftime("%H:%M")


def new_id() -> str:
    return uuid.uuid4().hex[:8]


sel_date = st.date_input(
    "Datum",
    value=date.today(),
    format="DD/MM/YYYY",
    help="Standaard vandaag. Kies een andere dag om te wijzigen.",
)
day_key = sel_date.isoformat()

if st.session_state.get("loaded_date") != day_key:
    stored = load_day(sel_date)

    if stored:
        shifts = [{
            "id": s.get("id") or new_id(),
            "begin": s.get("begin", fmt(DEFAULT_BEGIN)),
            "eind": s.get("eind", fmt(DEFAULT_EIND)),
            "type": s.get("type", "Standaard"),
            "commentaar": s.get("commentaar", ""),
            "saved": True,
        } for s in stored]
    else:
        shifts = [{
            "id": new_id(),
            "begin": fmt(DEFAULT_BEGIN),
            "eind": fmt(DEFAULT_EIND),
            "type": "Standaard",
            "commentaar": "",
            "saved": False,
        }]

    st.session_state["shifts"] = shifts

    for k in list(st.session_state.keys()):
        if any(k.startswith(p) for p in ("begin_", "eind_", "type_", "comment_")):
            del st.session_state[k]

    for s in shifts:
        st.session_state[f"begin_{s['id']}"] = parse_time(s["begin"])
        st.session_state[f"eind_{s['id']}"] = parse_time(s["eind"])
        st.session_state[f"type_{s['id']}"] = s["type"]
        st.session_state[f"comment_{s['id']}"] = s["commentaar"]

    st.session_state["loaded_date"] = day_key


settings = load_settings()
options = list(settings.get("shift_types", ["Standaard"]))
if "Standaard" not in options:
    options.insert(0, "Standaard")


def persist():
    to_store = [{
        "id": s["id"],
        "begin": s["begin"],
        "eind": s["eind"],
        "type": s["type"],
        "commentaar": s["commentaar"],
    } for s in st.session_state["shifts"] if s["saved"]]
    save_day(sel_date, to_store)


shifts = st.session_state["shifts"]

for i, s in enumerate(shifts):
    sid = s["id"]
    with st.container(border=True):
        st.subheader(f"Shift {i + 1}")

        c1, c2 = st.columns(2)
        b = c1.time_input("Begin", key=f"begin_{sid}", step=300)
        e = c2.time_input("Eind", key=f"eind_{sid}", step=300)

        keuze = st.selectbox("Type", options, key=f"type_{sid}")
        comment = st.text_area(
            "Commentaar", key=f"comment_{sid}", height=80,
            placeholder="Optionele opmerking…",
        )

        c_save, c_del = st.columns([3, 1])
        save_clicked = c_save.button(
            f"💾 Shift {i + 1} opslaan",
            key=f"save_{sid}",
            use_container_width=True,
            type="primary",
        )
        del_clicked = c_del.button(
            "🗑️",
            key=f"del_{sid}",
            help="Verwijder deze shift (ook uit de opslag)",
        )

        if save_clicked:
            if e <= b:
                st.error("Einduur moet na beginuur liggen.")
            else:
                s["begin"] = fmt(b)
                s["eind"] = fmt(e)
                s["type"] = keuze
                s["commentaar"] = comment.strip()
                s["saved"] = True
                try:
                    persist()
                    st.success(f"Shift {i + 1} opgeslagen ✅")
                    st.rerun()
                except Exception as ex:
                    st.error(f"Opslaan mislukt: {ex}")

        if del_clicked:
            st.session_state["shifts"] = [x for x in shifts if x["id"] != sid]
            for p in ("begin_", "eind_", "type_", "comment_"):
                st.session_state.pop(f"{p}{sid}", None)
            try:
                persist()
                st.toast(f"Shift {i + 1} verwijderd", icon="🗑️")
            except Exception as ex:
                st.error(f"Verwijderen mislukt: {ex}")
            st.rerun()


st.write("")
if st.button("➕ Extra shift", use_container_width=True):
    ns = {
        "id": new_id(),
        "begin": fmt(DEFAULT_BEGIN),
        "eind": fmt(DEFAULT_EIND),
        "type": "Standaard",
        "commentaar": "",
        "saved": False,
    }
    st.session_state["shifts"].append(ns)
    st.session_state[f"begin_{ns['id']}"] = DEFAULT_BEGIN
    st.session_state[f"eind_{ns['id']}"] = DEFAULT_EIND
    st.session_state[f"type_{ns['id']}"] = "Standaard"
    st.session_state[f"comment_{ns['id']}"] = ""
    st.rerun()

if not st.session_state["shifts"]:
    st.info("Nog geen shiften voor deze dag. Klik op **➕ Extra shift** om te beginnen.")

total_min = 0
for s in st.session_state["shifts"]:
    if s["saved"]:
        bt = parse_time(s["begin"])
        et = parse_time(s["eind"])
        total_min += int(
            (datetime.combine(date.min, et) - datetime.combine(date.min, bt)).total_seconds() // 60
        )

st.divider()
st.caption(
    f"Totaal opgeslagen: **{total_min // 60}u {total_min % 60:02d}m** "
    f"over {sum(1 for s in st.session_state['shifts'] if s['saved'])} shift(s)."
)
