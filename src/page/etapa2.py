import pandas as pd
import numpy as np
import streamlit as st
from src.tools.planejamento_pdi import planejamento_pdi

# 1. Função com Cache para ler o Excel do disco apenas UMA vez
@st.cache_data
def carregar_cadastro_servicos(caminho):
    return pd.read_excel(caminho)

def render_etapa02():
    col1, col2 = st.columns([1, 4])
    with col1:        
        st.image("logo/Logo_PDI-on-Track-02.png", width=125)
    with col2:
        st.title("Etapa 02 - Verificar serviços lançados no DATASUL")
        
    st.subheader("➡️ TABELA PLANEJAMENTO PDI")

    # 2. Carregamento seguro da Etapa 01
    if st.session_state.get("df_pendente_de_prep") is not None:
        st.session_state.df_inserir_datasul = st.session_state.df_pendente_de_prep[
            st.session_state.df_pendente_de_prep['PREPARAÇÃO'].notnull()
        ].reset_index(drop=True)

    st.write("Total com preparação do cliente")

    if st.session_state.get("df_inserir_datasul") is None:
        st.write("🔄️ Aguardando Etapa 1")
    else:
        st.write(st.session_state.df_inserir_datasul)

    # 3. Upload e Leitura do arquivo ES0564A
    st.subheader("➡️ TABELA ES0564A")
    st.file_uploader(
        "Selecione o arquivo CSV.\n Arquivos aceitos:'csv'",
        type=["csv"],
        key="arquivo_es0564a"
    )

    if st.session_state.arquivo_es0564a is not None:
        nome_atual = st.session_state.arquivo_es0564a.name
        nome_anterior = st.session_state.get("nome_ultimo_es0564a")
        
        # Lê o CSV apenas se a chave não existir ou se o arquivo enviado mudar
        if "df_es0564a" not in st.session_state or nome_anterior != nome_atual:
            try:
                st.session_state.arquivo_es0564a.seek(0)
                st.session_state.df_es0564a = pd.read_csv(
                    st.session_state.arquivo_es0564a,
                    encoding='ISO-8859-1',
                    sep=';'
                )
                st.session_state.nome_ultimo_es0564a = nome_atual
                
                # LIMPEZA OBRIGATÓRIA: Reseta o resultado antigo para forçar novo cálculo
                st.session_state.pop("df_planejamento_lançados_v4", None)
                st.session_state.pop("df_pendentes", None)
                st.session_state.pop("df_lancados", None)
                st.session_state.pop("df_planejamento_lançados_v2_nulos", None)
            except pd.errors.EmptyDataError:
                st.error("O arquivo CSV enviado está vazio ou não contém colunas legíveis.")
    else: 
        # Limpa todas as variáveis caso o arquivo seja removido pelo usuário
        st.session_state.pop("df_es0564a", None)
        st.session_state.pop("nome_ultimo_es0564a", None)
        st.session_state.pop("df_planejamento_lançados_v4", None)
        st.session_state.pop("df_pendentes", None)
        st.session_state.pop("df_lancados", None)
        st.session_state.pop("df_planejamento_lançados_v2_nulos", None)

    if st.session_state.get("df_es0564a") is not None:
        st.write(st.session_state.df_es0564a)

    # 4. Carrega a tabela de serviços via Cache
    if st.session_state.get("df_servicos") is None:
        st.session_state.df_servicos = carregar_cadastro_servicos("./cadastro_servicos.xlsx")

    # 5. Processamento PDI
    df_inserir = st.session_state.get("df_inserir_datasul")
    df_es0564a = st.session_state.get("df_es0564a")
    df_servicos = st.session_state.get("df_servicos")

    if df_inserir is not None and df_es0564a is not None and df_servicos is not None:

        # Executa o algoritmo pesado apenas 1 vez por alteração de arquivo
        if "df_planejamento_lançados_v4" not in st.session_state:
            with st.spinner("Processando planejamento PDI... Aguarde..."):
                res_pendentes, res_lancados, res_nulos, res_v4 = planejamento_pdi(
                    df_inserir,
                    df_es0564a,
                    df_servicos
                )
                st.session_state.df_pendentes = res_pendentes
                st.session_state.df_lancados = res_lancados
                st.session_state.df_planejamento_lançados_v2_nulos = res_nulos
                st.session_state.df_planejamento_lançados_v4 = res_v4

        # Exibição dos dados salvos no session_state
        st.subheader("VEICULOS SEM LANÇAMENTOS NO DATASUL:")
        st.write(f"Quantidade: {len(st.session_state.df_pendentes)}")
        st.write(st.session_state.df_pendentes)

        st.subheader('VEICULOS COM LANÇAMENTOS NO DATASUL:')
        st.write(f"Quantidade: {len(st.session_state.df_lancados)}")
        st.write(st.session_state.df_lancados)

        st.subheader('DESCRIÇÃO NAO ENCONTRADA FAVOR CADASTRAR NA TABELA cadastro_serviços')
        st.write(st.session_state.df_planejamento_lançados_v2_nulos)

        st.subheader('TABELA PARA CONFERENCIA DOS SERVIÇOS DATASUL E TABELA CLIENTE')
        st.write(st.session_state.df_planejamento_lançados_v4)