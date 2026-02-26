import streamlit as st
import numpy as np

def calcular_ia_intermediaria(ibf, g, k):
    # k = [k1, k2, k3, k4, k5, k6, k7, k8, k9, k10]
    # PARTE A: Logarítmica (Base da equação)
    # log10(Ia) = k1 + k2*log10(Ibf) + k3*log10(G)
    log_base = k[0] + k[1] * np.log10(ibf) + k[2] * np.log10(g)
    
    # PARTE B: Polinomial de correção (Termo aditivo)
    # k4*Ibf^6 + k5*Ibf^5 + k6*Ibf^4 + k7*Ibf^3 + k8*Ibf^2 + k9*Ibf + k10
    poli = (k[3]*ibf**6 + k[4]*ibf**5 + k[5]*ibf**4 + k[6]*ibf**3 + 
            k[7]*ibf**2 + k[8]*ibf + k[9])
    
    # EQUAÇÃO 1: O logaritmo final é a SOMA das duas partes
    log_ia_final = log_base + poli
    
    # Retorna 10 elevado ao logaritmo final
    return 10**log_ia_final

def main():
    st.title("Parte 1: Validação de Correntes Intermediárias (Eq. 1)")

    # Entradas conforme sua imagem
    ibf = st.number_input("Curto-Circuito Ibf (kA)", value=4.85, format="%.2f")
    gap = st.number_input("Gap G (mm)", value=152.0, format="%.2f")

    # Coeficientes Tabela 4 - Configuração VCB (NBR 17227)
    # Cada lista contém k1 a k10 na ordem exata
    k_vcb = {
        600:   [-0.04287, 1.035, -0.083, 0, 0, -4.783e-09, 1.962e-06, -0.000229, 0.003141, 1.092],
        2700:  [0.0065, 1.001, -0.024, -1.557e-12, 4.556e-10, -4.186e-08, 8.346e-07, 5.482e-05, -0.003191, 0.9729],
        14300: [0.005795, 1.015, -0.011, -1.557e-12, 4.556e-10, -4.186e-08, 8.346e-07, 5.482e-05, -0.003191, 0.9729]
    }

    if st.button("Testar Parte 1"):
        ia600 = calcular_ia_intermediaria(ibf, gap, k_vcb[600])
        ia2700 = calcular_ia_intermediaria(ibf, gap, k_vcb[2700])
        ia14300 = calcular_ia_intermediaria(ibf, gap, k_vcb[14300])

        st.success("Resultados da Equação 1 (Corrigidos):")
        st.write(f"**Ia @ 600V:** {ia600:.5f} kA")
        st.write(f"**Ia @ 2700V:** {ia2700:.5f} kA")
        st.write(f"**Ia @ 14300V:** {ia14300:.5f} kA")
        
        # Comparação de validação
        st.info(f"Validação: Ia_600 calculada é {ia600:.5f}. No Excel é 3,37423.")

if __name__ == "__main__":
    main()
