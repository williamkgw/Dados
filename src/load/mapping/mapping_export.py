def load_mapping_item_df(mapping_item_df, path_mapping_item):
    mapping_item_df.to_excel(path_mapping_item, index = 'ID do Item')
