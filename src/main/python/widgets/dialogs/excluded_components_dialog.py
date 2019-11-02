from PyQt5 import QtWidgets, QtCore
from utils import utils_collection as utils
from utils import db_manager
from utils.styling import excluded_dialog_title_style, excluded_dialog_subtitle_style


class ExcludedCompsDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(ExcludedCompsDialog, self).__init__(parent)
        self.setWindowFlags(
            QtCore.Qt.Dialog
            | QtCore.Qt.CustomizeWindowHint
            | QtCore.Qt.WindowCloseButtonHint
        )
        self.setFixedWidth(200)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)

        self.settings = QtCore.QSettings("solutronic", "admin_stock")

        layout = QtWidgets.QVBoxLayout()

        checkbox_layout = QtWidgets.QVBoxLayout()
        checkbox_layout.setAlignment(QtCore.Qt.AlignCenter)

        title = QtWidgets.QLabel("Componentes excluidos")
        subtitle = QtWidgets.QLabel("Componentes no integrados\na ninguna receta:")
        title.setAlignment(QtCore.Qt.AlignCenter)
        title.setStyleSheet(excluded_dialog_title_style)
        subtitle.setAlignment(QtCore.Qt.AlignCenter)
        subtitle.setStyleSheet(excluded_dialog_subtitle_style)

        self.checkbox = QtWidgets.QCheckBox("Resaltar excluidos en amarillo")

        if self.settings.value("excluded_checkbox") == "on":
            self.checkbox.setChecked(True)

        db = db_manager.DB_Manager()
        self.unused_components = db.get_components_not_in_use()
        db.close_connection()

        unused_components_string = ""
        for i in self.unused_components:
            unused_components_string += f"• {i}\n"

        if not self.unused_components:
            unused_components_string = "No hay excluidos."

        excluded_data = QtWidgets.QLabel(unused_components_string)
        excluded_data.setAlignment(QtCore.Qt.AlignCenter)

        checkbox_layout.addWidget(self.checkbox)

        self.back_button = QtWidgets.QPushButton("« Volver")
        self.back_button.setShortcut("Alt+v")
        self.back_button.setDefault(True)

        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addWidget(excluded_data)
        layout.addLayout(checkbox_layout)
        layout.addWidget(self.back_button)

        self.setLayout(layout)

        self.back_button.clicked.connect(self.close)
        self.checkbox.clicked.connect(self.on_checkbox_checked)

    def on_checkbox_checked(self):
        update = ""
        number_of_excluded_comps = len(self.unused_components)
        endstring = (
            "componente excluido"
            if number_of_excluded_comps == 1
            else "componentes excluidos"
        )
        number_of_excluded_comps_string = (
            str(number_of_excluded_comps) + " " + endstring
        )
        if self.checkbox.isChecked():
            self.settings.setValue("excluded_checkbox", "on")
            update = "Activado de excluidos"
        elif not self.checkbox.isChecked():
            self.settings.setValue("excluded_checkbox", "off")
            update = "Desactivado de excluidos"

        db = db_manager.DB_Manager()
        db.log_new_config_record(config=update, details=number_of_excluded_comps_string)
        db.close_connection()
        self.set_excluded_state_at_parent_and_recolor()

    def set_excluded_state_at_parent_and_recolor(self):
        main_section = self.parent()
        excluded_state = self.settings.value("excluded_checkbox")
        utils.color_criticals_in_orange_in_main_section(
            main_section.table, main_section.stored_criticals
        )
        utils.color_zeros_in_grey_in_main_section(
            main_section.table, main_section.stored_criticals
        )
        utils.color_excluded_in_yellow_in_main_section(
            main_section.table, excluded_state, main_section.unused_comps
        )
