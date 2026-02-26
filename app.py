import streamlit as st
import numpy as np

def main():
    st.set_page_config(page_title="NBR 17227 Pro", layout="wide")
    st.title("⚡ Sistema de Cálculo de Risco de Arco - NBR 17227:2025")

    # --- BANCO DE DADOS (ABA 1) ---
    dados_inv = {
        "CCM 15 kV": [152.0, 914.4, 914.4, 914.4, 914.4],
        "Conjunto de manobra 15 kV": [152.0, 914.4, 1143.0, 762.0, 762.0],
        "CCM 5 kV": [104.0, 914.4, 660.4, 660.4, 660.4],
        "CCM e painel típico de BT": [25.0, 457.2, 355.6, 304.8, 203.3]
    }

    tab1, tab2 = st.tabs(["📏 Dimensões e Invólucros", "🧪 Cálculos e Interpolação"])

    with tab1:
        st.header("Consulta de Tabela 1")
        escolha = st.selectbox("Equipamento:", list(dados_inv.keys()), key="sel_t1")
        info = dados_inv[escolha]
        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("GAP (G)", f"{info[0]} mm")
        c2.metric("Dist. Trab (D)", f"{info[1]} mm")
        c3.metric("Altura (A)", f"{info[2]} mm")
        c4.metric("Largura (L)", f"{info[3]} mm")
        c5.metric("Profundidade (P)", f"{info[4]} mm")

    with tab2:
        st.header("Parâmetros de Entrada")
        col1, col2, col3 = st.columns(3)
        with col1:
            # Chaves únicas (key) garantem que o Streamlit atualize as variáveis na hora
            v_oc = st.number_input("Tensão Voc (kV)", value=13.80, key="in_voc_f")
            i_bf = st.number_input("Curto-Circuito Ibf (kA)", value=4.85, key="in_ibf_f")
        with col2:
            config = st.selectbox("Eletrodos:", ["VCB", "VCBB", "HCB", "VOA", "HOA"], key="in_conf_f")
            gap = st.number_input("Gap G (mm)", value=float(info[0]), key="in_gap_f")
        with col3:
            dist_d = st.number_input("Distância D (mm)", value=float(info[1]), key="in_dist_f")
            tempo_t = st.number_input("Tempo T (ms)", value=20.0, key="in_tempo_f")

        # --- DICIONÁRIO DE COEFICIENTES (NBR 17227 / IEEE 1584-2018) ---
        # Coeficientes k1 a k10 para Ia e k1 a k13 para Energia (VCB 14.3kV)
        ki = [0.005795, 1.015, -0.011, -1.557e-12, 4.556e-10, -4.186e-08, 8.346e-07, 5.482e-05, -0.003191, 0.9729]
        ke = [3.825917, 0.11, -0.999749, -1.557e-12, 4.556e-10, -4.186e-08, 8.346e-07, 5.482e-05, -0.003191, 0.9729, 0, -1.568, 0.99]
        cf = 1.28372 # Fator de invólucro do seu Excel

        # --- MATEMÁTICA CORRIGIDA (Cálculos de Engenharia) ---
        # 1. Corrente de Arco (Ia)
        # log10(Ia) = k1 + k2*log10(Ibf) + k3*log10(G) + polinômio(Ibf)
        poli_ia = (ki[3]*i_bf**6 + ki[4]*i_bf**5 + ki[5]*i_bf**4 + ki[6]*i_bf**3 + ki[7]*i_bf**2 + ki[8]*i_bf + ki[9])
        log_ia = (ki[0] + ki[1]*np.log10(i_bf) + ki[2]*np.log10(gap)) + poli_ia
        ia_f = 10**log_ia

        # 2. Energia Incidente (E)
        poli_en = (ke[3]*i_bf**6 + ke[4]*i_bf**5 + ke[5]*i_bf**4 + ke[6]*i_bf**3 + ke[7]*i_bf**2 + ke[8]*i_bf + ke[9])
        log_e = ke[0] + ke[1]*np.log10(gap) + (ke[2]*ia_f)/poli_en + ke[10]*np.log10(i_bf) + ke[11]*np.log10(dist_d) + ke[12]*np.log10(ia_f) + np.log10(1.0/cf)
        
        # 12.552 (J/cm2) -> Normalizado (t/50ms). Conversão para cal/cm² (/4.184)
        e_cal = (12.552 * (tempo_t / 50.0) * 10**log_e) / 4.184

        # 3. Fronteira de Arco (DLA) para 1.2 cal/cm² (5.0 J/cm²)
        # log10(D) = (log10(5.0/(12.552*T/50)) - (k1 + k2*log10(G) + k3*Ia/poli + k4*log10(Ibf) + k6*log10(Ia) + log10(1/cf))) / k5
        termos_sem_d = (ke[0] + ke[1]*np.log10(gap) + (ke[2]*ia_f)/poli_en + ke[10]*np.log10(i_bf) + ke[12]*np.log10(ia_f) + np.log10(1.0/cf))
        log_dla = (np.log10(5.0 / (12.552 * (tempo_t/50.0))) - termos_sem_d) / ke[11]
        dla_f = 10**log_dla

        # --- RESULTADOS FINAIS ---
        st.divider()
        st.markdown("### ✅ Resultados Finais Validados")
        r1, r2, r3 = st.columns(3)
        r1.metric("I_arc Final", f"{ia_f:.3f} kA")
        r2.metric("Energia Incidente", f"{e_cal:.2f} cal/cm²")
        r3.metric("Fronteira (DLA)", f"{abs(dla_f):.0f} mm")

        # Categoria de Vestimenta
        cat = "Risco 0" if e_cal <= 1.2 else ("Cat 1 (4 cal)" if e_cal <= 4 else ("Cat 2 (8 cal)" if e_cal <= 8 else ("Cat 3 (25 cal)" if e_cal <= 25 else "Cat 4 (40 cal)")))
        st.warning(f"Vestimenta Obrigatória: {cat}")

if __name__ == "__main__":
    main()
