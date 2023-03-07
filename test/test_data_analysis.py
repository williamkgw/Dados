import sys
sys.path.insert(0, 'src')

import unittest
from pathlib import Path
import pandas as pd
from data_analysis import test_vendas, test_clientes

root_dir = Path('test/data/input')
year_month = '2023/01 - Janeiro'
cargas_dir = root_dir / year_month

def get_header_read_excel(sheet_name):
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

def get_index_read_excel(sheet_name):
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

def read_vendas(file):
    xl = pd.ExcelFile(file)
    sheet_names = xl.sheet_names
    dfs = []
    for sheet_name in sheet_names:
        df = pd.read_excel(file, sheet_name = sheet_name, header = get_header_read_excel(sheet_name), index_col = get_index_read_excel(sheet_name))
        dfs.append(df)
    return dfs

def read_clientes(file):
    xl = pd.ExcelFile(file)
    sheet_names = xl.sheet_names
    dfs = []
    for sheet_name in sheet_names:
        df = pd.read_excel(file, sheet_name = sheet_name, index_col = 0)
        dfs.append(df)
    return dfs

class TestVendas(unittest.TestCase):

    emp = 'Almir Tavares'
    carga_dir = cargas_dir / f'{emp}/Carga/{year_month}'
    output_dir = carga_dir / 'output'
    vendas_f = carga_dir / 'Vendas.csv'
    test_agg_f = output_dir / 'test_agg.xlsx'

    def test_test_vendas(self):
        vendas_df =  pd.read_csv(self.vendas_f, thousands = '.', decimal = ',', sep = ';',
                        encoding = 'latin1', parse_dates = ['Data e hora'], dayfirst=True,
                        )
        mapping_f = self.carga_dir / 'new_mapping.xlsx'
        mapping_df = pd.read_excel(mapping_f, index_col = 'Produto/serviço', 
                                    dtype = {'Produto/serviço': str, 'Categoria': str, 'Grupo': str, 'Pilar': str}
                                    )
        mapping_df.index = mapping_df.index.str.lower()

        dfs = test_vendas(vendas_df, mapping_df)

        dfs1 = read_vendas(self.test_agg_f)

        dfs = [df.astype(float) for df in dfs[:5]]
        dfs1 = [df1.astype(float) for df1 in dfs1]

        # self.assertEqual(len(dfs), len(dfs1))
        # for i in range(len(dfs)):
        #     pd.testing.assert_frame_equal(dfs[i], dfs1[i], check_freq = False)
        pd.testing.assert_frame_equal(dfs[0], dfs1[0], check_freq = False)
        pd.testing.assert_frame_equal(dfs[1], dfs1[1], check_freq = False)
        pd.testing.assert_frame_equal(dfs[2], dfs1[2], check_freq = False)
        pd.testing.assert_frame_equal(dfs[3], dfs1[3], check_freq = False)
        pd.testing.assert_frame_equal(dfs[4], dfs1[4], check_freq = False)

class TestClientes(unittest.TestCase):

    emp = 'Almir Tavares'
    carga_dir = cargas_dir / f'{emp}/Carga/{year_month}'
    output_dir = carga_dir / 'output'
    vendas_f = carga_dir / 'Vendas.csv'
    clientes_f = carga_dir / 'Clientes.csv'
    test_agg_clientes_f = output_dir / 'test_agg_clientes.xlsx'

    def test_test_clientes(self):
        vendas_df =  pd.read_csv(self.vendas_f, thousands = '.', decimal = ',', sep = ';',
                        encoding = 'latin1', parse_dates = ['Data e hora'], dayfirst=True,
                        )
        clientes_df = pd.read_csv(self.clientes_f, dayfirst = True, parse_dates = ['Inclusão'],
                        thousands = '.', decimal = ',', encoding = 'latin1', sep = ';'
                        )
        dfs = test_clientes(vendas_df, clientes_df)
        dfs1 = read_clientes(self.test_agg_clientes_f)

        dfs = [df.astype(float) for df in dfs]
        dfs1 = [df1.astype(float) for df1 in dfs1]
        self.assertEqual(len(dfs), len(dfs1))
        for i in range(len(dfs)):
            pd.testing.assert_frame_equal(dfs[i], dfs1[i], check_freq = False, check_names = False)


def main():
    unittest.main()

if __name__ == '__main__':
    main()