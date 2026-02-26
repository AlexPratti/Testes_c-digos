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

    # Base de dados (Tabela 1 e Tabela 3 da imagem)
    equipamentos = {
        "CCM 15 kV": {"gap": 152.0, "dist": 914.4, "dims": {"914,4 x 914,4 x 914,4": [914.4, 914.4, 914.4]}},
        "Conjunto de manobra 15 kV": {"gap": 152.0, "dist": 914.4, "dims": {"1143 x 762 x 762": [1143.0, 762.0, 762.0]}},
        "CCM 5 kV": {"gap": 104.0, "dist": 914.4, "dims": {"660,4 x 660,4 x 660,4": [660.4, 660.4, 660.4]}},
        "Conjunto de manobra 5 kV": {
            "gap": 104.0, "dist": 914.4, 
            "dims": {
                "914,4 x 914,4 x 914,4": [914.4, 914.4, 914.4],
                "1143 x 762 x 762": [1143.0, 762.0, 762.0]
            }
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
        
        # Criação da lista dinâmica de opções de dimensões para o equipamento selecionado
        opcoes_dim = list(info["dims"].keys()) + ["Inserir Dimensões Manualmente"]
        
        escolha_final_dim = st.selectbox(f"Selecione as dimensões para {equip_escolhido}:", options=opcoes_dim)
        
        # Variáveis de dimensão
        if escolha_final_dim == "Inserir Dimensões Manualmente":
            st.info("Digite os valores personalizados:")
            col_m1, col_m2, col_m3 = st.columns(3)
            alt = col_m1.number_input("Altura [A] (mm)", value=500.0)
            larg = col_m2.number_input("Largura [L] (mm)", value=500.0)
            prof = col_m3.number_input("Profundidade [P] (mm)", value=500.0)
        else:
            alt, larg, prof = info["dims"][escolha_final_dim]

        # Parâmetros automáticos de Gap e Distância
        gap_auto = info["gap"]
        dist_auto = info["dist"]
        dim_consolidada = f"{alt} x {larg} x {prof} mm"

        st.markdown("---")
        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("GAP sugerido (mm)", f"{gap_auto}")
        c2.metric("D_trab sugerida (mm)", f"{dist_auto}")
        c3.metric("Altura (A)", f"{alt} mm")
        c4.metric("Largura (L)", f"{larg} mm")
        c5.metric("Profundidade (P)", f"{prof} mm")

    # --- ABA 2: CÁLCULOS E RESULTADOS ---
    with tab2:
        col1, col2, col3 = st.columns(3)
        v_oc = col1.number_input("Tensão Voc (kV)", value=13.80, format="%.2f")
        gap_g = col2.number_input("Gap G (mm)", value=float(gap_auto), format="%.2f")
        tempo_t = col3.number_input("Tempo T (ms)", value=488.0, format="%.2f")

        col4, col5, col6 = st.columns(3)
        i_bf = col4.number_input("Curto Ibf (kA)", value=4.85, format="%.2f")
        dist_d = col5.number_input("Distância D (mm)", value=float(dist_auto), format="%.2f")

        if st.button("Calcular Resultados"):
            # Coeficientes
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
            
            # Cálculo do fator de caixa (CF)
            ees = (alt/25.4 + larg/25.4) / 2.0
            cf = -0.0003*ees**2 + 0.03441*ees + 0.4325
            
            ia_sts = [calc_ia_step(i_bf, gap_g, k_ia[v]) for v in [600, 2700, 14300]]
            en_sts = [calc_en_step(ia, i_bf, gap_g, dist_d, tempo_t, k_en[v], cf) for ia, v in zip(ia_sts, [600, 2700, 14300])]
            dl_sts = [calc_dla_step(ia, i_bf, gap_g, tempo_t, k_en[v], cf) for ia, v in zip(ia_sts, [600, 2700, 14300])]

            ia_f = interpolar(v_oc, *ia_sts)
            e_jcm2 = interpolar(v_oc, *en_sts)
            e_calcm2 = e_jcm2 / 4.184
            dla_f = interpolar(v_oc, *dl_sts)
            ia_min = ia_f * (1 - 0.5*(-0.0001*v_oc**2 + 0.0022*v_oc + 0.02))

            cat = "CAT 2" if e_calcm2 <= 8 else "CAT 4" if e_calcm2 <= 40 else "EXTREMO RISCO"
            
            st.session_state['res'] = {
                "Ia": ia_f, "IaMin": ia_min, "E_cal": e_calcm2, "E_joule": e_jcm2, "DLA": dla_f, 
                "Cat": cat, "Voc": v_oc, "Equip": equip_escolhido, "Gap": gap_g, "Dist": dist_d, 
                "Dim": dim_consolidada, "Ibf": i_bf, "Tempo": tempo_t
            }
            
            st.divider()
            r1, r2, r3, r4 = st.columns(4)
            r1.metric("Ia Final (kA)", f"{ia_f:.4f}")
            r2.metric("Energia (cal/cm²)", f"{e_calcm2:.2f}")
            r3.metric("Energia (J/cm²)", f"{e_jcm2:.2f}")
            r4.metric("Fronteira (mm)", f"{dla_f:.0f}")
            st.warning(f"🛡️ Vestimenta Sugerida: **{cat}**")

    # --- ABA 3: RELATÓRIO ---
    with tab3:
        if 'res' in st.session_state:
            r = st.session_state['res']
            st.subheader(f"Gerar Relatório Técnico - {r['Equip']}")
            
            def export_pdf():
                buf = io.BytesIO()
                c = canvas.Canvas(buf, pagesize=A4)
                
                # Cabeçalho Profissional
                c.setStrokeColor(colors.black); c.rect(1*cm, 25.5*cm, 19*cm, 3*cm)
                c.setFont("Helvetica-Bold", 14); c.drawString(7.5*cm, 27.5*cm, "LAUDO TÉCNICO DE ARCO ELÉTRICO")
                c.setFont("Helvetica", 9); c.drawString(7.5*cm, 27*cm, "NBR 17227:2025 | NR-10 | IEEE 1584")
                c.drawString(1.5*cm, 26.5*cm, "[ ESPAÇO PARA LOGOTIPO DA EMPRESA ]")
                
                # Dados de Entrada
                c.setFont("Helvetica-Bold", 11); c.drawString(1*cm, 24.5*cm, "1. DADOS DE ENTRADA")
                c.setFont("Helvetica", 10); y = 23.8*cm
                c.drawString(1.5*cm, y, f"Equipamento: {r['Equip']}") ; y -= 0.6*cm
                c.drawString(1.5*cm, y, f"GAP: {r['Gap']} mm | Distância de Trabalho [D]: {r['Dist']} mm") ; y -= 0.6*cm
                c.drawString(1.5*cm, y, f"Dimensões do Invólucro [AxLxP]: {r['Dim']}") ; y -= 0.6*cm
                c.drawString(1.5*cm, y, f"Tensão: {r['Voc']} kV | Curto (Ibf): {r['Ibf']} kA") ; y -= 1.2*cm

                # Resultados Técnicos
                c.setFont("Helvetica-Bold", 11); c.drawString(1*cm, y, "2. RESULTADOS TÉCNICOS")
                c.setFont("Helvetica", 10); y -= 0.8*cm
                c.drawString(1.5*cm, y, f"Corrente Arco (Iarc): {r['Ia']:.4f} kA | Reduzida: {r['IaMin']:.4f} kA") ; y -= 0.6*cm
                c.drawString(1.5*cm, y, f"Energia Incidente: {r['E_cal']:.4f} cal/cm² ({r['E_joule']:.4f} J/cm²)") ; y -= 0.6*cm
                c.drawString(1.5*cm, y, f"Distância Segura (DLA): {r['DLA']:.0f} mm") ; y -= 0.6*cm
                c.setFont("Helvetica-Bold", 10); c.drawString(1.5*cm, y, f"Vestimenta Recomendada: {r['Cat']}") ; y -= 1.5*cm

                # Texto de Segurança NR-10
                c.setFont("Helvetica-Bold", 11); c.drawString(1*cm, y, "3. PRESCRIÇÕES NR-10")
                c.setFont("Helvetica", 9); y -= 0.8*cm
                c.drawString(1.5*cm, y, "EPIs Obrigatórios: Capacete c/ viseira, Protetor Auditivo, Luvas Isolantes.") ; y -= 0.5*cm
                c.drawString(1.5*cm, y, f"Vestimenta: Nível de proteção mínima necessária: {r['E_cal']:.2f} cal/cm².") ; y -= 0.5*cm
                c.drawString(1.5*cm, y, "Atenção: Operação proibida acima de 40 cal/cm² sem procedimentos especiais.") ; y -= 1*cm
                
                # Assinatura
                c.line(5*cm, 3*cm, 16*cm, 3*cm)
                c.setFont("Helvetica", 8); c.drawString(8.5*cm, 2.6*cm, "Engenheiro Responsável / CREA")
                
                c.save(); return buf.getvalue()
                
            st.download_button("📩 Baixar Laudo Profissional (PDF)", export_pdf(), "laudo_arco_profissional.pdf", "application/pdf")
        else:
            st.info("⚠️ Execute o cálculo para gerar o relatório.")

if __name__ == "__main__":
    main()
