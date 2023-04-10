import pandas as pd
import locale
import datetime
from pathlib import Path

def get_year_month_str(date):
    locale.setlocale(locale.LC_ALL, 'pt_pt.UTF-8')
    return date.strftime('%Y/%m - %B').title()

def get_cargas_dir(input_dir, date):
    year_month_str = get_year_month_str(date)
    return input_dir / year_month_str

def get_carga_dir(input_dir, emp, date):
    cargas_dir = get_cargas_dir(input_dir, date)
    year_month_str = get_year_month_str(date)
    return cargas_dir / f'{emp}/Carga/{year_month_str}'

def get_carga_path(input_dir, date):
    return get_cargas_dir(input_dir, date) / 'carga.xlsx'

def load_carga_df(input_dir, date, excel_columns = None):
    carga_path = get_carga_path(input_dir, date)
    carga_df = pd.read_excel(
        carga_path,
        index_col = 'Empresas', 
        usecols = excel_columns
        )
    return carga_df

def update_carga_df(carga_df, input_dir, date):
    carga_path = get_carga_path(input_dir, date)
    carga_path = carga_path.parent / 'new_carga.xlsx'
    carga_df.to_excel(carga_path, index = 'Empresas')

def is_done_carga(input_dir, date, control_type):
    carga_df = load_carga_df(input_dir, date, ('Empresas', control_type))
    done_emps = carga_df[carga_df[control_type] == True]
    return  (done_emps.index)

def is_not_done_carga(input_dir, date, control_type):
    carga_df = load_carga_df(input_dir, date, ('Empresas', control_type))
    not_done_emps = carga_df[carga_df[control_type] == False]
    return tuple(not_done_emps.index)

def check_if_files_exist(path_files):
    ret = True
    for path_file in path_files:
        ret = ret & path_file.is_file()
    return ret

def update_done_carga(input_dir, date, control_type):
    carga_df = load_carga_df(input_dir, date)

    for emp in carga_df.index:
        print(emp)

        paths = get_files_path_control(input_dir, date, control_type, emp)
        files_exist = check_if_files_exist(paths)
        print(files_exist)

        carga_df.loc[emp, control_type] = files_exist

    print(carga_df)
    update_carga_df(carga_df, input_dir, date)

def get_dict_control_type_paths(cargas_dir, emp, date):
    year_month_str = get_year_month_str(date)

    dir_path_carga  = lambda arquivo: cargas_dir / f'{emp}/Carga/{year_month_str}/{arquivo}'
    dir_path_output = lambda arquivo: cargas_dir / f'{emp}/Carga/{year_month_str}/output/{arquivo}'

    dict_webscraping_type = {
        'Vendas': dir_path_carga('Vendas.csv'),
        'Clientes': dir_path_carga('Clientes.csv')
    }
    
    dict_mapping_type = {
        'mapping': dir_path_carga('mapping.xlsx')
    }

    dict_correct_mapping_type = {
        'mapping': dir_path_carga('mapping.xlsx'),
        'new_mapping': dir_path_carga('new_mapping.xlsx')
    }

    dict_new_mapping_type = {
        'new_mapping': dir_path_carga('new_mapping.xlsx')
    }

    dict_data_analysis_type = {
        'import': dir_path_carga('import.xlsx'),
        'out_import': dir_path_output('out_import.xlsx'),
        'test_agg': dir_path_output('test_agg.xlsx'),
        'test_agg_clientes': dir_path_output('test_agg_clientes.xlsx'),
        'testing_mapping_vendas': dir_path_output('testing_mapping_vendas.xlsx'),
        'missing_vendas_csv': dir_path_output('missing_vendas_csv.xlsx'),
        'vendas_csv': dir_path_output('vendas_csv.xlsx')
    }

    dict_import_automatico_type = {
        'import': dir_path_carga('import.xlsx'),
        'out_import': dir_path_output('out_import.xlsx')
    }

    dict_control_type_paths = {
        'webscraping': dict_webscraping_type,
        'mapping': dict_mapping_type,
        'correct_mapping': dict_correct_mapping_type,
        'new_mapping': dict_new_mapping_type,
        'data_analysis': dict_data_analysis_type,
        'import_automatico': dict_import_automatico_type
    }

    return dict_control_type_paths

def get_files_path_control(input_dir, date, control_type, emp):
    cargas_dir = get_cargas_dir(input_dir, date)
    dict_control_type_paths = get_dict_control_type_paths(cargas_dir, emp, date)
    return dict_control_type_paths[control_type]

END_DATE = datetime.date(day = 31, month = 3, year = 2023)
BEG_DATE = datetime.date(day = 28, month = 2, year = 2023)
INPUT_DIR = Path('data/input')