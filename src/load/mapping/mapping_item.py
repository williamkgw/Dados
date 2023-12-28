import src.utils as utils
from src.config import BEG_DATE, END_DATE, INPUT_DIR

def load_mapping_item():
    emps = utils.is_not_done_carga(INPUT_DIR, END_DATE, 'mapping_item')
    print(emps)
    import_item_paths = utils.get_cargas_dir(INPUT_DIR, BEG_DATE).rglob('mapping_item.xlsx')
    utils.get_file_on_dir(import_item_paths, emps, INPUT_DIR, END_DATE)

def load_mapping_item_all():
    emps = utils.is_not_done_carga(INPUT_DIR, END_DATE, 'mapping_item')
    print(emps)
    new_mapping_paths = utils.get_cargas_dir(INPUT_DIR, END_DATE).rglob('mapping_item.xlsx')
    utils.df_all(new_mapping_paths, emps, f'{INPUT_DIR}/mapping_item_all.xlsx', 3)

def load_mapping_item_all_to_company_dir():
    utils.df_all_to_df(f'{INPUT_DIR}/mapping_item_all_preenchido.xlsx')
