import streamlit as st

st.title("ℹ️ Handleiding")
st.caption("Alles wat je moet weten om de app te gebruiken.")

st.markdown("""
### 📝 Dagelijkse invoer

1. Open **Invoer** in het menu.
2. De datum staat standaard op **vandaag**. Werk je een oudere dag bij? Kies dan een andere datum.
3. Voor **elke shift** vul je in:
   - **Begin** en **Eind** (tijd)
   - **Type** (standaard staat dit op *Standaard*)
   - **Commentaar** (optioneel, vrije tekst)
4. Klik **💾 Shift opslaan** om te bevestigen. Pas dan wordt de shift écht bewaard.
5. Nieuwe shift toevoegen? Klik onderaan op **➕ Extra shift**.
6. Een shift wissen? Klik op het **🗑️**-icoon naast de opslaanknop.

> 💡 Je kan meerdere shiften per dag ingeven. Als je een dag niet werkt, laat je gewoon alles leeg of verwijder je de shiften.

---

### ⚙️ Beheer

Hier kan je:

- **Types aanpassen** — dit zijn de opties in de dropdown bij een shift (bv. *Verlof*, *Ziekte*, *Klant X*). *Standaard* kan je niet verwijderen.
- **Shiften verwijderen** — kies een periode, klap een dag open en verwijder een specifieke shift met **dubbele bevestiging**.

---

### 📊 Rapporten

- Kies een **periode**: dag, week, maand of een vrije datumrange.
- **Filter** op type indien gewenst.
- **Groepeer** per dag, week, maand of type.
- Onderaan vind je de knoppen om te **exporteren** naar **Excel** of **PDF**.
- Totalen worden getoond als **uren:minuten** (bv. `7:30`).

---

### 🔐 Inloggen

Je krijgt een gebruikersnaam en wachtwoord van de beheerder. Vergeten of werkt niet? Neem contact op.

---

### 📱 Op je telefoon

Open de app in **Chrome** → menu (drie puntjes) → **Toevoegen aan startscherm**. De app komt dan als icoon tussen je apps te staan, en opent als een volwaardige app.

---

### ❓ Problemen

- **Wijziging niet zichtbaar?** De app herlaadt soms traag. Sluit en open opnieuw, of wacht enkele seconden.
- **Iets fout ingevuld?** Ga naar de juiste dag via **Invoer** → corrigeer → klik opnieuw op **💾 Opslaan**.
- **Verkeerde shift?** Verwijder via het **🗑️**-icoon of via **Beheer**.
""")
