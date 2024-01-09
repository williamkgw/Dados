import pandas as pd
import numpy as np

import src.utils as utils
from src.config import END_DATE, INPUT_DIR

def med_n_levels(import_df, agg_vendas_df, mapping_item_df, mapping_item_cols, n):
    id_item_col = 'ID do Item'
    constant_col = 'Multiplicador'

    numero_niveis = len(mapping_item_cols)
    header_list = list(range(numero_niveis))
    for index, row in mapping_item_df.iterrows():

        if type(mapping_item_cols) is list:
            columns       = row[mapping_item_cols].to_list()
            tuple_columns = tuple(columns)
            med_s = agg_vendas_df.get(tuple_columns, default = 0)
            if type(med_s) == int:
                med = med_s
            else:
                med = med_s.iloc[n]
        else:
            column = row[mapping_item_cols]
            med_s = agg_vendas_df.get(column, default = 0)
            if type(med_s) == int:
                med = med_s
            else:
                med = med_s.iloc[n]

        k = row[constant_col]
        import_df.loc[index, 'Medição'] = k*med

    return import_df

def filter_mapping_item_df(mapping_item_df, type_of_filtering):

    args = ['Categoria', 'Pilar', 'Grupo', 'Op', 'Op_execao']

    null_mapping_item_df = pd.DataFrame(columns = mapping_item_df.columns)

    has_x       = lambda column: mapping_item_df[column] == 'x'
    has_total   = lambda column: mapping_item_df[column].str.casefold() == 'total'
    has_clientes = lambda: mapping_item_df['Op'] == 'Quantidade Totalizada Clientes'
    has_clientes_ativos = lambda: mapping_item_df['Op'] == 'Quantidade Totalizada Clientes Ativos'

    if type_of_filtering.casefold() == 'grupo_cliente':
        mask = has_x(args[0]) & has_x(args[1]) & ~has_total(args[2]) & ~has_x(args[2]) & ~has_x(args[3]) & has_x(args[4]) & has_clientes()
        mapping_item_df = mapping_item_df[mask]
        return mapping_item_df
    
    elif type_of_filtering.casefold() == 'grupo_total':
        mask = has_x(args[0]) & has_x(args[1]) & has_total(args[2]) & ~has_x(args[2]) & ~has_x(args[3]) & has_x(args[4]) & has_clientes()
        mapping_item_df = mapping_item_df[mask]
        return mapping_item_df

    elif type_of_filtering.casefold() == 'total_cliente':
        mask = has_x(args[0]) & has_x(args[1]) & has_total(args[2]) & ~has_x(args[2]) & ~has_x(args[3]) & has_x(args[4]) & has_clientes_ativos()
        mapping_item_df = mapping_item_df[mask]
        return mapping_item_df

    elif type_of_filtering.casefold() == 'grupo':

        mask = has_x(args[0]) & ~has_x(args[1]) & ~has_x(args[2]) & ~has_x(args[3]) & has_x(args[4])
        mapping_item_df = mapping_item_df[mask]
        return mapping_item_df

    elif type_of_filtering.casefold() == 'pilar':

        mask = ~has_x(args[0]) & ~has_x(args[1]) & has_x(args[2]) & ~has_x(args[3]) & has_x(args[4])
        mapping_item_df = mapping_item_df[mask]
        return mapping_item_df

    elif type_of_filtering.casefold() == 'categoria':

        mask = ~has_total(args[0]) & ~has_x(args[0]) & has_x(args[1]) & has_x(args[2]) & ~has_x(args[3]) & has_x(args[4])
        mapping_item_df = mapping_item_df[mask]
        return mapping_item_df

    elif type_of_filtering.casefold() == 'total':

        mask = has_total(args[0]) & ~has_x(args[0]) & has_x(args[1]) & has_x(args[2]) & ~has_x(args[3]) & has_x(args[4])
        mapping_item_df = mapping_item_df[mask]
        return mapping_item_df

    elif type_of_filtering.casefold() == 'exception':

        mask = has_x(args[0]) & has_x(args[1]) & has_x(args[2]) & has_x(args[3]) & ~has_x(args[4])
        mapping_item_df = mapping_item_df[mask]
        return mapping_item_df

    return null_mapping_item_df

def med_grupo(import_df, agg_vendas_df, mapping_item_df, n):
    mapping_item_cols = ['Op', 'Pilar', 'Grupo']
    mapping_item_df = filter_mapping_item_df(mapping_item_df, 'grupo')
    import_df = med_n_levels(import_df, agg_vendas_df, 
                                mapping_item_df, mapping_item_cols, n)

    return import_df

def med_pilar(import_df, agg_vendas_df, mapping_item_df, n):
    mapping_item_cols = ['Op', 'Categoria', 'Pilar']
    mapping_item_df = filter_mapping_item_df(mapping_item_df, 'pilar')
    import_df = med_n_levels(import_df, agg_vendas_df, 
                                mapping_item_df, mapping_item_cols, n)

    return import_df

def med_categoria(import_df, agg_vendas_df, mapping_item_df, n):
    mapping_item_cols = ['Op', 'Categoria']
    mapping_item_df = filter_mapping_item_df(mapping_item_df, 'categoria')
    import_df = med_n_levels(import_df, agg_vendas_df, 
                                mapping_item_df, mapping_item_cols, n)

    return import_df
    
def med_total(import_df, agg_vendas_df, mapping_item_df, n):
    mapping_item_cols = 'Op'
    mapping_item_df = filter_mapping_item_df(mapping_item_df, 'total')
    import_df = med_n_levels(import_df, agg_vendas_df, 
                                mapping_item_df, mapping_item_cols, n)

    return import_df

def med_execao(import_df, agg_vendas_df, mapping_item_df, n):
    mapping_item_cols = 'Op_execao'
    mapping_item_df = filter_mapping_item_df(mapping_item_df, 'exception')
    import_df = med_n_levels(import_df, agg_vendas_df, 
                                mapping_item_df, mapping_item_cols, n)

    return import_df

def med_clientes_grupo(import_df, agg_clientes_df, mapping_item_df, n):
    mapping_item_cols = ['Op', 'Grupo']
    mapping_item_df = filter_mapping_item_df(mapping_item_df, 'grupo_cliente')
    import_df = med_n_levels(import_df, agg_clientes_df, mapping_item_df, mapping_item_cols, n)
    return import_df

def med_clientes_total(import_df, agg_clientes_df, mapping_item_df, n):
    mapping_item_cols = 'Op'
    mapping_item_df = filter_mapping_item_df(mapping_item_df, 'grupo_total')
    import_df = med_n_levels(import_df, agg_clientes_df, mapping_item_df, mapping_item_cols, n)
    return import_df

def med_clientes_total_ativos(import_df, agg_clientes_total_df, mapping_item_df, n):
    mapping_item_cols = 'Op'
    mapping_item_df = filter_mapping_item_df(mapping_item_df, 'total_cliente')
    import_df = med_n_levels(import_df, agg_clientes_total_df, mapping_item_df, mapping_item_cols, n)
    return import_df

def med(import_file, agg_vendas_file, agg_clientes_file, mapping_item_file, n):
    id_item_col = 'ID do Item'

    import_df = pd.read_excel(import_file, index_col = id_item_col)

    arithmetic_seq_list = lambda n : list(range(n))

    agg_vendas_grupo_df  = pd.read_excel(agg_vendas_file, header = arithmetic_seq_list(3), sheet_name = 'grupo') 
    agg_vendas_pil_df   = pd.read_excel(agg_vendas_file, header = arithmetic_seq_list(3), sheet_name = 'pilar') 
    agg_vendas_cat_df   = pd.read_excel(agg_vendas_file, header = arithmetic_seq_list(2), sheet_name = 'categoria') 
    agg_vendas_tot_df   = pd.read_excel(agg_vendas_file, header = arithmetic_seq_list(1), sheet_name = 'total') 
    agg_vendas_exec_df  = pd.read_excel(agg_vendas_file, header = arithmetic_seq_list(1), sheet_name = 'exception') 

    mapping_item_df = pd.read_excel(mapping_item_file, index_col = id_item_col) 

    import_df = med_grupo(import_df, agg_vendas_grupo_df, mapping_item_df, n)
    import_df = med_pilar(import_df, agg_vendas_pil_df, mapping_item_df, n)
    import_df = med_categoria(import_df, agg_vendas_cat_df, mapping_item_df, n)
    import_df = med_total(import_df, agg_vendas_tot_df, mapping_item_df, n)
    import_df = med_execao(import_df, agg_vendas_exec_df, mapping_item_df, n)
    
    agg_clientes_grupo_df = pd.read_excel(agg_clientes_file, header = arithmetic_seq_list(2), sheet_name = 'grupo_clientes')
    agg_clientes_total_df = pd.read_excel(agg_clientes_file, header = arithmetic_seq_list(1), sheet_name = 'grupo_total')
    agg_clientes_total_ativos_df = pd.read_excel(agg_clientes_file, header = arithmetic_seq_list(1), sheet_name = 'ativos_clientes')
    
    import_df = med_clientes_grupo(import_df, agg_clientes_grupo_df, mapping_item_df, n)
    import_df = med_clientes_total(import_df, agg_clientes_total_df, mapping_item_df, n)
    import_df = med_clientes_total_ativos(import_df, agg_clientes_total_ativos_df, mapping_item_df, n)

    import_df = import_df.dropna(subset = ('Mês', 'Ano'))
    import_df = import_df.replace([np.inf, -np.inf], 0)

    faixa_columns = ['Fx Verde Inf/Previsto', 'Fx Verde Sup',
       'Fx Vermelha Inf', 'Fx Vermelha Sup', 'Fx Cliente Inf',
       'Fx Cliente Sup']

    import_df[faixa_columns] = pd.NA
    return import_df

def get_med_import(import_paths, emps_filter, input_dir, end_date):
    for import_path in import_paths:
        emp = import_path.parents[3].name
        if emp not in emps_filter:
            continue
        print(emp)

        carga_dir = utils.get_carga_dir(input_dir, emp, end_date)
        mapping_item = carga_dir / 'mapping_item.xlsx'
        import_file = carga_dir / 'import.xlsx'
        output_dir = carga_dir / 'output'
        agg_vendas_file = output_dir / 'test_agg.xlsx'
        agg_clientes_file = output_dir / 'test_agg_clientes.xlsx'
        out_import_file = output_dir / 'out_import.xlsx'

        df = med(import_file, agg_vendas_file, agg_clientes_file, mapping_item, -1)
        df.to_excel(out_import_file)

def transform_med_import():
    cargas_dir = utils.get_cargas_dir(INPUT_DIR, END_DATE)
    import_paths = cargas_dir.rglob('import.xlsx')
    emps = utils.is_not_done_carga(INPUT_DIR, END_DATE, 'import_automatico')
    get_med_import(import_paths, emps, INPUT_DIR, END_DATE)