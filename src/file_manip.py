from pathlib import Path
import shutil
import locale
import datetime

def get_mapping_on_dir(paths, root_dir, s_date):

    for path in paths:
        emp = path.parents[3].name
        print(emp)

        output_path = root_dir / f'{emp}/Carga/{s_date}'
        shutil.copy(path, output_path)

def backup_import(paths):

    for path in paths:

        copy_path = path.parent / 'import.xlsx'
        shutil.copy(path, copy_path)

def get_import_to_ftp_dir(paths, dir):

    dir.mkdir(parents = True, exist_ok = True)

    for path in paths:

        emp = path.parents[4].name
        file_name = path.name

        out_path = dir / f'{emp}_{file_name}'
        shutil.copy(path, out_path)

def del_dirs_rmtree(paths):

    for path in paths:
        shutil.rmtree(path)

def copy_dirs(dest_dir, src_carga_dirs):
    
    for src_carga_dir in src_carga_dirs:

        dest_carga_dir = dest_dir / src_carga_dir.name

        shutil.copytree(src_carga_dir, dest_carga_dir)

import carga_control
def main():
    locale.setlocale(locale.LC_ALL, 'pt_pt.UTF-8')
    end_date  = datetime.date(day = 31, month = 12, year = 2022)
    input_dir = Path('data/input')
    cargas_dir = carga_control.get_cargas_dir(input_dir, end_date)
    emps_filter = carga_control.not_done(input_dir, end_date, 'new_mapping')
    
    # src_carga_dirs = sorted(cargas_dir.glob('*'))
    # src_carga_filtered_dirs = [src_carga_dir for src_carga_dir in src_carga_dirs if src_carga_dir.name in emps_filter]
    # out_dir = Path('copy_dirs/emps_11')
    # copy_dirs(out_dir, src_carga_filtered_dirs)

if __name__ == '__main__':
    main()