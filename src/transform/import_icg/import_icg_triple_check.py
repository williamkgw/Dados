import pandas as pd

import src.util.dataframe as dataframe
from src.config import ConfigLoad

def triple_check(emps, export_all_companies, export_all_companies_compared):
    icg_import_cols = ('ID do Item', 'Mês', 'Ano', 'Medição', 'Item', 'Totalizado')
    icg_import_df = pd.read_excel(export_all_companies, index_col = 'ID do Item', usecols = icg_import_cols)

    df_all = pd.DataFrame()
    for emp in emps:
        config = ConfigLoad('end', emp)
        print(emp)
        out_import_df = pd.read_excel(config.input_dir.cargas.carga_company.output.export, index_col = 'ID do Item', usecols = icg_import_cols)

        set_id_out_import = set(out_import_df.index)
        set_id_icg_import = set(icg_import_df.index)
        common_id_import = list(set_id_icg_import & set_id_out_import)

        df = icg_import_df.loc[common_id_import, :]
        df['Empresa'] = emp
        df['Delta out_import'] = out_import_df.loc[common_id_import, 'Medição']
        df['Delta out_import'] = df['Delta out_import'] - df['Medição']
        df['Delta out_import'] = df['Delta out_import'].round(2)

        df_all = pd.concat([df_all, df])

    df_all.to_excel(export_all_companies_compared)

def transform_triple_check():
    config = ConfigLoad('end',  'null')

    emps = dataframe.is_not_done_carga(config.input_dir, config.date, 'triple_check')
    print(emps)
    triple_check(emps)