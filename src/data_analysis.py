import pandas as pd
import numpy as np
from pathlib import Path
import datetime
import logging

import carga_control

def get_ticket(df):
    df['__ticket'] = 1/df['Venda'].count()
    return df

def get_ticket_pilar(df):
    def percentage_of_the_row_against_df(df):
        df['__ticket_por_pilar'] = 1/len(df)
        return df
    return df.groupby('__pilar', dropna = False).apply(percentage_of_the_row_against_df)

def get_clientes_ativos(df):
    df['__clientes_ativos'] = 1/len(df)
    return df

def get_cliente_pilar(df):
    def percentage_of_the_row_against_df(df):
        df['__clientes_ativo_por_pilar'] = 1/len(df)
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

def test_vendas_to_excel(path, agg_grupo_df, agg_pilar_df, agg_categoria_df, agg_tempo_df, agg_exception_df, unique_mapping_df, vendas_missing_df, vendas_df):
    agg_f = path / 'test_agg.xlsx'
    vendas_missing_f = path / 'missing_vendas_csv.xlsx'
    vendas_csv_f = path / 'vendas_csv.xlsx'

    vendas_missing_df.to_excel(vendas_missing_f)
    vendas_df.to_excel(vendas_csv_f)

    analitico_dir = path.parents[3] / 'Analitico'
    analitico_dir.mkdir(exist_ok = 'True')
    analitico_vendas_csv_f = analitico_dir / 'vendas_csv.xlsx'
    vendas_df.to_excel(analitico_vendas_csv_f)
    with pd.ExcelWriter(agg_f) as writer:
        agg_grupo_df.to_excel(writer, sheet_name = 'grupo')
        agg_pilar_df.to_excel(writer, sheet_name = 'pilar')
        agg_categoria_df.to_excel(writer, sheet_name = 'categoria')
        agg_tempo_df.to_excel(writer, sheet_name = 'total')
        agg_exception_df.to_excel(writer, sheet_name = 'exception')
        unique_mapping_df.to_excel(writer, sheet_name = 'unique_mapping')

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

def agg_vendas_clientes(vendas_df):
    max_date = max(vendas_df['Data e hora'])
    end_date = pd.Period.to_timestamp(max_date.to_period(freq = 'M'))
    min_date = min(vendas_df['Data e hora'])
    start_date = pd.Period.to_timestamp(min_date.to_period(freq = 'M'))

    agg_v_clientes = pd.DataFrame()
    if start_date == end_date:
        n_clientes_6_meses = 0
        agg_new = pd.DataFrame(index = [end_date])
        agg_new['Clientes Ativos 6 Meses'] = n_clientes_6_meses
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
                agg_new['Clientes Ativos 6 Meses'] = n_clientes_6_meses
                agg_v_clientes = pd.concat([agg_new, agg_v_clientes])
                
                endDate -= pd.DateOffset(months = 1)
            break
        
        mask = (vendas_df['Data e hora'] >= startDate) & (vendas_df['Data e hora'] <= endDate)
        df = vendas_df[mask]
        n_clientes_6_meses = df['Cliente'].nunique()

        agg_new = pd.DataFrame(index = [endDate])
        agg_new['Clientes Ativos 6 Meses'] = n_clientes_6_meses
        agg_v_clientes = pd.concat([agg_new, agg_v_clientes])

        endDate -= pd.DateOffset(months = 1)

    return agg_v_clientes

def agg_clientes_mapping(clientes_agrupado):
    agg = pd.DataFrame()
    agg['Cliente Quantidade Totalizada'] = clientes_agrupado.agg({'Origem': 'count'})

    agg = agg.unstack(level = -1)
    agg = agg.dropna(axis = 1, how='all')
    agg = agg.fillna(0)
    return agg

def test_clientes_to_excel(path, agg_clientes, agg_v_clientes):
    agg_file = path / 'test_agg_clientes.xlsx'
    with pd.ExcelWriter(agg_file) as writer:
        agg_clientes.to_excel(writer, sheet_name = 'grupo_clientes')
        agg_v_clientes.to_excel(writer, sheet_name = 'ativos_clientes')

def test_clientes(vendas_df, clientes_df, mapping_clientes_df):
    clientes_df['Origem'] = clientes_df['Origem'].str.lower()

    clientes_df['_grupo'] = clientes_df['Origem'].map(mapping_clientes_df['Grupo'])
    clientes_df['_grupo'] = clientes_df['_grupo'].fillna('NULL')

    clientes_agrupado = clientes_df.groupby([pd.Grouper(key = 'Inclusão', freq = '1M'), '_grupo'], dropna = False)
    agg_clientes = agg_clientes_mapping(clientes_agrupado)

    agg_v_clientes = agg_vendas_clientes(vendas_df)

    agg_clientes = agg_clientes.last('6M')
    agg_v_clientes = agg_v_clientes.last('6M')
    return [agg_clientes, agg_v_clientes]

def correct_new_mapping(paths_correct_new_mapping):
    useful_cols = ['Categoria', 'Pilar', 'Grupo']

    mapping_f = paths_correct_new_mapping['mapping']
    new_mapping_f = paths_correct_new_mapping['new_mapping']

    mapping_df = pd.read_excel(mapping_f, index_col = 'Produto/serviço').fillna('')
    new_mapping_df = pd.read_excel(new_mapping_f, index_col = 'Produto/serviço').fillna('')
    set_values_mapping = set(mapping_df[useful_cols].value_counts().index)
    set_values_new_mapping = set(new_mapping_df[useful_cols].value_counts().index)
    set_excess_values_new_mapping = set_values_new_mapping - set_values_mapping
    excess_values_new_mapping_mask = new_mapping_df[useful_cols].agg(tuple, axis = 1).isin(set_excess_values_new_mapping)
    new_mapping_df.loc[excess_values_new_mapping_mask, 'Categoria'] = '*Reclassificar*'
    return new_mapping_df

def filter_and_correct_new_mapping_all(input_dir, end_date, emps_filter):
    new_mapping_all_df = pd.DataFrame()
    for emp in emps_filter:
        print(emp)

        paths_correct_new_mapping = carga_control.get_files_path_control(input_dir, end_date, 'correct_mapping', emp)
        new_mapping_df = correct_new_mapping(paths_correct_new_mapping)
        new_mapping_df['Empresa'] = emp
        new_mapping_df['path'] = paths_correct_new_mapping['new_mapping']

        new_mapping_all_df = pd.concat([new_mapping_all_df, new_mapping_df])
    
    new_mapping_all_df.to_excel(f'{input_dir}/corrected_new_mapping.xlsx')

def get_new_mapping_cliente(dest_cargas_dir, dest_date, src_cargas_dir, src_date, filter_emps):
    year_month_src_s  = carga_control.get_year_month_str(src_date)
    year_month_dest_s = carga_control.get_year_month_str(dest_date)

    search_pattern = f'Carga/{year_month_src_s}/mapping_cliente.xlsx'
    src_mappings_cliente = list(src_cargas_dir.rglob(search_pattern))

    for src_mapping_cliente in src_mappings_cliente:
        emp = src_mapping_cliente.parents[3].name
        if emp not in filter_emps:
            continue

        print(emp)
        dest_carga_dir = Path(f'{dest_cargas_dir}/{emp}/Carga/{year_month_dest_s}')

        dest_mapping_clientes_f = dest_carga_dir / 'new_mapping_cliente.xlsx'
        dest_clientes_f  = dest_carga_dir / 'Clientes.csv'

        try:
            dest_clientes_df = init_clientes(dest_clientes_f, dest_date)
            dest_clientes_df['Origem'] = dest_clientes_df['Origem'].fillna('_outros')

        except Exception as e:
            logging.warning(f'{emp}/exception {e}')
            continue

        src_mapping_clientes_df = pd.read_excel(src_mapping_cliente, index_col = 'Origem', usecols= ('Origem', 'Grupo'))

        src_origem_index = src_mapping_clientes_df.index.tolist()
        dest_origem_index = dest_clientes_df['Origem'].unique().tolist()

        src_origem_index = [index for index in src_origem_index if index is not np.nan]
        dest_origem_index = [index for index in dest_origem_index if index is not np.nan]

        not_found_origem_index = dest_origem_index
        if src_origem_index:
            not_found_origem_index = [index for index in dest_origem_index
                                            if index.lower() not in [e.lower() for e in src_origem_index]]
        
        dest_clientes_df['Grupo'] = pd.NA
        not_found_clientes_df = dest_clientes_df[dest_clientes_df['Origem'].isin(not_found_origem_index)].copy()
        dest_mapping_clientes_df = not_found_clientes_df.set_index('Origem')['Grupo']
        dest_mapping_clientes_df = dest_mapping_clientes_df[~dest_mapping_clientes_df.index.duplicated()]
        dest_mapping_clientes_df = pd.concat([src_mapping_clientes_df, dest_mapping_clientes_df])
        dest_mapping_clientes_df.to_excel(dest_mapping_clientes_f, columns = ['Grupo'])

def get_new_mapping(dest_cargas_dir, dest_date, src_cargas_dir, src_date, filter_emps):
    year_month_src_s  = carga_control.get_year_month_str(src_date)
    year_month_dest_s = carga_control.get_year_month_str(dest_date)

    search_pattern = f'Carga/{year_month_src_s}/mapping.xlsx'
    src_mappings = list(src_cargas_dir.rglob(search_pattern))

    for src_mapping in src_mappings:
        emp = src_mapping.parents[3].name
        if emp not in filter_emps:
            continue

        print(emp)
        dest_carga_dir = Path(f'{dest_cargas_dir}/{emp}/Carga/{year_month_dest_s}')

        dest_mapping_f = dest_carga_dir / 'new_mapping.xlsx'
        dest_vendas_f  = dest_carga_dir / 'Vendas.csv'

        try:
            dest_vendas_df = pd.read_csv(
                             dest_vendas_f, thousands = '.', decimal = ',', 
                             encoding = 'latin1', sep = ';', 
                             parse_dates = ['Data e hora'], dayfirst=True
                             )
        except Exception as e:
            logging.warning(f'{emp}/exception {e}')
            continue
        dest_vendas_df['Data e hora'] = pd.to_datetime(dest_vendas_df['Data e hora'], errors = 'coerce')
        dest_vendas_df = dest_vendas_df[dest_vendas_df['Data e hora'].dt.date >= src_date - datetime.timedelta(days = 180)]
        
        src_mapping_df = pd.read_excel(src_mapping, index_col = 'Produto/serviço', usecols = ('Produto/serviço', 'Categoria', 'Pilar', 'Grupo'))

        dest_prod_serv_index = dest_vendas_df['Produto/serviço'].unique().tolist()
        src_prod_serv_index  = src_mapping_df.index.unique().tolist()

        not_found_prod_serv_index = [index for index in dest_prod_serv_index 
                                     if index.lower() not in [e.lower() for e in src_prod_serv_index]]

        not_found_vendas_df = dest_vendas_df[dest_vendas_df['Produto/serviço'].isin(not_found_prod_serv_index)].copy()
        dest_mapping_df = not_found_vendas_df.set_index('Produto/serviço')['Grupo']
        dest_mapping_df = dest_mapping_df[~dest_mapping_df.index.duplicated()]
        dest_mapping_df = pd.concat([src_mapping_df, dest_mapping_df])
        dest_mapping_df = dest_mapping_df.rename(columns = {0: 'grupo_simplesvet'})
        grupo_simplesvet_por_produto_servico = dest_vendas_df.set_index('Produto/serviço').loc[:, 'Grupo']
        grupo_simplesvet_por_produto_servico = grupo_simplesvet_por_produto_servico[~grupo_simplesvet_por_produto_servico.index.duplicated()]
        
        dest_mapping_df['grupo_simplesvet'] = grupo_simplesvet_por_produto_servico
        dest_mapping_df.to_excel(dest_mapping_f, columns = ('Categoria', 'Pilar', 'Grupo', 'grupo_simplesvet'))

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

    test_mapping_vendas_to_excel(mapping_vendas_duplicated_df, missing_mapping_vendas_df, testing_vendas_out_f)

    return mapping_vendas_df

def init_mapping_vendas(mapping_f, path):
    mapping_vendas_df = pd.read_excel(mapping_f, index_col = 'Produto/serviço', 
                                    dtype = {'Produto/serviço': str, 'Categoria': str, 'Grupo': str, 'Pilar': str}
                                    )
    return mapping_vendas_df

def invert_key_value_dict(dict):
    return {value:key for key, value in dict.items()}

def get_filter_columns(vendas_or_clientes_f, interface_name):
    cargas_dir = vendas_or_clientes_f.parents[4]
    emp = vendas_or_clientes_f.parents[3].name
    interface_path = cargas_dir / interface_name
    interface_df = pd.read_excel(interface_path, index_col = 'Sistema')
    clean_interface_df = interface_df.fillna('')
    columns = dict(clean_interface_df.loc['Simplesvet', :])
    columns_cleaned = {key:value for key, value in columns.items() if value != ''}
    return columns_cleaned

def get_vendas_last_36_months(vendas_df):
    max_date = max(vendas_df['Data e hora'])
    min_date = datetime.datetime(year = max_date.year - 3, month = max_date.month, day = 1)
    mask = vendas_df['Data e hora'] > min_date
    return vendas_df[mask]

def init_vendas(vendas_f):
    useful_columns = get_filter_columns(vendas_f, 'interface_vendas.xlsx')
    vendas_df =  pd.read_csv(vendas_f, thousands = '.', decimal = ',', sep = ';',
                        encoding = 'latin1',# usecols = useful_columns.values(),
                        parse_dates = [useful_columns['Data e hora']], dayfirst=True,
                        )
    # vendas_df = vendas_df.rename(columns = invert_key_value_dict(useful_columns))
    vendas_df['Código'] = vendas_df['Código'].fillna(0)
    vendas_df = vendas_df.astype({'Produto/serviço': str, 'Quantidade': float, 'Bruto': float})
    # vendas_df = vendas_df.astype({'Código': int, 'Grupo': str, 'Produto/serviço': str, 'Quantidade': float, 'Bruto': float}) - código e grupo as vezes podem nao existir
    vendas_df = get_vendas_last_36_months(vendas_df)
    return vendas_df

def init_clientes(clientes_f, end_date):
    # useful_columns = get_filter_columns(clientes_f, 'interface_clientes.xlsx')
    clientes_df = pd.read_csv(clientes_f, dayfirst = True, parse_dates = ['Inclusão'],#[useful_columns['Inclusão']],
                        thousands = '.', decimal = ',', encoding = 'latin1',
                        sep = ';'#, usecols = useful_columns.values()
                        )
    # clientes_df = clientes_df.rename(columns = invert_key_value_dict(useful_columns))
    clientes_df['Inclusão'] = pd.to_datetime(clientes_df['Inclusão'], dayfirst = True, errors = 'coerce')
    clientes_df['Inclusão'] = clientes_df['Inclusão'].fillna('01/01/1900')
    mask = clientes_df['Inclusão'] <= pd.to_datetime(end_date)
    return clientes_df[mask]

def init_mapping_clientes(mapping_clientes_f, path):
    mapping_vendas_df = pd.read_excel(mapping_clientes_f, index_col = 'Origem', 
                                    dtype = {'Origem': str, 'Grupo': str}
                                    )
    return mapping_vendas_df

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

    test_mapping_clientes_to_excel(mapping_clientes_duplicated_df, missing_mapping_clientes_df, testing_mapping_clientes_f)

    return mapping_clientes_df

def get_analysis(mapping_f, vendas_f, mapping_clientes_f, clientes_f, path, end_date):
    path.mkdir(parents = True, exist_ok = True)

    mapping_vendas_df = init_mapping_vendas(mapping_f, path)
    mapping_vendas_df = test_mapping_vendas(mapping_vendas_df, path)
    vendas_df = init_vendas(vendas_f)
    result_vendas = test_vendas(vendas_df, mapping_vendas_df)
    test_vendas_to_excel(path, *result_vendas)

    mapping_clientes_df = init_mapping_clientes(mapping_clientes_f, path)
    mapping_clientes_df = test_mapping_clientes(mapping_clientes_df, path)

    vendas_df = init_vendas(vendas_f)
    clientes_df = init_clientes(clientes_f, end_date)
    result_clientes = test_clientes(vendas_df, clientes_df, mapping_clientes_df)
    test_clientes_to_excel(path, *result_clientes)

def loop(input_dir, end_date, filter_emps):
    cargas_dir = carga_control.get_cargas_dir(input_dir, end_date)
    year_month_s = carga_control.get_year_month_str(end_date)
    search_pattern = f'Carga/{year_month_s}/Vendas.csv'
    vendas = list(cargas_dir.rglob(search_pattern))

    for venda in vendas:
        
        emp = venda.parents[3].name
        if emp not in filter_emps:
            continue    
        print(emp)

        carga_dir = venda.parent

        carga_out_dir = carga_dir / 'output'

        new_mapping = carga_dir / 'new_mapping.xlsx'
        new_mapping_clientes = carga_dir / 'new_mapping_cliente.xlsx'
        clientes    = carga_dir / 'Clientes.csv'

        try:
            get_analysis(new_mapping, venda, new_mapping_clientes, clientes, carga_out_dir, end_date)
        except Exception as e:
            logging.warning(f'{emp}/Couldn\'t get data_analysis/{e}')

def main():
    import sys

    END_DATE = carga_control.END_DATE
    INPUT_DIR = carga_control.INPUT_DIR
    cargas_dir = carga_control.get_cargas_dir(INPUT_DIR, END_DATE)
    logging.basicConfig(filename = cargas_dir / 'log.log', filemode = 'w', encoding = 'utf-8')

    assert len(sys.argv) == 2
    type_of_execution = sys.argv[1]

    if type_of_execution == 'new_mapping':
        emps = carga_control.is_not_done_carga(INPUT_DIR, END_DATE, 'new_mapping')
        print(emps)
        get_new_mapping(cargas_dir, END_DATE, cargas_dir, END_DATE, emps)

    if type_of_execution == 'new_mapping_cliente':
        emps = carga_control.is_not_done_carga(INPUT_DIR, END_DATE, 'new_mapping_cliente')
        print(emps)
        get_new_mapping_cliente(cargas_dir, END_DATE, cargas_dir, END_DATE, emps)

    elif type_of_execution == 'correct_mapping':
        emps = carga_control.is_not_done_carga(INPUT_DIR, END_DATE, 'correct_mapping')
        print(emps)
        filter_and_correct_new_mapping_all(INPUT_DIR, END_DATE, emps)

    elif type_of_execution == 'data_analysis':
        emps = carga_control.is_not_done_carga(INPUT_DIR, END_DATE, 'data_analysis')
        print(emps)
        loop(INPUT_DIR, END_DATE, emps)

if __name__ == '__main__':
    main()