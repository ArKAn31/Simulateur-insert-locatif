
import streamlit as st

def mensualite_credit(montant, taux_annuel, duree_annees):
    taux_mensuel = taux_annuel / 12
    n = duree_annees * 12
    mensualite = montant * (taux_mensuel * (1 + taux_mensuel)**n) / ((1 + taux_mensuel)**n - 1)
    return mensualite

st.set_page_config(page_title="Simulateur Immo", page_icon="🏠", layout="centered")

st.title("🏠 Simulateur Achat Locatif")
st.markdown("**Calcule si ton achat immobilier locatif peut être autofinancé.**")

# Entrées
prix = st.number_input("💰 Prix du logement (€)", min_value=0, value=250000, step=1000)
apport = st.slider("💼 Apport personnel (€)", min_value=0, max_value=prix, value=20000, step=1000)
revenu = st.number_input("👤 Revenu mensuel net (€)", min_value=0, value=2000, step=100)
taux = st.slider("📈 Taux d’intérêt (%)", min_value=1.0, max_value=5.0, value=4.0, step=0.1) / 100
duree = st.slider("⏳ Durée du prêt (années)", min_value=5, max_value=30, value=25)

# Calculs
montant_emprunte = prix - apport
mensualite = mensualite_credit(montant_emprunte, taux, duree)
assurance = (montant_emprunte * 0.004) / 12
mensualite_totale = mensualite + assurance
ratio_endettement = mensualite_totale / revenu

# Résultats
st.subheader("📊 Résultats")
st.write(f"**Montant emprunté :** {montant_emprunte:,.0f} €")
st.write(f"**Mensualité hors assurance :** {mensualite:.2f} €")
st.write(f"**Assurance estimée (~0.4%/an) :** {assurance:.2f} €")
st.write(f"**Mensualité totale :** {mensualite_totale:.2f} €")
st.write(f"**Taux d’endettement :** {ratio_endettement * 100:.1f} %")

# Analyse
if ratio_endettement > 33:
    st.error("❌ Taux d’endettement trop élevé pour être finançable.")
else:
    st.success("✅ Projet finançable (endettement < 33%)")
