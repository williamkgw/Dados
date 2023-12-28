import argparse
import logging

import src.data_analysis
import src.io_import

from src.config import INPUT_DIR, END_DATE
import src.utils as utils

import src.extraction.webscraping
import src.load.mapping.mapping_clientes
import src.load.mapping.mapping_item
import src.load.mapping.mapping_vendas
import src.load.import_icg
import src.load.ftp_dir

def main():
    cargas_dir = utils.get_cargas_dir(INPUT_DIR, END_DATE)
    logging.basicConfig(filename = cargas_dir / 'log.log', filemode = 'w', encoding = 'utf-8')

    parser = argparse.ArgumentParser(
                        description='Um programa para realizar ETL no sistema Quattrus'
                        )

    parser.add_argument('file', help = 'Arquivo para executar')
    parser.add_argument('mode', help = 'Tipo de execução do arquivo')

    args = parser.parse_args()

    # Programa Refatorado
    if args.file == 'extraction':
        if args.mode == 'webscraping':
            src.extraction.webscraping.extract_webscraping()

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

    # Programa Legado

    if args.file == 'data_analysis':
        src.data_analysis.main()

    elif args.file == 'io_import':
        src.io_import.main()

if __name__ == '__main__':
    main()