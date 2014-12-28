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
import codecs

from dataDynRigTrans.dataDynRigTransUi import Ui_dataTransWidget
#from dataTrans import Model,BalanceG18
import numpy as np

class dataTransWidget(QDialog, Ui_dataTransWidget):
    def __init__(self, parent=None):
        super(dataTransWidget, self).__init__(parent)
        self.setupUi(self)
        self.txtModelArea.setValidator(QDoubleValidator())
        self.txtModelSpan.setValidator(QDoubleValidator())
        self.txtModelRootChord.setValidator(QDoubleValidator())
        self.txtModelRefChord.setValidator(QDoubleValidator())
        self.txtWindSpeed.setValidator(QDoubleValidator())
        self.txtDeltaX.setValidator(QDoubleValidator())
        self.txtDeltaY.setValidator(QDoubleValidator())
        self.txtDeltaZ.setValidator(QDoubleValidator())
        self.txtSampleRate.setValidator(QDoubleValidator())
        self.txtKineticsFre.setValidator(QDoubleValidator())
        self.txtPhi0.setValidator(QDoubleValidator())
        self.txtIgnorePoints.setValidator(QIntValidator())
        self.cbBalanceSty.addItems(__BalanceSty__)
        self.cbKineticsSty.addItems(__KineticsSty__)

        self.BalanceSty = self.cbBalanceSty.currentIndex()  # 初始化天平类型
        self.ModelArea = float(self.txtModelArea.text())    # 初始化模型面积
        self.ModelSpan = float(self.txtModelSpan.text())    # 初始化模型展长
        self.ModelRootChord = float(self.txtModelRootChord.text())   # 初始化模型根弦长
        self.ModelRefChord = float(self.txtModelRefChord.text())     # 初始化模型参考弦长
        self.WindSpeed = float(self.txtWindSpeed.text())             # 初始化试验风速
        self.TotalPressure = 0.5 * AIR_DENSITY * self.WindSpeed ** 2  # 初始化来流总压（根据试验风速计算得到）
        self.DeltaX = float(self.txtDeltaX.text())                    # 初始化deltaX
        self.DeltaY = float(self.txtDeltaY.text())
        self.DeltaZ = float(self.txtDeltaZ.text())
        self.StaFile = ""
        self.DynFile = ""
        self.BodyFile = ""
        self.AeroFile = ""
        self.KineticsSty = self.cbKineticsSty.currentIndex()    # 初始化运动类型
        self.SampleRate = float(self.txtSampleRate.text())      # 初始化采样频率
        self.KineticsFre = float(self.txtKineticsFre.text())    # 初始化运动频率
        self.Phi0 = float(self.txtPhi0.text())                  # 初始化起始滚转角
        self.HeaderRows = self.spbFileHeaderNums.value()        # 给定文件标题行数
        self.IgnorePoints = float(self.txtIgnorePoints.text())  # 给定文件处理忽略点数

        self._dir = "./"

    @pyqtSignature("int")
    def on_cbBalanceSty_activated(self, index):
        self.BalanceSty = index

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
                    params1 = [s.split('\t')[1].encode('ascii') for s in rawData[:5] ]
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
            self.StaFile = staticFn

    @pyqtSignature("QString")
    def on_txtStaticFile_textChanged(self, fileName):
        f = QFileInfo(fileName)
        if f.exists() and f.isFile():
            self.StaFile = f
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
            self.DynFile = dynFn

    @pyqtSignature("QString")
    def on_txtDynamicFile_textChanged(self, fileName):
        f = QFileInfo(fileName)
        if f.exits() and f.isFile():
            self.DynFile = f
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
            self.BodyFile = bodyFn

    @pyqtSignature("QString")
    def on_txtBodyFile_textChanged(self, fileName):
        f = QFileInfo(fileName)
        if f.dir().exists and not f.baseName().isEmpty() and not f.suffix().isEmpty():
            self.BodyFile = f
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
            self.AeroFile = aeroFn

    @pyqtSignature("QString")
    def on_txtAeroFile_textChanged(self, fileName):
        f = QFileInfo(fileName)
        if f.dir().exists and not f.baseName().isEmpty() and not f.suffix().isEmpty():
            self.AeroFile = f
        else:
            QMessageBox.warning(self, u"{0} -- warning".format(__appname__),
                                u"{0}不是有效文件".format(unicode(fileName)))

    @pyqtSignature("")
    def on_pbtnGenerateFile_clicked(self):
        if self.generateData():
            QMessageBox.about(self, u"{0}".format(__appname__), u"数据生成完成！")
        else:
            QMessageBox.about(self, u"{0}".format(__appname__), u"数据生成失败，请检查数据是否完整。")

    @pyqtSignature("")
    def on_pbtnHelp_clicked(self):
        QMessageBox.about(self, "Hello", u'''注意事项：
            1、请输入正确的模型参数值！
            2、请不要改动输出模型参数的格式，否则可能引起载入模型参数文件失败。''')

    @pyqtSignature("QString")
    def on_txtModelArea_textChanged(self, txtArea):
        self.ModelArea = float(txtArea)

    @pyqtSignature("QString")
    def on_txtModelSpan_textChanged(self, txtSpan):
        self.ModelSpan = float(txtSpan)

    @pyqtSignature("QString")
    def on_txtModelRootChord_textChanged(self, txtRootChord):
        self.ModelRootChord = float(txtRootChord)

    @pyqtSignature("QString")
    def on_txtModelRefChord_textChanged(self, txtRefChord):
        self.ModelRefChord = float(txtRefChord)

    @pyqtSignature("QString")
    def on_txtWindSpeed_textChanged(self, txtWindSpeed):
        self.WindSpeed = float(txtWindSpeed)
        self.TotalPressure = 0.5*AIR_DENSITY*self.WindSpeed**2

    @pyqtSignature("QString")
    def on_txtDeltaX_textChanged(self, txtDeltaX):
        self.DeltaX = float(txtDeltaX)

    @pyqtSignature("QString")
    def on_txtDeltaY_textChanged(self, txtDeltaY):
        self.DeltaY = float(txtDeltaY)


    @pyqtSignature("QString")
    def on_txtDeltaZ_textChanged(self, txtDeltaZ):
        self.DeltaZ = float(txtDeltaZ)

    @pyqtSignature("int")
    def on_spbFileHeaderNums_valueChanged(self, rows):
        self.HeaderRows = rows

    @pyqtSignature("int")
    def on_cbKineticsSty_valuechanged(self, index):
        self.KineticsSty = index

    @pyqtSignature("QString")
    def on_txtSamplingRate_textChanged(self, txtSampleRate):
        self.SampleRate = float(txtSampleRate)

    @pyqtSignature("QString")
    def on_txtKineticsFre_textChanged(self, txtFre):
        self.KineticsFre = float(txtFre)

    @pyqtSignature("QString")
    def on_txtIgnorePoints_textChanged(self, txtIgnorePoints):
        self.IgnorePoints = int(float(txtIgnorePoints))

    @pyqtSignature("QString")
    def on_txtPhi0_textChanged(self, txtPhi0):
        self.Phi0 = float(txtPhi0)

    def generateData(self):
        try:
            if 0 == self.BalanceSty:  # 14杆天平
                print u"14杆天平"
                pass

            if 1 == self.BalanceSty:  # 16杆天平
                print u"16杆天平"
                pass

            if 2 == self.BalanceSty:  # 18杆天平
                print u"18杆天平"
                if 0 == self.KineticsSty:    # Pitch
                    print "KS1"
                    self.balanceG18()
                if 1 == self.KineticsSty:    # Roll
                    pass
                if 2 == self.KineticsSty:    # Yaw
                    pass

            if 3 == self.BalanceSty:  # 盒式天平
                print u'盒式天平'
                pass

            return True

        except:
            return False

    def balanceG18(self):
        print "G1"
        cirPs = np.round(1./self.KineticsFre*self.SampleRate)

        staMaxPs = self.getMaxPs(self.StaFile, self.HeaderRows, self.IgnorePoints)
        print "g2"
        staBinPs = int(staMaxPs + cirPs/2.+1)  # python中np.round的.5为舍去，这里为了和matlib程序统一，所以+1
        staData = self.getRawData(self.StaFile, self.HeaderRows)
        print "g3"
        staStopPs = staBinPs + cirPs
        angle = staData[staBinPs-1:staStopPs, 1:5]
        staCoe = self.getAverageData(staData, cirPs, staBinPs)
        print "g4"

        dynMaxPs = self.getMaxPs(self.DynFile, self.HeaderRows, self.IgnorePoints)
        print "g5"
        dynBinPs = int(dynMaxPs + cirPs/2. + 1)
        dynData = self.getRawData(self.DynFile, self.HeaderRows)
        print "g6"
        #dynStopPs = dynBinPs + cirPs
        dynCoe = self.getAverageData(dynData, cirPs, dynBinPs)

        aeroAngle = self.getAeroAngle(angle, cirPs)

        Ct = self.calcuTempCt(dynCoe, staCoe, cirPs)
        Ctw=np.zeros((cirPs,6))
        dx = self.DeltaX
        dy = self.DeltaY
        dz = self.DeltaZ
        for i in xrange(cirPs):
            Ctw[i,0]=Ct[i,0]
            Ctw[i,1]=Ct[i,1]
            Ctw[i,2]=Ct[i,2]
            Ctw[i,3]=Ct[i,3]+Ct[i,2]*dy-Ct[i,1]*dz
            Ctw[i,4]=Ct[i,4]-Ct[i,0]*dz-Ct[i,2]*dx
            Ctw[i,5]=Ct[i,5]+Ct[i,0]*dy+Ct[i,1]*dx

        Cq = self.getTempAeroCoe(aeroAngle, Ctw, cirPs)

        q = self.TotalPressure
        s = self.ModelArea
        l = self.ModelSpan
        ba = self.ModelRefChord
        for i in xrange(cirPs):
            Ctw[i,0]=Ctw[i,0]*9.8/(q*s)
            Ctw[i,1]=Ctw[i,1]*9.8/(q*s)
            Ctw[i,2]=Ctw[i,2]*9.8/(q*s)
            Ctw[i,3]=Ctw[i,3]*9.8/(q*s*l)
            Ctw[i,4]=Ctw[i,4]*9.8/(q*s*l)
            Ctw[i,5]=Ctw[i,5]*9.8/(q*s*ba)
            
            Cq[i,0]=Cq[i,0]*9.8/(q*s)
            Cq[i,1]=Cq[i,1]*9.8/(q*s)
            Cq[i,2]=Cq[i,2]*9.8/(q*s)
            Cq[i,3]=Cq[i,3]*9.8/(q*s*l)
            Cq[i,4]=Cq[i,4]*9.8/(q*s*l)
            Cq[i,5]=Cq[i,5]*9.8/(q*s*ba)

        t = np.linspace(0.001, cirPs/1000., cirPs)

        m,n = Ctw.shape
        ag = aeroAngle
        with open(self.BodyFile,"w") as f:
            f.write("%d\t\t\t%d\n" % (m, n+5))
            f.write("%-s\t%-s\t%-s\t%-s\t%-s\t%-s\t%-s\t%-s\t%-s\t%-s\t%-s\t\n" \
                    %("Time","α","β","φ","θ","CA","CN","CY","Cl","Cn","Cm"))
            for i in xrange(m):
                f.write("%-.4f\t%-.4f\t%-.4f\t%-.4f\t%-.4f\t%-.4f\t%-.4f\t%-.4f\t%-.4f\t%-.4f\t%-.4f\t\n" \
                        % (t[i],ag[i,0],ag[i,1],ag[i,2],ag[i,3],Ctw[i,0],Ctw[i,1],Ctw[i,2],Ctw[i,3],Ctw[i,4],Ctw[i,5]))
            f.write("%-.4f\t%-.4f\t%-.4f\t%-.4f\t%-.4f\t%-.4f\t%-.4f\t%-.4f\t%-.4f\t%-.4f\t%-.4f\t\n" \
                    % (t[m-1]+0.001,ag[0,0],ag[0,1],ag[0,2],ag[0,3],Ctw[0,0],Ctw[0,1],Ctw[0,2],Ctw[0,3],Ctw[0,4],Ctw[0,5]))

        with open(self.AeroFile,"w") as f:
            f.write("%d\t\t\t%d\n" % (m, n+5))
            f.write("%-s\t%-s\t%-s\t%-s\t%-s\t%-s\t%-s\t%-s\t%-s\t%-s\t%-s\t\n" \
                    %("Time","α","β","φ","θ","CA","CN","CY","Cl","Cn","Cm"))
            for i in xrange(m):
                f.write("%-.4f\t%-.4f\t%-.4f\t%-.4f\t%-.4f\t%-.4f\t%-.4f\t%-.4f\t%-.4f\t%-.4f\t%-.4f\t\n" \
                        % (t[i],ag[i,0],ag[i,1],ag[i,2],ag[i,3],Cq[i,0],Cq[i,1],Cq[i,2],Cq[i,3],Cq[i,4],Cq[i,5]))
            f.write("%-.4f\t%-.4f\t%-.4f\t%-.4f\t%-.4f\t%-.4f\t%-.4f\t%-.4f\t%-.4f\t%-.4f\t%-.4f\t\n" \
                    % (t[m-1]+0.001,ag[0,0],ag[0,1],ag[0,2],ag[0,3],Cq[0,0],Cq[0,1],Cq[0,2],Cq[0,3],Cq[0,4],Cq[0,5]))

    def getMaxPs(self,fileName,headerRows,ignorePs):
        rawData = self.getRawData(fileName,headerRows)
        maxPoint =  ignorePs - 1    #计算第一个周期中的最高点数（起始位置），第n个点在数组中的位置为n-1
        if 0 == self.KineticsSty:
            i = 1
        elif 1 == self.KineticsSty:
            i = 3
        while rawData[maxPoint,i] <= rawData[maxPoint + 1,i]:
            maxPoint+=1
        return maxPoint+1   #结果返回最大点的位置，是因为Python的点数索引从0开始。

    def getRawData(self,fileName,headerRows):
        with open(fileName,"r") as f:
            rawData = np.loadtxt(f.readlines()[headerRows:], dtype=np.float)
        return rawData

    def getAverageData(self,data,cirPs,binPs):
        Cn=np.zeros((cirPs,6)) #构造数据集
        for j in xrange(9):
            for i in xrange(cirPs):
                k=binPs+i+cirPs*(j-1)-1   #每个周期对应的点 = 开始点+周期内某个点+周期数*周期点数
                Cn[i,0]=Cn[i,0]+data[k,5]
                Cn[i,1]=Cn[i,1]+data[k,6]
                Cn[i,2]=Cn[i,2]+data[k,7]
                Cn[i,3]=Cn[i,3]+data[k,8]
                Cn[i,4]=Cn[i,4]+data[k,9]
                Cn[i,5]=Cn[i,5]+data[k,10]
        return Cn/9.
    
    def getAeroAngle(self,angle,cirPs):
        '''
        计算气动角度
        '''
        aeroAngle=np.zeros((cirPs,4))    #np.zeros(shape) shape为元组类型
        for i in xrange(cirPs):
            aeroAngle[i,0]=atand((sind(angle[i,0])*cosd(angle[i,2])-cosd(angle[i,0])*sind(angle[i,1])*sind(angle[i,2]))/(cosd(angle[i,0])*cosd(angle[i,1])))
            aeroAngle[i,1]=asind(sind(angle[i,0])*sind(angle[i,2])+cosd(angle[i,0])*sind(angle[i,1])*cosd(angle[i,2]))
            aeroAngle[i,2]=angle[i,2]+self.Phi0
            aeroAngle[i,3]=angle[i,3]

        return aeroAngle

    def calcuTempCt(self,dynData,staData,cirPs):
        '''
        根据天平系数计算临时的Ct
        '''
        Cy = dynData
        Cn = staData
        Cy=Cy-Cn
        Ct=np.zeros((cirPs,6))
        for i in xrange(cirPs):
            cxw0=6.11960*Cy[i,0]
            cyw0=12.33276*Cy[i,1]
            czw0=4.76279*Cy[i,2]
            cmxw0=0.38218*Cy[i,3]
            cmyw0=0.19456*Cy[i,4]
            cmzw0=0.69732*Cy[i,5]
            Ct[i,0]=cxw0
            Ct[i,1]=cyw0
            Ct[i,2]=czw0
            Ct[i,3]=cmxw0
            Ct[i,4]=cmyw0
            Ct[i,5]=cmzw0
            for k in xrange(100):
                Ct[i,0]=cxw0+0.00548*Ct[i,1]+0.10290*Ct[i,2]+0.12796*Ct[i,3]+1.03638*Ct[i,4]-0.21182*Ct[i,5] \
                        +0.00090*Ct[i,0]*Ct[i,0]-0.00023*Ct[i,0]*Ct[i,1]+0.00034*Ct[i,0]*Ct[i,2]+0.00198*Ct[i,0]*Ct[i,3] \
                        +0.00447*Ct[i,0]*Ct[i,4]-0.00065*Ct[i,0]*Ct[i,5]-0.00001*Ct[i,1]*Ct[i,2]-0.00444*Ct[i,1]*Ct[i,3] \
                        -0.00041*Ct[i,1]*Ct[i,4]+0.00512*Ct[i,1]*Ct[i,5]+0.00014*Ct[i,2]*Ct[i,2]-0.00243*Ct[i,2]*Ct[i,3] \
                        -0.00292*Ct[i,2]*Ct[i,4]+0.00033*Ct[i,2]*Ct[i,5]-0.31818*Ct[i,3]*Ct[i,3]+0.04225*Ct[i,3]*Ct[i,4] \
                        +0.27065*Ct[i,3]*Ct[i,5]-0.02223*Ct[i,4]*Ct[i,4]-0.01045*Ct[i,4]*Ct[i,5]-0.02171*Ct[i,5]*Ct[i,5]
                Ct[i,1]=cyw0-0.01686*Ct[i,0]+0.01297*Ct[i,2]-0.23388*Ct[i,3]-0.19139*Ct[i,4]+0.18227*Ct[i,5] \
                        -0.00010*Ct[i,1]*Ct[i,1]-0.00010*Ct[i,1]*Ct[i,0]+0.00004*Ct[i,1]*Ct[i,2]-0.00274*Ct[i,1]*Ct[i,3] \
                        +0.00056*Ct[i,1]*Ct[i,4]+0.00107*Ct[i,1]*Ct[i,5]+0.00045*Ct[i,0]*Ct[i,0]+0.00030*Ct[i,0]*Ct[i,2] \
                        +0.00077*Ct[i,0]*Ct[i,3]+0.00181*Ct[i,0]*Ct[i,4]-0.00549*Ct[i,0]*Ct[i,5]-0.00006*Ct[i,2]*Ct[i,2] \
                        -0.01497*Ct[i,2]*Ct[i,3]+0.00340*Ct[i,2]*Ct[i,4]+0.00213*Ct[i,2]*Ct[i,5]-0.03901*Ct[i,3]*Ct[i,3] \
                        -0.15065*Ct[i,3]*Ct[i,4]+0.02407*Ct[i,3]*Ct[i,5]+0.00754*Ct[i,4]*Ct[i,4]+0.02244*Ct[i,4]*Ct[i,5] \
                        -0.01096*Ct[i,5]*Ct[i,5]
                Ct[i,2]=czw0-0.02295*Ct[i,1]+0.00338*Ct[i,0]-0.17365*Ct[i,3]-0.36139*Ct[i,4]+0.00857*Ct[i,5] \
                        +0.00032*Ct[i,2]*Ct[i,2]-0.00009*Ct[i,2]*Ct[i,1]-0.00016*Ct[i,2]*Ct[i,0]+0.00366*Ct[i,2]*Ct[i,3] \
                        -0.00382*Ct[i,2]*Ct[i,4]+0.00146*Ct[i,2]*Ct[i,5]+0.00031*Ct[i,1]*Ct[i,1]-0.00050*Ct[i,1]*Ct[i,0] \
                        +0.02079*Ct[i,1]*Ct[i,3]-0.00222*Ct[i,1]*Ct[i,4]-0.00709*Ct[i,1]*Ct[i,5]+0.00045*Ct[i,0]*Ct[i,0] \
                        +0.00588*Ct[i,0]*Ct[i,3]+0.01732*Ct[i,0]*Ct[i,4]-0.00223*Ct[i,0]*Ct[i,5]-0.12878*Ct[i,3]*Ct[i,3] \
                        +0.09362*Ct[i,3]*Ct[i,4]-0.24968*Ct[i,3]*Ct[i,5]+0.08996*Ct[i,4]*Ct[i,4]+0.01747*Ct[i,4]*Ct[i,5] \
                        +0.01161*Ct[i,5]*Ct[i,5]
                Ct[i,3]=cmxw0+0.00068*Ct[i,1]-0.00015*Ct[i,2]+0.00010*Ct[i,0]-0.0073*Ct[i,4]+0.01998*Ct[i,5] \
                        -0.00141*Ct[i,3]*Ct[i,3]-0.00067*Ct[i,3]*Ct[i,1]-0.00055*Ct[i,3]*Ct[i,2]+0.00016*Ct[i,3]*Ct[i,0] \
                        -0.00475*Ct[i,3]*Ct[i,4]+0.00236*Ct[i,3]*Ct[i,5]-0.00001*Ct[i,1]*Ct[i,1]+0.00001*Ct[i,2]*Ct[i,1] \
                        +0.00002*Ct[i,1]*Ct[i,0]+0.00025*Ct[i,1]*Ct[i,4]+0.00025*Ct[i,1]*Ct[i,5]-0.00003*Ct[i,2]*Ct[i,2] \
                        +0.00002*Ct[i,2]*Ct[i,0]+0.00026*Ct[i,2]*Ct[i,4]+0.00004*Ct[i,2]*Ct[i,5]-0.00004*Ct[i,0]*Ct[i,0] \
                        -0.00042*Ct[i,0]*Ct[i,4]+0.00023*Ct[i,0]*Ct[i,5]-0.00954*Ct[i,4]*Ct[i,4]-0.00136*Ct[i,4]*Ct[i,5] \
                        +0.00219*Ct[i,5]*Ct[i,5]
                Ct[i,4]=cmyw0-0.00007*Ct[i,1]+0.00227*Ct[i,2]+0.00113*Ct[i,3]-0.00012*Ct[i,0]+0.00488*Ct[i,5] \
                        +0.00714*Ct[i,4]*Ct[i,4]+0.00000*Ct[i,4]*Ct[i,1]-0.00010*Ct[i,4]*Ct[i,2]-0.00955*Ct[i,4]*Ct[i,3] \
                        +0.00158*Ct[i,0]*Ct[i,0]-0.00279*Ct[i,4]*Ct[i,5]+0.00001*Ct[i,1]*Ct[i,1]+0.00058*Ct[i,1]*Ct[i,3] \
                        -0.00035*Ct[i,1]*Ct[i,5]+0.00001*Ct[i,2]*Ct[i,2]-0.00035*Ct[i,2]*Ct[i,3]-0.00005*Ct[i,2]*Ct[i,0] \
                        -0.00006*Ct[i,2]*Ct[i,5]-0.00180*Ct[i,3]*Ct[i,3]+0.00022*Ct[i,3]*Ct[i,0]-0.02256*Ct[i,3]*Ct[i,5] \
                        -0.00005*Ct[i,0]*Ct[i,0]+0.00090*Ct[i,0]*Ct[i,5]-0.00117*Ct[i,5]*Ct[i,5]
                Ct[i,5]=cmzw0+0.00041*Ct[i,1]-0.00087*Ct[i,2]-0.05093*Ct[i,3]-0.03029*Ct[i,4]+0.00121*Ct[i,0] \
                        -0.00147*Ct[i,5]*Ct[i,5]-0.00009*Ct[i,5]*Ct[i,1]+0.00000*Ct[i,5]*Ct[i,2]+0.00302*Ct[i,5]*Ct[i,3] \
                        -0.00159*Ct[i,5]*Ct[i,4]+0.00169*Ct[i,5]*Ct[i,0]-0.00019*Ct[i,1]*Ct[i,3]-0.00007*Ct[i,1]*Ct[i,4] \
                        +0.00001*Ct[i,1]*Ct[i,0]-0.00001*Ct[i,2]*Ct[i,2]+0.00035*Ct[i,2]*Ct[i,3]+0.00011*Ct[i,2]*Ct[i,4] \
                        +0.00001*Ct[i,2]*Ct[i,0]-0.00497*Ct[i,3]*Ct[i,3]+0.01545*Ct[i,3]*Ct[i,4]-0.00069*Ct[i,3]*Ct[i,0] \
                        -0.00108*Ct[i,4]*Ct[i,4]+0.00031*Ct[i,4]*Ct[i,5]+0.00001*Ct[i,0]*Ct[i,0]

        return Ct

    def getTempAeroCoe(self,angle,bodyData,cirPs):
        # 得到有量纲的风轴下气动数据
        aeroAngle = angle
        Ctw = bodyData
        Cq=np.zeros((cirPs,6))
        for i in xrange(cirPs):
            Cq[i,0]=cosd(aeroAngle[i,0])*cosd(aeroAngle[i,1])*Ctw[i,0]+sind(aeroAngle[i,0])*cosd(aeroAngle[i,1])*Ctw[i,1] \
                    -sind(aeroAngle[i,1])*Ctw[i,2]
            Cq[i,1]=-sind(aeroAngle[i,0])*Ctw[i,0]+cosd(aeroAngle[i,0])*Ctw[i,1]
            Cq[i,2]=cosd(aeroAngle[i,0])*sind(aeroAngle[i,1])*Ctw[i,0]+sind(aeroAngle[i,0])*sind(aeroAngle[i,1])*Ctw[i,1] \
                    +cosd(aeroAngle[i,1])*Ctw[i,2]
            Cq[i,3]=cosd(aeroAngle[i,0])*cosd(aeroAngle[i,1])*Ctw[i,3]-sind(aeroAngle[i,0])*cosd(aeroAngle[i,0])*Ctw[i,4] \
                    +sind(aeroAngle[i,1])*Ctw[i,5]
            Cq[i,4]=sind(aeroAngle[i,0])*Ctw[i,3]+cosd(aeroAngle[i,0])*Ctw[i,4]
            Cq[i,5]=-cosd(aeroAngle[i,0])*sind(aeroAngle[i,1])*Ctw[i,3]+sind(aeroAngle[i,0])*sind(aeroAngle[i,1])*Ctw[i,4] \
                    +cosd(aeroAngle[i,1])*Ctw[i,5]
        return Cq

if __name__ == "__main__":
    app = QApplication(sys.argv)
    dataTrans = dataTransWidget()
    dataTrans.show()
    app.exec_()



