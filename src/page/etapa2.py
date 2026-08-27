import pandas as pd
import streamlit as st
from src.tools.planejamento_pdi import planejamento_pdi

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

    # 1. Carrega e persiste dados da Etapa 01
    if st.session_state.get("df_pendente_de_prep") is not None:
        st.session_state.df_inserir_datasul = st.session_state.df_pendente_de_prep[
            st.session_state.df_pendente_de_prep['PREPARAÇÃO'].notnull()
        ].reset_index(drop=True)

    df_inserir = st.session_state.get("df_inserir_datasul")

    st.write("Total com preparação do cliente")

    if df_inserir is None:
        st.write("🔄️ Aguardando Etapa 1")
    else:
        st.dataframe(df_inserir.head(100), height=200, use_container_width=True)

    # 2. Upload e persistência do arquivo ES0564A
    st.subheader("➡️ TABELA ES0564A")
    arquivo_es0564a = st.file_uploader(
        "Selecione o arquivo CSV.\n Arquivos aceitos:'csv'",
        type=["csv"],
        key="uploader_es0564a"
    )

    if arquivo_es0564a is not None:
        try:
            # Lê e grava na sessão
            st.session_state.df_es0564a = carregar_es0564a(arquivo_es0564a)
        except Exception as e:
            st.error(f"Erro ao processar o arquivo CSV: {e}")
    
    df_es0564a = st.session_state.get("df_es0564a")
    if df_es0564a is not None:
        st.success(f"Arquivo carregado com sucesso! Total de linhas: {len(df_es0564a)}")
        st.dataframe(df_es0564a.head(50), height=200, use_container_width=True)

    # 3. Carregamento e persistência do cadastro de serviços
    df_servicos = carregar_servicos("./cadastro_servicos.xlsx")
    st.session_state.df_servicos = df_servicos

    # 4. Processamento único e leitura mantida na sessão
    if df_inserir is not None and df_es0564a is not None and df_servicos is not None:
        
        # Executa a função apenas se o cálculo ainda NÃO existir na sessão
        if "df_planejamento_lançados_v4" not in st.session_state:
            with st.spinner("Processando cruzamento PDI..."):
                (
                    st.session_state.df_pendentes,
                    st.session_state.df_lancados,
                    st.session_state.df_planejamento_lançados_v2_nulos,
                    st.session_state.df_planejamento_lançados_v4
                ) = planejamento_pdi(df_inserir, df_es0564a, df_servicos)

        # Exibe os dados sempre vindos da sessão
        st.subheader("VEICULOS SEM LANÇAMENTOS NO DATASUL:")
        st.write(f"Quantidade: {len(st.session_state.df_pendentes)}")
        st.dataframe(st.session_state.df_pendentes, height=200, use_container_width=True)

        st.subheader('VEICULOS COM LANÇAMENTOS NO DATASUL:')
        st.write(f"Quantidade: {len(st.session_state.df_lancados)}")
        st.dataframe(st.session_state.df_lancados, height=200, use_container_width=True)

        st.subheader('DESCRIÇÃO NAO ENCONTRADA FAVOR CADASTRAR NA TABELA cadastro_serviços')
        st.dataframe(st.session_state.df_planejamento_lançados_v2_nulos, height=200, use_container_width=True)

        st.subheader('TABELA PARA CONFERENCIA DOS SERVIÇOS DATASUL E TABELA CLIENTE')
        st.dataframe(st.session_state.df_planejamento_lançados_v4, height=300, use_container_width=True)