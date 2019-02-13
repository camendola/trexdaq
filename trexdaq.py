import sys
import time

from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QAction, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QSpacerItem, QSizePolicy, QPushButton
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QSize, QThread, pyqtSignal

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import random

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar

import numpy as np

# Basic skeleton adapted from:
# https://stackoverflow.com/questions/48140576/matplotlib-toolbar-in-a-pyqt5-application

class MainWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)

        self.title = 'test'
        self.left = 10
        self.top = 10
        self.width = 800
        self.height = 600

        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        self.statusBar().showMessage('Ready')

        mainMenu = self.menuBar()
        mainMenu.setNativeMenuBar(False)
        fileMenu = mainMenu.addMenu('File')
        helpMenu = mainMenu.addMenu('Help')

        exitButton = QAction(QIcon('exit24.png'), 'Exit', self)
        exitButton.setShortcut('Ctrl+Q')
        exitButton.setStatusTip('Exit application')
        exitButton.triggered.connect(self.close)
        fileMenu.addAction(exitButton)


        widget =  QWidget(self)
        self.setCentralWidget(widget)
        vlay = QVBoxLayout(widget)
        hlay = QHBoxLayout()
        vlay.addLayout(hlay)

        self.nameLabel = QLabel('Name:', self)
        self.line = QLineEdit(self)
        self.nameLabel2 = QLabel('Result', self)

        hlay.addWidget(self.nameLabel)
        hlay.addWidget(self.line)
        hlay.addWidget(self.nameLabel2)
        hlay.addItem(QSpacerItem(1000, 10, QSizePolicy.Expanding))

        pybutton = QPushButton('Click me', self)
        pybutton.clicked.connect(self.clickMethod)
        hlay2 = QHBoxLayout()
        hlay2.addWidget(pybutton)
        hlay2.addItem(QSpacerItem(1000, 10, QSizePolicy.Expanding))
        vlay.addLayout(hlay2)
        self.widgetPlot = WidgetPlot(self)
        vlay.addWidget(self.widgetPlot)

    def clickMethod(self):
        print('Clicked Pyqt button.')

        if self.line.text() == '':
            self.statusBar().showMessage('Not a Number')
        else:
            print('Number: {}'.format(float(self.line.text())*2))
            self.statusBar().showMessage('Introduction of a number')
            self.nameLabel2.setText(str(float(self.line.text())*2))

class WidgetPlot(QWidget):
    def __init__(self, *args, **kwargs):
        QWidget.__init__(self, *args, **kwargs)
        self.setLayout(QVBoxLayout())
        self.canvas = HistCanvas(self, width=10, height=8)
        self.toolbar = NavigationToolbar(self.canvas, self)
        self.layout().addWidget(self.toolbar)
        self.layout().addWidget(self.canvas)

    def foo(self, x):
        self.canvas.figure.clf()
        self.canvas.digitize(x)
        self.canvas.plot()


class HistCanvas(FigureCanvas):
    def __init__(self, parent=None, width=10, height=8, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        FigureCanvas.__init__(self, fig)
        self.setParent(parent)
        FigureCanvas.setSizePolicy(self, QSizePolicy.Expanding, QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

        self.bins = np.linspace(0, 10, 11)
        self.content = np.zeros(12, dtype=np.int)

        self.plot()

    def digitize(self, x):
        self.content[np.digitize(x, self.bins, right=True)] += 1

    def plot(self):
        data = [random.random() for i in range(250)]
        ax = self.figure.add_subplot(111)
        ax.step(self.bins, np.concatenate([[0], self.content[1:-1]]))
        # ax.set_title("Trexdaq Histogram")
        ax.set_ylabel("counts")
        ax.set_ylim(bottom=0.0)
        ax.set_xlim(self.bins[0], self.bins[-1])
        self.draw()

# To get a background thread for acquiring the data, inspired from:
# https://stackoverflow.com/questions/6783194/background-thread-with-qthread-in-pyqt
class AquisitionThread(QThread):

    sig = pyqtSignal(float)

    def run(self):
        # while True:
        for line in sys.stdin:
            # x = input("Get data:")
            # print(x)
            self.sig.emit(float(line))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    thread = AquisitionThread()
    thread.sig.connect(mainWindow.widgetPlot.foo)
    # The thread finishing will not be connected to anything because it is not supposed to finish
    # thread.finished.connect(app.exit)
    thread.start()
    sys.exit( app.exec_())
