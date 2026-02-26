import streamlit as st
import numpy as np
def main():
st.set_page_config(page_title="Calculadora NBR 17227", layout="wide")
st.title("⚡ Gestão de Risco de Arco Elétrico - NBR 17227:2025")
tab1, tab2 = st.tabs(["📏 Dimensões e Invólucros (Tabela 1)", "🧪 Corrente de Arco (Tabela 4)"])
# --- ABA 1: CONSULTA DE EQUIPAMENTOS (Tabela 1 NBR 17227) ---
with tab1:
st.header("Classes de Equipamentos e Espaçamentos Típicos")
# Dados conforme Tabela 1 da NBR 17227:2025
dados_inv = {
"CCM 15 kV": [152, "914,4", "914,4", "914,4"],
"Conjunto de manobra 15 kV": [152, "1143", "762", "762"],
"CCM 5 kV": [104, "660,4", "660,4", "660,4"],
"Conjunto de manobra 5 kV (Opção 1)": [104, "914,4", "914,4", "914,4"],
"Conjunto de manobra 5 kV (Opção 2)": [104, "1143", "762", "762"],
"CCM e painel rasos de BT": [25, "355,6", "304,8", "≤203,2"],
"CCM e painel típico de BT": [25, "355,6", "304,8", ">203,2"],
"Conjunto de manobra BT": [32, "508", "508", "508"],
"Caixa de junção de cabos": [13, "355,6", "304,8", "Var."]
}
escolha = st.selectbox("Selecione o Equipamento para consulta:", list(dados_inv.keys()))
if escolha:
info = dados_inv[escolha]
c1, c2, c3, c4 = st.columns(4)
c1.metric("GAP Típico (G)", f"{info[0]} mm")
c2.metric("Altura (A)", f"{info[1]} mm")
c3.metric("Largura (L)", f"{info[2]} mm")
c4.metric("Profundidade (P)", f"{info[3]} mm")
# --- ABA 2: CÁLCULO DE ARCO (Tabela 4 e Equação 1) ---
with tab2:
st.header("Cálculo de Correntes de Arco Intermediárias")
# Dicionário COMPLETO com os 10 coeficientes (k1 a k10) da Tabela 4 da NBR 17227
coefs_nbr = {
"VCB": {
600: [-0.04287, 1.035, -0.083, 0, 0, -4.783e-09, 1.962e-06, -0.000229, 0.003141, 1.092],
2700: [0.0065, 1.001, -0.024, -1.557e-12, 4.556e-10, -4.186e-08, 8.346e-07, 5.482e-05, -0.003191, 0.9729],
14300: [0.005795, 1.015, -0.011, -1.557e-12, 4.556e-10, -4.186e-08, 8.346e-07, 5.482e-05, -0.003191, 0.9729]
},
"VCBB": {
600: [-0.017432, 0.98, -0.05, 0, 0, -5.767e-09, 2.542e-06, -0.00034, 0.01187, 1.013],
2700: [0.002823, 0.995, -0.0125, 0, -9.200e-11, 2.901e-08, -3.262e-06, 0.0001569, -0.004003, 0.9825],
14300: [0.014827, 1.01, -0.01, 0, -9.200e-11, 2.901e-08, -3.262e-06, 0.0001569, -0.004003, 0.9825]
},
"HCB": {
600: [0.054922, 0.988, -0.11, 0, 0, -5.382e-09, 2.316e-06, -0.000302, 0.0091, 0.9725],
2700: [0.001011, 1.003, -0.0249, 0, 0, 4.859e-10, -1.814e-07, -9.128e-06, -0.0007, 0.9881],
14300: [0.008693, 0.999, -0.02, 0, -5.040e-11, 2.233e-08, -3.046e-06, 0.000116, -0.001145, 0.9839]
},
"VOA": {
600: [0.043785, 1.04, -0.18, 0, 0, -4.783e-09, 1.962e-06, -0.000229, 0.003141, 1.092],
2700: [-0.02395, 1.006, -0.0188, -1.557e-12, 4.556e-10, -4.186e-08, 8.346e-07, 5.482e-05, -0.003191, 0.9729],
14300: [0.005371, 1.010, -0.029, -1.557e-12, 4.556e-10, -4.186e-08, 8.346e-07, 5.482e-05, -0.003191, 0.9729]
},
"HOA": {
600: [0.111147, 1.008, -0.24, 0, 0, -3.895e-09, 1.641e-06, -0.000197, 0.002615, 1.1],
2700: [0.000435, 1.006, -0.038, 0, 0, 7.859e-10, -1.914e-07, -9.128e-06, -0.0007, 0.9981],
14300: [0.000904, 0.999, -0.02, 0, 0, 7.859e-10, -1.914e-07, -9.128e-06, -0.0007, 0.9981]
}
}
col_in1, col_in2 = st.columns(2)
with col_in1:
v_oc = st.number_input("Tensão do Sistema Voc (kV)", 0.208, 15.0, 13.8)
i_bf = st.number_input("Corrente de Falta Franca Ibf (kA)", 0.5, 106.0, 20.0)
with col_in2:
config = st.selectbox("Configuração dos Eletrodos:", list(coefs_nbr.keys()))
gap = st.number_input("Gap entre Eletrodos G (mm)", value=float(info[0]) if 'info' in locals() else 25.0)
# EQUAÇÃO 1 da NBR 17227:2025
def calcular_ia(ibf, g, k):
# Parte do logaritmo: (k1 + k2log10(Ibf) + k3log10(G))
log_base = k[0] + k[1]np.log10(ibf) + k[2]np.log10(g)
# Parte polinomial: (k4Ibf^6 + k5Ibf^5 + k6Ibf^4 + k7Ibf^3 + k8Ibf^2 + k9Ibf + k10)
poli = (k[3]*ibf6 + k[4]*ibf5 + k[5]*ibf4 + k[6]*ibf3 + k[7]*ibf*2 + k[8]ibf + k[9])
return 10(log_base * poli)
# Cálculo das correntes para os 3 níveis
ia_600 = calcular_ia(i_bf, gap, coefs_nbr[config][600])
ia_2700 = calcular_ia(i_bf, gap, coefs_nbr[config][2700])
ia_14300 = calcular_ia(i_bf, gap, coefs_nbr[config][14300])
# Interpolação Final (Equações 16 a 20)
if v_oc <= 0.6:
ia_final = ia_600
elif v_oc <= 2.7:
ia_final = ia_600 + (ia_2700 - ia_600) * (v_oc - 0.6) / (2.7 - 0.6)
else:
ia_final = ia_2700 + (ia_14300 - ia_2700) * (v_oc - 2.7) / (14.3 - 2.7)
st.divider()
st.subheader("Resultados - Correntes de Arco (kA)")
r1, r2, r3, r_final = st.columns(4)
r1.metric("I_arc @ 600V", f"{ia_600:.3f}")
r2.metric("I_arc @ 2700V", f"{ia_2700:.3f}")
r3.metric("I_arc @ 14300V", f"{ia_14300:.3f}")
r_final.metric("CORRENTE FINAL (I_arc)", f"{ia_final:.3f} kA")
if name == "main":
main()
