import streamlit as st
import numpy as np

def main():
    st.set_page_config(page_title="NBR 17227 Pro", layout="wide")
    st.title("⚡ Sistema de Cálculo de Risco de Arco - NBR 17227:2025")

    # --- ABA 1: DIMENSÕES (Tabela 1) ---
    tab1, tab2 = st.tabs(["📏 Dimensões e Invólucros", "🧪 Cálculos e Resultados"])

    with tab1:
        st.header("Consulta de Equipamentos")
        dados_inv = {
            "CCM 15 kV": [152.0, 914.4, 914.4, 914.4, 914.4],
            "Conjunto de manobra 15 kV": [152.0, 914.4, 1143.0, 762.0, 762.0],
            "CCM e painel típico de BT": [25.0, 457.2, 355.6, 304.8, 203.3]
        }
        escolha = st.selectbox("Selecione o Equipamento:", list(dados_inv.keys()))
        info = dados_inv[escolha]
        c = st.columns(5)
        titles = ["GAP (G)", "Dist. Trab (D)", "Altura (A)", "Largura (L)", "Profundidade (P)"]
        for i, title in enumerate(titles):
            c[i].metric(title, f"{info[i]} mm")

    # --- ABA 2: CÁLCULOS TÉCNICOS ---
    with tab2:
        with st.form("calc_form"):
            st.subheader("Parâmetros de Entrada")
            col1, col2, col3 = st.columns(3)
            with col1:
                v_oc = st.number_input("Tensão Voc (kV)", value=13.80)
                i_bf = st.number_input("Curto-Circuito Ibf (kA)", value=4.85)
            with col2:
                config = st.selectbox("Eletrodos:", ["VCB", "VCBB", "HCB", "VOA", "HOA"])
                gap = st.number_input("Gap G (mm)", value=float(info[0]))
            with col3:
                dist = st.number_input("Distância D (mm)", value=float(info[1]))
                tempo = st.number_input("Tempo T (ms)", value=488.0)
            
            btn = st.form_submit_button("Calcular Resultados")

        if btn:
            # --- COEFICIENTES VCB (14.3kV) - Convertidos para Arrays NumPy ---
            ki = np.array([0.005795, 1.015, -0.011, -1.557e-12, 4.556e-10, -4.186e-8, 8.346e-7, 5.482e-5, -0.003191, 0.9729])
            ke = np.array([3.825917, 0.11, -0.999749, -1.557e-12, 4.556e-10, -4.186e-8, 8.346e-7, 5.482e-5, -0.003191, 0.9729, 0, -1.568, 0.99])
            cf = 1.28372 # Fator de invólucro

            # 1. Cálculo da Corrente de Arco (Ia)
            # log10(Ia) = k1 + k2*log10(Ibf) + k3*log10(G) + polinômio(k4...k10)
            poli_ia = (ki[3]*i_bf**6 + ki[4]*i_bf**5 + ki[5]*i_bf**4 + ki[6]*i_bf**3 + ki[7]*i_bf**2 + ki[8]*i_bf + ki[9])
            log_ia = (ki[0] + ki[1]*np.log10(i_bf) + ki[2]*np.log10(gap)) + poli_ia
            ia_final = 10**log_ia

            # 2. Cálculo da Energia Incidente (E) em cal/cm²
            poli_en = (ke[3]*i_bf**6 + ke[4]*i_bf**5 + ke[5]*i_bf**4 + ke[6]*i_bf**3 + ke[7]*i_bf**2 + ke[8]*i_bf + ke[9])
            log_e = ke[0] + ke[1]*np.log10(gap) + (ke[2]*ia_final)/poli_en + ke[10]*np.log10(i_bf) + ke[11]*np.log10(dist) + ke[12]*np.log10(ia_final) + np.log10(1.0/cf)
            e_cal = (12.552 * (tempo/50.0) * 10**log_e) / 4.184

            # 3. Fronteira de Arco (DLA)
            termos_fixos = ke[0] + ke[1]*np.log10(gap) + (ke[2]*ia_final)/poli_en + ke[10]*np.log10(i_bf) + ke[12]*np.log10(ia_final) + np.log10(1.0/cf)
            log_dla = (np.log10(5.0/(12.552*tempo/50.0)) - termos_fixos) / ke[11]
            dla_final = 10**log_dla

            # --- RESULTADOS ---
            st.divider()
            st.subheader("📊 Resultados Finais")
            r1, r2, r3 = st.columns(3)
            r1.metric("Corrente de Arco (Ia)", f"{ia_final:.5f} kA")
            r2.metric("Energia Incidente (E)", f"{e_cal:.5f} cal/cm²")
            r3.metric("Fronteira (DLA)", f"{dla_final:.1f} mm")

            # Categoria de Vestimenta
            if e_cal <= 1.2: cat = "Risco 0 (Algodão)"
            elif e_cal <= 8: cat = "Cat 2 (8 cal)"
            elif e_cal <= 25: cat = "Cat 3 (25 cal)"
            else: cat = "Cat 4 (40 cal)"
            st.warning(f"**Vestimenta recomendada:** {cat}")

if __name__ == "__main__":
    main()
