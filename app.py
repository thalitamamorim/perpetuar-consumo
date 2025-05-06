import streamlit as st
import sqlite3
from datetime import datetime
from PIL import Image

# CONFIGURAÇÕES
st.set_page_config(
    page_title="Consumo - Restaurante Perpetuar", layout="centered")
logo = Image.open("Perpetuar.png")
st.image(logo, use_container_width=True)

# CONEXÃO COM O BANCO DE DADOS
conn = sqlite3.connect("restaurante.db")
cursor = conn.cursor()

# Criação das tabelas, se não existirem
cursor.execute("""
CREATE TABLE IF NOT EXISTS funcionarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL UNIQUE
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS consumo (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    funcionario_id INTEGER,
    item TEXT,
    valor REAL,
    data TEXT,
    FOREIGN KEY(funcionario_id) REFERENCES funcionarios(id)
)
""")
conn.commit()

# ITENS DISPONÍVEIS
ITENS = {
    "Café": 2.50,
    "Suco": 4.00,
    "Refrigerante": 5.00,
    "Salgado": 3.50,
    "Prato Feito": 15.00,
    "Sobremesa": 6.00
}

# PROTEÇÃO DE SENHA
menu = st.sidebar.radio("Acesso", ["Administrador", "Administrador Master"])

if menu == "Administrador":
    st.title("Painel do Administrador")

    # Cadastro de Funcionários
    novo_nome = st.text_input("Cadastrar novo funcionário")
    if st.button("Adicionar Funcionário"):
        if novo_nome:
            cursor.execute(
                "INSERT OR IGNORE INTO funcionarios (nome) VALUES (?)", (novo_nome,))
            conn.commit()
            st.success(f"{novo_nome} cadastrado com sucesso!")

    # Listar Funcionários
    cursor.execute("SELECT nome FROM funcionarios")
    funcionarios = cursor.fetchall()

    if funcionarios:
        funcionarios = [f[0] for f in funcionarios]
    else:
        funcionarios = []

    st.header("Registrar Consumo")
    if funcionarios:
        nome = st.selectbox("Selecionar Funcionário", funcionarios)
        item_escolhido = st.selectbox("Item Consumido", list(ITENS.keys()))
        data_hoje = datetime.today().strftime("%Y-%m-%d")
        valor = ITENS[item_escolhido]

        if st.button("Adicionar Consumo"):
            cursor.execute(
                "SELECT id FROM funcionarios WHERE nome = ?", (nome,))
            funcionario_id = cursor.fetchone()[0]
            cursor.execute("INSERT INTO consumo (funcionario_id, item, valor, data) VALUES (?, ?, ?, ?)",
                           (funcionario_id, item_escolhido, valor, data_hoje))
            conn.commit()
            st.success(
                f"{item_escolhido} (R$ {valor:.2f}) registrado para {nome} em {data_hoje}")

    # Histórico com opção de apagar item
    st.header("Consultar Histórico Individual")
    nome_busca = st.selectbox(
        "Selecionar funcionário para consulta", funcionarios, key="consulta")
    if nome_busca:
        cursor.execute("""
        SELECT c.item, c.valor, c.data
        FROM consumo c
        JOIN funcionarios f ON f.id = c.funcionario_id
        WHERE f.nome = ?
        """, (nome_busca,))
        historico = cursor.fetchall()

        if historico:
            for i, item in enumerate(historico):
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.write(f"- {item[2]}: {item[0]} (R$ {item[1]:.2f})")
                with col2:
                    if st.button("Apagar", key=f"{nome_busca}_{i}"):
                        cursor.execute("""
                        DELETE FROM consumo WHERE item = ? AND valor = ? AND data = ? AND funcionario_id = (
                            SELECT id FROM funcionarios WHERE nome = ?
                        )
                        """, (item[0], item[1], item[2], nome_busca))
                        conn.commit()
                        st.success("Item apagado com sucesso.")
                        st.stop()  # Substituído o rerun por st.stop()

elif menu == "Administrador Master":
    st.title("Painel Master")

    senha = st.text_input("Digite a senha de acesso:", type="password")
    if senha == "master123":  # Substitua pela sua senha segura
        st.success("Acesso autorizado.")

        # Totais por Funcionário
        st.header("Totais por Funcionário")
        cursor.execute("""
        SELECT f.nome, SUM(c.valor) 
        FROM funcionarios f 
        LEFT JOIN consumo c ON f.id = c.funcionario_id
        GROUP BY f.id
        """)
        totais = cursor.fetchall()

        total_geral = 0
        for nome, total in totais:
            total_geral += total
            st.write(f"**{nome}**: R$ {total:.2f}")

        st.header("Total Geral")
        st.subheader(f"R$ {total_geral:.2f}")

    elif senha:
        st.error("Senha incorreta.")

# Fechar a conexão ao final
conn.close()
