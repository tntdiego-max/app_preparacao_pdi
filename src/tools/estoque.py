import pandas as pd
import streamlit as st

def estoque(
    df_cod_servicos, 
    df_estoque,
    df_planejamento_lançados_v4,
    df_servicos
):

    # ===============================
    # 1️⃣ NORMALIZAÇÃO
    # ===============================
    df_cod_servicos['ESTOQUE'] = df_cod_servicos['ESTOQUE'].astype('Int64')
    for col in df_cod_servicos.columns:
        df_cod_servicos[col] = df_cod_servicos[col].astype(str)

    colunas_estoque = list(df_estoque.loc[9])
    df_estoque.columns = colunas_estoque
    df_estoque = (
        df_estoque
        .dropna(subset=['Nome Cliente', 'Localizacao', 'Saldo Disponivel'])[1:]
        .reset_index(drop=True)
    )

    for col in df_estoque.columns:
        df_estoque[col] = df_estoque[col].astype(str)

    df_estoque['Saldo Disponivel'] = df_estoque['Saldo Disponivel'].astype(int)

    colunas_filtrar = [
        'Item', 'Descricao Item', 'Cod.Cliente',
        'Nome Cliente', 'Saldo Disponivel'
    ]

    df_estoque_base = (
        df_estoque[colunas_filtrar]
        .groupby(colunas_filtrar[:-1])['Saldo Disponivel']
        .sum()
        .reset_index()
    )

    # ===============================
    # 2️⃣ SESSION STATE (RESET CORRETO)
    # ===============================
    st.session_state.df_estoque_v1 = df_estoque_base.copy()
    st.session_state.df_servicos_pendentes = []
    st.session_state.df_servicos_com_baixa = []

    df_estoque_v1 = st.session_state.df_estoque_v1

    # ===============================
    # 3️⃣ FILTROS
    # ===============================
    df_com_placa = df_planejamento_lançados_v4[
        df_planejamento_lançados_v4.PLACA.notnull()
    ].copy()

    df_sem_placa = df_planejamento_lançados_v4[
        df_planejamento_lançados_v4.PLACA.isnull()
    ].copy()

    lista_nao_considerar = (
        df_servicos[df_servicos.ESTOQUE_VERIFICAR == 'NÃO']['CODIGO']
        .astype(str)
        .to_list()
    )

    # ===============================
    # 4️⃣ FUNÇÃO DE VERIFICAÇÃO
    # ===============================
    def verificar_servicos(linha):
        os_pdi = linha['OS PDI']
        cod_cliente = linha['COD_CLIENTE']

        servicos = [str(v) for v in linha.iloc[7:] if pd.notnull(v)]
        servicos_considerar = [s for s in servicos if s not in lista_nao_considerar]
        servicos_basicos = [s for s in servicos if s in lista_nao_considerar]

        if servicos_basicos and not servicos_considerar:
            return "servico basico"

        indices_para_baixa = []
        tem_falta = False

        for servico in servicos_considerar:
            itens = (
                df_cod_servicos
                .loc[df_cod_servicos['SERVIÇO'] == servico, 'ESTOQUE']
                .dropna()
            )

            # ❶ serviço não mapeado
            if itens.empty:
                tem_falta = True
                st.session_state.df_servicos_pendentes.append({
                    'OS PDI': os_pdi,
                    'SERVIÇO': servico,
                    'MOTIVO': 'serviço não encontrado na tabela cod_serviços'
                })
                continue

            estoque_cliente = df_estoque_v1[
                (df_estoque_v1['Item'].isin(itens)) &
                (df_estoque_v1['Cod.Cliente'] == cod_cliente)
            ]

            # ❷ cliente não possui item
            if estoque_cliente.empty:
                tem_falta = True
                st.session_state.df_servicos_pendentes.append({
                    'OS PDI': os_pdi,
                    'SERVIÇO': servico,
                    'MOTIVO': 'nenhum item encontrado no estoque do cliente'
                })
                continue

            encontrou_item_com_saldo = False

            # ❸ verifica saldo
            for idx, row in estoque_cliente.iterrows():
                if row['Saldo Disponivel'] > 0:
                    indices_para_baixa.append(idx)
                    st.session_state.df_servicos_com_baixa.append({
                        'OS PDI': os_pdi,
                        'SERVIÇO': servico,
                        'Item': row['Item'],
                        'Saldo Antes': row['Saldo Disponivel']
                    })
                    encontrou_item_com_saldo = True
                    break

            # ❹ existe item, mas saldo zero
            if not encontrou_item_com_saldo:
                tem_falta = True
                st.session_state.df_servicos_pendentes.append({
                    'OS PDI': os_pdi,
                    'SERVIÇO': servico,
                    'MOTIVO': 'itens encontrados, mas todos com saldo 0'
                })

        if tem_falta:
            return "pendente de acessorio"

        # 🔽 baixa definitiva
        for idx in indices_para_baixa:
            df_estoque_v1.at[idx, 'Saldo Disponivel'] -= 1

        return "em estoque"

    # ===============================
    # 5️⃣ APLICAÇÃO
    # ===============================
    df_com_placa['status_atual'] = df_com_placa.apply(verificar_servicos, axis=1)
    df_sem_placa['status_atual'] = df_sem_placa.apply(verificar_servicos, axis=1)

    ordernar_colunas = (
        list(df_com_placa.columns[-1:]) +
        list(df_com_placa.columns[:-1])
    )

    df_com_placa_v1 = df_com_placa[ordernar_colunas]
    df_sem_placa_v1 = df_sem_placa[ordernar_colunas]

    return (
        df_estoque_v1,
        df_com_placa_v1,
        df_sem_placa_v1,
        pd.DataFrame(st.session_state.df_servicos_com_baixa),
        pd.DataFrame(st.session_state.df_servicos_pendentes)
    )
