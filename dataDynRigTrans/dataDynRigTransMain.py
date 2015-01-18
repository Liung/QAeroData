#coding: UTF-8
from __future__ import division
__author__ = 'Vincent'
AIR_DENSITY = 1.2250    # 空气密度
__appname__ = u'实验数据转换'

'''
本文件主要作用是转换实验数据为风轴和体轴下的数据
'''

from PyQt4.QtGui import *
from PyQt4.QtCore import *
import sys, os
import tempfile
import numpy as np
from scipy.signal import butter, filtfilt
from dataDynRigTrans.dataDynRigTransUi import Ui_dataTransWidget
from dataTrans.dataTransMain import DataTransWidget


class DataDynRigTransWidget(QDialog, Ui_dataTransWidget):
    AppName = u"动态数据处理程序"

    def __init__(self, parent=None):
        super(DataDynRigTransWidget, self).__init__(parent)
        self.setupUi(self)
        self.setWindowTitle(DataDynRigTransWidget.AppName)

        self.layout = QVBoxLayout()
        self.dataTransWidget = DataTransWidget()
        self.dataTransWidget.pbtnGenerateFile.setHidden(True)
        self.dataTransWidget.pbtnExit.setHidden(True)
        self.dataTransWidget.tabBatchFile.setEnabled(False)
        self.layout.addWidget(self.dataTransWidget)
        self.userWidget.setLayout(self.layout)
        btn = QPushButton(u'生成数据')
        btn.clicked.connect(self.run)
        self.dataTransWidget.layoutBottom.addWidget(btn)

    def run(self):

        sf = unicode(self.dataTransWidget.txtStaticFile.text())
        df = unicode(self.dataTransWidget.txtDynamicFile.text())
        hr = self.dataTransWidget.spbFileHeaderNums.value()
        fr = self.dataTransWidget.spbFileFooterNums.value()
        try:
            # 读取原始文件数据
            staRawData = np.genfromtxt(sf, skiprows=hr, skip_footer=fr)
            dynRAWData = np.genfromtxt(df, skiprows=hr, skip_footer=fr)
            # 判断是否需要滤波处理并返回数据
            staFiltData = self._filt_array(staRawData) if self.chbButterFilter.isChecked() else staRawData
            dynFiltData = self._filt_array(dynRAWData) if self.chbButterFilter.isChecked() else dynRAWData
            # 截断数据
            staTruncData = self._truncate_array(staFiltData)
            dynTruncData = self._truncate_array(dynFiltData)
            # 根据运动类型返回正确角度信息：单独俯仰不做处理
            if self.cbKineticsSty.currentIndex() == 1:
                # roll oscillation
                phiCol = self.dataTransWidget.spbPhiCol.value() - 1
                staTruncData[:, phiCol] += self.spbPhi0.value()
                dynTruncData[:, phiCol] += self.spbPhi0.value()
            if self.cbKineticsSty.currentIndex() == 2:
                # yaw oscillation
                psiCol = self.dataTransWidget.spbPsiCol.value() - 1
                staTruncData[:, psiCol] += self.spbPsi0.value()
                dynTruncData[:, psiCol] += self.spbPsi0.value()
            # 判断是否进行周期平均并返回数据
            staData = self._average_period_data(staTruncData)[0] if self.chbPeriodAverage.isChecked() else staTruncData
            dynData = self._average_period_data(dynTruncData)[0] if self.chbPeriodAverage.isChecked() else dynTruncData

            newStaFile = 'temp_stafile.dat'
            newDynFile = 'temp_dynfile.dat'
            np.savetxt(newStaFile, staData, fmt='%-15.8f', delimiter='\t', header='static data', comments='')
            np.savetxt(newDynFile, dynData, fmt='%-15.8f', delimiter='\t', header='dynamic data', comments='')

            self.dataTransWidget.balance.setStaFile(newStaFile)
            self.dataTransWidget.balance.setDynFile(newDynFile)

            self.dataTransWidget.on_pbtnGenerateFile_clicked()
            os.remove(newStaFile)
            os.remove(newDynFile)
        except Exception, e:
            QMessageBox.warning(self, u"{0} -- warning".format(DataDynRigTransWidget.AppName), u"Error:{0}".format(e.message))

    def _truncate_array(self, array):
        # 总的周期采样点数
        period = self.spbPeriodNums.value()
        period_points = np.ceil(1 / self.spbKineticsFre.value() * self.spbSampleRatio.value()).astype('int')
        # 寻找指定列的第一个周期最大值点索引
        start_index = self.spbIgnorePts.value()
        refColumn = 1
        refValue = 0.
        if self.cbKineticsSty.currentIndex() == 0:
            refColumn = self.dataTransWidget.spbThetaCol.value() - 1
            refValue = self.spbTheta0.value() + self.spbAmplitude.value()
        if self.cbKineticsSty.currentIndex() == 1:
            refColumn = self.dataTransWidget.spbPhiCol.value() - 1
            refValue = self.spbAmplitude.value()
        if self.cbKineticsSty.currentIndex() == 2:
            refColumn = self.dataTransWidget.spbPsiCol.value() - 1
            refValue = self.spbAmplitude.value()
        ref_array = array[start_index:, refColumn]  # 读取忽略点数之后的数据
        for idx in xrange(np.max(ref_array.shape)):
            if (ref_array[idx] >= ref_array[idx - 1]) and \
                    (ref_array[idx] >= ref_array[idx + 1]) \
                    and np.abs(ref_array[idx] - refValue) < np.abs(refValue * (1 - self.spbCorr.value())):
                start_index += idx

                break
        first_index = start_index + int(period_points / 2)
        last_index = first_index + int(period * period_points)  # 最后一个周期的后一个周期起始点序列

        export_data = array[first_index:last_index, :]

        return export_data

    def _filt_array(self, array):
        order = self.spbFilterOrder.value()
        cutoff = self.spbCutoffFre.value()
        sampleRatio = self.spbSampleRatio.value()
        b, a = butter(order, cutoff / (sampleRatio / 2.), btype='low')
        filterData = np.zeros_like(array)

        fsc = self.dataTransWidget.spbFMStartCol.value() - 1
        fec = self.dataTransWidget.spbFMEndCol.value() - 1
        for i in xrange(array.shape[1]):
            if fsc <= i <= fec:  # 只对力和力矩进行滤波处理，角度列不进行滤波
                filterData[:, i] = filtfilt(b, a, array[:, i])
            else:
                filterData[:, i] = array[:, i]

        return filterData

    def _average_period_data(self, array):
        """
        周期平均一组周期数据
        :param array:
        :param peroid:
        :param time:
        :return:
        """
        m, n = array.shape
        period = self.spbPeriodNums.value()
        average_array = np.zeros((m / period, n))
        std_array = np.zeros_like(average_array)
        for i in range(n):
            temp_array = array[:, i].reshape((period, -1))
            average_array[:, i] = temp_array.mean(axis=0)  # 每一行为一个周期的数据,行数表示周期个数
            std_array[:, i] = temp_array.std(axis=0)

        return average_array, std_array

if __name__ == "__main__":
    app = QApplication(sys.argv)
    dataTrans = DataDynRigTransWidget()
    dataTrans.show()
    app.exec_()



