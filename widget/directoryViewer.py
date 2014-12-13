# -*-coding: utf-8 -*-
__author__ = 'LC'

from PyQt4.QtGui import *
from PyQt4.QtCore import *


class DirectoryViewer(QDialog):
    def __init__(self, parent=None):
        super(DirectoryViewer, self).__init__(parent)

        # self.model = QDirModel()
        #  QFileSystemModel(self):这里必须要有参数self
        # 否则会出现：
        # QObject::startTimer: QTimer can only be used with threads started with QThread
        self.model = QFileSystemModel(self)

        self.model.setRootPath(QDir.homePath())
        self.model.setReadOnly(True)
        # self.model.setSorting(QDir.DirsFirst | QDir.IgnoreCase | QDir.Name)

        self.treeView = QTreeView(self)
        self.treeView.setModel(self.model)
        self.treeView.header().setStretchLastSection(True)
        self.treeView.header().setSortIndicator(0, Qt.AscendingOrder)
        self.treeView.header().setClickable(True)

        index = self.model.index(QDir.currentPath())
        self.treeView.expand(index)
        self.treeView.scrollTo(index)
        self.treeView.resizeColumnToContents(0)

        createDirBtn = QPushButton(u'创建新目录')
        removeBtn = QPushButton(u'删除文件或目录')

        createDirBtn.clicked.connect(self.createDirectory)
        removeBtn.clicked.connect(self.remove)

        bottomLay = QHBoxLayout()
        bottomLay.addWidget(createDirBtn)
        bottomLay.addWidget(removeBtn)
        bottomLay.addStretch()

        mainLay = QVBoxLayout()
        mainLay.addWidget(self.treeView)
        # mainLay.addLayout(bottomLay)

        self.setLayout(mainLay)

    def createDirectory(self):
        index = self.treeView.currentIndex()
        if not index.isValid():
            return

        dirName, _ = QInputDialog.getText(self, u"Create a Directory",
                                          u"Directory name:")
        if not dirName.isEmpty():
            if not self.model.mkdir(index, dirName).isValid():
                QMessageBox.information(self, u"Create Directory",
                                        u"Failed to create a directory")

    def remove(self):
        index = self.treeView.currentIndex()
        if not index.isValid():
            return

        if self.model.fileInfo(index).isDir():
            ok = self.model.rmdir(index)
        else:
            ok = self.model.remove(index)

        if not ok:
            QMessageBox.information(self, u'Remove',
                                    u"Failed to0 remove {0}".format(self.model.fileName(index)))

if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    viewer = DirectoryViewer()
    viewer.show()
    app.exec_()

    # self.treeView = QTreeView()
    # self.treeModel = QFileSystemModel()
    # self.treeModel.setRootPath('C:/')
    # self.treeView.setModel(self.treeModel)
    # index = self.treeModel.index(QDir.currentPath())
    # self.treeView.expand(index)
    # self.treeView.scrollTo(index)
    # self.treeView.resizeColumnToContents(0)