# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'wingWin_ui.ui'
#
# Created: Sat Feb 22 21:30:38 2014
#      by: PyQt4 UI code generator 4.9.6
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName(_fromUtf8("Dialog"))
        Dialog.resize(905, 675)
        self.graphicsView = QtGui.QGraphicsView(Dialog)
        self.graphicsView.setGeometry(QtCore.QRect(9, 9, 256, 192))
        self.graphicsView.setObjectName(_fromUtf8("graphicsView"))
        self.imagewidget = ImageWidget(Dialog)
        self.imagewidget.setGeometry(QtCore.QRect(290, 10, 291, 191))
        self.imagewidget.setOrientation(QtCore.Qt.Vertical)
        self.imagewidget.setObjectName(_fromUtf8("imagewidget"))
        self.curvewidget = CurveWidget(Dialog)
        self.curvewidget.setGeometry(QtCore.QRect(620, 10, 241, 211))
        self.curvewidget.setOrientation(QtCore.Qt.Horizontal)
        self.curvewidget.setObjectName(_fromUtf8("curvewidget"))
        self.mplwidget = MatplotlibWidget(Dialog)
        self.mplwidget.setGeometry(QtCore.QRect(0, 230, 311, 231))
        self.mplwidget.setObjectName(_fromUtf8("mplwidget"))
        self.qwtPlot = Qwt5.QwtPlot(Dialog)
        self.qwtPlot.setGeometry(QtCore.QRect(540, 260, 281, 161))
        self.qwtPlot.setObjectName(_fromUtf8("qwtPlot"))
        self.AnalogClock = Qwt5.QwtAnalogClock(Dialog)
        self.AnalogClock.setGeometry(QtCore.QRect(30, 500, 151, 151))
        self.AnalogClock.setLineWidth(4)
        self.AnalogClock.setObjectName(_fromUtf8("AnalogClock"))
        self.Compass = Qwt5.QwtCompass(Dialog)
        self.Compass.setGeometry(QtCore.QRect(220, 490, 151, 151))
        self.Compass.setLineWidth(4)
        self.Compass.setObjectName(_fromUtf8("Compass"))
        self.Thermo = Qwt5.QwtThermo(Dialog)
        self.Thermo.setGeometry(QtCore.QRect(390, 480, 71, 151))
        self.Thermo.setObjectName(_fromUtf8("Thermo"))
        self.Wheel = Qwt5.QwtWheel(Dialog)
        self.Wheel.setGeometry(QtCore.QRect(510, 470, 151, 31))
        self.Wheel.setObjectName(_fromUtf8("Wheel"))
        self.label = QtGui.QLabel(Dialog)
        self.label.setGeometry(QtCore.QRect(80, 210, 131, 16))
        self.label.setObjectName(_fromUtf8("label"))
        self.label_2 = QtGui.QLabel(Dialog)
        self.label_2.setGeometry(QtCore.QRect(370, 210, 131, 16))
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.label_3 = QtGui.QLabel(Dialog)
        self.label_3.setGeometry(QtCore.QRect(690, 230, 131, 16))
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.label_4 = QtGui.QLabel(Dialog)
        self.label_4.setGeometry(QtCore.QRect(80, 470, 131, 16))
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.label_5 = QtGui.QLabel(Dialog)
        self.label_5.setGeometry(QtCore.QRect(370, 420, 131, 16))
        self.label_5.setObjectName(_fromUtf8("label_5"))
        self.label_6 = QtGui.QLabel(Dialog)
        self.label_6.setGeometry(QtCore.QRect(660, 430, 131, 16))
        self.label_6.setObjectName(_fromUtf8("label_6"))
        self.label_8 = QtGui.QLabel(Dialog)
        self.label_8.setGeometry(QtCore.QRect(60, 650, 131, 16))
        self.label_8.setObjectName(_fromUtf8("label_8"))
        self.label_9 = QtGui.QLabel(Dialog)
        self.label_9.setGeometry(QtCore.QRect(250, 650, 131, 16))
        self.label_9.setObjectName(_fromUtf8("label_9"))
        self.label_10 = QtGui.QLabel(Dialog)
        self.label_10.setGeometry(QtCore.QRect(410, 650, 131, 16))
        self.label_10.setObjectName(_fromUtf8("label_10"))
        self.label_11 = QtGui.QLabel(Dialog)
        self.label_11.setGeometry(QtCore.QRect(550, 530, 131, 16))
        self.label_11.setObjectName(_fromUtf8("label_11"))

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(_translate("Dialog", "Dialog", None))
        self.label.setText(_translate("Dialog", "Graphics View", None))
        self.label_2.setText(_translate("Dialog", "ImageWidget", None))
        self.label_3.setText(_translate("Dialog", "CurveWidget", None))
        self.label_4.setText(_translate("Dialog", "MatplotlibWidget", None))
        self.label_5.setText(_translate("Dialog", "QVTKWidget", None))
        self.label_6.setText(_translate("Dialog", "QwtPlot", None))
        self.label_8.setText(_translate("Dialog", "QwtAnalogClock", None))
        self.label_9.setText(_translate("Dialog", "QwtCompass", None))
        self.label_10.setText(_translate("Dialog", "QwtThermo", None))
        self.label_11.setText(_translate("Dialog", "QwtWheel", None))

from PyQt4 import Qwt5
from matplotlibwidget import MatplotlibWidget
from guiqwt.plot import CurveWidget, ImageWidget
