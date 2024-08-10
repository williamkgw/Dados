import pandas as pd
import logging
import datetime

import src.util.dataframe as dataframe
from src.config import ConfigLoad

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

def get_new_mapping(emps):

    for emp in emps:
        print(emp)

        config_src = ConfigLoad('end', emp)
        config_dest = ConfigLoad('end', emp)

        try:
            dest_vendas_df = init_vendas(config_dest.input_dir.cargas.carga_company.sales)
        except Exception as e:
            logging.warning(f'{emp}/exception {e}')
            continue
    
        dest_vendas_df['Data e hora'] = pd.to_datetime(dest_vendas_df['Data e hora'], errors = 'coerce')
        dest_vendas_df = dest_vendas_df[dest_vendas_df['Data e hora'].dt.date >= config_src.date - datetime.timedelta(days = 180)]
        
        src_mapping_df = pd.read_excel(config_src.input_dir.cargas.carga_company.mapping_sales, index_col = 'Produto/serviço', usecols = ('Produto/serviço', 'Categoria', 'Pilar', 'Grupo'))
        src_mapping_df = src_mapping_df[~src_mapping_df.index.duplicated(keep = 'first')]

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
        dest_mapping_df.to_excel(config_dest.input_dir.cargas.carga_company.new_mapping_sales, columns = ('Categoria', 'Pilar', 'Grupo', 'grupo_simplesvet'))

def correct_new_mapping(path_mapping_sales, path_new_mapping_sales):
    useful_cols = ['Categoria', 'Pilar', 'Grupo']

    mapping_df = pd.read_excel(path_mapping_sales, index_col = 'Produto/serviço').fillna('')
    new_mapping_df = pd.read_excel(path_new_mapping_sales, index_col = 'Produto/serviço').fillna('')
    set_values_mapping = set(mapping_df[useful_cols].value_counts().index)
    set_values_new_mapping = set(new_mapping_df[useful_cols].value_counts().index)
    set_excess_values_new_mapping = set_values_new_mapping - set_values_mapping
    excess_values_new_mapping_mask = new_mapping_df[useful_cols].agg(tuple, axis = 1).isin(set_excess_values_new_mapping)
    new_mapping_df.loc[excess_values_new_mapping_mask, 'Categoria'] = '*Reclassificar*'
    return new_mapping_df

def filter_and_correct_new_mapping_all(emps, path_new_mapping_sales_corrected_all):
    new_mapping_all_df = pd.DataFrame()
    for emp in emps:
        print(emp)
        config = ConfigLoad('end', emp)

        path_mapping_sales = config.input_dir.cargas.carga_company.mapping_sales
        path_new_mapping_sales = config.input_dir.cargas.carga_company.new_mapping_sales

        new_mapping_df = correct_new_mapping(path_mapping_sales, path_new_mapping_sales)
        new_mapping_df['Empresa'] = emp
        new_mapping_df['path'] = path_new_mapping_sales

        new_mapping_all_df = pd.concat([new_mapping_all_df, new_mapping_df])

    new_mapping_all_df.to_excel(path_new_mapping_sales_corrected_all)

def transform_new_mapping():
    config = ConfigLoad('end', 'null')

    logging.basicConfig(filename = config.input_dir.cargas.log, filemode = 'w', encoding = 'utf-8')

    emps = dataframe.is_not_done_carga(config.input_dir.cargas.control_flow, 'new_mapping')
    print(emps)
    get_new_mapping(emps)

def transform_correct_new_mapping():
    config = ConfigLoad('end', 'null')

    emps = dataframe.is_not_done_carga(config.input_dir.cargas.control_flow, 'correct_mapping')
    print(emps)
    filter_and_correct_new_mapping_all(emps, config.input_dir.new_mapping_sales_corrected_all)