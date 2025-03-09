import argparse
import time
import logging

import src.util.dataframe as dataframe

import src.scrape
import src.generate
import src.support

from src.config import ConfigLoad

def main():
    config = ConfigLoad('end', 'null')
    logging.basicConfig(
        filename = config.input_dir.cargas.log,
        filemode = 'w',
        encoding = 'utf-8',
        level = logging.INFO,
        format='%(asctime)s UTC - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s'
    )
    logging.Formatter.converter = time.gmtime
    logger = logging.getLogger('run')

    parser = argparse.ArgumentParser(
        description='Um programa para realizar ETL no sistema Quattrus'
    )

    parser.add_argument('file', help = 'Arquivo para executar')
    parser.add_argument('mode', help = 'Tipo de execução do arquivo')

    args = parser.parse_args()

    if args.file == 'scrape':
        if args.mode == 'webscraping':
            config = ConfigLoad('end', 'null')
            emps = dataframe.is_not_done_carga(config.input_dir.cargas.control_flow, 'webscraping')
            logger.info(f"Started to scrape on the following companies {emps}")
            src.scrape.get_logins(emps, config.input_dir.cargas.credentials)

    elif args.file == 'generate':
        if args.mode == 'import_icg':
            config = ConfigLoad('end',  'null')
            emps = dataframe.is_not_done_carga(config.input_dir.cargas.control_flow, 'import_automatico')
            logger.info(f"Started to generate imports on the following companies {emps}")
            src.generate.get_med_import(emps)

        elif args.mode == 'import_icg_triple_check':
            config = ConfigLoad('end',  'null')
            emps = dataframe.is_not_done_carga(config.input_dir, config.date, 'triple_check')
            logger.info(f"Started to triple check on the following companies {emps}")
            src.generate.triple_check(emps)

        elif args.mode == 'mapping_item':
            config = ConfigLoad('end', 'null')
            emps = dataframe.is_not_done_carga(config.input_dir.cargas.control_flow, 'mapping_item')
            logger.info(f"Started to generate mapping item on the following companies {emps}")
            src.generate.get_mapping_item(emps)
        
        elif args.mode == 'new_mapping':
            config = ConfigLoad('end', 'null')
            emps = dataframe.is_not_done_carga(config.input_dir.cargas.control_flow, 'new_mapping')
            logger.info(f"Started to generate new_mapping_sales on the following companies {emps}")
            src.generate.get_new_mapping(emps)

        elif args.mode == 'new_mapping_cliente':
            config = ConfigLoad('end', 'null')
            emps = dataframe.is_not_done_carga(config.input_dir.cargas.control_flow, 'new_mapping_cliente')
            logger.info(f"Started to generate new_mapping_clients on the following companies {emps}")
            src.generate.get_new_mapping_cliente(emps)

        elif args.mode == 'correct_new_mapping':
            config = ConfigLoad('end', 'null')
            emps = dataframe.is_not_done_carga(config.input_dir.cargas.control_flow, 'correct_mapping')
            logger.info(f"Started to generate the correct_new_mapping_sales on the following companies {emps}")
            src.generate.filter_and_correct_new_mapping_all(emps, config.input_dir.new_mapping_sales_corrected_all)

        elif args.mode == 'data_analysis':
            config = ConfigLoad('end', 'null')
            emps = dataframe.is_not_done_carga(config.input_dir.cargas.control_flow, 'data_analysis')
            logger.info(f"Started to generate the data_analysis on the following companies {emps}")
            src.generate.do_data_analysis(emps)

    elif args.file == 'support':
        if args.mode == 'mapping_clientes':
            config = ConfigLoad('end', 'null')
            emps = dataframe.is_not_done_carga(config.input_dir.cargas.control_flow, 'mapping_cliente')
            logger.info(f"Started to get the past mapping_clients on the following companies {emps}")
            src.support.copy_mapping_clientes(emps)

        elif args.mode == 'mapping_item':
            config = ConfigLoad('end', 'null')
            emps = dataframe.is_not_done_carga(config.input_dir.cargas.control_flow, 'mapping_item')
            logger.info(f"Started to get the past mapping_item on the following companies {emps}")
            src.support.copy_mapping_item(emps)

        elif args.mode == 'mapping_vendas':
            config = ConfigLoad('end', 'null')
            emps = dataframe.is_not_done_carga(config.input_dir.cargas.control_flow, 'mapping')
            logger.info(f"Started to get the past mapping_sales on the following companies {emps}")
            src.support.copy_mapping_vendas(emps)

        elif args.mode == 'import_icg':
            config = ConfigLoad('end', 'null')
            emps = dataframe.is_not_done_carga(config.input_dir.cargas.control_flow, 'import')
            logger.info(f"Started to get the past import template on the following companies {emps}")
            src.support.copy_import_icg(emps)
        
        elif args.mode == 'ftp_dir':
            config = ConfigLoad('end', 'null')
            emps = dataframe.is_not_done_carga(config.input_dir.cargas.control_flow, 'ftp_dir')
            logger.info(f"Started to post the files on the ftp directory on the following companies {emps}")
            src.support.copy_ftp_dir(emps, config.input_dir.results)

        elif args.mode == 'new_mapping_clientes_all':
            config = ConfigLoad('end', 'null')
            emps = dataframe.is_not_done_carga(config.input_dir.cargas.control_flow, 'new_mapping_cliente')
            logger.info(f"Started to get the aggregated new_mapping_clientes on the following companies {emps}")
            src.support.copy_new_mapping_clientes_all(emps, config.input_dir)

        elif args.mode == 'mapping_item_all':
            config = ConfigLoad('end', 'null')
            emps = dataframe.is_not_done_carga(config.input_dir.cargas.control_flow, 'mapping_item')
            logger.info(f"Started to get the aggregated mapping_item on the following companies {emps}")
            src.support.copy_mapping_item_all(emps, config.input_dir)

        elif args.mode == 'new_mapping_vendas_all':
            config = ConfigLoad('end', 'null')
            emps = dataframe.is_not_done_carga(config.input_dir.cargas.control_flow, 'new_mapping')
            logger.info(f"Started to get the aggregated new_mapping_sales on the following companies {emps}")
            src.support.copy_new_mapping_vendas_all(emps, config.input_dir)

        elif args.mode == 'new_mapping_clientes_all_to_company_dir':
            config = ConfigLoad('end', 'null')
            logger.info(f"Started to post the segregated new_mapping_clients from the directory {config.input_dir}")
            src.support.copy_new_mapping_clientes_all_to_company_dir(config.input_dir)

        elif args.mode == 'mapping_item_all_to_company_dir':
            config = ConfigLoad('end', 'null')
            logger.info(f"Started to post the segregated mapping_item from the directory {config.input_dir}")
            src.support.copy_mapping_item_all_to_company_dir(config.input_dir)

        elif args.mode == 'new_mapping_vendas_all_to_company_dir':
            config = ConfigLoad('end', 'null')
            logger.info(f"Started to post the segregated new_mapping_sales from the directory {config.input_dir}")
            src.support.copy_new_mapping_vendas_all_to_company_dir(config.input_dir)

        elif args.mode == 'correct_new_mapping_vendas_all_to_company_dir':
            config = ConfigLoad('end', 'null')
            logger.info(f"Started to post the segregated correct_new_mapping_sales from the directory {config.input_dir}")
            src.support.copy_correct_new_mapping_vendas_to_company_dir(config.input_dir)

if __name__ == '__main__':
    main()