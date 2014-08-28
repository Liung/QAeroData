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

    def _generateDataByG14(self):
        dx = self.model.dx
        dy = self.model.dy
        dz = self.model.dz
        q = self.model.flowPressure
        s = self.model.area
        l = self.model.span
        ba = self.model.refChord

        jData = np.loadtxt(fname=self.staFile, skiprows=self.headerRows)
        dData = np.loadtxt(fname=self.dynFile, skiprows=self.headerRows)
        m, _ = jData.shape
        theta = np.zeros((m, 1))
        psi = theta
        phi = theta
        alpha = theta
        beta = theta
        bodyAngle = np.hstack((theta, phi, psi))
        if self.thetaColumn == 0 and self.phiColumn == 0 and self.psiColumn == 0:
            if self.alphaColumn != 0:
                alpha = jData[:, self.alphaColumn - 1]
            if self.betaColumn != 0:
                beta = jData[:, self.betaColumn - 1]
            aeroAngle = np.hstack((alpha, beta))
        else:
            if self.thetaColumn != 0:
                theta = jData[:, self.thetaColumn - 1]
            if self.phiColumn != 0:
                phi = jData[:, self.phiColumn - 1] + self.phi0  # 考虑到滚转电机没有零位的的问题，动平台文件需要用到
            if self.psiColumn != 0:
                psi = jData[:, self.psiColumn - 1]
            bodyAngle = np.hstack((theta, phi, psi))
            aeroAngle = np.zeros_like(bodyAngle)
            aeroAngle[0] = atand((sind(bodyAngle[0]) * cosd(bodyAngle[2]) -
                                  cosd(bodyAngle[0]) * sind(bodyAngle[1]) * sind(bodyAngle[2])) /
                                 (cosd(bodyAngle[0]) * cosd(bodyAngle[1])))
            aeroAngle[1] = asind(sind(bodyAngle[0]) * sind(bodyAngle[2]) +
                                 cosd(bodyAngle[0]) * sind(bodyAngle[1]) * cosd(bodyAngle[2]))
            # aeroAngle[2] = bodyAngle[2] + self.phi0
            # aeroAngle[3] = bodyAngle[3]

        jCoe = np.hstack((jData[:, self.cxColumn - 1], jData[:, self.cyColumn - 1], jData[:, self.czColumn - 1],
                          jData[:, self.cmxColumn - 1], jData[:, self.cmyColumn - 1], jData[:, self.cmzColumn - 1]))
        dCoe = np.hstack((dData[:, self.cxColumn - 1], dData[:, self.cyColumn - 1], dData[:, self.czColumn - 1],
                          dData[:, self.cmxColumn - 1], dData[:, self.cmyColumn - 1], dData[:, self.cmzColumn - 1]))
        Coe = dCoe - jCoe
        Coe0 = Coe * np.array([6.11960, 12.33276, 4.76279, 0.38218, 0.19456, 0.69732])
        bCoe = Coe0
        cx0 = Coe0[:, 0]
        cy0 = Coe0[:, 1]
        cz0 = Coe0[:, 2]
        cmx0 = Coe0[:, 3]
        cmy0 = Coe0[:, 4]
        cmz0 = Coe0[:, 5]
        for k in xrange(100):
            bCoe[:, 0] = cx0 + 0.00548 * bCoe[:, 1] + 0.10290 * bCoe[:, 2] + 0.12796 * bCoe[:, 3] + 1.03638 * bCoe[:, 4] - \
                       0.21182 * bCoe[:, 5] + 0.00090 * bCoe[:, 0] * bCoe[:, 0] - 0.00023 * bCoe[:, 0] * bCoe[:, 1] + \
                       0.00034 * bCoe[:, 0] * bCoe[:, 2] + 0.00198 * bCoe[:, 3] + 0.00447 * bCoe[:, 0] * bCoe[:, 4] - \
                       0.00065 * bCoe[:, 0] * bCoe[:, 5] - 0.00001 * bCoe[:, 1] * bCoe[:, 2] - 0.00444 * bCoe[:, 1] * bCoe[:, 3] -\
                       0.00041 * bCoe[:, 1] * bCoe[:, 4] + 0.00512 * bCoe[:, 1] * bCoe[:, 5] + 0.00014 * bCoe[:, 2] * bCoe[:, 2] - \
                       0.00243 * bCoe[:, 2] * bCoe[:, 3] - 0.00292 * bCoe[:, 2] * bCoe[:, 4] + 0.00033 * bCoe[:, 2] * bCoe[:, 5] - \
                       0.31818 * bCoe[:, 3] * bCoe[:, 3] + 0.04225 * bCoe[:, 3] * bCoe[:, 4] + 0.27065 * bCoe[:, 3] * bCoe[:, 5] - \
                       0.02223 * bCoe[:, 4] * bCoe[:, 4] - 0.01045 * bCoe[:, 4] * bCoe[:, 5] - 0.02171 * bCoe[:, 5] * bCoe[:, 5]
            bCoe[:, 1] = cy0 - 0.01686 * bCoe[:, 0] + 0.01297 * bCoe[:, 2] - 0.23388 * bCoe[:, 3] - 0.19139 * bCoe[:, 4] + \
                       0.18227 * bCoe[:, 5] - 0.00010 * bCoe[:, 1] * bCoe[:, 1] - 0.00010 * bCoe[:, 1] * bCoe[:, 0] + \
                       0.00004 * bCoe[:, 1] * bCoe[:, 2] - 0.00274 * bCoe[:, 1] * bCoe[:, 3] + 0.00056 * bCoe[:, 1] * bCoe[:, 4] + \
                       0.00107 * bCoe[:, 1] * bCoe[:, 5] + 0.00045 * bCoe[:, 0] * bCoe[:, 0] + 0.00030 * bCoe[:, 0] * bCoe[:, 2] + \
                       0.00077 * bCoe[:, 0] * bCoe[:, 3] + 0.00181 * bCoe[:, 0] * bCoe[:, 4] - 0.00549 * bCoe[:, 0] * bCoe[:, 5] - \
                       0.00006 * bCoe[:, 2] * bCoe[:, 2] - 0.01497 * bCoe[:, 2] * bCoe[:, 3] + 0.00340 * bCoe[:, 2] * bCoe[:, 4] + \
                       0.00213 * bCoe[:, 2] * bCoe[:, 5] - 0.03901 * bCoe[:, 3] * bCoe[:, 3] - 0.15065 * bCoe[:, 3] * bCoe[:, 4] + \
                       0.02407 * bCoe[:, 3] * bCoe[:, 5] + 0.00754 * bCoe[:, 4] * bCoe[:, 4] + 0.02244 * bCoe[:, 4] * bCoe[:, 5] - \
                       0.01096 * bCoe[:, 5] * bCoe[:, 5]
            bCoe[:, 2] = cz0 - 0.02295 * bCoe[:, 1] + 0.00338 * bCoe[:, 0] - 0.17365 * bCoe[:, 3] - 0.36139 * bCoe[:, 4] + \
                       0.00857 * bCoe[:, 5] + 0.00032 * bCoe[:, 2] * bCoe[:, 2] - 0.00009 * bCoe[:, 2] * bCoe[:, 1] - \
                       0.00016 * bCoe[:, 2] * bCoe[:, 0] + 0.00366 * bCoe[:, 2] * bCoe[:, 0] - 0.00382 * bCoe[:, 2] * bCoe[:, 4] + \
                       0.00146 * bCoe[:, 2] * bCoe[:, 5] + 0.00031 * bCoe[:, 1] * bCoe[:, 1] - 0.00050 * bCoe[:, 1] * bCoe[:,0] + \
                       0.02079 * bCoe[:, 1] * bCoe[:, 3] - 0.00222 * bCoe[:, 1] * bCoe[:, 4] - 0.00709 * bCoe[:, 1] * bCoe[:, 5] + \
                       0.00045 * bCoe[:, 0] * bCoe[:, 0] + 0.00588 * bCoe[:, 0] * bCoe[:, 3] + 0.01732 * bCoe[:, 0] * bCoe[:, 4] - \
                       0.00223 * bCoe[:, 0] * bCoe[:, 5] - 0.12878 * bCoe[:, 3] * bCoe[:, 3] + 0.09362 * bCoe[:, 3] * bCoe[:, 4] - \
                       0.24968 * bCoe[:, 3] * bCoe[:, 5] + 0.08996 * bCoe[:, 4] * bCoe[:, 4] + 0.01747 * bCoe[:, 4] * bCoe[:, 5] + \
                       0.01161 * bCoe[:, 5] * bCoe[:, 5]
            bCoe[:, 3] = cmx0 + 0.00068 * bCoe[:, 1] - 0.00015 * bCoe[:, 2] + 0.00010 * bCoe[:, 0] - 0.0073 * bCoe[:, 4] + \
                       0.01998 * bCoe[:, 5] - 0.00141 * bCoe[:, 3] * bCoe[:, 3] - 0.00067 * bCoe[:, 3] * bCoe[:, 1] - \
                       0.00055 * bCoe[:, 3] * bCoe[:, 2] + 0.00016 * bCoe[:, 3] * bCoe[:, 0] - 0.00475 * bCoe[:, 3] * bCoe[:, 4] + \
                       0.00236 * bCoe[:, 3] * bCoe[:, 5] - 0.00001 * bCoe[:, 1] * bCoe[:, 1] + 0.00001 * bCoe[:, 2] * bCoe[:, 1] + \
                       0.00002 * bCoe[:, 1] * bCoe[:, 0] + 0.00025 * bCoe[:, 1] * bCoe[:, 4] + 0.00025 * bCoe[:, 1] * bCoe[:, 5] - \
                       0.00003 * bCoe[:, 2] * bCoe[:, 2] + 0.00002 * bCoe[:, 2] * bCoe[:, 0] + 0.00026 * bCoe[:, 2] * bCoe[:, 4] + \
                       0.00004 * bCoe[:, 2] * bCoe[:, 5] - 0.00004 * bCoe[:, 0] * bCoe[:, 0] - 0.00042 * bCoe[:, 0] * bCoe[:, 4] + \
                       0.00023 * bCoe[:, 0] * bCoe[:, 5] - 0.00954 * bCoe[:, 4] * bCoe[:, 4] - 0.00136 * bCoe[:, 4] * bCoe[:, 5] + \
                       0.00219 * bCoe[:, 5] * bCoe[:, 5]
            bCoe[:, 4] = cmy0 - 0.00007 * bCoe[:, 1] + 0.00227 * bCoe[:, 2] + 0.00113 * bCoe[:, 3] - 0.00012 * bCoe[:, 0] + \
                       0.00488 * bCoe[:, 5] + 0.00714 * bCoe[:, 4] * bCoe[:, 4] + 0.00000 * bCoe[:, 4] * bCoe[:, 1] - \
                       0.00010 * bCoe[:, 4] * bCoe[:, 2] - 0.00955 * bCoe[:, 4] * bCoe[:, 3] + 0.00158 * bCoe[:, 0] * bCoe[:, 0] - \
                       0.00279 * bCoe[:, 4] * bCoe[:, 5] + 0.00001 * bCoe[:, 1] * bCoe[:, 1] + 0.00058 * bCoe[:, 1] * bCoe[:, 3] - \
                       0.00035 * bCoe[:, 1] * bCoe[:, 5] + 0.00001 * bCoe[:, 2] * bCoe[:, 2] - 0.00035 * bCoe[:, 2] * bCoe[:, 3] - \
                       0.00005 * bCoe[:, 2] * bCoe[:, 0] - 0.00006 * bCoe[:, 2] * bCoe[:, 5] - 0.00180 * bCoe[:, 3] * bCoe[:, 3] + \
                       0.00022 * bCoe[:, 3] * bCoe[:, 0] - 0.02256 * bCoe[:, 3] * bCoe[:, 5] - 0.00005 * bCoe[:, 0] * bCoe[:, 0] + \
                       0.00090 * bCoe[:, 0] * bCoe[:, 5] - 0.00117 * bCoe[:, 5] * bCoe[:, 5]
            bCoe[:, 5] = cmz0 + 0.00041 * bCoe[:, 1] - 0.00087 * bCoe[:, 2] - 0.05093 * bCoe[:, 3] - 0.03029 * bCoe[:, 4] + \
                       0.00121 * bCoe[:, 0] - 0.00147 * bCoe[:, 5] * bCoe[:, 5] - 0.00009 * bCoe[:, 5] * bCoe[:, 1] + \
                       0.00000 * bCoe[:, 5] * bCoe[:, 2] + 0.00302 * bCoe[:, 5] * bCoe[:, 3] - 0.00159 * bCoe[:, 5] * bCoe[:, 4] + \
                       0.00169 * bCoe[:, 5] * bCoe[:, 0] - 0.00019 * bCoe[:, 1] * bCoe[:, 3] - 0.00007 * bCoe[:, 1] * bCoe[:, 4] + \
                       0.00001 * bCoe[:, 1] * bCoe[:, 0] - 0.00001 * bCoe[:, 2] * bCoe[:, 2] + 0.00035 * bCoe[:, 2] * bCoe[:, 3] + \
                       0.00011 * bCoe[:, 2] * bCoe[:, 4] + 0.00001 * bCoe[:, 2] * bCoe[:, 0] - 0.00497 * bCoe[:, 3] * bCoe[:, 3] + \
                       0.01545 * bCoe[:, 3] * bCoe[:, 4] - 0.00069 * bCoe[:, 3] * bCoe[:, 0] - 0.00108 * bCoe[:, 4] * bCoe[:, 4] + \
                       0.00031 * bCoe[:, 4] * bCoe[:, 5] + 0.00001 * bCoe[:, 0] * bCoe[:, 0]

        # 体轴下的气动力和力矩，并将力矩中心转换到模型重心
        bCoe = np.zeros_like(bCoe)
        bCoe[:, 0] = bCoe[:, 0] * 0.95
        bCoe[:, 1] = bCoe[:, 1] * 0.98
        bCoe[:, 2] = bCoe[:, 2]
        bCoe[:, 3] = bCoe[:, 3] + bCoe[:, 2] * dy - bCoe[:, 1] * dz
        bCoe[:, 4] = bCoe[:, 4] - bCoe[:, 0] * dz - bCoe[:, 2] * dx
        bCoe[:, 5] = (bCoe[:, 5] + bCoe[:, 0] * dy + bCoe[:, 1] * dx) * 0.56

        aCoe = np.zeros_like(bCoe)
        aCoe[:, 0] = cosd(aeroAngle[:, 0]) * cosd(aeroAngle[:, 1]) * bCoe[:, 0] + sind(aeroAngle[:, 0]) * cosd(
            aeroAngle[:, 1]) * bCoe[:, 1] - sind(aeroAngle[:, 1]) * bCoe[:, 2]
        aCoe[:, 1] = -sind(aeroAngle[:, 0]) * bCoe[:, 0] + cosd(aeroAngle[:, 0]) * bCoe[:, 1]
        aCoe[:, 2] = cosd(aeroAngle[:, 0]) * sind(aeroAngle[:, 1]) * bCoe[:, 0] + sind(aeroAngle[:, 0]) * sind(
            aeroAngle[:, 1]) * bCoe[:, 1] + cosd(aeroAngle[:, 1]) * bCoe[:, 2]
        aCoe[:, 3] = cosd(aeroAngle[:, 0]) * cosd(aeroAngle[:, 1]) * bCoe[:, 3] - sind(aeroAngle[:, 0]) * cosd(
            aeroAngle[:, 0]) * bCoe[:, 4] + sind(aeroAngle[:, 1]) * bCoe[:, 5]
        aCoe[:, 4] = sind(aeroAngle[:, 0]) * bCoe[:, 3] + cosd(aeroAngle[:, 0]) * bCoe[:, 4]
        aCoe[:, 5] = -cosd(aeroAngle[:, 0]) * sind(aeroAngle[:, 1]) * bCoe[:, 3] + sind(aeroAngle[:, 0]) * sind(
            aeroAngle[:, 1]) * bCoe[:, 4] + cosd(aeroAngle[:, 1]) * bCoe[:, 5]

        aeroCoe = np.zeros_like(aCoe)
        aeroCoe[:, 0] = aCoe[:, 0] * 9.8 / (q * s)
        aeroCoe[:, 1] = aCoe[:, 1] * 9.8 / (q * s)
        aeroCoe[:, 2] = aCoe[:, 2] * 9.8 / (q * s)
        aeroCoe[:, 3] = aCoe[:, 3] * 9.8 / (q * s * l)
        aeroCoe[:, 4] = aCoe[:, 4] * 9.8 / (q * s * l)
        aeroCoe[:, 5] = aCoe[:, 5] * 9.8 / (q * s * ba)

        bodyCoe = np.zeros_like(bCoe)
        bodyCoe[:, 0] = bCoe[:, 0] * 9.8 / (q * s)
        bodyCoe[:, 1] = bCoe[:, 1] * 9.8 / (q * s)
        bodyCoe[:, 2] = bCoe[:, 2] * 9.8 / (q * s)
        bodyCoe[:, 3] = bCoe[:, 3] * 9.8 / (q * s * l)
        bodyCoe[:, 4] = bCoe[:, 4] * 9.8 / (q * s * l)
        bodyCoe[:, 5] = bCoe[:, 5] * 9.8 / (q * s * ba)

        return aeroAngle, bodyAngle, bCoe, aCoe

    def _generateDataByG16(self):
        dx = self.model.dx
        dy = self.model.dy
        dz = self.model.dz
        q = self.model.flowPressure
        s = self.model.area
        l = self.model.span
        ba = self.model.refChord

        jData = np.loadtxt(fname=self.staFile, skiprows=self.headerRows)
        dData = np.loadtxt(fname=self.dynFile, skiprows=self.headerRows)
        m, _ = jData.shape
        theta = np.zeros((m, 1))
        psi = theta
        phi = theta
        alpha = theta
        beta = theta
        if self.thetaColumn == 0 and self.phiColumn == 0 and self.psiColumn == 0:
            if self.alphaColumn != 0:
                alpha = jData[:, self.alphaColumn - 1]
            if self.betaColumn != 0:
                beta = jData[:, self.betaColumn - 1]
            aeroAngle = np.hstack((alpha, beta))
        else:
            if self.thetaColumn != 0:
                theta = jData[:, self.thetaColumn - 1]
            if self.phiColumn != 0:
                phi = jData[:, self.phiColumn - 1] + self.phi0  # 考虑到滚转电机没有零位的的问题，动平台文件需要用到
            if self.psiColumn != 0:
                psi = jData[:, self.psiColumn - 1]
            bodyAngle = np.hstack((theta, phi, psi))
            aeroAngle = np.zeros_like(bodyAngle)
            aeroAngle[0] = atand((sind(bodyAngle[0]) * cosd(bodyAngle[2]) -
                                  cosd(bodyAngle[0]) * sind(bodyAngle[1]) * sind(bodyAngle[2])) /
                                 (cosd(bodyAngle[0]) * cosd(bodyAngle[1])))
            aeroAngle[1] = asind(sind(bodyAngle[0]) * sind(bodyAngle[2]) +
                                 cosd(bodyAngle[0]) * sind(bodyAngle[1]) * cosd(bodyAngle[2]))
            # aeroAngle[2] = bodyAngle[2] + self.phi0
            # aeroAngle[3] = bodyAngle[3]

        jCoe = np.hstack((jData[:, self.cxColumn - 1], jData[:, self.cyColumn - 1], jData[:, self.czColumn - 1],
                          jData[:, self.cmxColumn - 1], jData[:, self.cmyColumn - 1], jData[:, self.cmzColumn - 1]))
        dCoe = np.hstack((dData[:, self.cxColumn - 1], dData[:, self.cyColumn - 1], dData[:, self.czColumn - 1],
                          dData[:, self.cmxColumn - 1], dData[:, self.cmyColumn - 1], dData[:, self.cmzColumn - 1]))
        Coe = dCoe - jCoe
        Coe0 = Coe
        bCoe = Coe0
        bCoe[:, 0] = 0.2554675 * Coe0[:, 0] - 0.0154822 * Coe0[:, 1] + 0.00390868 * Coe0[:, 2] - \
                     0.0051715 * Coe0[:, 3] - 0.00178511 * Coe0[:, 4] - 0.0024596 * Coe0[:, 5]
        bCoe[:, 1] = 0.00068324 * Coe0[:, 0] + 0.6661034 * Coe0[:, 1] + 0.0120892 * Coe0[:, 2] - \
                     0.0109143 * Coe0[:, 3] + 0.0391122 * Coe0[:, 4] + 0.0151383 * Coe0[:, 5]
        bCoe[:, 2] = 0.00096904 * Coe0[:, 0] + 0.00120306 * Coe0[:, 1] + 0.585989 * Coe0[:, 2] + \
                     0.027769 * Coe0[:, 3] + 0.014161 * Coe0[:, 4] + 0.00452654 * Coe0[:, 5]
        bCoe[:, 3] = 0.000095445 * Coe0[:, 0] + 0.00029407 * Coe0[:, 1] + 0.00726843 * Coe0[:, 2] + \
                     0.03304980 * Coe0[:, 3] + 0.0082689 * Coe0[:, 4] + 0.000152507 * Coe0[:, 5]
        bCoe[:, 4] = -0.00036007 * Coe0[:, 0] - 0.00009756 * Coe0[:, 1] + 0.00098957 * Coe0[:, 2] + \
                     0.00055426 * Coe0[:, 3] + 0.02351212 * Coe0[:, 4] - 0.000134249 * Coe0[:, 5]
        bCoe[:, 5] = -0.000025559 * Coe0[:, 0] + 0.00075648 * Coe0[:, 1] + 0.000344149 * Coe0[:, 2] - \
                     0.000585242 * Coe0[:, 3] - 0.0022913 * Coe0[:, 4] + 0.0276978 * Coe0[:, 5]

        # 体轴下的气动力和力矩，并将力矩中心转换到模型重心
        bCoe = np.zeros_like(bCoe)
        bCoe[:, 0] = bCoe[:, 0] * 0.95
        bCoe[:, 1] = bCoe[:, 1] * 0.98
        bCoe[:, 2] = bCoe[:, 2]
        bCoe[:, 3] = bCoe[:, 3] + bCoe[:, 2] * dy - bCoe[:, 1] * dz
        bCoe[:, 4] = bCoe[:, 4] - bCoe[:, 0] * dz - bCoe[:, 2] * dx
        bCoe[:, 5] = (bCoe[:, 5] + bCoe[:, 0] * dy + bCoe[:, 1] * dx) * 0.56

        aCoe = np.zeros_like(bCoe)
        aCoe[:, 0] = cosd(aeroAngle[:, 0]) * cosd(aeroAngle[:, 1]) * bCoe[:, 0] + sind(aeroAngle[:, 0]) * cosd(
            aeroAngle[:, 1]) * bCoe[:, 1] - sind(aeroAngle[:, 1]) * bCoe[:, 2]
        aCoe[:, 1] = -sind(aeroAngle[:, 0]) * bCoe[:, 0] + cosd(aeroAngle[:, 0]) * bCoe[:, 1]
        aCoe[:, 2] = cosd(aeroAngle[:, 0]) * sind(aeroAngle[:, 1]) * bCoe[:, 0] + sind(aeroAngle[:, 0]) * sind(
            aeroAngle[:, 1]) * bCoe[:, 1] + cosd(aeroAngle[:, 1]) * bCoe[:, 2]
        aCoe[:, 3] = cosd(aeroAngle[:, 0]) * cosd(aeroAngle[:, 1]) * bCoe[:, 3] - sind(aeroAngle[:, 0]) * cosd(
            aeroAngle[:, 0]) * bCoe[:, 4] + sind(aeroAngle[:, 1]) * bCoe[:, 5]
        aCoe[:, 4] = sind(aeroAngle[:, 0]) * bCoe[:, 3] + cosd(aeroAngle[:, 0]) * bCoe[:, 4]
        aCoe[:, 5] = -cosd(aeroAngle[:, 0]) * sind(aeroAngle[:, 1]) * bCoe[:, 3] + sind(aeroAngle[:, 0]) * sind(
            aeroAngle[:, 1]) * bCoe[:, 4] + cosd(aeroAngle[:, 1]) * bCoe[:, 5]

        aeroCoe = np.zeros_like(aCoe)
        aeroCoe[:, 0] = aCoe[:, 0] * 9.8 / (q * s)
        aeroCoe[:, 1] = aCoe[:, 1] * 9.8 / (q * s)
        aeroCoe[:, 2] = aCoe[:, 2] * 9.8 / (q * s)
        aeroCoe[:, 3] = aCoe[:, 3] * 9.8 / (q * s * l)
        aeroCoe[:, 4] = aCoe[:, 4] * 9.8 / (q * s * l)
        aeroCoe[:, 5] = aCoe[:, 5] * 9.8 / (q * s * ba)

        bodyCoe = np.zeros_like(bCoe)
        bodyCoe[:, 0] = bCoe[:, 0] * 9.8 / (q * s)
        bodyCoe[:, 1] = bCoe[:, 1] * 9.8 / (q * s)
        bodyCoe[:, 2] = bCoe[:, 2] * 9.8 / (q * s)
        bodyCoe[:, 3] = bCoe[:, 3] * 9.8 / (q * s * l)
        bodyCoe[:, 4] = bCoe[:, 4] * 9.8 / (q * s * l)
        bodyCoe[:, 5] = bCoe[:, 5] * 9.8 / (q * s * ba)

        return aeroAngle, bodyAngle, bCoe, aCoe

    def _generateDataByG18(self):
        dx = self.model.dx
        dy = self.model.dy
        dz = self.model.dz
        q = self.model.flowPressure
        s = self.model.area
        l = self.model.span
        ba = self.model.refChord

        jData = np.loadtxt(fname=self.staFile, skiprows=self.headerRows)
        dData = np.loadtxt(fname=self.dynFile, skiprows=self.headerRows)
        m, _ = jData.shape
        theta = np.zeros((m, 1))
        psi = theta
        phi = theta
        alpha = theta
        beta = theta
        if self.thetaColumn == 0 and self.phiColumn == 0 and self.psiColumn == 0:
            if self.alphaColumn != 0:
                alpha = jData[:, self.alphaColumn - 1]
            if self.betaColumn != 0:
                beta = jData[:, self.betaColumn - 1]
            aeroAngle = np.hstack((alpha, beta))
        else:
            if self.thetaColumn != 0:
                theta = jData[:, self.thetaColumn - 1]
            if self.phiColumn != 0:
                phi = jData[:, self.phiColumn - 1] + self.phi0  # 考虑到滚转电机没有零位的的问题，动平台文件需要用到
            if self.psiColumn != 0:
                psi = jData[:, self.psiColumn - 1]
            bodyAngle = np.hstack((theta, phi, psi))
            aeroAngle = np.zeros_like(bodyAngle)
            aeroAngle[0] = atand((sind(bodyAngle[0]) * cosd(bodyAngle[2]) -
                                  cosd(bodyAngle[0]) * sind(bodyAngle[1]) * sind(bodyAngle[2])) /
                                 (cosd(bodyAngle[0]) * cosd(bodyAngle[1])))
            aeroAngle[1] = asind(sind(bodyAngle[0]) * sind(bodyAngle[2]) +
                                 cosd(bodyAngle[0]) * sind(bodyAngle[1]) * cosd(bodyAngle[2]))
            # aeroAngle[2] = bodyAngle[2] + self.phi0
            # aeroAngle[3] = bodyAngle[3]

        jCoe = np.hstack((jData[:, self.cxColumn - 1], jData[:, self.cyColumn - 1], jData[:, self.czColumn - 1],
                          jData[:, self.cmxColumn - 1], jData[:, self.cmyColumn - 1], jData[:, self.cmzColumn - 1]))
        dCoe = np.hstack((dData[:, self.cxColumn - 1], dData[:, self.cyColumn - 1], dData[:, self.czColumn - 1],
                          dData[:, self.cmxColumn - 1], dData[:, self.cmyColumn - 1], dData[:, self.cmzColumn - 1]))
        Coe = dCoe - jCoe
        Coe0 = Coe * np.array([6.11960, 12.33276, 4.76279, 0.38218, 0.19456, 0.69732])
        bCoe = Coe0
        cx0 = Coe0[:, 0]
        cy0 = Coe0[:, 1]
        cz0 = Coe0[:, 2]
        cmx0 = Coe0[:, 3]
        cmy0 = Coe0[:, 4]
        cmz0 = Coe0[:, 5]
        for k in xrange(100):
            bCoe[:, 0] = cx0 + 0.00548 * bCoe[:, 1] + 0.10290 * bCoe[:, 2] + 0.12796 * bCoe[:, 3] + \
                         1.03638 * bCoe[:, 4] - 0.21182 * bCoe[:, 5] + 0.00090 * bCoe[:, 0] * bCoe[:, 0] - \
                         0.00023 * bCoe[:, 0] * bCoe[:, 1] + 0.00034 * bCoe[:, 0] * bCoe[:, 2] + \
                         0.00198 * bCoe[:, 0] * bCoe[:, 3] + 0.00447 * bCoe[:, 0] * bCoe[:, 4] - \
                         0.00065 * bCoe[:, 0] * bCoe[:, 5] - 0.00001 * bCoe[:, 1] * bCoe[:, 2] - \
                         0.00444 * bCoe[:, 1] * bCoe[:, 3] - 0.00041 * bCoe[:, 1] * bCoe[:, 4] + \
                         0.00512 * bCoe[:, 1] * bCoe[:, 5] + 0.00014 * bCoe[:, 2] * bCoe[:, 2] - \
                         0.00243 * bCoe[:, 2] * bCoe[:, 3] - 0.00292 * bCoe[:, 2] * bCoe[:, 4] + \
                         0.00033 * bCoe[:, 2] * bCoe[:, 5] - 0.31818 * bCoe[:, 3] * bCoe[:, 3] + \
                         0.04225 * bCoe[:, 3] * bCoe[:, 4] + 0.27065 * bCoe[:, 3] * bCoe[:, 5] - \
                         0.02223 * bCoe[:, 4] * bCoe[:, 4] - 0.01045 * bCoe[:, 4] * bCoe[:, 5] - \
                         0.02171 * bCoe[:, 5] * bCoe[:, 5]
            bCoe[:, 1] = cy0 - 0.01686 * bCoe[:, 0] + 0.01297 * bCoe[:, 2] - 0.23388 * bCoe[:, 3] - \
                         0.19139 * bCoe[:, 4] + 0.18227 * bCoe[:, 5] - 0.00010 * bCoe[:, 1] * bCoe[:, 1] - \
                         0.00010 * bCoe[:, 1] * bCoe[:, 0] + 0.00004 * bCoe[:, 1] * bCoe[:, 2] - \
                         0.00274 * bCoe[:, 1] * bCoe[:, 3] + 0.00056 * bCoe[:, 1] * bCoe[:, 4] + \
                         0.00107 * bCoe[:, 1] * bCoe[:, 5] + 0.00045 * bCoe[:, 0] * bCoe[:, 0] + \
                         0.00030 * bCoe[:, 0] * bCoe[:, 2] + 0.00077 * bCoe[:, 0] * bCoe[:, 3] + \
                         0.00181 * bCoe[:, 0] * bCoe[:, 4] - 0.00549 * bCoe[:, 0] * bCoe[:, 5] - \
                         0.00006 * bCoe[:, 2] * bCoe[:, 2] - 0.01497 * bCoe[:, 2] * bCoe[:, 3] + \
                         0.00340 * bCoe[:, 2] * bCoe[:, 4] + 0.00213 * bCoe[:, 2] * bCoe[:, 5] - \
                         0.03901 * bCoe[:, 3] * bCoe[:, 3] - 0.15065 * bCoe[:, 3] * bCoe[:, 4] + \
                         0.02407 * bCoe[:, 3] * bCoe[:, 5] + 0.00754 * bCoe[:, 4] * bCoe[:, 4] + \
                         0.02244 * bCoe[:, 4] * bCoe[:, 5] - 0.01096 * bCoe[:, 5] * bCoe[:, 5]
            bCoe[:, 2] = cz0 - 0.02295 * bCoe[:, 1] + 0.00338 * bCoe[:, 0] - 0.17365 * bCoe[:, 3] - \
                         0.36139 * bCoe[:, 4] + 0.00857 * bCoe[:, 5] + 0.00032 * bCoe[:, 2] * bCoe[:, 2] - \
                         0.00009 * bCoe[:, 2] * bCoe[:, 1] - 0.00016 * bCoe[:, 2] * bCoe[:, 0] + \
                         0.00366 * bCoe[:, 2] * bCoe[:, 3] - 0.00382 * bCoe[:, 2] * bCoe[:, 4] + \
                         0.00146 * bCoe[:, 2] * bCoe[:, 5] + 0.00031 * bCoe[:, 1] * bCoe[:, 1] - \
                         0.00050 * bCoe[:, 1] * bCoe[:, 2] + 0.02079 * bCoe[:, 1] * bCoe[:, 3] - \
                         0.00222 * bCoe[:, 1] * bCoe[:, 4] - 0.00709 * bCoe[:, 1] * bCoe[:, 5] + \
                         0.00045 * bCoe[:, 0] * bCoe[:, 0] + 0.00588 * bCoe[:, 0] * bCoe[:, 3] + \
                         0.01732 * bCoe[:, 0] * bCoe[:, 4] - 0.00223 * bCoe[:, 0] * bCoe[:, 5] - \
                         0.12878 * bCoe[:, 3] * bCoe[:, 3] + 0.09362 * bCoe[:, 3] * bCoe[:, 4] - \
                         0.24968 * bCoe[:, 3] * bCoe[:, 5] + 0.08996 * bCoe[:, 4] * bCoe[:, 4] + \
                         0.01747 * bCoe[:, 4] * bCoe[:, 5] + 0.01161 * bCoe[:, 5] * bCoe[:, 5]
            bCoe[:, 3] = cmx0 + 0.00068 * bCoe[:, 1] - 0.00015 * bCoe[:, 2] + 0.00010 * bCoe[:, 0] - \
                         0.0073 * bCoe[:, 4] + 0.01998 * bCoe[:, 5] - 0.00141 * bCoe[:, 3] * bCoe[:, 3] - \
                         0.00067 * bCoe[:, 3] * bCoe[:, 1] - 0.00055 * bCoe[:, 3] * bCoe[:, 2] + \
                         0.00016 * bCoe[:, 3] * bCoe[:, 0] - 0.00475 * bCoe[:, 3] * bCoe[:, 4] + \
                         0.00236 * bCoe[:, 3] * bCoe[:, 5] - 0.00001 * bCoe[:, 1] * bCoe[:, 1] + \
                         0.00001 * bCoe[:, 2] * bCoe[:, 1] + 0.00002 * bCoe[:, 1] * bCoe[:, 0] + \
                         0.00025 * bCoe[:, 1] * bCoe[:, 4] + 0.00025 * bCoe[:, 1] * bCoe[:, 5] - \
                         0.00003 * bCoe[:, 2] * bCoe[:, 2] + 0.00002 * bCoe[:, 2] * bCoe[:, 0] + \
                         0.00026 * bCoe[:, 2] * bCoe[:, 4] + 0.00004 * bCoe[:, 2] * bCoe[:, 5] - \
                         0.00004 * bCoe[:, 0] * bCoe[:, 0] - 0.00042 * bCoe[:, 0] * bCoe[:, 4] + \
                         0.00023 * bCoe[:, 0] * bCoe[:, 5] - 0.00954 * bCoe[:, 4] * bCoe[:, 4] - \
                         0.00136 * bCoe[:, 4] * bCoe[:, 5] + 0.00219 * bCoe[:, 5] * bCoe[:, 5]
            bCoe[:, 4] = cmy0 - 0.00007 * bCoe[:, 1] + 0.00227 * bCoe[:, 2] + 0.00113 * bCoe[:, 3] - \
                         0.00012 * bCoe[:, 0] + 0.00488 * bCoe[:, 5] + 0.00714 * bCoe[:, 4] * bCoe[:, 4] + \
                         0.00000 * bCoe[:, 4] * bCoe[:, 1] - 0.00010 * bCoe[:, 4] * bCoe[:, 2] - \
                         0.00955 * bCoe[:, 4] * bCoe[:, 3] + 0.00158 * bCoe[:, 0] * bCoe[:, 0] - \
                         0.00279 * bCoe[:, 4] * bCoe[:, 5] + 0.00001 * bCoe[:, 1] * bCoe[:, 1] + \
                         0.00058 * bCoe[:, 1] * bCoe[:, 3] - 0.00035 * bCoe[:, 1] * bCoe[:, 5] + \
                         0.00001 * bCoe[:, 2] * bCoe[:, 0] - 0.00006 * bCoe[:, 2] * bCoe[:, 5] - \
                         0.00180 * bCoe[:, 3] * bCoe[:, 3] + 0.00022 * bCoe[:, 3] * bCoe[:, 0] - \
                         0.02256 * bCoe[:, 3] * bCoe[:, 5] - 0.00005 * bCoe[:, 0] * bCoe[:, 0] + \
                         0.00090 * bCoe[:, 0] * bCoe[:, 5] - 0.00117 * bCoe[:, 5] * bCoe[:, 5]
            bCoe[:, 5] = cmz0 + 0.00041 * bCoe[:, 1] - 0.00087 * bCoe[:, 2] - 0.05093 * bCoe[:, 3] - \
                         0.03029 * bCoe[:, 4] + 0.00121 * bCoe[:, 0] - 0.00147 * bCoe[:, 5] * bCoe[:, 5] - \
                         0.00009 * bCoe[:, 5] * bCoe[:, 1] + 0.00000 * bCoe[:, 5] * bCoe[:, 2] + \
                         0.00302 * bCoe[:, 5] * bCoe[:, 3] - 0.00159 * bCoe[:, 5] * bCoe[:, 4] + \
                         0.00169 * bCoe[:, 5] * bCoe[:, 0] - 0.00019 * bCoe[:, 1] * bCoe[:, 3] - \
                         0.00007 * bCoe[:, 1] * bCoe[:, 4] + 0.00001 * bCoe[:, 1] * bCoe[:, 0] - \
                         0.00001 * bCoe[:, 2] * bCoe[:, 2] + 0.00035 * bCoe[:, 2] * bCoe[:, 3] + \
                         0.00011 * bCoe[:, 2] * bCoe[:, 4] - 0.00108 * bCoe[:, 4] * bCoe[:, 4] + \
                         0.00031 * bCoe[:, 4] * bCoe[:, 5] + 0.00001 * bCoe[:, 0] * bCoe[:, 0]

        # 体轴下的气动力和力矩，并将力矩中心转换到模型重心
        bCoe = np.zeros_like(bCoe)
        bCoe[:, 0] = bCoe[:, 0] * 0.95
        bCoe[:, 1] = bCoe[:, 1] * 0.98
        bCoe[:, 2] = bCoe[:, 2]
        bCoe[:, 3] = bCoe[:, 3] + bCoe[:, 2] * dy - bCoe[:, 1] * dz
        bCoe[:, 4] = bCoe[:, 4] - bCoe[:, 0] * dz - bCoe[:, 2] * dx
        bCoe[:, 5] = (bCoe[:, 5] + bCoe[:, 0] * dy + bCoe[:, 1] * dx) * 0.56

        aCoe = np.zeros_like(bCoe)
        aCoe[:, 0] = cosd(aeroAngle[:, 0]) * cosd(aeroAngle[:, 1]) * bCoe[:, 0] + sind(aeroAngle[:, 0]) * cosd(
            aeroAngle[:, 1]) * bCoe[:, 1] - sind(aeroAngle[:, 1]) * bCoe[:, 2]
        aCoe[:, 1] = -sind(aeroAngle[:, 0]) * bCoe[:, 0] + cosd(aeroAngle[:, 0]) * bCoe[:, 1]
        aCoe[:, 2] = cosd(aeroAngle[:, 0]) * sind(aeroAngle[:, 1]) * bCoe[:, 0] + sind(aeroAngle[:, 0]) * sind(
            aeroAngle[:, 1]) * bCoe[:, 1] + cosd(aeroAngle[:, 1]) * bCoe[:, 2]
        aCoe[:, 3] = cosd(aeroAngle[:, 0]) * cosd(aeroAngle[:, 1]) * bCoe[:, 3] - sind(aeroAngle[:, 0]) * cosd(
            aeroAngle[:, 0]) * bCoe[:, 4] + sind(aeroAngle[:, 1]) * bCoe[:, 5]
        aCoe[:, 4] = sind(aeroAngle[:, 0]) * bCoe[:, 3] + cosd(aeroAngle[:, 0]) * bCoe[:, 4]
        aCoe[:, 5] = -cosd(aeroAngle[:, 0]) * sind(aeroAngle[:, 1]) * bCoe[:, 3] + sind(aeroAngle[:, 0]) * sind(
            aeroAngle[:, 1]) * bCoe[:, 4] + cosd(aeroAngle[:, 1]) * bCoe[:, 5]

        aeroCoe = np.zeros_like(aCoe)
        aeroCoe[:, 0] = aCoe[:, 0] * 9.8 / (q * s)
        aeroCoe[:, 1] = aCoe[:, 1] * 9.8 / (q * s)
        aeroCoe[:, 2] = aCoe[:, 2] * 9.8 / (q * s)
        aeroCoe[:, 3] = aCoe[:, 3] * 9.8 / (q * s * l)
        aeroCoe[:, 4] = aCoe[:, 4] * 9.8 / (q * s * l)
        aeroCoe[:, 5] = aCoe[:, 5] * 9.8 / (q * s * ba)

        bodyCoe = np.zeros_like(bCoe)
        bodyCoe[:, 0] = bCoe[:, 0] * 9.8 / (q * s)
        bodyCoe[:, 1] = bCoe[:, 1] * 9.8 / (q * s)
        bodyCoe[:, 2] = bCoe[:, 2] * 9.8 / (q * s)
        bodyCoe[:, 3] = bCoe[:, 3] * 9.8 / (q * s * l)
        bodyCoe[:, 4] = bCoe[:, 4] * 9.8 / (q * s * l)
        bodyCoe[:, 5] = bCoe[:, 5] * 9.8 / (q * s * ba)

        return aeroAngle, bodyAngle, bCoe, aCoe

    def _generateDytaByBox(self):
        pass


class BalanceG14(Balance):
    def __init__(self):
        super(BalanceG14, self).__init__()

    def translateData(self):
        super(BalanceG14, self).translateData()
        print 'hello'


class BalanceG16(Balance):
    def __init__(self, parent=None):
        super(BalanceG16, self).__init__(parent)

    def translateData(self):
        super(BalanceG16, self).translateData()
        print 'Hello'


class BalanceG18(Balance):
    def __init__(self, parent=None):
        super(BalanceG18, self).__init__(parent)

    def translateData(self):

        dx = self.model.BalanceDeltaX
        dy = self.model.BalanceDeltaY
        dz = self.model.BalanceDeltaZ
        q = self.model.FlowPressure
        s = self.model.Area
        l = self.model.Span
        ba = self.model.RefChord
    
        jf = open(self.staFile, 'r')
        df = open(self.dynFile, 'r')
        af = open(self.aeroFile, 'a')
        bf = open(self.bodyFile, 'a')
    
        jData = np.loadtxt(fname=self.staFile, skiprows=self.headerRows)
        dData = np.loadtxt(fname=self.dynFile, skiprows=self.headerRows)
        m, _ = jData.shape
        theta = np.zeros((m, 1))
        psi = theta
        phi = theta
        alpha = theta
        beta = theta
        if self.thetaColumn == 0 and self.phiColumn == 0 and self.psiColumn == 0:
            if self.alphaColumn != 0:
                alpha = jData[:, self.alphaColumn - 1]
            if self.betaColumn != 0:
                beta = jData[:, self.betaColumn - 1]
            aeroAngle = np.hstack((alpha, beta))
        else:
            if self.thetaColumn != 0:
                theta = jData[:, self.thetaColumn - 1]
            if self.phiColumn != 0:
                phi = jData[:, self.phiColumn - 1] + self.phi0  # 考虑到滚转电机没有零位的的问题，动平台文件需要用到
            if self.psiColumn != 0:
                psi = jData[:, self.psiColumn - 1]
            angle = np.hstack((theta, phi, psi))
            aeroAngle = np.zeros_like(angle)
            aeroAngle[0] = atand((sind(angle[0]) * cosd(angle[2]) -
                                  cosd(angle[0]) * sind(angle[1]) * sind(angle[2])) /
                                 (cosd(angle[0]) * cosd(angle[1])))
            aeroAngle[1] = asind(sind(angle[0]) * sind(angle[2]) + cosd(angle[0]) * sind(angle[1]) * cosd(angle[2]))
            # aeroAngle[2] = angle[2] + self.phi0
            # aeroAngle[3] = angle[3]
    
        jCoe = jData[:, 5:11]
        dCoe = dData[:, 5:11]
        Coe = dCoe - jCoe
        Coe0 = Coe * np.array([6.11960, 12.33276, 4.76279, 0.38218, 0.19456, 0.69732])
        bCoe = Coe0
        cx0 = Coe0[:, 0]
        cy0 = Coe0[:, 1]
        cz0 = Coe0[:, 2]
        cmx0 = Coe0[:, 3]
        cmy0 = Coe0[:, 4]
        cmz0 = Coe0[:, 5]
        for k in xrange(100):
            bCoe[:, 0] = cx0 + 0.00548 * bCoe[:, 1] + 0.10290 * bCoe[:, 2] + 0.12796 * bCoe[:, 3] + \
                1.03638 * bCoe[:, 4] - 0.21182 * bCoe[:, 5] + 0.00090 * bCoe[:, 0] * bCoe[:, 0] - \
                0.00023 * bCoe[:, 0] * bCoe[:, 1] + 0.00034 * bCoe[:, 0] * bCoe[:, 2] + \
                0.00198 * bCoe[:, 0] * bCoe[:, 3] + 0.00447 * bCoe[:, 0] * bCoe[:, 4] - \
                0.00065 * bCoe[:, 0] * bCoe[:, 5] - 0.00001 * bCoe[:, 1] * bCoe[:, 2] - \
                0.00444 * bCoe[:, 1] * bCoe[:, 3] - 0.00041 * bCoe[:, 1] * bCoe[:, 4] + \
                0.00512 * bCoe[:, 1] * bCoe[:, 5] + 0.00014 * bCoe[:, 2] * bCoe[:, 2] - \
                0.00243 * bCoe[:, 2] * bCoe[:, 3] - 0.00292 * bCoe[:, 2] * bCoe[:, 4] + \
                0.00033 * bCoe[:, 2] * bCoe[:, 5] - 0.31818 * bCoe[:, 3] * bCoe[:, 3] + \
                0.04225 * bCoe[:, 3] * bCoe[:, 4] + 0.27065 * bCoe[:, 3] * bCoe[:, 5] - \
                0.02223 * bCoe[:, 4] * bCoe[:, 4] - 0.01045 * bCoe[:, 4] * bCoe[:, 5] - \
                0.02171 * bCoe[:, 5] * bCoe[:, 5]
            bCoe[:, 1] = cy0 - 0.01686 * bCoe[:, 0] + 0.01297 * bCoe[:, 2] - 0.23388 * bCoe[:, 3] - \
                0.19139 * bCoe[:, 4] + 0.18227 * bCoe[:, 5]- 0.00010 * bCoe[:, 1] * bCoe[:, 1] - \
                0.00010 * bCoe[:, 1] * bCoe[:, 0] + 0.00004 * bCoe[:, 1] * bCoe[:, 2] - \
                0.00274 * bCoe[:, 1] * bCoe[:, 3] + 0.00056 * bCoe[:, 1] * bCoe[:, 4] + \
                0.00107 * bCoe[:, 1] * bCoe[:, 5] + 0.00045 * bCoe[:, 0] * bCoe[:, 0] + \
                0.00030 * bCoe[:, 0] * bCoe[:, 2] + 0.00077 * bCoe[:, 0] * bCoe[:, 3] + \
                0.00181 * bCoe[:, 0] * bCoe[:, 4] - 0.00549 * bCoe[:, 0] * bCoe[:, 5] - \
                0.00006 * bCoe[:, 2] * bCoe[:, 2] - 0.01497 * bCoe[:, 2] * bCoe[:, 3] + \
                0.00340 * bCoe[:, 2] * bCoe[:, 4] + 0.00213 * bCoe[:, 2] * bCoe[:, 5] - \
                0.03901 * bCoe[:, 3] * bCoe[:, 3] - 0.15065 * bCoe[:, 3] * bCoe[:, 4] + \
                0.02407 * bCoe[:, 3] * bCoe[:, 5] + 0.00754 * bCoe[:, 4] * bCoe[:, 4] + \
                0.02244 * bCoe[:, 4] * bCoe[:, 5] - 0.01096 * bCoe[:, 5] * bCoe[:, 5]
            bCoe[:, 2] = cz0 - 0.02295 * bCoe[:, 1] + 0.00338 * bCoe[:, 0] - 0.17365 * bCoe[:, 3] -\
                0.36139 * bCoe[:, 4] + 0.00857 * bCoe[:, 5] + 0.00032 * bCoe[:, 2] * bCoe[:, 2] - \
                0.00009 * bCoe[:, 2] * bCoe[:, 1] - 0.00016 * bCoe[:, 2] * bCoe[:, 0] + \
                0.00366 * bCoe[:, 2] * bCoe[:, 3] - 0.00382 * bCoe[:, 2] * bCoe[:, 4] + \
                0.00146 * bCoe[:, 2] * bCoe[:, 5] + 0.00031 * bCoe[:, 1] * bCoe[:, 1] - \
                0.00050 * bCoe[:, 1] * bCoe[:, 2] + 0.02079 * bCoe[:, 1] * bCoe[:, 3] - \
                0.00222 * bCoe[:, 1] * bCoe[:, 4] - 0.00709 * bCoe[:, 1] * bCoe[:, 5] + \
                0.00045 * bCoe[:, 0] * bCoe[:, 0] + 0.00588 * bCoe[:, 0] * bCoe[:, 3] + \
                0.01732 * bCoe[:, 0] * bCoe[:, 4] - 0.00223 * bCoe[:, 0] * bCoe[:, 5] - \
                0.12878 * bCoe[:, 3] * bCoe[:, 3] + 0.09362 * bCoe[:, 3] * bCoe[:, 4] - \
                0.24968 * bCoe[:, 3] * bCoe[:, 5] + 0.08996 * bCoe[:, 4] * bCoe[:, 4] + \
                0.01747 * bCoe[:, 4] * bCoe[:, 5] + 0.01161 * bCoe[:, 5] * bCoe[:, 5]
            bCoe[:, 3] = cmx0 + 0.00068 * bCoe[:, 1] - 0.00015 * bCoe[:, 2] + 0.00010 * bCoe[:, 0] - \
                0.0073 * bCoe[:, 4] + 0.01998 * bCoe[:, 5] - 0.00141 * bCoe[:, 3] * bCoe[:, 3] - \
                0.00067 * bCoe[:, 3] * bCoe[:, 1] - 0.00055 * bCoe[:, 3] * bCoe[:, 2] + \
                0.00016 * bCoe[:, 3] * bCoe[:, 0] - 0.00475 * bCoe[:, 3] * bCoe[:, 4] + \
                0.00236 * bCoe[:, 3] * bCoe[:, 5] - 0.00001 * bCoe[:, 1] * bCoe[:, 1] + \
                0.00001 * bCoe[:, 2] * bCoe[:, 1] + 0.00002 * bCoe[:, 1] * bCoe[:, 0] + \
                0.00025 * bCoe[:, 1] * bCoe[:, 4] + 0.00025 * bCoe[:, 1] * bCoe[:, 5] - \
                0.00003 * bCoe[:, 2] * bCoe[:, 2] + 0.00002 * bCoe[:, 2] * bCoe[:, 0] + \
                0.00026 * bCoe[:, 2] * bCoe[:, 4] + 0.00004 * bCoe[:, 2] * bCoe[:, 5] - \
                0.00004 * bCoe[:, 0] * bCoe[:, 0] - 0.00042 * bCoe[:, 0] * bCoe[:, 4] + \
                0.00023 * bCoe[:, 0] * bCoe[:, 5] - 0.00954 * bCoe[:, 4] * bCoe[:, 4] - \
                0.00136 * bCoe[:, 4] * bCoe[:, 5] + 0.00219 * bCoe[:, 5] * bCoe[:, 5]
            bCoe[:, 4] = cmy0 - 0.00007 * bCoe[:, 1] + 0.00227 * bCoe[:, 2] + 0.00113 * bCoe[:, 3] - \
                0.00012 * bCoe[:, 0] + 0.00488 * bCoe[:, 5] + 0.00714 * bCoe[:, 4] * bCoe[:, 4] + \
                0.00000 * bCoe[:, 4] * bCoe[:, 1] - 0.00010 * bCoe[:, 4] * bCoe[:, 2] - \
                0.00955 * bCoe[:, 4] * bCoe[:, 3] + 0.00158 * bCoe[:, 0] * bCoe[:, 0] - \
                0.00279 * bCoe[:, 4] * bCoe[:, 5] + 0.00001 * bCoe[:, 1] * bCoe[:, 1] + \
                0.00058 * bCoe[:, 1] * bCoe[:, 3] - 0.00035 * bCoe[:, 1] * bCoe[:, 5] + \
                0.00001 * bCoe[:, 2] * bCoe[:, 0] - 0.00006 * bCoe[:, 2] * bCoe[:, 5] - \
                0.00180 * bCoe[:, 3] * bCoe[:, 3] + 0.00022 * bCoe[:, 3] * bCoe[:, 0] - \
                0.02256 * bCoe[:, 3] * bCoe[:, 5] - 0.00005 * bCoe[:, 0] * bCoe[:, 0] + \
                0.00090 * bCoe[:, 0] * bCoe[:, 5] - 0.00117 * bCoe[:, 5] * bCoe[:, 5]
            bCoe[:, 5] = cmz0 + 0.00041 * bCoe[:, 1] - 0.00087 * bCoe[:, 2] - 0.05093 * bCoe[:, 3] - \
                0.03029 * bCoe[:, 4] + 0.00121 * bCoe[:, 0] - 0.00147 * bCoe[:, 5] * bCoe[:, 5] - \
                0.00009 * bCoe[:, 5] * bCoe[:, 1] + 0.00000 * bCoe[:, 5] * bCoe[:, 2] + \
                0.00302 * bCoe[:, 5] * bCoe[:, 3] - 0.00159 * bCoe[:, 5] * bCoe[:, 4] + \
                0.00169 * bCoe[:, 5] * bCoe[:, 0] - 0.00019 * bCoe[:, 1] * bCoe[:, 3] - \
                0.00007 * bCoe[:, 1] * bCoe[:, 4] + 0.00001 * bCoe[:, 1] * bCoe[:, 0] - \
                0.00001 * bCoe[:, 2] * bCoe[:, 2] + 0.00035 * bCoe[:, 2] * bCoe[:, 3] + \
                0.00011 * bCoe[:, 2] * bCoe[:, 4] - 0.00108 * bCoe[:, 4] * bCoe[:, 4] + \
                0.00031 * bCoe[:, 4] * bCoe[:, 5] + 0.00001 * bCoe[:, 0] * bCoe[:, 0]
    
        # 体轴下的气动力和力矩，并将力矩中心转换到模型重心
        bCoe = np.zeros_like(bCoe)
        bCoe[:, 0] = bCoe[:, 0] * 0.95
        bCoe[:, 1] = bCoe[:, 1] * 0.98
        bCoe[:, 2] = bCoe[:, 2]
        bCoe[:, 3] = bCoe[:, 3] + bCoe[:, 2] * dy - bCoe[:, 1] * dz
        bCoe[:, 4] = bCoe[:, 4] - bCoe[:, 0] * dz - bCoe[:, 2] * dx
        bCoe[:, 5] = (bCoe[:, 5] + bCoe[:, 0] * dy + bCoe[:, 1] * dx) * 0.56
    
        aCoe = np.zeros_like(bCoe)
        aCoe[:, 0] = cosd(aeroAngle[:, 0]) * cosd(aeroAngle[:, 1]) * bCoe[:, 0] + sind(aeroAngle[:, 0]) * cosd(
            aeroAngle[:, 1]) * bCoe[:, 1] - sind(aeroAngle[:, 1]) * bCoe[:, 2]
        aCoe[:, 1] = -sind(aeroAngle[:, 0]) * bCoe[:, 0] + cosd(aeroAngle[:, 0]) * bCoe[:, 1]
        aCoe[:, 2] = cosd(aeroAngle[:, 0]) * sind(aeroAngle[:, 1]) * bCoe[:, 0] + sind(aeroAngle[:, 0]) * sind(
            aeroAngle[:, 1]) * bCoe[:, 1] + cosd(aeroAngle[:, 1]) * bCoe[:, 2]
        aCoe[:, 3] = cosd(aeroAngle[:, 0]) * cosd(aeroAngle[:, 1]) * bCoe[:, 3] - sind(aeroAngle[:, 0]) * cosd(
            aeroAngle[:, 0]) * bCoe[:, 4] + sind(aeroAngle[:, 1]) * bCoe[:, 5]
        aCoe[:, 4] = sind(aeroAngle[:, 0]) * bCoe[:, 3] + cosd(aeroAngle[:, 0]) * bCoe[:, 4]
        aCoe[:, 5] = -cosd(aeroAngle[:, 0]) * sind(aeroAngle[:, 1]) * bCoe[:, 3] + sind(aeroAngle[:, 0]) * sind(
            aeroAngle[:, 1]) * bCoe[:, 4] + cosd(aeroAngle[:, 1]) * bCoe[:, 5]
    
        aeroCoe = np.zeros_like(aCoe)
        aeroCoe[:, 0] = aCoe[:, 0] * 9.8 / (q * s)
        aeroCoe[:, 1] = aCoe[:, 1] * 9.8 / (q * s)
        aeroCoe[:, 2] = aCoe[:, 2] * 9.8 / (q * s)
        aeroCoe[:, 3] = aCoe[:, 3] * 9.8 / (q * s * l)
        aeroCoe[:, 4] = aCoe[:, 4] * 9.8 / (q * s * l)
        aeroCoe[:, 5] = aCoe[:, 5] * 9.8 / (q * s * ba)
    
        bodyCoe = np.zeros_like(bCoe)
        bodyCoe[:, 0] = bCoe[:, 0] * 9.8 / (q * s)
        bodyCoe[:, 1] = bCoe[:, 1] * 9.8 / (q * s)
        bodyCoe[:, 2] = bCoe[:, 2] * 9.8 / (q * s)
        bodyCoe[:, 3] = bCoe[:, 3] * 9.8 / (q * s * l)
        bodyCoe[:, 4] = bCoe[:, 4] * 9.8 / (q * s * l)
        bodyCoe[:, 5] = bCoe[:, 5] * 9.8 / (q * s * ba)
    
        t = 0
        i = 0
        if i == 0:
            bf.write("%-s\t%-s\t%-s\t%-s\t%-s\t%-s\t%-s\t%-s\t%-s\t%-s\t%-s\t%-s\n"
                     % (u"Time", u"α", u"β", u"θ", u"φ", u"ψ", u"CA", u"CN", u"CY", u"Cl", u"Cn", u"Cm"))
            af.write("%-s\t%-s\t%-s\t%-s\t%-s\t%-s\t%-s\t%-s\t%-s\t%-s\t%-s\t%-s\n"
                     % (u"Time", u"α", u"β", u"θ", u"φ", u"ψ", u"CD", u"CL", u"CZ", u"Cx", u"Cy", u"Cz"))
        bf.write("%-.3f\t%-15.8f\t%-15.8f\t%-15.8f\t%-15.8f\t%-15.8f\t%-15.8f\t%-15.8f\t \
            %-15.8f\t%-15.8f\t%-15.8f\t%-15.8f\n"
                 % (t * (i + 1), aeroAngle[0], aeroAngle[1], angle[0], angle[1], angle[2], bodyCoe[0], bodyCoe[1],
                    bodyCoe[2], bodyCoe[3], bodyCoe[4], bodyCoe[5]))
        bf.write("%-.3f\t%-15.8f\t%-15.8f\t%-15.8f\t%-15.8f\t%-15.8f\t%-15.8f\t%-15.8f\t \
            %-15.8f\t%-15.8f\t%-15.8f\t%-15.8f\n"
                 % (t * (i + 1), aeroAngle[0], aeroAngle[1], angle[0], angle[1], angle[2], aeroCoe[0], aeroCoe[1],
                    aeroCoe[2], aeroCoe[3], aeroCoe[4], aeroCoe[5]))
    
        # i += 1
        # # line end loop
        # bf.write("%-.3f\t%-15.8f\t%-15.8f\t%-15.8f\t%-15.8f\t%-15.8f\t%-15.8f\t%-15.8f\t%-15.8f\t%-15.8f\t%-15.8f\t\n" \
        #          % (t * (i + 1), ag1[0], ag1[1], ag1[2], ag1[3], ct1[0], ct1[1], ct1[2], ct1[3], ct1[4], ct1[5]))
        # af.write("%-.3f\t%-15.8f\t%-15.8f\t%-15.8f\t%-15.8f\t%-15.8f\t%-15.8f\t%-15.8f\t%-15.8f\t%-15.8f\t%-15.8f\t\n" \
        #          % (t * (i + 1), ag1[0], ag1[1], ag1[2], ag1[3], cq1[0], cq1[1], cq1[2], cq1[3], cq1[4], cq1[5]))
    
        jf.close()
        df.close()
        af.close()
        bf.close()

    def writeToFile(self, aeroAngle, Cb, aCoe):

        m, n = Cb.shape
        t = np.linspace(0.001,m/1000.,m)
        ag = aeroAngle
        with open(self.bodyFile,"w") as f:
            #f.write("%d\t\t\t%d\n" % (m,n+5))
            f.write("%-s\t%-s\t%-s\t%-s\t%-s\t%-s\t%-s\t%-s\t%-s\t%-s\t%-s\t\n" \
                    %("Time","α","β","φ","θ","CA","CN","CY","Cl","Cn","Cm"))
            for i in xrange(m):
                f.write("%-.3f\t%-15.8f\t%-15.8f\t%-15.8f\t%-15.8f\t%-15.8f\t%-15.8f\t%-15.8f\t%-15.8f\t%-15.8f\t%-15.8f\t\n" \
                        % (t[i],ag[i,0],ag[i,1],ag[i,2],ag[i,3],Cb[i,0],Cb[i,1],Cb[i,2],Cb[i,3],Cb[i,4],Cb[i,5]))
            f.write("%-.3f\t%-15.8f\t%-15.8f\t%-15.8f\t%-15.8f\t%-15.8f\t%-15.8f\t%-15.8f\t%-15.8f\t%-15.8f\t%-15.8f\t\n" \
                    % (t[m-1]+0.001,ag[0,0],ag[0,1],ag[0,2],ag[0,3],Cb[0,0],Cb[0,1],Cb[0,2],Cb[0,3],Cb[0,4],Cb[0,5]))

        with open(self.aeroFile,"w") as f:
            #f.write("%d\t\t\t%d\n" % (m,n+5))
            f.write("%-s\t%-s\t%-s\t%-s\t%-s\t%-s\t%-s\t%-s\t%-s\t%-s\t%-s\t\n" \
                    %("Time","α","β","φ","θ","CA","CN","CY","Cl","Cn","Cm"))
            for i in xrange(m):
                f.write("%-.3f\t%-15.8f\t%-15.8f\t%-15.8f\t%-15.8f\t%-15.8f\t%-15.8f\t%-15.8f\t%-15.8f\t%-15.8f\t%-15.8f\t\n" \
                        % (t[i],ag[i,0],ag[i,1],ag[i,2],ag[i,3],aCoe[i,0],aCoe[i,1],aCoe[i,2],aCoe[i,3],aCoe[i,4],aCoe[i,5]))
            f.write("%-.3f\t%-15.8f\t%-15.8f\t%-15.8f\t%-15.8f\t%-15.8f\t%-15.8f\t%-15.8f\t%-15.8f\t%-15.8f\t%-15.8f\t\n" \
                    % (t[m-1]+0.001,ag[0,0],ag[0,1],ag[0,2],ag[0,3],aCoe[0,0],aCoe[0,1],aCoe[0,2],aCoe[0,3],aCoe[0,4],aCoe[0,5]))


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
