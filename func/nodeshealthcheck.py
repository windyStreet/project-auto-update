#!/usr/bin/env python
#!-*- coding:utf-8 -*-
import FormatPrint
import sys
import json
import os
import time
import socket
import urllib2
import RungroupFunc

class NodesHealthCheck(object):
    def __init__(self):
        FormatPrint.printDebug("NodesHealthCheck")
        self.tomcatConf_JSON={}#tomcat组配置信息
        self.nodeHealthStatus_JSON={}#节点健康检查运行状态信息
        self.deploymentmode='double'#默认使用全组启动方式

    #初始化tomcatGroup配置运行信息
    def initTomcatRunStatus(self):
        FormatPrint.printInfo("初始化tomcatGroup配置运行信息")
        try:
            with open(sys.path[0]+os.sep+'conf'+os.sep+'tomcat-conf.json') as tomcat_conf_file:
                self.tomcatConf_JSON=json.load(tomcat_conf_file)
        except Exception as e:
            FormatPrint.printError("tomcat-conf.json 配置文件出错,请检查配置文件")
            FormatPrint.printError("错误描述:"+str(e))
            sys.exit(-1)

    # 初始化节点健康运行状态信息
    def initNodeHealthRunStatus(self):
        FormatPrint.printInfo("初始化节点健康运行状态信息")
        try:
            with open(sys.path[0] + os.sep + 'runtime' + os.sep + 'node-health-status.json', 'r') as health_status_file:
                self.nodeHealthStatus_JSON=json.load(health_status_file)
        except Exception:
            # file not exist, create it
            FormatPrint.printInfo("未检测到健康检查节点信息,将初始化该文件")
            node_health_status={}
            ProjectNodeRunInfo={}
            for projectName in self.tomcatConf_JSON["projectname"].keys():
                rungroup = RungroupFunc.getRunGroupName(projectName)
                projectHealthNodesInfo={}
                for tomcat in self.tomcatConf_JSON["projectname"][projectName][rungroup]["tomcatgroupinfo"]["tomcats"]:
                    healthCheckUrl = "http://" + tomcat["serviceip"] + ":" + tomcat["port"] +  self.tomcatConf_JSON["projectname"][projectName][rungroup]["servicecheckurl"]
                    healthCheckData = self.tomcatConf_JSON["projectname"][projectName][rungroup]["servicecheckpar"]
                    nodeInfo = {
                        'health-check-url': healthCheckUrl,
                        'health-check-data': healthCheckData,
                        'status': 'n/a',
                        'last-response-data': 'n/a',
                        'last-response-time': 0,
                        'fail-count': 0,
                        'last-check-time': time.strftime('%Y-%m-%d %H:%M:%S')
                    }
                    projectHealthNodesInfo[tomcat["name"]]=nodeInfo
                ProjectNodeRunInfo[projectName]=projectHealthNodesInfo
            node_health_status["projectname"] = ProjectNodeRunInfo
            with open(sys.path[0] + os.sep + 'runtime' + os.sep + 'node-health-status.json','w') as new_health_status_file:
                new_health_status_file.write(json.dumps(node_health_status, indent=4))
            self.nodeHealthStatus_JSON=node_health_status
        FormatPrint.printDebug("node-health-status.json文件信息为:"+str(self.nodeHealthStatus_JSON))

    #检查节点服务
    def checkNodeService(self):
        FormatPrint.printInfo("检查节点服务")
        socket.setdefaulttimeout(5)
        new_node_health_status=self.nodeHealthStatus_JSON
        for projectName in self.nodeHealthStatus_JSON["projectname"]:
            node_health_status= self.nodeHealthStatus_JSON["projectname"][projectName]
            for node_name in node_health_status.keys():
                node = node_health_status[node_name]
                status = node_health_status[node_name]['status']
                url = node_health_status[node_name]['health-check-url']
                request_data = node_health_status[node_name]['health-check-data']

                response = None
                ret_code = 502
                begin_time = time.time()

                try:
                    response = urllib2.urlopen(url, request_data)
                    #response = urllib.request.urlopen(url, request_data)
                except Exception as e:
                    FormatPrint.printWarn(str(projectName) + "-" + str(node_name)+"节点服务检查时出现异常:"+str(e))
                    if hasattr(e, 'code'):
                        ret_code = e.code
                finally:
                    end_time = time.time()
                    if response:
                        ret_data = response.read()
                        ret_code = response.code
                        response.close()

                        if isinstance(ret_data, bytes):
                            ret_data = bytes.decode(ret_data)

                    node['last-response-time'] = round((end_time - begin_time), 3)
                    node['last-check-time'] = time.strftime('%Y-%m-%d %H:%M:%S')
                    node['last-response-code'] = ret_code

                    if ret_code == 200:
                        FormatPrint.printInfo("节点正常:" + str(projectName) + "-" + str(node_name) )
                        node['status'] = 'running'
                        try:  # 重启失败时，status为0
                            node['last-response-data'] = json.loads(ret_data)
                            if node['last-response-data']['status'] != 1:
                                node['status'] = 'error'
                        except:
                            node['status'] = 'error'
                        if node['status'] == 'running':  # http返回码为200且服务返回status=1，才重置fail-count
                            node['fail-count'] = 0
                    elif node['status'] == 'running' or node['status'] == 'n/a':
                        node['status'] = 'error'

                    if node['status'] == 'error':
                        node['fail-count'] += 1
                        if node['fail-count'] >= 3:
                            node['status'] = 'dead'
                    elif node['status'] == 'dead':
                        node['fail-count'] += 1

                    if node['status'] == 'error':
                        FormatPrint.printWarn("节点故障:"+str(projectName)+"-" + str(node_name) + " has been detected ERROR for fail-count " + str(node['fail-count']))

                    if node['status'] == 'dead':
                        FormatPrint.printError("节点死亡"+str(projectName)+ "-" + str(node_name) + " has been detected DEAD for fail-count " + str( node['fail-count']))

                node_health_status[node_name]=node
            new_node_health_status["projectname"][projectName]=node_health_status
        with open(sys.path[0] + os.sep + 'runtime' + os.sep + 'node-health-status.json', 'w') as new_health_status_file:
            new_health_status_file.write(json.dumps(new_node_health_status, indent=4))

#服务节点健康检查
def nodesHealthCheck():
    FormatPrint.printDebug("服务节点健康检查启动")
    NH = NodesHealthCheck()
    NH.initTomcatRunStatus()
    NH.initNodeHealthRunStatus()
    NH.checkNodeService()
    FormatPrint.printDebug("服务节点健康检查完毕")
#启动节点健康检查服务
def startNodeHealthCheck():
    FormatPrint.printInfo("启动节点健康检查服务")
#关闭节点健康检查服务
def killNodeHealthCheck():
    FormatPrint.printInfo("关闭节点健康检查服务")
