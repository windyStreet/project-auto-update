#!/usr/bin/env python
#!-*- coding:utf-8 -*-

import time
import FormatPrint
import JsonFileFunc
import sys
import os
class NodeRunStatusFunc(object):
    def __init__(self):
        pass


'''
    "1": {
        "status": "n/a",
        "health-check-url": "http://220.231.252.72:64001/LSIP/restservices/servicecheck/oamp_checkTomcatAvailable/query",
        "last-response-data": "n/a",
        "last-response-time": 0,
        "fail-count": 0,
        "last-check-time": "2016-12-01 16:37:09",
        "health-check-data": "{\"service\":\"timeservice\",\"version\":\"1.0.0\"}"
    },
    "2": {
        "status": "n/a",
        "health-check-url": "http://220.231.252.72:64002/LSIP/restservices/servicecheck/oamp_checkTomcatAvailable/query",
        "last-response-data": "n/a",
        "last-response-time": 0,
        "fail-count": 0,
        "last-check-time": "2016-12-01 16:37:09",
        "health-check-data": "{\"service\":\"timeservice\",\"version\":\"1.0.0\"}"
    },
    "currentrun": "groupmaster",
    "deploymentmode": "single"
'''

#init node-health-status file
'''
初始化node-health-status
'''
def initNodeHealthStatus(pu,groups):
    projectName = pu.projectName
    tomcatGroup = pu.willUpdateGroup
    currentRunGroup = pu.willUpdateGroup

    tomcat_conf = pu.projectJson.tomcatConf
    newTomcats = []
    for group in groups:
        tomcats = tomcat_conf['projectname'][projectName][group]['tomcatgroupinfo']['tomcats']
        for tomcat in tomcats:
            newTomcats.append(tomcat)
    servicecheckurl = tomcat_conf['projectname'][projectName][tomcatGroup[0]]['servicecheckurl']
    servicecheckpar = tomcat_conf['projectname'][projectName][tomcatGroup[0]]['servicecheckpar']

    upstreamName = tomcat_conf['projectname'][projectName][tomcatGroup[0]]['upstreamname']
    nginxConfPath = tomcat_conf['projectname'][projectName][tomcatGroup[0]]['nginxconfpath']
    nginxreloadcmd = tomcat_conf['projectname'][projectName][tomcatGroup[0]]['nginxreloadcmd']
    nginxreplacestarttag = tomcat_conf['projectname'][projectName][tomcatGroup[0]]['nginxreplacestarttag']
    nginxreplaceendtag = tomcat_conf['projectname'][projectName][tomcatGroup[0]]['nginxreplaceendtag']
    nginxrootstarttag = tomcat_conf['projectname'][projectName][tomcatGroup[0]]['nginxrootstarttag']
    nginxrootendtag = tomcat_conf['projectname'][projectName][tomcatGroup[0]]['nginxrootendtag']
    nginxrootconf = tomcat_conf['projectname'][projectName][tomcatGroup[0]]['nginxrootconf']
    tomcatstartscriptpath = tomcat_conf['projectname'][projectName][tomcatGroup[0]]['tomcatstartscriptpath']
    tomcatkillscriptpath = tomcat_conf['projectname'][projectName][tomcatGroup[0]]['tomcatkillscriptpath']

    node_health_status = {}
    node_health_status['currentrun'] = currentRunGroup
    node_health_status['upstreamName'] = upstreamName
    node_health_status['nginxConfPath'] = nginxConfPath
    node_health_status['nginxreloadcmd'] = nginxreloadcmd
    node_health_status['nginxreplacestarttag'] = nginxreplacestarttag
    node_health_status['nginxreplaceendtag'] = nginxreplaceendtag
    node_health_status['nginxrootstarttag'] = nginxrootstarttag
    node_health_status['nginxrootendtag'] = nginxrootendtag
    node_health_status['nginxrootconf'] = nginxrootconf
    node_health_status['tomcatstartscriptpath'] = tomcatstartscriptpath
    node_health_status['tomcatkillscriptpath'] = tomcatkillscriptpath
    node_health_status['nodeinfo']={}

    for tomcat in newTomcats:
        node_name = tomcat['tomcattag']
        health_check_url = "http://" + tomcat["serviceip"] + ":" + tomcat["port"] + str(servicecheckurl)
        upstreamStr = "server " + str(tomcat['upstreamip']) + ":" + str(tomcat["port"]) + " max_fails=5 fail_timeout=60s weight=" + str(tomcat['upstreamweight'])+";"
        nodeDetail = {
            'health-check-url': health_check_url,
            'health-check-data': servicecheckpar,
            'status': 'n/a',
            'last-response-data': 'n/a',
            'last-response-time': 0,
            'fail-count': 0,
            'last-check-time': time.strftime('%Y-%m-%d %H:%M:%S'),
            "upstream-str": str(upstreamStr)
        }
        node_health_status['nodeinfo'][node_name] = nodeDetail
    path = sys.path[0] + os.sep + 'runtime' + os.sep + str(projectName) +'-node-health-status.json'
    JsonFileFunc.createFile(path, node_health_status)
    return True

# modify node-health-status file
'''
修改nodehealthstatus 文件内容
注：修改过程为每次重新初始化该文件（避免修改过程过程比较繁琐），且在onehalf模式中存在不同组中的数据进行组合问题
'''
def modifyNodeHealthStatus(pu):
    projecName = pu.projectName
    deploymentmode = pu.deploymentmode
    tomcatGroup = pu.willUpdateGroup

    tomcat_conf = pu.projectJson.tomcatConf
    tomcatTags = tomcat_conf['projectname'][projecName][tomcatGroup]['tomcatgroupinfo']['tomcats']
    servicecheckurl = tomcat_conf['projectname'][projecName][tomcatGroup]['servicecheckurl']
    servicecheckpar = tomcat_conf['projectname'][projecName][tomcatGroup]['servicecheckpar']
    currentRunGroup = pu.willUpdateGroup

    if deploymentmode == 'single':
        FormatPrint.printError(" you must be joking , no posslible ")
    elif deploymentmode == 'onehalf':
        FormatPrint.printInfo(" onehalf mode modify node-health-status ")
    elif deploymentmode == 'double':
        FormatPrint.printInfo(" double mode modify node-health-status ")
    else:
        FormatPrint.printFalat(" you must bu configure worng deploymentmode ")

