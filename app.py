import streamlit as st
import numpy as np

def calcular_ia_intermediaria(ibf, g, k):
    # Coeficientes k1 a k10 passados como lista
    # PARTE A: Logarítmica (k1 + k2*log10(Ibf) + k3*log10(G))
    log_base = k[0] + k[1] * np.log10(ibf) + k[2] * np.log10(g)
    
    # PARTE B: Polinomial de correção (k4*Ibf^6 + ... + k10)
    # Importante: k10 é o termo constante do polinômio
    poli = (k[3]*ibf**6 + k[4]*ibf**5 + k[5]*ibf**4 + k[6]*ibf**3 + 
            k[7]*ibf**2 + k[8]*ibf + k[9])
    
    # Equação 1: log10(Ia) é a SOMA das duas partes
    log_ia = log_base + poli
    return 10**log_ia

def main():
    st.title("Parte 1: Validação de Correntes Intermediárias (Eq. 1)")

    # Entradas de teste conforme seu Excel
    ibf = st.number_input("Curto-Circuito Ibf (kA)", value=4.852)
    gap = st.number_input("Gap G (mm)", value=152.0)

    # Coeficientes Tabela 4 - Configuração VCB (NBR 17227)
    k_vcb = {
        600:   [-0.04287, 1.035, -0.083, 0, 0, -4.783e-9, 1.962e-6, -0.000229, 0.003141, 1.092],
        2700:  [0.0065, 1.001, -0.024, -1.557e-12, 4.556e-10, -4.186e-8, 8.346e-7, 5.482e-5, -0.003191, 0.9729],
        14300: [0.005795, 1.015, -0.011, -1.557e-12, 4.556e-10, -4.186e-8, 8.346e-7, 5.482e-5, -0.003191, 0.9729]
    }

    if st.button("Testar Parte 1"):
        ia600 = calcular_ia_intermediaria(ibf, gap, k_vcb[600])
        ia2700 = calcular_ia_intermediaria(ibf, gap, k_vcb[2700])
        ia14300 = calcular_ia_intermediaria(ibf, gap, k_vcb[14300])

        st.success("Resultados da Equação 1:")
        st.write(f"**Ia @ 600V:** {ia600:.5f} kA")
        st.write(f"**Ia @ 2700V:** {ia2700:.5f} kA")
        st.write(f"**Ia @ 14300V:** {ia14300:.5f} kA")
        st.info("Compare com seu Excel: Ia_600 deve ser ~3,37423 kA")

if __name__ == "__main__":
    main()
