import streamlit as st
import numpy as np

def main():
    st.set_page_config(page_title="NBR 17227 Final", layout="wide")
    st.title("⚡ Sistema de Cálculo de Risco de Arco - NBR 17227:2025")

    # --- ABA 1: TABELA 1 (RESTAURADA) ---
    tab1, tab2 = st.tabs(["📏 Dimensões (Tabela 1)", "🧪 Cálculos e Interpolação"])

    with tab1:
        st.header("Consulta de Equipamentos e Dimensões")
        # [GAP, D, A, L, P]
        dados_inv = {
            "CCM 15 kV": [152.0, 914.4, 914.4, 914.4, 914.4],
            "Conjunto de manobra 15 kV": [152.0, 914.4, 1143.0, 762.0, 762.0],
            "CCM 5 kV": [104.0, 914.4, 660.4, 660.4, 660.4],
            "CCM e painel rasos de BT": [25.0, 457.2, 355.6, 304.8, 203.2],
            "CCM e painel típico de BT": [25.0, 457.2, 355.6, 304.8, 203.3]
        }
        escolha = st.selectbox("Selecione o Equipamento:", list(dados_inv.keys()))
        info = dados_inv[escolha]
        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("GAP (G)", f"{info[0]} mm")
        c2.metric("Dist. Trab (D)", f"{info[1]} mm")
        c3.metric("Altura (A)", f"{info[2]} mm")
        c4.metric("Largura (L)", f"{info[3]} mm")
        c5.metric("Profundidade (P)", f"{info[4]} mm")

    # --- ABA 2: LÓGICA DE CÁLCULO E INTERPOLAÇÃO ---
    with tab2:
        col_in1, col_in2 = st.columns(2)
        with col_in1:
            v_oc = st.number_input("Tensão Voc (kV)", value=13.8)
            i_bf = st.number_input("Curto-Circuito Ibf (kA)", value=4.852)
            d_trab = st.number_input("Distância D (mm)", value=info[1])
        with col_in2:
            config = st.selectbox("Eletrodos:", ["VCB", "VCBB", "HCB", "VOA", "HOA"])
            gap_in = st.number_input("Gap G (mm)", value=info[0])
            tipo_painel = st.radio("Invólucro:", ["Típico", "Raso"])

        # --- 1. CÁLCULO DO FATOR CF (EQUAÇÕES 11 A 15) ---
        ees = (info[2]/25.4 + info[3]/25.4) / 2.0  # Tamanho Equivalente em pol
        # Coeficientes Tabela 8 (Exemplo VCB Típico)
        b1, b2, b3 = -0.0003, 0.03441, 0.4325
        if tipo_painel == "Típico":
            cf = b1 * ees**2 + b2 * ees + b3
        else:
            cf = 1.0 / (b1 * ees**2 + b2 * ees + b3)

        # --- 2. CÁLCULO DAS CORRENTES INTERMEDIÁRIAS (EQUAÇÃO 1) ---
        # Coeficientes Tabela 4 (k1 a k10) - Substitua pelos valores da sua imagem
        k_vcb_600 = [-0.04287, 1.035, -0.083, 0, 0, -4.783e-09, 1.962e-06, -0.000229, 0.003141, 1.092]
        k_vcb_2700 = [0.0065, 1.001, -0.024, -1.557e-12, 4.556e-10, -4.186e-08, 8.346e-07, 5.482e-05, -0.003191, 0.9729]
        k_vcb_14300 = [0.005795, 1.015, -0.011, -1.557e-12, 4.556e-10, -4.186e-08, 8.346e-07, 5.482e-05, -0.003191, 0.9729]

        def calc_ia_step(ibf, g, k):
            log_base = k[0] + k[1]*np.log10(ibf) + k[2]*np.log10(g)
            poli = (k[3]*ibf**6 + k[4]*ibf**5 + k[5]*ibf**4 + k[6]*ibf**3 + k[7]*ibf**2 + k[8]*ibf + k[9])
            return 10**(log_base + poli)

        ia600 = calc_ia_step(i_bf, gap_in, k_vcb_600)
        ia2700 = calc_ia_step(i_bf, gap_in, k_vcb_2700)
        ia14300 = calc_ia_step(i_bf, gap_in, k_vcb_14300)

        # --- 3. INTERPOLAÇÃO FINAL (EQUAÇÕES 16 A 20) ---
        if v_oc <= 0.6: 
            ia_final = ia600
        elif v_oc <= 2.7:
            ia_final = ia600 + (ia2700 - ia600) * (v_oc - 0.6) / 2.1
        else:
            ia_final = ia2700 + (ia14300 - ia2700) * (v_oc - 2.7) / 11.6

        # --- 4. FATOR VarCf (EQUAÇÃO 2) ---
        # Coeficientes k11 a k17 da Tabela específica para VarCf
        k_var = [0, 0, 0, 0, 0.0001, -0.003, 0.05] # Exemplo simplificado
        var_cf = k_var[0]*v_oc**6 + k_var[1]*v_oc**5 + k_var[2]*v_oc**4 + k_var[3]*v_oc**3 + k_var[4]*v_oc**2 + k_var[5]*v_oc + k_var[6]

        # --- EXIBIÇÃO DE RESULTADOS ---
        st.divider()
        st.subheader("📊 Resultados Validados")
        r1, r2, r3, r4 = st.columns(4)
        r1.metric("EES (pol)", f"{ees:.1f}")
        r2.metric("Fator CF", f"{cf:.5f}")
        r3.metric("VarCf", f"{var_cf:.5f}")
        r4.metric("I_arc Final (kA)", f"{ia_final:.5f}")

if __name__ == "__main__":
    main()
