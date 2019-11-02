from PyQt5 import QtWidgets, QtCore
from utils import db_manager
from utils.styling import (
    generic_title_style,
    edit_input_dialog_subtitle_style,
    generic_messagebox_style,
    edit_confirmation_box_label_normal_style,
    edit_confirmation_box_label_bold_style,
)
from utils import utils_collection as utils
from widgets.spec_fields import AutocapField
from widgets.message_boxes import InformationBox


class EditComponentDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(EditComponentDialog, self).__init__(parent)
        self.setWindowFlags(
            QtCore.Qt.Dialog
            | QtCore.Qt.CustomizeWindowHint
            | QtCore.Qt.WindowCloseButtonHint
        )
        self.setFixedWidth(200)
        self.setFixedHeight(250)

        self.comp_being_edited = ""

        title = QtWidgets.QLabel("Editar componente")
        title.setAlignment(QtCore.Qt.AlignCenter)
        title.setStyleSheet(generic_title_style)

        self.searchbar = AutocapField("Buscar componente a editar...")
        self.searchbar.set_completer(source="comps in stock")

        self.comps_table = QtWidgets.QTableWidget()
        self.comps_table.setColumnCount(1)
        self.comps_table.setHorizontalHeaderLabels(["Componente"])
        self.comps_table.setFocusPolicy(QtCore.Qt.NoFocus)
        self.comps_table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.comps_table.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)
        self.comps_table.verticalHeader().setVisible(False)
        self.comps_table.horizontalHeaderItem(0).setTextAlignment(
            QtCore.Qt.AlignHCenter
        )
        self.comps_table.horizontalHeader().setSectionResizeMode(
            0, QtWidgets.QHeaderView.Stretch
        )

        db = db_manager.DB_Manager()
        self.existing_comps = db.get_all_display_names_for_components()

        self.comps_table.setRowCount(len(self.existing_comps))
        utils.populate_table_column_with_list_of_strings(
            table=self.comps_table, col_num=0, input_list=self.existing_comps
        )
        self.comps_table.setSortingEnabled(True)
        self.comps_table.horizontalHeader().setSortIndicator(
            0, QtCore.Qt.AscendingOrder
        )
        self.comps_table.horizontalHeader().setSortIndicatorShown(False)

        back_button = QtWidgets.QPushButton("« Volver")
        back_button.setShortcut("Alt+v")

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(title)
        layout.addWidget(self.searchbar)
        layout.addWidget(self.comps_table)
        layout.addWidget(back_button)

        self.setLayout(layout)

        self.searchbar.returnPressed.connect(self.on_searchbar_return_pressed)
        self.comps_table.cellDoubleClicked.connect(self.on_table_item_double_clicked)
        back_button.clicked.connect(self.close)

        if not self.existing_comps:
            InformationBox("Sin componentes", "No hay componentes para editar.").exec_()
            QtCore.QTimer.singleShot(1, self.close)

    def on_searchbar_return_pressed(self):
        if self.searchbar.text() not in self.existing_comps:
            return
        utils.scroll_to_row_in_table(self.comps_table, self.searchbar.text())
        self.comp_being_edited = self.searchbar.text()
        EditInputDialog(parent=self).exec_()

    def on_table_item_double_clicked(self, row):
        self.comp_being_edited = self.comps_table.item(row, 0).text()
        EditInputDialog(parent=self).exec_()


class EditInputDialog(QtWidgets.QMessageBox):
    def __init__(self, parent=None):
        super(EditInputDialog, self).__init__(parent)
        self.setWindowTitle("Nuevo nombre")
        self.setWindowFlags(
            QtCore.Qt.Dialog
            | QtCore.Qt.CustomizeWindowHint
            | QtCore.Qt.WindowTitleHint
            | QtCore.Qt.WindowCloseButtonHint
        )
        self.comp_being_edited = self.parent().comp_being_edited

        title = QtWidgets.QLabel("Editar componente:")
        title.setAlignment(QtCore.Qt.AlignCenter)

        subtitle = QtWidgets.QLabel(self.comp_being_edited)
        subtitle.setAlignment(QtCore.Qt.AlignCenter)
        subtitle.setStyleSheet(edit_input_dialog_subtitle_style)

        self.new_name_field = AutocapField("Nuevo nombre...")

        bottom_section = QtWidgets.QHBoxLayout()

        back_button = QtWidgets.QPushButton("« Volver")
        back_button.setShortcut("Alt+v")

        execute_button = QtWidgets.QPushButton("Ejecutar »")
        execute_button.setShortcut("Alt+e")
        execute_button.setDefault(True)

        bottom_section.addWidget(back_button)
        bottom_section.addWidget(execute_button)

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addWidget(self.new_name_field)
        layout.addLayout(bottom_section)

        self.layout().addLayout(layout, 0, 0, 0, 0, QtCore.Qt.AlignCenter)
        self.setStyleSheet(generic_messagebox_style)

        back_button.clicked.connect(self.close)
        execute_button.clicked.connect(lambda: EditConfirmationBox(self).exec_())


class EditConfirmationBox(QtWidgets.QMessageBox):
    def __init__(self, parent=None):
        super(EditConfirmationBox, self).__init__(parent)
        self.setWindowTitle("Confirmación")
        self.setWindowFlags(
            QtCore.Qt.Dialog
            | QtCore.Qt.CustomizeWindowHint
            | QtCore.Qt.WindowTitleHint
            | QtCore.Qt.WindowCloseButtonHint
        )

        self.comp_old_display_name = self.parent().parent().comp_being_edited
        self.comp_new_display_name = self.parent().new_name_field.text()
        self.comp_new_sql_name = utils.format_display_name_into_sql_name(
            self.comp_new_display_name
        )

        db = db_manager.DB_Manager()
        relevant_recipes = db.get_recipes_containing_component(
            self.comp_old_display_name
        )
        self.comp_old_sql_name = db.get_SQL_name_for_component(
            self.comp_old_display_name
        )
        db.close_connection()

        label_left_1 = QtWidgets.QLabel("¿Editar este componente...?")
        label_left_2 = QtWidgets.QLabel(self.comp_old_display_name)
        label_right_1 = QtWidgets.QLabel("¿Con este nuevo nombre...?")
        label_right_2 = QtWidgets.QLabel(self.comp_new_display_name)
        label_3 = QtWidgets.QLabel("Se editará también en estas recetas:")
        label_4 = QtWidgets.QLabel("No está integrado a ninguna receta.")

        for i in [label_left_2, label_right_2]:
            i.setStyleSheet(edit_confirmation_box_label_bold_style)
        for i in [label_left_1, label_right_1, label_3, label_4]:
            i.setStyleSheet(edit_confirmation_box_label_normal_style)
        for i in [
            label_left_1,
            label_left_2,
            label_right_1,
            label_right_2,
            label_3,
            label_4,
        ]:
            i.setAlignment(QtCore.Qt.AlignCenter)

        label_layout_left = QtWidgets.QVBoxLayout()
        label_layout_right = QtWidgets.QVBoxLayout()
        label_layout_left.addWidget(label_left_1)
        label_layout_left.addWidget(label_left_2)
        label_layout_right.addWidget(label_right_1)
        label_layout_right.addWidget(label_right_2)

        label_container = QtWidgets.QHBoxLayout()
        label_container.addLayout(label_layout_left)
        label_container.addLayout(label_layout_right)

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

        utils.populate_table_column_with_list_of_strings(
            table=recipes_table, col_num=0, input_list=relevant_recipes.keys()
        )
        list_of_comp_being_edited_repeated_row_times = [
            self.comp_old_display_name for i in range(len(relevant_recipes))
        ]
        utils.populate_table_column_with_list_of_strings(
            table=recipes_table,
            col_num=1,
            input_list=list_of_comp_being_edited_repeated_row_times,
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
        layout.addLayout(label_container)
        if relevant_recipes != {}:
            layout.addWidget(label_3)
            layout.addWidget(recipes_table)
        else:
            layout.addWidget(label_4)
        bottom_section = QtWidgets.QHBoxLayout()
        bottom_section.addWidget(no_button)
        bottom_section.addWidget(yes_button)
        layout.addLayout(bottom_section)
        self.layout().addLayout(layout, 0, 0, 0, 0, QtCore.Qt.AlignCenter)
        no_button.clicked.connect(self.close)
        yes_button.clicked.connect(self.on_yes_at_confirmation)

    def on_yes_at_confirmation(self):
        db = db_manager.DB_Manager()
        db.enable_foreign_keys()
        db.edit_comp_name_everywhere(
            comp_old_sql_name=self.comp_old_sql_name,
            comp_new_sql_name=self.comp_new_sql_name,
            comp_old_display_name=self.comp_old_display_name,
            comp_new_display_name=self.comp_new_display_name,
        )
        message = f"{self.comp_old_display_name} a {self.comp_new_display_name}"
        db.log_new_config_record(config="Edición de componente", details=message)
        db.close_connection()
        admin_window = self.parent().parent().parent().parent().parent()
        admin_window.statusbar.show_quick_message("Componente editado: " + message)
        admin_window.start_screen.rebuild_main_section()

        QtWidgets.QApplication.processEvents()  # enables scrolling
        table = admin_window.start_screen.main_section.table
        utils.scroll_to_row_in_table(table, self.comp_new_display_name)

        self.close()
        self.parent().close()
        self.parent().parent().close()
