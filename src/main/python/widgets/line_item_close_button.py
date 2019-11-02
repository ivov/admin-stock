from PyQt5 import QtWidgets


class LineItemCloseButton(QtWidgets.QPushButton):
    """A QPushButton that is a tiny cross for closing a single line item."""

    def __init__(self, holder):
        super(LineItemCloseButton, self).__init__()
        self.holder = holder
        self.setText("×")
        self.setFixedWidth(20)
        self.clicked.connect(self.remove_line_item_in_holder)

    def remove_line_item_in_holder(self):
        for layout in self.holder.children():
            if layout.itemAt(2).widget() == self.sender():
                while layout.count():
                    child = layout.takeAt(0)
                    if child.widget():
                        child.widget().deleteLater()

                layout.setParent(None)
