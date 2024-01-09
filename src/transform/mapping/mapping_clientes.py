
import src.utils as utils
from src.config import END_DATE, INPUT_DIR
from pathlib import Path
import pandas as pd
import numpy as np
import logging

def init_clientes(clientes_f, end_date):
    # useful_columns = get_filter_columns(clientes_f, 'interface_clientes.xlsx')
    clientes_df = pd.read_csv(clientes_f, dayfirst = True, parse_dates = ['Inclusão'],#[useful_columns['Inclusão']],
                        thousands = '.', decimal = ',', encoding = 'latin1',
                        sep = ';'#, usecols = useful_columns.values()
                        )
    # clientes_df = clientes_df.rename(columns = invert_key_value_dict(useful_columns))
    clientes_df['Origem'] = clientes_df['Origem'].fillna('_outros')
    clientes_df['Inclusão'] = pd.to_datetime(clientes_df['Inclusão'], dayfirst = True, errors = 'coerce')
    clientes_df['Inclusão'] = clientes_df['Inclusão'].fillna('01/01/1900')
    mask = clientes_df['Inclusão'] <= pd.to_datetime(end_date)
    return clientes_df[mask]

def get_new_mapping_cliente(dest_cargas_dir, dest_date, src_cargas_dir, src_date, filter_emps):
    year_month_src_s  = utils.get_year_month_str(src_date)
    year_month_dest_s = utils.get_year_month_str(dest_date)

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


def transform_new_mapping_clientes():
    cargas_dir = utils.get_cargas_dir(INPUT_DIR, END_DATE)
    emps = utils.is_not_done_carga(INPUT_DIR, END_DATE, 'new_mapping_cliente')
    print(emps)
    get_new_mapping_cliente(cargas_dir, END_DATE, cargas_dir, END_DATE, emps)