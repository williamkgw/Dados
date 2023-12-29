import pandas as pd

import src.utils as utils
from src.config import END_DATE, INPUT_DIR

def template_mapping_item_add_rows(mapping_df):

    cat     = 'Categoria'
    pil     = 'Pilar'
    grup    = 'Grupo'
    op      = 'Op'
    op_exec = 'Op_execao'

    get_unique_values_from_series = lambda df, column : list(set(df[column].values))

    mapping_categoria_cols  = get_unique_values_from_series(mapping_df, cat)
    mapping_pilar_cols      = get_unique_values_from_series(mapping_df, pil)
    mapping_grupo_cols      = get_unique_values_from_series(mapping_df, grup)
    op_cols                 = ['Faturamento Bruto', 'Faturamento Médio por Clientes', 'Preço Médio', 'Quantidade Totalizada', 'Tickets Médio']
    op_exec_cols            = ['Consultas/Cirurgias', 'Consultas/Internação', 'Exames/Consultas']

    df_cat           = pd.DataFrame(mapping_categoria_cols, columns = [cat])
    df_pil           = pd.DataFrame(mapping_pilar_cols, columns = [pil])
    df_grup          = pd.DataFrame(mapping_grupo_cols, columns = [grup])
    df_op_cols       = pd.DataFrame(op_cols, columns = [op])
    df_op_exec_cols  = pd.DataFrame(op_exec_cols, columns = [op_exec])

    df = pd.concat([df_cat, df_pil, df_grup, df_op_cols, df_op_exec_cols]).reset_index(drop = True)
    return df

def template_mapping_item(import_file, mapping_file):
    template_import_cols    =   ('ID do Item', 'Mês', 'Ano', 'Item')
    template_filtering_cols =   ('Totalizado', )
    import_df_cols = template_import_cols + template_filtering_cols

    index_import = 'ID do Item'

    import_df = pd.read_excel(import_file, usecols = import_df_cols, index_col = index_import)
    filtered_import_df = import_df.drop(list(template_filtering_cols), axis = 1)
        
    mapping_df = pd.read_excel(mapping_file, index_col = 'Produto/serviço')
    add_rows_df = template_mapping_item_add_rows(mapping_df)

    mapping_item_df = pd.concat([filtered_import_df, add_rows_df])

    mapping_item_df['Multiplicador'] = 1
    mapping_item_df[add_rows_df.columns] = mapping_item_df[add_rows_df.columns].fillna('x')

    output_path = mapping_file.parent / 'mapping_item.xlsx'

    mapping_item_df.index.name = index_import
    mapping_item_df.to_excel(output_path, index = index_import)

    return mapping_item_df

def get_mapping_item(import_paths, emps_filter, input_dir, end_date):
    for import_path in import_paths:
        emp = import_path.parents[3].name
        if emp not in emps_filter:
            continue
        print(emp)
        
        carga_dir = utils.get_carga_dir(input_dir, emp, end_date)
        mapping = carga_dir / 'mapping.xlsx'
        template_mapping_item_f = carga_dir / 'mapping_item.xlsx'

        template_mapping_item_df = template_mapping_item(import_path, mapping)
        template_mapping_item_df.to_excel(template_mapping_item_f)

def transform_mapping_item():
    cargas_dir = utils.get_cargas_dir(INPUT_DIR, END_DATE)
    import_paths = cargas_dir.rglob('import.xlsx')
    emps = utils.is_not_done_carga(INPUT_DIR, END_DATE, 'mapping_item')
    get_mapping_item(import_paths, emps, INPUT_DIR, END_DATE)