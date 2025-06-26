
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

# --- State init ---
def init_session_state():
    if "credits_immo" not in st.session_state:
        st.session_state.credits_immo = []
    if "credits_conso" not in st.session_state:
        st.session_state.credits_conso = []
    if "page" not in st.session_state:
        st.session_state.page = "start"

def add_credit_immo():
    st.session_state.credits_immo.append({"montant": 0, "taux": 0.03, "duree": 10})

def add_credit_conso():
    st.session_state.credits_conso.append({"montant": 0, "taux": 0.05, "duree": 5})

def go_to_app():
    st.session_state.page = "app"

def go_to_start():
    st.session_state.page = "start"
    st.session_state.credits_immo = []
    st.session_state.credits_conso = []

st.set_page_config("Simulateur Locatif", "🏠", layout="wide")
init_session_state()

# --- Page d'accueil ---
if st.session_state.page == "start":
    st.title("🏠 Simulateur d'Achat Locatif")
    st.write("Bienvenue ! Cliquez pour démarrer la simulation.")
    if st.button("🚀 Démarrer", on_click=go_to_app):
        pass

# --- App principale ---
else:
    st.title("🏠 Simulateur Achat Locatif")
    tabs = st.tabs(["Paramètres généraux", "Crédits existants", "Résultats & Graphiques"])

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

        # Crédits immo
        st.subheader("🏠 Crédits immobiliers")
        if st.button("➕ Ajouter un crédit immo"):
            add_credit_immo()

        for i in range(len(st.session_state.credits_immo)):
            with st.expander(f"Crédit immo #{i}", expanded=True):
                credit = st.session_state.credits_immo[i]
                col1, col2, col3, col4 = st.columns([3, 3, 3, 1])
                with col1:
                    montant = st.number_input("Montant (€)", 0, 2_000_000, credit["montant"], key=f"immo_montant_{i}")
                with col2:
                    taux_ = st.slider("Taux (%)", 0.0, 10.0, credit["taux"] * 100, 0.1, key=f"immo_taux_{i}") / 100
                with col3:
                    duree_ = st.number_input("Durée (années)", 1, 40, credit["duree"], key=f"immo_duree_{i}")
                with col4:
                    if st.button("❌", key=f"suppr_immo_{i}"):
                        st.session_state.credits_immo.pop(i)
                        st.experimental_rerun()
                credit.update({"montant": montant, "taux": taux_, "duree": duree_})

        st.markdown("---")

        # Crédits conso
        st.subheader("💸 Crédits à la consommation")
        if st.button("➕ Ajouter un crédit conso"):
            add_credit_conso()

        for i in range(len(st.session_state.credits_conso)):
            with st.expander(f"Crédit conso #{i}", expanded=True):
                credit = st.session_state.credits_conso[i]
                col1, col2, col3, col4 = st.columns([3, 3, 3, 1])
                with col1:
                    montant = st.number_input("Montant (€)", 0, 500_000, credit["montant"], key=f"conso_montant_{i}")
                with col2:
                    taux_ = st.slider("Taux (%)", 0.0, 15.0, credit["taux"] * 100, 0.1, key=f"conso_taux_{i}") / 100
                with col3:
                    duree_ = st.number_input("Durée (années)", 1, 30, credit["duree"], key=f"conso_duree_{i}")
                with col4:
                    if st.button("❌", key=f"suppr_conso_{i}"):
                        st.session_state.credits_conso.pop(i)
                        st.experimental_rerun()
                credit.update({"montant": montant, "taux": taux_, "duree": duree_})

    # --- Résultats ---
    with tabs[2]:
        st.header("📊 Résultats")

        total_mens_immo = sum(mensualite_credit(c["montant"], c["taux"], c["duree"]) + calc_assurance(c["montant"])
                              for c in st.session_state.credits_immo)
        total_mens_conso = sum(mensualite_credit(c["montant"], c["taux"], c["duree"]) + calc_assurance(c["montant"])
                               for c in st.session_state.credits_conso)
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

    st.markdown("---")
    if st.button("⬅️ Retour à l’accueil", on_click=go_to_start):
        pass
















