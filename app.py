import streamlit as st
import pandas as pd
import plotly.express as px
from azure.storage.blob import BlobServiceClient
from io import StringIO
import os

st.set_page_config(layout="wide")
st.title("🌱 Painel de Ocorrências Ambientais - IBAMA")

# ==============================
# 🔐 Configuração do Azure Blob
# ==============================

connect_str = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
container_name = "dadosibama"
gold_files = {
    "Ocorrências por UF": "gold/ocorrencias_por_uf.csv",
    "Ocorrências por Tipo de Evento": "gold/ocorrencias_por_tipo_evento.csv",
    "Ocorrências por Tipo de Dano": "gold/ocorrencias_por_dano.csv",
    "Ocorrências com Produto Perigoso": "gold/ocorrencias_produto_perigoso.csv",
    "Instituições mais Atuantes": "gold/instituicoes_mais_atuantes.csv",
    "Ocorrências por Dia da Semana": "gold/ocorrencias_por_dia_semana.csv"
}

@st.cache_data
def carregar_csv_gold(blob_name):
    blob_service_client = BlobServiceClient.from_connection_string(connect_str)
    blob_client = blob_service_client.get_container_client(container_name).get_blob_client(blob_name)
    blob_data = blob_client.download_blob().readall()
    return pd.read_csv(StringIO(blob_data.decode("utf-8")), sep=",", encoding="utf-8", low_memory=False)

# ==============================
# 📊 Visualizações Interativas
# ==============================

aba = st.sidebar.selectbox("Escolha o relatório", list(gold_files.keys()))

try:
    df = carregar_csv_gold(gold_files[aba])
    st.subheader(f"📄 {aba}")
    st.dataframe(df)

    # Gráficos automáticos
    col_label = df.columns[0]
    col_value = df.columns[1]

    fig = px.bar(df, x=col_label, y=col_value, title=aba, labels={col_label: col_label, col_value: "Quantidade"})
    st.plotly_chart(fig, use_container_width=True)

except Exception as e:
    st.error(f"Erro ao carregar os dados da camada gold: {e}")
