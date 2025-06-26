
import streamlit as st
import plotly.graph_objects as go

# --- Fonctions de calcul ---
def mensualite_credit(montant, taux_annuel, duree_annees):
    if duree_annees == 0:
        return 0
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

# --- Config Streamlit ---
st.set_page_config(page_title="Simulateur Immo Avancé", page_icon="🏠", layout="wide")
st.title("🏠 Simulateur Achat Locatif Avancé")
st.markdown("Calcule si ton achat immobilier locatif peut être autofinancé, en tenant compte de tes crédits actuels.")

# --- Inputs principaux ---
st.header("📥 Paramètres principaux")

col1, col2 = st.columns(2)
with col1:
    prix = st.number_input("💰 Prix du logement (€)", min_value=0, value=250000, step=1000)
    apport = st.slider("💼 Apport personnel (€)", min_value=0, max_value=prix, value=20000, step=1000)
with col2:
    revenu = st.number_input("👤 Revenu mensuel net (€)", min_value=0, value=3000, step=100)
    taux = st.slider("📈 Taux d’intérêt nouveau prêt (%)", min_value=1.0, max_value=10.0, value=4.0, step=0.1) / 100
    duree = st.slider("⏳ Durée du nouveau prêt (années)", min_value=5, max_value=30, value=25)

# --- Onglets crédits existants ---
st.header("📊 Crédits existants")

tab_immo, tab_conso = st.tabs(["Crédits immobiliers existants", "Crédits conso existants"])

def gerer_credits(type_credit):
    st.write(f"### {type_credit.capitalize()} existants")
    a_un_credit = st.checkbox(f"J’ai au moins un crédit {type_credit}", key=f"check_{type_credit}")
    credits = []
    if a_un_credit:
        nb_credits = st.number_input(f"Nombre de crédits {type_credit}", min_value=1, max_value=10, value=1, key=f"nb_{type_credit}")
        for i in range(nb_credits):
            st.markdown(f"**Crédit {type_credit} #{i+1}**")
            montant = st.number_input(f"Montant restant crédit {type_credit} #{i+1} (€)", min_value=0, value=5000*(i+1), step=1000, key=f"montant_{type_credit}_{i}")
            taux_c = st.slider(f"Taux crédit {type_credit} #{i+1} (%)", 0.0, 10.0, 2.0, 0.1, key=f"taux_{type_credit}_{i}") / 100
            duree_c = st.slider(f"Durée restante crédit {type_credit} #{i+1} (années)", 0, 30, 10, key=f"duree_{type_credit}_{i}")
            credits.append({"montant": montant, "taux": taux_c, "duree": duree_c})
    return credits

with tab_immo:
    credits_immo = gerer_credits("immobilier")
with tab_conso:
    credits_conso = gerer_credits("conso")

# --- Calcul des mensualités crédits existants ---
mensualite_immo_tot = sum(mensualite_credit(c["montant"], c["taux"], c["duree"]) for c in credits_immo)
mensualite_conso_tot = sum(mensualite_credit(c["montant"], c["taux"], c["duree"]) for c in credits_conso)
mensualites_existantes = mensualite_immo_tot + mensualite_conso_tot

# --- Calcul nouveau crédit ---
montant_emprunte = max(prix - apport, 0)
mensualite_nouveau = mensualite_credit(montant_emprunte, taux, duree)
assurance = (montant_emprunte * 0.004) / 12
mensualite_nouveau_totale = mensualite_nouveau + assurance

# --- Taux d’endettement total ---
if revenu > 0:
    taux_endettement_total = (mensualites_existantes + mensualite_nouveau_totale) / revenu
else:
    taux_endettement_total = 1  # Forcer si revenu nul

# --- Affichage résultats ---
st.header("📋 Résultats")

colA, colB = st.columns(2)

with colA:
    st.subheader("💳 Crédits existants")
    st.write(f"Mensualités totales crédits immobiliers : **{mensualite_immo_tot:.2f} €**")
    st.write(f"Mensualités totales crédits conso : **{mensualite_conso_tot:.2f} €**")
    st.write(f"Mensualités totales crédits existants : **{mensualites_existantes:.2f} €**")

with colB:
    st.subheader("🏠 Nouveau crédit")
    st.write(f"Montant emprunté : **{montant_emprunte:,.0f} €**")
    st.write(f"Mensualité hors assurance : **{mensualite_nouveau:.2f} €**")
    st.write(f"Assurance (~0.4%/an) : **{assurance:.2f} €**")
    st.write(f"Mensualité totale nouveau crédit : **{mensualite_nouveau_totale:.2f} €**")

st.markdown("---")
st.subheader("📊 Taux d’endettement total")
st.write(f"Taux d’endettement total (anciens + nouveau crédit) : **{taux_endettement_total*100:.1f}%**")

if revenu == 0:
    st.warning("⚠️ Veuillez entrer un revenu mensuel pour calculer le taux d’endettement.")
elif taux_endettement_total > 0.33:
    st.error("❌ Taux d’endettement trop élevé pour être finançable.")
else:
    st.success("✅ Projet finançable (endettement < 33%)")

# --- Graphiques ---

# Camembert répartition endettement
libre = max(0, 1 - taux_endettement_total)
parts = [
    mensualite_immo_tot / revenu if revenu>0 else 0,
    mensualite_conso_tot / revenu if revenu>0 else 0,
    mensualite_nouveau_totale / revenu if revenu>0 else 0,
    libre
]
labels = [
    "Crédits immobiliers existants",
    "Crédits conso existants",
    "Nouveau crédit",
    "Revenu disponible"
]
colors = ['#636EFA', '#EF553B', '#00CC96', '#AB63FA']

fig_pie = go.Figure(data=[go.Pie(labels=labels, values=parts, hole=0.4, marker_colors=colors)])
fig_pie.update_layout(title_text="Répartition du taux d'endettement total")
st.plotly_chart(fig_pie, use_container_width=True)

# Graphique barres comparatives
fig_bar = go.Figure(data=[
    go.Bar(name="Crédits immo existants", x=["Mensualités"], y=[mensualite_immo_tot], marker_color='#636EFA', text=[f"{mensualite_immo_tot:.2f} €"], textposition='auto'),
    go.Bar(name="Crédits conso existants", x=["Mensualités"], y=[mensualite_conso_tot], marker_color='#EF553B', text=[f"{mensualite_conso_tot:.2f} €"], textposition='auto'),
    go.Bar(name="Nouveau crédit", x=["Mensualités"], y=[mensualite_nouveau_totale], marker_color='#00CC96', text=[f"{mensualite_nouveau_totale:.2f} €"], textposition='auto'),
    go.Bar(name="Revenu mensuel", x=["Mensualités"], y=[revenu], marker_color='#AB63FA', text=[f"{revenu:.2f} €"], textposition='auto')
])
fig_bar.update_layout(title_text="Comparaison des mensualités et revenu", barmode='group', yaxis_title="Montant (€)")
st.plotly_chart(fig_bar, use_container_width=True)

# --- Capacité d’achat max (optionnel) ---
st.header("📈 Capacité d’achat maximale")

if revenu > 0:
    emprunt_max, prix_max = montant_max_empruntable(revenu, taux, duree, apport)
    st.write(f"Montant empruntable max : **{emprunt_max} €**")
    st.write(f"Prix d'achat max (avec apport) : **{prix_max} €**")
else:
    st.info("Entrez votre revenu pour calculer la capacité d'achat maximale.")





