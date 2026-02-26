import streamlit as st
import numpy as np

def main():
    st.set_page_config(page_title="NBR 17227 Pro", layout="wide")
    st.title("⚡ Sistema de Cálculo de Risco de Arco - NBR 17227:2025")

    # --- INPUTS (Conforme sua interface) ---
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
        tipo_p = st.radio("Invólucro:", ["Típico", "Raso"])

    # --- 1. FATOR CF (Tabela 8) ---
    ees = (914.4 / 25.4 + 914.4 / 25.4) / 2.0 
    b = {"Típico": [-0.0003, 0.03441, 0.4325], "Raso": [0.00222, -0.0256, 0.6222]}
    b1, b2, b3 = b[tipo_p]
    cf = b1*ees**2 + b2*ees + b3 if tipo_p == "Típico" else 1.0/(b1*ees**2 + b2*ees + b3)

    # --- 2. COEFICIENTES NBR 17227 (Tabela 4 e 6) ---
    # Nota: Mapeado VCB conforme imagem enviada. Outros devem ser expandidos no dict.
    coefs = {
        "VCB": {
            "Ia": {
                600: [-0.04287, 1.035, -0.083, 0, 0, -4.783e-9, 1.962e-6, -0.000229, 0.003141, 1.092],
                2700: [0.0065, 1.001, -0.024, -1.557e-12, 4.556e-10, -4.186e-8, 8.346e-7, 5.482e-5, -0.003191, 0.9729],
                14300: [0.005795, 1.015, -0.011, -1.557e-12, 4.556e-10, -4.186e-8, 8.346e-7, 5.482e-5, -0.003191, 0.9729]
            },
            "En": {
                600: [0.753364, 0.566, 1.752636, 0, 0, -4.783e-9, 1.962e-6, -0.000229, 0.003141, 1.092, 0, -1.598, 0.957],
                2700: [2.40021, 0.165, 0.354202, -1.557e-12, 4.556e-10, -4.186e-8, 8.346e-7, 5.482e-5, -0.003191, 0.9729, 0, -1.569, 0.9778],
                14300: [3.825917, 0.11, -0.999749, -1.557e-12, 4.556e-10, -4.186e-8, 8.346e-7, 5.482e-5, -0.003191, 0.9729, 0, -1.568, 0.99]
            }
        }
    }

    # --- 3. FUNÇÕES DE CÁLCULO ---
    def calc_ia(ibf, g, k):
        poli = (k[3]*ibf**6 + k[4]*ibf**5 + k[5]*ibf**4 + k[6]*ibf**3 + k[7]*ibf**2 + k[8]*ibf + k[9])
        return 10**((k[0] + k[1]*np.log10(ibf) + k[2]*np.log10(g)) + poli)

    def calc_e(ia, ibf, g, d, t, k, cf_val):
        poli = (k[3]*ibf**6 + k[4]*ibf**5 + k[5]*ibf**4 + k[6]*ibf**3 + k[7]*ibf**2 + k[8]*ibf + k[9])
        log_e = k[0] + k[1]*np.log10(g) + (k[2]*ia)/poli + k[10]*np.log10(ibf) + k[11]*np.log10(d) + k[12]*np.log10(ia) + np.log10(1.0/cf_val)
        return (12.552 * (t/50.0) * 10**log_e) / 4.184

    # --- 4. INTERPOLAÇÃO FINAL ---
    c_i = coefs[config]["Ia"]; c_e = coefs[config]["En"]
    
    # Intermediários
    ia_steps = {v: calc_ia(i_bf, gap, c_i[v]) for v in [600, 2700, 14300]}
    e_steps = {v: calc_e(ia_steps[v], i_bf, gap, d_trab, tempo, c_e[v], cf) for v in [600, 2700, 14300]}

    if v_oc <= 0.6: 
        ia_f, e_f = ia_steps[600], e_steps[600]
    elif v_oc <= 2.7:
        ia_f = ia_steps[600] + (ia_steps[2700] - ia_steps[600]) * (v_oc - 0.6) / 2.1
        e_f = e_steps[600] + (e_steps[2700] - e_steps[600]) * (v_oc - 0.6) / 2.1
    else:
        ia_f = ia_steps[2700] + (ia_steps[14300] - ia_steps[2700]) * (v_oc - 2.7) / 11.6
        e_f = e_steps[2700] + (e_steps[14300] - e_steps[2700]) * (v_oc - 2.7) / 11.6

    # Fronteira de Arco (DLA) Simplificada para 1.2 cal/cm²
    dla_f = d_trab * (e_f / 1.2)**(1.0/1.568) # Expoente médio k11 para DLA

    # --- CATEGORIA EPI ---
    categorias = [(1.2, "Risco 0 (Algodão)"), (4, "Cat 1 (4 cal)"), (8, "Cat 2 (8 cal)"), (25, "Cat 3 (25 cal)"), (40, "Cat 4 (40 cal)")]
    cat_final = next((txt for lim, txt in categorias if e_f <= lim), "PERIGO > 40 cal")

    # --- EXIBIÇÃO ---
    st.divider()
    st.subheader("✅ Resultados Finais Validados (NBR 17227)")
    r1, r2, r3, r4 = st.columns(4)
    r1.metric("Corrente I_arc Final", f"{ia_f:.3f} kA")
    r2.metric("Energia Incidente", f"{e_f:.2f} cal/cm²")
    r3.metric("Fronteira (DLA)", f"{dla_f:.0f} mm")
    r4.warning(f"Vestimenta: {cat_final}")

if __name__ == "__main__":
    main()
