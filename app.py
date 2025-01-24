import streamlit as st
import pandas as pd
from datetime import date

# Configuração da Página
st.set_page_config(page_title="Captação de Pedidos", layout="wide")

# Dados iniciais
products = [
    {"code": "P001", "name": "Camiseta", "sizes": ["P", "M", "G"], "colors": ["Vermelho", "Azul"], "price": 50.0, "image": "https://luposport.vtexassets.com/arquivos/ids/225845-1200-auto?v=638621663186470000&width=1200&height=auto&aspect=true", "entry": "Entrada 1", "grade": {"P": 10, "M": 15, "G": 20}, "entry_date": "2025-02-01"},
    {"code": "P002", "name": "Calça", "sizes": ["38", "40", "42"], "colors": ["Preto", "Bege"], "price": 100.0, "image": "https://luposport.vtexassets.com/arquivos/ids/234606-1200-auto?v=638732387207030000&width=1200&height=auto&aspect=true", "entry": "Entrada 2", "grade": {"38": 5, "40": 10, "42": 15}, "entry_date": "2025-02-10"},
    {"code": "P003", "name": "Jaqueta", "sizes": ["M", "G"], "colors": ["Preto", "Azul"], "price": 200.0, "image": "https://luposport.vtexassets.com/arquivos/ids/230553-1200-auto?v=638621663905900000&width=1200&height=auto&aspect=true", "entry": "Entrada 3", "grade": {"M": 8, "G": 12}, "entry_date": "2025-02-20"}
]

product_variants = []
for product in products:
    for size in product["sizes"]:
        for color in product["colors"]:
            product_variants.append({
                "Imagem": product["image"],
                "Produto": product["name"],
                "Código": product["code"],
                "Tamanho": size,
                "Cor": color,
                "Preço": product["price"],
                "Entrada": product["entry"],
                "Grade": product["grade"][size],
                "Data de Entrada": product["entry_date"],
                "Quantidade": 0
            })

product_df = pd.DataFrame(product_variants)
product_df.sort_values(by=["Código", "Cor"], inplace=True)

franchisees = [
    {"code": "F001", "store_name": "Loja Centro"},
    {"code": "F002", "store_name": "Loja Norte"},
    {"code": "F003", "store_name": "Loja Sul"}
]
franchisee_df = pd.DataFrame(franchisees)

payment_conditions = ["À vista", "30 dias", "60 dias", "90 dias"]

def main_page():
    st.title("Captação de Pedidos - Franqueados")

    # Seleção de franqueado e condição de pagamento
    selected_franchisee = st.selectbox(
        "Selecione o Franqueado",
        franchisee_df["code"] + " - " + franchisee_df["store_name"]
    )
    franchisee_code = selected_franchisee.split(" - ")[0]

    payment_condition = st.selectbox("Condição de Pagamento", payment_conditions)

    st.header("Seleção de Produtos")

    if "orders" not in st.session_state:
        st.session_state.orders = []

    # Construção da tabela de produtos
    quantities = []
    for _, row in product_df.iterrows():
        cols = st.columns([2, 2, 1, 1, 2, 2, 3, 2])
        with cols[0]:
            st.image(row["Imagem"], width=75)
        with cols[1]:
            st.text(row["Produto"])
        with cols[2]:
            st.text(row["Código"])
        with cols[3]:
            st.text(row["Tamanho"])
        with cols[4]:
            st.text(row["Cor"])
        with cols[5]:
            st.text(row["Entrada"])
        with cols[6]:
            st.text(f'Grade sugerida: {row["Grade"]}')
        with cols[7]:
            qty_key = f"qty_{row['Código']}_{row['Tamanho']}_{row['Cor']}"
            quantity = st.number_input(
                "Quantidade",
                min_value=0,
                value=st.session_state.get(qty_key, 0),
                key=qty_key
            )
            quantities.append(quantity)

    product_df["Quantidade"] = quantities

    # Botões separados
    col1, col2 = st.columns(2, 2)
    with col1:
        if st.button("Adicionar ao Pedido"):
            st.session_state.orders = []
            for _, row in product_df.iterrows():
                if row["Quantidade"] > 0:
                    price = row["Preço"] * 0.94 if payment_condition == "À vista" else row["Preço"]
                    total_value = row["Quantidade"] * price
                    st.session_state.orders.append({
                        "codigo_franqueado": franchisee_code,
                        "condicao_pagamento": payment_condition,
                        "data_faturamento": date.today(),
                        "numero_entrada": row["Entrada"],
                        "codigo_produto": row["Código"],
                        "tamanho_cor": f"{row['Tamanho']} - {row['Cor']}",
                        "quantidade": row["Quantidade"],
                        "valor_total": total_value
                    })
    with col2:
        if st.button("Conferir Pedido"):
            st.session_state.page = "Conferência e Finalização"

def review_page():
    st.title("Conferência do Pedido")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.session_state.orders:
            df_orders = pd.DataFrame(st.session_state.orders)
    
            total_pieces = df_orders["quantidade"].sum()
            total_value = df_orders["valor_total"].sum()
    
            st.subheader("Resumo do Pedido")
            cols = st.columns(2)
            with cols[0]:
                st.metric(label="Total de Peças", value=total_pieces)
            with cols[1]:
                st.metric(label="Valor Total (R$)", value=f"{total_value:.2f}")
    
            selected_franchisee = df_orders.iloc[0]["codigo_franqueado"]
            franchisee_name = franchisee_df.loc[franchisee_df["code"] == selected_franchisee, "store_name"].values[0]
            st.write(f"**Franqueado:** {selected_franchisee} - {franchisee_name}")
            st.write(f"**Condição de Pagamento:** {df_orders.iloc[0]['condicao_pagamento']}")
    
            # Resumo por entrada
            st.subheader("Resumo por Entrada")
            summary_by_entry = df_orders.groupby("numero_entrada")[["quantidade", "valor_total"]].sum()
            summary_by_entry["Data de Faturamento"] = summary_by_entry.index.map(
                lambda x: next((p["entry_date"] for p in products if p["entry"] == x), "N/A")
            )
            st.dataframe(summary_by_entry, use_container_width=True)
            
         # Exibição da tabela detalhada
        st.subheader("Detalhamento do Pedido")
        display_df = df_orders.drop(columns=["codigo_franqueado", "condicao_pagamento", "data_faturamento"])
        display_df.reset_index(drop=True, inplace=True)
        st.dataframe(display_df, use_container_width=True)

        # Botões separados
        col1, col2 = st.columns(2, 2)
        with col1:
            if st.button("Voltar e Corrigir"):
                for order in st.session_state.orders:
                    qty_key = f"qty_{order['codigo_produto']}_{order['tamanho_cor'].replace(' - ', '_')}"
                    st.session_state[qty_key] = order["quantidade"]
                st.session_state.page = "Captação de Pedidos"

        with col2:
            if st.button("Finalizar Pedido e Gerar CSV"):
                csv_file = "pedido_franqueado.csv"
                df_orders.to_csv(csv_file, index=False, sep=";", encoding="utf-8-sig")
                st.success(f"Arquivo CSV '{csv_file}' gerado com sucesso!")
    
                with open(csv_file, "rb") as file:
                    st.download_button(
                        label="Baixar CSV",
                        data=file,
                        file_name=csv_file,
                        mime="text/csv"
                    )
        else:
            st.info("Nenhum pedido adicionado ainda.")

if "page" not in st.session_state:
    st.session_state.page = "Captação de Pedidos"

if st.session_state.page == "Captação de Pedidos":
    main_page()
elif st.session_state.page == "Conferência e Finalização":
    review_page()
