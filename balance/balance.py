#coding: UTF-8
from __future__ import division
import math
import os
import os.path
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


class TEnum(object):
    def __init__(self, *arguments):
        idx = 0
        for name in arguments:
            if '=' in name:
                name,val = name.rsplit('=', 1)
                if val.isalnum():
                    idx = eval(val)
            setattr(self, name.strip(), idx)
            idx += 1


class AircraftModel(object):
    def __init__(self, area=0., span=0., rootChord=0., refChord=0.,
                 dx=0., dy=0., dz=0., windSpeed=25.):
        self.area = area
        self.span = span
        self.rootChord = rootChord
        self.refChord = refChord       
        self.dx = dx
        self.dy = dy
        self.dz = dz
        self.windSpeed = windSpeed
        self.flowPressure = 0.5*AIR_DENSITY*self.windSpeed**2
    
    def setArea(self, area):
        self.area = area
        
    def setSpan(self, span):
        self.span = span
        
    def setRootChord(self, rootChord):
        self.rootChord = rootChord
        
    def setRefChord(self, refChord):
        self.refChord = refChord

    def setWindSpeed(self, windSpeed=0.):
        self.windSpeed = windSpeed
        self.flowPressure = 0.5*AIR_DENSITY*self.windSpeed**2

    def setFlowPressure(self, flowPressure=0.):
        self.flowPressure = flowPressure
        self.windSpeed = math.sqrt(2.*flowPressure/AIR_DENSITY)

    def setBalanceDistance(self, dx=0., dy=0, dz=0.):
        self.dx = dx
        self.dy = dy
        self.dz = dz


class Balance(object):
    def __init__(self, staFile='', dynFile='', aeroFile='', bodyFile='',
                 aircraftModel=AircraftModel(), balanceSty=0, headerRows=1):
        self.staFile = staFile
        self.dynFile = dynFile
        self.aeroFile = aeroFile
        self.bodyFile = bodyFile
        self.headerRows = headerRows
        self.model = aircraftModel
        self.balanceSty = balanceSty

        self.timeColumn = 0
        self.thetaColumn = 0
        self.psiColumn = 0
        self.phiColumn = 0
        self.alphaColumn = 0
        self.betaColumn = 0
        self.cxColumn = 0
        self.cyColumn = 0
        self.czColumn = 0
        self.cmxColumn = 0
        self.cmyColumn = 0
        self.cmzColumn = 0

        self.theta0 = 0.
        self.phi0 = 0.
        self.psi0 = 0.

    def __str__(self):
        return 'Balance:\t' + '\n' + \
               ('%20s\t\t%s' % ('Static File:', self.staFile)) + '\n' + \
               ('%20s\t\t%s' % ('Dynamic File:', self.dynFile)) + '\n' + \
               ('%20s\t\t%s' % ('Aero File:', self.aeroFile)) + '\n' + \
               ('%20s\t\t%s' % ('Body File:', self.bodyFile))

    def __repr__(self):
        return str(self)

    def setStaFile(self, staFile):
        self.staFile = staFile

    def setDynFile(self, dynFile):
        self.dynFile = dynFile

    def setAeroFile(self, aeroFile):
        self.aeroFile = aeroFile

    def setBodyFile(self, bodyFile):
        self.bodyFile = bodyFile

    def setAircraftModel(self, aircraftModel):
        self.model = aircraftModel

    def setHeaderRows(self, headerRows):
        self.headerRows = headerRows

    def setFileFormat(self, fileFormat={}):
        self.timeColumn = fileFormat.get('time', 0)
        self.thetaColumn = fileFormat.get('theta', 0)
        self.psiColumn = fileFormat.get('psi', 0)
        self.psiColumn = fileFormat.get('phi', 0)
        self.alphaColumn = fileFormat.get('alpha', 0)
        self.betaColumn = fileFormat.get('alpha', 0)
        self.cxColumn = fileFormat.get('cx', 0)
        self.cyColumn = fileFormat.get('cy', 0)
        self.czColumn = fileFormat.get('cz', 0)
        self.cmxColumn = fileFormat.get('cmx', 0)
        self.cmyColumn = fileFormat.get('cmy', 0)
        self.cmzColumn = fileFormat.get('cmz', 0)

    def setTheta0(self, theta0=0):
        self.theta0 = theta0

    def setPhi0(self, phi0=0):
        self.phi0 = phi0

    def setPsi0(self, psi0=0):
        self.psi0 = psi0

    def setBalanceSty(self, balanceSty=0):
        self.balanceSty = balanceSty

    def translateData(self):
        if self.balanceSty == 0:  # 14杆天平
            ag, bg, bc, ac = self._generateDataByG14()
            self.writeToFile(ag, bg, bc, ac, False)
            return True
        if self.balanceSty == 1:  # 16杆
            ag, bg, bc, ac = self._generateDataByG16()
            self.writeToFile(ag, bg, bc, ac, False)
            return True
        if self.balanceSty == 2:  # 18杆
            ag, bg, bc, ac = self._generateDataByG18()
            self.writeToFile(ag, bg, bc, ac, False)
            return True
        if self.balanceSty == 3:  # 盒式天平
            pass

    def writeToFile(self, aeroAngle, bodyAngle, bCoe, aCoe, circ=False):
        m, n = bCoe.shape
        t = np.linspace(0.001, m / 1000., m)
        ag = aeroAngle
        bg = bodyAngle
        with open(self.bodyFile, "w") as f:
            # f.write("%d\t\t\t%d\n" % (m,n+5))
            f.write("%-s\t%-s\t%-s\t%-s\t%-s\t%-s\t%-s\t%-s\t%-s\t%-s\t%-s\t%-s\n" \
                    % ("Time", u"α", u"β", u"θ", u"φ", u"ψ", "CA", "CN", "CY", "Cl", "Cn", "Cm"))
            for i in xrange(m):
                f.write(
                    "%-.3f\t%-15.8f\t%-15.8f\t%-15.8f\t%-15.8f\t%-15.8f\t%-15.8f\t%-15.8f\t%-15.8f\t%-15.8f\t%-15.8f"
                    "\t%-15.8f\n" % (t[i], ag[i, 0], ag[i, 1], bg[i, 0], bg[i, 1], bg[i, 2], bCoe[i, 0], bCoe[i, 1],
                                     bCoe[i, 2], bCoe[i, 3], bCoe[i, 4], bCoe[i, 5]))
            if circ:
                f.write("%-.3f\t%-15.8f\t%-15.8f\t%-15.8f\t%-15.8f\t%-15.8f\t%-15.8f\t%-15.8f\t%-15.8f\t%-15.8f\t"
                        "%-15.8f\t\n" % (t[m - 1] + 0.001, ag[0, 0], ag[0, 1], ag[0, 2], ag[0, 3], bCoe[0, 0],
                                         bCoe[0, 1], bCoe[0, 2], bCoe[0, 3], bCoe[0, 4], bCoe[0, 5]))

        with open(self.aeroFile, "w") as f:
            # f.write("%d\t\t\t%d\n" % (m,n+5))
            f.write("%-s\t%-s\t%-s\t%-s\t%-s\t%-s\t%-s\t%-s\t%-s\t%-s\t%-s\t%-s\n"
                    % ("Time", u"α", u"β", u"θ", u"φ", u"ψ", "CD", "CL", "CY", "Cx", "Cy", "Cz"))
            for i in xrange(m):
                f.write(
                    "%-.3f\t%-15.8f\t%-15.8f\t%-15.8f\t%-15.8f\t%-15.8f\t%-15.8f\t%-15.8f\t%-15.8f\t%-15.8f\t%-15.8f\t\n" \
                    % (t[i], ag[i, 0], ag[i, 1], ag[i, 2], ag[i, 3], aCoe[i, 0], aCoe[i, 1], aCoe[i, 2], aCoe[i, 3],
                       aCoe[i, 4], aCoe[i, 5]))
            if circ:
                f.write("%-.3f\t%-15.8f\t%-15.8f\t%-15.8f\t%-15.8f\t%-15.8f\t%-15.8f\t%-15.8f\t%-15.8f\t%-15.8f\t"
                        "%-15.8f\t%-15.8f\n" % (t[m - 1] + 0.001, ag[0, 0], ag[0, 1], bg[0, 0], bg[0, 1], bg[0, 2],
                                                aCoe[0, 0], aCoe[0, 1], aCoe[0, 2], aCoe[0, 3], aCoe[0, 4], aCoe[0, 5]))


class BalanceG14(Balance):
    def __init__(self):
        super(BalanceG14, self).__init__()

    def translateData(self):
        super(BalanceG14, self).translateData()
        print 'hello'


class BalanceBox(Balance):
    def __init__(self, parent=None):
        super(BalanceBox, self).__init__(parent)

    def translateData(self):
        super(BalanceBox, self).translateData()
        print 'hello'
        pass


if __name__ == '__main__':
    b = Balance("c:/tsdf.txt", "h:/sdf.x", "ds.xt", "sdf.x", AircraftModel())
    print b
