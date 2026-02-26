import streamlit as st
import numpy as np

def calcular_en_step(ia, ibf, g, d, t, k, cf):
    """Implementação exata da Equação 3 da NBR 17227"""
    k1, k2, k3, k4, k5, k6, k7, k8, k9, k10, k11, k12, k13 = k
    
    # 1. Denominador Polinomial (k4*Ibf^7 + k5*Ibf^6 + ... + k10*Ibf)
    poli_den = (k4*ibf**7 + k5*ibf**6 + k6*ibf**5 + k7*ibf**4 + 
                k8*ibf**3 + k9*ibf**2 + k10*ibf)
    
    # 2. Termo de Corrente de Arco
    termo_ia = (k3 * ia) / poli_den if poli_den != 0 else 0
    
    # 3. Soma Logarítmica no Expoente (conforme imagem da NBR)
    expoente = (k1 + k2*np.log10(g) + termo_ia + 
                k11*np.log10(ibf) + k12*np.log10(d) + 
                k13*np.log10(ia) + np.log10(1.0/cf))
    
    # 4. Cálculo em J/cm²
    e_jcm2 = (12.552 / 50.0) * t * (10**expoente)
    return e_jcm2

def main():
    st.title("Parte 4: Energias Intermediárias (NBR 17227)")

    # Parâmetros validados anteriormente
    ibf = 4.852; gap = 152.0; dist_d = 914.4; tempo_t = 488.0; cf = 1.28372
    # Correntes Ia validadas na Parte 1
    ia600 = 3.37423; ia2700 = 4.19239; ia14300 = 4.56798

    # Coeficientes Tabela 6 - Configuração VCB (NBR 17227)
    # [k1, k2, k3, k4, k5, k6, k7, k8, k9, k10, k11, k12, k13]
    k_en = {
        600:   [0.753364, 0.566, 1.752636, 0, 0, -4.783e-9, 1.962e-6, -0.000229, 0.003141, 1.092, 0, -1.598, 0.957],
        2700:  [2.40021, 0.165, 0.354202, -1.557e-12, 4.556e-10, -4.186e-8, 8.346e-7, 5.482e-5, -0.003191, 0.9729, 0, -1.569, 0.9778],
        14300: [3.825917, 0.11, -0.999749, -1.557e-12, 4.556e-10, -4.186e-8, 8.346e-7, 5.482e-5, -0.003191, 0.9729, 0, -1.568, 0.99]
    }

    if st.button("Calcular Energias Intermediárias"):
        e600_j = calcular_en_step(ia600, ibf, gap, dist_d, tempo_t, k_en[600], cf)
        e2700_j = calcular_en_step(ia2700, ibf, gap, dist_d, tempo_t, k_en[2700], cf)
        e14300_j = calcular_en_step(ia14300, ibf, gap, dist_d, tempo_t, k_en[14300], cf)

        st.subheader("Resultados em J/cm² (Validação NBR)")
        c1, c2, c3 = st.columns(3)
        c1.metric("E_600", f"{e600_j:.5f}")
        c2.metric("E_2700", f"{e2700_j:.5f}")
        c3.metric("E_14300", f"{e14300_j:.5f}")

        st.subheader("Resultados em cal/cm² (Para Vestimenta)")
        r1, r2, r3 = st.columns(3)
        r1.metric("E_600 (cal)", f"{e600_j/4.184:.5f}")
        r2.metric("E_2700 (cal)", f"{e2700_j/4.184:.5f}")
        r3.metric("E_14300 (cal)", f"{e14300_j/4.184:.5f}")

if __name__ == "__main__":
    main()
