import streamlit as st
import numpy as np

# 1. Função de Cálculo com Matemática Escalar (Evita o TypeError)
def realizar_calculos(ibf, g, d, t, config, cf_val):
    # Coeficientes Tabela 4 (Ia) e 6 (En) - Exemplo VCB 14.3kV
    # [k1, k2, k3, k4, k5, k6, k7, k8, k9, k10]
    ki = [0.005795, 1.015, -0.011, -1.557e-12, 4.556e-10, -4.186e-08, 8.346e-07, 5.482e-05, -0.003191, 0.9729]
    # [k1...k10, k11, k12, k13]
    ke = [3.825917, 0.11, -0.999749, -1.557e-12, 4.556e-10, -4.186e-08, 8.346e-07, 5.482e-05, -0.003191, 0.9729, 0, -1.568, 0.99]
    
    # Cálculo da Corrente de Arco (Ia) - Usando índices ki[0], ki[1]...
    poli_ia = (ki[3]*ibf**6 + ki[4]*ibf**5 + ki[5]*ibf**4 + ki[6]*ibf**3 + ki[7]*ibf**2 + ki[8]*ibf + ki[9])
    log_ia = (ki[0] + ki[1]*np.log10(ibf) + ki[2]*np.log10(g)) + poli_ia
    ia_f = 10**log_ia
    
    # Cálculo da Energia Incidente (E) em cal/cm²
    poli_en = (ke[3]*ibf**6 + ke[4]*ibf**5 + ke[5]*ibf**4 + ke[6]*ibf**3 + ke[7]*ibf**2 + ke[8]*ibf + ke[9])
    log_e = ke[0] + ke[1]*np.log10(g) + (ke[2]*ia_f)/poli_en + ke[10]*np.log10(ibf) + ke[11]*np.log10(d) + ke[12]*np.log10(ia_f) + np.log10(1.0/cf_val)
    e_cal = (12.552 * (t/50.0) * 10**log_e) / 4.184
    
    # Cálculo da Fronteira de Arco (DLA) para 1.2 cal/cm²
    termos_sem_d = (ke[0] + ke[1]*np.log10(g) + (ke[2]*ia_f)/poli_en + ke[10]*np.log10(ibf) + ke[12]*np.log10(ia_f) + np.log10(1.0/cf_val))
    log_dla = (np.log10(5.0 / (12.552 * (t/50.0))) - termos_sem_d) / ke[11]
    dla_f = 10**log_dla
    
    return ia_f, e_cal, abs(dla_f)

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

    tab1, tab2 = st.tabs(["📏 Dimensões", "🧪 Cálculos"])

    with tab1:
        st.header("Tabela 1: Dimensões de Invólucros")
        escolha = st.selectbox("Equipamento:", list(dados_inv.keys()), key="sel_tab1")
        info = dados_inv[escolha]
        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("GAP", f"{info[0]} mm"); c2.metric("Distância D", f"{info[1]} mm")
        c3.metric("Altura", f"{info[2]} mm"); c4.metric("Largura", f"{info[3]} mm"); c5.metric("Profundidade", f"{info[4]} mm")

    with tab2:
        with st.form("form_arco"):
            st.subheader("Parâmetros de Entrada")
            col1, col2, col3 = st.columns(3)
            with col1:
                v_oc = st.number_input("Tensão Voc (kV)", value=13.80)
                i_bf = st.number_input("Curto-Circuito Ibf (kA)", value=4.85)
            with col2:
                eletrodo = st.selectbox("Eletrodos:", ["VCB", "VCBB", "HCB"])
                gap = st.number_input("Gap G (mm)", value=float(info[0]))
            with col3:
                dist = st.number_input("Distância D (mm)", value=float(info[1]))
                tempo = st.number_input("Tempo T (ms)", value=488.0)
            
            submit = st.form_submit_button("Calcular Resultados")

        if submit:
            # CF conforme seu Excel
            ia, e, dla = realizar_calculos(i_bf, gap, dist, tempo, eletrodo, 1.28372)
            
            st.divider()
            st.subheader("📊 Resultados Finais")
            res1, res2, res3 = st.columns(3)
            res1.metric("Corrente de Arco (Ia)", f"{ia:.5f} kA")
            res2.metric("Energia Incidente (E)", f"{e:.5f} cal/cm²")
            res3.metric("Fronteira (DLA)", f"{dla:.1f} mm")
            
            # Classificação EPI
            cat = "Cat 2 (8 cal)" if e <= 8 else ("Cat 4 (40 cal)" if e <= 40 else "PERIGO")
            st.warning(f"**Vestimenta recomendada:** {cat}")

if __name__ == "__main__":
    main()
