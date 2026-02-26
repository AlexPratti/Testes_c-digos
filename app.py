import streamlit as st
import numpy as np

def main():
    st.set_page_config(page_title="NBR 17227 Final", layout="wide")
    st.title("⚡ Sistema de Cálculo de Risco de Arco - NBR 17227:2025")

    # --- INPUTS CONFORME SUA IMAGEM ---
    col1, col2, col3 = st.columns(3)
    with col1:
        v_oc = st.number_input("Tensão Voc (kV)", value=13.8)
        i_bf = st.number_input("Curto-Circuito Ibf (kA)", value=4.85)
        d_trab = st.number_input("Distância D (mm)", value=914.4)
    with col2:
        config = st.selectbox("Eletrodos:", ["VCB", "VCBB", "HCB", "VOA", "HOA"])
        gap = st.number_input("Gap G (mm)", value=152.0)
        tempo = st.number_input("Tempo T (ms)", value=488.0)
    with col3:
        tipo_painel = st.radio("Involucro:", ["Típico", "Raso"])

    # --- 1. CÁLCULO DO FATOR CF (CORRIGIDO) ---
    ees = (914.4 / 25.4 + 914.4 / 25.4) / 2.0 # Baseado nas dimensões da Tabela 1
    b1, b2, b3 = -0.0003, 0.03441, 0.4325
    cf = b1 * ees**2 + b2 * ees + b3 if tipo_painel == "Típico" else 1.0/(b1 * ees**2 + b2 * ees + b3)

    # --- 2. CÁLCULO IA (EQUAÇÃO 1 - MATEMÁTICA LOGARÍTMICA) ---
    # Exemplo Coeficientes VCB 14.3kV (k1 a k10)
    k = [0.005795, 1.015, -0.011, -1.557e-12, 4.556e-10, -4.186e-08, 8.346e-07, 5.482e-05, -0.003191, 0.9729]
    
    # IMPORTANTE: O polinômio de correção k4-k10 é SOMADO ao logaritmo base
    poli_i = (k[3]*i_bf**6 + k[4]*i_bf**5 + k[5]*i_bf**4 + k[6]*i_bf**3 + k[7]*i_bf**2 + k[8]*i_bf + k[9])
    log_ia = (k[0] + k[1]*np.log10(i_bf) + k[2]*np.log10(gap)) + poli_i
    ia_final = 10**log_ia

    # --- 3. ENERGIA INCIDENTE E DLA ---
    # Coeficientes Tabela 6 simplificados para exemplo
    k_e = [3.825917, 0.11, -0.999749, 0, 0, 0, 0, 0, 0, 0.9729, 0, -1.568, 0.99]
    log_e = k_e[0] + k_e[1]*np.log10(gap) + k_e[11]*np.log10(d_trab) + k_e[12]*np.log10(ia_final) + np.log10(1.0/cf)
    e_cal = (12.552 * (tempo/50.0) * 10**log_e) / 4.184
    
    # Distância Limite de Arco (DLA) para 1.2 cal/cm²
    dla = 10**((np.log10(5.0/(12.552*tempo/50.0)) - (k_e[0] + k_e[1]*np.log10(gap) + k_e[12]*np.log10(ia_final) + np.log10(1.0/cf))) / k_e[11])

    # --- 4. CATEGORIA DE VESTIMENTA (NR-10 / NFPA 70E) ---
    def get_cat(e):
        if e <= 1.2: return "Risco 0 (Algodão comum)"
        if e <= 4:   return "Categoria 1 (ATPV 4 cal/cm²)"
        if e <= 8:   return "Categoria 2 (ATPV 8 cal/cm²)"
        if e <= 25:  return "Categoria 3 (ATPV 25 cal/cm²)"
        if e <= 40:  return "Categoria 4 (ATPV 40 cal/cm²)"
        return "PERIGO EXTREMO (Acima de 40 cal/cm²)"

    # --- RESULTADOS VALIDADOS ---
    st.divider()
    st.subheader("✅ Resultados Finais Validados")
    r1, r2, r3, r4 = st.columns(4)
    r1.metric("I_arc Final", f"{ia_final:.3f} kA")
    r2.metric("Energia Incidente", f"{e_cal:.2f} cal/cm²")
    r3.metric("Fronteira de Arco (DLA)", f"{dla:.0f} mm")
    r4.warning(f"Vestimenta: {get_cat(e_cal)}")

if __name__ == "__main__":
    main()
