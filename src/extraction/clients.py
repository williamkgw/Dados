import pandas as pd

def init_clientes(clientes_f, end_date):
    clientes_df = pd.read_csv(clientes_f, dayfirst = True, parse_dates = ['Inclusão'],
                        thousands = '.', decimal = ',', encoding = 'latin1',
                        sep = ';'
                        )
    clientes_df['Origem'] = clientes_df['Origem'].fillna('_outros')
    clientes_df['Inclusão'] = pd.to_datetime(clientes_df['Inclusão'], dayfirst = True, errors = 'coerce')
    clientes_df['Inclusão'] = clientes_df['Inclusão'].fillna('01/01/1900')
    mask = clientes_df['Inclusão'] <= pd.to_datetime(end_date)
    return clientes_df[mask]