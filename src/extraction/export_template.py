import pandas as pd

def get_from_export_template_necessary_cols():
    export_template = {
        "is_necessary":{
            "ID do Item":True,
            "Mês":True,
            "Ano":True,
            "Medição":True,
            "Fx Verde Inf/Previsto":True,
            "Fx Verde Sup":True,
            "Fx Vermelha Inf":True,
            "Fx Vermelha Sup":True,
            "Fx Cliente Inf":True,
            "Fx Cliente Sup":True,
            "Item":True,
            "Indicador":True,
            "Usuário":True,
            "Tipo":True,
            "Auxiliar":True,
            "Totalizado":True,
            "Medido":True,
            "Calendário":True
        }
    }

    df = pd.DataFrame(export_template)
    is_column_necessary_df = df[df['is_necessary']]
    return tuple(is_column_necessary_df.index)

def init_export_template(path_export_emplate):
    export_template_necessary_columns = get_from_export_template_necessary_cols()
    import_df = pd.read_excel(path_export_emplate, index_col = 'ID do Item', usecols = export_template_necessary_columns)
    import_df['Medição'] = pd.NA
    return import_df