import streamlit as st
import numpy as np

def main():
    st.set_page_config(page_title="Calculadora NBR 17227", layout="wide")
    st.title("⚡ Gestão de Risco de Arco Elétrico - NBR 17227:2025")

    # --- ABA 1: TABELA DE EQUIPAMENTOS ---
    tab1, tab2 = st.tabs(["📏 Dimensões e Invólucros", "🧪 Cálculos de Arco"])

    with tab1:
        st.header("Consulta de Equipamentos (Tabela 1)")
        # GAP, Dist. Trabalho, Altura, Largura, Profundidade
        dados_inv = {
            "CCM 15 kV": [152.0, 914.4, 914.4, 914.4, 914.4],
            "Conjunto de manobra 15 kV": [152.0, 914.4, 1143.0, 762.0, 762.0],
            "CCM 5 kV": [104.0, 914.4, 660.4, 660.4, 660.4],
            "Conjunto de manobra 5 kV (Opção 1)": [104.0, 914.4, 914.4, 914.4, 914.4],
            "Conjunto de manobra 5 kV (Opção 2)": [104.0, 914.4, 1143.0, 762.0, 762.0],
            "CCM e painel rasos de BT": [25.0, 457.2, 355.6, 304.8, 203.2],
            "CCM e painel típico de BT": [25.0, 457.2, 355.6, 304.8, 203.3],
            "Conjunto de manobra BT": [32.0, 609.6, 508.0, 508.0, 508.0],
            "Caixa de junção de cabos": [13.0, 457.2, 355.6, 304.8, 203.2]
        }
        
        escolha = st.selectbox("Selecione o Equipamento:", list(dados_inv.keys()), key="sel_equip")
        info = dados_inv[escolha]
        
        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("GAP (G)", f"{info[0]} mm")
        c2.metric("Dist. Trabalho (D)", f"{info[1]} mm")
        c3.metric("Altura (A)", f"{info[2]} mm")
        c4.metric("Largura (L)", f"{info[3]} mm")
        c5.metric("Profundidade (P)", f"{info[4]} mm")

    # --- ABA 2: CÁLCULOS TÉCNICOS ---
    with tab2:
        st.header("Parâmetros de Entrada e Resultados")
        
        col_in1, col_in2 = st.columns(2)
        with col_in1:
            # Inputs com chaves únicas para garantir a reatividade
            v_oc = st.number_input("Tensão Voc (kV)", 0.208, 15.0, 0.38, step=0.01, key="v_oc")
            i_bf = st.number_input("Curto-Circuito Ibf (kA)", 0.5, 106.0, 20.0, key="i_bf")
            d_trab = st.number_input("Distância de Trabalho D (mm)", value=float(info[1]), key="d_trab")
        
        with col_in2:
            config = st.selectbox("Configuração dos Eletrodos:", ["VCB", "VCBB", "HCB", "VOA", "HOA"], key="config")
            gap_input = st.number_input("Gap G (mm)", value=float(info[0]), key="gap")
            tempo = st.number_input("Duração do Arco T (ms)", 10.0, 1000.0, 100.0, key="tempo")

        # --- Lógica de Cálculo (Equação 1 NBR 17227:2025) ---
        # Coeficientes para teste (VCB < 600V)
        k_i = [-0.04287, 1.035, -0.083, 0, 0, -4.783e-09, 1.962e-06, -0.000229, 0.003141, 1.092]
        
        # 1. Cálculo da Corrente de Arco (Ia)
        # log10(Ia) = k1 + k2*log10(Ibf) + k3*log10(G) + (polinômio k4..k10)
        polinomio_i = (k_i[3]*i_bf**6 + k_i[4]*i_bf**5 + k_i[5]*i_bf**4 + k_i[6]*i_bf**3 + k_i[7]*i_bf**2 + k_i[8]*i_bf + k_i[9])
        log_ia = k_i[0] + k_i[1]*np.log10(i_bf) + k_i[2]*np.log10(gap_input) + polinomio_i
        ia_f = 10**log_ia

        # 2. Cálculo da Energia Incidente (E) simplificado para validação
        k_e = [0.753364, 0.566, 1.752636, 0, 0, 0, 0, 0, 0, 1.092, 0, -1.598, 0.957]
        # log10(E) = k1 + k2*log10(G) + k3*Iarc/Ibf + k4*log10(Ibf) + k5*log10(D) + k6*log10(Ia) + log10(1/CF)
        log_e = k_e[0] + k_e[1]*np.log10(gap_input) + k_e[11]*np.log10(d_trab) + k_e[12]*np.log10(ia_f)
        e_jcm2 = 12.552 * (tempo/50.0) * 10**log_e
        e_cal = e_jcm2 / 4.184

        # 3. DLA (Fronteira de Arco) - onde E = 1.2 cal/cm2 (5.0 J/cm2)
        # D = 10^((log10(5.0/(12.552*T/50)) - (k1 + k2*log10(G) + k6*log10(Ia))) / k5)
        log_dla = (np.log10(5.0/(12.552*(tempo/50.0))) - (k_e[0] + k_e[1]*np.log10(gap_input) + k_e[12]*np.log10(ia_f))) / k_e[11]
        dla_f = 10**log_dla

        # --- RESULTADOS EM TEMPO REAL ---
        st.divider()
        st.subheader("🏁 RESULTADOS FINAIS (NBR 17227)")
        res1, res2, res3 = st.columns(3)
        res1.metric("Corrente de Arco (I_arc)", f"{ia_f:.3f} kA")
        res2.metric("Energia Incidente (E)", f"{e_cal:.2f} cal/cm²")
        res3.metric("Distância Limite (DLA)", f"{dla_f:.1f} mm")

if __name__ == "__main__":
    main()
