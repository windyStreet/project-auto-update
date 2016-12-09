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
        if self.willUpdateGroup[0] == 'groupbackup':
            tomcat_conf = self.projectJson.tomcatConf
            tomcats = tomcat_conf['projectname'][self.projectName]['groupmaster']['tomcatgroupinfo']['tomcats']
            for tomcat in tomcats:
                self.sucessRestartTomcatTags.append(tomcat['tomcattag'])
        if self.willUpdateGroup[0] == 'groupmaster':
            tomcat_conf = self.projectJson.tomcatConf
            tomcats = tomcat_conf['projectname'][self.projectName]['groupbackup']['tomcatgroupinfo']['tomcats']
            for tomcat in tomcats:
                self.sucessRestartTomcatTags.append(tomcat['tomcattag'])

    #合并两次成共的tomcatTags
    def getMergeSucessTomcatsTags(self,firstSucessRestartTomcatTags,secondSucessRestartTomcatTags):
        #firstSucessRestartTomcatTags.extend(secondSucessRestartTomcatTags)
        #return firstSucessRestartTomcatTags
        return firstSucessRestartTomcatTags + secondSucessRestartTomcatTags

def process(projectJson):
    __puo = __projectupdate_onehalf()
    __puo.projectJson = projectJson
    __puo.hostInfostr = projectJson.hostInfostr
    __puo.projectName = projectJson.projectName
    __puo.updateVersion = projectJson.updateVersion
    __puo.updateTime = projectJson.updateTime
    __puo.updateType = projectJson.updateType
    __puo.deploymentmode = projectJson.deploymentmode

    if ResourceFunc.replceResource(__puo):
        #先进行初始化
        __puo.willUpdateGroup.append("groupmaster")
        __puo.willUpdateGroup.append("groupbackup")
        if NodeRunStatusFunc.initNodeHealthStatus(__puo, __puo.willUpdateGroup):
            del __puo.willUpdateGroup[:]#清空设置的将被更新的组
            __puo.willUpdateGroup.append("groupbackup")#设置将要被更新的组
            __puo.setSucessRestartTomcatTags()#设置成功更新的组的信息
            if NginxFunc.changeNginxConf(__puo.projectName,__puo.sucessRestartTomcatTags):#修改NG的配置
                if TomcatFunc.restartWillUpdateTomcatGroup(__puo):#重启将要被更新的组的信息
                    __puo.sucessRestartTomcatTags = __checkServiceIsOK.checkServiceIsOk(__puo)#检查服务是否可用
                    firstSucessRestartTomcatTags = __puo.sucessRestartTomcatTags
                    if len(__puo.sucessRestartTomcatTags) > 0:
                        if NginxFunc.changeNginxConf(__puo.projectName,__puo.sucessRestartTomcatTags):#重新设置NG配置 == 》 第一组跟新完毕,同时进行了切换
                            #重启第二组
                            del __puo.willUpdateGroup[:]  # 清空设置的将被更新的组
                            __puo.willUpdateGroup.append("groupmaster")  # 设置将要被更新的组(第二组)
                            if TomcatFunc.restartWillUpdateTomcatGroup(__puo):  # 重启将要被更新的组的信息(第二组)
                                __puo.sucessRestartTomcatTags = __checkServiceIsOK.checkServiceIsOk(__puo)  # 检查服务是否可用(第二组)
                                if len(__puo.sucessRestartTomcatTags) > 0:
                                    __puo.sucessRestartTomcatTags = __puo.getMergeSucessTomcatsTags(firstSucessRestartTomcatTags, __puo.sucessRestartTomcatTags)
                                    if NginxFunc.changeNginxConf(__puo.projectName,__puo.sucessRestartTomcatTags,"update"): # 重置ng配置文件
                                        FormatPrint.printInfo(" update finish ")
                                    else:
                                        FormatPrint.printFalat(" third change NG fail ")
                                else:
                                    FormatPrint.printFalat(" second check service is fail ")
                            else:
                                FormatPrint.printFalat(" second restart tomcat fail ")
                        else:
                            FormatPrint.printFalat(" second change NG fail ")
                    else:
                        FormatPrint.printFalat(" first check service is fail ")
                else:
                    FormatPrint.printFalat(" first restart tomcat fail ")
            else:
                FormatPrint.printFalat(" first change NG fail ")
        else:
            FormatPrint.printFalat(" can not init node-health-status file ")
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