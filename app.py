import streamlit as st
import numpy as np

def calcular_ia_intermediaria(ibf, g, k):
    # Coeficientes k1 a k10 (da Tabela 4)
    k1, k2, k3, k4, k5, k6, k7, k8, k9, k10 = k
    
    # PARTE A: Logarítmica (k1 + k2*log10(Ibf) + k3*log10(G))
    log_base = k1 + k2 * np.log10(ibf) + k3 * np.log10(g)
    
    # PARTE B: Polinomial de correção (k4*Ibf^6 + ... + k10)
    # IMPORTANTE: k10 é o termo constante do polinômio, ele NÃO multiplica o log_base.
    poli = (k4 * ibf**6 + k5 * ibf**5 + k6 * ibf**4 + k7 * ibf**3 + 
            k8 * ibf**2 + k9 * ibf + k10)
    
    # EQUAÇÃO 1: log10(Ia) é a SOMA das duas partes
    # O erro no seu código atual é provavelmente um parêntese que faz poli multiplicar log_base
    log_ia_final = log_base + poli
    
    return 10**log_ia_final

def main():
    st.title("Parte 1: Validação de Correntes Intermediárias (Eq. 1)")

    ibf = st.number_input("Curto-Circuito Ibf (kA)", value=4.85)
    gap = st.number_input("Gap G (mm)", value=152.0)

    # Coeficientes Tabela 4 - Configuração VCB (NBR 17227 / IEEE 1584)
    # Certifique-se de que os valores k4 a k9 estão com os expoentes negativos corretos (e-09, etc)
    coefs = {
        600:   [-0.04287, 1.035, -0.083, 0.0, 0.0, -4.783e-09, 1.962e-06, -0.000229, 0.003141, 1.092],
        2700:  [0.0065, 1.001, -0.024, -1.557e-12, 4.556e-10, -4.186e-08, 8.346e-07, 5.482e-05, -0.003191, 0.9729],
        14300: [0.005795, 1.015, -0.011, -1.557e-12, 4.556e-10, -4.186e-08, 8.346e-07, 5.482e-05, -0.003191, 0.9729]
    }

    if st.button("Testar Parte 1"):
        ia600 = calcular_ia_intermediaria(ibf, gap, coefs[600])
        ia2700 = calcular_ia_intermediaria(ibf, gap, coefs[2700])
        ia14300 = calcular_ia_intermediaria(ibf, gap, coefs[14300])

        st.success("Resultados da Equação 1 (Corrigidos):")
        st.write(f"**Ia @ 600V:** {ia600:.5f} kA")
        st.write(f"**Ia @ 2700V:** {ia2700:.5f} kA")
        st.write(f"**Ia @ 14300V:** {ia14300:.5f} kA")
        
        # Validação cruzada com seu Excel
        st.info(f"Validação: Ia_600 esperado ~3,37423. Calculado: {ia600:.5f}")

if __name__ == "__main__":
    main()
