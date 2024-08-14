import numpy as np
import pandas as pd

from src.extraction.mapping.mapping_sales import init_mapping_vendas
from src.transform.mapping.mapping_sales import test_mapping_vendas
from src.load.mapping.mapping_sales import test_mapping_vendas_to_excel
from src.extraction.sales import init_vendas
from src.load.sales import test_vendas_to_excel

def get_clientes_ativos(df):
    df['__clientes_ativos'] = 1/len(df)
    return df

def get_cliente_pilar(df):
    def percentage_of_the_row_against_df(df):
        df['__clientes_ativo_por_pilar'] = 1/len(df)
        return df
    return df.groupby('__pilar', dropna = False).apply(percentage_of_the_row_against_df)

def get_ticket(df):
    df['__ticket'] = 1/df['Venda'].count()
    return df

def get_ticket_pilar(df):
    def percentage_of_the_row_against_df(df):
        df['__ticket_por_pilar'] = 1/len(df)
        return df
    return df.groupby('__pilar', dropna = False).apply(percentage_of_the_row_against_df)

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

def sel_exception_series(exception_df, key, is_grupo):
    exception_pilar = set(exception_df.columns.get_level_values(0))
    exception_grupo = set(exception_df.columns.get_level_values(1))

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

def agg_configure_exception(vendas_agrupado_grupo):
    exception_df = vendas_agrupado_grupo['Quantidade'].apply('sum')
    exception_df = exception_df.unstack(level = -2).unstack(level = -1)
    exception_df = exception_df.dropna(axis = 1, how = 'all')

    cirurgia_s    = sel_exception_series(exception_df, 'Cirurgia', True)
    consultas_s   = sel_exception_series(exception_df, 'Consulta', True)
    exames_s      = sel_exception_series(exception_df, 'Exames', False)
    internacao_s  = sel_exception_series(exception_df, 'Diária', True)

    agg_exception_df = pd.DataFrame()
    agg_exception_df['Consultas/Cirurgias']     = consultas_s/cirurgia_s
    agg_exception_df['Consultas/Internação']    = consultas_s/internacao_s
    agg_exception_df['Exames/Consultas']        = exames_s/consultas_s
    agg_exception_df = agg_exception_df.replace([np.inf, -np.inf, np.nan], 0)

    return agg_exception_df

def test_inadimplente(vendas_df, end_date):
    end_date_time_mask = end_date - pd.offsets.MonthBegin()
    begin_date_time_mask = end_date - pd.offsets.DateOffset(months = 11) - 2*pd.offsets.MonthBegin()

    time_mask = (vendas_df['Data e hora'] > begin_date_time_mask) & (vendas_df['Data e hora'] < end_date_time_mask)
    baixa_mask = vendas_df['Status da venda'] != 'Baixado'
    mask = time_mask & baixa_mask

    inadimpl_df = vendas_df[mask].groupby(pd.Grouper(key = 'Data e hora', freq = 'M'))['Bruto'].agg('sum').rolling(window = 12).sum()
    return inadimpl_df.rename('Inadimplencia do Faturamento Bruto')

def test_vendas(vendas_df, mapping_vendas_df):
    # configuring
    vendas_df['Produto/serviço'] = vendas_df['Produto/serviço'].str.lower()

    # mapping
    vendas_df['__categoria'] = vendas_df['Produto/serviço'].map(mapping_vendas_df['Categoria'])
    vendas_df['__pilar'] = vendas_df['Produto/serviço'].map(mapping_vendas_df['Pilar'])
    vendas_df['__grupo'] = vendas_df['Produto/serviço'].map(mapping_vendas_df['Grupo'])
    vendas_df[['__categoria', '__pilar', '__grupo']] = vendas_df[['__categoria', '__pilar', '__grupo']].fillna('NULL')

    # ano e mes
    vendas_df['__ano'] = vendas_df['Data e hora'].dt.year
    vendas_df['__mes'] = vendas_df['Data e hora'].dt.month

    # tickets
    vendas_df = vendas_df.groupby('Venda').apply(get_ticket)
    vendas_df = vendas_df.groupby('Venda').apply(get_ticket_pilar)

    # clientes ativos
    vendas_df = vendas_df.groupby([pd.Grouper(key = 'Data e hora', freq = '1M'), 'Código'], dropna = False).apply(get_clientes_ativos)
    vendas_df = vendas_df.groupby([pd.Grouper(key = 'Data e hora', freq = '1M'), 'Código'], dropna = False).apply(get_cliente_pilar)

    # output diagnosis
    vendas_missing_df = vendas_df[vendas_df[['__pilar', '__grupo']].isna().any(axis = 1)]

    vendas_agrupado_grupo      = vendas_df.groupby([pd.Grouper(key = 'Data e hora', freq = '1M'), '__pilar' ,'__grupo'], dropna = False)
    vendas_agrupado_pilar      = vendas_df.groupby([pd.Grouper(key = 'Data e hora', freq = '1M'), '__categoria' ,'__pilar'], dropna = False)
    vendas_agrupado_categoria  = vendas_df.groupby([pd.Grouper(key = 'Data e hora', freq = '1M'), '__categoria'], dropna = False)
    mask_null_cat_pil = vendas_df.loc[:, ('__categoria', '__pilar')].agg(tuple, axis = 1) == ('NULL', 'NULL')
    vendas_agrupado_tempo      = (  vendas_df[~mask_null_cat_pil]
                                    .copy()
                                    .groupby([pd.Grouper(key = 'Data e hora', freq = '1M')])
                                )

    agg_grupo_df     = agg_configure(vendas_agrupado_grupo, True)
    agg_pilar_df     = agg_configure(vendas_agrupado_pilar, True, 'pilar')
    agg_categoria_df = agg_configure(vendas_agrupado_categoria, False, 'categoria')
    agg_tempo_df     = agg_configure(vendas_agrupado_tempo, False, 'total') 
    agg_exception_df = agg_configure_exception(vendas_agrupado_grupo)

    agg_grupo_df = agg_grupo_df.last('6M')
    agg_pilar_df = agg_pilar_df.last('6M')
    agg_categoria_df = agg_categoria_df.last('6M')
    agg_tempo_df = agg_tempo_df.last('6M')
    agg_exception_df = agg_exception_df.last('6M')
    unique_mapping_df = mapping_vendas_df.groupby(['Categoria', 'Pilar', 'Grupo']).size()
    return [agg_grupo_df, agg_pilar_df, agg_categoria_df, agg_tempo_df,
             agg_exception_df, unique_mapping_df, vendas_missing_df, vendas_df]

def sales_data_analysis(config_carga_company, end_date):
    new_mapping_vendas_df = init_mapping_vendas(config_carga_company.new_mapping_sales)
    new_mapping_vendas_df, *info_mapping_vendas = test_mapping_vendas(new_mapping_vendas_df, config_carga_company.output.mapping_sales_mapped)
    test_mapping_vendas_to_excel(*info_mapping_vendas)
    
    vendas_df = init_vendas(config_carga_company.sales)
    result_vendas = test_vendas(vendas_df, new_mapping_vendas_df)
    inadimplencia = test_inadimplente(vendas_df, end_date)
    test_vendas_to_excel(config_carga_company.output, *result_vendas, inadimplencia)