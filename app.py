import streamlit as st

def calcular_ia_min(ia_final, var_cf):
    """Implementação da Equação 34 da NBR 17227"""
    # Iarc_min = Iarc * (1 - 0.5 * VarCf)
    return ia_final * (1.0 - 0.5 * var_cf)

def main():
    st.title("Parte 7: Corrente de Arco Reduzida (Eq. 34)")

    # 1. Valores obtidos nas etapas anteriores (Exemplos para validação)
    # Supondo Ia_final interpolada para 13.8kV
    ia_final = st.number_input("Corrente de Arco Final (kA)", value=4.55230, format="%.5f")
    # Supondo VarCf calculado para 13.8kV
    var_cf = st.number_input("Fator de Variação VarCf", value=0.03132, format="%.5f")

    if st.button("Calcular Corrente Mínima (Ia_min)"):
        ia_min = calcular_ia_min(ia_final, var_cf)
        
        reducao_percentual = (1 - (ia_min / ia_final)) * 100

        st.divider()
        st.subheader("Resultado da Corrente Reduzida")
        
        c1, c2 = st.columns(2)
        c1.metric("Ia_final (kA)", f"{ia_final:.5f}")
        c2.metric("Ia_min (kA)", f"{ia_min:.5f}")
        
        st.info(f"A corrente de arco foi reduzida em {reducao_percentual:.2f}% conforme a variabilidade da norma.")
        
        st.warning("""
        **Atenção Profissional:** 
        Agora você deve usar este valor de **Ia_min** para consultar a curva do seu disjuntor no Excel 
        e verificar se o novo tempo de atuação (T_min) gera uma energia incidente maior.
        """)

if __name__ == "__main__":
    main()
