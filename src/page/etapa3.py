import pandas as pd
import numpy as np
import streamlit as st
from src.tools.estoque import estoque
from src.tools.scripts import scripts


def render_etapa03():
    col1, col2 = st.columns([1,4])
    with col1:
        st.image("logo/Logo_PDI-on-Track-02.png", width=125)
    with col2:
        st.title("Etapa 03 - Verificar Estoque")
    st.subheader("TABELA ESTOQUE")

# VARIAVEIS DE SESSION_STATE
#LEITURA DO ARQUIVO EXCEL ESTOQUE e TABELA DE SERVIÇOS
    st.session_state.cod_servicos = pd.read_excel("./cod_serviços.xlsx")

    if "arquivo_estoque" not in st.session_state:
        st.session_state.arquivo_estoque = None

    if "df_estoque" not in st.session_state:
        st.session_state.df_estoque = None

# CARREGAR ARQUIVO ES0564A
    st.session_state.arquivo_estoque = st.file_uploader(
        "Selecione o arquivo Excel.\n Arquivos aceitos:'xlsx'",
        type=["xlsx"],
        key="upload_estoque"
    )
    if st.session_state.arquivo_estoque is not None:
        st.session_state.df_estoque = pd.read_excel(st.session_state.arquivo_estoque)

#CARREGAR APLICAÇÃO DE ESTOQUE
    if (st.session_state.cod_servicos is not None
        and st.session_state.df_estoque is not None
        and st.session_state.df_planejamento_lançados_v4 is not None
        and st.session_state.get("df_servicos") is not None
       ):
        (df_estoque, 
         df_com_placa_v1, 
         df_sem_placa_v1,
         df_servicos_com_baixa,
         df_servicos_pendentes) = estoque(
            st.session_state.cod_servicos, 
            st.session_state.df_estoque,
            st.session_state.df_planejamento_lançados_v4,
            st.session_state.df_servicos)

# VISUALIZAR ESTOQUE ATUAL
        st.subheader("ESTOQUE ATUAL")
        st.write(df_estoque)

        st.subheader('➡️ PLANEJAMENTO COM PLACA')
        st.write('➡️ STATUS EM ESTOQUE E SERVIÇOS BASICOS')
        st.write(df_com_placa_v1[df_com_placa_v1['status_atual']
            .isin(["em estoque","servico basico"])]
            .dropna(axis=1, how='all'))

        st.write('➡️ STATUS PENDENTE DE ACESSORIO')
        st.write(df_com_placa_v1[df_com_placa_v1['status_atual']
            .isin(["pendente de acessorio"])]
            .dropna(axis=1, how='all'))

        st.subheader('➡️ PLANEJAMENTO SEM PLACA')
        st.write('➡️ STATUS EM ESTOQUE E SERVIÇOS BASICOS')
        st.write(df_sem_placa_v1[df_sem_placa_v1['status_atual']
            .isin(["em estoque","servico basico"])]
            .dropna(axis=1, how='all'))

        st.write('➡️ STATUS PENDENTE DE ACESSORIO')
        st.write(df_sem_placa_v1[df_sem_placa_v1['status_atual']
            .isin(["pendente de acessorio"])]
            .dropna(axis=1, how='all'))


        st.subheader("📋 CRIAR SCRIPT VEICULOS COM PLACA EM ESTOQUE")
        (df_servicos_com_baixa_v1, 
         df_servicos_pendentes_v1) = scripts(st.session_state.df_servicos_com_baixa,
                                          st.session_state.df_servicos_pendentes)
        
        st.write("➡️ SCRIPT PARA LOCAÇÃO DO ESTOQUE")
        st.write(df_servicos_com_baixa)
        st.write(df_servicos_com_baixa_v1)
        st.write("➡️ SCRIPT OS COM PENDENCIAS")
        st.write(df_servicos_pendentes)
        st.write(df_servicos_pendentes_v1)















    