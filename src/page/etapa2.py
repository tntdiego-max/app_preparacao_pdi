import pandas as pd
import numpy as np
import streamlit as st
from src.tools.planejamento_pdi import planejamento_pdi

# 1. O Cache nativo memoriza o resultado e zera o tempo de execução no re-render
@st.cache_data
def executar_planejamento(df_inserir, df_es0564a, df_servicos):
    return planejamento_pdi(df_inserir, df_es0564a, df_servicos)

def render_etapa02():
    col1, col2 = st.columns([1, 4])
    with col1:        
        st.image("logo/Logo_PDI-on-Track-02.png", width=125)
    with col2:
        st.title("Etapa 02 - Verificar serviços lançados no DATASUL")
        
    st.subheader("➡️ TABELA PLANEJAMENTO PDI")

    # 2. Carrega dados da Etapa 1
    df_inserir = None
    if st.session_state.get("df_pendente_de_prep") is not None:
        df_inserir = st.session_state.df_pendente_de_prep[
            st.session_state.df_pendente_de_prep['PREPARAÇÃO'].notnull()
        ].reset_index(drop=True)
        st.session_state.df_inserir_datasul = df_inserir

    st.write("Total com preparação do cliente")

    if df_inserir is None:
        st.write("🔄️ Aguardando Etapa 1")
    else:
        st.write(df_inserir)

    # 3. Upload simples do CSV (Sem hacks de sessão)
    st.subheader("➡️ TABELA ES0564A")
    arquivo_es0564a = st.file_uploader(
        "Selecione o arquivo CSV.\n Arquivos aceitos:'csv'",
        type=["csv"]
    )

    df_es0564a = None
    if arquivo_es0564a is not None:
        try:
            arquivo_es0564a.seek(0)
            df_es0564a = pd.read_csv(arquivo_es0564a, encoding='ISO-8859-1', sep=';')
            st.session_state.df_es0564a = df_es0564a
            st.write(df_es0564a)
        except pd.errors.EmptyDataError:
            st.error("O arquivo CSV enviado está vazio ou não contém colunas legíveis.")

    # 4. Leitura da tabela de serviços
    df_servicos = st.session_state.get("df_servicos")
    if df_servicos is None:
        df_servicos = pd.read_excel("./cadastro_servicos.xlsx")
        st.session_state.df_servicos = df_servicos

    # 5. Processamento PDI limpo (Sem loops de estado)
    if df_inserir is not None and df_es0564a is not None and df_servicos is not None:
        
        with st.spinner("Processando planejamento PDI..."):
            df_pendentes, df_lancados, df_planejamento_lançados_v2_nulos, df_planejamento_lançados_v4 = executar_planejamento(
                df_inserir,
                df_es0564a,
                df_servicos
            )
            # Salva o resultado final para que outras páginas possam ler se preciso
            st.session_state.df_planejamento_lançados_v4 = df_planejamento_lançados_v4

        # Exibição imediata dos DataFrames
        st.subheader("VEICULOS SEM LANÇAMENTOS NO DATASUL:")
        st.write(f"Quantidade: {len(df_pendentes)}")
        st.write(df_pendentes)

        st.subheader('VEICULOS COM LANÇAMENTOS NO DATASUL:')
        st.write(f"Quantidade: {len(df_lancados)}")
        st.write(df_lancados)

        st.subheader('DESCRIÇÃO NAO ENCONTRADA FAVOR CADASTRAR NA TABELA cadastro_serviços')
        st.write(df_planejamento_lançados_v2_nulos)

        st.subheader('TABELA PARA CONFERENCIA DOS SERVIÇOS DATASUL E TABELA CLIENTE')
        st.write(df_planejamento_lançados_v4)