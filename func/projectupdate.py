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

class ProjectUpdate(object):
    def __init__(self,projectName):
        self.projectName = projectName#当前运行项目名称
        self.projectUpdateVersion = 0#将被更新的版本
        self.conf_JSON={}#配置文件信息
        self.projectConf_JSON={}#当前项目的配置信息
        self.crurentProjectRunTomcatGroup_JSON = {}  # 当前项目运行的tomcat组全部信息
        self.runTomcatGroup_JSON={}#当前运行中的tomcat组信息
        self.crurentProjectRunNginxGroup_JSON = {}#当前项目运行的nginx组全部信息
        self.runNginxGroup_JSON={}#当前运行中的nginx信息
        self.runState_INT=0#当前运行状态
        self.runGroup=""#当前运行的组 groupmaster  groupbackup
        self.willBeUpdatedGroup=""#将被更新的组 groupbackup  groupmaster
        self.willBeUpdateTomcatGroup_JSON={} #将被更新的tomcat组全部信息
        self.sucessRestartTomcats=[]
        self.tomcatStartScriptPath=None
        self.tomcatKillScriptPath=None
        self.tomcatResourceUpdateScriptPath=None
        self.updateType="update"#更新类型 “update” “rollback”
        self.updateTime="19700101"
        self.deploymentmode="double"#部署方式double(全组启动方式),single（单项目启动方式）,onehalf（半启动方式），默认采用全组启动方式

    # 读取配置文件
    def readConfig(self):
        FormatPrint.printInfo("读取配置文件:readConfig")
        with open(sys.path[0] + os.sep + 'conf' + os.sep + 'tomcat-conf.json', 'r') as tomcat_conf:
            self.conf_JSON = json.load(tomcat_conf)
            FormatPrint.printDebug("当前配置文件信息为:"+str(self.conf_JSON))
            if self.projectName in self.conf_JSON["projectname"].keys():
                self.projectConf_JSON=self.conf_JSON["projectname"][self.projectName]
                self.deploymentmode=self.conf_JSON["projectname"][self.projectName]["deploymentmode"]
                FormatPrint.printDebug("当前操作项目的配置文件信息为:" + str(self.projectConf_JSON))
            else:
                FormatPrint.printFalat("不存在"+str(self.projectName)+"项目配置信息,中断更新")
                sys.exit(-1)
    #初始化tomcat运行组数据
    def initRunTomcatGroup(self):
        FormatPrint.printInfo("初始化tomcat运行组数据")
        try:
            with open(sys.path[0] + os.sep + 'runtime' + os.sep + 'tomcat-group-runstatus.json','r') as tomcat_run_status_file:
                self.crurentProjectRunTomcatGroup_JSON = json.load(tomcat_run_status_file)["projectname"][self.projectName]
                currentRunGroup = self.crurentProjectRunTomcatGroup_JSON["currentrun"]
                self.runTomcatGroup_JSON = self.crurentProjectRunTomcatGroup_JSON[currentRunGroup]
        except Exception as e:
            # file not exist, create it
            FormatPrint.printWarn(str(e))
            FormatPrint.printWarn("初始化tomcat运行组数据,出现异常:tomcat运行时文件不存在，将创建文件")
            init_tomcat_groups_runstatus_JSON = {}
            init_tomcat_group_runstatus_JSON ={}

            for projectname in self.conf_JSON["projectname"].keys():
                FormatPrint.printInfo("当前配置项目:"+str(projectname))
                new_tomcat_group_runstatus_JSON={
                    "currentrun": "groupmaster",
                    "totalruntimes": "1",
                    "groupmaster": {
                        "lastmodifytime": time.strftime('%Y-%m-%d %H:%M:%S'),
                        "lastrollbacktime": time.strftime('%Y-%m-%d %H:%M:%S'),
                        "runtimes": "1",
                        "sucesstimes": "0",
                        "failtimes": "0",
                        "rollbacktimes": "0"
                    },
                    "groupbackup": {
                        "lastmodifytime": time.strftime('%Y-%m-%d %H:%M:%S'),
                        "lastrollbacktime": time.strftime('%Y-%m-%d %H:%M:%S'),
                        "runtimes": "0",
                        "sucesstimes": "0",
                        "failtimes": "0",
                        "rollbacktimes": "0"
                    }
                }
                init_tomcat_group_runstatus_JSON[projectname] = new_tomcat_group_runstatus_JSON
                init_tomcat_groups_runstatus_JSON={
                    "projectname":init_tomcat_group_runstatus_JSON
                }

            with open(sys.path[0] + os.sep + 'runtime' + os.sep + 'tomcat-group-runstatus.json','w') as new_tomcat_run_status_file:
                new_tomcat_run_status_file.write(json.dumps(init_tomcat_groups_runstatus_JSON, indent=4))
            FormatPrint.printInfo("创建tomcat组运行时状态文件完成")

            self.crurentProjectRunTomcatGroup_JSON = init_tomcat_groups_runstatus_JSON["projectname"][self.projectName]
            currentRunGroup = self.crurentProjectRunTomcatGroup_JSON["currentrun"]
            self.runTomcatGroup_JSON = self.crurentProjectRunTomcatGroup_JSON[currentRunGroup]

    #初始化nginx运行数据
    def initRunNgixn(self):
        FormatPrint.printInfo("初始化nginx运行数据")
        try:
            with open(sys.path[0] + os.sep + 'runtime' + os.sep + 'nginx-group-runstatus.json','r') as nginx_run_status_file:
                self.crurentProjectRunNginxGroup_JSON = json.load(nginx_run_status_file)["projectname"][self.projectName]
                currentRunNginxGroup = self.crurentProjectRunNginxGroup_JSON["currentrun"]
                self.runNginxGroup_JSON = self.crurentProjectRunNginxGroup_JSON[currentRunNginxGroup]
        except Exception as e:
            # file not exist, create it
            FormatPrint.printWarn(str(e))
            FormatPrint.printWarn("初始化tomcat运行组数据,出现异常:nginx运行时文件不存在，将创建文件")
            init_nginx_groups_runstatus_JSON = {}
            init_nginx_group_runstatus_JSON = {}

            for projectname in self.conf_JSON["projectname"].keys():
                FormatPrint.printInfo("当前配置项目:" + str(projectname))
                new_nginx_group_runstatus_JSON = {
                    "currentrun":"groupmaster",
                    "groupmaster":{
                        "lastmodify":time.strftime('%Y-%m-%d %H:%M:%S'),
                        "modifytimes":"1"
                    },
                    "groupbackup":{
                        "lastmodify":time.strftime('%Y-%m-%d %H:%M:%S'),
                        "modifytimes":"0"
                    }
                }
                init_nginx_group_runstatus_JSON[projectname] = new_nginx_group_runstatus_JSON
                init_nginx_groups_runstatus_JSON = {
                    "projectname": init_nginx_group_runstatus_JSON
                }
            with open(sys.path[0] + os.sep + 'runtime' + os.sep + 'nginx-group-runstatus.json','w') as new_tomcat_run_status_file:
                new_tomcat_run_status_file.write(json.dumps(init_nginx_groups_runstatus_JSON, indent=4))
            FormatPrint.printInfo("创建nginx组运行时状态文件完成")

            self.crurentProjectRunNginxGroup_JSON= init_nginx_groups_runstatus_JSON["projectname"][self.projectName]
            currentRunGroup = self.crurentProjectRunNginxGroup_JSON["currentrun"]
            self.runTomcatGroup_JSON = self.crurentProjectRunNginxGroup_JSON[currentRunGroup]

    # 检查运行时配置文件是否正确
    def checkRuntimeStateConf(self):
        FormatPrint.printInfo("检查运行时配置文件是否正确:checkRuntimeStateConf")
        '''
            1、如果 tomcat-group-runstate.json 运行时文件不存在，初始化一个固定的，以master为主（需改进）
            2、如果 nginx-runstae.json 运行时文件不存在，初始化一个固定的，以master为主（需改进）
            3、如果文件存在，比对文件中的运行组的情况，运行组相同则认为配置文件正确
        '''
        self.initRunTomcatGroup()
        self.initRunNgixn()
        FormatPrint.printInfo("crurentProjectRunTomcatGroup_JSON:" + str(self.crurentProjectRunTomcatGroup_JSON))
        FormatPrint.printInfo("crurentProjectRunNginxGroup_JSON:" + str(self.crurentProjectRunNginxGroup_JSON))
        if self.crurentProjectRunTomcatGroup_JSON["currentrun"] == self.crurentProjectRunNginxGroup_JSON["currentrun"]:
            self.runGroup = self.crurentProjectRunTomcatGroup_JSON["currentrun"]
            FormatPrint.printInfo("当前运行的组为:"+str(self.runGroup))
            return True
        else:
            FormatPrint.printError("检测到tomcat组运行与ngixn组运行不匹配")
            FormatPrint.printError("runTomcatGroup_JSON:" + str(self.runTomcatGroup_JSON))
            FormatPrint.printError("runNginxGroup_JSON:" + str(self.runNginxGroup_JSON))
            return False
        return False

    #替换更新资源
    def replaceResource(self):
        FormatPrint.printDebug("替换更新资源")
        command=self.willBeUpdateTomcatGroup_JSON["tomcatresourceupdatescriptpath"] + " " + str(self.projectUpdateVersion) +" "+str(self.updateTime)
        FormatPrint.printInfo("执行资源替换脚本:"+str(command))
        if os.system(command) == 0:
            return True
        else:
            return False

    #检查tomcat服务是否可用
    def checkServiceIsOk(self):
        FormatPrint.printDebug("检查tomcat服务是否可用")
        tomcatDict={}
        socket.setdefaulttimeout(5)
        for tomcatName in self.willBeUpdateTomcatGroup_JSON["tomcatgroupinfo"]["tomcats"]:
            #tomcatDict key:tomcatName value:{URL , DATA , TRYTIMES}
            tomcatNameTag = tomcatName["tomcattag"]
            checkUrl ="http://"+tomcatName["serviceip"]+":"+tomcatName["port"]+self.willBeUpdateTomcatGroup_JSON["servicecheckurl"]
            checkData=self.willBeUpdateTomcatGroup_JSON["servicecheckpar"]
            serviceDict={}
            serviceDict["URL"]=checkUrl
            serviceDict["DATA"]=checkData
            serviceDict["TRYTIMES"]=0
            serviceDict["PORT"] = tomcatName["port"]
            serviceDict["STARTTIME"] = time.strftime('%Y-%m-%d %H:%M:%S')
            tomcatDict[tomcatNameTag]=serviceDict
        tomcatStartTime=time.time()
        maxTime=self.conf_JSON["tomcatmaxrestattime"]
        endTime=self.conf_JSON["endUpdateWaiteMaxTime"]
        while True:
            intervalTime= time.time() - tomcatStartTime
            FormatPrint.printInfo("tomcat重启，服务检查耗时:"+str(intervalTime))
            if len(tomcatDict) == 0 or (intervalTime > float(maxTime) and len(self.sucessRestartTomcats) > 0):
                for tomcatTag in self.sucessRestartTomcats:
                    FormatPrint.printInfo("tomcat"+str(tomcatTag)+"启动成功")
                #记得关闭未启动成功的tocmat
                if len(tomcatDict) > 0 :
                    for failTocmatTag in tomcatDict.keys():
                        TomcatFunc.killTomcat(self.tomcatKillScriptPath,failTocmatTag)
                break
            if intervalTime > float(endTime):
                FormatPrint.printInfo("在最大重启时间内，未发现已经完成启动的tomcat，终止更新")
                return False
            delList=[]
            for tomcatTag in tomcatDict.keys():
                URL=tomcatDict[tomcatTag]["URL"]
                DATA=tomcatDict[tomcatTag]["DATA"]
                PORT=tomcatDict[tomcatTag]["PORT"]
                try:
                    response = urllib2.urlopen(URL, DATA)
                    ret_data = response.read()
                    ret_code = response.code
                    response.close()
                    if isinstance(ret_data, bytes):
                        ret_data = bytes.decode(ret_data)
                    ret_data = json.loads(ret_data)
                    if ret_data["status"] == 1 and ret_code == 200:
                        FormatPrint.printInfo("####################################################################")
                        FormatPrint.printInfo(str(self.conf_JSON["serverip"]) + "(" + str(self.conf_JSON["hostname"]) + ")" + str(self.projectName) + "_" + str(self.projectUpdateVersion) + "版本,tomcat" + str(tomcatTag) + ":" + str(PORT) + "更新重启成功")
                        FormatPrint.printInfo("tomcat更新记录如下:")
                        FormatPrint.printInfo("开始更新时间:" + str(serviceDict["STARTTIME"]))
                        FormatPrint.printInfo("更新结束时间:" + time.strftime('%Y-%m-%d %H:%M:%S'))
                        FormatPrint.printInfo("####################################################################")
                        # 更新成功，将tomcat的标识加入到delList中
                        delList.append(tomcatTag)
                        self.sucessRestartTomcats.append(tomcatTag)
                except Exception as e:
                    FormatPrint.printWarn(str(self.conf_JSON["serverip"]) + "(" + str(self.conf_JSON["hostname"]) + ")" + str(self.projectName) + "_" + str(self.projectUpdateVersion) + "版本,tomcat" + str(tomcatTag) + ":" + str(PORT) + "更新异常:"+str(e))
            if (len(delList) > 0):
                # 删除delList中的tomcat标识，这些tomcat已经更新完成
                for deltag in delList:
                    del tomcatDict[deltag]
            time.sleep(3)
            #delList.clear()
            del delList[:]
        return True

    #项目更新
    def projectUpdate(self):
        FormatPrint.printDebug("项目更新")
        tomcatTags = []
        for tomcat in self.willBeUpdateTomcatGroup_JSON["tomcatgroupinfo"]["tomcats"]:
            tomcatTags.append(tomcat["tomcattag"])
        if self.replaceResource() and  TomcatFunc.restartTomcats(self.tomcatStartScriptPath,self.tomcatKillScriptPath,tomcatTags) and self.checkServiceIsOk():
            return True
        else:
            return False

    #tomcat重启完成，修改nginx配置
    def modifyNginxconf(self):
        FormatPrint.printInfo("tomcat重启完成，修改nginx配置")
        '''
        1、读取配置，读取开始标识和结束标识
        2、生成修改部分内容
        3、循环读取配置文件，找到开始标识和结束标识
        4、替换开始标识和结束标识之间的内容
        '''
        willBeUpdatedGroup_JSON = self.willBeUpdateTomcatGroup_JSON
        startReplaceTag = willBeUpdatedGroup_JSON["nginxreplacestarttag"]
        endReplaceTag =willBeUpdatedGroup_JSON["nginxreplaceendtag"]
        rootStartReplaceTag = willBeUpdatedGroup_JSON["nginxrootstarttag"]
        rootEndReplaceTag = willBeUpdatedGroup_JSON["nginxrootendtag"]
        nginx_conf_path =willBeUpdatedGroup_JSON["nginxconfpath"]
        upstream_conf = startReplaceTag+'\n'
        upstream_conf += '\tupstream ' + willBeUpdatedGroup_JSON["upstreamname"] + '\n\t{\n'
        for tomcatinfo in willBeUpdatedGroup_JSON["tomcatgroupinfo"]["tomcats"]:
            if tomcatinfo["tomcattag"] in self.sucessRestartTomcats:
                upstream_conf += '\t\tserver ' + tomcatinfo['upstreamip']+':'+tomcatinfo["port"] + ' max_fails=5 fail_timeout=60s weight='+tomcatinfo["upstreamweight"]+';\n'
            else:
                print(str(tomcatinfo['upstreamip'])+':'+str(tomcatinfo["port"])+"tomcat在规定时间内启动失败")
        upstream_conf += '\t}\n'
        upstream_conf=upstream_conf.decode('utf-8')
        root_conf = startReplaceTag + '\n'
        root_conf+=willBeUpdatedGroup_JSON["nginxrootconf"]
        root_conf = root_conf.decode('utf-8')
        FormatPrint.printInfo("修改的nginx的upstream配置文件如下:\n"+upstream_conf.encode('utf-8'))
        FormatPrint.printInfo("修改的nginx的root路径配置文件如下:\n" + root_conf.encode('utf-8'))
        confstr = ""

        try:
            with open(nginx_conf_path,'r') as nginx_conf_temp_file:
                isContinue=False
                isRooTContinue=False
                for line in nginx_conf_temp_file:
                    line=line.decode('utf-8')
                    #找到这个标识,修改upstream内容
                    if line.find(endReplaceTag) != -1:
                        isContinue = False
                        confstr += upstream_conf
                    if isContinue or line.find(startReplaceTag) != -1:
                        isContinue = True
                        continue
                    #找到这个标识,修改root内容
                    if line.find(rootEndReplaceTag) != -1:
                        isRooTContinue = False
                        confstr += root_conf
                    if isRooTContinue or line.find(rootStartReplaceTag) != -1:
                        isRooTContinue = True
                        continue
                    confstr += line
        except Exception as e:
            FormatPrint.printError("读取配置nginx配置文件出错,错误信息如下:\n"+str(e))
            return False
        try:
            with open(nginx_conf_path, 'w') as nginx_conf_file:
                nginx_conf_file.write(confstr.encode('utf-8'))
        except Exception as e:
            FormatPrint.printError("修改配置nginx配置文件出错,错误信息如下:\n" + str(e))
            return False
        return True

    #修改tomcat组运行状态
    def modifyRunTomcatGroupStatusFile(self):
        FormatPrint.printDebug("修改tomcat组运行状态")
        try:
            with open(sys.path[0] + os.sep + 'runtime' + os.sep + 'tomcat-group-runstatus.json','r') as tomcat_run_status_file:
                tomcat_run_status_JSON=json.load(tomcat_run_status_file)
                willBeUpdateGroupRunStatus_JSON= self.crurentProjectRunTomcatGroup_JSON[self.willBeUpdatedGroup]
                new_updateGroupTomcatRunStatus_JSON={
                    'failtimes': willBeUpdateGroupRunStatus_JSON["failtimes"],
                    'lastrollbacktime':willBeUpdateGroupRunStatus_JSON["lastrollbacktime"],
                    'lastmodifytime': time.strftime('%Y-%m-%d %H:%M:%S'),
                    'sucesstimes': int(willBeUpdateGroupRunStatus_JSON["sucesstimes"])+1,
                    'rollbacktimes': '0',
                    'runtimes': int(willBeUpdateGroupRunStatus_JSON["runtimes"])+1
                }
                new_projectTomcatRunStatus_JSON={
                    "deploymentmode":self.deploymentmode,
                    "currentrun":self.willBeUpdatedGroup,
                    "totalruntimes":int(tomcat_run_status_JSON["projectname"][self.projectName]["totalruntimes"])+1,
                    self.willBeUpdatedGroup:new_updateGroupTomcatRunStatus_JSON,
                    self.runGroup:self.crurentProjectRunTomcatGroup_JSON[self.runGroup]
                }
                tomcat_run_status_JSON["projectname"][self.projectName]=new_projectTomcatRunStatus_JSON
                with open(sys.path[0] + os.sep + 'runtime' + os.sep + 'tomcat-group-runstatus.json','w') as new_tomcat_run_status_file:
                    new_tomcat_run_status_file.write(json.dumps(tomcat_run_status_JSON, indent=4))
        except Exception as e:
            FormatPrint.printError("修改tomcat组运行状态时，出现异常:"+str(e))
            return False
        return True
    #修改nginx组运行状态
    def modifyRunNginxGroupStatusFile(self):
        FormatPrint.printDebug("修改nginx组运行状态")
        try:
            with open(sys.path[0] + os.sep + 'runtime' + os.sep + 'nginx-group-runstatus.json','r') as nginx_run_status_file:
                nginx_run_status_JSON=json.load(nginx_run_status_file)
                willBeUpdateGroupRunStatus_JSON= self.crurentProjectRunNginxGroup_JSON[self.willBeUpdatedGroup]
                new_updateGroupNginxRunStatus_JSON={
                    "lastmodify": time.strftime('%Y-%m-%d %H:%M:%S'),
                    "modifytimes":  int(willBeUpdateGroupRunStatus_JSON["modifytimes"])+1
                }
                new_projectNginxRunStatus_JSON={
                    "deploymentmode": self.deploymentmode,
                    "currentrun":self.willBeUpdatedGroup,
                    self.willBeUpdatedGroup:new_updateGroupNginxRunStatus_JSON,
                    self.runGroup:self.crurentProjectRunNginxGroup_JSON[self.runGroup]
                }
                nginx_run_status_JSON["projectname"][self.projectName]=new_projectNginxRunStatus_JSON
                with open(sys.path[0] + os.sep + 'runtime' + os.sep + 'nginx-group-runstatus.json','w') as new_tomcat_run_status_file:
                    new_tomcat_run_status_file.write(json.dumps(nginx_run_status_JSON, indent=4))
        except Exception as e:
            FormatPrint.printError("修改nginx组运行状态时，出现异常:"+str(e))
            return False
        return True

    #更新完成后，修改node-health-runstauts文件中的状态
    #重置了该项目的节点信息状态，保证运行与启动时一直。如果存在未启动成功的部分，则在健康检查中进行新的重启操作
    def modifyNodeHealthStatusFile(self):
        FormatPrint.printDebug("更新完成后，修改node-health-runstauts文件中的状态")
        node_health_status_filePath=sys.path[0]+os.sep + 'runtime' + os.sep + 'node-health-status.json'
        if os.path.exists(node_health_status_filePath):
            try:
                with open(node_health_status_filePath,'r') as node_health_status_file_M:
                    node_health_status_JSON = json.load(node_health_status_file_M)
                    new_node_health_status=node_health_status_JSON
                    nodesInfo={}
                    for tomcat in self.willBeUpdateTomcatGroup_JSON["tomcatgroupinfo"]["tomcats"]:
                        healthCheckUrl="http://"+tomcat["serviceip"]+":"+tomcat["port"]+self.willBeUpdateTomcatGroup_JSON["servicecheckurl"]
                        healthCheckData=self.willBeUpdateTomcatGroup_JSON["servicecheckpar"]
                        if tomcat["tomcattag"] in self.sucessRestartTomcats:
                            nodeInfo = {
                                'health-check-url': healthCheckUrl,
                                'health-check-data': healthCheckData,
                                'status': 'n/a',
                                'last-response-data': 'n/a',
                                'last-response-time': 0,
                                'fail-count': 0,
                                'last-check-time': time.strftime('%Y-%m-%d %H:%M:%S')
                            }
                        else:
                            #项目更新时tomcat未启动成功处理
                            nodeInfo = {
                                'health-check-url': healthCheckUrl,
                                'health-check-data': healthCheckData,
                                'status': 'dead',
                                'last-response-data': 'n/a',
                                'last-response-time': 0,
                                'fail-count': 10,
                                'last-check-time': time.strftime('%Y-%m-%d %H:%M:%S')
                            }
                        nodesInfo[tomcat["name"]]=nodeInfo
                    new_node_health_status["projectname"][self.projectName]=nodesInfo
                try:
                    with open(node_health_status_filePath,'w') as new_health_status_file:
                        new_health_status_file.write(json.dumps(new_node_health_status, indent=4))
                except Exception as e1:
                    FormatPrint.printWarn("项目更新完,成修改node-health-status.json出现异常,修改失败:"+str(e1))
                    return False
            except Exception as e:
                FormatPrint.printWarn("项目更新完成,读取node-health-runstauts文件异常:"+str(e))
                return False
        else:
            FormatPrint.printWarn("node-health-runstauts文件不存在,该项目未初始化")
            return True
        return True

    #删除upstream-status文件
    def delUpstreamStatusFile(self):
        FormatPrint.printDebug("删除upstream-status文件")
        orgin_file = sys.path[0] + os.sep + 'runtime' + os.sep + 'upstream-status.json'
        if os.path.exists(orgin_file):
            try:
                new_file=sys.path[0] + os.sep + 'runtime' + os.sep + time.strftime('%Y%m%d%H%M%S')+'_upstream-status.json'
                os.rename(orgin_file, new_file)
            except Exception as e:
                FormatPrint.printError("删除upstream-status文件出错:"+str(e))
                return False
            return True
        else:
            FormatPrint.printInfo("upstream-status文件不存在，未初始化")
            return True

    #修改运行时状态文件
    def modifyRunStatus(self):
        FormatPrint.printInfo("修改运行时状态文件")
        '''
            项目启动完成后，发现存在问题：部分tomcat未启动，node-health-runstatus文件需要被修改，需要重新被定义
        '''
        if self.modifyRunTomcatGroupStatusFile() and self.modifyRunNginxGroupStatusFile() and self.modifyNodeHealthStatusFile() and self.delUpstreamStatusFile():
            return True
        else:
            return False

#项目更新功能
def projectUpdate(projectName,projectUpdateVersion,updateType,updateTime):
    pu = ProjectUpdate(projectName)
    pu.updateType=updateType
    pu.projectUpdateVersion= projectUpdateVersion
    pu.updateTime=updateTime
    pu.readConfig();  # 读取配置文件信息
    #(全组启动方式), （单项目启动方式）, （半启动方式），默认采用全组启动方式
    #self.deploymentmode = self.self.conf_JSON["projectname"][self.projectName]["deploymentmode"]
    if pu.deploymentmode == None or pu.deploymentmode not in ["double","single","onehalf"]:
        FormatPrint.printFalat("配置文件deploymentmode未配置")
        exit(-1)

    if pu.checkRuntimeStateConf():
        pass
    else:
        FormatPrint.printInfo("运行状态检查与当前配置文件不一致");
        FormatPrint.printInfo("是否进行运行时文件切换?");
        exit(-1)

    FormatPrint.printDebug("当前tomcat运行组信息:"+str(pu.crurentProjectRunTomcatGroup_JSON))
    FormatPrint.printDebug("当前nginx运行信息:"+str(pu.crurentProjectRunNginxGroup_JSON))
    FormatPrint.printDebug("当前运行的组为:"+str(pu.runGroup))

    if pu.deploymentmode == 'single':
        pu.willBeUpdatedGroup = 'groupmaster'
    elif pu.runGroup == 'groupmaster':
        pu.willBeUpdatedGroup='groupbackup'
    else:
        pu.willBeUpdatedGroup='groupmaster'
    FormatPrint.printInfo("即將被更新的组为:" + str(pu.willBeUpdatedGroup))
    pu.willBeUpdateTomcatGroup_JSON = pu.conf_JSON["projectname"][pu.projectName][pu.willBeUpdatedGroup]
    pu.tomcatKillScriptPath=pu.willBeUpdateTomcatGroup_JSON["tomcatkillscriptpath"]
    pu.tomcatStartScriptPath=pu.willBeUpdateTomcatGroup_JSON["tomcatstartscriptpath"]
    pu.tomcatResourceUpdateScriptPath=pu.willBeUpdateTomcatGroup_JSON["tomcatresourceupdatescriptpath"]

    if pu.projectUpdate():#更新项目
        FormatPrint.printInfo("项目更新成功")
        if pu.modifyNginxconf():#修改nginx配置文件
            FormatPrint.printInfo("修改nginx配置文件 成功")
            if NginxFunc.reloadNginx(pu.willBeUpdateTomcatGroup_JSON["nginxreloadcmd"]):
                if pu.modifyRunStatus():
                    FormatPrint.printInfo("运行时状态修改完成")
                    FormatPrint.printInfo("项目更新完成")
                else:
                    FormatPrint.printError("运行时状态修改失败")
            else:
                 FormatPrint.printError("reload nginx 失败")
        else:
            FormatPrint.printError("修改 nginx 配置文件 失败")
    else:
        FormatPrint.printError("项目更新失败")