import streamlit as st
import numpy as np

def main():
    st.set_page_config(page_title="Calculadora NBR 17227", layout="wide")
    st.title("⚡ Gestão de Risco de Arco Elétrico - NBR 17227:2025")
    
    tab1, tab2 = st.tabs(["📏 Dimensões e Invólucros", "🧪 Correntes e Distância de Arco (DLA)"])

    # --- DADOS DE ENTRADA COMPARTILHADOS ---
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

    with tab2:
        st.header("Cálculo de I_arc e DLA Final")
        col_in1, col_in2, col_in3 = st.columns(3)
        with col_in1:
            v_oc = st.number_input("Tensão Voc (kV)", 0.208, 15.0, 13.8)
            i_bf = st.number_input("Curto-Circuito Ibf (kA)", 0.5, 106.0, 20.0)
        with col_in2:
            config = st.selectbox("Configuração:", ["VCB", "VCBB", "HCB", "VOA", "HOA"])
            gap = st.number_input("Gap G (mm)", value=float(info[0]))
        with col_in3:
            tempo = st.number_input("Tempo de Arco T (ms)", min_value=10.0, value=100.0)
            tipo_painel = st.radio("Tipo de Compartimento:", ["Típico", "Raso"])

        # --- COEFICIENTES TABELA 4 (Corrente) e TABELA 6 (Energia/DLA) ---
        # Nota: Simplificado para VCB. Deve-se expandir o dicionário com os valores da Tabela 4 e 6.
        k_corrente = {
            "VCB": {
                600:   [-0.04287, 1.035, -0.083, 0, 0, -4.783e-09, 1.962e-06, -0.000229, 0.003141, 1.092],
                2700:  [0.0065, 1.001, -0.024, -1.557e-12, 4.556e-10, -4.186e-08, 8.346e-07, 5.482e-05, -0.003191, 0.9729],
                14300: [0.005795, 1.015, -0.011, -1.557e-12, 4.556e-10, -4.186e-08, 8.346e-07, 5.482e-05, -0.003191, 0.9729]
            }
        }
        
        # Coeficientes Tabela 6 para DLA (k1 a k13)
        k_dla = {
            "VCB": {
                600:   [0.753364, 0.566, 1.752636, 0, 0, -4.783e-09, 1.962e-06, -0.000229, 0.003141, 1.092, 0, -1.598, 0.957],
                2700:  [2.40021, 0.165, 0.354202, -1.557e-12, 4.556e-10, -4.186e-08, 8.346e-07, 5.482e-05, -0.003191, 0.9729, 0, -1.569, 0.9778],
                14300: [3.825917, 0.11, -0.999749, -1.557e-12, 4.556e-10, -4.186e-08, 8.346e-07, 5.482e-05, -0.003191, 0.9729, 0, -1.568, 0.99]
            }
        }

        # --- CÁLCULO DO FATOR DE CORREÇÃO DO INVÓLUCRO (CF) ---
        # Tabela 8: Coeficientes b1, b2, b3
        b = {"Típico": {"VCB": [-0.0003, 0.03441, 0.4325]}, "Raso": {"VCB": [0.00222, -0.0256, 0.6222]}}
        coef_b = b[tipo_painel].get(config, b[tipo_painel]["VCB"]) # Default VCB se não mapeado
        
        ees = (info[1]/25.4 + info[2]/25.4) / 2.0 # Tamanho equivalente em polegadas
        if tipo_painel == "Típico":
            cf = coef_b[0] * ees**2 + coef_b[1] * ees + coef_b[2]
        else:
            cf = 1.0 / (coef_b[0] * ees**2 + coef_b[1] * ees + coef_b[2])

        # --- FUNÇÕES DE CÁLCULO ---
        def calc_ia(ibf, g, k):
            return 10**((k[0] + k[1]*np.log10(ibf) + k[2]*np.log10(g)) + (k[3]*ibf**6 + k[4]*ibf**5 + k[5]*ibf**4 + k[6]*ibf**3 + k[7]*ibf**2 + k[8]*ibf + k[9]))

        def calc_dla(ia, ibf, g, t, cf_val, k):
            # Equações 7, 8, 9 da NBR 17227
            poly = (k[3]*ibf**6 + k[4]*ibf**5 + k[5]*ibf**4 + k[6]*ibf**3 + k[7]*ibf**2 + k[8]*ibf + k[9])
            log_dla = k[0] + k[1]*np.log10(g) + poly + k[10]*np.log10(ibf) + k[12]*np.log10(ia) + np.log10(1.0/cf_val) - np.log10(20.0/t)
            return 10**(log_dla / -k[11])

        # Intermediários
        ia600, ia2700, ia14300 = [calc_ia(i_bf, gap, k_corrente["VCB"][v]) for v in [600, 2700, 14300]]
        dla600, dla2700, dla14300 = [calc_dla(ia, i_bf, gap, tempo, cf, k_dla["VCB"][v]) for ia, v in zip([ia600, ia2700, ia14300], [600, 2700, 14300])]

        # Interpolação Final (Equações 26-30)
        if v_oc <= 0.6: 
            i_final, dla_final = ia600, dla600
        elif v_oc <= 2.7:
            i_final = ia600 + (ia2700 - ia600) * (v_oc - 0.6) / 2.1
            dla_final = dla600 + (dla2700 - dla600) * (v_oc - 0.6) / 2.1
        else:
            i_final = ia2700 + (ia14300 - ia2700) * (v_oc - 2.7) / 11.6
            dla_final = dla2700 + (dla14300 - dla2700) * (v_oc - 2.7) / 11.6

        st.divider()
        st.subheader("🏁 RESULTADOS FINAIS (NBR 17227)")
        res1, res2 = st.columns(2)
        res1.metric("Corrente de Arco Final (I_arc)", f"{i_final:.3f} kA")
        res2.metric("Distância-Limite de Arco (DLA/AFB)", f"{dla_final:.1f} mm")
        st.caption(f"Fator de Correção do Invólucro (CF) calculado: {cf:.4f}")

if __name__ == "__main__":
    main()
