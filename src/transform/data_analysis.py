from src.util.others import copy_file_to

from src.transform.clients import clients_data_analysis
from src.transform.sales import sales_data_analysis

def get_analysis(config_carga_company, end_date):
    output_dir = config_carga_company.output.dir_name
    output_dir.mkdir(parents = True, exist_ok = True)

    sales_data_analysis(config_carga_company, end_date)
    clients_data_analysis(config_carga_company, end_date)

def copy_carga_files_to_analytic(config_carga, config_analytic):
    copy_file_to(config_carga.animals_and_clients, config_analytic.animals_and_clients_analytic.animals_and_clients)
    copy_file_to(config_carga.output.sales, config_analytic.sales_analytic.sales)
    copy_file_to(config_carga.output.clients, config_analytic.clients_analytic.clients)
