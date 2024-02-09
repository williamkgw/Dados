
import src.utils as utils
from src.config import END_DATE, INPUT_DIR
from pathlib import Path
import pandas as pd
import logging
import datetime

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

def get_new_mapping(dest_cargas_dir, dest_date, src_cargas_dir, src_date, filter_emps):
    year_month_src_s  = utils.get_year_month_str(src_date)
    year_month_dest_s = utils.get_year_month_str(dest_date)

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
            dest_vendas_df = init_vendas(dest_vendas_f)
        except Exception as e:
            logging.warning(f'{emp}/exception {e}')
            continue
        dest_vendas_df['Data e hora'] = pd.to_datetime(dest_vendas_df['Data e hora'], errors = 'coerce')
        dest_vendas_df = dest_vendas_df[dest_vendas_df['Data e hora'].dt.date >= src_date - datetime.timedelta(days = 180)]
        
        src_mapping_df = pd.read_excel(src_mapping, index_col = 'Produto/serviço', usecols = ('Produto/serviço', 'Categoria', 'Pilar', 'Grupo'))
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
        dest_mapping_df.to_excel(dest_mapping_f, columns = ('Categoria', 'Pilar', 'Grupo', 'grupo_simplesvet'))

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

        paths_correct_new_mapping = utils.get_files_path_control(input_dir, end_date, 'correct_mapping', emp)
        new_mapping_df = correct_new_mapping(paths_correct_new_mapping)
        new_mapping_df['Empresa'] = emp
        new_mapping_df['path'] = paths_correct_new_mapping['new_mapping']

        new_mapping_all_df = pd.concat([new_mapping_all_df, new_mapping_df])
    
    new_mapping_all_df.to_excel(f'{input_dir}/corrected_new_mapping.xlsx')

def transform_new_mapping():
    cargas_dir = utils.get_cargas_dir(INPUT_DIR, END_DATE)

    logging.basicConfig(filename = cargas_dir / 'log.log', filemode = 'w', encoding = 'utf-8')

    emps = utils.is_not_done_carga(INPUT_DIR, END_DATE, 'new_mapping')
    print(emps)
    get_new_mapping(cargas_dir, END_DATE, cargas_dir, END_DATE, emps)

def transform_correct_new_mapping():
    emps = utils.is_not_done_carga(INPUT_DIR, END_DATE, 'correct_mapping')
    print(emps)
    filter_and_correct_new_mapping_all(INPUT_DIR, END_DATE, emps)