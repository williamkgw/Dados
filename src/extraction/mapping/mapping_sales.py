import pandas as pd

def init_mapping_vendas(mapping_f):
    columns = ('Produto/serviço', 'Categoria', 'Pilar', 'Grupo')
    mapping_vendas_df = pd.read_excel(mapping_f, index_col = 'Produto/serviço', usecols = columns,
                                    dtype = {'Produto/serviço': str, 'Categoria': str, 'Grupo': str, 'Pilar': str}
                                )
    return mapping_vendas_df