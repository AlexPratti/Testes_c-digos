import streamlit as st
import numpy as np
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4

# --- FUNÇÕES DE ENGENHARIA (Cálculo Escalar) ---

def calc_ia_step(ibf, g, k):
    """Equação 1: Corrente de Arco Intermediária"""
    # k = [k1 a k10]
    log_base = k[0] + k[1] * np.log10(ibf) + k[2] * np.log10(g)
    poli = (k[3]*ibf**6 + k[4]*ibf**5 + k[5]*ibf**4 + k[6]*ibf**3 + k[7]*ibf**2 + k[8]*ibf + k[9])
    return 10**(log_base * poli)

def interpolar(v, v1, v2, v3, f1, f2, f3):
    """Equações 16-33: Interpolação Final de Tensão"""
    # Garante que f1, f2 e f3 sejam números (float)
    f1, f2, f3 = float(f1), float(f2), float(f3)
    if v <= 0.6: return f1
    if v <= 2.7: return f1 + (f2 - f1) * (v - 0.6) / 2.1
    return f2 + (f3 - f2) * (v - 2.7) / 11.6

def main():
    st.set_page_config(page_title="NBR 17227 Expert", layout="wide")
    st.title("⚡ Gestão de Risco de Arco Elétrico - NBR 17227:2025")

    # Bancos de Dados
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
            i_bf = c1.number_input("Curto Ibf (kA)", value=4.85)
            gap = c2.number_input("Gap G (mm)", value=float(info[0]))
            dist = c2.number_input("Distância D (mm)", value=float(info[1]))
            tempo = c3.number_input("Tempo T (ms)", value=488.0)
            submit = st.form_submit_button("Calcular Resultados Finais")

        if submit:
            # Coeficientes Tabela 4 (Ia)
            k_ia = {
                600:   [-0.04287, 1.035, -0.083, 0, 0, -4.783e-9, 1.962e-6, -0.000229, 0.003141, 1.092],
                2700:  [0.0065, 1.001, -0.024, -1.557e-12, 4.556e-10, -4.186e-8, 8.346e-7, 5.482e-5, -0.003191, 0.9729],
                14300: [0.005795, 1.015, -0.011, -1.557e-12, 4.556e-10, -4.186e-8, 8.346e-7, 5.482e-5, -0.003191, 0.9729]
            }

            # Cálculos Intermediários
            ia600 = calc_ia_step(i_bf, gap, k_ia[600])
            ia2700 = calc_ia_step(i_bf, gap, k_ia[2700])
            ia14300 = calc_ia_step(i_bf, gap, k_ia[14300])

            # INTERPOLAÇÃO FINAL (Garante passagem de floats)
            ia_f = interpolar(v_oc, 0.6, 2.7, 14.3, ia600, ia2700, ia14300)

            # Salva na sessão para o relatório
            st.session_state['res'] = {"Ia": ia_f, "Voc": v_oc, "Ibf": i_bf}
            
            st.success(f"Corrente de Arco Final (Ia): {ia_f:.5f} kA")

    with tab3:
        if 'res' in st.session_state:
            def export_pdf():
                buf = io.BytesIO()
                c = canvas.Canvas(buf, pagesize=A4)
                c.drawString(100, 800, "RELATÓRIO TÉCNICO DE ARCO ELÉTRICO - NBR 17227")
                c.drawString(100, 770, f"Tensão: {st.session_state['res']['Voc']} kV")
                c.drawString(100, 750, f"Corrente Curto: {st.session_state['res']['Ibf']} kA")
                c.drawString(100, 730, f"Corrente Arco Final: {st.session_state['res']['Ia']:.5f} kA")
                c.save()
                return buf.getvalue()

            st.download_button("Baixar Relatório em PDF", export_pdf(), "laudo_tecnico.pdf", "application/pdf")
        else:
            st.info("Realize o cálculo primeiro.")

if __name__ == "__main__":
    main()
