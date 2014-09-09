# author = 'lenovo'
# -*- coding: utf-8 -*-
import json
from header import comm_key,comm_val
from  myexception import ServerNotFound, HttpLibError
import requests

class net:

    commHeader = \
    {
        comm_key.USER_AGENT:comm_val.USER_AGENT,
        comm_key.ACCEPT_ENCODING:comm_val.ACCEPT_ENCODING,
        comm_key.CONNECTION:comm_val.CONNECTION,
        comm_key.ACCEPT_LANG:comm_val.ACCEPT_LANG,
        comm_key.HOST:comm_val.HOST,
        comm_key.CACHE:comm_val.CACHE
    }
    def __init__(self):
        self._headers = dict()
        self._body= dict()
        self._cookie = dict()
        self.resp = None

    def getStatus(self):
        return self.resp.status_code

    def getJson(self):
        return self.resp.json()

    def getText(self):
        return self.resp.text

    def getContent(self):
        return self.resp.content
    #An application client must receive and send two cookies: the application-generated cookie
    # and the special Elastic Load Balancing cookie named AWSELB.
    #  This is the default behavior for many common web browsers.
    def updateCookie(self):
        try:
            self._cookie['JSESSIONID'] = self.resp.cookies['JSESSIONID']
            self._cookie['AWSELB'] = self.resp.cookies['AWSELB']
        except KeyError,e:
            pass

    def updateHeader(self, header):
        self._headers = self.commHeader
        self._headers.update(header)

    def updateBody(self,body):
        self._body.clear()
        self._body.update(body)

    def get(self,url):
        try:
            self.resp = requests.get(url, headers=self._headers,cookies=self._cookie,verify = False)
            self.updateCookie()
        except requests.ConnectionError,e:
            raise ServerNotFound()
        except requests.HTTPError:
            raise ServerNotFound()
        except requests.Timeout:
            raise ServerNotFound()

    def post(self,url):
        try:
            self.resp = requests.post(url, headers=self._headers, data=self._body,cookies=self._cookie,verify=False)
            self.updateCookie()
        except requests.ConnectionError,e:
            raise ServerNotFound()
        except requests.HTTPError:
            raise ServerNotFound()
        except requests.Timeout:
            raise ServerNotFound()


    def post_json(self,url):
        try:
            self.resp = requests.post(url, headers=self._headers, data=json.dumps(self._body,sort_keys=True),cookies=self._cookie,verify=False)
            self.updateCookie()
        except requests.ConnectionError,e:
            raise ServerNotFound()
        except requests.HTTPError:
            raise ServerNotFound()
        except requests.Timeout:
            raise ServerNotFound()

