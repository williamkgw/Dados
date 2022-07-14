import pandas as pd
import numpy as np

def dataframe_associative_vector(df, column , associative_vector):

    df_copy = df.copy()
    df_copy[column] = df_copy[column].map(associative_vector)
    return df_copy

def series_grupo(reagrupa_df):
    column = 'GRUPO'

    s = reagrupa_df[column].reset_index(drop = True)
    s = s.drop_duplicates() # Exclui apenas valores da serie e não o INDEX.
    s = s.reset_index(drop = True)

    return s

def calc_indicador(vendas_agrupado, grupo, arg, calc):
    
    if pd.isna(grupo):
        return pd.NA

    grupo = grupo.split(',')
    arg = arg.split(',')
    calc = calc.split(',')

    n = len(grupo)
    if n == 1:
        vendas_por_grupo_1 = vendas_agrupado.get_group(grupo[0])
        if calc[0] == 'sum':
            return vendas_por_grupo_1[arg[0]].sum()
        elif calc[0] == 'mean':
            return vendas_por_grupo_1[arg[0]].mean()

    elif n == 2:
        vendas_por_grupo_2 = []
        for e in range(0,2):
            vendas_por_grupo_2.append(vendas_agrupado.get_group(grupo[e]))
        if arg == ['Quantidade', 'Quantidade'] and calc == ['sum', 'sum']:
            grupo0_df = vendas_por_grupo_2[0]
            grupo1_df = vendas_por_grupo_2[1]

            return grupo0_df[arg[0]].sum()/grupo1_df[arg[1]].sum()


def medicao(import_desejado_df, item_grupo_df, vendas_df, reagrupa_df):

    vendas_reagrupa = dataframe_associative_vector(vendas_df, 'Produto/serviço', reagrupa_df['GRUPO'])
    vendas_agrupado = vendas_reagrupa.groupby('Produto/serviço')

    import_desejado = import_desejado_df.copy()
    for e in import_desejado_df['Item']:

        mask = import_desejado_df['Item'] == e

        grupo = item_grupo_df.loc[e, 'GRUPO']
        arg = item_grupo_df.loc[e, 'ARG']
        calc = item_grupo_df.loc[e, 'CALC']
        
        import_desejado.loc[mask,'Medição'] = calc_indicador(vendas_agrupado, grupo, arg, calc)
        
    return import_desejado