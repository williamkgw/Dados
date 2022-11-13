import pandas as pd
import numpy as np
from pathlib import Path

import io_excel

def safe_get_group(groupby, keys):

    if any(item in keys for item in groupby.groups.keys()):
        return pd.concat([group for (name, group) in groupby if name in keys]) # get multiple or single items
    else:
        vendas_columns = groupby.get_group(list(groupby.groups.keys())[0]).columns
        return pd.DataFrame(columns = vendas_columns)

def test_mapping_vendas(mapping_vendas_df, path):
    testing_vendas_out_f = path / 'testing_mapping_vendas.xlsx'

    # removing empty rows
    missing_mapping_vendas_df = mapping_vendas_df[mapping_vendas_df.isna().all(axis=1)]
    mapping_vendas_df = mapping_vendas_df.dropna(how = 'all', axis = 0)

    # configuring the dataframes to catch case sensitive
    mapping_vendas_df.index = mapping_vendas_df.index.str.lower()
    
    # removing duplicated index
    mapping_vendas_duplicated_df = mapping_vendas_df[mapping_vendas_df.index.duplicated(keep = False)]
    mapping_vendas_df = mapping_vendas_df[~mapping_vendas_df.index.duplicated(keep='last')]

    with pd.ExcelWriter(testing_vendas_out_f) as writer:  
        mapping_vendas_duplicated_df.to_excel(writer, sheet_name = 'duplicated_index')
        missing_mapping_vendas_df.to_excel(writer, sheet_name = 'missing_mapping')

    return mapping_vendas_df

def test_vendas(vendas_df, mapping_vendas_df, path):
    
    # configuring
    vendas_df['Produto/serviço'] = vendas_df['Produto/serviço'].str.lower()

    # mapping
    vendas_df['__categoria'] = vendas_df['Produto/serviço'].map(mapping_vendas_df['Categoria'])
    vendas_df['__pilar'] = vendas_df['Produto/serviço'].map(mapping_vendas_df['Pilar'])
    vendas_df['__grupo'] = vendas_df['Produto/serviço'].map(mapping_vendas_df['Grupo'])

    # ano e mes
    vendas_df['__ano'] = vendas_df['Data e hora'].dt.year
    vendas_df['__mes'] = vendas_df['Data e hora'].dt.month

    # tickets
    def get_ticket(df):
        df['__ticket'] = 1/df['Venda'].count()

        return df

    vendas_df = vendas_df.groupby('Venda').apply(get_ticket)
    

    def get_ticket_pilar(df):

        def f(df):
            
            df['__ticket_por_pilar'] = 1/len(df)

            return df

        df = df.groupby('__pilar', dropna = False).apply(f)

        return df

    vendas_df = vendas_df.groupby('Venda').apply(get_ticket_pilar)
    
    # clientes ativos
    def get_clientes_ativos(df):
        df['__clientes_ativos'] = 1/len(df)

        return df

    vendas_df = vendas_df.groupby([pd.Grouper(key = 'Data e hora', freq = '1M'), 'Código'], dropna = False).apply(get_clientes_ativos)

    def get_cliente_pilar(df):

        def f(df):
            
            df['__clientes_ativo_por_pilar'] = 1/len(df)

            return df

        df = df.groupby('__pilar', dropna = False).apply(f)

        return df

    vendas_df = vendas_df.groupby([pd.Grouper(key = 'Data e hora', freq = '1M'), 'Código'], dropna = False).apply(get_cliente_pilar)
    
    # output diagnosis
    vendas_missing_df = vendas_df[vendas_df[['__pilar', '__grupo']].isna().any(axis = 1)]
    vendas_missing_df.to_excel(path / 'missing_vendas_csv.xlsx')
    vendas_df.to_excel(path / 'vendas_csv.xlsx')

    vendas_agrupado_grupo      = vendas_df.groupby([pd.Grouper(key = 'Data e hora', freq = '1M'), '__pilar' ,'__grupo'], dropna = False)
    vendas_agrupado_pilar      = vendas_df.groupby([pd.Grouper(key = 'Data e hora', freq = '1M'), '__categoria' ,'__pilar'], dropna = False)
    vendas_agrupado_categoria  = vendas_df.groupby([pd.Grouper(key = 'Data e hora', freq = '1M'), '__categoria'], dropna = False)
    vendas_agrupado_tempo      = vendas_df.groupby([pd.Grouper(key = 'Data e hora', freq = '1M')])

    def agg_configure(groupby, has_outter_cat, pilar_or_total = 'none'):

        agg = pd.DataFrame()
        agg['Faturamento Bruto']        = groupby.agg({'Bruto': 'sum'})
        agg['Quantidade Totalizada']    = groupby.agg({'Quantidade': 'sum'})
        agg['Preço Médio']              = agg['Faturamento Bruto']/agg['Quantidade Totalizada']

        def tickets_fat_medio(type_of_ticket, type_of_cliente):
            agg['Tickets Médio']        = groupby.agg({type_of_ticket: 'sum'})
            agg['Tickets Médio']        = agg['Faturamento Bruto']/agg['Tickets Médio']
            
            agg['Faturamento Médio por Clientes'] = groupby.agg({type_of_cliente: 'sum'})
            agg['Faturamento Médio por Clientes'] = agg['Faturamento Bruto']/agg['Faturamento Médio por Clientes']

        if pilar_or_total.lower() == 'pilar':
            tickets_fat_medio('__ticket_por_pilar', '__clientes_ativo_por_pilar')

        elif pilar_or_total.lower() == 'categoria':
            agg = agg.unstack(level = -1)

        elif pilar_or_total.lower() == 'total':
            tickets_fat_medio('__ticket', '__clientes_ativos')

        if has_outter_cat:
            agg = agg.unstack(level = -2).unstack(level = -1)
        agg = agg.dropna(axis=1, how='all')
        agg = agg.fillna(0)

        return agg

    agg_grupo_df     = agg_configure(vendas_agrupado_grupo, True)
    agg_pilar_df     = agg_configure(vendas_agrupado_pilar, True, 'pilar')
    agg_categoria_df = agg_configure(vendas_agrupado_categoria, False, 'categoria')
    agg_tempo_df     = agg_configure(vendas_agrupado_tempo, False, 'total') 

    # exception
    exception_df = vendas_agrupado_grupo['Quantidade'].apply('sum')
    exception_df = exception_df.unstack(level = -2).unstack(level = -1)
    exception_df = exception_df.dropna(axis = 1, how = 'all')

    exception_pilar = set(exception_df.columns.get_level_values(0))
    exception_grupo = set(exception_df.columns.get_level_values(1))

    def sel_exception_series(key, is_grupo):

        if is_grupo:
            if key in exception_grupo:
                exception_df[f'__{key}'] = exception_df.xs(key, level = 1, axis = 1)
            else:
                exception_df[f'__{key}'] = 0
        else:
            if key in exception_pilar:
                exception_df[f'__{key}'] = exception_df.xs(key, level = 0, axis = 1).sum(axis = 1)
            else:
                exception_df[f'__{key}'] = 0
        
        return exception_df[f'__{key}']

    cirurgia_s    = sel_exception_series('Cirurgia', True)
    consultas_s   = sel_exception_series('Consulta', True)
    exames_s      = sel_exception_series('Exames', False)
    internacao_s  = sel_exception_series('Internação', False)

    agg_exception_df = pd.DataFrame()
    agg_exception_df['Consultas/Cirurgias']     = consultas_s/cirurgia_s
    agg_exception_df['Consultas/Internação']    = consultas_s/internacao_s
    agg_exception_df['Exames/Consultas']        = exames_s/consultas_s

    agg_file = path / 'test_agg.xlsx'
    with pd.ExcelWriter(agg_file) as writer:

        agg_grupo_df.last('6M').to_excel(writer, sheet_name = 'grupo')
        agg_pilar_df.last('6M').to_excel(writer, sheet_name = 'pilar')
        agg_categoria_df.last('6M').to_excel(writer, sheet_name = 'categoria')
        agg_tempo_df.last('6M').to_excel(writer, sheet_name = 'total')
        agg_exception_df.last('6M').to_excel(writer, sheet_name = 'exception')
        mapping_vendas_df.groupby(['Pilar', 'Grupo'], dropna = False).size().to_excel(writer, sheet_name = 'unique_mapping')

    return vendas_agrupado_pilar, vendas_agrupado_grupo

def agg_vendas_clientes(vendas_df):
    
    max_date = max(vendas_df['Data e hora'])
    end_date = pd.Period.to_timestamp(max_date.to_period(freq = 'M'))
    min_date = min(vendas_df['Data e hora'])
    start_date = pd.Period.to_timestamp(min_date.to_period(freq = 'M'))

    agg_v_clientes = pd.DataFrame()
    endDate = end_date
    while True:
        startDate = endDate - pd.DateOffset(months = 6)
        
        if startDate <=  start_date:
            while True:
                startDate = start_date
                if endDate <= startDate:
                    break
                mask = (vendas_df['Data e hora'] >= startDate) & (vendas_df['Data e hora'] <= endDate)
                df = vendas_df[mask]
                n_clientes_6_meses = df['Cliente'].nunique()

                agg_new = pd.DataFrame(index = [endDate])
                agg_new['Clientes Ativos 6 Meses'] = n_clientes_6_meses
                agg_v_clientes = pd.concat([agg_new, agg_v_clientes])
                
                endDate -= pd.DateOffset(months = 1)
            break
        
        mask = (vendas_df['Data e hora'] >= startDate) & (vendas_df['Data e hora'] <= endDate)
        df = vendas_df[mask]
        n_clientes_6_meses = df['Cliente'].nunique()

        agg_new = pd.DataFrame(index = [endDate])
        agg_new['Clientes Ativos 6 Meses'] = n_clientes_6_meses
        agg_v_clientes = pd.concat([agg_new, agg_v_clientes])

        endDate -= pd.DateOffset(months = 1)

    return agg_v_clientes

def test_clientes(vendas_df, clientes_df, path):
    
    clientes_df['Inclusão'] = pd.to_datetime(clientes_df['Inclusão'], dayfirst = True, errors = 'coerce')
    clientes_agrupado = clientes_df.groupby(pd.Grouper(key = 'Inclusão', freq = '1M'))
    agg_clientes = pd.DataFrame()
    agg_clientes = clientes_agrupado['Origem'].value_counts(dropna = False)
    agg_clientes = agg_clientes.unstack(level = 1)

    agg_v_clientes = agg_vendas_clientes(vendas_df)

    agg_file = path / 'test_agg_clientes.xlsx'
    with pd.ExcelWriter(agg_file) as writer:
        agg_clientes.to_excel(writer, sheet_name = 'grupo_clientes')
        agg_v_clientes.to_excel(writer, sheet_name = 'ativos_clientes')
     
def get_analysis(mapping_f, vendas_f, clientes_f, path):

    path.mkdir(parents = True, exist_ok = True)

    mapping_vendas_df = pd.read_excel(mapping_f, sheet_name = 'mapping_vendas', index_col = 'Produto/serviço',
    dtype={'Produto/serviço': str, 'Categoria': str, 'Grupo': str, 'Pilar': str}
    )

    vendas_df = pd.read_csv(vendas_f, thousands = '.', decimal = ',', 
    encoding = 'latin1', sep = ';', parse_dates = ['Data e hora'], dayfirst=True)

    clientes_df = pd.read_csv(clientes_f, dayfirst = True, parse_dates = ['Inclusão'],
    thousands = '.', decimal = ',', encoding = 'latin1', sep = ';')

    vendas_df['Produto/serviço'] = vendas_df['Produto/serviço'].str.lower()

    mapping_vendas_df = test_mapping_vendas(mapping_vendas_df, path)
    test_vendas(vendas_df, mapping_vendas_df, path)
    test_clientes(vendas_df, clientes_df, path)

def loop():

    root_dir = Path('data/input/falta')
    date = '2022/10 - Outubro'
    search_pattern = f'Carga/{date}/Vendas.csv'
    vendas = io_excel.search_files(root_dir, search_pattern)

    for venda in vendas:
        
        emp = venda.parents[3].name
        print(emp)

        dir = venda.parent
        output_dir = dir / 'output'

        mapping     = dir / 'mapping.xlsx'
        new_mapping = dir / 'new_mapping.xlsx'
        clientes    = dir / 'Clientes.csv'

        get_analysis(new_mapping, venda, clientes, output_dir)

def main():

    loop()

    # root_dir = Path('data/input/22_dados')

    # paths = list(root_dir.rglob('10 - Outubro/output/missing_vendas_csv.xlsx'))

    # df_all = pd.DataFrame()
    # for path in paths:
    #     df = pd.read_excel(path)

    #     emp = path.parents[4].name
    #     print(emp)

    #     df['__emp'] = emp

    #     df_all = pd.concat([df_all, df])

    # df_all.to_excel('missing_all_15.xlsx')

if __name__ == '__main__':
    main()