from PyQt5 import QtWidgets
from . import main_column, main_section


class StartScreen(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(StartScreen, self).__init__(parent)
        self.main_column = main_column.MainColumn(self)
        self.main_section = main_section.MainSection()
        self.layout = QtWidgets.QHBoxLayout()
        self.layout_left = QtWidgets.QHBoxLayout()
        self.layout_left.addWidget(self.main_column)
        self.layout_right = QtWidgets.QHBoxLayout()
        self.layout_right.addWidget(self.main_section)
        self.layout.addLayout(self.layout_left)
        self.layout.addLayout(self.layout_right)
        self.setLayout(self.layout)

    def rebuild_main_section(self):
        self.layout_right.takeAt(0).widget().deleteLater()
        self.main_section = main_section.MainSection()
        self.layout_right.addWidget(self.main_section)
