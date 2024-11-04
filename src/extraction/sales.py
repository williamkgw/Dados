import datetime
import pandas as pd

def correct_datetime_column(vendas_df):
    df = vendas_df.copy()
    df['Data e hora'] = pd.to_datetime(df['Data e hora'], errors = 'coerce')
    df = df.dropna(subset = 'Data e hora')
    return df

def get_vendas_last_36_months(vendas_df, end_date):
    max_datetime = pd.to_datetime(end_date) + pd.tseries.offsets.DateOffset(days=1)
    min_datetime = max_datetime - pd.tseries.offsets.DateOffset(years=3)
    mask = (vendas_df['Data e hora'] > min_datetime) & (vendas_df['Data e hora'] < max_datetime)
    return vendas_df[mask]

def init_vendas(path_sales):
    end_date = datetime.date(year = 2024, month = 10, day = 31)
    vendas_df =  pd.read_csv(path_sales, thousands = '.', decimal = ',', sep = ';',
                                encoding = 'latin1', parse_dates = ['Data e hora'],
                                dayfirst=True,
                        )
    vendas_df['Código'] = vendas_df['Código'].fillna(0)
    vendas_df = vendas_df.astype({'Produto/serviço': str, 'Quantidade': float, 'Bruto': float})
    vendas_df = correct_datetime_column(vendas_df)
    vendas_df = get_vendas_last_36_months(vendas_df, end_date)
    return vendas_df