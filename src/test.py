import pandas as pd

vendas_f = 'data/input/Bicho Vip/Vendas.csv'
mapping_f = 'data/input/Bicho Vip/Mapping.xlsx'

vendas_df = pd.read_csv(vendas_f, usecols=['Data e hora', 'Venda', 'Produto/serviço', 'Grupo', 'Bruto', 'Quantidade'] ,
thousands = '.', decimal = ',', encoding = 'latin1', sep = ';',
parse_dates = ['Data e hora'], dayfirst=True)

mapping_vendas_df = pd.read_excel(mapping_f, sheet_name = 'mapping_vendas', 
index_col = 'Produto/serviço', dtype={'Produto/serviço': str, 'Categoria': str, 'Grupo': str, 'Pilar': str})

vendas_df['__grupo'] = vendas_df['Produto/serviço'].map(mapping_vendas_df['Grupo'])
vendas_df['__pilar'] = vendas_df['Produto/serviço'].map(mapping_vendas_df['Pilar'])
#vendas_df['__categoria'] = vendas_df['Produto/serviço'].map(mapping_vendas_df['Categoria'])

vendas_agrupado = vendas_df.groupby([pd.Grouper(key = 'Data e hora', freq = '1M'), '__pilar' ,'__grupo'])



def agg_configure(groupby):

    agg = pd.DataFrame()
    agg['Faturamento Bruto'] = groupby.agg({'Bruto': 'sum'})
    agg['Quantidade Totalizada'] = groupby.agg({'Quantidade': 'sum'})
    agg['Preço Médio'] = agg['Faturamento Bruto']/agg['Quantidade Totalizada']

    agg = agg.unstack(level = -2).unstack(level = -1)
    agg = agg.dropna(axis=1, how='all')
    agg = agg.fillna(0)

    return agg

agg_vendas = agg_configure(vendas_agrupado)

agg_vendas.to_excel('ahhaah.xlsx')
