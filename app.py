import streamlit as st
import json
from pathlib import Path
from datetime import datetime
from PIL import Image

# ---------- CONFIGURAÇÕES ----------
st.set_page_config(
    page_title="Consumo - Restaurante Perpetuar", layout="centered")

# ---------- IMAGEM ----------
logo = Image.open("Perpetuar.png")
st.image(logo, use_column_width=True)

# ---------- DADOS ----------
DATA_FILE = Path("consumo_data.json")

ITENS = {
    "Café": 2.50,
    "Suco": 4.00,
    "Refrigerante": 5.00,
    "Salgado": 3.50,
    "Prato Feito": 15.00,
    "Sobremesa": 6.00
}

if DATA_FILE.exists():
    with open(DATA_FILE, "r") as f:
        consumo_data = json.load(f)
else:
    consumo_data = {}

# ---------- REGISTRO DE CONSUMO ----------
st.header("Registrar Consumo")

nome = st.text_input("Nome do Funcionário")
item_escolhido = st.selectbox("Item Consumido", list(ITENS.keys()))
data_hoje = datetime.today().strftime("%Y-%m-%d")
valor = ITENS[item_escolhido]

if st.button("Adicionar Consumo"):
    if nome:
        entrada = {"item": item_escolhido, "valor": valor, "data": data_hoje}
        if nome in consumo_data:
            consumo_data[nome].append(entrada)
        else:
            consumo_data[nome] = [entrada]
        with open(DATA_FILE, "w") as f:
            json.dump(consumo_data, f)
        st.success(
            f"{item_escolhido} (R$ {valor:.2f}) registrado para {nome} em {data_hoje}")
    else:
        st.error("Digite o nome do funcionário.")

# ---------- TOTAIS ----------
st.header("Totais por Funcionário")
for nome, registros in consumo_data.items():
    total = sum(item["valor"] for item in registros)
    st.write(f"**{nome}**: R$ {total:.2f}")

# ---------- HISTÓRICO INDIVIDUAL ----------
st.header("Consultar Histórico Individual")
nome_busca = st.text_input("Consultar histórico de:", key="consulta")
if nome_busca and nome_busca in consumo_data:
    st.subheader(f"Histórico de {nome_busca}")
    for item in consumo_data[nome_busca]:
        st.write(f"- {item['data']}: {item['item']} (R$ {item['valor']:.2f})")
elif nome_busca:
    st.warning("Funcionário não encontrado.")
