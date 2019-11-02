from PyQt5 import QtWidgets, QtCore
from utils import db_manager
from utils import utils_collection as utils
from utils.styling import (
    delete_component_dialog_label_normal_style,
    delete_component_dialog_label_bold_style,
    generic_title_style,
    generic_messagebox_style,
)
from widgets.spec_fields import AutocapField
from widgets.message_boxes import WarningBox


class DeleteComponentDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(DeleteComponentDialog, self).__init__(parent)
        self.setWindowFlags(
            QtCore.Qt.Dialog
            | QtCore.Qt.CustomizeWindowHint
            | QtCore.Qt.WindowCloseButtonHint
        )
        self.setFixedWidth(200)

        self.comp_being_deleted_display_name = ""

        title = QtWidgets.QLabel("Borrar componente")
        title.setAlignment(QtCore.Qt.AlignCenter)
        title.setStyleSheet(generic_title_style)

        self.search_field = AutocapField("Buscar componente a borrar...")
        self.search_field.setFocus()
        self.search_field.set_completer(source="comps in stock")

        back_button = QtWidgets.QPushButton("« Volver")
        back_button.setShortcut("Alt+v")

        execute_button = QtWidgets.QPushButton("Ejecutar »")
        execute_button.setShortcut("Alt+e")
        execute_button.setDefault(True)

        bottom_section = QtWidgets.QHBoxLayout()
        bottom_section.addWidget(back_button)
        bottom_section.addWidget(execute_button)

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(title)
        layout.addWidget(self.search_field)
        layout.addLayout(bottom_section)

        self.setLayout(layout)

        self.search_field.returnPressed.connect(self.delete_component)
        execute_button.clicked.connect(self.delete_component)
        back_button.clicked.connect(self.close)

    def test_if_there_are_unrecognized_components(self):
        db = db_manager.DB_Manager()
        existing_comps = db.get_all_display_names_for_components()
        db.close_connection()

        if self.search_field.text() not in existing_comps:
            WarningBox(
                "Componente extraño",
                "Componente no reconocido. Cargar el\ncomponente desde el autocompletado.",
            ).exec_()
            return True
        else:
            return False

    def delete_component(self):
        if self.test_if_there_are_unrecognized_components():
            return
        self.comp_being_deleted_display_name = self.search_field.text()
        main_section_table = self.parent().parent().main_section.table
        utils.scroll_to_row_in_table(
            main_section_table,
            (self.comp_being_deleted_display_name),
            keep_light_blue_color=True,
        )
        DeletionConfirmationBox(parent=self).exec_()


class DeletionConfirmationBox(QtWidgets.QMessageBox):
    def __init__(self, parent=None):
        super(DeletionConfirmationBox, self).__init__(parent)
        self.setWindowTitle("Confirmación")
        self.setWindowFlags(
            QtCore.Qt.Dialog
            | QtCore.Qt.CustomizeWindowHint
            | QtCore.Qt.WindowTitleHint
            | QtCore.Qt.WindowCloseButtonHint
        )

        self.comp_being_deleted_display_name = (
            self.parent().comp_being_deleted_display_name
        )

        db = db_manager.DB_Manager()
        relevant_recipes = db.get_recipes_containing_component(
            self.comp_being_deleted_display_name
        )
        db.close_connection()

        label_1 = QtWidgets.QLabel("¿Borrar este componente...?")
        label_2 = QtWidgets.QLabel(self.comp_being_deleted_display_name)
        label_2.setStyleSheet(delete_component_dialog_label_bold_style)
        label_3 = QtWidgets.QLabel("Se borrará también de estas recetas:")
        label_4 = QtWidgets.QLabel("No está integrado a ninguna receta.")

        for i in [label_1, label_3, label_4]:
            i.setStyleSheet(delete_component_dialog_label_normal_style)

        for i in [label_1, label_2, label_3, label_4]:
            i.setAlignment(QtCore.Qt.AlignCenter)

        recipes_table = QtWidgets.QTableWidget()
        recipes_table.setFixedWidth(400)
        recipes_table.setFocusPolicy(QtCore.Qt.NoFocus)
        recipes_table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        recipes_table.verticalHeader().setVisible(False)
        recipes_table.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)
        recipes_table.setColumnCount(3)
        recipes_table.setHorizontalHeaderLabels(["Receta", "Componente", "Cantidad"])
        recipes_table.horizontalHeaderItem(0).setTextAlignment(QtCore.Qt.AlignHCenter)
        recipes_table.horizontalHeaderItem(1).setTextAlignment(QtCore.Qt.AlignHCenter)
        recipes_table.horizontalHeaderItem(2).setTextAlignment(QtCore.Qt.AlignHCenter)
        recipes_table.horizontalHeader().setDefaultSectionSize(90)
        recipes_table.horizontalHeader().setSectionResizeMode(
            0, QtWidgets.QHeaderView.Fixed
        )
        recipes_table.horizontalHeader().setSectionResizeMode(
            1, QtWidgets.QHeaderView.Stretch
        )
        recipes_table.horizontalHeader().setSectionResizeMode(
            2, QtWidgets.QHeaderView.Fixed
        )
        recipes_table.setRowCount(len(relevant_recipes.items()))

        if recipes_table.rowCount() <= 5:
            custom_height = recipes_table.rowCount() * 30 + 25
            recipes_table.setMaximumHeight(custom_height)
            recipes_table.setFixedHeight(custom_height)
        elif recipes_table.rowCount() > 5:
            recipes_table.setMaximumHeight(171)
            recipes_table.setFixedHeight(171)

        utils.populate_table_column_with_list_of_strings(
            table=recipes_table, col_num=0, input_list=relevant_recipes.keys()
        )

        list_of_comp_being_deleted_repeated_row_times = [
            self.comp_being_deleted_display_name for i in range(len(relevant_recipes))
        ]

        utils.populate_table_column_with_list_of_strings(
            table=recipes_table,
            col_num=1,
            input_list=list_of_comp_being_deleted_repeated_row_times,
        )

        for row_number, amt_used in enumerate(relevant_recipes.values()):
            if len(str(amt_used).split(".")[1]) == 3:
                amt_used = utils.format_number_for_display(amt_used)
            else:
                amt_used = utils.format_number_for_display(amt_used)
            item = QtWidgets.QTableWidgetItem(amt_used)
            recipes_table.setItem(row_number, 2, item)
            item.setTextAlignment(QtCore.Qt.AlignCenter)

        no_button = QtWidgets.QPushButton("No")
        yes_button = QtWidgets.QPushButton("Sí")

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(label_1)
        layout.addWidget(label_2)

        if relevant_recipes != {}:
            layout.addWidget(label_3)
            layout.addWidget(recipes_table)
            self.related_records = True
        else:
            layout.addWidget(label_4)
            self.related_records = False

        bottom_section = QtWidgets.QHBoxLayout()
        bottom_section.addWidget(no_button)
        bottom_section.addWidget(yes_button)

        layout.addLayout(bottom_section)

        self.layout().addLayout(layout, 0, 0, 0, 0, QtCore.Qt.AlignCenter)
        self.setStyleSheet(generic_messagebox_style)

        no_button.clicked.connect(self.on_no_at_confirmation)
        yes_button.clicked.connect(self.on_yes_at_confirmation)

    def on_no_at_confirmation(self):
        admin_window = self.parent().parent().parent().parent()
        admin_window.start_screen.rebuild_main_section()
        self.close()
        self.parent().close()

    def on_yes_at_confirmation(self):
        db = db_manager.DB_Manager()
        db.enable_foreign_keys()

        comp_being_deleted_sql_name = db.get_SQL_name_for_component(
            self.comp_being_deleted_display_name
        )

        db.delete_comp_name_everywhere(comp_being_deleted_sql_name)

        db.log_new_config_record(
            config="Borrado de componente", details=self.comp_being_deleted_display_name
        )

        db.close_connection()

        admin_window = self.parent().parent().parent().parent()
        admin_window.statusbar.show_quick_message(
            "Componente borrado: " + self.comp_being_deleted_display_name
        )
        admin_window.start_screen.rebuild_main_section()

        self.close()
        self.parent().close()
