import streamlit as st
import numpy as np

def calcular_en_intermediaria(ia, ibf, g, d, t, k, cf):
    # k = [k1 a k10, k11, k12, k13] da Tabela 6
    k1, k2, k3, k4, k5, k6, k7, k8, k9, k10, k11, k12, k13 = k
    
    # 1. Parte Polinomial de Corrente (Denominador do termo k3)
    # k4*Ibf^7 + k5*Ibf^6 + ... + k10*Ibf (Note que na NBR os expoentes de Ibf mudam na Eq. 3)
    poli_den = (k4*ibf**7 + k5*ibf**6 + k6*ibf**5 + k7*ibf**4 + k8*ibf**3 + k9*ibf**2 + k10*ibf)
    
    # 2. Termo de Corrente de Arco (k3 * Ia / Polinômio)
    termo_corrente = (k3 * ia) / poli_den if poli_den != 0 else 0
    
    # 3. Soma dos Logaritmos (O que vai no expoente de 10)
    # log10(E) = k1 + k2*log10(G) + Termo_Corrente + k11*log10(Ibf) + k12*log10(D) + k13*log10(Ia) + log10(1/CF)
    expoente = (k1 + 
                k2 * np.log10(g) + 
                termo_corrente + 
                k11 * np.log10(ibf) + 
                k12 * np.log10(d) + 
                k13 * np.log10(ia) + 
                np.log10(1.0 / cf))
    
    # 4. Equação 3: E = (12.552/50) * T * 10^Expoente
    e_jcm2 = (12.552 / 50.0) * t * (10**expoente)
    
    return e_jcm2 # Retorna em J/cm² para validação com sua imagem

def main():
    st.title("Parte 4 Corrigida: Energia Intermediária (NBR 17227)")

    # Entradas Fixas para Validação (Conforme sua imagem e conversa)
    ibf = 4.852
    gap = 152.0
    dist_d = 914.4
    tempo_t = 488.0
    ia_600 = 3.37423
    cf = 1.28372 # Fator de invólucro do seu Excel

    # Coeficientes Tabela 6 - VCB 600V (Exatos da NBR 17227)
    k_en_600 = [0.753364, 0.566, 1.752636, 0, 0, -4.783e-09, 1.962e-06, -0.000229, 0.003141, 1.092, 0, -1.598, 0.957]

    if st.button("Calcular Energia Intermediária (600V)"):
        e600_j = calcular_en_intermediaria(ia_600, ibf, gap, dist_d, tempo_t, k_en_600, cf)
        
        st.subheader("Resultados Validação (600V)")
        c1, c2 = st.columns(2)
        c1.metric("Ia @ 600V (kA)", f"{ia_600:.5f}")
        c2.metric("Energia @ 600V (J/cm²)", f"{e600_j:.5f}")
        
        # Conversão para cal/cm² para sua conferência final
        st.write(f"**Energia em cal/cm²:** {e600_j / 4.184:.5f}")

if __name__ == "__main__":
    main()
