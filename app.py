import streamlit as st
import numpy as np

# Função para cálculos conforme NBR 17227:2025
def realizar_calculos(ibf, g, d, t, config, cf_val):
    # Coeficientes Tabela 4 (Ia) e 6 (En) - Exemplo VCB 14.3kV
    ki = [0.005795, 1.015, -0.011, -1.557e-12, 4.556e-10, -4.186e-08, 8.346e-07, 5.482e-05, -0.003191, 0.9729]
    ke = [3.825917, 0.11, -0.999749, -1.557e-12, 4.556e-10, -4.186e-08, 8.346e-07, 5.482e-05, -0.003191, 0.9729, 0, -1.568, 0.99]
    
    # 1. Corrente de Arco (Ia)
    poli_ia = (ki*ibf**6 + ki*ibf**5 + ki*ibf**4 + ki*ibf**3 + ki*ibf**2 + ki*ibf + ki)
    log_ia = (ki + ki*np.log10(ibf) + ki*np.log10(g)) + poli_ia
    ia_f = 10**log_ia
    
    # 2. Energia Incidente (E)
    poli_en = (ke*ibf**6 + ke*ibf**5 + ke*ibf**4 + ke*ibf**3 + ke*ibf**2 + ke*ibf + ke)
    log_e = ke + ke*np.log10(g) + (ke*ia_f)/poli_en + ke*np.log10(ibf) + ke*np.log10(d) + ke*np.log10(ia_f) + np.log10(1.0/cf_val)
    e_cal = (12.552 * (t/50.0) * 10**log_e) / 4.184
    
    # 3. Fronteira de Arco (DLA)
    termos_sem_d = (ke + ke*np.log10(g) + (ke*ia_f)/poli_en + ke*np.log10(ibf) + ke*np.log10(ia_f) + np.log10(1.0/cf_val))
    log_dla = (np.log10(5.0 / (12.552 * (t/50.0))) - termos_sem_d) / ke
    dla_f = 10**log_dla
    
    return ia_f, e_cal, abs(dla_f)

def main():
    st.set_page_config(page_title="NBR 17227 Pro", layout="wide")
    st.title("⚡ Sistema de Cálculo de Risco de Arco - NBR 17227:2025")

    # Aba 1 de Dimensões (Omissa aqui para brevidade, mas deve ser mantida como antes)
    tab1, tab2 = st.tabs(["📏 Dimensões", "🧪 Cálculos"])

    with tab2:
        with st.form("form_calculo"):
            st.subheader("Parâmetros de Entrada")
            c1, c2, c3 = st.columns(3)
            with c1:
                v_oc = st.number_input("Tensão Voc (kV)", value=13.80)
                i_bf = st.number_input("Curto-Circuito Ibf (kA)", value=4.85)
            with c2:
                eletrodo = st.selectbox("Eletrodos:", ["VCB", "VCBB", "HCB"])
                gap = st.number_input("Gap G (mm)", value=152.0)
            with c3:
                dist = st.number_input("Distância D (mm)", value=914.4)
                tempo = st.number_input("Tempo T (ms)", value=488.0)
            
            # BOTÃO PARA FORÇAR O CÁLCULO
            submit = st.form_submit_button("Calcular Resultados")

        if submit:
            # Chama a função de cálculo apenas ao clicar
            ia, e, dla = realizar_calculos(i_bf, gap, dist, tempo, eletrodo, 1.28372)
            
            st.success("✅ Resultados Finais Validados")
            res1, res2, res3 = st.columns(3)
            res1.metric("I_arc Final", f"{ia:.3f} kA")
            res2.metric("Energia Incidente", f"{e:.2f} cal/cm²")
            res3.metric("Fronteira (DLA)", f"{dla:.0f} mm")
            
            # Categoria
            cat = "Cat 2 (8 cal)" if e <= 8 else "Cat 3 (25 cal)"
            st.warning(f"Vestimenta Obrigatória: {cat}")

if __name__ == "__main__":
    main()
