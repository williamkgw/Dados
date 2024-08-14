import argparse
import logging

import src.util.dataframe as dataframe

import src.scrape
import src.generate
import src.support

from src.config import ConfigLoad

def main():
    config = ConfigLoad('end', 'null')
    logging.basicConfig(filename = config.input_dir.cargas.log, filemode = 'w', encoding = 'utf-8')

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
            print(emps)
            src.scrape.get_logins(emps, config.input_dir.cargas.credentials)

    elif args.file == 'generate':
        if args.mode == 'import_icg':
            config = ConfigLoad('end',  'null')
            emps = dataframe.is_not_done_carga(config.input_dir.cargas.control_flow, 'import_automatico')
            print(emps)
            src.generate.get_med_import(emps)

        elif args.mode == 'import_icg_triple_check':
            config = ConfigLoad('end',  'null')
            emps = dataframe.is_not_done_carga(config.input_dir, config.date, 'triple_check')
            print(emps)
            src.generate.triple_check(emps)

        elif args.mode == 'mapping_item':
            config = ConfigLoad('end', 'null')
            emps = dataframe.is_not_done_carga(config.input_dir.cargas.control_flow, 'mapping_item')
            src.generate.get_mapping_item(emps)
        
        elif args.mode == 'new_mapping':
            config = ConfigLoad('end', 'null')
            emps = dataframe.is_not_done_carga(config.input_dir.cargas.control_flow, 'new_mapping')
            print(emps)
            src.generate.get_new_mapping(emps)

        elif args.mode == 'new_mapping_cliente':
            config = ConfigLoad('end', 'null')
            emps = dataframe.is_not_done_carga(config.input_dir.cargas.control_flow, 'new_mapping_cliente')
            print(emps)
            src.generate.get_new_mapping_cliente(emps)

        elif args.mode == 'correct_new_mapping':
            config = ConfigLoad('end', 'null')
            emps = dataframe.is_not_done_carga(config.input_dir.cargas.control_flow, 'correct_mapping')
            print(emps)
            src.generate.filter_and_correct_new_mapping_all(emps, config.input_dir.new_mapping_sales_corrected_all)

        elif args.mode == 'data_analysis':
            config = ConfigLoad('end', 'null')
            emps = dataframe.is_not_done_carga(config.input_dir.cargas.control_flow, 'data_analysis')
            print(emps)
            src.generate.do_data_analysis(emps)

    elif args.file == 'support':
        if args.mode == 'mapping_clientes':
            config = ConfigLoad('end', 'null')
            emps = dataframe.is_not_done_carga(config.input_dir.cargas.control_flow, 'mapping_cliente')
            print(emps)
            src.support.copy_mapping_clientes(emps)

        elif args.mode == 'mapping_item':
            config = ConfigLoad('end', 'null')
            emps = dataframe.is_not_done_carga(config.input_dir.cargas.control_flow, 'mapping_item')
            print(emps)
            src.support.copy_mapping_item(emps)

        elif args.mode == 'mapping_vendas':
            config = ConfigLoad('end', 'null')
            emps = dataframe.is_not_done_carga(config.input_dir.cargas.control_flow, 'mapping')
            print(emps)
            src.support.copy_mapping_vendas(emps)

        elif args.mode == 'import_icg':
            config = ConfigLoad('end', 'null')
            emps = dataframe.is_not_done_carga(config.input_dir.cargas.control_flow, 'import')
            print(emps)
            src.support.copy_import_icg(emps)
        
        elif args.mode == 'ftp_dir':
            config = ConfigLoad('end', 'null')
            emps = dataframe.is_not_done_carga(config.input_dir.cargas.control_flow, 'ftp_dir')
            print(emps)
            src.support.copy_ftp_dir(emps, config.input_dir.results)

        elif args.mode == 'new_mapping_clientes_all':
            config = ConfigLoad('end', 'null')
            emps = dataframe.is_not_done_carga(config.input_dir.cargas.control_flow, 'new_mapping_cliente')
            print(emps)
            src.support.copy_new_mapping_clientes_all(emps, config.input_dir)

        elif args.mode == 'mapping_item_all':
            config = ConfigLoad('end', 'null')
            emps = dataframe.is_not_done_carga(config.input_dir.cargas.control_flow, 'mapping_item')
            print(emps)
            src.support.copy_mapping_item_all(emps, config.input_dir)

        elif args.mode == 'new_mapping_vendas_all':
            config = ConfigLoad('end', 'null')
            emps = dataframe.is_not_done_carga(config.input_dir.cargas.control_flow, 'new_mapping')
            print(emps)
            src.support.copy_new_mapping_vendas_all(emps, config.input_dir)

        elif args.mode == 'new_mapping_clientes_all_to_company_dir':
            config = ConfigLoad('end', 'null')
            src.support.copy_new_mapping_clientes_all_to_company_dir(config.input_dir)

        elif args.mode == 'mapping_item_all_to_company_dir':
            config = ConfigLoad('end', 'null')
            src.support.copy_mapping_item_all_to_company_dir(config.input_dir)

        elif args.mode == 'new_mapping_vendas_all_to_company_dir':
            config = ConfigLoad('end', 'null')
            src.support.copy_new_mapping_vendas_all_to_company_dir(config.input_dir)

        elif args.mode == 'correct_new_mapping_vendas_all_to_company_dir':
            config = ConfigLoad('end', 'null')
            src.support.copy_correct_new_mapping_vendas_to_company_dir(config.input_dir)

if __name__ == '__main__':
    main()