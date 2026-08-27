import pandas as pd
import streamlit as st
from src.tools.planejamento_pdi import planejamento_pdi

def render_etapa02():
    col1, col2 = st.columns([1, 4])
    with col1:        
        st.image("logo/Logo_PDI-on-Track-02.png", width=125)
    with col2:
        st.title("Etapa 02 - Verificar serviços lançados no DATASUL")
        
    st.subheader("➡️ TABELA PLANEJAMENTO PDI")

    # 1. Carrega os dados filtrados da Etapa 01
    df_inserir = None
    if st.session_state.get("df_pendente_de_prep") is not None:
        df_inserir = st.session_state.df_pendente_de_prep[
            st.session_state.df_pendente_de_prep['PREPARAÇÃO'].notnull()
        ].reset_index(drop=True)

    st.write("Total com preparação do cliente")

    if df_inserir is None:
        st.write("🔄️ Aguardando Etapa 1")
    else:
        st.write(df_inserir)

    # 2. Upload direto do arquivo ES0564A
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
            st.write(df_es0564a)
        except pd.errors.EmptyDataError:
            st.error("O arquivo CSV enviado está vazio ou não contém colunas legíveis.")

    # 3. Leitura da tabela de cadastro de serviços
    df_servicos = pd.read_excel("./cadastro_servicos.xlsx")

    # 4. Execução simples e sem travas de estado
    if df_inserir is not None and df_es0564a is not None and df_servicos is not None:
        df_pendentes, df_lancados, df_planejamento_lançados_v2_nulos, df_planejamento_lançados_v4 = planejamento_pdi(
            df_inserir,
            df_es0564a,
            df_servicos
        )

        # Salva o DataFrame final apenas para consulta de outras páginas
        st.session_state.df_planejamento_lançados_v4 = df_planejamento_lançados_v4

        # Exibição
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