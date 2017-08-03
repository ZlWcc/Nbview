#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017/8/2 8:00
# @Author  : 21w
# @File    : QIS.py
from ctypes import *
import time

class stt(object):
    def __init__(self):
         # 调用动态链接库
        self.dll = windll.LoadLibrary(r'F:\windows_voice\bin\msc_x64.dll')
         #登录参数，apppid一定要和你的下载SDK对应
        self.login_params = br"appid = 5980750e, work_dir = F:\windows_voice\bin"
        self.FRAME_LEN = 32768 # Byte
        self.piceLne = self.FRAME_LEN * 1
        self.audiofile = r'F:\windows_voice\bin\wav\iflytek01.wav'
        self.session_begin_params = b"sub = iat, ptt = 0, result_encoding = utf8, result_type = plain, domain = iat"
        self.ret= c_int(0)
        self.epStatus = c_int(0)
        self.recogStatus = c_int(0)

    def login(self):
        ret = self.dll.MSPLogin(None, None, self.login_params)


    def session_id(self):
        sessionID = c_voidp()
        self.dll.QISRSessionBegin.restype = c_char_p
        sessionID = self.dll.QISRSessionBegin(None, self.session_begin_params, byref(self.ret))
        print('QISRSessionBegin => sessionID:', sessionID, 'ret:', self.ret.value)
        return sessionID


    def first_write(self, data, sessionID):
        ret = self.dll.QISRAudioWrite(sessionID, data, len(data), 1, byref(self.epStatus), byref(self.recogStatus))
        print('len(wavData):', len(data), 'QISRAudioWrite ret:', ret, 'epStatus:', self.epStatus.value, 'recogStatus:', self.recogStatus.value)


    def continue_write(self, data, sessionID):
        ret = self.dll.QISRAudioWrite(sessionID, data, len(data), 2, byref(self.epStatus),
                                 byref(self.recogStatus))
        # print('len(wavData):', len(data), 'QISRAudioWrite ret:', ret, 'epStatus:', self.epStatus.value, 'recogStatus:',
        #       self.recogStatus.value)

    def last_write(self, sessionID):
         ret = self.dll.QISRAudioWrite(sessionID, None, 0, 4, byref(self.epStatus), byref(self.recogStatus))
         print('len(wavData):',  'QISRAudioWrite ret:', ret, 'epStatus:', self.epStatus.value, 'recogStatus:',
               self.recogStatus.value)

    def get_result(self, sessionID):
        counter = 0
        laststr = ''
        while self.recogStatus.value != 5:
            ret = c_int()
            self.dll.QISRGetResult.restype = c_char_p
            retstr = self.dll.QISRGetResult(sessionID, byref(self.recogStatus), 0, byref(ret))
            if retstr is not None:
                laststr += retstr.decode()
                print(laststr)
            print('ret:', ret.value, 'recogStatus:', self.recogStatus.value)
            counter += 1
            time.sleep(0.2)
            counter += 1
            if counter == 500:
                laststr += '讯飞语音识别失败'
                break

    def run_stt(self, wavData):
        ret = c_byte(0)
        sessionID = self.session_id()
        self.first_write(wavData, sessionID)

        self.last_write(sessionID)
        self.get_result(sessionID)
        ret = self.dll.QISRSessionEnd(sessionID, '\0')

    def logout(self):
        # print('end ret: ', self.ret)
        self.dll.MSPLogout()

stt = stt()
stt.login()
with open(r'F:\windows_voice\bin\wav\iflytek01.wav', 'rb') as wavFile:
    for i in range(1):
        wavData = wavFile.read(stt.piceLne)
        stt.run_stt(wavData)
        print(len(wavData))

stt.logout()