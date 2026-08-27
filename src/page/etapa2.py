import pandas as pd
import streamlit as st
from src.tools.planejamento_pdi import planejamento_pdi

# 1. Caches para evitar re-leitura pesada de arquivos a cada renderização
@st.cache_data
def carregar_es0564a(file):
    file.seek(0)
    return pd.read_csv(file, encoding='ISO-8859-1', sep=';', low_memory=False)

@st.cache_data
def carregar_servicos(caminho):
    return pd.read_excel(caminho)

def render_etapa02():
    col1, col2 = st.columns([1, 4])
    with col1:        
        st.image("logo/Logo_PDI-on-Track-02.png", width=125)
    with col2:
        st.title("Etapa 02 - Verificar serviços lançados no DATASUL")
        
    st.subheader("➡️ TABELA PLANEJAMENTO PDI")

    # Carrega dados da Etapa 01
    df_inserir = None
    if st.session_state.get("df_pendente_de_prep") is not None:
        df_inserir = st.session_state.df_pendente_de_prep[
            st.session_state.df_pendente_de_prep['PREPARAÇÃO'].notnull()
        ].reset_index(drop=True)

    st.write("Total com preparação do cliente")

    if df_inserir is None:
        st.write("🔄️ Aguardando Etapa 1")
    else:
        st.dataframe(df_inserir.head(100), height=200, use_container_width=True)

    # 2. Upload leve com Cache do arquivo ES0564A
    st.subheader("➡️ TABELA ES0564A")
    arquivo_es0564a = st.file_uploader(
        "Selecione o arquivo CSV.\n Arquivos aceitos:'csv'",
        type=["csv"],
        key="uploader_es0564a"
    )

    df_es0564a = None
    if arquivo_es0564a is not None:
        try:
            # A função em cache lê o CSV sem travar a sessão
            df_es0564a = carregar_es0564a(arquivo_es0564a)
            st.success(f"Arquivo carregado com sucesso! Total de linhas: {len(df_es0564a)}")
            
            # Mostra apenas as primeiras 50 linhas para não derrubar a conexão WebSocket
            st.dataframe(df_es0564a.head(50), height=200, use_container_width=True)
        except Exception as e:
            st.error(f"Erro ao processar o arquivo CSV: {e}")

    # 3. Carregamento em cache do cadastro de serviços
    df_servicos = carregar_servicos("./cadastro_servicos.xlsx")

    # 4. Execução do Planejamento
    if df_inserir is not None and df_es0564a is not None and df_servicos is not None:
        with st.spinner("Processando cruzamento PDI..."):
            df_pendentes, df_lancados, df_planejamento_lançados_v2_nulos, df_planejamento_lançados_v4 = planejamento_pdi(
                df_inserir,
                df_es0564a,
                df_servicos
            )

        st.session_state.df_planejamento_lançados_v4 = df_planejamento_lançados_v4

        # Exibição otimizada com rolagem
        st.subheader("VEICULOS SEM LANÇAMENTOS NO DATASUL:")
        st.write(f"Quantidade: {len(df_pendentes)}")
        st.dataframe(df_pendentes, height=200, use_container_width=True)

        st.subheader('VEICULOS COM LANÇAMENTOS NO DATASUL:')
        st.write(f"Quantidade: {len(df_lancados)}")
        st.dataframe(df_lancados, height=200, use_container_width=True)

        st.subheader('DESCRIÇÃO NAO ENCONTRADA FAVOR CADASTRAR NA TABELA cadastro_serviços')
        st.dataframe(df_planejamento_lançados_v2_nulos, height=200, use_container_width=True)

        st.subheader('TABELA PARA CONFERENCIA DOS SERVIÇOS DATASUL E TABELA CLIENTE')
        st.dataframe(df_planejamento_lançados_v4, height=300, use_container_width=True)