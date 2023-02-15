import pandas as pd
import numpy as np
from pathlib import Path

import datetime
import locale

import io_excel
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

def files_in_carga(cargas_dir, date, file_name):
    locale.setlocale(locale.LC_ALL, 'pt_pt.UTF-8')

    year_month_s = date.strftime('%Y/%m - %B').title()

    search_pattern = f'{year_month_s}/{file_name}'

    return io_excel.search_files(cargas_dir, search_pattern)

def triple_check(cargas_dir, date):

    get_totalizado = lambda import_df: import_df#[import_df['Totalizado'] == 'Sim']

    icg_import_f = cargas_dir / 'icg_export.xlsx'
    icg_import_df = pd.read_excel(
                                 icg_import_f, index_col = 'ID do Item',
                                 usecols = (
                                            'ID do Item', 'Mês', 'Ano',
                                            'Medição', 'Item', 
                                            'Totalizado'
                                            )
                                 )

    icg_import_totalizado_df = get_totalizado(icg_import_df)
    out_imports = files_in_carga(cargas_dir, date, 'output/out_import.xlsx')
    
    df_all = pd.DataFrame()
    for out_import in out_imports:
        emp = out_import.parents[4].name
        print(emp)

        out_import_df = pd.read_excel(out_import, index_col = 'ID do Item')
        out_import_totalizado_df = get_totalizado(out_import_df)

        df = pd.DataFrame()
        try:
            df = icg_import_totalizado_df.loc[out_import_totalizado_df.index]
            df['Delta out_import'] = out_import_totalizado_df['Medição']
        except:
            excess_id_item = (
                             set(out_import_totalizado_df.index) 
                             - set(icg_import_totalizado_df.index)
                             )
            common_id_itens = list(
                              set(out_import_totalizado_df.index) 
                              & set(icg_import_totalizado_df.index)
                              )
            df = icg_import_totalizado_df.loc[common_id_itens]
            df['Delta out_import'] = out_import_totalizado_df.loc[common_id_itens, 'Medição']
        
        df['Empresa'] = emp
        df['Delta out_import'] = df['Delta out_import'] - df['Medição']
        df['Delta out_import'] = df['Delta out_import'].round(2)
        df_all = pd.concat([df_all, df])

    out_import_comp = cargas_dir / 'comp_icg_out_import.xlsx'
    df_all.to_excel(out_import_comp)

def loop2():
    end_date = datetime.date(day = 31, month = 1, year = 2023)
    input_dir = Path('data/input')

    cargas_dir = carga_control.get_cargas_dir(input_dir, end_date)
    emps = carga_control.not_done(input_dir, end_date, 'mapping')

    imports = files_in_carga(cargas_dir, end_date, 'import.xlsx')

    imports = [_import for _import in imports if _import.parents[3].name in emps]

    for _import in imports:
        emp = _import.parents[3].name
        print(emp)
        
        carga_dir = _import.parent
        mapping = carga_dir / 'mapping.xlsx'
        template_mapping_item_f = carga_dir / 'mapping_item.xlsx'

        template_mapping_item_df = template_mapping_item(_import, mapping)
        template_mapping_item_df.to_excel(template_mapping_item_f)

def loop():
    end_date = datetime.date(day = 31, month = 1, year = 2023)

    input_dir = Path(f'data/input')

    cargas_dir = carga_control.get_cargas_dir(input_dir, end_date)

    imports = files_in_carga(cargas_dir, end_date, 'import.xlsx')
    emps_filter = carga_control.not_done(input_dir, end_date, 'import_automatico')

    for import_f in imports:

        emp = import_f.parents[3].name

        if emp not in emps_filter:
            continue
        
        print(emp)

        carga_dir = import_f.parent

        mapping_item = carga_dir / 'mapping_item.xlsx'
        import_file     = carga_dir / 'import.xlsx'
        
        output_dir = carga_dir / 'output'
        agg_vendas_file = output_dir / 'test_agg.xlsx'
        out_import_file = output_dir / 'out_import.xlsx'

        # med(import_file, agg_vendas_file, mapping_item, out_import_file)

    triple_check(cargas_dir, end_date)

def main():
    loop()

if __name__ == '__main__':
    main()