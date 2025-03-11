import logging
from pathlib import Path
import pandas as pd

def load_carga_df(control_flow_path, excel_columns = None):
    carga_df = pd.read_excel(
        control_flow_path,
        index_col = 'Empresas', 
        usecols = excel_columns
        )
    return carga_df

def is_not_done_carga(control_flow_path, control_type):
    carga_df = load_carga_df(control_flow_path, ('Empresas', control_type))
    not_done_emps = carga_df[carga_df[control_type] == False]
    return tuple(not_done_emps.index)

def df_all(paths_f, path_all_f, n):
    logger = logging.getLogger("src.util.dataframe")
    df = pd.DataFrame()

    for path_f in paths_f:
        emp = path_f.parents[n].name
        logger.info(f"Started merging dataframe from {emp}: {path_f}")
        try:
            df_new = pd.read_excel(path_f)
            df_new['Empresa'] = emp
            df_new['path'] = path_f
            df = pd.concat([df, df_new])
        
        except Exception as e:
            logger.exception(f"Exception during df_all from {emp}: {path_f}")
            continue
    
    df.to_excel(path_all_f, index = False)

def df_all_to_df(path_all_f):
    logger = logging.getLogger("src.util.dataframe")

    try:
        logger.info(f"Started to load dataframe from {path_all_f}")
        df = pd.read_excel(path_all_f, index_col = 0)
    except Exception as e:
        logger.exception(f"Exception during load dataframe from {path_all_f}")
        return

    for name, group in df.groupby('Empresa'):
        logger.info(f"Started getting groupped dataframe from {name} in {path_all_f}")

        path = group['path'].iloc[0]
        path = Path(path)

        df = pd.DataFrame(data = group, columns = group.columns[:-2])
        
        try:
            logger.info(f"Started loading dataframe from {name} in {path}")
            df.to_excel(path)
        except Exception as e:
            logger.exception(f"Exception during loading dataframe from {name} in {path}")
            continue
