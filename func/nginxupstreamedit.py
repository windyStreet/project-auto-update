#!/usr/bin/env python
#!-*- coding:utf-8 -*-

import FormatPrint
import sys
import json
import os
import time
import NginxFunc
import JsonFileFunc

class NginxUpstreamEdit(object):
    def __init__(self):
        FormatPrint.printInfo("NginxUpstreamEdit")
        self.projectName = None
        self.nodeHealthStatus = None
        self.upstreamStatus = None

    def readNodeHealthStatus(self):
        path = sys.path[0] + os.sep + 'runtime' + os.sep + str(self.projectName) + '-node-health-status.json'
        self.nodeHealthStatus = JsonFileFunc.readFile(path)

    #检查upstream
    def checkUpstream(self):
        alive_count = 0
        alive_nodes = []
        dead_count = 0
        dead_nodes = []
        upstream_changed = False

        node_health_status = self.nodeHealthStatus['nodeinfo']
        upstream_status = self.upstreamStatus

        for node_name in sorted(node_health_status.keys()):
            if node_health_status[node_name]['status'] == 'running' or \
                            node_health_status[node_name]['status'] == 'error' or \
                            node_health_status[node_name]['status'] == 'n/a':
                alive_count += 1
                alive_nodes.append(node_name)

            if node_health_status[node_name]['status'] == 'dead':
                dead_nodes.append(node_name)
                dead_count += 1

            if (upstream_status[node_name]['last-status'] == 'running' or
                        upstream_status[node_name]['last-status'] == 'error' or
                        upstream_status[node_name]['last-status'] == 'n/a') and \
                            node_health_status[node_name]['status'] == 'dead':
                upstream_changed = True

            if upstream_status[node_name]['last-status'] == 'dead' and node_health_status[node_name][
                'status'] == 'running':
                upstream_changed = True

        if alive_count == 0:
            print('[FATAL]' + time.strftime('%Y-%m-%d %H:%M:%S') + ' - no alive node, abort upstream edit.')
        elif upstream_changed:
            upstream_conf = '\tupstream ' + config['upstream-name'] + '\n\t{\n'
            for alive_node_key in alive_nodes:
                upstream_conf += '\t\tserver ' + config['upstream']['nodes'][alive_node_key]['upstream-url'] + ' max_fails=5 fail_timeout=60s weight=1;\n'
            upstream_conf += '\t}\n'
            print('[INFO]' + time.strftime('%Y-%m-%d %H:%M:%S') + ' - upstream changed, reload nginx.')
            print(upstream_conf)
            nginx_conf_path = config['upstream-conf-path']
            with open(sys.path[0] + os.sep + 'conf' + os.sep + 'nginx.conf', 'r') as nginx_conf_temp_file:
                with open(nginx_conf_path, 'w') as nginx_conf_file:
                    for line in nginx_conf_temp_file:
                        if line.find('###UPSTREAM-PLACE-HOLDER###') != -1:
                            line = line + upstream_conf
                        nginx_conf_file.write(line)
            print('[INFO]' + time.strftime('%Y-%m-%d %H:%M:%S') + ' - execute: ' + config['nginx-reload-cmd'])
            os.system(config['nginx-reload-cmd'])

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

        for dead_node_key in dead_nodes:
            is_rebooting = True
            rebooting_count = upstream_status[dead_node_key]['rebooting-count']
            if upstream_status[dead_node_key]['is-rebooting'] is False:
                print('[INFO]' + time.strftime('%Y-%m-%d %H:%M:%S') + ' - restart dead node ' + dead_node_key)
                print('[INFO]' + time.strftime('%Y-%m-%d %H:%M:%S') + ' - execute: ' + config['upstream']['nodes'][dead_node_key]['stop-cmd'])
                os.system(config['upstream']['nodes'][dead_node_key]['stop-cmd'])
                time.sleep(1)
                print('[INFO]' + time.strftime('%Y-%m-%d %H:%M:%S') + ' - execute: ' + config['upstream']['nodes'][dead_node_key]['start-cmd'])
                os.system(config['upstream']['nodes'][dead_node_key]['start-cmd'])
            else:
                rebooting_count += 1
                print('[INFO]' + time.strftime('%Y-%m-%d %H:%M:%S') + ' - dead node ' + dead_node_key + ' is in rebooting count: ' + str(rebooting_count))
                if rebooting_count % 5 == 0:
                    is_rebooting = False

            latest_upstream_status[dead_node_key] = {
                'last-status': node_health_status[dead_node_key]['status'],
                'is-in-upstream': False,
                'is-rebooting': is_rebooting,
                'rebooting-count': rebooting_count,
                'last-check-time': time.strftime('%Y-%m-%d %H:%M:%S')
            }

        with open(sys.path[0] + os.sep + 'runtime' + os.sep + 'upstream-status.json', 'w') as new_status_file:
            new_status_file.write(json.dumps(latest_upstream_status, indent=4))

def nginxUpstreamEdit(projectName):
    nue=NginxUpstreamEdit()
    nue.projectName = projectName
    nue.upstreamStatus = NginxFunc.initUpstreamRunstatus()
    nue.readNodeHealthStatus()
    nue.checkUpstream()