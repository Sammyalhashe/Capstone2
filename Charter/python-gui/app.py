import sys
from PyQt5.QtWidgets import QApplication, QWidget, QGridLayout, QPushButton, \
    QLineEdit, QComboBox
from PyQt5.QtCore import QRect  # pyqtSlot
import pyqtgraph as pg
from pyqtgraph.Qt import QtGui
import zerorpc
import numpy as np
from data import dataRPC

# import threading


class thread_runner(object):
    def __init__(self):
        self.data_rpc = dataRPC()
        # self.thread = threading.Thread(target=self.init_daemon, args=())
        # self.thread.daemon = True
        # self.thread.start()

    def get_rpc(self):
        if not self.data_rpc:
            self.data_rpc = dataRPC()

    def init_daemon(self):
        if not self.data_rpc:
            self.get_rpc()
        s = zerorpc.Server(self.data_rpc)
        s.bind("tcp://0.0.0.0:4242")
        s.run()
        sys.stdout.flush()


class Plotter(QWidget):
    def __init__(self):
        # application init
        super().__init__()
        # self.initThread()
        self.data_rpc = dataRPC()
        self.observer = None
        self.init_UI()

    def initThread(self):
        # self.thread = thread_runner()
        # zerorpc setup
        # self.c = zerorpc.Client()
        # self.c.connect("tcp://0.0.0.0:4242")
        # self.observer = None
        pass

    def init_UI(self):
        # common component init
        self.btn = QPushButton("Start Plotting", self)
        self.Xtext = QLineEdit("Label for x-axis", self)
        self.Ytext = QLineEdit("Label for y-axis", self)

        # combobox init
        self.YcomboBox = QComboBox(self)
        self.YcomboBox.setGeometry(QRect(40, 40, 491, 31))
        self.YcomboBox.setObjectName(("Pick Y Axis"))
        self.initComboBox(self.YcomboBox)
        self.XcomboBox = QComboBox(self)
        self.XcomboBox.setGeometry(QRect(40, 40, 491, 31))
        self.XcomboBox.setObjectName(("Pick X Axis"))
        self.initComboBox(self.XcomboBox)

        # functionality
        self.btn.clicked.connect(lambda _: self.plotData())

        # pyqt graph init
        self.plot = pg.PlotWidget()

        # layout init
        self.layout = QGridLayout()
        self.layout.setSpacing(10)

        # adding the widgets to the layout
        self.layout.addWidget(self.btn, 0, 0)
        self.layout.addWidget(self.YcomboBox, 0, 1)
        self.layout.addWidget(self.XcomboBox, 0, 2)
        self.layout.addWidget(self.Xtext, 1, 0)
        self.layout.addWidget(self.Ytext, 1, 1)
        self.layout.addWidget(self.plot, 2, 0)
        self.layout.setRowStretch(0, 2)

        # application showing
        self.setLayout(self.layout)
        self.setGeometry(300, 300, 550, 450)
        self.setWindowTitle("Plotter")
        self.show()

    def initComboBox(self, box):
        items = ["channel {}".format(i + 1) for i in range(4)]
        for name in items:
            box.addItem(name)

    def getObserver(self):
        if not self.observer:
            self.data_rpc.activateStream()
            self.observer = self.data_rpc.getStream()

    def plotData(self):
        if not self.observer:
            self.getObserver()
        self.data = np.array([])
        self.observer.subscribe_(lambda x: self.addData(x))
        self.data_rpc.getData_test()

    def addData(self, newData):
        self.data = np.append(self.data, newData[0])
        self.plot.plot(self.data)
        QtGui.QApplication.processEvents()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    plotter = Plotter()
    # only exit when the exec_ function is called
    sys.exit(app.exec_())
