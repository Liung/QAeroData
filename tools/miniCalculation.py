# *-.-* coding: UTF-8 *-.-*
__author__ = 'LC'

from PyQt4.QtGui import QApplication, QHBoxLayout, QTextBrowser, \
    QVBoxLayout, QLineEdit,QPushButton, QListWidget, QDialog, \
    QMessageBox
import math
from math import *

class MiniCalculation(QDialog):
    def __init__(self, parent=None):
        super(MiniCalculation, self).__init__(parent)
        self.btnHelpState = False

        self.txtBrower = QTextBrowser()
        self.txtLine = QLineEdit()
        self.txtLine.setPlaceholderText(u"请输入表达式，按回车结束...")

        self.btnCal = QPushButton(u"计算")
        self.btnClear = QPushButton(u"清空")
        self.btnHelp = QPushButton(u"特殊函数表>>")
        self.btnHelp.setCheckable(True)
        self.btnHelp.setChecked(True)

        mathList = [s for s in dir(math) if not s.startswith("__")]
        self.listWidget = QListWidget()
        self.listWidget.addItems(mathList)
        for i in range(len(mathList)):
            item = self.listWidget.item(i)
            strFun = item.text() + '.__doc__'
            item.setToolTip(eval(str(strFun)))
        self.listWidget.setMaximumWidth(100)

        midLay = QHBoxLayout()
        midLay.addWidget(self.btnCal)
        midLay.addWidget(self.btnClear)
        midLay.addStretch()
        midLay.addWidget(self.btnHelp)

        bottomLay = QHBoxLayout()
        bottomLay.addWidget(self.txtBrower)
        bottomLay.addWidget(self.listWidget)

        lay = QVBoxLayout()
        lay.addWidget(self.txtLine)
        lay.addItem(midLay)
        lay.addItem(bottomLay)

        self.resize(450, 300)
        self.setLayout(lay)
        self.updateUI()

        self.btnCal.clicked.connect(self.btnCalClicked)
        self.btnClear.clicked.connect(self.txtLine.clear)
        self.btnClear.clicked.connect(self.txtBrower.clear)
        self.btnHelp.clicked.connect(self.updateUI)
        self.listWidget.itemDoubleClicked.connect(self.listItemDoubleClicked)

    def updateUI(self):
        state = not self.btnHelp.isChecked()
        self.listWidget.setHidden(state)
        text = u"特殊函数表>>" if state else u"特殊函数表<<"
        self.btnHelp.setText(text)

    def btnCalClicked(self):
        try:
            txt = str(self.txtLine.text())
            self.txtBrower.append("%s = <b>%s</b>" % (txt, eval(txt)))
        except UnicodeEncodeError:
            QMessageBox.warning(self,u"QData -- 迷你计算机",
                    u"表达式中存在中文或全角字符\n",
                    QMessageBox.Ok)
        except:
            self.txtBrower.append("<font color=red>%s <b>is invalid</b>" % txt)

    def listItemDoubleClicked(self):
        item = self.listWidget.currentItem()
        self.txtLine.insert(item.text())
        self.txtLine.setFocus()

if __name__ == "__main__":
    import sys
    from math import *

    app = QApplication(sys.argv)
    cal = MiniCalculation()
    cal.show()
    app.exec_()
