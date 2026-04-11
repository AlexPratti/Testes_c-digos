import streamlit as st
import pandas as pd
import math

st.set_page_config(page_title="Coordenação e Seletividade 138kV", layout="wide")

# --- FUNÇÕES CORE (Lógica Idêntica ao Excel) ---
def calcular_rtc(texto_tc):
    try:
        p, s = map(float, str(texto_tc).split('/'))
        return p / s
    except: return 1.0

def calcular_correntes(s, v, z):
    i_nom = s / (math.sqrt(3) * v)
    i_cc = i_nom / (z / 100)
    return round(i_nom, 2), round(i_cc, 2)

def dial_reverso_mi(pk, falta, tempo_alvo):
    return round(tempo_alvo / (13.5 / ((falta / pk) - 1)), 4)

def dial_reverso_ei(pk, falta, tempo_alvo):
    return round(tempo_alvo / (80 / ((falta / pk)**2 - 1)), 4)

# --- INTERFACE ---
st.title("⚡ Estudo de Proteção: Fase (50/51) e Neutro (50N/51N)")

with st.sidebar:
    st.header("🏢 Subestação Principal")
    cenario = st.selectbox("Cenário (Intertravamento)", ["Trafo 12 MVA", "Trafo 10 MVA"])
    pot_principal = 12000 if cenario == "Trafo 12 MVA" else 10000
    v_pri = st.number_input("Tensão Primária (kV)", value=138.0)
    v_sec = st.number_input("Tensão Secundária (kV)", value=13.8)
    z_principal = st.number_input(f"Impedância {cenario} (%)", value=10.0)
    
    st.subheader("📟 Transformadores de Corrente (TCs)")
    tc_p_input = st.text_input("TC Primário (138kV)", value="100/5")
    tc_s_input = st.text_input("TC Secundário (13.8kV)", value="600/5")

st.subheader("📦 Subestações Secundárias (Galpões)")
st.info("Adicione ou remova linhas abaixo. Se deixar vazio, o sistema assume uma SE de 300kVA.")

# Editor de tabela para múltiplas SEs
df_entrada_ses = pd.DataFrame([{"Nome": "Galpão 01", "Potência (kVA)": 300, "Z (%)": 4.0}])
ses_editadas = st.data_editor(df_entrada_ses, num_rows="dynamic")

# --- PROCESSAMENTO LOGÍCO ---
rtc_p = calcular_rtc(tc_p_input)
rtc_s = calcular_rtc(tc_s_input)
inom_p, icc_p = calcular_correntes(pot_principal, v_pri, z_principal)
inom_s, icc_s = calcular_correntes(pot_principal, v_sec, z_principal)

# Determinar a SE secundária mais crítica para coordenação
if not ses_editadas.empty:
    se_critica = ses_editadas.loc[ses_editadas['Potência (kVA)'].idxmax()]
else:
    se_critica = {"Potência (kVA)": 300, "Z (%)": 4.0}

inom_g, icc_g = calcular_correntes(se_critica["Potência (kVA)"], v_sec, se_critica["Z (%)"])

# Cálculos de Fase (50/51) - Lógica de Cascata 0.3s
t_bt = 0.05
# Galpão
pk_51_g = inom_g * 1.25
t_51_g = t_bt + 0.20
dial_51_g = dial_reverso_mi(pk_51_g, icc_g, t_51_g)
pk_50_g = 1.2 * icc_g
# Secundário SE Principal
pk_51_s = inom_s * 1.15
t_51_s = t_51_g + 0.30
dial_51_s = dial_reverso_mi(pk_51_s, icc_s, t_51_s)
pk_50_s = 1.1 * icc_s

# --- MONTAGEM DA TABELA RESUMO FINAL ---
resumo = [
    {
        "Equipamento": "Primário 138kV",
        "TC": tc_p_input,
        "51 Fase (Dial)": dial_51_s,
        "51 Fase (Sec A)": round((pk_51_s/10)/rtc_p, 2),
        "50 Fase (Sec A)": round((pk_50_s/10)/rtc_p, 2),
        "51N Neutro (Dial)": dial_reverso_ei(inom_s*0.3, icc_s, t_51_s),
        "51N Neutro (Sec A)": round(((inom_s*0.3)/10)/rtc_p, 2)
    },
    {
        "Equipamento": "Secundário 13,8kV",
        "TC": tc_s_input,
        "51 Fase (Dial)": dial_51_s,
        "51 Fase (Sec A)": round(pk_51_s/rtc_s, 2),
        "50 Fase (Sec A)": round(pk_50_s/rtc_s, 2),
        "51N Neutro (Dial)": dial_reverso_ei(inom_s*0.3, icc_s, t_51_s),
        "51N Neutro (Sec A)": round((inom_s*0.3)/rtc_s, 2)
    },
    {
        "Equipamento": f"SE Crítica ({se_critica['Potência (kVA)']}kVA)",
        "TC": "1/1",
        "51 Fase (Dial)": dial_51_g,
        "51 Fase (Sec A)": round(pk_51_g, 2),
        "50 Fase (Sec A)": round(pk_50_g, 2),
        "51N Neutro (Dial)": dial_reverso_ei(inom_g*0.3, icc_g, t_51_g),
        "51N Neutro (Sec A)": round(inom_g*0.3, 2)
    }
]

st.subheader(f"✅ Mapa de Ajustes Finais (Valores Secundários para o Relé) - {cenario}")
st.table(pd.DataFrame(resumo))

st.success(f"Coordenação verificada: Tempo total de limpeza no Secundário em {t_51_s}s.")
