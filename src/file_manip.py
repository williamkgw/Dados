import shutil
import logging
import carga_control
import pandas as pd

def update_import_date(paths, emps_filter, date):
    for path in paths:
        emp = path.parents[3].name
        if emp not in emps_filter:
            continue
        import_df = pd.read_excel(path, index_col = 'ID do Item')
        import_df.loc[:, 'Mês'] = date.month
        import_df.loc[:, 'Ano'] = date.year
        import_df.to_excel(path)

def reset_medicao_import(paths, emps_filter):
    for path in paths:
        emp = path.parents[3].name
        if emp not in emps_filter:
            continue
        import_df = pd.read_excel(path, index_col = 'ID do Item')
        cols_to_reset = ('Medição' ,'Fx Verde Inf/Previsto' ,'Fx Verde Sup' ,'Fx Vermelha Inf' ,
                         'Fx Vermelha Sup' ,'Fx Cliente Inf' ,'Fx Cliente Sup')
        import_df.loc[:, cols_to_reset] = pd.NA
        import_df.to_excel(path)

def change_filename_on_dir(paths, emps_filter, filename):
    for path in paths:
        emp = path.parents[3].name
        if emp not in emps_filter:
            continue
        path.rename(path.parent / filename)

def get_file_on_dir(paths, emps_filter, input_dir, end_date):
    for path in paths:
        emp = path.parents[3].name
        if emp not in emps_filter:
            continue
        filename_with_extension = path.name
        output_path = carga_control.get_carga_dir(input_dir, emp, end_date) / filename_with_extension
        shutil.copy2(path, output_path)

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

def remove_all_inside_results(input_dir):
    dest_dir = input_dir / '.result'
    shutil.rmtree(dest_dir)

def ftp_dir(input_dir, date, emps):
    dest_dir = input_dir / '.result/imports'
    cargas_dir = carga_control.get_cargas_dir(input_dir, date)
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

def copy_dir_to_export(input_dir, date, emps):
    dest_dir = input_dir / '.result/dirs'
    cargas_dir = carga_control.get_cargas_dir(input_dir, date)
    dest_dir.mkdir(parents = True, exist_ok = True)
    dirs = [dir for dir in list(cargas_dir.glob('*')) if dir.name in emps if dir.is_dir()]

    for dir in dirs:
        shutil.copytree(dir, dest_dir / dir.name, dirs_exist_ok = True)

def main():
    import sys

    END_DATE = carga_control.END_DATE
    BEG_DATE = carga_control.BEG_DATE
    INPUT_DIR = carga_control.INPUT_DIR
    cargas_dir = carga_control.get_cargas_dir(INPUT_DIR, END_DATE)
    logging.basicConfig(filename = cargas_dir / 'log.log', filemode = 'w', encoding = 'utf-8')

    assert len(sys.argv) == 2
    type_of_execution = sys.argv[1]

    if type_of_execution == 'mapping':
        emps = carga_control.is_not_done_carga(INPUT_DIR, END_DATE, 'mapping')
        print(emps)
        new_mapping_paths = carga_control.get_cargas_dir(INPUT_DIR, BEG_DATE).rglob('new_mapping.xlsx')
        get_file_on_dir(new_mapping_paths, emps, INPUT_DIR, END_DATE)
        new_mapping_copied_paths = carga_control.get_cargas_dir(INPUT_DIR, END_DATE).rglob('new_mapping.xlsx')
        change_filename_on_dir(new_mapping_copied_paths, emps, 'mapping.xlsx')

    if type_of_execution == 'mapping_cliente':
        emps = carga_control.is_not_done_carga(INPUT_DIR, END_DATE, 'mapping_cliente')
        print(emps)
        new_mapping_paths = carga_control.get_cargas_dir(INPUT_DIR, BEG_DATE).rglob('new_mapping_cliente.xlsx')
        get_file_on_dir(new_mapping_paths, emps, INPUT_DIR, END_DATE)
        new_mapping_copied_paths = carga_control.get_cargas_dir(INPUT_DIR, END_DATE).rglob('new_mapping_cliente.xlsx')
        change_filename_on_dir(new_mapping_copied_paths, emps, 'mapping_cliente.xlsx')

    elif type_of_execution == 'import':
        emps = carga_control.is_not_done_carga(INPUT_DIR, END_DATE, 'import')
        print(emps)
        import_paths = carga_control.get_cargas_dir(INPUT_DIR, BEG_DATE).rglob('import.xlsx')
        get_file_on_dir(import_paths, emps, INPUT_DIR, END_DATE)
        import_copied_paths = list(carga_control.get_cargas_dir(INPUT_DIR, END_DATE).rglob('import.xlsx'))
        update_import_date(import_copied_paths, emps, END_DATE)
        reset_medicao_import(import_copied_paths, emps)

    elif type_of_execution == 'mapping_item':
        emps = carga_control.is_not_done_carga(INPUT_DIR, END_DATE, 'mapping_item')
        print(emps)
        import_item_paths = carga_control.get_cargas_dir(INPUT_DIR, BEG_DATE).rglob('mapping_item.xlsx')
        get_file_on_dir(import_item_paths, emps, INPUT_DIR, END_DATE)

    elif type_of_execution == 'ftp_dir':
        emps = carga_control.is_not_done_carga(INPUT_DIR, END_DATE, 'ftp_dir')
        print(emps)
        remove_all_inside_results(INPUT_DIR)
        copy_dir_to_export(INPUT_DIR, END_DATE, emps)
        ftp_dir(INPUT_DIR, END_DATE, emps)

if __name__ == '__main__':
    main()