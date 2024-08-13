import datetime
import pandas as pd

def get_vendas_last_36_months(vendas_df):
    max_date = max(vendas_df['Data e hora'])
    min_date = datetime.datetime(year = max_date.year - 3, month = max_date.month, day = 1)
    mask = vendas_df['Data e hora'] > min_date
    return vendas_df[mask]

def init_vendas(vendas_f):
    vendas_df =  pd.read_csv(vendas_f, thousands = '.', decimal = ',', sep = ';',
                        encoding = 'latin1', parse_dates = ['Data e hora'],
                          dayfirst=True,
                        )
    vendas_df['Código'] = vendas_df['Código'].fillna(0)
    vendas_df = vendas_df.astype({'Produto/serviço': str, 'Quantidade': float, 'Bruto': float})
    vendas_df = get_vendas_last_36_months(vendas_df)
    return vendas_df