import pandas as pd

import src.utils as utils
from src.config import END_DATE, INPUT_DIR

def triple_check(out_imports, emps_filter, input_dir):
    icg_import_f = input_dir / 'icg_export.xlsx'
    icg_import_cols = ('ID do Item', 'Mês', 'Ano',
                       'Medição', 'Item', 'Totalizado'
                        )
    icg_import_df = pd.read_excel(icg_import_f, index_col = 'ID do Item', usecols = icg_import_cols)

    df_all = pd.DataFrame()
    for out_import in out_imports:
        emp = out_import.parents[4].name
        if emp not in emps_filter:
            continue
        print(emp)

        out_import_df = pd.read_excel(out_import, index_col = 'ID do Item', usecols = icg_import_cols)

        set_id_out_import = set(out_import_df.index)
        set_id_icg_import = set(icg_import_df.index)
        common_id_import = list(set_id_icg_import & set_id_out_import)

        df = icg_import_df.loc[common_id_import, :]
        df['Empresa'] = emp
        df['Delta out_import'] = out_import_df.loc[common_id_import, 'Medição']
        df['Delta out_import'] = df['Delta out_import'] - df['Medição']
        df['Delta out_import'] = df['Delta out_import'].round(2)

        df_all = pd.concat([df_all, df])

    out_import_comp = input_dir / 'comp_icg_out_import.xlsx'
    df_all.to_excel(out_import_comp)

def transform_triple_check():
        cargas_dir = utils.get_cargas_dir(INPUT_DIR, END_DATE)
        out_imports = cargas_dir.rglob('out_import.xlsx')
        emps = utils.is_not_done_carga(INPUT_DIR, END_DATE, 'triple_check')
        print(emps)
        triple_check(out_imports, emps, INPUT_DIR)