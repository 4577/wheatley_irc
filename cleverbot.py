#!/usr/bin/python
#-*- encoding: utf-8 -*-
from htmlentitydefs import name2codepoint
from urllib import urlencode
from requests import post
from hashlib import md5
from time import time
from re import sub

class Session:
	def __init__(self):
		self.params = {'emotionaloutput':'','asbotname':'','emotionalhistory':'','ttsvoice':'','sub':'Say','vText8':'','vText7':'','vText6':'','vText5':'','vText4':'','vText3':'','vText2':'','start':'y','lineref':'','typing':'','fno':'0','sessionid':'','stimulus':'','islearning':'1','icognocheck':'','icognoid':'wsf','prevref':'','cleanslate':'false'}
	
	def ask(self, text):
		self.lastTs = time()
		
		self.params['stimulus'] = text
		self.params['icognocheck'] = md5(urlencode(self.params)[9:29]).hexdigest()
		
		resp = post('http://www.cleverbot.com/webservicemin', self.params)
		resp = resp.content.split('\r')
		
		botResp = sub('&(.+?);', replaceEntities, resp[0].decode('latin1', 'ignore'))
		
		self.params['sessionid'] = resp[1]
		self.params['prevref'] = resp[10]
		self.params['emotionalhistory'] = resp[12]
		
		for i in xrange(3, 10):
			self.params['vText' + str(11 - i)] = resp[i]
		
		return botResp.encode('utf-8')

def replaceEntities(text):
	text = text.groups()[0]
	
	if text[0] == '#':
		return unichr(int(text[1:]))
	else:
		return unichr(name2codepoint[text])
