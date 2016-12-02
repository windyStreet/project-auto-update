#!/usr/bin/env python
#!-*- coding:utf-8 -*-

import FormatPrint
import os
import __projectupdate_double
class NginxFunc(object):
    def __init__(self):
        pass

#关闭nginx
def killNginx(cmd):
    FormatPrint.printInfo("关闭nginx")
    FormatPrint.printInfo("执行命令:"+str(cmd))
    if os.system(cmd) == 0:
        FormatPrint.printInfo("关闭nginx成功")
        return True
    else:
        FormatPrint.printInfo("关闭nginx失败")
        return False

#启动nginx
def startNginx(cmd):
    FormatPrint.printInfo("启动nginx")
    FormatPrint.printInfo("执行命令:"+str(cmd))
    if os.system(cmd) == 0:
        FormatPrint.printInfo("启动nginx成功")
        return True
    else:
        FormatPrint.printInfo("启动nginx失败")
        return False
#重载nginx
def reloadNginx(cmd):
    FormatPrint.printInfo("exec command:"+str(cmd))
    if os.system(cmd) == 0:
        FormatPrint.printInfo("reload ngninx sucess")
        return True
    else:
        FormatPrint.printError("reload ngninx error ")
        return False

#获取upstream lsit 信息
def getUpstreamList(projecName,tomcat_conf,tomcatGroup,tomcatTags):
    upstreamList=[]
    tomcats = tomcat_conf['projectname'][projecName][tomcatGroup]['tomcats']
    for tomcatInfo in tomcats:
        for tomcatTag in tomcatTags:
            if tomcatTag == tomcatInfo['tomcattag']:
                upstreamStr = 'server ' + tomcatInfo['upstreamip'] + ':' + tomcatInfo["port"] + ' max_fails=5 fail_timeout=60s weight=' + tomcatInfo["upstreamweight"] + ';'
                upstreamList.append(upstreamStr)
    return upstreamList

#修改nginx配置文件
def changeNginxConf(pu):
    #1、获取ng配置文件路径
    #2、生成需要修改的upstream
    #3、reloadNginx()

    projecName=pu.projecName
    tomcat_conf = pu.projectJson
    tomcatGroup = pu.willUpdateGroup
    tomcatTags = pu.sucessRestartTomcatTags

    upstreamName = tomcat_conf['projectname'][projecName][tomcatGroup]['upstreamname']
    nginxConfPath = tomcat_conf['projectname'][projecName][tomcatGroup]['nginxconfpath']
    nginxreloadcmd = tomcat_conf['projectname'][projecName][tomcatGroup]['nginxreloadcmd']
    nginxreplacestarttag = tomcat_conf['projectname'][projecName][tomcatGroup]['nginxreplacestarttag']
    nginxreplaceendtag = tomcat_conf['projectname'][projecName][tomcatGroup]['nginxreplaceendtag']
    nginxrootstarttag = tomcat_conf['projectname'][projecName][tomcatGroup]['nginxrootstarttag']
    nginxrootendtag = tomcat_conf['projectname'][projecName][tomcatGroup]['nginxrootendtag']
    nginxrootconf = tomcat_conf['projectname'][projecName][tomcatGroup]['nginxrootconf']
    upstreamList=getUpstreamList(projecName,tomcat_conf,tomcatGroup,tomcatTags)
    FormatPrint.printInfo("tomcat重启完成，修改nginx配置")
    '''
    1、读取配置，读取开始标识和结束标识
    2、生成修改部分内容
    3、循环读取配置文件，找到开始标识和结束标识
    4、替换开始标识和结束标识之间的内容
    '''
    upstream_conf = nginxreplacestarttag + '\n'
    upstream_conf += '\tupstream ' + upstreamName + '\n\t{\n'
    for upstreamStr in upstreamList :
        upstream_conf += '\t\t'+upstreamStr+'\n'
    upstream_conf += '\t}\n'
    upstream_conf = upstream_conf.decode('utf-8')
    root_conf = nginxrootstarttag + '\n'
    root_conf += nginxrootconf
    root_conf = root_conf.decode('utf-8')
    FormatPrint.printInfo("修改的nginx的upstream配置文件如下:\n" + upstream_conf.encode('utf-8'))
    FormatPrint.printInfo("修改的nginx的root路径配置文件如下:\n" + root_conf.encode('utf-8'))
    confstr = ""

    try:
        with open(nginxConfPath, 'r') as nginx_conf_temp_file:
            isContinue = False
            isRooTContinue = False
            for line in nginx_conf_temp_file:
                line = line.decode('utf-8')
                # 找到这个标识,修改upstream内容
                if line.find(nginxreplaceendtag) != -1:
                    isContinue = False
                    confstr += upstream_conf
                if isContinue or line.find(nginxreplacestarttag) != -1:
                    isContinue = True
                    continue
                # 找到这个标识,修改root内容
                if line.find(nginxrootendtag) != -1:
                    isRooTContinue = False
                    confstr += root_conf
                if isRooTContinue or line.find(nginxrootstarttag) != -1:
                    isRooTContinue = True
                    continue
                confstr += line
    except Exception as e:
        FormatPrint.printError("读取配置nginx配置文件出错,错误信息如下:\n" + str(e))
        return False
    try:
        with open(nginxConfPath, 'w') as nginx_conf_file:
            nginx_conf_file.write(confstr.encode('utf-8'))
    except Exception as e:
        FormatPrint.printError("修改配置nginx配置文件出错,错误信息如下:\n" + str(e))
        return False
    if reloadNginx(nginxreloadcmd):
        return True
    else:
        return False