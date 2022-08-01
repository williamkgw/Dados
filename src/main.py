from data_analysis import get_import_csv
from webscraping import login

import sys
from PyQt5 import QtWidgets, uic

def run():

    app = QtWidgets.QApplication(sys.argv)

    w = uic.loadUi('src//gui//firstQtDesigner.ui')
    w.show()
    w.get_import.clicked.connect(lambda: get_import_csv())
    w.get_vendas.clicked.connect(lambda: login('williamkennedyg7@gmail.com', '32habbo32'))
    app.exec()

run()