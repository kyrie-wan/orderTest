#__author__ = 'lenovo'
# -*- coding:utf-8 -*-
import Queue
import time
import re
import json

from PyQt4 import QtCore


# below is self-def pack

import util
from header import *
from network import net
from data import *
from myexception import *


Store = [ 'R388', 'R448', 'R320'] # xd,wfj,slt

Product = ['ME458CH/A','ME455CH/A','ME452CH/A']

CaptchaUrl = 'https://ireservea.apple.com/captchas/file.jpeg?%d'
orderUrl = 'https://ireservea.apple.com/CN/zh_CN/reserve/iPhone'
ReservationUrl = 'https://ireservea.apple.com/CN/zh_CN/reserve/iPhone/productReservation'
SkusForProductUrl = 'https://ireservea.apple.com/CN/zh_CN/reserve/iPhone/skusForStoreProduct'
GetTimeSlotsUrl = 'https://ireservea.apple.com/CN/zh_CN/reserve/iPhone/getTimeSlots'
CreatePickUpUrl = 'https://ireservea.apple.com/CN/zh_CN/reserve/iPhone/createPickUp'
error_url = 'https://ireservea.apple.com/CN/zh_CN/reserve/iPhone/reservationInactive'


mutex = QtCore.QMutex()

class worker(QtCore.QThread):

    def __init__(self,user_queue,out_queue,id,p_trigger,d_trigger,c_trigger):
        QtCore.QThread.__init__(self,)
        self.queue = user_queue
        self.code_queue = out_queue
        self.info = None
        self.cToken = ''
        self.captcha = ''
        self.code = ''
        self.timeStart = ''
        self.timeSlotID = ''
        self.hasStop = False
        self.network = net()
        self.id = id
        self.p_trigger =p_trigger
        self.d_trigger =d_trigger
        self.c_trigger =c_trigger

    def __del__(self):
        self.wait()

    def run(self):
            while not self.queue.empty():
                try:
                    self.info = self.queue.get()
                    # Check contents of message and do what it says
                    # As a test, we simply print it
                    self.goIntoPage()
                    self.refreshCaptcha()
                    self.getReseCode()
                    self.postToProduct()
                    self.getTimeSlot()
                    self.createPickUp()
                    self.queue.task_done()
                except Queue.Empty:
                    break

    def goIntoPage(self):
        st = u'请稍后再回来预订 iPhone'
        while True:
            try:
                self.sendPageReq()
                if self.network.getStatus() != 200:
                    self.p_trigger.emit(self.info.phoneNumber,u'服务器忙,正在努力............')
                    continue
                elif st in self.network.getText():
                    self.p_trigger.emit(self.info.phoneNumber,u'本次预定没有开始,继续刷新............')
                    continue
                else:
                    self.cToken = util.getCToken(self.network.getText())
                    self.p_trigger.emit(self.info.phoneNumber,u'进入预定页面............')
                    break
            except ServerNotFound, e:
                self.p_trigger.emit(self.info.phoneNumber,u'服务器忙,努力中............')
                continue

    def refreshCaptcha(self):
        while True:
            try:
                self.sendCaptchaReq()
                if self.network.getStatus() == 200:
                    self.p_trigger.emit(self.info.phoneNumber,u'识别验证码............')
                    self.captcha = util.GetCaptcha(self.network.getContent())
                    print self.captcha
                    break
            except D2FILE,e:
                self.p_trigger.emit(self.info.phoneNumber,unicode(e.errStr))
                continue
            except ServerNotFound,e:
                self.p_trigger.emit(self.info.phoneNumber,u'服务器忙,努力中............')
                continue

    def getReseCode(self):
        global mutex
        mutex.lock()
        self.d_trigger.emit(self.id,self.info.phoneNumber)
        self.code = self.code_queue.get()
        mutex.unlock()

    def postToProduct(self):
        while True:
            try:
                self.sendProductReq()
                if self.network.getStatus() == 200:
                    self.p_trigger.emit(self.info.phoneNumber,u'选择产品............')
                    break
                else:
                    continue
            except ServerNotFound,e:
                self.p_trigger.emit(self.info.phoneNumber,u'服务器忙,努力中............')
                continue

    def getTimeSlot(self):
        while True:
            try:
                self.sendTimeSlotReq()
                if self.network.getStatus() == 200:
                    self.startTime,self.timeSlotId = util.GetTimeSlot(self.network.getJson(), self.info.timeSlot)
                    break
                else:
                    continue
            except ServerNotFound,e:
                self.p_trigger.emit(self.info.phoneNumber,u'服务器忙,努力中............')
                continue
            except NoJsonData, e:
                continue

    def createPickUp(self):
        while True:
            try:
                self.sendPickUpReq(2)
                status = self.network.getStatus()
                if status >= 200 and status < 400:
                    self.p_trigger.emit(self.info.phoneNumber,u'预定成功,查询邮件确认')
                    self.c_trigge.emit(2)
                    util.sendEmail(2)
                    break
                else:
                    self.sendPickUpReq(1)
                    status = self.network.getStatus()
                    if status >=200 and status < 400:
                        self.p_trigger.emit(self.info.phoneNumber,u'预定成功,查询邮件确认')
                        self.c_trigge.emit(1)
                        util.sendEmail(1)
                    else:
                        try:
                            isError, errorMessage = self.getPickUpError()
                            if not isError:
                                self.p_trigger.emit(self.info.phoneNumber,(unicode(errorMessage)))
                        except ValueError,e:
                            self.p_trigger.emit(self.info.phoneNumber,u'预定失败')
                    break
            except ServerNotFound,e:
                self.p_trigger.emit(self.info.phoneNumber,u'服务器忙,努力中............')
                continue

    def sendPageReq(self):
        m_header = {spe_key.ACCEPT:acc_val.MS,
                    spe_key.REFERER:ref_val.BSTART}
        self.network.updateHeader(m_header)
        self.network.get(orderUrl)

    def sendCaptchaReq(self):
        url = CaptchaUrl % (time.time() * 1000)
        m_header = {spe_key.ACCEPT:acc_val.JS,
                    spe_key.REFERER: ref_val.BRESERVATION,
                    spe_key.X_REQUEST:x_val.xmlHttpRequest,
        }
        self.network.updateHeader(m_header)
        self.network.get(url)

    def sendProductReq(self):
        m_header = {spe_key.ACCEPT:acc_val.MS,
                    spe_key.REFERER:ref_val.BRESERVATION,
                    spe_key.CONTENT_TYPE:ct_val.XFORM,
        }
        m_body ={order.cToken:self.cToken,
                 order.phoneNumber:self.info.phoneNumber,
                 order.reservationCode:self.code,
                 order.captchaAnswer: self.captcha,
                 order.captchaFormat:'IMAGE'}
        self.network.updateBody(m_body)
        self.network.post(ReservationUrl)
     # below is post method
    def sendSkusReq(self):
        m_header = {spe_key.ACCEPT:acc_val.JS,
                    spe_key.REFERER:ref_val.BOTHER,
                    spe_key.CONTENT_TYPE:ct_val.XFORM,
                    spe_key.X_REQUEST:x_val.xmlHttpRequest,
                    spe_key.CTOKEN: self.cToken,
                    }
        self.network.updateHeader(m_header)
        m_body = {
                skus_prodcut.PRODUCT:'null',
                skus_prodcut.TAG:'iPhone',
                skus_prodcut:Store[self.info.storeNumber]
        }
        self.network.updateBody(m_body)
        self.network.post(SkusForProductUrl)

    def sendTimeSlotReq(self):
         m_header ={spe_key.ACCEPT:acc_val.JS,
                    spe_key.REFERER:ref_val.BOTHER,
                    spe_key.CONTENT_TYPE:ct_val.XFORM,
                    spe_key.X_REQUEST:x_val.xmlHttpRequest,
                    spe_key.CTOKEN: self.cToken,
                    }
         self.network.updateHeader(m_header)
         m_body ={
                timeslot.ProductName:'iPhone 5s',
                timeslot.StoreNumber:Store[self.info.storeNumber],
                timeslot.Plan:'UNLOCKED',
                timeslot.Mode:'POST_LAUNCH'
                }
         self.network.updateBody(m_body)
         self.network.post(GetTimeSlotsUrl)



    def sendPickUpReq(self,quantity):
        m_header ={spe_key.ACCEPT:acc_val.JS,
                    spe_key.REFERER:ref_val.BOTHER,
                    spe_key.CONTENT_TYPE:ct_val.JSON,
                    spe_key.X_REQUEST:x_val.xmlHttpRequest,
                    spe_key.CTOKEN:self.cToken,
                    }
        self.network.updateHeader(m_header)
        m_body ={
            pick_up.Email:self.info.email,
            pick_up.FirstName:self.info.firstName,
            pick_up.LastName:self.info.lastName,
            pick_up.PhoneNumber:self.info.phoneNumber,
            pick_up.StoreNumber:Store[self.info.storeNumber],
            pick_up.PartNumber:Product[self.info.partNumber],
            pick_up.PickUpMode:'POST_LAUNCH',
            pick_up.TimeSlotID:self.timeSlotID,
            pick_up.Plan:'UNLOCKED',
            pick_up.ProductName:'iPhone 5s',
            pick_up.Quantity:quantity,
            pick_up.GovID:self.info.govId
        }
        self.network.updateBody(m_body)
        self.network.post_json(CreatePickUpUrl)
    def getPickUpError(self):
        q = json.loads(self.network.getJson())
        return q['isError'],q['errorMessage']
