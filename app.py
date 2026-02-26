import streamlit as st

def main():
    st.title("Calculadora de Dimensões e Espaçamentos")

    # Base de dados baseada na imagem (Tabela 1)
    # Formato: "Equipamento": [Espaçamento, Altura, Largura, Profundidade]
    dados = {
        "CCM 15 kV": ["152", "914,4", "914,4", "914,4"],
        "Conjunto de manobra 15 kV": ["152", "1143", "762", "762"],
        "CCM 5 kV": ["104", "660,4", "660,4", "660,4"],
        "Conjunto de manobra 5 kV (Opção 1)": ["104", "914,4", "914,4", "914,4"],
        "Conjunto de manobra 5 kV (Opção 2)": ["104", "1143", "762", "762"],
        "CCM e painel rasos de BT": ["25", "355,6", "304,8", "≤203,2"],
        "CCM e painel típico de BT": ["25", "355,6", "304,8", ">203,2"],
        "Conjunto de manobra BT": ["32", "508", "508", "508"],
        "Caixa de junção de cabos": ["13", "355,6", "304,8", "≤203,2 ou >203,2"]
    }

    # Campo único de seleção
    escolha = st.selectbox("Selecione o Equipamento e Classe de Tensão:", list(dados.keys()))

    if escolha:
        info = dados[escolha]
        
        # Layout em colunas para os resultados
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Espaçamento Típico", f"{info[0]} mm")
        
        with col2:
            st.subheader("Tamanho do Invólucro (mm)")
            st.write(f"**Altura:** {info[1]}")
            st.write(f"**Largura:** {info[2]}")
            st.write(f"**Profundidade:** {info[3]}")

if __name__ == "__main__":
    main()
