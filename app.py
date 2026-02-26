import streamlit as st
import numpy as np

def main():
    st.set_page_config(page_title="Engenharia NBR 17227", layout="wide")
    st.title("⚡ Calculadora de Risco de Arco Elétrico - NBR 17227:2025")
    
    tab1, tab2 = st.tabs(["📏 Dimensões e Invólucros", "🧪 Cálculos de Arco (Iarc, DLA, Energia)"])

    # --- ABA 1: CONSULTA DE EQUIPAMENTOS (Tabela 1) ---
    with tab1:
        st.header("Classes de Equipamentos e Espaçamentos Típicos")
        dados_inv = {
            "CCM 15 kV": [152, 914.4, 914.4, 914.4],
            "Conjunto de manobra 15 kV": [152, 1143.0, 762.0, 762.0],
            "CCM 5 kV": [104, 660.4, 660.4, 660.4],
            "Conjunto de manobra 5 kV (Opção 1)": [104, 914.4, 914.4, 914.4],
            "Conjunto de manobra 5 kV (Opção 2)": [104, 1143.0, 762.0, 762.0],
            "CCM e painel rasos de BT": [25, 355.6, 304.8, 203.2],
            "CCM e painel típico de BT": [25, 355.6, 304.8, 203.3],
            "Conjunto de manobra BT": [32, 508.0, 508.0, 508.0],
            "Caixa de junção de cabos": [13, 355.6, 304.8, 203.2]
        }
        escolha = st.selectbox("Selecione o Equipamento:", list(dados_inv.keys()))
        info = dados_inv[escolha]
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("GAP Típico (G)", f"{info[0]} mm")
        c2.metric("Altura (A)", f"{info[1]} mm")
        c3.metric("Largura (L)", f"{info[2]} mm")
        c4.metric("Profundidade (P)", f"{info[3]} mm")

    # --- ABA 2: CÁLCULOS TÉCNICOS ---
    with tab2:
        st.header("Parâmetros de Entrada e Resultados")
        col_in1, col_in2, col_in3 = st.columns(3)
        with col_in1:
            v_oc = st.number_input("Tensão Voc (kV)", 0.208, 15.0, 13.8)
            i_bf = st.number_input("Curto-Circuito Ibf (kA)", 0.5, 106.0, 20.0)
            d_trab = st.number_input("Distância de Trabalho D (mm)", 305.0, 2000.0, 914.4)
        with col_in2:
            config = st.selectbox("Configuração dos Eletrodos:", ["VCB", "VCBB", "HCB", "VOA", "HOA"])
            gap = st.number_input("Gap G (mm)", value=float(info[0]))
            tempo = st.number_input("Duração do Arco T (ms)", min_value=10.0, value=100.0)
        with col_in3:
            tipo_painel = st.radio("Tipo de Compartimento:", ["Típico", "Raso"])
            st.info("Nota: DLA é calculada para 1,2 cal/cm² (5,0 J/cm²).")

        # --- DICIONÁRIO DE COEFICIENTES (Exemplo VCB - Preencher os demais conforme Tabela 4 e 6) ---
        # Ordem k1 a k10 (Tabela 4) e k1 a k13 (Tabela 6)
        k_corrente = {"VCB": {
            600: [-0.04287, 1.035, -0.083, 0, 0, -4.783e-09, 1.962e-06, -0.000229, 0.003141, 1.092],
            2700: [0.0065, 1.001, -0.024, -1.557e-12, 4.556e-10, -4.186e-08, 8.346e-07, 5.482e-05, -0.003191, 0.9729],
            14300: [0.005795, 1.015, -0.011, -1.557e-12, 4.556e-10, -4.186e-08, 8.346e-07, 5.482e-05, -0.003191, 0.9729]
        }}
        k_energia = {"VCB": {
            600: [0.753364, 0.566, 1.752636, 0, 0, -4.783e-09, 1.962e-06, -0.000229, 0.003141, 1.092, 0, -1.598, 0.957],
            2700: [2.40021, 0.165, 0.354202, -1.557e-12, 4.556e-10, -4.186e-08, 8.346e-07, 5.482e-05, -0.003191, 0.9729, 0, -1.569, 0.9778],
            14300: [3.825917, 0.11, -0.999749, -1.557e-12, 4.556e-10, -4.186e-08, 8.346e-07, 5.482e-05, -0.003191, 0.9729, 0, -1.568, 0.99]
        }}

        # --- FATOR CF (Tabela 8) ---
        b = {"Típico": {"VCB": [-0.0003, 0.03441, 0.4325]}, "Raso": {"VCB": [0.00222, -0.0256, 0.6222]}}
        cb = b[tipo_painel].get(config, b[tipo_painel]["VCB"])
        ees = (info[2]/25.4 + info[1]/25.4) / 2.0
        cf = (cb[0]*ees**2 + cb[1]*ees + cb[2]) if tipo_painel == "Típico" else (1.0/(cb[0]*ees**2 + cb[1]*ees + cb[2]))

        # --- FUNÇÕES DE CÁLCULO ---
        def calc_ia(ibf, g, k):
            return 10**((k[0] + k[1]*np.log10(ibf) + k[2]*np.log10(g)) + (k[3]*ibf**6 + k[4]*ibf**5 + k[5]*ibf**4 + k[6]*ibf**3 + k[7]*ibf**2 + k[8]*ibf + k[9]))

        def calc_energia_e_dla(ia, ibf, g, t, cf_val, d, k):
            # Equação 3: Energia Incidente em J/cm²
            p_ibf = (k[3]*ibf**7 + k[4]*ibf**6 + k[5]*ibf**5 + k[6]*ibf**4 + k[7]*ibf**3 + k[8]*ibf**2 + k[9]*ibf)
            log_e = k[0] + k[1]*np.log10(g) + (k[2]*ia / p_ibf if p_ibf != 0 else 0) + k[10]*np.log10(ibf) + k[11]*np.log10(d) + k[12]*np.log10(ia) + np.log10(1.0/cf_val)
            e_jcm2 = 12.552 * (t/50.0) * 10**log_e
            # DLA (Equação 7): Distância para 5,0 J/cm²
            log_dla = (np.log10(5.0/(12.552*(t/50.0))) - (k[0] + k[1]*np.log10(g) + (k[2]*ia/p_ibf if p_ibf !=0 else 0) + k[10]*np.log10(ibf) + k[12]*np.log10(ia) + np.log10(1.0/cf_val))) / k[11]
            return e_jcm2 / 4.184, 10**log_dla

        # Resultados Intermediários e Finais
        ia_600, ia_2700, ia_14300 = [calc_ia(i_bf, gap, k_corrente["VCB"][v]) for v in [600, 2700, 14300]]
        e_dla_600, e_dla_2700, e_dla_14300 = [calc_energia_e_dla(ia, i_bf, gap, tempo, cf, d_trab, k_energia["VCB"][v]) for ia, v in zip([ia_600, ia_2700, ia_14300], [600, 2700, 14300])]

        if v_oc <= 0.6: i_f, e_f, d_f = ia_600, e_dla_600[0], e_dla_600[1]
        elif v_oc <= 2.7:
            i_f = ia_600 + (ia_2700 - ia_600) * (v_oc - 0.6) / 2.1
            e_f = e_dla_600[0] + (e_dla_2700[0] - e_dla_600[0]) * (v_oc - 0.6) / 2.1
            d_f = e_dla_600[1] + (e_dla_2700[1] - e_dla_600[1]) * (v_oc - 0.6) / 2.1
        else:
            i_f = ia_2700 + (ia_14300 - ia_2700) * (v_oc - 2.7) / 11.6
            e_f = e_dla_2700[0] + (e_dla_14300[0] - e_dla_2700[0]) * (v_oc - 2.7) / 11.6
            d_f = e_dla_2700[1] + (e_dla_14300[1] - e_dla_2700[1]) * (v_oc - 2.7) / 11.6

        st.divider()
        st.subheader("🏁 RESULTADOS FINAIS (NBR 17227)")
        r1, r2, r3 = st.columns(3)
        r1.metric("Corrente de Arco (I_arc)", f"{i_f:.3f} kA")
        r2.metric("Energia Incidente (E)", f"{e_f:.2f} cal/cm²")
        r3.metric("Distância-Limite de Arco (DLA)", f"{d_f:.1f} mm")

if __name__ == "__main__":
    main()
