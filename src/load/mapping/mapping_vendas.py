import src.utils as utils
from src.config import BEG_DATE, END_DATE, INPUT_DIR

def load_mapping_vendas():
    emps = utils.is_not_done_carga(INPUT_DIR, END_DATE, 'mapping')
    print(emps)
    new_mapping_paths = utils.get_cargas_dir(INPUT_DIR, BEG_DATE).rglob('new_mapping.xlsx')
    utils.get_file_on_dir(new_mapping_paths, emps, INPUT_DIR, END_DATE)
    new_mapping_copied_paths = utils.get_cargas_dir(INPUT_DIR, END_DATE).rglob('new_mapping.xlsx')
    utils.change_filename_on_dir(new_mapping_copied_paths, emps, 'mapping.xlsx')

def load_new_mapping_vendas_all():
    emps = utils.is_not_done_carga(INPUT_DIR, END_DATE, 'new_mapping')
    print(emps)
    new_mapping_paths = utils.get_cargas_dir(INPUT_DIR, END_DATE).rglob('new_mapping.xlsx')
    utils.df_all(new_mapping_paths, emps, f'{INPUT_DIR}/new_mapping_all.xlsx', 3)

def load_new_mapping_vendas_all_to_company_dir():
    utils.df_all_to_df(f'{INPUT_DIR}/new_mapping_all_preenchido.xlsx')

def load_correct_new_mapping_vendas_to_company_dir():
    utils.df_all_to_df(f'{INPUT_DIR}/corrected_new_mapping_preenchido.xlsx')