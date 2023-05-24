from pathlib import Path
import pandas as pd
import logging
import carga_control

def search_files(root_dir, pattern):
    return sorted(root_dir.rglob(pattern))

def get_list_path(year_month_s):

    root_dir = Path('C:/Users/willi/OneDrive/Documentos/Programas/Database/gpet/.Gestão Pet Clientes')
    
    search_string = f'**/Carga/{year_month_s}/*-*Vendas*.xlsx'
    ret = search_files(root_dir, search_string)
    
    search_string = f'**/Carga/{year_month_s}/new_mappign.xlsx'
    new_files = search_files(root_dir, search_string)
    ret.extend(new_files)

    emps = set([path.parents[3].name for path in ret])
    paths = []
    for emp in emps:

        emp_files = [file for file in ret if file.parents[3].name == emp]
        emp_files_mtime = [file.stat().st_mtime for file in emp_files]
        emp_files_name = [file.name for file in emp_files]

        vendas_new = 'Vendas.csv'
        if vendas_new in emp_files_name:
            searched_index = emp_files_name.index(vendas_new)
            paths.append(emp_files[searched_index])
        else:
            max_mtime = max(emp_files_mtime)
            searched_index = emp_files_mtime.index(max_mtime)
            paths.append(emp_files[searched_index])
                
    return sorted(paths)

def get_vendas(depara_vendas_f):
    vendas_new = 'Vendas.csv'
    if depara_vendas_f.name == vendas_new:
        get_vendas_new(depara_vendas_f)
    else:
        get_vendas_old(depara_vendas_f)

def get_mapping(depara_vendas_f):
    vendas_new = 'Vendas.csv'
    if depara_vendas_f.name == vendas_new:
        get_mapping_new(depara_vendas_f)
    else:
        get_mapping_old(depara_vendas_f)

def get_vendas_old(depara_f):
    emp = depara_f.parents[3].name

    excel_file = pd.ExcelFile(depara_f)
    sheet_to_find = 'Vendas'

    sheet_names = excel_file.sheet_names
    sheet_names = [name.lower() for name in sheet_names]

    if sheet_to_find.lower() in sheet_names:
        index = sheet_names.index(sheet_to_find.lower())

        sheet_needed = pd.read_excel(excel_file, sheet_name = index)
        sheet_needed['__emp'] = emp

        vendas_f = Path('data/output/vendas/' + depara_f.stem + '.xlsx')
        sheet_needed.to_excel(vendas_f, index = False)
    else:
        file = depara_f.name

        log_error = f'not found vendas: {emp}\n in file: {file}'
        print(log_error)

def get_mapping_old(depara_f):
    emp = depara_f.parents[3].name

    excel_file = pd.ExcelFile(depara_f)
    sheet_to_find = 'Reagrupa'

    sheet_names = excel_file.sheet_names
    sheet_names = [name.lower() for name in sheet_names]

    if sheet_to_find.lower() in sheet_names:

        index = sheet_names.index(sheet_to_find.lower())

        sheet_needed = pd.read_excel(excel_file, sheet_name = index)

        df = sheet_needed.iloc[:, 0:3].copy()
        df.columns = ['Produto/serviço', 'Grupo', 'Pilar']
        df['Categoria'] = pd.NA
        df = df.set_index('Produto/serviço').iloc[:, [2, 1, 0]]
        return df
    else:
        file = depara_f.name

        log_error = f'not found reagrupa: {emp}\n in file: {file}'
        print(log_error)

def get_vendas_new(vendas_f):

    sheet_needed = pd.read_csv(vendas_f, thousands = '.', decimal = ',', 
    encoding = 'latin1', sep = ';')

    emp = vendas_f.parents[3].name
    sheet_needed['__emp'] = emp

    vendas_f = Path(f'data/output/vendas/{emp} - new vendas.xlsx')
    sheet_needed.to_excel(vendas_f, index = False)

def get_mapping_new(vendas_f):
    mapping_f = vendas_f.parent / 'mapping.xlsx'

    sheet_needed = pd.read_excel(mapping_f)

    emp = mapping_f.parents[3].name
    sheet_needed['__emp'] = emp
    mapping_f = Path(f'data/output/mappings/{emp} - new mapping.xlsx')
    sheet_needed.to_excel(mapping_f, index = False)

def get_columns_of_vendas():
    root_dir = Path('data/output/vendas')
    paths = search_files(root_dir, '*.xlsx')

    a = dict()
    for path in paths:
        
        df = pd.read_excel(path)
        emp = df['__emp'].values[0]
        print(emp)

        a.update({emp: df.columns})

    df_all = pd.DataFrame.from_dict(a, orient='index')
    df_all.to_excel('columns_vendas_all.xlsx')

def get_vendas_all(paths, vendas_all_f):
    
    vendas_all_df = pd.DataFrame()

    print(paths)
    for path in paths:
        
        empresa = path.parents[4].name
        print(empresa)

        vendas_df = pd.read_excel(path)
        vendas_df['Empresa'] = empresa
        
        vendas_all_df = pd.concat([vendas_all_df, vendas_df])

    vendas_all_df.to_excel(vendas_all_f)

def get_mapping_all_from_files(paths):

    mapping_all_df = pd.DataFrame()

    for path in paths:
        mapping_df = pd.read_excel(path)
        emp = mapping_df['__emp'].values[0]

        mapping_all_df = pd.concat([mapping_df, mapping_all_df])
    
    return mapping_all_df

def get_mapping_all(paths, mapping_all_f):
    
    mapping_all_df = pd.DataFrame()

    print(paths)
    for path in paths:
        
        empresa = path.parents[3].name
        print(empresa)

        mapping_df = pd.read_excel(path, index_col = 'Produto/serviço')
        mapping_df['Empresa'] = empresa
        
        if 'Categoria' not in set(mapping_df.columns):
            mapping_df['Categoria'] = pd.NA 
        
        mapping_all_df = pd.concat([mapping_all_df, mapping_df])

    mapping_all_df.to_excel(mapping_all_f)

def read_and_get_from_mapping_all(database_dir, mapping_all_f, date):

    year_month_s = date.strftime('%Y/%m - %B').title()

    mapping_all_df = pd.read_excel(mapping_all_f, index_col = 'Produto/serviço')
    
    for name, group in mapping_all_df.groupby('Empresa'):

        empresa = name
        new_dir     = database_dir / f'{empresa}/Carga/{year_month_s}'
        new_mapping = new_dir / 'new_mapping.xlsx'
        print(f'{new_mapping.is_file()} : read_and_get_from_mapping_all: {empresa}')
        
        #remove cols
        cols = set(group.columns)
        cols.remove('Empresa')
        cols = list(cols)

        new_mapping_df = group[cols]
        new_dir.mkdir(parents = True, exist_ok = True)
        new_mapping_df.to_excel(new_mapping, sheet_name = 'mapping_vendas', index = 'Produto/serviço',
        columns = ['Categoria', 'Pilar', 'Grupo'])

def read_and_get_from_mapping_item_all(database_dir, mapping_item_all_f, date):

    mapping_item_all_df = pd.read_excel(mapping_item_all_f, index_col = 'ID do Item')
    
    for name, group in mapping_item_all_df.groupby('Empresa'):

        empresa = name
        new_dir     = database_dir / f'{empresa}/Carga/{date}'
        new_mapping = new_dir / 'new_mapping_item.xlsx'
        print(f'{new_mapping.is_file()} : read_and_get_from_mapping_item_all: {empresa}')
        
        #remove cols
        cols = set(group.columns)
        cols.remove('Empresa')
        cols = list(cols)

        new_mapping_df = group[cols]
        new_dir.mkdir(parents = False, exist_ok = True)
        new_mapping_df.to_excel(new_mapping, index = 'ID do Item', columns = ('Mês', 'Ano', 'Item', 'Categoria', 'Pilar', 'Grupo', 'Op', 'Op_execao', 'Multiplicador'))


def get_import(dest_dir, dest_date, src_dir, src_date, emps):

    year_month_src_s  = src_date.strftime('%Y/%m - %B').title()
    year_month_dest_s = dest_date.strftime('%Y/%m - %B').title()

    search_pattern = f'Carga/{year_month_src_s}/output/out_import.xlsx'
    src_imports = search_files(src_dir, search_pattern)
    
    for src_import in src_imports:
        emp = src_import.parents[4].name
        if emp not in emps:
            print(f'not iiiiiiin: {emp}')
            continue
        print(emp)

        dest_carga_dir = Path(f'{dest_dir}/{year_month_dest_s}/{emp}/Carga/{year_month_dest_s}/output')

        dest_carga_import_f = dest_carga_dir / 'import.xlsx'

        src_carga_import_df = pd.read_excel(src_import, index_col = 'ID do Item')
        src_carga_import_df['Mês'] = dest_date.month
        src_carga_import_df['Ano'] = dest_date.year
        columns_to_fill_na = ['Medição', 'Fx Verde Inf/Previsto', 'Fx Verde Sup',
                             'Fx Vermelha Inf', 'Fx Vermelha Sup', 'Fx Cliente Inf', 'Fx Cliente Sup']
        src_carga_import_df[columns_to_fill_na] = pd.NA
        
        src_carga_import_df.to_excel(dest_carga_import_f)

def get_mapping_item(dest_dir, dest_date, src_dir, src_date, emps):

    year_month_src_s  = src_date.strftime('%Y/%m - %B').title()
    year_month_dest_s = dest_date.strftime('%Y/%m - %B').title()

    search_pattern = f'Carga/{year_month_src_s}/mapping_item.xlsx'
    src_mapping_items = search_files(src_dir, search_pattern)
    
    for src_mapping_item in src_mapping_items:
        print(src_mapping_item)
        emp = src_mapping_item.parents[3].name
        if emp not in emps:
            print(f'not iiiiiiin: {emp}')
            continue
        print(emp)

        dest_carga_dir = Path(f'{dest_dir}/{year_month_dest_s}/{emp}/Carga/{year_month_dest_s}')

        dest_carga_mapping_item_f = dest_carga_dir / 'mapping_item.xlsx'

        src_carga_mapping_item_df = pd.read_excel(src_mapping_item, index_col = 'ID do Item')
        src_carga_mapping_item_df['Mês'] = dest_date.month
        src_carga_mapping_item_df['Ano'] = dest_date.year
        
        print(dest_carga_mapping_item_f)
        src_carga_mapping_item_df.to_excel(dest_carga_mapping_item_f)

def delete_files(paths):
    for path in paths:
        path.unlink()

def delete_input_data_carga(input_dir, date):
    cargas_dir = carga_control.get_cargas_dir(input_dir , date)
    vendas_paths = cargas_dir.rglob('Vendas.csv')
    clientes_paths = cargas_dir.rglob('Clientes.csv')

    delete_files(vendas_paths)
    delete_files(clientes_paths)

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

def main():
    import sys

    END_DATE = carga_control.END_DATE
    INPUT_DIR = carga_control.INPUT_DIR
    cargas_dir = carga_control.get_cargas_dir(INPUT_DIR, END_DATE)
    logging.basicConfig(filename = cargas_dir / 'log.log', filemode = 'w', encoding = 'utf-8')

    assert len(sys.argv) == 2
    type_of_execution = sys.argv[1]

    if type_of_execution == 'new_mapping':
        emps = carga_control.is_not_done_carga(INPUT_DIR, END_DATE, 'new_mapping')
        print(emps)
        new_mapping_paths = carga_control.get_cargas_dir(INPUT_DIR, END_DATE).rglob('new_mapping.xlsx')
        df_all(new_mapping_paths, emps, f'{INPUT_DIR}/new_mapping_all.xlsx', 3)

    elif type_of_execution == 'new_mapping_all':
        df_all_to_df(f'{INPUT_DIR}/new_mapping_all_preenchido.xlsx')

    elif type_of_execution == 'correct_mapping':
        df_all_to_df(f'{INPUT_DIR}/corrected_new_mapping_preenchido.xlsx')

if __name__ == '__main__':
    main()