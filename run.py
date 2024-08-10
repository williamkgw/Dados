import argparse
import logging

import src.extraction.webscraping
import src.transform.import_icg.import_icg
import src.transform.import_icg.import_icg_triple_check
import src.transform.mapping.mapping_clientes
import src.transform.mapping.mapping_item
import src.transform.mapping.mapping_vendas
import src.transform.clientes_vendas
import src.load.mapping.mapping_clientes
import src.load.mapping.mapping_item
import src.load.mapping.mapping_vendas
import src.load.import_icg
import src.load.ftp_dir

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

    if args.file == 'extraction':
        if args.mode == 'webscraping':
            src.extraction.webscraping.extract_webscraping()

    elif args.file == 'transform':
        if args.mode == 'import_icg':
            src.transform.import_icg.import_icg.transform_med_import()

        elif args.mode == 'import_icg_triple_check':
            src.transform.import_icg.import_icg_triple_check.transform_triple_check()

        elif args.mode == 'mapping_item':
            src.transform.mapping.mapping_item.transform_mapping_item()
        
        elif args.mode == 'new_mapping':
            src.transform.mapping.mapping_vendas.transform_new_mapping()

        elif args.mode == 'new_mapping_cliente':
            src.transform.mapping.mapping_clientes.transform_new_mapping_clientes()

        elif args.mode == 'correct_new_mapping':
            src.transform.mapping.mapping_vendas.transform_correct_new_mapping()

        elif args.mode == 'data_analysis':
            src.transform.clientes_vendas.transform_data_analysis()

    elif args.file == 'load':
        if args.mode == 'mapping_clientes':
            src.load.mapping.mapping_clientes.load_mapping_clientes()

        elif args.mode == 'mapping_item':
            src.load.mapping.mapping_item.load_mapping_item()

        elif args.mode == 'mapping_vendas':
            src.load.mapping.mapping_vendas.load_mapping_vendas()

        elif args.mode == 'import_icg':
            src.load.import_icg.load_import_icg()
        
        elif args.mode == 'ftp_dir':
            src.load.ftp_dir.load_ftp_dir()

        elif args.mode == 'new_mapping_clientes_all':
            src.load.mapping.mapping_clientes.load_new_mapping_clientes_all()

        elif args.mode == 'mapping_item_all':
            src.load.mapping.mapping_item.load_mapping_item_all()

        elif args.mode == 'new_mapping_vendas_all':
            src.load.mapping.mapping_vendas.load_new_mapping_vendas_all()

        elif args.mode == 'new_mapping_clientes_all_to_company_dir':
            src.load.mapping.mapping_clientes.load_new_mapping_clientes_all_to_company_dir()

        elif args.mode == 'mapping_item_all_to_company_dir':
            src.load.mapping.mapping_item.load_mapping_item_all_to_company_dir()

        elif args.mode == 'new_mapping_vendas_all_to_company_dir':
            src.load.mapping.mapping_vendas.load_new_mapping_vendas_all_to_company_dir()

        elif args.mode == 'correct_new_mapping_vendas_all_to_company_dir':
            src.load.mapping.mapping_vendas.load_correct_new_mapping_vendas_to_company_dir()

if __name__ == '__main__':
    main()