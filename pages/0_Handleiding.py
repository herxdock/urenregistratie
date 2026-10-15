import streamlit as st

st.title("ℹ️ Handleiding")
st.caption("Alles wat je moet weten om de app te gebruiken.")

# ============================================================
# Invoer
# ============================================================
with st.container(border=True):
    st.markdown("### 📝 Dagelijkse invoer")

    st.markdown("""
1. Open **Invoer** in het menu. Bovenaan zie je meteen of er voor vandaag al uren zijn geregistreerd.
2. De datum staat standaard op **vandaag**. Werk je een oudere dag bij? Kies dan een andere datum.
3. Voor **elke shift** vul je in:
   - **Begin** en **Eind**
   - **Type** (standaard = *Standaard*)
   - **Commentaar** (optioneel, over die specifieke shift)
4. Klik **💾 Shift opslaan**. Pas dan wordt de shift bewaard.
5. Nieuwe shift toevoegen? Klik op **➕ Extra shift**.
6. Een shift wissen? Klik op het **🗑️**-icoon.
7. Onderaan kan je een **notitie voor de hele dag** toevoegen (bv. *ziek gemeld*).
""")

    st.warning(
        "⚠️ De app waarschuwt je bij **overlappende shiften** of bij een "
        "**onwaarschijnlijke duur** (<15 min of >12 u). Je moet dan een tweede "
        "keer op **Opslaan** klikken om te bevestigen."
    )

# ============================================================
# Beheer
# ============================================================
with st.container(border=True):
    st.markdown("### ⚙️ Beheer")

    st.markdown("""
**🏷️ Types** — de opties in de dropdown bij een shift (bv. *Verlof*, *Ziekte*, *Klant X*).
- Je kan een type **hernoemen** (💾) of **verwijderen** (🗑️).
- *Standaard* kan je niet verwijderen (🔒).

**➕ Nieuw type toevoegen** — geef een naam op en klik op **Toevoegen**.

**🗑️ Shiften verwijderen** — kies een periode, klap een dag open en verwijder een specifieke shift.
Je ziet bovenaan de totalen van die periode. Verwijderen vraagt **dubbele bevestiging**.
""")

# ============================================================
# Rapporten
# ============================================================
with st.container(border=True):
    st.markdown("### 📊 Rapporten")

    st.markdown("""
- **📅 Periode** — kies *Dag*, *Week*, *Maand* of een vrije **datumrange**.
- **🎛️ Filters** — filter op **type** (meerdere mogelijk) en kies de **groepering**: per dag, week, maand of type.
- **🧮 Totalen** — vier kaartjes: totaal uren, aantal shiften, dagen met uren, gemiddelde per dag.
- **📋 Samenvatting** — klap open om de tabel per gekozen groepering te zien.
- **🔍 Detail per shift** — klap open om alle individuele shiften te zien.
- **⬇️ Exporteren** — download als **Excel** of **PDF**.

Totalen worden getoond als **uren:minuten** (bv. `7:30`).
""")

with st.container(border=True):
    st.markdown("### 📅 Kalender")
    st.markdown(
        "Maandoverzicht met visuele weergave van ingevulde dagen:\n\n"
        "- 🟩 ingevulde dag (met aantal uren)\n"
        "- ⬜ geen uren\n"
        "- 📝 dag met notitie\n"
        "- Blauwe rand = vandaag\n\n"
        "Kies bovenaan maand en jaar. Onderaan zie je het maandtotaal."
    )

# ============================================================
# Inloggen
# ============================================================
with st.container(border=True):
    st.markdown("### 🔐 Inloggen")
    st.markdown(
        "Je krijgt een gebruikersnaam en wachtwoord van de beheerder. "
        "Werkt je login niet? Neem contact op."
    )

# ============================================================
# Telefoon
# ============================================================
with st.container(border=True):
    st.markdown("### 📱 Op je telefoon")
    st.markdown(
        "Open de app in **Chrome** → menu (drie puntjes) → **Toevoegen aan startscherm**. "
        "De app komt dan als icoon tussen je apps te staan, en opent als een volwaardige app."
    )

# ============================================================
# Problemen
# ============================================================
with st.container(border=True):
    st.markdown("### ❓ Problemen")

    st.markdown("""
- **Wijziging niet zichtbaar?** De app herlaadt soms traag. Sluit en open opnieuw, of wacht enkele seconden.
- **Iets fout ingevuld?** Ga naar de juiste dag via **Invoer** → corrigeer → klik opnieuw op **💾 Opslaan**.
- **Verkeerde shift?** Verwijder via het **🗑️**-icoon of via **Beheer**.
""")
