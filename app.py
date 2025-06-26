
import streamlit as st
import plotly.graph_objects as go
import pandas as pd

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
    if "apport" not in st.session_state:
        st.session_state.apport = 20000  # valeur par défaut

def add_credit_immo():
    st.session_state.credits_immo.append({"montant": 0, "taux": 0.03, "duree": 10})

def add_credit_conso():
    st.session_state.credits_conso.append({"montant": 0, "taux": 0.05, "duree": 5})

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

        st.markdown("### 💼 Apport personnel")
        # Boutons pour apport %
        apport_pct_list = [10, 15, 20, 25]
        cols_pct = st.columns(len(apport_pct_list))
        for idx, pct in enumerate(apport_pct_list):
            if cols_pct[idx].button(f"{pct}%"):
                st.session_state.apport = int(prix * pct / 100)
        # Curseur apport
        apport = st.slider("Apport libre (€)", min_value=0, max_value=prix, value=st.session_state.apport, step=500, key="apport_slider")
        st.session_state.apport = apport
        apport_pct = (apport / prix * 100) if prix > 0 else 0
        st.markdown(f"**Apport sélectionné : {apport:,} € ({apport_pct:.1f}%)**")

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

        remove_index_immo = None
        for i, credit in enumerate(st.session_state.credits_immo):
            with st.expander(f"🏦 Crédit immobilier #{i+1}", expanded=True):
                colm1, colm2, colm3, colm4 = st.columns([2,2,2,1])
                with colm1:
                    montant = st.number_input(f"Montant restant dû crédit immo #{i+1} (€)", min_value=0, value=credit["montant"], key=f"immo_montant_{i}")
                with colm2:
                    taux_ = st.slider(f"Taux (%) crédit immo #{i+1}", min_value=0.0, max_value=10.0, value=credit["taux"]*100, step=0.1, key=f"immo_taux_{i}") / 100
                with colm3:
                    duree_ = st.number_input(f"Durée restante (années) crédit immo #{i+1}", min_value=1, max_value=40, value=credit["duree"], key=f"immo_duree_{i}")
                with colm4:
                    if st.button(f"❌ Supprimer", key=f"immo_del_{i}"):
                        remove_index_immo = i

                st.session_state.credits_immo[i]["montant"] = montant
                st.session_state.credits_immo[i]["taux"] = taux_
                st.session_state.credits_immo[i]["duree"] = duree_

        if remove_index_immo is not None:
            st.session_state.credits_immo.pop(remove_index_immo)
            st.experimental_rerun()

    # CONSO
    st.subheader("Crédits à la consommation")
    has_conso = st.checkbox("J’ai un ou plusieurs crédits à la consommation existants", value=len(st.session_state.credits_conso) > 0)
    if has_conso:
        if st.button("➕ Ajouter un crédit conso"):
            add_credit_conso()

        remove_index_conso = None
        for i, credit in enumerate(st.session_state.credits_conso):
            with st.expander(f"🏦 Crédit consommation #{i+1}", expanded=True):
                colc1, colc2, colc3, colc4 = st.columns([2,2,2,1])
                with colc1:
                    montant = st.number_input(f"Montant restant dû crédit conso #{i+1} (€)", min_value=0, value=credit["montant"], key=f"conso_montant_{i}")
                with colc2:
                    taux_ = st.slider(f"Taux (%) crédit conso #{i+1}", min_value=0.0, max_value=15.0, value=credit["taux"]*100, step=0.1, key=f"conso_taux_{i}") / 100
                with colc3:
                    duree_ = st.number_input(f"Durée restante (années) crédit conso #{i+1}", min_value=1, max_value=20, value=credit["duree"], key=f"conso_duree_{i}")
                with colc4:
                    if st.button(f"❌ Supprimer", key=f"conso_del_{i}"):
                        remove_index_conso = i

                st.session_state.credits_conso[i]["montant"] = montant
                st.session_state.credits_conso[i]["taux"] = taux_
                st.session_state.credits_conso[i]["duree"] = duree_

        if remove_index_conso is not None:
            st.session_state.credits_conso.pop(remove_index_conso)
            st.experimental_rerun()

with tabs[2]:
    st.header("📊 Résultats & Visualisations")

    # Calcul mensualités
    mensualites_immo = [mensualite_credit(c["montant"], c["taux"], c["duree"]) + calc_assurance(c["montant"]) for c in st.session_state.credits_immo]
    mensualites_conso = [mensualite_credit(c["montant"], c["taux"], c["duree"]) + calc_assurance(c["montant"]) for c in st.session_state.credits_conso]

    total_immo = sum(mensualites_immo)
    total_conso = sum(mensualites_conso)
    montant_emprunte = max(prix - st.session_state.apport, 0)
    mensu_nouveau = mensualite_credit(montant_emprunte, taux, duree) + calc_assurance(montant_emprunte) if montant_emprunte > 0 else 0

    total_mensualites = total_immo + total_conso + mensu_nouveau
    taux_endettement = (total_mensualites / revenu) * 100 if revenu > 0 else 0

    # Tableau récapitulatif
    df = pd.DataFrame({
        "Type": ["Crédits immobiliers existants", "Crédits conso existants", "Nouveau crédit"],
        "Mensualité (€)": [total_immo, total_conso, mensu_nouveau]
    })
    st.table(df.style.format({"Mensualité (€)": "{:,.2f} €"}))

    st.markdown(f"**Mensualités totales : {total_mensualites:,.2f} €**")
    st.markdown(f"**Taux d'endettement estimé : {taux_endettement:.1f}%**")

    # Graphique à barres
    fig_bar = go.Figure()
    fig_bar.add_trace(go.Bar(
        x=df["Type"],
        y=df["Mensualité (€)"],
        text=[f"{x:,.0f} €" for x in df["Mensualité (€)"]],
        textposition='auto',
        marker_color=['#636EFA', '#EF553B', '#00CC96']
    ))
    fig_bar.update_layout(title="Répartition des mensualités par type de crédit", yaxis_title="Mensualité (€)")
    st.plotly_chart(fig_bar, use_container_width=True)

    # Jauge taux d'endettement
    fig_gauge = go.Figure(go.Indicator(
        mode="gauge+number",
        value=taux_endettement,
        title={'text': "Taux d'endettement (%)"},
        gauge={'axis': {'range': [0, 60]},
               'bar': {'color': "darkblue"},
               'steps': [
                   {'range': [0, 33], 'color': "lightgreen"},
                   {'range': [33, 45], 'color': "yellow"},
                   {'range': [45, 60], 'color': "red"}]}
    ))
    st.plotly_chart(fig_gauge, use_container_width=True)











