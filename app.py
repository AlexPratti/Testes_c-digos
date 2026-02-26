import streamlit as st
import numpy as np

def main():
    st.set_page_config(page_title="NBR 17227 Revisada", layout="wide")
    st.title("⚡ Calculadora de Arco Elétrico - NBR 17227:2025")
    
    # --- ABAS ---
    tab1, tab2 = st.tabs(["📏 Dimensões", "🧪 Cálculos Técnicos"])

    # --- ABA 1: CONSULTA (Tabela 1) ---
    with tab1:
        dados_inv = {
            "CCM 15 kV": [152, 914.4], "CCM 5 kV": [104, 914.4],
            "CCM BT": [25, 457.2], "Conjunto Manobra BT": [32, 609.6]
        }
        escolha = st.selectbox("Selecione o Equipamento:", list(dados_inv.keys()))
        gap_padrao, d_padrao = dados_inv[escolha]
        st.info(f"Sugestão Tabela 1: G={gap_padrao}mm | D={d_padrao}mm")

    # --- ABA 2: CÁLCULOS (Matemática Corrigida) ---
    with tab2:
        col1, col2 = st.columns(2)
        with col1:
            v_oc = st.number_input("Tensão Voc (kV)", 0.208, 15.0, 13.8)
            i_bf = st.number_input("Curto-Circuito Ibf (kA)", 0.5, 106.0, 20.0)
            d_trab = st.number_input("Distância de Trabalho D (mm)", value=d_padrao)
        with col2:
            gap = st.number_input("Gap G (mm)", value=float(gap_padrao))
            tempo_ms = st.number_input("Duração T (ms)", 10.0, 2000.0, 100.0)
            t_sec = tempo_ms / 1000.0 # CONVERSÃO PARA SEGUNDOS É CRUCIAL

        # COEFICIENTES TABELA 4 (EXEMPLO VCB 14.3kV)
        k_ia = [0.005795, 1.015, -0.011, -1.557e-12, 4.556e-10, -4.186e-08, 8.346e-07, 5.482e-05, -0.003191, 0.9729]
        k_e = [3.825917, 0.11, -0.999749, -1.557e-12, 4.556e-10, -4.186e-08, 8.346e-07, 5.482e-05, -0.003191, 0.9729, 0, -1.568, 0.99]

        # 1. CÁLCULO IA (kA) - EQUAÇÃO 1
        # log10(Ia) = k1 + k2*log10(Ibf) + k3*log10(G) + polinômio(Ibf)
        poli_i = (k_ia[3]*i_bf**6 + k_ia[4]*i_bf**5 + k_ia[5]*i_bf**4 + k_ia[6]*i_bf**3 + k_ia[7]*i_bf**2 + k_ia[8]*i_bf + k_ia[9])
        ia_f = 10**(k_ia[0] + k_ia[1]*np.log10(i_bf) + k_ia[2]*np.log10(gap) + poli_i)

        # 2. CÁLCULO ENERGIA (cal/cm²) - EQUAÇÃO 3
        # log10(E) = k1 + k2*log10(G) + (k3*Ia)/poli + k11*log10(Ibf) + k12*log10(D) + k13*log10(Ia)
        poli_e = (k_e[3]*i_bf**6 + k_e[4]*i_bf**5 + k_e[5]*i_bf**4 + k_e[6]*i_bf**3 + k_e[7]*i_bf**2 + k_e[8]*i_bf + k_e[9])
        log_e = k_e[0] + k_e[1]*np.log10(gap) + (k_e[2]*ia_f)/poli_e + k_e[10]*np.log10(i_bf) + k_e[11]*np.log10(d_trab) + k_e[12]*np.log10(ia_f)
        e_jcm2 = 12.552 * (t_sec/0.05) * 10**log_e # Normalizado para 50ms
        e_cal = e_jcm2 / 4.184

        # 3. DLA (mm) - DISTÂNCIA PARA 1,2 cal/cm² (5.0 J/cm²)
        log_dla = (np.log10(5.0/(12.552*(t_sec/0.05))) - (k_e[0] + k_e[1]*np.log10(gap) + (k_e[2]*ia_f)/poli_e + k_e[10]*np.log10(i_bf) + k_e[12]*np.log10(ia_f))) / k_e[11]
        dla_f = 10**log_dla

        st.divider()
        res1, res2, res3 = st.columns(3)
        res1.metric("Corrente de Arco (Ia)", f"{ia_f:.3f} kA")
        res2.metric("Energia Incidente (E)", f"{e_cal:.2f} cal/cm²")
        res3.metric("Fronteira de Arco (DLA)", f"{dla_f:.1f} mm")

if __name__ == "__main__":
    main()
