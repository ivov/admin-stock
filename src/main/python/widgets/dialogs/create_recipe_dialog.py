from PyQt5 import QtWidgets, QtCore
from utils.styling import generic_title_style, generic_groupbox_normal_style
from utils import utils_collection as utils
from utils import db_manager
from utils import tests
from widgets.line_item_close_button import LineItemCloseButton
from widgets.spec_fields import AutocapField, StockNumberField
from widgets.message_boxes import WarningBox


class CreateRecipeDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(CreateRecipeDialog, self).__init__(parent)
        self.setWindowFlags(
            QtCore.Qt.Dialog
            | QtCore.Qt.CustomizeWindowHint
            | QtCore.Qt.WindowCloseButtonHint
        )

        title = QtWidgets.QLabel("Crear receta")
        title.setAlignment(QtCore.Qt.AlignCenter)
        title.setStyleSheet(generic_title_style)

        self.product_field = AutocapField("Producto a crear...")
        self.product_field.setFixedWidth(200)

        self.model_field = AutocapField("Modelo de producto...")
        self.model_field.setFixedWidth(200)

        fields_layout = QtWidgets.QHBoxLayout()
        fields_layout.addWidget(self.product_field)
        fields_layout.addWidget(self.model_field)

        groupbox = QtWidgets.QGroupBox("Componentes y cantidades")
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

        back_button = QtWidgets.QPushButton("« Volver")
        back_button.setShortcut("Alt+v")
        back_button.setFixedWidth(200)

        execute_button = QtWidgets.QPushButton("Ejecutar »")
        execute_button.setShortcut("Alt+e")
        execute_button.setFixedWidth(200)

        bottom_layout = QtWidgets.QHBoxLayout()
        bottom_layout.addWidget(back_button)
        bottom_layout.addWidget(execute_button)

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(title)
        layout.addLayout(fields_layout)
        layout.addLayout(groupbox_section)
        layout.addStretch(1)
        layout.addLayout(bottom_layout)
        layout.setSizeConstraint(QtWidgets.QLayout.SetFixedSize)

        self.setLayout(layout)

        back_button.clicked.connect(self.close)
        add_component_button.clicked.connect(self.add_line)
        execute_button.clicked.connect(self.create_recipe)

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

    def create_recipe(self):
        for i in [
            self.test_if_product_or_model_fields_are_empty,
            self.test_if_there_are_recipe_data,
            self.test_if_there_are_duplicates,
            self.test_if_there_are_unrecognized_components,
        ]:
            if i():
                return

        self.insert_new_recipe_into_db()

    def test_if_product_or_model_fields_are_empty(self):
        if self.product_field.text() == "":
            WarningBox(
                "Producto faltante", "Ingresar producto\nantes de ejecutar."
            ).exec_()
            self.product_field.setFocus()
            return True
        elif self.model_field.text() == "":
            WarningBox("Modelo faltante", "Ingresar modelo\nantes de ejecutar.").exec_()
            self.model_field.setFocus()
            return True
        else:
            return False

    def test_if_there_are_recipe_data(self):
        contents = utils.get_line_items_contents(self.comps_holder_section)
        empty_strings_exist = tests.test_if_empty_string_in_line_items_contents(
            contents
        )

        if self.comps_holder_section.children() and empty_strings_exist:
            WarningBox(
                "Sin componentes",
                "Completar o borrar campos\nvacíos antes de ejecutar.",
            ).exec_()
            return True
        else:
            return False

    def test_if_there_are_duplicates(self):
        contents = utils.get_line_items_contents(self.comps_holder_section)

        if tests.test_if_duplicated_first_value_in_line_items_contents(contents):
            WarningBox(
                "Componentes duplicados", "Borrar uno de los componentes duplicados."
            ).exec_()
            return True
        else:
            return False

    def test_if_there_are_unrecognized_components(self):
        contents = utils.get_line_items_contents(self.comps_holder_section)

        incoming_components = contents[0::2]
        db = db_manager.DB_Manager()
        existing_comps = db.get_all_display_names_for_components()
        db.close_connection()

        if not set(incoming_components).issubset(existing_comps):
            WarningBox(
                "Componente extraño",
                "Componente no reconocido. Cargar el\ncomponente desde el autocompletado.",
            ).exec_()
            return True
        else:
            return False

    def insert_new_recipe_into_db(self):
        recipe_being_created_display = (
            self.product_field.text() + "-" + self.model_field.text()
        )
        recipe_being_created_sql = utils.format_display_name_into_sql_name(
            recipe_being_created_display
        )
        fields_contents = utils.get_line_items_contents(self.comps_holder_section)
        components = fields_contents[0::2]
        amounts = fields_contents[1::2]
        recipe_contents = dict(zip(components, amounts))

        db = db_manager.DB_Manager()
        db.create_recipe(recipe_being_created_sql)
        db.populate_recipe(recipe_being_created_sql, recipe_contents)
        db.log_new_config_record(
            config="Creación de receta", details=recipe_being_created_display
        )
        db.close_connection()

        admin_window = self.parent().parent().parent()
        admin_window.statusbar.show_quick_message(
            "Receta creada: " + recipe_being_created_display
        )

        self.close()
