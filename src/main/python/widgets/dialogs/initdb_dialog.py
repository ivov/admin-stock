import os
import sys
from PyQt5 import QtWidgets, QtCore
from utils.styling import initdb_dialog_title_style


class InitDBDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(InitDBDialog, self).__init__(parent)
        self.setWindowFlags(
            QtCore.Qt.Dialog
            | QtCore.Qt.CustomizeWindowHint
            | QtCore.Qt.WindowCloseButtonHint
        )
        self.setFixedHeight(100)

        self.settings = QtCore.QSettings("solutronic", "admin_stock")
        self.db_location = self.settings.value("db_location")

        self.title = QtWidgets.QLabel("Cambiar base de datos")
        self.title.setAlignment(QtCore.Qt.AlignCenter)
        self.title.setStyleSheet(initdb_dialog_title_style)

        if not os.path.isfile(self.db_location):
            self.title.setText("Administrador con ruta desactualizada")

        horizontal_section = QtWidgets.QHBoxLayout()
        location_label = QtWidgets.QLabel("Ubicación:")
        location_label.setAlignment(QtCore.Qt.AlignCenter)

        self.location_field = QtWidgets.QLineEdit()
        self.location_field.setPlaceholderText(self.db_location)
        self.location_field.setReadOnly(True)

        self.set_location_field_width(self.db_location)

        self.examine_button = QtWidgets.QPushButton("Examinar...")
        self.examine_button.setShortcut("Alt+e")

        horizontal_section.addWidget(location_label)
        horizontal_section.addWidget(self.location_field)
        horizontal_section.addWidget(self.examine_button)

        bottom_section = QtWidgets.QHBoxLayout()

        self.close_button = QtWidgets.QPushButton("× Cerrar")
        self.close_button.setShortcut("Alt+c")

        self.save_button = QtWidgets.QPushButton("≡ Guardar")
        self.save_button.setShortcut("Alt+g")
        self.save_button.setEnabled(False)

        bottom_section.addWidget(self.close_button)
        bottom_section.addWidget(self.save_button)

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.title)
        layout.addLayout(horizontal_section)
        layout.addLayout(bottom_section)

        self.setLayout(layout)
        self.center_dialog()

        self.close_button.clicked.connect(self.handle_close)
        self.examine_button.clicked.connect(self.select_db)
        self.save_button.clicked.connect(self.save_selected_db)

    def handle_close(self):
        if not os.path.isfile(self.db_location):
            sys.exit()
        self.close()

    def center_dialog(self):
        dialog_height = 116
        dialog_width = self.location_field.width() + 174
        screenGeometry = QtWidgets.QDesktopWidget().screenGeometry()
        x = screenGeometry.width() / 2 - dialog_width / 2
        y = screenGeometry.height() / 2 - dialog_height / 2
        self.move(x, y)

    def set_location_field_width(self, db_location):
        location_field_length = len(db_location)
        if location_field_length < 25:
            self.location_field.setFixedWidth(150)
        elif location_field_length < 50:
            self.location_field.setFixedWidth(230)
        elif location_field_length > 50:
            self.location_field.setFixedWidth(location_field_length * 6)

    def select_db(self):
        default_db_dirpath = os.getcwd() + "\\src\\main\\resources"
        new_db_location, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, "Elegir base de datos", default_db_dirpath, "Base de datos (*.db)"
        )
        if new_db_location == "":
            return
        self.title.setText("Nueva ruta elegida")
        self.location_field.setPlaceholderText(new_db_location)
        self.set_location_field_width(new_db_location)
        self.center_dialog()
        self.save_button.setEnabled(True)

    def save_selected_db(self):
        if not os.path.isfile(self.db_location):
            new_db_location = self.location_field.placeholderText()
            self.settings.setValue("db_location", new_db_location)
        else:
            new_db_location = self.location_field.placeholderText()
            self.settings.setValue("db_location", new_db_location)
            admin_window = self.parent().parent().parent()
            admin_window.set_statusbar()
        self.close()
