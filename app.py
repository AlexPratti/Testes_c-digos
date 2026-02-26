import streamlit as st
import numpy as np

def main():
    st.set_page_config(page_title="Calculadora NBR 17227", layout="wide")
    st.title("⚡ Gestão de Risco de Arco Elétrico - NBR 17227:2025")

    tab1, tab2 = st.tabs(["📏 Dimensões e Invólucros", "🧪 Cálculos Técnicos (Iarc, DLA e Energia)"])

    # --- ABA 1: CONSULTA DE EQUIPAMENTOS (TABELA 1) ---
    with tab1:
        st.header("Classes de Equipamentos e Espaçamentos Típicos")
        dados_inv = {
            "CCM 15 kV": [152, 914.4, 914.4, 914.4, 914.4],
            "Conjunto de manobra 15 kV": [152, 914.4, 1143.0, 762.0, 762.0],
            "CCM 5 kV": [104, 914.4, 660.4, 660.4, 660.4],
            "CCM e painel rasos de BT": [25, 457.2, 355.6, 304.8, 203.2],
            "CCM e painel típico de BT": [25, 457.2, 355.6, 304.8, 203.3],
            "Conjunto de manobra BT": [32, 609.6, 508.0, 508.0, 508.0],
        }
        escolha = st.selectbox("Selecione o Equipamento:", list(dados_inv.keys()))
        info = dados_inv[escolha]
        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("GAP (G)", f"{info[0]} mm")
        c2.metric("Dist. Trabalho (D)", f"{info[1]} mm")
        c3.metric("Altura (A)", f"{info[2]} mm")
        c4.metric("Largura (L)", f"{info[3]} mm")
        c5.metric("Profundidade (P)", f"{info[4]} mm")

    # --- ABA 2: CÁLCULOS (EQUAÇÕES 1-6) ---
    with tab2:
        st.header("Entradas de Dados para Cálculo")
        col1, col2, col3 = st.columns(3)
        with col1:
            v_oc = st.number_input("Tensão Voc (kV)", 0.208, 15.0, 13.8)
            i_bf = st.number_input("Curto-Circuito Ibf (kA)", 0.5, 106.0, 4.852)
        with col2:
            gap = st.number_input("Gap G (mm)", value=float(info[0]))
            d_trab = st.number_input("Distância de Trabalho D (mm)", value=float(info[1]))
        with col3:
            tempo = st.number_input("Duração T (ms)", 10.0, 1000.0, 488.0)
            config = st.selectbox("Configuração:", ["VCB", "VCBB", "HCB", "VOA", "HOA"])

        # --- DICIONÁRIOS DE COEFICIENTES (NBR 17227:2025) ---
        # Tabela 4 - Corrente de Arco (k1 a k10)
        coef_ia = {
            "VCB": {
                600: [-0.04287, 1.035, -0.083, 0, 0, -4.783e-9, 1.962e-6, -0.000229, 0.003141, 1.092],
                2700: [0.0065, 1.001, -0.024, -1.557e-12, 4.556e-10, -4.186e-8, 8.346e-7, 5.482e-5, -0.003191, 0.9729],
                14300: [0.005795, 1.015, -0.011, -1.557e-12, 4.556e-10, -4.186e-8, 8.346e-7, 5.482e-5, -0.003191, 0.9729]
            }
        }
        # Tabela 6 - Energia Incidente (k1 a k13)
        coef_e = {
            "VCB": {
                600: [0.753364, 0.566, 1.752636, 0, 0, -4.783e-9, 1.962e-6, -0.000229, 0.003141, 1.092, 0, -1.598, 0.957],
                2700: [2.40021, 0.165, 0.354202, -1.557e-12, 4.556e-10, -4.186e-8, 8.346e-7, 5.482e-5, -0.003191, 0.9729, 0, -1.569, 0.9778],
                14300: [3.825917, 0.11, -0.999749, -1.557e-12, 4.556e-10, -4.186e-8, 8.346e-7, 5.482e-5, -0.003191, 0.9729, 0, -1.568, 0.99]
            }
        }

        # --- FUNÇÕES DE CÁLCULO (NBR 17227 Eq. 1 e Eq. 3) ---
        def calc_ia_intermediaria(ibf, g, k):
            log_ia = (k[0] + k[1]*np.log10(ibf) + k[2]*np.log10(g)) + (k[3]*ibf**6 + k[4]*ibf**5 + k[5]*ibf**4 + k[6]*ibf**3 + k[7]*ibf**2 + k[8]*ibf + k[9])
            return 10**log_ia

        def calc_e_intermediaria(ia, ibf, g, d, t, k):
            # Equação 3: log10(E) = k1 + k2*log10(G) + (k3*Ia)/(k4*Ibf^6...+k10) + k11*log10(Ibf) + k12*log10(D) + k13*log10(Ia)
            poli_ia = (k[3]*ibf**6 + k[4]*ibf**5 + k[5]*ibf**4 + k[6]*ibf**3 + k[7]*ibf**2 + k[8]*ibf + k[9])
            log_e = k[0] + k[1]*np.log10(g) + (k[2]*ia)/poli_ia + k[10]*np.log10(ibf) + k[11]*np.log10(d) + k[12]*np.log10(ia)
            e_jcm2 = 12.552 * (t/50.0) * 10**log_e
            return e_jcm2 / 4.184 # Retorna cal/cm²

        # Processamento Intermediário
        c = coef_ia["VCB"]; ce = coef_e["VCB"]
        ia600, ia2700, ia14300 = [calc_ia_intermediaria(i_bf, gap, c[v]) for v in [600, 2700, 14300]]
        e600, e2700, e14300 = [calc_e_intermediaria(ia, i_bf, gap, d_trab, tempo, ce[v]) for ia, v in zip([ia600, ia2700, ia14300], [600, 2700, 14300])]

        # Interpolação Final
        if v_oc <= 0.6: i_final, e_final = ia600, e600
        elif v_oc <= 2.7:
            i_final = ia600 + (ia2700 - ia600) * (v_oc - 0.6) / 2.1
            e_final = e600 + (e2700 - e600) * (v_oc - 0.6) / 2.1
        else:
            i_final = ia2700 + (ia14300 - ia2700) * (v_oc - 2.7) / 11.6
            e_final = e2700 + (e14300 - e2700) * (v_oc - 2.7) / 11.6

        # Resultados
        st.divider()
        st.subheader("🏁 RESULTADOS FINAIS")
        res1, res2 = st.columns(2)
        res1.metric("Corrente de Arco (I_arc)", f"{i_final:.5f} kA")
        res2.metric("Energia Incidente (E)", f"{e_final:.5f} cal/cm²")

if __name__ == "__main__":
    main()
