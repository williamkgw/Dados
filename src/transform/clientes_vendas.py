import logging
import pandas as pd
import datetime
import numpy as np
from pathlib import Path

import shutil

import src.util.dataframe as dataframe
from src.config import ConfigLoad

def copy_clientes_e_animais_to_dir(path):
    clientes_e_animais_file = path.parents[0] / 'Animais_e_Clientes.csv'
    clientes_e_animais_dir = path.parents[3] / 'Animais_e_Clientes'
    clientes_e_animais_dir.mkdir(exist_ok = True)
    shutil.copy2(clientes_e_animais_file, clientes_e_animais_dir)

def test_clientes_to_excel(path, agg_clientes, agg_clientes_total, agg_v_clientes, clientes_df):
    agg_file = path / 'test_agg_clientes.xlsx'

    analitico_dir = path.parents[3] / 'Clientes'
    analitico_dir.mkdir(exist_ok = True)
    analitico_clientes_csv_f = analitico_dir / 'clientes_csv.xlsx'
    clientes_df.to_excel(analitico_clientes_csv_f)
    with pd.ExcelWriter(agg_file) as writer:
        agg_clientes.to_excel(writer, sheet_name = 'grupo_clientes')
        agg_clientes_total.to_excel(writer, sheet_name = 'grupo_total')
        agg_v_clientes.to_excel(writer, sheet_name = 'ativos_clientes')

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

def init_clientes(clientes_f, end_date):
    clientes_df = pd.read_csv(clientes_f, dayfirst = True, parse_dates = ['Inclusão'],
                        thousands = '.', decimal = ',', encoding = 'latin1',
                        sep = ';'
                        )
    clientes_df['Origem'] = clientes_df['Origem'].fillna('_outros')
    clientes_df['Inclusão'] = pd.to_datetime(clientes_df['Inclusão'], dayfirst = True, errors = 'coerce')
    clientes_df['Inclusão'] = clientes_df['Inclusão'].fillna('01/01/1900')
    mask = clientes_df['Inclusão'] <= pd.to_datetime(end_date)
    return clientes_df[mask]

def test_mapping_clientes_to_excel(mapping_vendas_duplicated_df, missing_mapping_vendas_df, testing_vendas_out_f):
    with pd.ExcelWriter(testing_vendas_out_f) as writer:
        mapping_vendas_duplicated_df.to_excel(writer, sheet_name = 'duplicated_index')
        missing_mapping_vendas_df.to_excel(writer, sheet_name = 'missing_mapping')

def test_mapping_clientes(mapping_clientes_df, path):
    testing_mapping_clientes_f = path / 'testing_mapping_clientes.xlsx'

    # removing empty rows
    missing_mapping_clientes_df = mapping_clientes_df[mapping_clientes_df.isna().all(axis=1)]
    mapping_clientes_df = mapping_clientes_df.dropna(how = 'all', axis = 0)

    # configuring the dataframes to catch case sensitive
    mapping_clientes_df.index = mapping_clientes_df.index.str.lower()
    
    # removing duplicated index
    mapping_clientes_duplicated_df = mapping_clientes_df[mapping_clientes_df.index.duplicated(keep = False)]
    mapping_clientes_df = mapping_clientes_df[~mapping_clientes_df.index.duplicated(keep='last')]

    return [mapping_clientes_df, mapping_clientes_duplicated_df, missing_mapping_clientes_df, testing_mapping_clientes_f]

def init_mapping_clientes(mapping_clientes_f):
    mapping_vendas_df = pd.read_excel(mapping_clientes_f, index_col = 'Origem', 
                                    dtype = {'Origem': str, 'Grupo': str}
                                    )
    return mapping_vendas_df

def get_clientes_ativos(df):
    df['__clientes_ativos'] = 1/len(df)
    return df

def get_cliente_pilar(df):
    def percentage_of_the_row_against_df(df):
        df['__clientes_ativo_por_pilar'] = 1/len(df)
        return df
    return df.groupby('__pilar', dropna = False).apply(percentage_of_the_row_against_df)

def test_vendas_to_excel(
        path, agg_grupo_df, agg_pilar_df, agg_categoria_df, agg_tempo_df,
        agg_exception_df, unique_mapping_df, vendas_missing_df,
        vendas_df, inadimplente
        ):
    agg_f = path / 'test_agg.xlsx'
    vendas_missing_f = path / 'missing_vendas_csv.xlsx'
    vendas_csv_f = path / 'vendas_csv.xlsx'

    vendas_missing_df.to_excel(vendas_missing_f)
    vendas_df.to_excel(vendas_csv_f)

    analitico_dir = path.parents[3] / 'Analitico'
    analitico_dir.mkdir(exist_ok = True)
    analitico_vendas_csv_f = analitico_dir / 'vendas_csv.xlsx'
    vendas_df.to_excel(analitico_vendas_csv_f)
    with pd.ExcelWriter(agg_f) as writer:
        agg_grupo_df.to_excel(writer, sheet_name = 'grupo')
        agg_pilar_df.to_excel(writer, sheet_name = 'pilar')
        agg_categoria_df.to_excel(writer, sheet_name = 'categoria')
        agg_tempo_df.to_excel(writer, sheet_name = 'total')
        agg_exception_df.to_excel(writer, sheet_name = 'exception')
        inadimplente.to_excel(writer, sheet_name = 'inadimplencia')
        unique_mapping_df.to_excel(writer, sheet_name = 'unique_mapping')

def get_ticket(df):
    df['__ticket'] = 1/df['Venda'].count()
    return df

def get_ticket_pilar(df):
    def percentage_of_the_row_against_df(df):
        df['__ticket_por_pilar'] = 1/len(df)
        return df
    return df.groupby('__pilar', dropna = False).apply(percentage_of_the_row_against_df)

def agg_configure(groupby, has_outter_cat, pilar_or_total = 'none'):
    agg = pd.DataFrame()
    agg['Faturamento Bruto']        = groupby.agg({'Bruto': 'sum'})
    agg['Quantidade Totalizada']    = groupby.agg({'Quantidade': 'sum'})
    agg['Preço Médio']              = agg['Faturamento Bruto']/agg['Quantidade Totalizada']

    def tickets_fat_medio(type_of_ticket, type_of_cliente):
        agg['Tickets Médio']        = groupby.agg({type_of_ticket: 'sum'})
        agg['Tickets Médio']        = agg['Faturamento Bruto']/agg['Tickets Médio']
        
        agg['Faturamento Médio por Clientes'] = groupby.agg({type_of_cliente: 'sum'})
        agg['Faturamento Médio por Clientes'] = agg['Faturamento Bruto']/agg['Faturamento Médio por Clientes']

    if pilar_or_total.lower() == 'pilar':
        tickets_fat_medio('__ticket_por_pilar', '__clientes_ativo_por_pilar')

    elif pilar_or_total.lower() == 'categoria':
        agg = agg.unstack(level = -1)

    elif pilar_or_total.lower() == 'total':
        tickets_fat_medio('__ticket', '__clientes_ativos')

    if has_outter_cat:
        agg = agg.unstack(level = -2).unstack(level = -1)
    agg = agg.dropna(axis=1, how='all')
    agg = agg.fillna(0)

    return agg

def sel_exception_series(exception_df, key, is_grupo):
    exception_pilar = set(exception_df.columns.get_level_values(0))
    exception_grupo = set(exception_df.columns.get_level_values(1))

    if is_grupo:
        if key in exception_grupo:
            exception_df[f'__{key}'] = exception_df.xs(key, level = 1, axis = 1)
        else:
            exception_df[f'__{key}'] = 0
    else:
        if key in exception_pilar:
            exception_df[f'__{key}'] = exception_df.xs(key, level = 0, axis = 1).sum(axis = 1)
        else:
            exception_df[f'__{key}'] = 0
    
    return exception_df[f'__{key}']

def agg_configure_exception(vendas_agrupado_grupo):
    exception_df = vendas_agrupado_grupo['Quantidade'].apply('sum')
    exception_df = exception_df.unstack(level = -2).unstack(level = -1)
    exception_df = exception_df.dropna(axis = 1, how = 'all')

    cirurgia_s    = sel_exception_series(exception_df, 'Cirurgia', True)
    consultas_s   = sel_exception_series(exception_df, 'Consulta', True)
    exames_s      = sel_exception_series(exception_df, 'Exames', False)
    internacao_s  = sel_exception_series(exception_df, 'Diária', True)

    agg_exception_df = pd.DataFrame()
    agg_exception_df['Consultas/Cirurgias']     = consultas_s/cirurgia_s
    agg_exception_df['Consultas/Internação']    = consultas_s/internacao_s
    agg_exception_df['Exames/Consultas']        = exames_s/consultas_s
    agg_exception_df = agg_exception_df.replace([np.inf, -np.inf, np.nan], 0)

    return agg_exception_df

def test_inadimplente(vendas_df, end_date):
    end_date_time_mask = end_date - pd.offsets.MonthBegin()
    begin_date_time_mask = end_date - pd.offsets.DateOffset(months = 11) - 2*pd.offsets.MonthBegin()

    time_mask = (vendas_df['Data e hora'] > begin_date_time_mask) & (vendas_df['Data e hora'] < end_date_time_mask)
    baixa_mask = vendas_df['Status da venda'] != 'Baixado'
    mask = time_mask & baixa_mask

    inadimpl_df = vendas_df[mask].groupby(pd.Grouper(key = 'Data e hora', freq = 'M'))['Bruto'].agg('sum').rolling(window = 12).sum()
    return inadimpl_df.rename('Inadimplencia do Faturamento Bruto')

def test_vendas(vendas_df, mapping_vendas_df):
    # configuring
    vendas_df['Produto/serviço'] = vendas_df['Produto/serviço'].str.lower()

    # mapping
    vendas_df['__categoria'] = vendas_df['Produto/serviço'].map(mapping_vendas_df['Categoria'])
    vendas_df['__pilar'] = vendas_df['Produto/serviço'].map(mapping_vendas_df['Pilar'])
    vendas_df['__grupo'] = vendas_df['Produto/serviço'].map(mapping_vendas_df['Grupo'])
    vendas_df[['__categoria', '__pilar', '__grupo']] = vendas_df[['__categoria', '__pilar', '__grupo']].fillna('NULL')

    # ano e mes
    vendas_df['__ano'] = vendas_df['Data e hora'].dt.year
    vendas_df['__mes'] = vendas_df['Data e hora'].dt.month

    # tickets
    vendas_df = vendas_df.groupby('Venda').apply(get_ticket)
    vendas_df = vendas_df.groupby('Venda').apply(get_ticket_pilar)

    # clientes ativos
    vendas_df = vendas_df.groupby([pd.Grouper(key = 'Data e hora', freq = '1M'), 'Código'], dropna = False).apply(get_clientes_ativos)
    vendas_df = vendas_df.groupby([pd.Grouper(key = 'Data e hora', freq = '1M'), 'Código'], dropna = False).apply(get_cliente_pilar)

    # output diagnosis
    vendas_missing_df = vendas_df[vendas_df[['__pilar', '__grupo']].isna().any(axis = 1)]

    vendas_agrupado_grupo      = vendas_df.groupby([pd.Grouper(key = 'Data e hora', freq = '1M'), '__pilar' ,'__grupo'], dropna = False)
    vendas_agrupado_pilar      = vendas_df.groupby([pd.Grouper(key = 'Data e hora', freq = '1M'), '__categoria' ,'__pilar'], dropna = False)
    vendas_agrupado_categoria  = vendas_df.groupby([pd.Grouper(key = 'Data e hora', freq = '1M'), '__categoria'], dropna = False)
    mask_null_cat_pil = vendas_df.loc[:, ('__categoria', '__pilar')].agg(tuple, axis = 1) == ('NULL', 'NULL')
    vendas_agrupado_tempo      = (  vendas_df[~mask_null_cat_pil]
                                    .copy()
                                    .groupby([pd.Grouper(key = 'Data e hora', freq = '1M')])
                                )

    agg_grupo_df     = agg_configure(vendas_agrupado_grupo, True)
    agg_pilar_df     = agg_configure(vendas_agrupado_pilar, True, 'pilar')
    agg_categoria_df = agg_configure(vendas_agrupado_categoria, False, 'categoria')
    agg_tempo_df     = agg_configure(vendas_agrupado_tempo, False, 'total') 
    agg_exception_df = agg_configure_exception(vendas_agrupado_grupo)

    agg_grupo_df = agg_grupo_df.last('6M')
    agg_pilar_df = agg_pilar_df.last('6M')
    agg_categoria_df = agg_categoria_df.last('6M')
    agg_tempo_df = agg_tempo_df.last('6M')
    agg_exception_df = agg_exception_df.last('6M')
    unique_mapping_df = mapping_vendas_df.groupby(['Categoria', 'Pilar', 'Grupo']).size()
    return [agg_grupo_df, agg_pilar_df, agg_categoria_df, agg_tempo_df,
             agg_exception_df, unique_mapping_df, vendas_missing_df, vendas_df]

def get_vendas_last_36_months(vendas_df):
    max_date = max(vendas_df['Data e hora'])
    min_date = datetime.datetime(year = max_date.year - 3, month = max_date.month, day = 1)
    mask = vendas_df['Data e hora'] > min_date
    return vendas_df[mask]

def init_vendas(vendas_f):
    vendas_df =  pd.read_csv(vendas_f, thousands = '.', decimal = ',', sep = ';',
                        encoding = 'latin1', parse_dates = ['Data e hora'],
                          dayfirst=True,
                        )
    vendas_df['Código'] = vendas_df['Código'].fillna(0)
    vendas_df = vendas_df.astype({'Produto/serviço': str, 'Quantidade': float, 'Bruto': float})
    vendas_df = get_vendas_last_36_months(vendas_df)
    return vendas_df

def test_mapping_vendas_to_excel(mapping_vendas_duplicated_df, missing_mapping_vendas_df, testing_vendas_out_f):
    with pd.ExcelWriter(testing_vendas_out_f) as writer:
        mapping_vendas_duplicated_df.to_excel(writer, sheet_name = 'duplicated_index')
        missing_mapping_vendas_df.to_excel(writer, sheet_name = 'missing_mapping')

def test_mapping_vendas(mapping_vendas_df, path):
    testing_vendas_out_f = path / 'testing_mapping_vendas.xlsx'

    # removing empty rows
    missing_mapping_vendas_df = mapping_vendas_df[mapping_vendas_df.isna().all(axis=1)]
    mapping_vendas_df = mapping_vendas_df.dropna(how = 'all', axis = 0)

    # configuring the dataframes to catch case sensitive
    mapping_vendas_df.index = mapping_vendas_df.index.str.lower()
    
    # removing duplicated index
    mapping_vendas_duplicated_df = mapping_vendas_df[mapping_vendas_df.index.duplicated(keep = False)]
    mapping_vendas_df = mapping_vendas_df[~mapping_vendas_df.index.duplicated(keep='last')]

    return [mapping_vendas_df, mapping_vendas_duplicated_df, missing_mapping_vendas_df, testing_vendas_out_f]

def init_mapping_vendas(mapping_f):
    mapping_vendas_df = pd.read_excel(mapping_f, index_col = 'Produto/serviço', 
                                    dtype = {'Produto/serviço': str, 'Categoria': str, 'Grupo': str, 'Pilar': str}
                                    )
    return mapping_vendas_df

def get_analysis(config_carga_company, end_date):
    output_dir = config_carga_company.output.dir_name

    output_dir.mkdir(parents = True, exist_ok = True)

    new_mapping_vendas_df = init_mapping_vendas(config_carga_company.new_mapping_sales)
    new_mapping_vendas_df, *info_mapping_vendas = test_mapping_vendas(new_mapping_vendas_df, output_dir)
    test_mapping_vendas_to_excel(*info_mapping_vendas)
    
    vendas_df = init_vendas(config_carga_company.sales)
    result_vendas = test_vendas(vendas_df, new_mapping_vendas_df)
    inadimplencia = test_inadimplente(vendas_df, end_date)
    test_vendas_to_excel(output_dir, *result_vendas, inadimplencia)

    new_mapping_clientes_df = init_mapping_clientes(config_carga_company.new_mapping_client)
    new_mapping_clientes_df, *info_mapping_clientes = test_mapping_clientes(new_mapping_clientes_df, output_dir)
    test_mapping_clientes_to_excel(*info_mapping_clientes)

    vendas_df = init_vendas(config_carga_company.sales)
    clientes_df = init_clientes(config_carga_company.clients, end_date)
    result_clientes = test_clientes(vendas_df, clientes_df, new_mapping_clientes_df)
    test_clientes_to_excel(output_dir, *result_clientes)

    copy_clientes_e_animais_to_dir(output_dir)

def loop(emps):
    for emp in emps:
        print(emp)

        config = ConfigLoad('end', emp)
        try:
            get_analysis(config.input_dir.cargas.carga_company, config.date)
        except Exception as e:
            logging.warning(f'{emp}/Couldn\'t get data_analysis/{e}')

def transform_data_analysis():
    config = ConfigLoad('end', 'null')

    emps = dataframe.is_not_done_carga(config.input_dir.cargas.control_flow, 'data_analysis')
    print(emps)
    loop(emps)