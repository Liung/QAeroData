 #-*- coding: cp936 -*-
from distutils.core import setup

import py2exe

excludes = []
includes = ["sip","encodings", "encodings.*",]   
#Ҫ�������������ļ�

options = {
	"py2exe":{
		"compressed": 1, #ѹ��
		"optimize": 2,
		"ascii": 1,
		"includes":includes,
		"excludes":excludes,
		#"bundle_files": 1 #�����ļ������һ��exe�ļ�
    }
}
setup(    
    options = options, #{'py2exe':{'dll_excludes':['MSVCP90.dll']}},     
    zipfile=None,   #������library.zip�ļ�
	windows=[{"script": "QAeroData.py","icon_resources":[(1,"aircraft01.ico")]}]
    #Դ�ļ�������ͼ��
    ) 
