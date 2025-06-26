
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

def add_credit_immo():
    st.session_state.credits_immo.append({"montant": 0, "taux": 0.03, "duree": 10})

def add_credit_conso():
    st.session_state.credits_conso.append({"montant": 0, "taux": 0.05, "duree": 5})

def remove_credit_immo(idx):
    st.session_state.credits_immo.pop(idx)

def remove_credit_conso(idx):
    st.session_state.credits_conso.pop(idx)

# --- Setup page ---
st.set_page_config(page_title="Simulateur Achat Locatif", page_icon="🏠", layout="wide")
st.title("🏠 Simulateur Achat Locatif Avancé")

init_session_state()

# Onglets
tabs = st.tabs(["Paramètres généraux", "Crédits existants", "Résultats & Graphiques"])

with tabs[0]:
    st.header("📥 Paramètres généraux")

    col1, col2 = st.columns(2)
    with col1:
        prix = st.number_input("💰 Prix du logement (€)", min_value=0, value=250000, step=1000)

        st.subheader("💼 Apport personnel")

        # Options rapides pour l'apport en %
        apport_options = [0, 0.1, 0.15, 0.2, 0.25, 0.3]
        apport_pct_selected_idx = st.radio(
            "Sélectionnez un pourcentage d'apport",
            options=[f"{int(p*100)}%" for p in apport_options],
            index=3,  # par défaut 20%
            horizontal=True,
            key="apport_radio"
        )

        # Valeur d'apport initiale calculée depuis le radio
        apport_init = int(prix * apport_options[[f"{int(p*100)}%" for p in apport_options].index(apport_pct_selected_idx)])

        # Slider manuel pour affiner l'apport
        apport = st.slider(
            "Ajustez l'apport personnel (€)",
            min_value=0,
            max_value=prix,
            value=apport_init,
            step=1000,
            key="apport_slider"
        )

        # Affichage % réel apport
        apport_pct_effectif = (apport / prix * 100) if prix > 0 else 0
        st.markdown(f"**Apport représente {apport_pct_effectif:.1f}% du prix.**")

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

        for i, credit in enumerate(st.session_state.credits_immo):
            with st.expander(f"Crédit immobilier #{i+1}", expanded=True):
                colm1, colm2, colm3, colm4 = st.columns([2,2,2,1])
                with colm1:
                    montant = st.number_input(f"🏦 Capital restant dû sur ce crédit immobilier #{i+1} (€)", min_value=0, value=credit["montant"], key=f"immo_montant_{i}")
                with colm2:
                    taux_ = st.slider(f"Taux (%) crédit immo #{i+1}", min_value=0.0, max_value=10.0, value=credit["taux"]*100, step=0.1, key=f"immo_taux_{i}") / 100
                with colm3:
                    duree_ = st.number_input(f"Durée restante (années) crédit immo #{i+1}", min_value=1, max_value=40, value=credit["duree"], key=f"immo_duree_{i}")
                with colm4:
                    if st.button(f"❌ Supprimer", key=f"immo_del_{i}"):
                        remove_credit_immo(i)
                        st.experimental_rerun()
                # Update state
                st.session_state.credits_immo[i]["montant"] = montant
                st.session_state.credits_immo[i]["taux"] = taux_
                st.session_state.credits_immo[i]["duree"] = duree_

    # CONSO
    st.subheader("Crédits à la consommation")
    has_conso = st.checkbox("J’ai un ou plusieurs crédits à la consommation existants", value=len(st.session_state.credits_conso) > 0)
    if has_conso:
        if st.button("➕ Ajouter un crédit conso"):
            add_credit_conso()

        for i, credit in enumerate(st.session_state.credits_conso):
            with st.expander(f"Crédit conso #{i+1}", expanded=True):
                colc1, colc2, colc3, colc4 = st.columns([2,2,2,1])
                with colc1:
                    montant = st.number_input(f"🏦 Capital restant dû sur ce crédit conso #{i+1} (€)", min_value=0, value=credit["montant"], key=f"conso_montant_{i}")
                with colc2:
                    taux_ = st.slider(f"Taux (%) crédit conso #{i+1}", min_value=0.0, max_value=15.0, value=credit["taux"]*100, step=0.1, key=f"conso_taux_{i}") / 100
                with colc3:
                    duree_ = st.number_input(f"Durée restante (années) crédit conso #{i+1}", min_value=1, max_value=20, value=credit["duree"], key=f"conso_duree_{i}")
                with colc4:
                    if st.button(f"❌ Supprimer", key=f"conso_del_{i}"):
                        remove_credit_conso(i)
                        st.experimental_rerun()
                # Update state
                st.session_state.credits_conso[i]["montant"] = montant
                st.session_state.credits_conso[i]["taux"] = taux_
                st.session_state.credits_conso[i]["duree"] = duree_

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
    mensu_tot_nouveau = mensu_nouveau + assurance_nouveau

    mensu_totale = total_credits_existants + mensu_tot_nouveau

    # Affichage résultats
    st.subheader("💳 Crédits existants")
    st.write(f"Mensualités totales crédits immobiliers existants : {total_mensualites_immo:.2f} €")
    st.write(f"Mensualités totales crédits consommation existants : {total_mensualites_conso:.2f} €")
    st.write(f"Mensualités totales crédits existants : {total_credits_existants:.2f} €")

    st.subheader("🏠 Nouveau prêt immobilier")
    st.write(f"Montant emprunté (prix - apport) : {montant_emprunte:.2f} €")
    st.write(f"Mensualité du nouveau crédit : {mensu_nouveau:.2f} €")
    st.write(f"Assurance mensuelle : {assurance_nouveau:.2f} €")
    st.write(f"Mensualité totale nouveau crédit : {mensu_tot_nouveau:.2f} €")

    st.subheader("📅 Total mensualités tous crédits")
    st.write(f"Mensualité totale (existants + nouveau) : {mensu_totale:.2f} €")

    # Graphique répartition mensualités
    labels = ["Crédits immobiliers existants", "Crédits consommation existants", "Nouveau crédit immobilier"]
    values = [total_mensualites_immo, total_mensualites_conso, mensu_tot_nouveau]

    fig = go.Figure(data=[go.Pie(labels=labels, values=values, hole=0.4)])
    fig.update_traces(textinfo='label+percent', hoverinfo='label+value')
    st.plotly_chart(fig, use_container_width=True)










