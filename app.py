import streamlit as st
import numpy as np

def calcular_i_arc_intermediaria(i_bf, gap, k_list):
    """Calcula a corrente de arco para um patamar específico (600, 2700 ou 14300V)"""
    k1, k2, k3, k4, k5, k6, k7, k8, k9, k10 = k_list
    log_i_arc = (k1 + k2 * np.log10(i_bf) + k3 * np.log10(gap)) * \
                (k4 * i_bf**6 + k5 * i_bf**5 + k6 * i_bf**4 + k7 * i_bf**3 + k8 * i_bf**2 + k9 * i_bf + k10)
    return 10**log_i_arc

def main():
    st.set_page_config(page_title="Engenharia Elétrica Pro", layout="wide")
    tab1, tab2 = st.tabs(["Dimensões e Invólucros", "Corrente de Arco (IEEE 1584-2018)"])

    with tab1:
        st.header("Consulta de Equipamentos")
        # (Seu código anterior que funcionou satisfatoriamente entra aqui)

    with tab2:
        st.header("Cálculo de Corrente de Arco Final")
        
        # --- Entradas de Dados ---
        col1, col2 = st.columns(2)
        with col1:
            v_oc = st.number_input("Tensão do Sistema (kV)", 0.208, 15.0, 13.8)
            i_bf = st.number_input("Corrente de Curto-Circuito Simétrica (kA)", 0.5, 106.0, 20.0)
        with col2:
            config = st.selectbox("Configuração dos Eletrodos", ["VCB", "VCBB", "HCB", "VOA", "HOA"])
            gap = st.number_input("Gap entre Eletrodos (mm)", 0.5, 250.0, 25.0)

        # --- Coeficientes Tabela 4 (Exemplo VCB - Substitua pelos valores da sua imagem) ---
        # Ordem: k1 a k10 para os níveis [600V, 2700V, 14300V]
        coefs = {
            "VCB": {
                600:   [0.0039, 0.983, 0.002, 0, 0, 0, 0, 0, 0, 1], # Exemplo simplificado
                2700:  [0.0040, 0.985, 0.002, 0, 0, 0, 0, 0, 0, 1],
                14300: [0.0042, 0.990, 0.002, 0, 0, 0, 0, 0, 0, 1]
            }
        }

        if st.button("Calcular Corrente Final"):
            try:
                # 1. Cálculos Intermediários
                i600  = calcular_i_arc_intermediaria(i_bf, gap, coefs[config][600])
                i2700 = calcular_i_arc_intermediaria(i_bf, gap, coefs[config][2700])
                i14300= calcular_i_arc_intermediaria(i_bf, gap, coefs[config][14300])

                # 2. Interpolação Final
                if 0.6 < v_oc <= 2.7:
                    # Interpolação entre 600V e 2700V
                    i_arc = i600 * (2.7 - v_oc)/(2.7 - 0.6) + i2700 * (v_oc - 0.6)/(2.7 - 0.6)
                elif 2.7 < v_oc <= 15.0:
                    # Interpolação entre 2700V e 14300V (ajustado para kV)
                    i_arc = i2700 * (14.3 - v_oc)/(14.3 - 2.7) + i14300 * (v_oc - 2.7)/(14.3 - 2.7)
                else:
                    i_arc = i600

                # 3. Exibição dos Resultados
                st.subheader("Resultados da Interpolação")
                c1, c2, c3, c4 = st.columns(4)
                c1.metric("I_arc @ 600V", f"{i600:.2f} kA")
                c2.metric("I_arc @ 2700V", f"{i2700:.2f} kA")
                c3.metric("I_arc @ 14300V", f"{i14300:.2f} kA")
                c4.metric("CORRENTE FINAL", f"{i_arc:.2f} kA", delta_color="inverse")

            except KeyError:
                st.error("Configuração de eletrodos ainda não mapeada no dicionário de coeficientes.")

if __name__ == "__main__":
    main()

