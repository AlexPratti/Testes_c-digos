import streamlit as st
import numpy as np
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4

# --- FUNÇÕES CORE (NBR 17227:2025) - MANTIDAS ---

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
    st.set_page_config(page_title="Gestão de Risco de Arco Elétrico", layout="wide")
    st.title("⚡ Gestão de Risco de Arco Elétrico - NBR 17227:2025")

    # Base de dados atualizada conforme Tabela 1 e Tabela 3
    equipamentos = {
        "CCM 15 kV": {"gap": 152.0, "dist": 914.4, "dim": [914.4, 914.4, 914.4]},
        "Conjunto de manobra 15 kV": {"gap": 152.0, "dist": 914.4, "dim": [1143.0, 762.0, 762.0]},
        "CCM 5 kV": {"gap": 104.0, "dist": 914.4, "dim": [660.4, 660.4, 660.4]},
        "Conjunto de manobra 5 kV": {
            "gap": 104.0, "dist": 914.4, 
            "opcoes": {
                "914,4 x 914,4 x 914,4": [914.4, 914.4, 914.4],
                "1143 x 762 x 762": [1143.0, 762.0, 762.0]
            }
        },
        "CCM e painel raso de BT": {"gap": 25.0, "dist": 457.2, "dim": [355.6, 304.8, 203.2]},
        "CCM e painel típico de BT": {"gap": 25.0, "dist": 457.2, "dim": [355.6, 304.8, 210.0]},
        "Conjunto de manobra BT": {"gap": 32.0, "dist": 609.6, "dim": [508.0, 508.0, 508.0]},
        "Caixa de junção de cabos": {"gap": 13.0, "dist": 457.2, "dim": [355.6, 304.8, 203.2]},
    }
    
    tab1, tab2, tab3 = st.tabs(["Equipamento/Dimensões", "Cálculos e Resultados", "Relatório"])

    with tab1:
        st.subheader("Seleção de Equipamento e Dimensões")
        escolha = st.selectbox("Selecione o Equipamento:", list(equipamentos.keys()))
        info = equipamentos[escolha]
        
        # Lógica para dimensões variáveis
        if escolha == "Conjunto de manobra 5 kV":
            escolha_dim = st.selectbox("Selecione as dimensões (AxLxP):", options=list(info["opcoes"].keys()))
            dimensoes = info["opcoes"][escolha_dim]
        else:
            dimensoes = info["dim"]

        gap_atu = info["gap"]
        dist_atu = info["dist"]
        alt, larg, prof = dimensoes

        st.markdown("---")
        c = st.columns(5)
        c[0].metric("GAP (mm)", f"{gap_atu}")
        c[1].metric("D_trab (mm)", f"{dist_atu}")
        c[2].metric("Altura [A]", f"{alt} mm")
        c[3].metric("Largura [L]", f"{larg} mm")
        c[4].metric("Profundidade [P]", f"{prof} mm")

    with tab2:
        # Layout conforme a imagem enviada (Tensão, Gap, Tempo / Curto, Distância)
        c1, c2, c3 = st.columns(3)
        v_oc = c1.number_input("Tensão Voc (kV)", value=13.80, format="%.2f")
        gap_input = c2.number_input("Gap G (mm)", value=float(gap_atu), format="%.2f")
        tempo = c3.number_input("Tempo T (ms)", value=488.0, format="%.2f")

        c4, c5, c6 = st.columns(3)
        i_bf = c4.number_input("Curto Ibf (kA)", value=4.85, format="%.2f")
        dist_input = c5.number_input("Distância D (mm)", value=float(dist_atu), format="%.2f")
        
        # Botão centralizado ou à esquerda conforme imagem
        if st.button("Calcular Resultados"):
            # Coeficientes (Mantidos do seu original)
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
            
            # Cálculo do CF baseado nas dimensões da Aba 1
            ees = (alt/25.4 + larg/25.4) / 2.0
            cf = -0.0003*ees**2 + 0.03441*ees + 0.4325
            
            # Processamento (Usando os valores dos inputs sincronizados)
            ia_sts = [calc_ia_step(i_bf, gap_input, k_ia[v]) for v in [600, 2700, 14300]]
            en_sts = [calc_en_step(ia, i_bf, gap_input, dist_input, tempo, k_en[v], cf) for ia, v in zip(ia_sts, [600, 2700, 14300])]
            dl_sts = [calc_dla_step(ia, i_bf, gap_input, tempo, k_en[v], cf) for ia, v in zip(ia_sts, [600, 2700, 14300])]

            ia_f = interpolar(v_oc, *ia_sts)
            e_f = interpolar(v_oc, *en_sts)/4.184
            dla_f = interpolar(v_oc, *dl_sts)
            var_cf = -0.0001*v_oc**2 + 0.0022*v_oc + 0.02
            ia_min = ia_f * (1 - 0.5*var_cf)

            cat = "Cat 2 (8 cal)" if e_f <= 8 else "Cat 4 (40 cal)" if e_f <= 40 else "PERIGO"
            
            st.session_state['res'] = {"Ia": ia_f, "E": e_f, "DLA": dla_f, "IaMin": ia_min, "Cat": cat, "Voc": v_oc, "Equip": escolha}
            
            # Exibição dos resultados abaixo do botão
            st.divider()
            res_c1, res_c2, res_c3, res_c4 = st.columns(4)
            res_c1.metric("Ia Final (kA)", f"{ia_f:.5f}")
            res_c2.metric("Ia Reduzida (kA)", f"{ia_min:.5f}")
            res_c3.metric("Energia (cal/cm²)", f"{e_f:.4f}")
            res_c4.metric("Fronteira (mm)", f"{dla_f:.0f}")
            st.warning(f"🛡️ Vestimenta Recomendada: **{cat}**")
            st.info(f"Dimensões do Invólucro aplicadas: {alt} x {larg} x {prof} mm")

    with tab3:
        if 'res' in st.session_state:
            r = st.session_state['res']
            st.subheader(f"Relatório Técnico - {r['Equip']}")
            def export_pdf():
                buf = io.BytesIO(); c = canvas.Canvas(buf, pagesize=A4)
                c.drawString(100, 800, "LAUDO TÉCNICO DE ARCO ELÉTRICO - NBR 17227")
                c.drawString(100, 780, f"Equipamento: {r['Equip']}")
                c.drawString(100, 760, f"Tensão: {r['Voc']} kV | Energia: {r['E']:.4f} cal/cm2")
                c.drawString(100, 740, f"Ia: {r['Ia']:.5f} kA | Ia_min: {r['IaMin']:.5f} kA")
                c.drawString(100, 720, f"DLA: {r['DLA']:.0f} mm | Vestimenta: {r['Cat']}")
                c.save(); return buf.getvalue()
            st.download_button("📩 Baixar Relatório em PDF", export_pdf(), "laudo_arco.pdf", "application/pdf")

if __name__ == "__main__":
    main()
