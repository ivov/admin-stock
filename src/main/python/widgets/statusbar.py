from PyQt5 import QtWidgets, QtCore
from utils import db_manager
from utils.styling import (
    statusbar_style,
    statusbar_first_label_style,
    statusbar_bold_label_style,
    statusbar_last_label_style,
    statusbar_during_quick_message_style,
    statusbar_quick_message_label_style,
)


class StatusBar(QtWidgets.QStatusBar):
    def __init__(self):
        super(StatusBar, self).__init__()

        self.setSizeGripEnabled(False)
        self.setStyleSheet(statusbar_style)

        self.settings = QtCore.QSettings("solutronic", "admin_stock")
        self.db_location = self.settings.value("db_location")
        self.username = self.settings.value("username")

        db = db_manager.DB_Manager()
        component_total, recipe_total = db.get_totals_for_components_and_recipes()
        db.close_connection()

        statusbar_label_text_and_style = {
            "Base:": statusbar_first_label_style,
            self.db_location: "",
            "Componentes:": statusbar_bold_label_style,
            component_total: "",
            "Recetas:": statusbar_bold_label_style,
            recipe_total: "",
            "Usuario:": statusbar_bold_label_style,
            self.username: statusbar_last_label_style,
        }

        for text, style in statusbar_label_text_and_style.items():
            label = QtWidgets.QLabel(text)
            label.setStyleSheet(style)
            if text == "Base:" or text == self.db_location:
                self.addWidget(label)
            elif text != "Base:":
                self.addPermanentWidget(label)

        for i in self.layout().children():
            i.setSpacing(0)

    def show_quick_message(self, quick_message):
        self.setStyleSheet(statusbar_during_quick_message_style)
        for i in self.children():
            if not isinstance(i, QtWidgets.QVBoxLayout):
                self.removeWidget(i)

        quick_message_label = QtWidgets.QLabel(quick_message)
        quick_message_label.setStyleSheet(statusbar_quick_message_label_style)
        self.addWidget(quick_message_label)
        QtCore.QTimer.singleShot(5000, self.reset_statusbar)

    def reset_statusbar(self):
        self.parent().set_statusbar()
