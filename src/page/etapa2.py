import pandas as pd
import numpy as np
import streamlit as st
from src.tools.planejamento_pdi import planejamento_pdi

def render_etapa02():
    col1, col2 = st.columns([1,4])
    with col1:        
        st.image("logo/Logo_PDI-on-Track-02.png", width=125)
    with col2:
        st.title("Etapa 02 - Verificar serviços lançados no DATASUL")
    st.subheader("➡️ TABELA PLANEJAMENTO PDI")


    if "df_inserir_datasul" not in st.session_state:
        st.session_state.df_inserir_datasul = None

    if st.session_state.df_pendente_de_prep is not None:
        st.session_state.df_inserir_datasul = st.session_state.df_pendente_de_prep[st.session_state.df_pendente_de_prep['PREPARAÇÃO'].notnull()].reset_index(drop=True)

    st.write("Total com preparação do cliente")

    if st.session_state.df_inserir_datasul is None:
        st.write("🔄️ Aguardando Etapa 1")
    elif st.session_state.df_inserir_datasul is not None:
        st.write(st.session_state.df_inserir_datasul)

    #LEITURA DO ARQUIVO EXCEL ES0564A e TABELA DE SERVIÇOS
    st.subheader("➡️ TABELA ES0564A")
    # 1. O key salva o arquivo enviado em st.session_state.arquivo_es0564a
    st.file_uploader(
        "Selecione o arquivo Excel.\n Arquivos aceitos:'csv'",
        type=["csv"],
        key="arquivo_es0564a"
    )

    # 2. Processa o arquivo apenas na primeira vez ou quando o arquivo muda
    if st.session_state.arquivo_es0564a is not None:
        if "df_es0564a" not in st.session_state or st.session_state.get("nome_ultimo_es0564a") != st.session_state.arquivo_es0564a.name:
            try:
                # Reset do ponteiro de leitura do arquivo
                st.session_state.arquivo_es0564a.seek(0)
                
                st.session_state.df_es0564a = pd.read_csv(
                    st.session_state.arquivo_es0564a,
                    encoding='ISO-8859-1',
                    sep=';'
                )
                st.session_state.nome_ultimo_es0564a = st.session_state.arquivo_es0564a.name

            except pd.errors.EmptyDataError:
                st.error("O arquivo CSV enviado está vazio ou não contém colunas legíveis.")
            
    else: 
        # Limpa a sessão se o arquivo for removido pelo usuário
        st.session_state.pop("df_es0564a",None)
        st.session_state.pop("nome_ultimo_es0564a", None)

    # 3. Exibe a tabela se ela existir na sessão
    if st.session_state.get("df_es0564a") is not None:
        st.write(st.session_state.df_es0564a)


# CARREGAR ARQUIVO SERVIÇOS
    if "df_servicos" not in st.session_state:
        st.session_state.df_servicos = None
        
    st.session_state.df_servicos = pd.read_excel("./cadastro_servicos.xlsx")
    
# CARREGAR APLICAÇÃO PLANEJAMENTO PDI
    if (st.session_state.get("df_inserir_datasul") is not None
        and st.session_state.get("df_es0564a") is not None
        and st.session_state.get("df_servicos") is not None):

        df_pendentes, df_lancados, df_planejamento_lançados_v2_nulos, df_planejamento_lançados_v4 = planejamento_pdi(
            st.session_state.df_inserir_datasul,
            st.session_state.df_es0564a,
            st.session_state.df_servicos
        )
    
        
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

    
# SALVAR SESSION_STATE PARA DEMAIS APLICAÇÕES E PAGINAS
        st.session_state.df_planejamento_lançados_v4 = df_planejamento_lançados_v4
    
















    

