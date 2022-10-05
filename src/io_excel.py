import pandas as pd
from pathlib import Path

def search_files(root_dir, pattern):

    files = root_dir.rglob(pattern)
    files = sorted(files)

    return files

def get_list_path(date):

    root_dir = Path('C:/Users/willi/OneDrive/Documentos/Programas/Database/.Gestão Pet Clientes')
    
    search_string = f'**/Carga/{date}/*-*Vendas*.xlsx'
    ret = search_files(root_dir, search_string)
    
    search_string = f'**/Carga/{date}/vendas_6_meses.csv'
    new_files = search_files(root_dir, search_string)
    ret.extend(new_files)

    emps = set([path.parents[3].name for path in ret])
    paths = []
    for emp in emps:

        emp_files = [file for file in ret if file.parents[3].name == emp]
        emp_files_mtime = [file.stat().st_mtime for file in emp_files]
        emp_files_name = [file.name for file in emp_files]

        vendas_new = 'vendas_6_meses.csv'
        if vendas_new in emp_files_name:
            searched_index = emp_files_name.index(vendas_new)
            paths.append(emp_files[searched_index])
        else:
            max_mtime = max(emp_files_mtime)
            searched_index = emp_files_mtime.index(max_mtime)
            paths.append(emp_files[searched_index])
                
    return sorted(paths)

def get_vendas(depara_vendas_f):
    vendas_new = 'vendas_6_meses.csv'
    if depara_vendas_f.name == vendas_new:
        get_vendas_new(depara_vendas_f)
    else:
        get_vendas_old(depara_vendas_f)

def get_mapping(depara_vendas_f):
    vendas_new = 'vendas_6_meses.csv'
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
        df['__emp'] = emp

        mapping_f = Path('data/output/mappings/' + depara_f.stem + ' mapping.xlsx')
        df.to_excel(mapping_f, index = False)
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

    paths = root_dir.rglob('*.xlsx')
    paths = sorted(paths)

    a = dict()
    for path in paths:
        
        df = pd.read_excel(path)
        emp = df['__emp'].values[0]
        print(emp)

        a.update({emp: df.columns})

    df_all = pd.DataFrame.from_dict(a, orient='index')
    df_all.to_excel('columns_vendas_all.xlsx')

def get_mapping_all_from_files(paths):

    mapping_all_df = pd.DataFrame()
    emps = ['Almir Tavares', 'Amor Cão e Gato', 'Amor de Bichos - MG', 'Animed RS', 'Arca de Noé - ES', 'Auqmia RJ', 'BEVET SP', 'Burlina', 'Cia Veterinária RJ', 'Cidade dos Bichos SP', 'EBVet', 'Fórmula Pet', 'Mania Animal', 'MyVet - Morumbi - SP', 'Tierplatz RS', 'Vet dos Anjos SP', 'VetCenter MT']

    for path in paths:
        mapping_df = pd.read_excel(path)
        emp = mapping_df['__emp'].values[0]

        if emp not in emps:
            continue
        mapping_all_df = pd.concat([mapping_df, mapping_all_df])
    
    return mapping_all_df

def get_mapping_all(paths, mapping_all_f):
    
    mapping_all_df = pd.DataFrame()

    for path in paths:
        
        empresa = path.parents[3].name
        print(empresa)

        mapping_df = pd.read_excel(path, sheet_name = 'mapping_vendas', index_col = 'Produto/serviço')
        mapping_df['Empresa'] = empresa
        
        if 'Categoria' not in set(mapping_df.columns):
            mapping_df['Categoria'] = pd.NA 
        
        mapping_all_df = pd.concat([mapping_all_df, mapping_df])

    mapping_all_df.to_excel(mapping_all_f, columns = ['Categoria', 'Pilar', 'Grupo', 'Empresa'])

def read_and_get_from_mapping_all(mapping_all_f, date):

    mapping_all_df = pd.read_excel(mapping_all_f, index_col = 'Produto/serviço')
    
    for name, group in mapping_all_df.groupby('Empresa'):

        empresa = name
        new_dir     = Path('.') / f'data/input/{empresa}/Carga/{date}'
        new_mapping = new_dir / 'mapping.xlsx'
        print(f'read_and_get_from_mapping_all: {new_mapping} :{new_mapping.is_file()}')
        
        #remove cols
        cols = set(group.columns)
        cols.remove('Empresa')
        cols = list(cols)

        new_mapping_df = group[cols]
        new_dir.mkdir(parents = True, exist_ok = True)
        new_mapping_df.to_excel(new_mapping, sheet_name = 'mapping_vendas', index = 'Produto/serviço',
        columns = ['Categoria', 'Pilar', 'Grupo'])