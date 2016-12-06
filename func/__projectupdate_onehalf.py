#!/usr/bin/env python
#!-*- coding:utf-8 -*-

import FormatPrint
import TomcatFunc
import NginxFunc
import RungroupFunc
import NodeRunStatusFunc
import __checkServiceIsOK
import ResourceFunc

class __projectupdate_onehalf(object):
    def __init__(self):
        self.hostInfostr = None
        self.projectJson = None
        self.projectName = None
        self.updateVersion = None
        self.updateTime = None
        self.updateType = None
        self.deploymentmode = None
        self.willUpdateGroup = []
        self.sucessRestartTomcatTags = []

    def setSucessRestartTomcatTags(self):
        if self.willUpdateGroup[0] == 'backupgroup':
            tomcat_conf = self.projectJson.tomcatConf
            pass
        if self.willUpdateGroup[0] == 'mastergroup':
            pass


def process(projectJson):
    __puo = __projectupdate_onehalf()
    __puo.projectJson = projectJson
    __puo.hostInfostr = projectJson.hostInfostr
    __puo.projectName = projectJson.projectName
    __puo.updateVersion = projectJson.updateVersion
    __puo.updateTime = projectJson.updateTime
    __puo.updateType = projectJson.updateType
    __puo.deploymentmode = projectJson.deploymentmode


    # currentRunGroup = RungroupFunc.getRunGroupName(__puo.projectName)
    #
    #
    # if currentRunGroup == "mastergroup":
    #     __puo.willUpdateGroup = "backupgroup"
    # elif currentRunGroup == "backupgroup":
    #     __puo.willUpdateGroup = "mastergroup"
    # else:
    #     FormatPrint.printFalat(" can not get the will update group , please check config ")

    #先进行初始化
    __puo.willUpdateGroup.append("mastergroup")
    __puo.willUpdateGroup.append("backupgroup")
    if NodeRunStatusFunc.initNodeHealthStatus(__puo, __puo.willUpdateGroup):
        pass
    else:
        FormatPrint.printFalat(" can not init node-health-status file ")

    del __puo.willUpdateGroup[:]

    #默认情况下，认为配置的tomcat无任何问题，完全可以独立访问

    #====1、更新master组
    __puo.willUpdateGroup.append("backupgroup")
    #修改 NG（认为backup组是可以使用的）
    #替换资源
    #重启tomcat
    #修改NG
    #重启tomgcat
    #修改NG

    if NginxFunc.changeNginxConf(__puo):
        pass
    else:
        FormatPrint.printError(" modify nginx errof ")

    #替换全部资源
    if ResourceFunc.replceResource(__puo):
        #初始化本次配置()


        if TomcatFunc.restartWillUpdateTomcatGroup(__puo):
            __puo.sucessRestartTomcatTags = __checkServiceIsOK.checkServiceIsOk(__puo)
            if len(__puo.sucessRestartTomcatTags) > 0:
                if NodeRunStatusFunc.initNodeHealthStatus(__puo, __puo.willUpdateGroup):
                    if NginxFunc.changeNginxConf(__puo):
                        FormatPrint.printInfo(" update finish ")
                    else:
                        FormatPrint.printError(" modifu Nginx error ")
                else:
                    FormatPrint.printFalat(" modify runtime file fail ")
            else:
                FormatPrint.printFalat(" service is not available ")
        else:
            FormatPrint.printFalat(" restart tomcat fail ")

    else:
        FormatPrint.printFalat(" replace resource fail ")
'''
    A、关闭健康检查服务
    B、读取配置文件
    C、初始化node-health-status文件
        i:single模式需要初始化全部的tomcat信息，master以及backup两组的tomcat信息
    D、替换资源
    E、重启tomcat
        1:修改nginx文件（剔除mastert 服务配置）
        2:reload nginx
        3:重启master tomcat
        4:修改nginx文件（剔除backup  ，添加master 服务配置）
        5:reload nginx
        6:重启backup tomcat
        7:修改nginx文件（添加master以及backup服务配置）
        8:reload nginx
     F、启动健康检查服务
'''