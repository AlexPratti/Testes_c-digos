import streamlit as st

# Configuração da página
st.set_page_config(page_title="Gestão de Risco de Arco Elétrico", layout="wide")

# 1. Base de dados baseada nas Tabelas 1 e 3 da imagem (8 opções únicas)
EQUIPAMENTOS_DATA = {
    "CCM 15 kV": {"gap": 152.0, "dist_trab": 914.4, "dim": "914,4 x 914,4 x 914,4"},
    "Conjunto de manobra 15 kV": {"gap": 152.0, "dist_trab": 914.4, "dim": "1143 x 762 x 762"},
    "CCM 5 kV": {"gap": 104.0, "dist_trab": 914.4, "dim": "660,4 x 660,4 x 660,4"},
    "Conjunto de manobra 5 kV": {"gap": 104.0, "dist_trab": 914.4, "dim": "914,4 x 914,4 x 914,4 ou 1143 x 762 x 762"},
    "CCM e painel raso de BT": {"gap": 25.0, "dist_trab": 457.2, "dim": "355,6 x 304,8 x ≤203,2"},
    "CCM e painel típico de BT": {"gap": 25.0, "dist_trab": 457.2, "dim": "355,6 x 304,8 x >203,2"},
    "Conjunto de manobra BT": {"gap": 32.0, "dist_trab": 609.6, "dim": "508 x 508 x 508"},
    "Caixa de junção de cabos": {"gap": 13.0, "dist_trab": 457.2, "dim": "355,6 x 304,8 x ≤203,2 ou >203,2"},
}

st.title("⚡ Gestão de Risco de Arco Elétrico - NBR 17227:2025")

# Criação das abas com o novo nome para a Tab 1
tab1, tab2, tab3 = st.tabs(["Equipamento/Dimensões", "Cálculo e Resultados", "Relatório"])

# --- ABA 1: EQUIPAMENTO/DIMENSÕES ---
with tab1:
    st.subheader("Seleção de Equipamento e Parâmetros")
    
    # Selectbox com as 8 opções conforme Tabela 1 (sem repetições)
    equip_selecionado = st.selectbox(
        "Selecione o Equipamento e Classe de Tensão:", 
        options=list(EQUIPAMENTOS_DATA.keys())
    )
    
    # Recuperação dos valores do dicionário
    dados = EQUIPAMENTOS_DATA[equip_selecionado]
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        gap_val = st.number_input("GAP (mm)", value=dados["gap"], key="gap_input")
    with col2:
        dist_val = st.number_input("Distância de Trabalho (mm)", value=dados["dist_trab"], key="dist_input")
    
    st.markdown(f"**Tamanho do invólucro (AxLxP) (mm):** {dados['dim']}")
    st.info("Os valores acima serão aplicados automaticamente na aba de Cálculos.")

# --- ABA 2: CÁLCULO E RESULTADOS ---
with tab2:
    st.subheader("Parâmetros de Entrada para Cálculo")
    
    col_c1, col_c2 = st.columns(2)
    
    with col_c1:
        # Tensão e Curto (Inputs manuais padrão)
        tensao_vac = st.number_input("Tensão Vac (kV)", value=13.80)
        # Gap G (Puxando automaticamente da Tab 1)
        gap_g = st.number_input("Gap G (mm)", value=gap_val)
        
    with col_c2:
        curto_ibf = st.number_input("Curto Ibf (kA)", value=4.35)
        # Distância D (Puxando automaticamente da Tab 1)
        distancia_d = st.number_input("Distância D (mm)", value=dist_val)
    
    tempo_t = st.number_input("Tempo T (ms)", value=488.00)

    if st.button("Calcular Resultados"):
        # --- MANTENHA SUA LÓGICA DE CÁLCULO ABAIXO ---
        # Exemplo de placeholder para os resultados
        st.success("Cálculo realizado com sucesso utilizando os parâmetros da NBR 17227!")
        st.write(f"Utilizando Gap: {gap_g} mm e Distância: {distancia_d} mm")
        
        # Insira aqui suas fórmulas: Energia Incidente, Limite de Aproximação, etc.
        # energia = calculo_especifico(tensao_vac, curto_ibf, gap_g, distancia_d, tempo_t)

# --- ABA 3: RELATÓRIO ---
with tab3:
    st.subheader("Relatório Técnico")
    st.write("Visualize e exporte aqui o relatório dos cálculos realizados.")
