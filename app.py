
import streamlit as st

# --- Fonctions de calcul ---
def mensualite_credit(montant, taux_annuel, duree_annees):
    taux_mensuel = taux_annuel / 12
    n = duree_annees * 12
    if taux_mensuel == 0:
        return montant / n
    mensualite = montant * (taux_mensuel * (1 + taux_mensuel)**n) / ((1 + taux_mensuel)**n - 1)
    return mensualite

def montant_max_empruntable(revenu_mensuel, taux_annuel, duree_annees, apport, taux_assurance_annuel=0.004):
    mensualite_max = revenu_mensuel * 0.33
    low, high = 0, 1_000_000
    precision = 1

    while high - low > precision:
        mid = (low + high) / 2
        assurance = (mid * taux_assurance_annuel) / 12
        mensualite = mensualite_credit(mid, taux_annuel, duree_annees) + assurance
        if mensualite > mensualite_max:
            high = mid
        else:
            low = mid

    montant_emprunte = low
    prix_total = montant_emprunte + apport
    return round(montant_emprunte), round(prix_total)

# --- Configuration de la page ---
st.set_page_config(page_title="Simulateur Immo", page_icon="🏠", layout="centered")

st.title("🏠 Simulateur Achat Locatif")
st.markdown("**Calcule si ton achat immobilier locatif peut être autofinancé et quel est ton budget max.**")

# --- Entrées utilisateur ---
st.header("📥 Paramètres")
col1, col2 = st.columns(2)

with col1:
    prix = st.number_input("💰 Prix du logement (€)", min_value=0, value=250000, step=1000)
    apport = st.slider("💼 Apport personnel (€)", min_value=0, max_value=prix, value=20000, step=1000)

with col2:
    revenu = st.number_input("👤 Revenu mensuel net (€)", min_value=0, value=2000, step=100)
    taux = st.slider("📈 Taux d’intérêt (%)", min_value=1.0, max_value=5.0, value=4.0, step=0.1) / 100
    duree = st.slider("⏳ Durée du prêt (années)", min_value=5, max_value=30, value=25)

# --- Calcul autofinancement ---
montant_emprunte = prix - apport
mensualite = mensualite_credit(montant_emprunte, taux, duree)
assurance = (montant_emprunte * 0.004) / 12
mensualite_totale = mensualite + assurance
ratio_endettement = mensualite_totale / revenu

# --- Affichage résultats autofinancement ---
st.header("📊 Analyse de l’opération choisie")
st.write(f"**Montant emprunté :** {montant_emprunte:,.0f} €")
st.write(f"**Mensualité hors assurance :** {mensualite:.2f} €")
st.write(f"**Assurance estimée (~0.4%/an) :** {assurance:.2f} €")
st.write(f"**Mensualité totale :** {mensualite_totale:.2f} €")
st.write(f"**Taux d’endettement :** {ratio_endettement * 100:.1f} %")

if ratio_endettement > 33:
    st.error("❌ Taux d’endettement trop élevé pour être finançable.")
else:
    st.success("✅ Projet finançable (endettement < 33%)")

# --- Calcul capacité d’achat max ---
st.header("📈 Quelle est ta capacité d’achat maximale ?")
emprunt_max, prix_max = montant_max_empruntable(
    revenu, taux, duree, apport
)

st.write(f"👉 Avec un apport de **{apport:,.0f} €**, tu pourrais emprunter jusqu’à **{emprunt_max:,.0f} €**.")
st.write(f"🏡 Cela correspond à un bien immobilier d’un prix max de **{prix_max:,.0f} €**.")



