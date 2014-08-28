#coding: UTF-8
# '''本文件主要为天平的数据处理文件：给定角度列和数据列，根据方法返回不同轴系下的气动数据'''
from __future__ import division
import numpy as np

__author__ = 'Vincent'

__balanceSty__ = [u"14杆天平", u"16杆天平", u"18杆天平", u"盒式天平"]  # 天平编号列表
#'''
#杆式天平：Beam Balance
#盒式天平：Box Balance
#'''
__airDensity__ = 1.225    #空气密度

def sind(deg):
    return np.sin(np.deg2rad(deg))
def asind(rad):
    return np.arcsin(rad)
def atand(rad):
    return np.arctan(rad)
def cosd(deg):
    return np.cos(np.deg2rad(deg))

class Model(object):

    def __init__(self,area=0.,span=0.,rootChord=0.,refChord=0.,totalPressure=0.,balanceSty = 2):
        self.Area = area
        self.Span = span
        self.RootChord = rootChord
        self.RefChord = refChord
        self.TotalPressure = totalPressure
        self.BalanceSty = balanceSty

    def setModelGeometry(self,area=0.,span=0.,rootChord=0.,refChord=0.):
        '''设置模型几何尺寸'''
        self.Area = area
        self.Span = span
        self.RootChord = rootChord
        self.RefChord = refChord

    def setTestConditions(self,totalPressure=0.):
        '''设置实验条件'''
        #self.WindSpeed = windSpeed
        self.TotalPressure = totalPressure

    def setBalanceSty(self,index):
        '''设置天平类型'''
        self.BalanceSty = index

    def getBalanceSty(self):
        '''返回天平类型'''
        return self.BalanceSty

class BalanceG18(object):
    '''
    十八杆天平
    '''
    def __init__(self,angle = None,staData = None,dynData = None,deltaX=0.,deltaY=0.,deltaZ=0.,phi0=0.):
        '''
        初始化天平数据，要求给出：
                angle：姿态角（欧拉角）；
                staData：静态气动数据数组；
                dynData：动态气动数据数组；
                deltaX：模型重心与天平中的ΔX
                deltaY：模型重心与天平中的ΔY
                deltaZ：模型重心与天平中的ΔZ
        '''
        self._angle = angle
        self._staData = staData
        self._dynData = dynData
        self.DeltaX = deltaX
        self.DeltaY = deltaY
        self.DeltaZ = deltaZ
        self.Phi0 = phi0

    def setPhi0(self,phi0=0.):
        '''
        如果为横航向运动，必须给出强迫振荡的中心滚转角phi0
        '''
        self.Phi0 = phi0

    def setAngleData(self,angle):
        self._angle = angle

    def setStaData(self,staData):
        self._staData = staData

    def setDynData(self,dynData):
        self._dynData = dynData

    def getCirclePoints(self):
        '''
        得到数据总行数
        '''
        return self._angle.shape[0]

    def getTimeArray(self):
        '''
        返回时间列
        '''
        circlePoints = self.getCirclePoints()
        n = self.getCirclePoints()
        #return np.arange(0.001,circlePoints/1000.,0.001)   此处生成的时间行数为1249
        return np.linspace(0.001,circlePoints/1000.,circlePoints)  #时间shape=（1250）

    def getAeroAngle(self):
        '''
        计算气动角度
        '''
        circlePoints = self.getCirclePoints()
        angle = self._angle
        _aeroAngle=np.zeros((circlePoints,4))    #np.zeros(shape) shape为元组类型
        for i in xrange(circlePoints):
            _aeroAngle[i,0]=atand((sind(angle[i,0])*cosd(angle[i,2])-cosd(angle[i,0])*sind(angle[i,1])*sind(angle[i,2]))/(cosd(angle[i,0])*cosd(angle[i,1])))
            _aeroAngle[i,1]=asind(sind(angle[i,0])*sind(angle[i,2])+cosd(angle[i,0])*sind(angle[i,1])*cosd(angle[i,2]))
            _aeroAngle[i,2]=angle[i,2]+self.Phi0
            _aeroAngle[i,3]=angle[i,3]

        return _aeroAngle

    def _calcuTempCt(self):
        '''
        根据天平系数计算临时的Ct
        '''
        Cy = self._dynData
        Cn = self._staData
        Cy=Cy-Cn
        circlePoints = self.getCirclePoints()
        Ct=np.zeros((circlePoints,6))
        for i in xrange(circlePoints):
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

    def getTempBodyCoe(self):
        '''
        得到有量纲的体轴系下气动数据
        '''
        circlePoints = self.getCirclePoints()
        Ctw=np.zeros((circlePoints,6))
        Ct = self._calcuTempCt()
        dx = self.DeltaX
        dy = self.DeltaY
        dz = self.DeltaZ
        for i in xrange(circlePoints):
            Ctw[i,0]=Ct[i,0]
            Ctw[i,1]=Ct[i,1]
            Ctw[i,2]=Ct[i,2]
            Ctw[i,3]=Ct[i,3]+Ct[i,2]*dy-Ct[i,1]*dz
            Ctw[i,4]=Ct[i,4]-Ct[i,0]*dz-Ct[i,2]*dx
            Ctw[i,5]=Ct[i,5]+Ct[i,0]*dy+Ct[i,1]*dx

        return Ctw

    def getTempAeroCoe(self):
        '''
        得到有量纲的风轴下气动数据
        '''
        circlePoints = self.getCirclePoints()
        aeroAngle = self.getAeroAngle()
        Ctw = self.getTempBodyCoe()
        Cq=np.zeros((circlePoints,6))
        for i in xrange(circlePoints):
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

    def _getUnitCoe(self,coe,aircraftModel):
        '''
        给定系数和模型（aircraftModel，父类：Model），得到无量纲气动系数
        '''
        circlePoints = self.getCirclePoints()
        q = aircraftModel.TotalPressure
        s = aircraftModel.Area
        l = aircraftModel.Span
        ba = aircraftModel.RefChord
        for i in xrange(circlePoints):
            coe[i,0]=coe[i,0]*9.8/(q*s)
            coe[i,1]=coe[i,1]*9.8/(q*s)
            coe[i,2]=coe[i,2]*9.8/(q*s)
            coe[i,3]=coe[i,3]*9.8/(q*s*l)
            coe[i,4]=coe[i,4]*9.8/(q*s*l)
            coe[i,5]=coe[i,5]*9.8/(q*s*ba)

        return coe

    def getBodyCoe(self,aircraftModel):
        '''
        得到无量纲体轴气动系数
        '''
        Ctw = self.getTempBodyCoe()
        return self._getUnitCoe(Ctw,aircraftModel)

    def getAeroCoe(self,aircraftModel):
        '''
        得到无量纲风轴气动系数
        '''
        Cq = self.getTempAeroCoe()
        return self._getUnitCoe(Cq,aircraftModel)

    def toBodyFile(self,bodyFileDir,aircraftModel):
        with open(bodyFileDir,'w') as f:
            m,n = self.getBodyCoe(aircraftModel).shape
            t = self.getTimeArray()
            ag = self.getAeroAngle()
            Ctw = self.getBodyCoe(aircraftModel)
            f.write("%d\t\t\t%d\n" % (m,n+5))
            f.write("%-8s\t%-8s\t%-8s\t%-8s\t%-8s\t%-8s\t%-8s\t%-8s\t%-8s\t%-8s\t%-8s\t" \
                    %("Time","α","β","φ","θ","CA","CN","CY","Cl","Cn","Cm"))
            for i in xrange(m):
                f.write("%-8.4f\t%-8.4f\t%-8.4f\t%-8.4f\t%-8.4f\t%-8.4f\t%-8.4f\t%-8.4f\t%-8.4f\t%-8.4f\t%-8.4f\t" \
                        % (t[i],ag[i,0],ag[i,1],ag[i,2],ag[i,3],Ctw[i,0],Ctw[i,1],Ctw[i,2],Ctw[i,3],Ctw[i,4],Ctw[i,5]))
            f.write("%-8.4f\t%-8.4f\t%-8.4f\t%-8.4f\t%-8.4f\t%-8.4f\t%-8.4f\t%-8.4f\t%-8.4f\t%-8.4f\t%-8.4f\t" \
                    % (t[m-1]+0.001,ag[0,0],ag[0,1],ag[0,2],ag[0,3],Ctw[0,0],Ctw[0,1],Ctw[0,2],Ctw[0,3],Ctw[0,4],Ctw[0,5]))
            
    def toAeroFile(self,aeroFileDir,aircraftModel):
        with open(aeroFileDir,'w') as f:
            m,n = self.getBodyCoe(aircraftModel).shape
            t = self.getTimeArray()
            ag = self.getAeroAngle()
            Cq = self.getAeroCoe(aircraftModel)
            f.write("%d\t\t\t%d\n" % (m,n+5))
            f.write("%-8s\t%-8s\t%-8s\t%-8s\t%-8s\t%-8s\t%-8s\t%-8s\t%-8s\t%-8s\t%-8s\t" \
                    %("Time","α","β","φ","θ","CA","CN","CY","Cl","Cn","Cm"))
            for i in xrange(m):
                f.write("%-8.4f\t%-8.4f\t%-8.4f\t%-8.4f\t%-8.4f\t%-8.4f\t%-8.4f\t%-8.4f\t%-8.4f\t%-8.4f\t%-8.4f\t" \
                        % (t[i],ag[i,0],ag[i,1],ag[i,2],ag[i,3],Cq[i,0],Cq[i,1],Cq[i,2],Cq[i,3],Cq[i,4],Cq[i,5]))
            f.write("%-8.4f\t%-8.4f\t%-8.4f\t%-8.4f\t%-8.4f\t%-8.4f\t%-8.4f\t%-8.4f\t%-8.4f\t%-8.4f\t%-8.4f\t" \
                    % (t[m-1]+0.001,ag[0,0],ag[0,1],ag[0,2],ag[0,3],Cq[0,0],Cq[0,1],Cq[0,2],Cq[0,3],Cq[0,4],Cq[0,5]))

class BalanceG14(object):
    '''
    十四杆天平
    '''
    pass

class BalanceG16(object):
    '''
    十六杆天平
    '''
    pass

class BalanceH1(object):
    '''
    盒式天平
    '''
    pass



