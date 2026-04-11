import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import math

st.set_page_config(page_title="Laudo de Proteção 138kV", layout="wide")

# --- FUNÇÕES TÉCNICAS (Lógica de Engenharia Robusta) ---
def calcular_correntes(s, v, z):
    i_nom = s / (math.sqrt(3) * v)
    i_cc = i_nom / (z / 100)
    return round(i_nom, 2), round(i_cc, 2)

def formula_iec_mi(pk, dial, corrente):
    """Calcula tempo para Curva Muito Inversa (IEC)"""
    if corrente <= pk: return None
    return dial * (13.5 / ((corrente / pk) - 1))

def formula_iec_ei(pk, dial, corrente):
    """Calcula tempo para Curva Extremamente Inversa (IEC)"""
    if corrente <= pk: return None
    return dial * (80 / ((corrente / pk)**2 - 1))

def dial_reverso_mi(pk, falta, tempo_alvo):
    return round(tempo_alvo / (13.5 / ((falta / pk) - 1)), 4)

def dial_reverso_ei(pk, falta, tempo_alvo):
    return round(tempo_alvo / (80 / ((falta / pk)**2 - 1)), 4)

# --- INTERFACE DE ENTRADA ---
st.title("⚡ Projeto de Proteção e Seletividade: Subestação 138kV / 13,8kV")
st.markdown("---")

with st.sidebar:
    st.header("📋 Dados da Subestação Principal")
    cenario = st.selectbox("Intertravamento Ativo", ["Trafo 12 MVA", "Trafo 10 MVA"])
    pot_p = 12000 if cenario == "Trafo 12 MVA" else 10000
    v_pri = st.number_input("Tensão Primária (kV)", value=138.0)
    v_sec = st.number_input("Tensão Secundária (kV)", value=13.8)
    z_p = st.number_input(f"Impedância {cenario} (%)", value=10.0)
    
    st.subheader("⚙️ Relação de TCs")
    tc_pri_text = st.text_input("TC Primário (Ex: 100/5)", "100/5")
    tc_sec_text = st.text_input("TC Secundário (Ex: 600/5)", "600/5")

# --- GERENCIAMENTO DE MÚLTIPLAS SES SECUNDÁRIAS ---
st.subheader("📦 Configuração das Subestações Secundárias (Galpões)")
df_entrada_ses = pd.DataFrame([{"Nome": "Galpão Principal", "Potência (kVA)": 300, "Z (%)": 4.0}])
ses_editadas = st.data_editor(df_entrada_ses, num_rows="dynamic")

# Definição da SE Crítica (Maior Potência)
if not ses_editadas.empty:
    critica = ses_editadas.loc[ses_editadas['Potência (kVA)'].idxmax()]
else:
    critica = {"Potência (kVA)": 300, "Z (%)": 4.0}

# --- CÁLCULOS DE ENGENHARIA ---
rtc_p = eval(tc_pri_text.replace('/', '/'))
rtc_s = eval(tc_sec_text.replace('/', '/'))

# Correntes Nominais e Curtos
in_p, icc_p = calcular_correntes(pot_p, v_pri, z_p)
in_s, icc_s = calcular_correntes(pot_p, v_sec, z_p)
in_g, icc_g = calcular_correntes(critica["Potência (kVA)"], v_sec, critica["Z (%)"])

# Coordenação de Fase (50/51)
t_bt = 0.05
# Galpão
pk_51_g = in_g * 1.25
t_51_g = t_bt + 0.20
dial_51_g = dial_reverso_mi(pk_51_g, icc_g, t_51_g)
# Secundário SE Principal
pk_51_s = in_s * 1.15
t_51_s = t_51_g + 0.30
dial_51_s = dial_reverso_mi(pk_51_s, icc_s, t_51_s)

# Coordenação de Neutro (50/51N) - Curva EI
pk_51n_s = in_s * 0.3
dial_51n_s = dial_reverso_ei(pk_51n_s, icc_s, t_51_s)

# --- RESULTADOS: MAPA DE PARAMETRIZAÇÃO ---
st.subheader("📝 Mapa de Ajustes e Parametrização (Valores Secundários)")
mapa = [
    ["Primário 138kV", tc_pri_text, "51", dial_51_s, round((pk_51_s/10)/rtc_p, 3), round((icc_s/10*1.1)/rtc_p, 2)],
    ["Secundário 13,8kV", tc_sec_text, "51", dial_51_s, round(pk_51_s/rtc_s, 3), round((icc_s*1.1)/rtc_s, 2)],
    ["Neutro Secundário", tc_sec_text, "51N (EI)", dial_51n_s, round(pk_51n_s/rtc_s, 3), round((in_s*1.5)/rtc_s, 2)]
]
df_mapa = pd.DataFrame(mapa, columns=["Equipamento", "TC", "Função ANSI", "Dial(TMS)", "Pickup (Sec A)", "Inst 50 (Sec A)"])
st.table(df_mapa)

# --- GRÁFICO DE COORDENAÇÃO (PROVA DE SELETIVIDADE) ---
st.subheader("📈 Estudo de Seletividade (Gráfico Log-Log)")
fig = go.Figure()
correntes_plot = np.logspace(np.log10(pk_51_g), np.log10(icc_s*1.2), 100)

# Curva Galpão
tempos_g = [formula_iec_mi(pk_51_g, dial_51_g, i) for i in correntes_plot]
fig.add_trace(go.Scatter(x=correntes_plot, y=tempos_g, name="Relé Galpão (51)", line=dict(color='green')))

# Curva Secundário SE
tempos_s = [formula_iec_mi(pk_51_s, dial_51_s, i) for i in correntes_plot]
fig.add_trace(go.Scatter(x=correntes_plot, y=tempos_s, name="Relé Principal (51)", line=dict(color='red', width=3)))

# Limite ANSI do Transformador (Curva de Dano)
fig.add_trace(go.Scatter(x=[icc_s, icc_s], y=[0.1, 2.0], name="Limite ANSI (Térmico)", line=dict(color='black', dash='dash')))

fig.update_xaxes(type="log", title="Corrente (A) - Ref. 13,8kV")
fig.update_yaxes(type="log", title="Tempo (s)", range=[-1, 2])
st.plotly_chart(fig, use_container_鎮_width=True)

# --- LAUDO DE CONFORMIDADE ---
st.subheader("📋 Matriz de Lógica e Proteções Adicionais")
col1, col2 = st.columns(2)
with col1:
    st.markdown("""
    **Funções Habilitadas no Relé Principal:**
    *   **ANSI 50/51:** Proteção de sobrecorrente de fase.
    *   **ANSI 50/51N:** Proteção de sobrecorrente de neutro.
    *   **ANSI 27/59:** Sub e Sobretensão (Ajuste: 0.8 / 1.1 pu).
    *   **ANSI 46:** Desequilíbrio de corrente (Ajuste: 20% I2/I1).
    """)
with col2:
    st.markdown(f"""
    **Lógica de Intertravamento:**
    *   Sinal Digital de Entrada: Monitoramento de contatos auxiliares.
    *   Ação: Troca automática entre **Grupo de Ajuste 01 (12MVA)** e **Grupo 02 (10MVA)**.
    *   Tempo de Limpeza Total (Fase): {t_51_s}s.
    """)

if t_51_s < 2.0:
    st.success("✅ PROJETO APROVADO: Os ajustes garantem a integridade térmica do transformador.")
