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
import JsonFileFunc
import __projectupdate_double
import __projectupdate_onehalf
import __projectupdate_single
import HealthCheck

class ProjectUpdate(object):
    def __init__(self):
        self.projectName=None
        self.updateVersion=None
        self.updateTime=None
        self.updateType=None
        self.deploymentmode=None
        self.tomcatConf=None
        self.hostInfostr=None

def projectUpdate(projectName,updateVersion,updateType,updateTime):
    pu=ProjectUpdate()
    pu.projectName=projectName
    pu.updateVersion=updateVersion
    pu.updateType=updateType
    pu.updateTime=updateTime

    #A、关闭健康检查服务
    if HealthCheck.stopHealthCheck():
        pass
    else:
        FormatPrint.printFalat("stopHealthCheck is wrong")
    tomcatPath=sys.path[0] + os.sep + 'conf' + os.sep + 'tomcat-conf.json'
    pu.tomcatConf = JsonFileFunc.readFile(tomcatPath)
    if pu.tomcatConf is None:
        FormatPrint.printFalat('can not read tomcat-conf configure')
    if pu.projectName not in pu.tomcatConf['projectname']:
        FormatPrint.printFalat(str(pu.projectName)+' not configure in the tomcat-conf.json')
    pu.deploymentmode=pu.tomcatConf['projectname'][projectName]['deploymentmode']
    pu.hostInfostr=str(pu.tomcatConf['hostname'])+":"+str(pu.tomcatConf['serverip'])
    ##################调用服务
    if pu.deploymentmode == 'single':
        FormatPrint.printDebug("curent project is single deploymentmode")
        __projectupdate_single.process(pu)
    elif pu.deploymentmode =='onehalf':
        FormatPrint.printDebug("curent project is onehalf deploymentmode")
        __projectupdate_onehalf.process(pu)
    elif pu.deploymentmode == 'double':
        FormatPrint.printDebug("curent project is double deploymentmode")
        __projectupdate_double.process(pu)
    else:
        FormatPrint.printFalat(str(pu.projectName)+'project configure wrong deploymentmode ')

    #F、启动健康检查服务
    if HealthCheck.startHealthCheck():
        pass
    else:
        FormatPrint.printFalat("startHealthCheck is wrong")

'''
1、如果是single模式
    A、关闭健康检查服务
        B、读取配置文件
        C、初始化tomcatgroup-runstatus文件以及nginxgroup-runstatus文件
        D、替换资源
        E、重启tomcat
    F、启动健康检查服务
2、如果是onehalf模式
    A、关闭健康检查服务
    B、读取配置文件
    C、初始化tomcatgrup-runstatus文件以及nginxgroup-runstatus文件
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
3、如果是double模式
    A、关闭健康检查服务
    B、读取配置文件
    C、初始化tomcatgrup-runstatus文件以及nginxgroup-runstatus文件
        1、判断当前运行组
        2、配置tomcat信息为将运行组tomcat的信息
    D、替换资源
        1、判断当前运行组
        2、替换将被更新组配置的项目
    E、重启tomcat
        1、判断当前运行组
        2、重启将被更新组的tomcat
    F、启动健康检查服务
'''

'''
健康检查服务需要通过运行状态信息来处理
'''