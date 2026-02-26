import streamlit as st
import numpy as np

def calcular_ia_step(ibf, g, k):
    # Equação 1 validada
    k1, k2, k3, k4, k5, k6, k7, k8, k9, k10 = k
    log_base = k1 + k2 * np.log10(ibf) + k3 * np.log10(g)
    poli = (k4 * ibf**6 + k5 * ibf**5 + k6 * ibf**4 + k7 * ibf**3 + k8 * ibf**2 + k9 * ibf + k10)
    return 10**(log_base * poli)

def calcular_en_step(ia, ibf, g, d, t, k, cf):
    # Coeficientes Tabela 6: k1 a k13
    k1, k2, k3, k4, k5, k6, k7, k8, k9, k10, k11, k12, k13 = k
    
    # Termo polinomial de Ibf da energia (k4 a k10)
    poli_en = (k4 * ibf**6 + k5 * ibf**5 + k6 * ibf**4 + k7 * ibf**3 + k8 * ibf**2 + k9 * ibf + k10)
    
    # EQUAÇÃO 3 CORRETA: O logaritmo é a soma dos termos
    # log10(E) = k1 + k2*log10(G) + (k3*Ia)/poli_en + k11*log10(Ibf) + k12*log10(D) + k13*log10(Ia) + log10(1/CF)
    log_e = (k1 + k2*np.log10(g) + (k3*ia)/poli_en + 
             k11*np.log10(ibf) + k12*np.log10(d) + k13*np.log10(ia) + np.log10(1.0/cf))
    
    # Resultado em J/cm²: 12.552 * (t/50) * 10^log_e
    e_jcm2 = 12.552 * (t / 50.0) * (10**log_e)
    
    # Conversão para cal/cm² (dividir por 4.184)
    return e_jcm2 / 4.184

def main():
    st.title("Parte 4 Corrigida: Energia Intermediária (NBR 17227)")

    # Entradas de teste
    ibf = 4.852
    gap = 152.0
    dist_d = 914.4
    tempo_t = 488.0
    cf = 1.28372 # Validado na Parte 3

    # Coeficientes VCB 600V (Exemplo Tabela 4 e 6)
    k_ia_600 = [-0.04287, 1.035, -0.083, 0, 0, -4.783e-09, 1.962e-06, -0.000229, 0.003141, 1.092]
    k_en_600 = [0.753364, 0.566, 1.752636, 0, 0, -4.783e-09, 1.962e-06, -0.000229, 0.003141, 1.092, 0, -1.598, 0.957]

    if st.button("Calcular Energia Intermediária (600V)"):
        ia600 = calcular_ia_step(ibf, gap, k_ia_600)
        e600 = calcular_en_step(ia600, ibf, gap, dist_d, tempo_t, k_en_600, cf)
        
        st.subheader("Resultados Validação (600V)")
        c1, c2 = st.columns(2)
        c1.metric("Ia @ 600V (kA)", f"{ia600:.5f}")
        c2.metric("Energia @ 600V (cal/cm²)", f"{e600:.5f}")
        
        st.info("O valor agora deve estar na casa de unidades (ex: 2.xx ou 5.xx), não milhares.")

if __name__ == "__main__":
    main()
