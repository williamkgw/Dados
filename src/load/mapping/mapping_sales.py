import pandas as pd

def load_mapping_vendas_df(mapping_vendas_df, path_vendas):
    columns_vendas = ('Categoria', 'Pilar', 'Grupo', 'grupo_simplesvet')
    mapping_vendas_df.to_excel(path_vendas, columns = columns_vendas)

def test_mapping_vendas_to_excel(mapping_vendas_duplicated_df, missing_mapping_vendas_df, testing_vendas_out_f):
    with pd.ExcelWriter(testing_vendas_out_f) as writer:
        mapping_vendas_duplicated_df.to_excel(writer, sheet_name = 'duplicated_index')
        missing_mapping_vendas_df.to_excel(writer, sheet_name = 'missing_mapping')
