import logging

from src.util.others import copy_file_to
import src.util.dataframe as dataframe
from src.config import ConfigLoad

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

def do_data_analysis(emps):
    for emp in emps:
        print(emp)

        config = ConfigLoad('end', emp)
        try:
            get_analysis(config.input_dir.cargas.carga_company, config.date)
            copy_carga_files_to_analytic(config.input_dir.cargas.carga_company, config.input_dir.analytic)
        except Exception as e:
            logging.warning(f'{emp}/Couldn\'t get data_analysis/{e}')

def transform_data_analysis():
    config = ConfigLoad('end', 'null')

    emps = dataframe.is_not_done_carga(config.input_dir.cargas.control_flow, 'data_analysis')
    print(emps)
    do_data_analysis(emps)