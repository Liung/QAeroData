#coding: UTF-8
__author__ = 'Vincent'
__appname__ = u'单文件巴特沃斯低通滤波工具'

from PyQt4.QtGui import *
from PyQt4.QtCore import *
from dataFilterUi import Ui_dataFilter
from dataFilter import DataFilter
import sys
sys.path.append("..")
from widget.matplotlibWidget import MatplotlibWidget


class DataFilterWidget(QDialog, Ui_dataFilter):
    def __init__(self, parent=None):
        super(DataFilterWidget, self).__init__(parent)
        self.setupUi(self)
        self.mplTabWidget.hide()
        self.mainLayout.setSizeConstraint(QLayout.SetFixedSize)    # 设置对话框尺寸策略为固定尺寸大小

        self.txtSamplingRate.setValidator(QDoubleValidator())     # 添加验证器
        self.txtCutoffFre.setValidator(QDoubleValidator())
        self.txtRawFile.setReadOnly(True)
        self.txtFilterFile.setReadOnly(True)
        self._dir = "./"
        self._rawFile = ''
        self._filterFile = ''

    @pyqtSignature("")
    def on_btnRawFile_clicked(self):
        rawFile = QFileDialog.getOpenFileName(self,
                                              u"打开需要滤波的文件...", directory=self._dir,
                                              filter=u"文本文件(*.txt);;数据文件(*.dat);;所有文件(*.*)",
                                              selectedFilter=u"文本文件(*.txt)")
        if not rawFile.isEmpty():
            self._dir = rawFile  # 设置文件路径为当前选择目录
            self._rawFile = unicode(rawFile)
            self.txtRawFile.setText(rawFile)

    @pyqtSignature("")
    def on_btnFilterFile_clicked(self):
        filterFile = QFileDialog.getSaveFileName(self,
                                                 u"存储生成滤波之后的文件...", directory=self._dir,
                                                 filter=u"文本文件(*.txt);;数据文件(*.dat);;所有文件(*.*)",
                                                 selectedFilter=u"文本文件(*.txt)")
        if not filterFile.isEmpty():
            self._dir = filterFile  # 设置文件路径为当前选择目录
            self._filterFile = unicode(filterFile)
            self.txtFilterFile.setText(filterFile)

    @pyqtSignature("")
    def on_btnFilterStart_clicked(self):

        samplingRate = float(self.txtSamplingRate.text())
        cutoffFre = float(self.txtCutoffFre.text())
        rawFile = self._rawFile
        filterFile = self._filterFile
        filtOrder = self.spbFilterOrders.value()

        if rawFile == unicode("") or filterFile == unicode(""):
            QMessageBox.warning(self, u"{0} -- {1}".format(unicode(qApp.applicationName()),
                                                           __appname__),
                                u"没有可用的滤波文件或滤波存储文件输入！")
            return

        try:
            dataFilterObj = DataFilter(samplingRate, filterOrder=filtOrder, cutoffFre=cutoffFre)
            headerNums = self.spbFileHeaderNums.value()
            dataFilterObj.setRawFile(rawFile)
            dataFilterObj.setFiltFile(filterFile)
            dataFilterObj.setHeaderRows(headerNums)
            dataFilterObj.toDataFile()

            if self.chbFilterShow.isChecked():
                mplTuple = dataFilterObj.showWidget(self)
                for tab, mpl in zip([self.tabCx, self.tabCy, self.tabCz,
                                     self.tabCmx, self.tabCmy, self.tabCmz], mplTuple):
                    if tab.layout():    # 如果tab选项卡中存在布局管理器
                        for child in tab.children():    # 遍历选项卡中的子项（含布局管理器）
                            if isinstance(child, MatplotlibWidget):    # 如果是MatplotlibWidget子类
                                tab.layout().removeWidget(child)    # 从布局管理器中移除部件（部件并没有销毁）
                                child.hide()    # 将该部件隐藏（更好的办法是将该部件删除）
                                child.destroy()    # 将该部件删除？（删除测试发现有问题）
                        tab.layout().addWidget(mpl)    # 布局管理器中添加新的MatplotlibWidget实例对象
                    else:
                        lay = QVBoxLayout()
                        lay.addWidget(mpl)
                        tab.setLayout(lay)
                self.mplTabWidget.setVisible(True)
                self.mainLayout.setSizeConstraint(QLayout.SetDefaultConstraint)    # 将对话框尺寸策略改为默认
            QMessageBox.warning(self, u"{0} -- {1}".format(unicode(qApp.applicationName()),
                                                           __appname__),
                                u"滤波完成")
        except Exception, msg:
            QMessageBox.warning(self, u"{0} -- {1}".format(unicode(qApp.applicationName()),
                                                           __appname__),
                                u"文件{0}滤波失败\n{1}".format(unicode(rawFile), msg))
            return


if __name__ == "__main__":
    app = QApplication(sys.argv)
    dataFilter = DataFilterWidget()
    dataFilter.show()
    app.exec_()

