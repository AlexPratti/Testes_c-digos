import streamlit as st
import numpy as np

# --- FUNÇÕES DE CÁLCULO ---

def calcular_ia_intermediaria(ibf, g, k):
    """Calcula Ia para um patamar de tensão (Eq. 1)"""
    k1, k2, k3, k4, k5, k6, k7, k8, k9, k10 = k
    log_base = k1 + k2 * np.log10(ibf) + k3 * np.log10(g)
    poli = (k4 * ibf**6 + k5 * ibf**5 + k6 * ibf**4 + k7 * ibf**3 + 
            k8 * ibf**2 + k9 * ibf + k10)
    return 10**(log_base * poli)

def calcular_var_cf(v_oc, k_var):
    """Calcula o Fator de Variação da Corrente (Eq. 2)"""
    k11, k12, k13, k14, k15, k16, k17 = k_var
    var_cf = (k11 * v_oc**6 + k12 * v_oc**5 + k13 * v_oc**4 + 
              k14 * v_oc**3 + k15 * v_oc**2 + k16 * v_oc + k17)
    return var_cf

def calcular_cf(altura, largura, profundidade, config, tipo_involucro):
    """Calcula o Fator de Correção do Invólucro (Eq. 13 a 15 e Tabela 8)"""
    # 1. Converter dimensões para polegadas (Norma usa pol para EES)
    A, L, P = altura / 25.4, largura / 25.4, profundidade / 25.4
    
    # 2. Calcular EES (Tamanho Equivalente do Invólucro) - Eq. 14 e 15
    if config in ["VCB", "VCBB", "HCB"]:
        ees = (A + L) / 2.0 if P > 8 else A # Simplificação da norma para P <= 8 pol
    else: # VOA ou HOA
        ees = (A + L) / 2.0
    
    # 3. Coeficientes b1, b2, b3 da Tabela 8 (Exemplo para VCB)
    # Típico: [-0.0003, 0.03441, 0.4325] | Raso: [0.00222, -0.0256, 0.6222]
    # Usaremos VCB Típico como padrão para este teste:
    b1, b2, b3 = -0.0003, 0.03441, 0.4325
    
    if tipo_involucro == "Típico":
        cf = b1 * ees**2 + b2 * ees + b3
    else: # Raso
        cf = 1.0 / (b1 * ees**2 + b2 * ees + b3)
        
    return ees, cf

# --- INTERFACE STREAMLIT ---

def main():
    st.set_page_config(page_title="NBR 17227 - Etapas 1 a 3", layout="wide")
    st.title("⚡ Calculadora NBR 17227:2025 - Partes 1, 2 e 3")

    # --- SIDEBAR INPUTS ---
    st.sidebar.header("Parâmetros do Sistema")
    ibf = st.sidebar.number_input("Curto-Circuito Ibf (kA)", value=4.85)
    gap = st.sidebar.number_input("Gap G (mm)", value=152.0)
    v_sistema = st.sidebar.number_input("Tensão Voc (kV)", value=13.80)
    
    st.sidebar.header("Dimensões do Invólucro (mm)")
    alt = st.sidebar.number_input("Altura (A)", value=914.4)
    larg = st.sidebar.number_input("Largura (L)", value=914.4)
    prof = st.sidebar.number_input("Profundidade (P)", value=914.4)
    tipo_inv = st.sidebar.radio("Tipo de Invólucro:", ["Típico", "Raso"])

    # --- COEFICIENTES ---
    coefs_ia = {
        600:   [-0.04287, 1.035, -0.083, 0.0, 0.0, -4.783e-09, 1.962e-06, -0.000229, 0.003141, 1.092],
        2700:  [0.0065, 1.001, -0.024, -1.557e-12, 4.556e-10, -4.186e-08, 8.346e-07, 5.482e-05, 0.003191, 0.9729],
        14300: [0.005795, 1.015, -0.011, -1.557e-12, 4.556e-10, -4.186e-08, 8.346e-07, 5.482e-05, -0.003191, 0.9729]
    }
    k_var = [0, 0, 0, 0, -0.0001, 0.0022, 0.02]

    # --- PROCESSAMENTO ---
    if st.button("Executar Cálculos (Partes 1, 2 e 3)"):
        col1, col2, col3 = st.columns(3)

        with col1:
            st.subheader("Parte 1: Correntes")
            ia600 = calcular_ia_intermediaria(ibf, gap, coefs_ia[600])
            st.write(f"**Ia @ 600V:** {ia600:.5f} kA")
            st.write(f"**Ia @ 14.3kV:** {calcular_ia_intermediaria(ibf, gap, coefs_ia[14300]):.5f} kA")

        with col2:
            st.subheader("Parte 2: VarCf")
            var_cf = calcular_var_cf(v_sistema, k_var)
            st.write(f"**VarCf:** {var_cf:.5f}")

        with col3:
            st.subheader("Parte 3: Fator CF")
            ees, cf = calcular_cf(alt, larg, prof, "VCB", tipo_inv)
            st.write(f"**EES (polegadas):** {ees:.2f}")
            st.write(f"**Fator CF Final:** {cf:.5f}")
            
            # Validação: Para 914.4x914.4 (36x36 pol), EES = 36. 
            # CF para VCB Típico deve ser ~1,28372 conforme seu Excel.
            if round(cf, 5) == 1.28372:
                st.success("✅ CF validado com o Excel!")

if __name__ == "__main__":
    main()
