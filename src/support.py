import logging
from src.config import ConfigLoad

from src.util.others import copy_file_to

def copy_mapping_clientes(emps):
    logger = logging.getLogger("src.support")

    for emp in emps:
        logger.info(f"Starting copying mapping_clients for {emp}")
        src_config = ConfigLoad('beg', emp)
        dest_config = ConfigLoad('end', emp)

        copy_file_to(src_config.input_dir.cargas.carga_company.new_mapping_client, dest_config.input_dir.cargas.carga_company.mapping_client)

def copy_mapping_item(emps):
    logger = logging.getLogger("src.support")
    
    for emp in emps:
        logger.info(f"Starting copying mapping_item for {emp}")
        src_config = ConfigLoad('beg', emp)
        dest_config = ConfigLoad('end', emp)

        copy_file_to(src_config.input_dir.cargas.carga_company.mapping_export, dest_config.input_dir.cargas.carga_company.mapping_export)

def copy_mapping_vendas(emps):
    logger = logging.getLogger("src.support")

    for emp in emps:
        logger.info(f"Starting copying mapping_sales for {emp}")
        src_config = ConfigLoad('beg', emp)
        dest_config = ConfigLoad('end', emp)

        copy_file_to(src_config.input_dir.cargas.carga_company.new_mapping_sales, dest_config.input_dir.cargas.carga_company.mapping_sales)

def copy_import_icg(emps):
    logger = logging.getLogger("src.support")

    for emp in emps:
        logger.info(f"Starting copying import_template for {emp}")
        src_config = ConfigLoad('beg', emp)
        dest_config = ConfigLoad('end', emp)

        copy_file_to(src_config.input_dir.cargas.carga_company.export_template, dest_config.input_dir.cargas.carga_company.export_template)

from src.load.ftp_dir import (
    remove_all_inside_results,
    copy_dirs_carga_to_results_dirs_carga,
    copy_exports_to_results_exports_carga
)

def copy_ftp_dir(emps, config_results):
    logger = logging.getLogger("src.support")

    logger.info(f"Started to remove the contents of {config_results.dir_name}")
    remove_all_inside_results(config_results.dir_name)
    logger.info(f"Started to copy dirs of {emps}")
    copy_dirs_carga_to_results_dirs_carga(config_results.dirs_carga, emps)
    logger.info(f"Started to copy exports of {emps}")
    copy_exports_to_results_exports_carga(config_results.exports_carga, emps)
    logger.info(f"Ending copy ftp for {emps}")

from src.util.dataframe import df_all

def copy_new_mapping_clientes_all(emps, config_input_dir):
    paths_new_mapping_client = []
    for emp in emps:
        config_company = ConfigLoad('end', emp)
        paths_new_mapping_client.append(config_company.input_dir.cargas.carga_company.new_mapping_client)

    df_all(paths_new_mapping_client, config_input_dir.new_mapping_clients_all, 3)

def copy_mapping_item_all(emps, config_input_dir):
    paths_mapping_item = []
    for emp in emps:
        config_company = ConfigLoad('end', emp)
        paths_mapping_item.append(config_company.input_dir.cargas.carga_company.mapping_export)

    df_all(paths_mapping_item, config_input_dir.mapping_export_all, 3)


def copy_new_mapping_vendas_all(emps, config_input_dir):
    paths_new_mapping_sales = []
    for emp in emps:
        config_company = ConfigLoad('end', emp)
        paths_new_mapping_sales.append(config_company.input_dir.cargas.carga_company.new_mapping_sales)

    df_all(paths_new_mapping_sales, config_input_dir.new_mapping_sales_all, 3)

from src.util.dataframe import df_all_to_df

def copy_new_mapping_clientes_all_to_company_dir(config_input_dir):
    df_all_to_df(config_input_dir.new_mapping_clients_all_modified)

def copy_mapping_item_all_to_company_dir(config_input_dir):
    df_all_to_df(config_input_dir.mapping_export_all_modified)

def copy_new_mapping_vendas_all_to_company_dir(config_input_dir):
    df_all_to_df(config_input_dir.new_mapping_sales_all_modified)

def copy_correct_new_mapping_vendas_to_company_dir(config_input_dir):
    df_all_to_df(config_input_dir.new_mapping_sales_corrected_all_modified)
