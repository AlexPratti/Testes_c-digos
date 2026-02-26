import streamlit as st
import numpy as np

def main():
    st.set_page_config(page_title="NBR 17227 Pro", layout="wide")
    st.title("⚡ Sistema de Cálculo de Risco de Arco - NBR 17227:2025")

    # --- BANCO DE DADOS DA TABELA 1 ---
    dados_inv = {
        "CCM 15 kV": [152.0, 914.4, 914.4, 914.4, 914.4],
        "Conjunto de manobra 15 kV": [152.0, 914.4, 1143.0, 762.0, 762.0],
        "CCM 5 kV": [104.0, 914.4, 660.4, 660.4, 660.4],
        "CCM e painel rasos de BT": [25.0, 457.2, 355.6, 304.8, 203.2],
        "CCM e painel típico de BT": [25.0, 457.2, 355.6, 304.8, 203.3]
    }

    tab1, tab2 = st.tabs(["📏 Dimensões e Invólucros", "🧪 Cálculos e Interpolação"])

    with tab1:
        st.header("Consulta de Equipamentos")
        escolha = st.selectbox("Selecione o Equipamento:", list(dados_inv.keys()), key="equip_principal")
        info = dados_inv[escolha]
        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("GAP (G)", f"{info[0]} mm")
        c2.metric("Dist. Trab (D)", f"{info[1]} mm")
        c3.metric("Altura (A)", f"{info[2]} mm")
        c4.metric("Largura (L)", f"{info[3]} mm")
        c5.metric("Profundidade (P)", f"{info[4]} mm")

    with tab2:
        st.header("Parâmetros de Entrada")
        col_in1, col_in2, col_in3 = st.columns(3)
        
        with col_in1:
            v_oc = st.number_input("Tensão Voc (kV)", 0.208, 15.0, 13.8, step=0.01, key="v_oc_act")
            i_bf = st.number_input("Curto-Circuito Ibf (kA)", 0.5, 106.0, 4.85, step=0.01, key="i_bf_act")
        with col_in2:
            config = st.selectbox("Eletrodos:", ["VCB", "VCBB", "HCB", "VOA", "HOA"], key="conf_act")
            gap_in = st.number_input("Gap G (mm)", value=float(info[0]), key="gap_act")
        with col_in3:
            d_trab = st.number_input("Distância D (mm)", value=float(info[1]), key="dist_act")
            tempo = st.number_input("Tempo T (ms)", value=488.0, key="tempo_act")

        # --- LÓGICA DE CÁLCULO (NBR 17227:2025) ---
        # Coeficientes Tabela 4 (Ia) e 6 (En) - Exemplo VCB 14.3kV
        ki = [0.005795, 1.015, -0.011, -1.557e-12, 4.556e-10, -4.186e-08, 8.346e-07, 5.482e-05, -0.003191, 0.9729]
        ke = [3.825917, 0.11, -0.999749, 0, 0, 0, 0, 0, 0, 0.9729, 0, -1.568, 0.99]

        # 1. Corrente de Arco (Ia) - Estrutura Logarítmica Aditiva
        def calcular_ia_real(ibf, g, k):
            poli = (k[3]*ibf**6 + k[4]*ibf**5 + k[5]*ibf**4 + k[6]*ibf**3 + k[7]*ibf**2 + k[8]*ibf + k[9])
            log_ia = (k[0] + k[1]*np.log10(ibf) + k[2]*np.log10(g)) + poli
            return 10**log_ia

        ia_f = calcular_ia_real(i_bf, gap_in, ki)

        # 2. Energia Incidente (E) e DLA
        cf = 1.28372 # Conforme seu Excel
        log_e = ke[0] + ke[1]*np.log10(gap_in) + ke[2]*(ia_f/i_bf) + ke[11]*np.log10(d_trab) + ke[12]*np.log10(ia_f) + np.log10(1.0/cf)
        e_cal = (12.552 * (tempo/50.0) * 10**log_e) / 4.184
        
        # Fronteira (DLA)
        dla_f = 10**((np.log10(5.0/(12.552*tempo/50.0)) - (ke[0] + ke[1]*np.log10(gap_in) + ke[2]*(ia_f/i_bf) + ke[12]*np.log10(ia_f) + np.log10(1.0/cf))) / ke[11])

        # 3. Categoria de Vestimenta
        def get_vestimenta(e):
            if e <= 1.2: return "Risco 0 (Algodão)"
            if e <= 8:   return "Categoria 2 (8 cal)"
            if e <= 25:  return "Categoria 3 (25 cal)"
            return "Categoria 4 (40 cal)"

        # --- EXIBIÇÃO DE RESULTADOS (FORÇA REPROCESSAMENTO) ---
        st.divider()
        st.subheader("✅ Resultados Finais Validados")
        r1, r2, r3, r4 = st.columns(4)
        r1.metric("I_arc Final", f"{ia_f:.3f} kA")
        r2.metric("Energia Incidente", f"{e_cal:.2f} cal/cm²")
        r3.metric("Fronteira (DLA)", f"{abs(dla_f):.0f} mm")
        r4.warning(f"Vestimenta: {get_vestimenta(e_cal)}")

if __name__ == "__main__":
    main()
