#!/usr/bin/env python
#!-*- coding:utf-8 -*-

import FormatPrint
import json

class __jsonFileFunc(object):
    def __init__(self):
        pass

#read content
def readFile(fielPath):
	jsonData=None
	try:
		with open(fielPath, 'r') as tomcat_conf:
			jsonData = json.load(tomcat_conf)
	except Exception as e:
		FormatPrint.printError('read'+str(fielPath)+'no exists')
	return jsonData