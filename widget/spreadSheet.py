# -*-coding: utf-8 -*-
__author__ = 'LC'
__appname__ = 'QAeroData'

from PyQt4.QtGui import *
from PyQt4.QtCore import *

import string
import codecs


class SpreadSheet(QTableWidget):

    NextId = 1

    def __init__(self, filename=QString(), parent=None):
        super(SpreadSheet, self).__init__(parent)

        self.setAttribute(Qt.WA_DeleteOnClose)

        self.setAlternatingRowColors(True)
        self.setRowCount(100)
        self.setColumnCount(len(string.uppercase))
        self.setHorizontalHeaderLabels(string.uppercase)

        self._modified = False
        self._isNewFile = False

        self.filename = QString(filename)
        if self.filename.isEmpty():
            self.filename = QString("Unnamed-{0}.txt".format(SpreadSheet.NextId))
            SpreadSheet.NextId += 1
            self._modified = False
            self._isNewFile = True

        self.setWindowTitle(QFileInfo(self.filename).fileName())

        self.itemChanged.connect(self.setModified)

        self.actionEditCopy = self.createAction(u"复制(&Copy)", self.copy,
                                           QKeySequence.Copy, "edit-copy", u"复制文本到粘贴板")

        self.actionEditCut = self.createAction(u"剪切(&Cut)", self.cut,
                                          QKeySequence.Cut, "edit-cut", u"剪切文本到粘贴板")
        self.actionEditPaste = self.createAction(u"粘贴(&Paste)", self.paste,
                                            QKeySequence.Paste, "edit-paste", u"从粘贴板中粘贴文本")
        self.setContextMenuPolicy(Qt.ActionsContextMenu)
        self.addActions((self.actionEditCopy,
                         self.actionEditPaste,
                         self.actionEditCut))

    def sizeHint(self):
        return QSize(800, 600)

    def closeEvent(self, event):
        if self._modified and QMessageBox.question(self,
                                                   u"{0} -- Unsaved Changes".format(__appname__),
                                                   u"文件{0}内容已经发生变化，是否要保存已做的修改？".format(self.filename),
                                                   QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
            try:
                self.save()
            except (IOError, OSError), err:
                QMessageBox.warning(self, u"{0} -- Save Error".format(__appname__),
                                    u"Failed to save {0}:{1}".format(unicode(self.filename), err))

    def isModified(self):

        return self._modified

    def setModified(self):
        # self.setWindowTitle('*' + self.windowTitle())
        self._modified = True

    def save(self):
        with open(unicode(self.filename), mode='w') as f:
            rows, columns = self.rowCount(), self.columnCount()
            headers = [unicode(self.horizontalHeaderItem(i).text())
                       for i in range(columns)]
            try:
                headersLine = '\t'.join(headers).encode('utf-8')
            except:
                headersLine = '\t'.join(headers).encode('gbk2312')
            f.write(headersLine + '\n')
            for row in xrange(rows):
                dataLine = []
                for column in xrange(columns):
                    item = self.item(row, column)
                    if item is not None:
                        dataLine.append(unicode(item.text()))
                    else:
                        dataLine.append('unKnown')
                dataStr = '\t'.join(dataLine)
                f.write(dataStr + '\n')

    def load(self):
        try:
            with codecs.open(unicode(self.filename), encoding="utf-8") as f:
                headers = f.readline().split()
                data = []
                line = f.readline()
                while line:
                    data.append(line.split())
                    line = f.readline()
                self.loadHeaderAndData(headers, data)
                self._modified = False
        except UnicodeDecodeError:
            try:
                with codecs.open(unicode(self.filename), encoding="cp936") as f:
                    headers = f.readline().split()
                    data = []
                    line = f.readline()
                    while line:
                        data.append(line.split())
                        line = f.readline()
                    self.loadHeaderAndData(headers, data)
                    self._modified = False
            except:
                raise IOError
        except OSError:
            return OSError

    def copy(self):
        select_range = self.selectedRange()

        text_str = ''
        for i in xrange(select_range.rowCount()):
            if i > 0:
                text_str += '\n'
            for j in xrange(select_range.columnCount()):
                if j > 0:
                    text_str += '\t'
                try:
                    text_str += self.item(select_range.topRow() + i, select_range.leftColumn() + j).text()
                except AttributeError:
                    text_str += ''

        QApplication.clipboard().setText(text_str)

    def paste(self):
        select_range = self.selectedRange()
        paste_str = QApplication.clipboard().text()

        rows = paste_str.split('\n')
        numRows = rows.count()
        numColumns = rows.first().count('\t') + 1

        if (select_range.topRow() + numRows) > self.rowCount() or \
                (select_range.leftColumn() + numColumns) > self.columnCount():
            # 如果要粘贴的文本内容超出表格范围，则返回
            QMessageBox.information(self, __appname__, u"粘贴失败！\n粘贴内容超过表格范围")
            return

        for i in range(numRows):
            select_cols = rows[i].split('\t')
            for j in range(numColumns):
                row = select_range.topRow() + i
                column = select_range.leftColumn() + j
                self.setItem(row, column, QTableWidgetItem(select_cols[j]))

    def delete(self):
        select_items = self.selectedItems()     # type(select_items) = list
        if select_items:
            for item in select_items:
                item.setText('')

    def cut(self):
        self.copy()
        self.delete()

    def selectedRange(self):
        ranges = self.selectedRanges()    # type(ranges) = list
        if not ranges:
            return QTableWidgetSelectionRange()
        return ranges[0]

    def loadHeaderAndData(self, headers, data):
        rows, columns = len(data), len(headers)
        self.setRowCount(rows)
        self.setColumnCount(columns)
        self.setHorizontalHeaderLabels(headers)
        for row in xrange(rows):
            for column in xrange(columns):
                try:
                    text = data[row][column]
                except:
                    text = ""
                item = QTableWidgetItem(text)
                self.setItem(row, column, item)

    def createAction(self, text, slot=None, shortcut=None, icon=None,
                     tip=None, checkable=False):
        action = QAction(text, self)
        if icon is not None:
            action.setIcon(QIcon(":icons/imgs/{0}.png".format(icon)))
        if shortcut is not None:
            action.setShortcut(shortcut)
        if tip is not None:
            action.setToolTip(tip)
            action.setStatusTip(tip)
        if slot is not None:
            action.triggered.connect(slot)
        if checkable:
            action.setCheckable(True)
        return action

if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    spread = SpreadSheet()
    spread.show()
    app.exec_()