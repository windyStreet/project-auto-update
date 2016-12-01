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
		with open(fielPath, 'r') as file:
			jsonData = json.load(file)
	except Exception as e:
		FormatPrint.printError('read [ '+str(fielPath)+' ] not exists')
	return jsonData

#create json File
def createFile(fielPath,data):
	try:
		with open(fielPath, 'w') as file:
			file.write(json.dumps(data, indent=4))
	except Exception as e:
		FormatPrint.printFalat('create '+str(fielPath)+' fail')

