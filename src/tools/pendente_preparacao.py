import pandas as pd
import streamlit as st

def pendente_preparacao(df_cliente,df_datasul):
        
# ALTERA COLUNAS PARA MAIUSCULAS
    df_datasul = df_datasul.copy()
    df_cliente = df_cliente.copy()
        
    df_datasul.columns = [x.upper() for x in df_datasul.columns]
    df_cliente.columns = [x.upper() for x in df_cliente.columns]
    
#CONVERTE TIPOS DOS DADOS EM STRINGS
    for tab in [df_cliente,df_datasul]:
        for col in tab:
            tab[col] = tab[col].astype('str')
    
    df_cliente['CHASSI'] = df_cliente['CHASSI'].str.strip()

    df_cliente.rename(columns={
        "DT INCLUSÃO" : "DATA",
        "DESCRITIVO" : "ACESSORIO"
    },inplace=True)
    
    colunas_cliente =['CHASSI','DATA','ACESSORIO','OBSERVAÇÃO']

    df_cliente = df_cliente[colunas_cliente]
    
    colunas_datasul =['MODELO','CHASSI','N° DA O.S','DESCRIÇÃO CONCESSIONÁRIA','RECEB NF NO PDI']
    df_datasul = df_datasul[df_datasul['STATUS ATUAL']=='Pendente informação Preparação']
    df_datasul = df_datasul[colunas_datasul].reset_index(drop=True)
        
    
    df_pendente_de_prep = df_datasul.merge(df_cliente, \
       on=['CHASSI'],
       how='left')
    
    
    df_pendente_de_prep = df_pendente_de_prep[colunas_datasul+colunas_cliente[1:]]
    
    df_pendente_de_prep.rename(columns={'DATA':'DATA DE ENVIO DE PREPARAÇÃO',
                                        'ACESSORIO':'PREPARAÇÃO'
                                       }
                               ,inplace=True
                              )
    return df_pendente_de_prep, df_cliente




    