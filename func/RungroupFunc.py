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

# 重启tomcat
def getRunGroupName(projectName):
    nodeHealStatusFile=node_health_status_file = sys.path[0] + os.sep + 'runtime' + os.sep + str(projectName) +'-node-health-status.json'
    nodeHealStatus = JsonFileFunc.readFile(nodeHealStatusFile)
    if nodeHealStatus == None:
        return "groupmaster"
    else:
        return nodeHealStatus["currentrun"]
