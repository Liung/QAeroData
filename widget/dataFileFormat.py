# ~*-.-*~ coding: utf-8 -*-
__author__ = 'LC'


from PyQt4.QtGui import QWidget, QCheckBox, QHBoxLayout, QVBoxLayout, QSpinBox, QDialog, QGroupBox, QDialogButtonBox,\
    QApplication
# from PyQt4.QtCore import *


class CheckBoxEdit(QWidget):
    def __init__(self, label='', value=0, parent=None):
        super(CheckBoxEdit, self).__init__(parent)
        self.check = QCheckBox(label)
        self.columnSpin = QSpinBox()
        self.columnSpin.setRange(0, 20)
        self.columnSpin.setValue(value)
        lay = QHBoxLayout()
        lay.addWidget(self.check)
        lay.addWidget(self.columnSpin)
        self.setLayout(lay)

        self.column = 0

        self.columnSpin.setEnabled(False)
        self.check.stateChanged.connect(self.columnSpin.setEnabled)
        self.columnSpin.valueChanged[int].connect(self.setColumn)

    def setColumn(self, column):
        self.column = column


class DataFileFormat(QDialog):
    params = {}
    def __init__(self, parent=None):
        super(DataFileFormat, self).__init__(parent)

        timeGroup = QGroupBox(u"时间列", self)
        self.time = CheckBoxEdit("Time")
        timeLay = QHBoxLayout()
        timeLay.addWidget(self.time)
        timeLay.addStretch()
        timeGroup.setLayout(timeLay)
        angleGroup = QGroupBox(u"角度列")
        self.alpha = CheckBoxEdit(u"α")
        self.beta = CheckBoxEdit(u"β")
        self.theta = CheckBoxEdit(u"θ")
        self.psi = CheckBoxEdit(u"ψ")
        self.phi = CheckBoxEdit(u"φ")
        angleLay = QHBoxLayout()
        angleLay.addWidget(self.alpha)
        angleLay.addWidget(self.beta)
        angleLay.addWidget(self.theta)
        angleLay.addWidget(self.psi)
        angleLay.addWidget(self.phi)
        angleLay.addStretch()
        angleGroup.setLayout(angleLay)
        coeGroup = QGroupBox(u"气动系数列")
        self.cx = CheckBoxEdit("Cx")
        self.cy = CheckBoxEdit("Cy")
        self.cz = CheckBoxEdit("Cz")
        self.cmx = CheckBoxEdit("Cmx")
        self.cmy = CheckBoxEdit("Cmy")
        self.cmz = CheckBoxEdit("Cmz")
        coeLay = QHBoxLayout()
        coeLay.addWidget(self.cx)
        coeLay.addWidget(self.cy)
        coeLay.addWidget(self.cz)
        coeLay.addWidget(self.cmx)
        coeLay.addWidget(self.cmy)
        coeLay.addWidget(self.cmz)
        coeLay.addStretch()
        coeGroup.setLayout(coeLay)

        self.btnBox = QDialogButtonBox(self)
        self.btnBox.addButton(QDialogButtonBox.Reset)
        self.btnBox.addButton(QDialogButtonBox.Ok)
        self.btnBox.addButton(QDialogButtonBox.Apply)
        self.btnBox.addButton(QDialogButtonBox.Cancel)

        mainLay = QVBoxLayout()
        mainLay.addWidget(timeGroup)
        mainLay.addWidget(angleGroup)
        mainLay.addWidget(coeGroup)
        mainLay.addWidget(self.btnBox)
        self.setLayout(mainLay)
        self.setWindowTitle(u'设置文件数据列')

        self.tempParams = {}
        self.updateParams()

        for item in [self.time, self.alpha, self.beta, self.theta,
                     self.psi, self.phi, self.cx, self.cy, self.cz,
                     self.cmx, self.cmy, self.cmz]:
            item.columnSpin.valueChanged.connect(self.updateParams)
        self.btnBox.clicked.connect(self.updateState)

    def updateParams(self):
        for s, item in zip(['time', 'alpha', 'beta', 'theta',
                            'psi', 'phi', 'cx', 'cy', 'cz',
                            'cmx', 'cmy', 'cmz'],
                           [self.time, self.alpha, self.beta,
                            self.theta, self.psi, self.phi,
                            self.cx, self.cy, self.cz,
                            self.cmx, self.cmy, self.cmz]):
            self.tempParams[s] = item.column

    def updateState(self, btn):
        if btn == self.btnBox.button(QDialogButtonBox.Reset):  # 载入之前的文件设定
            for s, item in zip(['time', 'alpha', 'beta', 'theta',
                                'psi', 'phi', 'cx', 'cy', 'cz',
                                'cmx', 'cmy', 'cmz'],
                               [self.time, self.alpha, self.beta,
                                self.theta, self.psi, self.phi,
                                self.cx, self.cy, self.cz,
                                self.cmx, self.cmy, self.cmz]):
                value = DataFileFormat.params.get(s, 0)
                item.columnSpin.setValue(value)
                if value != 0:
                    item.check.setChecked(True)
        if btn == self.btnBox.button(QDialogButtonBox.Ok):
            DataFileFormat.params.update(self.tempParams)
            self.close()
        if btn == self.btnBox.button(QDialogButtonBox.Cancel):
            self.close()
        if btn == self.btnBox.button(QDialogButtonBox.Apply):
            DataFileFormat.params.update(self.tempParams)


if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    f = DataFileFormat()
    f.show()
    app.exec_()