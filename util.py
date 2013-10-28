#__author__ = 'hello'
# -*- coding: cp936 -*-
import re
import os
import random
import json
import string
import ctypes

from myexception import *


PATH = './img/'

dm2 = ctypes.WinDLL('./CrackCaptchaAPI.dll')
if not os.path.exists('./img'):
    os.mkdir('./img')

def str_tr(content):
    instr = "0123456789"
    outstr ="QAEDTGUJOL"
    trantab = string.maketrans(instr,outstr)
    return content.translate(trantab)

def getHid():
    import wmi
    m = wmi.WMI()
    a = ''
    b = ''
    for cpu in m.Win32_Processor():
        a = cpu.Processorid.strip()
    for bd in m.Win32_BIOS():
        b= bd.SerialNumber.strip()
    return a+b

def getEightRandomString():
    return ''.join(random.sample(string.ascii_letters,8))



def getCToken(content):
    s = ''
    pattern = re.compile('securityCToken = "([+-]?\d*)"')
    match = pattern.search(content)
    if match:
        s = match.group(1)
    return s

def GetCaptcha(content):
    global PATH
    filename = ''.join(random.sample(string.ascii_letters,8))
    filename += '.jpg'
    filename = PATH+filename
    img = None
    try:
        img = open(filename,'wb')
        img.write(content)
    except IOError:
        raise FileCanNotCreate('open file error')
    finally:
        if img:
            img.close()

    dm2.D2File.argtypes=[ctypes.c_char_p, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_short, ctypes.c_int, ctypes.c_char_p]
    dm2.D2File.restype = ctypes.c_int
    key = ctypes.c_char_p('fa6fd217145f273b59d7e72c1b63386e')
    id = ctypes.c_long(54)
    user = ctypes.c_char_p('test')
    pas = ctypes.c_char_p('test')
    timeout = ctypes.c_short(30)
    result = ctypes.create_string_buffer('/0'*100)
    ret = -1
    ret = dm2.D2File(key,user, pas, filename,timeout,id,(result))
    if ret > 0:
        return result.value
    elif ret == -101:
        raise D2FILE(u'余额不足,需要充值')
    elif ret > -199:
        raise D2FILE('user info error')
    elif ret == -208:
        raise D2FILE('software can not user')
    elif ret == -210:
         raise D2FILE('invalid user')
    elif ret == -301:
         raise D2FILE('can not find dll')
    else:
         raise D2FILE(u'识别库出错')

def GetTimeSlot(content,num):
    try:
        timeslot = json.loads(content)
        slotLen = len(timeslot['timeSlots'])
        if num < slotLen:
            return timeslot['timeSlots'][num]['startTime'],timeslot['timeSlots]'[num]['timeslotID']]
        elif slotLen > 0:
            return timeslot['timeSlots'][slotLen-1]['startTime'],timeslot['timeSlots]'[slotLen-1]['timeslotID']]
    except ValueError,e:
        raise NoJsonData('')

def sendEmail(count):
    import smtplib
    from email.mime.text import MIMEText
    from email.header import Header
    smtpserver = 'smtp.163.com'
    sender = 'sghcarbon@163.com'
    receiver = 'sghcarbon@163.com'
    subject = u'预订个数'
    user = 'sghcarbon'
    pas = 'carbon216'
    content = getHid()+u'预订个数:'+str(count)
    msg = MIMEText(content,'plain','utf-8')
    msg['Subject'] = Header(subject,'utf-8')
    msg['From'] = sender
    msg['To'] = receiver
    try:
        send_smtp = smtplib.SMTP()
        send_smtp.connect(smtpserver)
        send_smtp.login(user,pas)
        send_smtp.sendmail(sender,receiver,msg.as_string())
        send_smtp.close()
        print 'ok'
    except:
        print 'error'


