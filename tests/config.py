from pathlib import Path

from src.utils import get_config, get_carga_dir, get_cargas_dir

class ConfigLoad():

    def __init__(self):
        config_path = 'data/data_test.yaml'
        configs = get_config(config_path)

        self.company_name = configs['utils']['company_name']
        self.end_date = configs['utils']['end_date']
        self.beg_date = configs['utils']['beg_date']
        self.input_dir = Path(configs['utils']['input_dir'])
        self.cargas_dir = get_cargas_dir(self.input_dir, self.end_date)
        self.carga_dir = get_carga_dir(self.input_dir, self.company_name, self.end_date)
        self.output_dir = self.carga_dir / 'output'
        self.vendas_f = self.carga_dir / 'Vendas.csv'
        self.clientes_f = self.carga_dir / 'Clientes.csv'
        self.mapping_vendas_f = self.carga_dir / 'new_mapping.xlsx'
        self.mapping_clientes_f = self.carga_dir / 'mapping_cliente.xlsx'
        self.test_agg_clientes_f = self.output_dir / 'test_agg_clientes.xlsx'
        self.test_agg_f = self.output_dir / 'test_agg.xlsx'