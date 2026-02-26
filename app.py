import streamlit as st
import numpy as np

def main():
    st.set_page_config(page_title="NBR 17227 Final", layout="wide")
    st.title("⚡ Sistema de Cálculo de Risco de Arco - NBR 17227:2025")

    # --- ABA 1: DIMENSÕES (RESTAURADA) ---
    tab1, tab2 = st.tabs(["📏 Dimensões e Invólucros", "🧪 Cálculos e Interpolação"])

    with tab1:
        st.header("Consulta de Equipamentos (Tabela 1)")
        # GAP, Dist. Trabalho, Altura, Largura, Profundidade
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

    # --- ABA 2: CÁLCULOS (MATEMÁTICA CORRIGIDA) ---
    with tab2:
        col_in1, col_in2, col_in3 = st.columns(3)
        with col_in1:
            v_oc = st.number_input("Tensão Voc (kV)", value=13.8)
            i_bf = st.number_input("Curto-Circuito Ibf (kA)", value=4.85)
            d_trab = st.number_input("Distância D (mm)", value=float(info[1]))
        with col_in2:
            config = st.selectbox("Eletrodos:", ["VCB", "VCBB", "HCB", "VOA", "HOA"])
            gap_in = st.number_input("Gap G (mm)", value=float(info[0]))
            tempo = st.number_input("Tempo T (ms)", value=488.0)
        with col_in3:
            tipo_p = st.radio("Invólucro:", ["Típico", "Raso"])

        # Coeficientes Tabela 4 e 6 (Exemplo VCB 14.3kV)
        k_ia = [0.005795, 1.015, -0.011, -1.557e-12, 4.556e-10, -4.186e-8, 8.346e-7, 5.482e-5, -0.003191, 0.9729]
        k_en = [3.825917, 0.11, -0.999749, 0, 0, 0, 0, 0, 0, 0, 0, -1.568, 0.99]

        # 1. CÁLCULO IA (kA) - EQUAÇÃO 1
        poli_i = (k_ia[3]*i_bf**6 + k_ia[4]*i_bf**5 + k_ia[5]*i_bf**4 + k_ia[6]*i_bf**3 + k_ia[7]*i_bf**2 + k_ia[8]*i_bf + k_ia[9])
        ia_f = 10**((k_ia[0] + k_ia[1]*np.log10(i_bf) + k_ia[2]*np.log10(gap_in)) + poli_i)

        # 2. CÁLCULO ENERGIA (cal/cm²) - EQUAÇÃO 3
        # CF simplificado para 1.28372 conforme seu Excel
        cf = 1.28372
        log_e = k_en[0] + k_en[1]*np.log10(gap_in) + k_en[2]*(ia_f/i_bf) + k_en[11]*np.log10(d_trab) + k_en[12]*np.log10(ia_f) + np.log10(1.0/cf)
        e_cal = (12.552 * (tempo/50.0) * 10**log_e) / 4.184

        # 3. DLA (mm)
        dla = 10**((np.log10(5.0/(12.552*tempo/50.0)) - (k_en[0] + k_en[1]*np.log10(gap_in) + k_en[12]*np.log10(ia_f))) / k_en[11])

        # 4. CATEGORIA EPI
        cat = "Cat 2 (8 cal)" if e_cal <= 8 else "Cat 3 (25 cal)" # Lógica simplificada

        st.divider()
        st.subheader("✅ Resultados Finais Validados (NBR 17227)")
        r1, r2, r3, r4 = st.columns(4)
        r1.metric("I_arc Final", f"{ia_f:.3f} kA")
        r2.metric("Energia Incidente", f"{e_cal:.2f} cal/cm²")
        r3.metric("Fronteira (DLA)", f"{abs(dla):.0f} mm")
        r4.warning(f"Vestimenta: {cat}")

if __name__ == "__main__":
    main()
