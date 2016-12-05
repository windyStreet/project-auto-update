#!/usr/bin/env python
#!-*- coding:utf-8 -*-
import FormatPrint
import os
import sys
import json
import JsonFileFunc

class RunGroup(object):
    def __init__(self):
        pass
'''
获取当前运行组的名称
par:projectName
retunr:currentrungroupname
'''
def getRunGroupName(projectName):
    nodeHealStatusFile = sys.path[0] + os.sep + 'runtime' + os.sep + str(projectName) +'-node-health-status.json'
    nodeHealStatus = JsonFileFunc.readFile(nodeHealStatusFile)
    if nodeHealStatus == None:
        return "groupmaster"
    else:
        return nodeHealStatus["currentrun"]