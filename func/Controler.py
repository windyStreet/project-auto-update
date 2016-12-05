#!/usr/bin/env python
#!-*- coding:utf-8 -*-

import projectupdate
import FormatPrint
import getopt
import sys
import TomcatFunc
import HealthCheck

method=None
projectName=None
projectVersion=None
tomcatTag=None
path=None
command=None
time=None

#项目更新
def update():
    FormatPrint.printInfo("更新项目" + str(projectName) + "更新版本" + str(projectVersion))
    #更新项目
    projectupdate.projectUpdate(projectName, projectVersion,"update",time)

#项目回滚
def rollBack():
    FormatPrint.printInfo("更新回滚" + str(projectName) + "回滚版本" + str(projectVersion))
    projectupdate.projectUpdate(projectName, projectVersion,"rollback")

#启动tomcat
def tomcatStart():
    FormatPrint.printDebug("tomcatStart")
    FormatPrint.printInfo("启动tocmat"+str(tomcatTag))
    TomcatFunc.restartTomcat(path,tomcatTag)

#关闭tomcat
def tomatKill():
    FormatPrint.printDebug("tomatKill")
    FormatPrint.printInfo("关闭tocmat"+str(tomcatTag))
    TomcatFunc.killTomcat(path,tomcatTag)

#启动健康检查服务
def startHealthCheck():
    FormatPrint.printDebug("startHealCheck")
    if HealthCheck.startHealthCheck():
        FormatPrint.printInfo("启动健康检查服务成功")
    else:
        FormatPrint.printInfo("启动健康检查服务失败")

#关闭健康检查服务
def stopHealthCheck():
    FormatPrint.printDebug("stopHealthCheck")
    if HealthCheck.stopHealthCheck():
        FormatPrint.printInfo("关闭健康检查服务成功")
    else:
        FormatPrint.printInfo("关闭健康检查服务失败")

#重启健康检查服务
def restartHealthCheck():
    FormatPrint.printDebug("restartHealthCheck")
    if HealthCheck.restartHealthCheck():
        FormatPrint.printInfo("重启健康检查服务成功")
    else:
        FormatPrint.printInfo("重启健康检查服务失败")

#一次性健康检查服务
def healthCheckOnce():
    FormatPrint.printDebug("startHealthCheckOnce")
    if HealthCheck.checkOnce():
        FormatPrint.printInfo("一次性健康检查服务成功")
    else:
        FormatPrint.printInfo("一次性健康检查服务失败")

#多次性健康检查服务
def healthCheckAll():
    FormatPrint.printDebug("healthCheckAll")
    if HealthCheck.checkAllTime():
        FormatPrint.printInfo("多次性健康检查服务成功")
    else:
        FormatPrint.printInfo("多次性健康检查服务失败")

def healthCheckStatus():
    FormatPrint.printDebug("healthCheckStatus")
    HealthCheck.healthCheckStatus()

#帮助
def help():
    print ("-h,--help")
    print ("-m:,--method=,will be run method:update|rollBack|tomcatStart|tomatKill|startHealthCheck|stopHealthCheck|restartHealthCheck|healthCheckOnce|healthCheckAll|healthCheckStatus")
    print ("-u:,--update=,specify update project name")
    print ("-r:,--roolback=,specify roolback project name")
    print ("-v:,--version=,specify projectupdate version number")
    print ("-k:,--killtomcat=,specify close tomcattag")
    print ("-s:,--starttomcat=,specify start tomcattag ")
    print ("-p:,--path=,specify a detail path")
    print ("-c:,--command=,shell command")
    print ("-P:,--Project=,project name")
    print ("-t:,--Time=,project update time")

operator =\
{
    'update':update,
    'rollback':rollBack,
    'help':help,
    'starttomcat':tomcatStart,
    'killtomcat':tomatKill,
    'update':update,
    'rollBack':rollBack,
    'tomcatStart':tomcatStart,
    'tomatKill':tomatKill,
    'startHealthCheck':startHealthCheck,
    'stopHealthCheck':stopHealthCheck,
    'restartHealthCheck':restartHealthCheck,
    'healthCheckOnce':healthCheckOnce,
    'healthCheckAll':healthCheckAll,
    'healthCheckStatus':healthCheckStatus
}

options,args = getopt.getopt(sys.argv[1:],"hu:r:v:k:s:p:c:m:P:t:",["help","update=","rollback=","version=","killtomcat=","starttomcat=","path=","command=","method=","Project=","Time="])

method = "help"
if len(options) <=0:
    method = "help"
else:
    for name, value in options:
        if name in ['-h', '--help']:
            method = "help"
        if name in ['-u','--update']:
            method = "update"
            if value == None or str(value).startswith("-"):
                FormatPrint.printInfo("-u:--update需要参数projectname")
                sys.exit(1)
            projectName = value
        elif name in ['-r','--rollback']:
            method = "rollback"
            if value == None or str(value).startswith("-"):
                FormatPrint.printInfo("-r:--rollback需要参数projectname")
                sys.exit(1)
            projectName = value
        elif name in ['-v','--version=']:
            if value == None or str(value).startswith("-"):
                FormatPrint.printInfo("-v:--version需要参数projectVersion")
                sys.exit(1)
            projectVersion = value
        elif name in ['-k','--killtomcat']:
            method = "killtomcat"
            if value == None or str(value).startswith("-"):
                FormatPrint.printInfo("-k:--killtomcat需要参数tomcatTag")
                sys.exit(1)
            tomcatTag = value
        elif name in ['-s','--starttomcat']:
            method = "starttomcat"
            if value == None or str(value).startswith("-"):
                FormatPrint.printInfo("-s:--starttomcat需要参数tomcatTag")
                sys.exit(1)
            tomcatTag = value
        elif name in ['-p','--path=']:
            if value == None or str(value).startswith("-"):
                FormatPrint.printInfo("-p:--path需要参数filepath")
                sys.exit(1)
            path = value
        elif name in ['-c','--command=']:
            if value == None or str(value).startswith("-"):
                FormatPrint.printInfo("-c:--command需要参数command")
                sys.exit(1)
            command = value
        elif name in ['-m','--method=']:
            if value == None or str(value).startswith("-"):
                FormatPrint.printInfo("-m:--method需要参数method")
                sys.exit(1)
            method = value
        elif name in ['-P', '--Project=']:
            if value == None or str(value).startswith("-"):
                FormatPrint.printInfo("-P:--Project需要参数projectname")
                sys.exit(1)
            projectName = value
        elif name in ['-t', '--Time=']:
            if value == None or str(value).startswith("-"):
                FormatPrint.printInfo("-t:--Time需要参数timestamp")
                sys.exit(1)
            time = value
        else:
            method = "help"
operator.get(method)()
