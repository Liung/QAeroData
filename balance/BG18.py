#coding: UTF-8
"""
本文件为天平数据处理程序,包含：
BalanceG18——》18杆天平
BalanceG16——》16杆天平
BalanceG14——》14杆天平
BalanceBox——》盒式天平
"""

from __future__ import division
import math
import os
import re
import shutil
import string
import numpy as np
from numpy import (genfromtxt, zeros, deg2rad, sin, cos, savetxt, hstack)

AIR_DENSITY = 1.2250    # 空气密度
ABSOLUTE_ZERO = 273.15  # 绝对零度
DYN_PITCH, DYN_YAW, DYN_ROLL, STA_PITCH, STA_YAW, STA_ROLL = range(6)


class AircraftModel(object):
    def __init__(self, area=0., span=0., rootChord=0., refChord=0., V=25, dx=0., dy=0., dz=0.):
        self.Area = area
        self.Span = span
        self.RootChord = rootChord
        self.RefChord = refChord
        self.V = V
        self.FlowPressure = 0.5*AIR_DENSITY*self.V**2
        self.dx = dx
        self.dy = dy
        self.dz = dz

    def setV(self, V=0.):
        self.V = V
        self.FlowPressure = 0.5*AIR_DENSITY*self.V**2

    def setFlowPressure(self,flowPressure=0.):
        self.FlowPressure = flowPressure
        self.V = math.sqrt(2.*flowPressure/AIR_DENSITY)

    def setDelta(self, dx=0., dy=0, dz=0.):
        self.dx = dx
        self.dy = dy
        self.dz = dz


class Balance(object):
    def __init__(self, staFile=None, dynFile=None, bodyFile=None, aeroFile=None,
                 headerRows=1, footerRows=0, angleStartCol=0, angleEndCol=3,
                 forceStartCol=4, forceEndCol=9, aircraftModel=None):
        self._staFile = staFile
        self._dynFile = dynFile
        self._bodyFile = bodyFile
        self._aeroFile = aeroFile
        self._headerRows = headerRows
        self._footerRows = footerRows
        self._angleStartCol = angleStartCol
        self._angleEndCol = angleEndCol
        self._angleCols = angleEndCol + 1 - angleStartCol
        self._forceStartCol = forceStartCol
        self._forceEndCol = forceEndCol

        self._V = 0.
        self._S = 0.
        self._L = 0.
        self._rootChord = 0.
        self._refChord = 0.
        self._FlowPressure = 0.
        self._dx = 0.
        self._dy = 0.
        self._dz = 0.
        self.setAircraftModel(aircraftModel)

    def setStaFile(self, staFile):
        self._staFile = staFile

    def setDynFile(self, dynFile):
        self._dynFile = dynFile

    def setBodyFile(self, bodyFile):
        self._bodyFile = bodyFile

    def setAeroFile(self, aeroFile):
        self._aeroFile = aeroFile

    def setHeaderRows(self, headerRows):
        self._headerRows = headerRows

    def setFooterRows(self, footerRows):
        self._footerRows = footerRows

    def setAngleStartCol(self, angleStartCol):
        self._angleStartCol = angleStartCol

    def setAngleEndCol(self, angleEndCol):
        self._angleEndCol = angleEndCol

    def setForceStartCol(self, forceStartCol):
        self._forceStartCol = forceStartCol

    def setForceEndCol(self, forceEndCol):
        self._forceEndCol = forceEndCol

    def setAircraftModel(self, aircraftModel=None):
        if aircraftModel is not None:
            self._V = aircraftModel.V
            self._S = aircraftModel.Area
            self._L = aircraftModel.Span
            self._rootChord = aircraftModel.RootChord
            self._refChord = aircraftModel.RefChord
            self._FlowPressure = aircraftModel.FlowPressure
            self._dx = aircraftModel.dx
            self._dy = aircraftModel.dy
            self._dz = aircraftModel.dz

    def transData(self):
        pass


class BalanceG18(Balance):
    # def __init__(self):
    #     super(self, BalanceG18).__init__()

    def transData(self):
        # aircraft's area, characteristic chord, free flow pressure, dx, dy, dz, air speed:V, flow pressure.
        s = self._S                     # unit: m2
        l = self._L                     # unit: m
        ba = self._refChord             # unit: pa
        dx = self._dx                   # unit: m
        dy = self._dy                   # unit: m
        dz = self._dz                   # unit: m
        V = self._V                           # unit: m/s
        q = 0.5 * AIR_DENSITY * V ** 2  # unit: pa

        staFile = self._staFile         # static file's name
        dynFile = self._dynFile         # dynamic file's name
        bodyFile = self._bodyFile       # body file's name
        aeroFile = self._aeroFile       # aero file's name

        headerRows = self._headerRows  # data file's header nums
        footerRows = self._footerRows  # data file's footer nums
        angleStartCol = self._angleStartCol  # angle start column
        angleEndCol = self._angleEndCol  # angle end column
        angleCols = angleEndCol - angleStartCol + 1  # angle columns
        forceStartCol = self._forceStartCol  # force and moment start column
        forceEndCol = self._forceEndCol  # force and moment end column
        forceCols = forceEndCol - forceStartCol + 1  # force and moment columns

        #load static file and dynamic file
        staData = genfromtxt(fname=staFile, skip_header=headerRows, skip_footer=footerRows)
        dynData = genfromtxt(fname=dynFile, skip_header=headerRows, skip_footer=footerRows)
        staAngle, staForce = staData[:, (angleStartCol - 1):angleEndCol], staData[:, (forceStartCol - 1):forceEndCol]
        dynAngle, dynForce = dynData[:, (angleStartCol - 1):angleEndCol], dynData[:, (forceStartCol - 1):forceEndCol]
        staAngleR, dynAngleR = deg2rad(staAngle), deg2rad(dynAngle)  # change the degrees to radius
        angle = (staAngle + dynAngle) / 2.
        angleR = (staAngleR + dynAngleR) / 2.
        m, n = staData.shape
        # read the file's headers and footers
        rawList = open(staFile).readlines()
        headerList = rawList[:headerRows] if headerRows else []
        footerList = rawList[-footerRows:] if footerRows else []

        #calculate the "body frame"'s fore and moment's coefficient
        Fe = dynForce - staForce  # Fe: the raw Force and moment of Balance at the "Body frame"in the experiment
        Fbb = zeros(shape=(m, forceCols))  # Fbb: Force and moment of Balance at the "Body frame"

        Fbb[:, 0] = 6.11960 * Fe[:, 0]
        Fbb[:, 1] = 12.33276 * Fe[:, 1]
        Fbb[:, 2] = 4.76279 * Fe[:, 2]
        Fbb[:, 3] = 0.38218 * Fe[:, 3]
        Fbb[:, 4] = 0.19456 * Fe[:, 4]
        Fbb[:, 5] = 0.69732 * Fe[:, 5]
        for i in range(100):
            Fbb[:, 0] = 6.11960 * Fe[:, 0] + \
                0.00548 * Fbb[:, 1] + 0.10290 * Fbb[:, 2] + 0.12796 * Fbb[:, 3] + 1.03638 * Fbb[:,4] - 0.21182 * Fbb[:, 5] + \
                0.00090 * Fbb[:, 0] * Fbb[:, 0] - 0.00023 * Fbb[:, 0] * Fbb[:, 1] + 0.00034 * Fbb[:, 0] * Fbb[:, 2] + \
                0.00198 * Fbb[:, 0] * Fbb[:, 3] + 0.00447 * Fbb[:, 0] * Fbb[:, 4] - 0.00065 * Fbb[:, 0] * Fbb[:, 5] - \
                0.00001 * Fbb[:, 1] * Fbb[:, 2] - 0.00444 * Fbb[:, 1] * Fbb[:, 3] - 0.00041 * Fbb[:, 1] * Fbb[:, 4] + \
                0.00512 * Fbb[:, 1] * Fbb[:, 5] + 0.00014 * Fbb[:, 2] * Fbb[:, 2] - 0.00243 * Fbb[:, 2] * Fbb[:, 3] - \
                0.00292 * Fbb[:, 2] * Fbb[:, 4] + 0.00033 * Fbb[:, 2] * Fbb[:, 5] - 0.31818 * Fbb[:, 3] * Fbb[:, 3] + \
                0.04225 * Fbb[:, 3] * Fbb[:, 4] + 0.27065 * Fbb[:, 3] * Fbb[:, 5] - 0.02223 * Fbb[:, 4] * Fbb[:, 4] - \
                0.01045 * Fbb[:, 4] * Fbb[:, 5] - 0.02171 * Fbb[:, 5] * Fbb[:, 5]
            Fbb[:, 1] = 12.33276 * Fe[:, 1] - \
                0.01686 * Fbb[:, 0] + 0.01297 * Fbb[:, 2] - 0.23388 * Fbb[:, 3] - 0.19139 * Fbb[:, 4] + 0.18227 * Fbb[:, 5] - \
                0.00010 * Fbb[:, 1] * Fbb[:, 1] - 0.00010 * Fbb[:, 1] * Fbb[:, 0] + 0.00004 * Fbb[:, 1] * Fbb[:, 2] - \
                0.00274 * Fbb[:, 1] * Fbb[:, 3] + 0.00056 * Fbb[:, 1] * Fbb[:, 4] + 0.00107 * Fbb[:, 1] * Fbb[:, 5] + \
                0.00045 * Fbb[:, 0] * Fbb[:, 0] + 0.00030 * Fbb[:, 0] * Fbb[:, 2] + 0.00077 * Fbb[:, 0] * Fbb[:, 3] + \
                0.00181 * Fbb[:, 0] * Fbb[:, 4] - 0.00549 * Fbb[:, 0] * Fbb[:, 5] - 0.00006 * Fbb[:, 2] * Fbb[:, 2] - \
                0.01497 * Fbb[:, 2] * Fbb[:, 3] + 0.00340 * Fbb[:, 2] * Fbb[:, 4] + 0.00213 * Fbb[:, 2] * Fbb[:, 5] - \
                0.03901 * Fbb[:, 3] * Fbb[:, 3] - 0.15065 * Fbb[:, 3] * Fbb[:, 4] + 0.02407 * Fbb[:, 3] * Fbb[:, 5] + \
                0.00754 * Fbb[:, 4] * Fbb[:, 4] + 0.02244 * Fbb[:, 4] * Fbb[:, 5] - 0.01096 * Fbb[:, 5] * Fbb[:, 5]
            Fbb[:, 2] = 4.76279 * Fe[:, 2] - \
                0.02295 * Fbb[:, 1] + 0.00338 * Fbb[:, 0] - 0.17365 * Fbb[:, 3] - 0.36139 * Fbb[:, 4] + 0.00857 * Fbb[:, 5] + \
                0.00032 * Fbb[:, 2] * Fbb[:, 2] - 0.00009 * Fbb[:, 2] * Fbb[:, 1] - 0.00016 * Fbb[:, 2] * Fbb[:, 0] + \
                0.00366 * Fbb[:, 2] * Fbb[:, 3] - 0.00382 * Fbb[:, 2] * Fbb[:, 4] + 0.00146 * Fbb[:, 2] * Fbb[:, 5] + \
                0.00031 * Fbb[:, 1] * Fbb[:, 1] - 0.00050 * Fbb[:, 1] * Fbb[:, 0] + 0.02079 * Fbb[:, 1] * Fbb[:, 3] - \
                0.00222 * Fbb[:, 1] * Fbb[:, 4] - 0.00709 * Fbb[:, 1] * Fbb[:, 5] + 0.00045 * Fbb[:, 0] * Fbb[:, 0] + \
                0.00588 * Fbb[:, 0] * Fbb[:, 3] + 0.01732 * Fbb[:, 0] * Fbb[:, 4] - 0.00223 * Fbb[:, 0] * Fbb[:, 5] - \
                0.12878 * Fbb[:, 3] * Fbb[:, 3] + 0.09362 * Fbb[:, 3] * Fbb[:, 4] - 0.24968 * Fbb[:, 3] * Fbb[:, 5] + \
                0.08996 * Fbb[:, 4] * Fbb[:, 4] + 0.01747 * Fbb[:, 4] * Fbb[:, 5] + 0.01161 * Fbb[:, 5] * Fbb[:, 5]
            Fbb[:, 3] = 0.38218 * Fe[:, 3] + \
                0.00068 * Fbb[:, 1] - 0.00015 * Fbb[:, 2] + 0.00010 * Fbb[:, 0] - 0.0073 * Fbb[:, 4] + 0.01998 * Fbb[:, 5] - \
                0.00141 * Fbb[:, 3] * Fbb[:, 3] - 0.00067 * Fbb[:, 3] * Fbb[:, 1] - 0.00055 * Fbb[:, 3] * Fbb[:, 2] + \
                0.00016 * Fbb[:, 3] * Fbb[:, 0] - 0.00475 * Fbb[:, 3] * Fbb[:, 4] + 0.00236 * Fbb[:, 3] * Fbb[:, 5] - \
                0.00001 * Fbb[:, 1] * Fbb[:, 1] + 0.00001 * Fbb[:, 2] * Fbb[:, 1] + 0.00002 * Fbb[:, 1] * Fbb[:, 0] + \
                0.00025 * Fbb[:, 1] * Fbb[:, 4] + 0.00025 * Fbb[:, 1] * Fbb[:, 5] - 0.00003 * Fbb[:, 2] * Fbb[:, 2] + \
                0.00002 * Fbb[:, 2] * Fbb[:, 0] + 0.00026 * Fbb[:, 2] * Fbb[:, 4] + 0.00004 * Fbb[:, 2] * Fbb[:, 5] - \
                0.00004 * Fbb[:, 0] * Fbb[:, 0] - 0.00042 * Fbb[:, 0] * Fbb[:, 4] + 0.00023 * Fbb[:, 0] * Fbb[:, 5] - \
                0.00954 * Fbb[:, 4] * Fbb[:, 4] - 0.00136 * Fbb[:, 4] * Fbb[:, 5] + 0.00219 * Fbb[:, 5] * Fbb[:, 5]
            Fbb[:, 4] = 0.19456 * Fe[:, 4] - \
                0.00007 * Fbb[:, 1] + 0.00227 * Fbb[:, 2] + 0.00113 * Fbb[:, 3] - 0.00012 * Fbb[:, 0] + 0.00488 * Fbb[:, 5] + \
                0.00714 * Fbb[:, 4] * Fbb[:, 4] + 0.00000 * Fbb[:, 4] * Fbb[:, 1] - 0.00010 * Fbb[:, 4] * Fbb[:, 2] - \
                0.00955 * Fbb[:, 4] * Fbb[:, 3] + 0.00158 * Fbb[:, 0] * Fbb[:, 0] - 0.00279 * Fbb[:, 4] * Fbb[:, 5] + \
                0.00001 * Fbb[:, 1] * Fbb[:, 1] + 0.00058 * Fbb[:, 1] * Fbb[:, 3] - 0.00035 * Fbb[:, 1] * Fbb[:, 5] + \
                0.00001 * Fbb[:, 2] * Fbb[:, 2] - 0.00035 * Fbb[:, 2] * Fbb[:, 3] - 0.00005 * Fbb[:, 2] * Fbb[:, 0] - \
                0.00006 * Fbb[:, 2] * Fbb[:, 5] - 0.00180 * Fbb[:, 3] * Fbb[:, 3] + 0.00022 * Fbb[:, 3] * Fbb[:, 0] - \
                0.02256 * Fbb[:, 3] * Fbb[:, 5] - 0.00005 * Fbb[:, 0] * Fbb[:, 0] + 0.00090 * Fbb[:, 0] * Fbb[:, 5] - \
                0.00117 * Fbb[:, 5] * Fbb[:, 5]
            Fbb[:, 5] = 0.69732 * Fe[:, 5] + \
                0.00041 * Fbb[:, 1] - 0.00087 * Fbb[:, 2] - 0.05093 * Fbb[:, 3] - 0.03029 * Fbb[:, 4] + 0.00121 * Fbb[:, 0] - \
                0.00147 * Fbb[:, 5] * Fbb[:, 5] - 0.00009 * Fbb[:, 5] * Fbb[:, 1] + 0.00000 * Fbb[:, 5] * Fbb[:, 2] + \
                0.00302 * Fbb[:, 5] * Fbb[:, 3] - 0.00159 * Fbb[:, 5] * Fbb[:, 4] + 0.00169 * Fbb[:, 5] * Fbb[:, 0] - \
                0.00019 * Fbb[:, 1] * Fbb[:, 3] - 0.00007 * Fbb[:, 1] * Fbb[:, 4] + 0.00001 * Fbb[:, 1] * Fbb[:, 0] - \
                0.00001 * Fbb[:, 2] * Fbb[:, 2] + 0.00035 * Fbb[:, 2] * Fbb[:, 3] + 0.00011 * Fbb[:, 2] * Fbb[:, 4] + \
                0.00001 * Fbb[:, 2] * Fbb[:, 0] - 0.00497 * Fbb[:, 3] * Fbb[:, 3] + 0.01545 * Fbb[:, 3] * Fbb[:, 4] - \
                0.00069 * Fbb[:, 3] * Fbb[:, 0] - 0.00108 * Fbb[:, 4] * Fbb[:, 4] + 0.00031 * Fbb[:, 4] * Fbb[:, 5] + \
                0.00001 * Fbb[:, 0] * Fbb[:, 0]

        #the balance's "body frame" data translation to aircraft 's "body frame"
        Fb = zeros(shape=(m, forceCols))  # Fb: Force and moment of aircraft at the "Body frame"
        Fb[:, 0] = Fbb[:, 0] * 0.95
        Fb[:, 1] = Fbb[:, 1] * 0.98
        Fb[:, 2] = Fbb[:, 2]
        Fb[:, 3] = Fbb[:, 3] + Fbb[:, 2] * dy - Fbb[:, 1] * dz
        Fb[:, 4] = Fbb[:, 4] - Fbb[:, 0] * dz - Fbb[:, 2] * dx
        Fb[:, 5] = (Fbb[:, 5] + Fbb[:, 0] * dy + Fbb[:, 1] * dx) * 0.56

        #calculate the aero data
        Fa = zeros(shape=(m, forceCols))  # Fa: aero's Force and moment
        Fa[:, 0] = cos(angleR[:, 0]) * cos(angleR[:, 1]) * Fb[:, 0] + sin(angleR[:, 0]) * cos(angleR[:, 1]) * Fb[:, 1] - sin(angleR[:, 1]) * Fb[:, 2]
        Fa[:, 1] = - sin(angleR[:, 0]) * Fb[:, 0] + cos(angleR[:, 0]) * Fb[:, 1]
        Fa[:, 2] = cos(angleR[:, 0]) * sin(angleR[:, 1]) * Fb[:, 0] + sin(angleR[:, 0]) * sin(angleR[:, 1]) * Fb[:, 1] + cos(angleR[:, 1]) * Fb[:, 2]
        Fa[:, 3] = cos(angleR[:, 0]) * cos(angleR[:, 1]) * Fb[:, 3] - sin(angleR[:, 0]) * cos(angleR[:, 0]) * Fb[:, 4] + sin(angleR[:, 1]) * Fb[:, 5]
        Fa[:, 4] = sin(angleR[:, 0]) * Fb[:, 3] + cos(angleR[:, 0]) * Fb[:, 4]
        Fa[:, 5] = - cos(angleR[:, 0]) * sin(angleR[:, 1]) * Fb[:, 3] + sin(angleR[:, 0]) * sin(angleR[:, 1]) * Fb[:, 4] + cos(angleR[:, 1]) * Fb[:, 5]

        # Cb: Coefficient of force and moment at the Body frame
        Cb = zeros(shape=(m, forceCols))
        Cb[:, :3] = Fb[:, :3] * 9.8 / (q * s)
        Cb[:, 3:5] = Fb[:, 3:5] * 9.8 / (q * s * l)
        Cb[:, 5] = Fb[:, 5] * 9.8 / (q * s * ba)
        # Ca: Coefficient of force and moment at the Aero frame
        Ca = zeros(shape=(m, forceCols))
        Ca[:, :3] = Fa[:, :3] * 9.8 / (q * s)
        Ca[:, 3:5] = Fa[:, 3:5] * 9.8 / (q * s * l)
        Ca[:, 5] = Fa[:, 5] * 9.8 / (q * s * ba)

        Mb = hstack((angle, Cb))
        Ma = hstack((angle, Ca))

        savetxt(bodyFile, Mb, fmt='%-15.8f',
                header=''.join(headerList).strip(),
                footer=''.join(footerList).strip(),
                comments='')
        savetxt(aeroFile, Ma, fmt='%-15.8f',
                header=''.join(headerList).strip(),
                footer=''.join(footerList).strip(),
                comments='')


class BalanceG16(Balance):
    # def __init__(self):
    #     super(self, BalanceG16).__init__(self)

    def transData(self):
        # aircraft's area, characteristic chord, free flow pressure, dx, dy, dz, air speed:V, flow pressure.
        s = self._S                     # unit: m2
        l = self._L                     # unit: m
        ba = self._refChord             # unit: pa
        dx = self._dx                   # unit: m
        dy = self._dy                   # unit: m
        dz = self._dz                   # unit: m
        V = self._V                           # unit: m/s
        q = 0.5 * AIR_DENSITY * V ** 2  # unit: pa

        staFile = self._staFile         # static file's name
        dynFile = self._dynFile         # dynamic file's name
        bodyFile = self._bodyFile       # body file's name
        aeroFile = self._aeroFile       # aero file's name

        headerRows = self._headerRows  # data file's header nums
        footerRows = self._footerRows  # data file's footer nums
        angleStartCol = self._angleStartCol  # angle start column
        angleEndCol = self._angleEndCol  # angle end column
        angleCols = angleEndCol - angleStartCol + 1  # angle columns
        forceStartCol = self._forceStartCol  # force and moment start column
        forceEndCol = self._forceEndCol  # force and moment end column
        forceCols = forceEndCol - forceStartCol + 1  # force and moment columns

        #load static file and dynamic file
        staData = genfromtxt(fname=staFile, skip_header=headerRows, skip_footer=footerRows)
        dynData = genfromtxt(fname=dynFile, skip_header=headerRows, skip_footer=footerRows)
        staAngle, staForce = staData[:, (angleStartCol - 1):angleEndCol], staData[:, (forceStartCol - 1):forceEndCol]
        dynAngle, dynForce = dynData[:, (angleStartCol - 1):angleEndCol], dynData[:, (forceStartCol - 1):forceEndCol]
        staAngleR, dynAngleR = deg2rad(staAngle), deg2rad(dynAngle)  # change the degrees to radius
        angle = (staAngle + dynAngle) / 2.
        angleR = (staAngleR + dynAngleR) / 2.
        m, n = staData.shape
        # read the file's headers and footers
        rawList = open(staFile).readlines()
        headerList = rawList[:headerRows] if headerRows else []
        footerList = rawList[-footerRows:] if footerRows else []

        #calculate the "body frame"'s fore and moment's coefficient
        Fe = dynForce - staForce  # Fe: the raw Force and moment of Balance at the "Body frame"in the experiment
        Fbb = zeros(shape=(m, forceCols))  # Fbb: Force and moment of Balance at the "Body frame"

        Fbb[:, 0] = 0.2554675*Fe[:, 0] - 0.0154822*Fe[:, 1] + 0.00390868*Fe[:, 2] - 0.0051715*Fe[:, 3] - \
            0.00178511*Fe[:, 4] - 0.0024596*Fe[:, 5]
        Fbb[:, 1] = 0.00068324*Fe[:, 0] + 0.6661034*Fe[:, 1] + 0.0120892*Fe[:, 2] - 0.0109143*Fe[:, 3] + \
            0.0391122*Fe[:, 4] + 0.0151383*Fe[:, 5]
        Fbb[:, 2] = 0.00096904*Fe[:, 0] + 0.00120306*Fe[:, 1] + 0.585989*Fe[:, 2] + 0.027769*Fe[:, 3] + \
            0.014161*Fe[:, 4] + 0.00452654*Fe[:, 5]
        Fbb[:, 3] = 0.000095445*Fe[:, 0] + 0.00029407*Fe[:, 1] + 0.00726843*Fe[:, 2] + 0.03304980*Fe[:, 3] + \
            0.0082689*Fe[:, 4] + 0.000152507*Fe[:, 5]
        Fbb[:, 4] = -0.00036007*Fe[:, 0] - 0.00009756*Fe[:, 1] + 0.00098957*Fe[:, 2] + 0.00055426*Fe[:, 3] + \
            0.02351212*Fe[:, 4] - 0.000134249*Fe[:, 5]
        Fbb[:, 5] = -0.000025559*Fe[:, 0] + 0.00075648*Fe[:, 1] + 0.000344149*Fe[:, 2] - 0.000585242*Fe[:, 3] - \
            0.0022913*Fe[:, 4] + 0.0276978*Fe[:, 5]

        #the balance's "body frame" data translation to aircraft 's "body frame"
        Fb = zeros(shape=(m, forceCols))   # Fb: Force and moment of aircraft at the "Body frame"
        Fb[:, 3] = Fbb[:, 3] + Fbb[:, 2]*dy - Fbb[:, 1]*dz
        Fb[:, 4] = Fbb[:, 4] - Fbb[:, 0]*dz - Fbb[:, 2]*dx
        Fb[:, 5] = Fbb[:, 5] + Fbb[:, 0]*dy + Fbb[:, 1]*dx

        #calculate the aero data
        Fa = zeros(shape=(m, forceCols))  # Fa: aero's Force and moment
        Fa[:, 0] = cos(angleR[:, 0])*cos(angleR[:, 1])*Fb[:, 0] + sin(angleR[:, 0])*cos(angleR[:, 1])*Fb[:, 1] - sin(angleR[:, 1])*Fb[:, 2]
        Fa[:, 1] = - sin(angleR[:, 0])*Fb[:, 0] + cos(angleR[:, 0])*Fb[:, 1]
        Fa[:, 2] = cos(angleR[:, 0])*sin(angleR[:, 1])*Fb[:, 0] + sin(angleR[:, 0])*sin(angleR[:, 1])*Fb[:, 1] + cos(angleR[:, 1])*Fb[:, 2]
        Fa[:, 3] = cos(angleR[:, 0])*cos(angleR[:, 1])*Fb[:, 3] - sin(angleR[:, 0])*cos(angleR[:, 0])*Fb[:, 4] + sin(angleR[:, 1])*Fb[:, 5]
        Fa[:, 4] = sin(angleR[:, 0])*Fb[:, 3] + cos(angleR[:, 0])*Fb[:, 4]
        Fa[:, 5] = - cos(angleR[:, 0])*sin(angleR[:, 1])*Fb[:, 3] + sin(angleR[:, 0])*sin(angleR[:, 1])*Fb[:, 4] + cos(angleR[:, 1])*Fb[:, 5]

        # Cb: Coefficient of force and moment at the Body frame
        Cb = zeros(shape=(m, forceCols))
        Cb[:, :3] = Fb[:, :3] * 9.8 / (q * s)
        Cb[:, 3:5] = Fb[:, 3:5] * 9.8 / (q * s * l)
        Cb[:, 5] = Fb[:, 5] * 9.8 / (q * s * ba)
        # Ca: Coefficient of force and moment at the Aero frame
        Ca = zeros(shape=(m, forceCols))
        Ca[:, :3] = Fa[:, :3] * 9.8 / (q * s)
        Ca[:, 3:5] = Fa[:, 3:5] * 9.8 / (q * s * l)
        Ca[:, 5] = Fa[:, 5] * 9.8 / (q * s * ba)

        Mb = hstack((angle, Cb))
        Ma = hstack((angle, Ca))

        savetxt(bodyFile, Mb, fmt='%-15.8f',
                header=''.join(headerList).strip(),
                footer=''.join(footerList).strip(),
                comments='')
        savetxt(aeroFile, Ma, fmt='%-15.8f',
                header=''.join(headerList).strip(),
                footer=''.join(footerList).strip(),
                comments='')

class DynamicRig(object):
    def __init__(self, samplingRate=1000, kineticsFre=0.2, kineticsSty=DYN_PITCH):
        self.SampleRate = samplingRate
        self.KineticsFre = kineticsFre
        self.KineticsSty = kineticsSty

    def setOutputFileFormat(self,beginAngleColumn=1, stopAngleColumn=4,
                            beginForceColumn=5, stopForceColumn=10):
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


class DataFromDynRig(DynamicRig):
    def __init__(self, filePath='', sampleRate=1000., kineticsFre=0.2):
        super(DataFromDynRig, self).__init__(sampleRate, kineticsFre)
        self.FilePath = filePath
        self.CirlePts = int(1./self.KineticsFre*self.SampleRate)

    def setFilePath(self, filePath=''):
        self.FilePath = filePath

    def setDataFileFormat(self, headerRows=1, ignorePts=200):
        self.HeaderRows = headerRows
        self.IgnorePts = ignorePts

    def getMaxPts(self):
        rawData = self.getRawData()
        maxPoint = self.IgnorePts - 1    # 计算第一个周期中的最高点数（起始位置），第n个点在数组中的位置为n-1
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
        while rawData[maxPoint, i] < ans*0.85:
            maxPoint += 1
        while rawData[maxPoint, i] <= rawData[maxPoint + 1, i]:
            maxPoint += 1
        print 'MaxPoints:', maxPoint+1, 'MaxAngle:', rawData[maxPoint, i]
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
        jfileList = [item for item in os.listdir(fileDir) if string.lower(item).endswith('jf.txt')]
        dfileList = [item for item in os.listdir(fileDir) if string.lower(item).endswith('df.txt')]
        lowerJfileList = [string.lower(item) for item in jfileList]
        lowerDfileList = [string.lower(item) for item in dfileList]
        for id1, lowerJfile in enumerate(lowerJfileList):
            lowerDfile = lowerJfile.split('jf')[0] + 'df.txt'
            if lowerDfile in lowerDfileList:
                id2 = lowerDfileList.index(lowerDfile)
                yield os.path.abspath(jfileList[id1]), os.path.abspath(dfileList[id2])


def main():
    saccon = AircraftModel(span=0.4, area=0.0521,
                           rootChord=0.2759, refChord=0.1246)
    saccon.setV(V=25)
    saccon.setDelta(dx=0, dy=0, dz=0)

    fileDir = r"D:\Workspace\SACCON\20131223SACCON\Roll\Filter-Cutoff4-Order5"
    newPath = os.path.join(fileDir, 'Results')
    print os.listdir(fileDir)
    if os.path.exists(newPath):
        shutil.rmtree(newPath)
    os.mkdir(newPath)
    for staFile, dynFile in searchFileIter(fileDir):
        #创建数据模型
        print staFile, '--->>', dynFile
        info = DataFileInfo(staFile)
        kineticsFre = info.getKineticsFre()
        kineticsSty = info.getKineticsSty()
        phi0 = info.getRollAngle()
        dataObj = DataFromDynRig(filePath=staFile, sampleRate=1000, kineticsFre=kineticsFre)
        dataObj.setKineticsSty(kineticsSty)
        dataObj.setDataFileFormat(headerRows=1, ignorePts=200)
        angle = dataObj.getAngleData()
        staCoe = dataObj.getAverageCoeData()

        dataObj.setFilePath(filePath=dynFile)
        dynCoe = dataObj.getAverageCoeData()

        tempFile = os.path.splitext(os.path.split(staFile)[1])
        aeroFile = tempFile[0].split('JF')[0] + 'FQ' + tempFile[1]
        aeroFile = os.path.join(newPath, aeroFile)
        bodyFile = tempFile[0].split('JF')[0] + 'FT' + tempFile[1]
        bodyFile = os.path.join(newPath, bodyFile)

        print aeroFile, '--->>', bodyFile

        balance = BalanceG18(staFile=staFile, dynFile=dynFile,
                             aeroFile=aeroFile, bodyFile=bodyFile,
                             aircraftModel=saccon)
        balance.setPhi0(phi0)
        aeroAngle = balance.getAeroAngle(angle)
        tempBodyData = balance.getTempBodyForceAndMoment(staData=staCoe, dynData=dynCoe)
        tempAeroData = balance.getTempAeroForceAndMoment(aeroAngle, tempBodyData)
        bodyData = balance.getForceAndMoment(tempBodyData)
        aeroData = balance.getForceAndMoment(tempAeroData)

        balance.writeToFile(aeroAngle, bodyData, aeroData)
if __name__ == '__main__':
    #创建一个SACCON模型
    import profile
    profile.run(main())




