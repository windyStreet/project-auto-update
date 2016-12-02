#!/usr/bin/env python
#!-*- coding:utf-8 -*-

import time
import  FormatPrint
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
def initNodeHealthStatus(pu):
    projecName = pu.projectName
    tomcat_conf = pu.projectJson.tomcatConf
    tomcatGroup = pu.willUpdateGroup
    deploymentmode = pu.deploymentmode
    tomcatTags = tomcat_conf['projectname'][projecName][tomcatGroup]['tomcats']
    servicecheckurl = tomcat_conf['projectname'][projecName][tomcatGroup]['servicecheckurl']
    servicecheckpar = tomcat_conf['projectname'][projecName][tomcatGroup]['servicecheckpar']
    currentRunGroup = pu.willUpdateGroup()

    node_health_status = {}
    node_health_status['currentrun'] = currentRunGroup
    node_health_status['deploymentmode'] = deploymentmode

    for tomcat in tomcatTags:
        node_name = tomcat['tomcattag']
        health_check_url = "http://" + tomcat["serviceip"] + ":" + tomcat["port"] + str(servicecheckurl)
        node_health_status[node_name] = {
            'health-check-url': health_check_url,
            'health-check-data': servicecheckpar,
            'status': 'n/a',
            'last-response-data': 'n/a',
            'last-response-time': 0,
            'fail-count': 0,
            'last-check-time': time.strftime('%Y-%m-%d %H:%M:%S')
        }
    return node_health_status

# modify node-health-status file
def modifyNodeHealthStatus(pu):
    projecName = pu.projectName
    tomcat_conf = pu.projectJson.tomcatConf
    tomcatGroup = pu.willUpdateGroup
    deploymentmode = pu.deploymentmode
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

