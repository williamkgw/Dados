import argparse

import src.data_analysis
import src.file_manip
import src.io_excel
import src.io_import
import src.webscraping

parser = argparse.ArgumentParser(
                    description='Um programa para realizar ETL no sistema Quattrus'
                    )

parser.add_argument('file', help = 'Arquivo para executar')
parser.add_argument('mode', help = 'Tipo de execução do arquivo')

args = parser.parse_args()

if args.file == 'data_analysis':
    src.data_analysis.main()

elif args.file == 'file_manip':
    src.file_manip.main()

elif args.file == 'io_excel':
    src.io_excel.main()

elif args.file == 'io_import':
    src.io_import.main()
    
elif args.file == 'webscraping':
    src.webscraping.main()