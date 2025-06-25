import streamlit as st
import math

# --- Funzioni Erlang C ---
def erlang_c_probability(traffic_intensity, agents):
    if agents <= traffic_intensity:
        return 1.0
    numeratore = (traffic_intensity ** agents) / math.factorial(agents)
    somma = sum((traffic_intensity ** k) / math.factorial(k) for k in range(agents))
    return numeratore / (numeratore + (1 - (traffic_intensity / agents)) * somma)

def service_level(traffic_intensity, agents, aht_sec, target_sec):
    ec = erlang_c_probability(traffic_intensity, agents)
    wait_prob = ec * math.exp(-(agents - traffic_intensity) * (target_sec / aht_sec))
    return 1 - wait_prob

def required_agents(calls_per_hour, aht_sec, target_sla, target_sec, shrinkage):
    traffic_intensity = (calls_per_hour * aht_sec) / 3600
    agents = max(1, math.ceil(traffic_intensity))

    while service_level(traffic_intensity, agents, aht_sec, target_sec) < target_sla:
        agents += 1

    adjusted_agents = math.ceil(agents / (1 - shrinkage))
    return adjusted_agents, agents, traffic_intensity

# --- Streamlit UI ---
st.set_page_config(page_title="Erlang C Staffing Tool")
st.title("📞 Erlang C Contact Center Staffing Calculator")

with st.form("input_form"):
    calls_per_hour = st.number_input("📈 Chiamate previste all'ora", value=100)
    aht_sec = st.number_input("⏱️ Average Handling Time (in secondi)", value=300)
    target_sla = st.slider("🎯 Target SLA (es. 0.80 = 80% delle chiamate risposte in tempo)", 0.5, 0.95, 0.8)
    target_sec = st.number_input("⏲️ Tempo massimo per rispettare SLA (secondi)", value=20)
    shrinkage = st.slider("📉 Shrinkage (percentuale tempo non produttivo)", 0.0, 0.5, 0.3)
    submitted = st.form_submit_button("Calcola")

if submitted:
    adj_agents, base_agents, erlang = required_agents(
        calls_per_hour, aht_sec, target_sla, target_sec, shrinkage
    )

    st.success("Calcolo completato ✅")
    st.metric("🚦 Agenti richiesti (post-shrinkage)", adj_agents)
    st.metric("👥 Agenti richiesti (netti)", base_agents)
    st.metric("📶 Traffic Intensity (Erlang)", round(erlang, 2))

    st.caption("Basato sul modello Erlang C semplificato.")
