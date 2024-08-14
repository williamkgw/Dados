from src.util.others import (
    copy_dir_to_recursively,
    delete_dir_recursively,
    copy_file_to,
    create_dir
)
from src.config import ConfigLoad

def remove_all_inside_results(dir_results):
    delete_dir_recursively(dir_results)

def copy_dirs_carga_to_results_dirs_carga(dirs_carga, emps):
    dirs_company = []
    for emp in emps:
        config_company = ConfigLoad('end', emp)
        dir_company = config_company.input_dir.cargas.dir_name / emp
        dirs_company.append(dir_company)

    for dir_company in dirs_company:
        copy_dir_to_recursively(dir_company, dirs_carga / dir_company.name)


def copy_exports_to_results_exports_carga(dir_exports, emps):
    delete_dir_recursively(dir_exports)
    create_dir(dir_exports)

    for emp in emps:
        config_company = ConfigLoad('end', emp)
        print(emp)
        out_path = config_company.input_dir.cargas.carga_company.output.export

        dest_path = dir_exports / f'{emp} - {out_path.name}'
        copy_file_to(out_path, dest_path)
