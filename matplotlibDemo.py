#coding: UTF-8
__author__ = 'LC'

import sys
from PyQt4.QtGui import QApplication, QMainWindow, \
	QWidget, QVBoxLayout,QSizePolicy, QDockWidget, QTextBrowser
from PyQt4 import QtCore
from PyQt4.QtCore import Qt, QSize
import numpy as np
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt4agg \
	import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg \
	import NavigationToolbar2QTAgg as NavigationToolbar


class Qt4MplCanvas(FigureCanvas):
	def __init__(self, parent=None):
		self.fig = Figure()
		# self.axes = self.fig.add_subplot(111)
		self.x = np.arange(0.0, 3.0, 0.01)
		self.y = np.cos(2*np.pi*self.x)
		# self.axes.plot(self.x, self.y)

		FigureCanvas.__init__(self, self.fig)
		self.setParent(parent)

		self.setMinimumSize(QSize(100,100))
		FigureCanvas.setSizePolicy(self,
		                           QSizePolicy.Expanding,
		                           QSizePolicy.Expanding)
		FigureCanvas.updateGeometry(self)

class MplWithToolbar(QWidget):
	def __init__(self):
		vbl = QVBoxLayout()
		qmc = Qt4MplCanvas(self)
		ntb = NavigationToolbar(qmc, self)

		vbl.addWidget(qmc)
		vbl.addWidget(ntb)

		self.setLayout(vbl)


class MplMainWindow(QMainWindow):
	def __init__(self):
		QMainWindow.__init__(self)
		self.setWindowTitle("Maplotlib Demo")

		self.mainWidget = QWidget()
		vbl = QVBoxLayout()
		qmc = Qt4MplCanvas(self.mainWidget)
		ntb = NavigationToolbar(qmc, self.mainWidget)

		vbl.addWidget(qmc)
		vbl.addWidget(ntb)
		widget = QWidget()
		widget.setLayout(vbl)

		# self.mainWidget.setFocus()
		dock1 = QDockWidget('Picture')
		dock1.setWidget(widget)
		dock2 = QDockWidget('Toolbar')
		dock2.setWidget(ntb)
		self.setCentralWidget(QTextBrowser())
		self.addDockWidget(Qt.RightDockWidgetArea, dock2)
		self.addDockWidget(Qt.RightDockWidgetArea, dock1)

qApp = QApplication(sys.argv)
mpl = MplMainWindow()
mpl.show()
sys.exit(qApp.exec_())
