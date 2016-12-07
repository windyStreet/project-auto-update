#!/usr/bin/env python
#!-*- coding:utf-8 -*-
import FormatPrint
import sys
import json
import os
import time
import socket
import urllib2
import JsonFileFunc

class NodesHealthCheck(object):
    def __init__(self):
        self.projectName = None
        self.runtimes = 1

    #检查节点服务
    def checkNodeService(self):
        FormatPrint.printInfo("check nginx-tomcat node service is " + str(self.runtimes))
        self.runtimes = int(self.runtimes) + 1

        socket.setdefaulttimeout(5)

        path = sys.path[0] + os.sep + 'runtime' + os.sep + str(self.projectName) + '-node-health-status.json'
        nodeHealthStatus = JsonFileFunc.readFile(path)

        for node_name in nodeHealthStatus['nodeinfo'].keys():
            node = nodeHealthStatus[node_name]
            url = nodeHealthStatus[node_name]['health-check-url']
            request_data = nodeHealthStatus[node_name]['health-check-data']

            response = None
            ret_code = 502
            begin_time = time.time()

            try:
                response = urllib2.urlopen(url, request_data)
                #response = urllib.request.urlopen(url, request_data)
            except Exception as e:
                FormatPrint.printWarn(str(self.projectName) + "-" + str(node_name)+"service node exception:"+str(e))
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
                    FormatPrint.printInfo("节点正常:" + str(self.projectName) + "-" + str(node_name) )
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
                    FormatPrint.printWarn("node error:"+str(self.projectName)+"-" + str(node_name) + " has been detected ERROR for fail-count " + str(node['fail-count']))

                if node['status'] == 'dead':
                    FormatPrint.printError("node dead"+str(self.projectName)+ "-" + str(node_name) + " has been detected DEAD for fail-count " + str( node['fail-count']))
            nodeHealthStatus['nodeinfo'][node_name] = node
        JsonFileFunc.createFile(path, nodeHealthStatus)

#服务节点健康检查
def nodesHealthCheck(projectName):
    nh = NodesHealthCheck()
    nh.projectName = projectName
    nh.checkNodeService()
