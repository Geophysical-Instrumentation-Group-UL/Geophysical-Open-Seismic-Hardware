
from PyQt5.QtCore import Qt, QAbstractTableModel, QObject
import json
from PyQt5.QtWidgets import QTableView, QSizePolicy, QHeaderView, QWidget, QItemDelegate, QPushButton, QAbstractItemView, QComboBox
from PyQt5.QtCore import pyqtSignal, pyqtSlot, QModelIndex, QAbstractItemModel
from PyQt5 import QtCore
from PyQt5.QtGui import QPixmap, QIcon
from tools.qtableTools import ComboDelegate, ButtonDelegate
import os
import logging


log = logging.getLogger(__name__)


class ParametersTableModel(QAbstractTableModel):
    s_data_changed = pyqtSignal()

    def __init__(self):
        super(ParametersTableModel, self).__init__()
        self.headerText = ["ageGroup", "Parameter name", "Param 1", "Param 2"]
        self.data = []

    def rowCount(self, parent=None):
        return len(self.data)

    def columnCount(self, parent=None):
        return len(self.headerText)

    def headerData(self, col, orientation, role):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return self.headerText[col]

    def data(self, index, role):
        if role == Qt.DisplayRole or role == Qt.EditRole:
            return self.data[index.row()][index.column()]

    def flags(self, index):
        if not index.isValid():
            return None
        else:
            if index.column() == 1:
                return Qt.ItemIsEnabled | Qt.ItemIsSelectable
            else:
                return Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsEditable

    def setData(self, index, value, role):
        if role == Qt.EditRole or role == Qt.DisplayRole:
            self.data[index.row()][index.column()] = value
            self.dataChanged.emit(index, index)
            self.s_data_changed.emit()
            return True

    def update(self, dataIn):
        self.data = dataIn
        self.beginResetModel()
        self.endResetModel()


class ParametersTableView(QWidget):
    def __init__(self, parent, table_model):
        super(ParametersTableView, self).__init__()
        self.parent = parent
        self.table_view = QTableView(self.parent)
        self.table_model = table_model
        self.table_view.setModel(self.table_model)
        self.setup_table_visuals()
        self.table_view.clicked.connect(self.get_selected_index_on_click)

    def load_data(self, jsonData):
        for parameter in jsonData['[all]'].keys():
            a = [""]
            a.append(parameter)
            for i in range(2):
                try:
                    a.append(jsonData['[all]'][parameter]["p{}".format(i+1)])
                except Exception:
                    a.append("")
            self.add_data_row(a)

    def setup_table_visuals(self):
        self.table_view.setAlternatingRowColors(True)
        self.table_view.setSizePolicy(QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum))

        self.table_view.setEditTriggers(QAbstractItemView.DoubleClicked)

        self.table_view.setSortingEnabled(False)
        self.table_view.verticalHeader().highlightSections()
        self.table_view.verticalHeader().hide()
        self.table_view.setColumnWidth(0, 60)
        self.table_view.setColumnWidth(1, 120)
        self.table_view.setColumnWidth(2, 120)
        self.table_view.setColumnWidth(3, 120)

        self.table_view.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table_view.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.table_view.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)

        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(self.table_view.sizePolicy().hasHeightForWidth())
        self.table_view.setSizePolicy(sizePolicy)

        #self.insert_delete_delegate()
        self.insert_unity_delegate()
        self.table_view.setSelectionBehavior(QAbstractItemView.SelectRows)

    def table_content_changed(self):
        self.table_view.resizeColumnsToContents()

    def add_data_row(self, args):
        actualData = self.table_model.data
        actualData.append(args)
        self.table_model.update(actualData)

    def add_new_row(self):
        actualData = self.table_model.data
        actualData.append(["", "", "", ""])
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
        ageGroup = ["[all]", "[0-9]", "[10-19]", "[20-29]", "[30-39]", "[40-49]",
                    "[50-59]", "[60-69]", "[70-79]", "[80-89]", "[90-99]"]
        comboBox = ComboDelegate(self.table_view, ageGroup, self.table_model)
        self.table_view.setItemDelegateForColumn(0, comboBox)

    @property
    def table_model(self):
        return self._table_model

    @table_model.setter
    def table_model(self, value):
        self._table_model = value
        self.table_view.setModel(value)

    def get_selected_index_on_click(self):
        self.parent.selected_item_index = self.table_view.selectionModel().currentIndex()
        self.parent.set_distribution_type_value()
        self.parent.update_slider_distribution_parameter()
        self.parent.generate_graph_data()


# TODO: manage view and modal interaction (comprehension)
# TODO: change initial json load and keep it modular (isn't hardcoded, will load all param in json)
