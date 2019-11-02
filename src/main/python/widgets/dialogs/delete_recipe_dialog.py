from PyQt5 import QtWidgets, QtCore
from utils import utils_collection as utils
from utils import db_manager
from utils.styling import generic_title_style
from widgets.spec_fields import AutocapField
from widgets.message_boxes import QuestionBox, InformationBox


class DeleteRecipeDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(DeleteRecipeDialog, self).__init__(parent)
        self.recipe_being_deleted_display = ""
        self.recipe_being_deleted_sql = ""
        self.setWindowFlags(
            QtCore.Qt.Dialog
            | QtCore.Qt.CustomizeWindowHint
            | QtCore.Qt.WindowCloseButtonHint
        )
        self.setFixedWidth(200)
        self.setFixedHeight(250)

        title = QtWidgets.QLabel("Borrar receta")
        title.setAlignment(QtCore.Qt.AlignCenter)
        title.setStyleSheet(generic_title_style)

        self.searchbar = AutocapField("Buscar receta a borrar...")
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
            InformationBox("Sin recetas", "No hay recetas para borrar.").exec_()
            QtCore.QTimer.singleShot(1, self.close)

    def on_searchbar_return_pressed(self):
        if self.searchbar.text() not in self.all_recipes_display:
            return
        utils.scroll_to_row_in_table(self.table, self.searchbar.text())
        self.recipe_being_deleted_display = self.searchbar.text()
        self.delete_recipe_from_db()

    def on_table_item_double_clicked(self, row, col):
        self.recipe_being_deleted_display = self.table.item(row, col).text()
        self.delete_recipe_from_db()

    def delete_recipe_from_db(self):
        self.recipe_being_deleted_sql = utils.format_display_name_into_sql_name(
            self.recipe_being_deleted_display
        )
        box = QuestionBox(
            "Confirmación", f"¿Borrar receta {self.recipe_being_deleted_display}?"
        )
        box.exec_()

        if box.clickedButton() == box.button(QtWidgets.QMessageBox.No):
            pass
        elif box.clickedButton() == box.button(QtWidgets.QMessageBox.Yes):
            db = db_manager.DB_Manager()
            db.delete_recipe(self.recipe_being_deleted_sql)
            db.log_new_config_record(
                config="Borrado de receta", details=self.recipe_being_deleted_display
            )
            db.close_connection()
            admin_window = self.parent().parent().parent()
            admin_window.statusbar.show_quick_message(
                "Receta borrada: " + self.recipe_being_deleted_display
            )
            admin_window.start_screen.rebuild_main_section()

            self.close()
