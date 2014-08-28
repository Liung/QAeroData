#coding: UTF-8
from __future__ import division
__author__ = 'Vincent'
AIR_DENSITY = 1.2250    # 空气密度
__appname__ = u'实验数据转换'
__BalanceSty__ = [u"14杆天平", u"16杆天平", u"18杆天平", u"盒式天平"]
__KineticsSty__ = [u"俯仰运动", u"滚转运动", u"偏航运动"]

'''
本文件主要作用是转换实验数据为风轴和体轴下的数据
'''

from PyQt4.QtGui import *
from PyQt4.QtCore import *
import sys
sys.path.append('..')
import codecs
import numpy as np
from dataTransUi import Ui_dataTransWidget
from balance.balance import AircraftModel, Balance
from widget.dataFileFormat import DataFileFormat


class DataTransWidget(QDialog, Ui_dataTransWidget):
    def __init__(self, parent=None):
        super(DataTransWidget, self).__init__(parent)
        self.setupUi(self)
        self.txtModelArea.setValidator(QDoubleValidator())
        self.txtModelSpan.setValidator(QDoubleValidator())
        self.txtModelRootChord.setValidator(QDoubleValidator())
        self.txtModelRefChord.setValidator(QDoubleValidator())
        self.txtWindSpeed.setValidator(QDoubleValidator())
        self.txtDeltaX.setValidator(QDoubleValidator())
        self.txtDeltaY.setValidator(QDoubleValidator())
        self.txtDeltaZ.setValidator(QDoubleValidator())
        self.cbBalanceSty.addItems(__BalanceSty__)
        #创建飞行器试验模型
        self.model = AircraftModel()
        self.model.setArea(float(self.txtModelArea.text()))    # 初始化模型面积
        self.model.setSpan(float(self.txtModelSpan.text()))    # 初始化模型展长
        self.model.setRootChord(float(self.txtModelRootChord.text()))   # 初始化模型根弦长
        self.model.setRefChord(float(self.txtModelRefChord.text()))     # 初始化模型参考弦长
        self.model.setWindSpeed(float(self.txtWindSpeed.text()))             # 初始化试验风速
        self.model.dx = float(self.txtDeltaX.text())                    # 初始化deltaX
        self.model.dy = float(self.txtDeltaY.text())
        self.model.dz = float(self.txtDeltaZ.text())
        #创建天平类型
        self.balance = Balance()
        self.balance.setBalanceSty(self.cbBalanceSty.currentIndex())  # 初始化天平类型
        self.balance.setHeaderRows(self.spbFileHeaderNums.value())
        self.balance.setAircraftModel(self.model)

        self._dir = "./"

    @pyqtSignature("int")
    def on_cbBalanceSty_activated(self, index):
        self.balance.setBalanceSty(index)

    @pyqtSignature("")
    def on_pbtnModelDataInput_clicked(self):
        mdFn = QFileDialog.getOpenFileName(self, u"打开模型文件...",
                                           directory=self._dir,
                                           filter=u"文本文件(*.txt);;数据文件(*.dat);;所有文件(*.*)",
                                           selectedFilter=u"文本文件(*.txt)")

        if not mdFn.isEmpty():
            self._dir = mdFn
            try:
                with codecs.open(mdFn, "r", "utf8") as f:
                    rawData = f.readlines()[2:-2]
                    params1 = [s.split('\t')[1].encode('ascii') for s in rawData[:5]]
                    params2 = [s.split('\t')[1].encode('ascii') for s in rawData[6:]]
                    self.txtModelArea.setText(params1[0])
                    self.txtModelSpan.setText(params1[1])
                    self.txtModelRootChord.setText(params1[2])
                    self.txtModelRefChord.setText(params1[3])
                    self.txtWindSpeed.setText(params1[4])
                    self.txtDeltaX.setText(params2[0])
                    self.txtDeltaY.setText(params2[1])
                    self.txtDeltaZ.setText(params2[2])
                return True
            except Exception, msg:
                QMessageBox.about(self, u"{0}提示".format(__appname__),
                                  u"模型文件打开失败\n{0}".format(msg))

            return

    @pyqtSignature("")
    def on_pbtnModelDataExport_clicked(self):
        mdFn = QFileDialog.getSaveFileName(self, u"存储模型文件...",
                                           directory=self._dir,
                                           filter=u"文本文件(*.txt);;数据文件(*.dat);;所有文件(*.*)",
                                           selectedFilter=u"文本文件(*.txt)")
        if not mdFn.isEmpty():
            self._dir = mdFn
            with codecs.open(mdFn, "w", "utf8") as f:
                f.write('#'*80+"\r\n")
                f.write('\n')
                f.write(u"面积:\t%s\t㎡\r\n" % self.txtModelArea.text())
                f.write(u"展长:\t%s\tm\r\n" % self.txtModelSpan.text())
                f.write(u"根弦长:\t%s\tm\r\n" % self.txtModelRootChord.text())
                f.write(u"参考弦长:\t%s\tm\r\n" % self.txtModelRefChord.text())
                f.write(u"实验风速:\t%s\tm/s\r\n" % self.txtWindSpeed.text())
                f.write(u"模型重心距天平中心:\r\n")
                f.write(u"\t%s\tm\r\n" % self.txtDeltaX.text())
                f.write(u"\t%s\tm\r\n" % self.txtDeltaY.text())
                f.write(u"\t%s\tm\r\n" % self.txtDeltaZ.text())
                f.write('\n')
                f.write('#'*80+"\r\n")

                QMessageBox.about(self, u"{0}提示".format(__appname__),
                                  u"模型文件存储成功")
                return True
        return False

    @pyqtSignature("")
    def on_pbtnStaticFile_clicked(self):
        staticFn = QFileDialog.getOpenFileName(self, u"打开静态文件...",
                                               directory=self._dir,
                                               filter=u"文本文件(*.txt);;数据文件(*.dat);;所有文件(*.*)",
                                               selectedFilter=u"文本文件(*.txt)")
        if not staticFn.isEmpty():
            self._dir = staticFn
            self.txtStaticFile.setText(staticFn)
            self.balance.setStaFile(unicode(staticFn))

    @pyqtSignature("QString")
    def on_txtStaticFile_textChanged(self, fileName):
        f = QFileInfo(fileName)
        if f.exists() and f.isFile():
            self.balance.setStaFile(unicode(fileName))
        else:
            QMessageBox.warning(self, u"{0} -- warning".format(__appname__),
                                u"{0}文件不存在".format(unicode(fileName)))

    @pyqtSignature("")
    def on_pbtnDynamicFile_clicked(self):
        dynFn = QFileDialog.getOpenFileName(self, u"打开动态文件...",
                                            directory=self._dir,
                                            filter=u"文本文件(*.txt);;数据文件(*.dat);;所有文件(*.*)",
                                            selectedFilter=u"文本文件(*.txt)")
        if not dynFn.isEmpty():
            self._dir = dynFn
            self.txtDynamicFile.setText(dynFn)
            self.balance.setDynFile(unicode(dynFn))

    @pyqtSignature("QString")
    def on_txtDynamicFile_textChanged(self, fileName):
        f = QFileInfo(fileName)
        if f.exists() and f.isFile():
            self.balance.setDynFile(unicode(fileName))
        else:
            QMessageBox.warning(self, u"{0} -- warning".format(__appname__),
                                u"{0}文件不存在".format(unicode(fileName)))

    @pyqtSignature("")
    def on_pbtnBodyFile_clicked(self):
        bodyFn = QFileDialog.getSaveFileName(self, u"存储体轴文件...",
                                             directory=self._dir,
                                             filter=u"文本文件(*.txt);;数据文件(*.dat);;所有文件(*.*)",
                                             selectedFilter=u"文本文件(*.txt)")
        if not bodyFn.isEmpty():
            self._dir = bodyFn
            self.txtBodyFile.setText(bodyFn)
            self.balance.setBodyFile(unicode(bodyFn))

    @pyqtSignature("QString")
    def on_txtBodyFile_textChanged(self, fileName):
        f = QFileInfo(fileName)
        if f.dir().exists and not f.baseName().isEmpty() and not f.suffix().isEmpty():
            self.balance.setBodyFile(unicode(fileName))
        else:
            QMessageBox.warning(self, u"{0} -- warning".format(__appname__),
                                u"{0}不是有效文件".format(unicode(fileName)))

    @pyqtSignature("")
    def on_pbtnAeroFile_clicked(self):
        aeroFn = QFileDialog.getSaveFileName(self, u"存储风轴文件...",
                                             directory=self._dir,
                                             filter=u"文本文件(*.txt);;数据文件(*.dat);;所有文件(*.*)",
                                             selectedFilter=u"文本文件(*.txt)")
        if not aeroFn.isEmpty():
            self._dir = aeroFn
            self.txtAeroFile.setText(aeroFn)
            self.balance.setAeroFile(unicode(aeroFn))

    @pyqtSignature("QString")
    def on_txtAeroFile_textChanged(self, fileName):
        f = QFileInfo(fileName)
        if f.dir().exists and not f.baseName().isEmpty() and not f.suffix().isEmpty():
            self.balance.setAeroFile(unicode(fileName))
        else:
            QMessageBox.warning(self, u"{0} -- warning".format(__appname__),
                                u"{0}不是有效文件".format(unicode(fileName)))

    @pyqtSignature("")
    def on_pbtnFileFormat_clicked(self):
        dff = DataFileFormat(self)
        dff.exec_()
        self.balance.setFileFormat(dff.params)

    @pyqtSignature("")
    def on_pbtnGenerateFile_clicked(self):
        try:
            if self.balance.translateData():
                QMessageBox.about(self, u"{0}".format(__appname__), u"数据生成完成！")
        except Exception, msg:
            QMessageBox.about(self, u"{0}".format(__appname__),
                              u"Failed to translate the data files.\n{0}".format(msg))

    @pyqtSignature("")
    def on_pbtnHelp_clicked(self):
        QMessageBox.about(self, u"{0} -- {1}".format(qApp.applicationName(), __appname__),
                          u'''注意事项：
            1、请输入正确的模型参数值！
            2、请不要改动输出模型参数的格式，否则可能引起载入模型参数文件失败。''')

    @pyqtSignature("QString")
    def on_txtModelArea_textChanged(self, txtArea):
        self.model.area = float(txtArea)


    @pyqtSignature("QString")
    def on_txtModelSpan_textChanged(self, txtSpan):
        self.model.span = float(txtSpan)

    @pyqtSignature("QString")
    def on_txtModelRootChord_textChanged(self, txtRootChord):
        self.model.rootChord = float(txtRootChord)

    @pyqtSignature("QString")
    def on_txtModelRefChord_textChanged(self, txtRefChord):
        self.model.refChord = float(txtRefChord)

    @pyqtSignature("QString")
    def on_txtWindSpeed_textChanged(self, txtWindSpeed):
        self.model.windSpeed = float(txtWindSpeed)

    @pyqtSignature("QString")
    def on_txtDeltaX_textChanged(self, txtDeltaX):
        self.model.dx = float(txtDeltaX)

    @pyqtSignature("QString")
    def on_txtDeltaY_textChanged(self, txtDeltaY):
        self.model.dy = float(txtDeltaY)

    @pyqtSignature("QString")
    def on_txtDeltaZ_textChanged(self, txtDeltaZ):
        self.model.dz = float(txtDeltaZ)

    @pyqtSignature("int")
    def on_spbFileHeaderNums_valueChanged(self, rows):
        self.balance.setHeaderRows(rows)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    dataTrans = DataTransWidget()
    dataTrans.show()
    app.exec_()



