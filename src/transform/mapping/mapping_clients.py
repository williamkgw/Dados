import pandas as pd
import numpy as np
import logging

import src.util.dataframe as dataframe
from src.extraction.clients import init_clientes
from src.config import ConfigLoad

def test_mapping_clientes_to_excel(config_company_output, mapping_vendas_duplicated_df, missing_mapping_vendas_df):
    testing_mapping_clientes_f = config_company_output.mapping_clients_mapped
    with pd.ExcelWriter(testing_mapping_clientes_f) as writer:
        mapping_vendas_duplicated_df.to_excel(writer, sheet_name = 'duplicated_index')
        missing_mapping_vendas_df.to_excel(writer, sheet_name = 'missing_mapping')

def test_mapping_clientes(mapping_clientes_df):
    # removing empty rows
    missing_mapping_clientes_df = mapping_clientes_df[mapping_clientes_df.isna().all(axis=1)]
    mapping_clientes_df = mapping_clientes_df.dropna(how = 'all', axis = 0)

    # configuring the dataframes to catch case sensitive
    mapping_clientes_df.index = mapping_clientes_df.index.str.lower()
    
    # removing duplicated index
    mapping_clientes_duplicated_df = mapping_clientes_df[mapping_clientes_df.index.duplicated(keep = False)]
    mapping_clientes_df = mapping_clientes_df[~mapping_clientes_df.index.duplicated(keep='last')]

    return [mapping_clientes_df, mapping_clientes_duplicated_df, missing_mapping_clientes_df]

def get_new_mapping_cliente(emps):
    for emp in emps:
        print(emp)

        src_config = ConfigLoad('end', emp)
        dest_config = ConfigLoad('end', emp)

        try:
            dest_clientes_df = init_clientes(dest_config.input_dir.cargas.carga_company.clients, dest_config.date)
            dest_clientes_df['Origem'] = dest_clientes_df['Origem'].fillna('_outros')

        except Exception as e:
            logging.warning(f'{emp}/exception {e}')
            continue

        src_mapping_clientes_df = pd.read_excel(src_config.input_dir.cargas.carga_company.mapping_client, index_col = 'Origem', usecols= ('Origem', 'Grupo'))

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
        dest_mapping_clientes_df.to_excel(dest_config.input_dir.cargas.carga_company.new_mapping_client, columns = ['Grupo'])


def transform_new_mapping_clientes():
    config = ConfigLoad('end', 'null')

    emps = dataframe.is_not_done_carga(config.input_dir.cargas.control_flow, 'new_mapping_cliente')
    print(emps)
    get_new_mapping_cliente(emps)