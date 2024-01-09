import shutil

import src.utils as utils
from src.config import END_DATE, INPUT_DIR

def remove_all_inside_results(input_dir):
    dest_dir = input_dir / '.result'
    shutil.rmtree(dest_dir)

def copy_dir_to_export(input_dir, date, emps):
    dest_dir = input_dir / '.result/dirs'
    cargas_dir = utils.get_cargas_dir(input_dir, date)
    dest_dir.mkdir(parents = True, exist_ok = True)
    dirs = [dir for dir in list(cargas_dir.glob('*')) if dir.name in emps if dir.is_dir()]

    for dir in dirs:
        shutil.copytree(dir, dest_dir / dir.name, dirs_exist_ok = True)

def ftp_dir(input_dir, date, emps):
    dest_dir = input_dir / '.result/imports'
    cargas_dir = utils.get_cargas_dir(input_dir, date)
    dest_dir.mkdir(parents = True, exist_ok = True)
    for file in sorted(dest_dir.glob('*.xlsx')):
        file.unlink()

    out_paths = cargas_dir.rglob('out_import.xlsx')
    for out_path in out_paths:

        emp = out_path.parents[4].name
        if emp not in emps:
            continue
        print(emp)

        dest_path = dest_dir /f'{emp} - {out_path.name}'
        shutil.copy(out_path, dest_path)

def load_ftp_dir():
    emps = utils.is_not_done_carga(INPUT_DIR, END_DATE, 'ftp_dir')
    print(emps)
    remove_all_inside_results(INPUT_DIR)
    copy_dir_to_export(INPUT_DIR, END_DATE, emps)
    ftp_dir(INPUT_DIR, END_DATE, emps)