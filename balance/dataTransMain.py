# -*-coding: utf-8 -*-
"""
this is App main code

本文件主要作用是转换实验数据为风轴和体轴下的数据

Author: liuchao
Date: 2014-09-05
"""
from __future__ import division
import sys
import os
import numpy as np
from PyQt4.QtGui import *
from PyQt4.QtCore import *
import codecs
from dataTransUi import Ui_dataTransWidget
from aircraft import AircraftModel
from balance import Balance
import imgs_rc

AIR_DENSITY = 1.2250    # 空气密度
__AppName__ = u'实验数据转换'
__BalanceSty__ = [u"14杆天平", u"16杆天平", u"18杆天平", u"盒式天平(内)", u"盒式天平(外)"]
__KineticsSty__ = [u"俯仰运动", u"滚转运动", u"偏航运动"]

docSettingStr = QString(u"""
<p><h1>天平数据转换工具</h1></p>
<p>本工具主要用来将实验测得的天平数据转换为风轴和体轴下的数据</p>
<hr/>
<p><h2>使用说明：</h2></p>
<p>
<big><b>选择天平类型：</b></big>选择天平类型后，请第一时间点击<b>天平系数设置</b>按钮，调入相应的天平系数文件。天平系数文件用空格或制表符\t隔开。
十四杆天平和十六杆天平系数矩阵：6 X 6 型，十八杆为：6 X 27 型， 盒式为： 6 X 8 型， 天平系数顺序以原Matlab天平处理文件为参考。当天平类型改变后，
系统自动将原天平系数清零，需再次调入天平系数文件。
</P>
<P>
<big><b>载入模型参数、模型参数导出：</b></big>第一次使用该工具时，可以编辑自己的模型参数，然后点击<b>模型参数导出</b>按钮，将参数保存在文件目录中，
下次使用时，点击<b>载入模型参数</b>，选择对应模型参数文件，避免再次输入各个模型参数。
</P>
<p>
<big><b>角度起始列、角度终止列：</b></big>程序需要知道你所提供的文件的角度列数，例如有些文件中只有俯仰角一列角度数据，当没有提供其他角度列时，
程序默认其他角度列为0。
</P>
<p>
<big><b>力/力矩起始列、力/力矩终止列：</b></big>力矩起始列，默认力和力矩共六列，<b>力/力矩终止列</b>参数系统自动设定。
</P>
<p>
<big><b>角度类型：</b></big>一般来讲，用<b>α-β机构</b>采集得到的角度为<b>气动角度</b>，因为该机构的坐标系统与风洞中风轴系相同；
如果使用<b>动态机构</b>采集得到的角度，则为<b>欧拉角度</b>，因为动态机构的俯仰、滚转、偏航角度（电机输出的）都是以体轴系为坐标参考系。角度类型不同，
会影响到体轴系下模型力和力矩向气动轴系转换的结果。一般情况下为体轴角度</p>
<p>
<big><b>角度偏移量：</b></big>对某些数据列进行<b>+或-</b>相应的偏移量。原因：以动态机构滚转运动为例，由于电机没有绝对零点，
文件记录的滚转数据列为相对于当时零点的相对滚转量，处理过程中必须给该列加上当时实际的滚转角度，才为真正的滚转角。格式设置(冒号和逗号皆为西文标点符号)：
<b>列1：偏移量1，列2：偏移量2，...</b>
</p>
<p>
<big><b>盒式天平内、外区别：</b></big>盒式天平一般用来做翼型试验。当翼型的+y方向指向一米风洞内侧，选用盒式天平（内）转换，否则，选用盒式天平（外）
</P>
<hr/>
<p>Author: <b>liung</b>
Date:<b> 2014-09-05</b></p>
""")


class BalanceCoesTable(QDialog):
    def __init__(self, parent=None, rows=1, cols=1, balance=None):
        super(BalanceCoesTable, self).__init__(parent)
        mainLay = QVBoxLayout()

        self.label = QLabel('')
        self.spacerItem1 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.label1 = QLabel(u'编号：')
        self.labelIndex = QLabel('')
        topLay = QHBoxLayout()
        topLay.addWidget(self.label)
        topLay.addItem(self.spacerItem1)
        topLay.addWidget(self.label1)
        topLay.addWidget(self.labelIndex)

        self.tableWidget = QTableWidget()
        self.tableWidget.setRowCount(rows)
        self.tableWidget.setColumnCount(cols)

        bottomLay = QHBoxLayout()
        self.btnExport = QPushButton(u'导出系数')
        self.btnInput = QPushButton(u"导入系数")
        self.btnApply = QPushButton("Apply")
        self.btnApply.setEnabled(False)
        self.btnClose = QPushButton("Close")
        self.spacerItem = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        bottomLay.addWidget(self.btnExport)
        bottomLay.addWidget(self.btnInput)
        bottomLay.addItem(self.spacerItem)
        bottomLay.addWidget(self.btnApply)
        bottomLay.addWidget(self.btnClose)

        mainLay.addLayout(topLay)
        mainLay.addWidget(self.tableWidget)
        mainLay.addLayout(bottomLay)

        self.setLayout(mainLay)
        self.setWindowTitle(u"天平参数设置")
        self.resize(1000, 400)

        self.connect(self.btnClose, SIGNAL("clicked()"), self.close)
        self.connect(self.btnApply, SIGNAL('clicked()'), self.updateBalanceCoes)

        self.connect(self.btnExport, SIGNAL("clicked()"), self.exportCoes)
        self.connect(self.btnInput, SIGNAL("clicked()"), self.inputCoes)
        self.tableWidget.itemChanged.connect(self.updateBtnApply)

        self.balance = balance

    def updateBtnApply(self):
        self.btnApply.setEnabled(True)

    def exportCoes(self):
        coesFile = QFileDialog.getSaveFileName(self, u"存储文件...",
                                               directory='.',
                                               filter=u"所有文件(*.*);;数据文件(*.dat);;文本文件(*.txt)",
                                               selectedFilter=u"文本文件(*.*)")
        if coesFile.isEmpty():
            return
        rows = self.tableWidget.rowCount()
        cols = self.tableWidget.columnCount()
        coes = np.zeros(shape=(rows, cols))
        try:
            for i in range(rows):
                for j in range(cols):
                    val = float(self.tableWidget.item(i, j).text())
                    coes[i, j] = val
            np.savetxt(fname=unicode(coesFile), X=coes, delimiter='\t', fmt="%.12f")
        except Exception, e:
            QMessageBox.warning(self, __AppName__, u"参数导出失败\n{0}".format(e.message))

    def inputCoes(self):
        coesFile = QFileDialog.getOpenFileName(self, u"载入文件...",
                                               directory='.',
                                               filter=u"所有文件(*.*);;数据文件(*.dat);;文本文件(*.txt)",
                                               selectedFilter=u"文本文件(*.*)")
        if coesFile.isEmpty():
            return
        try:
            fn = unicode(coesFile)
            coes = np.loadtxt(fn, dtype=float)
            rows, cols = coes.shape
            index = int(self.labelIndex.text()) - 1
            if index == 0 or index == 1:
                if rows != 6 or cols != 6:
                    QMessageBox.warning(self, __AppName__,
                                        u"{0} 的矩阵系数为 6 X 6 型，您输入的矩阵维数为：{1} X {2} 型.".format(
                                            __BalanceSty__[index], rows, cols))
                    return
            if index == 2:
                if rows != 6 or cols != 27:
                    QMessageBox.warning(self, __AppName__,
                                        u"{0} 的矩阵系数为 6 X 27 型，您输入的矩阵维数为：{1} X {2} 型.".format(
                                            __BalanceSty__[index], rows, cols))
                    return
            if index == 3 or index == 4:
                if rows != 6 or cols != 8:
                    QMessageBox.warning(self, __AppName__,
                                        u"{0} 的矩阵系数为 6 X 8 型，您输入的矩阵维数为：{1} X {2} 型.".format(
                                            __BalanceSty__[index], rows, cols))
                    return

            self.tableWidget.setRowCount(rows)
            self.tableWidget.setColumnCount(cols)
            for i in range(rows):
                for j in range(cols):
                    val = coes[i, j]
                    self.tableWidget.setItem(i, j, QTableWidgetItem(str(val)))
            self.updateBalanceCoes()
        except Exception, e:
            QMessageBox.about(self, __AppName__, u"参数载入失败，请检查参数文件格式是否正确\n{0}".format(e.message))

    def setBalanceCoes(self, coes):
        if coes is not None:
            rows, cols = coes.shape
            self.tableWidget.setRowCount(rows)
            self.tableWidget.setColumnCount(cols)
            for i in range(rows):
                for j in range(cols):
                    item = QTableWidgetItem(str(coes[i, j]))
                    self.tableWidget.setItem(i, j, item)

    def updateBalanceCoes(self):
        rows = self.tableWidget.rowCount()
        cols = self.tableWidget.columnCount()
        coes = np.zeros(shape=(rows, cols))
        try:
            for i in range(rows):
                for j in range(cols):
                    item = self.tableWidget.item(i, j)
                    if not item:
                        raise Exception
                    coes[i, j] = float(item.text())
            self.balance.setBalanceCoes(coes)
            self.btnApply.setEnabled(False)
        except Exception, e:
            QMessageBox.warning(self, __AppName__, u"天平系数设置失败\n{0}".format(e.message))


class DataTransWidget(QDialog, Ui_dataTransWidget):
    def __init__(self, parent=None):
        super(DataTransWidget, self).__init__(parent)
        self.setupUi(self)

        # 创建飞行器试验模型
        self.model = AircraftModel()
        self.initModel()
        #创建天平类型
        self.balance = Balance()
        self.initBalance()
        self.updateModel()

        self._dir = "./"
        self.balanceParamsTable = BalanceCoesTable(self, balance=self.balance)

        self.tabWidget.setCurrentIndex(0)
        self.txtModelArea.setValidator(QDoubleValidator())
        self.txtModelSpan.setValidator(QDoubleValidator())
        self.txtModelRootChord.setValidator(QDoubleValidator())
        self.txtModelRefChord.setValidator(QDoubleValidator())
        self.txtWindSpeed.setValidator(QDoubleValidator())
        self.txtDeltaX.setValidator(QDoubleValidator())
        self.txtDeltaY.setValidator(QDoubleValidator())
        self.txtDeltaZ.setValidator(QDoubleValidator())
        self.cbBalanceSty.addItems(__BalanceSty__)
        self.cbBalanceSty.setCurrentIndex(-1)

    def initModel(self):
        self.model.setArea(float(self.txtModelArea.text()))    # 初始化模型面积
        self.model.setSpan(float(self.txtModelSpan.text()))    # 初始化模型展长
        self.model.setRootChord(float(self.txtModelRootChord.text()))   # 初始化模型根弦长
        self.model.setRefChord(float(self.txtModelRefChord.text()))     # 初始化模型参考弦长
        self.model.setWindSpeed(float(self.txtWindSpeed.text()))             # 初始化试验风速
        self.model.dx = float(self.txtDeltaX.text())                    # 初始化deltaX
        self.model.dy = float(self.txtDeltaY.text())
        self.model.dz = float(self.txtDeltaZ.text())

    def initBalance(self):
        self.balance.setBalanceSty(self.cbBalanceSty.currentIndex())  # 初始化天平类型
        self.balance.setHeaderRows(self.spbFileHeaderNums.value())
        self.balance.setFooterRows(self.spbFileFooterNums.value())
        self.balance.setAngleStartCol(self.spbAngleStartCol.value())
        self.balance.setAngleEndCol(self.spbAngleEndCol.value())
        self.balance.setForceStartCol(self.spbForceStartCol.value())
        self.balance.setForceEndCol(self.spbForceEndCol.value())

    def updateModel(self):
        self.balance.setAircraftModel(self.model)

    @pyqtSignature("int")
    def on_cbBalanceSty_currentIndexChanged(self, index):
        self.balance.setBalanceSty(index)
        self.balance.setBalanceCoes(None)
        self.balanceParamsTable.tableWidget.clear()

    @pyqtSignature("")
    def on_pbtnBalanceParamsSetting_clicked(self):
        if self.cbBalanceSty.currentIndex() == -1:
            QMessageBox.warning(self, u"{0}提示".format(__AppName__), u"未选择天平类型")
            return

        index = self.cbBalanceSty.currentIndex()
        self.balanceParamsTable.label.setText(__BalanceSty__[index])
        self.balanceParamsTable.labelIndex.setText(str(index + 1))
        coes = self.balance.getBalanceCoes()
        if coes is not None:
            self.balanceParamsTable.setBalanceCoes(coes)
        else:
            if index == 0:
                self.balanceParamsTable.tableWidget.setRowCount(6)
                self.balanceParamsTable.tableWidget.setColumnCount(6)
            if index == 1:
                self.balanceParamsTable.tableWidget.setRowCount(6)
                self.balanceParamsTable.tableWidget.setColumnCount(6)
            if index == 2:
                self.balanceParamsTable.tableWidget.setRowCount(6)
                self.balanceParamsTable.tableWidget.setColumnCount(27)
            if index == 3 or index == 4:
                self.balanceParamsTable.label.setText(__BalanceSty__[3] + '/' + __BalanceSty__[4])
                self.balanceParamsTable.tableWidget.setRowCount(6)
                self.balanceParamsTable.tableWidget.setColumnCount(8)
        self.balanceParamsTable.exec_()

    @pyqtSignature("")
    def on_pbtnModelDataInput_clicked(self):
        mdFn = QFileDialog.getOpenFileName(self, u"打开模型文件...",
                                           directory=self._dir,
                                           filter=u"所有文件(*.*);;数据文件(*.dat);;文本文件(*.txt)",
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
                QMessageBox.about(self, u"{0}提示".format(__AppName__),
                                  u"模型文件打开失败\n{0}".format(msg))

            return

    @pyqtSignature("")
    def on_pbtnModelDataExport_clicked(self):
        mdFn = QFileDialog.getSaveFileName(self, u"存储模型文件...",
                                           directory=self._dir,
                                           filter=u"所有文件(*.*);;数据文件(*.dat);;文本文件(*.txt)",
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

                QMessageBox.about(self, u"{0}提示".format(__AppName__),
                                  u"模型文件存储成功")
                return True
        return False

    @pyqtSignature("")
    def on_pbtnStaticFile_clicked(self):
        staticFn = QFileDialog.getOpenFileName(self, u"打开静态文件...",
                                               directory=self._dir,
                                               filter=u"所有文件(*.*);;数据文件(*.dat);;文本文件(*.txt)",
                                               selectedFilter=u"文本文件(*.*)")
        if not staticFn.isEmpty():
            self._dir = staticFn
            self.txtStaticFile.setText(staticFn)
            self.balance.setStaFile(unicode(staticFn))

    @pyqtSignature("")
    def on_txtStaticFile_lostFocus(self):
        fileName = self.txtStaticFile.text()
        if fileName.isEmpty():
            return
        f = QFileInfo(fileName)
        if f.exists() and f.isFile():
            self.balance.setStaFile(unicode(fileName))
        else:
            QMessageBox.warning(self, u"{0} -- warning".format(__AppName__),
                                u"{0}文件不存在".format(unicode(fileName)))
            self.txtStaticFile.setText('')

    @pyqtSignature("")
    def on_pbtnDynamicFile_clicked(self):
        dynFn = QFileDialog.getOpenFileName(self, u"打开动态文件...",
                                            directory=self._dir,
                                            filter=u"所有文件(*.*);;数据文件(*.dat);;文本文件(*.txt)",
                                            selectedFilter=u"文本文件(*.*)")
        if not dynFn.isEmpty():
            self._dir = dynFn
            self.txtDynamicFile.setText(dynFn)
            self.balance.setDynFile(unicode(dynFn))

    @pyqtSignature("")
    def on_txtDynamicFile_lostFocus(self):
        fileName = self.txtDynamicFile.text()
        if fileName.isEmpty():
            return
        f = QFileInfo(fileName)
        if f.exists() and f.isFile():
            self.balance.setDynFile(unicode(fileName))
        else:
            QMessageBox.warning(self, u"{0} -- warning".format(__AppName__),
                                u"{0}文件不存在".format(unicode(fileName)))
            self.txtDynamicFile.setText('')

    @pyqtSignature("")
    def on_pbtnBodyFile_clicked(self):
        bodyFn = QFileDialog.getSaveFileName(self, u"存储体轴文件...",
                                             directory=self._dir,
                                             filter=u"所有文件(*.*);;数据文件(*.dat);;文本文件(*.txt)",
                                             selectedFilter=u"文本文件(*.*)")
        if not bodyFn.isEmpty():
            self._dir = bodyFn
            self.txtBodyFile.setText(bodyFn)
            self.balance.setBodyFile(unicode(bodyFn))

    @pyqtSignature("")
    def on_txtBodyFile_lostFocus(self):
        fileName = self.txtBodyFile.text()
        if fileName.isEmpty():
            return
        f = QFileInfo(fileName)
        if f.dir().exists and not f.baseName().isEmpty() and not f.suffix().isEmpty():
            self.balance.setBodyFile(unicode(fileName))
        else:
            QMessageBox.warning(self, u"{0} -- warning".format(__AppName__),
                                u"{0}不是有效文件".format(unicode(fileName)))
            self.txtBodyFile.setText('')

    @pyqtSignature("")
    def on_pbtnAeroFile_clicked(self):
        aeroFn = QFileDialog.getSaveFileName(self, u"存储风轴文件...",
                                             directory=self._dir,
                                             filter=u"所有文件(*.*);;数据文件(*.dat);;文本文件(*.txt)",
                                             selectedFilter=u"文本文件(*.*)")
        if not aeroFn.isEmpty():
            self._dir = aeroFn
            self.txtAeroFile.setText(aeroFn)
            self.balance.setAeroFile(unicode(aeroFn))

    @pyqtSignature("")
    def on_txtAeroFile_lostFocus(self):
        fileName = self.txtAeroFile.text()
        if fileName.isEmpty():
            return
        f = QFileInfo(fileName)
        if f.dir().exists and not f.baseName().isEmpty() and not f.suffix().isEmpty():
            self.balance.setAeroFile(unicode(fileName))
        else:
            QMessageBox.warning(self, u"{0} -- warning".format(__AppName__),
                                u"{0}不是有效文件".format(unicode(fileName)))
            self.txtAeroFile.setText('')

    @pyqtSignature("")
    def on_pbtnGenerateFile_clicked(self):
        #判断天平是否选择
        if self.cbBalanceSty.currentIndex() < 0:
            QMessageBox.warning(self, u"{0}".format(__AppName__),
                                u"转换数据前请先选择用了哪个天平哦~~\n")
            return

        if self.balance.getBalanceCoes() is None:
            QMessageBox.warning(self, u"{0}".format(__AppName__),
                                u"选择天平后请先设置天平参数~~\n")
            return
        #判断列数格式是否正确
        if self.spbAngleStartCol.value() > self.spbAngleEndCol.value():
            QMessageBox.warning(self, u"{0}".format(__AppName__),
                                u"角度起始列应该小于等于角度终止列!\n")
            return
        if self.spbAngleEndCol.value() >= self.spbForceStartCol.value():
            QMessageBox.warning(self, u"{0}".format(__AppName__),
                                u"角度终止列应该小于力和力矩起始列!\n")
            return
        try:
            if self.tabWidget.currentIndex() == 0:      # single file translation
                state, msg = self.balance.translateData()
                if state:
                    QMessageBox.about(self, u"{0}".format(__AppName__), u"数据生成完成！")
                else:
                    QMessageBox.warning(self, u"{0}".format(__AppName__),
                                        u"转换失败！\n{0}".format(msg))
            else:       # batch file translation
                fileNums = self.listWidgetBatchFiles.count()
                if fileNums == 0:
                    QMessageBox.warning(self, u"{0}".format(__AppName__),
                                        u"没有待转换的数据文件\n")
                    return
                while self.listWidgetBatchFiles.count() > 0:
                    staFile = unicode(self.listWidgetBatchFiles.item(0).text())
                    dynFile = unicode(self.listWidgetBatchFiles.item(1).text())
                    self.balance.setStaFile(staFile)
                    self.balance.setDynFile(dynFile)
                    bodyFile = os.path.splitext(dynFile)[0] + 'T' + os.path.splitext(dynFile)[1]
                    aeroFile = os.path.splitext(dynFile)[0] + 'Q' + os.path.splitext(dynFile)[1]
                    if not self.txtBatchResultDir.text().isEmpty():
                        target_path = unicode(self.txtBatchResultDir.text())
                        bodyFile = os.path.join(target_path, os.path.basename(bodyFile))
                        aeroFile = os.path.join(target_path, os.path.basename(aeroFile))
                    self.balance.setBodyFile(bodyFile)
                    self.balance.setAeroFile(aeroFile)
                    state, msg = self.balance.translateData()
                    if not state:
                        QMessageBox.warning(self, u"{0}".format(__AppName__),
                                            u"文件{0}数据转换失败！\n{1}".format(dynFile, msg))
                        return
                    # 删除当前列表中的前两个元素
                    self.listWidgetBatchFiles.takeItem(0)
                    self.listWidgetBatchFiles.takeItem(0)

                QMessageBox.about(self, u"{0}".format(__AppName__), u"恭喜~文件转换完成。\n")

        except Exception, msg:
            QMessageBox.about(self, u"{0}".format(__AppName__),
                              u"Failed to translate the data files.\n{0}".format(msg))

    @pyqtSignature("")
    def on_pbtnHelp_clicked(self):
        QMessageBox.about(self, u"{0} -- {1}".format(qApp.applicationName(), __AppName__),
                          docSettingStr)

    @pyqtSignature("QString")
    def on_txtModelArea_textChanged(self, txtArea):
        self.model.setArea(float(txtArea))
        self.updateModel()

    @pyqtSignature("QString")
    def on_txtModelSpan_textChanged(self, txtSpan):
        self.model.setSpan(float(txtSpan))
        self.updateModel()

    @pyqtSignature("QString")
    def on_txtModelRootChord_textChanged(self, txtRootChord):
        self.model.setRootChord(float(txtRootChord))
        self.updateModel()

    @pyqtSignature("QString")
    def on_txtModelRefChord_textChanged(self, txtRefChord):
        self.model.setRefChord(float(txtRefChord))
        self.updateModel()

    @pyqtSignature("QString")
    def on_txtWindSpeed_textChanged(self, txtWindSpeed):
        self.model.setWindSpeed(float(txtWindSpeed))
        self.updateModel()

    @pyqtSignature("QString")
    def on_txtDeltaX_textChanged(self, txtDeltaX):
        self.model.setDx(float(txtDeltaX))
        self.updateModel()

    @pyqtSignature("QString")
    def on_txtDeltaY_textChanged(self, txtDeltaY):
        self.model.setDy(float(txtDeltaY))
        self.updateModel()

    @pyqtSignature("QString")
    def on_txtDeltaZ_textChanged(self, txtDeltaZ):
        self.model.setDz(float(txtDeltaZ))
        self.updateModel()

    @pyqtSignature("")
    def on_chbBatchStaticFile_clicked(self):
        self.updateBatchFiles()

    @pyqtSignature("")
    def on_pbtnBatchStaticFile_clicked(self):
        batchStaticFile = QFileDialog.getOpenFileName(self, u"打开静态文件...",
                                                      directory=self._dir,
                                                      filter=u"所有文件(*.*);;数据文件(*.dat);;文本文件(*.txt)",
                                                      selectedFilter=u"文本文件(*.*)")
        if not batchStaticFile.isEmpty():
            self._dir = batchStaticFile
            self.txtBatchStaticFile.setText(batchStaticFile)
            self.balance.setStaFile(unicode(batchStaticFile))

    @pyqtSignature("")
    def on_txtBatchStaticFile_lostFocus(self):
        fileName = self.txtBatchStaticFile.text()
        if fileName.isEmpty():
            return
        f = QFileInfo(fileName)
        if f.exists() and f.isFile():
            self.balance.setStaFile(unicode(fileName))
        else:
            QMessageBox.warning(self, u"{0} -- warning".format(__AppName__),
                                u"{0}文件不存在".format(unicode(fileName)))
            self.txtBatchStaticFile.setText('')

    def updateBatchFiles(self):
        self.listWidgetBatchFiles.clear()
        rawReg = self.txtBatchDynFileReg.text()
        if not rawReg:
            QMessageBox.warning(self, u"{0} -- warning".format(__AppName__),
                                u"请输入动/静文件校验符")
            return
        regList = unicode(rawReg).strip().lower().split(';')
        if len(regList) != 2:
            QMessageBox.warning(self, u"{0} -- warning".format(__AppName__),
                                u"动/静文件校验符格式错误")
            return
        dReg, jReg = regList[0], regList[1]
        dirNums = self.listWidgetBatchDirs.count()
        if self.chbBatchStaticFile.isChecked():
            staticFile = unicode(self.txtBatchStaticFile.text())
            if not staticFile:
                QMessageBox.warning(self, u"{0} -- warning".format(__AppName__),
                                    u"请输入静态文件")
                return
            for i in range(dirNums):
                rawDir = unicode(self.listWidgetBatchDirs.item(i).text())
                fileList = os.listdir(rawDir)
                for f in fileList:
                    if f.lower().endswith(dReg):
                        filePath = os.path.join(rawDir, f)
                        self.listWidgetBatchFiles.addItem(staticFile)
                        self.listWidgetBatchFiles.addItem(filePath)
        else:
            for i in range(dirNums):
                rawDir = unicode(self.listWidgetBatchDirs.item(i).text())
                fileList = os.listdir(rawDir)
                for df in fileList:
                    if df.lower().endswith(dReg):
                        jfLower = df.lower().replace(dReg, jReg)
                        fileLowerList = [item.lower() for item in fileList]
                        if jfLower in fileLowerList:
                            index = fileLowerList.index(jfLower)
                            jf = fileList[index]
                            jfilePath = os.path.join(rawDir, jf)
                            dfilePath = os.path.join(rawDir, df)
                            self.listWidgetBatchFiles.addItem(jfilePath)
                            self.listWidgetBatchFiles.addItem(dfilePath)

    @pyqtSignature("QString")
    def on_txtBatchDynFileReg_textChanged(self):
        self.updateBatchFiles()

    @pyqtSignature("")
    def on_pbtnBatchAddDir_clicked(self):
        directory = unicode(QFileDialog.getExistingDirectory(self, u"添加目录...",
                                                             directory=self._dir,))
        if not directory:
            return
        self.listWidgetBatchDirs.addItem(directory)
        self.updateBatchFiles()

    @pyqtSignature("")
    def on_pbtnBatchDelDir_clicked(self):
        index = self.listWidgetBatchDirs.currentRow()
        if index >= 0:
            self.listWidgetBatchDirs.takeItem(index)
            self.updateBatchFiles()

    @pyqtSignature("")
    def on_pbtnBatchResultDir_clicked(self):
        directory = unicode(QFileDialog.getExistingDirectory(self, u"选择目录...",
                                                             directory=self._dir, ))
        if directory:
            self.txtBatchResultDir.setText(directory)

    @pyqtSignature("")
    def on_txtBatchResultDir_lostFocus(self):
        fileName = self.txtBatchResultDir.text()
        if fileName.isEmpty():
            return
        f = QFileInfo(fileName)
        if f.exists() and f.isDir():
            return
        else:
            QMessageBox.warning(self, u"{0} -- warning".format(__AppName__),
                                u"{0}文件目录不存在".format(unicode(fileName)))
            self.txtBatchResultDir.setText('')

    @pyqtSignature("int")
    def on_spbFileHeaderNums_valueChanged(self, rows):
        self.balance.setHeaderRows(rows)

    @pyqtSignature("int")
    def on_spbFileFooterNums_valueChanged(self, rows):
        self.balance.setFooterRows(rows)

    @pyqtSignature("int")
    def on_spbAngleStartCol_valueChanged(self, col):
        self.balance.setAngleStartCol(col)

    @pyqtSignature("int")
    def on_spbAngleEndCol_valueChanged(self, col):
        self.balance.setAngleEndCol(col)

    @pyqtSignature("int")
    def on_spbForceStartCol_valueChanged(self, col):
        self.balance.setForceStartCol(col)
        self.spbForceEndCol.setValue(col + 5)

    @pyqtSignature("")
    def on_txtColumnOffset_lostFocus(self):
        dicString = unicode(self.txtColumnOffset.text())
        try:
            dic = eval("{" + unicode(dicString) + "}")
            if dic:
                self.balance.setColumnOffset(dic)
        except Exception, e:
            QMessageBox.warning(self, u"警告", u"角度偏移量格式不正确，请重新输入\n{0}".format(e.message))
            self.txtColumnOffset.setText('')

    @pyqtSignature("")
    def on_pbtnBalanceInfo_clicked(self):
        QMessageBox.about(self, u"当前设置信息", unicode(self.balance))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    dataTrans = DataTransWidget()
    dataTrans.show()
    app.exec_()
