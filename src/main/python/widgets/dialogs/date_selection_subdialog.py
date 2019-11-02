from PyQt5 import QtWidgets, QtCore
from utils.styling import movements_dialog_date_selection_subdialog_style
from utils import db_manager
from utils import utils_collection as utils


class DateSelectionSubdialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(DateSelectionSubdialog, self).__init__(parent)
        self.setWindowFlags(
            QtCore.Qt.Dialog
            | QtCore.Qt.CustomizeWindowHint
            | QtCore.Qt.WindowCloseButtonHint
        )
        self.setFixedWidth(270)

        self.selected_date = ""

        groupbox = QtWidgets.QGroupBox("Período")
        groupbox.setStyleSheet(movements_dialog_date_selection_subdialog_style)

        self.combobox_month = QtWidgets.QComboBox()
        self.combobox_month.setFixedWidth(85)
        self.combobox_month.addItem("Mes")

        months = [
            "Enero",
            "Febrero",
            "Marzo",
            "Abril",
            "Mayo",
            "Junio",
            "Julio",
            "Agosto",
            "Septiembre",
            "Octubre",
            "Noviembre",
            "Diciembre",
        ]

        for i in months:
            self.combobox_month.addItem(i)

        self.combobox_year = QtWidgets.QComboBox()
        self.combobox_year.addItem("Año")
        self.combobox_year.setFixedWidth(85)

        years = []
        db = db_manager.DB_Manager()
        if self.parent().title.text() == "Historial de movimientos":
            years = db.get_years_from_movements()
        elif self.parent().title.text() == "Historial de configuraciones":
            years = db.get_years_from_configs()
        for i in years:
            self.combobox_year.addItem(i)

        combobox_layout = QtWidgets.QHBoxLayout()
        combobox_layout.addWidget(self.combobox_month)
        combobox_layout.addWidget(self.combobox_year)

        groupbox_inner_layout = QtWidgets.QVBoxLayout()
        groupbox_inner_layout.addLayout(combobox_layout)
        groupbox.setLayout(groupbox_inner_layout)

        self.back_button = QtWidgets.QPushButton("« Volver")
        self.back_button.setShortcut("Alt+v")

        if self.parent().date_button.text() != "Período":
            self.back_button.setText("× Cancelar")
            self.back_button.setShortcut("Alt+c")

        self.select_button = QtWidgets.QPushButton("Seleccionar »")
        self.select_button.setShortcut("Alt+s")
        self.select_button.setEnabled(False)

        bottom_section = QtWidgets.QHBoxLayout()
        bottom_section.addWidget(self.back_button)
        bottom_section.addWidget(self.select_button)

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(groupbox)
        layout.addLayout(bottom_section)

        self.setLayout(layout)

        self.back_button.clicked.connect(self.on_back)
        self.select_button.clicked.connect(self.on_select_button_clicked)
        self.combobox_month.currentTextChanged.connect(self.on_combobox_change)
        self.combobox_year.currentTextChanged.connect(self.on_combobox_change)

    def on_combobox_change(self):
        if self.combobox_month.currentText() == "Mes":
            return
        if self.combobox_year.currentText() == "Año":
            return
        self.select_button.setEnabled(True)

    def on_select_button_clicked(self):
        self.selected_date = (
            utils.get_month_number(self.combobox_month.currentText())
            + "/"
            + self.combobox_year.currentText()
        )
        self.parent().on_date_selected()
        self.close()

    def on_back(self):
        if self.back_button.text() == "« Volver":
            self.close()
        elif self.back_button.text() == "× Cancelar":
            self.parent().clear_all_filters()
            self.close()
