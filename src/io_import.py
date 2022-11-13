import pandas as pd
import numpy as np
from pathlib import Path

import io_excel

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

def med(import_file, agg_vendas_file, mapping_item_file, output_file):
    id_item_col = 'ID do Item'

    import_df = pd.read_excel(import_file, index_col = id_item_col)

    arithmetic_seq_list = lambda n : list(range(n))   

    agg_vendas_grup_df  = pd.read_excel(agg_vendas_file, header = arithmetic_seq_list(3), sheet_name = 'grupo') 
    agg_vendas_pil_df   = pd.read_excel(agg_vendas_file, header = arithmetic_seq_list(3), sheet_name = 'pilar') 
    agg_vendas_cat_df   = pd.read_excel(agg_vendas_file, header = arithmetic_seq_list(2), sheet_name = 'categoria') 
    agg_vendas_tot_df   = pd.read_excel(agg_vendas_file, header = arithmetic_seq_list(1), sheet_name = 'total') 
    agg_vendas_exec_df  = pd.read_excel(agg_vendas_file, header = arithmetic_seq_list(1), sheet_name = 'exception') 

    mapping_item_df = pd.read_excel(mapping_item_file, index_col = id_item_col) 

    #import_df['Medição'] = pd.NA
    import_df = med_grupo(import_df, agg_vendas_grup_df, mapping_item_df)
    import_df = med_pilar(import_df, agg_vendas_pil_df, mapping_item_df)
    import_df = med_categoria(import_df, agg_vendas_cat_df, mapping_item_df)
    import_df = med_total(import_df, agg_vendas_tot_df, mapping_item_df)
    import_df = med_execao(import_df, agg_vendas_exec_df, mapping_item_df)
    import_df = import_df.dropna(subset = ('Mês', 'Ano'))
    import_df = import_df.replace([np.inf, -np.inf], 0)

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

def files_import(root_dir, date):
    search_pattern = f'Carga/{date}/output/import.xlsx'
    return io_excel.search_files(root_dir, search_pattern)

def files_mapping_item(root_dir, date):
    search_pattern = f'Carga/{date}/new_mapping_item.xlsx'
    return io_excel.search_files(root_dir, search_pattern)

def triple_check(import_from_icg_file, agg_vendas_file, mapping_file, mapping_item_file):
    index_produto = 'Produto/serviço'
    mapping_df = pd.read_excel(mapping_file, index_col = index_produto)
    mapping_groupped = mapping_df.groupby(['Categoria', 'Pilar', 'Grupo'])
    group_mapping = mapping_groupped.size().reset_index(level = [0,1]).drop(0, axis = 1)
    x = group_mapping
    print(x)

    id_item_col = 'ID do Item'
    mapping_item_df = pd.read_excel(mapping_item_file, index_col = id_item_col)
    mapping_item_cat_df = filter_mapping_item_df(mapping_item_df, 'categoria')
    mapping_item_pil_df = filter_mapping_item_df(mapping_item_df, 'pilar')
    mapping_item_tot_df = filter_mapping_item_df(mapping_item_df, 'Total')
    mapping_item_df = pd.concat([mapping_item_cat_df, mapping_item_pil_df, mapping_item_tot_df])
    
    import_icg_df = pd.read_excel(import_from_icg_file)
    filtered_import_icg_df = import_icg_df[import_icg_df['Totalizado'] == 'Sim']
    filtered_import_icg_df = filtered_import_icg_df.rename(columns = {'Medição': 'Medição_ref'})
    
    pos_med_ref = filtered_import_icg_df.columns.get_loc('Medição_ref')
    filtered_import_icg_df.insert(pos_med_ref, 'Medição', pd.NA)
    filtered_import_icg_df.insert(pos_med_ref + 2, 'Erro_Med', pd.NA)

    med(filtered_import_icg_df, agg_vendas_file, mapping_item_)
    x = filtered_import_icg_df
    print(x)
    
    import_df = med_pilar(import_df, agg_vendas_pil_df, mapping_item_df)
    import_df = med_categoria(import_df, agg_vendas_cat_df, mapping_item_df)
    import_df = med_total(import_df, agg_vendas_tot_df, mapping_item_df)
    

def main():

    root_dir = Path('data/input/falta')
    date = '2022/10 - Outubro'

    imports = files_import(root_dir, date)
    mappings_item = files_mapping_item(root_dir, date)
    print(imports)

    # df_all = pd.read_excel('import_all_empresa.xlsx', index_col = 'ID do Item')
    # df_all['Empresa'] = pd.NA
    # df_all_med = pd.DataFrame()
    # for import_f in imports:

    #     mapping_file = import_f.parent.parent / 'new_mapping.xlsx'
    #     mapping_item = mapping_file.parent / 'mapping_item.xlsx'

    #     emp = mapping_file.parents[3].name
    #     print(emp)

    #     # df = pd.read_excel(mapping_item)
    #     # df['Empresa'] = emp
    #     # df = df.reindex(df.index.values.tolist() + ['null'])
    #     # df_all = pd.concat([df, df_all])


    #     template_mapping_item(import_f, mapping_file)

    # df_all.to_excel('1_mapping_item.xlsx')
    for mapping_item in mappings_item:
        emp = mapping_item.parents[3].name
        print(emp)
        
        input_dir = mapping_item.parent
        output_dir = input_dir / 'output'

        import_file     = output_dir / 'import.xlsx'
        agg_vendas_file = output_dir / 'test_agg.xlsx'
        out_import_file = output_dir / 'out_import.xlsx'

        # df = pd.read_excel(import_file, index_col = 'ID do Item')
        # df_med = df.dropna(subset = ['Medição']).copy()
        # df_med['Empresa'] = emp

        # index_join = [index for index in df_med.index if index in df_all.index]

        # df_all.loc[index_join, 'Empresa'] = emp
        # print(f'{emp}: {sorted(index_join)}')
        # df_all_med = pd.concat([df_all_med, df_all.loc[index_join, :]])

    # df_all_med.groupby('Empresa').size().to_excel('qnts_itens_med.xlsx')
    # df_all_med.to_excel('todas_medicoes_com_empresa.xlsx')
        med(import_file, agg_vendas_file, mapping_item, out_import_file)

if __name__ == '__main__':
    main()