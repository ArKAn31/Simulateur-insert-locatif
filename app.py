
import streamlit as st
import plotly.graph_objects as go

# --- Fonctions calcul ---
def mensualite_credit(montant, taux_annuel, duree_annees):
    taux_mensuel = taux_annuel / 12
    n = duree_annees * 12
    if taux_mensuel == 0:
        return montant / n
    mensualite = montant * (taux_mensuel * (1 + taux_mensuel)**n) / ((1 + taux_mensuel)**n - 1)
    return mensualite

def calc_assurance(montant, taux_assurance_annuel=0.004):
    return (montant * taux_assurance_annuel) / 12

# --- Callbacks ---
def go_to_app():
    st.session_state.page = "app"
    st.experimental_rerun()

def add_credit_immo():
    st.session_state.credits_immo.append({"montant": 0, "taux": 0.03, "duree": 10})
    st.experimental_rerun()

def add_credit_conso():
    st.session_state.credits_conso.append({"montant": 0, "taux": 0.05, "duree": 5})
    st.experimental_rerun()

def delete_credit_immo(idx):
    if 0 <= idx < len(st.session_state.credits_immo):
        st.session_state.credits_immo.pop(idx)
        st.experimental_rerun()

def delete_credit_conso(idx):
    if 0 <= idx < len(st.session_state.credits_conso):
        st.session_state.credits_conso.pop(idx)
        st.experimental_rerun()

def set_apport_pct(pct):
    st.session_state.apport = int(st.session_state.prix * pct / 100)
    # No rerun needed, slider updates automatically

# --- Initialisation état ---
if "page" not in st.session_state:
    st.session_state.page = "start"
if "credits_immo" not in st.session_state:
    st.session_state.credits_immo = []
if "credits_conso" not in st.session_state:
    st.session_state.credits_conso = []
if "prix" not in st.session_state:
    st.session_state.prix = 250000
if "apport" not in st.session_state:
    st.session_state.apport = 20000

# --- Page démarrage ---
if st.session_state.page == "start":
    st.title("🏠 Simulateur Achat Locatif")
    st.write("Bienvenue dans le simulateur d'achat locatif. Cliquez sur le bouton pour démarrer.")
    st.button("Démarrer la simulation", on_click=go_to_app)

# --- Page principale ---
elif st.session_state.page == "app":

    st.title("🏠 Simulateur Achat Locatif Avancé")

    tabs = st.tabs(["Paramètres généraux", "Crédits existants", "Résultats & Graphiques"])

    with tabs[0]:
        st.header("📥 Paramètres généraux")

        col1, col2 = st.columns(2)
        with col1:
            prix = st.number_input("💰 Prix du logement (€)", min_value=0, value=st.session_state.prix, step=1000, key="prix")
            st.session_state.prix = prix

            st.write("Sélectionnez un apport rapide :")
            c1, c2, c3 = st.columns(3)
            with c1:
                if st.button("10 %"):
                    set_apport_pct(10)
            with c2:
                if st.button("15 %"):
                    set_apport_pct(15)
            with c3:
                if st.button("20 %"):
                    set_apport_pct(20)

            apport = st.slider("💼 Apport personnel (€)", min_value=0, max_value=prix, value=st.session_state.apport, step=1000, key="apport")
            st.session_state.apport = apport
            apport_pct = (apport / prix * 100) if prix > 0 else 0
            st.markdown(f"**Apport représente {apport_pct:.1f}% du prix.**")

        with col2:
            revenu = st.number_input("👤 Revenu mensuel net (€)", min_value=0, value=3000, step=100, key="revenu")
            taux = st.slider("📈 Taux d’intérêt annuel (%)", min_value=0.5, max_value=10.0, value=3.5, step=0.1, key="taux") / 100
            duree = st.slider("⏳ Durée du prêt (années)", min_value=5, max_value=30, value=20, key="duree")

    with tabs[1]:
        st.header("💳 Crédits existants")

        st.subheader("Crédits immobiliers")
        has_immo = st.checkbox("J’ai un ou plusieurs crédits immobiliers existants", value=len(st.session_state.credits_immo) > 0, key="has_immo")
        if has_immo:
            st.button("➕ Ajouter un crédit immobilier", on_click=add_credit_immo)

            for i, credit in enumerate(st.session_state.credits_immo):
                with st.expander(f"Crédit immobilier #{i+1}", expanded=True):
                    colm1, colm2, colm3, colm4 = st.columns([3, 2, 2, 1])
                    with colm1:
                        montant = st.number_input(f"🏦 Capital restant dû sur ce crédit immo #{i+1} (€)",
                                                 min_value=0, value=credit["montant"], key=f"immo_montant_{i}")
                    with colm2:
                        taux_ = st.slider(f"Taux annuel (%) crédit immo #{i+1}",
                                         min_value=0.0, max_value=10.0, value=credit["taux"]*100,
                                         step=0.1, key=f"immo_taux_{i}") / 100
                    with colm3:
                        duree_ = st.number_input(f"Durée restante (années) crédit immo #{i+1}",
                                                min_value=1, max_value=40, value=credit["duree"], key=f"immo_duree_{i}")
                    with colm4:
                        if st.button(f"❌ Supprimer", key=f"immo_del_{i}", on_click=delete_credit_immo, args=(i,)):
                            pass
                    # Update state
                    st.session_state.credits_immo[i]["montant"] = montant
                    st.session_state.credits_immo[i]["taux"] = taux_
                    st.session_state.credits_immo[i]["duree"] = duree_

        st.subheader("Crédits à la consommation")
        has_conso = st.checkbox("J’ai un ou plusieurs crédits à la consommation existants", value=len(st.session_state.credits_conso) > 0, key="has_conso")
        if has_conso:
            st.button("➕ Ajouter un crédit conso", on_click=add_credit_conso)

            for i, credit in enumerate(st.session_state.credits_conso):
                with st.expander(f"Crédit conso #{i+1}", expanded=True):
                    colc1, colc2, colc3, colc4 = st.columns([3, 2, 2, 1])
                    with colc1:
                        montant = st.number_input(f"🏦 Capital restant dû sur ce crédit conso #{i+1} (€)",
                                                 min_value=0, value=credit["montant"], key=f"conso_montant_{i}")
                    with colc2:
                        taux_ = st.slider(f"Taux annuel (%) crédit conso #{i+1}",
                                         min_value=0.0, max_value=15.0, value=credit["taux"]*100,
                                         step=0.1, key=f"conso_taux_{i}") / 100
                    with colc3:
                        duree_ = st.number_input(f"Durée restante (années) crédit conso #{i+1}",
                                                min_value=1, max_value=20, value=credit["duree"], key=f"conso_duree_{i}")
                    with colc4:
                        if st.button(f"❌ Supprimer", key=f"conso_del_{i}", on_click=delete_credit_conso, args=(i,)):
                            pass
                    # Update state
                    st.session_state.credits_conso[i]["montant"] = montant
                    st.session_state.credits_conso[i]["taux"] = taux_
                    st.session_state.credits_conso[i]["duree"] = duree_

    with tabs[2]:
        st.header("📊 Résultats & Graphiques")

        total_mensualites_immo = sum(
            mensualite_credit(c["montant"], c["taux"], c["duree"]) + calc_assurance(c["montant"])
            for c in st.session_state.credits_immo
        )
        total_mensualites_conso = sum(
            mensualite_credit(c["montant"], c["taux"], c["duree"])
            for c in st.session_state.credits_conso
        )

        nouveau_credit_mensualite = mensualite_credit(
            st.session_state.prix - st.session_state.apport, taux, duree
        ) + calc_assurance(st.session_state.prix - st.session_state.apport)

        total_mensualites = total_mensualites_immo + total_mensualites_conso + nouveau_credit_mensualite

        st.metric("Total mensualités crédits immobiliers existants", f"{total_mensualites_immo:,.0f} €")
        st.metric("Total mensualités crédits conso existants", f"{total_mensualites_conso:,.0f} €")
        st.metric("Nouvelle mensualité crédit logement", f"{nouveau_credit_mensualite:,.0f} €")
        st.metric("Total mensualités tous crédits", f"{total_mensualites:,.0f} €")

        # Graphique simple : répartition mensualités
        labels = ["Crédits immobiliers", "Crédits consommation", "Nouveau crédit"]
        values = [total_mensualites_immo, total_mensualites_conso, nouveau_credit_mensualite]

        fig = go.Figure(data=[go.Pie(labels=labels, values=values, hole=0.4)])
        fig.update_layout(title="Répartition des mensualités totales")
        st.plotly_chart(fig, use_container_width=True)

        # Affichage ratio endettement
        revenu = st.session_state.get("revenu", 3000)
        taux_endettement = (total_mensualites / revenu * 100) if revenu > 0 else 0
        st.write(f"**Taux d'endettement total estimé : {taux_endettement:.1f} %**")
        if taux_endettement > 35:
            st.warning("⚠️ Votre taux d'endettement est supérieur à 35%, ce qui peut être un frein pour obtenir un prêt.")














