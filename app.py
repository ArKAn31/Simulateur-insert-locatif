
import streamlit as st

# --- Fonctions ---
def mensualite_credit(montant, taux_annuel, duree_annees):
    taux_mensuel = taux_annuel / 12
    n = duree_annees * 12
    if taux_mensuel == 0:
        return montant / n
    return montant * (taux_mensuel * (1 + taux_mensuel)**n) / ((1 + taux_mensuel)**n - 1)

def montant_max_empruntable(revenu_mensuel, taux_annuel, duree_annees, apport, autres_mensualites, taux_assurance_annuel=0.004):
    mensualite_max = revenu_mensuel * 0.33 - autres_mensualites
    if mensualite_max <= 0:
        return 0, apport

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
    return round(montant_emprunte), round(montant_emprunte + apport)

# --- Configuration ---
st.set_page_config(page_title="Simulateur Immo", page_icon="🏠", layout="centered")
st.title("🏠 Simulateur Achat Locatif")
st.markdown("Calcule si ton projet immobilier est finançable et quelle est ta capacité d'achat maximale.")

# --- Paramètres utilisateur ---
st.header("📥 Paramètres")
col1, col2 = st.columns(2)

with col1:
    prix = st.number_input("💰 Prix du logement (€)", min_value=0, value=250000, step=1000)
    apport = st.slider("💼 Apport personnel (€)", min_value=0, max_value=prix, value=20000, step=1000)

with col2:
    revenu = st.number_input("👤 Revenu mensuel net (€)", min_value=0, value=2000, step=100)
    taux = st.slider("📈 Taux d’intérêt (%)", min_value=0.0, max_value=10.0, value=4.0, step=0.1) / 100
    duree = st.slider("⏳ Durée du prêt (années)", min_value=5, max_value=30, value=25)

# --- Crédits en cours ---
st.header("💳 Crédits déjà en cours")
nb_credits = st.number_input("Nombre de crédits en cours", min_value=0, max_value=5, value=0, step=1)

mensualites_existantes = 0
for i in range(nb_credits):
    st.subheader(f"Crédit #{i + 1}")
    montant = st.number_input(f"🔹 Montant restant dû crédit #{i + 1} (€)", min_value=0, value=10000, step=1000, key=f"montant_{i}")
    duree_restante = st.slider(f"⏳ Durée restante (années) crédit #{i + 1}", min_value=1, max_value=30, value=10, key=f"duree_{i}")
    taux_credit = st.slider(f"📈 Taux d’intérêt (%) crédit #{i + 1}", min_value=0.0, max_value=10.0, value=2.0, step=0.1, key=f"taux_{i}") / 100
    mensualite = mensualite_credit(montant, taux_credit, duree_restante)
    st.write(f"💸 Mensualité estimée : {mensualite:.2f} €")
    mensualites_existantes += mensualite

# --- Calcul de l’opération choisie ---
st.header("📊 Analyse de l’opération choisie")
montant_emprunte = prix - apport
mensualite = mensualite_credit(montant_emprunte, taux, duree)
assurance = (montant_emprunte * 0.004) / 12
mensualite_totale = mensualite + assurance
ratio_endettement = (mensualite_totale + mensualites_existantes) / revenu if revenu > 0 else 1

st.write(f"**Montant emprunté :** {montant_emprunte:,.0f} €")
st.write(f"**Mensualité hors assurance :** {mensualite:.2f} €")
st.write(f"**Assurance estimée (~0.4%/an) :** {assurance:.2f} €")
st.write(f"**Mensualité totale :** {mensualite_totale:.2f} €")
if mensualites_existantes > 0:
    st.write(f"**Mensualités de tes autres crédits :** {mensualites_existantes:.2f} €")

st.write(f"**Taux d’endettement total :** {ratio_endettement * 100:.1f} %")

# --- Feu vert ou rouge ---
if revenu == 0:
    st.warning("⚠️ Indique ton revenu pour évaluer la faisabilité.")
elif ratio_endettement > 0.33:
    st.error("❌ Taux d’endettement trop élevé. Le projet est difficilement finançable.")
else:
    st.success("✅ Projet finançable ! Endettement sous les 33%.")

# --- Capacité d’achat maximale ---
st.header("📈 Quelle est ta capacité d’achat maximale ?")
if revenu > 0:
    emprunt_max, prix_max = montant_max_empruntable(revenu, taux, duree, apport, mensualites_existantes)
    st.write(f"👉 Avec un apport de **{apport:,.0f} €**, tu pourrais emprunter jusqu’à **{emprunt_max:,.0f} €**.")
    st.write(f"🏡 Cela correspond à un bien immobilier d’un prix max de **{prix_max:,.0f} €**.")



