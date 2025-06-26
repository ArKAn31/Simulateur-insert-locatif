
import streamlit as st
import plotly.graph_objects as go

# --- Fonctions ---
def mensualite_credit(montant, taux_annuel, duree_annees):
    taux_mensuel = taux_annuel / 12
    n = duree_annees * 12
    if taux_mensuel == 0:
        return montant / n
    return montant * (taux_mensuel * (1 + taux_mensuel)**n) / ((1 + taux_mensuel)**n - 1)

def montant_max_empruntable(revenu_mensuel, taux_annuel, duree_annees, apport, mensualites_existantes, taux_assurance_annuel=0.004):
    mensualite_max = revenu_mensuel * 0.33 - mensualites_existantes
    if mensualite_max <= 0:
        return 0, apport
    low, high = 0, 1_000_000
    while high - low > 1:
        mid = (low + high) / 2
        assurance = (mid * taux_assurance_annuel) / 12
        mensualite = mensualite_credit(mid, taux_annuel, duree_annees) + assurance
        if mensualite > mensualite_max:
            high = mid
        else:
            low = mid
    return round(low), round(low + apport)

# --- Interface ---
st.set_page_config(page_title="Simulateur Immo", page_icon="🏠", layout="wide")
st.title("🏠 Simulateur Achat Locatif + Crédits Existants")

# Inputs achat
col1, col2 = st.columns(2)
with col1:
    prix = st.number_input("Prix logement (€)", 0, 1_000_000, 250_000, step=1000)
    apport = st.slider("Apport personnel (€)", 0, prix, 20_000, step=1000)
with col2:
    revenu = st.number_input("Revenu mensuel net (€)", 0, 20_000, 2000, step=100)
    taux = st.slider("Taux d’intérêt (%)", 1.0, 5.0, 4.0, 0.1) / 100
    duree = st.slider("Durée du prêt (années)", 5, 30, 25)

st.markdown("---")

# Inputs crédits existants (immo + conso)
st.header("📉 Crédits existants")
col3, col4, col5 = st.columns(3)
with col3:
    nb_immo = st.number_input("Nombre crédits immobiliers", 0, 5, 0)
    nb_conso = st.number_input("Nombre crédits conso", 0, 5, 0)
with col4:
    mensualite_immo = st.number_input("Mensualités totales crédits immo (€)", 0, 10_000, 0)
    mensualite_conso = st.number_input("Mensualités totales crédits conso (€)", 0, 10_000, 0)
with col5:
    duree_restante = st.slider("Durée restante crédits (années)", 0, 30, 0)
    taux_credits_existants = st.slider("Taux moyen crédits existants (%)", 0.0, 10.0, 2.0, 0.1) / 100

mensualites_existants = mensualite_immo + mensualite_conso

# Calcul nouveau crédit
montant_emprunte = prix - apport
mensualite_nouveau = mensualite_credit(montant_emprunte, taux, duree)
assurance = (montant_emprunte * 0.004) / 12
mensualite_totale_nouveau = mensualite_nouveau + assurance
mensualites_total = mensualite_totale_nouveau + mensualites_existants

# Endettement
ratio_endettement = mensualites_total / revenu if revenu > 0 else 1

# Résultats
col6, col7 = st.columns(2)
with col6:
    st.subheader("🔍 Analyse du projet")
    st.write(f"Montant emprunté : {montant_emprunte:,.0f} €")
    st.write(f"Mensualité hors assurance : {mensualite_nouveau:.2f} €")
    st.write(f"Assurance (~0.4%/an) : {assurance:.2f} €")
    st.write(f"Mensualité totale nouveau crédit : {mensualite_totale_nouveau:.2f} €")
    st.write(f"Taux d’endettement total : {ratio_endettement * 100:.1f} %")
    if revenu == 0:
        st.warning("⚠️ Entrez un revenu pour calculer l’endettement.")
    elif ratio_endettement > 0.33:
        st.error("❌ Endettement trop élevé.")
    else:
        st.success("✅ Projet finançable (endettement < 33%)")

with col7:
    st.subheader("📈 Capacité d’achat max")
    emprunt_max, prix_max = montant_max_empruntable(revenu, taux, duree, apport, mensualites_existants)
    st.write(f"👉 Avec un apport de **{apport:,.0f} €**, tu peux emprunter jusqu’à **{emprunt_max:,.0f} €**")
    st.write(f"🏡 Soit un bien jusqu’à **{prix_max:,.0f} €**")

st.markdown("---")

# Graphiques côte à côte
col8, col9 = st.columns(2)

with col8:
    st.subheader("📊 Répartition endettement")
    libre = max(revenu - mensualites_total, 0)
    fig1 = go.Figure(data=[go.Pie(
        labels=["Crédits existants", "Nouveau crédit", "Revenu libre"],
        values=[mensualites_existants, mensualite_totale_nouveau, libre],
        marker=dict(colors=["#636EFA", "#EF553B", "#00CC96"]),
        hole=0.4
    )])
    st.plotly_chart(fig1, use_container_width=True)

with col9:
    st.subheader("📊 Comparaison mensualités")
    fig2 = go.Figure()
    fig2.add_trace(go.Bar(name="Crédits existants", x=["Mensualités"], y=[mensualites_existants], text=[f"{mensualites_existants:.0f} €"], textposition="auto", marker_color="#636EFA"))
    fig2.add_trace(go.Bar(name="Nouveau crédit", x=["Mensualités"], y=[mensualite_totale_nouveau], text=[f"{mensualite_totale_nouveau:.0f} €"], textposition="auto", marker_color="#EF553B"))
    fig2.add_trace(go.Bar(name="Total mensualités", x=["Mensualités"], y=[mensualites_total], text=[f"{mensualites_total:.0f} €"], textposition="auto", marker_color="#00CC96"))
    fig2.add_trace(go.Scatter(x=["Mensualités"], y=[revenu], mode="lines+text", name="Revenu", line=dict(color="black", dash="dash"), text=[f"{revenu:.0f} €"], textposition="top center"))
    fig2.update_layout(barmode='group', yaxis_title="€")
    st.plotly_chart(fig2, use_container_width=True)




