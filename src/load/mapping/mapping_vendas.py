import src.util.dataframe as dataframe
from src.util.others import copy_file_to 
from src.config import ConfigLoad

def load_mapping_vendas():
    config = ConfigLoad('end', 'null')

    emps = dataframe.is_not_done_carga(config.input_dir.cargas.control_flow, 'mapping')
    print(emps)

    for emp in emps:
        print(emp)
        src_config = ConfigLoad('beg', emp)
        dest_config = ConfigLoad('end', emp)

        copy_file_to(src_config.input_dir.cargas.carga_company.new_mapping_sales, dest_config.input_dir.cargas.carga_company.mapping_sales)

def load_new_mapping_vendas_all():
    config = ConfigLoad('end', 'null')

    emps = dataframe.is_not_done_carga(config.input_dir.cargas.control_flow, 'new_mapping')
    print(emps)
    paths_new_mapping_sales = []
    for emp in emps:
        config_company = ConfigLoad('end', emp)
        paths_new_mapping_sales.append(config_company.input_dir.cargas.carga_company.new_mapping_sales)

    dataframe.df_all(paths_new_mapping_sales, config.input_dir.new_mapping_sales_all, 3)

def load_new_mapping_vendas_all_to_company_dir():
    config = ConfigLoad('end', 'null')

    dataframe.df_all_to_df(config.input_dir.new_mapping_sales_all_modified)

def load_correct_new_mapping_vendas_to_company_dir():
    config = ConfigLoad('end', 'null')

    dataframe.df_all_to_df(config.input_dir.new_mapping_sales_corrected_all_modified)
