import streamlit as st
import numpy as np

def main():
    st.set_page_config(page_title="NBR 17227 Pro", layout="wide")
    st.title("⚡ Sistema de Cálculo de Risco de Arco - NBR 17227:2025")

    # --- ABA 1: DIMENSÕES (RESTABELECIDA) ---
    tab1, tab2 = st.tabs(["📏 Dimensões e Invólucros", "🧪 Cálculos e Interpolação"])

    with tab1:
        dados_inv = {
            "CCM 15 kV": [152.0, 914.4, 914.4, 914.4, 914.4],
            "Conjunto de manobra 15 kV": [152.0, 914.4, 1143.0, 762.0, 762.0],
            "CCM e painel típico de BT": [25.0, 457.2, 355.6, 304.8, 203.3]
        }
        escolha = st.selectbox("Selecione o Equipamento:", list(dados_inv.keys()))
        info = dados_inv[escolha]
        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("GAP (G)", f"{info[0]} mm"); c2.metric("Dist. Trab (D)", f"{info[1]} mm")
        c3.metric("Altura", f"{info[2]} mm"); c4.metric("Largura", f"{info[3]} mm"); c5.metric("Profundidade", f"{info[4]} mm")

    # --- ABA 2: CÁLCULOS TÉCNICOS ---
    with tab2:
        col1, col2, col3 = st.columns(3)
        with col1:
            v_oc = st.number_input("Tensão Voc (kV)", value=13.8, key="v_oc")
            i_bf = st.number_input("Curto-Circuito Ibf (kA)", value=10.0, key="i_bf")
        with col2:
            config = st.selectbox("Eletrodos:", ["VCB", "VCBB", "HCB"], key="config")
            gap = st.number_input("Gap G (mm)", value=float(info[0]), key="gap")
        with col3:
            dist_d = st.number_input("Distância D (mm)", value=float(info[1]), key="dist")
            tempo_t = st.number_input("Tempo T (ms)", value=1000.0, key="tempo")

        # --- COEFICIENTES VCB (14.3kV) ---
        k_ia = [0.005795, 1.015, -0.011, -1.557e-12, 4.556e-10, -4.186e-8, 8.346e-7, 5.482e-5, -0.003191, 0.9729]
        k_en = [3.825917, 0.11, -0.999749, -1.557e-12, 4.556e-10, -4.186e-8, 8.346e-7, 5.482e-5, -0.003191, 0.9729, 0, -1.568, 0.99]

        # MATEMÁTICA SEGURA (Evitando multiplicação vetorial)
        def calcular_ia(ibf, g, k):
            poli = (k[3]*ibf**6 + k[4]*ibf**5 + k[5]*ibf**4 + k[6]*ibf**3 + k[7]*ibf**2 + k[8]*ibf + k[9])
            log_ia = (k[0] + k[1]*np.log10(ibf) + k[2]*np.log10(g)) + poli
            return 10**log_ia

        def calcular_energia(ia, ibf, g, d, t, k):
            poli = (k[3]*ibf**6 + k[4]*ibf**5 + k[5]*ibf**4 + k[6]*ibf**3 + k[7]*ibf**2 + k[8]*ibf + k[9])
            log_e = k[0] + k[1]*np.log10(g) + (k[2]*ia)/poli + k[10]*np.log10(ibf) + k[11]*np.log10(d) + k[12]*np.log10(ia)
            # 12.552 (J/cm2) -> Normalizado por 50ms (T em segundos / 0.05)
            e_jcm2 = 12.552 * (t/50.0) * 10**log_e
            return e_jcm2 / 4.184

        # EXECUÇÃO DOS CÁLCULOS
        ia_f = calcular_ia(i_bf, gap, k_ia)
        e_f = calcular_energia(ia_f, i_bf, gap, dist_d, tempo_t, k_en)
        dla = dist_d * (e_f / 1.2)**(1.0 / 1.568)

        # CATEGORIA EPI
        cat = "Cat 2 (8 cal)" if e_f <= 8 else ("Cat 4 (40 cal)" if e_f <= 40 else "PERIGO")

        # --- RESULTADOS ---
        st.divider()
        st.subheader("✅ Resultados Finais Validados")
        r1, r2, r3 = st.columns(3)
        r1.metric("I_arc Final", f"{ia_f:.3f} kA")
        r2.metric("Energia Incidente", f"{e_f:.2f} cal/cm²")
        r3.metric("Fronteira (DLA)", f"{dla:.0f} mm")
        st.warning(f"Vestimenta Obrigatória: {cat}")

if __name__ == "__main__":
    main()
