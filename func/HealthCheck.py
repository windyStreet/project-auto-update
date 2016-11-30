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
        pass

    def check(self):
        nodeshealthcheck.nodesHealthCheck()
        nginxupstreamedit.nginxUpstreamEdit()
        return True

    def checkAllTime(self):
        while True:
            self.check()
            time.sleep(60)

#一直启动检查服务
def checkAllTime():
    HC = HealthCheck()
    HC.checkAllTime()

#检查服务单独执行一次
def checkOnce():
    HC = HealthCheck()
    return HC.check()

#启动健康检查
def startHealthCheck():
    FormatPrint.printDebug("startHealthCheck")
    path=sys.path[0] + os.sep + 'shell' + os.sep + 'healthCheck.sh'
    cmd = path + " start"
    if os.system(cmd) == 0:
        FormatPrint.printInfo("启动健康检查服务成功")
        return True
    else:
        FormatPrint.printInfo("启动健康检查服务失败")
        return False

#关闭健康检查
def stopHealthCheck():
    FormatPrint.printDebug("stopHealthCheck")
    path=sys.path[0] + os.sep + 'shell' + os.sep + 'healthCheck.sh'
    cmd = path + " stop"
    if os.system(cmd) == 0:
        FormatPrint.printInfo("关闭健康检查服务成功")
        return True
    else:
        FormatPrint.printInfo("关闭健康检查服务失败")
        return False

#重启健康检查
def restartHealthCheck():
    FormatPrint.printDebug("restartHealthCheck")
    path=sys.path[0] + os.sep + 'shell' + os.sep + 'healthCheck.sh'
    cmd = path + " restart"
    if os.system(cmd) == 0:
        FormatPrint.printInfo("重启健康检查服务成功")
        return True
    else:
        FormatPrint.printInfo("重启健康检查服务失败")
        return False

#健康检查服务状态
def healthCheckStatus():
    FormatPrint.printDebug("healthCheckStatus")
    path = sys.path[0] + os.sep + 'shell' + os.sep + 'healthCheck.sh'
    cmd = path + " status"
    os.system(cmd)
