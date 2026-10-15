import streamlit as st

st.title("ℹ️ Handleiding")
st.caption("Alles wat je moet weten om de app te gebruiken.")

# ============================================================
# Invoer
# ============================================================
with st.container(border=True):
    st.markdown("### 📝 Dagelijkse invoer")

    st.markdown("""
1. Open **Invoer** in het menu.
2. De datum staat standaard op **vandaag**. Werk je een oudere dag bij? Kies dan een andere datum.
3. Voor **elke shift** vul je in:
   - **Begin** en **Eind** (tijd)
   - **Type** (standaard staat dit op *Standaard*)
   - **Commentaar** (optioneel, vrije tekst)
4. Klik **💾 Shift opslaan** om te bevestigen. Pas dan wordt de shift écht bewaard.
5. Nieuwe shift toevoegen? Klik onderaan op **➕ Extra shift**.
6. Een shift wissen? Klik op het **🗑️**-icoon naast de opslaanknop.
""")

    st.info("💡 Je kan meerdere shiften per dag ingeven. "
            "Werk je die dag niet, laat dan alles leeg of verwijder de shiften.")

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
