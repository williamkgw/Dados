import pandas as pd
import logging

from src.extraction.webscraping import download_with_timeout

from src.config import ConfigLoad

logger = logging.getLogger('src.scrape')

def get_logins(emps, credentials):
    import numpy as np

    credentials_df = pd.read_excel(credentials)
    credentials_df = credentials_df[credentials_df['SITES'] == 'SIMPLESVET']
    for emp in emps:
        logger.info(f"Starting scrape for {emp}")
        config_company = ConfigLoad('end', emp)

        credentials_filtered_df = credentials_df[credentials_df['EMPRESA'] == emp]

        if credentials_filtered_df.empty:
            logger.warning(f"No credentials found for {emp}")

        for _, row in credentials_filtered_df.iterrows():
            date = config_company.date
            vendas_clientes_dir = config_company.input_dir.cargas.carga_company.dir_name

            nome_acesso = row['NOME DE ACESSO']
            acesso = row['ACESSO']
            senha = row['SENHA']
            extra = row['EXTRA']

            if extra is not np.nan:
                vendas_clientes_dir = vendas_clientes_dir / f'{extra}'

            sucess = download_with_timeout(acesso, senha, nome_acesso, vendas_clientes_dir, date)

            if sucess:
                logger.info(f"Download completed for {emp} - {nome_acesso}")
            else:
                expected_downloaded_file_patterns = ("Vendas*", "Clientes*", "Animais_e_Clientes*")
                for expected_downloaded_file_pattern in expected_downloaded_file_patterns:
                    for matched_downloaded_file_path in vendas_clientes_dir.glob(expected_downloaded_file_pattern):
                        matched_downloaded_file_path.unlink()
                        logging.info(f"Removed file: {matched_downloaded_file_path}")

                logger.warning(f"Download failed for {emp} - {nome_acesso}")
