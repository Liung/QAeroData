#coding: UTF-8
__author__ = 'Vincent'
__appname__ = u'批处理滤波工具'

from PyQt4.QtGui import *
from PyQt4.QtCore import *
import sys
from dataFilterBatchUi import Ui_dataFilterBatch
from dataFilter import DataFilter

text = u'''<P>本工具支持批处理滤波文件。
    <p>如果需要显示波形，则每次需要手动关闭波形图才能进行下一步的滤波处理。
    所以，批处理时一般请不要勾选显示波形图。'''


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
        self.txtRawFiles.clear()
        self._rawFiles = rawFiles
        self.txtRawFiles.addItems(rawFiles)
        self.updateFilterFiles()

    @pyqtSignature("")
    def on_btnBatchFilterFilesClear_clicked(self):
        self.txtRawFiles.clear()
        self.txtFilterFiles.clear()
        self._rawFiles.clear()

    def updateFilterFiles(self):
        if len(self._rawFiles) == 0 or \
                self.txtFilterFilesDirectory.text().isEmpty():
            return
        self.txtFilterFiles.clear()
        for fn in self._rawFiles:
            rawFn = QFileInfo(fn)
            tempFn = rawFn.completeBaseName() + "F." + rawFn.suffix().toLower()
            newDir = self.txtFilterFilesDirectory.text()
            newFn = newDir + '\\' + tempFn
            self._filterFiles.append(newFn)
            item = QListWidgetItem(newFn)
            self.txtFilterFiles.addItem(item)
        return

    @pyqtSignature("")
    def on_btnBatchFilterStart_clicked(self):
        if self.txtRawFiles.count() == 0:
            QMessageBox.about(self, u"{0} -- {1}".format(qApp.applicationName(),
                                                         __appname__),
                              u"请输入滤波文件列表")
            return
        if self.txtFilterFilesDirectory.text().isEmpty():
            QMessageBox.warning(self, u"{0} -- {1}".format(qApp.applicationName(),
                                                           __appname__),
                                u"请选择一个滤波后文件的存储目录")
            return
        try:
            sampleRate = float(self.txtBatchSampleRate.text())
            cutoffFre = float(self.txtBatchCutoffFre.text())
            fileNums = len(self._filterFiles)
            filterOrder = self.spbBatchFilterOrders.value()
            headerNums = self.spbFilterHeaderNums.value()

            progress = QProgressDialog(self)
            progress.setLabelText("Filting:...")
            progress.setRange(0, fileNums - 1)
            progress.setModal(True)
            for i in xrange(fileNums):
                progress.setValue(i)
                rawFile = unicode(self._rawFiles[i])    # np.loadtxt载入的文件名需要python字符串类型
                filterFile = unicode(self._filterFiles[i])
                progress.setLabelText(QString("Filting: \n\t%1").arg(rawFile))
                qApp.processEvents()
                if progress.wasCanceled():
                    return
                dataFilter = DataFilter(samplingRate=sampleRate,
                                        filterOrder=filterOrder,
                                        cutoffFre=cutoffFre)
                dataFilter.setFileFormat(rawFile, filterFile, headerNums)
                dataFilter.toDataFile()

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
