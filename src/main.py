from data_analysis import get_import
from webscraping import login

from pathlib import Path
import sys
from PyQt5 import QtWidgets, uic

def run():
    import os

    input_file_import_desejado = Path('data/input/import_desejado.xlsx').resolve()
    input_file_reagrupa = Path('data/input/reagrupa.xlsx').resolve()
    input_file_vendas = Path('data/input/vendas.csv').resolve()
    ui_file = Path('src/gui/firstQtDesigner.ui').resolve()

    app = QtWidgets.QApplication(sys.argv)

    w = uic.loadUi(ui_file)
    w.show()
    w.get_import.clicked.connect(lambda: get_import(input_file_vendas, input_file_reagrupa, input_file_import_desejado))
    w.get_vendas.clicked.connect(lambda: login('williamkennedyg7@gmail.com', '32habbo32'))
    app.exec()

run()