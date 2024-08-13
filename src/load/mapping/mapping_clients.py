import src.util.dataframe as dataframe
from src.util.others import copy_file_to
from src.config import ConfigLoad

def load_mapping_clientes():
    config = ConfigLoad('end', 'null')

    emps = dataframe.is_not_done_carga(config.input_dir.cargas.control_flow, 'mapping_cliente')
    print(emps)

    for emp in emps:
        print(emp)
        src_config = ConfigLoad('beg', emp)
        dest_config = ConfigLoad('end', emp)

        copy_file_to(src_config.input_dir.cargas.carga_company.new_mapping_client, dest_config.input_dir.cargas.carga_company.mapping_client)

def load_new_mapping_clientes_all():
    config = ConfigLoad('end', 'null')

    emps = dataframe.is_not_done_carga(config.input_dir.cargas.control_flow, 'new_mapping_cliente')
    print(emps)
    paths_new_mapping_client = []
    for emp in emps:
        config_company = ConfigLoad('end', emp)
        paths_new_mapping_client.append(config_company.input_dir.cargas.carga_company.new_mapping_client)

    dataframe.df_all(paths_new_mapping_client, config.input_dir.new_mapping_clients_all, 3)

def load_new_mapping_clientes_all_to_company_dir():
    config = ConfigLoad('end', 'null')

    dataframe.df_all_to_df(config.input_dir.new_mapping_clients_all_modified)
