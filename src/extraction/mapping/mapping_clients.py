import pandas as pd

def init_mapping_clientes(mapping_clientes_f):
    mapping_vendas_df = pd.read_excel(mapping_clientes_f, index_col = 'Origem', 
                                    dtype = {'Origem': str, 'Grupo': str}
                                    )
    return mapping_vendas_df