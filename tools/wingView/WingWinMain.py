from PyQt4.QtCore import *
from PyQt4.QtGui import *
import sys
from wingWin_ui import Ui_Dialog
class WingWidget(QDialog,Ui_Dialog):
    def __init__(self,parent=None):
        super(WingWidget, self).__init__(parent)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    frame = WingWidget()
    frame.show()
    sys.exit(app.exec_())