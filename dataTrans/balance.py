# -*-coding: utf-8 -*-
"""
this is the  balance data's translation programming.

Author: liuchao
Date: 2014-09-05
"""
from __future__ import division

import numpy as np
from numpy import sin, cos

from aircraft import AircraftModel


class Balance(object):

    BalanceDic = {-1: u"None", 0: u"14杆天平", 1: u"16杆天平", 2: u"18杆天平", 3: u"盒式天平(内)", 4: u"盒式天平(外)"}
    AIR_DENSITY = 1.2250  # 空气密度
    ABSOLUTE_ZERO = 273.15  # 绝对零度

    def __init__(self, staFile=None, dynFile=None, bodyFile=None, aeroFile=None, headerRows=1, footerRows=0,
                 angleType='body', thetaCol=None, phiCol=None, psiCol=None, alphaCol=None, betaCol=None, time=True,
                 forceStartCol=4, forceEndCol=9, aircraftModel=None, balanceSty=-1, balanceCoes=None):
        self._staFile = staFile
        self._dynFile = dynFile
        self._bodyFile = bodyFile
        self._aeroFile = aeroFile
        self._headerRows = headerRows
        self._footerRows = footerRows
        self._angleType = angleType
        self._thetaCol = thetaCol
        self._phiCol = phiCol
        self._psiCol = psiCol
        self._alphaCol = alphaCol
        self._betaCol = betaCol
        self._time = time
        self._FMStartCol = forceStartCol
        self._FMEndCol = forceEndCol

        self._balanceSty = balanceSty
        self._balanceCoes = balanceCoes
        self._model = aircraftModel

    def __str__(self):
        return unicode(u'''<p><b>{:<10s}</b></p><p>{:>}</p><p><b>{:<10s}</b></p><p>{:>}</p><p><b>{:<10s}</b></p><p>{:>}</p>
<p><b>{:<10s}</b></p><p>{:>}</p><p><b>{:<15s}</b>{:<s}</p><p><b>{:<15s}</b>{:<f}㎡</p><p><b>{:<15s}</b>{:<f}m</p>
<p><b>{:<15s}</b>{:<f}m</p><p><b>{:<15s}</b>{:<f}m</p><p><b>{:<15s}</b>{:<f}m/s</p><p><b>{:<15s}</b>{:<f}m</p>
<p><b>{:<15s}</b>{:<f}m</p><p><b>{:<15s}</b>{:<f}m</p>
'''.format(u'静态文件:', self._staFile, u'动态文件:', self._dynFile, u'生成的气动文件:', self._aeroFile, u'要生成的体轴文件:', self._bodyFile,
           u'天平类型:', Balance.BalanceDic[self._balanceSty], u'模型面积:', self._model.area, u'模型展长:', self._model.span, u'模型根弦长:', self._model.rootChord,
           u'模型参考弦长:', self._model.refChord, u'试验风速:', self._model.speed, u'ΔX:', self._model.dx, u'ΔY:', self._model.dy, u'ΔZ:', self._model.dz))

    def __repr__(self):
        return str(self)

    def setStaFile(self, staFile):
        self._staFile = staFile

    def getStaFile(self):
        return self._staFile

    def setDynFile(self, dynFile):
        self._dynFile = dynFile

    def getDynFile(self):
        return self._dynFile

    def setBodyFile(self, bodyFile):
        self._bodyFile = bodyFile

    def getBodyFile(self):
        return self._bodyFile

    def setAeroFile(self, aeroFile):
        self._aeroFile = aeroFile

    def getAeroFile(self):
        return  self._aeroFile

    def setHeaderRows(self, headerRows):
        self._headerRows = headerRows

    def setFooterRows(self, footerRows):
        self._footerRows = footerRows

    def setAngleType(self, angleType=''):
        self._angleType = angleType

    def setTime(self, t):
        self._time = t

    def setThetaCol(self, col):
        self._thetaCol = col

    def setPhiCol(self, col):
        self._phiCol = col

    def setPsiCol(self, col):
        self._psiCol = col

    def setAlphaCol(self, col):
        self._alphaCol = col

    def setBetaCol(self, col):
        self._betaCol = col

    def setFMStartCol(self, col):
        self._FMStartCol = col

    def setFMEndCol(self, col):
        self._FMEndCol = col

    def setAircraftModel(self, model=None):
        if isinstance(model, AircraftModel):
            self._model = model

    def setBalanceSty(self, style=-1):
        if style == -1 and style > 3:
            return False
        else:
            self._balanceSty = style

    def setBalanceCoes(self, balanceCoes=None):
        self._balanceCoes = balanceCoes

    def getBalanceCoes(self):
        return self._balanceCoes

    def run(self):
        try:
            # load static file and dynamic file
            staData = np.genfromtxt(fname=self._staFile, skip_header=self._headerRows, skip_footer=self._footerRows)
            dynData = np.genfromtxt(fname=self._dynFile, skip_header=self._headerRows, skip_footer=self._footerRows)

            m, n = staData.shape
            if m != dynData.shape[0] or n != dynData.shape[1]:
                raise Exception(u"静态数据与动态数据行数不一致")

            bodyAngle = np.zeros((m, 3))
            aeroAngle = np.zeros((m, 2))
            if self._angleType == 'body':
                thetaArray = (staData[:, self._thetaCol]+dynData[:, self._thetaCol])/2. if self._thetaCol is not None else 0.
                phiArray = (staData[:, self._phiCol]+dynData[:, self._phiCol])/2. if self._phiCol is not None else 0.
                psiArray = (staData[:, self._psiCol]+dynData[:, self._psiCol])/2. if self._psiCol is not None else 0.
                alpharArray, betarArray = self._trans_aeroAngle_from_bodyAngle(np.deg2rad(thetaArray), np.deg2rad(phiArray), np.deg2rad(psiArray))

                bodyAngle[:, 0] = thetaArray
                bodyAngle[:, 1] = phiArray
                bodyAngle[:, 2] = psiArray
                aeroAngle[:, 0] = np.rad2deg(alpharArray)
                aeroAngle[:, 1] = np.rad2deg(betarArray)
            else:
                aeroAngle[:, 0] = (staData[:, self._alphaCol]+dynData[:, self._alphaCol])/2. if self._alphaCol is not None else 0.
                aeroAngle[:, 1] = (staData[:, self._betaCol]+dynData[:, self._betaCol])/2. if self._betaCol is not None else 0.

            # calculate the "body frame"'s fore and moment's coefficient
            expCoe = dynData[:, self._FMStartCol:(self._FMStartCol+6)] - staData[:, self._FMStartCol:(self._FMStartCol+6)]
            balanceCoe = np.zeros((m, 6))
            bodyCoe = np.zeros((m, 6))
            if self._balanceSty == 0:  # 14杆天平
                balanceCoe = self._get_balance_from_expCoe_G14(fe=expCoe)
            if self._balanceSty == 1:  # 16杆
                balanceCoe = self._get_balanceCoe_from_expCoe_G16(fe=expCoe)
            if self._balanceSty == 2:  # 18杆
                balanceCoe = self._get_balance_from_expCoe_G18(fe=expCoe)
            if self._balanceSty == 3:  # 盒式天平(内)
                bodyCoe = self._get_bodyCoe_from_expCoe_BoxIn(fe=expCoe)
            if self._balanceSty == 4:  # 盒式天平(外)
                bodyCoe = self._ger_bodyCoe_from_expCoe_BoxOut(fe=expCoe)
            if self._balanceSty in [0, 1, 2]:
                bodyCoe = self._get_bodyCoe_from_balanceCoe(fbb=balanceCoe)
            #calculate the aero data
            aerorAngle = np.deg2rad(aeroAngle)
            aeroCoe = self._get_aeroCoe_from_bodyCoe(angr=aerorAngle, fb=bodyCoe)
            # Cb: Coefficient of force and moment at the Body frame
            Cb = self._get_dimensionless_Coe(bodyCoe)
            # Ca: Coefficient of force and moment at the Aero frame
            Ca = self._get_dimensionless_Coe(aeroCoe)

            if self._angleType == 'body':
                Mb = np.concatenate((bodyAngle, aeroAngle, Cb), axis=1)
                Ma = np.concatenate((bodyAngle, aeroAngle, Ca), axis=1)
                bodyTitle = ['theta', 'phi', 'psi', 'alpha', 'beta', 'CA', 'CN', 'CY', 'Cl', 'Cn', 'Cm']
                aeroTitle = ['theta', 'phi', 'psi', 'alpha', 'beta', 'CD', 'CL', 'Cy', 'Cmx', 'Cmy', 'Cmz']
                if self._time:
                    time = np.arange(1, m + 1) * 0.001
                    bodyTitle.insert(0, 'time')
                    aeroTitle.insert(0, 'time')
                    Mb = np.concatenate((time[:, np.newaxis], Mb), axis=1)
                    Ma = np.concatenate((time[:, np.newaxis], Ma), axis=1)
                np.savetxt(self._bodyFile, Mb, fmt='%+010.8f', header='\t'.join(bodyTitle).strip(), comments='')
                np.savetxt(self._aeroFile, Ma, fmt='%+010.8f', header='\t'.join(aeroTitle).strip(), comments='')
            else:
                Mb = np.concatenate((aeroAngle, Cb), axis=1)
                Ma = np.concatenate((aeroAngle, Cb), axis=1)
                bodyTitle = ['alpha', 'beta', 'CA', 'CN', 'CY', 'Cl', 'Cn', 'Cm']
                aeroTitle = ['alpha', 'beta', 'CD', 'CL', 'Cy', 'Cmx', 'Cmy', 'Cmz']
                if self._time:
                    time = np.arange(1, m + 1) * 0.001
                    bodyTitle.insert(0, 'time')
                    aeroTitle.insert(0, 'time')
                    Mb = np.concatenate((time[:, np.newaxis], Mb), axis=1)
                    Ma = np.concatenate((time[:, np.newaxis], Ma), axis=1)
                np.savetxt(self._bodyFile, Mb, fmt='%+010.8f', header='\t'.join(bodyTitle).strip(), comments='')
                np.savetxt(self._aeroFile, Ma, fmt='%+010.8f', header='\t'.join(aeroTitle).strip(), comments='')

            return True, None
        except Exception, e:
            return False, e.message

    def _get_balanceCoe_from_expCoe_G16(self, fe):
        coe = self._balanceCoes
        Fbb = np.dot(fe, coe.T)    # 采用数组的点积，可以加快运算速度
        return Fbb

    def _get_balance_from_expCoe_G14(self, fe):
        coe = self._balanceCoes
        Fbb = np.dot(fe, coe.T)
        return Fbb

    def _get_balance_from_expCoe_G18(self, fe):
        Fbb = np.zeros_like(fe)  # Fbb: Force and moment of Balance at the "Body frame"
        coe = self._balanceCoes
        Fbb[:, 0] = coe[0, 0] * fe[:, 0]
        Fbb[:, 1] = coe[1, 0] * fe[:, 1]
        Fbb[:, 2] = coe[2, 0] * fe[:, 2]
        Fbb[:, 3] = coe[3, 0] * fe[:, 3]
        Fbb[:, 4] = coe[4, 0] * fe[:, 4]
        Fbb[:, 5] = coe[5, 0] * fe[:, 5]
        for i in range(100):
            Fbb[:, 0] = coe[0, 0] * fe[:, 0] + \
                        coe[0, 1] * Fbb[:, 1] + coe[0, 2] * Fbb[:, 2] + coe[0, 3] * Fbb[:, 3] + coe[0, 4] * Fbb[:, 4] + coe[0, 5] * Fbb[:, 5] \
                        + coe[0, 6] * Fbb[:, 0] * Fbb[:, 0] + coe[0, 7] * Fbb[:, 0] * Fbb[:, 1] + coe[0, 8] * Fbb[:, 0] * Fbb[:, 2] + coe[0, 9] * Fbb[:, 0] * Fbb[:, 3] + coe[0, 10] * Fbb[:, 0] * Fbb[:, 4] + coe[0, 11] * Fbb[:, 0] * Fbb[:, 5] \
                        + coe[0, 12] * Fbb[:, 1] * Fbb[:, 1] + coe[0, 13] * Fbb[:, 1] * Fbb[:, 2] + coe[0, 14] * Fbb[:, 1] * Fbb[:, 3] + coe[0, 15] * Fbb[:, 1] * Fbb[:, 4] + coe[0, 16] * Fbb[:, 1] * Fbb[:, 5] \
                        + coe[0, 17] * Fbb[:, 2] * Fbb[:, 2] + coe[0, 18] * Fbb[:, 2] * Fbb[:, 3] + coe[0, 19] * Fbb[:, 2] * Fbb[:, 4] + coe[0, 20] * Fbb[:, 2] * Fbb[:, 5] \
                        + coe[0, 21] * Fbb[:, 3] * Fbb[:, 3] + coe[0, 22] * Fbb[:, 3] * Fbb[:, 4] + coe[0, 23] * Fbb[:, 3] * Fbb[:, 5] \
                        + coe[0, 24] * Fbb[:, 4] * Fbb[:, 4] + coe[0, 25] * Fbb[:, 4] * Fbb[:, 5] \
                        + coe[0, 26] * Fbb[:, 5] * Fbb[:, 5]

            Fbb[:, 1] = coe[1, 0] * fe[:, 1] + \
                        coe[1, 1] * Fbb[:, 0] + coe[1, 2] * Fbb[:, 2] + coe[1, 3] * Fbb[:, 3] + coe[1, 4] * Fbb[:, 4] + coe[1, 5] * Fbb[:, 5] \
                        + coe[1, 6] * Fbb[:, 1] * Fbb[:, 1] + coe[1, 7] * Fbb[:, 1] * Fbb[:, 0] + coe[1, 8] * Fbb[:, 1] * Fbb[:, 2] + coe[1, 9] * Fbb[:, 1] * Fbb[:, 3] + coe[1, 10] * Fbb[:, 1] * Fbb[:, 4] + coe[1, 11] * Fbb[:, 1] * Fbb[:, 5] \
                        + coe[1, 12] * Fbb[:, 0] * Fbb[:, 0] + coe[1, 13] * Fbb[:, 0] * Fbb[:, 2] + coe[1, 14] * Fbb[:, 0] * Fbb[:, 3] + coe[1, 15] * Fbb[:, 0] * Fbb[:, 4] + coe[1, 16] * Fbb[:, 0] * Fbb[:, 5] \
                        + coe[1, 17] * Fbb[:, 2] * Fbb[:, 2] + coe[1, 18] * Fbb[:, 2] * Fbb[:, 3] + coe[1, 19] * Fbb[:, 2] * Fbb[:, 4] + coe[1, 20] * Fbb[:, 2] * Fbb[:, 5] \
                        + coe[1, 21] * Fbb[:, 3] * Fbb[:, 3] + coe[1, 22] * Fbb[:, 3] * Fbb[:, 4] + coe[1, 23] * Fbb[:, 3] * Fbb[:, 5] \
                        + coe[1, 24] * Fbb[:, 4] * Fbb[:, 4] + coe[1, 25] * Fbb[:, 4] * Fbb[:, 5] \
                        + coe[1, 26] * Fbb[:, 5] * Fbb[:, 5]

            Fbb[:, 2] = coe[2, 0] * fe[:, 2] + \
                        coe[2, 1] * Fbb[:, 1] + coe[2, 2] * Fbb[:, 0] + coe[2, 3] * Fbb[:, 3] + coe[2, 4] * Fbb[:, 4] + coe[2, 5] * Fbb[:, 5] \
                        + coe[2, 6] * Fbb[:, 2] * Fbb[:, 2] + coe[2, 7] * Fbb[:, 2] * Fbb[:, 1] + coe[2, 8] * Fbb[:, 2] * Fbb[:, 0] + coe[2, 9] * Fbb[:, 2] * Fbb[:, 3] + coe[2, 10] * Fbb[:, 2] * Fbb[:, 4] + coe[2, 11] * Fbb[:, 2] * Fbb[:, 5] \
                        + coe[2, 12] * Fbb[:, 1] * Fbb[:, 1] + coe[2, 13] * Fbb[:, 1] * Fbb[:, 0] + coe[2, 14] * Fbb[:, 1] * Fbb[:, 3] + coe[2, 15] * Fbb[:, 1] * Fbb[:, 4] + coe[2, 16] * Fbb[:, 1] * Fbb[:, 5] \
                        + coe[2, 17] * Fbb[:, 0] * Fbb[:, 0] + coe[2, 18] * Fbb[:, 0] * Fbb[:, 3] + coe[2, 19] * Fbb[:, 0] * Fbb[:, 4] + coe[2, 20] * Fbb[:, 0] * Fbb[:, 5] \
                        + coe[2, 21] * Fbb[:, 3] * Fbb[:, 3] + coe[2, 22] * Fbb[:, 3] * Fbb[:, 4] + coe[2, 23] * Fbb[:, 3] * Fbb[:, 5] \
                        + coe[2, 24] * Fbb[:, 4] * Fbb[:, 4] + coe[2, 25] * Fbb[:, 4] * Fbb[:, 5] \
                        + coe[2, 26] * Fbb[:, 5] * Fbb[:, 5]

            Fbb[:, 3] = coe[3, 0] * fe[:, 3] + \
                        coe[3, 1] * Fbb[:, 1] + coe[3, 2] * Fbb[:, 2] + coe[3, 3] * Fbb[:, 0] + coe[3, 4] * Fbb[:, 4] + coe[3, 5] * Fbb[:, 5] \
                        + coe[3, 6] * Fbb[:, 3] * Fbb[:, 3] + coe[3, 7] * Fbb[:, 3] * Fbb[:, 1] + coe[3, 8] * Fbb[:, 3] * Fbb[:, 2] + coe[3, 9] * Fbb[:, 3] * Fbb[:, 0] + coe[3, 10] * Fbb[:, 3] * Fbb[:, 4] + coe[3, 11] * Fbb[:, 3] * Fbb[:, 5] \
                        + coe[3, 12] * Fbb[:, 1] * Fbb[:, 1] + coe[3, 13] * Fbb[:, 1] * Fbb[:, 2] + coe[3, 14] * Fbb[:, 1] * Fbb[:, 0] + coe[3, 15] * Fbb[:, 1] * Fbb[:, 4] + coe[3, 16] * Fbb[:, 1] * Fbb[:, 5] \
                        + coe[3, 17] * Fbb[:, 2] * Fbb[:, 2] + coe[3, 18] * Fbb[:, 2] * Fbb[:, 0] + coe[3, 19] * Fbb[:, 2] * Fbb[:, 4] + coe[3, 20] * Fbb[:, 2] * Fbb[:, 5] \
                        + coe[3, 21] * Fbb[:, 0] * Fbb[:, 0] + coe[3, 22] * Fbb[:, 0] * Fbb[:, 4] + coe[3, 23] * Fbb[:, 0] * Fbb[:, 5] \
                        + coe[3, 24] * Fbb[:, 4] * Fbb[:, 4] + coe[3, 25] * Fbb[:, 4] * Fbb[:, 5] \
                        + coe[3, 26] * Fbb[:, 5] * Fbb[:, 5]

            Fbb[:, 4] = coe[4, 0] * fe[:, 4] + \
                        coe[4, 1] * Fbb[:, 1] + coe[4, 2] * Fbb[:, 2] + coe[4, 3] * Fbb[:, 3] + coe[4, 4] * Fbb[:, 0] + coe[4, 5] * Fbb[:, 5] \
                        + coe[4, 6] * Fbb[:, 4] * Fbb[:, 4] + coe[4, 7] * Fbb[:, 4] * Fbb[:, 1] + coe[4, 8] * Fbb[:, 4] * Fbb[:, 2] + coe[4, 9] * Fbb[:, 4] * Fbb[:, 3] + coe[4, 10] * Fbb[:, 4] * Fbb[:, 0] + coe[4, 11] * Fbb[:, 4] * Fbb[:, 5] \
                        + coe[4, 12] * Fbb[:, 1] * Fbb[:, 1] + coe[4, 13] * Fbb[:, 1] * Fbb[:, 2] + coe[4, 14] * Fbb[:, 1] * Fbb[:, 3] + coe[4, 15] * Fbb[:, 1] * Fbb[:, 0] + coe[4, 16] * Fbb[:, 1] * Fbb[:, 5] \
                        + coe[4, 17] * Fbb[:, 2] * Fbb[:, 2] + coe[4, 18] * Fbb[:, 2] * Fbb[:, 3] + coe[4, 19] * Fbb[:, 2] * Fbb[:, 0] + coe[4, 20] * Fbb[:, 2] * Fbb[:, 5] \
                        + coe[4, 21] * Fbb[:, 3] * Fbb[:, 3] + coe[4, 22] * Fbb[:, 3] * Fbb[:, 0] + coe[4, 23] * Fbb[:, 3] * Fbb[:, 5] \
                        + coe[4, 24] * Fbb[:, 0] * Fbb[:, 0] + coe[4, 25] * Fbb[:, 0] * Fbb[:, 5] \
                        + coe[4, 26] * Fbb[:, 5] * Fbb[:, 5]

            Fbb[:, 5] = coe[5, 0] * fe[:, 5] + \
                        coe[5, 1] * Fbb[:, 1] + coe[5, 2] * Fbb[:, 2] + coe[5, 3] * Fbb[:, 3] + coe[5, 4] * Fbb[:, 4] + coe[5, 5] * Fbb[:, 0] \
                        + coe[5, 6] * Fbb[:, 5] * Fbb[:, 5] + coe[5, 7] * Fbb[:, 5] * Fbb[:, 1] + coe[5, 8] * Fbb[:, 5] * Fbb[:, 2] + coe[5, 9] * Fbb[:, 5] * Fbb[:, 3] + coe[5, 10] * Fbb[:, 5] * Fbb[:, 4] + coe[5, 11] * Fbb[:, 5] * Fbb[:, 0] \
                        + coe[5, 12] * Fbb[:, 1] * Fbb[:, 1] + coe[5, 13] * Fbb[:, 1] * Fbb[:, 2] + coe[5, 14] * Fbb[:, 1] * Fbb[:, 3] + coe[5, 15] * Fbb[:, 1] * Fbb[:, 4] + coe[5, 16] * Fbb[:, 1] * Fbb[:, 0] \
                        + coe[5, 17] * Fbb[:, 2] * Fbb[:, 2] + coe[5, 18] * Fbb[:, 2] * Fbb[:, 3] + coe[5, 19] * Fbb[:, 2] * Fbb[:, 4] + coe[5, 20] * Fbb[:, 2] * Fbb[:, 0] \
                        + coe[5, 21] * Fbb[:, 3] * Fbb[:, 3] + coe[5, 22] * Fbb[:, 3] * Fbb[:, 4] + coe[5, 23] * Fbb[:, 3] * Fbb[:, 0] \
                        + coe[5, 24] * Fbb[:, 4] * Fbb[:, 4] + coe[5, 25] * Fbb[:, 4] * Fbb[:, 0] \
                        + coe[5, 26] * Fbb[:, 0] * Fbb[:, 0]
        return Fbb

    def _get_balance_from_expCoe_G18_Vec(self, fe):
        Fbb = np.zeros_like(fe)  # Fbb: Force and moment of Balance at the "Body frame"
        coe = self._balanceCoes
        Fbb[:, 0] = coe[0, 0] * fe[:, 0]
        Fbb[:, 1] = coe[1, 0] * fe[:, 1]
        Fbb[:, 2] = coe[2, 0] * fe[:, 2]
        Fbb[:, 3] = coe[3, 0] * fe[:, 3]
        Fbb[:, 4] = coe[4, 0] * fe[:, 4]
        Fbb[:, 5] = coe[5, 0] * fe[:, 5]
        for i in range(100):
            Fbb[:, 0] = coe[0, 0]*fe[:, 0] + sum(Fbb[:, [1, 2, 3, 4, 5]]*coe[0, 1:6], 1) + \
                sum(Fbb[:, 0]*(Fbb[:, 0:6]*coe[0,  6:12]), 1) + \
                sum(Fbb[:, 1]*(Fbb[:, 1:6]*coe[0, 12:17]), 1) + \
                sum(Fbb[:, 2]*(Fbb[:, 2:6]*coe[0, 17:21]), 1) + \
                sum(Fbb[:, 3]*(Fbb[:, 3:6]*coe[0, 21:24]), 1) + \
                sum(Fbb[:, 4]*(Fbb[:, 4:6]*coe[0, 24:26]), 1) + \
                sum(Fbb[:, 5]*(Fbb[:, 5:6]*coe[0, 26:27]), 1)
            Fbb[:, 1] = coe[1, 0]*fe[:, 1] + sum(Fbb[:, [0, 2, 3, 4, 5]]*coe[1, 1:6], 1) + \
                sum(Fbb[:, 0]*(Fbb[:, 0:6]*coe[1,  6:12]), 1) + \
                sum(Fbb[:, 1]*(Fbb[:, 1:6]*coe[1, 12:17]), 1) + \
                sum(Fbb[:, 2]*(Fbb[:, 2:6]*coe[1, 17:21]), 1) + \
                sum(Fbb[:, 3]*(Fbb[:, 3:6]*coe[1, 21:24]), 1) + \
                sum(Fbb[:, 4]*(Fbb[:, 4:6]*coe[1, 24:26]), 1) + \
                sum(Fbb[:, 5]*(Fbb[:, 5:6]*coe[1, 26:27]), 1)
            Fbb[:, 2] = coe[2, 0]*fe[:, 2] + sum(Fbb[:, [0, 1, 3, 4, 5]]*coe[2, 1:6], 1) + \
                sum(Fbb[:, 0]*(Fbb[:, 0:6]*coe[2,  6:12]), 1) + \
                sum(Fbb[:, 1]*(Fbb[:, 1:6]*coe[2, 12:17]), 1) + \
                sum(Fbb[:, 2]*(Fbb[:, 2:6]*coe[2, 17:21]), 1) + \
                sum(Fbb[:, 3]*(Fbb[:, 3:6]*coe[2, 21:24]), 1) + \
                sum(Fbb[:, 4]*(Fbb[:, 4:6]*coe[2, 24:26]), 1) + \
                sum(Fbb[:, 5]*(Fbb[:, 5:6]*coe[2, 26:27]), 1)
            Fbb[:, 3] = coe[3, 0]*fe[:, 3] + sum(Fbb[:, [0, 1, 2, 4, 5]]*coe[3, 1:6], 1) + \
                sum(Fbb[:, 0]*(Fbb[:, 0:6]*coe[3,  6:12]), 1) + \
                sum(Fbb[:, 1]*(Fbb[:, 1:6]*coe[3, 12:17]), 1) + \
                sum(Fbb[:, 2]*(Fbb[:, 2:6]*coe[3, 17:21]), 1) + \
                sum(Fbb[:, 3]*(Fbb[:, 3:6]*coe[3, 21:24]), 1) + \
                sum(Fbb[:, 4]*(Fbb[:, 4:6]*coe[3, 24:26]), 1) + \
                sum(Fbb[:, 5]*(Fbb[:, 5:6]*coe[3, 26:27]), 1)
            Fbb[:, 4] = coe[4, 0]*fe[:, 4] + sum(Fbb[:, [0, 1, 2, 3, 5]]*coe[4, 1:6], 1) + \
                sum(Fbb[:, 0]*(Fbb[:, 0:6]*coe[4,  6:12]), 1) + \
                sum(Fbb[:, 1]*(Fbb[:, 1:6]*coe[4, 12:17]), 1) + \
                sum(Fbb[:, 2]*(Fbb[:, 2:6]*coe[4, 17:21]), 1) + \
                sum(Fbb[:, 3]*(Fbb[:, 3:6]*coe[4, 21:24]), 1) + \
                sum(Fbb[:, 4]*(Fbb[:, 4:6]*coe[4, 24:26]), 1) + \
                sum(Fbb[:, 5]*(Fbb[:, 5:6]*coe[4, 26:27]), 1)
            Fbb[:, 5] = coe[5, 0]*fe[:, 5] + sum(Fbb[:, [0, 1, 2, 3, 4]]*coe[5, 1:6], 1) + \
                sum(Fbb[:, 0]*(Fbb[:, 0:6]*coe[5,  6:12]), 1) + \
                sum(Fbb[:, 1]*(Fbb[:, 1:6]*coe[5, 12:17]), 1) + \
                sum(Fbb[:, 2]*(Fbb[:, 2:6]*coe[5, 17:21]), 1) + \
                sum(Fbb[:, 3]*(Fbb[:, 3:6]*coe[5, 21:24]), 1) + \
                sum(Fbb[:, 4]*(Fbb[:, 4:6]*coe[5, 24:26]), 1) + \
                sum(Fbb[:, 5]*(Fbb[:, 5:6]*coe[5, 26:27]), 1)

        return Fbb

    def _ger_bodyCoe_from_expCoe_BoxOut(self, fe):
        coe = self._balanceCoes
        Fbb = np.dot(fe, coe[:, :6].T)
        Fbb[:, 5] = coe[5, 0]*fe[:, 0] + coe[5, 1]*fe[:, 1] + coe[5, 2]*fe[:, 1]**2 + coe[5, 3] * fe[:, 2] + coe[5, 4] * fe[:, 2] ** 2 + coe[5, 5]*fe[:, 3] + coe[5, 6]*fe[:, 4] + coe[5, 7]*fe[:, 5]

        dx, dy, dz = self._model.dx, self._model.dy, self._model.dz
        Fb = np.zeros_like(Fbb)  # Fb: Force and moment of aircraft at the "Body frame"
        Fb[:, 0] = Fbb[:, 0]
        Fb[:, 1] = - Fbb[:, 2]
        Fb[:, 2] = Fbb[:, 1]
        Fb[:, 3] = Fbb[:, 3] + Fbb[:, 2] * dy - Fbb[:, 1] * dz
        Fb[:, 4] = -Fbb[:, 5] - Fbb[:, 0] * dy - Fbb[:, 1] * dx
        Fb[:, 5] = Fbb[:, 4] - Fbb[:, 0] * dz - Fbb[:, 2] * dx

        return Fb

    def _get_bodyCoe_from_expCoe_BoxIn(self, fe):
        coe = self._balanceCoes
        Fbb = np.dot(fe, coe[:, :6].T)
        Fbb[:, 5] = coe[5, 0]*fe[:, 0] + coe[5, 1]*fe[:, 1] + coe[5, 2]*fe[:, 1]**2 + coe[5, 3] * fe[:, 2] + coe[5, 4] * fe[:, 2] ** 2 + coe[5, 5]*fe[:, 3] + coe[5, 6]*fe[:, 4] + coe[5, 7]*fe[:, 5]

        # the new balance's "body frame" data translation to aircraft 's "body frame"
        dx, dy, dz = self._model.dx, self._model.dy, self._model.dz
        Fb = np.zeros_like(Fbb)  # Fb: Force and moment of aircraft at the "Body frame"
        Fb[:, 0] = Fbb[:, 0]
        Fb[:, 1] = Fbb[:, 2]
        Fb[:, 2] = - Fbb[:, 1]
        Fb[:, 3] = Fbb[:, 3] + Fbb[:, 2] * dy - Fbb[:, 1] * dz
        Fb[:, 4] = Fbb[:, 5] + Fbb[:, 0] * dy + Fbb[:, 1] * dx
        Fb[:, 5] = -Fbb[:, 4] + Fbb[:, 0] * dz + Fbb[:, 2] * dx

        return Fb
    
    def _get_bodyCoe_from_balanceCoe(self, fbb):
        #the new balance's "body frame" data translation to aircraft 's "body frame"
        fb = np.zeros_like(fbb)  # fb: Force and moment of aircraft at the "Body frame"
        dx = self._model.dx
        dy = self._model.dy
        dz = self._model.dz
        fb[:, :3] = fbb[:, :3]
        fb[:, 3] = fbb[:, 3] + fbb[:, 2] * dy - fbb[:, 1] * dz
        fb[:, 4] = fbb[:, 4] - fbb[:, 0] * dz - fbb[:, 2] * dx
        fb[:, 5] = fbb[:, 5] + fbb[:, 0] * dy + fbb[:, 1] * dx

        return fb

    @staticmethod
    def _get_aeroCoe_from_bodyCoe(angr, fb):
        # calculate the aero data
        fa = np.zeros_like(fb)     # fa: aero's Force and moment
        fa[:, 0] = cos(angr[:, 0]) * cos(angr[:, 1]) * fb[:, 0] + sin(angr[:, 0]) * cos(angr[:, 1]) * fb[:, 1] - sin(angr[:, 1]) * fb[:, 2]
        fa[:, 1] = - sin(angr[:, 0]) * fb[:, 0] + cos(angr[:, 0]) * fb[:, 1]
        fa[:, 2] = cos(angr[:, 0]) * sin(angr[:, 1]) * fb[:, 0] + sin(angr[:, 0]) * sin(angr[:, 1]) * fb[:, 1] + cos(angr[:, 1]) * fb[:, 2]
        fa[:, 3] = cos(angr[:, 0]) * cos(angr[:, 1]) * fb[:, 3] - sin(angr[:, 0]) * cos(angr[:, 0]) * fb[:, 4] + sin(angr[:, 1]) * fb[:, 5]
        fa[:, 4] = sin(angr[:, 0]) * fb[:, 3] + cos(angr[:, 0]) * fb[:, 4]
        fa[:, 5] = - cos(angr[:, 0]) * sin(angr[:, 1]) * fb[:, 3] + sin(angr[:, 0]) * sin(angr[:, 1]) * fb[:, 4] + cos(angr[:, 1]) * fb[:, 5]

        return fa
    
    def _get_dimensionless_Coe(self, f):
        # coe: coefficient of force and moment
        coe = np.zeros_like(f)
        s = self._model.area
        l = self._model.span
        ba = self._model.refChord
        V = self._model.speed  # unit: m/s
        q = 0.5 * Balance.AIR_DENSITY * V ** 2  # unit: pa

        coe[:, :3] = f[:, :3] * 9.8 / (q * s)
        coe[:, 3:5] = f[:, 3:5] * 9.8 / (q * s * l)
        coe[:, 5] = f[:, 5] * 9.8 / (q * s * ba)
        
        return coe

    @staticmethod
    def _trans_aeroAngle_from_bodyAngle(thetar=None, phir=None, psir=None):
        """
        由欧拉角计算气动角度，单位：弧度
        """

        thetar = thetar if thetar is not None else 0.
        phir = phir if phir is not None else 0.
        psir = psir if psir is not None else 0.

        tan_alpha = (np.cos(phir) * np.sin(thetar) - np.sin(phir) * np.sin(psir) * np.cos(thetar)) / (np.cos(psir) * np.cos(thetar))
        sin_beta = np.sin(phir) * np.sin(thetar) + np.cos(phir) * np.sin(psir) * np.cos(thetar)
        alphar, betar = np.arctan(tan_alpha), np.arcsin(sin_beta)

        return alphar, betar


if __name__ == '__main__':
    airmodel = AircraftModel()
    b = Balance("c:/tsdf.txt", "h:/sdf.x", "ds.xt", "sdf.x", aircraftModel=airmodel)
    print unicode(b)
