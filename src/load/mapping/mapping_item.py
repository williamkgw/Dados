import src.util.dataframe as dataframe
from src.util.others import copy_file_to 
from src.config import ConfigLoad

def load_mapping_item():
    config = ConfigLoad('end', 'null')

    emps = dataframe.is_not_done_carga(config.input_dir.cargas.control_flow, 'mapping_item')
    print(emps)

    for emp in emps:
        print(emp)
        src_config = ConfigLoad('beg', emp)
        dest_config = ConfigLoad('end', emp)

        copy_file_to(src_config.input_dir.cargas.carga_company.mapping_export, dest_config.input_dir.cargas.carga_company.mapping_export)

def load_mapping_item_all():
    config = ConfigLoad('end', 'null')

    emps = dataframe.is_not_done_carga(config.input_dir.cargas.control_flow, 'mapping_item')
    print(emps)
    paths_mapping_item = []
    for emp in emps:
        config_company = ConfigLoad('end', emp)
        paths_mapping_item.append(config_company.input_dir.cargas.carga_company.mapping_export)

    dataframe.df_all(paths_mapping_item, config.input_dir.mapping_export_all, 3)

def load_mapping_item_all_to_company_dir():
    config = ConfigLoad('end', 'null')

    dataframe.df_all_to_df(config.input_dir.mapping_export_all_modified)
