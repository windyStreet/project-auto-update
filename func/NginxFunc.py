#!/usr/bin/env python
#!-*- coding:utf-8 -*-

import FormatPrint
import os
import JsonFileFunc
import sys

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
    return True
    if os.system(cmd) == 0:
        FormatPrint.printInfo("reload ngninx sucess")
        return True
    else:
        FormatPrint.printError("reload ngninx error ")
        return False

#获取upstream lsit 信息
def getUpstreamList(nodehealthstatus,sucessRestartTomcatTags):
    upstreamList=[]
    for tomcatTag in sucessRestartTomcatTags:
        upstreamList.append(nodehealthstatus['nodeinfo'][tomcatTag]['upstream-str'])
    return upstreamList

#修改nginx配置文件
def changeNginxConf(projectName,sucessRestartTomcatTags):
    path = sys.path[0] + os.sep + 'runtime' + os.sep + str(projectName) + '-node-health-status.json'
    nodehealthstatus = JsonFileFunc.readFile(path)

    upstreamName = nodehealthstatus['upstreamName']
    nginxConfPath = nodehealthstatus['nginxConfPath']
    nginxreloadcmd = nodehealthstatus['nginxreloadcmd']
    nginxreplacestarttag = nodehealthstatus['nginxreplacestarttag']
    nginxreplaceendtag = nodehealthstatus['nginxreplaceendtag']
    nginxrootstarttag = nodehealthstatus['nginxrootstarttag']
    nginxrootendtag = nodehealthstatus['nginxrootendtag']
    nginxrootconf = nodehealthstatus['nginxrootconf']

    upstreamList=getUpstreamList(nodehealthstatus,sucessRestartTomcatTags)

    FormatPrint.printInfo("tomcat重启完成，修改nginx配置")
    '''
    1、读取配置，读取开始标识和结束标识
    2、生成修改部分内容
    3、循环读取配置文件，找到开始标识和结束标识
    4、替换开始标识和结束标识之间的内容
    '''
    upstream_conf = nginxreplacestarttag + '\n'
    upstream_conf += '\tupstream ' + upstreamName + '\n\t{\n'
    for upstreamStr in upstreamList:
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