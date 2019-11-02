from PyQt5 import QtWidgets, QtCore
from widgets.spec_fields import AutocapField, StockNumberField
from widgets import message_boxes
from utils import utils_collection as utils
from utils import db_manager
from utils.styling import generic_title_style


class CreateComponentDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(CreateComponentDialog, self).__init__(parent)
        self.setWindowFlags(
            QtCore.Qt.Dialog
            | QtCore.Qt.CustomizeWindowHint
            | QtCore.Qt.WindowCloseButtonHint
        )

        title = QtWidgets.QLabel("Crear componente")
        title.setAlignment(QtCore.Qt.AlignCenter)
        title.setStyleSheet(generic_title_style)

        self.compname_field = AutocapField("Componente a crear...")
        self.compname_field.setFixedWidth(150)
        self.compname_field.setFocus()

        self.initstock_field = StockNumberField("Stock inicial...")
        self.initstock_field.setFixedWidth(80)

        back_button = QtWidgets.QPushButton("« Volver")
        back_button.setShortcut("Alt+v")

        self.execute_button = QtWidgets.QPushButton("Ejecutar »")
        self.execute_button.setDefault(True)

        line_edits_layout = QtWidgets.QHBoxLayout()
        line_edits_layout.addWidget(self.compname_field)
        line_edits_layout.addWidget(self.initstock_field)

        bottom_section = QtWidgets.QHBoxLayout()
        bottom_section.addWidget(back_button)
        bottom_section.addWidget(self.execute_button)

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(title)
        layout.addLayout(line_edits_layout)
        layout.addLayout(bottom_section)

        self.setLayout(layout)

        back_button.clicked.connect(self.close)
        self.execute_button.clicked.connect(self.create_component)

    def create_component(self):
        if self.compname_field.text() == "":
            message_boxes.WarningBox(
                "Sin nombre", "Dar nombre al componente\nantes de ejecutar."
            ).exec_()
            self.compname_field.setFocus()
            return

        db = db_manager.DB_Manager()
        component_names_display = db.get_all_display_names_for_components()

        if self.compname_field.text() in component_names_display:
            message_boxes.WarningBox(
                "Nombre ya existente",
                "El nombre tiene que ser\ndiferente de los existentes.",
            ).exec_()
            self.compname_field.clear()
            self.compname_field.setFocus()
            return

        newcomp_display_name = self.compname_field.text()
        newcomp_sql_name = utils.format_display_name_into_sql_name(newcomp_display_name)

        initstock = 0
        if self.initstock_field.text() != "":
            initstock = utils.format_number_for_calculation(self.initstock_field.text())

        db.create_new_component(newcomp_sql_name, newcomp_display_name, initstock)
        db.log_new_config_record(
            config="Creación de componente", details=newcomp_display_name
        )
        db.close_connection()

        admin_window = self.parent().parent().parent()
        admin_window.statusbar.show_quick_message(
            "Componente creado: " + newcomp_display_name
        )
        admin_window.start_screen.rebuild_main_section()

        QtWidgets.QApplication.processEvents()  # enables scrolling
        table = admin_window.start_screen.main_section.table
        utils.scroll_to_row_in_table(table, newcomp_display_name)

        self.compname_field.clear()
        self.initstock_field.clear()
        self.close()
