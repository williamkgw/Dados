from pathlib import Path
import shutil

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

def main():
    root_dir = Path('data/input/upar_drive')
    paths = list(root_dir.rglob('10 - Outubro/output/out_import.xlsx'))
    out_dir = Path('ftp/8_emp_nova')
    emps = [path.parents[4].name for path in paths]
    print(emps)
    get_import_to_ftp_dir(paths, out_dir)

if __name__ == '__main__':
    main()