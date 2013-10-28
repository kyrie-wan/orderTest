#__author__ = 'hello'
#-*-coding=utf-8 -*-

import hashlib

from PyQt4 import QtGui

import util


class LoginDialog(QtGui.QDialog):
    m = hashlib.md5()
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self,parent)
        self.setWindowTitle(u'登录')
        self.resize(300,150)
        self.font=QtGui.QFont("Times", 10, QtGui.QFont.Bold)
        layout = QtGui.QVBoxLayout()
        id_layout = QtGui.QHBoxLayout()
        self.lbdid = QtGui.QLabel(self)
        self.lbdid.setText(u'识别码:')
        self.lbdid.setFont(self.font)

        self.lbdid_val = QtGui.QLineEdit(self)
        self.lbdid_val.setFont(self.font)
        self.lbdid_val_val = str(util.getHid())
        self.lbdid_val.setText(self.lbdid_val_val)
        self.lbdid_val.setReadOnly(True)
        id_layout.addWidget(self.lbdid)
        id_layout.addWidget(self.lbdid_val)

        sec_layout = QtGui.QHBoxLayout()
        self.lbsec = QtGui.QLabel(self)
        self.lbsec.setText(u'安全码:')
        self.lbsec.setFont(self.font)

        self.lbsec_val = QtGui.QLineEdit(self)
        self.lbsec_val.setFont(self.font)
        self.lbsec_val_val =str(util.getEightRandomString())
        self.lbsec_val.setText(self.lbsec_val_val)
        self.lbsec_val.setReadOnly(True)
        sec_layout.addWidget(self.lbsec)
        sec_layout.addWidget(self.lbsec_val)

        pass_layout = QtGui.QHBoxLayout()
        self.lbpass = QtGui.QLabel(self)
        self.lbpass.setText(u'密    码:')
        self.lbpass.setFont(self.font)

        self.lepass = QtGui.QLineEdit(self)
        self.lepass.setFont(self.font)
        pass_layout.addWidget(self.lbpass)
        pass_layout.addWidget(self.lepass)

        self.pbLogin = QtGui.QPushButton(u'进入',self)
        self.pbLogin.clicked.connect(self.login)
        self.pbCancel = QtGui.QPushButton(u'退出',self)
        self.pbCancel.clicked.connect(self.cancel)
        buttonLayout = QtGui.QHBoxLayout()
        spancerItem2 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        buttonLayout.addItem(spancerItem2)
        buttonLayout.addWidget(self.pbLogin)
        buttonLayout.addWidget(self.pbCancel)
        layout.addLayout(id_layout)
        layout.addLayout(sec_layout)
        layout.addLayout(pass_layout)
        spacerItem = QtGui.QSpacerItem(20, 48, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        layout.addItem(spacerItem)
        layout.addLayout(buttonLayout)
        self.setLayout(layout)
        self.m.update(util.str_tr(self.lbdid_val_val)+self.lbsec_val_val[0:8:2]+self.lbsec_val_val[1:8:2])

    def login(self):
        inputValue = str(self.lepass.text())
        if len(inputValue) == 0:
            return
        if inputValue == self.m.hexdigest()[10:16]:
            self.accept()
        else:
            QtGui.QMessageBox.critical(self,u'对话框',u'密码错误,请联系QQ:980920722,获取密码')
            return
    def cancel(self):
        self.reject()