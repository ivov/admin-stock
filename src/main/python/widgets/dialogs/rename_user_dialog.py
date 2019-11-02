from PyQt5 import QtWidgets, QtCore
from utils.styling import rename_user_dialog_title_style


class RenameUserDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(RenameUserDialog, self).__init__(parent)
        self.setWindowFlags(
            QtCore.Qt.Dialog
            | QtCore.Qt.CustomizeWindowHint
            | QtCore.Qt.WindowCloseButtonHint
        )
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setFixedHeight(100)

        self.settings = QtCore.QSettings("solutronic", "admin_stock")
        self.username = self.settings.value("username")

        title = QtWidgets.QLabel("Editar usuario")
        title.setAlignment(QtCore.Qt.AlignCenter)
        title.setStyleSheet(rename_user_dialog_title_style)

        self.name_label = QtWidgets.QLabel("Nombre:")
        self.name_label.setAlignment(QtCore.Qt.AlignCenter)
        self.name_label.setFixedWidth(45)

        self.name_field = QtWidgets.QLineEdit()
        self.name_field.setPlaceholderText("Nombre...")
        self.name_field.setFixedWidth(115)

        horizontal_section = QtWidgets.QHBoxLayout()
        horizontal_section.addWidget(self.name_label)
        horizontal_section.addWidget(self.name_field)

        back_button = QtWidgets.QPushButton("× Cerrar")
        back_button.setShortcut("Alt+c")

        self.save_button = QtWidgets.QPushButton("≡ Guardar")
        self.save_button.setShortcut("Alt+g")
        self.save_button.setEnabled(False)
        self.save_button.setDefault(True)

        bottom_section = QtWidgets.QHBoxLayout()
        bottom_section.addWidget(back_button)
        bottom_section.addWidget(self.save_button)

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(title)
        layout.addLayout(horizontal_section)
        layout.addLayout(bottom_section)

        self.setLayout(layout)

        self.name_field.textChanged.connect(self.on_name_field_change)
        back_button.clicked.connect(self.close)
        self.save_button.clicked.connect(self.save_name_and_update_statusbar)

    def on_name_field_change(self):
        if self.name_field.text() != "":
            self.save_button.setEnabled(True)
        elif self.name_field.text() == "":
            self.save_button.setEnabled(False)

    def save_name_and_update_statusbar(self):
        self.settings.setValue("username", self.name_field.text())
        main_window = self.parent().parent().parent().parent()
        main_window.set_statusbar()

        self.close()
