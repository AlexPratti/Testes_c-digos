# --- ADICIONAR ESTA FUNÇÃO AO SEU CÓDIGO ---
def calcular_var_cf(v_oc, k_var):
    # Coeficientes k11 a k17 da Tabela 5 da NBR 17227
    k11, k12, k13, k14, k15, k16, k17 = k_var
    
    # Equação 2: VarCf é um polinômio de 6º grau baseado na Tensão Voc
    var_cf = (k11 * v_oc**6 + k12 * v_oc**5 + k13 * v_oc**4 + 
              k14 * v_oc**3 + k15 * v_oc**2 + k16 * v_oc + k17)
    return var_cf

# --- DENTRO DA FUNÇÃO MAIN, ADICIONE OS COEFICIENTES E O TESTE ---
# Coeficientes Tabela 5 - Todos os eletrodos (VCB, VCBB, HCB, VOA, HOA) usam estes:
k_tabela5 = [0, 0, 0, 0, -0.0001, 0.0022, 0.02]

st.divider()
st.header("Parte 2: Fator de Variação (Eq. 2)")

v_sistema = st.number_input("Tensão do Sistema Voc (kV)", value=13.80, format="%.2f")

if st.button("Testar Parte 2"):
    # 1. Calculamos o VarCf
    var_cf = calcular_var_cf(v_sistema, k_tabela5)
    
    # 2. Para testar o I_a_min, precisamos do I_a_final (interpolação da Parte 1)
    # Supondo que você já tenha o 'ia_final' calculado da Parte 1:
    # ia_min = ia_final * (1 - 0.5 * var_cf)
    
    st.success(f"Fator VarCf calculado: {var_cf:.5f}")
    st.info(f"Nota: Se Voc=13.8kV, VarCf deve ser ~0.03132")

