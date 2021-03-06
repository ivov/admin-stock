from datetime import datetime
import os
from pandas import ExcelWriter
from PyQt5 import QtWidgets, QtGui, QtCore
from widgets.spec_fields import AutocapField
from widgets.dialogs.date_selection_subdialog import DateSelectionSubdialog
from widgets.message_boxes import QuestionBox
from utils import db_manager
from utils import utils_collection as utils
from utils.styling import (
    movements_dialog_title_style,
    generic_groupbox_normal_style,
    movements_dialog_groupbox_filter_selected_style,
    movements_dialog_table_view_style,
)


class MovementsDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(MovementsDialog, self).__init__(parent)
        self.setWindowFlags(
            QtCore.Qt.Dialog
            | QtCore.Qt.CustomizeWindowHint
            | QtCore.Qt.WindowCloseButtonHint
        )
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setFixedWidth(800)
        self.setFixedHeight(403)

        self.df = ""

        self.title = QtWidgets.QLabel("Historial de movimientos")
        self.title.setStyleSheet(movements_dialog_title_style)
        self.title.setAlignment(QtCore.Qt.AlignCenter)

        self.groupbox = QtWidgets.QGroupBox("Filtros")
        self.groupbox.setStyleSheet(generic_groupbox_normal_style)
        self.groupbox.setMinimumWidth(400)

        self.date_button = QtWidgets.QPushButton("Período")
        self.date_button.setMaximumHeight(22)
        self.date_button.setFocusPolicy(QtCore.Qt.NoFocus)

        self.mov_combobox = QtWidgets.QComboBox()
        self.mov_combobox.addItem("Movimiento")
        self.mov_combobox.addItem("Ingreso")
        self.mov_combobox.addItem("Egreso")
        self.mov_combobox.setFixedWidth(85)

        self.comp_field = AutocapField("Componente...")
        self.comp_field.setFixedWidth(300)
        self.comp_field.set_completer(source="comps in movements")
        self.comp_field.setFocus()
        self.dest_combobox = QtWidgets.QComboBox()
        self.dest_combobox.addItem("Destino")

        destinations = ["Depósito", "Karina", "Brid", "Tercero", "Uso interno"]

        for destination in destinations:
            self.dest_combobox.addItem(destination)

        self.user_combobox = QtWidgets.QComboBox()
        self.user_combobox.addItem("Usuario")

        self.db = db_manager.DB_Manager()

        users = self.db.get_all_admin_users()
        for user in users:
            self.user_combobox.addItem(user)

        self.user_combobox.setFixedWidth(100)

        filters_layout = QtWidgets.QHBoxLayout()
        filters_layout.addWidget(self.date_button)
        filters_layout.addWidget(self.mov_combobox)
        filters_layout.addWidget(self.comp_field)
        filters_layout.addWidget(self.dest_combobox)
        filters_layout.addWidget(self.user_combobox)

        groupbox_inner_section = QtWidgets.QVBoxLayout()
        groupbox_inner_section.addLayout(filters_layout)
        self.groupbox.setLayout(groupbox_inner_section)
        groupbox_section = QtWidgets.QHBoxLayout()
        groupbox_section.addStretch()
        groupbox_section.addWidget(self.groupbox)
        groupbox_section.addStretch()

        back_button = QtWidgets.QPushButton("« Volver")
        back_button.setShortcut("Alt+v")
        back_button.setFocusPolicy(QtCore.Qt.NoFocus)

        self.delete_button = QtWidgets.QPushButton("× Borrar historial")
        self.delete_button.setShortcut("Alt+b")
        self.delete_button.setFocusPolicy(QtCore.Qt.NoFocus)

        self.export_button = QtWidgets.QPushButton("Exportar historial »")
        self.export_button.setShortcut("Alt+x")
        self.export_button.setFocusPolicy(QtCore.Qt.NoFocus)

        bottom_section = QtWidgets.QHBoxLayout()
        bottom_section.addWidget(back_button)
        bottom_section.addWidget(self.delete_button)
        bottom_section.addWidget(self.export_button)

        table_layout = QtWidgets.QVBoxLayout()

        self.table_view = QtWidgets.QTableView()
        self.table_view.verticalHeader().setVisible(False)

        table_layout.addWidget(self.table_view)
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.title)
        layout.addLayout(groupbox_section)
        layout.addLayout(table_layout)
        layout.addLayout(bottom_section)

        self.setLayout(layout)

        self.build_table_view()

        back_button.clicked.connect(self.close)
        self.delete_button.clicked.connect(self.delete_movements)
        self.export_button.clicked.connect(self.export_to_spreadsheet)
        self.date_button.clicked.connect(self.create_date_selection_subdialog)
        self.comp_field.returnPressed.connect(self.on_comp_field_return_press)
        self.mov_combobox.currentIndexChanged.connect(self.on_combobox_change)
        self.dest_combobox.currentIndexChanged.connect(self.on_combobox_change)
        self.user_combobox.currentIndexChanged.connect(self.on_combobox_change)

    def create_date_selection_subdialog(self):
        self.date_selection_subdialog = DateSelectionSubdialog(self)
        self.date_selection_subdialog.exec_()

    def build_table_view(self):
        self.df = self.db.get_movements_as_dataframe()
        self.db.close_connection()

        widgets = [
            self.delete_button,
            self.export_button,
            self.date_button,
            self.mov_combobox,
            self.dest_combobox,
            self.user_combobox,
            self.comp_field,
        ]
        if self.df.empty:
            for i in widgets:
                i.setDisabled(True)
            return

        row_count = len(self.df.index)
        col_count = len(self.df.columns)

        self.model = QtGui.QStandardItemModel(row_count, col_count)
        self.model.setHorizontalHeaderLabels(self.df.columns)
        self.table_view.setModel(self.model)

        for count, df_col_name in enumerate(self.df):
            utils.populate_model_column_with_list_of_items(
                model=self.model, col_num=count, input_list=self.df[df_col_name]
            )

        text_and_color = {
            "Ingreso": QtGui.QColor("#a3be8c"),
            "Egreso": QtGui.QColor("#ff91a4"),
        }

        for text, color in text_and_color.items():
            for x in range(self.model.rowCount()):
                for y in range(self.model.columnCount()):
                    if self.model.item(x, 2).text() == text:
                        self.model.item(x, y).setBackground(color)

        self.table_view.setColumnWidth(0, 95)
        self.table_view.setColumnWidth(1, 65)
        self.table_view.horizontalHeader().setSectionResizeMode(
            3, QtWidgets.QHeaderView.Stretch
        )
        self.table_view.setColumnWidth(2, 90)
        self.table_view.setColumnWidth(4, 80)
        self.table_view.setColumnWidth(5, 120)
        self.table_view.setColumnWidth(6, 100)
        self.table_view.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)
        self.table_view.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.table_view.setFocusPolicy(QtCore.Qt.NoFocus)
        self.table_view.setStyleSheet(movements_dialog_table_view_style)

    def clear_all_filters(self):
        self.date_button.setText("Período")
        self.comp_field.clear()
        self.mov_combobox.setCurrentIndex(0)
        self.dest_combobox.setCurrentIndex(0)
        self.user_combobox.setCurrentIndex(0)
        self.table_view.setModel(self.model)
        self.groupbox.setTitle("Filtros")
        self.groupbox.setStyleSheet(generic_groupbox_normal_style)

    def clear_all_filters_except(self, chosen_filter):
        comboboxes = [self.mov_combobox, self.dest_combobox, self.user_combobox]

        if isinstance(chosen_filter, QtWidgets.QComboBox):
            self.date_button.setText("Período")
            self.comp_field.clear()
            for i in comboboxes:
                if i != chosen_filter:
                    i.setCurrentIndex(0)
        elif isinstance(chosen_filter, QtWidgets.QLineEdit):
            self.date_button.setText("Período")
            for i in comboboxes:
                i.setCurrentIndex(0)
        elif isinstance(chosen_filter, QtWidgets.QPushButton):
            self.comp_field.clear()
            for i in comboboxes:
                i.setCurrentIndex(0)

    def apply_filter_based_on_item(self, chosen_filter, chosen_item):
        filter_proxy_model = self.get_filter_proxy_model(chosen_filter)
        filter_proxy_model.setSourceModel(self.model)
        filter_proxy_model.setFilterFixedString(chosen_item)
        self.table_view.setModel(filter_proxy_model)
        self.groupbox.setTitle("Filtro activado")
        self.groupbox.setStyleSheet(movements_dialog_groupbox_filter_selected_style)

    def get_filter_proxy_model(self, chosen_filter):
        filter_proxy_model = QtCore.QSortFilterProxyModel()
        if chosen_filter in ("Movimiento", "Destino", "Usuario"):
            filter_and_column = {"Movimiento": 2, "Destino": 5, "Usuario": 6}
            filter_proxy_model.setFilterKeyColumn(filter_and_column[chosen_filter])
        elif chosen_filter == "Componente":
            filter_proxy_model.setFilterRegExp(QtCore.QRegExp(self.comp_field.text()))
            filter_proxy_model.setFilterKeyColumn(3)
        return filter_proxy_model

    def on_combobox_change(self):
        combobox = self.sender()
        chosen_filter = combobox.itemText(0)
        chosen_item = combobox.currentText()
        self.clear_all_filters_except(combobox)
        if chosen_item in ("Movimiento", "Destino", "Usuario"):
            self.clear_all_filters()
        else:
            self.apply_filter_based_on_item(chosen_filter, chosen_item)

    def on_comp_field_return_press(self):
        user_input = self.comp_field.text()
        self.clear_all_filters_except(self.comp_field)
        if not user_input:
            self.clear_all_filters()
        elif user_input:
            self.apply_filter_based_on_item("Componente", user_input)

    def on_date_selected(self):
        selected_date = self.date_selection_subdialog.selected_date
        self.date_button.setText(selected_date)
        self.clear_all_filters_except(self.date_button)
        self.apply_filter_based_on_item("Fecha", selected_date)

    def delete_movements(self):
        box = QuestionBox("Confirmación", "¿Borrar historial de movimientos?")
        box.exec_()
        if box.clickedButton() == box.button(QtWidgets.QMessageBox.Yes):
            db = db_manager.DB_Manager()
            db.delete_all_movements()
            db.close_connection()
            self.close()
            statusbar = self.parent().parent().parent().parent().statusbar
            statusbar.show_quick_message("Historial de movimientos borrado")
        elif box.clickedButton() == box.button(QtWidgets.QMessageBox.No):
            pass

    def export_to_spreadsheet(self):
        self.export_button.setText("Esperar...")
        current_date = datetime.now().strftime("%d-%m-%Y")
        filepath_and_name = f"output\\Historial de movimientos {current_date}.xlsx"
        writer = ExcelWriter(filepath_and_name)
        self.df.to_excel(writer, "Hoja1", index=False)
        writer.sheets["Hoja1"].column_dimensions["A"].width = 13
        writer.sheets["Hoja1"].column_dimensions["B"].width = 8
        writer.sheets["Hoja1"].column_dimensions["C"].width = 15
        writer.sheets["Hoja1"].column_dimensions["D"].width = 30
        writer.sheets["Hoja1"].column_dimensions["E"].width = 10
        writer.sheets["Hoja1"].column_dimensions["F"].width = 15
        writer.sheets["Hoja1"].column_dimensions["G"].width = 15
        writer.save()
        os.startfile(filepath_and_name)

        self.export_button.setText("Exportar historial »")

        self.close()

        statusbar = self.parent().parent().parent().parent().statusbar
        statusbar.show_quick_message("Historial de movimientos exportado")
