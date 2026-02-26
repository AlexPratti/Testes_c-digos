import streamlit as st
import numpy as np

def main():
    st.set_page_config(page_title="Calculadora NBR 17227 Corrigida", layout="wide")
    st.title("⚡ Calculadora de Arco Elétrico - NBR 17227:2025")
    
    # --- ENTRADAS (Conforme sua imagem) ---
    col1, col2, col3 = st.columns(3)
    with col1:
        v_oc = st.number_input("Tensão Voc (kV)", value=0.38, step=0.01)
        i_bf = st.number_input("Curto-Circuito Ibf (kA)", value=20.0, step=1.0)
        d_trabalho = st.number_input("Distância de Trabalho D (mm)", value=914.4)
    with col2:
        config = st.selectbox("Configuração dos Eletrodos:", ["VCB", "VCBB", "HCB", "VOA", "HOA"])
        gap = st.number_input("Gap G (mm)", value=104.0)
        tempo = st.number_input("Duração do Arco T (ms)", value=100.0)
    with col3:
        tipo_painel = st.radio("Tipo de Compartimento:", ["Típico", "Raso"])

    # --- COEFICIENTES TÉCNICOS (Exemplo VCB para < 600V) ---
    # Nota: Para precisão total, mapear todos os k da Tabela 4 e 6 da norma
    k_corrente = [-0.04287, 1.035, -0.083, 0, 0, -4.783e-09, 1.962e-06, -0.000229, 0.003141, 1.092]
    k_energia = [0.753364, 0.566, 1.752636, 0, 0, -4.783e-09, 1.962e-06, -0.000229, 0.003141, 1.092, 0, -1.598, 0.957]

    # --- LOGICA DE CÁLCULO CORRIGIDA ---
    def calcular_i_arc(ibf, g, k):
        # O polinômio de correção DEVE ser somado ao logaritmo base
        polinomio = (k[3]*ibf**6 + k[4]*ibf**5 + k[5]*ibf**4 + k[6]*ibf**3 + k[7]*ibf**2 + k[8]*ibf + k[9])
        log_ia = k[0] + k[1]*np.log10(ibf) + k[2]*np.log10(g) + polinomio
        return 10**log_ia

    def calcular_energia_cal(ia, ibf, g, t, d, k):
        # A distância 'd' e o gap 'g' na fórmula da norma costumam ser em mm, mas o log base 10 é sensível
        # Equação de energia corrigida para retornar cal/cm²
        polinomio = (k[3]*ibf**6 + k[4]*ibf**5 + k[5]*ibf**4 + k[6]*ibf**3 + k[7]*ibf**2 + k[8]*ibf + k[9])
        # CF (Fator de invólucro) simplificado para 1.0 nesta revisão de erro
        log_e = k[0] + k[1]*np.log10(g) + polinomio + k[10]*np.log10(ibf) + k[11]*np.log10(d) + k[12]*np.log10(ia)
        e_jcm2 = 12.552 * (t/50.0) * 10**log_e
        return e_jcm2 / 4.184

    # Processamento
    i_arc_final = calcular_i_arc(i_bf, gap, k_corrente)
    energia_final = calcular_energia_cal(i_arc_final, i_bf, gap, tempo, d_trabalho, k_energia)
    
    # DLA (Aproximação: onde E = 1.2 cal/cm²)
    dla_final = d_trabalho * (energia_final / 1.2)**(1/k_energia[11])

    # --- RESULTADOS ---
    st.divider()
    st.subheader("📊 RESULTADOS FINAIS (REVISADOS)")
    res1, res2, res3 = st.columns(3)
    res1.metric("Corrente de Arco (I_arc)", f"{i_arc_final:.3f} kA")
    res2.metric("Energia Incidente (E)", f"{energia_final:.4f} cal/cm²")
    res3.metric("Distância Limite de Arco (DLA)", f"{abs(dla_final):.1f} mm")

if __name__ == "__main__":
    main()
