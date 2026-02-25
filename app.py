import streamlit as st

# Configuração da página
st.set_page_config(page_title="Calculadora de Distância", page_icon="⚡")

st.title("Calculadora de Distância de Trabalho")

# Base de dados
tabela = {
    ("CCM", "15 kV"): 914.4,
    ("Conjunto de manobra", "15 kV"): 914.4,
    ("CCM", "5 kV"): 914.4,
    ("Conjunto de manobra", "5 kV"): 914.4,
    ("CCM e painel raso de BT", "BT"): 457.2,
    ("CCM e painel típico de BT", "BT"): 457.2,
    ("Conjunto de manobra BT", "BT"): 609.6,
    ("Caixa de junção de cabos", "BT"): 457.2
}

# Inputs do usuário
equip = st.selectbox("Selecione o Equipamento:", [
    "CCM", "Conjunto de manobra", "CCM e painel raso de BT", 
    "CCM e painel típico de BT", "Conjunto de manobra BT", "Caixa de junção de cabos"
])

tensao = st.selectbox("Selecione a Classe de Tensão:", ["15 kV", "5 kV", "BT"])

if st.button("Verificar Distância"):
    resultado = tabela.get((equip, tensao))
    
    if resultado:
        st.success(f"### Distância: {resultado} mm")
    else:
        st.warning("Combinação não encontrada na tabela.")
