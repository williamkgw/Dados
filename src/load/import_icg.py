import src.util.dataframe as dataframe
from src.util.others import copy_file_to 
from src.config import ConfigLoad

def load_import_icg():
    config = ConfigLoad('end', 'null')

    emps = dataframe.is_not_done_carga(config.input_dir.cargas.control_flow, 'import')
    print(emps)

    for emp in emps:
        print(emp)
        src_config = ConfigLoad('beg', emp)
        dest_config = ConfigLoad('end', emp)

        copy_file_to(src_config.input_dir.cargas.carga_company.export_template, dest_config.input_dir.cargas.carga_company.export_template)
