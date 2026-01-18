import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# ==============================================================================
# 1. FUNÇÃO DE GERAÇÃO DE DADOS SIMULADOS (MOCK DATA)
#    - Esta função simula o carregamento dos seus dados.
#    - SUBSTITUA ESTA FUNÇÃO pela sua lógica de carregamento de dados reais.
# ==============================================================================
def generate_mock_data():
    # 1. df_produtos (Products)
    produtos = {
        "id_produto": [101, 102, 103, 104, 105, 106, 107, 108, 109, 110],
        "nome_produto": [
            "Laptop Pro X", "Monitor Ultra HD", "Teclado Mecânico", "Mouse Sem Fio",
            "Webcam 4K", "Headset Gamer", "SSD 1TB", "Roteador Wi-Fi 6",
            "Impressora Laser", "Cadeira Ergonômica"
        ],
        "preco_venda": [4500.00, 1800.00, 350.00, 150.00, 500.00, 400.00, 600.00, 750.00, 1200.00, 900.00],
        "preco_custo": [3000.00, 1200.00, 150.00, 50.00, 200.00, 180.00, 300.00, 350.00, 500.00, 400.00],
    }
    df_produtos = pd.DataFrame(produtos)

    # 2. df_clientes (Clients)
    clientes = {
        "id_cliente": [201, 202, 203, 204, 205, 206, 207, 208, 209, 210],
        "nome_cliente": [
            "Ana Silva", "Bruno Costa", "Carla Dias", "Daniel Esteves",
            "Elisa Ferreira", "Fábio Gomes", "Helena Ivo", "Igor Jorge",
            "Joana Lima", "Luís Martins"
        ],
        "cidade": [
            "Lisboa", "Porto", "Coimbra", "Lisboa", "Faro", "Porto",
            "Braga", "Coimbra", "Lisboa", "Faro"
        ],
    }
    df_clientes = pd.DataFrame(clientes)

    # 3. df_vendedores (Sellers)
    vendedores = {
        "id_vendedor": [301, 302, 303, 304, 305],
        "nome_vendedor": ["Maria", "João", "Sofia", "Pedro", "Inês"],
    }
    df_vendedores = pd.DataFrame(vendedores)

    # 4. df_vendas (Sales)
    start_date = datetime(2024, 1, 1)
    end_date = datetime(2024, 12, 31)
    num_vendas = 1000

    data_venda = [start_date + timedelta(days=np.random.randint(0, (end_date - start_date).days)) for _ in range(num_vendas)]
    id_produto = np.random.choice(df_produtos["id_produto"], num_vendas, p=[0.15, 0.10, 0.10, 0.10, 0.05, 0.10, 0.10, 0.10, 0.05, 0.15])
    id_cliente = np.random.choice(df_clientes["id_cliente"], num_vendas)
    id_vendedor = np.random.choice(df_vendedores["id_vendedor"], num_vendas, p=[0.3, 0.2, 0.2, 0.15, 0.15])
    quantidade = np.random.randint(1, 5, num_vendas)

    df_vendas = pd.DataFrame({
        "data_venda": data_venda,
        "id_produto": id_produto,
        "id_cliente": id_cliente,
        "id_vendedor": id_vendedor,
        "quantidade": quantidade,
    })

    # Tratamento de tipos (como no código original)
    df_vendas["data_venda"] = pd.to_datetime(df_vendas["data_venda"])
    df_vendas["quantidade"] = pd.to_numeric(df_vendas["quantidade"])
    
    df_produtos["preco_venda"] = pd.to_numeric(df_produtos["preco_venda"])
    df_produtos["preco_custo"] = pd.to_numeric(df_produtos["preco_custo"])

    return df_vendas, df_produtos, df_clientes, df_vendedores

# ==============================================================================
# 2. CONFIGURAÇÃO DA PÁGINA
# ==============================================================================
st.set_page_config(
    page_title="Dashboard Interativo de Análise de Vendas",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==============================================================================
# 3. CARREGAMENTO E PROCESSAMENTO DE DADOS (CACHE)
# ==============================================================================
@st.cache_data
def load_and_process_data():
    # --------------------------------------------------------------------------
    # PONTO DE SUBSTITUIÇÃO:
    # Se quiser usar dados reais, substitua a linha abaixo pela sua lógica.
    # Exemplo para carregar CSVs:
    # df_vendas = pd.read_csv("vendas.csv")
    # df_produtos = pd.read_csv("produtos.csv")
    # ...
    # --------------------------------------------------------------------------
    df_vendas, df_produtos, df_clientes, df_vendedores = generate_mock_data()

    # 4) MERGES (RELACIONAMENTOS)
    df = df_vendas.merge(df_produtos, on="id_produto", how="left")
    df = df.merge(df_clientes, on="id_cliente", how="left")
    df = df.merge(df_vendedores, on="id_vendedor", how="left")

    # 5) CÁLCULO DE MÉTRICAS
    df["faturamento"] = df["quantidade"] * df["preco_venda"]
    df["lucro"] = df["quantidade"] * (df["preco_venda"] - df["preco_custo"])
    
    # Converter 'data_venda' para o formato de data para Plotly
    df["data_venda"] = pd.to_datetime(df["data_venda"])
    df["mes_ano"] = df["data_venda"].dt.to_period("M").astype(str)
    
    return df

df_main = load_and_process_data()

# ==============================================================================
# 4. SIDEBAR (FILTROS)
# ==============================================================================
st.sidebar.header("Filtros")

# Filtro de Mês/Ano
meses_disponiveis = sorted(df_main["mes_ano"].unique())
meses_selecionados = st.sidebar.multiselect(
    "Selecione o Mês/Ano:",
    options=meses_disponiveis,
    default=meses_disponiveis
)

# Filtro de Cidade
cidades_disponiveis = sorted(df_main["cidade"].unique())
cidades_selecionadas = st.sidebar.multiselect(
    "Selecione a Cidade:",
    options=cidades_disponiveis,
    default=cidades_disponiveis
)

# Filtro de Vendedor
vendedores_disponiveis = sorted(df_main["nome_vendedor"].unique())
vendedores_selecionados = st.sidebar.multiselect(
    "Selecione o Vendedor:",
    options=vendedores_disponiveis,
    default=vendedores_disponiveis
)

# Aplicar filtros
df_filtered = df_main[
    df_main["mes_ano"].isin(meses_selecionados) &
    df_main["cidade"].isin(cidades_selecionadas) &
    df_main["nome_vendedor"].isin(vendedores_selecionados)
]

if df_filtered.empty:
    st.warning("Nenhum dado corresponde aos filtros selecionados. Por favor, ajuste os filtros.")
    st.stop()

# ==============================================================================
# 5. TÍTULO PRINCIPAL E MÉTRICAS CHAVE (KPIs)
# ==============================================================================
st.title("📊 Dashboard Interativo de Análise de Vendas")
st.markdown("Análise de **Faturamento**, **Lucro** e **Volume de Vendas**.")

# MÉTRICAS CHAVE (KPIs)
total_faturamento = df_filtered["faturamento"].sum()
total_lucro = df_filtered["lucro"].sum()
total_vendas = df_filtered["quantidade"].sum()

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        label="Faturamento Total",
        value=f"R$ {total_faturamento:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    )

with col2:
    st.metric(
        label="Lucro Total",
        value=f"R$ {total_lucro:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    )

with col3:
    st.metric(
        label="Volume Total de Vendas",
        value=f"{total_vendas:,.0f} Unidades".replace(",", ".")
    )

st.markdown("---")

# ==============================================================================
# 6. GRÁFICOS (VISUALIZAÇÕES)
# ==============================================================================

# 6.1 Faturamento Mensal (Gráfico de Barras)
st.subheader("Faturamento Mensal")
vendas_mes = df_filtered.groupby("mes_ano")["faturamento"].sum().reset_index()
vendas_mes.columns = ["Mês/Ano", "Faturamento"]

fig_faturamento_mensal = px.bar(
    vendas_mes,
    x="Mês/Ano",
    y="Faturamento",
    title="Faturamento Mensal",
    labels={"Faturamento": "Faturamento (R$)"},
    color="Faturamento",
    color_continuous_scale=px.colors.sequential.Plasma
)
fig_faturamento_mensal.update_layout(xaxis_tickangle=-45)
st.plotly_chart(fig_faturamento_mensal, use_container_width=True) # Manter por enquanto, mas Streamlit sugere width='stretch'

# 6.2 Top 5 Produtos por Faturamento
st.subheader("Análise de Produtos e Vendedores")
col_prod, col_vend = st.columns(2)

with col_prod:
    produto_fat = df_filtered.groupby("nome_produto")["faturamento"].sum().sort_values(ascending=False).head(5).reset_index()
    produto_fat.columns = ["Produto", "Faturamento"]
    
    fig_produto_fat = px.bar(
        produto_fat,
        x="Faturamento",
        y="Produto",
        orientation="h",
        title="Top 5 Produtos por Faturamento",
        labels={"Faturamento": "Faturamento (R$)"},
        color="Faturamento",
        color_continuous_scale=px.colors.sequential.Viridis
    )
    fig_produto_fat.update_layout(yaxis={'categoryorder':'total ascending'})
    st.plotly_chart(fig_produto_fat, use_container_width=True) # Manter por enquanto, mas Streamlit sugere width='stretch'

# 6.3 Vendedor com Maior Faturamento
with col_vend:
    vendedor_fat = df_filtered.groupby("nome_vendedor")["faturamento"].sum().sort_values(ascending=False).head(5).reset_index()
    vendedor_fat.columns = ["Vendedor", "Faturamento"]
    
    fig_vendedor_fat = px.pie(
        vendedor_fat,
        values="Faturamento",
        names="Vendedor",
        title="Faturamento por Vendedor (Top 5)",
        hole=.3
    )
    st.plotly_chart(fig_vendedor_fat, use_container_width=True) # Manter por enquanto, mas Streamlit sugere width='stretch'

# 6.4 Top 5 Clientes por Volume de Compras
st.subheader("Análise de Clientes e Cidades")
col_cli, col_cid = st.columns(2)

with col_cli:
    top_clientes = df_filtered.groupby("nome_cliente")["quantidade"].sum().sort_values(ascending=False).head(5).reset_index()
    top_clientes.columns = ["Cliente", "Quantidade Comprada"]
    
    fig_top_clientes = px.bar(
        top_clientes,
        x="Quantidade Comprada",
        y="Cliente",
        orientation="h",
        title="Top 5 Clientes por Volume de Compras",
        labels={"Quantidade Comprada": "Quantidade Comprada (Unidades)"},
        color="Quantidade Comprada",
        color_continuous_scale=px.colors.sequential.Sunset
    )
    fig_top_clientes.update_layout(yaxis={'categoryorder':'total ascending'})
    st.plotly_chart(fig_top_clientes, use_container_width=True) # Manter por enquanto, mas Streamlit sugere width='stretch'

# 6.5 Cidade com Maior Número de Compras
with col_cid:
    cidade_compras = df_filtered["cidade"].value_counts().reset_index()
    cidade_compras.columns = ["Cidade", "Número de Compras"]
    
    fig_cidade_compras = px.bar(
        cidade_compras,
        x="Cidade",
        y="Número de Compras",
        title="Número de Compras por Cidade",
        labels={"Número de Compras": "Total de Transações"},
        color="Número de Compras",
        color_continuous_scale=px.colors.sequential.Agsunset
    )
    st.plotly_chart(fig_cidade_compras, use_container_width=True) # Manter por enquanto, mas Streamlit sugere width='stretch'

# ==============================================================================
# 7. EXIBIÇÃO DE DADOS BRUTOS (OPCIONAL) E INFORMAÇÃO DE DADOS
# ==============================================================================
if st.checkbox("Mostrar Dados Brutos"):
    st.subheader("Dados Brutos (Filtrados)")
    st.dataframe(df_filtered)

st.sidebar.markdown("---")
st.sidebar.info(
    "**Nota:** Este dashboard está a usar um **conjunto de dados simulado** (mock dataset) para demonstrar a funcionalidade interativa. "
    "Para usar os seus dados reais, edite a função `load_and_process_data()` no código."
)
