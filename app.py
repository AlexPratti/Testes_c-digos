import streamlit as st
import numpy as np

def main():
    st.set_page_config(page_title="Validação NBR 17227", layout="wide")
    st.title("⚡ Validador de Arco Elétrico - NBR 17227 / IEEE 1584")

    # --- Entradas (Inputs) ---
    col1, col2 = st.columns(2)
    with col1:
        v_oc = st.number_input("Tensão Voc (kV)", value=0.48)
        i_bf = st.number_input("Curto-Circuito Ibf (kA)", value=20.0)
        gap  = st.number_input("Gap G (mm)", value=32.0)
    with col2:
        d_trab = st.number_input("Distância de Trabalho D (mm)", value=457.2)
        tempo  = st.number_input("Duração T (ms)", value=100.0)
        eletrodo = st.selectbox("Eletrodos:", ["VCB", "VCBB", "HCB"])

    # --- Coeficientes Tabela 4 e 6 (Simplificados para teste BT) ---
    # k1 a k10 para corrente; k1 a k13 para energia
    k_i = {"VCB": [-0.0428, 1.035, -0.083, 0, 0, 0, 0, 0, 0, 1.092]}
    k_e = {"VCB": [0.7533, 0.566, 1.752, 0, 0, 0, 0, 0, 0, 1.092, 0, -1.598, 0.957]}

    # --- Cálculo da Corrente de Arco (Ia) ---
    k = k_i["VCB"]
    log_ia = k[0] + k[1]*np.log10(i_bf) + k[2]*np.log10(gap) + k[9] # simplificado k4-k8=0
    i_arc = 10**log_ia

    # --- Cálculo da Energia Incidente (E) ---
    ke = k_e["VCB"]
    # CF (Fator de invólucro) - simplificado para 1.0
    cf = 1.0 
    log_e = ke[0] + ke[1]*np.log10(gap) + ke[11]*np.log10(d_trab) + ke[12]*np.log10(i_arc) + np.log10(1.0/cf)
    e_jcm2 = 12.552 * (tempo/50.0) * 10**log_e
    e_cal = e_jcm2 / 4.184 # Conversão para cal/cm²

    # --- Cálculo da Distância Limite (DLA) ---
    # Onde E = 1.2 cal/cm² -> 5.0 J/cm²
    log_dla = (np.log10(5.0 / (12.552 * (tempo/50.0))) - (ke[0] + ke[1]*np.log10(gap) + ke[12]*np.log10(i_arc))) / ke[11]
    dla = 10**log_dla

    # --- Exibição de Resultados ---
    st.divider()
    c1, c2, c3 = st.columns(3)
    c1.metric("Corrente de Arco (I_arc)", f"{i_arc:.3f} kA")
    c2.metric("Energia Incidente (E)", f"{e_cal:.2f} cal/cm²")
    c3.metric("Distância Limite (DLA)", f"{dla:.1f} mm")

if __name__ == "__main__":
    main()
