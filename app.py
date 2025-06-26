
import streamlit as st
import plotly.graph_objects as go

# --- Fonctions ---
def mensualite_credit(montant, taux_annuel, duree_annees):
    taux_mensuel = taux_annuel / 12
    n = duree_annees * 12
    if taux_mensuel == 0:
        return montant / n
    mensualite = montant * (taux_mensuel * (1 + taux_mensuel) ** n) / ((1 + taux_mensuel) ** n - 1)
    return mensualite

# --- Page Setup ---
st.set_page_config(page_title="Simulateur Achat Locatif", page_icon="🏠", layout="centered")
st.title("🏠 Simulateur Achat Locatif")
st.markdown("**Calcule ta capacité d'achat et autofinancement locatif**")

# --- Inputs principaux ---
st.header("Paramètres de ton projet")

col1, col2 = st.columns(2)
with col1:
    prix = st.number_input("Prix du logement (€)", min_value=0, value=250000, step=1000)
    apport = st.number_input("Apport personnel (€)", min_value=0, max_value=prix, value=20000, step=1000)
    taux = st.slider("Taux d’intérêt annuel (%)", min_value=0.1, max_value=10.0, value=4.0, step=0.1) / 100
with col2:
    revenu = st.number_input("Revenu mensuel net (€)", min_value=0, value=3000, step=100)
    duree = st.slider("Durée du prêt (années)", min_value=5, max_value=30, value=25)

# --- Crédits existants avec onglets ---
st.header("Crédits existants")

tab_immo, tab_conso = st.tabs(["Crédits immobiliers", "Crédits conso"])

def saisir_credits(type_credit):
    credits = []
    n = st.number_input(f"Nombre de crédits {type_credit}", min_value=0, max_value=10, value=0, step=1, key=f"nb_{type_credit}")
    for i in range(n):
        st.markdown(f"**Crédit {i+1} - {type_credit}**")
        montant = st.number_input(f"Montant restant à rembourser (€) ({type_credit})", min_value=0, value=50000, step=1000, key=f"{type_credit}_montant_{i}")
        taux_credit = st.slider(f"Taux annuel (%) ({type_credit})", min_value=0.0, max_value=10.0, value=3.0, step=0.1, key=f"{type_credit}_taux_{i}") / 100
        duree_credit = st.slider(f"Durée restante (années) ({type_credit})", min_value=1, max_value=30, value=10, key=f"{type_credit}_duree_{i}")
        mens = mensualite_credit(montant, taux_credit, duree_credit)
        credits.append({"montant": montant, "taux": taux_credit, "duree": duree_credit, "mensualite": mens})
    return credits

with tab_immo:
    credits_immo = saisir_credits("immobilier")
with tab_conso:
    credits_conso = saisir_credits("conso")

mensualites_immo = sum(c["mensualite"] for c in credits_immo) if credits_immo else 0
mensualites_conso = sum(c["mensualite"] for c in credits_conso) if credits_conso else 0
mensualites_existantes = mensualites_immo + mensualites_conso

# --- Calcul nouveau crédit ---
montant_emprunte = prix - apport
mensualite_nouveau = mensualite_credit(montant_emprunte, taux, duree)
assurance = (montant_emprunte * 0.004) / 12
mensualite_totale_nouveau = mensualite_nouveau + assurance

# Taux d'endettement total
ratio_endettement = (mensualite_totale_nouveau + mensualites_existantes) / revenu if revenu > 0 else 1

# Pourcentage apport vs prix et vs montant emprunté
pourcentage_apport_prix = (apport / prix * 100) if prix > 0 else 0
pourcentage_apport_emprunt = (apport / montant_emprunte * 100) if montant_emprunte > 0 else 0

# --- Résultats ---
st.markdown("---")
st.header("Résultats")

# Affichage clair et structuré
st.subheader("📝 Détail des crédits existants")
st.write(f"Mensualités totales crédits immobiliers : **{mensualites_immo:,.2f} €**")
st.write(f"Mensualités totales crédits conso : **{mensualites_conso:,.2f} €**")
st.write(f"Mensualités totales crédits existants : **{mensualites_existantes:,.2f} €**")

st.subheader("🏠 Nouveau crédit")
st.write(f"Montant emprunté : **{montant_emprunte:,.0f} €**")
st.write(f"Apport personnel : **{apport:,.0f} €** soit **{pourcentage_apport_prix:.1f}%** du prix total et **{pourcentage_apport_emprunt:.1f}%** du montant emprunté")
st.write(f"Mensualité hors assurance : **{mensualite_nouveau:.2f} €**")
st.write(f"Assurance (~0.4%/an) : **{assurance:.2f} €**")
st.write(f"Mensualité totale nouveau crédit : **{mensualite_totale_nouveau:.2f} €**")

total_mensualites = mensualite_totale_nouveau + mensualites_existantes

st.markdown("---")
st.subheader("📊 Totaux & taux d'endettement")
st.write(f"Mensualités totales (anciens + nouveau) : **{total_mensualites:,.2f} €**")
st.write(f"Taux d’endettement global : **{ratio_endettement * 100:.1f} %**")

if revenu == 0:
    st.warning("⚠️ Tu dois entrer un revenu mensuel pour estimer la faisabilité.")
elif ratio_endettement > 0.33:
    st.error("❌ Taux d’endettement trop élevé (>33%), projet risqué.")
else:
    st.success("✅ Projet finançable (endettement < 33%)")

# --- Graphiques ---
st.markdown("---")
st.header("Visualisation")

# Camembert du taux d’endettement total
labels = ["Crédits existants", "Nouveau crédit", "Capacité restante"]
values = [mensualites_existantes, mensualite_totale_nouveau, max(0, revenu - total_mensualites)]

fig_pie = go.Figure(data=[go.Pie(labels=labels, values=values, hole=0.5,
                                 marker=dict(colors=['#636EFA', '#EF553B', '#00CC96']),
                                 hoverinfo="label+percent+value")])
fig_pie.update_layout(title_text="Répartition du taux d’endettement total", title_x=0.5,
                      font=dict(size=14), legend=dict(orientation="h", y=-0.1))

# Graphique barre des mensualités
fig_bar = go.Figure(data=[
    go.Bar(name='Mensualités crédits existants', x=['Mensualités'], y=[mensualites_existantes], marker_color='#636EFA'),
    go.Bar(name='Mensualité nouveau crédit', x=['Mensualités'], y=[mensualite_totale_nouveau], marker_color='#EF553B'),
    go.Bar(name='Total mensualités', x=['Mensualités'], y=[total_mensualites], marker_color='#AB63FA'),
    go.Bar(name='% du revenu', x=['Mensualités'], y=[(total_mensualites / revenu * 100) if revenu > 0 else 0], marker_color='#00CC96')
])
fig_bar.update_layout(title_text="Comparaison des mensualités", title_x=0.5,
                      yaxis=dict(title="€ ou %"), barmode='group',
                      font=dict(size=14))

col1, col2 = st.columns(2)
with col1:
    st.plotly_chart(fig_pie, use_container_width=True)
with col2:
    st.plotly_chart(fig_bar, use_container_width=True)







