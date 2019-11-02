from PyQt5 import QtWidgets, QtCore
from utils import utils_collection as utils
from utils import db_manager
from utils.styling import generic_title_style
from utils import tests
from widgets.spec_fields import AutocapField, StockNumberField
from widgets.message_boxes import QuestionBox, WarningBox, InformationBox


class EditRecipeDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(EditRecipeDialog, self).__init__(parent)

        self.recipe_being_edited_display = ""
        self.recipe_being_edited_sql = ""
        self.stored_recipe_contents = {}

        self.setWindowFlags(
            QtCore.Qt.Dialog
            | QtCore.Qt.CustomizeWindowHint
            | QtCore.Qt.WindowCloseButtonHint
        )

        self.setFixedWidth(200)
        self.setFixedHeight(250)

        title = QtWidgets.QLabel("Editar receta")
        title.setAlignment(QtCore.Qt.AlignCenter)
        title.setStyleSheet(generic_title_style)

        self.searchbar = AutocapField("Buscar receta a editar...")
        self.searchbar.set_completer(source="recipes")

        self.table = QtWidgets.QTableWidget()
        self.table.setFocusPolicy(QtCore.Qt.NoFocus)
        self.table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)
        self.table.setColumnCount(1)
        self.table.setHorizontalHeaderLabels(["Producto"])
        self.table.horizontalHeaderItem(0).setTextAlignment(QtCore.Qt.AlignHCenter)
        self.table.horizontalHeader().setSectionResizeMode(
            0, QtWidgets.QHeaderView.Stretch
        )

        db = db_manager.DB_Manager()
        self.all_recipes_display = db.get_all_recipes_as_display()
        db.close_connection()
        self.table.setRowCount(len(self.all_recipes_display))
        utils.populate_table_column_with_list_of_strings(
            table=self.table, col_num=0, input_list=self.all_recipes_display
        )

        back_button = QtWidgets.QPushButton("« Volver")
        back_button.setShortcut("Alt+v")

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(title)
        layout.addWidget(self.searchbar)
        layout.addWidget(self.table)
        layout.addWidget(back_button)

        self.setLayout(layout)

        back_button.clicked.connect(self.close)
        self.searchbar.returnPressed.connect(self.on_searchbar_return_pressed)
        self.table.cellDoubleClicked.connect(self.on_table_item_double_clicked)

        if not self.all_recipes_display:
            InformationBox("Sin recetas", "No hay recetas para editar.").exec_()
            QtCore.QTimer.singleShot(1, self.close)

    def on_searchbar_return_pressed(self):
        if self.searchbar.text() not in self.all_recipes_display:
            return
        utils.scroll_to_row_in_table(self.table, self.searchbar.text())
        self.recipe_being_edited_display = self.searchbar.text()
        RecipeDetailsDialog(parent=self).exec_()

    def on_table_item_double_clicked(self, row, col):
        self.recipe_being_edited_display = self.table.item(row, col).text()
        RecipeDetailsDialog(parent=self).exec_()


class RecipeDetailsDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(RecipeDetailsDialog, self).__init__(parent)
        self.recipe_being_edited_contents = {}
        self.setWindowFlags(
            QtCore.Qt.Dialog
            | QtCore.Qt.CustomizeWindowHint
            | QtCore.Qt.WindowCloseButtonHint
        )
        self.setFixedWidth(300)

        self.recipe_being_edited_display = self.parent().recipe_being_edited_display
        self.recipe_being_edited_sql = self.parent().recipe_being_edited_sql

        title = QtWidgets.QLabel("Receta: " + self.recipe_being_edited_display)
        title.setStyleSheet(generic_title_style)
        title.setAlignment(QtCore.Qt.AlignCenter)

        self.comps_holder_section = QtWidgets.QVBoxLayout()

        add_buton = QtWidgets.QPushButton("+ Agregar")
        add_buton.setShortcut("Alt+a")

        save_button = QtWidgets.QPushButton("≡ Guardar")
        save_button.setShortcut("Alt+g")

        layout = QtWidgets.QVBoxLayout()
        bottom_layout = QtWidgets.QHBoxLayout()
        bottom_layout.addWidget(add_buton)
        bottom_layout.addWidget(save_button)
        layout.setSizeConstraint(QtWidgets.QLayout.SetFixedSize)
        layout.addWidget(title)
        layout.addLayout(self.comps_holder_section)
        layout.addLayout(bottom_layout)

        self.setLayout(layout)

        self.populate_recipe_data()

        add_buton.clicked.connect(self.add_recipe_item_line)
        save_button.clicked.connect(self.save_recipe)

    def populate_recipe_data(self):
        db = db_manager.DB_Manager()
        self.recipe_being_edited_sql = utils.format_display_name_into_sql_name(
            self.recipe_being_edited_display
        )
        self.stored_recipe_contents = db.get_recipe_contents(
            self.recipe_being_edited_sql
        )
        db.close_connection()

        for _ in self.stored_recipe_contents.items():
            self.add_recipe_item_line()

        for i, layout in enumerate(self.comps_holder_section.children()):
            component = list(self.stored_recipe_contents.keys())[i]
            amount = list(self.stored_recipe_contents.values())[i]
            amount = utils.format_number_for_display(amount)
            layout.itemAt(0).widget().setText(component)
            layout.itemAt(1).widget().setText(amount)

    def add_recipe_item_line(self):
        searchbar_recipe_component = AutocapField("Componente...")
        searchbar_recipe_component.setFixedWidth(130)

        searchbar_recipe_component.set_completer(source="comps in stock")
        searchbar_recipe_amount = StockNumberField("Cantidad...")
        searchbar_recipe_amount.setFixedWidth(85)

        close_button = QtWidgets.QPushButton("×")
        close_button.setFixedWidth(20)
        close_button.clicked.connect(self.remove_recipe_item_via_close_button)

        recipe_item_line_layout = QtWidgets.QHBoxLayout()
        recipe_item_line_layout.addWidget(searchbar_recipe_component)
        recipe_item_line_layout.addWidget(searchbar_recipe_amount)
        recipe_item_line_layout.addWidget(close_button)

        self.comps_holder_section.addLayout(recipe_item_line_layout)

    def save_recipe(self):
        if not self.comps_holder_section.children():
            self.delete_empty_recipe()
            return
        for i in [
            self.test_if_there_are_recipe_data,
            self.test_if_there_are_duplicates,
            self.test_if_there_are_unrecognized_components,
        ]:
            if i():
                return

        self.insert_edited_recipe_into_db()

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

    def test_if_edited_recipe_is_equal_to_original(self):
        db = db_manager.DB_Manager()
        original_recipe_contents = db.get_recipe_contents(self.recipe_being_edited_sql)
        db.close_connection()

        if self.recipe_being_edited_contents == original_recipe_contents:
            self.close()
            self.parent().close()

    def delete_empty_recipe(self):
        box = QuestionBox(
            "Confirmación",
            f"¿Borrar receta {self.recipe_being_edited_display}?\n\nNo puede existir una receta vacía.",
        )
        box.exec_()

        if box.clickedButton() == box.button(QtWidgets.QMessageBox.No):
            pass
        elif box.clickedButton() == box.button(QtWidgets.QMessageBox.Yes):
            db = db_manager.DB_Manager()
            db.delete_recipe(self.recipe_being_edited_sql)
            db.log_new_config_record(
                config="Borrado de receta", details=self.recipe_being_edited_display
            )
            db.close_connection()
            admin_window = self.parent().parent().parent()
            admin_window.statusbar.show_quick_message(
                "Receta guardada: " + self.recipe_being_edited_display
            )
            admin_window.start_screen.rebuild_main_section()
            self.close()
            self.parent().close()

    def insert_edited_recipe_into_db(self):
        fields_contents = utils.get_line_items_contents(self.comps_holder_section)
        components = fields_contents[0::2]
        amounts = fields_contents[1::2]

        self.test_if_edited_recipe_is_equal_to_original()

        self.recipe_being_edited_contents = dict(zip(components, amounts))
        db = db_manager.DB_Manager()
        db.edit_recipe(self.recipe_being_edited_sql, self.recipe_being_edited_contents)
        db.log_new_config_record(
            config="Edición de receta", details=self.recipe_being_edited_display
        )
        db.close_connection()

        admin_window = self.parent().parent().parent().parent()
        admin_window.statusbar.show_quick_message(
            "Receta guardada: " + self.recipe_being_edited_display
        )

        self.close()
        self.parent().close()

    def remove_recipe_item_via_close_button(self):
        for layout in self.comps_holder_section.children():
            if layout.itemAt(2).widget() == self.sender():
                selected_component = layout.itemAt(0).widget().text()
                selected_amount = layout.itemAt(1).widget().text()

        if selected_component == "":
            pass
        if selected_amount == "":
            for layout in self.comps_holder_section.children():
                if layout.itemAt(2).widget() == self.sender():
                    utils.remove_three_widget_layout(layout)

        elif selected_component != "" or selected_amount != "":
            selected_component = (
                selected_component if selected_component != "" else "[Vacío]"
            )
            selected_amount = selected_amount if selected_amount != "" else "0"
            box = QuestionBox(
                "Confirmación",
                f"¿Borrar este ítem en esta receta?\n\nComponente: {selected_component}\nCantidad: {selected_amount}",
            )
            box.exec_()
            if box.clickedButton() == box.button(QtWidgets.QMessageBox.No):
                pass
            elif box.clickedButton() == box.button(QtWidgets.QMessageBox.Yes):
                for layout in self.comps_holder_section.children():
                    if layout.itemAt(2).widget() == self.sender():
                        utils.remove_three_widget_layout(layout)
