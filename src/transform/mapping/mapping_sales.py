from src.extraction.mapping.mapping_sales import init_mapping_vendas

def test_mapping_vendas(mapping_vendas_df, path_mapping_sales_mapped):
    # removing empty rows
    missing_mapping_vendas_df = mapping_vendas_df[mapping_vendas_df.isna().all(axis=1)]
    mapping_vendas_df = mapping_vendas_df.dropna(how = 'all', axis = 0)

    # configuring the dataframes to catch case sensitive
    mapping_vendas_df.index = mapping_vendas_df.index.str.lower()
    
    # removing duplicated index
    mapping_vendas_duplicated_df = mapping_vendas_df[mapping_vendas_df.index.duplicated(keep = False)]
    mapping_vendas_df = mapping_vendas_df[~mapping_vendas_df.index.duplicated(keep='last')]

    return [mapping_vendas_df, mapping_vendas_duplicated_df, missing_mapping_vendas_df, path_mapping_sales_mapped]

def correct_new_mapping(path_mapping_sales, path_new_mapping_sales):
    useful_cols = ['Categoria', 'Pilar', 'Grupo']

    mapping_df = init_mapping_vendas(path_mapping_sales).fillna('')
    new_mapping_df = init_mapping_vendas(path_new_mapping_sales).fillna('')
    set_values_mapping = set(mapping_df[useful_cols].value_counts().index)
    set_values_new_mapping = set(new_mapping_df[useful_cols].value_counts().index)
    set_excess_values_new_mapping = set_values_new_mapping - set_values_mapping
    excess_values_new_mapping_mask = new_mapping_df[useful_cols].agg(tuple, axis = 1).isin(set_excess_values_new_mapping)
    new_mapping_df.loc[excess_values_new_mapping_mask, 'Categoria'] = '*Reclassificar*'
    return new_mapping_df
