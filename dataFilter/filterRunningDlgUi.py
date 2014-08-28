# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'filterRunningDlg.ui'
#
# Created: Tue Jan 14 16:08:14 2014
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

class Ui_FilterRunningDlg(object):
    def setupUi(self, FilterRunningDlg):
        FilterRunningDlg.setObjectName(_fromUtf8("FilterRunningDlg"))
        FilterRunningDlg.resize(300, 113)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(FilterRunningDlg.sizePolicy().hasHeightForWidth())
        FilterRunningDlg.setSizePolicy(sizePolicy)
        FilterRunningDlg.setMinimumSize(QtCore.QSize(300, 113))
        FilterRunningDlg.setMaximumSize(QtCore.QSize(300, 120))
        self.verticalLayout = QtGui.QVBoxLayout(FilterRunningDlg)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.label = QtGui.QLabel(FilterRunningDlg)
        self.label.setObjectName(_fromUtf8("label"))
        self.verticalLayout.addWidget(self.label)
        self.txtFileName = QtGui.QLabel(FilterRunningDlg)
        self.txtFileName.setText(_fromUtf8(""))
        self.txtFileName.setObjectName(_fromUtf8("txtFileName"))
        self.verticalLayout.addWidget(self.txtFileName)
        self.progressBar = QtGui.QProgressBar(FilterRunningDlg)
        self.progressBar.setMaximum(100)
        self.progressBar.setProperty("value", 0)
        self.progressBar.setObjectName(_fromUtf8("progressBar"))
        self.verticalLayout.addWidget(self.progressBar)
        spacerItem = QtGui.QSpacerItem(20, 20, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)

        self.retranslateUi(FilterRunningDlg)
        QtCore.QMetaObject.connectSlotsByName(FilterRunningDlg)

    def retranslateUi(self, FilterRunningDlg):
        FilterRunningDlg.setWindowTitle(_translate("FilterRunningDlg", "滤波...", None))
        self.label.setText(_translate("FilterRunningDlg", "正在滤波...", None))

