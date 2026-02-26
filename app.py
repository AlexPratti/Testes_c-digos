import streamlit as st
import numpy as np

def main():
    st.set_page_config(page_title="Engenharia Elétrica Pro", layout="wide")
    tab1, tab2 = st.tabs(["📏 Dimensões e Invólucros", "⚡ Corrente de Arco (IEEE 1584)"])

    # --- ABA 1: CONSULTA DE EQUIPAMENTOS (DADOS DA SUA IMAGEM) ---
    with tab1:
        st.header("Consulta de Equipamentos e Espaçamentos")
        
        # Dados extraídos da Tabela 1 da sua imagem
        # Formato: "Nome": [GAP(mm), Altura, Largura, Profundidade]
        dados_inv = {
            "CCM 15 kV": [152, "914,4", "914,4", "914,4"],
            "Conjunto de manobra 15 kV": [152, "1143", "762", "762"],
            "CCM 5 kV": [104, "660,4", "660,4", "660,4"],
            "Conjunto de manobra 5 kV (Opção 1)": [104, "914,4", "914,4", "914,4"],
            "Conjunto de manobra 5 kV (Opção 2)": [104, "1143", "762", "762"],
            "CCM e painel rasos de BT": [25, "355,6", "304,8", "≤203,2"],
            "CCM e painel típico de BT": [25, "355,6", "304,8", ">203,2"],
            "Conjunto de manobra BT": [32, "508", "508", "508"],
            "Caixa de junção de cabos": [13, "355,6", "304,8", "≤203,2 ou >203,2"]
        }

        escolha = st.selectbox("Selecione o Equipamento:", list(dados_inv.keys()))
        
        if escolha:
            info = dados_inv[escolha]
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("GAP / Espaçamento", f"{info[0]} mm")
            c2.metric("Altura (A)", f"{info[1]} mm")
            c3.metric("Largura (L)", f"{info[2]} mm")
            c4.metric("Profundidade (P)", f"{info[3]} mm")

    # --- ABA 2: CÁLCULO DE ARCO COM COEFICIENTES AUTOMÁTICOS ---
    with tab2:
        st.header("Calculadora de Corrente de Arco Intermediária")

        # Dicionário de Coeficientes (Exemplo simplificado da Tabela 4 da IEEE 1584-2018)
        # Em um cenário real, você preencheria todos os k1-k10 aqui para cada nível
        coefs_ieee = {
            "VCB":  {"k1": -0.019, "k2": 0.940, "k3": 0.012},
            "VCBB": {"k1": -0.025, "k2": 0.945, "k3": 0.010},
            "HCB":  {"k1": -0.030, "k2": 0.950, "k3": 0.008},
            "VOA":  {"k1": -0.015, "k2": 0.930, "k3": 0.015},
            "HOA":  {"k1": -0.020, "k2": 0.935, "k3": 0.012}
        }

        col_a, col_b = st.columns(2)
        with col_a:
            v_sistema = st.number_input("Tensão do Sistema (kV)", 0.208, 15.0, 13.8)
            i_bf = st.number_input("Corrente de Curto-Circuito (kA)", 0.5, 106.0, 20.0)
        with col_b:
            eletrodo = st.selectbox("Configuração do Eletrodo:", list(coefs_ieee.keys()))
            gap_input = st.number_input("Gap entre Eletrodos (mm)", value=float(info[0]) if 'info' in locals() else 25.0)

        # Atualização Automática de Coeficientes
        c = coefs_ieee[eletrodo]
        st.write(f"**Coeficientes Atuais ({eletrodo}):** k1={c['k1']}, k2={c['k2']}, k3={c['k3']}")

        # Lógica de Cálculo e Interpolação
        def calc_i_arc(k1, k2, k3, ibf, g):
            return 10**(k1 + k2 * np.log10(ibf) + k3 * np.log10(g))

        # Calculando para os 3 níveis padrão da norma
        i600 = calc_i_arc(c['k1'], c['k2'], c['k3'], i_bf, gap_input)
        i2700 = calc_i_arc(c['k1']+0.005, c['k2'], c['k3'], i_bf, gap_input) # Exemplo de variação por tensão
        i14300 = calc_i_arc(c['k1']+0.01, c['k2'], c['k3'], i_bf, gap_input)

        # Interpolação Final
        if v_sistema <= 0.6:
            i_final = i600
        elif v_sistema <= 2.7:
            i_final = i600 + (i2700 - i600) * (v_sistema - 0.6) / (2.7 - 0.6)
        else:
            i_final = i2700 + (i14300 - i2700) * (v_sistema - 2.7) / (14.3 - 2.7)

        st.divider()
        res1, res2, res3, res_final = st.columns(4)
        res1.metric("I_arc @ 600V", f"{i600:.2f} kA")
        res2.metric("I_arc @ 2700V", f"{i2700:.2f} kA")
        res3.metric("I_arc @ 14300V", f"{i14300:.2f} kA")
        res_final.subheader(f"Corrente Final: {i_final:.2f} kA")

if __name__ == "__main__":
    main()
