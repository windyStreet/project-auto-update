#!/usr/bin/env python
#!-*- coding:utf-8 -*-
import sys
import os
import json
import time
import urllib2
import socket
import FormatPrint
import TomcatFunc
import NginxFunc
import RungroupFunc
import __checkServiceIsOK
import JsonFileFunc

class __projectupdate_double(object):
    def __init__(self):
        self.hostInfostr = None
        self.projectJson = None
        self.endUpdateWaiteMaxTime = None
        self.tomcatmaxrestattime = None
        self.currentProjectConf = None
        self.projectName = None
        self.updateVersion = None
        self.updateTime = None
        self.updateType = None
        self.deploymentmode = None
        self.nodeHealthStatus = None
        self.willUpdateGroup = None
        self.willBeRestartTomcats = []
        self.tomcatstartscriptpath = None
        self.tomcatkillscriptpath = None
        self.sucessRestartTomcatsTag = []

    #项目资源替换
    def replceResource(self):
        command = self.currentProjectConf[self.willUpdateGroup]['tomcatresourceupdatescriptpath']+ " " + str(self.updateVersion) + " " + str(self.updateTime)
        FormatPrint.printInfo("执行资源替换脚本:" + str(command))
        if os.system(command) == 0:
            FormatPrint.printInfo("replace resource sucess ")
            return True
        else:
            FormatPrint.printInfo("replace resource fail ")
            return False

    # 重启当前tomcat组
    def restartCurrentTomcats(self):
        if len(self.willBeRestartTomcats) == 0:
            FormatPrint.printError(" no tomcat is able to restart ")
            return False
        else:
            self.tomcatstartscriptpath = self.currentProjectConf[self.willUpdateGroup]['tomcatstartscriptpath']
            self.tomcatkillscriptpath = self.currentProjectConf[self.willUpdateGroup]['tomcatkillscriptpath']
            return TomcatFunc.restartTomcats(self.tomcatstartscriptpath, self.tomcatkillscriptpath,self.willBeRestartTomcats)

    #初始化node-health-status 文件
    def initNodeHealthStatusFile(self):
        pass

    #修改node-healh-status 文件
    def modifNodeHealthStatusFile(self):
        pass

    # 修改node-healh-status
    def modifyNodeHealthStatus(self):
        nodeHealthStatusFile = sys.path[0] + os.sep + 'runtime' + os.sep + str(self.projectName)+'-node-health-status.json'
        if JsonFileFunc.readFile(nodeHealthStatusFile) == None:
            self.initNodeHealthStatusFile()
            return True
        else:
            self.modifNodeHealthStatusFile()
            return True

    #删除 upstream-status 文件
    def delUpstreamStatus(self):
        orgin_file = sys.path[0] + os.sep + 'runtime' + os.sep + str(self.projectName)+'-upstream-status.json'
        if os.path.exists(orgin_file):
            try:
                new_file = sys.path[0] + os.sep + 'runtime' + os.sep + time.strftime('%Y%m%d%H%M%S') + '-'+str(self.projectName)+'-upstream-status.json'
                os.rename(orgin_file, new_file)
            except Exception as e:
                FormatPrint.printFalat("删除"+str(orgin_file)+"文件出错:" + str(e))
                return False
            return True
        else:
            FormatPrint.printInfo(str(orgin_file)+"文件不存在，未初始化")
            return True

    #修改运行时状态
    def modifyRuntimeStatus(self):
        if self.modifyNodeHealthStatus() and self.delUpstreamStatus():
            return True
        else:
            return False

#功能实现函数
def process(projectJson):
    __pud=__projectupdate_double()
    __pud.projectJson=projectJson

    __pud.projectJson=projectJson
    __pud.endUpdateWaiteMaxTime=projectJson.tomcatConf['endUpdateWaiteMaxTime']
    __pud.tomcatmaxrestattime=projectJson.tomcatConf['tomcatmaxrestattime']
    __pud.currentProjectConf=projectJson.tomcatConf['projectname'][projectJson.projectName]
    __pud.hostInfostr =projectJson.hostInfostr
    __pud.projectName=projectJson.projectName
    __pud.updateVersion=projectJson.updateVersion
    __pud.updateTime=projectJson.updateTime
    __pud.updateType=projectJson.updateType
    __pud.deploymentmode=projectJson.deploymentmode

    currentRunGroup = RungroupFunc.getRunGroupName(__pud.projectName)
    if currentRunGroup == "mastergroup":
        __pud.willUpdateGroup = "backupgroup"
    elif currentRunGroup == "backupgroup":
        __pud.willUpdateGroup = "mastergroup"
    else:
        FormatPrint.printFalat(" can not get the will update group , please check config ")

    __pud.willBeRestartTomcats=__pud.currentProjectConf[__pud.willUpdateGroup]['tomcats']
    # 替换资源
    if __pud.replceResource():
        if __pud.restartCurrentTomcats():
            __pud.sucessRestartTomcatsTag = __checkServiceIsOK.checkServiceIsOk(__pud.willBeRestartTomcats, __pud.projectName,__pud.tomcatmaxrestattime, __pud.endUpdateWaiteMaxTime,__pud.tomcatkillscriptpath, __pud.hostInfostr)
            if len(__pud.sucessRestartTomcatsTag) > 0 :
                if __pud.modifyRuntimeStatus():
                    FormatPrint.printInfo(" update finish ")
                else:
                    FormatPrint.printFalat(" modify runtime file fail ")
            else:
                FormatPrint.printFalat(" service is not available ")
        else:
            FormatPrint.printFalat(" restart tomcat fail ")
    else:
        format(" replace resource fail ")

    # 初始化运行时文件
    __pud.initNodeHealthStatus()
'''
    A、关闭健康检查服务
    B、读取配置文件

        1、判断当前运行组
        D、替换资源
        2、替换将被更新组配置的项目
    E、重启tomcat
        1、判断当前运行组
        2、重启将被更新组的tomcat
    F、启动健康检查服务
'''