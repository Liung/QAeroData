#coding: UTF-8
from __future__ import division
import math
import os
import re
import shutil
import string

import numpy as np


__author__ = 'Vincent'

'''
本文件为天平数据处理程序,包含：
BalanceG18——》18杆天平
BalanceG16——》16杆天平
BalanceG14——》14杆天平
BalanceBox——》盒式天平
'''

AIR_DENSITY = 1.2250  # 空气密度
ABSOLUTE_ZERO = 273.15  # 绝对零度
DYN_PITCH, DYN_YAW, DYN_ROLL, STA_PITCH, STA_YAW, STA_ROLL = range(6)

def sind(deg):
    return np.sin(np.deg2rad(deg))

def asind(num):
    return np.rad2deg(np.arcsin(num))

def atand(num):
    return np.rad2deg(np.arctan(num))

def cosd(deg):
    return np.cos(np.deg2rad(deg))

class Model(object):
    pass

class AircraftModel(Model):
    def __init__(self,area=0.,span=0.,rootChord=0.,refChord=0.):
        self.Area = area
        self.Span = span
        self.RootChord = rootChord
        self.RefChord = refChord

        #初始化数据：
        self.WindSpeed = 25
        self.FlowPressure = 0.5*AIR_DENSITY*self.WindSpeed**2
        self.CelsiusTemperature = 25
        self.KelvinTemperature = self.CelsiusTemperature + ABSOLUTE_ZERO

        self.BalanceDeltaX = 0.
        self.BalanceDeltaY = 0.
        self.BalanceDeltaZ = 0.

    def setWindSpeed(self,windSpeed=0.):
        self.WindSpeed = windSpeed
        self.FlowPressure = 0.5*AIR_DENSITY*self.WindSpeed**2

    def setFlowPressure(self,flowPressure=0.):
        self.FlowPressure = flowPressure
        self.WindSpeed = math.sqrt(2.*flowPressure/AIR_DENSITY)

    def setCelsiusTemperature(self,celsiusTemperature=0.):
        self.CelsiusTemperature = celsiusTemperature
        self.KelvinTemperature = celsiusTemperature + ABSOLUTE_ZERO

    def setKelvinTemperature(self,kelvinTemperature=273.15):
        self.KelvinTemperature = kelvinTemperature
        self.CelsiusTemperature = kelvinTemperature - ABSOLUTE_ZERO

    def setBalanceDistance(self, deltaX=0., deltaY=0, deltaZ=0.):
        self.BalanceDeltaX = deltaX
        self.BalanceDeltaY = deltaY
        self.BalanceDeltaZ = deltaZ


def BalanceG18(staFile='', dynFile='', aeroFile='', bodyFile='',
               headerRows=1, phi0=0, aircraftModel=None):

    dx = aircraftModel.BalanceDeltaX
    dy = aircraftModel.BalanceDeltaY
    dz = aircraftModel.BalanceDeltaZ
    q = aircraftModel.FlowPressure
    s = aircraftModel.Area
    l = aircraftModel.Span
    ba = aircraftModel.RefChord

    jf = open(staFile,'r')
    df = open(dynFile,'r')
    jdata = np.loadtxt(jf.readlines()[headerRows:], dtype=np.float)
    ddata = np.loadtxt(df.readlines()[headerRows:], dtype=np.float)
    jf.close()
    df.close()

    angle = jdata[:,1:5]
    Cy = jdata[:,5:11]
    Cn = ddata[:,5:11]
    Cy=Cy-Cn
    aeroAngle = np.zeros_like(angle)
    Ct=np.zeros_like(Cy)
    Ctw=np.zeros_like(Cy)
    Cq=np.zeros_like(Cy)
    aeroCoe = np.zeros_like(Cy)
    bodyCoe = np.zeros_like(Cy)
    m, = angle.shape
    t = np.linspace(0.001,m/1000,m)

    for i in xrange(m): 
        aeroAngle[i,0] = atand((sind(angle[i,0])*cosd(angle[i,2])-cosd(angle[i,0])*sind(angle[i,1])*sind(angle[i,2]))/(cosd(angle[i,0])*cosd(angle[i,1])))
        aeroAngle[i,1]=asind(sind(angle[i,0])*sind(angle[i,2])+cosd(angle[i,0])*sind(angle[i,1])*cosd(angle[i,2]))
        aeroAngle[i,2]=angle[i,2]+phi0
        aeroAngle[i,3]=angle[i,3]
        
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

    
        Ctw[i,0]=Ct[i,0]*0.95
        Ctw[i,1]=Ct[i,1]*0.98
        Ctw[i,2]=Ct[i,2]
        Ctw[i,3]=Ct[i,3]+Ct[i,2]*dy-Ct[i,1]*dz
        Ctw[i,4]=Ct[i,4]-Ct[i,0]*dz-Ct[i,2]*dx
        Ctw[i,5]=(Ct[i,5]+Ct[i,0]*dy+Ct[i,1]*dx)*0.56

    
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

        aeroCoe[i,0]=Cq[i,0]*9.8/(q*s)
        aeroCoe[i,1]=Cq[i,1]*9.8/(q*s)
        aeroCoe[i,2]=Cq[i,2]*9.8/(q*s)
        aeroCoe[i,3]=Cq[i,3]*9.8/(q*s*l)
        aeroCoe[i,4]=Cq[i,4]*9.8/(q*s*l)
        aeroCoe[i,5]=Cq[i,5]*9.8/(q*s*ba)

        bodyCoe[i,0]=Ctw[i,0]*9.8/(q*s)
        bodyCoe[i,1]=Ctw[i,1]*9.8/(q*s)
        bodyCoe[i,2]=Ctw[i,2]*9.8/(q*s)
        bodyCoe[i,3]=Ctw[i,3]*9.8/(q*s*l)
        bodyCoe[i,4]=Ctw[i,4]*9.8/(q*s*l)
        bodyCoe[i,5]=Ctw[i,5]*9.8/(q*s*ba)

        t = np.linspace(0.001,m/1000.,m)
        with open(bodyFile,"w") as f:
            #f.write("%d\t\t\t%d\n" % (m,n+5))
            f.write("%-s\t%-s\t%-s\t%-s\t%-s\t%-s\t%-s\t%-s\t%-s\t%-s\t%-s\t\n" \
                    %("Time","α","β","φ","θ","CA","CN","CY","Cl","Cn","Cm"))
            for i in xrange(m):
                f.write("%-.3f\t%-15.8f\t%-15.8f\t%-15.8f\t%-15.8f\t%-15.8f\t%-15.8f\t%-15.8f\t%-15.8f\t%-15.8f\t%-15.8f\t\n" \
                        % (t[i],aeroAngle[i,0],aeroAngle[i,1],aeroAngle[i,2],aeroAngle[i,3],bodyCoe[i,0],bodyCoe[i,1],bodyCoe[i,2],bodyCoe[i,3],bodyCoe[i,4],bodyCoe[i,5]))
            f.write("%-.3f\t%-15.8f\t%-15.8f\t%-15.8f\t%-15.8f\t%-15.8f\t%-15.8f\t%-15.8f\t%-15.8f\t%-15.8f\t%-15.8f\t\n" \
                    % (t[m-1]+0.001,aeroAngle[0,0],aeroAngle[0,1],aeroAngle[0,2],aeroAngle[0,3],bodyCoe[0,0],bodyCoe[0,1],bodyCoe[0,2],bodyCoe[0,3],bodyCoe[0,4],bodyCoe[0,5]))

        with open(aeroFile,"w") as f:
            #f.write("%d\t\t\t%d\n" % (m,n+5))
            f.write("%-s\t%-s\t%-s\t%-s\t%-s\t%-s\t%-s\t%-s\t%-s\t%-s\t%-s\t\n" \
                    %("Time","α","β","φ","θ","CA","CN","CY","Cl","Cn","Cm"))
            for i in xrange(m):
                f.write("%-.3f\t%-15.8f\t%-15.8f\t%-15.8f\t%-15.8f\t%-15.8f\t%-15.8f\t%-15.8f\t%-15.8f\t%-15.8f\t%-15.8f\t\n" \
                        % (t[i],aeroAngle[i,0],aeroAngle[i,1],aeroAngle[i,2],aeroAngle[i,3],aeroCoe[i,0],aeroCoe[i,1],aeroCoe[i,2],aeroCoe[i,3],aeroCoe[i,4],aeroCoe[i,5]))
            f.write("%-.3f\t%-15.8f\t%-15.8f\t%-15.8f\t%-15.8f\t%-15.8f\t%-15.8f\t%-15.8f\t%-15.8f\t%-15.8f\t%-15.8f\t\n" \
                    % (t[m-1]+0.001,aeroAngle[0,0],aeroAngle[0,1],aeroAngle[0,2],aeroAngle[0,3],aeroCoe[0,0],aeroCoe[0,1],aeroCoe[0,2],aeroCoe[0,3],aeroCoe[0,4],aeroCoe[0,5]))

class DynamicRig(object):
    def __init__(self,samplingRate=1000,kineticsFre=0.2,kineticsSty=DYN_PITCH):
        self.SampleRate = samplingRate
        self.KineticsFre = kineticsFre
        self.KineticsSty = kineticsSty

    def setOutputFileFormat(self,beginAngleColumn=1,stopAngleColumn=4,
                            beginForceColumn=5,stopForceColumn=10):
        self.BeginAngleColumn = beginAngleColumn
        self.StopAngleColumn = stopAngleColumn
        self.BeginForceColumn = beginForceColumn
        self.StopForceColumn = stopForceColumn

    def setSamplingRate(self,samplingRate=1000):
        self.SampleRate = samplingRate

    def setKineticsFre(self,kineticsFre=0.2):
        self.KineticsFre = kineticsFre

    def setKineticsSty(self,kineticsSty = DYN_PITCH):
        self.KineticsSty = kineticsSty


class DataFileInfo(object):
    def __init__(self, filePath=''):
        self.__filePath = filePath

    @property
    def filePath(self):
        return self.__filePath

    @filePath.setter
    def filePath(self, filePath):
        if isinstance(filePath, type('Hello')):
            self.__filePath = filePath
        else:
            raise TypeError('filePath is a type of str')

    def getKineticsSty(self):
        fileName = os.path.basename(self.__filePath)
        if string.upper(fileName[:2]) == 'DP':
            kineticsSty = DYN_PITCH
        elif string.upper(fileName[:2]) == 'DR':
            kineticsSty = DYN_ROLL
        else:
            kineticsSty = DYN_YAW

        return kineticsSty

    def getPitchAngle(self):
        # '''
        # DP_P60R00AP05_N05JF.txt
        # '''
        reStr = '(p|P)[-|+]{0,1}\d+(r|R)'
        fileName = os.path.basename(self.__filePath)
        m = re.search(reStr,fileName)
        pitchAngle = float(m.group()[1:-1]) if m is not None else 0

        return pitchAngle

    def getYawAngle(self):
        return 0.0

    def getRollAngle(self):
        # '''
        # DP_P60R00AP05_N05JF.txt
        # '''
        reStr = '(r|R)[-|+]{0,1}\d+(a|A)'
        fileName = os.path.basename(self.__filePath)
        m = re.search(reStr,fileName)
        rollAngle = float(m.group()[1:-1]) if m is not None else 0

        return rollAngle

    def getAmAngle(self):
        fileName = os.path.basename(self.__filePath)
        if fileName[:2] == 'DP':
            reStr = '(ap|AP)[-|+]{0,1}\d+(_n|_N)'
        elif fileName[:2] == 'DR':
            reStr = '(ar|AR)[-|+]{0,1}\d+(_n|_N)'
        else:
            pass
        m = re.search(reStr, fileName)
        am = float(m.group()[2:-2]) if m is not None else 0

        return am

    def getKineticsFre(self):
        reStr = '(n|N)[-|+]{0,1}\d+(j|d|J|D)'
        fileName = os.path.basename(self.__filePath)
        m = re.search(reStr, fileName)
        index = int(m.group()[1:-1]) if m is not None else 0

        return index*0.2

class DataFrDynRig(DynamicRig):
    def __init__(self, filePath='', sampleRate=1000., kineticsFre=0.2):
        super(DataFrDynRig, self).__init__(sampleRate, kineticsFre)
        self.FilePath = filePath
        self.CirlePts = int(1./self.KineticsFre*self.SampleRate)

    def setFilePath(self, filePath=''):
        self.FilePath = filePath

    def setDataFileFormat(self, headerRows=1, ignorePts=200):
        self.HeaderRows = headerRows
        self.IgnorePts = ignorePts

    def getMaxPts(self):
        rawData = self.getRawData()
        maxPoint =  self.IgnorePts - 1    #计算第一个周期中的最高点数（起始位置），第n个点在数组中的位置为n-1
        if DYN_PITCH == self.KineticsSty:
            i = 1
        elif DYN_YAW == self.KineticsSty:
            i = 2
        elif DYN_ROLL == self.KineticsSty:
            i = 3
        print u'运动类型：', i
        angle = DataFileInfo(self.FilePath)
        if angle.getKineticsSty() == DYN_PITCH:
            ans = angle.getPitchAngle() + angle.getAmAngle()
        elif angle.getKineticsSty() == DYN_ROLL:
            ans = angle.getAmAngle()   # 因为辨识角度列为相对角度
        else:
            ans = angle.getYawAngle() + angle.getAmAngle()
        print ans
        while rawData[maxPoint,i] < ans*0.85:
            maxPoint+=1
        while rawData[maxPoint,i] <= rawData[maxPoint + 1,i]:
            maxPoint+=1
        print 'MaxPoints:',maxPoint+1,'MaxAngle:', rawData[maxPoint,i]
        return maxPoint+1   # 结果返回最大点的位置，是因为Python的点数索引从0开始。

    def getBinPts(self):
        maxPts = self.getMaxPts()
        binPts = int(maxPts + self.CirlePts/2)  # 此处不需要+1
        print 'BinginPoints:', binPts
        return binPts

    def getRawData(self):
        fileName = self.FilePath
        headerRows = self.HeaderRows
        with open(fileName,"r") as f:
            rawData = np.loadtxt(f.readlines()[headerRows:], dtype=np.float)
        return rawData

    def getAngleData(self):
        staBinPs = self.getBinPts()
        staStopPs = staBinPs + self.CirlePts
        rawData = self.getRawData()
        angle = rawData[staBinPs-1:staStopPs-1, 1:5]

        return angle

    def getAverageCoeData(self):
        cirPs = self.CirlePts
        binPs = self.getBinPts()
        data = self.getRawData()
        Cn=np.zeros(shape=(cirPs, 6))  # 构造数据集
        for j in range(9):  # 9个周期平均
            for i in range(cirPs):
                k=binPs+i+cirPs*j - 1   # 每个周期对应的点 = 开始点+周期内某个点+周期数*周期点数
                Cn[i,0]=Cn[i,0]+data[k,5]
                Cn[i,1]=Cn[i,1]+data[k,6]
                Cn[i,2]=Cn[i,2]+data[k,7]
                Cn[i,3]=Cn[i,3]+data[k,8]
                Cn[i,4]=Cn[i,4]+data[k,9]
                Cn[i,5]=Cn[i,5]+data[k,10]
        return Cn/9.

def searchFileIter(fileDir=''):
    fileDir = os.path.abspath(fileDir)
    os.chdir(fileDir)
    if os.path.isdir(fileDir):
        jfileList = [item for item in os.listdir(fileDir)
                        if string.lower(item).endswith('jf.txt')]
        dfileList = [item for item in os.listdir(fileDir)
                        if string.lower(item).endswith('df.txt')]
        lowerJfileList = [string.lower(item) for item in jfileList]
        lowerDfileList = [string.lower(item) for item in dfileList]
        for id1,lowerJfile in enumerate(lowerJfileList):
            lowerDfile = lowerJfile.split('jf')[0] + 'df.txt'
            if lowerDfile in lowerDfileList:
                id2 = lowerDfileList.index(lowerDfile)
                yield os.path.abspath(jfileList[id1]),os.path.abspath(dfileList[id2])

def main():
    saccon = AircraftModel(span=0.4, area=0.0521,
                           rootChord=0.2759, refChord=0.1246)
    saccon.setWindSpeed(windSpeed=25)
    saccon.setBalanceDistance(deltaX=0, deltaY=0, deltaZ=0)

    fileDir = r"D:\Workspace\SACCON\20131223SACCON\Roll\Filter-Cutoff4-Order5"
    newPath = os.path.join(fileDir,'Results')
    print os.listdir(fileDir)
    if os.path.exists(newPath):
        shutil.rmtree(newPath)
    os.mkdir(newPath)
    for staFile,dynFile in searchFileIter(fileDir):
        #创建数据模型
        print staFile, '--->>', dynFile
        info = DataFileInfo(staFile)
        kineticsFre = info.getKineticsFre()
        kineticsSty = info.getKineticsSty()
        phi0 = info.getRollAngle()
        dataObj = DataFrDynRig(filePath=staFile, sampleRate=1000,kineticsFre=kineticsFre)
        dataObj.setKineticsSty(kineticsSty)
        dataObj.setDataFileFormat(headerRows=1,ignorePts=200)
        angle = dataObj.getAngleData()
        staCoe = dataObj.getAverageCoeData()

        dataObj.setFilePath(filePath=dynFile)
        dynCoe = dataObj.getAverageCoeData()

        tempFile = os.path.splitext(os.path.split(staFile)[1])
        aeroFile = tempFile[0].split('JF')[0] + 'FQ' + tempFile[1]
        aeroFile = os.path.join(newPath,aeroFile)
        bodyFile = tempFile[0].split('JF')[0] + 'FT' + tempFile[1]
        bodyFile = os.path.join(newPath,bodyFile)

        print aeroFile, '--->>', bodyFile

        balance = BalanceG18(staFile=staFile, dynFile=dynFile,
                             aeroFile=aeroFile, bodyFile=bodyFile,
                             aircraftModel=saccon)
        balance.setPhi0(phi0)
        aeroAngle = balance.getAeroAngle(angle)
        tempBodyData = balance.getTempBodyForceAndMoment(staData=staCoe,dynData=dynCoe)
        tempAeroData = balance.getTempAeroForceAndMoment(aeroAngle,tempBodyData)
        bodyData = balance.getForceAndMoment(tempBodyData)
        aeroData = balance.getForceAndMoment(tempAeroData)

        balance.writeToFile(aeroAngle, bodyData, aeroData)
if __name__ == '__main__':
    #创建一个SACCON模型
	import profile
	profile.run(main())




