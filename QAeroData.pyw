#coding: UTF-8

import platform
import sys

from PyQt4.QtGui import *
from PyQt4.QtCore import *

from dataDynRigTrans import dataDynRigTransMain
from dataTrans import DataTransWidget
from tools.wingView import WingViewWin
from tools import miniCalculation, QPicConvertor, img2gifWidget, Tetris
from dataFilter import dataFilterMain, dataFilterBatchMain
from widget import MatplotlibWidget, DirectoryViewer, SpreadSheet

import qrc_resources

__version__ = '1.0.0'
__author__ = 'liuchao'
__appname__ = 'QAeroData'


class MainWindow(QMainWindow):

    def __init__(self):
        super(MainWindow, self).__init__()

        self.currentPath = QDir.currentPath()
        self.initUI()
        self.initActions()
        self.loadSettings()
        self.updateWindowMenu()
        self.updateEditMenu()
        self.setWindowTitle(__appname__)
        self.setIconSize(QSize(32, 32))
        QTimer.singleShot(0, self.loadFiles)

        # 设置主应用程序可拖拽
        self.setAcceptDrops(True)

        self.xAxisData = []
        self.yAxisData = []
        #
        # # initUI's elements
        # self.mdi = None
        # self.treeView = None
        # self.treeModel = None
        # self.dockWidgetFileManager = None
        # self.plotWidget = None
        # self.docWidgetPlot = None
        #
        # # initActions' elements
        # self.actionFileManager = None
        # self.actionWindowNext = None
        # self.actionWindowPrev = None
        # self.actionWindowCascade = None
        # self.actionWindowTile = None
        # self.actionWindowMinimize = None
        # self.actionWindowRestore = None
        # self.actionWindowClose = None
        # self.actionWindowCloseAll = None
        # self.actionWindowSubView = None
        # self.actionWindowTabbedView = None
        # self.windowMapper = None
        # self.menuWindow = None

    def initUI(self):

        self.mdi = QMdiArea()
        self.mdi.setTabsMovable(True)
        self.mdi.setTabsClosable(True)
        self.mdi.setContextMenuPolicy(Qt.ActionsContextMenu)
        self.setCentralWidget(self.mdi)

        self.treeView = DirectoryViewer()
        self.treeModel = self.treeView.model
        self.dockWidgetFileManager = QDockWidget()
        self.dockWidgetFileManager.setWindowTitle(u"文件管理器")
        self.dockWidgetFileManager.setObjectName(u"文件管理器")
        self.dockWidgetFileManager.setWidget(self.treeView)
        self.treeView.treeView.doubleClicked[QModelIndex].connect(self.treeViewDoubleClicked)

        self.plotWidget = MatplotlibWidget()
        self.docWidgetPlot = QDockWidget()
        self.docWidgetPlot.setWindowTitle(u"Plot")
        self.docWidgetPlot.setObjectName(u"MatplotlibPlot")
        self.docWidgetPlot.setWidget(self.plotWidget)

        self.addDockWidget(Qt.RightDockWidgetArea, self.docWidgetPlot)
        self.addDockWidget(Qt.RightDockWidgetArea, self.dockWidgetFileManager)
        self.statusBar().showMessage(u"Copyright: 南京航空航天大学 航空宇航学院 史志伟课题组", 5000)

    def initActions(self):
        # File menu and toolbar
        actionFileNew = self.createAction(u"新建(&New)", self.fileNew,
                                          QKeySequence.New, "document-new", u"新建文件")
        actionFileOpen = self.createAction(u"打开(&Open)", self.fileOpen,
                                           QKeySequence.Open, "document-open",u"打开文件")
        actionFileSave = self.createAction(u"保存(&Save)", self.fileSave,
                                           QKeySequence.Save, "document-save", u"保存文件")
        actionFileSaveAs = self.createAction(u"另存为...(&Save as...)",
                                             self.fileSaveAs, "Ctrl+Shift+S", "document-save-as",
                                             u"文件另存为...")
        actionFileSaveAll = self.createAction(u"全部保存(Save A&ll)",
                                              self.fileSaveAll, None, "document-save-all", u"全部保存文件")
        actionQuit = self.createAction(u"退出(&Quit)", self.close,
                                       "Ctrl+Q", "app-exit", u"退出程序")

        menuFile = self.menuBar().addMenu(u"文件(&F)")
        self.addActions(menuFile, (actionFileNew, actionFileOpen,
                                   actionFileSave, actionFileSaveAs, actionFileSaveAll,
                                   None, actionQuit))

        toolbarFile = self.addToolBar(u"文件")
        toolbarFile.setObjectName(u"文件")
        self.addActions(toolbarFile, (actionFileNew, actionFileOpen,
                                      actionFileSave))

        self.mdi.addActions((actionFileNew, actionFileOpen))

        #Edit menu and toolbar
        self.actionEditCopy = self.createAction(u"复制(&Copy)", icon="edit-copy")
        self.actionEditCut = self.createAction(u"剪切(&Cut)", icon="edit-cut")
        self.actionEditPaste = self.createAction(u"粘贴(&Paste)", icon="edit-paste")
        self.actionEditCopy.setEnabled(False)
        self.actionEditCut.setEnabled(False)
        self.actionEditPaste.setEnabled(False)
        menuEdit = self.menuBar().addMenu(u"编辑(&E)")
        self.addActions(menuEdit, (self.actionEditCopy, self.actionEditCut,
                                   self.actionEditPaste))

        toolbarEdit = self.addToolBar(u"编辑")
        toolbarEdit.setObjectName(u"编辑")
        self.addActions(toolbarEdit, (self.actionEditCopy, self.actionEditCut,
                                      self.actionEditPaste))

        self.mdi.addActions((self.actionEditCopy, self.actionEditCut, self.actionEditPaste))

        #view menu and toolbar
        actionToolbarFile = toolbarFile.toggleViewAction()
        actionToolbarEdit = toolbarEdit.toggleViewAction()
        self.actionFileManager = self.dockWidgetFileManager.toggleViewAction()
        self.actionFileManager.setText(u"文件管理器")
        menuView = self.menuBar().addMenu(u"&View")
        # the view's "self.addActions()" Function is the end of this scope..0-0..

        #Balance menu and toolbar
        menuBalanceSys = self.menuBar().addMenu(u"天平数据(&B)")
        actionBalanceTrans = self.createAction(u"天平数据转换", self.balanceTrans)

        self.addActions(menuBalanceSys, (actionBalanceTrans, ))

        #dynamic rig menu and toolbar
        actionDynRigParamsSetting = self.createAction(u"动平台参数设置", self.dynrigParamsSetting)
        actionFileFilterSingle = self.createAction(u"单文件滤波", self.fileFilterSingle)
        actionFileFilterBatch = self.createAction(u"多文件滤波", self.fileFilterBatch)
        actionDynRigDataManu = self.createAction(u"动平台数据处理", self.dynrigDataManu)

        menuDynRig = self.menuBar().addMenu(u"动态机构(&D)")
        self.addActions(menuDynRig, (actionDynRigParamsSetting, ))
        menuFileFilter = menuDynRig.addMenu(u"文件滤波")
        self.addActions(menuFileFilter, (actionFileFilterSingle,
                                         actionFileFilterBatch))
        self.addActions(menuDynRig, (actionDynRigDataManu, ))

        #tools menu and toolbar
        actionToolsMiniCalculator = self.createAction(u"迷你计算器", self.toolsMiniCalculator,
                                                      icon="calculator00", tip=u"功能强大的迷你计算器")
        actionToolsWingManager = self.createAction(u"翼型管理器", self.toolsWingManager,
                                                   icon="WingManager", tip=u"多种翼型库管理工具")
        actionToolsPicConvertor = self.createAction(u"图像格式转换", self.toolsPicConvertor,
                                                    tip=u"支持多种图片文件的格式转换和大小转换")
        actionToolsImg2Gif = self.createAction(u"Gif生成器", self.toolsImg2Gif,
                                               tip=u"快速生成简单GIF动画文件")
        actionToolsTetris = self.createAction(u"Tetris", self.toolsTetris,
                                              tip=u"super Funny - 0.0")

        menuTools = self.menuBar().addMenu(u"工具(&T)")
        self.addActions(menuTools, (actionToolsMiniCalculator,
                                    actionToolsWingManager, actionToolsPicConvertor,
                                    actionToolsImg2Gif, actionToolsTetris))
        toolbarTools = self.addToolBar(u"工具")
        toolbarTools.setObjectName(u"工具")
        self.addActions(toolbarTools, (actionToolsMiniCalculator,
                                       actionToolsWingManager))

        #Window menu and toolbar
        self.actionWindowNext = self.createAction(u"下一个窗口(&Next)",
                                                  self.mdi.activateNextSubWindow, QKeySequence.NextChild)
        self.actionWindowPrev = self.createAction(u"上一个窗口(&Previous)",
                                                  self.mdi.activatePreviousSubWindow, QKeySequence.PreviousChild)
        self.actionWindowCascade = self.createAction(u"层叠(Casca&de)",
                                                     self.mdi.cascadeSubWindows)
        self.actionWindowTile = self.createAction(u"平铺(&Tile)",
                                                  self.mdi.tileSubWindows)
        self.actionWindowMinimize = self.createAction(u"最小化所有窗口(&Iconize All)",
                                                      self.windowMinimizeAll)
        self.actionWindowRestore = self.createAction(u"还原所有窗口(&Restore All)",
                                                     self.windowRestoreAll)
        self.actionWindowClose = self.createAction(u"关闭当前窗口(&Close)",
                                                   self.mdi.closeActiveSubWindow, QKeySequence.Close)
        self.actionWindowCloseAll = self.createAction(u"关闭所有窗口(Close a&ll)",
                                                      self.mdi.closeAllSubWindows, "Ctrl+Shift+F4")
        self.actionWindowSubView = self.createAction(u"子窗口形式(&S)",
                                                     self.windowSubWindowView, checkable=True)
        self.actionWindowTabbedView = self.createAction(u"标签形式(&b)",
                                                        self.windowTabbedView, checkable=True)
        self.actionWindowSubView.setChecked(True)

        self.windowMapper = QSignalMapper(self)
        self.windowMapper.mapped[QWidget].connect(self.mdi.setActiveSubWindow)

        self.menuWindow = self.menuBar().addMenu(u"窗口(&W)")
        self.menuWindow.aboutToShow.connect(self.updateWindowMenu)

        #about menu and toolbar
        actionAbout = self.createAction(u"About {0}".format(__appname__), self.showAbout)
        # actionAboutQt = self.createAction(u"About Qt", qApp.aboutQt())
        menuAbout = self.menuBar().addMenu(u"关于(&A)")
        self.addActions(menuAbout, (actionAbout,
                                    # actionAboutQt,
                                    ))

        #view menu and toolbar
        actionToolbarTools = toolbarTools.toggleViewAction()
        actionMatplotlibWidget = self.docWidgetPlot.toggleViewAction()
        self.addActions(menuView, (actionToolbarFile, actionToolbarEdit,
                                   actionToolbarTools, None,
                                   self.actionFileManager, actionMatplotlibWidget))

        #右键菜单plot命令：Set X， Set Y
        actionPlot = self.createAction("Plot", self.dataPlot)
        actionSetX = self.createAction("Set X", self.setXAxisData)
        actionSetY = self.createAction("Set Y", self.setYAxisData)
        self.mdi.addActions((actionPlot, actionSetX, actionSetY))

    def loadSettings(self):
        settings = QSettings()
        self.restoreGeometry(settings.value("MainWindow/Geometry").toByteArray())
        self.restoreState(settings.value("MainWindow/State").toByteArray())

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

    def addActions(self, target, actions):
        for action in actions:
            if action is None:
                target.addSeparator()
            else:
                target.addAction(action)

    def dragEnterEvent(self, event):
        if event.mimeData().hasFormat("text/uri-list"):

            # 主程序默认不接受拖入请求，设置接受
            event.acceptProposedAction()

    def dropEvent(self, event):
        urls = event.mimeData().urls()  # the type of urls is PyQt4.QtCore.Urls
        if not urls:
            return
        for fileName_urls in urls:
            fileName = fileName_urls.toLocalFile()    # fileName's type is QString
            if fileName.isEmpty():
                return

            # 加载文件
            self.loadFile(fileName)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._startMousePressPos = event.pos()

    # def mouseMoveEvent(self, event):
    #     if (event.buttons() & Qt.LeftButton):
    #         distance = (event.pos() - self._startMousePressPos).manhattanLength()
    #         if (distance >= QApplication.startDragDistance()):
    #             drag = QDrag(self)
    #             drag.setMimeData(event.mimeData)
    #             drag.setPixmap(QPixmap(":icons/imgs/document-file.png"))
    #             drag.exec_(Qt.MoveAction)

    def closeEvent(self, event):
        failures = []
        for subWindow in self.mdi.subWindowList():
            spreadSheet = subWindow.widget()
            if spreadSheet.isModified():
                try:
                    spreadSheet.save()
                except IOError, err:
                    failures.append(unicode(err))
        if (failures and QMessageBox.warning(self,
                                             "{0} -- SaveError".format(__appname__),
                                             "Failed to save {0} \n Quit anyway?".format(
                                                     "\n\t".join(failures)),
                                             QMessageBox.Yes | QMessageBox.No) == QMessageBox.No):
            event.ignore()
            return
        self.saveSettings()
        self.mdi.closeAllSubWindows()

    def saveSettings(self):
        settings = QSettings()
        settings.setValue("MainWindow/Geometry",
                          QVariant(self.saveGeometry()))
        settings.setValue("MainWindow/State",
                          QVariant(self.saveState()))
        files = QStringList()
        for subWindow in self.mdi.subWindowList():
            spreadSheet = subWindow.widget()
            files.append(spreadSheet.filename)
        settings.setValue("CurrentFiles", QVariant(files))

    def loadFiles(self):
        if len(sys.argv) > 1:
            for filename in sys.argv[1:31]:
                filename = QString(filename)
                if QFileInfo(filename).isFile():
                    self.loadFile(filename)
                    QApplication.processEvents()
        # 程序开始之后不加载以前文件
        # else:
        #     settings = QSettings()
        #     files = settings.value("CurrentFiles").toStringList()
        #     for filename in files:
        #         filename = QString(filename)
        #         self.loadFile(filename)
        #         QApplication.processEvents()

    def fileNew(self):
        spreadSheet = SpreadSheet()
        self.mdi.addSubWindow(spreadSheet)
        spreadSheet.show()
        self.updateEditMenu()

    def fileOpen(self):
        filename = QFileDialog.getOpenFileName(self,
                                               "{0} -- Open Files".format(__appname__),
                                               self.currentPath)
        if not filename.isEmpty():
            loaded = False   # judge the file have loaded
            for subWindow in self.mdi.subWindowList():
                spreadSheet = subWindow.widget()
                if spreadSheet.filename == filename:
                    self.mdi.setActiveSubWindow(subWindow)
                    loaded = True
                    break
            if not loaded:
                self.currentPath = filename
                self.loadFile(filename)

    def loadFile(self, filename):
        spreadSheet = SpreadSheet(filename)
        try:
            spreadSheet.load()
        except (UnicodeDecodeError, IOError, OSError), err:
            QMessageBox.warning(self, "{0} -- Load Error".format(__appname__),
                                "Failed to load {0}\n{1}".format(filename, err))
            spreadSheet.close()
            del spreadSheet
        else:
            self.mdi.addSubWindow(spreadSheet)
            spreadSheet.show()
            self.updateEditMenu()

    def fileSave(self):
        subWindow = self.mdi.activeSubWindow()
        spreadSheet = subWindow.widget() if subWindow is not None else None
        if spreadSheet is None or not isinstance(spreadSheet, QTableWidget):
            return True
        if spreadSheet.isNewFile:
            return self.fileSaveAs()
        try:
            spreadSheet.save()
            QMessageBox.about(self, u"{0} -- save succeed".format(__appname__),
                              u"Succeed to save {0}".format(spreadSheet.filename))
            return True
        except (IOError, OSError), err:
            QMessageBox.warning(self, u"{0} -- Save Error".format(__appname__),
                                u"Failed to save {0}: \n{1}".format(spreadSheet.filename, err))
            return False

    def fileSaveAs(self):
        subWindow = self.mdi.activeSubWindow()
        spreadSheet = subWindow.widget() if subWindow is not None else None
        if spreadSheet is None or not isinstance(spreadSheet, QTableWidget):
            return
        filename = QFileDialog.getSaveFileName(self,
                                               u"{0} -- Save File As".format(__appname__),
                                               self.currentPath, "Text files(*.txt *.dat *.*)")
        if not filename.isEmpty():
            self.currentPath = filename
            spreadSheet.filename = filename
            spreadSheet.isNewFile = False
            return self.fileSave()
        return True

    def fileSaveAll(self):
        errors = []
        for subWindow in self.mdi.subWindowList():
            spreadSheet = subWindow.widget()
            if spreadSheet.isModified():
                try:
                    spreadSheet.save()
                except (IOError, OSError), err:
                    errors.append(u"{0}: {1}".format(spreadSheet.filename, err))
            if errors:
                QMessageBox.warning(self,
                                    u"{0} -- Save All Error".format(__appname__),
                                    u"Failed to save \n{0}".format("\n".join(errors)))

    def editCopy(self):
        subWindow = self.mdi.activeSubWindow()
        spreadSheet = subWindow.widget() if subWindow is not None else None
        if spreadSheet is None or not isinstance(spreadSheet, QTableWidget):
            return
        items = spreadSheet.selectedItems()
        if len(items) == 0:
            return
        text = None
        start_column = spreadSheet.column(items[0])
        for item in items:
            now_column = spreadSheet.column(item)
            if now_column == start_column:
                if not text:
                    text = item.text()
                else:
                    text = text + '\t' + item.text()
            else:
                start_column = now_column
                text = text + '\n' + item.text()
        if not text.isEmpty():
            clipboard = QApplication.clipboard()
            clipboard.setText(text)

    def editCut(self):
        subWindow = self.mdi.activeSubWindow()
        spreadSheet = subWindow.widget() if subWindow is not None else None
        if spreadSheet is None or not isinstance(spreadSheet, QTableWidget):
            return
        items = spreadSheet.selectedItems()
        if len(items) == 0:
            return
        text = None
        start_column = spreadSheet.column(items[0])
        for item in items:
            now_column = spreadSheet.column(item)
            if now_column == start_column:
                if not text:
                    text = item.text()
                else:
                    text = text + '\t' + item.text()
                item.setText(u"")
            else:
                start_column = now_column
                text = text + '\n' + item.text()
            item.setText(u"")
        if not text.isEmpty():
            clipboard = QApplication.clipboard()
            clipboard.setText(text)

    def editPaste(self):
        subWindow = self.mdi.activeSubWindow()
        spreadSheet = subWindow.widget() if subWindow is not None else None
        if spreadSheet is None or not isinstance(spreadSheet, QTableWidget):
            return
        items = spreadSheet.selectedItems()
        if len(items) == 0:
            return
        text = QApplication.clipboard().text()
        try:
            data = text.split('\n')
            columns = len(data)
            rows = len(data[0].split('\t'))
            start_item = items[0]
            start_row = start_item.row()
            start_column = start_item.column()
            for column in xrange(columns):
                for row in xrange(rows):
                    text = data[column].split('\t')[row]
                    now_column = start_column + column
                    now_row = start_row + row
                    item = spreadSheet.item(now_row, now_column)
                    item.setText(text)
        except Exception, msg:
            QMessageBox.information(self, u"{0} -- paste".format(__appname__),
                                    u"Failed to paste\n{0}".format(msg))

    def treeViewDoubleClicked(self, index):
        filename = QFileSystemModel.filePath(self.treeModel, index)
        if QFileInfo(filename).isFile() and \
                (filename.toLower().endsWith(".dat") or
                 filename.toLower().endsWith(".txt")):
            loaded = False
            for subWindow in self.mdi.subWindowList():
                spreadSheet = subWindow.widget()
                if spreadSheet.filename == filename:
                    self.mdi.setActiveSubWindow(subWindow)
                    loaded = True
                    break
            if not loaded:
                self.loadFile(filename)

    def balanceTrans(self):
        bt = DataTransWidget(self)
        bt.show()

    def dynrigParamsSetting(self):
        pass

    def fileFilterSingle(self):
        ffs = dataFilterMain.DataFilterWidget(self)
        ffs.show()

    def fileFilterBatch(self):
        ffb = dataFilterBatchMain.DataFilterBatchWidget(self)
        ffb.show()

    def dynrigDataManu(self):
        dt = dataDynRigTransMain.DataDynRigTransWidget(self)
        dt.show()

    def toolsMiniCalculator(self):
        miniCal = miniCalculation.MiniCalculation(self)
        miniCal.show()

    def toolsWingManager(self):
        wingWin = WingViewWin.WingViewWidget(self)
        wingWin.show()

    def toolsPicConvertor(self):
        pcon = QPicConvertor.PicConvertor(self)
        pcon.show()

    def toolsImg2Gif(self):
        i2g = img2gifWidget.Img2GifWidget(self)
        i2g.show()

    def toolsTetris(self):
        tetris = Tetris.Tetris(self)
        tetris.show()

    def windowRestoreAll(self):
        for subWindow in self.mdi.subWindowList():
            subWindow.showNormal()

    def windowMinimizeAll(self):
        for subWindow in self.mdi.subWindowList():
            subWindow.showMinimized()

    def windowSubWindowView(self):
        self.actionWindowSubView.setChecked(True)
        self.actionWindowTabbedView.setChecked(False)
        self.mdi.setViewMode(QMdiArea.SubWindowView)

    def windowTabbedView(self):
        self.actionWindowSubView.setChecked(False)
        self.actionWindowTabbedView.setChecked(True)
        self.mdi.setViewMode(QMdiArea.TabbedView)

    def dataPlot(self):
        subWindow = self.mdi.activeSubWindow()
        spreadSheet = subWindow.widget() if subWindow is not None else None
        if spreadSheet is None or not isinstance(spreadSheet, QTableWidget):
            return
        items = spreadSheet.selectedItems()
        if len(items) == 0:
            return
        x = []
        start_column = spreadSheet.column(items[0])
        rows = spreadSheet.rowCount()
        for row in xrange(rows):
            item = spreadSheet.item(row, start_column)
            num, state = item.text().toDouble()
            if not state:
                num = 0
            x.append(num)
        self.plotWidget.canvas.axes.cla()
        self.plotWidget.plot(range(len(x)), x)
        self.plotWidget.canvas.draw()

    def setXAxisData(self):
        subWindow = self.mdi.activeSubWindow()
        spreadSheet = subWindow.widget() if subWindow is not None else None
        if spreadSheet is None or not isinstance(spreadSheet, QTableWidget):
            return
        items = spreadSheet.selectedItems()
        if len(items) == 0:
            return
        start_column = spreadSheet.column(items[0])
        rows = spreadSheet.rowCount()
        self.xAxisData = []
        for row in xrange(rows):
            item = spreadSheet.item(row, start_column)
            num, state = item.text().toDouble()
            if not state:
                num = 0
            self.xAxisData.append(num)
        m, n = len(self.xAxisData), len(self.yAxisData)
        if self.xAxisData and self.yAxisData and m == n:
            self.plotWidget.canvas.axes.cla()
            self.plotWidget.plot(self.xAxisData, self.yAxisData)
            self.plotWidget.canvas.draw()

    def setYAxisData(self):
        subWindow = self.mdi.activeSubWindow()
        spreadSheet = subWindow.widget() if subWindow is not None else None
        if spreadSheet is None or not isinstance(spreadSheet, QTableWidget):
            return
        items = spreadSheet.selectedItems()
        if len(items) == 0:
            return
        selectedRanges = spreadSheet.selectedRanges()
        selectedColumnsList = []
        for selectedRange in selectedRanges:
            for column in xrange(selectedRange.columnCount()):
                selectedColumnsList.append(selectedRange.leftColumn() + column)
        selectedColumnsList = list(set(selectedColumnsList))
        rows = spreadSheet.rowCount()
        self.yAxisData = []
        for column in selectedColumnsList:
            columnData = []
            for row in xrange(rows):
                item = spreadSheet.item(row, column)
                num, state = item.text().toDouble()
                if not state:
                    num = 0
                columnData.append(num)
            self.yAxisData.append(columnData)
        if self.xAxisData and self.yAxisData:
            self.plotWidget.canvas.axes.cla()
            xRows = len(self.xAxisData)
            for ydata in self.yAxisData:
                yRows = len(ydata)
                if xRows == yRows:
                    self.plotWidget.plot(self.xAxisData, ydata)
                    self.plotWidget.canvas.draw()

    def updateWindowMenu(self):
        self.menuWindow.clear()
        self.addActions(self.menuWindow, (self.actionWindowNext,
                                          self.actionWindowPrev, None, self.actionWindowCascade,
                                          self.actionWindowTile, None, self.actionWindowMinimize,
                                          self.actionWindowRestore, None,
                                          self.actionWindowSubView, self.actionWindowTabbedView,
                                          None, self.actionWindowClose, self.actionWindowCloseAll))
        subWindows = self.mdi.subWindowList()
        if not subWindows:
            return
        self.menuWindow.addSeparator()
        menu = self.menuWindow
        i = 1
        for subWindow in subWindows:
            title = subWindow.windowTitle()
            if i == 10:
                self.menuWindow.addSeparator()
                menu = menu.addMenu("&More")
            accel = ""
            if i < 10:
                accel = "&{0} ".format(i)
            elif i < 36:
                accel = "&{0} ".format(chr(i + ord("@") - 9))
            action = menu.addAction(u"{0}{1}".format(accel, title))
            action.triggered.connect(self.windowMapper.map)
            self.windowMapper.setMapping(action, subWindow)
            i += 1
            
    def updateEditMenu(self):
        subWindows = self.mdi.subWindowList()
        if not subWindows:
            return
        subWindow = self.mdi.currentSubWindow().widget()
        self.actionEditCopy = subWindow.actionEditCopy
        self.actionEditCut = subWindow.actionEditCut
        self.actionEditPaste = subWindow.actionEditPaste
        self.actionEditCopy.setEnabled(True)
        self.actionEditCut.setEnabled(True)
        self.actionEditPaste.setEnabled(True)

    def showAbout(self):
        QMessageBox.about(self, u"About {0}".format(__appname__),
                          u"""<b>%s</b> v %s
        <p>Copyright &copy; 2014 南京航空航天大学 航空宇航学院 史志伟课题组 所有。
        <p>该应用旨在方便对气动实验数据进行处理和简单的展示，以提供友好的GUI界面。
        <hr><p>软件信息:
        <p>本程序使用了：
        <p>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
        Python %s - Qt %s - PyQt %s on %s.
        <p>作者:&nbsp;&nbsp;%s
        <p>邮箱:&nbsp;&nbsp;lc.chao.liu@gmail.com"""
                          % (__appname__, __version__, platform.python_version(),
                             QT_VERSION_STR, PYQT_VERSION_STR, platform.system(),
                             __author__))


def main():

    import time

    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(":icons/imgs/aircraft01.png"))
    app.setOrganizationName("NUAA")
    app.setOrganizationDomain("nuaa.edu.cn")
    app.setApplicationName(__appname__)

    splash = QSplashScreen()
    splash.setPixmap(QPixmap(":icons/imgs/qdata.png"))
    splash.show()

    splash.showMessage(u"正在启动主程序...",
                       Qt.AlignRight | Qt.AlignBottom, Qt.black)
    form = MainWindow()
    time.sleep(0.5)
    splash.showMessage(u"Copy: 史志伟课题组所有 南京航空航天大学 流体力学系",
                       Qt.AlignRight | Qt.AlignBottom, Qt.black)
    time.sleep(0.5)
    splash.showMessage(u"Developer: Liuchao Email: Lc.pypi@gmail.com",
                       Qt.AlignRight | Qt.AlignBottom, Qt.black)
    time.sleep(0.5)
    form.show()
    splash.finish(form)
    del splash

    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
