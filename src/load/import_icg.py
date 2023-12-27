import pandas as pd

import src.utils as utils
from src.config import BEG_DATE, END_DATE, INPUT_DIR

def update_import_date(paths, emps_filter, date):
    for path in paths:
        emp = path.parents[3].name
        if emp not in emps_filter:
            continue
        import_df = pd.read_excel(path, index_col = 'ID do Item')
        import_df.loc[:, 'Mês'] = date.month
        import_df.loc[:, 'Ano'] = date.year
        import_df.to_excel(path)

def reset_medicao_import(paths, emps_filter):
    for path in paths:
        emp = path.parents[3].name
        if emp not in emps_filter:
            continue
        import_df = pd.read_excel(path, index_col = 'ID do Item')
        cols_to_reset = ('Medição' ,'Fx Verde Inf/Previsto' ,'Fx Verde Sup' ,'Fx Vermelha Inf' ,
                         'Fx Vermelha Sup' ,'Fx Cliente Inf' ,'Fx Cliente Sup')
        import_df.loc[:, cols_to_reset] = pd.NA
        import_df.to_excel(path)

def load_import_icg():
    emps = utils.is_not_done_carga(INPUT_DIR, END_DATE, 'import')
    print(emps)
    import_paths = utils.get_cargas_dir(INPUT_DIR, BEG_DATE).rglob('import.xlsx')
    utils.get_file_on_dir(import_paths, emps, INPUT_DIR, END_DATE)
    import_copied_paths = list(utils.get_cargas_dir(INPUT_DIR, END_DATE).rglob('import.xlsx'))
    update_import_date(import_copied_paths, emps, END_DATE)
    reset_medicao_import(import_copied_paths, emps)