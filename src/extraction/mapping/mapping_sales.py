import pandas as pd

def init_mapping_vendas(mapping_f):
    mapping_vendas_df = pd.read_excel(mapping_f, index_col = 'Produto/serviço', 
                                    dtype = {'Produto/serviço': str, 'Categoria': str, 'Grupo': str, 'Pilar': str}
                                    )
    return mapping_vendas_df