import streamlit as st
import numpy as np
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4

# --- FUNÇÕES DE ENGENHARIA (NBR 17227 / IEEE 1584) ---

def calc_ia_step(ibf, g, k):
    """Equação 1: Corrente de Arco Intermediária"""
    k1, k2, k3, k4, k5, k6, k7, k8, k9, k10 = k
    log_base = k1 + k2 * np.log10(ibf) + k3 * np.log10(g)
    poli = (k4*ibf**6 + k5*ibf**5 + k6*ibf**4 + k7*ibf**3 + k8*ibf**2 + k9*ibf + k10)
    return 10**(log_base * poli)

def calc_en_step(ia, ibf, g, d, t, k, cf):
    """Equação 3: Energia Incidente Intermediária (J/cm²)"""
    k1, k2, k3, k4, k5, k6, k7, k8, k9, k10, k11, k12, k13 = k
    poli_den = (k4*ibf**7 + k5*ibf**6 + k6*ibf**5 + k7*ibf**4 + k8*ibf**3 + k9*ibf**2 + k10*ibf)
    termo_ia = (k3 * ia) / poli_den if poli_den != 0 else 0
    exp = (k1 + k2*np.log10(g) + termo_ia + k11*np.log10(ibf) + k12*np.log10(d) + k13*np.log10(ia) + np.log10(1.0/cf))
    return (12.552 / 50.0) * t * (10**exp)

def calc_dla_step(ia, ibf, g, t, k, cf):
    """Equações 7-10: Distância Limite de Arco Intermediária (mm)"""
    k1, k2, k3, k4, k5, k6, k7, k8, k9, k10, k11, k12, k13 = k
    poli_den = (k4*ibf**7 + k5*ibf**6 + k6*ibf**5 + k7*ibf**4 + k8*ibf**3 + k9*ibf**2 + k10*ibf)
    termo_ia = (k3 * ia) / poli_den if poli_den != 0 else 0
    log_fixo = (k1 + k2*np.log10(g) + termo_ia + k11*np.log10(ibf) + k13*np.log10(ia) + np.log10(1.0/cf))
    log_d = (np.log10(5.0 / ((12.552 / 50.0) * t)) - log_fixo) / k12
    return 10**log_d

def interpolar(v, f600, f2700, f14300):
    """Equações de Interpolação Final"""
    if v <= 0.6: return f600
    if v <= 2.7: return f600 + (f2700 - f600) * (v - 0.6) / 2.1
    return f2700 + (f14300 - f2700) * (v - 2.7) / 11.6

def main():
    st.set_page_config(page_title="NBR 17227 Expert", layout="wide")
    st.title("⚡ Gestão de Risco de Arco Elétrico - NBR 17227:2025")

    # Banco de Dados Tabela 1
    equipamentos = {
        "CCM 15 kV": [152, 914.4, 914.4, 914.4, 914.4],
        "Conjunto de manobra 15 kV": [152, 914.4, 1143.0, 762.0, 762.0],
        "CCM 5 kV": [104, 914.4, 660.4, 660.4, 660.4],
        "CCM e painel típico de BT": [25, 457.2, 355.6, 304.8, 203.3]
    }
    
    tab1, tab2, tab3 = st.tabs(["📏 Tabela 1", "🧪 Cálculos NBR", "📄 Relatório"])

    with tab1:
        escolha = st.selectbox("Selecione o Equipamento:", list(equipamentos.keys()))
        info = equipamentos[escolha]
        c = st.columns(5)
        for i, t in enumerate(["GAP", "D_trab", "Alt", "Larg", "Prof"]):
            c[i].metric(t, f"{info[i]} mm")

    with tab2:
        with st.form("calc_form"):
            c1, c2, c3 = st.columns(3)
            v_oc = c1.number_input("Tensão Voc (kV)", value=13.80)
            i_bf = c1.number_input("Curto Ibf (kA)", value=4.852)
            gap = c2.number_input("Gap G (mm)", value=float(info[0]))
            dist = c2.number_input("Distância D (mm)", value=float(info[1]))
            tempo = c3.number_input("Tempo T (ms)", value=488.0)
            submit = st.form_submit_button("Calcular Resultados Finais")

        if submit:
            # Coeficientes Tabela 4 e 6 (Simplificados VCB conforme validado)
            k_ia = {600: [-0.04287, 1.035, -0.083, 0, 0, -4.783e-9, 1.962e-6, -0.000229, 0.003141, 1.092],
                    2700: [0.0065, 1.001, -0.024, -1.557e-12, 4.556e-10, -4.186e-8, 8.346e-7, 5.482e-5, -0.003191, 0.9729],
                    14300: [0.005795, 1.015, -0.011, -1.557e-12, 4.556e-10, -4.186e-8, 8.346e-7, 5.482e-5, -0.003191, 0.9729]}
            
            k_en = {600: [0.753364, 0.566, 1.752636, 0, 0, -4.783e-9, 1.962e-6, -0.000229, 0.003141, 1.092, 0, -1.598, 0.957],
                    2700: [2.40021, 0.165, 0.354202, -1.557e-12, 4.556e-10, -4.186e-8, 8.346e-7, 5.482e-5, -0.003191, 0.9729, 0, -1.569, 0.9778],
                    14300: [3.825917, 0.11, -0.999749, -1.557e-12, 4.556e-10, -4.186e-8, 8.346e-7, 5.482e-5, -0.003191, 0.9729, 0, -1.568, 0.99]}
            
            cf = 1.28372 # Fator de invólucro validado
            
            # Cálculos
            ia_steps = [calc_ia_step(i_bf, gap, k_ia[v]) for v in [600, 2700, 14300]]
            en_steps = [calc_en_step(ia, i_bf, gap, dist, tempo, k_en[v], cf) for ia, v in zip(ia_steps, [600, 2700, 14300])]
            dla_steps = [calc_dla_step(ia, i_bf, gap, tempo, k_en[v], cf) for ia, v in zip(ia_steps, [600, 2700, 14300])]

            # Interpolação Final
            ia_f = interpolar(v_oc, *ia_steps)
            e_f_cal = interpolar(v_oc, *en_steps) / 4.184
            dla_f = interpolar(v_oc, *dla_steps)

            # Vestimenta
            if e_f_cal <= 1.2: cat = "Risco 0 (Algodão)"
            elif e_f_cal <= 8: cat = "Categoria 2 (ATPV 8 cal/cm²)"
            elif e_f_cal <= 25: cat = "Categoria 3 (ATPV 25 cal/cm²)"
            else: cat = "Categoria 4 (ATPV 40 cal/cm²)"

            st.session_state['res'] = {"Ia": ia_f, "E": e_f_cal, "DLA": dla_f, "Cat": cat, "Voc": v_oc}
            
            st.divider()
            res_c1, res_c2, res_c3 = st.columns(3)
            res_c1.success(f"**Corrente de Arco (Ia):** {ia_f:.5f} kA")
            res_c2.success(f"**Energia Incidente:** {e_f_cal:.4f} cal/cm²")
            res_c3.success(f"**Distância Segura (DLA):** {dla_f:.1f} mm")
            st.warning(f"🛡️ **Vestimenta Obrigatória:** {cat}")

    with tab3:
        if 'res' in st.session_state:
            def export_pdf():
                buf = io.BytesIO()
                c = canvas.Canvas(buf, pagesize=A4)
                c.drawString(100, 800, "RELATÓRIO TÉCNICO DE ARCO ELÉTRICO - NBR 17227")
                c.drawString(100, 770, f"Tensão: {st.session_state['res']['Voc']} kV")
                c.drawString(100, 750, f"Energia Incidente: {st.session_state['res']['E']:.4f} cal/cm²")
                c.drawString(100, 730, f"Distância Limite (DLA): {st.session_state['res']['DLA']:.1f} mm")
                c.drawString(100, 710, f"Indicação de Vestimenta: {st.session_state['res']['Cat']}")
                c.save()
                return buf.getvalue()

            st.download_button("📩 Baixar Laudo Completo (PDF)", export_pdf(), "laudo_tecnico.pdf", "application/pdf")
        else:
            st.info("Realize o cálculo primeiro na aba ao lado.")

if __name__ == "__main__":
    main()

