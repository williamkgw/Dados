import pandas as pd
from pathlib import Path

def get_paths_from_depara(month):
    paths = sorted(Path('.').rglob(f'{month}/*Vendas*.xlsx'))

    return paths

def get_paths_from_mappings(month):
    print(f'{month}/mapping.xlsx')

    paths = sorted(Path('.').rglob(f'{month}/mapping.xlsx'))

def get_reagrupa(depara_f):

    excel_file = pd.ExcelFile(depara_f)
    sheet_to_find = 'Reagrupa'

    sheet_names = excel_file.sheet_names
    sheet_names = [name.lower() for name in sheet_names]

    index = sheet_names.index(sheet_to_find.lower())

    sheet_needed = pd.read_excel(excel_file, sheet_name = index)

    df = sheet_needed.iloc[:, 0:3]
    
    df.columns = ['Produto/serviço', 'Grupo', 'Pilar']

    mapping_f = depara_f.parent.parent / '08 - Agosto/mapping.xlsx'
    df.to_excel(mapping_f, sheet_name = 'mapping_vendas', index = False)

def get_mapping_all(paths, mapping_all_f):
    
    mapping_all_df = pd.DataFrame()

    for path in paths:
        
        empresa = path.parents[1].name
        print(empresa)

        input_path          = path.parent.parent / '08 - Agosto'
        input_file_mapping          = input_path / 'new_mapping.xlsx'

        mapping_df = pd.read_excel(input_file_mapping, sheet_name = 'mapping_vendas', index_col = 'Produto/serviço')
        mapping_df['Empresa'] = empresa
        
        if 'Categoria' not in set(mapping_df.columns):
            mapping_df['Categoria'] = pd.NA 
        
        mapping_all_df = pd.concat([mapping_all_df, mapping_df])

    mapping_all_df.to_excel(mapping_all_f, columns = ['Categoria', 'Pilar', 'Grupo', 'Empresa'])

def read_and_get_from_mapping_all(mapping_all_f):

    mapping_all_df = pd.read_excel(mapping_all_f, index_col = 'Produto/serviço')
    
    for name, group in mapping_all_df.groupby('Empresa'):

        empresa = name
        new_mapping = Path('.') / f'data/input/{empresa}/08 - Agosto/new_mapping.xlsx'
        print(f'read_and_get_from_mapping_all: {new_mapping} :{new_mapping.is_file()}')
        
        #remove cols
        cols = set(group.columns)
        cols.remove('Empresa')
        cols = list(cols)

        new_mapping_df = group[cols]
        new_mapping_df.to_excel(new_mapping, sheet_name = 'mapping_vendas', index = 'Produto/serviço',
        columns = ['Categoria', 'Pilar', 'Grupo'])