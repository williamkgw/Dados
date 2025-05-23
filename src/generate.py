from src.config import ConfigLoad
import logging

from src.transform.export import med
from src.load.export import load_export_df

logger = logging.getLogger('src.generate')

def get_med_import(emps):
    for emp in emps:
        config = ConfigLoad('end', emp)

        mapping_item = config.input_dir.cargas.carga_company.mapping_export
        import_file = config.input_dir.cargas.carga_company.export_template
        agg_vendas_file = config.input_dir.cargas.carga_company.output.sales_mapped
        agg_clientes_file = config.input_dir.cargas.carga_company.output.clients_mapped
        out_import_file = config.input_dir.cargas.carga_company.output.export
        date = config.date

        try:
            logger.info(f"Started to generate import for {emp}")
            df = med(import_file, agg_vendas_file, agg_clientes_file, mapping_item, date, -1)
        except Exception as e:
            logger.warning(f"Exception during generating import for {emp}: {e}")
            continue

        load_export_df(df, out_import_file)

import pandas as pd
from src.extraction.export_template import init_export_template

def triple_check(emps, export_all_companies, export_all_companies_compared):
    try:
        icg_import_df = init_export_template(export_all_companies)

        df_all = pd.DataFrame()
        for emp in emps:
            config = ConfigLoad('end', emp)
            logger.info(f"Processing triple check for {emp}")
            
            try:
                out_import_df = init_export_template(config.input_dir.cargas.carga_company.output.export)

                set_id_out_import = set(out_import_df.index)
                set_id_icg_import = set(icg_import_df.index)
                common_id_import = list(set_id_icg_import & set_id_out_import)

                df = icg_import_df.loc[common_id_import, :]
                df['Empresa'] = emp
                df['Delta out_import'] = out_import_df.loc[common_id_import, 'Medição']
                df['Delta out_import'] = df['Delta out_import'] - df['Medição']
                df['Delta out_import'] = df['Delta out_import'].round(2)

                df_all = pd.concat([df_all, df])
            except Exception as e:
                logger.exception(f"Error in triple_check for {emp}: {str(e)}")
                continue

        logger.info(f"Saving triple check results to {export_all_companies_compared}")
        df_all.to_excel(export_all_companies_compared)
    except Exception as e:
        logger.exception(f"Error in triple_check: {str(e)}")

from src.transform.mapping.mapping_export import template_mapping_item
from src.load.mapping.mapping_export import load_mapping_item_df

def get_mapping_item(emps):
    for emp in emps:
        logger.info(f"Processing mapping item for {emp}")
        config = ConfigLoad('end', emp)

        try:
            path_mapping_sales = config.input_dir.cargas.carga_company.mapping_sales
            path_mapping_export = config.input_dir.cargas.carga_company.mapping_export
            path_export = config.input_dir.cargas.carga_company.export_template
            path_mapping_export = config.input_dir.cargas.carga_company.mapping_export

            template_mapping_item_df = template_mapping_item(path_export, path_mapping_sales, path_mapping_export)
            load_mapping_item_df(template_mapping_item_df, path_mapping_export)
            logger.info(f"Successfully created mapping item for {emp}")
        except Exception as e:
            logger.exception(f"Error in get_mapping_item for {emp}: {str(e)}")
            continue

from src.transform.mapping.mapping_sales import correct_new_mapping

def filter_and_correct_new_mapping_all(emps, path_new_mapping_sales_corrected_all):
    new_mapping_all_df = pd.DataFrame()
    for emp in emps:
        logger.info(f"Started correcting new_mapping_sales for {emp}")
        config = ConfigLoad('end', emp)

        path_mapping_sales = config.input_dir.cargas.carga_company.mapping_sales
        path_new_mapping_sales = config.input_dir.cargas.carga_company.new_mapping_sales

        try: 
            new_mapping_df = correct_new_mapping(path_mapping_sales, path_new_mapping_sales)
            new_mapping_df['Empresa'] = emp
            new_mapping_df['path'] = path_new_mapping_sales

            new_mapping_all_df = pd.concat([new_mapping_all_df, new_mapping_df])
        except Exception as e:
            logger.exception(f"Exception during the correcting new_mapping_sales for {emp}: {str(e)}")
            continue

    logger.info(f"Started to placing correct_new_mapping of {emps} into {path_new_mapping_sales_corrected_all}")
    try:
        new_mapping_all_df.to_excel(path_new_mapping_sales_corrected_all)
        logger.info(f"Successfully saved corrected mapping to {path_new_mapping_sales_corrected_all}")
    except Exception as e:
        logger.exception(f"Error saving corrected mapping to {path_new_mapping_sales_corrected_all}: {str(e)}")

from src.extraction.clients import init_clientes
from src.extraction.mapping.mapping_clients import init_mapping_clientes
import numpy as np
from src.load.mapping.mapping_clients import load_mapping_clientes_df

def get_new_mapping_cliente(emps):
    for emp in emps:
        logger.info(f"Started to correct new mapping cliente for {emp}")

        src_config = ConfigLoad('end', emp)
        dest_config = ConfigLoad('end', emp)

        try:
            dest_clientes_df = init_clientes(dest_config.input_dir.cargas.carga_company.clients, dest_config.date)
            dest_clientes_df['Origem'] = dest_clientes_df['Origem'].fillna('_outros')
        except Exception as e:
            logger.warning(f'{emp}/exception {e}')
            continue

        try:
            src_mapping_clientes_df = init_mapping_clientes(src_config.input_dir.cargas.carga_company.mapping_client)

            src_origem_index = src_mapping_clientes_df.index.tolist()
            dest_origem_index = dest_clientes_df['Origem'].unique().tolist()

            src_origem_index = [index for index in src_origem_index if index is not np.nan]
            dest_origem_index = [index for index in dest_origem_index if index is not np.nan]

            not_found_origem_index = dest_origem_index
            if src_origem_index:
                not_found_origem_index = [index for index in dest_origem_index
                                                if index.lower() not in [e.lower() for e in src_origem_index]]

            dest_clientes_df['Grupo'] = pd.NA
            not_found_clientes_df = dest_clientes_df[dest_clientes_df['Origem'].isin(not_found_origem_index)].copy()
            dest_mapping_clientes_df = not_found_clientes_df.set_index('Origem')['Grupo']
            dest_mapping_clientes_df = dest_mapping_clientes_df[~dest_mapping_clientes_df.index.duplicated()]
            dest_mapping_clientes_df = pd.concat([src_mapping_clientes_df, dest_mapping_clientes_df])
            
            load_mapping_clientes_df(dest_mapping_clientes_df, dest_config.input_dir.cargas.carga_company.new_mapping_client)
            logger.info(f"Successfully updated client mapping for {emp}")
        except Exception as e:
            logger.exception(f"Error processing client mapping for {emp}: {str(e)}")
            continue

from src.extraction.sales import init_vendas
import datetime
from src.extraction.mapping.mapping_sales import init_mapping_vendas
from src.load.mapping.mapping_sales import load_mapping_vendas_df

def get_new_mapping(emps):
    for emp in emps:
        logger.info(f"Started generating new_mapping_sales for {emp}")

        config_src = ConfigLoad('end', emp)
        config_dest = ConfigLoad('end', emp)

        try:
            dest_vendas_df = init_vendas(config_dest.input_dir.cargas.carga_company.sales, config_dest.date)
 
            dest_vendas_df['Data e hora'] = pd.to_datetime(dest_vendas_df['Data e hora'], errors = 'coerce')
            dest_vendas_df = dest_vendas_df[dest_vendas_df['Data e hora'].dt.date >= config_src.date - datetime.timedelta(days = 180)]

            src_mapping_df = init_mapping_vendas(config_src.input_dir.cargas.carga_company.mapping_sales)
            src_mapping_df = src_mapping_df[~src_mapping_df.index.duplicated(keep = 'first')]

            dest_prod_serv_index = dest_vendas_df['Produto/serviço'].unique().tolist()
            src_prod_serv_index  = src_mapping_df.index.unique().tolist()

            not_found_prod_serv_index = [index for index in dest_prod_serv_index 
                                        if index.lower() not in [e.lower() for e in src_prod_serv_index]]

            not_found_vendas_df = dest_vendas_df[dest_vendas_df['Produto/serviço'].isin(not_found_prod_serv_index)].copy()
            dest_mapping_df = not_found_vendas_df.set_index('Produto/serviço')['Grupo']
            dest_mapping_df = dest_mapping_df[~dest_mapping_df.index.duplicated()]
            dest_mapping_df = pd.concat([src_mapping_df, dest_mapping_df])
            dest_mapping_df = dest_mapping_df.rename(columns = {0: 'grupo_simplesvet'})
            grupo_simplesvet_por_produto_servico = dest_vendas_df.set_index('Produto/serviço').loc[:, 'Grupo']
            grupo_simplesvet_por_produto_servico = grupo_simplesvet_por_produto_servico[~grupo_simplesvet_por_produto_servico.index.duplicated()]

            dest_mapping_df['grupo_simplesvet'] = grupo_simplesvet_por_produto_servico
            load_mapping_vendas_df(dest_mapping_df, config_dest.input_dir.cargas.carga_company.new_mapping_sales)
            logger.info(f"Successfully updated sales mapping for {emp}")
        except Exception as e:
            logger.exception(f"Exception during get_new_mapping for {emp}: {str(e)}")
            continue

from src.transform.data_analysis import get_analysis
from src.transform.data_analysis import copy_carga_files_to_analytic

def do_data_analysis(emps):
    for emp in emps:
        logger.info(f"Started data analysis for {emp}")

        config = ConfigLoad('end', emp)
        try:
            get_analysis(config.input_dir.cargas.carga_company, config.date)
            copy_carga_files_to_analytic(config.input_dir.cargas.carga_company, config.input_dir.analytic)
            logger.info(f"Successfully completed data analysis for {emp}")
        except Exception as e:
            logger.exception(f"Exception during data analysis for {emp}: {str(e)}")

    logger.info(f"Ending data analysis for {emps}")

def gen_template_mapping(emps):
    for emp in emps:
        logger.info(f"Started generating template mapping_sales for {emp}")

        config = ConfigLoad('end', emp)

        sales_mapped_excel_path = config.input_dir.cargas.carga_company.sales_mapped_excel
        grupo_df = (
            pd.read_excel(sales_mapped_excel_path, sheet_name = 'Reagrupa', usecols = ('Descrição', '2ª - Indicador'))
            .rename(columns = {'Descrição': 'Produto/serviço', '2ª - Indicador': 'Grupo'})
        )
        pilar_df = (
            pd.read_excel(sales_mapped_excel_path, sheet_name = 'Pilar', usecols = ('2ª - Indicador', '1ª - Pilar de Negócio'))
            .rename(columns = {'2ª - Indicador': 'Grupo', '1ª - Pilar de Negócio': 'Pilar'})
        )

        categoria_map = {
            "PetShop": "B&T+P&S",
            "Exames": "Clí+",
            "Clínica": "Clí+",
            "Centro Cirurgico": "Clí+",
            "Banho e Tosa": "B&T+P&S",
            "Internação": "Clí+",
        }

        mapping_df = grupo_df.copy()
        mapping_df = mapping_df.set_index('Produto/serviço')
        mapping_df['Pilar'] = mapping_df['Grupo'].map(pilar_df.set_index('Grupo')['Pilar'])
        mapping_df['Categoria'] = mapping_df['Pilar'].map(categoria_map)
        reorganized_mapping_df = mapping_df[['Categoria', 'Pilar', 'Grupo']]
        logger.info(f"Generating the diagnostic for mapping_df: \n\n {reorganized_mapping_df.value_counts(dropna = False)} \n")

        logger.info(f"Started writing mapping_df to {config.input_dir.cargas.carga_company.mapping_sales}")
        mapping_df.to_excel(config.input_dir.cargas.carga_company.mapping_sales)