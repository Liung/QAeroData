#coding: UTF-8

try:
    import cPickle as pickle
except:
    import pickle
import sys
from PyQt4.QtGui import *
from PyQt4.QtCore import *
import sqlite3
import string


class DrawWing(QWidget):
    def __init__(self, data=[], parent=None):
        super(DrawWing, self).__init__(parent)
        self._data = data

    def setData(self, data):
        self._data = data
        self.update()

    def paintEvent(self, QPaintEvent):
        data = self._data
        paint = QPainter()
        paint.begin(self)
        pen = QPen(Qt.blue,2,Qt.SolidLine)
        pen.setCapStyle(Qt.RoundCap)
        pen.setJoinStyle(Qt.RoundJoin)
        paint.setPen(pen)
        qPolygon = QPolygon()

        rmin = min(self.width(),self.height())
        rmax = max(self.width(),self.height())
        paint.translate((rmax - rmin)/2.,self.height()/2.)
        for x,y in data:
            nx,ny = x*rmin,y*rmin
            #nx,ny = x*self.width(),(y*self.width()+self.height()/2)
            #nnx,nny = (self.width()/2 - (self.width()/2-nx)*0.9),(self.height()/2 - (self.height()/2 - ny)*0.9)
            point = QPoint(nx,ny)
            qPolygon.append(point)
        paint.drawPolygon(qPolygon)
        paint.end()

class WingViewWidget(QDialog):
    def __init__(self,parent=None):
        super(WingViewWidget, self).__init__(parent)

        self._dir = '.'
        self._data = None

        self.lblChangeDB = QLabel(u'选择数据库：')
        self.cbChangeDB = QComboBox()
        self.cbChangeDB.addItems(['WingProfile.db'])
        self.lblFilter = QLabel('Filter:')
        self.txtFilter = QLineEdit()
        self.txtFilter.setMaximumWidth(150)
        spacerItem = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.listWidget = QListWidget()
        self.drawWing = DrawWing()
        self.drawWing.setAutoFillBackground(True)
        palette = self.drawWing.palette()
        palette.setColor(QPalette.Window,Qt.white)
        self.drawWing.setPalette(palette)

        self.layout1 = QHBoxLayout()
        self.layout1.addWidget(self.lblChangeDB)
        self.layout1.addWidget(self.cbChangeDB)
        self.layout1.addWidget(self.lblFilter)
        self.layout1.addWidget(self.txtFilter)
        self.layout1.addSpacerItem(spacerItem)

        self.layout2 = QHBoxLayout()
        self.layout2.addWidget(self.listWidget,0)
        self.layout2.addWidget(self.drawWing,1)

        self.mainLayout = QVBoxLayout()
        self.mainLayout.addLayout(self.layout1,)
        self.mainLayout.addLayout(self.layout2)

        self.setLayout(self.mainLayout)


        self.actionExportTxt = QAction('Export as file(.txt)',None)
        self.actionExportDat = QAction('Export as file(.dat)',None)
        self.actionExportDwg = QAction('Export as file(.dwg)',None)
        self.actionExportDxf = QAction('Export as file(.dxf)',None)
        self.actionExportImg = QAction('Export as Img',None)

        self.actionExportTxt.triggered.connect(self.slotExportTxt)
        self.actionExportDat.triggered.connect(self.slotExportDat)
        self.actionExportDwg.triggered.connect(self.slotExportDwg)
        self.actionExportDxf.triggered.connect(self.slotExportDxf)
        self.listWidget.addActions([self.actionExportTxt,self.actionExportDat,
                                    self.actionExportDwg,self.actionExportDxf])
        self.listWidget.setContextMenuPolicy(Qt.ActionsContextMenu)

        self.actionExportImg.triggered.connect(self.slotExportImg)
        self.drawWing.addActions([self.actionExportImg])
        self.drawWing.setContextMenuPolicy(Qt.ActionsContextMenu)


        self.connect(self.cbChangeDB,SIGNAL('currentIndexChanged(QString)'),self.onLoadWingDB)
        self.listWidget.currentItemChanged.connect(self.onDrawWing)
        self.txtFilter.textChanged.connect(self.onFilter)

        self.initListWidget()
        self.setWindowTitle(u'翼型管理器')
        self.resize(800,500)

    def initListWidget(self):
        li = self.getAllFromTable()
        nameList = [item[0] for item in li]
        self._data = nameList
        self.listWidget.addItems(nameList)

    def onFilter(self):

        text = str(self.txtFilter.text())
        text = string.capitalize(text)
        if text:
            self.listWidget.clear()
            for item in self._data:
                capItem = string.capitalize(item)
                idList = []
                for word in text:
                    if word.strip():#如果word为非空字符
                        id = capItem.find(word)
                        idList.append(id)
                        capItem = capItem[id+1:]
                if idList and not (-1 in idList) and (idList == sorted(idList)):
                    self.listWidget.addItem(item)
        else:
            self.listWidget.addItems(self._data)



    def onLoadWingDB(self,text):
        with sqlite3.connect(str(text)) as conn:
            cur = conn.cursor()
            cur.execute("select name,data from wingProfile")
            li = cur.fetchall()
            cur.close()
            nameList = [item[0] for item in li]
            self.listWidget.addItems(nameList)
        self.onDrawWing()

    def onDrawWing(self):
        item = self.listWidget.currentItem()
        if item:
            name = unicode(self.listWidget.currentItem().text())
        else:
            return
        data = self.getDataByName(name)
        if data:
            self.drawWing.setData(data)

    def slotExportTxt(self):
        fname = self.listWidget.currentItem().text()
        dlg = QFileDialog.getSaveFileName(self,u'保存为...',directory = fname,
                                          filter = u"文本文件(*.txt)")
        dlg = unicode(dlg)
        if dlg:
            try:
                with open(dlg,'w') as f:
                    name = unicode(self.listWidget.currentItem().text())
                    data = self.getDataByName(name)
                    f.write(name)
                    f.write('\n')
                    for x,y in data:
                        f.write('%f\t%f\n' % (x,y))
                QMessageBox.information(self,'',u'保存成功！')
            except:
                QMessageBox.information(self,'',u'保存失败')

    def slotExportDat(self):
        fname = self.listWidget.currentItem().text()
        dlg = QFileDialog.getSaveFileName(self,u'保存为...',directory = fname,
                                          filter = u"数据文件(*.dat)")
        dlg = unicode(dlg)
        if dlg:
            try:
                with open(dlg,'w') as f:
                    name = unicode(self.listWidget.currentItem().text())
                    data = self.getDataByName(name)
                    f.write(name)
                    f.write('\n')
                    for x,y in data:
                        f.write('%f\t%f\n' % (x,y))
                QMessageBox.information(self,'',u'保存成功！')
            except:
                QMessageBox.information(self,'',u'保存失败')

    def slotExportDwg(self):
        pass

    def slotExportDxf(self):
        pass

    def slotExportImg(self):
        name = unicode(self.listWidget.currentItem().text())
        data = self.getDataByName(name)
        dlg = QFileDialog.getSaveFileName(self,u'保存为...',directory = name,
                                          filter = u"数据文件(*.png)")
        dlg = unicode(dlg)
        if dlg:
            w,h = self.drawWing.width(),self.drawWing.height()
            img = QImage(w,h,QImage.Format_RGB32)
            try:
                paint = QPainter()
                paint.begin(img)
                pen = QPen(Qt.blue,2,Qt.SolidLine)
                pen.setCapStyle(Qt.RoundCap)
                pen.setJoinStyle(Qt.RoundJoin)
                paint.setPen(pen)
                qPolygon = QPolygon()

                rmin,rmax = min(w,h),max(w,h)
                paint.translate((rmax - rmin)/2.,w/2.)
                for x,y in data:
                    nx,ny = x*rmin,y*rmin
                    #nx,ny = x*self.width(),(y*self.width()+self.height()/2)
                    #nnx,nny = (self.width()/2 - (self.width()/2-nx)*0.9),(self.height()/2 - (self.height()/2 - ny)*0.9)
                    point = QPoint(nx,ny)
                    qPolygon.append(point)
                paint.drawPolygon(qPolygon)
                paint.end()

                img.save(dlg)
                QMessageBox.information(self,'',u'存储成功！')
            except:
                QMessageBox.information(self,'',u'存储失败！')


    def getAllFromTable(self):
        db = str(self.cbChangeDB.currentText())
        with sqlite3.connect(db) as conn:
            cur = conn.cursor()
            cur.execute("select name,data from wingProfile")
            li = cur.fetchall()
            cur.close()
        return li

    def getDataByName(self,name):
        db = str(self.cbChangeDB.currentText())
        with sqlite3.connect(db) as conn:
            cur = conn.cursor()
            cur.execute("select data from wingProfile where name = ?",[name])
            li = cur.fetchone()
            cur.close()
            if li:
                data = pickle.loads(str(li[0]))
            else:
                return None

        return data


if __name__ == '__main__':
    app = QApplication(sys.argv)
    frame = WingViewWidget()
    frame.show()
    sys.exit(app.exec_())
