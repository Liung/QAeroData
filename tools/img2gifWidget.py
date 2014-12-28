# -*-coding: utf-8 -*-
__author__ = 'LC'

import sys
import img2gif
from PyQt4.QtGui import (QDialog, QListWidget, QLabel,QLineEdit, QPushButton,
                         QVBoxLayout, QHBoxLayout, QSpinBox, QDoubleSpinBox,
                         QApplication, QDialogButtonBox, QFileDialog, qApp,
                         QMessageBox)
from PyQt4.QtCore import (QFileInfo, )


class Img2GifWidget(QDialog):
    AppName = u"GIF生成工具"
    
    def __init__(self, parent=None):
        super(Img2GifWidget, self).__init__(parent)
        self.setWindowTitle(Img2GifWidget.AppName)

        self.listWidget = QListWidget()
        self.listWidget.setMinimumSize(400, 300)
        self.btnAdd = QPushButton("&Add")
        self.btnUp = QPushButton("&Up")
        self.btnDown = QPushButton("&Down")
        self.btnDel = QPushButton("&Delete")
        self.btnClear = QPushButton("&Clear")
        topLeftLay = QVBoxLayout()
        topLeftLay.addWidget(self.btnAdd)
        topLeftLay.addWidget(self.btnUp)
        topLeftLay.addWidget(self.btnDown)
        topLeftLay.addWidget(self.btnDel)
        topLeftLay.addWidget(self.btnClear)
        topLeftLay.addStretch()
        topLay = QHBoxLayout()
        topLay.addWidget(self.listWidget)
        topLay.addLayout(topLeftLay)
        
        label = QLabel(u"Gif文件路径：")
        self.txtGifPath = QLineEdit()
        self.btnBrowser = QPushButton('...')
        midLay = QHBoxLayout()
        midLay.addWidget(label)
        midLay.addWidget(self.txtGifPath)
        midLay.addWidget(self.btnBrowser)

        timeLabel = QLabel(u"时间间隔：")
        self.spbTime = QDoubleSpinBox()
        self.spbTime.setRange(0.001, 10)
        self.spbTime.setSingleStep(0.001)
        self.spbTime.setValue(1)
        self.spbTime.setSuffix('s')
        loopLabel = QLabel(u"循环：")
        self.spbLoop = QDoubleSpinBox()
        self.spbLoop = QSpinBox()
        self.spbLoop.setRange(0, 1000)
        self.spbLoop.setSingleStep(1)
        self.spbLoop.setValue(0)
        self.spbLoop.setToolTip(u"0次循环表示永久循环")
        self.spbLoop.setSuffix(u"次")
        self.btnBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        bottomLay = QHBoxLayout()
        bottomLay.addWidget(timeLabel)
        bottomLay.addWidget(self.spbTime)
        bottomLay.addWidget(loopLabel)
        bottomLay.addWidget(self.spbLoop)
        bottomLay.addStretch()
        bottomLay.addWidget(self.btnBox)
        
        mainLay = QVBoxLayout()
        mainLay.addLayout(topLay)
        mainLay.addLayout(midLay)
        mainLay.addLayout(bottomLay)
        self.setLayout(mainLay)

        self.btnAdd.clicked.connect(self.itemAdd)
        self.btnUp.clicked.connect(self.itemUp)
        self.btnDown.clicked.connect(self.itemDown)
        self.btnDel.clicked.connect(self.itemDel)
        self.btnClear.clicked.connect(self.listWidget.clear)
        self.btnBrowser.clicked.connect(self.setGifPath)
        self.btnBox.rejected.connect(self.close)
        self.btnBox.accepted.connect(self.makeGif)

        self.txtGifPath.returnPressed.connect(self.updateGifPath)

    def itemAdd(self):
        fileNames = QFileDialog.getOpenFileNames(None, u"{0} -- {1}".format(qApp.applicationName(), Img2GifWidget.AppName),
                                                 '.', u'所有文件(*.*);;BMP文件(*.bmp);;PNG文件(*.png);;JPG文件(*.jpg *.jpeg)')
        for fn in fileNames:
            f = QFileInfo(fn)
            if unicode(f.suffix().toLower()) in ['jpg', 'png', 'bmp', 'jpeg']:
                self.listWidget.addItem(fn)

    def itemUp(self):
        row = self.listWidget.currentRow()
        if row <= 0:
            return
        item = self.listWidget.currentItem()
        self.listWidget.takeItem(row)
        self.listWidget.insertItem(row - 1, item)
        self.listWidget.setCurrentRow(row - 1)

    def itemDown(self):
        rows = self.listWidget.count()
        row = self.listWidget.currentRow()
        if (row < 0) or (row == rows - 1):
            return
        item = self.listWidget.currentItem()
        self.listWidget.takeItem(row)
        self.listWidget.insertItem(row + 1, item)
        self.listWidget.setCurrentRow(row + 1)

    def itemDel(self):
        row = self.listWidget.currentRow()
        if row >= 0:
            self.listWidget.takeItem(row)

    def setGifPath(self):
        filename = QFileDialog.getSaveFileName(self, u"{0} -- {1}".format(qApp.applicationName(), Img2GifWidget.AppName),
                                               ".", "Gif(*.gif)")
        self.txtGifPath.setText(filename)

    def updateGifPath(self):
        fileName = self.txtGifPath.text()
        f = QFileInfo(fileName)
        if f.dir().exists and not f.baseName().isEmpty() and not f.suffix().isEmpty():
            self.txtGifPath.setText(fileName)
            return True
        else:
            QMessageBox.warning(self, u"{0} -- warning".format(Img2GifWidget.AppName),
                                u"要生成的GIF存储路径{0}不是有效的GIF文件".format(unicode(fileName)))
            return False

    def makeGif(self):

        imgs = [unicode(self.listWidget.item(i).text()) for i in range(self.listWidget.count())]
        if len(imgs) <= 1:
            QMessageBox.warning(self, u"{0} - {1}".format(qApp.applicationName(), Img2GifWidget.AppName),
                                u"GIF动画文件必须要给定大于一张图片。")
            return
        if not self.updateGifPath():
            return
        durations = self.spbTime.value()
        loops = self.spbLoop.value()
        ok, msg = img2gif.images2gif(imgs, self.txtGifPath.text(), durations=durations, loops=loops)
        if ok:
            QMessageBox.about(self, u"{0} - {1}".format(qApp.applicationName(), Img2GifWidget.AppName),
                              u"Succeed!\n{0}".format(msg))
            qApp.processEvents()
        else:
            QMessageBox.about(u"{0} - {1}".format(qApp.applicationName(), Img2GifWidget.AppName),
                              u"sorry! Failed to generate the {0}".format(unicode(self.txtGifPath)))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    gif = Img2GifWidget()
    gif.show()
    app.exec_()
