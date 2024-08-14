import pandas as pd
import numpy as np

from src.extraction.mapping.mapping_export import init_mapping_export_template
from src.extraction.export_template import init_export_template

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
    has_inadimplencia = lambda: mapping_item_df['Op_execao'] == 'Inadimplencia do Faturamento Bruto'

    if type_of_filtering.casefold() == 'grupo_cliente':
        mask = has_x(args[0]) & has_x(args[1]) & ~has_total(args[2]) & ~has_x(args[2]) & ~has_x(args[3]) & has_x(args[4]) & has_clientes() & ~has_clientes_ativos()
        mapping_item_df = mapping_item_df[mask]
        return mapping_item_df
    
    elif type_of_filtering.casefold() == 'grupo_total':
        mask = has_x(args[0]) & has_x(args[1]) & has_total(args[2]) & ~has_x(args[2]) & ~has_x(args[3]) & has_x(args[4]) & has_clientes() & ~has_clientes_ativos()
        mapping_item_df = mapping_item_df[mask]
        return mapping_item_df

    elif type_of_filtering.casefold() == 'total_cliente':
        mask = has_x(args[0]) & has_x(args[1]) & has_total(args[2]) & ~has_x(args[2]) & ~has_x(args[3]) & has_x(args[4]) & ~has_clientes() & has_clientes_ativos()
        mapping_item_df = mapping_item_df[mask]
        return mapping_item_df

    elif type_of_filtering.casefold() == 'grupo':

        mask = has_x(args[0]) & ~has_x(args[1]) & ~has_x(args[2]) & ~has_x(args[3]) & has_x(args[4]) & ~has_clientes() & ~has_clientes_ativos()
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

        mask = has_x(args[0]) & has_x(args[1]) & has_x(args[2]) & has_x(args[3]) & ~has_x(args[4]) & ~has_inadimplencia()
        mapping_item_df = mapping_item_df[mask]
        return mapping_item_df
    
    elif type_of_filtering.casefold() == 'inadimplencia':

        mask = has_x(args[0]) & has_x(args[1]) & has_x(args[2]) & has_x(args[3]) & ~has_x(args[4]) & has_inadimplencia()
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

def med_inadimplencia_df(import_df, agg_inadimplencia_df, mapping_item_df, n):
    mapping_item_cols = 'Op_execao'
    mapping_item_df = filter_mapping_item_df(mapping_item_df, 'inadimplencia')
    import_df = med_n_levels(import_df, agg_inadimplencia_df, 
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

def update_import_date(import_df, date):
    import_df.loc[:, 'Mês'] = date.month
    import_df.loc[:, 'Ano'] = date.year
    return import_df

def reset_import_medicao(import_df):
    cols_to_reset = ('Medição' ,'Fx Verde Inf/Previsto' ,'Fx Verde Sup' ,'Fx Vermelha Inf' ,
                        'Fx Vermelha Sup' ,'Fx Cliente Inf' ,'Fx Cliente Sup')
    import_df.loc[:, cols_to_reset] = pd.NA
    return import_df

def load_clean_import_df(import_file, date):
    import_df = init_export_template(import_file)
    import_df = update_import_date(import_df, date)
    import_df = reset_import_medicao(import_df)
    return import_df

def med(import_file, agg_vendas_file, agg_clientes_file, mapping_item_file, date, n):
    import_df = load_clean_import_df(import_file, date)

    arithmetic_seq_list = lambda n : list(range(n))

    agg_vendas_grupo_df  = pd.read_excel(agg_vendas_file, header = arithmetic_seq_list(3), sheet_name = 'grupo')
    agg_vendas_pil_df   = pd.read_excel(agg_vendas_file, header = arithmetic_seq_list(3), sheet_name = 'pilar')
    agg_vendas_cat_df   = pd.read_excel(agg_vendas_file, header = arithmetic_seq_list(2), sheet_name = 'categoria')
    agg_vendas_tot_df   = pd.read_excel(agg_vendas_file, header = arithmetic_seq_list(1), sheet_name = 'total')
    agg_inadimplencia_df = pd.read_excel(agg_vendas_file, header = arithmetic_seq_list(1), sheet_name = 'inadimplencia')
    agg_vendas_exec_df  = pd.read_excel(agg_vendas_file, header = arithmetic_seq_list(1), sheet_name = 'exception')

    mapping_item_df = init_mapping_export_template(mapping_item_file)

    import_df = med_grupo(import_df, agg_vendas_grupo_df, mapping_item_df, n)
    import_df = med_pilar(import_df, agg_vendas_pil_df, mapping_item_df, n)
    import_df = med_categoria(import_df, agg_vendas_cat_df, mapping_item_df, n)
    import_df = med_total(import_df, agg_vendas_tot_df, mapping_item_df, n)
    import_df = med_inadimplencia_df(import_df, agg_inadimplencia_df, mapping_item_df, n)
    import_df = med_execao(import_df, agg_vendas_exec_df, mapping_item_df, n)

    agg_clientes_grupo_df = pd.read_excel(agg_clientes_file, header = arithmetic_seq_list(2), sheet_name = 'grupo_clientes')
    agg_clientes_total_df = pd.read_excel(agg_clientes_file, header = arithmetic_seq_list(1), sheet_name = 'grupo_total')
    agg_clientes_total_ativos_df = pd.read_excel(agg_clientes_file, header = arithmetic_seq_list(1), sheet_name = 'ativos_clientes')

    import_df = med_clientes_grupo(import_df, agg_clientes_grupo_df, mapping_item_df, n)
    import_df = med_clientes_total(import_df, agg_clientes_total_df, mapping_item_df, n)
    import_df = med_clientes_total_ativos(import_df, agg_clientes_total_ativos_df, mapping_item_df, n)

    import_df = import_df.dropna(subset = ('Mês', 'Ano'))
    import_df = import_df.replace([np.inf, -np.inf], 0)

    return import_df
