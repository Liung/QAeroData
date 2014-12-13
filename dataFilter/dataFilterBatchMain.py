#coding: UTF-8
__author__ = 'Vincent'
__appname__ = u'多文件巴特沃斯低通滤波工具'

from PyQt4.QtGui import *
from PyQt4.QtCore import *
import sys
from dataFilterBatchUi import Ui_dataFilterBatch
from dataFilter import DataFilter

text = u'''<P>本工具支持批处理滤波文件。但文件滤波工具适用于单个文件滤波及参数调节；
    <p>多文件滤波默认关闭波形图，以便节省内存，使滤波更快进行。'''


class DataFilterBatchWidget(QDialog, Ui_dataFilterBatch):
    def __init__(self, parent=None):
        super(QDialog, self).__init__(parent)
        self.setupUi(self)
        self.setWindowTitle(u"{0} --  {1}".format(qApp.applicationName(),
                                                  __appname__))
        self.txtRawFiles.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        self.txtFilterFiles.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)

        self.txtBatchSampleRate.setValidator(QDoubleValidator())
        self.txtBatchCutoffFre.setValidator(QDoubleValidator())

        self._rawFiles = QStringList()
        self._filterFiles = QStringList()

    @pyqtSignature("")
    def on_btnFilterFilesDirectory_clicked(self):
        fileDir = QFileDialog.getExistingDirectory(self,
                                                   u"{0} -- {1}".format(qApp.applicationName(),
                                                                        __appname__),
                                                   directory=QDir.currentPath())
        if not fileDir.isEmpty():
            self.txtFilterFilesDirectory.setText(fileDir)
            self.updateFilterFiles()

    @pyqtSignature("")
    def on_btnBatchFilterFilesAdd_clicked(self):
        rawFiles = QFileDialog.getOpenFileNames(self, u"打开需要滤波的文件...",
                                                directory=QDir.currentPath(),
                                                filter=u"文本文件(*.txt);;数据文件(*.dat);;所有文件(*.*)",
                                                selectedFilter=u"文本文件(*.txt)")
        if len(rawFiles) == 0:
            return

        self.txtRawFiles.addItems(rawFiles)
        self.updateFilterFiles()

    @pyqtSignature("")
    def on_btnBatchFilterFilesClear_clicked(self):
        self.txtRawFiles.clear()
        self.txtFilterFiles.clear()

    def updateFilterFiles(self):

        if self.txtRawFiles.count() == 0 or \
                self.txtFilterFilesDirectory.text().isEmpty():
            return
        self.txtFilterFiles.clear()
        for i in range(self.txtRawFiles.count()):
            fn = self.txtRawFiles.item(i).text()
            rawFn = QFileInfo(fn)
            tempFn = rawFn.completeBaseName() + "F." + rawFn.suffix().toLower()
            newDir = self.txtFilterFilesDirectory.text()
            newFn = newDir + '\\' + tempFn
            item = QListWidgetItem(newFn)
            self.txtFilterFiles.addItem(item)
        return

    @pyqtSignature("")
    def on_btnBatchFilterStart_clicked(self):

        if self.txtRawFiles.count() == 0:
            return

        if self.txtFilterFilesDirectory.text().isEmpty():
            QMessageBox.warning(self, u"{0} -- {1}".format(qApp.applicationName(),
                                                           __appname__),
                                u"请选择一个滤波后文件的存储目录")
            return

        # starting data-filting
        try:
            sampleRate = float(self.txtBatchSampleRate.text())
            cutoffFre = float(self.txtBatchCutoffFre.text())

            filterOrder = self.spbBatchFilterOrders.value()
            headerNums = self.spbFilterHeaderNums.value()

            fileNums = self.txtRawFiles.count()

            progress = QProgressDialog(self)
            progress.setLabelText("Filting:...")
            progress.setRange(0, fileNums - 1)
            progress.setModal(True)
            for i in xrange(fileNums):
                progress.setValue(i)
                rawFile = unicode(self.txtRawFiles.item(i).text())            # np.loadtxt载入的文件名需要python字符串类型
                filterFile = unicode(self.txtFilterFiles.item(i).text())

                progress.setLabelText(QString("Filting: \n\t%1").arg(rawFile))
                qApp.processEvents()
                if progress.wasCanceled():
                    return
                dataFilterObj = DataFilter(samplingRate=sampleRate,
                                           filterOrder=filterOrder,
                                           cutoffFre=cutoffFre)
                dataFilterObj.setRawFile(rawFile)
                dataFilterObj.setFiltFile(filterFile)
                dataFilterObj.setHeaderRows(headerNums)

                dataFilterObj.toDataFile()

            QMessageBox.about(self, u"{0} -- {1}".format(qApp.applicationName(), __appname__),
                              u"滤波完成")
        except Exception, msg:
            QMessageBox.about(self, u"{0} -- {1}".format(qApp.applicationName(), __appname__),
                              u"文件%s滤波失败\n%s" % (rawFile, msg))

    @pyqtSignature("")
    def on_btnBatchFilterAbout_clicked(self):
        QMessageBox.about(self, u"注意...", text)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    dataFilter = DataFilterBatchWidget()
    dataFilter.show()
    app.exec_()
