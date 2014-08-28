# -*- mode: python -*-
a = Analysis(['QAeroData.py'],
             pathex=['C:\\Anaconda', 'D:\\Work\\DataMaker\\QAeroData', 'D:\\Work\\DataMaker\\QAeroData'],
             hiddenimports=[],
             hookspath=None,
             runtime_hooks=None)
pyz = PYZ(a.pure)
exe = EXE(pyz,
          a.scripts,
          exclude_binaries=True,
          name='QAeroData.exe',
          debug=False,
          strip=None,
          upx=True,
          console=True )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=None,
               upx=True,
               name='QAeroData')
