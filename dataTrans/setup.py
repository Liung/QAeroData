 #-*- coding: utf-8 -*-
from distutils.core import setup
import py2exe

excludes = []
includes = ["sip", "encodings", "encodings.*", ]    # 要包含的其它库文件

opts = {
    "py2exe": {
        "compressed": 1,                # 压缩
        "optimize": 2,
        "ascii": 1,
        "includes": includes,
        "excludes": excludes,
        "bundle_files": 1,              # 所有文件打包成一个exe文件
        "dll_excludes": ['MSVCP90.dll']
    }
}
data_files = ['G14.csv', 'G16.csv', 'G18.csv', 'Box.csv']
setup(
    version="0.2.0",
    description="Balance data programming",
    author='Liung',
    author_email='lc.chao.liu@gmail.com',
    name="Balance Maker",
    options=opts,
    data_files=data_files,
    zipfile=None,                       # 不生成library.zip文件
    windows=[{
        "script": "dataTransMain.py",
        "icon_resources": [(1, "airplane.ico")],    # 源文件，程序图标
    }]
)
