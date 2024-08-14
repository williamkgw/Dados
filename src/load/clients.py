import pandas as pd

def test_clientes_to_excel(config_company_output, agg_clientes, agg_clientes_total, agg_v_clientes, clientes_df):
    agg_file = config_company_output.clients_mapped
    clients_file = config_company_output.clients

    clientes_df.to_excel(clients_file)
    with pd.ExcelWriter(agg_file) as writer:
        agg_clientes.to_excel(writer, sheet_name = 'grupo_clientes')
        agg_clientes_total.to_excel(writer, sheet_name = 'grupo_total')
        agg_v_clientes.to_excel(writer, sheet_name = 'ativos_clientes')