import pandas as pd
import re
from xlsxwriter.utility import xl_cell_to_rowcol

def cell_range(range):
    regex_rule = '(.+):(.+)'

    cell_list = re.split(regex_rule, range)[1:-1]

    return cell_list

def count_row_or_col_range(range, row_or_column):
    array_range = cell_range(range)

    (row_begin, col_begin) = xl_cell_to_rowcol(array_range[0])
    (row_end, col_end) = xl_cell_to_rowcol(array_range[1])

    if row_or_column.casefold() == 'row':
        return row_end - row_begin
    elif row_or_column.casefold() == 'column':
        return col_end - col_begin
    else:
        return -1

def get_row_or_col_array(range, row_or_column):

    array_range = cell_range(range)

    (row, col) = xl_cell_to_rowcol(array_range[0])

    if row_or_column.casefold() == 'row':
        return row
    elif row_or_column.casefold() == 'column':
        return col
    else:
        return -1

def get_pd_usecols(range):

    regex_rule = '\d'
    s = re.sub(regex_rule, '', range)

    return s

def read_excel(filepath, range_index = None, range_column = None, range_data = None):

    _index_col, _header, _usecols = None,None,None

    if range_index is not None:
        _index_col = get_row_or_col_array(range_index, 'column')
        print(_index_col)

    if range_column is not None:
        _header = get_row_or_col_array(range_column, 'row')
        print(_header)

    if range_data is not None:
        _usecols = get_pd_usecols(range_data)
        print(_usecols)


    df = pd.read_excel( filepath,
                        index_col = _index_col,
                        header = _header,
                        usecols = _usecols
    )

    return df
