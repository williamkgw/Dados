import pandas as pd

def test_vendas_to_excel(
        config_carga_output, agg_grupo_df, agg_pilar_df, agg_categoria_df, agg_tempo_df,
        agg_exception_df, unique_mapping_df, vendas_missing_df,
        vendas_df, inadimplente
        ):
    agg_f = config_carga_output.sales_mapped
    vendas_missing_f = config_carga_output.missing_sales
    vendas_csv_f = config_carga_output.sales

    vendas_missing_df.to_excel(vendas_missing_f)
    vendas_df.to_excel(vendas_csv_f)
    with pd.ExcelWriter(agg_f) as writer:
        agg_grupo_df.to_excel(writer, sheet_name = 'grupo')
        agg_pilar_df.to_excel(writer, sheet_name = 'pilar')
        agg_categoria_df.to_excel(writer, sheet_name = 'categoria')
        agg_tempo_df.to_excel(writer, sheet_name = 'total')
        agg_exception_df.to_excel(writer, sheet_name = 'exception')
        inadimplente.to_excel(writer, sheet_name = 'inadimplencia')
        unique_mapping_df.to_excel(writer, sheet_name = 'unique_mapping')