import pandas as pd
import locale
import datetime
from pathlib import Path

from io_excel import search_files

def get_carga_control_path(input_dir, date):

    return get_cargas_dir(input_dir, date) / 'carga.xlsx'

def load_carga_control_df(input_dir, date, excel_columns = None):

    carga_control_path = get_carga_control_path(input_dir, date)
    carga_control_df = pd.read_excel(
        carga_control_path,
        index_col = 'Empresas', 
        usecols = excel_columns
        )
    
    return carga_control_df

def update_carga_control_df(carga_control_df, input_dir, date):

    carga_control_path = get_carga_control_path(input_dir, date)
    carga_control_path = carga_control_path.parent / 'new_carga.xlsx'
    carga_control_df.to_excel(carga_control_path, index = 'Empresas')

def done(input_dir, date, control_type):
    carga_control_df = load_carga_control_df(input_dir, date, ('Empresas', control_type))
    done_emps = carga_control_df[carga_control_df[control_type] == True]
    return  (done_emps.index)

def not_done(input_dir, date, control_type):
    carga_control_df = load_carga_control_df(input_dir, date, ('Empresas', control_type))
    not_done_emps = carga_control_df[carga_control_df[control_type] == False]
    return tuple(not_done_emps.index)

def get_cargas_dir(input_dir, date):
    locale.setlocale(locale.LC_ALL, 'pt_pt.UTF-8')
    year_month_str = date.strftime('%Y/%m - %B').title()

    return input_dir / year_month_str

def get_dict_paths_control_type(cargas_dir, emp, date):

    locale.setlocale(locale.LC_ALL, 'pt_pt.UTF-8')
    year_month_str = date.strftime('%Y/%m - %B').title()

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
        'new_mapping': dir_path_carga('new_new_new_new_mapping.xlsx')
    }

    dict_new_mapping_type = {
        'new_mapping': dir_path_carga('new_mapping.xlsx')
    }

    dict_data_analysis_type = {
        'import': dir_path_output('import.xlsx'),
        'missing_vendas_csv': dir_path_output('missing_vendas_csv.xlsx'),
        'out_import': dir_path_output('out_import.xlsx'),
        'test_agg': dir_path_output('test_agg.xlsx'),
        'test_agg_clientes': dir_path_output('test_agg_clientes.xlsx'),
        'testing_mapping_vendas': dir_path_output('testing_mapping_vendas.xlsx'),
        'vendas_csv': dir_path_output('vendas_csv.xlsx')
    }

    dict_import_automatico_type = {
        'import': dir_path_output('import.xlsx'),
        'out_import': dir_path_output('out_import.xlsx')
    }

    dict_paths_control_type = {
        'webscraping': dict_webscraping_type,
        'mapping': dict_mapping_type,
        'correct_mapping': dict_correct_mapping_type,
        'new_mapping': dict_new_mapping_type,
        'data_analysis': dict_data_analysis_type,
        'import_automatico': dict_import_automatico_type
    }

    return dict_paths_control_type

def get_files_path_control(input_dir, date, control_type, emp):

    cargas_dir = get_cargas_dir(input_dir, date)
    dict_paths_control_type = get_dict_paths_control_type(cargas_dir, emp, date)
    return dict_paths_control_type[control_type]

def check_if_files_exist(path_files):
    ret = True
    for path_file in path_files:
        ret = ret & path_file.is_file()
    return ret

def update_done(input_dir, date, control_type):
    cargas_dir = get_cargas_dir(input_dir, date)
    carga_control_df = load_carga_control_df(input_dir, date)

    for emp in carga_control_df.index:
        print(emp)

        paths = get_files_path_control(input_dir, date, control_type, emp)
        files_exist = check_if_files_exist(paths)
        print(files_exist)

        carga_control_df.loc[emp, control_type] = files_exist

    print(carga_control_df)
    update_carga_control_df(carga_control_df, input_dir, date)

def main():

    input_dir = Path('data/input')
    end_date  = datetime.date(day = 8, month = 12, year = 2022)

    update_done(input_dir, end_date, 'webscraping')

if __name__ == '__main__':
    main()