#!/usr/bin/env python
#!-*- coding:utf-8 -*-

import os
import time
import sys
import nodeshealthcheck
import nginxupstreamedit

import FormatPrint
class HealthCheck(object):
    def __init__(self):
        self.projectName = None

    def check(self):
        nodeshealthcheck.nodesHealthCheck(self.projectName)
        nginxupstreamedit.nginxUpstreamEdit(self.projectName)
        return True

    def checkAllTime(self):
        while True:
            self.check(self.projectName)
            time.sleep(60)

#一直启动检查服务
def checkAllTime(projectName):
    hc = HealthCheck()
    hc.projectName = projectName
    hc.checkAllTime(hc.projectName)

#检查服务单独执行一次
def checkOnce(projectName):
    hc = HealthCheck()
    hc.projectName = projectName
    return hc.check(hc.projectName)

#启动健康检查
def startHealthCheck(projectName):
    FormatPrint.printDebug("startHealthCheck")
    path=sys.path[0] + os.sep + 'shell' + os.sep + 'healthCheck.sh '
    cmd = path + " start " + str(projectName)
    if os.system(cmd) == 0:
        FormatPrint.printInfo("启动健康检查服务成功")
        return True
    else:
        FormatPrint.printInfo("启动健康检查服务失败")
        return False

#关闭健康检查
def stopHealthCheck(projectName):
    path=sys.path[0] + os.sep + 'shell' + os.sep + 'healthCheck.sh '
    cmd = path + " stop " + str(projectName)
    if os.system(cmd) == 0:
        FormatPrint.printInfo(" close ngxnx-tomcat service sucess ")
        return True
    else:
        FormatPrint.printInfo(" close ngxnx-tomcat service fail ")
        return False

#重启健康检查
def restartHealthCheck(projectName):
    path=sys.path[0] + os.sep + 'shell' + os.sep + 'healthCheck.sh '
    cmd = path + " restart " + str(projectName)
    if os.system(cmd) == 0:
        FormatPrint.printInfo(" start ngxnx-tomcat service sucess ")
        return True
    else:
        FormatPrint.printInfo(" start ngxnx-tomcat service fail ")
        return False

#健康检查服务状态
def healthCheckStatus(projectName):
    path = sys.path[0] + os.sep + 'shell' + os.sep + 'healthCheck.sh '
    cmd = path + " status" + str(projectName)
    os.system(cmd)
