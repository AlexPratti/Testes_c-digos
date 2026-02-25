import tkinter as tk
from tkinter import messagebox, ttk

def calcular():
    equip = combo_equip.get().lower()
    tensao = combo_tensao.get().lower()
    
    # Base de dados (conforme sua imagem)
    tabela = {
        ("ccm", "15 kv"): 914.4,
        ("conjunto de manobra", "15 kv"): 914.4,
        ("ccm", "5 kv"): 914.4,
        ("conjunto de manobra", "5 kv"): 914.4,
        ("ccm e painel raso de bt", "bt"): 457.2,
        ("ccm e painel típico de bt", "bt"): 457.2,
        ("conjunto de manobra bt", "bt"): 609.6,
        ("caixa de junção de cabos", "bt"): 457.2
    }
    
    resultado = tabela.get((equip, tensao))
    
    if resultado:
        lbl_resultado.config(text=f"Distância: {resultado} mm", fg="blue")
    else:
        messagebox.showwarning("Aviso", "Combinação não encontrada na tabela.")

# Configuração da Janela Principal
janela = tk.Tk()
janela.title("Calculadora de Distância de Trabalho")
janela.geometry("400x250")

# Labels e Campos de Seleção (Combobox)
tk.Label(janela, text="Selecione o Equipamento:").pack(pady=5)
combo_equip = ttk.Combobox(janela, width=35, values=[
    "CCM", "Conjunto de manobra", "CCM e painel raso de BT", 
    "CCM e painel típico de BT", "Conjunto de manobra BT", "Caixa de junção de cabos"
])
combo_equip.pack()

tk.Label(janela, text="Selecione a Classe de Tensão:").pack(pady=5)
combo_tensao = ttk.Combobox(janela, width=15, values=["15 kV", "5 kV", "BT"])
combo_tensao.pack()

# Botão de Calcular
btn_calc = tk.Button(janela, text="Verificar Distância", command=calcular, bg="#4CAF50", fg="white")
btn_calc.pack(pady=20)

# Exibição do Resultado
lbl_resultado = tk.Label(janela, text="", font=("Arial", 12, "bold"))
lbl_resultado.pack()

janela.mainloop()
