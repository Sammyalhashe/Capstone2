import sys
from PyQt5.QtWidgets import QApplication, QWidget


def test():
    app = QApplication(sys.argv)
    w = QWidget()
    w.setWindowTitle('asdf')
    w.show()

    sys.exit(app.exec_())


test()
