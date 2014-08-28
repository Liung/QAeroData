#coding: UTF-8
#__author__ = 'Vincent'
__appname__ = 'Plot'

import sys
from PyQt4.QtGui import *
import numpy as np
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QTAgg as NavigationToolbar


class Qt4MplCanvas(FigureCanvas):
    def __init__(self, parent):
        self.fig = Figure()
        self.fig.set_facecolor('#FFFFFF')
        self.axes = self.fig.add_subplot(111)
        self.axes.grid(True)
        # self.axes.legend()
        # self.xlist
        # self.x, self.y = [], []
        # self.line1, = self.axes.plot(self.x, self.y)

        FigureCanvas.__init__(self, self.fig)
        self.setParent(parent)

        FigureCanvas.setSizePolicy(self, QSizePolicy.Expanding, QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)


class MatplotlibWidget(QWidget):
    def __init__(self, parent=None):
        super(MatplotlibWidget, self).__init__(parent)
        self.setMinimumSize(250, 250)

        self.canvas = Qt4MplCanvas(self)
        ntb = NavigationToolbar(self.canvas, self)

        vbl = QVBoxLayout()
        vbl.addWidget(self.canvas)
        vbl.addWidget(ntb)

        self.setLayout(vbl)
        self.setWindowTitle(u"{0} -- {1}".format(qApp.applicationName(), __appname__))

    def plot(self, newX, newY, label=''):
        self.canvas.axes.plot(newX, newY, label=label)
        self.canvas.axes.grid(True)

    def legend(self):
        self.canvas.axes.legend()

if __name__ == '__main__':
    qApp = QApplication(sys.argv)
    mpl = MatplotlibWidget()
    x = np.sin(np.linspace(0, 2*np.pi, 100))
    y = np.cos(np.linspace(0, 2*np.pi, 100))
    mpl.plot(x, y, "Sin(x)")
    mpl.legend()
    mpl.show()
    sys.exit(qApp.exec_())


