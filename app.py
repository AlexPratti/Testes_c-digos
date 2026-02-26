import streamlit as st
import numpy as np

# --- FUNÇÕES DE CÁLCULO ---

def calcular_ia_step(ibf, g, k):
    """Calcula Ia intermediária (Eq. 1)"""
    # k = [k1 a k10]
    log_base = k[0] + k[1] * np.log10(ibf) + k[2] * np.log10(g)
    poli = (k[3]*ibf**6 + k[4]*ibf**5 + k[5]*ibf**4 + k[6]*ibf**3 + 
            k[7]*ibf**2 + k[8]*ibf + k[9])
    return 10**(log_base * poli)

def calcular_en_step(ia, ibf, g, d, t, k, cf):
    """Calcula Energia Incidente Intermediária (Eq. 3) em cal/cm²"""
    # k = [k1 a k13 da Tabela 6]
    # Termo polinomial de Ibf para energia
    poli_en = (k[3]*ibf**6 + k[4]*ibf**5 + k[5]*ibf**4 + k[6]*ibf**3 + 
               k[7]*ibf**2 + k[8]*ibf + k[9])
    
    # log10(E) = k1 + k2*log10(G) + (k3*Ia)/poli_en + k11*log10(Ibf) + k12*log10(D) + k13*log10(Ia) + log10(1/CF)
    log_e = (k[0] + k[1]*np.log10(g) + (k[2]*ia)/poli_en + 
             k[10]*np.log10(ibf) + k[11]*np.log10(d) + k[12]*np.log10(ia) + np.log10(1.0/cf))
    
    # Energia em J/cm² (Normalizada p/ 50ms)
    e_jcm2 = 12.552 * (t / 50.0) * 10**log_e
    return e_jcm2 / 4.184 # Retorna cal/cm²

# --- INTERFACE STREAMLIT ---

def main():
    st.set_page_config(page_title="NBR 17227 - Etapa 4", layout="wide")
    st.title("⚡ Calculadora NBR 17227:2025 - Parte 4 (Energia Intermediária)")

    # --- SIDEBAR INPUTS ---
    st.sidebar.header("Parâmetros do Sistema")
    ibf = st.sidebar.number_input("Curto-Circuito Ibf (kA)", value=4.852)
    gap = st.sidebar.number_input("Gap G (mm)", value=152.0)
    dist_d = st.sidebar.number_input("Distância de Trabalho D (mm)", value=914.4)
    tempo_t = st.sidebar.number_input("Duração do Arco T (ms)", value=488.0)
    
    # Coeficientes Tabela 4 (Ia) - VCB 600V (Exemplo)
    k_ia_600 = [-0.04287, 1.035, -0.083, 0.0, 0.0, -4.783e-09, 1.962e-06, -0.000229, 0.003141, 1.092]
    # Coeficientes Tabela 6 (Energia) - VCB 600V (Exemplo)
    k_en_600 = [0.753364, 0.566, 1.752636, 0.0, 0.0, -4.783e-09, 1.962e-06, -0.000229, 0.003141, 1.092, 0, -1.598, 0.957]
    
    # Fator CF (Calculado na Parte 3, fixado aqui para teste conforme seu Excel)
    cf = 1.28372

    if st.button("Calcular Energia Intermediária (600V)"):
        # 1. Primeiro calculamos a Ia para 600V
        ia600 = calcular_ia_step(ibf, gap, k_ia_600)
        
        # 2. Calculamos a Energia para 600V
        e600 = calcular_en_step(ia600, ibf, gap, dist_d, tempo_t, k_en_600, cf)
        
        st.subheader("Resultados Validação (600V)")
        col1, col2 = st.columns(2)
        col1.metric("Ia @ 600V (kA)", f"{ia600:.5f}")
        col2.metric("Energia @ 600V (cal/cm²)", f"{e600:.5f}")
        
        st.info("Nota: Compare o valor de Energia com sua célula correspondente no Excel.")

if __name__ == "__main__":
    main()
