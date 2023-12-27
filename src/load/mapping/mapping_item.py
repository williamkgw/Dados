import src.utils as utils
from src.config import BEG_DATE, END_DATE, INPUT_DIR

def load_mapping_item():
    emps = utils.is_not_done_carga(INPUT_DIR, END_DATE, 'mapping_item')
    print(emps)
    import_item_paths = utils.get_cargas_dir(INPUT_DIR, BEG_DATE).rglob('mapping_item.xlsx')
    utils.get_file_on_dir(import_item_paths, emps, INPUT_DIR, END_DATE)