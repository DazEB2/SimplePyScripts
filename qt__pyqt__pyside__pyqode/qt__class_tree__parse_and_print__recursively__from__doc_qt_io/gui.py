#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'ipetrash'


from PyQt5 import QtWidgets as qtw
from PyQt5.QtTest import QTest

import time
import requests
from bs4 import BeautifulSoup

from console import get_inherited_children, ROOT_URL


class MainWindow(qtw.QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('qt__class_tree__parse_and_print__recursively__from__doc_qt_io')

        self.tree = qtw.QTreeWidget()
        self.tree.setAlternatingRowColors(True)
        self.tree.setHeaderLabel('NAME')

        self.setCentralWidget(self.tree)

        self.number_total_class = 0

    def _fill_root(self, node: qtw.QTreeWidgetItem, url: str, global_number: int, indent_level=0):
        if global_number > 0 and self.number_total_class >= global_number:
            return

        QTest.qWait(1000)

        indent = '  ' * indent_level

        rs = requests.get(url)
        root = BeautifulSoup(rs.content, 'html.parser')

        name_class = root.select_one('.context > .title').text.split()[0]

        inherited_children = get_inherited_children(url, root)
        number_inherited_children = len(inherited_children)
        if number_inherited_children > 0:
            name_class = '{} ({})'.format(name_class, number_inherited_children)
            print(indent + name_class + ':')
        else:
            print(indent + name_class)

        item = qtw.QTreeWidgetItem([name_class])

        if not node:
            self.tree.addTopLevelItem(item)
        else:
            node.addChild(item)
            node.setExpanded(True)

        self.number_total_class += 1

        for name, url in inherited_children:
            self._fill_root(item, url, global_number, indent_level + 1)

    def fill_tree(self, global_number=-1):
        self.number_total_class = 0
        self.tree.clear()

        t = time.clock()

        self._fill_root(None, ROOT_URL, global_number)

        qtw.QMessageBox.information(
            self,
            'Complete!',
            'Items: {}.\nElapsed: {:.3f} sec'.format(self.number_total_class, time.clock() - t)
        )

    def closeEvent(self, e):
        quit()


if __name__ == '__main__':
    app = qtw.QApplication([])

    w = MainWindow()
    w.resize(500, 500)
    w.show()

    w.fill_tree()

    app.exec()
