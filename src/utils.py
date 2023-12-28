import locale
import shutil
from pathlib import Path
import pandas as pd
import yaml

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

def is_not_done_carga(input_dir, date, control_type):
    carga_df = load_carga_df(input_dir, date, ('Empresas', control_type))
    not_done_emps = carga_df[carga_df[control_type] == False]
    return tuple(not_done_emps.index)

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

def get_file_on_dir(paths, emps_filter, input_dir, end_date):
    for path in paths:
        emp = path.parents[3].name
        if emp not in emps_filter:
            continue
        filename_with_extension = path.name
        output_path = get_carga_dir(input_dir, emp, end_date) / filename_with_extension
        shutil.copy2(path, output_path)

def change_filename_on_dir(paths, emps_filter, filename):
    for path in paths:
        emp = path.parents[3].name
        if emp not in emps_filter:
            continue
        path.rename(path.parent / filename)

def df_all(paths_f, emps_filter, path_all_f, n):
    df = pd.DataFrame()

    for path_f in paths_f:
        emp = path_f.parents[n].name
        if emp not in emps_filter:
            continue
        print(emp)
        df_new = pd.read_excel(path_f)
        df_new['Empresa'] = emp
        df_new['path'] = path_f
        df = pd.concat([df, df_new])
    
    df.to_excel(path_all_f, index = False)

def df_all_to_df(path_all_f):

    df = pd.read_excel(path_all_f, index_col = 0)

    for name, group in df.groupby('Empresa'):
        print(name)

        path = group['path'].iloc[0]
        path = Path(path)

        df = pd.DataFrame(data = group, columns = group.columns[:-2])
        
        print(path)
        if path.parent.is_dir():
            df.to_excel(path)
        else:
            print('NÃO EXISTE: ', name)

def get_config(config_path):

    config_path = Path(config_path)
    with open(config_path, 'r') as file:
        config = yaml.safe_load(file)

    return config