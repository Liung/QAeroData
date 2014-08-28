#coding: UTF-8
from __future__ import division
import os
import numpy as np
import sys
import re
import string
import shutil
from dataFilter import DataFilter

__author__ = 'Vincent'


PITCH,YAW,ROLL = range(3)

class DataFileInfo:
    def __init__(self,filePath=''):
        self.__filePath = filePath

    @property
    def filePath(self):
        return self.__filePath

    @filePath.setter
    def filePath(self,filePath):
        if isinstance(filePath,type('Hello')):
            self.__filePath = filePath
        else:
            raise TypeError('filePath is a type of str')

    def getKineticsSty(self):
        fileName = os.path.basename(self.__filePath)
        if string.upper(fileName[:2]) == 'DP':
            kineticsSty = PITCH
        elif string.upper(fileName[:2]) == 'DR':
            kineticsSty = ROLL
        else:
            kineticsSty = YAW

        return kineticsSty

    def getPitchAngle(self):
        '''
        DP_P60R00AP05_N05JF.txt
        '''
        reStr = '(p|P)[-|+]{0,1}\d+(r|R)'
        fileName = os.path.basename(self.__filePath)
        m = re.search(reStr,fileName)
        pitchAngle = float(m.group()[1:-1]) if m is not None else 0

        return pitchAngle

    def getYawAngle(self):
        return 0.0

    def getRollAngle(self):
        '''
        DP_P60R00AP05_N05JF.txt
        '''
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
        m = re.search(reStr,fileName)
        am = float(m.group()[2:-2]) if m is not None else 0

        return am

    def getKineticsFre(self):
        reStr = '(n|N)[-|+]{0,1}\d+(j|d|J|D)'
        fileName = os.path.basename(self.__filePath)
        m = re.search(reStr,fileName)
        index = int(m.group()[1:-1]) if m is not None else 0

        return index*0.2

ratio = 3. 
fpath = 'G:/Workspace/SACCON/20131223SACCON/Pitch/Dynamic/'
tarpath = os.path.join(fpath,'filter-%.1f' % (ratio))
if os.path.exists(tarpath):
	shutil.rmtree(tarpath)
os.mkdir(tarpath)

fp = [ f for f in os.listdir(fpath) if f.endswith('.txt')]
print fp
for f in fp:
	rawfile = os.path.join(fpath,f)
	fobj = DataFileInfo(f)
	fz = fobj.getKineticsFre()

	print f,':',fz
	filtfilename = f.replace('.txt','F.txt')
	filtfile = os.path.join(tarpath,filtfilename)
	filtobj = DataFilter(samplingRate=1000,filterOrder=5)
	filtobj.setFileFormat(rawFileName=rawfile,filtFileName=filtfile,headerNums=1)
	filtobj.setFileFre(fz)
	filtobj.setCutoffFreRatio(ratio)
	cutFre = filtobj._cutoffFre
	print filtfile,':',cutFre
	filtobj.toDataFile()
