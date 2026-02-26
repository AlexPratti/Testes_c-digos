import streamlit as st
import numpy as np

def interpolar(v_oc, val_600, val_2700, val_14300):
    """Lógica de Interpolação conforme Seção 5.2.11 da NBR 17227"""
    if v_oc <= 0.6:
        return val_600
    elif 0.6 < v_oc <= 2.7:
        # Interpolação entre 600V e 2.700V
        return val_600 + (val_2700 - val_600) * (v_oc - 0.6) / (2.7 - 0.6)
    elif 2.7 < v_oc <= 15.0:
        # Interpolação entre 2.700V e 14.300V
        return val_2700 + (val_14300 - val_2700) * (v_oc - 2.7) / (14.3 - 2.7)
    return val_14300

def main():
    st.title("Parte 6: Interpolação Final (NBR 17227)")

    # 1. Tensão de Entrada do Sistema
    v_sistema = st.number_input("Tensão de Operação Voc (kV)", value=13.80, format="%.2f")

    # 2. Valores Intermediários Validados nas Etapas Anteriores
    # Correntes (kA)
    ia600 = 3.37423; ia2700 = 4.19239; ia14300 = 4.56798
    # Energias (J/cm²)
    e600_j = 30.62206; e2700_j = 31.85000; e14300_j = 32.45000 # Exemplos para teste
    # DLAs (mm)
    dla600 = 2450.0; dla2700 = 2680.0; dla14300 = 2850.0 # Exemplos para teste

    if st.button("Executar Interpolação Final"):
        # Cálculos Finais
        ia_final = interpolar(v_sistema, ia600, ia2700, ia14300)
        e_final_j = interpolar(v_sistema, e600_j, e2700_j, e14300_j)
        dla_final = interpolar(v_sistema, dla600, dla2700, dla14300)

        # Conversão de Energia para cal/cm²
        e_final_cal = e_final_j / 4.184

        # Determinação da Categoria (NBR 10 / NFPA 70E)
        if e_final_cal <= 1.2: cat = "Risco 0"
        elif e_final_cal <= 4: cat = "Categoria 1 (4 cal)"
        elif e_final_cal <= 8: cat = "Categoria 2 (8 cal)"
        elif e_final_cal <= 25: cat = "Categoria 3 (25 cal)"
        elif e_final_cal <= 40: cat = "Categoria 4 (40 cal)"
        else: cat = "PERIGO (Acima de 40 cal/cm²)"

        st.divider()
        st.subheader(f"🏁 RESULTADOS FINAIS PARA {v_sistema} kV")
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Corrente I_arc Final", f"{ia_final:.5f} kA")
        c2.metric("Energia Incidente Final", f"{e_final_cal:.5f} cal/cm²")
        c3.metric("Fronteira DLA Final", f"{dla_final:.2f} mm")

        st.warning(f"**Vestimenta Recomendada:** {cat}")

if __name__ == "__main__":
    main()
