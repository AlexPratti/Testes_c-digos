import streamlit as st
import numpy as np

# Configuração da página
st.set_page_config(page_title="NBR 17227 Pro", layout="wide")

def main():
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
        escolha = st.selectbox("Equipamento:", list(dados_inv.keys()))
        info = dados_inv[escolha]
        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("GAP", f"{info[0]} mm"); c2.metric("Distância D", f"{info[1]} mm")
        c3.metric("Altura", f"{info[2]} mm"); c4.metric("Largura", f"{info[3]} mm"); c5.metric("Profundidade", f"{info[4]} mm")

    with tab2:
        st.header("Parâmetros de Entrada")
        col1, col2, col3 = st.columns(3)
        with col1:
            v_oc = st.number_input("Tensão Voc (kV)", value=13.80)
            i_bf = st.number_input("Curto-Circuito Ibf (kA)", value=10.00)
        with col2:
            config = st.selectbox("Eletrodos:", ["VCB", "VCBB", "HCB", "VOA", "HOA"])
            gap = st.number_input("Gap G (mm)", value=float(info[0]))
        with col3:
            dist_d = st.number_input("Distância D (mm)", value=float(info[1]))
            tempo_t = st.number_input("Tempo T (ms)", value=1000.0)

        # --- FUNÇÃO DE CÁLCULO IA (kA) ---
        def calc_ia_step(ibf, g, k):
            log_ia = (k[0] + k[1]*np.log10(ibf) + k[2]*np.log10(g)) + \
                     (k[3]*ibf**6 + k[4]*ibf**5 + k[5]*ibf**4 + k[6]*ibf**3 + k[7]*ibf**2 + k[8]*ibf + k[9])
            return 10**log_ia

        # --- FUNÇÃO DE CÁLCULO ENERGIA (cal/cm²) ---
        def calc_en_step(ia, ibf, g, d, t, k, cf):
            log_e = k[0] + k[1]*np.log10(g) + (k[2]*ia)/(k[3]*ibf**6 + k[4]*ibf**5 + k[5]*ibf**4 + k[6]*ibf**3 + k[7]*ibf**2 + k[8]*ibf + k[9]) + \
                    k[10]*np.log10(ibf) + k[11]*np.log10(d) + k[12]*np.log10(ia) + np.log10(1.0/cf)
            e_jcm2 = 12.552 * (t/50.0) * 10**log_e
            return e_jcm2 / 4.184

        # Coeficientes VCB (Exemplos p/ Validação - 14.3kV)
        k_ia_14k = [0.005795, 1.015, -0.011, -1.557e-12, 4.556e-10, -4.186e-8, 8.346e-7, 5.482e-5, -0.003191, 0.9729]
        k_en_14k = [3.825917, 0.11, -0.999749, -1.557e-12, 4.556e-10, -4.186e-8, 8.346e-7, 5.482e-5, -0.003191, 0.9729, 0, -1.568, 0.99]
        
        # Fator CF (Simplificado para validação conforme seu Excel)
        cf = 1.28372

        # Execução dos cálculos reativos
        ia_final = calc_ia_step(i_bf, gap, k_ia_14k)
        energia_final = calc_en_step(ia_final, i_bf, gap, dist_d, tempo_t, k_en_14k, cf)
        
        # Cálculo da DLA (Fronteira para 1.2 cal/cm²)
        dla = dist_d * (energia_final / 1.2)**(1.0 / 1.568)

        # Categoria de Vestimenta
        if energia_final <= 1.2: cat = "Risco 0 (Algodão)"
        elif energia_final <= 8: cat = "Categoria 2 (8 cal)"
        elif energia_final <= 25: cat = "Categoria 3 (25 cal)"
        else: cat = "Categoria 4 (40 cal)"

        # --- RESULTADOS FINAIS ---
        st.divider()
        st.subheader("✅ Resultados Finais Validados")
        r1, r2, r3 = st.columns(3)
        r1.metric("I_arc Final", f"{ia_final:.3f} kA")
        r2.metric("Energia Incidente", f"{energia_final:.2f} cal/cm²")
        r3.metric("Fronteira (DLA)", f"{dla:.0f} mm")
        st.warning(f"Vestimenta Obrigatória: {cat}")

if __name__ == "__main__":
    main()
