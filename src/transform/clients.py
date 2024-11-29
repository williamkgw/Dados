import pandas as pd

from src.extraction.sales import init_vendas

from src.extraction.clients import init_clientes
from src.load.clients import test_clientes_to_excel

from src.extraction.mapping.mapping_clients import init_mapping_clientes
from src.transform.mapping.mapping_clients import test_mapping_clientes
from src.load.mapping.mapping_clients import test_mapping_clientes_to_excel

def agg_vendas_clientes(vendas_df):
    max_date = max(vendas_df['Data e hora'])
    end_date = pd.Period.to_timestamp(max_date.to_period(freq = 'M'))
    min_date = min(vendas_df['Data e hora'])
    start_date = pd.Period.to_timestamp(min_date.to_period(freq = 'M'))

    agg_v_clientes = pd.DataFrame()
    if start_date == end_date:
        n_clientes_6_meses = 0
        agg_new = pd.DataFrame(index = [end_date])
        agg_new['Quantidade Totalizada Clientes Ativos'] = n_clientes_6_meses
        return agg_new
    
    endDate = end_date
    while True:
        startDate = endDate - pd.DateOffset(months = 6)

        if startDate <= start_date:
            while True:
                startDate = start_date
                if endDate <= startDate:
                    break
                mask = (vendas_df['Data e hora'] >= startDate) & (vendas_df['Data e hora'] <= endDate)
                df = vendas_df[mask]
                n_clientes_6_meses = df['Cliente'].nunique()
                agg_new = pd.DataFrame(index = [endDate])
                agg_new['Quantidade Totalizada Clientes Ativos'] = n_clientes_6_meses
                agg_v_clientes = pd.concat([agg_new, agg_v_clientes])
                
                endDate -= pd.DateOffset(months = 1)
            break
        
        mask = (vendas_df['Data e hora'] >= startDate) & (vendas_df['Data e hora'] <= endDate)
        df = vendas_df[mask]
        n_clientes_6_meses = df['Cliente'].nunique()

        agg_new = pd.DataFrame(index = [endDate])
        agg_new['Quantidade Totalizada Clientes Ativos'] = n_clientes_6_meses
        agg_v_clientes = pd.concat([agg_new, agg_v_clientes])

        endDate -= pd.DateOffset(months = 1)

    return agg_v_clientes

def agg_clientes_mapping(clientes_agrupado):
    agg = pd.DataFrame()
    agg['Quantidade Totalizada Clientes'] = clientes_agrupado.agg({'Origem': 'count'})

    agg = agg.dropna(axis = 1, how='all')
    agg = agg.unstack(level = -1, fill_value = 0)
    return agg

def test_clientes(vendas_df, clientes_df, mapping_clientes_df):
    clientes_df['Origem'] = clientes_df['Origem'].str.lower()

    clientes_df['_grupo'] = clientes_df['Origem'].map(mapping_clientes_df['Grupo'])
    clientes_df['_grupo'] = clientes_df['_grupo'].fillna('NULL')

    clientes_agrupado = clientes_df.groupby([pd.Grouper(key = 'Inclusão', freq = '1M'), '_grupo'], dropna = False)
    clientes_agrupado_tempo = clientes_df.groupby([pd.Grouper(key = 'Inclusão', freq = '1M')])

    agg_clientes = agg_clientes_mapping(clientes_agrupado)
    agg_clientes = agg_clientes.last('6M')
    agg_clientes_total = pd.DataFrame()
    agg_clientes_total['Quantidade Totalizada Clientes'] = clientes_agrupado_tempo.agg({'Origem': 'count'}).last('6M')
    agg_v_clientes = agg_vendas_clientes(vendas_df)
    agg_v_clientes = agg_v_clientes.last('6M')
    return [agg_clientes, agg_clientes_total, agg_v_clientes, clientes_df]

def clients_data_analysis(config_carga_company, end_date):
    new_mapping_clientes_df = init_mapping_clientes(config_carga_company.new_mapping_client)
    new_mapping_clientes_df, *info_mapping_clientes = test_mapping_clientes(new_mapping_clientes_df)
    test_mapping_clientes_to_excel(config_carga_company.output, *info_mapping_clientes)

    vendas_df = init_vendas(config_carga_company.sales, end_date)
    clientes_df = init_clientes(config_carga_company.clients, end_date)
    result_clientes = test_clientes(vendas_df, clientes_df, new_mapping_clientes_df)
    test_clientes_to_excel(config_carga_company.output, *result_clientes)