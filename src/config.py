import locale
from pathlib import Path
import yaml

def get_config(config_path):
    config_path = Path(config_path)
    with open(config_path, 'r') as file:
        config = yaml.safe_load(file)

    return config


class ConfigCargasLoad:

    def __init__(self, data, base_dir, emp, year_month_str):
        self._year_month_str = year_month_str
        self.dir_name = base_dir / year_month_str /data['dir-name']
        self.control_flow = self.dir_name / data['control-flow']
        self.credentials = self.dir_name / data['credentials']
        self.log = self.dir_name / data['log']
        self.carga_company = ConfigCargaCompanyLoad(data['carga-company'], self.dir_name, emp, year_month_str)


class ConfigCargaCompanyLoad:

    def __init__(self, data, base_dir, emp, year_month_str):
        self._emp = emp
        self._year_month_str = year_month_str
        self.dir_name = base_dir / emp / data['dir-name'] / year_month_str
        self.animals_and_clients = self.dir_name / data['animals-and-clients']
        self.clients = self.dir_name / data['clients']
        self.sales = self.dir_name / data['sales']
        self.export_template = self.dir_name / data['export-template']
        self.mapping_sales = self.dir_name / data['mapping-sales']
        self.new_mapping_sales = self.dir_name / data['new-mapping-sales']
        self.mapping_client = self.dir_name / data['mapping-client']
        self.new_mapping_client = self.dir_name / data['new-mapping-client']
        self.mapping_export = self.dir_name / data['mapping-export']
        self.output = ConfigOutputLoad(data['output'], self.dir_name)


class ConfigOutputLoad:

    def __init__(self, data, base_dir):
        self.dir_name = base_dir / data['dir-name']
        self.export = self.dir_name / data['export']
        self.sales_mapped = self.dir_name / data['sales-mapped']
        self.clients_mapped = self.dir_name / data['clients-mapped']
        self.mapping_sales_mapped = self.dir_name / data['mapping-sales-mapped']
        self.mapping_clients_mapped = self.dir_name / data['mapping-clients-mapped']
        self.missing_sales = self.dir_name / data['missing-sales']
        self.sales = self.dir_name / data['sales']
        self.clients = self.dir_name / data['clients']


class ConfigAnalyticSalesLoad:

    def __init__(self, data, base_dir):
        self.dir_name = base_dir / data['dir-name']
        self.sales = self.dir_name / data['sales']


class ConfigAnalyticClientsLoad:

        def __init__(self, data, base_dir):
            self.dir_name = base_dir / data['dir-name']
            self.clients = self.dir_name / data['clients']


class ConfigAnalyticAnimalsAndClients:

    def __init__(self, data, base_dir):
        self.dir_name = base_dir / data['dir-name']
        self.animals_and_clients = self.dir_name / data['animals-and-clients']


class ConfigAnalyticLoad:

    def __init__(self, data, base_dir, emp, year_month_str):
        self.dir_name = base_dir / year_month_str / emp / data['dir-name']
        self.sales_analytic = ConfigAnalyticSalesLoad(data['sales-analytic'], self.dir_name)
        self.clients_analytic = ConfigAnalyticClientsLoad(data['clients-analytic'], self.dir_name)
        self.animals_and_clients_analytic = ConfigAnalyticAnimalsAndClients(data['animals-and-clients-analytic'], self.dir_name)


class ConfigResultsLoad:

    def __init__(self, data, base_dir):
        self.dir_name = base_dir / data['dir-name']
        self.dirs_carga = self.dir_name / data['dirs-carga']
        self.exports_carga = self.dir_name / data['exports-carga']


class ConfigInputDirLoad:

    def __init__(self, data, emp, date):
        self.dir_name = Path(data['dir-name'])
        self.str_year_month = self.get_str_year_month(date)
        self.new_mapping_sales_corrected_all = self.dir_name / data['new-mapping-sales-corrected-all']
        self.new_mapping_sales_corrected_all_modified = self.dir_name / data['new-mapping-sales-corrected-all-modified']
        self.mapping_export_all = self.dir_name / data['mapping-export-all']
        self.mapping_export_all_modified = self.dir_name / data['mapping-export-all-modified']
        self.new_mapping_sales_all = self.dir_name / data['new-mapping-sales-all']
        self.new_mapping_sales_all_modified = self.dir_name / data['new-mapping-sales-all-modified']
        self.new_mapping_clients_all = self.dir_name / data['new-mapping-clients-all']
        self.new_mapping_clients_all_modified = self.dir_name / data['new-mapping-clients-all-modified']
        self.export_all_companies = self.dir_name / data['export-all-companies-compared']
        self.results = ConfigResultsLoad(data['results'], self.dir_name)
        self.cargas = ConfigCargasLoad(data['cargas'], self.dir_name, emp, self.get_str_year_month(date))
        self.analytic = ConfigAnalyticLoad(data['analytic'], self.dir_name, emp, self.get_str_year_month(date))

    def get_str_year_month(self, date):
        locale.setlocale(locale.LC_ALL, 'pt_pt.UTF-8')
        return date.strftime('%Y/%m - %B').title()


class ConfigLoad:

    def __init__(self, type, emp):
        data_yaml = get_config('data/data.yaml')
        data = data_yaml[type]

        self.date = data['date']
        self.emp = emp
        self.input_dir = ConfigInputDirLoad(data['input-dir'], self.emp, self.date)
