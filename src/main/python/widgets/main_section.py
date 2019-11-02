import os
from PyQt5 import QtWidgets, QtCore, QtGui
import qtawesome as qta
from widgets.dialogs.critical_components_dialog import CriticalCompsDialog
from widgets.dialogs.excluded_components_dialog import ExcludedCompsDialog
from widgets.dialogs.movements_dialog import MovementsDialog
from widgets.dialogs.component_details_dialog import ComponentDetailsDialog
from widgets.dialogs.configs_dialog import ConfigsDialog
from widgets.spec_fields import AutocapField
from utils import db_manager
from utils import utils_collection as utils
from utils.styling import (
    main_section_table_style,
    main_section_title_style,
    main_section_menu_style,
)


class MainSection(QtWidgets.QWidget):
    def __init__(self):
        super(MainSection, self).__init__()

        self.selected_comp_display = ""
        self.selected_comp_SQL = ""

        title = QtWidgets.QLabel("Resumen de componentes")
        title.setStyleSheet(main_section_title_style)
        title.setAlignment(QtCore.Qt.AlignCenter)

        self.searchbar = AutocapField("Buscar componente...")
        self.searchbar.set_completer(source="comps in stock")

        sb_shortcut = QtWidgets.QShortcut(QtGui.QKeySequence("Alt+b"), self.searchbar)
        sb_shortcut.activated.connect(self.searchbar.setFocus)

        self.update_button = QtWidgets.QPushButton("Actualizado")
        self.update_button.setShortcut("Alt+a")
        self.update_button.setFixedWidth(110)
        self.update_button.setEnabled(False)

        primary_button = QtWidgets.QToolButton()
        primary_button.setIcon(qta.icon("mdi.view-list"))
        primary_button.setText("Cuadro de inventario")
        primary_button.setShortcut("Alt+p")

        secondary_button = QtWidgets.QToolButton()
        secondary_button.setIcon(qta.icon("mdi.file-tree"))
        secondary_button.setText("Cuadros secundarios")
        secondary_button.setShortcut("Alt+s")

        for i in [primary_button, secondary_button]:
            i.setIconSize(QtCore.QSize(42, 42))
            i.setToolButtonStyle(QtCore.Qt.ToolButtonTextUnderIcon)
            i.setSizePolicy(
                QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding
            )
            i.setPopupMode(QtWidgets.QToolButton.InstantPopup)
            i.setFixedHeight(70)
            i.setFixedWidth(126)

        primary_menu = QtWidgets.QMenu()
        primary_menu_item_1 = primary_menu.addAction("Resaltar críticos")
        primary_menu_item_2 = primary_menu.addAction("Resaltar excluidos")
        primary_menu_item_3 = primary_menu.addAction("Exportar datos")
        primary_menu.setStyleSheet(main_section_menu_style)
        primary_button.setMenu(primary_menu)

        secondary_menu = QtWidgets.QMenu()
        secondary_menu.setStyleSheet(main_section_menu_style)
        secondary_menu_item_1 = secondary_menu.addAction("Movimientos")
        secondary_menu_item_2 = secondary_menu.addAction("Configuraciones")
        secondary_button.setMenu(secondary_menu)

        horizontal_section_layout = QtWidgets.QHBoxLayout()
        horizontal_section_layout.addWidget(self.searchbar)
        horizontal_section_layout.addWidget(self.update_button)

        table_layout = QtWidgets.QVBoxLayout()
        self.table = QtWidgets.QTableWidget()
        self.table.setStyleSheet(main_section_table_style)
        self.table.setColumnCount(6)
        self.table.setFixedHeight(355)
        self.table.setFocusPolicy(QtCore.Qt.NoFocus)
        self.table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.table.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)
        self.table.verticalHeader().setVisible(False)
        self.main_section_header_labels = [
            "Componente",
            "Total",
            "Depósito",
            "Karina",
            "Brid",
            "Tercero",
        ]
        self.table.setHorizontalHeaderLabels(self.main_section_header_labels)
        self.table.horizontalHeader().setDefaultSectionSize(70)

        self.table.horizontalHeader().setSectionResizeMode(
            0, QtWidgets.QHeaderView.Stretch
        )
        self.table.horizontalHeader().setSectionResizeMode(
            1, QtWidgets.QHeaderView.Fixed
        )
        self.table.horizontalHeader().setSectionResizeMode(
            2, QtWidgets.QHeaderView.Fixed
        )
        self.table.horizontalHeader().setSectionResizeMode(
            3, QtWidgets.QHeaderView.Fixed
        )
        self.table.horizontalHeader().setSectionResizeMode(
            4, QtWidgets.QHeaderView.Fixed
        )
        self.table.horizontalHeader().setSectionResizeMode(
            5, QtWidgets.QHeaderView.Fixed
        )

        for i in range(6):
            self.table.horizontalHeaderItem(i).setTextAlignment(QtCore.Qt.AlignHCenter)

        table_layout.addWidget(self.table)
        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        header_layout = QtWidgets.QHBoxLayout()
        header_left_layout = QtWidgets.QVBoxLayout()
        header_right_layout = QtWidgets.QHBoxLayout()
        header_left_layout.addWidget(title)
        header_left_layout.addLayout(horizontal_section_layout)
        header_right_layout.addWidget(primary_button)
        header_right_layout.addWidget(secondary_button)
        header_layout.addLayout(header_left_layout)
        header_layout.addLayout(header_right_layout)

        layout.addLayout(header_layout)
        layout.addLayout(table_layout)

        self.setLayout(layout)

        db = db_manager.DB_Manager()
        total_table_count = db.get_total_table_count()
        stocks_1 = db.get_stocks_for_owner("stock_valdenegro")
        stocks_2 = db.get_stocks_for_owner("stock_karina")
        stocks_3 = db.get_stocks_for_owner("stock_brid")
        stocks_4 = db.get_stocks_for_owner("stock_tercero")
        self.all_components_display = db.get_all_display_names_for_components()
        self.stored_criticals = db.get_stored_criticals()
        self.unused_comps = db.get_components_not_in_use()
        db.close_connection()

        settings = QtCore.QSettings("solutronic", "admin_stock")
        self.excluded_state = settings.value("excluded_checkbox")

        stocks_g = []
        for i in range(total_table_count):
            result = stocks_1[i] + stocks_2[i] + stocks_3[i] + stocks_4[i]
            stocks_g.append(result)

        self.table.setRowCount(total_table_count)

        stocks_g_display = [utils.format_number_for_display(i) for i in stocks_g]
        stocks_1_display = [utils.format_number_for_display(i) for i in stocks_1]
        stocks_2_display = [utils.format_number_for_display(i) for i in stocks_2]
        stocks_3_display = [utils.format_number_for_display(i) for i in stocks_3]
        stocks_4_display = [utils.format_number_for_display(i) for i in stocks_4]

        for count, value in enumerate(
            [
                self.all_components_display,
                stocks_g_display,
                stocks_1_display,
                stocks_2_display,
                stocks_3_display,
                stocks_4_display,
            ]
        ):
            utils.populate_table_column_with_list_of_strings(
                table=self.table, col_num=count, input_list=value
            )

        utils.color_criticals_in_orange_in_main_section(
            self.table, self.stored_criticals
        )
        utils.color_zeros_in_grey_in_main_section(self.table, self.stored_criticals)
        utils.color_excluded_in_yellow_in_main_section(
            self.table, self.excluded_state, self.unused_comps
        )

        self.searchbar.returnPressed.connect(self.get_searched_component)
        primary_menu_item_1.triggered.connect(lambda: CriticalCompsDialog(self).exec_())
        primary_menu_item_2.triggered.connect(lambda: ExcludedCompsDialog(self).exec_())
        primary_menu_item_3.triggered.connect(self.export_to_spreadsheet)
        secondary_menu_item_1.triggered.connect(lambda: MovementsDialog(self).exec_())
        secondary_menu_item_2.triggered.connect(lambda: ConfigsDialog(self).exec_())
        self.table.horizontalHeader().sortIndicatorChanged.connect(
            self.sort_components_alphabetically
        )
        self.table.cellDoubleClicked.connect(self.open_component_details)

    def get_searched_component(self):
        if self.searchbar.text() not in self.all_components_display:
            return
        for i in range(self.table.rowCount()):
            for j in range(self.table.columnCount()):
                if self.table.item(i, 0).background().color() != QtGui.QColor("orange"):
                    if self.table.item(i, 0).background().color() != QtGui.QColor(
                        "yellow"
                    ):
                        self.table.item(i, j).setBackground(QtGui.QColor("white"))

        found_item_list = self.table.findItems(
            self.searchbar.text(), QtCore.Qt.MatchExactly
        )
        found_item = found_item_list[0]
        self.table.scrollToItem(found_item, QtWidgets.QAbstractItemView.PositionAtTop)
        utils.give_light_blue_color_to_found_item_row(self.table, found_item)

    def export_to_spreadsheet(self):
        from pandas import DataFrame, ExcelWriter
        from datetime import datetime

        num_rows = self.table.rowCount()
        num_cols = self.table.columnCount()
        df = DataFrame(columns=self.main_section_header_labels, index=range(num_rows))
        for i in range(num_rows):
            for j in range(num_cols):
                df.iloc[(i, j)] = self.table.item(i, j).text()

        date = datetime.now().strftime("%d-%m-%Y")
        filepath_and_name = f"output\\RESUMEN DE STOCK {date}.xlsx"
        writer = ExcelWriter(filepath_and_name)
        df.to_excel(writer, "Hoja1", index=False)
        writer.sheets["Hoja1"].column_dimensions["A"].width = 30
        writer.save()
        os.startfile(filepath_and_name)

        statusbar = self.parent().parent().statusbar
        statusbar.show_quick_message("Resumen exportado")

    def sort_components_alphabetically(self, logical_index):
        if logical_index == 0:
            self.table.setSortingEnabled(True)
            self.table.horizontalHeader().setSortIndicatorShown(False)
        if logical_index != 0:
            self.table.setSortingEnabled(False)

    def open_component_details(self, row, col):
        if col == 0:
            self.selected_comp_display = self.table.item(row, col).text()
            db = db_manager.DB_Manager()
            self.selected_comp_SQL = db.get_SQL_name_for_component(
                self.selected_comp_display
            )
            db.close_connection()
        ComponentDetailsDialog(self).exec_()
