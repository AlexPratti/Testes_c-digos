import streamlit as st

# Configuração da página
st.set_page_config(page_title="Gestão de Risco de Arco Elétrico", layout="wide")

# 1. Base de dados baseada nas Tabelas 1 e 3
EQUIPAMENTOS_DATA = {
    "CCM 15 kV": {"gap": 152.0, "dist": 914.4, "dim": [914.4, 914.4, 914.4]},
    "Conjunto de manobra 15 kV": {"gap": 152.0, "dist": 914.4, "dim": [1143.0, 762.0, 762.0]},
    "CCM 5 kV": {"gap": 104.0, "dist": 914.4, "dim": [660.4, 660.4, 660.4]},
    "Conjunto de manobra 5 kV": {
        "gap": 104.0, 
        "dist": 914.4, 
        "opcoes": {
            "914,4 x 914,4 x 914,4": [914.4, 914.4, 914.4],
            "1143 x 762 x 762": [1143.0, 762.0, 762.0]
        }
    },
    "CCM e painel raso de BT": {"gap": 25.0, "dist": 457.2, "dim": [355.6, 304.8, 203.2]},
    "CCM e painel típico de BT": {"gap": 25.0, "dist": 457.2, "dim": [355.6, 304.8, 210.0]},
    "Conjunto de manobra BT": {"gap": 32.0, "dist": 609.6, "dim": [508.0, 508.0, 508.0]},
    "Caixa de junção de cabos": {"gap": 13.0, "dist": 457.2, "dim": [355.6, 304.8, 203.2]},
}

st.title("⚡ Gestão de Risco de Arco Elétrico - NBR 17227:2025")

# Definição das abas
tab1, tab2, tab3 = st.tabs(["Equipamento/Dimensões", "Cálculo e Resultados", "Relatório"])

# --- ABA 1: EQUIPAMENTO/DIMENSÕES ---
with tab1:
    st.subheader("Seleção de Equipamento e Dimensões")
    
    equip_selecionado = st.selectbox(
        "Selecione o Equipamento e Classe de Tensão:", 
        options=list(EQUIPAMENTOS_DATA.keys())
    )
    
    dados = EQUIPAMENTOS_DATA[equip_selecionado]
    
    # Lógica de múltiplas dimensões para Conjunto 5kV
    if equip_selecionado == "Conjunto de manobra 5 kV":
        escolha_dim = st.selectbox("Selecione a dimensão do invólucro (AxLxP):", options=list(dados["opcoes"].keys()))
        dimensoes = dados["opcoes"][escolha_dim]
    else:
        dimensoes = dados["dim"]

    # Variáveis globais para a Tab 2
    gap_auto = dados["gap"]
    dist_auto = dados["dist"]
    alt, larg, prof = dimensoes

    st.markdown("---")
    c1, c2, c3 = st.columns(3)
    c1.metric("GAP sugerido (mm)", f"{gap_auto}")
    c2.metric("Distância sugerida (mm)", f"{dist_auto}")
    c3.write(f"**Dimensões [AxLxP]:**\n{alt} x {larg} x {prof} mm")

# --- ABA 2: CÁLCULO E RESULTADOS (LAYOUT CONFORME IMAGEM) ---
with tab2:
    # Primeira Linha de Inputs (Tensão, Gap, Tempo)
    col1, col2, col3 = st.columns(3)
    with col1:
        tensao_vac = st.number_input("Tensão Vac (kV)", value=13.80, step=0.01, format="%.2f")
    with col2:
        # Puxa automaticamente o GAP da Tab 1, mas permite edição manual se necessário
        gap_g = st.number_input("Gap G (mm)", value=float(gap_auto), step=0.01, format="%.2f")
    with col3:
        tempo_t = st.number_input("Tempo T (ms)", value=488.00, step=0.01, format="%.2f")

    # Segunda Linha de Inputs (Curto, Distância)
    col4, col5, col6 = st.columns(3)
    with col4:
        curto_ibf = st.number_input("Curto Ibf (kA)", value=4.35, step=0.01, format="%.2f")
    with col5:
        # Puxa automaticamente a Distância da Tab 1
        distancia_d = st.number_input("Distância D (mm)", value=float(dist_auto), step=0.01, format="%.2f")
    with col6:
        st.write("") # Espaço vazio para manter o alinhamento da imagem

    # Botão de Calcular posicionado à esquerda
    if st.button("Calcular Resultados"):
        # Mantenha aqui sua lógica de cálculo existente da NBR 17227
        st.divider()
        st.subheader("Resultados do Cálculo")
        st.info("Cálculo realizado com sucesso utilizando os parâmetros sincronizados.")

# --- ABA 3: RELATÓRIO ---
with tab3:
    st.subheader("Relatório")
    st.write("Área destinada à geração do relatório técnico.")
