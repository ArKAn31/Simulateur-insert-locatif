
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

def calc_assurance(montant, taux_assurance_annuel=0.004):
    return (montant * taux_assurance_annuel) / 12

# --- Session State Helpers ---
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

# --- Setup page ---
st.set_page_config(page_title="Simulateur Achat Locatif", page_icon="🏠", layout="wide")
init_session_state()

if st.session_state.page == "start":
    st.title("🏠 Simulateur Achat Locatif")
    st.write("Bienvenue sur le simulateur d'achat locatif !")
    st.write("Cliquez sur le bouton ci-dessous pour commencer la simulation.")
    if st.button("Démarrer la simulation", on_click=go_to_app):
        pass

else:
    st.title("🏠 Simulateur Achat Locatif Avancé")

    tabs = st.tabs(["Paramètres généraux", "Crédits existants", "Résultats & Graphiques"])

    with tabs[0]:
        st.header("📥 Paramètres généraux")

        col1, col2 = st.columns(2)
        with col1:
            prix = st.number_input("💰 Prix du logement (€)", min_value=0, value=250000, step=1000)
            apport = st.slider("💼 Apport personnel (€)", min_value=0, max_value=prix, value=20000, step=1000)

            # Boutons pour fixer l'apport en % du prix
            col_apport_1, col_apport_2, col_apport_3 = st.columns(3)
            with col_apport_1:
                if st.button("10% apport"):
                    apport = int(prix * 0.10)
            with col_apport_2:
                if st.button("15% apport"):
                    apport = int(prix * 0.15)
            with col_apport_3:
                if st.button("20% apport"):
                    apport = int(prix * 0.20)

            # Slider ajusté si modifié par bouton
            apport = st.slider("💼 Apport personnel ajusté (€)", min_value=0, max_value=prix, value=apport, step=1000)

            apport_pct = (apport / prix * 100) if prix > 0 else 0
            st.markdown(f"**Apport représente {apport_pct:.1f}% du prix.**")

        with col2:
            revenu = st.number_input("👤 Revenu mensuel net (€)", min_value=0, value=3000, step=100)
            taux = st.slider("📈 Taux d’intérêt annuel (%)", min_value=0.5, max_value=10.0, value=3.5, step=0.1) / 100
            duree = st.slider("⏳ Durée du prêt (années)", min_value=5, max_value=30, value=20)

    with tabs[1]:
        st.header("💳 Crédits existants")

        # IMMOBILIERS
        st.subheader("Crédits immobiliers")
        has_immo = st.checkbox("J’ai un ou plusieurs crédits immobiliers existants", value=len(st.session_state.credits_immo) > 0)
        if has_immo:
            if st.button("➕ Ajouter un crédit immobilier"):
                add_credit_immo()

            indices_a_supprimer_immo = []
            for i, credit in enumerate(st.session_state.credits_immo):
                with st.expander(f"Crédit immobilier #{i+1}", expanded=True):
                    colm1, colm2, colm3, colm4 = st.columns([2, 2, 2, 1])
                    with colm1:
                        montant = st.number_input(f"🏦 Capital restant dû sur ce crédit immo #{i+1} (€)", min_value=0, value=credit["montant"], key=f"immo_montant_{i}")
                    with colm2:
                        taux_ = st.slider(f"Taux (%) crédit immo #{i+1}", min_value=0.0, max_value=10.0, value=credit["taux"]*100, step=0.1, key=f"immo_taux_{i}") / 100
                    with colm3:
                        duree_ = st.number_input(f"Durée restante (années) crédit immo #{i+1}", min_value=1, max_value=40, value=credit["duree"], key=f"immo_duree_{i}")
                    with colm4:
                        if st.button(f"❌ Supprimer", key=f"immo_del_{i}"):
                            indices_a_supprimer_immo.append(i)

                    # Mise à jour des données
                    st.session_state.credits_immo[i]["montant"] = montant
                    st.session_state.credits_immo[i]["taux"] = taux_
                    st.session_state.credits_immo[i]["duree"] = duree_

            # Suppression hors boucle
            if indices_a_supprimer_immo:
                for idx in sorted(indices_a_supprimer_immo, reverse=True):
                    st.session_state.credits_immo.pop(idx)
                st.experimental_rerun()

        # CONSO
        st.subheader("Crédits à la consommation")
        has_conso = st.checkbox("J’ai un ou plusieurs crédits à la consommation existants", value=len(st.session_state.credits_conso) > 0)
        if has_conso:
            if st.button("➕ Ajouter un crédit conso"):
                add_credit_conso()

            indices_a_supprimer_conso = []
            for i, credit in enumerate(st.session_state.credits_conso):
                with st.expander(f"Crédit conso #{i+1}", expanded=True):
                    colc1, colc2, colc3, colc4 = st.columns([2, 2, 2, 1])
                    with colc1:
                        montant = st.number_input(f"🏦 Capital restant dû sur ce crédit conso #{i+1} (€)", min_value=0, value=credit["montant"], key=f"conso_montant_{i}")
                    with colc2:
                        taux_ = st.slider(f"Taux (%) crédit conso #{i+1}", min_value=0.0, max_value=15.0, value=credit["taux"]*100, step=0.1, key=f"conso_taux_{i}") / 100
                    with colc3:
                        duree_ = st.number_input(f"Durée restante (années) crédit conso #{i+1}", min_value=1, max_value=20, value=credit["duree"], key=f"conso_duree_{i}")
                    with colc4:
                        if st.button(f"❌ Supprimer", key=f"conso_del_{i}"):
                            indices_a_supprimer_conso.append(i)

                    # Mise à jour des données
                    st.session_state.credits_conso[i]["montant"] = montant
                    st.session_state.credits_conso[i]["taux"] = taux_
                    st.session_state.credits_conso[i]["duree"] = duree_

            # Suppression hors boucle
            if indices_a_supprimer_conso:
                for idx in sorted(indices_a_supprimer_conso, reverse=True):
                    st.session_state.credits_conso.pop(idx)
                st.experimental_rerun()

    with tabs[2]:
        st.header("📊 Résultats & Graphiques")

        # Calcul mensualités crédits existants
        total_mensualites_immo = sum(
            mensualite_credit(c["montant"], c["taux"], c["duree"]) + calc_assurance(c["montant"])
            for c in st.session_state.credits_immo
        )
        total_mensualites_conso = sum(
            mensualite_credit(c["montant"], c["taux"], c["duree"]) + calc_assurance(c["montant"])
            for c in st.session_state.credits_conso
        )
        total_credits_existants = total_mensualites_immo + total_mensualites_conso

        # Nouveau crédit
        montant_emprunte = max(prix - apport, 0)
        mensu_nouveau = mensualite_credit(montant_emprunte, taux, duree) if montant_emprunte > 0 else 0
        assurance_nouveau = calc_assurance(montant_emprunte) if montant_emprunte > 0 else 0

        st.subheader("Synthèse")
        st.markdown(f"- **Montant emprunté pour le nouveau crédit :** {montant_emprunte:,.0f} €")
        st.markdown(f"- **Mensualité nouveau crédit (hors assurance) :** {mensu_nouveau:,.0f} €")
        st.markdown(f"- **Assurance mensuelle nouveau crédit :** {assurance_nouveau:,.0f} €")
        st.markdown(f"- **Total mensualités crédits existants :** {total_credits_existants:,.0f} €")
        st.markdown(f"- **Total mensualités (nouveau + existants) :** {(mensu_nouveau + assurance_nouveau + total_credits_existants):,.0f} €")
        st.markdown(f"- **Revenu mensuel :** {revenu:,.0f} €")

        # Graphique ratio mensualités / revenu
        fig = go.Figure()

        categories = ["Crédits existants", "Nouveau crédit"]
        valeurs = [total_credits_existants, mensu_nouveau + assurance_nouveau]

        fig.add_trace(go.Bar(x=categories, y=valeurs, marker_color=['#636EFA', '#EF553B']))

        fig.update_layout(
            title="Comparaison mensualités",
            yaxis_title="Montant (€)",
            yaxis=dict(range=[0, max(valeurs + [revenu]) * 1.2]),
            template="plotly_white",
        )

        st.plotly_chart(fig, use_container_width=True)

        # Ratio endettement
        endettement = (mensu_nouveau + assurance_nouveau + total_credits_existants) / revenu if revenu > 0 else 0
        st.markdown(f"### 📉 Ratio d'endettement total : {endettement*100:.1f} %")

    # Bouton retour accueil
    st.markdown("---")
    if st.button("⬅️ Retour à l'accueil", on_click=go_to_start):
        pass
















