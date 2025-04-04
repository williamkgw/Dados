import logging
from pathlib import Path
import pandas as pd

logger = logging.getLogger("src.util.dataframe")

def load_carga_df(control_flow_path, excel_columns = None):
    try:
        logger.info(f"Loading control flow data from {control_flow_path}")
        carga_df = pd.read_excel(
            control_flow_path,
            index_col = 'Empresas', 
            usecols = excel_columns
            )
        logger.info(f"Successfully loaded control flow data from {control_flow_path}")
        return carga_df
    except Exception as e:
        logger.exception(f"Error loading control flow data from {control_flow_path}: {str(e)}")
        raise

def is_not_done_carga(control_flow_path, control_type):
    try:
        logger.info(f"Checking incomplete tasks of type '{control_type}' in {control_flow_path}")
        carga_df = load_carga_df(control_flow_path, ('Empresas', control_type))
        not_done_emps = carga_df[carga_df[control_type] == False]
        result = tuple(not_done_emps.index)
        logger.info(f"Found {len(result)} companies with incomplete '{control_type}' tasks")
        return result
    except Exception as e:
        logger.exception(f"Error checking incomplete tasks in {control_flow_path}: {str(e)}")
        return tuple()

def df_all(paths_f, path_all_f, n):
    df = pd.DataFrame()

    for path_f in paths_f:
        emp = path_f.parents[n].name
        logger.info(f"Started merging dataframe from {emp}: {path_f}")
        try:
            df_new = pd.read_excel(path_f)
            df_new['Empresa'] = emp
            df_new['path'] = path_f
            df = pd.concat([df, df_new])
            logger.info(f"Successfully merged data from {emp}")
        except Exception as e:
            logger.exception(f"Exception during df_all from {emp}: {str(e)}")
            continue
    
    try:
        logger.info(f"Saving combined dataframe to {path_all_f}")
        df.to_excel(path_all_f, index = False)
        logger.info(f"Successfully saved combined dataframe to {path_all_f}")
    except Exception as e:
        logger.exception(f"Error saving combined dataframe to {path_all_f}: {str(e)}")

def df_all_to_df(path_all_f):
    try:
        logger.info(f"Started to load dataframe from {path_all_f}")
        df = pd.read_excel(path_all_f, index_col = 0)
        logger.info(f"Successfully loaded dataframe from {path_all_f}")
    except Exception as e:
        logger.exception(f"Exception during load dataframe from {path_all_f}: {str(e)}")
        return

    for name, group in df.groupby('Empresa'):
        logger.info(f"Started getting groupped dataframe from {name} in {path_all_f}")

        try:
            path = group['path'].iloc[0]
            path = Path(path)

            company_df = pd.DataFrame(data = group, columns = group.columns[:-2])
            
            logger.info(f"Started loading dataframe from {name} in {path}")
            company_df.to_excel(path)
            logger.info(f"Successfully saved dataframe for {name} to {path}")
        except Exception as e:
            logger.exception(f"Exception during loading dataframe from {name} in {path}: {str(e)}")
            continue