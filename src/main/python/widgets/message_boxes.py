from PyQt5 import QtWidgets, QtCore


class QuestionBox(QtWidgets.QMessageBox):
    def __init__(self, title, question):
        QtWidgets.QMessageBox.__init__(
            self, QtWidgets.QMessageBox.Question, title, question
        )
        self.setWindowTitle(title)
        self.setText(question)
        self.setWindowFlags(QtCore.Qt.CustomizeWindowHint | QtCore.Qt.WindowTitleHint)
        self.setStandardButtons(QtWidgets.QMessageBox.No | QtWidgets.QMessageBox.Yes)
        yes_button = self.button(QtWidgets.QMessageBox.Yes)
        yes_button.setText("Sí")


class WarningBox(QtWidgets.QMessageBox):
    def __init__(self, title, warning):
        QtWidgets.QMessageBox.__init__(
            self, QtWidgets.QMessageBox.Warning, title, warning
        )
        self.setWindowTitle(title)
        self.setText(warning)
        self.setWindowFlags(QtCore.Qt.CustomizeWindowHint | QtCore.Qt.WindowTitleHint)


class InformationBox(QtWidgets.QMessageBox):
    def __init__(self, title, information):
        QtWidgets.QMessageBox.__init__(
            self, QtWidgets.QMessageBox.Information, title, information
        )
        self.setWindowTitle(title)
        self.setText(information)
        self.setWindowFlags(QtCore.Qt.CustomizeWindowHint | QtCore.Qt.WindowTitleHint)
