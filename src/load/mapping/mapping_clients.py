import pandas as pd

def load_mapping_clientes_df(dest_mapping_clientes_df, path_mapping_clientes):
    dest_mapping_clientes_df.to_excel(path_mapping_clientes, columns = ['Grupo'])

def test_mapping_clientes_to_excel(config_company_output, mapping_vendas_duplicated_df, missing_mapping_vendas_df):
    testing_mapping_clientes_f = config_company_output.mapping_clients_mapped
    with pd.ExcelWriter(testing_mapping_clientes_f) as writer:
        mapping_vendas_duplicated_df.to_excel(writer, sheet_name = 'duplicated_index')
        missing_mapping_vendas_df.to_excel(writer, sheet_name = 'missing_mapping')

