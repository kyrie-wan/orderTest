#__author__ = 'lenovo'
# -*- coding=utf-8 -*-

import sys
import Queue

from PyQt4 import QtCore, QtGui

import workthread
import order
from myexception import HttpLibError
from dialog import LoginDialog

WIN_WIDTH = 1366
WIN_HEIGHT = 700
THREAD_NUM = 10

TIMESLOT = [u'10:00 上午 - 11:00 上午',u'11:00 上午 - 12:00 下午',u'12:00 下午 - 1:00 下午',u'1:00 下午 - 2:00 下午',u'2:00 下午 - 3:00 下午', u'3:00 下午 - 4:00 下午',u'4:00 下午 - 5:00 下午',u'5:00 下午 - 6:00 下午',u'6:00 下午 - 7:00 下午',u'7:00 下午 - 8:00 下午']
PRODUCTNAME =[u'金色64GB',u'金色32GB',u'金色16GB']
STORENAME =[u'西单',u'王府井',u'三里屯']





def showMessage(widget,errorMessage):
    QtGui.QMessageBox.critical(widget,u'错误',unicode(errorMessage))

class MainWindow(QtGui.QMainWindow):
    queue = Queue.Queue()
    count = 0
    thread_list =[]
    queue_list =[]
    proc_trigger = QtCore.pyqtSignal(QtCore.QString,QtCore.QString,name = 'updateProcess')
    dialog_trigger = QtCore.pyqtSignal(int,QtCore.QString, name = 'getPhoneCode')
    count_trigger =  QtCore.pyqtSignal(int,name = 'updateLCDNumber')
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setWindowTitle('HelloIphone')
        self.font =QtGui.QFont("Times", 10, QtGui.QFont.Bold)
        self.setMinimumSize(WIN_WIDTH, WIN_HEIGHT)
        self.verticalLayoutWidget = QtGui.QWidget()
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(0, 0, WIN_WIDTH, WIN_HEIGHT))
        #create the whole vbox container
        self.verticalLayout = QtGui.QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setMargin(2)

        #---------------------------------------below create tip

        self.hBoxForTip = QtGui.QHBoxLayout()
        self.verticalLayout.addLayout(self.hBoxForTip)
        self.label = QtGui.QLabel(u'成功个数')
        self.label.setMaximumSize(50,50)
        self.hBoxForTip.addWidget(self.label)
        self.labelNumber = QtGui.QLabel('0')
        self.labelNumber.setMaximumSize(50,50)
        self.hBoxForTip.addWidget(self.labelNumber)

        #---------------------------below code create table widget

        self.tableWidget = QtGui.QTableWidget()
        self.tableWidget.resizeColumnsToContents()
        self.tableWidget.setWordWrap(True)
        self.tableWidget.setColumnCount(8)

        item = QtGui.QTableWidgetItem()
        item.setText(u'姓')
        self.tableWidget.setHorizontalHeaderItem(0, item)
        self.tableWidget.setColumnWidth(0,100)

        item = QtGui.QTableWidgetItem()
        item.setText(u'名')
        self.tableWidget.setHorizontalHeaderItem(1, item)
        self.tableWidget.setColumnWidth(1,100)

        item = QtGui.QTableWidgetItem()
        item.setText(u'手机')
        self.tableWidget.setHorizontalHeaderItem(2, item)
        self.tableWidget.setColumnWidth(2,150 )

        item = QtGui.QTableWidgetItem()
        item.setText(u'邮箱')
        self.tableWidget.setHorizontalHeaderItem(3, item)
        self.tableWidget.setColumnWidth(3,200)


        item = QtGui.QTableWidgetItem()
        item.setText(u'身份证号')
        self.tableWidget.setHorizontalHeaderItem(4, item)
        self.tableWidget.setColumnWidth(4, 200)

        item = QtGui.QTableWidgetItem()
        item.setText(u'取货时间')
        self.tableWidget.setHorizontalHeaderItem(5, item)
        self.tableWidget.setColumnWidth(5, 200)

        item = QtGui.QTableWidgetItem()
        item.setText(u'型号')
        self.tableWidget.setHorizontalHeaderItem(6, item)
        self.tableWidget.setColumnWidth(6,150 )

        item = QtGui.QTableWidgetItem()
        item.setText(u'店址')
        self.tableWidget.setHorizontalHeaderItem(7, item)
        self.tableWidget.setColumnWidth(7,150 )
        self.tableWidget.horizontalHeader().setStretchLastSection(True)
        self.verticalLayout.addWidget(self.tableWidget)

        #---------------------------below code create start widget
        self.hBoxForAction = QtGui.QHBoxLayout()
        self.verticalLayout.addLayout(self.hBoxForAction)
        self.btnStart = QtGui.QPushButton(u'开始')
        self.btnStart.setMaximumSize(100,100)
        self.hBoxForAction.addWidget(self.btnStart)
        self.connect(self.btnStart, QtCore.SIGNAL('clicked()'), self.Start)
        #---------------------------below code create display window
        self.processWin = QtGui.QTextEdit()
        self.processWin.setMaximumSize(700,100)
        self.hBoxForAction.addWidget(self.processWin)
        #---------------------------below code create add , delete widget
        self.vBoxForAddDel = QtGui.QVBoxLayout()
        self.btnAddUser = QtGui.QPushButton(u'添加')
        self.btnAddUser.setMaximumSize(50,50)
        self.connect(self.btnAddUser, QtCore.SIGNAL('clicked()'), self.insertRecord)
        self.vBoxForAddDel.addWidget(self.btnAddUser)

        self.btnDeleteUser = QtGui.QPushButton(u'删除')
        self.btnDeleteUser.setMaximumSize(50,50)
        self.connect(self.btnDeleteUser, QtCore.SIGNAL('clicked()'), self.removeRecord)
        self.vBoxForAddDel.addWidget(self.btnDeleteUser)

        self.hBoxForAction.addLayout(self.vBoxForAddDel)
        #--------------------------------------------------------------
        self.setCentralWidget(self.verticalLayoutWidget)
        self.isbusy = False
        self.proc_trigger.connect(self.updateProcess)
        self.dialog_trigger.connect(self.getPhoneCode)
        self.count_trigger.connect(self.updateLCDNumber,QtCore.Qt.QueuedConnection)

    # insert a user record
    def insertRecord(self):
        row = self.tableWidget.rowCount()
        self.tableWidget.setRowCount(row+1)
        for c in range(5):
            item = QtGui.QLineEdit()
            self.tableWidget.setCellWidget(row,c,item)
        combox5 = QtGui.QComboBox()
        combox5.addItems(TIMESLOT)
        self.tableWidget.setCellWidget(row,5,combox5)
        combox6 = QtGui.QComboBox()
        combox6.addItems(PRODUCTNAME)
        self.tableWidget.setCellWidget(row,6,combox6)
        combox7 = QtGui.QComboBox()
        combox7.addItems(STORENAME)
        self.tableWidget.setCellWidget(row,7,combox7)
        self.tableWidget.setCurrentCell(row,0)


    # delete selected user
    def removeRecord(self):
        curRow = self.tableWidget.currentRow()
        self.tableWidget.removeRow(curRow)


    # collect user info
    def collectData(self):
        rn = self.tableWidget.rowCount()
        cn = self.tableWidget.columnCount()
        for row in range(rn):
            info = order.orderInfo()
            info.rowNumber = row
            item = self.tableWidget.cellWidget(row, 0)
            info.lastName =unicode(item.text())
            item = self.tableWidget.cellWidget(row, 1)
            info.firstName =unicode(item.text())
            item = self.tableWidget.cellWidget(row, 2)
            info.phoneNumber = unicode(item.text())

            item = self.tableWidget.cellWidget(row, 3)
            info.email =unicode(item.text())

            item = self.tableWidget.cellWidget(row,4)
            info.govId = unicode(item.text())

            item = self.tableWidget.cellWidget(row,5)
            info.timeSlot = item.currentIndex()

            item = self.tableWidget.cellWidget(row,6)
            info.partNumber = item.currentIndex()

            item = self.tableWidget.cellWidget(row,7)
            info.storeNumber = item.currentIndex()
            self.queue.put(info)

    @QtCore.pyqtSlot(int)
    def updateLCDNumber(self,num):
        global count
        count += num
        self.labelNumber.setText(str(count))

    @QtCore.pyqtSlot(str,str)
    def updateProcess(self,arg1,arg2):
        allMessage =unicode(arg1)+ ' : ' + unicode(arg2)
        self.processWin.append(allMessage)

    @QtCore.pyqtSlot(int,str)
    def getPhoneCode(self,arg1,arg2):
        dlg = QtGui.QInputDialog()
        comment = u'请输入 '+arg2+ u' 的预定码'
        text, ok =dlg.getText(self, u'输入对话框',comment)
        if ok and (not text.isEmpty()):
            self.queue_list[arg1].put(str(text))

    def Start(self):
        self.collectData()
        try:
            for index in range(2):
                out_queue = Queue.Queue()
                t1 = workthread.worker(self.queue,out_queue,index,self.proc_trigger,self.dialog_trigger,self.count_trigger)
                self.thread_list.append(t1)
                self.queue_list.append(out_queue)
            for t in self.thread_list:
                t.start()
        except HttpLibError:
            showMessage(u'网络库异常,建议重新启动程序,但数据会丢失')

    def quit(self):
        sys.exit()


def login():
    dialog = LoginDialog()
    if dialog.exec_():
         return True

if __name__ == '__main__':
    app = QtGui.QApplication( sys.argv )
    #if login():
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())