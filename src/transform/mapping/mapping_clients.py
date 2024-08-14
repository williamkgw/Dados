def test_mapping_clientes(mapping_clientes_df):
    # removing empty rows
    missing_mapping_clientes_df = mapping_clientes_df[mapping_clientes_df.isna().all(axis=1)]
    mapping_clientes_df = mapping_clientes_df.dropna(how = 'all', axis = 0)

    # configuring the dataframes to catch case sensitive
    mapping_clientes_df.index = mapping_clientes_df.index.str.lower()
    
    # removing duplicated index
    mapping_clientes_duplicated_df = mapping_clientes_df[mapping_clientes_df.index.duplicated(keep = False)]
    mapping_clientes_df = mapping_clientes_df[~mapping_clientes_df.index.duplicated(keep='last')]

    return [mapping_clientes_df, mapping_clientes_duplicated_df, missing_mapping_clientes_df]
