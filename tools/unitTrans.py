# -*-coding: utf-8 -*-
__author__ = 'LC'

import sys
from PyQt4.QtGui import *
from PyQt4.QtCore import *


class UnitTransWidget(QDialog):
    def __init__(self, parent=None):
        super(UnitTransWidget, self).__init__(parent)
        listWidget = QListWidget()
        listWidget.addItem(u"长度")
        listWidget.addItem(u"体积")
        listWidget.addItem(u"质量")
        listWidget.addItem(u"压力")
        listWidget.addItem(u"功率")
        listWidget.addItem(u"功/能/热")
        listWidget.addItem(u"力")
        listWidget.addItem(u"时间")
        listWidget.addItem(u"速度")
        listWidget.addItem(u"光照度")
        listWidget.addItem(u"角度")
        listWidget.addItem(u"密度")
        listWidget.addItem(u"数据存储")
        listWidget.addItem(u"立体力学相关")
        listWidget.setFont(QFont(15))
        listWidget.setFixedWidth(100)

        stackedLayout = QStackedLayout()
        stackedLayout.addWidget(QPushButton(u"hello"))
        stackedLayout.addWidget(QPushButton('sdf'))

        listWidget.currentRowChanged[int].connect(stackedLayout.setCurrentIndex)

        lay = QHBoxLayout()
        lay.addWidget(listWidget)
        lay.addLayout(stackedLayout)
        self.setLayout(lay)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    utw = UnitTransWidget()
    utw.show()
    app.exec_()