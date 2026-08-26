import pandas as pd

def scripts(df_servicos_com_baixa, df_servicos_pendentes):
    df_servicos_com_baixa_script = pd.DataFrame(df_servicos_com_baixa).iloc[:,:-1]
    df_servicos_pendentes_script = pd.DataFrame(df_servicos_pendentes).iloc[:,:-1]
    
    from datetime import datetime 
    agora = datetime.now().strftime("%d/%m/%Y")
    
    #df de serviços pendentes para lançamento de pendencia de acessorio
    #df_servicos_com_baixa_script['DATA'] = agora
    if not df_servicos_com_baixa_script.empty:
        df_servicos_com_baixa_script = df_servicos_com_baixa_script[['OS PDI','SERVIÇO','Item']].copy()
        df_servicos_com_baixa_script['SCRIPT'] = df_servicos_com_baixa_script.astype(str).apply(lambda x: ','.join(x)+';',axis=1)

    if not df_servicos_pendentes_script.empty:
        #df de serviços em estoque para lançamento e alocação do estoque na OS
        df_servicos_pendentes_script['DATA'] = agora
        df_servicos_pendentes_script = df_servicos_pendentes_script[['OS PDI','SERVIÇO','DATA']].copy()
        df_servicos_pendentes_script['SCRIPT'] = df_servicos_pendentes_script.astype(str).apply(lambda x: ','.join(x)+';',axis=1)
        
    return df_servicos_com_baixa_script, df_servicos_pendentes_script
