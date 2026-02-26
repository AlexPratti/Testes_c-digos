import streamlit as st
import numpy as np
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm

# --- FUNÇÕES CORE (NBR 17227:2025) ---
def calc_ia_step(ibf, g, k):
    k1, k2, k3, k4, k5, k6, k7, k8, k9, k10 = k
    log_base = k1 + k2 * np.log10(ibf) + k3 * np.log10(g)
    poli = (k4*ibf**6 + k5*ibf**5 + k6*ibf**4 + k7*ibf**3 + k8*ibf**2 + k9*ibf + k10)
    return 10**(log_base * poli)

def calc_en_step(ia, ibf, g, d, t, k, cf):
    k1, k2, k3, k4, k5, k6, k7, k8, k9, k10, k11, k12, k13 = k
    poli_den = (k4*ibf**7 + k5*ibf**6 + k6*ibf**5 + k7*ibf**4 + k8*ibf**3 + k9*ibf**2 + k10*ibf)
    termo_ia = (k3 * ia) / poli_den if poli_den != 0 else 0
    exp = (k1 + k2*np.log10(g) + termo_ia + k11*np.log10(ibf) + k12*np.log10(d) + k13*np.log10(ia) + np.log10(1.0/cf))
    return (12.552 / 50.0) * t * (10**exp)

def calc_dla_step(ia, ibf, g, t, k, cf):
    k1, k2, k3, k4, k5, k6, k7, k8, k9, k10, k11, k12, k13 = k
    poli_den = (k4*ibf**7 + k5*ibf**6 + k6*ibf**5 + k7*ibf**4 + k8*ibf**3 + k9*ibf**2 + k10*ibf)
    termo_ia = (k3 * ia) / poli_den if poli_den != 0 else 0
    log_fixo = (k1 + k2*np.log10(g) + termo_ia + k11*np.log10(ibf) + k13*np.log10(ia) + np.log10(1.0/cf))
    return 10**((np.log10(5.0 / ((12.552 / 50.0) * t)) - log_fixo) / k12)

def interpolar(v, f600, f2700, f14300):
    if v <= 0.6: return f600
    if v <= 2.7: return f600 + (f2700 - f600) * (v - 0.6) / 2.1
    return f2700 + (f14300 - f2700) * (v - 2.7) / 11.6

def main():
    st.set_page_config(page_title="Gestão de Arco Elétrico", layout="wide")
    st.title("⚡ Gestão de Risco de Arco Elétrico - NBR 17227:2025")

    equipamentos = {
        "CCM 15 kV": {"gap": 152.0, "dist": 914.4, "dims": {"914,4 x 914,4 x 914,4": [914.4, 914.4, 914.4]}},
        "Conjunto de manobra 15 kV": {"gap": 152.0, "dist": 914.4, "dims": {"1143 x 762 x 762": [1143.0, 762.0, 762.0]}},
        "CCM 5 kV": {"gap": 104.0, "dist": 914.4, "dims": {"660,4 x 660,4 x 660,4": [660.4, 660.4, 660.4]}},
        "Conjunto de manobra 5 kV": {
            "gap": 104.0, "dist": 914.4, 
            "dims": {"914,4 x 914,4 x 914,4": [914.4, 914.4, 914.4], "1143 x 762 x 762": [1143.0, 762.0, 762.0]}
        },
        "CCM e painel raso de BT": {"gap": 25.0, "dist": 457.2, "dims": {"355,6 x 304,8 x ≤203,2": [355.6, 304.8, 203.2]}},
        "CCM e painel típico de BT": {"gap": 25.0, "dist": 457.2, "dims": {"355,6 x 304,8 x >203,2": [355.6, 304.8, 210.0]}},
        "Conjunto de manobra BT": {"gap": 32.0, "dist": 609.6, "dims": {"508 x 508 x 508": [508.0, 508.0, 508.0]}},
        "Caixa de junção de cabos": {"gap": 13.0, "dist": 457.2, "dims": {"355,6 x 304,8": [355.6, 304.8, 203.2]}},
    }
    
    tab1, tab2, tab3 = st.tabs(["Equipamento/Dimensões", "Cálculos e Resultados", "Relatório"])

    # --- ABA 1: EQUIPAMENTO/DIMENSÕES ---
    with tab1:
        st.subheader("Configuração de Equipamento e Dimensões")
        equip_escolhido = st.selectbox("Selecione o Equipamento:", list(equipamentos.keys()))
        info = equipamentos[equip_escolhido]
        
        opcoes_dim = list(info["dims"].keys()) + ["Inserir Dimensões Manualmente"]
        escolha_final_dim = st.selectbox(f"Selecione as dimensões para {equip_escolhido}:", options=opcoes_dim)
        
        if escolha_final_dim == "Inserir Dimensões Manualmente":
            st.info("Digite os valores personalizados:")
            col_m1, col_m2, col_m3 = st.columns(3)
            alt = col_m1.number_input("Altura [A] (mm)", value=500.0)
            larg = col_m2.number_input("Largura [L] (mm)", value=500.0)
            prof = col_m3.number_input("Profundidade [P] (mm)", value=500.0)
        else:
            alt, larg, prof = info["dims"][escolha_final_dim]

        gap_auto, dist_auto = info["gap"], info["dist"]
        dim_consolidada = f"{alt} x {larg} x {prof} mm"

        st.markdown("---")
        # Linha 1: Gap e Distância Horizontal
        row1_col1, row1_col2 = st.columns(2)
        row1_col1.metric("GAP sugerido (mm)", f"{gap_auto}")
        row1_col2.metric("D_trab sugerida (mm)", f"{dist_auto}")
        
        # Linha 2: A, L e P Horizontal (Abaixo)
        row2_col1, row2_col2, row2_col3 = st.columns(3)
        row2_col1.metric("Altura [A]", f"{alt} mm")
        row2_col2.metric("Largura [L]", f"{larg} mm")
        row2_col3.metric("Profundidade [P]", f"{prof} mm")

    # --- ABA 2: CÁLCULOS E RESULTADOS ---
    with tab2:
        c1, c2, c3 = st.columns(3)
        with c1:
            v_oc = st.number_input("Tensão Voc (kV)", value=13.80, format="%.2f")
            i_bf = st.number_input("Curto Ibf (kA)", value=4.85, format="%.2f")
            tempo_t = st.number_input("Tempo T (ms)", value=488.0, format="%.2f") # Abaixo do Curto
        with c2:
            gap_g = st.number_input("Gap G (mm)", value=float(gap_auto), format="%.2f")
            dist_d = st.number_input("Distância D (mm)", value=float(dist_auto), format="%.2f")
        with c3:
            st.write("") # Espaço vazio para manter o grid

        if st.button("Calcular Resultados"):
            # Lógica de Coeficientes (NBR 17227)
            k_ia = {
                600: [-0.04287, 1.035, -0.083, 0, 0, -4.783e-9, 1.962e-6, -0.000229, 0.003141, 1.092],
                2700: [0.0065, 1.001, -0.024, -1.557e-12, 4.556e-10, -4.186e-8, 8.346e-7, 5.482e-5, -0.003191, 0.9729],
                14300: [0.005795, 1.015, -0.011, -1.557e-12, 4.556e-10, -4.186e-8, 8.346e-7, 5.482e-5, -0.003191, 0.9729]
            }
            k_en = {
                600: [0.753364, 0.566, 1.752636, 0, 0, -4.783e-9, 1.962e-6, -0.000229, 0.003141, 1.092, 0, -1.598, 0.957],
                2700: [2.40021, 0.165, 0.354202, -1.557e-12, 4.556e-10, -4.186e-8, 8.346e-7, 5.482e-5, -0.003191, 0.9729, 0, -1.569, 0.9778],
                14300: [3.825917, 0.11, -0.999749, -1.557e-12, 4.556e-10, -4.186e-8, 8.346e-7, 5.482e-5, -0.003191, 0.9729, 0, -1.568, 0.99]
            }
            
            ees = (alt/25.4 + larg/25.4) / 2.0
            cf = -0.0003*ees**2 + 0.03441*ees + 0.4325
            ia_sts = [calc_ia_step(i_bf, gap_g, k_ia[v]) for v in [600, 2700, 14300]]
            en_sts = [calc_en_step(ia, i_bf, gap_g, dist_d, tempo_t, k_en[v], cf) for ia, v in zip(ia_sts, [600, 2700, 14300])]
            dl_sts = [calc_dla_step(ia, i_bf, gap_g, tempo_t, k_en[v], cf) for ia, v in zip(ia_sts, [600, 2700, 14300])]

            ia_f = interpolar(v_oc, *ia_sts)
            e_j = interpolar(v_oc, *en_sts)
            e_cal = e_j / 4.184
            dla_f = interpolar(v_oc, *dl_sts)
            ia_min = ia_f * (1 - 0.5*(-0.0001*v_oc**2 + 0.0022*v_oc + 0.02))
            cat = "CAT 2" if e_cal <= 8 else "CAT 4" if e_cal <= 40 else "EXTREMO RISCO"
            
            st.session_state['res'] = {
                "Ia": ia_f, "IaMin": ia_min, "E_cal": e_cal, "E_j": e_j, "DLA": dla_f, 
                "Cat": cat, "Voc": v_oc, "Equip": equip_escolhido, "Gap": gap_g, "Dist": dist_d, 
                "Dim": dim_consolidada, "Ibf": i_bf, "Tempo": tempo_t
            }
            
            # Retorno em COLUNA (Verticalmente alinhados)
            st.divider()
            st.write("### Resultados do Cálculo:")
            st.metric("Corrente de Arco Final (Iarc)", f"{ia_f:.4f} kA")
            st.metric("Corrente de Arco Reduzida", f"{ia_min:.4f} kA")
            st.metric("Energia Incidente (cal/cm²)", f"{e_cal:.4f}")
            st.metric("Energia Incidente (J/cm²)", f"{e_j:.4f}")
            st.metric("Distância Segura - Fronteira (mm)", f"{dla_f:.0f}")
            st.warning(f"🛡️ Vestimenta: **{cat}**")

    # --- ABA 3: RELATÓRIO ---
    with tab3:
        if 'res' in st.session_state:
            r = st.session_state['res']
            st.subheader(f"Laudo Técnico - {r['Equip']}")
            def export_pdf():
                buf = io.BytesIO(); c = canvas.Canvas(buf, pagesize=A4)
                c.setStrokeColor(colors.black); c.rect(1*cm, 25.5*cm, 19*cm, 3*cm)
                c.setFont("Helvetica-Bold", 14); c.drawString(7.5*cm, 27.5*cm, "LAUDO TÉCNICO DE ARCO ELÉTRICO")
                c.setFont("Helvetica", 9); c.drawString(1.5*cm, 26.5*cm, "[ LOGOTIPO ]")
                c.setFont("Helvetica", 10); y = 23.5*cm
                for text in [f"Equipamento: {r['Equip']}", f"GAP: {r['Gap']} mm | Distância D: {r['Dist']} mm", 
                             f"Dimensões [AxLxP]: {r['Dim']}", f"Iarc Final: {r['Ia']:.4f} kA | Reduzida: {r['IaMin']:.4f} kA",
                             f"Energia: {r['E_cal']:.4f} cal/cm² ({r['E_j']:.4f} J/cm²)", f"DLA: {r['DLA']:.0f} mm", f"Vestimenta: {r['Cat']}"]:
                    c.drawString(1.5*cm, y, text); y -= 0.7*cm
                c.save(); return buf.getvalue()
            st.download_button("📩 Baixar PDF", export_pdf(), "laudo_arco.pdf", "application/pdf")
        else: st.info("⚠️ Execute o cálculo para gerar o relatório.")

if __name__ == "__main__": main()
