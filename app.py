import streamlit as st

# Configuração da página
st.set_page_config(page_title="Gestão de Risco de Arco Elétrico", page_icon="⚡", layout="wide")

# --- BANCO DE DADOS (Tabela 1 e Tabela 3 da Imagem) ---
dados_norma = {
    "CCM 15 kV": [{"gap": 152.0, "dist": 914.4, "dim": "914,4 x 914,4 x 914,4"}],
    "Conjunto de manobra 15 kV": [{"gap": 152.0, "dist": 914.4, "dim": "1143 x 762 x 762"}],
    "CCM 5 kV": [{"gap": 104.0, "dist": 914.4, "dim": "660,4 x 660,4 x 660,4"}],
    "Conjunto de manobra 5 kV": [
        {"gap": 104.0, "dist": 914.4, "dim": "914,4 x 914,4 x 914,4"},
        {"gap": 104.0, "dist": 914.4, "dim": "1143 x 762 x 762"}
    ],
    "CCM e painel rasos de BT": [{"gap": 25.0, "dist": 457.2, "dim": "355,6 x 304,8 x ≤203,2"}],
    "CCM e painel típico de BT": [{"gap": 25.0, "dist": 457.2, "dim": "355,6 x 304,8 x >203,2"}],
    "Conjunto de manobra BT": [{"gap": 32.0, "dist": 609.6, "dim": "508 x 508 x 508"}],
    "Caixa de junção de cabos": [
        {"gap": 13.0, "dist": 457.2, "dim": "355,6 x 304,8 x ≤203,2"},
        {"gap": 13.0, "dist": 457.2, "dim": "355,6 x 304,8 x >203,2"}
    ]
}

st.title("⚡ Gestão de Risco de Arco Elétrico - NBR 17227:2025")

# Criação das abas conforme solicitado
aba1, aba2, aba3 = st.tabs(["Equipamento/Dimensões", "Cálculo de Resultados", "Relatório"])

with aba1:
    st.subheader("Seleção de Equipamento")
    
    # Seleção de Equipamento conforme Tabela 1 (sem repetição de nomes)
    equip_sel = st.selectbox("Equipamento e classe de tensão:", list(dados_norma.keys()))
    
    opcoes = dados_norma[equip_sel]
    
    # Lógica para nomes repetidos: Se houver mais de uma opção de invólucro, mostra o seletor opcional
    if len(opcoes) > 1:
        dim_opcoes = [opt["dim"] for opt in opcoes]
        dim_escolhida = st.selectbox("Selecione o Tamanho do invólucro (AxLxP):", dim_opcoes)
        selecao_final = next(item for item in opcoes if item["dim"] == dim_escolhida)
    else:
        selecao_final = opcoes[0]
        st.text(f"Tamanho do invólucro (AxLxP): {selecao_final['dim']}")

    # Exibição dos dados que serão levados para a Aba 2
    st.markdown("---")
    c1, c2 = st.columns(2)
    c1.metric("GAP G (mm)", selecao_final['gap'])
    c2.metric("Distância de Trabalho D (mm)", selecao_final['dist'])

with aba2:
    st.subheader("Cálculo de Resultados")
    
    # Layout espelhado na imagem enviada
    col1, col2, col3 = st.columns(3)
    tensao_voc = col1.number_input("Tensão Voc (kV)", value=13.80)
    # GAP G recebe automaticamente o valor da Aba 1
    gap_g = col2.number_input("Gap G (mm)", value=selecao_final['gap'])
    tempo_t = col3.number_input("Tempo T (ms)", value=488.0)
    
    col4, col5 = st.columns(2)
    curto_ibf = col4.number_input("Curto Ibf (kA)", value=4.85)
    # Distância D recebe automaticamente o valor da Aba 1
    distancia_d = col5.number_input("Distância D (mm)", value=selecao_final['dist'])
    
    st.markdown("---")
    if st.button("Calcular Resultados", type="primary"):
        # Mantendo o restante da sua lógica funcional
        st.write("Processando cálculos...")

with aba3:
    st.subheader("Relatório")
    st.write("Conteúdo do relatório...")
