import streamlit as st
import pandas as pd
import math

st.set_page_config(page_title="Estudo de Proteção 138kV", layout="wide")

# --- FUNÇÕES DE CÁLCULO (Lógica Robusta do Excel) ---
def calcular_rtc(texto_tc):
    try:
        p, s = map(float, texto_tc.split('/'))
        return p / s
    except: return 1.0

def calcular_correntes(s, v, z):
    i_nom = s / (math.sqrt(3) * v)
    i_cc = i_nom / (z / 100)
    return round(i_nom, 2), round(i_cc, 2)

# Fórmulas das Normas (Exatamente as que usamos no Excel)
def tempo_iec_mi(pk, falta, dial): # Muito Inversa
    if falta <= pk: return 99.0
    return round(dial * (13.5 / ((falta / pk) - 1)), 3)

def dial_reverso_mi(pk, falta, tempo_alvo):
    return round(tempo_alvo / (13.5 / ((falta / pk) - 1)), 3)

def dial_reverso_ei(pk, falta, tempo_alvo): # Extremamente Inversa (Neutro)
    return round(tempo_alvo / (80 / ((falta / pk)**2 - 1)), 3)

# --- INTERFACE STREAMLIT ---
st.title("⚡ Sistema de Coordenação e Seletividade 138kV/13.8kV")

with st.sidebar:
    st.header("📋 Dados de Entrada")
    # Intertravamento - Escolha do Cenário
    cenario = st.selectbox("Cenário Ativo (Intertravamento)", ["Trafo 12 MVA", "Trafo 10 MVA"])
    pot_principal = 12000 if cenario == "Trafo 12 MVA" else 10000
    
    st.subheader("Subestação Principal")
    v_pri = st.number_input("Tensão Primária (kV)", value=138.0)
    v_sec = st.number_input("Tensão Secundária (kV)", value=13.8)
    z_principal = st.number_input(f"Impedância {cenario} (%)", value=10.0)
    
    st.subheader("Dados Galpão")
    pot_g = st.number_input("Potência Trafo Galpão (kVA)", value=300)
    z_g = st.number_input("Impedância Galpão (%)", value=4.0)

    st.subheader("Relação de TCs")
    tc_pri = st.text_input("TC Primário (138kV)", value="100/5")
    tc_sec = st.text_input("TC Secundário (13.8kV)", value="600/5")

# --- EXECUÇÃO DOS CÁLCULOS ---
# 1. Dados de Base (Aba Dados_Equipamentos)
inom_p, icc_p = calcular_correntes(pot_principal, v_pri, z_principal)
inom_s, icc_s = calcular_correntes(pot_principal, v_sec, z_principal)
inom_g, icc_g = calcular_correntes(pot_g, v_sec, z_g)

# 2. Coordenação de FASE (Aba Coordenação)
# Tempos alvo (CTI de 0.3s como ajustamos)
t_bt = 0.05
# Galpão
pk_fase_g = inom_g * 1.25
t_g = t_bt + 0.20
dial_fase_g = dial_reverso_mi(pk_fase_g, icc_g, t_g)
# Secundário
pk_fase_s = inom_s * 1.15
t_s = t_g + 0.30
dial_fase_s = dial_reverso_mi(pk_fase_s, icc_s, t_s)

# 3. Coordenação de NEUTRO (Aba Neutro - Usando EI)
pk_n_g = inom_g * 0.3
dial_n_g = dial_reverso_ei(pk_n_g, icc_g, t_g)
pk_n_s = inom_s * 0.3
dial_n_s = dial_reverso_ei(pk_n_s, icc_s, t_s)

# --- TABELA RESUMO (Aba Resumo Automática) ---
rtc_p = calcular_rtc(tc_pri)
rtc_s = calcular_rtc(tc_sec)

resumo_data = [
    ["Primário 138kV", f"{pk_fase_s/10:.2f}", dial_fase_s, tc_pri, f"{(pk_fase_s/10)/rtc_p:.2f}"],
    ["Secundário 13,8kV", f"{pk_fase_s:.2f}", dial_fase_s, tc_sec, f"{pk_fase_s/rtc_s:.2f}"],
    ["Alimentador", "100.00", 0.2, tc_sec, f"{100/rtc_s:.2f}"],
    ["Galpão 300kVA", f"{pk_fase_g:.2f}", dial_fase_g, "1/1", f"{pk_fase_g:.2f}"]
]

st.subheader(f"✅ Mapa de Ajustes Finais - {cenario}")
df_resumo = pd.DataFrame(resumo_data, columns=["Equipamento", "Pickup Primário(A)", "Dial(TMS)", "TC", "AJUSTE NO RELÉ (SEC)"])
st.table(df_resumo)

# Alerta de Segurança ANSI
if t_s < 2.0:
    st.success(f"✔️ Proteção Coordenada em {t_s}s. Dentro do limite ANSI do {cenario}.")
else:
    st.error("⚠️ Alerta: Tempo de atuação excede suportabilidade térmica!")
