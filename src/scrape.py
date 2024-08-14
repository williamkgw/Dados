import pandas as pd
import logging

from src.extraction.webscraping import download

from src.config import ConfigLoad

def get_logins(emps, credentials):
    import numpy as np

    credentials_df = pd.read_excel(credentials)
    credentials_df = credentials_df[credentials_df['SITES'] == 'SIMPLESVET']
    for emp in emps:
        config_company = ConfigLoad('end', emp)

        credentials_filtered_df = credentials_df[credentials_df['EMPRESA'] == emp]
        for _, row in credentials_filtered_df.iterrows():
            print(emp)
            date = config_company.date
            vendas_clientes_dir = config_company.input_dir.cargas.carga_company.dir_name

            nome_acesso = row['NOME DE ACESSO']
            acesso = row['ACESSO']
            senha = row['SENHA']
            extra = row['EXTRA']

            if extra is not np.nan:
                vendas_clientes_dir = vendas_clientes_dir / f'{extra}'
            try:
                download(acesso, senha, nome_acesso, vendas_clientes_dir, date)
            except Exception as e:
                logging.warning(f'{emp}/Falha no Download/{e}')
