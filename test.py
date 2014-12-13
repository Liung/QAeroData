# -*-coding: utf-8 -*-
__author__ = 'LC'

import sys
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from widget import DirectoryViewer

if __name__ == "__main__":
    app = QApplication(sys.argv)
    treeView = DirectoryViewer()
    treeModel = treeView.model
    dockWidgetFileManager = QDockWidget()
    dockWidgetFileManager.setWindowTitle(u"文件管理器")
    dockWidgetFileManager.setObjectName(u"文件管理器")
    dockWidgetFileManager.setWidget(treeView)
    dockWidgetFileManager.show()

    app.exec_()