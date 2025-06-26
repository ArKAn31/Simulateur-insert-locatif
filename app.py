
import streamlit as st
import plotly.graph_objects as go
import pandas as pd

# --- Fonctions financières ---
def mensualite_credit(montant, taux_annuel, duree_annees):
    if montant <= 0 or duree_annees <= 0:
        return 0
    taux_mensuel = taux_annuel / 12
    n = duree_annees * 12
    if taux_mensuel == 0:
        return montant / n
    return montant * (taux_mensuel * (1 + taux_mensuel)**n) / ((1 + taux_mensuel)**n - 1)

def calc_assurance(montant, taux_assurance_annuel=0.004):
    return (montant * taux_assurance_annuel) / 12

# --- Initialisation de l'état ---
def init_state():
    if "started" not in st.session_state:
        st.session_state.started = False
    if "prix" not in st.session_state:
        st.session_state.prix = 250000
    if "apport" not in st.session_state:
        st.session_state.apport = 20000
    if "apport_slider" not in st.session_state:
        st.session_state.apport_slider = st.session_state.apport
    if "revenu" not in st.session_state:
        st.session_state.revenu = 3000
    if "taux" not in st.session_state:
        st.session_state.taux = 0.035
    if "duree" not in st.session_state:
        st.session_state.duree = 20
    if "credits_immo" not in st.session_state:
        st.session_state.credits_immo = []
    if "credits_conso" not in st.session_state:
        st.session_state.credits_conso = []
    if "to_delete_immo" not in st.session_state:
        st.session_state.to_delete_immo = None
    if "to_delete_conso" not in st.session_state:
        st.session_state.to_delete_conso = None

# --- Reset ---
def reset_all():
    st.session_state.started = False
    st.session_state.prix = 250000
    st.session_state.apport = 20000
    st.session_state.apport_slider = 20000
    st.session_state.revenu = 3000
    st.session_state.taux = 0.035
    st.session_state.duree = 20
    st.session_state.credits_immo = []
    st.session_state.credits_conso = []
    st.session_state.to_delete_immo = None
    st.session_state.to_delete_conso = None

# --- Ajout crédits ---
def add_credit_immo():
    st.session_state.credits_immo.append({"montant": 0, "taux": 0.03, "duree": 10})

def add_credit_conso():
    st.session_state.credits_conso.append({"montant": 0, "taux": 0.05, "duree": 5})

# --- Interface ---
st.set_page_config(page_title="Simulateur Achat Locatif", page_icon="🏠", layout="wide")
st.title("🏠 Simulateur Achat Locatif Avancé")

init_state()

if not st.session_state.started:
    st.info("Remplissez les informations principales puis cliquez sur ▶️ Démarrer la simulation")

# -- Paramètres principaux (bloqués si simulation démarrée)
col1, col2 = st.columns(2)

with col1:
    prix = st.number_input("💰 Prix du logement (€)", min_value=0, value=st.session_state.prix, step=1000, disabled=st.session_state.started)
    apport_pct_list = [10, 15, 20, 25]
    st.markdown("### Apport personnel")
    pct_cols = st.columns(len(apport_pct_list))
    for idx, pct in enumerate(apport_pct_list):
        if pct_cols[idx].button(f"{pct}%", disabled=st.session_state.started):
            apport_calc = int(prix * pct / 100)
            st.session_state.apport = apport_calc
            st.session_state.apport_slider = apport_calc
    apport = st.slider("Apport libre (€)", min_value=0, max_value=prix, value=st.session_state.apport_slider, step=500, disabled=st.session_state.started, key="apport_slider")
    st.session_state.apport = apport
    apport_pct = (apport / prix * 100) if prix > 0 else 0
    st.markdown(f"**Apport sélectionné : {apport:,} € ({apport_pct:.1f}%)**")

with col2:
    revenu = st.number_input("👤 Revenu mensuel net (€)", min_value=0, value=st.session_state.revenu, step=100, disabled=st.session_state.started)
    taux = st.slider("📈 Taux d’intérêt annuel (%)", min_value=0.5, max_value=10.0, value=st.session_state.taux * 100, step=0.1, disabled=st.session_state.started) / 100
    duree = st.slider("⏳ Durée du prêt (années)", min_value=5, max_value=30, value=st.session_state.duree, disabled=st.session_state.started)

if not st.session_state.started:
    if st.button("▶️ Démarrer la simulation"):
        # Validation basique
        erreurs = []
        if prix <= 0:
            erreurs.append("Le prix doit être supérieur à 0.")
        if revenu <= 0:
            erreurs.append("Le revenu doit être supérieur à 0.")
        if apport > prix:
            erreurs.append("L'apport ne peut pas être supérieur au prix du bien.")
        if len(erreurs) > 0:
            for e in erreurs:
                st.error(e)
        else:
            st.session_state.prix = prix
            st.session_state.apport = apport
            st.session_state.apport_slider = apport
            st.session_state.revenu = revenu
            st.session_state.taux = taux
            st.session_state.duree = duree
            st.session_state.started = True
            st.experimental_rerun()
else:
    st.success("Simulation en cours...")
    if st.button("🔄 Réinitialiser la simulation"):
        reset_all()
        st.experimental_rerun()

    tabs = st.tabs(["💳 Crédits existants", "📊 Résultats & Graphiques"])

    with tabs[0]:
        st.header("Crédits existants")

        st.subheader("🏠 Crédits immobiliers")
        if st.button("➕ Ajouter un crédit immobilier"):
            add_credit_immo()
            st.experimental_rerun()

        # Suppression gérée hors boucle
        st.session_state.to_delete_immo = None

        for i, credit in enumerate(st.session_state.credits_immo):
            with st.expander(f"Crédit immobilier #{i+1}", expanded=True):
                c1, c2, c3, c4 = st.columns([2, 2, 2, 1])
                with c1:
                    montant = st.number_input(f"Montant restant dû immo #{i+1} (€)", min_value=0, value=credit["montant"], key=f"immo_montant_{i}")
                with c2:
                    taux_ = st.slider(f"Taux (%) immo #{i+1}", min_value=0.0, max_value=10.0, value=credit["taux"] * 100, step=0.1, key=f"immo_taux_{i}") / 100
                with c3:
                    duree_ = st.number_input(f"Durée restante (années) immo #{i+1}", min_value=1, max_value=40, value=credit["duree"], key=f"immo_duree_{i}")
                with c4:
                    if st.button(f"❌", key=f"immo_del_{i}"):
                        st.session_state.to_delete_immo = i
                st.session_state.credits_immo[i]["montant"] = montant
                st.session_state.credits_immo[i]["taux"] = taux_
                st.session_state.credits_immo[i]["duree"] = duree_

        if st.session_state.to_delete_immo is not None:
            st.session_state.credits_immo.pop(st.session_state.to_delete_immo)
            st.session_state.to_delete_immo = None
            st.experimental_rerun()

        st.subheader("🛒 Crédits à la consommation")
        if st.button("➕ Ajouter un crédit conso"):
            add_credit_conso()
            st.experimental_rerun()

        st.session_state.to_delete_conso = None

        for i, credit in enumerate(st.session_state.credits_conso):
            with st.expander(f"Crédit conso #{i+1}", expanded=True):
                c1, c2, c3, c4 = st.columns([2, 2, 2, 1])
                with c1:
                    montant = st.number_input(f"Montant restant dû conso #{i+1} (€)", min_value=0, value=credit["montant"], key=f"conso_montant_{i}")
                with c2:
                    taux_ = st.slider(f"Taux (%) conso #{i+1}", min_value=0.0, max_value=15.0, value=credit["taux"] * 100, step=0.1, key=f"conso_taux_{i}") / 100
                with c3:
                    duree_ = st.number_input(f"Durée restante (années) conso #{i+1}", min_value=1, max_value=20, value=credit["duree"], key=f"conso_duree_{i}")
                with c4:
                    if st.button(f"❌", key=f"conso_del_{i}"):
                        st.session_state.to_delete_conso = i
                st.session_state.credits_conso[i]["montant"] = montant
                st.session_state.credits_conso[i]["taux"] = taux_
                st.session_state.credits_conso[i]["duree"] = duree_

        if st.session_state.to_delete_conso is not None:
            st.session_state.credits_conso.pop(st.session_state.to_delete_conso)
            st.session_state.to_delete_conso = None
            st.experimental_rerun()

    with tabs[1]:
        st.header("Résultats & Visualisations")

        mensualites_immo = [
            mensualite_credit(c["montant"], c["taux"], c["duree"]) + calc_assurance(c["montant"])
            for c in st.session_state.credits_immo
        ]
        mensualites_conso = [
            mensualite_credit(c["montant"], c["taux"], c["duree"]) + calc_assurance(c["montant"])
            for c in st.session_state.credits_conso
        ]

        total_immo = sum(mensualites_immo)
        total_conso = sum(mensualites_conso)
        montant_emprunte = max(st.session_state.prix - st.session_state.apport, 0)
        mensu_nouveau = mensualite_credit(montant_emprunte, st.session_state.taux, st.session_state.duree) + calc_assurance(montant_emprunte) if montant_emprunte > 0 else 0

        total_mensualites = total_immo + total_conso + mensu_nouveau
        taux_endettement = (total_mensualites / st.session_state.revenu) * 100 if st.session_state.revenu > 0 else 0

        df = pd.DataFrame({
            "Type": ["Crédits immobiliers existants", "Crédits consommation existants", "Nouveau crédit"],
            "Mensualité (€)": [total_immo, total_conso, mensu_nouveau]
        })

        st.table(df.style.format({"Mensualité (€)": "{:,.2f} €"}))
        st.markdown(f"**Mensualités totales : {total_mensualites:,.2f} €**")
        st.markdown(f"**Taux d'endettement estimé : {taux_endettement:.1f}%**")

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












