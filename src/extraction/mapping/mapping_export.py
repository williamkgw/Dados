import pandas as pd

def init_mapping_export_template(path_export_template):
    return pd.read_excel(path_export_template, index_col = 'ID do Item')