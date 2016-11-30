#!/usr/bin/env python
#!-*- coding:utf-8 -*-

import FormatPrint
import sys
import json
import os
import time
import RungroupFunc
import TomcatFunc
import NginxFunc

class NginxUpstreamEdit(object):
    def __init__(self):
        FormatPrint.printInfo("NginxUpstreamEdit")
        self.tomcatConf_JSON=None
        self.nodeHealthStatus_JSON=None
        self.upstreamStatus_JSON=None

    #初始化基本数据
    def init(self):
        FormatPrint.printInfo("健康检查修改nginx文件初始化")
        try:
            with open(sys.path[0]+os.sep+'conf'+os.sep+'tomcat-conf.json','r') as tomcat_conf_file:
                self.tomcatConf_JSON=json.load(tomcat_conf_file)
        except Exception as e:
            FormatPrint.printFalat("健康检查修改nginx文件初始化,初始化tomcat-conf.json文件,出现错误"+str(e))
            sys.exit(-1)
        try:
            with open(sys.path[0]+os.sep + 'runtime' + os.sep + 'node-health-status.json','r') as node_health_status_file:
                self.nodeHealthStatus_JSON = json.load(node_health_status_file)
        except Exception as e:
            FormatPrint.printFalat("健康检查修改nginx文件初始化,初始化node-healtah-status.json文件,出现错误"+str(e))
            sys.exit(-1)

    #初始化upstream运行状态
    def initUpstreamRunstatus(self):
        FormatPrint.printInfo("初始化upstream运行状态")
        try:
            with open(sys.path[0]+os.sep+'runtime'+os.sep+'upstream-status.json','r') as upstream_status_file:
                self.upstreamStatus_JSON=json.load(upstream_status_file)
        except Exception as e:
            FormatPrint.printWarn("初始化upstream运行状态，出现异常:"+str(e)+"即将创建")
            upstream_status={}
            upstream_statu={}
            for projectName in self.nodeHealthStatus_JSON["projectname"].keys():
                nodeInfos=self.nodeHealthStatus_JSON["projectname"][projectName]
                upstream_infos={}
                for nodeName in nodeInfos.keys():
                    nodeInfo=nodeInfos[nodeName]
                    upstream_infos[nodeName] = {
                        'last-status': 'running',
                        'is-in-upstream': True,
                        'is-rebooting': False,
                        'rebooting-count': 0,
                        'last-check-time': time.strftime('%Y-%m-%d %H:%M:%S')
                    }
                upstream_statu[projectName]=upstream_infos
            upstream_status["projectname"]=upstream_statu
            self.upstreamStatus_JSON=upstream_status
            with open(sys.path[0] + os.sep + 'runtime' + os.sep + 'upstream-status.json', 'w') as new_upstream_status_file:
                new_upstream_status_file.write(json.dumps(self.upstreamStatus_JSON, indent=4))
    #检查upstream
    def checkUpstream(self):
        FormatPrint.printInfo("检查upstream")
        '''
            此处不循环检查配置，只用于修改upstream的状态，对node-health-status 做进一步处理
        '''
        new_upstreamstatus_file={}
        new_upstreamstatus={}
        for projectName in self.nodeHealthStatus_JSON["projectname"].keys():
            upstream_status=None
            rungroupInfo=None
            rungroup = RungroupFunc.getRunGroupName(projectName)
            rungroupInfo = self.tomcatConf_JSON["projectname"][projectName][rungroup]
            #####################################################################
            node_health_status = self.nodeHealthStatus_JSON["projectname"][projectName]
            #####################################################################
            alive_count = 0
            alive_nodes = []
            dead_count = 0
            dead_nodes = []
            upstream_changed = False


            for node_name in sorted(node_health_status.keys()):
                if node_health_status[node_name]['status'] == 'running' or node_health_status[node_name]['status'] == 'error' or  node_health_status[node_name]['status'] == 'n/a':
                    alive_count += 1
                    alive_nodes.append(node_name)

                if node_health_status[node_name]['status'] == 'dead':
                    dead_nodes.append(node_name)
                    dead_count += 1
                #####################################################################
                upstream_status=self.upstreamStatus_JSON["projectname"][projectName]
                #####################################################################
                if (upstream_status[node_name]['last-status'] == 'running' or upstream_status[node_name]['last-status'] == 'error' or upstream_status[node_name]['last-status'] == 'n/a') and node_health_status[node_name]['status'] == 'dead':
                    upstream_changed = True
                if upstream_status[node_name]['last-status'] == 'dead' and node_health_status[node_name]['status'] == 'running':
                    upstream_changed = True
            if alive_count == 0:
                FormatPrint.printFalat(" - no alive node, abort upstream edit.")
            elif upstream_changed:
                startReplaceTag=rungroupInfo["nginxreplacestarttag"]
                endReplaceTag=rungroupInfo["nginxreplaceendtag"]
                nginx_reload_cmd=rungroupInfo["nginxreloadcmd"]
                nginx_conf_path=rungroupInfo["nginxconfpath"]
                upstreamname=rungroupInfo["upstreamname"]

                upstream_conf = startReplaceTag + '\n'
                upstream_conf += '\tupstream ' + upstreamname + '\n\t{\n'
                for tomcatinfo in rungroupInfo["tomcatgroupinfo"]["tomcats"]:
                    for alivenode in alive_nodes:
                        if tomcatinfo["name"] == alivenode:
                            upstream_conf += '\t\tserver ' + tomcatinfo['upstreamip'] + ':' + tomcatinfo["port"] + ' max_fails=5 fail_timeout=60s weight=' + tomcatinfo["upstreamweight"] + ';\n'
                upstream_conf += '\t}\n'
                upstream_conf=upstream_conf.decode("utf-8")
                FormatPrint.printInfo("修改的nginx的配置文件如下:")
                FormatPrint.printInfo(upstream_conf)
                try:
                    confstr = ""
                    with open(nginx_conf_path, 'r') as nginx_conf_temp_file:
                        isContinue = False
                        for line in nginx_conf_temp_file:
                            line=line.decode("utf-8")
                            # 找到这个标识，结束continue,追加上述字符串
                            if line.find(endReplaceTag) != -1:
                                isContinue = False
                                confstr += upstream_conf
                            if isContinue or line.find(startReplaceTag) != -1:
                                isContinue = True
                                continue
                            confstr += line
                    with open(nginx_conf_path, 'w') as nginx_conf_file:
                        nginx_conf_file.write(confstr.encode("utf-8"))
                except Exception as e:
                    FormatPrint.printError("修改配置nginx配置文件出错,错误信息如下:\n" + str(e))
                    pass
                NginxFunc.reloadNginx(nginx_reload_cmd)
            latest_upstream_status = {
                'total-node-count': alive_count + dead_count,
                'upstream-node-count': alive_count
            }

            for alive_node_key in alive_nodes:
                latest_upstream_status[alive_node_key] = {
                    'last-status': node_health_status[alive_node_key]['status'],
                    'is-in-upstream': True,
                    'is-rebooting': False,
                    'rebooting-count': 0,
                    'last-check-time': time.strftime('%Y-%m-%d %H:%M:%S')
                }

            #定义列表，查询nodekey使用
            tomcatTageList = {}
            for tomcat in rungroupInfo["tomcatgroupinfo"]["tomcats"]:
                tomcatTageList[tomcat["name"]] = tomcat["tomcattag"]

            for dead_node_key in dead_nodes:
                is_rebooting = True
                rebooting_count = upstream_status[dead_node_key]['rebooting-count']
                if upstream_status[dead_node_key]['is-rebooting'] is False:
                    FormatPrint.printInfo(' - restart dead node ' + str(dead_node_key))
                    tomcatstartscriptpath = rungroupInfo["tomcatstartscriptpath"]
                    tomcatkillscriptpath=rungroupInfo["tomcatkillscriptpath"]
                    TomcatFunc.restartTomcat(tomcatstartscriptpath,tomcatkillscriptpath,tomcatTageList[dead_node_key])
                else:
                    rebooting_count += 1
                    FormatPrint.printInfo("- dead node "  + str(dead_node_key) +' is in rebooting count: ' + str(rebooting_count))
                    if rebooting_count % 5 == 0:
                        is_rebooting = False

                latest_upstream_status[dead_node_key] = {
                    'last-status': node_health_status[dead_node_key]['status'],
                    'is-in-upstream': False,
                    'is-rebooting': is_rebooting,
                    'rebooting-count': rebooting_count,
                    'last-check-time': time.strftime('%Y-%m-%d %H:%M:%S')
                }
            new_upstreamstatus[projectName]=latest_upstream_status
        new_upstreamstatus_file["projectname"]=new_upstreamstatus
        with open(sys.path[0] + os.sep + 'runtime' + os.sep + 'upstream-status.json', 'w') as new_upstream_status_file:
            new_upstream_status_file.write(json.dumps(new_upstreamstatus_file, indent=4))

def nginxUpstreamEdit():
    NUE=NginxUpstreamEdit()
    NUE.init()
    NUE.initUpstreamRunstatus()
    NUE.checkUpstream()