import pandas as pd
import streamlit as st
import numpy as np
from src.tools.pendente_preparacao import pendente_preparacao

def render_etapa01():
    col1, col2 = st.columns([1,4])
    with col1:        
        st.image("logo/Logo_PDI-on-Track-02.png", width=125)
    with col2:
        st.title("Etapa 01 - Carregar dados do Cliente")
    st.subheader("TABELA PRODUÇÃO INTERNA")

# CARREGAR ARQUIVO CLIENTE
    with st.container():
        st.subheader("➡️ RELATORIO CLIENTE EMAIL")
        
        if "arquivo_email" not in st.session_state:
            st.session_state.arquivo_email = None
        
        if "df_email" not in st.session_state:
            st.session_state.df_email = None
            
        st.session_state.arquivo_email = st.file_uploader(
        "Selecione o arquivo Excel.\n Arquivos aceitos:'xlsx','xls'",
            type=["xlsx","xls"],
            key="upload_email"
        )
                
        if st.session_state.arquivo_email is not None:
            st.session_state.df_email = pd.read_excel(st.session_state.arquivo_email)
            
# TRATAMENTO DOS DADOS DO EXCEL, FILTRA COLUNAS EM BRANCO E PREPARA PARA DATASET
            st.session_state.df_email = st.session_state.df_email[st.session_state.df_email.iloc[:,6].notna()]
            colunas = st.session_state.df_email.iloc[0].tolist()
            st.session_state.df_email.columns = colunas
            st.session_state.df_email = st.session_state.df_email.iloc[1:].reset_index(drop=True)

        
        if st.session_state.df_email is not None:
            st.write(st.session_state.df_email)

        
# CARREGAR ARQUIVO DATASUL ES0988
    with st.container():
        st.subheader("➡️ RELATORIO DATASUL ES0988")

        if "arquivo_es0988" not in st.session_state:
            st.session_state.arquivo_es0988 = None

        if "df_es0988" not in st.session_state:
            st.session_state.df_es0988 = None

        if "df_pendente_de_prep" not in st.session_state:
            st.session_state.df_pendente_de_prep = None

        if "df_cliente" not in st.session_state:
            st.session_state.df_cliente = None
            
        st.session_state.arquivo_es0988 = st.file_uploader(
        "Selecione o arquivo Excel.\n Arquivos aceitos:'xlsx','xls'",
            type=["xlsx","xls"],
            key="upload_es0988"
        )
            
        if st.session_state.arquivo_es0988 is not None:
            st.session_state.df_es0988 = pd.read_excel(st.session_state.arquivo_es0988)
            
        if st.session_state.df_es0988 is not None:
            st.write(st.session_state.df_es0988)
    
# CARREGAR APLICAÇÃO PENDENTE DE PREPARAÇÃO
    if (st.session_state.df_email is not None 
        and st.session_state.df_es0988 is not None):
                
        st.subheader("VERIFICA SE EXISTE PREPARAÇÃO NO EMAIL DO CLIENTE")
        st.session_state.df_pendente_de_prep, st.session_state.df_cliente = pendente_preparacao(
                st.session_state.df_email,
                st.session_state.df_es0988
            )
        df_pendente_de_prep = st.session_state.df_pendente_de_prep
        
    # VISUALIAÇÕES DO RESULTADO
        df_inserir_datasul = df_pendente_de_prep[df_pendente_de_prep['PREPARAÇÃO'].notnull()].reset_index(drop=True)
        df_sem_preparacao = df_pendente_de_prep[df_pendente_de_prep['PREPARAÇÃO'].isnull()].reset_index(drop=True)
        
        qtd_nulos_inserir_datasul = len(df_inserir_datasul['PREPARAÇÃO'])
        qtd_nulos_sem_preparacao = len(df_sem_preparacao['PREPARAÇÃO'])

        st.write(f"Total com preparação do cliente: {qtd_nulos_inserir_datasul}")
        st.write(df_inserir_datasul)
        st.write(f"Total sem preparação do cliente: {qtd_nulos_sem_preparacao}")
        st.write(df_sem_preparacao)



        