from datetime import date, time, datetime, timedelta
import uuid
import streamlit as st

from src.auth import current_user
from src.github_store import load_day_full, save_day
from src.settings_store import load_settings
from src.reports import shift_minutes, fmt_hm

st.title("📝 Uren invullen")

user = current_user()
username = user.get("name", "")

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


def minutes_between(begin: time, eind: time) -> int:
    return max(0, int(
        (datetime.combine(date.min, eind) - datetime.combine(date.min, begin)).total_seconds() // 60
    ))


def _warnings_for(begin, eind, shifts, current_id) -> list[str]:
    warns = []
    dur = minutes_between(begin, eind)
    if 0 < dur < 15:
        warns.append(f"⏱️ Deze shift duurt slechts **{dur} minuten**.")
    if dur > 12 * 60:
        h, m = divmod(dur, 60)
        warns.append(f"⏱️ Deze shift duurt **{h}u {m:02d}m** (meer dan 12 uur).")
    b_min = begin.hour * 60 + begin.minute
    e_min = eind.hour * 60 + eind.minute
    for s in shifts:
        if s["id"] == current_id or not s.get("saved"):
            continue
        ob = parse_time(s["begin"]); oe = parse_time(s["eind"])
        ob_min = ob.hour * 60 + ob.minute
        oe_min = oe.hour * 60 + oe.minute
        if not (e_min <= ob_min or b_min >= oe_min):
            warns.append(f"⚠️ Overlap met shift **{s['begin']}–{s['eind']}**.")
    return warns


def _week_totals(monday: date) -> tuple[int, int]:
    from src.github_store import load_month
    cache = {}
    total, days = 0, 0
    for i in range(7):
        d = monday + timedelta(days=i)
        k = (d.year, d.month)
        if k not in cache:
            cache[k] = load_month(d)
        entry = cache[k].get(d.isoformat(), {})
        if "users" in entry:
            shifts_w = entry["users"].get(username, {}).get("shifts", [])
        else:
            shifts_w = entry.get("shifts", [])
        if shifts_w:
            days += 1
            total += sum(shift_minutes(s) for s in shifts_w)
    return total, days


# ---------------- Datum ----------------
sel_date = st.date_input(
    "Datum", value=date.today(), format="DD/MM/YYYY",
    help="Standaard vandaag.",
)
day_key = sel_date.isoformat()

# ---------------- Load bij datumwissel ----------------
if st.session_state.get("loaded_date") != day_key or st.session_state.get("loaded_user") != username:
    full = load_day_full(sel_date, username)
    stored = full["shifts"]
    stored_note = full["note"]

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
        if any(k.startswith(p) for p in ("begin_", "eind_", "type_", "comment_", "pending_")):
            del st.session_state[k]

    for s in shifts:
        st.session_state[f"begin_{s['id']}"] = parse_time(s["begin"])
        st.session_state[f"eind_{s['id']}"] = parse_time(s["eind"])
        st.session_state[f"type_{s['id']}"] = s["type"]
        st.session_state[f"comment_{s['id']}"] = s["commentaar"]

    st.session_state["note_input"] = stored_note
    st.session_state["loaded_date"] = day_key
    st.session_state["loaded_user"] = username


# ---------------- Indicator ----------------
saved_now = [s for s in st.session_state["shifts"] if s.get("saved")]
if saved_now:
    total_now = sum(minutes_between(parse_time(s["begin"]), parse_time(s["eind"]))
                    for s in saved_now)
    n_now = len(saved_now)
    if sel_date == date.today():
        st.success(f"✅ Vandaag: **{n_now}** shift(s) — totaal **{fmt_hm(total_now)}**")
    else:
        st.info(f"ℹ️ {sel_date:%d/%m/%Y}: **{n_now}** shift(s) — totaal **{fmt_hm(total_now)}**")


# ---------------- Weekoverzicht ----------------
monday = sel_date - timedelta(days=sel_date.weekday())
sunday = monday + timedelta(days=6)
wk_total, wk_days = _week_totals(monday)

with st.container(border=True):
    st.markdown(f"#### 📊 Week van {monday:%d/%m} t/m {sunday:%d/%m}")
    st.markdown(f"**{fmt_hm(wk_total)}** over **{wk_days}** dag(en) met uren.")


# ---------------- Opties ----------------
settings = load_settings()
options = list(settings.get("shift_types", ["Standaard"]))
if "Standaard" not in options:
    options.insert(0, "Standaard")


def persist_shifts():
    to_store = [{
        "id": s["id"], "begin": s["begin"], "eind": s["eind"],
        "type": s["type"], "commentaar": s["commentaar"],
    } for s in st.session_state["shifts"] if s["saved"]]
    save_day(sel_date, username, shifts=to_store)


# ---------------- Shift-blokken ----------------
shifts = st.session_state["shifts"]

for i, s in enumerate(shifts):
    sid = s["id"]
    with st.container(border=True):
        st.subheader(f"Shift {i + 1}")

        c1, c2 = st.columns(2)
        b = c1.time_input("Begin", key=f"begin_{sid}", step=300)
        e = c2.time_input("Eind", key=f"eind_{sid}", step=300)

        keuze = st.selectbox("Type", options, key=f"type_{sid}")
        comment = st.text_area("Commentaar", key=f"comment_{sid}", height=80,
                               placeholder="Optionele opmerking…")

        c_save, c_del = st.columns([3, 1])
        save_clicked = c_save.button(
            f"💾 Shift {i + 1} opslaan", key=f"save_{sid}",
            use_container_width=True, type="primary")
        del_clicked = c_del.button("🗑️", key=f"del_{sid}", help="Verwijder deze shift")

        if save_clicked:
            if e <= b:
                st.error("Einduur moet na beginuur liggen.")
            else:
                warns = _warnings_for(b, e, shifts, sid)
                pending_key = f"pending_{sid}"
                token = f"{fmt(b)}|{fmt(e)}|{keuze}"

                if warns and st.session_state.get(pending_key) != token:
                    for w in warns:
                        st.warning(w)
                    st.session_state[pending_key] = token
                    st.info("👆 Klik nogmaals op **Opslaan** om te bevestigen.")
                else:
                    st.session_state.pop(pending_key, None)
                    s["begin"] = fmt(b); s["eind"] = fmt(e)
                    s["type"] = keuze; s["commentaar"] = comment.strip()
                    s["saved"] = True
                    try:
                        persist_shifts()
                        st.success(f"Shift {i + 1} opgeslagen ✅")
                        st.rerun()
                    except Exception as ex:
                        st.error(f"Opslaan mislukt: {ex}")

        if del_clicked:
            st.session_state["shifts"] = [x for x in shifts if x["id"] != sid]
            for p in ("begin_", "eind_", "type_", "comment_", "pending_"):
                st.session_state.pop(f"{p}{sid}", None)
            try:
                persist_shifts()
                st.toast(f"Shift {i + 1} verwijderd", icon="🗑️")
            except Exception as ex:
                st.error(f"Verwijderen mislukt: {ex}")
            st.rerun()


# ---------------- Extra shift ----------------
st.write("")
if st.button("➕ Extra shift", use_container_width=True):
    ns = {"id": new_id(), "begin": fmt(DEFAULT_BEGIN), "eind": fmt(DEFAULT_EIND),
          "type": "Standaard", "commentaar": "", "saved": False}
    st.session_state["shifts"].append(ns)
    st.session_state[f"begin_{ns['id']}"] = DEFAULT_BEGIN
    st.session_state[f"eind_{ns['id']}"] = DEFAULT_EIND
    st.session_state[f"type_{ns['id']}"] = "Standaard"
    st.session_state[f"comment_{ns['id']}"] = ""
    st.rerun()

if not st.session_state["shifts"]:
    st.info("Geen shiften voor deze dag. Klik op **➕ Extra shift**.")


# ---------------- Totaal ----------------
total_min = sum(minutes_between(parse_time(s["begin"]), parse_time(s["eind"]))
                for s in st.session_state["shifts"] if s["saved"])
st.caption(f"Totaal opgeslagen: **{total_min // 60}u {total_min % 60:02d}m** "
           f"over {sum(1 for s in st.session_state['shifts'] if s['saved'])} shift(s).")


# ---------------- Notitie ----------------
with st.container(border=True):
    st.markdown("#### 📝 Notitie voor deze dag")
    st.caption("Vrije tekst over de hele dag (los van shift-commentaar).")

    note_val = st.text_area("Notitie", key="note_input", height=100,
                            label_visibility="collapsed",
                            placeholder="bv. ziek gemeld, verkeersellende…")
    if st.button("💾 Notitie opslaan", key="save_note", use_container_width=True):
        try:
            save_day(sel_date, username, note=note_val)
            st.success("Notitie opgeslagen ✅")
            st.rerun()
        except Exception as ex:
            st.error(f"Opslaan mislukt: {ex}")
