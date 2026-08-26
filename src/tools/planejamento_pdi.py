import pandas as pd
import streamlit as st

def planejamento_pdi(df_inserir_datasul,
                     df_es0564a,
                     df_servicos):

#RELAÇÃO DE CHASSI LANÇADOS NO SISTEMA
    df_ls_chassi = df_inserir_datasul[['CHASSI']]
    
    colunas_df_es0564a = ['CHASSI', 'OS PDI','Desc Cliente','Cliente']
    df_es0564a.rename(columns={'Chassi':'CHASSI'},inplace=True)
    df_es0564a['CHASSI'] = df_es0564a['CHASSI'].str.strip()
    
    df_planejamento = df_ls_chassi.merge(df_es0564a[colunas_df_es0564a].drop_duplicates(subset=['CHASSI','OS PDI']),
                                         on=['CHASSI'],
                                         how='left'
                                        )

#VEICULOS SEM e COM LANÇAMENTO NO DATASUL
    df_planejamento_pendentes = df_planejamento[df_planejamento['OS PDI'].isnull()]
    df_planejamento_lançados = df_planejamento[df_planejamento['OS PDI'].notnull()]

#VEICULOS LANÇADOS NO DATASUL
    df_planejamento_lançados = df_planejamento_lançados.merge(df_inserir_datasul[['CHASSI','MODELO']],
                                   on=['CHASSI'],
                                   how='left'
                                  )

#ALTERA NOME DA COLUNA
    df_planejamento_lançados.rename(columns={'Desc Cliente':'CLIENTE',
                                             'Cliente':'COD_CLIENTE'}
                                   ,inplace=True)
    
#CONVERTE COLUNAS PARA STRING
    colunas_conversao = df_planejamento_lançados.select_dtypes('float').columns
    for col in colunas_conversao:
        df_planejamento_lançados[col] = df_planejamento_lançados[col].astype('int').astype('str')
    


#MERGE TABELA df_planejamento_lançados PARA ESO564A PARA PEGAR SERVIÇOS LANÇADOS
    df_planejamento_lançados_v1 = df_planejamento_lançados.merge(df_es0564a[['CHASSI','Item']],
                                                                 on=['CHASSI'],
                                                                 how='left')
    
    df_planejamento_lançados_v1['Item'] = df_planejamento_lançados_v1['Item'].astype(str)
    
    
#REMOVER DUPLICADAS DOS CODIGO DE SERVIÇOS E CONVERTE COLUNA PARA STRING
    df_servicos = df_servicos.drop_duplicates(subset='CODIGO')
    df_servicos['CODIGO'] = df_servicos['CODIGO'].astype(str)
    
    df_planejamento_lançados_v2 = df_planejamento_lançados_v1.merge(df_servicos[['CODIGO','DESCRICAO']].rename(columns={'CODIGO':'Item'}),
                                                                 on=['Item'],
                                                                 how='left')
    
#ITEM NAO ENCONTRADO FAVOR CADASTRAR
    df_planejamento_lançados_v2_nulos = df_planejamento_lançados_v2[df_planejamento_lançados_v2['DESCRICAO'].isnull()]
    
#PIVOT A LINHA EM COLUNA
    df_planejamento_lançados_v3 = df_planejamento_lançados_v2.pivot_table(
                                            index=['CHASSI','OS PDI','CLIENTE','COD_CLIENTE','MODELO'],
                                            columns='DESCRICAO',
                                            values='Item',
                                            aggfunc='first').reset_index()
    df_planejamento_lançados_v3.columns.name = None


#ORDENAÇÃO DAS COLUNAS
    colunas_ordenacao = ['CHASSI', 'OS PDI', 'CLIENTE', 'COD_CLIENTE', 'MODELO','ACESSORIO', 'OBSERVAÇÃO']
    colunas_extra = ['MANUAL', 'INSPEÇÃO', 'PLACA']
    
# Garante que as colunas existam antes de tentar ordenar
    colunas_ordenacao_existentes = [c for c in colunas_ordenacao if c in df_planejamento_lançados_v3.columns]
    colunas_extra_existentes = [c for c in colunas_extra if c in df_planejamento_lançados_v3.columns]
    
# Pega todas as outras colunas que não estão nas listas acima
    outras_colunas = [
        c for c in df_planejamento_lançados_v3.columns 
        if c not in colunas_ordenacao_existentes + colunas_extra_existentes
    ]
    
# Reorganiza a ordem final
    nova_ordem = colunas_ordenacao + colunas_extra_existentes + outras_colunas
    
    df_planejamento_lançados_v4 = df_planejamento_lançados_v3.merge(st.session_state.df_cliente[['CHASSI', 'ACESSORIO', 'OBSERVAÇÃO']], left_on=['CHASSI'], right_on=['CHASSI'], how='left')

# Reorganiza o DataFrame mantendo as colunas desejadas primeiro
    df_planejamento_lançados_v4 = df_planejamento_lançados_v4[nova_ordem]
    
    if "PLACA" not in df_planejamento_lançados_v4.columns:
        df_planejamento_lançados_v4["PLACA"] = None
    
    return df_planejamento_pendentes, df_planejamento_lançados, df_planejamento_lançados_v2_nulos, df_planejamento_lançados_v4









    