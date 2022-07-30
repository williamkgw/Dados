from io_excel import read_excel
import data_analysis
import pandas as pd

def input_excel_path(num):
    filedir = ''
    filename = ''

    if num == 0:
        filedir = 'data\\excel_input\\'
        filename = 'import_desejado.xlsx'
        return filedir + filename

    elif num == 1:
        filedir = 'data\\excel_input\\'
        filename = 'item_grupo.xlsx'
        return filedir + filename

    elif num == 2:
        filedir = 'data\\excel_input\\'
        filename = 'reagrupa.xlsx'
        return filedir + filename

    elif num == 3:
        filedir = 'data\\excel_input\\'
        filename = 'vendas_teste.csv'
        return filedir + filename


def output_excel_path(num):

    filedir = ''
    filename = ''

    if num == 0:
        filedir = 'data\\excel_output\\'
        filename = 'import_original.xlsx'
        return filedir + filename
    
    if num == 1:
        filedir = 'data\\excel_output\\'
        filename = 'import_obtido.xlsx'
        return filedir + filename

    elif num==2:
        filedir = 'data\\excel_output\\'
        filename = 'comp.xlsx'
        return filedir + filename

def run():

    input_file_import_desejado = input_excel_path(0)
    input_file_item_grupo = input_excel_path(1)
    input_file_reagrupa = input_excel_path(2)
    input_file_vendas = input_excel_path(3)

    output_file_import_obtido = output_excel_path(1)
    output_file_comp = output_excel_path(2)

    import_desejado_df = pd.read_excel(input_file_import_desejado)
    item_grupo_df = pd.read_excel(input_file_item_grupo, index_col=0)
    reagrupa_df = read_excel(input_file_reagrupa, range_index='A1:A1', range_column='B1:B1', range_data='A1:B813')
    vendas_df = pd.read_csv(input_file_vendas, thousands='.', decimal=',', encoding='latin1', sep=';')
    
    import_obtido_df = data_analysis.medicao(import_desejado_df, item_grupo_df, vendas_df, reagrupa_df)

    comp = pd.DataFrame(columns = ['Medição Desejada', 'Medição Obtida', 'Item'])
    comp['Medição Desejada'] = import_desejado_df['Medição']
    comp['Medição Obtida'] = import_obtido_df['Medição']
    comp['Item'] = import_desejado_df['Item']

    comp.to_excel(output_file_comp)
    import_obtido_df.to_excel(output_file_import_obtido, index = False)

run()

#= SE(C2 = ""; "";SE(B2=C2;"Igual";"Diferente"))