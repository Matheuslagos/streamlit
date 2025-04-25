import streamlit as st
import pandas as pd
import plotly.express as px
from azure.storage.blob import BlobServiceClient
from io import StringIO
import os
st.title("📊 Painel de Autos de Infração - IBAMA")

# ==============================
# 🔐 Configurações do Azure Blob
# ==============================

connect_str = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
container_name = "gold"
blob_name = "relatorio_acidentes_ambientais.csv"  # ou "relatorio_estatistico_embargos.csv"
blob_service_client = BlobServiceClient.from_connection_string(connect_str)
containers = blob_service_client.list_containers()
st.write("Containers disponíveis:")
for c in containers:
    st.write("-", c.name)
@st.cache_data
def carregar_dados_azure():
    blob_service_client = BlobServiceClient.from_connection_string(connect_str)
    blob_client = blob_service_client.get_container_client(container_name).get_blob_client(blob_name)
    blob_data = blob_client.download_blob().readall()
    return pd.read_csv(StringIO(blob_data.decode("utf-8")), sep=",", encoding="utf-8", low_memory=False)

try:
    df = carregar_dados_azure()

    st.subheader("👀 Visualização dos primeiros registros")
    st.dataframe(df.head())

    # ==========================
    # 🔢 Estatísticas Gerais
    # ==========================
    st.subheader("📈 Estatísticas Descritivas")

    # Converter colunas para numéricas
    df["val_auto_infracao"] = pd.to_numeric(df["val_auto_infracao"], errors="coerce")
    df["qt_area"] = pd.to_numeric(df["qt_area"], errors="coerce")

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Valor total das multas", f"R$ {df['val_auto_infracao'].sum():,.2f}")
        st.metric("Média de valor por infração", f"R$ {df['val_auto_infracao'].mean():,.2f}")
    with col2:
        st.metric("Área total autuada", f"{df['qt_area'].sum():,.2f} ha")
        st.metric("Média de área por infração", f"{df['qt_area'].mean():,.2f} ha")

    # ==========================
    # 📍 Distribuição por UF
    # ==========================
    st.subheader("📌 Distribuição por Estado (UF)")
    uf_counts = df["uf"].value_counts().reset_index()
    uf_counts.columns = ["UF", "Quantidade"]

    fig_uf = px.bar(uf_counts, x="UF", y="Quantidade", title="Quantidade de Autos por UF")
    st.plotly_chart(fig_uf)

    # ==========================
    # 🏙️ Municípios com mais autos
    # ==========================
    st.subheader("🏙️ Top 10 Municípios com mais autos")
    mun_counts = df["municipio"].value_counts().nlargest(10).reset_index()
    mun_counts.columns = ["Município", "Quantidade"]

    fig_mun = px.bar(mun_counts, x="Município", y="Quantidade", title="Top 10 Municípios com mais Autos de Infração")
    st.plotly_chart(fig_mun)

    # ==========================
    # 🧾 Tipos de Multa
    # ==========================
    st.subheader("🧾 Tipos de Multa Aplicadas")
    tipo_multa = df["tipo_multa"].value_counts().reset_index()
    tipo_multa.columns = ["Tipo de Multa", "Contagem"]
    st.dataframe(tipo_multa)

except Exception as e:
    st.error(f"Erro ao carregar os dados do Azure Blob Storage: {e}")
