# -*-coding: utf-8 -*-
"""
this is the φ18 balance data's translation programming.

Author: liuchao
Date: 2014-09-05
"""
from __future__ import division
from numpy import (zeros_like, sin, cos, genfromtxt, deg2rad, hstack, savetxt, zeros, sum, dot)
from aircraft import AircraftModel

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


class Balance(object):

    BalanceDic = {-1: u"None", 0: u"14杆天平", 1: u"16杆天平", 2: u"18杆天平", 3: u"盒式天平(内)", 4: u"盒式天平(外)"}

    def __init__(self, staFile=None, dynFile=None, bodyFile=None, aeroFile=None,
                 headerRows=1, footerRows=0, angleStartCol=0, angleEndCol=3,
                 forceStartCol=4, forceEndCol=9, aircraftModel=None, balanceSty=-1, balanceCoes=None):
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
        self._balanceSty = balanceSty
        self._balanceCoes = balanceCoes

        self._speed = 0.
        self._area = 0.
        self._span = 0.
        self._rootChord = 0.
        self._refChord = 0.
        self._dx = 0.
        self._dy = 0.
        self._dz = 0.
        self.setAircraftModel(aircraftModel)

        self._columnOffset = {}

    def __str__(self):
        return unicode(u'''<p><b>{:<10s}</b></p><p>{:>}</p>
<p><b>{:<10s}</b></p><p>{:>}</p>
<p><b>{:<10s}</b></p><p>{:>}</p>
<p><b>{:<10s}</b></p><p>{:>}</p>
<p><b>{:<15s}</b>{:<s}</p>
<p><b>{:<15s}</b>{:<f}㎡</p>
<p><b>{:<15s}</b>{:<f}m</p>
<p><b>{:<15s}</b>{:<f}m</p>
<p><b>{:<15s}</b>{:<f}m</p>
<p><b>{:<15s}</b>{:<f}m/s</p>
<p><b>{:<15s}</b>{:<f}m</p>
<p><b>{:<15s}</b>{:<f}m</p>
<p><b>{:<15s}</b>{:<f}m</p>
'''.format(u'静态文件:', self._staFile,
           u'动态文件:', self._dynFile,
           u'生成的气动文件:', self._aeroFile,
           u'要生成的体轴文件:', self._bodyFile,
           u'天平类型:', Balance.BalanceDic[self._balanceSty],
           u'模型面积:', self._area,
           u'模型展长:', self._span,
           u'模型根弦长:', self._rootChord,
           u'模型参考弦长:', self._refChord,
           u'试验风速:', self._speed,
           u'ΔX:', self._dx, u'ΔY:', self._dy, u'ΔZ:', self._dz))

    def __repr__(self):
        return str(self)

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
        if isinstance(aircraftModel, AircraftModel):
            self._speed = aircraftModel.speed
            self._area = aircraftModel.area
            self._span = aircraftModel.span
            self._rootChord = aircraftModel.rootChord
            self._refChord = aircraftModel.refChord
            self._dx = aircraftModel.dx
            self._dy = aircraftModel.dy
            self._dz = aircraftModel.dz

    def setColumnOffset(self, offset=None):
        if isinstance(offset, type({})):
            self._columnOffset = offset
            return True
        else:
            return False

    def setBalanceSty(self, balanceSty=-1):
        if balanceSty == -1 and balanceSty > 3:
            return False
        else:
            self._balanceSty = balanceSty

    def setBalanceCoes(self, balanceCoes=None):
        self._balanceCoes = balanceCoes
        return

    def getBalanceCoes(self):
        return self._balanceCoes

    # def _genDataByG16(self, fe):
    #     Fe = fe
    #     Fbb = zeros_like(Fe)
    #     coe = self._balanceCoes
    #     Fbb[:, 0] = coe[0, 0]*Fe[:, 0] + coe[0, 1]*Fe[:, 1] + coe[0, 2]*Fe[:, 2] + coe[0, 3]*Fe[:, 3] + coe[0, 4]*Fe[:, 4] + coe[0, 5]*Fe[:, 5]
    #     Fbb[:, 1] = coe[1, 0]*Fe[:, 0] + coe[1, 1]*Fe[:, 1] + coe[1, 2]*Fe[:, 2] + coe[1, 3]*Fe[:, 3] + coe[1, 4]*Fe[:, 4] + coe[1, 5]*Fe[:, 5]
    #     Fbb[:, 2] = coe[2, 0]*Fe[:, 0] + coe[2, 1]*Fe[:, 1] + coe[2, 2]*Fe[:, 2] + coe[2, 3]*Fe[:, 3] + coe[2, 4]*Fe[:, 4] + coe[2, 5]*Fe[:, 5]
    #     Fbb[:, 3] = coe[3, 0]*Fe[:, 0] + coe[3, 1]*Fe[:, 1] + coe[3, 2]*Fe[:, 2] + coe[3, 3]*Fe[:, 3] + coe[3, 4]*Fe[:, 4] + coe[3, 5]*Fe[:, 5]
    #     Fbb[:, 4] = coe[4, 0]*Fe[:, 0] + coe[4, 1]*Fe[:, 1] + coe[4, 2]*Fe[:, 2] + coe[4, 3]*Fe[:, 3] + coe[4, 4]*Fe[:, 4] + coe[4, 5]*Fe[:, 5]
    #     Fbb[:, 5] = coe[5, 0]*Fe[:, 0] + coe[5, 1]*Fe[:, 1] + coe[4, 2]*Fe[:, 2] + coe[5, 3]*Fe[:, 3] + coe[5, 4]*Fe[:, 4] + coe[5, 5]*Fe[:, 5]
    #
    #     return Fbb

    def _genDataByG16(self, fe):
        Fe = fe

        coe = self._balanceCoes
        # func 1:
        # Fbb = zeros_like(Fe)
        # for i in range(6):
        #     Fbb[:, i] = sum(coe[i, :] * Fe, axis=1)
        # func 2：
        Fbb = dot(Fe, coe.T)    # 采用数组的点积，可以加快运算速度
        return Fbb

    def _genDataByG14(self, fe):
        Fe = fe
        # Fbb = zeros_like(Fe)  # Fbb: Force and moment of Balance at the "Body frame"
        coe = self._balanceCoes
        # for i in range(6):
        #     Fbb[:, i] = sum(coe[i, :] * Fe, axis=1)
        Fbb = dot(Fe, coe.T)
        return Fbb

    def _genDataByG18(self, fe):
        Fe = fe
        Fbb = zeros_like(Fe)  # Fbb: Force and moment of Balance at the "Body frame"
        coe = self._balanceCoes
        Fbb[:, 0] = coe[0, 0] * Fe[:, 0]
        Fbb[:, 1] = coe[1, 0] * Fe[:, 1]
        Fbb[:, 2] = coe[2, 0] * Fe[:, 2]
        Fbb[:, 3] = coe[3, 0] * Fe[:, 3]
        Fbb[:, 4] = coe[4, 0] * Fe[:, 4]
        Fbb[:, 5] = coe[5, 0] * Fe[:, 5]
        for i in range(100):
            Fbb[:, 0] = coe[0, 0] * Fe[:, 0] + \
                        coe[0, 1] * Fbb[:, 1] + coe[0, 2] * Fbb[:, 2] + coe[0, 3] * Fbb[:, 3] + coe[0, 4] * Fbb[:, 4] + coe[0, 5] * Fbb[:, 5] \
                        + coe[0, 6] * Fbb[:, 0] * Fbb[:, 0] + coe[0, 7] * Fbb[:, 0] * Fbb[:, 1] + coe[0, 8] * Fbb[:, 0] * Fbb[:, 2] + coe[0, 9] * Fbb[:, 0] * Fbb[:, 3] + coe[0, 10] * Fbb[:, 0] * Fbb[:, 4] + coe[0, 11] * Fbb[:, 0] * Fbb[:, 5] \
                        + coe[0, 12] * Fbb[:, 1] * Fbb[:, 1] + coe[0, 13] * Fbb[:, 1] * Fbb[:, 2] + coe[0, 14] * Fbb[:, 1] * Fbb[:, 3] + coe[0, 15] * Fbb[:, 1] * Fbb[:, 4] + coe[0, 16] * Fbb[:, 1] * Fbb[:, 5] \
                        + coe[0, 17] * Fbb[:, 2] * Fbb[:, 2] + coe[0, 18] * Fbb[:, 2] * Fbb[:, 3] + coe[0, 19] * Fbb[:, 2] * Fbb[:, 4] + coe[0, 20] * Fbb[:, 2] * Fbb[:, 5] \
                        + coe[0, 21] * Fbb[:, 3] * Fbb[:, 3] + coe[0, 22] * Fbb[:, 3] * Fbb[:, 4] + coe[0, 23] * Fbb[:, 3] * Fbb[:, 5] \
                        + coe[0, 24] * Fbb[:, 4] * Fbb[:, 4] + coe[0, 25] * Fbb[:, 4] * Fbb[:, 5] \
                        + coe[0, 26] * Fbb[:, 5] * Fbb[:, 5]

            Fbb[:, 1] = coe[1, 0] * Fe[:, 1] + \
                        coe[1, 1] * Fbb[:, 0] + coe[1, 2] * Fbb[:, 2] + coe[1, 3] * Fbb[:, 3] + coe[1, 4] * Fbb[:, 4] + coe[1, 5] * Fbb[:, 5] \
                        + coe[1, 6] * Fbb[:, 1] * Fbb[:, 1] + coe[1, 7] * Fbb[:, 1] * Fbb[:, 0] + coe[1, 8] * Fbb[:, 1] * Fbb[:, 2] + coe[1, 9] * Fbb[:, 1] * Fbb[:, 3] + coe[1, 10] * Fbb[:, 1] * Fbb[:, 4] + coe[1, 11] * Fbb[:, 1] * Fbb[:, 5] \
                        + coe[1, 12] * Fbb[:, 0] * Fbb[:, 0] + coe[1, 13] * Fbb[:, 0] * Fbb[:, 2] + coe[1, 14] * Fbb[:, 0] * Fbb[:, 3] + coe[1, 15] * Fbb[:, 0] * Fbb[:, 4] + coe[1, 16] * Fbb[:, 0] * Fbb[:, 5] \
                        + coe[1, 17] * Fbb[:, 2] * Fbb[:, 2] + coe[1, 18] * Fbb[:, 2] * Fbb[:, 3] + coe[1, 19] * Fbb[:, 2] * Fbb[:, 4] + coe[1, 20] * Fbb[:, 2] * Fbb[:, 5] \
                        + coe[1, 21] * Fbb[:, 3] * Fbb[:, 3] + coe[1, 22] * Fbb[:, 3] * Fbb[:, 4] + coe[1, 23] * Fbb[:, 3] * Fbb[:, 5] \
                        + coe[1, 24] * Fbb[:, 4] * Fbb[:, 4] + coe[1, 25] * Fbb[:, 4] * Fbb[:, 5] \
                        + coe[1, 26] * Fbb[:, 5] * Fbb[:, 5]

            Fbb[:, 2] = coe[2, 0] * Fe[:, 2] + \
                        coe[2, 1] * Fbb[:, 1] + coe[2, 2] * Fbb[:, 0] + coe[2, 3] * Fbb[:, 3] + coe[2, 4] * Fbb[:, 4] + coe[2, 5] * Fbb[:, 5] \
                        + coe[2, 6] * Fbb[:, 2] * Fbb[:, 2] + coe[2, 7] * Fbb[:, 2] * Fbb[:, 1] + coe[2, 8] * Fbb[:, 2] * Fbb[:, 0] + coe[2, 9] * Fbb[:, 2] * Fbb[:, 3] + coe[2, 10] * Fbb[:, 2] * Fbb[:, 4] + coe[2, 11] * Fbb[:, 2] * Fbb[:, 5] \
                        + coe[2, 12] * Fbb[:, 1] * Fbb[:, 1] + coe[2, 13] * Fbb[:, 1] * Fbb[:, 0] + coe[2, 14] * Fbb[:, 1] * Fbb[:, 3] + coe[2, 15] * Fbb[:, 1] * Fbb[:, 4] + coe[2, 16] * Fbb[:, 1] * Fbb[:, 5] \
                        + coe[2, 17] * Fbb[:, 0] * Fbb[:, 0] + coe[2, 18] * Fbb[:, 0] * Fbb[:, 3] + coe[2, 19] * Fbb[:, 0] * Fbb[:, 4] + coe[2, 20] * Fbb[:, 0] * Fbb[:, 5] \
                        + coe[2, 21] * Fbb[:, 3] * Fbb[:, 3] + coe[2, 22] * Fbb[:, 3] * Fbb[:, 4] + coe[2, 23] * Fbb[:, 3] * Fbb[:, 5] \
                        + coe[2, 24] * Fbb[:, 4] * Fbb[:, 4] + coe[2, 25] * Fbb[:, 4] * Fbb[:, 5] \
                        + coe[2, 26] * Fbb[:, 5] * Fbb[:, 5]

            Fbb[:, 3] = coe[3, 0] * Fe[:, 3] + \
                        coe[3, 1] * Fbb[:, 1] + coe[3, 2] * Fbb[:, 2] + coe[3, 3] * Fbb[:, 0] + coe[3, 4] * Fbb[:, 4] + coe[3, 5] * Fbb[:, 5] \
                        + coe[3, 6] * Fbb[:, 3] * Fbb[:, 3] + coe[3, 7] * Fbb[:, 3] * Fbb[:, 1] + coe[3, 8] * Fbb[:, 3] * Fbb[:, 2] + coe[3, 9] * Fbb[:, 3] * Fbb[:, 0] + coe[3, 10] * Fbb[:, 3] * Fbb[:, 4] + coe[3, 11] * Fbb[:, 3] * Fbb[:, 5] \
                        + coe[3, 12] * Fbb[:, 1] * Fbb[:, 1] + coe[3, 13] * Fbb[:, 1] * Fbb[:, 2] + coe[3, 14] * Fbb[:, 1] * Fbb[:, 0] + coe[3, 15] * Fbb[:, 1] * Fbb[:, 4] + coe[3, 16] * Fbb[:, 1] * Fbb[:, 5] \
                        + coe[3, 17] * Fbb[:, 2] * Fbb[:, 2] + coe[3, 18] * Fbb[:, 2] * Fbb[:, 0] + coe[3, 19] * Fbb[:, 2] * Fbb[:, 4] + coe[3, 20] * Fbb[:, 2] * Fbb[:, 5] \
                        + coe[3, 21] * Fbb[:, 0] * Fbb[:, 0] + coe[3, 22] * Fbb[:, 0] * Fbb[:, 4] + coe[3, 23] * Fbb[:, 0] * Fbb[:, 5] \
                        + coe[3, 24] * Fbb[:, 4] * Fbb[:, 4] + coe[3, 25] * Fbb[:, 4] * Fbb[:, 5] \
                        + coe[3, 26] * Fbb[:, 5] * Fbb[:, 5]

            Fbb[:, 4] = coe[4, 0] * Fe[:, 4] + \
                        coe[4, 1] * Fbb[:, 1] + coe[4, 2] * Fbb[:, 2] + coe[4, 3] * Fbb[:, 3] + coe[4, 4] * Fbb[:, 0] + coe[4, 5] * Fbb[:, 5] \
                        + coe[4, 6] * Fbb[:, 4] * Fbb[:, 4] + coe[4, 7] * Fbb[:, 4] * Fbb[:, 1] + coe[4, 8] * Fbb[:, 4] * Fbb[:, 2] + coe[4, 9] * Fbb[:, 4] * Fbb[:, 3] + coe[4, 10] * Fbb[:, 4] * Fbb[:, 0] + coe[4, 11] * Fbb[:, 4] * Fbb[:, 5] \
                        + coe[4, 12] * Fbb[:, 1] * Fbb[:, 1] + coe[4, 13] * Fbb[:, 1] * Fbb[:, 2] + coe[4, 14] * Fbb[:, 1] * Fbb[:, 3] + coe[4, 15] * Fbb[:, 1] * Fbb[:, 0] + coe[4, 16] * Fbb[:, 1] * Fbb[:, 5] \
                        + coe[4, 17] * Fbb[:, 2] * Fbb[:, 2] + coe[4, 18] * Fbb[:, 2] * Fbb[:, 3] + coe[4, 19] * Fbb[:, 2] * Fbb[:, 0] + coe[4, 20] * Fbb[:, 2] * Fbb[:, 5] \
                        + coe[4, 21] * Fbb[:, 3] * Fbb[:, 3] + coe[4, 22] * Fbb[:, 3] * Fbb[:, 0] + coe[4, 23] * Fbb[:, 3] * Fbb[:, 5] \
                        + coe[4, 24] * Fbb[:, 0] * Fbb[:, 0] + coe[4, 25] * Fbb[:, 0] * Fbb[:, 5] \
                        + coe[4, 26] * Fbb[:, 5] * Fbb[:, 5]

            Fbb[:, 5] = coe[5, 0] * Fe[:, 5] + \
                        coe[5, 1] * Fbb[:, 1] + coe[5, 2] * Fbb[:, 2] + coe[5, 3] * Fbb[:, 3] + coe[5, 4] * Fbb[:, 4] + coe[5, 5] * Fbb[:, 0] \
                        + coe[5, 6] * Fbb[:, 5] * Fbb[:, 5] + coe[5, 7] * Fbb[:, 5] * Fbb[:, 1] + coe[5, 8] * Fbb[:, 5] * Fbb[:, 2] + coe[5, 9] * Fbb[:, 5] * Fbb[:, 3] + coe[5, 10] * Fbb[:, 5] * Fbb[:, 4] + coe[5, 11] * Fbb[:, 5] * Fbb[:, 0] \
                        + coe[5, 12] * Fbb[:, 1] * Fbb[:, 1] + coe[5, 13] * Fbb[:, 1] * Fbb[:, 2] + coe[5, 14] * Fbb[:, 1] * Fbb[:, 3] + coe[5, 15] * Fbb[:, 1] * Fbb[:, 4] + coe[5, 16] * Fbb[:, 1] * Fbb[:, 0] \
                        + coe[5, 17] * Fbb[:, 2] * Fbb[:, 2] + coe[5, 18] * Fbb[:, 2] * Fbb[:, 3] + coe[5, 19] * Fbb[:, 2] * Fbb[:, 4] + coe[5, 20] * Fbb[:, 2] * Fbb[:, 0] \
                        + coe[5, 21] * Fbb[:, 3] * Fbb[:, 3] + coe[5, 22] * Fbb[:, 3] * Fbb[:, 4] + coe[5, 23] * Fbb[:, 3] * Fbb[:, 0] \
                        + coe[5, 24] * Fbb[:, 4] * Fbb[:, 4] + coe[5, 25] * Fbb[:, 4] * Fbb[:, 0] \
                        + coe[5, 26] * Fbb[:, 0] * Fbb[:, 0]
        return Fbb

    def _genDataByG18Vec(self, fe):
        Fe = fe
        Fbb = zeros_like(Fe)  # Fbb: Force and moment of Balance at the "Body frame"
        coe = self._balanceCoes
        Fbb[:, 0] = coe[0, 0] * Fe[:, 0]
        Fbb[:, 1] = coe[1, 0] * Fe[:, 1]
        Fbb[:, 2] = coe[2, 0] * Fe[:, 2]
        Fbb[:, 3] = coe[3, 0] * Fe[:, 3]
        Fbb[:, 4] = coe[4, 0] * Fe[:, 4]
        Fbb[:, 5] = coe[5, 0] * Fe[:, 5]
        for i in range(100):
            Fbb[:, 0] = coe[0, 0]*Fe[:, 0] + sum(Fbb[:, [1, 2, 3, 4, 5]]*coe[0, 1:6], 1) + \
                sum(Fbb[:, 0]*(Fbb[:, 0:6]*coe[0,  6:12]), 1) + \
                sum(Fbb[:, 1]*(Fbb[:, 1:6]*coe[0, 12:17]), 1) + \
                sum(Fbb[:, 2]*(Fbb[:, 2:6]*coe[0, 17:21]), 1) + \
                sum(Fbb[:, 3]*(Fbb[:, 3:6]*coe[0, 21:24]), 1) + \
                sum(Fbb[:, 4]*(Fbb[:, 4:6]*coe[0, 24:26]), 1) + \
                sum(Fbb[:, 5]*(Fbb[:, 5:6]*coe[0, 26:27]), 1)
            Fbb[:, 1] = coe[1, 0]*Fe[:, 1] + sum(Fbb[:, [0, 2, 3, 4, 5]]*coe[1, 1:6], 1) + \
                sum(Fbb[:, 0]*(Fbb[:, 0:6]*coe[1,  6:12]), 1) + \
                sum(Fbb[:, 1]*(Fbb[:, 1:6]*coe[1, 12:17]), 1) + \
                sum(Fbb[:, 2]*(Fbb[:, 2:6]*coe[1, 17:21]), 1) + \
                sum(Fbb[:, 3]*(Fbb[:, 3:6]*coe[1, 21:24]), 1) + \
                sum(Fbb[:, 4]*(Fbb[:, 4:6]*coe[1, 24:26]), 1) + \
                sum(Fbb[:, 5]*(Fbb[:, 5:6]*coe[1, 26:27]), 1)
            Fbb[:, 2] = coe[2, 0]*Fe[:, 2] + sum(Fbb[:, [0, 1, 3, 4, 5]]*coe[2, 1:6], 1) + \
                sum(Fbb[:, 0]*(Fbb[:, 0:6]*coe[2,  6:12]), 1) + \
                sum(Fbb[:, 1]*(Fbb[:, 1:6]*coe[2, 12:17]), 1) + \
                sum(Fbb[:, 2]*(Fbb[:, 2:6]*coe[2, 17:21]), 1) + \
                sum(Fbb[:, 3]*(Fbb[:, 3:6]*coe[2, 21:24]), 1) + \
                sum(Fbb[:, 4]*(Fbb[:, 4:6]*coe[2, 24:26]), 1) + \
                sum(Fbb[:, 5]*(Fbb[:, 5:6]*coe[2, 26:27]), 1)
            Fbb[:, 3] = coe[3, 0]*Fe[:, 3] + sum(Fbb[:, [0, 1, 2, 4, 5]]*coe[3, 1:6], 1) + \
                sum(Fbb[:, 0]*(Fbb[:, 0:6]*coe[3,  6:12]), 1) + \
                sum(Fbb[:, 1]*(Fbb[:, 1:6]*coe[3, 12:17]), 1) + \
                sum(Fbb[:, 2]*(Fbb[:, 2:6]*coe[3, 17:21]), 1) + \
                sum(Fbb[:, 3]*(Fbb[:, 3:6]*coe[3, 21:24]), 1) + \
                sum(Fbb[:, 4]*(Fbb[:, 4:6]*coe[3, 24:26]), 1) + \
                sum(Fbb[:, 5]*(Fbb[:, 5:6]*coe[3, 26:27]), 1)
            Fbb[:, 4] = coe[4, 0]*Fe[:, 4] + sum(Fbb[:, [0, 1, 2, 3, 5]]*coe[4, 1:6], 1) + \
                sum(Fbb[:, 0]*(Fbb[:, 0:6]*coe[4,  6:12]), 1) + \
                sum(Fbb[:, 1]*(Fbb[:, 1:6]*coe[4, 12:17]), 1) + \
                sum(Fbb[:, 2]*(Fbb[:, 2:6]*coe[4, 17:21]), 1) + \
                sum(Fbb[:, 3]*(Fbb[:, 3:6]*coe[4, 21:24]), 1) + \
                sum(Fbb[:, 4]*(Fbb[:, 4:6]*coe[4, 24:26]), 1) + \
                sum(Fbb[:, 5]*(Fbb[:, 5:6]*coe[4, 26:27]), 1)
            Fbb[:, 5] = coe[5, 0]*Fe[:, 5] + sum(Fbb[:, [0, 1, 2, 3, 4]]*coe[5, 1:6], 1) + \
                sum(Fbb[:, 0]*(Fbb[:, 0:6]*coe[5,  6:12]), 1) + \
                sum(Fbb[:, 1]*(Fbb[:, 1:6]*coe[5, 12:17]), 1) + \
                sum(Fbb[:, 2]*(Fbb[:, 2:6]*coe[5, 17:21]), 1) + \
                sum(Fbb[:, 3]*(Fbb[:, 3:6]*coe[5, 21:24]), 1) + \
                sum(Fbb[:, 4]*(Fbb[:, 4:6]*coe[5, 24:26]), 1) + \
                sum(Fbb[:, 5]*(Fbb[:, 5:6]*coe[5, 26:27]), 1)

        return Fbb

    def _genDataByBoxOutToFb(self, fe, dx, dy, dz):
        Fe = fe
        # Fbb = zeros_like(Fe)  # Fbb: Force and moment of Balance at the "Body frame"
        coe = self._balanceCoes
        # for i in range(6):
        #     Fbb[:, i] = sum(coe[i, :] * Fe, axis=1)
        Fbb = dot(Fe, coe[:, :6].T)
        Fbb[:, 5] = coe[5, 0]*Fe[:, 0] + coe[5, 1]*Fe[:, 1] + coe[5, 2]*Fe[:, 1]**2 + coe[5, 3] * Fe[:, 2] + coe[5, 4] * Fe[:, 2] ** 2 + coe[5, 5]*Fe[:, 3] + coe[5, 6]*Fe[:, 4] + coe[5, 7]*Fe[:, 5]


        #the balance's "body frame" data translation to aircraft 's "body frame"
        Fb = zeros_like(Fbb)  # Fb: Force and moment of aircraft at the "Body frame"
        Fb[:, 0] = Fbb[:, 0]
        Fb[:, 1] = - Fbb[:, 2]
        Fb[:, 2] = Fbb[:, 1]
        Fb[:, 3] = Fbb[:, 3] + Fbb[:, 2] * dy - Fbb[:, 1] * dz
        Fb[:, 4] = -Fbb[:, 5] - Fbb[:, 0] * dy - Fbb[:, 1] * dx
        Fb[:, 5] = Fbb[:, 4] - Fbb[:, 0] * dz - Fbb[:, 2] * dx

        return Fb

    def _genDataByBoxInToFb(self, fe, dx, dy, dz):
        Fe = fe
        # Fbb = zeros_like(Fe)
        coe = self._balanceCoes
        # for i in range(6):
        #     Fbb[:, i] = sum(coe[i, :] * Fe, axis=1)
        Fbb = dot(Fe, coe[:, :6].T)
        Fbb[:, 5] = coe[5, 0]*Fe[:, 0] + coe[5, 1]*Fe[:, 1] + coe[5, 2]*Fe[:, 1]**2 + coe[5, 3] * Fe[:, 2] + coe[5, 4] * Fe[:, 2] ** 2 + coe[5, 5]*Fe[:, 3] + coe[5, 6]*Fe[:, 4] + coe[5, 7]*Fe[:, 5]

        # the balance's "body frame" data translation to aircraft 's "body frame"
        Fb = zeros_like(Fbb)  # Fb: Force and moment of aircraft at the "Body frame"
        Fb[:, 0] = Fbb[:, 0]
        Fb[:, 1] = Fbb[:, 2]
        Fb[:, 2] = - Fbb[:, 1]
        Fb[:, 3] = Fbb[:, 3] + Fbb[:, 2] * dy - Fbb[:, 1] * dz
        Fb[:, 4] = Fbb[:, 5] + Fbb[:, 0] * dy + Fbb[:, 1] * dx
        Fb[:, 5] = -Fbb[:, 4] + Fbb[:, 0] * dz + Fbb[:, 2] * dx

        return Fb

    def translateData(self):
        staFile = self._staFile  # static file's name
        dynFile = self._dynFile  # dynamic file's name
        bodyFile = self._bodyFile  # body file's name
        aeroFile = self._aeroFile  # aero file's name

        headerRows = self._headerRows  # data file's header nums
        footerRows = self._footerRows  # data file's footer nums
        angleStartCol = self._angleStartCol  # angle start column
        angleEndCol = self._angleEndCol  # angle end column
        angleCols = angleEndCol - angleStartCol + 1  # angle columns
        forceStartCol = self._forceStartCol  # force and moment start column
        forceEndCol = self._forceEndCol  # force and moment end column
        forceCols = forceEndCol - forceStartCol + 1  # force and moment columns
        try:
            # load static file and dynamic file
            staData = genfromtxt(fname=staFile, skip_header=headerRows, skip_footer=footerRows)
            dynData = genfromtxt(fname=dynFile, skip_header=headerRows, skip_footer=footerRows)
            if self._columnOffset:
                for col in range(angleStartCol, angleEndCol + 1):
                    offset = self._columnOffset.get(col, 0)
                    staData[:, col - 1] = staData[:, col - 1] + offset
                    dynData[:, col - 1] = dynData[:, col - 1] + offset
            staAngle, staForce = staData[:, (angleStartCol - 1):angleEndCol], staData[:, (forceStartCol - 1):forceEndCol]
            dynAngle, dynForce = dynData[:, (angleStartCol - 1):angleEndCol], dynData[:, (forceStartCol - 1):forceEndCol]
            staAngleR, dynAngleR = deg2rad(staAngle), deg2rad(dynAngle)  # change the degrees to radius
            ang = (staAngle + dynAngle) / 2.
            angR = (staAngleR + dynAngleR) / 2.
            m = staData.shape[0]
            if angleCols == 1:  # 非典型角度列
                ang = hstack((ang, zeros(shape=(m, 2))))
                angR = hstack((angR, zeros(shape=(m, 2))))
            if angleCols == 2:
                ang = hstack((ang, zeros(shape=(m, 1))))
                angR = hstack((angR, zeros(shape=(m, 1))))
            # read the file's headers and footers
            rawList = open(staFile).readlines()
            headerList = rawList[:headerRows] if headerRows else []
            footerList = rawList[-footerRows:] if footerRows else []

            # calculate the "body frame"'s fore and moment's coefficient
            Fe = dynForce - staForce  # Fe: the raw Force and moment of Balance at the "Body frame"in the experiment
            Fbb = zeros((m, forceCols))
            Fb = zeros((m, forceCols))
            if self._balanceSty == 0:  # 14杆天平
                Fbb = self._genDataByG14(fe=Fe)
            if self._balanceSty == 1:  # 16杆
                Fbb = self._genDataByG16(fe=Fe)
            if self._balanceSty == 2:  # 18杆
                Fbb = self._genDataByG18(fe=Fe)
            if self._balanceSty == 3:  # 盒式天平(内)
                dx = self._dx
                dy = self._dy
                dz = self._dz
                Fb = self._genDataByBoxInToFb(fe=Fe, dx=dx, dy=dy, dz=dz)
            if self._balanceSty == 4:  # 盒式天平(外)
                dx = self._dx
                dy = self._dy
                dz = self._dz
                Fb = self._genDataByBoxOutToFb(fe=Fe, dx=dx, dy=dy, dz=dz)
            #  the balance's "body frame" data translation to aircraft 's "body frame"
            if self._balanceSty in [0, 1, 2]:
                Fb = self._getFbFromFbb(fbb=Fbb)
            #calculate the aero data
            Fa = self._getFaFromFb(angR=angR, fb=Fb)
            # Cb: Coefficient of force and moment at the Body frame
            Cb = self._getCoe(Fb)
            # Ca: Coefficient of force and moment at the Aero frame
            Ca = self._getCoe(Fa)

            Mb = hstack((ang, Cb))
            Ma = hstack((ang, Ca))

            savetxt(bodyFile, Mb, fmt='%-15.8f',
                    header=''.join(headerList).strip(),
                    footer=''.join(footerList).strip(),
                    comments='')
            savetxt(aeroFile, Ma, fmt='%-15.8f',
                    header=''.join(headerList).strip(),
                    footer=''.join(footerList).strip(),
                    comments='')
            return True, None
        except Exception, e:
            return False, e.message
    
    def _getFbFromFbb(self, fbb):
        #the balance's "body frame" data translation to aircraft 's "body frame"
        fb = zeros_like(fbb)  # fb: Force and moment of aircraft at the "Body frame"
        dx = self._dx
        dy = self._dy
        dz = self._dz
        fb[:, :3] = fbb[:, :3]
        fb[:, 3] = fbb[:, 3] + fbb[:, 2] * dy - fbb[:, 1] * dz
        fb[:, 4] = fbb[:, 4] - fbb[:, 0] * dz - fbb[:, 2] * dx
        fb[:, 5] = fbb[:, 5] + fbb[:, 0] * dy + fbb[:, 1] * dx

        return fb

    @staticmethod
    def _getFaFromFb(angR, fb):
        # calculate the aero data
        fa = zeros_like(fb)     # fa: aero's Force and moment

        fa[:, 0] = cos(angR[:, 0]) * cos(angR[:, 1]) * fb[:, 0] + sin(angR[:, 0]) * cos(angR[:, 1]) * fb[:, 1] - sin(angR[:, 1]) * fb[:, 2]
        fa[:, 1] = - sin(angR[:, 0]) * fb[:, 0] + cos(angR[:, 0]) * fb[:, 1]
        fa[:, 2] = cos(angR[:, 0]) * sin(angR[:, 1]) * fb[:, 0] + sin(angR[:, 0]) * sin(angR[:, 1]) * fb[:, 1] + cos(angR[:, 1]) * fb[:, 2]
        fa[:, 3] = cos(angR[:, 0]) * cos(angR[:, 1]) * fb[:, 3] - sin(angR[:, 0]) * cos(angR[:, 0]) * fb[:, 4] + sin(angR[:, 1]) * fb[:, 5]
        fa[:, 4] = sin(angR[:, 0]) * fb[:, 3] + cos(angR[:, 0]) * fb[:, 4]
        fa[:, 5] = - cos(angR[:, 0]) * sin(angR[:, 1]) * fb[:, 3] + sin(angR[:, 0]) * sin(angR[:, 1]) * fb[:, 4] + cos(angR[:, 1]) * fb[:, 5]

        return fa
    
    def _getCoe(self, f):
        # coe: coefficient of force and moment
        coe = zeros_like(f)
        s = self._area
        l = self._span
        ba = self._refChord
        V = self._speed  # unit: m/s
        q = 0.5 * AIR_DENSITY * V ** 2  # unit: pa
        coe[:, :3] = f[:, :3] * 9.8 / (q * s)
        coe[:, 3:5] = f[:, 3:5] * 9.8 / (q * s * l)
        coe[:, 5] = f[:, 5] * 9.8 / (q * s * ba)
        
        return coe


if __name__ == '__main__':
    airmodel = AircraftModel()
    b = Balance("c:/tsdf.txt", "h:/sdf.x", "ds.xt", "sdf.x", aircraftModel=airmodel)
    print unicode(b)
