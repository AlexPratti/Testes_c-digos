import streamlit as st

# Configuração da página
st.set_page_config(page_title="Gestão de Risco de Arco Elétrico", layout="wide")

# 1. Base de dados baseada nas Tabelas 1 e 3 da imagem
# Estrutura: { "Equipamento": { "gap": float, "dist": float, "dim": [A, L, P] ou dict para multiplos } }
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
    "CCM e painel típico de BT": {"gap": 25.0, "dist": 457.2, "dim": [355.6, 304.8, 210.0]}, # Exemplo > 203.2
    "Conjunto de manobra BT": {"gap": 32.0, "dist": 609.6, "dim": [508.0, 508.0, 508.0]},
    "Caixa de junção de cabos": {"gap": 13.0, "dist": 457.2, "dim": [355.6, 304.8, 203.2]},
}

st.title("⚡ Gestão de Risco de Arco Elétrico - NBR 17227:2025")

tab1, tab2, tab3 = st.tabs(["Equipamento/Dimensões", "Cálculo e Resultados", "Relatório"])

# --- ABA 1: EQUIPAMENTO/DIMENSÕES ---
with tab1:
    st.subheader("Seleção de Equipamento e Dimensões")
    
    equip_selecionado = st.selectbox(
        "Selecione o Equipamento e Classe de Tensão:", 
        options=list(EQUIPAMENTOS_DATA.keys())
    )
    
    # Lógica para tratar múltiplas dimensões no Conjunto de manobra 5 kV
    dados = EQUIPAMENTOS_DATA[equip_selecionado]
    
    if equip_selecionado == "Conjunto de manobra 5 kV":
        escolha_dim = st.selectbox("Selecione a dimensão do invólucro (AxLxP):", options=list(dados["opcoes"].keys()))
        dimensoes = dados["opcoes"][escolha_dim]
    else:
        dimensoes = dados["dim"]

    # Atribuição das variáveis para uso na Aba 2
    gap_final = dados["gap"]
    dist_final = dados["dist"]
    alt, larg, prof = dimensoes

    # Exibição dos resultados em colunas
    st.markdown("---")
    col_res1, col_res2 = st.columns(2)
    with col_res1:
        st.metric("GAP (mm)", f"{gap_final}")
        st.metric("Distância de Trabalho (mm)", f"{dist_final}")
    
    with col_res2:
        st.write("**Dimensões do Invólucro:**")
        st.write(f"📏 Altura [A]: **{alt} mm**")
        st.write(f"↔️ Largura [L]: **{larg} mm**")
        st.write(f"↗️ Profundidade [P]: **{prof} mm**")

# --- ABA 2: CÁLCULO E RESULTADOS ---
with tab2:
    st.subheader("Parâmetros de Entrada (Sincronizados)")
    
    col_c1, col_c2 = st.columns(2)
    with col_c1:
        tensao_vac = st.number_input("Tensão Vac (kV)", value=13.80)
        # Recebe valor automático da Tab 1
        gap_g = st.number_input("Gap G (mm)", value=float(gap_final))
        
    with col_c2:
        curto_ibf = st.number_input("Curto Ibf (kA)", value=4.35)
        # Recebe valor automático da Tab 1
        distancia_d = st.number_input("Distância D (mm)", value=float(dist_final))
    
    tempo_t = st.number_input("Tempo T (ms)", value=488.00)

    if st.button("Calcular Resultados"):
        # Sua lógica de cálculo NBR 17227 aqui
        st.success(f"Cálculo processado para {equip_selecionado}")
        st.info(f"Dimensões utilizadas no cálculo: {alt}x{larg}x{prof} mm")

# --- ABA 3: RELATÓRIO ---
with tab3:
    st.subheader("Relatório Técnico")
    st.write("Dados prontos para exportação.")
