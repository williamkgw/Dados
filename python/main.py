from io_excel import read_excel

filedir = 'data/excel_input/'
filename = 'reagrupa.xlsx'

filepath = filedir + filename

df = read_excel(filepath, range_index='C1:C813',range_column='A1:C1', range_data='A1:C813')


print(df)
