
import streamlit as st
import plotly.graph_objects as go

# --- Fonctions de calcul ---
def mensualite_credit(montant, taux_annuel, duree_annees):
    taux_mensuel = taux_annuel / 12
    n = duree_annees * 12
    if taux_mensuel == 0:
        return montant / n
    return montant * (taux_mensuel * (1 + taux_mensuel)**n) / ((1 + taux_mensuel)**n - 1)

def total_mensualites_credits(credits):
    total = 0
    for c in credits:
        mensualite = mensualite_credit(c["montant"], c["taux"], c["duree"])
        total += mensualite
    return total

# --- Page config ---
st.set_page_config("Simulateur Locatif", "🏠", layout="wide")
st.title("🏠 Simulateur Investissement Locatif")

# --- Paramètres utilisateur ---
st.sidebar.header("📥 Paramètres principaux")
prix = st.sidebar.number_input("💰 Prix du bien", 0, 2_000_000, 250000, 1000)
apport = st.sidebar.slider("💼 Apport perso (€)", 0, prix, 20000, 1000)
revenu = st.sidebar.number_input("👤 Revenu net mensuel (€)", 0, 10000, 2000, 100)
taux = st.sidebar.slider("📈 Taux crédit (%)", 1.0, 6.0, 4.0, 0.1) / 100
duree = st.sidebar.slider("⏳ Durée crédit (années)", 5, 30, 25)

# --- Crédits existants ---
st.header("📉 Crédits existants")
nb_immo = st.number_input("🏠 Nombre de crédits immobiliers en cours", 0, 5, 1)
nb_conso = st.number_input("💳 Nombre de crédits conso en cours", 0, 5, 1)

credits_existants = []

st.subheader("🏠 Crédits immobiliers")
for i in range(nb_immo):
    with st.expander(f"Immo #{i+1}"):
        m = st.number_input(f"Montant crédit immo #{i+1}", 0, 1_000_000, 100000, 1000)
        t = st.slider(f"Taux (%) immo #{i+1}", 0.0, 10.0, 2.5, 0.1) / 100
        d = st.slider(f"Durée restante (années) immo #{i+1}", 1, 30, 15)
        credits_existants.append({"montant": m, "taux": t, "duree": d})

st.subheader("💳 Crédits conso")
for i in range(nb_conso):
    with st.expander(f"Conso #{i+1}"):
        m = st.number_input(f"Montant crédit conso #{i+1}", 0, 100_000, 10000, 500)
        t = st.slider(f"Taux (%) conso #{i+1}", 0.0, 20.0, 5.0, 0.5) / 100
        d = st.slider(f"Durée restante (années) conso #{i+1}", 1, 10, 5)
        credits_existants.append({"montant": m, "taux": t, "duree": d})

# --- Nouveau crédit ---
montant_emprunte = prix - apport
assurance = (montant_emprunte * 0.004) / 12
mensualite_nouveau = mensualite_credit(montant_emprunte, taux, duree)
mensualite_totale_nouveau = mensualite_nouveau + assurance

mensualites_existants = total_mensualites_credits(credits_existants)
mensualites_total = mensualites_existants + mensualite_totale_nouveau

taux_endettement = mensualites_total / revenu if revenu else 1

# --- Affichage résultats ---
st.header("📊 Résultats")

col1, col2, col3, col4 = st.columns(4)
col1.metric("📉 Crédits existants", f"{mensualites_existants:.0f} €/mois")
col2.metric("📈 Nouveau crédit", f"{mensualite_totale_nouveau:.0f} €/mois")
col3.metric("💳 Total mensualités", f"{mensualites_total:.0f} €/mois")
col4.metric("⚖️ Taux endettement", f"{taux_endettement*100:.1f} %")

if taux_endettement > 0.33:
    st.error("❌ Endettement trop élevé (> 33%)")
else:
    st.success("✅ Projet finançable")

# --- Graphiques ---
st.subheader("📊 Visualisation")

colg1, colg2 = st.columns(2)

with colg1:
    fig = go.Figure(data=[go.Pie(labels=["Crédits existants", "Nouveau crédit", "Revenu libre"],
                                 values=[mensualites_existants, mensualite_totale_nouveau, max(revenu - mensualites_total, 0)],
                                 hole=0.3)])
    fig.update_layout(title="Répartition de l’endettement", height=400)
    st.plotly_chart(fig, use_container_width=True)

with colg2:
    fig2 = go.Figure()
    fig2.add_trace(go.Bar(name="Existants", x=["Mensualités"], y=[mensualites_existants]))
    fig2.add_trace(go.Bar(name="Nouveau", x=["Mensualités"], y=[mensualite_totale_nouveau]))
    fig2.add_trace(go.Bar(name="Total", x=["Mensualités"], y=[mensualites_total]))
    fig2.update_layout(title="Comparaison des mensualités", barmode='group', height=400)
    st.plotly_chart(fig2, use_container_width=True)



