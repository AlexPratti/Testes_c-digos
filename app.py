import streamlit as st
import numpy as np

# --- FUNÇÕES DE CÁLCULO ---

def calcular_ia_intermediaria(ibf, g, k):
    """Calcula Ia para um patamar de tensão (Eq. 1)"""
    k1, k2, k3, k4, k5, k6, k7, k8, k9, k10 = k
    
    # PARTE A: Logarítmica
    log_base = k1 + k2 * np.log10(ibf) + k3 * np.log10(g)
    
    # PARTE B: Polinomial de correção
    poli = (k4 * ibf**6 + k5 * ibf**5 + k6 * ibf**4 + k7 * ibf**3 + 
            k8 * ibf**2 + k9 * ibf + k10)
    
    # EQUAÇÃO 1: Conforme validado (Multiplicação)
    log_ia_final = log_base * poli
    
    return 10**log_ia_final

def calcular_var_cf(v_oc, k_var):
    """Calcula o Fator de Variação da Corrente (Eq. 2)"""
    k11, k12, k13, k14, k15, k16, k17 = k_var
    
    # Equação 2: Polinômio baseado na Tensão do Sistema (kV)
    var_cf = (k11 * v_oc**6 + k12 * v_oc**5 + k13 * v_oc**4 + 
              k14 * v_oc**3 + k15 * v_oc**2 + k16 * v_oc + k17)
    return var_cf

# --- INTERFACE STREAMLIT ---

def main():
    st.set_page_config(page_title="NBR 17227 - Etapas 1 e 2", layout="wide")
    st.title("⚡ Calculadora NBR 17227:2025 - Partes 1 e 2")
    st.markdown("Validação de Correntes Intermediárias e Fator de Variação.")

    # --- INPUTS ---
    st.sidebar.header("Parâmetros de Entrada")
    ibf = st.sidebar.number_input("Curto-Circuito Ibf (kA)", value=4.85, format="%.2f")
    gap = st.sidebar.number_input("Gap G (mm)", value=152.00, format="%.2f")
    v_sistema = st.sidebar.number_input("Tensão do Sistema Voc (kV)", value=13.80, format="%.2f")

    # --- COEFICIENTES ---
    # Tabela 4 - Coeficientes de Corrente (Configuração VCB)
    coefs_ia = {
        600:   [-0.04287, 1.035, -0.083, 0.0, 0.0, -4.783e-09, 1.962e-06, -0.000229, 0.003141, 1.092],
        2700:  [0.0065, 1.001, -0.024, -1.557e-12, 4.556e-10, -4.186e-08, 8.346e-07, 5.482e-05, 0.003191, 0.9729],
        14300: [0.005795, 1.015, -0.011, -1.557e-12, 4.556e-10, -4.186e-08, 8.346e-07, 5.482e-05, -0.003191, 0.9729]
    }
    
    # Tabela 5 - Coeficientes VarCf (Padrão para todos os eletrodos)
    k_tabela5 = [0, 0, 0, 0, -0.0001, 0.0022, 0.02]

    # --- PROCESSAMENTO ---
    if st.button("Executar Cálculos (Partas 1 e 2)"):
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Parte 1: Correntes Intermediárias")
            ia600 = calcular_ia_intermediaria(ibf, gap, coefs_ia[600])
            ia2700 = calcular_ia_intermediaria(ibf, gap, coefs_ia[2700])
            ia14300 = calcular_ia_intermediaria(ibf, gap, coefs_ia[14300])

            st.write(f"**Ia @ 600V:** {ia600:.5f} kA")
            st.write(f"**Ia @ 2700V:** {ia2700:.5f} kA")
            st.write(f"**Ia @ 14300V:** {ia14300:.5f} kA")
            
            # Validação rápida
            if round(ia600, 2) == 3.37:
                st.success("✅ Ia_600 validado com o Excel!")

        with col2:
            st.subheader("Parte 2: Fator de Variação")
            var_cf = calcular_var_cf(v_sistema, k_tabela5)
            
            st.write(f"**Fator VarCf:** {var_cf:.5f}")
            
            # Cálculo da redução de corrente sugerida pela norma
            ia_reduzida_percent = (1 - 0.5 * var_cf) * 100
            st.info(f"Corrente mínima será {ia_reduzida_percent:.2f}% da corrente de arco calculada.")

if __name__ == "__main__":
    main()
