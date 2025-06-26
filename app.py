
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

            mensu = mensualite_credit(montant, taux_, duree_)
            st.markdown(f"**Mensualité estimée (hors assurance) :** {mensu:,.0f} €")

            credits_immo.append({"montant": montant, "taux": taux_, "duree": duree_})

    # Crédits conso
    st.subheader("💸 Crédits à la consommation")
    credits_conso = []
    for i in range(nb_conso):
        with st.expander(f"Crédit conso #{i+1}", expanded=True):
            montant = st.number_input(f"Montant restant dû crédit conso #{i+1} (€)", 0, 500_000, 10_000, key=f"conso_montant_{i}")
            taux_ = st.slider(f"Taux crédit conso #{i+1} (%)", 0.0, 15.0, 5.0, 0.1, key=f"conso_taux_{i}") / 100
            duree_ = st.number_input(f"Durée restante (années) crédit conso #{i+1}", 1, 30, 5, key=f"conso_duree_{i}")

            mensu = mensualite_credit(montant, taux_, duree_)
            st.markdown(f"**Mensualité estimée (hors assurance) :** {mensu:,.0f} €")

            credits_conso.append({"montant": montant, "taux": taux_, "duree": duree_})

# --- Résultats ---
with tabs[2]:
    st.header("📊 Résultats & Synthèse")

    # --- Calculs ---
    total_mensualites_immo = sum(
        mensualite_credit(c["montant"], c["taux"], c["duree"]) + calc_assurance(c["montant"])
        for c in credits_immo
    )
    total_mensualites_conso = sum(
        mensualite_credit(c["montant"], c["taux"], c["duree"]) + calc_assurance(c["montant"])
        for c in credits_conso
    )
    total_credits_existants = total_mensualites_immo + total_mensualites_conso

    montant_emprunte = max(prix - apport, 0)
    mensu_nouveau = mensualite_credit(montant_emprunte, taux, duree) if montant_emprunte > 0 else 0
    assurance_nouveau = calc_assurance(montant_emprunte) if montant_emprunte > 0 else 0
    total_nouveau_credit = mensu_nouveau + assurance_nouveau

    total_mensualites = total_credits_existants + total_nouveau_credit
    endettement = total_mensualites / revenu if revenu > 0 else 0

    # --- Affichage simplifié ---
    st.subheader("🧾 Résumé financier mensuel")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"- **💳 Crédits existants :** {total_credits_existants:,.0f} €")
        st.markdown(f"- **🏠 Nouveau crédit :** {total_nouveau_credit:,.0f} €")
        st.markdown(f"- **🧮 Total mensualités :** {total_mensualites:,.0f} €")
    with col2:
        st.markdown(f"- **💰 Revenu mensuel :** {revenu:,.0f} €")
        st.markdown(f"- **📉 Taux d’endettement :** {endettement*100:.1f} %")

        if endettement < 0.35:
            st.success("🟢 Endettement maîtrisé")
        elif endettement < 0.45:
            st.warning("🟠 Attention à l’endettement")
        else:
            st.error("🔴 Endettement élevé — risque de refus bancaire")

    # --- Camembert : répartition des revenus ---
    st.subheader("📈 Répartition de votre revenu mensuel")

    labels = ["Crédits existants", "Nouveau crédit", "Revenu restant"]
    values = [total_credits_existants, total_nouveau_credit, max(revenu - total_mensualites, 0)]

    fig = go.Figure(go.Pie(
        labels=labels,
        values=values,
        hole=0.4,
        marker_colors=["#636EFA", "#EF553B", "#00CC96"]
    ))
    fig.update_layout(
        title="Répartition de votre revenu mensuel",
        showlegend=True
    )
    st.plotly_chart(fig, use_container_width=True)

    # ... (après affichage du graphique)

    # --- Conclusion crédit max possible ---
    st.subheader("🔎 Conclusion")
    # Calcul du crédit max possible en fonction d’un endettement max de 35%
    endettement_max = 0.35
    capacité_mensuelle = revenu * endettement_max - total_credits_existants
    if capacité_mensuelle <= 0:
        st.error("❌ Votre capacité d'emprunt est déjà dépassée avec vos crédits existants.")
    else:
        # Calcul montant max empruntable avec mensualité capacité_mensuelle
        # On cherche montant_emprunte_max tel que mensualite_credit = capacité_mensuelle - assurance
        # Ici on fait une estimation simple en inversant la formule (approximation)
        # On peut faire une recherche binaire pour être plus précis

        def montant_max_emprunte(mensualite_cible, taux_annuel, duree_annees):
            taux_mensuel = taux_annuel / 12
            n = duree_annees * 12
            if taux_mensuel == 0:
                return mensualite_cible * n
            montant = mensualite_cible * ((1 + taux_mensuel)**n - 1) / (taux_mensuel * (1 + taux_mensuel)**n)
            return montant

        # On enlève l'assurance (qui dépend du montant), donc on ajuste la mensualité cible
        # On va faire une boucle pour affiner car assurance dépend du montant

        mensualite_dispo = capacité_mensuelle
        montant_estime = 0
        for _ in range(10):
            montant_estime = montant_max_emprunte(mensualite_dispo, taux, duree)
            assurance = calc_assurance(montant_estime)
            mensualite_dispo = capacité_mensuelle + assurance  # on ajoute assurance à la mensualité dispo

        st.info(f"💡 Montant maximal empruntable estimé : {montant_estime:,.0f} €")
        st.info(f"💡 Mensualité correspondante (hors assurance) : {mensualite_credit(montant_estime, taux, duree):,.0f} €")
        st.info(f"💡 Assurance mensuelle estimée : {calc_assurance(montant_estime):,.0f} €")
        st.info(f"💡 Endettement total estimé : {(total_credits_existants + mensualite_credit(montant_estime, taux, duree) + calc_assurance(montant_estime)) / revenu * 100:.1f} %")


















