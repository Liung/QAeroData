# *-.-* coding: UTF-8 *-.-*
__author__ = 'LC'
__appname__ = 'PicConvertor'

import sys
from PyQt4.QtGui import *
from PyQt4.QtCore import *

class PicConvertor(QDialog):
    def __init__(self, parent=None):
        super(PicConvertor, self).__init__(parent)

        self.txtRawFilename = QLineEdit()
        btnRawFilename = QPushButton(u"选择文件...")
        self.txtResultFilename = QLineEdit()
        btnResultFilename = QPushButton(u"存储到...")
        topLay = QGridLayout()
        topLay.addWidget(self.txtRawFilename, 0, 0)
        topLay.addWidget(btnRawFilename, 0, 1)
        topLay.addWidget(self.txtResultFilename, 1, 0)
        topLay.addWidget(btnResultFilename, 1, 1)

        self.lblPicture = QLabel()
        self.lblPicture.setMinimumSize(QSize(500,400))
        pic = QPixmap()

        lbl0 = QLabel(u"原始图像大小(pixel)：")
        self.lblRawSize = QLabel()
        lblUserDefSize = QLabel(u"转换图片大小(pixel)：")
        combUserDefsize = QComboBox()
        combUserDefsize.addItems(["16X16",
                "24X24", "32X32", "64X64", "128X128",
                "256X256", "512X512", "1024X1024", u"用户自定义"])
        combUserDefsize.setCurrentIndex(0)

        self.UDFHeight = QDoubleSpinBox()
        self.UDFHeight.setRange(0, 5000)
        label = QLabel(u"×")
        self.UDFWith = QDoubleSpinBox()
        self.UDFWith.setRange(0, 5000)
        self.UDFHeight.setValue(0)
        self.UDFWith.setValue(0)

        self.UDFSizerWidget = QWidget(self)
        lay = QHBoxLayout()
        lay.addWidget(self.UDFWith)
        lay.addWidget(label)
        lay.addWidget(self.UDFHeight)
        self.UDFSizerWidget.setLayout(lay)
        self.UDFSizerWidget.setEnabled(False)

        self.btnPickConvert = QPushButton(u"转换")

        downRigthLay = QVBoxLayout()
        downRigthLay.addWidget(lbl0)
        space = QSpacerItem(50, 15)
        downRigthLay.addSpacerItem(space)
        downRigthLay.addWidget(self.lblRawSize)
        downRigthLay.addWidget(lblUserDefSize)
        downRigthLay.addSpacerItem(space)
        downRigthLay.addWidget(combUserDefsize)
        downRigthLay.addWidget(self.UDFSizerWidget)
        downRigthLay.addStretch()
        downRigthLay.addWidget(self.btnPickConvert)

        downLay = QHBoxLayout()
        downLay.addWidget(self.lblPicture, 1)
        downLay.addItem(downRigthLay)

        mainLay = QVBoxLayout()
        mainLay.addLayout(topLay)
        mainLay.addLayout(downLay)

        self.setLayout(mainLay)
        self.setWindowTitle(__appname__)

        self.resultImageWidth = 16
        self.resultImageHeigth = 16
        self.rawImage = QImage()
        self.resultImage = QImage()

        btnRawFilename.clicked.connect(self.setRawFilename)
        self.txtRawFilename.editingFinished.connect(self.loadFile)
        btnResultFilename.clicked.connect(self.saveFile)
        combUserDefsize.currentIndexChanged[int].connect(self.setUserDefSize)
        self.btnPickConvert.clicked.connect(self.picConvert)
        self.UDFWith.valueChanged.connect(self.setUserDefWidth)
        self.UDFHeight.valueChanged.connect(self.setUserDefHeight)

    def loadFile(self):
        filename = self.txtRawFilename.text()
        if not filename.isEmpty():
            if QFileInfo(filename).exists():
                self.rawImage = QImage(filename)
                if self.rawImage.isNull():
                    message = "Failed to read {0}".format(filename)
                    QMessageBox.warning(self, __appname__,
                                        message,QMessageBox.Ok)
                    return
                width = self.rawImage.width()
                height = self.rawImage.height()
                self.lblRawSize.setText("{0} X {1}".format(width, height))
                self.UDFWith.setValue(width)
                self.UDFHeight.setValue(height)
                newImage = self.rawImage.scaled(self.lblPicture.width(), self.lblPicture.height(),
                                                Qt.KeepAspectRatio)
                self.lblPicture.setPixmap(QPixmap.fromImage(newImage))
            else:
                QMessageBox.warning(self,__appname__,
                                    u"输入图像文件不存在！")
                return

    def saveFile(self):
        filename = QFileDialog.getSaveFileName(self, u'{0} -- save file'.format(__appname__),
                            self.txtResultFilename.text(),
                            " ".join(["*.{0}".format(pic)
                                      for pic in QImageWriter.supportedImageFormats()]))
        self.txtResultFilename.setText(filename)

    def setRawFilename(self):
        filename = QFileDialog.getOpenFileName(self, u'{0} -- open file'.format(__appname__),
                                               self.txtRawFilename.text(),
                                               " ".join(["*.{0}".format(pic)
                                                         for pic in QImageReader.supportedImageFormats()]))
        self.txtRawFilename.setText(filename)
        self.loadFile()

    def setUserDefSize(self, index):
        factor = [16, 24, 32, 64, 128, 256, 512, 1024]
        try:
            self.UDFSizerWidget.setEnabled(False)
            self.resultImageWidth, self.resultImageHeigth = factor[index], factor[index]
        except:
            self.UDFSizerWidget.setEnabled(True)

    def setUserDefWidth(self):
        self.resultImageWidth = self.UDFWith.value()

    def setUserDefHeight(self):
        self.resultImageHeigth = self.UDFHeight.value()

    def picConvert(self):
        if not self.rawImage.isNull():
            filename = self.txtResultFilename.text()
            if QFileInfo(filename).completeSuffix() in QImageWriter.supportedImageFormats():
                self.resultImage = self.rawImage.scaled(self.resultImageWidth, self.resultImageHeigth)
                self.resultImage.save(filename)
                QMessageBox.information(self, __appname__, u"文件转换成功！")
            else:
                QMessageBox.warning(self, __appname__, u"输出文件错误，请选择正确的输出文件格式！")
        else:
            QMessageBox.warning(self, __appname__, u"请先输入要转换的图片文件！")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    picConvertor = PicConvertor()
    picConvertor.show()
    app.exec_()



