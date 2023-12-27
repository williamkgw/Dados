from pathlib import Path
import pandas as pd
import logging

import src.utils as utils
from src.config import END_DATE, INPUT_DIR

def df_all(paths_f, emps_filter, path_all_f, n):
    df = pd.DataFrame()

    for path_f in paths_f:
        emp = path_f.parents[n].name
        if emp not in emps_filter:
            continue
        print(emp)
        df_new = pd.read_excel(path_f)
        df_new['Empresa'] = emp
        df_new['path'] = path_f
        df = pd.concat([df, df_new])
    
    df.to_excel(path_all_f, index = False)

def df_all_to_df(path_all_f):

    df = pd.read_excel(path_all_f, index_col = 0)

    for name, group in df.groupby('Empresa'):
        print(name)

        path = group['path'].iloc[0]
        path = Path(path)

        df = pd.DataFrame(data = group, columns = group.columns[:-2])
        
        print(path)
        if path.parent.is_dir():
            df.to_excel(path)
        else:
            print('NÃO EXISTE: ', name)

def main():
    import sys

    cargas_dir = utils.get_cargas_dir(INPUT_DIR, END_DATE)
    logging.basicConfig(filename = cargas_dir / 'log.log', filemode = 'w', encoding = 'utf-8')

    assert len(sys.argv) == 3
    type_of_execution = sys.argv[-1]

    if type_of_execution == 'mapping':
        emps = utils.is_not_done_carga(INPUT_DIR, END_DATE, 'mapping')
        print(emps)
        new_mapping_paths = utils.get_cargas_dir(INPUT_DIR, END_DATE).rglob('mapping.xlsx')
        df_all(new_mapping_paths, emps, f'{INPUT_DIR}/mapping_all.xlsx', 3)

    elif type_of_execution == 'new_mapping':
        emps = utils.is_not_done_carga(INPUT_DIR, END_DATE, 'new_mapping')
        print(emps)
        new_mapping_paths = utils.get_cargas_dir(INPUT_DIR, END_DATE).rglob('new_mapping.xlsx')
        df_all(new_mapping_paths, emps, f'{INPUT_DIR}/new_mapping_all.xlsx', 3)

    elif type_of_execution == 'new_mapping_cliente':
        emps = utils.is_not_done_carga(INPUT_DIR, END_DATE, 'new_mapping_cliente')
        print(emps)
        new_mapping_paths = utils.get_cargas_dir(INPUT_DIR, END_DATE).rglob('new_mapping_cliente.xlsx')
        df_all(new_mapping_paths, emps, f'{INPUT_DIR}/new_mapping_cliente_all.xlsx', 3)

    elif type_of_execution == 'mapping_item':
        emps = utils.is_not_done_carga(INPUT_DIR, END_DATE, 'mapping_item')
        print(emps)
        new_mapping_paths = utils.get_cargas_dir(INPUT_DIR, END_DATE).rglob('mapping_item.xlsx')
        df_all(new_mapping_paths, emps, f'{INPUT_DIR}/mapping_item_all.xlsx', 3)

    elif type_of_execution == 'new_mapping_all':
        df_all_to_df(f'{INPUT_DIR}/new_mapping_all_preenchido.xlsx')

    elif type_of_execution == 'new_mapping_cliente_all':
        df_all_to_df(f'{INPUT_DIR}/new_mapping_cliente_all_preenchido.xlsx')

    elif type_of_execution == 'mapping_item_all':
        df_all_to_df(f'{INPUT_DIR}/mapping_item_all_preenchido.xlsx')

    elif type_of_execution == 'correct_mapping':
        df_all_to_df(f'{INPUT_DIR}/corrected_new_mapping_preenchido.xlsx')

if __name__ == '__main__':
    main()