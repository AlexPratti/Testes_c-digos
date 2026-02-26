import streamlit as st
import numpy as np

def calcular_en_intermediaria(ia, ibf, g, d, t, k, cf):
    # Coeficientes k1 a k13 da Tabela 6
    k1, k2, k3, k4, k5, k6, k7, k8, k9, k10, k11, k12, k13 = k
    
    # 1. Termo polinomial de correção da corrente (k4 a k10)
    poli_en = (k4 * ibf**6 + k5 * ibf**5 + k6 * ibf**4 + k7 * ibf**3 + 
               k8 * ibf**2 + k9 * ibf + k10)
    
    # 2. Cálculo do Logaritmo Base 10 (SOMA dos termos conforme NBR 17227)
    # Importante: k12 é negativo, o que faz a energia cair com a distância
    log_e = (k1 + 
             k2 * np.log10(g) + 
             (k3 * ia) / poli_en + 
             k11 * np.log10(ibf) + 
             k12 * np.log10(d) + 
             k13 * np.log10(ia) + 
             np.log10(1.0 / cf))
    
    # 3. Conversão final: 12.552 * (tempo/50ms) * 10^log_e
    e_jcm2 = 12.552 * (t / 50.0) * (10**log_e)
    
    # 4. Retorno em cal/cm2 (dividir Joules por 4.184)
    return e_jcm2 / 4.184

def main():
    st.title("Parte 4 Corrigida: Energia Intermediária (NBR 17227)")

    # Entradas de teste (Conforme seu Excel)
    ibf = 4.852
    gap = 152.0
    dist_d = 914.4
    tempo_t = 488.0
    cf = 1.28372 # Fator de invólucro validado na Parte 3
    ia_600 = 3.37423 # Corrente validada na Parte 1

    # Coeficientes Tabela 6 - VCB 600V (Exatos da Norma)
    k_en_600 = [0.753364, 0.566, 1.752636, 0, 0, -4.783e-09, 1.962e-06, -0.000229, 0.003141, 1.092, 0, -1.598, 0.957]

    if st.button("Calcular Energia Intermediária (600V)"):
        e600 = calcular_en_intermediaria(ia_600, ibf, gap, dist_d, tempo_t, k_en_600, cf)
        
        st.subheader("Resultados Validação (600V)")
        col1, col2 = st.columns(2)
        col1.metric("Ia @ 600V (kA)", f"{ia_600:.5f}")
        col2.metric("Energia @ 600V (cal/cm²)", f"{e600:.5f}")
        
        st.info("O valor esperado deve estar entre 2.0 e 8.0 cal/cm². Verifique se coincide com seu Excel.")

if __name__ == "__main__":
    main()
