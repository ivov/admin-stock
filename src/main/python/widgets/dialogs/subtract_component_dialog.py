from PyQt5 import QtWidgets, QtGui, QtCore
from widgets.line_item_close_button import LineItemCloseButton
from widgets.spec_fields import AutocapField, StockNumberField
from widgets.message_boxes import WarningBox
from utils.styling import (
    generic_title_style,
    generic_groupbox_normal_style,
    generic_messagebox_style,
)
from utils import utils_collection as utils
from utils import db_manager
from utils import tests


class SubtractComponentDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(SubtractComponentDialog, self).__init__(parent)

        self.setWindowFlags(
            QtCore.Qt.Dialog
            | QtCore.Qt.CustomizeWindowHint
            | QtCore.Qt.WindowCloseButtonHint
        )
        self.setFixedWidth(410)

        self.final_dialog_data = {}

        title = QtWidgets.QLabel("Egreso a uso interno")
        title.setAlignment(QtCore.Qt.AlignCenter)
        title.setStyleSheet(generic_title_style)

        bottom_section = QtWidgets.QHBoxLayout()
        back_button = QtWidgets.QPushButton("« Volver")
        back_button.setShortcut("Alt+v")

        execute_button = QtWidgets.QPushButton("Ejecutar »")
        execute_button.setShortcut("Alt+e")
        execute_button.setDefault(True)

        bottom_section.addWidget(back_button)
        bottom_section.addWidget(execute_button)

        groupbox = QtWidgets.QGroupBox("Componentes a restar")
        groupbox.setStyleSheet(generic_groupbox_normal_style)
        groupbox.setMinimumWidth(333)

        add_component_button = QtWidgets.QPushButton("+ Agregar componente")
        add_component_button.setShortcut("Alt+a")

        self.comps_holder_section = QtWidgets.QVBoxLayout()

        groupbox_inner_section = QtWidgets.QVBoxLayout()
        groupbox_inner_section_1 = QtWidgets.QHBoxLayout()
        groupbox_inner_section_1.addWidget(add_component_button)
        groupbox_inner_section_2 = QtWidgets.QHBoxLayout()
        groupbox_inner_section_2.addLayout(self.comps_holder_section)
        groupbox_inner_section.addLayout(groupbox_inner_section_1)
        groupbox_inner_section.addLayout(groupbox_inner_section_2)
        groupbox.setLayout(groupbox_inner_section)
        groupbox_section = QtWidgets.QHBoxLayout()
        groupbox_section.addStretch()
        groupbox_section.addWidget(groupbox)
        groupbox_section.addStretch()

        layout = QtWidgets.QVBoxLayout()
        layout.setSizeConstraint(QtWidgets.QLayout.SetFixedSize)
        layout.addWidget(title)
        layout.addLayout(groupbox_section)
        layout.addLayout(bottom_section)

        self.setLayout(layout)

        back_button.clicked.connect(self.close)
        add_component_button.clicked.connect(self.add_line)
        execute_button.clicked.connect(self.execute_subtract_comps)

    def add_line(self):
        single_line_section = QtWidgets.QHBoxLayout()

        component_field = AutocapField("Componente...")
        component_field.setFixedWidth(200)
        component_field.setFocus()
        component_field.set_completer(source="comps in stock")

        value_field = StockNumberField("Cantidad...")
        value_field.setFixedWidth(80)

        close_button = LineItemCloseButton(holder=self.comps_holder_section)

        single_line_section.addWidget(component_field)
        single_line_section.addWidget(value_field)
        single_line_section.addWidget(close_button)

        self.comps_holder_section.addLayout(single_line_section)

    def execute_subtract_comps(self):
        for i in [
            self.test_if_there_are_no_components,
            self.test_if_there_are_duplicates,
            self.test_if_there_are_empty_fields,
            self.test_if_there_are_unrecognized_components,
        ]:
            if i():
                return

        self.insert_subtraction_comps_into_db()

    def test_if_there_are_no_components(self):
        no_line_items = not self.comps_holder_section.children()
        contents = utils.get_line_items_contents(self.comps_holder_section)
        empty_string = tests.test_if_empty_string_in_line_items_contents(contents)
        if no_line_items or empty_string:
            WarningBox(
                "Sin componentes",
                "Completar o borrar campos\nvacíos antes de ejecutar.",
            ).exec_()
            return True
        else:
            return False

    def test_if_there_are_duplicates(self):
        contents = utils.get_line_items_contents(self.comps_holder_section)
        duplicates = tests.test_if_duplicated_first_value_in_line_items_contents(
            contents
        )
        if duplicates:
            WarningBox(
                "Componentes duplicados", "Borrar uno de los componentes duplicados."
            ).exec_()
            return True
        else:
            return False

    def test_if_there_are_empty_fields(self):
        contents = utils.get_line_items_contents(self.comps_holder_section)
        if not all(contents):
            return self.autoremove_line()
        else:
            return False

    def test_if_there_are_unrecognized_components(self):
        contents = utils.get_line_items_contents(self.comps_holder_section)
        incoming_comps = contents[0::2]
        db = db_manager.DB_Manager()
        existing_comps = db.get_all_display_names_for_components()
        db.close_connection()
        unrecognized_comps = not set(incoming_comps).issubset(existing_comps)
        if unrecognized_comps:
            WarningBox(
                "Componente extraño",
                "Componente no reconocido. Cargar el\ncomponente desde el autocompletado.",
            ).exec_()
            return True
        else:
            return False

    def autoremove_line(self):
        for line_layout in self.comps_holder_section.layout().children():
            two_empty_fields_on_same_line = (
                line_layout.itemAt(0).widget().text() == ""
                and line_layout.itemAt(1).widget().text() == ""
            )
            if two_empty_fields_on_same_line:
                if len(self.comps_holder_section.layout().children()) > 1:
                    utils.remove_three_widget_layout(line_layout)
                    return False
                else:
                    if len(self.comps_holder_section.layout().children()) <= 1:
                        WarningBox(
                            "Sin componentes",
                            "Completar o borrar campos\nvacíos antes de ejecutar.",
                        ).exec_()
                    return True
            elif not two_empty_fields_on_same_line:
                WarningBox(
                    "Sin componentes",
                    "Completar o borrar campos\nvacíos antes de ejecutar.",
                ).exec_()
                return True

    def insert_subtraction_comps_into_db(self):
        comps_to_subtract = utils.get_line_items_contents(
            (self.comps_holder_section), as_dictionary=True
        )
        db = db_manager.DB_Manager()
        for comp_display, subtr_amount in comps_to_subtract.items():
            comp_sql = db.get_SQL_name_for_component(comp_display)
            stock_vald_pre_appl = db.get_stock_at_valdenegro_for(comp_sql)
            stock_vald_post_appl = stock_vald_pre_appl - subtr_amount
            self.final_dialog_data[comp_display] = [
                stock_vald_pre_appl,
                stock_vald_post_appl,
                subtr_amount,
            ]
            data_to_apply_subtraction = {
                "comp_sql": comp_sql,
                "subtr_amount": subtr_amount,
                "stock_vald_post_appl": stock_vald_post_appl,
            }
            db.apply_subtraction_to_valdenegro_only(data_to_apply_subtraction)
            settings = QtCore.QSettings("solutronic", "admin_stock")
            db.log_new_movement(
                movement="Egreso",
                destination="Uso interno",
                component=comp_display,
                amount=subtr_amount,
                user=settings.value("username"),
            )

        db.close_connection()
        self.close()
        SubtractionAppliedMessageBox(self).exec_()


class SubtractionAppliedMessageBox(QtWidgets.QMessageBox):
    def __init__(self, parent=None):
        super(SubtractionAppliedMessageBox, self).__init__(parent)
        self.final_dialog_data = self.parent().final_dialog_data
        self.setWindowTitle("Finalizado")
        self.setWindowFlags(
            QtCore.Qt.Dialog
            | QtCore.Qt.CustomizeWindowHint
            | QtCore.Qt.WindowTitleHint
            | QtCore.Qt.WindowCloseButtonHint
        )

        title = QtWidgets.QLabel("Egreso a uso interno")
        title.setAlignment(QtCore.Qt.AlignCenter)
        title.setStyleSheet(generic_title_style)

        table = QtWidgets.QTableWidget()
        table.setFixedWidth(500)
        table.setFocusPolicy(QtCore.Qt.NoFocus)
        table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        table.verticalHeader().setVisible(False)
        table.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)
        table.setColumnCount(4)
        table.setHorizontalHeaderLabels(["Componente", "Inicial", "Egreso", "Final"])
        table.horizontalHeaderItem(0).setTextAlignment(QtCore.Qt.AlignHCenter)
        table.horizontalHeaderItem(1).setTextAlignment(QtCore.Qt.AlignHCenter)
        table.horizontalHeaderItem(2).setTextAlignment(QtCore.Qt.AlignHCenter)
        table.horizontalHeaderItem(3).setTextAlignment(QtCore.Qt.AlignHCenter)
        table.horizontalHeader().setDefaultSectionSize(70)
        table.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        table.horizontalHeader().setSectionResizeMode(1, QtWidgets.QHeaderView.Fixed)
        table.horizontalHeader().setSectionResizeMode(2, QtWidgets.QHeaderView.Fixed)
        table.horizontalHeader().setSectionResizeMode(3, QtWidgets.QHeaderView.Fixed)
        table.setRowCount(len(self.final_dialog_data))

        utils.populate_table_column_with_list_of_strings(
            table=table, col_num=0, input_list=self.final_dialog_data.keys()
        )

        components_pre_application_amts = [
            i[0] for i in self.final_dialog_data.values()
        ]

        utils.populate_table_column_with_list_of_integers(
            table=table, col_num=1, input_list=components_pre_application_amts
        )

        components_subtraction_amts = [i[2] for i in self.final_dialog_data.values()]

        utils.populate_table_column_with_list_of_integers(
            table=table,
            col_num=2,
            input_list=components_subtraction_amts,
            with_minus=True,
        )
        for i in range(table.rowCount()):
            table.item(i, 2).setBackground(QtGui.QColor("red"))
            table.item(i, 2).setForeground(QtGui.QColor("white"))

        components_post_application_amts = [
            i[1] for i in self.final_dialog_data.values()
        ]

        utils.populate_table_column_with_list_of_integers(
            table=table, col_num=3, input_list=components_post_application_amts
        )

        custom_height = table.rowCount() * 30 + 25

        table.setMaximumHeight(custom_height)
        table.setFixedHeight(custom_height)

        ok_button = QtWidgets.QPushButton("OK")
        ok_button.clicked.connect(self.close)

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(title)
        layout.addWidget(table)
        layout.addWidget(ok_button)

        self.layout().addLayout(layout, 0, 0, 0, 0, QtCore.Qt.AlignTop)

        self.setStyleSheet(generic_messagebox_style)

        admin_window = self.parent().parent().parent().parent()
        admin_window.statusbar.show_quick_message(
            "Egreso a uso interno aplicado a Depósito"
        )
        admin_window.start_screen.rebuild_main_section()
