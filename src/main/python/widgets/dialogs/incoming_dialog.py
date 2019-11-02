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


class IncomingDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(IncomingDialog, self).__init__(parent)

        self.incoming_comps_and_amounts_for_operation = {}
        self.data_for_final_dialog = {}
        self.setWindowFlags(
            QtCore.Qt.Dialog
            | QtCore.Qt.CustomizeWindowHint
            | QtCore.Qt.WindowCloseButtonHint
        )
        self.setFixedWidth(410)

        title = QtWidgets.QLabel("Ingreso de componentes")
        title.setAlignment(QtCore.Qt.AlignCenter)
        title.setStyleSheet(generic_title_style)

        top_section = QtWidgets.QHBoxLayout()

        self.packing_list_field = QtWidgets.QLineEdit()
        self.packing_list_field.setPlaceholderText("Remito...")

        self.supplier_field = QtWidgets.QLineEdit()
        self.supplier_field.setPlaceholderText("Proveedor...")

        self.note_field = QtWidgets.QLineEdit()
        self.note_field.setPlaceholderText("Nota...")

        for i in [self.packing_list_field, self.supplier_field, self.note_field]:
            i.setFixedWidth(125)
            top_section.addWidget(i)

        bottom_section = QtWidgets.QHBoxLayout()
        back_button = QtWidgets.QPushButton("« Volver")
        back_button.setShortcut("Alt+v")

        execute_button = QtWidgets.QPushButton("Ejecutar »")
        execute_button.setShortcut("Alt+e")
        execute_button.setDefault(True)

        bottom_section.addWidget(back_button)
        bottom_section.addWidget(execute_button)

        groupbox = QtWidgets.QGroupBox("Componentes ingresantes")
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
        layout.addLayout(top_section)
        layout.addLayout(groupbox_section)
        layout.addLayout(bottom_section)

        self.setLayout(layout)

        back_button.clicked.connect(self.close)
        add_component_button.clicked.connect(self.add_line)
        execute_button.clicked.connect(self.execute_incoming_comps)

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

    def execute_incoming_comps(self):
        for i in [
            self.test_if_packing_list_or_supplier_fields_are_empty,
            self.test_if_there_are_no_components,
            self.test_if_there_are_duplicates,
            self.test_if_there_are_empty_main_fields,
            self.test_if_there_are_unrecognized_components,
        ]:
            if i():
                return

        self.insert_incoming_comps_into_db()

    def test_if_packing_list_or_supplier_fields_are_empty(self):
        if self.packing_list_field.text() == "":
            WarningBox("Remito faltante", "Ingresar remito\nantes de ejecutar.").exec_()
            self.packing_list_field.setFocus()
            return True
        elif self.supplier_field.text() == "":
            WarningBox(
                "Proveedor faltante", "Ingresar proveedor\nantes de ejecutar."
            ).exec_()
            self.supplier_field.setFocus()
            return True
        else:
            return False

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

    def test_if_there_are_empty_main_fields(self):
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

    def insert_incoming_comps_into_db(self):
        fields_contents = utils.get_line_items_contents(self.comps_holder_section)
        incoming_components = fields_contents[0::2]
        incoming_amounts = fields_contents[1::2]
        incoming_components_and_amounts_for_display = dict(
            zip(incoming_components, incoming_amounts)
        )

        db = db_manager.DB_Manager()

        for k, v in incoming_components_and_amounts_for_display.items():
            self.incoming_comps_and_amounts_for_operation[
                db.get_SQL_name_for_component(k)
            ] = utils.format_number_for_calculation(v)

        for component_display in incoming_components_and_amounts_for_display.keys():
            for (
                comp_sql,
                amount,
            ) in self.incoming_comps_and_amounts_for_operation.items():
                stock_vald_pre_application = db.get_stock_at_valdenegro_for(comp_sql)
                stock_vald_post_application = stock_vald_pre_application + amount
                self.data_for_final_dialog[component_display] = [
                    stock_vald_pre_application,
                    stock_vald_post_application,
                ]
                data = {
                    "comp_sql": comp_sql,
                    "amount": amount,
                    "packing_list": self.packing_list_field.text(),
                    "supplier": self.supplier_field.text(),
                    "note": self.note_field.text() if self.note_field.text() else "---",
                    "stock_vald_post_application": stock_vald_post_application,
                    "stock_karina": db.get_stock_at_assembler_for(comp_sql, "karina"),
                    "stock_brid": db.get_stock_at_assembler_for(comp_sql, "brid"),
                    "stock_tercero": db.get_stock_at_assembler_for(comp_sql, "tercero"),
                }
                db.apply_incoming_to_valdenegro(data)

        start_screen = self.parent().parent().parent().start_screen
        start_screen.rebuild_main_section()
        settings = QtCore.QSettings("solutronic", "admin_stock")
        for component, amount in incoming_components_and_amounts_for_display.items():
            db.log_new_movement(
                movement="Ingreso",
                destination="Depósito",
                component=component,
                amount=amount,
                user=settings.value("username"),
            )

        db.close_connection()
        IncomingAppliedMessageBox(self).exec_()


class IncomingAppliedMessageBox(QtWidgets.QMessageBox):
    def __init__(self, parent=None):
        super(IncomingAppliedMessageBox, self).__init__(parent)

        comps_and_amounts = (
            self.sender().parent().incoming_comps_and_amounts_for_operation
        )
        data_for_final_dialog = self.sender().parent().data_for_final_dialog

        self.setWindowTitle("Finalizado")
        self.setWindowFlags(
            QtCore.Qt.Dialog
            | QtCore.Qt.CustomizeWindowHint
            | QtCore.Qt.WindowTitleHint
            | QtCore.Qt.WindowCloseButtonHint
        )

        title = QtWidgets.QLabel("Ingreso aplicado a Depósito")
        title.setAlignment(QtCore.Qt.AlignCenter)
        title.setStyleSheet(generic_title_style)

        table = QtWidgets.QTableWidget()
        table.setFixedWidth(400)
        table.setFocusPolicy(QtCore.Qt.NoFocus)
        table.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)
        table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        table.verticalHeader().setVisible(False)
        table.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)
        table.setColumnCount(4)
        table.setHorizontalHeaderLabels(["Componente", "Inicial", "Ingreso", "Final"])
        table.horizontalHeaderItem(0).setTextAlignment(QtCore.Qt.AlignHCenter)
        table.horizontalHeaderItem(1).setTextAlignment(QtCore.Qt.AlignHCenter)
        table.horizontalHeaderItem(2).setTextAlignment(QtCore.Qt.AlignHCenter)
        table.horizontalHeaderItem(3).setTextAlignment(QtCore.Qt.AlignHCenter)
        table.horizontalHeader().setDefaultSectionSize(70)
        table.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        table.horizontalHeader().setSectionResizeMode(1, QtWidgets.QHeaderView.Fixed)
        table.horizontalHeader().setSectionResizeMode(2, QtWidgets.QHeaderView.Fixed)
        table.horizontalHeader().setSectionResizeMode(3, QtWidgets.QHeaderView.Fixed)
        table.setRowCount(len(comps_and_amounts))

        incoming_comp_names = data_for_final_dialog.keys()
        incoming_comp_amounts = comps_and_amounts.values()

        stock_vald_pre_application = [v[0] for v in data_for_final_dialog.values()]
        stock_vald_post_application = [v[1] for v in data_for_final_dialog.values()]

        utils.populate_table_column_with_list_of_strings(
            table=table, col_num=0, input_list=incoming_comp_names
        )
        utils.populate_table_column_with_list_of_integers(
            table=table, col_num=1, input_list=stock_vald_pre_application
        )
        utils.populate_table_column_with_list_of_integers(
            table=table, col_num=2, input_list=incoming_comp_amounts, with_plus=True
        )

        for i in range(table.rowCount()):
            table.item(i, 2).setBackground(QtGui.QColor("#79c879"))

        utils.populate_table_column_with_list_of_integers(
            table=table, col_num=3, input_list=stock_vald_post_application
        )
        custom_height = table.rowCount() * 30 + 25

        table.setMaximumHeight(custom_height)
        table.setFixedHeight(custom_height)

        ok_button = QtWidgets.QPushButton("OK")

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(title)
        layout.addWidget(table)
        layout.addWidget(ok_button)

        self.layout().addLayout(layout, 0, 0, 0, 0, QtCore.Qt.AlignTop)

        self.setStyleSheet(generic_messagebox_style)

        admin_window = self.parent().parent().parent().parent()
        admin_window.statusbar.show_quick_message("Ingreso aplicado a Depósito")

        ok_button.clicked.connect(self.close)
        ok_button.clicked.connect(self.parent().close)
