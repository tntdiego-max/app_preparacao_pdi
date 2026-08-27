import pandas as pd
import streamlit as st

def planejamento_pdi(df_inserir_datasul,
                    df_es0564a,
                    df_servicos,
                    df_cliente=None):

    # 1. Trata cópias locais para EVITAR alterar o session_state diretamente
    df_es0564a = df_es0564a.copy()
    df_inserir_datasul = df_inserir_datasul.copy()
    df_servicos = df_servicos.copy()

    # Recupera df_cliente por parâmetro ou busca segura do session_state
    if df_cliente is None:
        df_cliente = st.session_state.get("df_cliente")

    # RELAÇÃO DE CHASSI LANÇADOS NO SISTEMA
    df_ls_chassi = df_inserir_datasul[['CHASSI']]
    
    # Tratamento sem inplace=True
    df_es0564a = df_es0564a.rename(columns={'Chassi': 'CHASSI'})
    if 'CHASSI' in df_es0564a.columns:
        df_es0564a['CHASSI'] = df_es0564a['CHASSI'].astype(str).str.strip()
    
    colunas_df_es0564a = ['CHASSI', 'OS PDI', 'Desc Cliente', 'Cliente']
    colunas_existentes = [c for c in colunas_df_es0564a if c in df_es0564a.columns]
    
    df_planejamento = df_ls_chassi.merge(
        df_es0564a[colunas_existentes].drop_duplicates(subset=['CHASSI', 'OS PDI']),
        on=['CHASSI'],
        how='left'
    )

    # VEICULOS SEM e COM LANÇAMENTO NO DATASUL
    df_planejamento_pendentes = df_planejamento[df_planejamento['OS PDI'].isnull()]
    df_planejamento_lançados = df_planejamento[df_planejamento['OS PDI'].notnull()].copy()

    # VEICULOS LANÇADOS NO DATASUL
    df_planejamento_lançados = df_planejamento_lançados.merge(
        df_inserir_datasul[['CHASSI', 'MODELO']],
        on=['CHASSI'],
        how='left'
    )

    # ALTERA NOME DA COLUNA
    df_planejamento_lançados = df_planejamento_lançados.rename(
        columns={'Desc Cliente': 'CLIENTE', 'Cliente': 'COD_CLIENTE'}
    )
    
    # CONVERTE COLUNAS COM TRATAMENTO DE VALORES NULOS (NaN)
    colunas_conversao = df_planejamento_lançados.select_dtypes('float').columns
    for col in colunas_conversao:
        df_planejamento_lançados[col] = (
            df_planejamento_lançados[col]
            .fillna(0)
            .astype('int64')
            .astype(str)
        )

    # MERGE TABELA PARA PEGAR SERVIÇOS LANÇADOS
    df_planejamento_lançados_v1 = df_planejamento_lançados.merge(
        df_es0564a[['CHASSI', 'Item']],
        on=['CHASSI'],
        how='left'
    )
    df_planejamento_lançados_v1['Item'] = df_planejamento_lançados_v1['Item'].astype(str)

    # REMOVER DUPLICADAS DOS CÓDIGOS DE SERVIÇOS
    df_servicos = df_servicos.drop_duplicates(subset='CODIGO')
    df_servicos['CODIGO'] = df_servicos['CODIGO'].astype(str)
    
    df_planejamento_lançados_v2 = df_planejamento_lançados_v1.merge(
        df_servicos[['CODIGO', 'DESCRICAO']].rename(columns={'CODIGO': 'Item'}),
        on=['Item'],
        how='left'
    )

    # ITEM NÃO ENCONTRADO
    df_planejamento_lançados_v2_nulos = df_planejamento_lançados_v2[
        df_planejamento_lançados_v2['DESCRICAO'].isnull()
    ]

    # PIVOT A LINHA EM COLUNA
    df_planejamento_lançados_v3 = df_planejamento_lançados_v2.pivot_table(
        index=['CHASSI', 'OS PDI', 'CLIENTE', 'COD_CLIENTE', 'MODELO'],
        columns='DESCRICAO',
        values='Item',
        aggfunc='first'
    ).reset_index()
    df_planejamento_lançados_v3.columns.name = None

    # MERGE SEGURO COM TABELA CLIENTE
    if df_cliente is not None and set(['CHASSI', 'ACESSORIO', 'OBSERVAÇÃO']).issubset(df_cliente.columns):
        df_planejamento_lançados_v4 = df_planejamento_lançados_v3.merge(
            df_cliente[['CHASSI', 'ACESSORIO', 'OBSERVAÇÃO']],
            on=['CHASSI'],
            how='left'
        )
    else:
        df_planejamento_lançados_v4 = df_planejamento_lançados_v3.copy()
        if 'ACESSORIO' not in df_planejamento_lançados_v4.columns:
            df_planejamento_lançados_v4['ACESSORIO'] = None
        if 'OBSERVAÇÃO' not in df_planejamento_lançados_v4.columns:
            df_planejamento_lançados_v4['OBSERVAÇÃO'] = None

    if "PLACA" not in df_planejamento_lançados_v4.columns:
        df_planejamento_lançados_v4["PLACA"] = None

    # REORGANIZAÇÃO DE COLUNAS
    colunas_desejadas = ['CHASSI', 'OS PDI', 'CLIENTE', 'COD_CLIENTE', 'MODELO', 'ACESSORIO', 'OBSERVAÇÃO', 'MANUAL', 'INSPEÇÃO', 'PLACA']
    existentes = [c for c in colunas_desejadas if c in df_planejamento_lançados_v4.columns]
    outras = [c for c in df_planejamento_lançados_v4.columns if c not in existentes]
    
    df_planejamento_lançados_v4 = df_planejamento_lançados_v4[existentes + outras]

    return df_planejamento_pendentes, df_planejamento_lançados, df_planejamento_lançados_v2_nulos, df_planejamento_lançados_v4