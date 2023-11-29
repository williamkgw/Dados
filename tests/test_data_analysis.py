import unittest
import pandas as pd

from src.data_analysis import init_clientes, init_vendas, init_mapping_clientes, init_mapping_vendas
from src.data_analysis import test_vendas, test_clientes, test_mapping_vendas, test_mapping_clientes

from tests.config import ConfigLoad

def vendas_get_header_read_excel(sheet_name):
    header_list = lambda x: list(range(x))
    dict_selection_header_list = {
        'grupo': header_list(3),
        'pilar': header_list(3),
        'categoria': header_list(2),
        'total': header_list(1),
        'exception': header_list(1),
        'unique_mapping': header_list(1)
    }
    return dict_selection_header_list[sheet_name]

def vendas_get_index_read_excel(sheet_name):
    index_list = lambda x: list(range(x))
    dict_selection_index_list = {
        'grupo': index_list(1),
        'pilar': index_list(1),
        'categoria': index_list(1),
        'total': index_list(1),
        'exception': index_list(1),
        'unique_mapping': index_list(3)
    }
    return dict_selection_index_list[sheet_name]

def clientes_get_header_read_excel(sheet_name):
    header_list = lambda x: list(range(x))
    dict_selection_header_list = {
        'grupo_clientes': header_list(2),
        'grupo_total': header_list(1),
        'ativos_clientes': header_list(1),
    }
    return dict_selection_header_list[sheet_name]

def clientes_get_index_read_excel(sheet_name):
    index_list = lambda x: list(range(x))
    dict_selection_index_list = {
        'grupo_clientes': index_list(1),
        'grupo_total': index_list(1),
        'ativos_clientes': index_list(1)
    }
    return dict_selection_index_list[sheet_name]


def read_vendas(file):
    xl = pd.ExcelFile(file)
    sheet_names = xl.sheet_names
    dfs = []
    for sheet_name in sheet_names:
        df = pd.read_excel(file, sheet_name = sheet_name, index_col = vendas_get_index_read_excel(sheet_name), header = vendas_get_header_read_excel(sheet_name))
        df = df.astype(float)
        dfs.append(df)
    return dfs

def read_clientes(file):
    xl = pd.ExcelFile(file)
    sheet_names = xl.sheet_names
    dfs = []
    for sheet_name in sheet_names:
        df = pd.read_excel(file, sheet_name = sheet_name, index_col = clientes_get_index_read_excel(sheet_name), header = clientes_get_header_read_excel(sheet_name))
        dfs.append(df)
    return dfs

class TestVendas(unittest.TestCase):

    configs = ConfigLoad()

    def test_test_vendas(self):
        vendas_df =  init_vendas(self.configs.vendas_f)
        mapping_df = init_mapping_vendas(self.configs.mapping_vendas_f)
        mapping_df, *_ = test_mapping_vendas(mapping_df, self.configs.output_dir)
        
        dfs = test_vendas(vendas_df, mapping_df)[0:5]
        dfs1 = read_vendas(self.configs.test_agg_f)[0:5]

        self.assertEqual(len(dfs), len(dfs1))
        for i in range(len(dfs)):
            pd.testing.assert_frame_equal(dfs[i], dfs1[i], check_freq = False)

class TestClientes(unittest.TestCase):

    configs = ConfigLoad()

    def test_test_clientes(self):
        vendas_df =  init_vendas(self.configs.vendas_f)
        clientes_df = init_clientes(self.configs.clientes_f, self.configs.end_date)
        mapping_clientes_df = init_mapping_clientes(self.configs.mapping_clientes_f)
        mapping_clientes_df = test_mapping_clientes(mapping_clientes_df, self.configs.output_dir)
        dfs = test_clientes(vendas_df, clientes_df, mapping_clientes_df)[0:3]
        dfs1 = read_clientes(self.configs.test_agg_clientes_f)

        self.assertEqual(len(dfs), len(dfs1))
        for i in range(len(dfs)):
            pd.testing.assert_frame_equal(dfs[i], dfs1[i], check_freq = False, check_names = False)
