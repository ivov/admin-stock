import os
import sys
from fbs_runtime.application_context.PyQt5 import ApplicationContext
from PyQt5 import QtWidgets, QtGui, QtCore
from utils import except_hook
from widgets import start_screen, statusbar
from widgets.dialogs.initdb_dialog import InitDBDialog


class AdminWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        sys.excepthook = except_hook.except_hook

        self.settings = QtCore.QSettings("solutronic", "admin_stock")

        self.set_defaults_on_first_boot()
        self.check_if_db_path_is_valid()

        self.setWindowTitle("Administrador de stock v1.0.0")
        self.icon_path = os.getcwd() + "\\src\\main\\resources\\solu_icon.png"
        self.setWindowIcon(QtGui.QIcon(self.icon_path))
        self.setFixedWidth(800)
        self.start_screen = start_screen.StartScreen(self)
        self.setCentralWidget(self.start_screen)
        self.set_statusbar()
        self.center_window()

    def set_statusbar(self):
        self.setStatusBar(None)
        self.statusbar = statusbar.StatusBar()
        self.setStatusBar(self.statusbar)

    def center_window(self):
        window_height = 515
        window_width = 816
        screenGeometry = QtWidgets.QDesktopWidget().screenGeometry()
        x = screenGeometry.width() / 2 - window_width / 2
        y = screenGeometry.height() / 2 - window_height / 2
        self.move(x, y)

    def set_defaults_on_first_boot(self):
        if not self.settings.contains("db_location"):
            default_db_path = os.getcwd() + "\\src\\main\\resources\\comp_stock.db"
            self.settings.setValue("db_location", default_db_path)
        if not self.settings.contains("username"):
            default_username = "Nombre"
            self.settings.setValue("username", default_username)

    def check_if_db_path_is_valid(self):
        db_location = self.settings.value("db_location")
        if not os.path.isfile(db_location):
            InitDBDialog(self).exec_()


if __name__ == "__main__":
    app_context = ApplicationContext()
    window = AdminWindow()
    window.show()
    exit_code = app_context.app.exec_()
    sys.exit(exit_code)
