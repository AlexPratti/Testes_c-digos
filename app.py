import streamlit as st
import numpy as np

def calcular_dla_step(ia, ibf, g, t, k, cf):
    """Implementação da Equação de DLA (Derivada da Eq. de Energia)"""
    k1, k2, k3, k4, k5, k6, k7, k8, k9, k10, k11, k12, k13 = k
    
    # 1. Denominador Polinomial (Igual ao da Energia)
    poli_den = (k4*ibf**7 + k5*ibf**6 + k6*ibf**5 + k7*ibf**4 + 
                k8*ibf**3 + k9*ibf**2 + k10*ibf)
    
    # 2. Termo de Corrente de Arco
    termo_ia = (k3 * ia) / poli_den if poli_den != 0 else 0
    
    # 3. Termos fixos da equação (tudo exceto a distância)
    # log10(5.0) refere-se ao limite de 5.0 J/cm² (1.2 cal/cm²)
    log_fixo = (k1 + k2*np.log10(g) + termo_ia + 
                k11*np.log10(ibf) + k13*np.log10(ia) + np.log10(1.0/cf))
    
    # 4. Isolando o Log da Distância (D):
    # log10(D) = [log10(5.0 / (12.552/50 * T)) - log_fixo] / k12
    log_d = (np.log10(5.0 / ((12.552 / 50.0) * t)) - log_fixo) / k12
    
    return 10**log_d # Retorna a DLA em mm

def main():
    st.title("Parte 5: Distâncias-Limite de Arco Intermediárias (DLA)")

    # Parâmetros e Correntes validados nas etapas anteriores
    ibf = 4.852; gap = 152.0; tempo_t = 488.0; cf = 1.28372
    ia600 = 3.37423; ia2700 = 4.19239; ia14300 = 4.56798

    # Mesmos coeficientes da Tabela 6 usados na Parte 4
    k_en = {
        600:   [0.753364, 0.566, 1.752636, 0, 0, -4.783e-9, 1.962e-6, -0.000229, 0.003141, 1.092, 0, -1.598, 0.957],
        2700:  [2.40021, 0.165, 0.354202, -1.557e-12, 4.556e-10, -4.186e-8, 8.346e-7, 5.482e-5, -0.003191, 0.9729, 0, -1.569, 0.9778],
        14300: [3.825917, 0.11, -0.999749, -1.557e-12, 4.556e-10, -4.186e-8, 8.346e-7, 5.482e-5, -0.003191, 0.9729, 0, -1.568, 0.99]
    }

    if st.button("Calcular DLAs Intermediárias"):
        dla600 = calcular_dla_step(ia600, ibf, gap, tempo_t, k_en[600], cf)
        dla2700 = calcular_dla_step(ia2700, ibf, gap, tempo_t, k_en[2700], cf)
        dla14300 = calcular_dla_step(ia14300, ibf, gap, tempo_t, k_en[14300], cf)

        st.subheader("Resultados de DLA (Fronteira em mm)")
        c1, c2, c3 = st.columns(3)
        c1.metric("DLA_600", f"{dla600:.2f} mm")
        c2.metric("DLA_2700", f"{dla2700:.2f} mm")
        c3.metric("DLA_14300", f"{dla14300:.2f} mm")
        
        st.info("Verifique se as distâncias intermediárias coincidem com seu Excel.")

if __name__ == "__main__":
    main()
