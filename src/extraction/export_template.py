import pandas as pd

def init_export_template(path_export_emplate):
    icg_import_cols = ('ID do Item', 'Mês', 'Ano', 'Medição', 'Item', 'Totalizado')
    return pd.read_excel(path_export_emplate, index_col = 'ID do Item', usecols = icg_import_cols)