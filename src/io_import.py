import pandas as pd
import numpy as np
import logging

import carga_control

def med_n_levels(import_df, agg_vendas_df, mapping_item_df, mapping_item_cols):
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
                med = med_s.iloc[-1]
        else:
            column = row[mapping_item_cols]
            med_s = agg_vendas_df.get(column, default = 0)
            if type(med_s) == int:
                med = med_s
            else:
                med = med_s.iloc[-1]

        k = row[constant_col]
        import_df.loc[index, 'Medição'] = k*med

    return import_df

def filter_mapping_item_df(mapping_item_df, type_of_filtering):

    args = ['Categoria', 'Pilar', 'Grupo', 'Op', 'Op_execao']
    x_value = 'x'

    null_mapping_item_df = pd.DataFrame(columns = mapping_item_df.columns)

    has_x       = lambda column: mapping_item_df[column] == x_value
    has_total   = lambda column: mapping_item_df[column].str.casefold() == 'total'

    if type_of_filtering.casefold() == 'grupo':

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

def med_grupo(import_df, agg_vendas_df, mapping_item_df):
    mapping_item_cols = ['Op', 'Pilar', 'Grupo']
    mapping_item_df = filter_mapping_item_df(mapping_item_df, 'grupo')
    import_df = med_n_levels(import_df, agg_vendas_df, 
                                mapping_item_df, mapping_item_cols)

    return import_df

def med_pilar(import_df, agg_vendas_df, mapping_item_df):
    mapping_item_cols = ['Op', 'Categoria', 'Pilar']

    mapping_item_df = filter_mapping_item_df(mapping_item_df, 'pilar')

    import_df = med_n_levels(import_df, agg_vendas_df, 
                                mapping_item_df, mapping_item_cols)

    return import_df

def med_categoria(import_df, agg_vendas_df, mapping_item_df):
    mapping_item_cols = ['Op', 'Categoria']

    mapping_item_df = filter_mapping_item_df(mapping_item_df, 'categoria')

    import_df = med_n_levels(import_df, agg_vendas_df, 
                                mapping_item_df, mapping_item_cols)

    return import_df
    
def med_total(import_df, agg_vendas_df, mapping_item_df):
    mapping_item_cols = 'Op'

    mapping_item_df = filter_mapping_item_df(mapping_item_df, 'total')

    import_df = med_n_levels(import_df, agg_vendas_df, 
                                mapping_item_df, mapping_item_cols)

    return import_df

def med_execao(import_df, agg_vendas_df, mapping_item_df):
    mapping_item_cols = 'Op_execao'

    mapping_item_df = filter_mapping_item_df(mapping_item_df, 'exception')

    import_df = med_n_levels(import_df, agg_vendas_df, 
                                mapping_item_df, mapping_item_cols)

    return import_df

def med(import_file, agg_vendas_file, mapping_item_file):
    id_item_col = 'ID do Item'

    import_df = pd.read_excel(import_file, index_col = id_item_col)

    arithmetic_seq_list = lambda n : list(range(n))   

    agg_vendas_grup_df  = pd.read_excel(agg_vendas_file, header = arithmetic_seq_list(3), sheet_name = 'grupo') 
    agg_vendas_pil_df   = pd.read_excel(agg_vendas_file, header = arithmetic_seq_list(3), sheet_name = 'pilar') 
    agg_vendas_cat_df   = pd.read_excel(agg_vendas_file, header = arithmetic_seq_list(2), sheet_name = 'categoria') 
    agg_vendas_tot_df   = pd.read_excel(agg_vendas_file, header = arithmetic_seq_list(1), sheet_name = 'total') 
    agg_vendas_exec_df  = pd.read_excel(agg_vendas_file, header = arithmetic_seq_list(1), sheet_name = 'exception') 

    mapping_item_df = pd.read_excel(mapping_item_file, index_col = id_item_col) 

    import_df = med_grupo(import_df, agg_vendas_grup_df, mapping_item_df)
    import_df = med_pilar(import_df, agg_vendas_pil_df, mapping_item_df)
    import_df = med_categoria(import_df, agg_vendas_cat_df, mapping_item_df)
    import_df = med_total(import_df, agg_vendas_tot_df, mapping_item_df)
    import_df = med_execao(import_df, agg_vendas_exec_df, mapping_item_df)
    import_df = import_df.dropna(subset = ('Mês', 'Ano'))
    import_df = import_df.replace([np.inf, -np.inf], 0)

    faixa_columns = ['Fx Verde Inf/Previsto', 'Fx Verde Sup',
       'Fx Vermelha Inf', 'Fx Vermelha Sup', 'Fx Cliente Inf',
       'Fx Cliente Sup']

    import_df[faixa_columns] = pd.NA
    return import_df
    import_df.to_excel(output_file)

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
        
        carga_dir = carga_control.get_carga_dir(input_dir, emp, end_date)
        mapping = carga_dir / 'mapping.xlsx'
        template_mapping_item_f = carga_dir / 'mapping_item.xlsx'

        template_mapping_item_df = template_mapping_item(import_path, mapping)
        template_mapping_item_df.to_excel(template_mapping_item_f)

def get_med_import(import_paths, emps_filter, input_dir, end_date):
    for import_path in import_paths:
        emp = import_path.parents[3].name
        if emp not in emps_filter:
            continue
        print(emp)

        carga_dir = carga_control.get_carga_dir(input_dir, emp, end_date)
        mapping_item = carga_dir / 'mapping_item.xlsx'
        import_file = carga_dir / 'import.xlsx'
        output_dir = carga_dir / 'output'
        agg_vendas_file = output_dir / 'test_agg.xlsx'
        out_import_file = output_dir / 'out_import.xlsx'

        df = med(import_file, agg_vendas_file, mapping_item)
        df.to_excel(out_import_file)

def triple_check(out_imports, emps_filter, input_dir, end_date):
    cargas_dir = carga_control.get_cargas_dir(input_dir, end_date)
    icg_import_f = cargas_dir / 'icg_export.xlsx'
    icg_import_cols = ('ID do Item', 'Mês', 'Ano',
                       'Medição', 'Item', 'Totalizado'
                        )
    icg_import_df = pd.read_excel(icg_import_f, index_col = 'ID do Item', usecols = icg_import_cols)

    df_all = pd.DataFrame()
    for out_import in out_imports:
        emp = out_import.parents[4].name
        if emp not in emps_filter:
            continue
        print(emp)

        out_import_df = pd.read_excel(out_import, index_col = 'ID do Item', usecols = icg_import_cols)

        set_id_out_import = set(out_import_df.index)
        set_id_icg_import = set(icg_import_df.index)
        common_id_import = list(set_id_icg_import & set_id_out_import)

        df = icg_import_df.loc[common_id_import, :]
        df['Empresa'] = emp
        df['Delta out_import'] = out_import_df.loc[common_id_import, 'Medição']
        df['Delta out_import'] = df['Delta out_import'] - df['Medição']
        df['Delta out_import'] = df['Delta out_import'].round(2)

        df_all = pd.concat([df_all, df])

    out_import_comp = cargas_dir / 'comp_icg_out_import.xlsx'
    df_all.to_excel(out_import_comp)

def main():
    import sys

    END_DATE = carga_control.END_DATE
    INPUT_DIR = carga_control.INPUT_DIR
    cargas_dir = carga_control.get_cargas_dir(INPUT_DIR, END_DATE)
    logging.basicConfig(filename = cargas_dir / 'log.log', filemode = 'w', encoding = 'utf-8')

    assert len(sys.argv) == 2
    type_of_execution = sys.argv[1]

    if type_of_execution == 'mapping_item':
        import_paths = cargas_dir.rglob('import.xlsx')
        emps = carga_control.is_not_done_carga(INPUT_DIR, END_DATE, 'mapping_item')
        get_mapping_item(import_paths, emps, INPUT_DIR, END_DATE)

    elif type_of_execution == 'import_automatico':
        import_paths = cargas_dir.rglob('import.xlsx')
        emps = carga_control.is_not_done_carga(INPUT_DIR, END_DATE, 'import_automatico')
        get_med_import(import_paths, emps, INPUT_DIR, END_DATE)

    elif type_of_execution == 'triple_check':
        out_imports = cargas_dir.rglob('out_import.xlsx')
        emps = carga_control.is_not_done_carga(INPUT_DIR, END_DATE, 'triple_check')
        triple_check(out_imports, emps, INPUT_DIR, END_DATE)

if __name__ == '__main__':
    main()