
import streamlit as st
import plotly.graph_objects as go

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

# --- Streamlit Config ---
st.set_page_config(page_title="Simulateur Achat Locatif Avancé", page_icon="🏠", layout="wide")
st.title("🏠 Simulateur Achat Locatif Avancé")

# --- Inputs utilisateur ---
with st.sidebar:
    st.header("Paramètres du projet")
    prix = st.number_input("Prix du logement (€)", value=250_000, step=1000, min_value=0)
    apport = st.slider("Apport personnel (€)", 0, prix, 20_000, step=1000)
    revenu = st.number_input("Revenu mensuel net (€)", value=2000, step=100)
    taux = st.slider("Taux d’intérêt (%)", 1.0, 5.0, 4.0, 0.1) / 100
    duree = st.slider("Durée du prêt (années)", 5, 30, 25)

# --- Saisie crédits existants ---
st.header("📋 Crédits existants")

credits = []

# Fonction pour saisir un crédit
def saisir_credit(idx):
    st.subheader(f"Crédit #{idx+1}")
    montant = st.number_input(f"Montant restant dû crédit #{idx+1} (€)", min_value=0, step=1000, key=f"montant_{idx}")
    taux_c = st.slider(f"Taux annuel crédit #{idx+1} (%)", 0.0, 10.0, 3.0, 0.1, key=f"taux_{idx}") / 100
    duree_c = st.slider(f"Durée restante crédit #{idx+1} (années)", 0, 30, 10, key=f"duree_{idx}")
    return montant, taux_c, duree_c

# Choix du nombre de crédits existants
nb_credits = st.slider("Nombre de crédits existants", 0, 5, 0)

for i in range(nb_credits):
    montant_c, taux_c, duree_c = saisir_credit(i)
    credits.append({'montant': montant_c, 'taux': taux_c, 'duree': duree_c})

# --- Calcul mensualité crédits existants ---
mensualites_credits_existants = 0
for c in credits:
    mensualites_credits_existants += mensualite_credit(c['montant'], c['taux'], c['duree'])

# --- Calcul nouvelle opération ---
montant_emprunte = prix - apport
mensualite_nouvelle = mensualite_credit(montant_emprunte, taux, duree)
assurance = (montant_emprunte * 0.004) / 12
mensualite_nouvelle_totale = mensualite_nouvelle + assurance

# --- Calcul taux d'endettement total ---
mensualites_totales = mensualites_credits_existants + mensualite_nouvelle_totale
if revenu > 0:
    taux_endettement = mensualites_totales / revenu
else:
    taux_endettement = 1

# --- Affichage résultats ---
st.header("📊 Résultats")

st.markdown(f"**Montant emprunté pour ce projet :** {montant_emprunte:,.0f} €")
st.markdown(f"**Mensualité nouvelle opération (avec assurance) :** {mensualite_nouvelle_totale:.2f} €")
st.markdown(f"**Mensualités crédits existants :** {mensualites_credits_existants:.2f} €")
st.markdown(f"**Mensualités totales (nouveau + existants) :** {mensualites_totales:.2f} €")
st.markdown(f"**Taux d'endettement total :** {taux_endettement * 100:.1f} %")

if taux_endettement > 0.33:
    st.error("❌ Taux d'endettement trop élevé pour être finançable.")
else:
    st.success("✅ Projet finançable (endettement < 33%)")

# --- Graphiques ---

st.header("📈 Visualisation du taux d'endettement")

# Part du revenu dans le camembert
part_existants = mensualites_credits_existants / revenu if revenu > 0 else 0
part_nouveau = mensualite_nouvelle_totale / revenu if revenu > 0 else 0
part_libre = max(0, 1 - part_existants - part_nouveau)

labels = ["Crédits existants", "Nouveau crédit", "Revenu disponible"]
values = [part_existants, part_nouveau, part_libre]

fig_pie = go.Figure(data=[go.Pie(labels=labels, values=values, hole=0.4)])
fig_pie.update_traces(marker=dict(colors=['#636EFA', '#EF553B', '#00CC96']))
fig_pie.update_layout(title_text="Répartition du taux d'endettement total")

st.plotly_chart(fig_pie, use_container_width=True)

# Barres mensuelles côte à côte
st.header("📊 Comparaison des mensualités")

fig_bar = go.Figure(data=[
    go.Bar(name='Crédits existants', x=['Mensualités'], y=[mensualites_credits_existants], marker_color='#636EFA'),
    go.Bar(name='Nouveau crédit', x=['Mensualités'], y=[mensualite_nouvelle_totale], marker_color='#EF553B'),
    go.Bar(name='Total', x=['Mensualités'], y=[mensualites_totales], marker_color='#AB63FA')
])

fig_bar.update_layout(barmode='group', yaxis_title='Montant (€)', title='Mensualités comparées')

st.plotly_chart(fig_bar, use_container_width=True)



