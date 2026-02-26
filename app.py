import streamlit as st
import numpy as np

def main():
    st.set_page_config(page_title="Calculadora NBR 17227", layout="wide")
    st.title("⚡ Gestão de Risco de Arco Elétrico - NBR 17227:2025")

    # --- ABA 1: CONSULTA DE EQUIPAMENTOS (Tabela 1) ---
    tab1, tab2, tab3 = st.tabs(["📏 Dimensões e Invólucros", "🧪 Cálculos de Arco", "📄 Relatório"])

    with tab1:
        st.header("Classes de Equipamentos e Espaçamentos Típicos")
        dados_inv = {
            "CCM 15 kV": [152, 914.4, 914.4, 914.4, 914.4],
            "Conjunto de manobra 15 kV": [152, 914.4, 1143.0, 762.0, 762.0],
            "CCM 5 kV": [104, 914.4, 660.4, 660.4, 660.4],
            "Conjunto de manobra 5 kV (Opção 1)": [104, 914.4, 914.4, 914.4, 914.4],
            "Conjunto de manobra 5 kV (Opção 2)": [104, 914.4, 1143.0, 762.0, 762.0],
            "CCM e painel rasos de BT": [25, 457.2, 355.6, 304.8, 203.2],
            "CCM e painel típico de BT": [25, 457.2, 355.6, 304.8, 203.3],
            "Conjunto de manobra BT": [32, 609.6, 508.0, 508.0, 508.0],
            "Caixa de junção de cabos": [13, 457.2, 355.6, 304.8, 203.2]
        }
        
        escolha = st.selectbox("Selecione o Equipamento e Classe de Tensão:", list(dados_inv.keys()))
        info = dados_inv[escolha]
        
        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("GAP (G)", f"{info[0]} mm")
        c2.metric("Dist. Trabalho (D)", f"{info[1]} mm")
        c3.metric("Altura (A)", f"{info[2]} mm")
        c4.metric("Largura (L)", f"{info[3]} mm")
        c5.metric("Profundidade (P)", f"{info[4]} mm")

    # --- ABA 2: CÁLCULOS TÉCNICOS (CORRIGIDOS) ---
    with tab2:
        st.header("Parâmetros de Entrada")
        col_in1, col_in2, col_in3 = st.columns(3)
        
        with col_in1:
            # Tensão e Curto
            v_oc = st.number_input("Tensão Voc (kV)", 0.208, 15.0, 0.38, format="%.3f")
            i_bf = st.number_input("Curto-Circuito Ibf (kA)", 0.5, 106.0, 20.0)
            d_trab = st.number_input("Distância de Trabalho D (mm)", value=float(info[1]))
        
        with col_in2:
            config = st.selectbox("Configuração dos Eletrodos:", ["VCB", "VCBB", "HCB", "VOA", "HOA"])
            gap_input = st.number_input("Gap G (mm)", value=float(info[0]))
            tempo = st.number_input("Duração do Arco T (ms)", 10.0, 1000.0, 100.0)
            
        with col_in3:
            tipo_p = st.radio("Tipo de Compartimento:", ["Típico", "Raso"])

        # --- Lógica de Cálculo IEEE 1584 / NBR 17227 ---
        # Coeficientes simplificados para validação (VCB < 600V)
        # log10(Ia) = k1 + k2*log10(Ibf) + k3*log10(G) + k10
        k_i = [-0.04287, 1.035, -0.083, 0, 0, 0, 0, 0, 0, 1.092]
        k_e = [0.753364, 0.566, 1.752636, 0, 0, 0, 0, 0, 0, 1.092, 0, -1.598, 0.957]

        # 1. Cálculo da Corrente de Arco (Ia)
        log_ia = k_i[0] + k_i[1]*np.log10(i_bf) + k_i[2]*np.log10(gap_input) + k_i[9]
        ia_f = 10**log_ia

        # 2. Cálculo da Energia Incidente (E)
        # CF simplificado como 1.0 para este teste
        log_e = k_e[0] + k_e[1]*np.log10(gap_input) + k_e[11]*np.log10(d_trab) + k_e[12]*np.log10(ia_f)
        e_jcm2 = 12.552 * (tempo/50.0) * 10**log_e
        e_cal = e_jcm2 / 4.184

        # 3. DLA (Onde E = 1.2 cal/cm2 -> 5.0 J/cm2)
        log_dla = (np.log10(5.0 / (12.552 * (tempo/50.0))) - (k_e[0] + k_e[1]*np.log10(gap_input) + k_e[12]*np.log10(ia_f))) / k_e[11]
        dla_f = 10**log_dla

        st.divider()
        st.subheader("🏁 RESULTADOS FINAIS")
        r1, r2, r3 = st.columns(3)
        r1.metric("Corrente de Arco (I_arc)", f"{ia_f:.3f} kA")
        r2.metric("Energia Incidente (E)", f"{e_cal:.2f} cal/cm²")
        r3.metric("Distância Limite (DLA)", f"{dla_f:.1f} mm")

    with tab3:
        st.info("Aba de Relatórios: Os resultados acima podem ser exportados.")
        st.button("Gerar PDF do Cálculo Atual")

if __name__ == "__main__":
    main()
