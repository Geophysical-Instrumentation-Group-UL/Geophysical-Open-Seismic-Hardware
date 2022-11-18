from PyQt5.QtWidgets import QTableView, QSizePolicy, QHeaderView, QWidget, QItemDelegate, QPushButton, QAbstractItemView, QComboBox, QApplication, QStyle, QStyleOptionComboBox
from PyQt5.QtCore import pyqtSignal, pyqtSlot
from PyQt5 import QtCore, Qt
from PyQt5.QtGui import QPixmap, QIcon

import os
import logging

log = logging.getLogger(__name__)


class AbstractTableView(QWidget):

    def __init__(self, parent, table_model):
        super(AbstractTableView, self).__init__()
        self.table_view = QTableView(parent)
        self.table_model = table_model
        self.table_view.setModel(self.table_model)
        self.setup_table_visuals()

    def setup_table_visuals(self):
        self.table_view.setStyleSheet(''' ''')

        self.table_view.setAlternatingRowColors(True)
        self.table_view.setSizePolicy(QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum))

        self.table_view.setEditTriggers(QAbstractItemView.NoEditTriggers |
                             QAbstractItemView.AllEditTriggers)

        self.table_view.setSortingEnabled(False)
        self.table_view.verticalHeader().highlightSections()
        self.table_view.verticalHeader().hide()
        self.table_view.setColumnWidth(0, 120)
        self.table_view.setColumnWidth(1, 40)
        self.table_view.setColumnWidth(2, 80)
        self.table_view.setColumnWidth(3, 80)
        self.table_view.setColumnWidth(4, 80)
        self.table_view.setColumnWidth(5, 120)
        self.table_view.setColumnWidth(6, 40)

        self.table_view.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        # self.table_view.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        # self.table_view.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        # self.table_view.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        # self.table_view.horizontalHeader().setSectionResizeMode(4, QHeaderView.Stretch)
        self.table_view.horizontalHeader().setSectionResizeMode(5, QHeaderView.Stretch)
        # self.table_view.horizontalHeader().setSectionResizeMode(6, QHeaderView.Stretch)

        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(self.table_view.sizePolicy().hasHeightForWidth())
        self.table_view.setSizePolicy(sizePolicy)

        self.insert_delete_delegate()
        self.insert_unity_delegate()

    def table_content_changed(self):
        self.table_view.resizeColumnsToContents()

    def add_new_row(self):
        actualData = self.table_model.data
        actualData.append(["", "", "", "", "", "", ""])
        self.table_model.update(actualData)

    def insert_delete_delegate(self):
        button = ButtonDelegate(self.table_view)
        self.table_view.setItemDelegateForColumn(self._table_model.columnCount() - 1, button)
        button.s_button.connect(self.delete_button_clicked)

    def delete_button_clicked(self, row):
        actualData = self.table_model.data
        actualData.pop(row)
        self.table_model.update(actualData)

    def insert_unity_delegate(self):
        self.comboBox = ComboDelegate(self.table_view, ["EACH", "FT", "IN", "METER", "LITER"], self.table_model)
        self.table_view.setItemDelegateForColumn(self.table_model.columnCount() - 4, self.comboBox)

    @property
    def table_model(self):
        return self._table_model
    @table_model.setter
    def table_model(self, value):
        self._table_model = value
        self.table_view.setModel(value)


class ButtonDelegate(QItemDelegate):
    s_button = pyqtSignal(int)

    def __init__(self, parent):
        super(ButtonDelegate, self).__init__(parent)
        self.was_clicked = False
        self.button = None
        self.image = QPixmap(os.path.dirname(os.path.realpath(__file__))+"\\..\\images\\trash_bin.png")
        self.icon = QIcon(self.image)

    def paint(self, painter, option, index):
        if not self.parent().indexWidget(index):
            a = index.data()
            self.button = QPushButton(str(index.data()), self.parent(), clicked=self.cellButtonClicked)
            self.button.setIcon(self.icon)
            self.parent().setIndexWidget(index, self.button)

    def createEditor(self, parent, option, index):
        button = QPushButton(str(index.data()), parent)
        button.clicked.connect(self.cellButtonClicked)
        return button

    def setEditorData(self, editor, index):
        editor.blockSignals(True)
        # editor.setCurrentIndex(int(index.model().data(index)))
        editor.blockSignals(False)

    def setModelData(self, editor, model, index):
        if self.was_clicked:
            self.s_button.emit(index.row())
            self.was_clicked = False

    @pyqtSlot()
    def cellButtonClicked(self, index):
        self.was_clicked = True
        self.commitData.emit(self.sender())


# class ComboDelegate(QItemDelegate):
#
#     def __init__(self, parent, items, model):
#         super(ComboDelegate, self).__init__(parent)
#         self.combo = None
#         self.tableModel = model
#         self.items = items
#         self.oldData = ""
#
#     # def paint(self, painter, option, index):
#     #     #super(ComboDelegate, self).paint(painter, option, index)
#     #     if not self.parent().indexWidget(index):
#     #         self.combo = QComboBox(self.parent())
#     #         self.combo.addItems(self.items)
#     #         self.combo.setCurrentText(self.tableModel.data[index.row()][index.column()])
#     #         print("\nCREATING:\n" + self.combo.currentText() + "\n")
#     #
#     #         self.setData(index, self.combo.currentText(), Qt.DisplayRole)
#     #         self.parent().setIndexWidget(index, self.combo)
#     #     else:
#     #         print("\nHOLDING:\n" + self.combo.currentText() + "\n" + "ROW:" + index.row() + "\n" + "COL:" + index.column())
#     #         self.setData(index, self.combo.currentText(), Qt.DisplayRole)
#
#     def createEditor(self, parent, option, index):
#         combo = QComboBox(parent)
#         combo.addItems(self.items)
#         combo.setEditable(True)
#         combo.currentIndexChanged.connect(self.currentIndexChanged)
#         return combo
#
#     @QtCore.pyqtSlot()
#     def currentIndexChanged(self):
#         self.commitData.emit(self.sender())
#
#     def setData(self, index, value, role=QtCore.Qt.DisplayRole):
#         print("setData", index.row(), index.column(), value)
#         self.tableModel.setData(index, value, role)
#         print(self.tableModel.data)

class ComboDelegate(QItemDelegate):

    def __init__(self, parent, items, model):
        super(ComboDelegate, self).__init__(parent)
        self.combo = None
        self.items = items
        self.tableModel = model
        self.oldData = ""

    def createEditor(self, parent, options, index):
        self.combo = QComboBox(parent)
        self.combo.addItems(self.items)
        self.combo.setEditable(True)
        self.combo.setCurrentIndex(0)
        self.combo.currentData(QtCore.Qt.DisplayRole)
        self.combo.lineEdit().setReadOnly(True)
        self.combo.currentIndexChanged.connect(self.currentIndexChanged)
        return self.combo

    def setModelData(self, editor, model, index):
        model.setData(index, editor.currentText(), QtCore.Qt.DisplayRole)

    @QtCore.pyqtSlot()
    def currentIndexChanged(self):
        self.commitData.emit(self.sender())

    def setData(self, index, value, role=QtCore.Qt.DisplayRole):
        print("setData", index.row(), index.column(), value)
        self.tableModel.setData(index, value, role)
        print(self.tableModel.data)
