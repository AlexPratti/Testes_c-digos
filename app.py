import streamlit as st
import numpy as np

def main():
    st.set_page_config(page_title="NBR 17227 Pro", layout="wide")
    st.title("⚡ Gestão de Risco de Arco Elétrico - NBR 17227:2025")

    # --- ABA 1: DIMENSÕES (RESTAURADA) ---
    tab1, tab2 = st.tabs(["📏 Dimensões e Invólucros", "🧪 Cálculos de Arco"])

    with tab1:
        st.header("Consulta de Equipamentos (Tabela 1)")
        # Formato: [GAP, Dist. Trabalho, Altura, Largura, Profundidade]
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
        escolha = st.selectbox("Selecione o Equipamento:", list(dados_inv.keys()))
        info = dados_inv[escolha]
        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("GAP (G)", f"{info[0]} mm")
        c2.metric("Dist. Trabalho (D)", f"{info[1]} mm")
        c3.metric("Altura (A)", f"{info[2]} mm")
        c4.metric("Largura (L)", f"{info[3]} mm")
        c5.metric("Profundidade (P)", f"{info[4]} mm")

    # --- ABA 2: CÁLCULOS (MATEMÁTICA CORRIGIDA) ---
    with tab2:
        st.header("Entradas e Resultados Técnicos")
        col_in1, col_in2 = st.columns(2)
        with col_in1:
            v_oc = st.number_input("Tensão Voc (kV)", 0.208, 15.0, 13.8)
            i_bf = st.number_input("Curto-Circuito Ibf (kA)", 0.5, 106.0, 4.852)
            d_trab = st.number_input("Distância de Trabalho D (mm)", value=info[1])
        with col_in2:
            config = st.selectbox("Eletrodos:", ["VCB", "VCBB", "HCB", "VOA", "HOA"])
            gap_in = st.number_input("Gap G (mm)", value=info[0])
            tempo = st.number_input("Duração T (ms)", 10.0, 2000.0, 488.0)

        # COEFICIENTES TABELA 4 (CORRENTE - EXEMPLO VCB 14.3kV)
        k_ia = [0.005795, 1.015, -0.011, -1.557e-12, 4.556e-10, -4.186e-08, 8.346e-07, 5.482e-05, -0.003191, 0.9729]
        # COEFICIENTES TABELA 6 (ENERGIA - EXEMPLO VCB 14.3kV)
        k_en = [3.825917, 0.11, -0.999749, -1.557e-12, 4.556e-10, -4.186e-08, 8.346e-07, 5.482e-05, -0.003191, 0.9729, 0, -1.568, 0.99]

        # 1. CÁLCULO IA (kA) - EQUAÇÃO 1
        # log10(Ia) = k1 + k2*log10(Ibf) + k3*log10(G) + polinômio(Ibf)
        poli_i = (k_ia[3]*i_bf**6 + k_ia[4]*i_bf**5 + k_ia[5]*i_bf**4 + k_ia[6]*i_bf**3 + k_ia[7]*i_bf**2 + k_ia[8]*i_bf + k_ia[9])
        log_ia = k_ia[0] + k_ia[1]*np.log10(i_bf) + k_ia[2]*np.log10(gap_in) + poli_i
        ia_f = 10**log_ia

        # 2. CÁLCULO ENERGIA (cal/cm²) - EQUAÇÃO 3
        # log10(E) = k1 + k2*log10(G) + (k3*Ia)/poli + k11*log10(Ibf) + k12*log10(D) + k13*log10(Ia)
        poli_e = (k_en[3]*i_bf**6 + k_en[4]*i_bf**5 + k_en[5]*i_bf**4 + k_en[6]*i_bf**3 + k_en[7]*i_bf**2 + k_en[8]*i_bf + k_en[9])
        log_e = k_en[0] + k_en[1]*np.log10(gap_in) + (k_en[2]*ia_f)/poli_e + k_en[10]*np.log10(i_bf) + k_en[11]*np.log10(d_trab) + k_en[12]*np.log10(ia_f)
        
        # Constante 12.552 (J/cm2) normalizada para tempo em ms (tempo/50ms)
        e_jcm2 = 12.552 * (tempo/50.0) * 10**log_e
        e_cal = e_jcm2 / 4.184

        st.divider()
        st.subheader("🏁 RESULTADOS FINAIS")
        r1, r2 = st.columns(2)
        r1.metric("Corrente de Arco (I_arc)", f"{ia_f:.3f} kA")
        r2.metric("Energia Incidente (E)", f"{e_cal:.2f} cal/cm²")

if __name__ == "__main__":
    main()
