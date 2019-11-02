from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QSizePolicy
import qtawesome as qta
from widgets.dialogs.outgoing_dialog import OutgoingDialog
from widgets.dialogs.incoming_dialog import IncomingDialog
from widgets.dialogs.create_component_dialog import CreateComponentDialog
from widgets.dialogs.edit_component_dialog import EditComponentDialog
from widgets.dialogs.delete_component_dialog import DeleteComponentDialog
from widgets.dialogs.create_recipe_dialog import CreateRecipeDialog
from widgets.dialogs.edit_recipe_dialog import EditRecipeDialog
from widgets.dialogs.delete_recipe_dialog import DeleteRecipeDialog
from widgets.dialogs.initdb_dialog import InitDBDialog
from widgets.dialogs.rename_user_dialog import RenameUserDialog
from widgets.dialogs.production_report_dialog import ProductionReport
from widgets.dialogs.subtract_component_dialog import SubtractComponentDialog
from widgets.message_boxes import QuestionBox
from utils.styling import main_column_menu_style as menu_style


class MainColumn(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(MainColumn, self).__init__(parent)
        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        incoming_menu = QtWidgets.QMenu()
        inc_menu_item_1 = incoming_menu.addAction("> Ingreso a Depósito")
        inc_menu_item_2 = incoming_menu.addAction("+ Crear componente")
        inc_menu_item_3 = incoming_menu.addAction("~ Editar componente")
        inc_menu_item_4 = incoming_menu.addAction("× Borrar componente")

        outgoing_menu = QtWidgets.QMenu()
        out_menu_item_1 = outgoing_menu.addAction("> Egreso a armador")
        out_menu_item_2 = outgoing_menu.addAction("> Egreso interno")

        recipes_menu = QtWidgets.QMenu()
        recipes_menu_item_1 = recipes_menu.addAction("+ Crear receta")
        recipes_menu_item_2 = recipes_menu.addAction("~ Editar receta")
        recipes_menu_item_3 = recipes_menu.addAction("× Borrar receta")

        database_menu = QtWidgets.QMenu()
        database_menu_item_1 = database_menu.addAction("+ Respaldar base")
        database_menu_item_2 = database_menu.addAction("~ Cambiar base")
        database_menu_item_3 = database_menu.addAction("~ Editar usuario")

        for i in [incoming_menu, outgoing_menu, recipes_menu, database_menu]:
            i.setStyleSheet(menu_style)

        incoming_button = QtWidgets.QToolButton()
        incoming_button.setIcon(qta.icon("mdi.import"))
        incoming_button.setText("Ingreso de componentes")
        incoming_button.setShortcut("Alt+1")
        incoming_button.setMenu(incoming_menu)

        report_button = QtWidgets.QToolButton()
        report_button.setIcon(qta.icon("mdi.content-paste"))
        report_button.setText("Informe de producción")
        report_button.setShortcut("Alt+2")

        outgoing_button = QtWidgets.QToolButton()
        outgoing_button.setIcon(qta.icon("mdi.export"))
        outgoing_button.setText("Egreso de componentes")
        outgoing_button.setShortcut("Alt+3")
        outgoing_button.setMenu(outgoing_menu)

        recipes_button = QtWidgets.QToolButton()
        recipes_button.setIcon(qta.icon("mdi.folder-open"))
        recipes_button.setText("Recetas de productos")
        recipes_button.setShortcut("Alt+4")
        recipes_button.setMenu(recipes_menu)

        database_button = QtWidgets.QToolButton()
        database_button.setIcon(qta.icon("mdi.select-all"))
        database_button.setText("Base de datos")
        database_button.setShortcut("Alt+5")
        database_button.setMenu(database_menu)

        for i in [
            incoming_button,
            report_button,
            outgoing_button,
            recipes_button,
            database_button,
        ]:
            i.setIconSize(QtCore.QSize(44, 44))
            i.setToolButtonStyle(QtCore.Qt.ToolButtonTextUnderIcon)
            i.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
            i.setPopupMode(QtWidgets.QToolButton.InstantPopup)
            i.setFixedWidth(140)
            if i == report_button:
                i.setIconSize(QtCore.QSize(42, 42))
            layout.addWidget(i)

        self.setLayout(layout)

        inc_menu_item_1.triggered.connect(lambda: IncomingDialog(self).exec_())
        inc_menu_item_2.triggered.connect(lambda: CreateComponentDialog(self).exec_())
        inc_menu_item_3.triggered.connect(lambda: EditComponentDialog(self).exec_())
        inc_menu_item_4.triggered.connect(lambda: DeleteComponentDialog(self).exec_())

        report_button.clicked.connect(lambda: ProductionReport(self).exec_())

        out_menu_item_1.triggered.connect(lambda: OutgoingDialog(self).exec_())
        out_menu_item_2.triggered.connect(lambda: SubtractComponentDialog(self).exec_())

        recipes_menu_item_1.triggered.connect(lambda: CreateRecipeDialog(self).exec_())
        recipes_menu_item_2.triggered.connect(lambda: EditRecipeDialog(self).exec_())
        recipes_menu_item_3.triggered.connect(lambda: DeleteRecipeDialog(self).exec_())

        database_menu_item_1.triggered.connect(self.confirm_for_backup)
        database_menu_item_2.triggered.connect(lambda: InitDBDialog(self).exec_())
        database_menu_item_3.triggered.connect(lambda: RenameUserDialog(self).exec_())

    def confirm_for_backup(self):
        box = QuestionBox(
            "Confirmación", "¿Generar copia de seguridad\nde la base de datos?"
        )
        box.exec_()

        if box.clickedButton() == box.button(QtWidgets.QMessageBox.No):
            box.close()
        elif box.clickedButton() == box.button(QtWidgets.QMessageBox.Yes):
            from datetime import datetime
            from shutil import copy2

            settings = QtCore.QSettings("solutronic", "admin_stock")
            db_location = settings.value("db_location")
            db_name = db_location.replace(".db", "")
            dt_stamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
            copy2(db_location, f"{db_name}_{dt_stamp}.db")
            statusbar = self.parent().parent().statusbar
            statusbar.show_quick_message("Copia de seguridad generada")
