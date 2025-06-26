
import streamlit as st
import matplotlib.pyplot as plt

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

# --- Configuration Streamlit ---
st.set_page_config(page_title="Simulateur Immo", page_icon="🏠", layout="centered")
st.title("🏠 Simulateur Achat Locatif")
st.markdown("**Calcule si ton achat immobilier locatif peut être autofinancé, et ta capacité d'achat maximale.**")

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

# --- Entrées crédits existants ---
st.header("📉 Crédits existants")
col3, col4 = st.columns(2)

with col3:
    montant_credits = st.number_input("Montant total crédits en cours (€)", min_value=0, value=0, step=1000)
    taux_credits = st.slider("Taux moyen crédits existants (%)", min_value=0.0, max_value=10.0, value=2.0, step=0.1) / 100
with col4:
    duree_credits = st.slider("Durée restante crédits existants (années)", min_value=0, max_value=30, value=0)
    
# --- Calculs ---
# Nouveau crédit
montant_emprunte = prix - apport
mensualite = mensualite_credit(montant_emprunte, taux, duree)
assurance = (montant_emprunte * 0.004) / 12
mensualite_nouveau = mensualite + assurance

# Crédits existants
mensualite_credits = mensualite_credit(montant_credits, taux_credits, duree_credits) if montant_credits > 0 and duree_credits > 0 else 0

# Total mensualités
mensualite_totale = mensualite_nouveau + mensualite_credits

# Ratio endettement
if revenu > 0:
    ratio_endettement = mensualite_totale / revenu
else:
    ratio_endettement = 1  # Forcer endettement élevé si revenu nul

# --- Affichage résultats autofinancement ---
st.header("📊 Analyse de l’opération choisie")
st.write(f"**Montant emprunté :** {montant_emprunte:,.0f} €")
st.write(f"**Mensualité hors assurance (nouveau crédit) :** {mensualite:.2f} €")
st.write(f"**Assurance estimée (~0.4%/an) :** {assurance:.2f} €")
st.write(f"**Mensualité totale nouveau crédit :** {mensualite_nouveau:.2f} €")
st.write(f"**Mensualité totale crédits existants :** {mensualite_credits:.2f} €")
st.write(f"**Mensualité totale (crédits + nouveau) :** {mensualite_totale:.2f} €")
st.write(f"**Taux d’endettement global :** {ratio_endettement * 100:.1f} %")

if revenu == 0:
    st.warning("⚠️ Tu dois entrer un revenu mensuel pour estimer la faisabilité.")
elif ratio_endettement > 0.33:
    st.error("❌ Taux d’endettement trop élevé pour être finançable.")
else:
    st.success("✅ Projet finançable (endettement < 33%)")

# --- Calcul capacité d’achat max ---
st.header("📈 Capacité d’achat maximale")
if revenu > 0:
    emprunt_max, prix_max = montant_max_empruntable(
        revenu, taux, duree, apport
    )
    st.write(f"👉 Avec un apport de **{apport:,.0f} €**, tu pourrais emprunter jusqu’à **{emprunt_max:,.0f} €**.")
    st.write(f"🏡 Cela correspond à un bien immobilier d’un prix max de **{prix_max:,.0f} €**.")

# --- Graphiques ---

# Camembert endettement
st.header("📊 Répartition du taux d’endettement")

part_credits_existants = mensualite_credits / revenu if revenu > 0 else 0
part_nouveau_credit = mensualite_nouveau / revenu if revenu > 0 else 0
part_libre = 1 - (part_credits_existants + part_nouveau_credit)
if part_libre < 0:
    part_libre = 0

labels = ['Crédits existants', 'Nouveau crédit', 'Capacité restante']
sizes = [part_credits_existants, part_nouveau_credit, part_libre]
colors = ['#ff9999','#66b3ff','#99ff99']

fig1, ax1 = plt.subplots()
ax1.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90, colors=colors)
ax1.axis('equal')  # Cercle parfait
st.pyplot(fig1)

# Graphique barres mensualités
st.header("📉 Comparaison des mensualités")

labels_bar = ['Crédits existants', 'Nouveau crédit', 'Total mensualités']
values_bar = [mensualite_credits, mensualite_nouveau, mensualite_totale]

fig2, ax2 = plt.subplots()
bars = ax2.bar(labels_bar, values_bar, color=['#ff9999','#66b3ff','#555555'])
ax2.set_ylabel('Montant (€)')
ax2.set_title('Mensualités en euros')

# Ajout % du revenu au-dessus des barres
for bar in bars:
    height = bar.get_height()
    pct = (height / revenu * 100) if revenu > 0 else 0
    ax2.text(bar.get_x() + bar.get_width()/2., height, f'{pct:.1f}%', ha='center', va='bottom')

st.pyplot(fig2)



