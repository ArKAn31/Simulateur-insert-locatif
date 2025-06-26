
import streamlit as st
import plotly.graph_objects as go

# --- Fonctions de calcul ---
def mensualite_credit(montant, taux_annuel, duree_annees):
    taux_mensuel = taux_annuel / 12
    n = duree_annees * 12
    if taux_mensuel == 0:
        return montant / n
    return montant * (taux_mensuel * (1 + taux_mensuel)**n) / ((1 + taux_mensuel)**n - 1)

def calc_assurance(montant, taux_annuel=0.004):
    return (montant * taux_annuel) / 12

st.set_page_config("Simulateur Locatif", "🏠", layout="wide")
st.title("🏠 Simulateur Achat Locatif")

tabs = st.tabs(["Paramètres généraux", "Crédits existants", "Résultats"])

# --- Paramètres généraux ---
with tabs[0]:
    st.header("📋 Paramètres")
    col1, col2 = st.columns(2)
    with col1:
        prix = st.number_input("Prix du logement (€)", 0, 2_000_000, 250_000, step=1000)
        apport = st.slider("Apport personnel (€)", 0, prix, 20_000, step=1000)
    with col2:
        revenu = st.number_input("Revenu mensuel (€)", 0, 100_000, 3000, step=100)
        taux = st.slider("Taux d’intérêt annuel (%)", 0.5, 10.0, 3.5, step=0.1) / 100
        duree = st.slider("Durée du prêt (années)", 5, 30, 20)

# --- Crédits existants ---
with tabs[1]:
    st.header("💳 Crédits existants")

    # Choix du nombre de crédits
    nb_immo = st.selectbox("Nombre de crédits immobiliers", range(6), index=0)
    nb_conso = st.selectbox("Nombre de crédits conso", range(6), index=0)

    # Crédits immo
    st.subheader("🏠 Crédits immobiliers")
    credits_immo = []
    for i in range(nb_immo):
        with st.expander(f"Crédit immo #{i+1}", expanded=True):
            montant = st.number_input(f"Montant restant dû crédit immo #{i+1} (€)", 0, 2_000_000, 100_000, key=f"immo_montant_{i}")
            taux_ = st.slider(f"Taux crédit immo #{i+1} (%)", 0.0, 10.0, 3.0, 0.1, key=f"immo_taux_{i}") / 100
            duree_ = st.number_input(f"Durée restante (années) crédit immo #{i+1}", 1, 40, 15, key=f"immo_duree_{i}")
            credits_immo.append({"montant": montant, "taux": taux_, "duree": duree_})

    # Crédits conso
    st.subheader("💸 Crédits à la consommation")
    credits_conso = []
    for i in range(nb_conso):
        with st.expander(f"Crédit conso #{i+1}", expanded=True):
            montant = st.number_input(f"Montant restant dû crédit conso #{i+1} (€)", 0, 500_000, 10_000, key=f"conso_montant_{i}")
            taux_ = st.slider(f"Taux crédit conso #{i+1} (%)", 0.0, 15.0, 5.0, 0.1, key=f"conso_taux_{i}") / 100
            duree_ = st.number_input(f"Durée restante (années) crédit conso #{i+1}", 1, 30, 5, key=f"conso_duree_{i}")
            credits_conso.append({"montant": montant, "taux": taux_, "duree": duree_})

# --- Résultats ---
with tabs[2]:
    st.header("📊 Résultats")

    total_mens_immo = sum(mensualite_credit(c["montant"], c["taux"], c["duree"]) + calc_assurance(c["montant"]) for c in credits_immo)
    total_mens_conso = sum(mensualite_credit(c["montant"], c["taux"], c["duree"]) + calc_assurance(c["montant"]) for c in credits_conso)
    total_existants = total_mens_immo + total_mens_conso

    montant_nouveau = max(prix - apport, 0)
    mensu_nouveau = mensualite_credit(montant_nouveau, taux, duree)
    assurance_nouveau = calc_assurance(montant_nouveau)
    total_mensualite = mensu_nouveau + assurance_nouveau + total_existants

    st.subheader("Synthèse")
    st.markdown(f"- **Montant emprunté :** {montant_nouveau:,.0f} €")
    st.markdown(f"- **Mensualité nouveau crédit :** {mensu_nouveau:,.0f} €")
    st.markdown(f"- **Assurance :** {assurance_nouveau:,.0f} €")
    st.markdown(f"- **Crédits existants :** {total_existants:,.0f} €")
    st.markdown(f"- **Total mensualités :** {total_mensualite:,.0f} €")
    st.markdown(f"- **Revenu mensuel :** {revenu:,.0f} €")

    # Graphique
    fig = go.Figure()
    fig.add_trace(go.Bar(x=["Crédits existants", "Nouveau crédit"],
                         y=[total_existants, mensu_nouveau + assurance_nouveau],
                         marker_color=["#636EFA", "#EF553B"]))
    fig.update_layout(title="Mensualités par type", yaxis_title="Montant (€)",
                      yaxis=dict(range=[0, max(total_mensualite, revenu) * 1.2]),
                      template="plotly_white")
    st.plotly_chart(fig, use_container_width=True)

    # Endettement
    ratio = total_mensualite / revenu if revenu > 0 else 0
    st.markdown(f"### 📉 Ratio d'endettement : **{ratio*100:.1f}%**")
















