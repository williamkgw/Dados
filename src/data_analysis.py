import pandas as pd
import numpy as np
from pathlib import Path

def calc_indicador(vendas_agrupado, item):
    group = lambda gp, arg: vendas_agrupado.get_group(gp)[arg]
    nothing = lambda: None
    
    functions = {
        'Atendimentos de Emergência':           lambda: group('Emergencia', 'Quantidade').sum(),
        'Consultas Realizadas':                 lambda: group('Consultas', 'Quantidade').sum(), 
        'Faturamento - Consulta':               lambda: group('Consultas', 'Bruto').sum(),
        'Faturamento - Emergência':             lambda: group('Emergencia', 'Bruto').sum(),
        'Faturamento - Farmácia':               lambda: group('Farmácia', 'Bruto').sum(),
        'Faturamento - Insumos Clínica':        lambda: nothing(),
        'Faturamento - Procedimentos':          lambda: nothing(),
        'Faturamento - Vacina':                 lambda: group('Vacinas', 'Bruto').sum(),
        'Insumos Clínica Vendidos':             lambda: nothing(),
        'Preço Médio Consulta':                 lambda: group('Consultas', 'Bruto').mean(),
        'Preço Médio Emergência':               lambda: group('Emergencia', 'Bruto').mean(),
        'Preço Médio Farmácia':                 lambda: group('Farmácia', 'Bruto').mean(),
        'Preço Médio Insumos Clínica':          lambda: nothing(),
        'Preço Médio Procedimentos':            lambda: nothing(),
        'Preço Médio Vacina':                   lambda: group('Vacinas', 'Bruto').mean(),
        'Procedimentos Realizados':             lambda: nothing(),
        'Produtos Vendidos Farmácia':           lambda: group('Farmácia', 'Quantidade').sum(),
        'Vacinas Realizadas':                   lambda: group('Vacinas', 'Quantidade').sum(),
        'Consultas / Cirurgias':                lambda: group('Consultas', 'Quantidade').sum()/group('Cirurgias', 'Quantidade').sum(),
        'Consultas / Exames':                   lambda: nothing(),
        'Consultas / Internação':               lambda: group('Consultas', 'Quantidade').sum()/group('Internação', 'Quantidade').sum(),
        'Tícket Médio ':                        lambda: nothing(),
        'Alimentação Internação Realizada':     lambda: nothing(),
        'Aluguel CC Realizados':                lambda: nothing(),
        'Anestesias Realizadas':                lambda: group('Anestesias', 'Quantidade').sum(),
        'Cirurgias Realizadas':                 lambda: group('Cirurgias', 'Quantidade').sum(),
        'Doação Realizada':                     lambda: group('Doação', 'Quantidade').sum(),
        'Especialidades Realizada':             lambda: group('Especialidades', 'Quantidade').sum(),
        'Faturamento Alimentos Internação':     lambda: nothing(),
        'Faturamento Aluguel CC':               lambda: nothing(),
        'Faturamento Anestesia':                lambda: group('Anestesias', 'Bruto').sum(),
        'Faturamento Cirurgia':                 lambda: group('Cirurgias', 'Bruto').sum(),
        'Faturamento Doação':                   lambda: group('Doação', 'Bruto').sum(),
        'Faturamento Especialidades':           lambda: group('Especialidades', 'Bruto').sum(),
        'Faturamento Insumos Internação':       lambda: nothing(),
        'Faturamento Internação':               lambda: group('Internação', 'Bruto').sum(),
        'Faturamento Procedimento Internação':  lambda: group('Procedimentos Internação', 'Bruto').sum(),
        'Insumos Internação Realizados':        lambda: nothing(),
        'Internação Realizada':                 lambda: group('Internação', 'Quantidade').sum(),
        'Preço Médio Alimentos Internação':     lambda: group('Alimentos', 'Bruto').mean(),
        'Preço Médio Aluguel CC':               lambda: nothing(),
        'Preço Médio Anestesia':                lambda: group('Anestesias', 'Bruto').mean(),
        'Preço Médio Cirurgia':                 lambda: group('Cirurgias', 'Bruto').mean(),
        'Preço Médio Doação':                   lambda: group('Doação', 'Bruto').mean(),
        'Preço Médio Especialidades':           lambda: group('Especialidades', 'Bruto').mean(),
        'Preço Médio Insumos Internação':       lambda: nothing(),
        'Preço Médio Internação':               lambda: group('Internação', 'Bruto').mean(),
        'Preço Médio Procedimento Internação':  lambda: group('Procedimentos Internação', 'Bruto').mean(),
        'Procedimento Internação Realizados':   lambda: group('Procedimentos Internação', 'Quantidade').sum(),
        'Exames Imagem Vendidos':               lambda: nothing(),
        'Exames Laboratório Vendidos':          lambda: nothing(),
        'Faturamento - Imagem':                 lambda: nothing(),
        'Faturamento - Laboratório':            lambda: group('Laboratório', 'Bruto').sum(),
        'Preço Médio Exame':                    lambda: nothing(),
        'Preço Médio Exame Imgem':              lambda: nothing(),
        'Preço Médio Exame Laboratorial':       lambda: nothing()
        }
    function = functions[item]
    return function()

def medicao(import_desejado_df, vendas_df, reagrupa_s):

    import_obtido = import_desejado_df.copy()
    import_obtido['Medição'] = pd.NA

    vendas_df['Produto/serviço'] = vendas_df['Produto/serviço'].map(reagrupa_s)
    vendas_agrupado = vendas_df.groupby('Produto/serviço')

    for e in import_obtido.index:
        item = import_obtido.loc[e, 'Item']
        import_obtido.loc[e, 'Medição'] = calc_indicador(vendas_agrupado, item)

    return import_obtido

def get_import_csv():

    input_file_import_desejado = Path('data/input/import_desejado.xlsx')
    input_file_item_grupo = Path('data/input/item_grupo.xlsx')
    input_file_reagrupa = Path('data/input/reagrupa.xlsx')
    input_file_vendas = Path('data/input/vendas_teste.csv')

    output_file_import_obtido = Path('data/output/obtido.xlsx')
    output_file_comp = Path('data/output/comp.xlsx')

    import_desejado_df = pd.read_excel(input_file_import_desejado)
    item_grupo_df = pd.read_excel(input_file_item_grupo, index_col = 'Item')
    reagrupa_s = pd.read_excel(input_file_reagrupa, index_col = 'PRODUTOS/SERVIÇO').squeeze('columns')

    vendas_df = pd.read_csv(input_file_vendas, thousands='.', decimal=',', encoding='latin1', sep=';')
    
    import_obtido_df = medicao(import_desejado_df, item_grupo_df, vendas_df, reagrupa_s)

    comp = pd.DataFrame()
    comp['Medição Desejada'] = import_desejado_df['Medição']
    comp['Medição Obtida'] = import_obtido_df['Medição']
    comp['Item'] = import_desejado_df['Item']

    comp.to_excel(output_file_comp)
    import_obtido_df.to_excel(output_file_import_obtido, index = False)