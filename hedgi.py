#!/usr/bin/python3
import tracemalloc #By examining the traceback, you can identify the specific part of the code that is causing the socket to remain unclosed.
tracemalloc.start()
from gevent import monkey;monkey.patch_all() #for gevent use: this allows async gevent (without it pool.join() is needed so gevents wrok that will block the workload generator) and must be placed before import Flask
from flask import Flask, request, send_file, make_response, json, jsonify  # pip3 install flask
from waitress import serve  # pip3 install waitress
import requests  # pip3 install requests
import threading
# import jsonpickle
import logging
from logging.handlers import RotatingFileHandler
import datetime
import time
import math
from random import choice
# Monitor
import psutil
from cpufreq import cpuFreq
import numpy as np
import statistics  # for using satistics.mean()  #numpy also has mean()
import re
import copy
import utils
if utils.what_device_is_it('raspberry pi 3') or utils.what_device_is_it('raspberry pi 4'):
    import RPi.GPIO as GPIO
    from pijuice import PiJuice  # sudo apt-get install pijuice-gui
from bluetooth import *  # sudo apt-get install bluetooth bluez libbluetooth-dev && sudo python3 -m pip install pybluez
# sudo systemctl start bluetooth
# echo "power on" | bluetoothctl
import random
import socket
import os  # file path
import shutil  # empty a folder, copy a file
import subprocess as sp  # to run cmd to disconnect Bluetooth
import getpass
# setup file exists?
dir_path = os.path.dirname(os.path.realpath(__file__))
if os.path.exists(dir_path + "/setup.py"): import setup
if os.path.exists(dir_path + "/excel_writer.py"): import excel_writer  # pip3 install pythonpyxl
from os.path import expanduser  # get home directory by home = expanduser("~")
if os.path.exists(dir_path + "/pyhpa.py"): import pyhpa
if os.path.exists(dir_path + "/pyloadbalancing.py"): import pyloadbalancing
if os.path.exists(dir_path + "/pymanifest.py"): import pymanifest
if os.path.exists(dir_path + "/pykubectl.py"): import pykubectl


app = Flask(__name__)
app.config["DEBUG"] = True

from gevent.pool import Pool
from gevent import Timeout

session_enabled = False


# config
node_name = socket.gethostname()
node_role = ""  # MONITOR #LOAD_GENERATOR #STANDALONE #MASTER


def set_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    actual_ip = s.getsockname()[0]
    s.close()
    return actual_ip

cluster_info = None
node_IP = set_ip()
load_balancing ={}
peers = []
test_index = 0
test_updates = {}

epoch = 0
test_name = socket.gethostname() + "_test"
workers = []
functions = []
history = {'functions': [], 'workers': [], 'load_balancer': [], 'scheduler': [], 'autoscaler': []}
metrics = {}

sessions = {}

debug = False
erro_collector = []
waitress_threads = 8  # default is 4

try:
    cpuFreq = cpuFreq()
except FileNotFoundError as e:
    #This error happens for intel devices since Intel is not publishing available frequencies, ref: https://askubuntu.com/questions/1064269/cpufrequtils-available-frequencies
    #Instead, all CPU informations are in files located in 'cd /sys/devices/system/cpu/cpu0/cpufreq'
    #Collect informations by 'paste <(ls *) <(cat *) | column -s $'\t' -t'
    #???If an Intel device is part of experiments + measurements, this is not considering them.
    cpuFreq = None
    print('cpuFreq object is not created. If this is a master node and Intel, dismiss it.\n' + str(e))

# get home directory
home = expanduser("~")
log_path = home + "/" + test_name
if not os.path.exists(log_path):
    os.makedirs(log_path)

bluetooth_addr = "00:15:A3:00:52:2B"
hiccups_injection = []
active_sensor_time_slots=[]
# master: #00:15:A3:00:52:2B #w1: 00:15:A3:00:68:C4 #w2: 00:15:A5:00:03:E7 #W3: 00:15:A5:00:02:ED #w4: 00:15:A3:00:19:A7 #w5: 00:15:A3:00:5A:6F
pics_folder = "/home/" + getpass.getuser()+ "/pics/"
pics_num = 170  # pics name "pic_#.jpg"
file_storage_folder = "/home/" + getpass.getuser() + "/storage/"
if not os.path.exists(file_storage_folder):
    os.makedirs(file_storage_folder)
# settings
# [0]app name
# [1] run/not
# [2] w type: "static" or "poisson" or "exponential" or "exponential-poisson"
# [3] workload: [[0]iteration
# [1]interval/exponential lambda(10=avg 8s)
# [2]concurrently/poisson lambda (15=avg 17reqs ) [3] random seed (def=5)]
# [4] func_name [5] func_data [6] created [7] recv
# [8][min,max,mem requests, mem limits, cpu req, cpu limits,env.counter, env.redisServerIp, env,redisServerPort,
# read,write,exec,handlerWaitDuration,linkerd,queue,profile
apps = []

usb_meter_involved = False
# Either battery_operated or battery_cfg should be True, if the second, usb meter needs enabling
battery_operated = False
# Battery simulation
#0: battery_sim True/False, 1:max (variable), 2:initial #3current SoC,
        #4: renewable type, 5:poisson seed&lambda,6:dataset, 7:interval, 8 min_battery_charge, 9 turned on at,10 soc_unlimited, 11 battery_excess_input per charge input mwh
        #12: status 0/1, 13: energy_input, 14: energy_consumed
# battery_cfg = []
battery_cfg = [True, 906, 906, 906, "poisson", [5, 5], [], 30, 90]
# NOTE: apps and battery_cfg values change during execution
down_time = 0
time_based_termination = [False, 3600]
snapshot_report = ['False', '200', '800']  # begin and end time
max_request_timeout = 30
min_request_generation_interval = 0
sensor_admission_timeout = 3
node_down_sensor_hold_duration = 0
monitor_interval = 1
failure_handler_interval = 3
overlapped_allowed = True
max_cpu_capacity = 4000
boot_up_delay = 0
usb_eth_ports = None
raspbian_upgrade_error = False  # True, if psutil io_disk error due to upgrade
# controllers
test_started = None
test_finished = None
under_test = False
lock = threading.Lock()
metrcis_received = []
actuations = 0
# network_name_server={}
sock = None  # bluetooth connection
sensor_log = {}
suspended_replies = []
# monitoring parameters
# in owl_actuator
response_time = []
# in monitor
response_time_accumulative = []
current_time = []
current_time_ts = []
battery_charge = []
node_op = []
battery_history = []
cpuUtil = []
cpu_temp = []
cpu_freq_curr = []
cpu_freq_max = []
cpu_freq_min = []
cpu_ctx_swt = []
cpu_inter = []
cpu_soft_inter = []
memory = []
disk_usage = []
disk_io_usage = []
bw_usage = []

power_usage = []
throughput = []
throughput2 = []

if (utils.what_device_is_it('raspberry pi 3') or utils.what_device_is_it('raspberry pi 4')) and battery_operated:
    relay_pin = 20
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    pijuice = PiJuice(1, 0x14)


##############################
internal_session = requests.Session()
# s.keep_alive = False  # Disable keep-alive to close connections immediately after sending requests
# s.mount('http://', requests.adapters.HTTPAdapter(pool_connections=1, pool_maxsize=1))  # Limit the connection pool to 1
# s.mount('https://', requests.adapters.HTTPAdapter(pool_connections=1, pool_maxsize=1))

# Set the SO_LINGER option with a timeout of 10 seconds
internal_session.socket_options = [
(socket.SOL_SOCKET, socket.SO_LINGER, struct.pack('ii', 1, 10)),
]
############################

#reboot_agents
def reboot_agents(nodes, action):
    logger.info('reboot_agents: start...')

    #reboot
    if 're-boot' in action:
        logger.info('reboot_agents start re-boot')
        for node in nodes:
            position = node[0]
            if position != "PEER":
                continue
            
            name = node[1]
            ip = node[2]
            user_name = node[3] #ubuntu

            #reboot
            cmd= "ssh " + user_name + "@" + ip + " sudo reboot "
            logger.info(f'reboot_agents. cmd= {cmd}')
            out, error = utils.shell(cmd)
            logger.info(out + error)

        #ping to ensure all nodes are up
        for node in nodes:
            position = node[0]
            if position != "PEER":
                continue
            
            name = node[1]
            ip = node[2]
            user_name = node[3] #ubuntu

            #wait until ping is done
            ping(ip)

        #wait till peers bootup after ping
        logger.info(f'reboot_agents: wait for peers bootup after ping for {setup.agents_bootup_sec} sec...')
        time.sleep(setup.agents_bootup_sec)


    #run agents
    if 're-execute' in action:
        logger.info('reboot_agents start re-execute')

        for node in nodes:
            position = node[0]
            if position != "PEER":
                continue

            name = node[1]
            ip = node[2]
            user_name = node[3] #ubuntu

            #wait until ping is done
            ping(ip)
                
            
            #kill current one
            agent_name = os.path.basename(__file__)
            agent_path = os.path.abspath(os.path.basename(__file__))
            #kill

            # cmd= "ssh " + user_name + "@" + ip + " kill -9 \$(ps -aux |grep " + agent_name + " | awk '{print \$2}')"
            cmd = "ssh " + user_name + "@" + ip + " 'kill -9 $(ps -aux | grep " + agent_name + " | awk \"{print \$2}\")'"
            logger.info(f'reboot_agents. cmd= {cmd}')
            out, error = utils.shell(cmd)
            logger.info(f'out={out}.  error={error}')

            time.sleep(1)

            #run
            agent_name = os.path.basename(__file__)
            agent_path = os.path.abspath(os.path.basename(__file__))

            cmd= "ssh " + user_name + "@" + ip + " nohup python3 " + agent_path + "> " + agent_name.split('.')[0] + ".out" + " 2> " + agent_name.split('.')[0] + ".err" + " < /dev/null & "
            logger.info(f'reboot_agents. cmd= {cmd}')

            out, error = utils.shell(cmd)
            logger.info(out + error)
            logger.warning('Note: as agent is run in background using nohup, no output is received, so ensure agent is running remotely')
        
    logger.info('reboot_agents: done')

# #restart_agents
# def restart_agents(nodes):
#     logger.info('restart_agent: start')
#     for node in nodes:
#         position = node[0]
#         if position != "PEER":
#             continue
        
#         name = node[1]
#         ip = node[2]
#         user_name = node[3] #ubuntu

        
#         #kill current one
#         agent_name = os.path.basename(__file__)
#         agent_path = os.path.abspath(os.path.basename(__file__))
#         #kill

#         # cmd= "ssh " + user_name + "@" + ip + " kill -9 \$(ps -aux |grep " + agent_name + " | awk '{print \$2}')"
#         cmd = "ssh " + user_name + "@" + ip + " 'kill -9 $(ps -aux | grep " + agent_name + " | awk \"{print \$2}\")'"
#         logger.info(f'restart_agent. cmd= {cmd}')
#         out, error = utils.shell(cmd)
#         logger.info(f'out={out}.  error={error}')

#         #run

#         cmd= "ssh " + user_name + "@" + ip + " nohup python3 " + agent_path + "> " + agent_name.split('.')[0] + ".out" + " 2> " + agent_name.split('.')[0] + ".err" + " < /dev/null & "
#         logger.info(f'restart_agent. cmd= {cmd}')
#         #run
#         out, error = utils.shell(cmd)
#         logger.info(out + error)
#         logger.warning('Note: as agent is run in background using nohup, no output is received, so ensure agent is running remotely')

#     logger.info('restart_agent: done')
def ping(ip):
    done=False
    while True:
        #ping
        cmd = "ping -c 1 " + ip
        logger.info(cmd)
        out, error = utils.shell(cmd)
        logger.info(out + error)
        if "1 received" in out:
            logger.info('ping OK')
            done=True
            break
        else:
            time.sleep(1)
    return done

    
def launcher(coordinator):
    global logger
    global node_name
    global node_IP
    global epoch
    global internal_session
    logger.info('start')

    #if continous test, no change to epoch
    #if master reboot, get epoch from config file
    if setup.master_behavior_after_test_if_multiple_tests == 'reboot-before-starting-next-test':
        cmd='grep "epoch" /home/ubuntu/logs/config.txt'
        logger.info('read epoch value: ' + cmd)
        out, error = utils.shell(cmd)
        logger.info(out + error)
        try:
            epoch = int(out.split('=')[1])
        except Exception as e:
            logger.exception(f'Error: make sure epoch=? a number is in /home/ubuntu/logs/config.txt \n{e}')
            sys.exit()

        #exit if epochs are done already
        if epoch >= len(setup.test_name):
            logger.info(f"all tests are done already as epoch={epoch}, so sys.exit()")
            sys.exit()
        
    # set plan for coordinator itself.
    name = coordinator[1]
    ip = coordinator[2]

    plan = copy.deepcopy(setup.plans[name])
    
    # config for multi-tests
    plan["test_name"] = setup.test_name[epoch]
    # # set counter per app ???
    # #This f'{foo=}'.split('=')[0].split('.')[-1] returns the name of the given variable 'foo' by excluding the value '=*' and prefix 'setup.' from f'{foo=}'
    # plan["apps"][0][8][6] = setup.counter[epoch if f'{setup.counter=}'.split('=')[0].split('.')[-1] in setup.variable_parameters else 0 ]["ssd"]
    # plan["apps"][1][8][6] = setup.counter[epoch if f'{setup.counter=}'.split('=')[0].split('.')[-1] in setup.variable_parameters else 0]["yolo3"]
    # plan["apps"][2][8][6] = setup.counter[epoch if f'{setup.counter=}'.split('=')[0].split('.')[-1] in setup.variable_parameters else 0]["irrigation"]
    # plan["apps"][3][8][6] = setup.counter[epoch if f'{setup.counter=}'.split('=')[0].split('.')[-1] in setup.variable_parameters else 0]["crop-monitor"]
    # plan["apps"][4][8][6] = setup.counter[epoch if f'{setup.counter=}'.split('=')[0].split('.')[-1] in setup.variable_parameters else 0]["short"]
    # print('111111111111111111111')
    # print(plan["apps"][0][3][2])
    # #set [0]ssd, [3]workload_cfg, [2] concurrency. ???this applies for only for ssd app
    # #This plan["apps"][0][3] retruns [10000, 1, [7],seed, shapes["w7"],worker]
    # #if workload_cfg in setup.variable_parameters, get concurrency item with the index of epoch' otherwise get the index 0 and set it as a float/int single value for concurrency
    # plan["apps"][0][3][2] = plan["apps"][0][3][2][epoch if f'{setup.workload_cfg=}'.split('=')[0].split('.')[-1] in setup.variable_parameters else 0]

    # #if workload_cfg in variable_parameters
    # # if f'{setup.workload_cfg=}'.split('=')[0].split('.')[-1] in setup.variable_parameters:
    # #     #if concurrency for ssd app is a list of values [] in setup.workload_cfg
    # #     if isinstance(plan["apps"][0][3][2], list):
    # #         #get concurrency for this epoch from list and set it as a single int/float
    # #         plan["apps"][0][3][2] = plan["apps"][0][3][2][epoch]
    # #     #if concurrency is not a list, it is wrong
    # #     else:
    # #         logger.error('workload_cfg in setup.variable_parameters, but plan["apps"][0][3][2] is NOT a list')
    # #         time.sleep(3600)
    # # #if workload_cfg is Not in variable_parameters and concurrency is a list, that is wrong. 
    # # elif isinstance(plan["apps"][0][3][2], list):
    # #     logger.error('workload_cfg NOT in setup.variable_parameters, but plan["apps"][0][3][2] is a list. Change it to single int/float')
    # #     time.sleep(3600)
    
    # set battery size per test. All batteries are considered homogeneous. 
    plan["battery_cfg"][1] = setup.max_battery_charge[epoch if 'max_battery_charge' in setup.variable_parameters else 0]
    #solar_panel_scale
    plan["battery_cfg"][17] = setup.solar_panel_scale[epoch if 'solar_panel_scale' in setup.variable_parameters else 0]
    # set cpu governor per test
    plan["cpu_freq_config"]["governors"] = setup.cpu_governor[epoch if 'cpu_governor' in setup.variable_parameters else 0]
    #set interarrival_rate
    if plan['active_sensor_time_slots']['enabled'] == True:
        plan['active_sensor_time_slots']['interarrival_rate'] = setup.interarrival_rate[epoch if 'interarrival_rate' in setup.variable_parameters else 0]
    # verify node_name
    if name != node_name:
        logger.error('MAIN: Mismatch node name: actual= ' + node_name + ' assigned= ' + name)
        return 'Mismatch node name: actual= ' + node_name + ' assigned= ' + name
    # verify assigned ip
    if ip != node_IP:
        logger.error('Mismatch node ip: actual= ' + node_IP + ' assigned= ' + ip)
        return ""

    sender = plan["node_role"]  # used in sending plan to peers
    logger.info(name + ' : ' + str(ip))
    # set local plan
    reply = main_handler('plan', 'INTERNAL', plan)

    if reply != "success":
        logger.error('INTERNAL interrupted and stopped')
        return "failed"
    else:
         logger.info(name + ' reply: ' + 'success')

    #agent_reuse
    logger.info('agent_reuse...')
    if 're-execute-at-start' in setup.agents_reuse:
        action="re-execute"
        reboot_agents(setup.nodes, action)
    elif 're-boot-at-start' in setup.agents_reuse:
        action= ""
        #as of second test onward
        if epoch > 0 :
            action="re-boot-then-re-execute"
            reboot_agents(setup.nodes, action)
        else:
            action="re-execute"
            reboot_agents(setup.nodes, action)
    else:
        logger.error('ERROR - setup.agents_reuse not found, ' + str(setup.agents_reuse) )

    time.sleep(3)

    try:
        #peers
        reply_success = 0
        # set peers plan, sequentially, including USB Meter connection
        for node in setup.nodes:
            position = node[0]
            if position != "PEER":
                continue
            
            name = node[1]
            ip = node[2]
            user_name = node[3] #ubuntu
            
            logger.info('********* peer plan set for ' + name)
            plan = {}
            plan = copy.deepcopy(setup.plans[name])
            # config for multi-test
            plan["test_name"] = setup.test_name[epoch]
            # set counter per app ???
            plan["apps"][0][8][6] = copy.deepcopy(setup.counter[epoch if 'counter' in setup.variable_parameters else 0]["ssd"])
            plan["apps"][1][8][6] = copy.deepcopy(setup.counter[epoch if 'counter' in setup.variable_parameters else 0]["yolo3"])
            plan["apps"][2][8][6] = copy.deepcopy(setup.counter[epoch if 'counter' in setup.variable_parameters else 0]["irrigation"])
            plan["apps"][3][8][6] = copy.deepcopy(setup.counter[epoch if 'counter' in setup.variable_parameters else 0]["crop-monitor"])
            plan["apps"][4][8][6] = copy.deepcopy(setup.counter[epoch if 'counter' in setup.variable_parameters else 0]["short"])

            #set [0]ssd, [3]workload_cfg, [2] concurrency. ???this applies for only for ssd app
            #This plan["apps"][0][3] retruns [10000, 1, [7],seed, shapes["w7"],worker]
            #if workload_cfg in setup.variable_parameters, get concurrency item with the index of epoch' otherwise get the index 0 and set it as a float/int single value for concurrency
            for app in plan['apps']:

                #if app is True
                if app[1] == False:
                    continue


                #if workload_config not in variable_parameters, get the first value in the list of concurrency always
                concurrency_index = 0
                if 'workload_cfg' in setup.variable_parameters:
                    #otherwise, get the corresponding index to the current epoch
                    concurrency_index = epoch

                #pick correspondng value from the list that is prepared in setup.py
                concurrency_value = app[3][2]

                if isinstance(concurrency_value, list):
                    logger.info(f'isinstace list, ---------')
                    picked_concurrency = app[3][2][concurrency_index]
                    
                elif 'workload_cfg' in setup.variable_parameters:
                    logger.error('ERORRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRR')
                    logger.error(f'plan could not pick concurrency for app {app[0]} as a list. It must be a list if workload_cfg is in setup.parameters, so it can be picked based on epoch')

                else:
                    pass
                logger.info(f'picked_concurrency={picked_concurrency}')
                #set it. only a single int/float is given to the node, not a list
                app[3][2] = picked_concurrency
            # plan["apps"][0][3][2] = copy.deepcopy(plan["apps"][0][3][2][epoch if 'workload_cfg' in setup.variable_parameters else 0])


            # set battery size per test
            plan["battery_cfg"][1] = copy.deepcopy(setup.max_battery_charge[epoch if 'max_battery_charge' in setup.variable_parameters else 0])
            #solar_panel_scale
            plan["battery_cfg"][17] = copy.deepcopy(setup.solar_panel_scale[epoch if 'solar_panel_scale' in setup.variable_parameters else 0])
            # set cpu governor per test
            plan["cpu_freq_config"]["governors"] = copy.deepcopy(setup.cpu_governor[epoch if 'cpu_governor' in setup.variable_parameters else 0])
            #set interarrival_rate
            if plan['active_sensor_time_slots']['enabled'] == True:
                plan['active_sensor_time_slots']['interarrival_rate'] = copy.deepcopy(setup.interarrival_rate[epoch if 'interarrival_rate' in setup.variable_parameters else 0])
        
            logger.info('peers:' + name + ': ' + str(ip))
            response = None
            
            logger.info('********************************* start')
            for k,v in plan.items():
                logger.info(f'**************key={k}')
                logger.info(v)
            # logger.info(plan)
            logger.info('************ dumps')
            # logger.info(json.dumps(plan, indent=4))

            logger.info(json.dumps(plan))
            

            #send plan
            while True:
                # replier -= 1
                try:
                    # url = 'http://' + ip + ':5000/main_handler/plan/' + sender
                    
                    response = internal_session.post('http://' + ip + ':5000/main_handler/plan/' + sender, json=plan, timeout=10)
                    
                    # serialized_data = jsonpickle.encode(plan, unpicklable=False)
                    # response.close()
                    break
                except Exception as e:
                    logger.error('peers: failed for ' + name + ":" + ip)
                    logger.error('peers: exception:' + str(e))
                    
                    #ping and wait until done
                    ping(ip)
                    # cmd = "ping -c 1 " + ip
                    # logger.info('ping before network restart ' + cmd)
                    # out, error = utils.shell(cmd)
                    # logger.info(out + error)
                    # if "1 received" in out:
                    #     logger.info('ping OK')
                    #     if replier < 7 and replier > 3:

                    #re-run the app on the remote host
                    filename = os.path.basename(__file__)
                    cmd="ssh " + user_name + "@" + ip + " ./" + "nohup python3 " + filename + " > hedgi.out 2> hedgi.err < /dev/null &"
                    logger.info('re-run remote code ' + cmd)
                    out, error = utils.shell(cmd)
                    logger.info(out + error)

                    #wait to run
                    
                    time.sleep(5)
                    # else:
                    #     logger.error('ping Fail')

                    #restart network manager
                    net_interface_manager_restart()
                    # cmd = "sudo systemctl restart NetworkManager.service"
                    # logger.info('restart network manager: ' + cmd)
                    # out, error = utils.shell(cmd)
                    # logger.info(out + error)

                    time.sleep(3)

            if response and response.text == "success":
                logger.info(name + ' reply: ' + 'success')
                reply_success += 1
            elif response:
                logger.error('peers: request.text for ' + name + ' ' + str(response.text))
            else:
                logger.error('peer: failed to connect to ' + ip)
        # verify peers reply
        peers = len([node for node in setup.nodes if node[0] == "PEER"])
        if reply_success == peers:
            logger.info('all ' + str(peers) + ' nodes successful')

            # run local main_handler on
            logger.info('run all nodes main_handler')

            # internal
            thread_main_handler = threading.Thread(target=main_handler, args=('on', 'INTERNAL',))
            thread_main_handler.name = "main_handler"
            # it calls scheduler that initiates functions & workers and deploys functions also calls autoscaler and load balancer
            thread_main_handler.start()
            # wait for initial function deployment roll-out
            logger.info('function roll out wait ' + str(setup.function_creation_roll_out) + 's')
            time.sleep(setup.function_creation_roll_out)

            # set peers on sequentially
            reply_success = 0
            for node in setup.nodes:
                position = node[0]
                name = node[1]
                ip = node[2]
                if position == "PEER":
                    logger.info('main_handler on: peers:' + name + ': ' + str(ip))
                    try:
                        response = internal_session.post('http://' + ip + ':5000/main_handler/on/' + sender)
                        # response.close()
                    except Exception as e:
                        logger.error('main_handler on: peers: failed for ' + name + ":" + ip)
                        logger.error('main_handler on: peers: exception:' + str(e))
                    if response.text == "success":
                        logger.info('main_handler on:' + name + ' reply: ' + 'success')
                        reply_success += 1
                    else:
                        logger.info('main_handler on:' + name + ' reply: ' + str(response.text))
            # verify peers reply
            peers = len([node for node in setup.nodes if node[0] == "PEER"])
            if reply_success == peers:
                logger.info('main_handler on: all ' + str(peers) + ' nodes successful')
            else:
                logger.info('main_handler on: only ' + str(reply_success) + ' of ' + str(peers))

        else:
            logger.info('failed: only ' + str(reply_success) + ' of ' + str(len(peers)))
    except Exception as e:
        logger.info('ERROR - call peers ' + str(e))

    logger.info('stop')

#load balancer
def load_balancer():
    global logger
    global under_test
    global debug
    global epoch
    global history
    #timing
    logger.info("started...")
    start = datetime.datetime.now(datetime.timezone.utc).astimezone().timestamp()
    
    #get config (as dict)
    load_balancing_config = copy.deepcopy(setup.load_balancing)

    #history initializing
    history['load_balancer']= []
    
    #counter initializing
    load_balancing_round = 0
    
    #create nodes list
    nodes_new = []
    for node in setup.nodes:
        if node[0] == 'PEER':
            nodes_new.append({'name': node[1], 'ip': node[2]})

    #load balance
    while under_test:
        #[new round timing]
        now = datetime.datetime.now(datetime.timezone.utc).astimezone().timestamp()
        logger.info('Load balancing round #' + str(load_balancing_round) + ' started at ' + str(now))
        #set round number
        load_balancing_config['load_balancing_round'] = load_balancing_round

        #[MONITORING]
        logger.info('monitoring...')

        #get nodes status like cpuUtil or charge
        nodes_new = monitor_pull(nodes_new, 'MASTER')
        #update load_balancing_config
        load_balancing_config['nodes'] = nodes_new

        logger.info('load_balancing_config=\n' + str(load_balancing_config))

        #[ANALYZING]
        logger.info('analyzing...')

        #[PLANNING]: run an algorithm and get updated plan for backends
        logger.info('planning...')

        #update backends  
        ##???test
        logger.info('backend_discovery before load blaancing plan in setup.py=\n' + str(setup.load_balancing['backend_discovery']))
        load_balancing_config, msg, error = pyloadbalancing.plan(**load_balancing_config)
        logger.info('backend_discovery after update in setup.py=\n' + str(setup.load_balancing['backend_discovery']))
        logger.info('plan:' + msg)
        
        if error:
            logger.error('load_balancing plan failed \n' + str(error))
            time.sleep(3600)


        #[Execution]
        logger.info('execution...')

        #execute
        load_balancing_config, msg, error = pyloadbalancing.execute(**load_balancing_config)
        logger.info('execution:' + msg)
        if error:
            logger.error('execution failed err\n' + error)
            time.sleep(3600)

        #print logs
        logger.info(load_balancing_config)

        #history
        history['load_balancer'].append(load_balancing_config)

        # sliced interval in 1 minutes
        logger.info('Load balancer done (round #' + str(load_balancing_round) + ') --- sleep for ' + str(
            load_balancing_config['interval']) + ' sec / ' + str(load_balancing_config['interval']/60) + ' min.')
        remained = load_balancing_config['interval']
        minute = 60
        while remained > 0:
            if remained >= minute:
                time.sleep(minute)
                remained -= minute
                if not under_test:
                    break
            else:
                time.sleep(remained)
                remained = 0

        load_balancing_round +=1

    # load balancer clean_up???
    logger.info('stop')

# monitor_fetch
def monitor_pull(nodes, current_node_role):
    global logger
    logger.info("monitor_pull: start")
    # MONITOR
    template = {'cpuUtil': -1, 'charge': -1}

    # Fetch data from peers
    for node in nodes:
        success = False
        # retry
        while success == False:
            try:
                logger.info('monitor_pull: get ' + node['name'] + ' ...')
                response = internal_session.get('http://' + node['ip'] + ':5000/main_handler/pull/'
                                        + current_node_role, timeout=10, json=template)
                # response.close()
            except Exception as e:
                logger.error('monitor_pull: get failed for ' + node['name'] + ":" + str(e))
                time.sleep(1)
            else:
                logger.info('monitor_pull response \n' + str(response.json()))
                if response.json() and 'cpuUtil' in response.json():
                # if response.json().get('cpuUtil'):
                    node['cpuUtil'] = response.json()['cpuUtil']
                    logger.info('pull_monitor: response of ' + node['name'] + ' is ' + str(node['cpuUtil']) + '%')
                    success = True
                else:
                    logger.error('key cpuUtil not found in response.json()')
                    logger.error(str(response.headers))

    logger.info('pull_monitor:\n' + '\n'.join([str(node) for node in nodes]))
    logger.info("pull_monitor: done")

    return nodes


#autoscaler 
def autoscaler():
    global logger
    global under_test
    global debug
    global epoch
    global functions
    global history
    
    if setup.auto_scaling == "openfaas":
        logger.info("openfaas will handle the autoscaling by a request-per second policy")
        return None
    
    autoscaling_interval = setup.autoscaling_interval
    
    #this thread is started after launcher method, so functions are already created.
    logger.info("started...")
    start = datetime.datetime.now(datetime.timezone.utc).astimezone().timestamp()
    #wait for the scheduler to initialize functions variable, then get functions name
    while functions == []:
        time.sleep(1)
    
    end = datetime.datetime.now(datetime.timezone.utc).astimezone().timestamp()
    logger.info("waited for functions variable to be set by scheduler for " + str(round(end-start,2)) + "s")
    #create HPA objects for functions and keep replacing them according to the load
    autoscaling_round = 0
    while under_test:
        autoscaling_round +=1
        logger.info("Started round #" + str(autoscaling_round))
        start = datetime.datetime.now(datetime.timezone.utc).astimezone().timestamp()
        
        for function in functions:
            # function = [identity, hosts[], func_info, profile]
            
            #identify function's name, i.e, from function[0]
            function_identity = function[0]
            
            function_node_name = function_identity[0] #e.g., "w1"
            function_app_name = function_identity[1] #e.g., "yolo3"
            function_name = function_node_name + "-" + function_app_name
            
            #get the following from function_info, i.e., from function[2]
            function_info = function[2]
            
            #set min replica
            min_replicas = function_info[0]
            #set max replicas
            max_replicas = function_info[1]
            
            #get the following from global values in setup.py file
            
            #set avg CPU utilization condition
            avg_cpu_utilization = setup.avg_cpu_utilization
            #set scale down stabilaztion window
            scale_down_stabilizationWindowSeconds = setup.scale_down_stabilizationWindowSeconds

            #create HPA
            pyhpa.auto_scaling_by_hpa(logger,
                                      function_name,
                                      min_replicas,
                                      max_replicas,
                                      avg_cpu_utilization,
                                      scale_down_stabilizationWindowSeconds)
        
        
        end = datetime.datetime.now(datetime.timezone.utc).astimezone().timestamp()
        
        #sleep
        # sliced interval in 1 minutes
        logger.info('End autoscaler round #' + str(autoscaling_round) + ' in ' + str(round(end-start,2)) + 's: sleep for ' + str(
            autoscaling_interval) + ' sec...')
        remained = autoscaling_interval
        minute = 60
        while remained > 0:
            sleep_duration = min(minute, remained)
            time.sleep(sleep_duration)
            remained -= sleep_duration
            if not under_test:
                break
    
    logger.info("stopped.")
    
    
# scheduler
def scheduler():
    global epoch
    global under_test
    global logger
    global debug
    global node_role
    global battery_cfg
    global workers
    global functions
    global max_cpu_capacity
    global log_path
    global history
    logger.info('start')

    # initialize workers and funcitons lists
    # default all functions' host are set to be placed locally
    
    workers, functions = initialize_workers_and_functions(setup.nodes, workers, functions,
                                                          battery_cfg, setup.plans, setup.zones)
    # history
    history["functions"] = []
    history["workers"] = []

    logger.info('after initialize_workers_and_functions:\n'
                + '\n'.join([str(worker) for worker in workers]))
    logger.info('after initialize_workers_and_functions:\n'
                + '\n'.join([str(function) for function in functions]))

    scheduling_round = 0
    while under_test:
        scheduling_round += 1
        logger.info('################################')
        logger.info('MAPE LOOP START: round #' + str(scheduling_round))
        # monitor: update Soc
        logger.info('monitor: call')
        workers = scheduler_monitor(workers, node_role)

        # ANALYZE (prepare for new placements)
        logger.info('analyzer: call')

        # definitions
        new_functions = copy.deepcopy(functions)

        # reset F's new location to null
        for new_function in new_functions:
            new_function[1] = []

        # reset nodes' capacity to max
        for worker in workers:
            worker[3] = setup.max_cpu_capacity

        # planner :workers set capacity, functions set hosts
        logger.info('planner: call: ' + str(setup.scheduler_name[epoch if 'scheduler_name' in setup.variable_parameters else 0]))
        # Greedy
        if "greedy" in setup.scheduler_name[epoch if 'scheduler_name' in setup.variable_parameters else 0]:
            workers, functions = scheduler_planner_greedy(workers, functions, new_functions,
                                                          setup.max_battery_charge[epoch if 'max_battery_charge' in setup.variable_parameters else 0], setup.zones,
                                                          setup.warm_scheduler[epoch if 'warm_scheduler' in setup.variable_parameters else 0],
                                                          setup.sticky, setup.stickiness[epoch if 'stickiness' in setup.variable_parameters else 0], setup.scale_to_zero,
                                                          debug)
        # shortfaas
        elif "shortfaas" in setup.scheduler_name[epoch if 'scheduler_name' in setup.variable_parameters else 0]:
            workers, functions = scheduler_planner_shortfaas(workers, functions, new_functions,
                                                             setup.max_battery_charge[epoch if 'max_battery_charge' in setup.variable_parameters else 0], setup.warm_scheduler[epoch if 'warm_scheduler' in setup.variable_parameters else 0],
                                                             setup.plugins[epoch if 'plugins' in setup.variable_parameters else 0], debug)
        # hospital_resident
        elif "hospital_resident" in setup.scheduler_name[epoch if 'scheduler_name' in setup.variable_parameters else 0]:
            workers, functions = scheduler_planner_hospital_resident(workers, functions, new_functions,
                                                             setup.max_battery_charge[epoch if 'max_battery_charge' in setup.variable_parameters else 0], setup.warm_scheduler[epoch if 'warm_scheduler' in setup.variable_parameters else 0],
                                                             setup.plugins[epoch if 'plugins' in setup.variable_parameters else 0], debug)
        #mthg
        elif "mthg" in setup.scheduler_name[epoch if 'scheduler_name' in setup.variable_parameters else 0]:
            workers, functions = scheduler_planner_mthg(workers, functions, new_functions,
                                                             setup.max_battery_charge[epoch if 'max_battery_charge' in setup.variable_parameters else 0], setup.warm_scheduler[epoch if 'warm_scheduler' in setup.variable_parameters else 0],
                                                             setup.plugins[epoch if 'plugins' in setup.variable_parameters else 0], debug, scheduling_round)
        #mthg
        elif "ffd" in setup.scheduler_name[epoch if 'scheduler_name' in setup.variable_parameters else 0]:
            workers, functions = scheduler_planner_first_fit_decreasing(workers, functions, new_functions,
                                                             setup.max_battery_charge[epoch if 'max_battery_charge' in setup.variable_parameters else 0], setup.warm_scheduler[epoch if 'warm_scheduler' in setup.variable_parameters else 0],
                                                             setup.plugins[epoch if 'plugins' in setup.variable_parameters else 0], debug, scheduling_round)

        
        # Local
        elif "local" in setup.scheduler_name[epoch if 'scheduler_name' in setup.variable_parameters else 0]:
            workers, functions = scheduler_planner_local(workers, new_functions, debug)
        # Default-Kubernetes
        elif "default" in setup.scheduler_name[epoch if 'scheduler_name' in setup.variable_parameters else 0]:
            workers, functions = scheduler_planner_default(workers, new_functions, debug)
        # Random
        elif "random" in setup.scheduler_name[epoch if 'scheduler_name' in setup.variable_parameters else 0]:
            workers, functions = scheduler_planner_random(workers, new_functions, debug)
        # Bin-Packing
        elif "bin-packing" in setup.scheduler_name[epoch if 'scheduler_name' in setup.variable_parameters else 0]:
            workers, functions = scheduler_planner_binpacking(workers, functions, new_functions, debug)
        # Optimal
        elif "optimal" in setup.scheduler_name[epoch if 'scheduler_name' in setup.variable_parameters else 0]:
            pass
        else:
            logger.error('scheduler_name not found: ' + str(setup.scheduler_name[epoch if 'scheduler_name' in setup.variable_parameters else 0]))
            return

        # EXECUTE
        logger.info('executor: call')
        # translate hosts to profile and then run helm command
        # return functions as it is modifying functions (i.e., profiles)
        functions = scheduler_executor(functions, setup.profile_chart,
                                       setup.profile_creation_roll_out,
                                       setup.function_chart, scheduling_round, log_path,
                                       setup.scheduler_name[epoch if 'scheduler_name' in setup.variable_parameters else 0], workers, debug)

        # history
        history["functions"].append(copy.deepcopy(functions))
        history["workers"].append(copy.deepcopy(workers))

        # sliced interval in 1 minutes
        logger.info('MAPE LOOP (round #' + str(scheduling_round) + ') done: sleep for ' + str(
            setup.scheduling_interval[epoch if 'scheduling_interval' in setup.variable_parameters else 0]) + ' sec...')
        remained = setup.scheduling_interval[epoch if 'scheduling_interval' in setup.variable_parameters else 0]
        minute = 60
        while remained > 0:
            if remained >= minute:
                time.sleep(minute)
                remained -= minute
                if not under_test:
                    break
            else:
                time.sleep(remained)
                remained = 0

                # save history

    # scheduler clean_up???
    logger.info('stop')


# scoring
def scheduler_planner_shortfaas(workers, functions, new_functions,
                                max_battery_charge, warm_scheduler, plugins, debug):
    global logger
    # workers have full capacity available
    # new_functions have null as hosts

    logger.info("shortfaas:start")
    logger.info('shortfaas:\n available Workers \n'
                + '\n'.join([str(worker) for worker in workers]))

    # define and initialize scoring scheme
    scoring = {new_function[0][0] + '-' + new_function[0][1]:
                   {worker[0]:
                        {plugin: 0 for plugin in plugins}
                    for worker in workers} for new_function in new_functions}
    logger.info('shortfaas: set ' + '\n' + str(scoring))
    # add summations initialize
    for func, value in scoring.items():
        #
        for worker_name, value2 in scoring[func].items():
            scoring[func][worker_name]['sum_worker_scores'] = 0
        scoring[func]['sum_function_scores'] = 0
    # E.g.,
    # print(scoring['f1'])
    # print(scoring['f1']['w1'])
    # print(scoring['f1']['w1']['energy'])
    # print(scoring['f1']['sum_func_score'])
    # print(scoring['f1']['w1']['sum_worker_score'])

    logger.info('shortfaas: sum ' + '\n' + str(scoring))
    #scores = {'function1': 
    #               {
    #                   node1: 
    #                       {energy:0, locality:0, sticky:0, sum_worker_scores:0}, 
    #                   sum_function_scores:0
    #               },
    #        }
    # calculate and set soc percent and normalize to -1-1 (index 4 of worker used for soc percent, instead of zone)
    for worker in workers:
        soc = worker[2]
        # assume all nodes have batteries of same size????
        # max_battery_charge = copy.deepcopy(nodes_plan[worker[0]]["battery_cfg"][1])
        soc_percent = round(soc / max_battery_charge * 100)
        logger.info(worker[0] + ' soc : ' + str(soc_percent) + ' %')
        # normalize to 0-1
        worker[4] = round(soc_percent / 100, 2)

    logger.info('shortfaas:updated soc %:\n'
                + '\n'.join([str(worker) for worker in workers]))

    # so far, new_functions have [] as hosts, workers have full as capacity and both workers and new_functions are sorted now
    logger.info('shortfaas: start setting scores per functions')
    for new_function in new_functions:
        # function_name
        function_name = new_function[0][0] + '-' + new_function[0][1]
        logger.info('shortfaas: functions **** ' + function_name + '  ****')
        logger.info('workers:\n'
                    + '\n'.join([str(worker) for worker in workers]))
        # function's old_hosts: last placement scheme
        old_hosts = copy.deepcopy([*(function[1] for function in functions if function[0] == new_function[0])][0])

        # old_hosts have soc value based on last epoch, so update them
        for index, old_host in enumerate(old_hosts):
            # update host's zone, capacity and Soc based on current status
            old_hosts[index] = [*(worker for worker in workers if worker[0] == old_host[0])][0]
        logger.info('old_hosts\n' + str(old_hosts))

        # function's owner
        owner = [*(worker for worker in workers if worker[0] == new_function[0][0])][0]
        owner_name = owner[0]
        # owner soc normalized
        owner_soc_normalized = copy.deepcopy(owner[4])

        logger.info(f'start scoring for {function_name} by plugins={plugins}')
        # score per node
        for worker in workers:
            worker_name = copy.deepcopy(worker[0])
            worker_soc_normalized = copy.deepcopy(worker[4])

            # per plugin
            # energy
            # deduct remote soc from owner
            scoring[function_name][worker_name]['energy'] = (round((
                                                                           worker_soc_normalized - owner_soc_normalized) *
                                                                   plugins['energy'], 2))

            # locally
            if owner_name == worker_name:
                # if itself, score locally
                scoring[function_name][worker_name]['locally'] = (round(
                    owner_soc_normalized * plugins['locally'], 2))
            else:
                # default 0
                pass

            # sticky
            # assume first replica (old_hosts[0]) location represents the whole replicas  ???
            if old_hosts[0][0] != owner_name:
                # has been offloaded in last round
                if old_hosts[0][0] == worker_name:
                    # if this worker was the last place
                    scoring[function_name][worker_name]['sticky'] = (
                        round(1 * plugins['sticky'], 2))
                else:
                    # default 0
                    pass
            else:
                # default 0
                pass
            # sum worker scores
            scoring[function_name][worker_name]['sum_worker_scores'] = (
                    scoring[function_name][worker_name]['energy']
                    + scoring[function_name][worker_name]['locally']
                    + scoring[function_name][worker_name]['sticky'])

        # sum function scores
        for key, value in scoring[function_name].items():
            worker_name = key
            # items, except the summation
            if worker_name != 'sum_function_scores':
                # add per worker
                scoring[function_name]['sum_function_scores'] += (
                    scoring[function_name][worker_name]['sum_worker_scores'])
        logger.info('shortfaas: end scoring for ' + function_name + '\n' +
                    str(scoring[function_name]))

    # end scoring
    logger.info('scoring done:' + '\n'.join(str(func) + str(info) for func, info in scoring.items()))




    # get a scores_tmp dict of function_name: sum_function_scores
    scores_tmp = {}  # function_name: sum_function_scores
    # create a dict
    for k, v in scoring.items():
        func_name = k
        sum_function_scores = v['sum_function_scores']
        scores_tmp[func_name] = sum_function_scores
    # sort dict (large to small)
    # scores_tmp={k: v for k,v in sorted(scores_tmp.items(), key=lambda item: item[],
    #                                                             reverse=True)}
    logger.info('scored functions in tmp \n' + str(scores_tmp))

    logger.info('*******    start placements    *******')
    # place by max score
    while len(scores_tmp):
        # get max scored functions
        function_name = max(scores_tmp.items(), key=lambda k: k[1])[0]  # key
        sum_function_scores = max(scores_tmp.items(), key=lambda k: k[1])[1]  # value
        logger.info('placement for ----- ' + function_name + '(sum scores=' + str(sum_function_scores) + ') -----')

        # get full function
        new_function = [*(new_function for new_function in new_functions if
                          new_function[0][0] == function_name.split('-')[0] and new_function[0][1] ==
                          function_name.split('-', 1)[1])][0]

        # function required capacity
        func_required_cpu_capacity = 0
        # exclude 'm'
        replica_cpu_reqs = int(new_function[2][4].split('m')[0])
        func_max_replica = new_function[2][1]
        func_required_cpu_capacity = replica_cpu_reqs * func_max_replica

        # placement
        # set new hosts
        new_hosts = []

        owner_name = function_name.split('-')[0]  # e.g. w1-irrigation
        owner = [*(worker for worker in workers if worker[0] == owner_name)][0]
        owner_soc = owner[2]
        logger.info('function owner \n' + str(owner))
        # if function not belong to a dead node or warm scheduling is enabled
        if owner_soc >= battery_cfg[8] or warm_scheduler:
            # get max scored worker of this function
            max_score = float('-inf')  # minimum value, for max value remove '-' from inf
            selected_worker_name = ""

            nodes_score = scoring[function_name]
            for key, value in nodes_score.items():
                # keys: w1, w2, w3, sum_function_scores
                # e.g. {'w1': {'energy': 0, 'locally': 0, 'sticky': 0, 'sum_worker_score': 0}, 'w2': {'energy': 0, 'locally': 0, 'sticky': 0, 'sum_worker_score': 0}, 'sum_func_score': 1}
                # items, except 'sum_function_scores'
                if key != 'sum_function_scores':
                    if value['sum_worker_scores'] > max_score:
                        worker = [*(worker for worker in workers if worker[0] == key)][0]

                        # #add# if host node is down, skip it
                        # if worker[2] < setup.min_battery_charge:
                        #     for rep in range(func_max_replica):
                        #         new_hosts.append(copy.deepcopy(owner))
                        # #edded#
                        # if capacity
                        if worker[3] >= func_required_cpu_capacity:
                            max_score = value['sum_worker_scores']
                            selected_worker_name = key

            #add# if no node is picked, place it locally
            if selected_worker_name == "":
                logger.info('abcd')
                selected_worker_name = owner[0]
            #added#

            # get the remote host
            worker = [*(worker for worker in workers if worker[0] == selected_worker_name)][0]

            # if offloading placement, first localize functions of remote host
            if worker[0] != owner_name:
                worker, new_functions, scores_tmp = localizer(worker, new_functions, scores_tmp)

            # set new_hosts
            for rep in range(func_max_replica):
                new_hosts.append(copy.deepcopy(worker))
            logger.info('placement for  ' + function_name + '\n' + str(worker))
        else:
            # when owner is dead, place it locally
            logger.info('(dead node) placement locally for ' + function_name)
            # how about functions belong to a dead node??? they are still scheduled locally
            for rep in range(func_max_replica):
                new_hosts.append(copy.deepcopy(owner))

        logger.info('deduct capacity for ' + function_name)
        # deduct function cpu requirement from worker's cpu capacity
        for new_host in new_hosts:
            # get selected worker index per replica
            index = workers.index([*(worker for worker in workers if worker[0] == new_host[0])][0])
            # deduct replica cpu requirement
            workers[index][3] -= replica_cpu_reqs
            # update new_host, particulalrly its capacity
            new_host[3] = workers[index][3]

        # set new_function new hosts
        new_function[1] = new_hosts
        if debug: logger.info("shortfaas: new_hosts for ("
                              + new_function[0][0] + "-" + new_function[0][1] + "):\n" + str(new_function[1]))

        # delete
        del scores_tmp[function_name]

    # for loop: next new_function

    logger.info('shortfaas: done: functions:\n'
                + '\n'.join([str(new_function) for new_function in new_functions]))

    return workers, new_functions


# hospital residents:
#1-prepare a scoring
#2-prepare a dict of keys equal to functions names and values equal to the sorted list of workers names for each function as its preferences sorted by sum_worker_scores from largest to smallest given by the function
#3-prepare a dict of key equal to workers name and values equal to the sorted list of functions for each worker as its preferences sorted by sum_function_scores from largest to smallest given by the function
#4-prepare a dict of key equal to workers name and values equal to the capacity of the worker in terms of the number of functions it can fit in.
#5-do matching and receive a dict with keys equal to workers name and value for each worker is a list of function names assigned to the worker.
#6-convert matching to actual assignemtns by setting the new_hosts for each function given the obtained matchings.

#note: cpacity constraint is considered in the prepared dict to workers capacity
#note: all nodes are involved, so it is like always warm scheduling is applied.
#note: worker's own function (or locality) hard constraint is not applied.
#priority of placing functions is need earlier is indirectly applied when nodes give their preference to the functions based on the sum_function_scores which represents the priority of the function.
def scheduler_planner_hospital_resident(workers, functions, new_functions,
                                max_battery_charge, warm_scheduler, plugins, debug):
    global logger


    # workers have full capacity available
    # new_functions have null as hosts

    logger.info("hospital_resident:start")
    logger.info('hospital_resident:\n available Workers \n'
                + '\n'.join([str(worker) for worker in workers]))

    # define and initialize scoring scheme
    scoring = {new_function[0][0] + '-' + new_function[0][1]:
                   {worker[0]:
                        {plugin: 0 for plugin in plugins}
                    for worker in workers} for new_function in new_functions}
    logger.info('hospital_resident: set ' + '\n' + str(scoring))
    # add summations initialize
    for func, value in scoring.items():
        #
        for worker_name, value2 in scoring[func].items():
            scoring[func][worker_name]['sum_worker_scores'] = 0
        scoring[func]['sum_function_scores'] = 0
    # E.g.,
    # print(scoring['f1'])
    # print(scoring['f1']['w1'])
    # print(scoring['f1']['w1']['energy'])
    # print(scoring['f1']['sum_func_score'])
    # print(scoring['f1']['w1']['sum_worker_score'])

    logger.info('hospital_resident: sum ' + '\n' + str(scoring))
    #scores = {'function1': 
    #               {
    #                   node1: 
    #                       {energy:0, locality:0, sticky:0, sum_worker_scores:0}, 
    #                   sum_function_scores:0
    #               },
    #        }
    # calculate and set soc percent and normalize to -1-1 (index 4 of worker used for soc percent, instead of zone)
    for worker in workers:
        soc = worker[2]
        # assume all nodes have batteries of same size????
        # max_battery_charge = copy.deepcopy(nodes_plan[worker[0]]["battery_cfg"][1])
        soc_percent = round(soc / max_battery_charge * 100)
        logger.info(worker[0] + ' soc : ' + str(soc_percent) + ' %')
        # normalize to 0-1
        worker[4] = round(soc_percent / 100, 2)

    logger.info('hospital_resident:updated soc %:\n'
                + '\n'.join([str(worker) for worker in workers]))

    # so far, new_functions have [] as hosts, workers have full as capacity and both workers and new_functions are sorted now
    logger.info('hospital_resident: start setting scores per functions')
    for new_function in new_functions:
        # function_name
        function_name = new_function[0][0] + '-' + new_function[0][1]
        logger.info('hospital_resident: functions **** ' + function_name + '  ****')
        logger.info('workers:\n'
                    + '\n'.join([str(worker) for worker in workers]))
        # function's old_hosts: last placement scheme
        old_hosts = copy.deepcopy([*(function[1] for function in functions if function[0] == new_function[0])][0])

        # old_hosts have soc value based on last epoch, so update them
        for index, old_host in enumerate(old_hosts):
            # update host's zone, capacity and Soc based on current status
            old_hosts[index] = [*(worker for worker in workers if worker[0] == old_host[0])][0]
        logger.info('old_hosts\n' + str(old_hosts))

        # function's owner
        owner = [*(worker for worker in workers if worker[0] == new_function[0][0])][0]
        owner_name = owner[0]
        # owner soc normalized
        owner_soc_normalized = copy.deepcopy(owner[4])

        logger.info(f'start scoring for {function_name} by plugins={plugins}')
        # score per node
        for worker in workers:
            worker_name = copy.deepcopy(worker[0])
            worker_soc_normalized = copy.deepcopy(worker[4])

            # per plugin
            # energy
            # deduct remote soc from owner
            scoring[function_name][worker_name]['energy'] = (round((
                                                                           worker_soc_normalized - owner_soc_normalized) *
                                                                   plugins['energy'], 2))

            # locally
            if owner_name == worker_name:
                # if itself, score locally
                scoring[function_name][worker_name]['locally'] = (round(
                    owner_soc_normalized * plugins['locally'], 2))
            else:
                # default 0
                pass

            # sticky
            # assume first replica (old_hosts[0]) location represents the whole replicas  ???
            if old_hosts[0][0] != owner_name:
                # has been offloaded in last round
                if old_hosts[0][0] == worker_name:
                    # if this worker was the last place
                    scoring[function_name][worker_name]['sticky'] = (
                        round(1 * plugins['sticky'], 2))
                else:
                    # default 0
                    pass
            else:
                # default 0
                pass
            # sum worker scores
            scoring[function_name][worker_name]['sum_worker_scores'] = (
                    scoring[function_name][worker_name]['energy']
                    + scoring[function_name][worker_name]['locally']
                    + scoring[function_name][worker_name]['sticky'])

        # sum function scores
        for key, value in scoring[function_name].items():
            worker_name = key
            # items, except the summation
            if worker_name != 'sum_function_scores':
                # add per worker
                scoring[function_name]['sum_function_scores'] += (
                    scoring[function_name][worker_name]['sum_worker_scores'])
        logger.info('hospital_resident: end scoring for ' + function_name + '\n' +
                    str(scoring[function_name]))

    # end scoring
    logger.info('scoring done:' + '\n'.join(str(func) + str(info) for func, info in scoring.items()))


    #scores = {'function1': 
    #               {
    #                   node1: 
    #                       {energy:0, locality:0, sticky:0, sum_worker_scores:0}, 
    #                   sum_function_scores:0
    #               },
    #        }
    functions_prefs = {}
    workers_prefs = {}
    workers_caps= {}

    #set functions_prefs
    #prepare a dict with keys equal to func_names and value for each item is a list of worker_names that are sorted as preferences of a function based on the sum_worker_scores given to the worker by the function.
    #search over all functions : name and scores
    for func_name, func_scores in scoring.items():
        #prepare an unsorted preference list for the function. Each item will be a tuple (worker name, sum_worker_scores)
        func_prefs = []
        #search over all (only) workers scored for this funciton - exclude sum_funcion_scores
        #k is a worker name or sum_function_scores wheras a v is the scores a function has given to workers + sum_function_scores that is not needed here
        for k, v in func_scores.items():
            #prepare a new preference tuple per worker that will have (worker name, sum_worker_scores) pairs
            new_pref = ()
            #exclude the key that is not a worker scores
            if k!= 'sum_function_scores':
                #new worker tuple = (worker name, sum_worker_scores)
                new_pref=(k, v['sum_worker_scores'])
                func_prefs.append(new_pref)

        #func_prefs list is ready.
        #now sort it and convert the tuple (worker name, sum_worker_scores) items to a sorted list of worker names only
        #Example func_prefs = [('homo1', 10), ('homo3', 30), ('homo2', 20)]

        # Sort the list of tuples based on the second item (index 1) from largest to smallest
        sorted_list = sorted(func_prefs, key=lambda x: x[1], reverse=True)

        # Create a new list with only the sorted first elements
        sorted_first_elements = [item[0] for item in sorted_list]
        #add function with its preferences to the list
        functions_prefs[func_name] = sorted_first_elements


    #set workers_prefs
    #get a worker_name and prepare a list of  sorted func_names for it as its preferences based on functions sum_function_scores which means a needing function (the one with more given scores to nodes) is prefered over others
    for worker in workers:
        worker_name = worker[0]
        worker_prefs = []
        #search in all functions scores and per function pick a tuple that contains (func_name and sum_function_scores) and add this tuple to the list of worker_prefs
        for func_name, func_scores in scoring.items():
            new_pref = ()
            #per function only pick the key that is equal to sum_function_scores
            for k, v in func_scores.items():
                if k == 'sum_function_scores':
                    #v = 'sum_function_scores'
                    new_pref = (func_name, v)
                    worker_prefs.append(new_pref)
        #worker_prefs list is ready
        #now sort the prefs and make it a list of only sorted func_names
        #Example func_prefs = [('homo1-ssd', 10), ('homo3-ssd', 30), ('homo2-ssd', 20)]

        # Sort the list of tuples based on the second item (index 1) from largest to smallest
        sorted_list = sorted(worker_prefs, key=lambda x: x[1], reverse=True)

        # Create a new list with only the sorted first elements
        sorted_first_elements = [item[0] for item in sorted_list]
        #add function with its preferences to the list
        workers_prefs[worker_name] = sorted_first_elements

    #set workers_caps = {}
    for worker in workers:
        worker_name = worker[0]
        workers_caps[worker_name] = setup.hospital_and_mthg_placment_capacity
    

    #solve matching
    from matching.games import HospitalResident

    resident_preferences = functions_prefs
    hospital_preferences = workers_prefs
    hospital_capacities = workers_caps
    logger.info('*******    start matching    *******')
    game = HospitalResident.create_from_dictionaries(
        resident_preferences, hospital_preferences, hospital_capacities
    )

    matching = game.solve(optimal="resident")
    logger.info(f'hospital matching\n={matching}')

    logger.info('*******    check validity    *******')
    assert game.check_validity()
    logger.info('*******    check validity    *******')
    assert game.check_stability()

    logger.info('*******    check complete matching    *******')
    matched_residents = []
    for _, residents in matching.items():
        for resident in residents:
            matched_residents.append(resident.name)

    unmatched_residents = set(resident_preferences.keys()) - set(matched_residents)
    if len(unmatched_residents) > 0:
        logger.error(f'unmatched residents: {unmatched_residents}')
    else:
        logger.info(f'unmatched residents: {unmatched_residents}')
    
    #result of matching example matching = {worker_name: [func_name, ................], ....}
    #convert matching results to assignments. 
    #for each worker_name, pick its assigned functions one by one, then for each function, set its new-hosts to the worker and do not need to check for capacity constraints as it is already considered in the game by workers_caps
    
    for worker_name, assigned_functions in matching.items():
        for func_name in assigned_functions:
            # get full function
            new_function = [*(new_function for new_function in new_functions if
                            new_function[0][0] == func_name.name.split('-')[0] and new_function[0][1] ==
                            func_name.name.split('-', 1)[1])][0]


            # function required capacity
            func_required_cpu_capacity = 0
            # exclude 'm'
            replica_cpu_reqs = int(new_function[2][4].split('m')[0])
            func_max_replica = new_function[2][1]
            func_required_cpu_capacity = replica_cpu_reqs * func_max_replica

            # placement
            # set new hosts
            new_hosts = []

            # get the worker
            worker = [*(worker for worker in workers if worker[0] == worker_name.name)][0]

            # set new_hosts
            for rep in range(func_max_replica):
                new_hosts.append(copy.deepcopy(worker))

            logger.info('deduct capacity for ' + func_name.name)
            # deduct function cpu requirement from worker's cpu capacity
            for new_host in new_hosts:
                # get selected worker index per replica
                index = workers.index([*(worker for worker in workers if worker[0] == new_host[0])][0])
                # deduct replica cpu requirement
                workers[index][3] -= replica_cpu_reqs
                # update new_host, particulalrly its capacity
                new_host[3] = workers[index][3]

            # set new_function new hosts
            new_function[1] = new_hosts
            if debug: logger.info("hospital_resident: new_hosts for ("
                                + new_function[0][0] + "-" + new_function[0][1] + "):\n" + str(new_function[1]))


    return workers, new_functions

#first_fit_decreasing
#1-scoring
#2-sort functions by sum_function_scores from largest to smallest
#3-sort workers by sum_worker_scores from largest to smallest
#4- assign functions one by one to the first available worker given capacity constraints.
def scheduler_planner_first_fit_decreasing(workers, functions, new_functions,
                                max_battery_charge, warm_scheduler, plugins, debug, scheduling_round):
    global logger


    # workers have full capacity available
    # new_functions have null as hosts

    logger.info(f"FFD:start {scheduling_round}")
    logger.info('FFD:\n available Workers \n'
                + '\n'.join([str(worker) for worker in workers]))

    # define and initialize scoring scheme
    scoring = {new_function[0][0] + '-' + new_function[0][1]:
                   {worker[0]:
                        {plugin: 0 for plugin in plugins}
                    for worker in workers} for new_function in new_functions}
    logger.info('FFD: set ' + '\n' + str(scoring))
    # add summations initialize
    for func, value in scoring.items():
        #
        for worker_name, value2 in scoring[func].items():
            scoring[func][worker_name]['sum_worker_scores'] = 0
        scoring[func]['sum_function_scores'] = 0
    # E.g.,
    # print(scoring['f1'])
    # print(scoring['f1']['w1'])
    # print(scoring['f1']['w1']['energy'])
    # print(scoring['f1']['sum_func_score'])
    # print(scoring['f1']['w1']['sum_worker_score'])

    logger.info('FFD: sum ' + '\n' + str(scoring))
    #scores = {'function1': 
    #               {
    #                   node1: 
    #                       {energy:0, locality:0, sticky:0, sum_worker_scores:0}, 
    #                   sum_function_scores:0
    #               },
    #        }
    # calculate and set soc percent and normalize to -1-1 (index 4 of worker used for soc percent, instead of zone)
    for worker in workers:
        soc = worker[2]
        # assume all nodes have batteries of same size????
        # max_battery_charge = copy.deepcopy(nodes_plan[worker[0]]["battery_cfg"][1])
        soc_percent = round(soc / max_battery_charge * 100)
        logger.info(worker[0] + ' soc : ' + str(soc_percent) + ' %')
        # normalize to 0-1
        worker[4] = round(soc_percent / 100, 2)

    logger.info('FFD:updated soc %:\n'
                + '\n'.join([str(worker) for worker in workers]))

    # so far, new_functions have [] as hosts, workers have full as capacity and both workers and new_functions are sorted now
    logger.info('FFD: start setting scores per functions')
    for new_function in new_functions:
        # function_name
        function_name = new_function[0][0] + '-' + new_function[0][1]
        logger.info('FFD: functions **** ' + function_name + '  ****')
        logger.info('workers:\n'
                    + '\n'.join([str(worker) for worker in workers]))
        # function's old_hosts: last placement scheme
        old_hosts = copy.deepcopy([*(function[1] for function in functions if function[0] == new_function[0])][0])

        # old_hosts have soc value based on last epoch, so update them
        for index, old_host in enumerate(old_hosts):
            # update host's zone, capacity and Soc based on current status
            old_hosts[index] = [*(worker for worker in workers if worker[0] == old_host[0])][0]
        logger.info('old_hosts\n' + str(old_hosts))

        # function's owner
        owner = [*(worker for worker in workers if worker[0] == new_function[0][0])][0]
        owner_name = owner[0]
        # owner soc normalized
        owner_soc_normalized = copy.deepcopy(owner[4])

        logger.info(f'start scoring for {function_name} by plugins={plugins}')
        # score per node
        for worker in workers:
            worker_name = copy.deepcopy(worker[0])
            worker_soc_normalized = copy.deepcopy(worker[4])

            # per plugin
            # energy
            # deduct remote soc from owner
            scoring[function_name][worker_name]['energy'] = (round((
                                                                           worker_soc_normalized - owner_soc_normalized) *
                                                                   plugins['energy'], 2))

            # locally
            if owner_name == worker_name:
                # if itself, score locally
                scoring[function_name][worker_name]['locally'] = (round(
                    owner_soc_normalized * plugins['locally'], 2))
            else:
                # default 0
                pass

            # sticky
            # assume first replica (old_hosts[0]) location represents the whole replicas  ???
            if old_hosts[0][0] != owner_name:
                # has been offloaded in last round
                if old_hosts[0][0] == worker_name:
                    # if this worker was the last place
                    scoring[function_name][worker_name]['sticky'] = (
                        round(1 * plugins['sticky'], 2))
                else:
                    # default 0
                    pass
            else:
                # default 0
                pass
            # sum worker scores
            scoring[function_name][worker_name]['sum_worker_scores'] = (
                    scoring[function_name][worker_name]['energy']
                    + scoring[function_name][worker_name]['locally']
                    + scoring[function_name][worker_name]['sticky'])

        # sum function scores
        for key, value in scoring[function_name].items():
            worker_name = key
            # items, except the summation
            if worker_name != 'sum_function_scores':
                # add per worker
                scoring[function_name]['sum_function_scores'] += (
                    scoring[function_name][worker_name]['sum_worker_scores'])
        logger.info('FFD: end scoring for ' + function_name + '\n' +
                    str(scoring[function_name]))

    # end scoring
    logger.info('scoring done:' + '\n'.join(str(func) + str(info) for func, info in scoring.items()))

    logger.info(f"FFD:preparing sorted functions and workers {scheduling_round}")

    #scores = {'function1': 
    #               {
    #                   node1: 
    #                       {energy:0, locality:0, sticky:0, sum_worker_scores:0}, 
    #                   sum_function_scores:0
    #               },
    #        }

    sorted_sum_functions_scores = [] # sorted from largest to smallest by sum_func_scores = [(func_name, sum_func_scores),]
    for func_name, func_scores in scoring.items():
        
        #k is a worker name or sum_function_scores wheras a v is the scores a function has given to workers + sum_function_scores that is not needed here
        for k, v in func_scores.items():
            if k == 'sum_function_scores':
                sorted_sum_functions_scores.append((func_name, v))
                break

    #sort it
    sorted_sum_functions_scores = sorted(sorted_sum_functions_scores, key=lambda x: x[1],reverse=True)
    logger.info(f"FFD:sorted_sum_functions_scores {sorted_sum_functions_scores}")

    sorted_sum_workers_scores = [] # sorted from largest to smallest by sum_worker_scores = [(worker_name, sum_worker_scores),]
    #per worker
    for worker in workers:
        worker_name = worker[0]
        #calculate sum of the scores given to it by funcitons through sum_worker_scores
        sum_worker_scores = 0
        #per function
        for func_name, func_scores in scoring.items():
            #among all key values
            for k, v in func_scores.items():
                #pick only key value that is sum_worker_scores and for this worker_name
                if k != 'sum_function_scores' and k == worker_name:
                    sum_worker_scores += v['sum_worker_scores']
                    break
        sorted_sum_workers_scores.append((worker_name, sum_worker_scores))

    #sort it
    sorted_sum_workers_scores = sorted(sorted_sum_workers_scores, key=lambda x: x[1],reverse=True)
    logger.info(f"FFD:sorted_sum_workers_scores {sorted_sum_workers_scores}")

    #assignment
    #assign functions to workers with capacity
    for func_name, _ in sorted_sum_functions_scores:
        logger.info(f"FFD:assigning {func_name}")

        #go through all available sorted workers and pick the first one that has enough capacity
        for worker_name, _ in sorted_sum_workers_scores:
            logger.info(f"FFD:worker_name {worker_name}")
            # get full function
            new_function = [*(new_function for new_function in new_functions if
                            new_function[0][0] == func_name.split('-')[0] and new_function[0][1] ==
                            func_name.split('-', 1)[1])][0]


            # function required capacity
            func_required_cpu_capacity = 0
            # exclude 'm'
            replica_cpu_reqs = int(new_function[2][4].split('m')[0])
            func_max_replica = new_function[2][1]
            func_required_cpu_capacity = replica_cpu_reqs * func_max_replica

            # placement
            # set new hosts
            new_hosts = []

            # get the worker
            worker = [*(worker for worker in workers if worker[0] == worker_name)][0]

            #capacity check
            if worker[3] < func_required_cpu_capacity:
                logger.info(f"FFD:not enough capacity for {func_name}")
                continue
            
            # set new_hosts
            for rep in range(func_max_replica):
                new_hosts.append(copy.deepcopy(worker))

            logger.info('deduct capacity for ' + func_name)
            # deduct function cpu requirement from worker's cpu capacity
            for new_host in new_hosts:
                # get selected worker index per replica
                index = workers.index([*(worker for worker in workers if worker[0] == new_host[0])][0])
                # deduct replica cpu requirement
                workers[index][3] -= replica_cpu_reqs
                # update new_host, particulalrly its capacity
                new_host[3] = workers[index][3]

            # set new_function new hosts
            new_function[1] = new_hosts
            if debug: logger.info("FFD: new_hosts for ("
                                + new_function[0][0] + "-" + new_function[0][1] + "):\n" + str(new_function[1]))

            break

    return workers, new_functions

#mthg
#Prepare scoring
#prepare functions preferences to nodes (NO the other way around)
#prepare assignment variables as profits, capacities, and weights
#calculate profits using preferences
#solve assignment using mknapsack module
#extract results and convert them to correct format

def scheduler_planner_mthg(workers, functions, new_functions,
                                max_battery_charge, warm_scheduler, plugins, debug, scheduling_round):
    global logger

    # workers have full capacity available
    # new_functions have null as hosts

    logger.info(f"MTH:start {scheduling_round}")
    logger.info('MTH:\n available Workers \n'
                + '\n'.join([str(worker) for worker in workers]))

    # define and initialize scoring scheme
    scoring = {new_function[0][0] + '-' + new_function[0][1]:
                   {worker[0]:
                        {plugin: 0 for plugin in plugins}
                    for worker in workers} for new_function in new_functions}
    logger.info('MTH: set ' + '\n' + str(scoring))
    # add summations initialize
    for func, value in scoring.items():
        #
        for worker_name, value2 in scoring[func].items():
            scoring[func][worker_name]['sum_worker_scores'] = 0
        scoring[func]['sum_function_scores'] = 0
    # E.g.,
    # print(scoring['f1'])
    # print(scoring['f1']['w1'])
    # print(scoring['f1']['w1']['energy'])
    # print(scoring['f1']['sum_func_score'])
    # print(scoring['f1']['w1']['sum_worker_score'])

    logger.info('MTH: sum ' + '\n' + str(scoring))
    #scores = {'function1': 
    #               {
    #                   node1: 
    #                       {energy:0, locality:0, sticky:0, sum_worker_scores:0}, 
    #                   sum_function_scores:0
    #               },
    #        }
    # calculate and set soc percent and normalize to -1-1 (index 4 of worker used for soc percent, instead of zone)
    for worker in workers:
        soc = worker[2]
        # assume all nodes have batteries of same size????
        # max_battery_charge = copy.deepcopy(nodes_plan[worker[0]]["battery_cfg"][1])
        soc_percent = round(soc / max_battery_charge * 100)
        logger.info(worker[0] + ' soc : ' + str(soc_percent) + ' %')
        # normalize to 0-1
        worker[4] = round(soc_percent / 100, 2)

    logger.info('MTH:updated soc %:\n'
                + '\n'.join([str(worker) for worker in workers]))

    # so far, new_functions have [] as hosts, workers have full as capacity and both workers and new_functions are sorted now
    logger.info('MTH: start setting scores per functions')
    for new_function in new_functions:
        # function_name
        function_name = new_function[0][0] + '-' + new_function[0][1]
        logger.info('MTH: functions **** ' + function_name + '  ****')
        logger.info('workers:\n'
                    + '\n'.join([str(worker) for worker in workers]))
        # function's old_hosts: last placement scheme
        old_hosts = copy.deepcopy([*(function[1] for function in functions if function[0] == new_function[0])][0])

        # old_hosts have soc value based on last epoch, so update them
        for index, old_host in enumerate(old_hosts):
            # update host's zone, capacity and Soc based on current status
            old_hosts[index] = [*(worker for worker in workers if worker[0] == old_host[0])][0]
        logger.info('old_hosts\n' + str(old_hosts))

        # function's owner
        owner = [*(worker for worker in workers if worker[0] == new_function[0][0])][0]
        owner_name = owner[0]
        # owner soc normalized
        owner_soc_normalized = copy.deepcopy(owner[4])

        logger.info(f'start scoring for {function_name} by plugins={plugins}')
        # score per node
        for worker in workers:
            worker_name = copy.deepcopy(worker[0])
            worker_soc_normalized = copy.deepcopy(worker[4])

            # per plugin
            # energy
            # deduct remote soc from owner
            scoring[function_name][worker_name]['energy'] = (round((
                                                                           worker_soc_normalized - owner_soc_normalized) *
                                                                   plugins['energy'], 2))

            # locally
            if owner_name == worker_name:
                # if itself, score locally
                scoring[function_name][worker_name]['locally'] = (round(
                    owner_soc_normalized * plugins['locally'], 2))
            else:
                # default 0
                pass

            # sticky
            # assume first replica (old_hosts[0]) location represents the whole replicas  ???
            if old_hosts[0][0] != owner_name:
                # has been offloaded in last round
                if old_hosts[0][0] == worker_name:
                    # if this worker was the last place
                    scoring[function_name][worker_name]['sticky'] = (
                        round(1 * plugins['sticky'], 2))
                else:
                    # default 0
                    pass
            else:
                # default 0
                pass
            # sum worker scores
            scoring[function_name][worker_name]['sum_worker_scores'] = (
                    scoring[function_name][worker_name]['energy']
                    + scoring[function_name][worker_name]['locally']
                    + scoring[function_name][worker_name]['sticky'])

        # sum function scores
        for key, value in scoring[function_name].items():
            worker_name = key
            # items, except the summation
            if worker_name != 'sum_function_scores':
                # add per worker
                scoring[function_name]['sum_function_scores'] += (
                    scoring[function_name][worker_name]['sum_worker_scores'])
        logger.info('MTH: end scoring for ' + function_name + '\n' +
                    str(scoring[function_name]))

    # end scoring
    logger.info('MTH scoring done:' + '\n'.join(str(func) + str(info) for func, info in scoring.items()))


    logger.info(f'MTH:assignment start {scheduling_round}')
    #assignment

    #scores = {'function1': 
    #               {
    #                   node1: 
    #                       {energy:0, locality:0, sticky:0, sum_worker_scores:0}, 
    #                   sum_function_scores:0
    #               },
    #        }
    

    
    functions_prefs = {}

    #set functions_prefs
    #prepare a dict with keys equal to func_names and value for each item is a list of worker_names that are sorted as preferences of a function based on the sum_worker_scores given to the worker by the function.
    #search over all functions : name and scores
    

    for func_name, func_scores in scoring.items():
        
        #prepare an unsorted preference list for the function. Each item will be a tuple (worker name, sum_worker_scores)
        func_prefs = []
        #search over all (only) workers scored for this funciton - exclude sum_funcion_scores
        #k is a worker name or sum_function_scores wheras a v is the scores a function has given to workers + sum_function_scores that is not needed here
        for k, v in func_scores.items():
            #prepare a new preference tuple per worker that will have (worker name, sum_worker_scores) pairs
            new_pref = ()
            #exclude the key that is not a worker scores
            if k!= 'sum_function_scores':
                #new worker tuple = (worker name, sum_worker_scores)
                #the solver only accepts input values >= 1q
                new_pref=(k, v['sum_worker_scores'] if v['sum_worker_scores'] >=1 else 1)
                func_prefs.append(new_pref)

        #func_prefs list is ready.
        #Example func_prefs = [('homo1', 10), ('homo3', 30), ('homo2', 20)]

        #add function with its preferences to the list
        functions_prefs[func_name] = func_prefs

    #functions_prefs is ready.
    #Example 
    # functions_prefs={'homo1-ssd': [('homo3',5), ('homo1',1), ('homo2',1)],
                    # 'homo2-ssd': [('homo1',2), ('homo2',5), ('homo3',1)],
                    # 'homo3-ssd': [('homo1',5), ('homo2',3), ('homo3',1)],
                    # 'homo4-ssd': [('homo1',3), ('homo2',4), ('homo3',5)],
                    # 'homo5-ssd': [('homo1',2), ('homo2',1), ('homo3',5)],
                    # }


    #GAP input preparation

    from mknapsack import solve_generalized_assignment

    #profits sample
    # profits = [[1,2,5,3,2],
    #         [1,5,3,4,1],
    #         [5,1,1,5,5]]
    #profits matrix
        #         func1 func2 func3
        #        _________________
        # worker1|1      1    1
        # worker2|1      2    1
        # worker3|3      1    2
    #it means func 1 has preference to worker 3, 2 and then 1
    #it means worker 3 has preference to func 1, 3 and then  2

    #GAP inputs
    #set weights
    weights = [[1]* len(new_functions) for worker in workers]
    #set capacities
    capacities = [setup.hospital_and_mthg_placment_capacity] * len(workers)

    #The profit of placing a function on each node
    profits = [[-1]* len(new_functions) for worker in workers]

    #set profits from preferences by creating a matrix of profits

    for func_name, func_prefs in functions_prefs.items():
        #func_name like homo1-ssd
        #get function id like 1
        func_id = int(re.search(r'\d+', func_name).group())

        #id starts from 1 but list index from 0, so deduct 1
        func_id -=1

        #get preferenced worker names one by one
        
        #pick the func_pref = (worker_name, given score)
        for func_pref in func_prefs:

            worker_name = func_pref[0]
            #worker_name os like homo1
            #get worker id like 1
            worker_id = int(re.search(r'\d+', worker_name).group())

            #id starts from 1 but list index from 0, so deduct 1
            worker_id -=1
            
            #given_score
            given_score = func_pref[1]

            #update profits
            profits[worker_id][func_id] = given_score
            

    logger.info(f'profits={profits}')
    logger.info(f'weights={weights}')
    logger.info(f'capacities={capacities}')    

    #solve matching
    #Implementation: https://mknapsack.readthedocs.io/en/latest/readme.html#generalized-assignment-problem
    
    #MTHG Book + code: Martello, Silvano, and Paolo Toth. Knapsack problems: algorithms and computer implementations. John Wiley & Sons, Inc., 1990.

    #Exact Paper that proposed the algorithm: 
    #https://scholar.google.com/scholar?hl=en&as_sdt=0%2C5&q=Martello%2C+Silvano%2C+and+Paolo+Toth.+An+algorithm+for+the+generalized+assignment+problem.+Operational+research%2C+1981&btnG=
    
    # Martello, S. P. "Toth., An algorithm for the generalized assignment problem, operational Research’81, ed. JP Brans." (1981): 589-603.
    
    #Description: It is a polynomial-time approximate solution to GAP using a branch and bound method. The overal time complexity of the algorithm is O(nmlogm + n^2) where n is items and m is bins The desirability of 
    # assigning a function to a node is determined in two phases of identifying the maximum difference between the largest and second largest feasible solution for an initial assignment and then improving the 
    #solution through local exchanges.

    assignments = solve_generalized_assignment(profits, weights, capacities, verbose=True, method='mthg')
    #Example [3 2 1 2 3] means function 1 on worker 3 and function 2 on worker 2 ,...
    #it also gives index starting from 1
    logger.info(f'assignments={assignments}')
    #Example assignments=[ 6 10 10  9  3  3  2  7  7  6] each item is the id of a worker and each index is the index+1 of a function

    #convert results to proper format
    func_index = 1
    for selected_node_id in assignments:
        #as indexes in the list start from 0 but host names start from 1, add 1
        # selected_node_id += 1

        worker_name = 'homo' + str(selected_node_id)

        #function name
        func_name = 'homo' + str(func_index) + '-ssd' 

        logger.info(f'assign function {func_name} to worker {worker_name}')

        func_index += 1

        #get new_function
        for new_function in new_functions:
            if new_function[0][0] == func_name.split('-')[0] and new_function[0][1] == func_name.split('-')[1]:
                logger.info(f'function found {new_function}')
                # function required capacity
                func_required_cpu_capacity = 0
                # exclude 'm'
                replica_cpu_reqs = int(new_function[2][4].split('m')[0])
                func_max_replica = new_function[2][1]
                func_required_cpu_capacity = replica_cpu_reqs * func_max_replica

                # placement
                # set new hosts
                new_hosts = []

                # get the worker
                worker = [*(worker for worker in workers if worker[0] == worker_name)][0]

                logger.info('fworker found {worker}')

                # set new_hosts
                for rep in range(func_max_replica):
                    new_hosts.append(copy.deepcopy(worker))

                logger.info('deduct capacity for ' + func_name)
                # deduct function cpu requirement from worker's cpu capacity
                for new_host in new_hosts:
                    # get selected worker index per replica
                    index = workers.index([*(worker for worker in workers if worker[0] == new_host[0])][0])
                    # deduct replica cpu requirement
                    workers[index][3] -= replica_cpu_reqs
                    # update new_host, particulalrly its capacity
                    new_host[3] = workers[index][3]

                # set new_function new hosts
                new_function[1] = new_hosts
                if debug: logger.info("MTH: new_hosts for ("
                                    + new_function[0][0] + "-" + new_function[0][1] + "):\n" + str(new_function[1]))

                #only one function matches the selection
                break

    logger.info(f'MTH planning done {scheduling_round}')

    return workers, new_functions

#getFunctionName
def getFunctionName(function):
    return function[0][0] + '-' + function[0][1]


def localizer(worker, new_functions, scores_tmp):
    global logger
    logger.info('localizer: start for worker ' + str(worker))
    logger.info('localizer: scores_tmp \n' + str(scores_tmp))
    worker_name = worker[0]

    # get functions of the worker
    for new_function in new_functions:
        # get function name
        function_name = getFunctionName(new_function)
        # get function owner
        function_owner = new_function[0][0]
        # if this function belongs to the worker, place locally
        if function_owner == worker[0]:
            logger.info('localizer: placement for ----- ' + function_name + ' -----')
            # if already placed, skip
            hosts = new_function[1]
            # if hosts not set yet
            if hosts != []:
                logger.info('localizer: already done, localizer skip for ' + function_name)
                continue
            # else place locally
            else:

                # function required capacity
                func_required_cpu_capacity = 0
                # exclude 'm'
                replica_cpu_reqs = int(new_function[2][4].split('m')[0])
                func_max_replica = new_function[2][1]
                func_required_cpu_capacity = replica_cpu_reqs * func_max_replica

                # placement
                # set new hosts
                new_hosts = []
                logger.info('localizer: placement locally for ' + function_name)
                for rep in range(func_max_replica):
                    new_hosts.append(copy.deepcopy(worker))

                # deduct capacity
                logger.info('localizer: deduct capacity for ' + function_name)
                # deduct function cpu requirement from worker's cpu capacity
                for new_host in new_hosts:
                    # deduct replica cpu requirement
                    worker[3] -= replica_cpu_reqs
                    # update new_host, particulalrly its capacity
                    new_host[3] = worker[3]

                # set new_function new hosts
                new_function[1] = new_hosts
                if debug: logger.info("localizer: new_hosts for ("
                                      + new_function[0][0] + "-" + new_function[0][1] + "):\n" + str(new_function[1]))

                # delete
                del scores_tmp[function_name]
                logger.info('localizer: deleted scores_tmp: ' + str(scores_tmp))

    return worker, new_functions, scores_tmp


# -----------------
# ??? functions are received for only getting old_hosts. Only old_hosts can be sent to this planner
#ccgrid
def scheduler_planner_greedy(workers, functions, new_functions, max_battery_charge, zones,
                             warm_scheduler, sticky, stickiness, scale_to_zero, debug):
    global logger
    logger.info("scheduler_planner_greedy:start")
    logger.info('scheduler_planner_greedy:\n available Workers \n'
                + '\n'.join([str(worker) for worker in workers]))
    zone_name = {1: 'rich', 2: 'poor', 3: 'vulnerable', 4: 'dead'}
    # update zones
    for worker in workers:
        soc = worker[2]
        # assume nodes have same size battery???
        # max_battery_charge = copy.deepcopy(nodes_plan[worker[0]]["battery_cfg"][1])
        soc_percent = round(soc / max_battery_charge * 100)
        logger.info('soc percent: ' + str(soc_percent))
        new_zone = [*(zone[1] for zone in zones if soc_percent <= zone[2]
                      and soc_percent > zone[3])][0]
        worker[4] = new_zone

    logger.info('scheduler_planner_greedy:updated zones by Soc:\n'
                + '\n'.join([str(worker) for worker in workers]))

    # sort nodes by soc (large->small | descending)
    workers.sort(key=lambda x: x[2], reverse=True)
    logger.info('before showing : ' + str(workers))
    logger.info('scheduler_planner_greedy:sorted nodes by Soc (large->small):\n'
                + '\n'.join([str([worker, zone_name[worker[4]]]) for worker in workers]))
    logger.info('after showing : ' + str(workers))
    # sort functions: A: by priority of their owner's zone (small -> large | ascending)
    for i in range(len(new_functions)):
        lowest_value_index = i
        for j in range(i + 1, len(new_functions)):
            # find function's owner zone
            zone_j = [*(worker[4] for worker in workers if worker[0] == new_functions[j][0][0])][0]
            zone_lowest_value_index = \
            [*(worker[4] for worker in workers if worker[0] == new_functions[lowest_value_index][0][0])][0]
            # compare zone priorities
            if zone_j < zone_lowest_value_index:
                lowest_value_index = j
        # swap
        new_functions[i], new_functions[lowest_value_index] = new_functions[lowest_value_index], new_functions[i]
    # end sort
    logger.info('scheduler_planner_greedy:sorted functions by owner\'s zone priority (small->large):\n'
                + '\n'.join([str(new_function[0]) for new_function in new_functions]))

    # B: sort functions in each zone (small to large for poor and vulnerable) opposite dead, for rich does not matter
    for i in range(len(new_functions)):
        lowest_value_index = i
        largest_value_index = i
        lowest, largest = False, False
        zone_i = [*(worker[4] for worker in workers if worker[0] == new_functions[i][0][0])][0]
        # rich or dead
        if zone_i == 1 or zone_i == 4:
            # largest first
            largest = True
        # poor or vulnerable
        else:
            lowest = True

        for j in range(i + 1, len(new_functions)):
            # get function's owner zone
            zone_j = [*(worker[4] for worker in workers if worker[0] == new_functions[j][0][0])][0]
            zone_lowest_value_index = \
            [*(worker[4] for worker in workers if worker[0] == new_functions[lowest_value_index][0][0])][0]
            zone_largest_value_index = \
            [*(worker[4] for worker in workers if worker[0] == new_functions[largest_value_index][0][0])][0]
            if zone_j == zone_lowest_value_index:  # similar to say ==largest_value_index
                # get functions' owner soc
                soc_j = [*(worker[2] for worker in workers if worker[0] == new_functions[j][0][0])][0]
                soc_lowest_value_index = \
                [*(worker[2] for worker in workers if worker[0] == new_functions[lowest_value_index][0][0])][0]
                soc_largest_value_index = \
                [*(worker[2] for worker in workers if worker[0] == new_functions[largest_value_index][0][0])][0]
                # compare socs based on zones policy
                # if rich or dead , large to small
                if zone_largest_value_index == 1 or zone_largest_value_index == 4:
                    if soc_j > soc_largest_value_index:
                        largest_value_index = j
                # if poor or vulnerable, small to large
                elif zone_lowest_value_index == 2 or zone_lowest_value_index == 3:
                    if soc_j < soc_lowest_value_index:
                        lowest_value_index = j
        # swap
        if lowest:
            index = lowest_value_index
        else:
            index = largest_value_index
        new_functions[i], new_functions[index] = new_functions[index], new_functions[i]
    logger.info(
        'scheduler_planner_greedy:sorted functions by soc in zones (poor and vulnerable small to large. Rich and dead opposite):\n'
        + '\n'.join([str(new_function[0]) for new_function in new_functions]))

    # so far, new_functions have [] as hosts, workers have full as capacity and both workers and new_functions are sorted now
    logger.info("scheduler_planner_greedy: start planning hosts for functions by priority")
    # PLAN
    # set hosts per function
    for new_function in new_functions:
        # function's old_hosts: last placement scheme
        old_hosts = copy.deepcopy([*(function[1] for function in functions if function[0] == new_function[0])][0])

        # old_hosts have zone numbers and Soc based on last epoch and the hosts zone may have changed now, so update their zones based on new status
        for index, old_host in enumerate(old_hosts):
            # update host's zone, capacity and Soc based on current status
            old_hosts[index] = [*(worker for worker in workers if worker[0] == old_host[0])][0]
        logger.info('greedy: old_hosts\n' + str(old_hosts))

        # function's owner
        owner = [*(worker for worker in workers if worker[0] == new_function[0][0])][0]
        func_required_cpu_capacity = 0
        # exclude 'm'
        replica_cpu_reqs = int(new_function[2][4].split('m')[0])
        func_max_replica = new_function[2][1]
        func_required_cpu_capacity = replica_cpu_reqs * func_max_replica
        owner_zone = owner[4]
        logger.info('greedy: planning for *** ' + str(new_function[0][0]) + '-'
                    + str(new_function[0][1]) + ' *** ')
        # try to fill new hosts for new_function
        new_hosts = []
        # if new_function belongs to a rich node
        if owner_zone == 1:
            # place locally
            logger.info('greedy: ' + owner[0] + '-' + new_function[0][1] + ' ---> locally')
            for rep in range(func_max_replica):
                new_hosts.append(copy.deepcopy(owner))

        # if poor, vulnerable or dead
        else:
            # if offloading
            # if setup.offloading == True:
            # if owners is dead, only offload if warm_scheduler is True; also if owner is poor or vulnerable, do the offloading
            if not (owner_zone == 4 and warm_scheduler == False):
                # Get rich and vulnerable (if the func is not vulnerable) workers
                volunteers = [*(worker for worker in workers if worker[4] == 1
                                or (worker[4] == 3 and owner_zone != 3))]

                logger.info('greedy: call offloader: volunteers \n'
                            + '\n'.join([str(volunteer) for volunteer in volunteers]))

                new_hosts = offloader(workers, functions, volunteers, new_function, sticky, stickiness,
                                      old_hosts, warm_scheduler, owner, func_max_replica,
                                      func_required_cpu_capacity, scale_to_zero, debug)

        # if not offloading was possible for fonctions owned by poor, vulnerable and dead nodes
        if new_hosts == []:
            # place locally
            logger.info('greedy: ' + owner[0] + '-' + new_function[0][1] + ' ---> locally')
            # how about functions belong to a dead node??? they are still scheduled locally
            for rep in range(func_max_replica):
                new_hosts.append(copy.deepcopy(owner))

        # deduct function cpu requirement from worker's cpu capacity
        for new_host in new_hosts:
            # get selected worker index per replica
            index = workers.index([*(worker for worker in workers if worker[0] == new_host[0])][0])
            # deduct replica cpu requirement
            workers[index][3] -= replica_cpu_reqs
            # update new_host, particulalrly its capacity
            new_host[3] = workers[index][3]

        # set new_function new hosts
        new_function[1] = new_hosts
        if debug: logger.info("scheduler_planner_greedy: new_hosts for ("
                              + new_function[0][0] + "-" + new_function[0][1] + "):\n" + str(new_function[1]))

    # for loop: next new_function

    # replacad original functions with new_functions to apply new_hosts (placements)
    # functions = new_functions
    logger.info('scheduler_planner_greedy: done: functions:\n'
                + '\n'.join([str(new_function) for new_function in new_functions]))

    return workers, new_functions


# ??? functions are received for only getting old_hosts. Only old_hosts can be sent to this planner
def scheduler_planner_binpacking(workers, functions, new_functions, debug):
    global logger
    logger.info("scheduler_planner_binpacking:start")
    logger.info('scheduler_planner_binpacking:\n available Workers \n'
                + '\n'.join([str(worker) for worker in workers]))

    # sort nodes by soc (large->small | descending)
    workers.sort(key=lambda x: x[2], reverse=True)

    logger.info('scheduler_planner_binpacking:sorted nodes by Soc (large->small):\n'
                + str(workers))

    # sort functions: by owner's soc (small -> large | ascending)
    for i in range(len(new_functions)):
        lowest_value_index = i
        for j in range(i + 1, len(new_functions)):
            # find function's owner soc
            soc_j = [*(worker[2] for worker in workers if worker[0] == new_functions[j][0][0])][0]
            soc_lowest_value_index = \
            [*(worker[2] for worker in workers if worker[0] == new_functions[lowest_value_index][0][0])][0]
            # compare socs
            if soc_j < soc_lowest_value_index:
                lowest_value_index = j
        # swap
        new_functions[i], new_functions[lowest_value_index] = new_functions[lowest_value_index], new_functions[i]
    # end sort
    logger.info('scheduler_planner_binpacking:sorted functions by owner\'s soc(small->large):\n'
                + '\n'.join([str(new_function[0]) for new_function in new_functions]))

    # so far, new_functions have [] as hosts, workers have full as capacity and both workers and new_functions are sorted now
    logger.info("scheduler_planner_binpacking: start planning hosts for functions by soc")
    # PLAN
    # set hosts per function
    for new_function in new_functions:

        # function's owner
        owner = [*(worker for worker in workers if worker[0] == new_function[0][0])][0]
        func_required_cpu_capacity = 0
        # exclude 'm'
        replica_cpu_reqs = int(new_function[2][4].split('m')[0])
        func_max_replica = new_function[2][1]
        func_required_cpu_capacity = replica_cpu_reqs * func_max_replica

        logger.info('binpacking: planning for *** ' + str(new_function[0][0]) + '-'
                    + str(new_function[0][1]) + ' *** \n Required_cpu_capacity: '
                    + str(func_required_cpu_capacity))
        # try to fill new hosts for new_function
        new_hosts = []
        # only functions belong to up nodes are scheduled. Those belong to dead nodes schedule locally
        min_battery_charge = battery_cfg[8]
        if owner[2] >= min_battery_charge:
            # pick the first possible option
            for index, worker in enumerate(workers):
                # if node is up
                if worker[2] >= min_battery_charge:
                    # if node has capacity
                    if worker[3] >= func_required_cpu_capacity:
                        for rep in range(func_max_replica):
                            new_hosts.append(copy.deepcopy(worker))
                # if set
                if new_hosts != []:
                    break
            #add#if no node is picked (all other nodes are down), place it locally
            if new_hosts == []:
                logger.info('bin_packing: locally')
                for rep in range(func_max_replica):
                    new_hosts.append(copy.deepcopy(owner))    


        # dead node, schedule locally
        else:
            logger.info('bin_packing: locally')
            for rep in range(func_max_replica):
                new_hosts.append(copy.deepcopy(owner))

        # deduct function cpu requirement from worker's cpu capacity
        for new_host in new_hosts:
            # get selected worker index per replica
            index = workers.index([*(worker for worker in workers if worker[0] == new_host[0])][0])
            # deduct replica cpu requirement
            workers[index][3] -= replica_cpu_reqs
            # update new_host, particulalrly its capacity
            new_host[3] = workers[index][3]
        logger.info('bin_packing: after deduction: new_hosts: ' + str(new_hosts))
        # set new_function new hosts
        new_function[1] = new_hosts
        if debug: logger.info("scheduler_planner_binpacking: new_hosts for ("
                              + new_function[0][0] + "-" + new_function[0][1] + "):\n" + str(new_function[1]))

    # for loop: next new_function

    # replacad original functions with new_functions to apply new_hosts (placements)
    # functions = new_functions
    logger.info('scheduler_planner_binpacking: done: functions:\n'
                + '\n'.join([str(new_function) for new_function in new_functions]))

    return workers, new_functions


# scheduler_planner_local
def scheduler_planner_local(workers, new_functions, debug):
    global logger
    logger.info("scheduler_planner_local:start")
    # set hosts for new_functions and update workers capacity
    logger.info('scheduler_planner_local:\n available Workers \n'
                + '\n'.join([str(worker) for worker in workers]))
    # PLAN
    # set hosts per function
    for new_function in new_functions:
        # function's owner
        owner = [*(worker for worker in workers if worker[0] == new_function[0][0])][0]
        # func required cpu capacity
        func_required_cpu_capacity = 0
        # exclude 'm'
        replica_cpu_reqs = int(new_function[2][4].split('m')[0])
        func_max_replica = new_function[2][1]
        func_required_cpu_capacity = replica_cpu_reqs * func_max_replica

        # try to fill new hosts for new_function
        new_hosts = []

        # place locally
        # how about functions belong to a dead node??? they are still scheduled locally
        for rep in range(func_max_replica):
            new_hosts.append(copy.deepcopy(owner))

        # deduct function cpu requirement from worker's cpu capacity per replica
        for new_host in new_hosts:
            # get selected worker index
            index = workers.index([*(worker for worker in workers if worker[0] == new_host[0])][0])
            # deduct replica cpu requirement
            workers[index][3] -= replica_cpu_reqs
            # apply worker's updated capacity to new_host as well
            new_host[3] = workers[index][3]

        # set new_function new hosts
        new_function[1] = new_hosts
        if debug: logger.info("scheduler_planner_local: new_hosts for ("
                              + new_function[0][0] + "-" + new_function[0][1] + "):\n" + str(new_function[1]))
    # for loop: next new_function

    logger.info('scheduler_planner_local: all done: functions:\n'
                + '\n'.join([str(new_function) for new_function in new_functions]))

    return workers, new_functions


# scheduler_planner_default
# As using nodeSelector (or constraints in Funciton), no selection is made in this algorithm. Kubenretes does it by nodes' performance, only once.
# If a node is under pressure, kubernetes is free to reschedule any time.
def scheduler_planner_default(workers, new_functions, debug):
    global logger
    logger.info("scheduler_planner_default:start")
    # set hosts for new_functions and update workers capacity
    logger.info('scheduler_planner_default:\n available Workers \n'
                + '\n'.join([str(worker) for worker in workers]))
    # PLAN
    # set hosts per function
    for new_function in new_functions:
        # function's owner
        owner = [*(worker for worker in workers if worker[0] == new_function[0][0])][0]
        # func required cpu capacity
        func_required_cpu_capacity = 0
        # exclude 'm'
        replica_cpu_reqs = int(new_function[2][4].split('m')[0])
        func_max_replica = new_function[2][1]
        func_required_cpu_capacity = replica_cpu_reqs * func_max_replica

        # try to fill new hosts for new_function
        new_hosts = []

        # place anywhere you like Kubernetes
        # how about functions belong to a dead node??? they are still scheduled

        for worker in workers:
            new_hosts.append(copy.deepcopy(worker))

        # deduct function cpu requirement from worker's cpu capacity per replica
        for new_host in new_hosts:
            # get selected worker index
            index = workers.index([*(worker for worker in workers if worker[0] == new_host[0])][0])
            # deduct replica cpu requirement
            workers[index][3] -= replica_cpu_reqs
            # apply worker's updated capacity to new_host as well
            new_host[3] = workers[index][3]

            # set new_function new hosts
        new_function[1] = new_hosts
        if debug: logger.info("scheduler_planner_default: new_hosts for ("
                              + new_function[0][0] + "-" + new_function[0][1] + "):\n" + str(new_function[1]))

    # for loop: next new_function

    logger.info('scheduler_planner_default: all done: functions:\n'
                + '\n'.join([str(new_function) for new_function in new_functions]))

    return workers, new_functions


# scheduler_planner_random: 
#bulky places all replicas of a function on a single node

#REMOVED#if function's owner is down, functions placed locally and others functions are not placed in this node
#REMOVED#if all node including itself is down (no candidate), place locally.
#ADDED#always select a random host that has capacity, no matter if it is up or down (requests know if they should be delivered to the func or not in create_sensor)
def scheduler_planner_random(workers, new_functions, debug):
    global logger
    logger.info("scheduler_planner_random:start")
    # set hosts for new_functions and update workers capacity
    logger.info('scheduler_planner_random:\n available Workers \n'
                + '\n'.join([str(worker) for worker in workers]))
    # PLAN
    # set hosts per function
    for new_function in new_functions:
        # function's owner, e.g., ['homo1', '10.0.0.80', 1250, 3600, 1]
        owner = [*(worker for worker in workers if worker[0] == new_function[0][0])][0]
        print(f'funcrion={new_function[0][0]}')
        print(f'workers={workers}')

        # func required cpu capacity
        func_required_cpu_capacity = 0
        # exclude 'm'
        replica_cpu_reqs = int(new_function[2][4].split('m')[0])
        func_max_replica = new_function[2][1]
        #required CPU given all possible replicas in bulk, not per replica!
        func_required_cpu_capacity = replica_cpu_reqs * func_max_replica

        
        # try to fill new hosts for new_function
        new_hosts = []

        #add# check all nodes are down?
        #REMOVE#
        # all_are_down = True if len([workers.index(worker) for worker in workers if worker[2] >= setup.min_battery_charge]) == 0 else False
        #add# if all nodes are down, place it locally
        # if all_are_down:
        #     logger.info('all_are_down: all node are down,so place function locally')
        #     #for all replicas
        #     for rep in range(func_max_replica):
        #         new_hosts.append(copy.deepcopy(owner))
        #REMOVED#

        #if owner is down (battery soc < min_battery_charge), place its function on itself. ??? Assumed all batteries are the same size
        #REMOVE#
        # elif owner[2] < setup.min_battery_charge:
            #for all replicas
            # for rep in range(func_max_replica):
            #     new_hosts.append(copy.deepcopy(owner))
        #REMOCED#
        #select hosts randomly
        if False:
            pass
        else:
            # place on a random node that has capacity
            # how about functions belong to a dead node??? they are still scheduled
            random_places = []
            while random_places == []:
                
                #exclude dead nodes by id
                excluded_list_indexes = []
                #REMOVE#
                # excluded_list_indexes = [workers.index(worker) for worker in workers if worker[2] < setup.min_battery_charge]
                #REMOVED#

                #pick a node id
                random_index = choice([i for i in range(0, len(workers) ) if i not in excluded_list_indexes])
                # random_index = random.randint(0, len(workers))  # 0 to 5
                
                # has enough capacity for all function replicas?
                if workers[random_index][3] >= func_required_cpu_capacity:
                    # set place
                    for rep in range(func_max_replica):
                        random_places.append(copy.deepcopy(workers[random_index]))
                else:
                    print(f'##########worker={workers[random_index][3]} no capacity for func_required_cpu_capacity={func_required_cpu_capacity}')
            new_hosts = random_places


        # deduct function cpu requirement from worker's cpu capacity per replica
        for new_host in new_hosts:
            # get selected worker index
            index = workers.index([*(worker for worker in workers if worker[0] == new_host[0])][0])
            # deduct replica cpu requirement
            workers[index][3] -= replica_cpu_reqs
            # apply worker's updated capacity to new_host as well
            new_host[3] = workers[index][3]

        # set new_function new hosts
        new_function[1] = new_hosts
        if debug: logger.info("scheduler_planner_random: new_hosts for ("
                              + new_function[0][0] + "-" + new_function[0][1] + "):\n" + str(new_function[1]) + '\n')
    # for loop: next new_function

    logger.info('scheduler_planner_random: all done: functions:\n'
                + '\n'.join([str(new_function) for new_function in new_functions]))

    return workers, new_functions


# scheduler_monitor
def scheduler_monitor(workers, node_role):
    global logger
    logger.info("scheduler_monitor: start")
    # MONITOR
    template = {'charge': -1}

    # Update SoC
    for worker in workers:
        ip = worker[1]
        success = False
        # retry
        while success == False:
            try:
                logger.info('scheduler_monitor: Soc req.: ' + worker[0])
                response = internal_session.get('http://' + ip + ':5000/main_handler/pull/'
                                        + node_role, timeout=10, json=template)
                # response.close()

            except Exception as e:
                logger.error('scheduler_monitor:request failed for ' + worker[0] + ":" + str(e))
                time.sleep(1)
            else:
                # logger.info(str(response.json()))

                if response.json() and 'charge' in response.json():
                    soc = response.json()['charge']
                    index = workers.index(worker)
                    workers[index][2] = soc
                    logger.info('scheduler_monitor: Soc recv.: ' + worker[0] + ":" + str(soc) + " mWh")
                    success = True
                else:
                    logger.error('scheduler_monitor: failed to receive requested values')

    logger.info('scheduler_monitor:\n' + '\n'.join([str(worker) for worker in workers]))
    logger.info("scheduler_monitor: done")

    return workers


# set initial workers and functions
def initialize_workers_and_functions(nodes, workers, functions, battery_cfg, nodes_plan, zones):
    global logger
    logger.info("initialize_workers_and_functions: start")
    # Set Workers & Functions
    for node in nodes:
        # worker = [name, ip, soc, capacity, zone]
        position = node[0]
        name = node[1]
        ip = node[2]
        soc = battery_cfg[3]  # set current SoC
        capacity = copy.deepcopy(nodes_plan[name]["max_cpu_capacity"])  # set capacity as full
        # set zone
        max_battery_charge = battery_cfg[1]
        soc_percent = min(100, round(soc / max_battery_charge * 100))
        zone = [*(zone[1] for zone in zones if soc_percent <= zone[2] and soc_percent > zone[3])][0]
        # if node is involved in this tests
        if position == "PEER":
            # add worker
            worker = [name, ip, soc, capacity, zone]
            workers.append(worker)

            # add functions
            apps = copy.deepcopy(nodes_plan[name]["apps"])
            for app in apps:
                if app[1] == True:
                    # function = [identity, hosts[], func_info, profile]
                    # set identity
                    worker_name = worker[0]
                    app_name = app[0]
                    identity = [worker_name, app_name]
                    # set hosts
                    hosts = []
                    # set function info
                    func_info = app[8]
                    # create and set profile name in function info
                    func_info[15] = worker_name + '-' + app_name
                    # set profile
                    profile = app[9]

                    function = []

                    # set local host per replicas and deduct cpu capacity from node
                    max_replica = func_info[1]
                    for rep in range(max_replica):
                        # update host capacity
                        replica_cpu_reqs = func_info[4]
                        # exclude 'm'
                        replica_cpu_reqs = int(replica_cpu_reqs.split('m')[0])
                        index = workers.index(worker)
                        workers[index][3] -= replica_cpu_reqs

                        # set host: default is local placement
                        hosts.append(worker)
                    # end for rep

                    # add function
                    function = [identity, hosts, func_info, profile]
                    functions.append(function)
                    f_name = function[0][0] + '-' + function[0][1]
            # end for app
    # end for node
    logger.info("initialize_workers_and_functions:stop")
    return workers, functions


# executor :set functions' profile using hosts, apply helm charts
def scheduler_executor(functions, profile_chart, profile_creation_roll_out,
                       function_chart, scheduling_round, log_path, scheduler_name, workers, debug):
    # 1 set profile based on hosts= set function[3] by new updates on function[1]
    logger.info('scheduler_executor:start')
    logger.info("scheduler_executor:set_profile per function")
    duration = datetime.datetime.now(datetime.timezone.utc).astimezone().timestamp()
    for function in functions:
        # if debug: logger.info('scheduler_executor: set_profile:before:\n' + str(function[3]))
        # get old profile
        old_profile = copy.deepcopy(function[3])

        # translate hosts and map them to profile and set new profile scheme
        #profile  ={"api_version": api_version, "kind": kind, "namespace": namespace, "operation": operation, "manifest": manifest}
        function[3] = scheduler_executor_set_profile(function, scheduler_name, workers, debug)
        # compare profiles, profile = function[3] looks like this ["w1", "nothing", "nothing",....]
        if old_profile != function[3]:
            logger.info(f'OLD%%%%%%%%%%%%%%={old_profile}\n%%%%%%%%%%%new={function[3]}')
            # if profile is changed, set version to force re-schedule function based on new profile config
            function[2][16] += 1
            logger.info('scheduler_executor: ' + str(function[0][0]) + '-' + str(function[0][1])
                        + ': version = ' + str(function[2][16]))

        # if debug: logger.info('scheduler_executor: set_profile:after:\n' + str(function[3]))
    # all new profiles
    logger.info('scheduler_executor: All new profiles \n'
                + '\n'.join([str(str(function[0]) + '--->'
                                 + str(function[3])) for function in functions]))
    # 2 apply the new scheduling for functions by helm chart

    #Note: if first scheduling round <= 1, first delete the function left from previous experiment to avoid mismatching config like replicas.
    
    if scheduling_round <=1:
        logger.info('delete functions left from previous experiments.')
        for function in functions:
            func_name = str(function[0][0]) + '-' + str(function[0][1])
            #kubectl apply (delete)
            func_args = {'api_version': 'openfaas.com/v1',
                        'kind': 'Function',
                        'object_name': func_name,
                        'namespace': 'openfaas-fn',
                        'operation': 'safe-delete'}
            logger.info('delete_function start for ' + func_name + '\n' + str(func_args))

            pykubectl.apply(**func_args)
            
            logger.info('delete_function done for ' + func_name + ' \n' + str(func_args))

        logger.info('wait for 10 sec so deletion is affected by openfaas...')
        time.sleep(10)

    # if no change in profile happend, no re-scheduling is affected
    logger.info("scheduler_executor:APPLYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYY")

    scheduler_executor_apply(functions, profile_chart, profile_creation_roll_out,
                             function_chart, scheduling_round, log_path,
                             setup.auto_scaling, setup.auto_scaling_factor)

    duration = datetime.datetime.now(datetime.timezone.utc).astimezone().timestamp() - duration
    logger.info('scheduler_executor: done in ' + str(int(duration)) + 'sec')

    #3 customize Deployment of functions in kubernetes
    #only if it is the first round of scheduling or the function has been redeployed (it is redeployed, if the profile object is changed. Verifiable by comparing the version value in the function)
    
    logger.info("scheduler_executor: patch functions for customizations after 10 sec")
    time.sleep(10)
    # sys.exit()
    for function in functions:
        #if first scheduling
        if scheduling_round <= 1:
            #patch it
            function_name = copy.deepcopy(function[0][0] + '-' + function[0][1])
            function_worker_name = copy.deepcopy(function[0][0])
            logger.info('patch functions ' + function_name + ' for customizations.')
            #patch affinity if algorithm is Default kubernetes
            if 'default' in setup.scheduler_name[epoch if 'scheduler_name' in setup.variable_parameters else 0]:
                affinity = copy.deepcopy(function[3]['manifest']['spec']['affinity'])
            else:
                affinity = {}
            logger.info(f'%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%{affinity}')
            res, msg, err = utils.openfaas_function_customizations(logger, function_name, function_worker_name, setup.accelerators, setup.replacement_strategy, affinity, setup.model_inference_repeat)
            if err:
                logger.error('openfaas_function_customizations failed:' 
                + '\nmsg: ' + msg
                + '\nerror: ' + err)
            else:
                logger.info('patch done')

        #if function redeployed
        else:
            #get previous version value of this function
            previous_round_functions = history["functions"][-1]
            # previous_round_functions = history["functions"][scheduling_round - 1]???
            for old_function in previous_round_functions:
                if old_function[0][0] == function[0][0] and old_function[0][1] == function[0][1]:
                    old_version = old_function[2][16]
                    version = function[2][16]
            #if version has changed
            if old_version != version:
                #patch it
                logger.info('patch functions for customizations.')
                function_name = function[0][0] + '-' + function[0][1]
                function_worker_name = function[0][0]

                #patch affinity if algorithm is Default kubernetes
                if 'default' in setup.scheduler_name[epoch if 'scheduler_name' in setup.variable_parameters else 0]:
                    affinity = copy.deepcopy(function[3]['manifest']['spec']['affinity'])
                else:
                    affinity = {}
                logger.info(f'%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%{affinity}')   
                logger.info('patch functions ' + function_name + ' for customizations.')
                
                res, msg, err = utils.openfaas_function_customizations(logger, function_name, function_worker_name, setup.accelerators, setup.replacement_strategy, affinity, setup.model_inference_repeat)
                if err:
                    logger.error('openfaas_function_customizations failed:' 
                    + '\nmsg: ' + msg
                    + '\nerror: ' + err)
                else:
                    logger.info('patch done')



    return functions


# offload
def offloader(workers, functions, volunteers, new_function, sticky, stickiness, old_hosts,
              warm_scheduler, owner, func_max_replica, func_required_cpu_capacity, scale_to_zero, debug):
    global logger
    logger.info("offloader: start: " + str(new_function[0][0] + '-' + new_function[0][1]))
    new_hosts = []
    # ??? assume that all replicas are always placed on 1 node
    # if sticky enabled and function was offloaded last time
    if owner[0] != old_hosts[0][0] and sticky:
        new_hosts = sticky_offloader(workers, functions, volunteers, stickiness, old_hosts,
                                     owner, func_max_replica, func_required_cpu_capacity,
                                     warm_scheduler, scale_to_zero)
    else:
        logger.info('offloader: skip sticky_offloader')
    # if sticky unsuccessful
    if new_hosts == []:
        # iterate over rich and vulnerables, already sorted by SoC (large -> small)
        for volunteer in volunteers:
            # if function belongs to a poor node
            if owner[4] == 2:
                if debug: logger.info('offloader: poor function')
                # if node is in rich zone
                volunteer_zone = volunteer[4]
                if volunteer_zone == 1:
                    if debug: logger.info('offloader: rich volunteer (' + volunteer[0] + ')')
                    # if enough capacity on volunteer node is available
                    if volunteer[3] >= func_required_cpu_capacity:
                        if debug: logger.info('offloader: rich volunteer has capacity')
                        # place this poor function on this rich volunteer per replica
                        for rep in range(func_max_replica):
                            new_hosts.append(copy.deepcopy(volunteer))
                            # volunteer capacity is deducted later on in main algorithm
                        return new_hosts
                    else:
                        if debug: logger.info('offloader: rich volunteer has NOT capacity')
                # OR volunteer node is in vulnerable zone
                if volunteer_zone == 3:
                    if debug: logger.info('offloader: vulnerable volunteer (' + volunteer[0] + ')')
                    # evaluate cpu reservation for the vulnerable node own functions
                    reserved_capacity = 0
                    available_capacity = 0
                    for function in functions:
                        # if function belongs to this vulnerable volunteer node
                        if function[0][0] == volunteer[0]:
                            # caclulate reserved cpu capacity per replica for the function
                            reserved_capacity += function[2][1] * int(function[2][4].split('m')[0])
                    # if already one has offloaded on this, that one is also included here as volunteer[3] is the result of full capacity minus offloaded (end of each offloading this is deducted)
                    available_capacity = volunteer[3] - reserved_capacity

                    # if volunteer has enough cpu capacity, considering reservation
                    if available_capacity >= func_required_cpu_capacity:
                        if debug: logger.info('offloader: vulnerable volunteer has capacity + reservation')
                        # place functions belong to a poor node on volunteer per replica
                        for rep in range(func_max_replica):
                            new_hosts.append(copy.deepcopy(volunteer))
                        return new_hosts
                    else:
                        if debug: logger.info('offloader: vulnerable volunteer has NOT capacity + reservation')
            # if function belongs to a vulnerable zone
            elif owner[4] == 3:
                if debug: logger.info('offloader: vulnerable function')
                # only if volunteer is in rich zone
                if volunteer[4] == 1:
                    if debug: logger.info('offloader: volunteer node\'s zone is rich (' + volunteer[0] + ')')
                    # and volunteer has cpu capacity for function
                    if volunteer[3] >= func_required_cpu_capacity:
                        logger.info('offloader: volunteer rich has capacity')
                        for rep in range(func_max_replica):
                            new_hosts.append(copy.deepcopy(volunteer))
                        return new_hosts
                    else:
                        if debug: logger.info('offloader: volunteer rich has NOT capacity')
                else:
                    if debug: logger.info('offloader: volunteer node\'s zone is NOT rich')
            # if function belongs to a dead node
            elif owner[4] == 4:
                if debug: logger.info('offloader: dead function')
                # if warm_scheduler on, otherwise functions belong to dead nodes are just placed locally
                if warm_scheduler == True:
                    if debug: logger.info('offloader: warm scheduler is True')
                    # if volunteer is in rich zone
                    if volunteer[4] == 1:
                        if debug: logger.info('offloader: rich volunteer (' + volunteer[0] + ')')
                        # if volunteer has cpu capacity
                        if volunteer[3] >= func_required_cpu_capacity:
                            if debug: logger.info('offloader: rich volunteer has capacity')
                            for rep in range(func_max_replica):
                                new_hosts.append(copy.deepcopy(volunteer))
                            return new_hosts
                        else:
                            if debug: logger.info('offloader: rich volunteer has NOT capacity')
                    else:
                        if debug: logger.info('offloader: volunteer is NOT rich (' + volunteer[0] + ')')

                    # or not exist any rich and all volunteers are just vulnerable
                    rich_nodes = [*(worker for worker in workers if worker[4] == 1)]
                    if len(rich_nodes) == 0:
                        if debug: logger.info('offloader: not exist any rich node and all volunteers are vulnerable')
                        # if volunteer has cpu capacity
                        if volunteer[3] >= func_required_cpu_capacity:
                            if debug: logger.info('offloader: vulnerable volunteer has capacity')
                            for rep in range(func_max_replica):
                                new_hosts.append(copy.deepcopy(volunteer))
                            return new_hosts
                        # if no cpu capacity, if scale to zero on, do it ????
                        elif setup.scale_to_zero == True:
                            pass
                        else:
                            if debug: logger.info('offloader: vulnerable volunteer has NOT capacity')
                    else:
                        if debug: logger.info('offloader: unlukily, exist rich volunteer')
                else:
                    if debug: logger.info('offloader: warm scheduler is False')
        # end for volunteer
        if len(volunteers) == 0:
            logger.info('offloader: skip offloading, no volunteer found')

    logger.info("offloader: done: " + str(new_function[0][0] + '-' + new_function[0][1])
                + ": new_hosts:\n" + str(new_hosts) if new_hosts != [] else ": [ ]")
    return new_hosts


# sticky offloader
def sticky_offloader(workers, functions, volunteers, stickiness, old_hosts, owner,
                     func_max_replica, func_required_cpu_capacity, warm_scheduler, scale_to_zero):
    global logger
    logger.info('sticky_offloader: start')
    new_hosts = []
    logger.info('sticky_offloader: old_hosts: ' + str(old_hosts))
    # apply sticky only if all replicas of the functions have been scheduled on only 1 zone???? how about per replica evaluation and letting each replica sticks to its last place
    old_hosts_zone = [host[4] for host in old_hosts]
    old_hosts_zone_set = list(set(old_hosts_zone))
    if len(old_hosts_zone_set) > 1:
        logger.error('sticky_offloader: all replicas are NOT on 1 node')
        logger.info('sticky_offloader: done' + str(new_hosts))
        return new_hosts

    logger.info('sticky_offloader: get best option')
    # Get best option for offloading, regardless of sticky
    # nodes (rich and vulnerable) already sorted by suitability
    best_option = []
    for volunteer in volunteers:
        # if function belongs to a poor node, and volunteer node is in vulnerable zone,
        # then because of undecided functions belonging to the node, consider node's own reservation
        available_capacity = 0
        if owner[4] == 2 and volunteer[4] == 3:
            # consider reservation to evaluate volunteer capacity
            # evaluate cpu reservation for the vulnerable node own functions
            reserved_capacity = 0

            for function in functions:
                # if function belongs to the volunteer node that is a vulnerable node
                if function[0][0] == volunteer[0]:
                    # caclulate reserved cpu capacity per replica for the function
                    reserved_capacity += function[2][1] * int(function[2][4].split('m')[0])
            # Note:if already one has offloaded on this, that one is also included here as volunteer[3] is the result of full capacity minus offloaded (end of each offloading this is deducted)
            available_capacity = volunteer[3] - reserved_capacity
        else:
            available_capacity = volunteer[3]
        # if node has capacity
        if available_capacity >= func_required_cpu_capacity:
            best_option = volunteer
            # the first answer, is the best option, do not continue
            break
    # end for
    logger.info('sticky_offloader: best option: ' + str(best_option))

    if best_option == []:
        logger.error('sticky_offloader: not a best option found, return null to offloader')
        logger.info('sticky_offloader: done' + str(new_hosts))
        return new_hosts

    # if old location of function (belonging to poor, vulnerable or (dead if warm is true)) is rich
    if old_hosts_zone[0] == 1:
        logger.info('sticky_offloader: old_host is rich')
        # if old node soc satisfies stickiness
        old_option_soc = old_hosts[0][2]
        best_option_soc = best_option[2]
        if old_option_soc >= (best_option_soc - (best_option_soc * stickiness)):
            logger.info('sticky_offloader: old_host_soc satisfy stickiness')
            # if old has capacity
            if old_hosts[0][3] >= func_required_cpu_capacity:
                logger.info('sticky_offloader: old_host has capacity')
                new_hosts = copy.deepcopy(old_hosts)
                # function requried cpu is later deducted from the node capacity in main algorithm
                logger.info('sticky_offloader: done' + str(new_hosts))
                return new_hosts
            # old has no capacity, but if f belongs to a dead node, place and scale to 0 even if no resource
            elif owner[4] == 4:
                # if scale to zero on ???
                if scale_to_zero == True:
                    logger.info('sticky_offloader: old_host NOT capacity, but func is dead and scale_to_zero is on')
                    # ??? it can be limited to only 1 zero function per node: if not exist any 0 already on this node
                    new_hosts = copy.deepcopy(old_hosts)
                    logger.info('sticky_offloader: done' + str(new_hosts))
                    return new_hosts
            else:
                logger.info('sticky_offloader: old_hosts has NOT capacity (or NOT a dead func + scale_to_zero=True)\n'
                            + 'func capacity = ' + str(func_required_cpu_capacity)
                            + ' old_host capacity= ' + str(old_hosts[0][3]))
        else:
            logger.info('sticky_offloader: old_host_soc NOT satisfy stickiness')
    # if old host is vulnerable and function belongs to a poor or dead node
    elif old_hosts_zone[0] == 3 and (owner[4] == 2 or owner[4] == 4):
        logger.info('sticky_offloader: old_host is vulnerable and func belongs to poor or dead node')
        # evaluate cpu reservation for the vulnerable node functions itself
        reserved_capacity = 0
        available_capacity = 0
        for function in functions:
            # if node name in function is equal to the old_host name, it is its local func
            if function[0][0] == old_hosts[0][0]:
                # caclulate reserved cpu capacity per replica for the function
                reserved_capacity += function[2][1] * int(function[2][4].split('m')[0])

        available_capacity = old_hosts[0][3] - reserved_capacity

        # if f belongs to a poor node and (no rich node exists || all are filled)
        # skip this part: and (best_option[4] != 1)
        if owner[4] == 2:
            logger.info('sticky_offloader: func belong to poor skipped(and (no rich or all riches are filled)')
            # if old host can satisfy stickiness, stick it
            # check stickiness
            old_option_soc = old_hosts[0][2]
            best_option_soc = best_option[2]
            if old_option_soc >= (best_option_soc - (best_option_soc * stickiness)):
                logger.info('sticky_offloader: satisfy stickiness')
                # if old has capacity
                if available_capacity >= func_required_cpu_capacity:
                    logger.info('sticky_offloader: has capacity')
                    new_hosts = copy.deepcopy(old_hosts)
                    logger.info('sticky_offloader: done' + str(new_hosts))
                    return new_hosts
                else:
                    logger.info('sticky_offloader: has NOT capacity')
            else:
                logger.info('sticky_offloader: NOT satisfy stickiness')
        # OR if f belongs to a dead node & warm & no rich node exists
        elif (owner[4] == 4 and warm_scheduler == True and
              (len([*(worker for worker in workers if worker[4] == 1)]) == 0)):
            logger.info('sticky_offloader: func belong to dead node and no rich node exist')
            # if enough capacity
            if available_capacity >= func_required_cpu_capacity:
                logger.info('sticky_offloader: has capacity')
                new_hosts = copy.deepcopy(old_hosts)
                logger.info('sticky_offloader: done' + str(new_hosts))
                return new_hosts
            else:
                logger.info('sticky_offloader: has NOT capacity')
            # if does not exist a dead already placed somewhere with scale to zero ???
            # else:
        else:
            logger.info('sticky: not happened: not being: \n'
                        + 'f belongs to a poor node and (no rich node exists || all are filled)\n'
                        + ' OR f belongs to a dead node & no rich node exists')
    logger.info('sticky_offloader: done' + str(new_hosts))

    return new_hosts


# set ptofile
# it only works for 5 nodes and 3 replica???
def scheduler_executor_set_profile(function, scheduler_name, workers, debug):
    global logger
    try:
        
        owner_name = function[0][0]
        app_name = function[0][1]
        func_name = owner_name + '-' + app_name
        logger.info(f'scheduler_executor_set_profile for {func_name} start ...')

        hosts = function[1]
        
        selected_nodes = []
        for host in hosts:
            selected_nodes.append(host[0])
        # if selected_nodes=[w1,w2,w2] then selected_nodes_set result is [w1, w2]
        selected_nodes_set = list(set(selected_nodes))

        #sort the list, so if there is a change only in the order of hosts, it will not be resulting in a redeployment.

        import re
        # Define a regular expression to match the number in each item
        number_regex = re.compile(r'\d+')

        # Define a function to extract the number from each item
        def extract_number(s):
            match = number_regex.search(s)
            if match:
                return int(match.group())
            else:
                return float('inf')

        # Sort the list based on the number in each item
        selected_nodes_set.sort(key=extract_number)


        #set host names as node affinity required
        nodeAffinity_required_filters = selected_nodes_set
        nodeAffinity_preferred_sort=[] 
        podAntiAffinity_preferred_functionName=[]
        podAntiAffinity_required_functionName=[]
        #create profile descripton in json
        api_version, kind, namespace, operation, manifest = pykubectl.create_openfaas_profile(logger, func_name, nodeAffinity_required_filters, nodeAffinity_preferred_sort, podAntiAffinity_preferred_functionName, podAntiAffinity_required_functionName)
        
        profile_description = {"object_name": func_name, "api_version": api_version, "kind": kind, "namespace": namespace, "operation": operation, "manifest": manifest}
        
        logger.info(f'scheduler_executor_set_profile for {func_name} done profile_description={profile_description}')

        return profile_description
    
    except Exception as e:
        logger.exception(str(e))

        # profile = {
        #     "api_version": 
        #     }
        # nodeAffinity_required_filter1 = "unknown"
        # nodeAffinity_required_filter2 = "unknown"
        # nodeAffinity_required_filter3 = "unknown"
        # nodeAffinity_required_filter4 = "unknown"
        # nodeAffinity_required_filter5 = "unknown"
        # nodeAffinity_required_filter6 = "unknown"
        # nodeAffinity_required_filter7 = "unknown"
        # nodeAffinity_required_filter8 = "unknown"
        # nodeAffinity_required_filter9 = "unknown"
        # nodeAffinity_required_filter10 = "unknown"
        # nodeAffinity_preferred_sort1 = "unknown"
        # podAntiAffinity_preferred_functionName = "unknown"
        # podAntiAffinity_required_functionName = "unknown"

        # owner_name = function[0][0]
        # app_name = function[0][1]
        # function_name = owner_name + '-' + app_name
        # hosts = function[1]
        # # if debug: logger.info("scheduler_executor_set_profile:" + function_name + ":start")
        # selected_nodes = []
        # for host in hosts:
        #     selected_nodes.append(host[0])
        # # if selected_nodes=[w1,w2,w2] then selected_nodes_set result is [w1, w2]
        # selected_nodes_set = list(set(selected_nodes))

        # if ("greedy" in scheduler_name or
        #         "shortfaas" in scheduler_name or
        #         "local" in scheduler_name or
        #         "random" in scheduler_name or
        #         "bin-packing" in scheduler_name):

        #     # place on 1 node #random is always 1
        #     if len(selected_nodes_set) == 1:
        #         # nodeAffinity_required_filter1 = 'w4'
        #         nodeAffinity_required_filter1 = selected_nodes_set[0]
        #     # place on 2 nodes
        #     elif len(selected_nodes_set) == 2:
        #         nodeAffinity_required_filter1 = selected_nodes_set[0]
        #         nodeAffinity_required_filter2 = selected_nodes_set[1]
        #         preference = ""
        #         if selected_nodes.count(selected_nodes_set[0]) == 2:
        #             preference = selected_nodes_set[0]
        #         else:
        #             preference = selected_nodes_set[1]

        #         nodeAffinity_preferred_sort1 = preference
        #         podAntiAffinity_preferred_functionName = function_name
        #     # place on 3 nodes
        #     elif len(selected_nodes_set) == 3:
        #         nodeAffinity_required_filter1 = selected_nodes_set[0]
        #         nodeAffinity_required_filter2 = selected_nodes_set[1]
        #         nodeAffinity_required_filter3 = selected_nodes_set[2]
        #         podAntiAffinity_required_functionName = function_name
        #     else:
        #         logger.error('scheduler_set_profile:' + function_name + ': selected_nodes_set length = '
        #                      + str(len(selected_nodes_set)))
        # # default-kubernetes scheduler
        # elif "default" in scheduler_name:
        #     if len(selected_nodes_set) == len(workers):
        #         if len(selected_nodes_set) == 4:  # t????emporary code, both if else should be merged
        #             nodeAffinity_required_filter1 = selected_nodes_set[0]
        #             nodeAffinity_required_filter2 = selected_nodes_set[1]
        #             nodeAffinity_required_filter3 = selected_nodes_set[2]
        #             nodeAffinity_required_filter4 = selected_nodes_set[3]

        #         elif len(selected_nodes_set) == 5:  # ????temporary code
        #             nodeAffinity_required_filter1 = selected_nodes_set[0]
        #             nodeAffinity_required_filter2 = selected_nodes_set[1]
        #             nodeAffinity_required_filter3 = selected_nodes_set[2]
        #             nodeAffinity_required_filter4 = selected_nodes_set[3]
        #             nodeAffinity_required_filter5 = selected_nodes_set[4]
        #         elif len(selected_nodes_set) == 10:  # ????temporary code
        #             nodeAffinity_required_filter1 = selected_nodes_set[0]
        #             nodeAffinity_required_filter2 = selected_nodes_set[1]
        #             nodeAffinity_required_filter3 = selected_nodes_set[2]
        #             nodeAffinity_required_filter4 = selected_nodes_set[3]
        #             nodeAffinity_required_filter5 = selected_nodes_set[4]
        #             nodeAffinity_required_filter6 = selected_nodes_set[5]
        #             nodeAffinity_required_filter7 = selected_nodes_set[6]
        #             nodeAffinity_required_filter8 = selected_nodes_set[7]
        #             nodeAffinity_required_filter9 = selected_nodes_set[8]
        #             nodeAffinity_required_filter10 = selected_nodes_set[9]
        #     else:
        #         logger.error('scheduler_set_profile: not all workers are selected: (len=='
        #                      + str(len(selected_nodes_set)) + ')')
        # else:
        #     logger.error('scheduler_set_profile: scheduler_name not found:' + scheduler_name)

        # # if debug: logger.info("scheduler_executor_set_profile:" + function_name + ":done")
        # return
        # return [nodeAffinity_required_filter1,
        #         nodeAffinity_required_filter2,
        #         nodeAffinity_required_filter3,
        #         nodeAffinity_required_filter4,
        #         nodeAffinity_required_filter5,
        #         nodeAffinity_required_filter6,
        #         nodeAffinity_required_filter7,
        #         nodeAffinity_required_filter8,
        #         nodeAffinity_required_filter9,
        #         nodeAffinity_required_filter10,
        #         nodeAffinity_preferred_sort1,
        #         podAntiAffinity_preferred_functionName,
        #         podAntiAffinity_required_functionName]


last_version = [0]


# scheduler_executor_apply
def scheduler_executor_apply(functions, profile_chart, profile_creation_roll_out,
                             function_chart, scheduling_round, log_path,
                             auto_scaling, auto_scaling_factor):
    global logger
    global last_version
    logger.info('scheduler_executor_apply:start')
    # logger.info('scheduler_executor_apply:profiles:start')
    # try:
    #     for function in functions:
    #         profile = function[3]
    #         logger.info(f'scheduler_executor_apply start profile={profile}')
    #         #apply
    #         output, msg, err = pykubectl.apply(**profile)

    #         logger.info(output, msg)
    #         if err:
    #             logger.error(err)
    # except Exception as e:
    #     logger.exception(f"scheduler_executor_apply: {str(e)}")





    # wait to apply
    # logger.info('scheduler_executor_apply:cmd:profile:rolling out (' + str(profile_creation_roll_out) + 's)')
    # time.sleep(profile_creation_roll_out)
    # logger.info('scheduler_executor_apply:profiles:done')

    # Functions Helm CHart
    # Get Functions String
    logger.info('scheduler_executor_apply:functions:start')
    for function in functions:
        func_config = {}
        func_config["name"] = function[0][0] + "-" + function[0][1]
        
        # info
        func_info = function[2]
    
        func_config["annotations"] = {
            "linkerd.io/inject": func_info[13],
            "com.openfaas.queue": func_info[14],
            "com.openfaas.profile": func_info[15],
            }
        
        func_config["labels"] = {
            "com.openfaas.scale.min": "1" if auto_scaling == "hpa" else str(func_info[0]),
            "com.openfaas.scale.max": "1" if auto_scaling == "hpa" else str(func_info[1]),
            "com.openfaas.scale.factor": "0" if auto_scaling == "hpa" else str(auto_scaling_factor),
            }
        func_config["limits"] = {
                "cpu": func_info[5],
                "memory": func_info[3],
            }
        func_config["requests"] = {
                "cpu": func_info[4],
                "memory": func_info[2],
            }
        func_config["environment"]= {
            "COUNTER": func_info[6],
            "REDIS_SERVER_IP": func_info[7],
            "REDIS_SERVER_PORT": func_info[8],
            "exec_timeout": func_info[11],
            "handler_wait_duration": func_info[12],
            "read_timeout": func_info[9],
            "version": str(func_info[16]),
            "write_debug": "true",
            "write_timeout": func_info[10],}
    
        #???if image name is especifically defined in setup.apps_image for this function name, get that; otherwise, do the usual.
        if name in setup.apps_image:
            func_config["image"] = setup.apps_image[name]
        else:
            func_config["image"] = func_info[17]
        
        #if default kubernetes scheduling, this is moved to Deployment affinity, so it takes effect in affinity of Deployment, as default alg needs to allow all nodes be placed, but constraints only gets one node to host a function that works for other algorihtms.
        #If only one item in constraints, it is okay (which applies to all algs except default).
        func_config["constraints"] =  copy.deepcopy(function[3]['manifest']['spec']['affinity']['nodeAffinity']['requiredDuringSchedulingIgnoredDuringExecution']['nodeSelectorTerms'][0]['matchExpressions'][0]['values'])
        
        #Default algorithm (Deployment affinity handles the scheduling)
        if len(func_config["constraints"]) > 1:
            func_config["constraints"] = []
            logger.info('scheduling handled by Deployment affinity instead of Function constraints!')
        
        #others (Function constraints handle the scheduling)
        else:
            #fix key value for constraints (input is only node name)
            if func_config["constraints"]:
                for i in range(len(func_config["constraints"])):
                    func_config["constraints"][i] = "kubernetes.io/hostname=" + func_config["constraints"][i]

        # if function[3]['manifest']['spec']['affinity']:
        #     func_config["constraints"] = function[3]['manifest']['spec']['affinity']['nodeAffinity']['requiredDuringSchedulingIgnoredDuringExecution']['nodeSelectorTerms'][0]['matchExpressions'][0]['values']
        # else:
        #     func_config["constraints"] = []


        
        #prepare kubectl apply: manifest + command
        logger.info(f"scheduler_executor_apply call pykubectl.create_openfaas_function_manifest_for_patch for func_config={func_config} ")
        #create or patch Function
        output, msg, err = pykubectl.create_openfaas_function_manifest_for_patch(**func_config)
        if not err:
            logger.info(f"scheduler_executor_apply call pykubectl.create_openfaas_function_manifest_for_patch done output={output}, msg={msg}")
        else:
            logger.error(f"scheduler_executor_apply call pykubectl.create_openfaas_function_manifest_for_patch FAILED output={output}, msg={msg}, \nerror={err}")

        #apply
        logger.info(f"scheduler_executor_apply: call pykubectl.apply for {func_config['name']}\ninput={output}")

        result, msg, err = pykubectl.apply(**output)
        if not err:
            logger.info(f"scheduler_executor_apply pykubectl.apply done for {func_config['name']}\nresult={result}, \nmsg={msg}")
        else:
            logger.error(f"scheduler_executor_apply pykubectl.apply FAILED for {func_config['name']}\nresult={result}, \nmsg={msg},\nerror={err}")


    logger.info('scheduler_executor_apply:functions:done')

    logger.info('scheduler_executor_apply:stop')



#cluster_info_populator
def cluster_info_populator():
    #if enabled, every x sec get nodes and functs status and populate info to all nodes. Nodes keep info in cluster_info variable
    global under_test

    while under_test:
        #cluster info for nodes and functions. cluster_info['nodes']={'homo1':1...}  cluster_info['functions'] = {'homo1-ssd': ['homo3']}
        cluster_info = {'nodes':{}, 'functions': {}}

        #A:  get all nodes status (up/down)
        #fill cluster_info['nodes']=?

        for node in setup.nodes:
            #if node is in test included
            # ["PEER", "homo1","10.0.0.80", "ubuntu"],
            if node[0] == 'PEER':
                ip = node[2]
                node_name = node[1]
                #0 failed, 1 pending , 2 running, -1 unavaible, -2 test not started yet
                node_status = pull_node_status(ip, node_name)

                #update node_status
                cluster_info['nodes'][node_name] = node_status



        #B: get all functions host
        #fill cluster_info['functions']=?

        #get all function names
        func_names = []
        for function in functions:
            name = getFunctionName(function)
            func_names.append(name)
        
        #ask kubectl to get all pods name and matches pod name with function names
        #functions_hosts={'function1': [host1, host2...] ...}
        functions_hosts = get_function_hosts_by_kubernetes(func_names)
        
        #add to cluster_info
        cluster_info['functions'] = functions_hosts
        
        now = datetime.datetime.now(datetime.timezone.utc).astimezone().timestamp()
        test_elapsed_time = now - test_started
        logger.info(f'************************* cluster_info (time_elapsed={round(test_elapsed_time/60,2)} min.) (test_name={test_name})\n{cluster_info}')

        #log_on_file
        if setup.cluster_info_populate['log_on_file']['enable']:
            #log_on_file?
            pass

        #C: populate nodes with new info by a push
        for node in setup.nodes:
            #if node is in test included
            # ["PEER", "homo1","10.0.0.80", "ubuntu"],
            if node[0] == 'PEER' or node[0] == 'COORDINATOR':
                peer_or_coordinator=node[0]
                ip = node[2]
                node_name = node[1]
                #push cluster_info to node
                populator_config = setup.cluster_info_populate
                output = push_cluster_info_to_node(ip, node_name, peer_or_coordinator, cluster_info,  populator_config)
            

        

        #sleep
        logger.info('cluster_info_populator sleep for ' + str(setup.cluster_info_populate['interval']) + ' sec')
        time.sleep(setup.cluster_info_populate['interval'])

    logger.info(f'cluster_info_populator stop')


#get_function_hosts_by_kubernetes
#assume functions are in openfaas-fn namespace and assume container name in index 0 equals function name
def get_function_hosts_by_kubernetes(functions_name):
    #functions_hosts={'function1': [host1, host2...] ...}
    functions_hosts = {}

    #get list of pods as json
    input_data={'operation': 'get-all-json', 'api_version': 'v1', 'kind': 'Pod', 'namespace': 'openfaas-fn'}
    #returns keys = kind, apiVersion, metadata and items
    pod_list, msg, err = pykubectl.apply(**input_data)
    
    #extract only pod name as function name and nodeName as host name
    #get hosts of afunction by name
    for function_name in functions_name:
        hosts = []
        #search in all pods
        for pod in pod_list['items']:
            #get all pods nodeName that whose container name is equal function_name
            if pod['spec']['containers'][0]['name'] == function_name:
                #if pod is running and has received a nodeName
                if 'nodeName' in pod['spec']:
                    hosts.append(pod['spec']['nodeName'])
                    logger.info(f"function/pod={pod['spec']['containers'][0]['name']} host/nodeName={pod['spec']['nodeName']}")
                #Pod is Pending
                else:
                    logger.error(f'Pod is Pending --> {pod["metadata"]["name"]}')
        #uppdate functions_hosts
        functions_hosts[function_name] = hosts

    #done
    return functions_hosts

#push_cluster_info_to_node
def push_cluster_info_to_node(ip, node_name, peer_or_coordinator, cluster_info, populator_config):
    sender ='MASTER'
    template = {}
    template['cluster_info'] = cluster_info
    template['populator_config'] = populator_config

    try:
        logger.info(f'push_cluster_info_to_node send request to node_name={node_name}, ip={ip}, cluster_info')
        #PEER by HTTP
        if peer_or_coordinator == 'PEER':
            response = internal_session.post('http://' + ip + ':5000/main_handler/push/'+ sender, timeout=10, json=template)
            done = True if response.ok else False
        #COORDINATOR by internal call
        else:
            response = main_handler('push', 'INTERNAL', template)
            done = True if response == "success" else False

    except Exception as e:
        logger.error(f'push_cluster_info_to_node failed \n{e}')
        return 0
    else:
        if done:
            logger.info(f'push_cluster_info_to_node: node {node_name} ok ')
            return 1
        else:
            logger.error(f'push_cluster_info_to_node: node {node_name} FAILED ')
            return 0


#pull_node_status
def pull_node_status(ip, node_name):
    #get node_status (0/1/2) 0 is down, 1 is up in boot, 2 is running and -1 is unavalable -2 test not started yet
    node_status = -1
    template = {'node_status': -1}
    sender = node_role

    try:
        response = internal_session.post('http://' + ip + ':5000/main_handler/pull/'+ sender, timeout=10, json=template)
    except Exception as e:
        logger.error(f'cluster_info_populate failed \n{e}')
    else:
        #extract response
        if response.json() and 'node_status' in response.json():
                node_status = response.json()['node_status']
                logger.info(f'cluster_info_populate: node {node_name} ok (status={node_status})')
        else:
            logger.error(f'cluster_info_populate: node {node_name} FAILED (status={node_status})')

    return node_status


#workload shape generator: reshape the concurrently based on the predefined stages
def workload_shape_generator(test_duration_time, test_elapsed_time, base_concurrently, stages, logger):
    #if no stage is defined, return the bas concurrently
    if stages == []: return base_concurrently

    # determine the concurrently based on the relevant stage specification

    # if no re-assignment occurs, the base_concurrently (original value) is used instead
    new_concurrently = base_concurrently

    # get test elapsed time in percent, as the stages start and end time are in percent format
    test_elapsed_percent = round(test_elapsed_time / test_duration_time * 100, 2)

    for stage in stages:
        # collect the stage information (pick default values if required)
        stageStartTimePercent = 0 if stage["stageStartTimePercent"] == None else stage["stageStartTimePercent"]
        stageEndTimePercent = 100 if stage["stageEndTimePercent"] == None else stage["stageEndTimePercent"]
        stageConcurrentlyStart = base_concurrently if stage["stageConcurrentlyStart"] == None else stage[
            "stageConcurrentlyStart"]
        stageConcurrentlyEnd = base_concurrently if stage["stageConcurrentlyEnd"] == None else stage[
            "stageConcurrentlyEnd"]
        stageSlope = "normal" if stage["stageSlope"] == None else stage["stageSlope"]
        stageStepLength = 1 if stage["stageStepLength"] == None else stage["stageStepLength"]

        # if test elapsed time is in the range of a specific stage, pick that stage
        if test_elapsed_percent >= stageStartTimePercent and test_elapsed_percent <= stageEndTimePercent:

            # step 1: Check the slope

            # if slope is set to default (45), do the usual, i.e., increment/decrement the concurrently towards the concurrentlyEnd gradually.
            if stageSlope == "normal":

                # normal slope

                # prepare some variables for calculations
                # measure stage duration time (max length) from percent values
                stage_duration_time = round(test_duration_time * ((stageEndTimePercent - stageStartTimePercent) / 100))
                # measure stage elapsed time
                # measure stage start time from its percent value
                stage_start_time = int(test_duration_time * (stageStartTimePercent / 100))
                stage_elapsed_time = test_elapsed_time - stage_start_time

                # main calculation
                # new_concurrently = base_concurrently
                new_concurrently = stageConcurrentlyStart
                new_concurrently += ((stageConcurrentlyEnd - stageConcurrentlyStart) / (
                            stage_duration_time / stageStepLength)) * \
                                    math.ceil((stage_elapsed_time / stageStepLength))
                # note that the steps are up then flat by "ceil". Otherwise, "floor" can be used. Now, partial steps are changed to full step.

            else:  # if the slope is flat, set the concurrently so it constantly remains equal to "stageConcurrentlyStart"; otherwise equal to base_concurrently
                if stageSlope == "flat":
                    # this simulates a flat rate in the button for the duration of the stage
                    new_concurrently = stageConcurrentlyStart if stageConcurrentlyStart != None else base_concurrently

                else:
                    logger.error("ERROR: The value for stageSlope is out of range")

            # only one stage applies at a time; hence stop searching at this interval.
            # Note: If some stages start and end time overlap, the one with the smallest index in stages is selected and the rest are ignored.
            break
        
    return round(new_concurrently)

#spawners
def workload_spawner(app_name, workload_type, iteration, interval, min_request_generation_interval, concurrently, time_based_termination, func_name, func_data, w_config, workload_shape, logger):
    global under_test
    global apps

    logger.info('spawner started')

    # sensor counter
    created = 0

    # iterations
    logger.info('iterations started for ' + str(iteration) + ' repeats')
    for i in range(iteration):
        iter_started = datetime.datetime.now(datetime.timezone.utc).astimezone().timestamp()
        
        # interarrival
        interarrival = (interval[i] if "exponential" in workload_type else interval)
        #min interarrival (not for sync)
        if interarrival < min_request_generation_interval and workload_type != 'sync':
            interarrival = min_request_generation_interval
        #no interval for sync workloads
        if workload_type == 'sync':
            if interarrival > 0:
                logger.warning('interarrival=' + str(interarrival) + ' while workload_type=' + workload_type + 'so I set interarrival=0')
                interarrival = 0

        if not 'poisson' in workload_type:
            if isinstance(concurrently, float):
                logger.error('Only if workload_type is poisson, concurrently can be a float number')

        #concurrency
        con = 1
        if workload_type != 'sync':
            # base concurrently (it may be manipulated by workload_shape_generator method)
            con = (round(concurrently[i]) if "poisson" in workload_type else round(concurrently))
            
                #shape to adjust concurrently
            test_duration_time = time_based_termination[1]
            now = datetime.datetime.now(datetime.timezone.utc).astimezone().timestamp()
            test_elapsed_time = now - test_started

            con = workload_shape_generator(test_duration_time, test_elapsed_time, con, workload_shape, logger)
        else:
            if (round(concurrently[i]) if "poisson" in workload_type else round(concurrently)) > 1:
                logger.warning('if workload_type=sync, concurrency is always 1 and no shape applies to it.')
                #????implement concurrency > 1 for sync

        #spawner index usd for sensor_id
        spawner_index = threading.current_thread().name.split('-')[-1]

        #start issuing requests

        # gevent or thread
        workload_worker = w_config[5]
        
        if workload_worker == "gevent":
            #gevents are created and started thank to monkey.
            pool = Pool(size=con)
            for gevent_i in range(con):
                pool.spawn(spawner_index, created, func_name, func_data, interarrival, workload_type, )
            
            if workload_type == 'sync':
                pool.join()
            #this is synchronous (blocking) and waits for all gevents to finish, otherwise kills them after timeout.
            #pool = Pool(size=concurrently)
            #timeout = gevent.Timeout(2, gevent.Timeout)
            #timeout.start()

            #try:
            #    for gevent_i in range(concurrently):
            #        pool.spawn(sample, session,i,i,"i")
            #    pool.join()
            #except gevent.Timeout as e:
            #    print("rrrrr")
            #finally:
            #    timeout.close()
            
        # thread
        elif workload_worker == "thread":
            threads = []

            for c in range(con):
                created += 1
                thread_create_sensor = threading.Thread(target=create_sensor,
                                                        args=(spawner_index, created, func_name, func_data, interarrival, workload_type, ))
                thread_create_sensor.name = "create_sensor" + "-" + func_name + "#" + str(spawner_index) + "#" + str(created)
                threads.append(thread_create_sensor)

            for t in threads:
                t.start()
        
            if workload_type == 'sync':
                for t in threads:
                    t.join()

        else:
            logger.error("spawner: workload_worker not found (thread, gevent, or...")


        # check termination: do not sleep after the final iteration or test is forced to finish
        if i == iteration - 1 or under_test == False:
            break
        # Get iteration duration
        now = datetime.datetime.now(datetime.timezone.utc).astimezone().timestamp()
        iter_elapsed = now - iter_started
        # check duration
        if iter_elapsed < interarrival and workload_type != 'sync':
            if iter_elapsed > (interarrival / 2):
                logger.warning('Workload iteration #' + str(i) + ' rather long! (' + str(iter_elapsed) + ')')
            # wait untill next iteration -deduct elapsed time
            time.sleep(interarrival - iter_elapsed)

        elif workload_type != 'sync':
            logger.error('Workload: Iteration #' + str(i)
                         + ' overlapped! (' + str(iter_elapsed) + ' elapsed) - next interval= ' + str(interarrival))
            print('Workload Iteration #' + str(i) + ' overlapped!')
            # ???skip next intervals that are passed
        else:
            logger.info('Iteration #' + str(i) + ' took ' + str(round(iter_elapsed,3)) + ' sec.')

    # end iterations
    now = datetime.datetime.now(datetime.timezone.utc).astimezone().timestamp()
    logger.info('spawner: Generated: #' + str(created) + ' requests for '  + func_name + ': in ' + str(round(now - test_started, 2)) + ' sec')

    # set created
    app_index = [apps.index(app) for app in apps  if app[0]== app_name and app[1]== True][0]
    apps[app_index][6] += created

    logger.info('stop')




#workload generator : a thread per application
@app.route('/workload', methods=['POST'])
def workload(my_app):
    time.sleep(1)  # Give enough time gap to create req to server to avoid connection error. or use sessions
    global logger
    global test_started
    global test_finished
    global apps
    global max_request_timeout
    global min_request_generation_interval
    global sessions
    global time_based_termination
    global under_test
    
    logger.info('workload: started')
    # [2] w type: "sync" or "static" or "poisson" or "exponential-poisson"
    # [3] workload: [[0]iteration [1]interval/exponential lambda(10=avg 8s)
    # [2]concurrently/poisson lambda (15=avg 17reqs ) [3] random seed (def=5)]
    # [4] func_name [5] func_data [6] created [7] recv
    app_name = my_app[0]

    workload_type = my_app[2]  # "sync" or "async-static" or "async-poisson" or "async-exponential-poisson"
    w_config = my_app[3]


    app_session = requests.session()
    # ???? 10 times concurrently is set by taste. pool_max_size can consider the max concurrently in workload_shape
    app_session.mount(
        'http://',
        requests.adapters.HTTPAdapter(pool_maxsize=w_config[2] * 10,
                                      max_retries=3,
                                      pool_block=True)
    )
    sessions[my_app[4]] = app_session

    iteration = 0
    interval = 0
    concurrently = 0
    seed = ""
    #sync (back to back)
    if workload_type == 'sync':
        iteration = w_config[0]
        #interval 
        interval = 0
        #concurrency ??? poisson can be also added for sync for dynamic number of workers
        concurrently = w_config[2]

    #static interarrival and concurrently
    elif workload_type == 'async-static':
        iteration = w_config[0]
        # interval
        interval = w_config[1]
        # concurrently
        concurrently = w_config[2]

    #random concurrently
    elif workload_type == 'async-poisson':
        iteration = w_config[0]
        # interval
        interval = w_config[1]
        # determine concurrently list
        # set seed
        seed = w_config[3]
        np.random.seed(seed)

        lmd_rate = w_config[2]
        if lmd_rate != 0:
            concurrently = np.random.poisson(lam=lmd_rate, size=iteration)
        else:  # force 0, if lambda is 0
            concurrently = [0] * iteration

    #random interarrival and concurrently
    elif workload_type == 'async-exponential-poisson':
        iteration = w_config[0]
        # determine interval list
        # set seed
        seed = w_config[3]
        np.random.seed(seed)

        lmd_scale = w_config[1]
        if lmd_scale != 0:
            # random.exponential(scale=1.0, size=None)
            interval = np.random.exponential(scale=lmd_scale, size=iteration)
        else:  # force 0, if lambda is 0
            interval = [0] * iteration

        # determine concurrently list
        lmd_rate = w_config[2]
        if lmd_rate != 0:
            concurrently = np.random.poisson(lam=lmd_rate, size=iteration)
        else:  # force 0 if lambda is 0
            concurrently = [0] * iteration

    #random interarrival
    elif workload_type == 'async-exponential':
        iteration = w_config[0]
        # determine interval list
        # set seed
        seed = w_config[3]
        np.random.seed(seed)

        lmd_scale = w_config[1]
        if lmd_scale != 0:
            # random.exponential(scale=1.0, size=None)
            interval = np.random.exponential(scale=lmd_scale, size=iteration)
        else:  # force 0 if lambda is 0
            interval = [0] * iteration

        concurrently = w_config[2]

    #workload shape
    workload_shape = w_config[4]

    func_name = my_app[4]
    func_data = my_app[5]
    # my_app[6] sensor created counter
    # my_app[7] actuation recv counter

    #spawners, if sync workload type, concurrency means spawners and isolated spawners start in their own thread to generate sync requests with concurrency of 1; otherwise, one spawner starts and generates requests with defined concurrency. Multiple spawners and concurrency>1 is to be implemented????
    spawners = 1 if workload_type != 'sync' else concurrently

    logger.info("workload: App {0} \n workload: {1} spawners: {2} \n Iterations: {3} \n "
                "Interval Avg. {4} ({5}-{6}) \n"
                "Concurrently Avg. {7} ({8}--{9})\n"
                " Seed {10} \n function {11} data {12}\n---------------------------".format(
        func_name, workload_type, str(spawners), iteration,
        round(sum(interval) / len(interval), 3) if "exponential" in workload_type else interval,
        round(min(interval), 3) if "exponential" in workload_type else "--",
        round(max(interval), 3) if "exponential" in workload_type else "--",
        round(sum(concurrently) / len(concurrently), 3) if "poisson" in workload_type else concurrently,
        round(min(concurrently), 3) if "poisson" in workload_type else "--",
        round(max(concurrently), 3) if "poisson" in workload_type else "--",
        seed, func_name, func_data))

    generator_st = datetime.datetime.now(datetime.timezone.utc).astimezone().timestamp()

    thread_spawners = []
    for spawner_index in range(spawners):
        thread_spawner = threading.Thread(target=workload_spawner,
                args=(app_name, workload_type, iteration, interval, min_request_generation_interval, concurrently, time_based_termination, func_name, func_data, w_config, workload_shape, logger,))
        thread_spawner.name = "spawner" + "-" + func_name + "-" + str(spawner_index)
        thread_spawners.append(thread_spawner)

    for t in thread_spawners:
        t.start()

    logger.info('waiting for ' + str(spawners) + ' spawners to finish...')
    for t in thread_spawners:
        t.join()

    logger.info('all spawners finished.')

    # # sensor counter
    # created = 0

    # # iterations
    # for i in range(iteration):
    #     iter_started = datetime.datetime.now(datetime.timezone.utc).astimezone().timestamp()

    #     # interarrival
    #     interarrival = (interval[i] if "exponential" in workload_type else interval)
    #     #min interarrival (not for sync)
    #     if interarrival < min_request_generation_interval and workload_type != 'sync':
    #         interarrival = min_request_generation_interval

    #     if not 'poisson' in workload_type:
    #         if isinstance(concurrently, float):
    #             logger.error('Only if workload_type is poisson, concurrently can be a float number')

    #     # base concurrently (it may be manipulated by workload_shape_generator method)
    #     con = (round(concurrently[i]) if "poisson" in workload_type else round(concurrently))
        
    #         #shape to adjust concurrently
    #     test_duration_time = time_based_termination[1]
    #     now = datetime.datetime.now(datetime.timezone.utc).astimezone().timestamp()
    #     test_elapsed_time = now - test_started

    #     con = workload_shape_generator(test_duration_time, test_elapsed_time, con, workload_shape, logger)

    #     #start issuing requests

    #     # gevent or thread
    #     workload_worker = w_config[5]
        
    #     if workload_worker == "gevent":
    #         #gevents are created and started thank to monkey.
    #         pool = Pool(size=con)
    #         for gevent_i in range(con):
    #             pool.spawn(create_sensor, created, func_name, func_data, interarrival, )
            
    #         #this is synchronous (blocking) and waits for all gevents to finish, otherwise kills them after timeout.
    #         #pool = Pool(size=concurrently)
    #         #timeout = gevent.Timeout(2, gevent.Timeout)
    #         #timeout.start()

    #         #try:
    #         #    for gevent_i in range(concurrently):
    #         #        pool.spawn(sample, session,i,i,"i")
    #         #    pool.join()
    #         #except gevent.Timeout as e:
    #         #    print("rrrrr")
    #         #finally:
    #         #    timeout.close()
            
    #     # thread
    #     elif workload_worker == "thread":
    #         threads = []

    #         for c in range(con):
    #             created += 1
    #             thread_create_sensor = threading.Thread(target=create_sensor,
    #                                                     args=(created, func_name, func_data, interarrival,))
    #             thread_create_sensor.name = "create_sensor" + "-" + func_name + "#" + str(created)
    #             threads.append(thread_create_sensor)

    #         for t in threads:
    #             t.start()
        
    #     else:
    #         logger.error("workload: workload_worker not found")


    #     # check termination: do not sleep after the final iteration or test is forced to finish
    #     if i == iteration - 1 or under_test == False:
    #         break
    #     # Get iteration duration
    #     now = datetime.datetime.now(datetime.timezone.utc).astimezone().timestamp()
    #     iter_elapsed = now - iter_started
    #     # check duration
    #     if iter_elapsed < interarrival and workload_type != 'sync':
    #         if iter_elapsed > (interarrival / 2):
    #             logger.warning('Workload iteration #' + str(i) + ' rather long! (' + str(iter_elapsed) + ')')
    #         # wait untill next iteration -deduct elapsed time
    #         time.sleep(interarrival - iter_elapsed)

    #     else:
    #         logger.error('Workload: Iteration #' + str(i)
    #                      + ' overlapped! (' + str(iter_elapsed) + ' elapsed) - next interval= ' + str(interarrival))
    #         print('Workload Iteration #' + str(i) + ' overlapped!')
    #         # ???skip next intervals that are passed
    
    # # end iterations
    # now = datetime.datetime.now(datetime.timezone.utc).astimezone().timestamp()
    # logger.info('workload: All Generated: ' + func_name + ': in ' + str(round(now - test_started, 2)) + ' sec')

    # # set created
    # apps[apps.index(my_app)][6] = created



    # ????if some are dropped. they are not added to app[7], so this condition is always false
    # wait for all actuators of this app, or for timeout, then move
    #???it assumes timeout is always > 30 sec
    app_index = [apps.index(app) for app in apps  if app[0]== app_name and app[1]== True][0]

    if apps[app_index][7] < apps[app_index][6]:
        logger.info('workload: ' + my_app[4] + ' sleep 5 sec: '
                    + str(apps[app_index][6]) + ' > ' + str(apps[app_index][7]))
        time.sleep(5)
    if apps[app_index][7] < apps[app_index][6]:
        logger.info('workload: func: ' + my_app[4] + ' sleep 10sec: '
                    + str(apps[app_index][6]) + ' > ' + str(apps[app_index][7]))
        time.sleep(10)
    if apps[app_index][7] < apps[app_index][6]:
        logger.info('workload: func: ' + my_app[4] + ' sleep 15sec: '
                    + str(apps[app_index][6]) + ' > ' + str(apps[app_index][7]))
        time.sleep(15)
    if apps[app_index][7] < apps[app_index][6]:
        logger.info('workload: func: ' + my_app[4] + ' sleep ' + str(max_request_timeout - 30 + 1) + 'sec: '
                    + str(apps[app_index][6]) + ' > ' + str(apps[app_index][7]))
        time.sleep(max_request_timeout - 30 + 1)

    logger.info("Workload: done, func: " + my_app[4] + " created:" + str(my_app[6])
                + " recv:" + str(apps[app_index][7]))

    # App workload is finished, call main_handler if timer is not already stopped
    if under_test:
        main_handler('app_done', 'INTERNAL')
    logger.info('workload: func: ' + my_app[4] + ' stop')
    return 'workload: Generator done'


def all_apps_done():
    global logger
    global apps
    global sensor_log
    global time_based_termination
    global test_finished  # by the last app
    global node_role
    global peers
    global max_request_timeout
    global lock
    global sensor_log
    logger.info('all_apps_done: start')
    now = datetime.datetime.now(datetime.timezone.utc).astimezone().timestamp()
    # alternative, if exist any -1 in finished time list, wait for timeout and then finish

    # all apps termination
    all_apps_done = True
    for app in apps:
        # Among enabled apps
        if app[1] == True:
            # Have you finished creating?
            if app[6] != 0:
                # Have you finished receiving?
                if app[6] == app[7]:
                    # app is done
                    logger.info("all_apps_done: True: Func {0} done, recv {1} of {2}".format(
                        app[4], str(app[7]), str(app[6])))
                else:
                    # receiving in progress
                    logger.info(
                        'all_apps_done: False: func ' + app[4] + ' created < recv: ' + str(app[6]) + " < " + str(
                            app[7]))
                    all_apps_done = False
                    break
            else:  # creating in progres
                logger.info('all_apps_done:False: func ' + app[4] + ' not set created yet')
                all_apps_done = False
                break

    logger.info('all_apps_done: stop: ' + str(all_apps_done))
    return all_apps_done

backend_discovery_counter = 0
# def backend_discovery():
#     global load_balancing
#     backends = load_balancing['backend_discovery']['backends']

def create_sensor(spawner_index, counter, func_name, func_data, admission_deadline, workload_type):
    global sessions
    global session_enabled
    global pics_num
    global pics_folder
    global sensor_log
    global load_balancing
    global node_IP
    global overlapped_allowed
    global debug
    global battery_cfg
    global sensor_admission_timeout
    global functions
    global boot_up_delay
    global lock
    global node_down_sensor_hold_duration
    # one-off sensor
    sample_started = datetime.datetime.now(datetime.timezone.utc).astimezone().timestamp()
    try:
        # random image name, pic names must be like "pic_1.jpg"????
        # n = random.randint(1, pics_num)

        #????Only pics image if yolo3 or ssd is in the function name. A parameter in the app config should tell if a function read images or not and it should be passed to the sensor_create.
        if 'yolo3' in func_name or 'ssd' in func_name:

            file_name = 'pic_' + str(counter % pics_num if counter % pics_num != 0  else 1) + '.jpg'
            file = {'image_file': open(pics_folder + file_name, 'rb')}

        # create sensor id
        sensor_id = str(sample_started) + '#' + func_name + '#' + str(spawner_index) + '#' + str(counter)
        
        # [0] func_name [1]created, [2]submitted/admission-dur, [3]queue-dur, [4]exec-dur,
        # [5] finished, [6]rt, [7] status, [8] repeat, [9] executor_ip, [10] objects, [11] accuracy
        sensor_log[sensor_id] = [func_name, sample_started, 0, 0, 0, 0, 0, -1, 0, "n/a", "n/a", [], []]

        #
        now = datetime.datetime.now(datetime.timezone.utc).astimezone().timestamp()
        test_elapsed = now - test_started

        #active_sensor_time_slots 449
        in_active_period = False

        #if active_sensor is not enabled, always workload is gone through.
        if active_sensor_time_slots['enabled'] == False:
            in_active_period = True
        
        for time_slot in active_sensor_time_slots['time_slots'][node_name]:
            #current time is within one of the active_sensor_time_slots
            if time_slot['start'] <= test_elapsed < time_slot['end']:
                in_active_period = True
                break
        
        #node_down_sensor_hold_duration. if async, it is 0
        node_down_sensor_hold_duration = node_down_sensor_hold_duration if not 'async' in workload_type else 0

        #not in any active period
        if not in_active_period:
            if debug: logger.info(f'dropped ***449*** since sensor in NOT in any active_sensor_time_slots. Then, hold the sensor for {node_down_sensor_hold_duration} sec')
            # drop and set code to 449
            sensor_log[sensor_id][7] = 449

            #hold the sensor. This is for when sync is used and we do not want to bommbard the workload generator becasue by droping this request, the next one immidiately is issued.
            #This hold duration simulates a think time.
            #For async, set it to 0
            time.sleep(node_down_sensor_hold_duration)

            #skip the rest of thread
            return None

        #hiccups_injection 450
        for hiccup in hiccups_injection:
            if test_elapsed >= hiccup['start'] and test_elapsed < hiccup['end']:
                #inside this hiccup period
                if debug: logger.info(f'dropped ***450*** since sensor in hiccup={hiccup}. Then, hold the sensor for {node_down_sensor_hold_duration} sec')
                
                # drop and set code to 450
                sensor_log[sensor_id][7] = 450
                
                #hold the sensor. This is for when sync is used and we do not want to bommbard the workload generator becasue by droping this request, the next one immidiately is issued.
                #This hold duration simulates a think time.
                #For async, set it to 0
                time.sleep(node_down_sensor_hold_duration)

                #skip the rest of thread
                return None
        
        # drop if no energy on node or on function's host (in battery sim mode only)
        if battery_cfg[0] == True:
            #if changed, a waiting time applies
            request_skipped = False

            soc = battery_cfg[3]
            min_battery_charge = battery_cfg[8]
            #A: node is down --> drop 451
            #DELETED
            # if soc < min_battery_charge:
            #ADDED node itself failed: failed.status=1
            if node_operation_status_getter(battery_cfg[12]) == 0:
                if debug: logger.info(f'dropped ***451*** since it is a dead node. Then, hold the sensor for {node_down_sensor_hold_duration} sec')
                # drop and set code to 451
                sensor_log[sensor_id][7] = 451

                request_skipped = True

            #B:  node come back to up, but not ready yet, drop it, except scheduler is warm --> drop 452
            #DELETED
            # elif (sample_started - battery_cfg[9]) < boot_up_delay:
            #ADDED node itself pending: pending.status = 1
            elif node_operation_status_getter(battery_cfg[12]) == 1:
                if debug: logger.info('dropped ***452*** -- booting up')
                # drop and set code to 452
                sensor_log[sensor_id][7] = 452

                request_skipped = True

            #neither is true
            elif not request_skipped:
                #check func hosts condtion!

                #Get func_hosts
                func_hosts = []
                for _f_name, _f_hosts in cluster_info['functions'].items():
                    if _f_name == func_name:
                        func_hosts = _f_hosts

                #C: hosts of function is empty (maybe Pending Pod) --> drop 453
                if not func_hosts:
                    #453
                    if debug: logger.info(f'dropped ***453*** since hosts of function is empty (maybe Pending Pod). Then, hold the sensor for {node_down_sensor_hold_duration} sec')
                    # drop and set code to 453
                    sensor_log[sensor_id][7] = 453

                    request_skipped = True
                
                #D: hosts of function are down --> drop 454
                else:
                    #check all hosts of the function (function may be scaled up to multiple replicas and each on different nodes - we consider that if one replica is on a dead host, no request is sent even to others as no pod-level load balancing is enabled in this method)
                    func_host_is_down=False

                    for _f_host in func_hosts:
                        for _node_name, _status in cluster_info['nodes'].items():
                            if _f_host == _node_name:
                                #DELETED
                                # if _status == 0:
                                #ADDED running.status = 1
                                if _status != 2:
                                    func_host_is_down = True
                                    break
                    #454 and 455
                    if func_host_is_down:
                        #D1 454 if func host is down and is remote
                        if node_name not in func_hosts:
                            #454
                            if debug: logger.info(f'dropped ***454*** since hosts of function are down. Then, hold the sensor for {node_down_sensor_hold_duration} sec')

                            # drop and set code to 454
                            sensor_log[sensor_id][7] = 454
                            
                            request_skipped = True

                        #455 func host is down and it is actually local. It is not captured as 451 since cluster_info can get updated later than soc. So, here, func is placed locally and while soc is > threshold, cluster_info is behind and says func's host is not ready
                        #to eliminate this kind of requests, minimize cluster_info intervals
                        else:
                            #local func_hosts
                            if debug: logger.info(f'dropped ***455*** since hosts of function that are local are down. Then, hold the sensor for {node_down_sensor_hold_duration} sec')

                            sensor_log[sensor_id][7] = 455
                            
                            request_skipped = True

            #a condition is not met
            if request_skipped:
                #hold the sensor. This is for when sync is used and we do not want to bommbard the workload generator becasue by droping this request, the next one immidiately is issued.
                #This hold duration simulates a think time.
                #For async, set it to 0
                time.sleep(node_down_sensor_hold_duration)

                #skip the rest of thread
                return None


        # value: Send async req to yolo function along with image_file
        if func_data == 'value':
            #HOW about if workload_type is sync???
            # no response is received, just call back is received
            ##if normal functions, the route is /function_name, but if trafficsplit is used, the gateway function is used (depicted in 'service' key of load_balancing, set by setup.py)
            
            #url
            listeners = load_balancing['frontends'][0]['listeners']
            ip = listeners['ip']
            port = str(listeners['port'])
            path = listeners['path']
            postfix = listeners['postfix'] if listeners['postfix'] else ''
            #convert postfix to func_name
            postfix = func_name if postfix == 'func_name' else postfix
            url = 'http://' + ip + ':' + port + path + postfix

            #header
            #Sensor-ID
            header ={}
            header['Sensor-ID'] = sensor_id

            #X-Callback-Url
            if 'async' in workload_type:
                header['X-Callback-Url'] = 'http://' + node_IP + ':5000/actuator'

            #??? only ssd and yolo is accepted for image load
            img = (file if 'yolo3' in func_name or 'ssd' in func_name else None)

            json_list = {}
            if 'crop-monitor' in func_name:
                json_list = {"user": sensor_id, "temperature": "10", "humidity": "5",
                             "moisture": "3", "luminosity": "1"}
            elif 'irrigation' in func_name:
                json_list = {"user": sensor_id, "temperature": "10", "humidity": "5",
                             "soil_temperature": "3", "water_level": "1", "spatial_location": "1"}

            #send
            try:
                #through session
                if session_enabled:
                    #open connection   
                    with sessions[func_name] as s:
                        #get = sync
                        if workload_type == 'sync':  
                            response = s.get(url, headers=header, files=img, json=json_list,
                                                    timeout=max_request_timeout)

                        #or post = async
                        else:
                            response = s.post(url, headers=header, files=img, json=json_list,
                                                    timeout=sensor_admission_timeout)
                    #close connection

                #through requestes
                else:
                    #get
                    if workload_type == 'sync':
                        response = requests.get(url, headers=header, files=img, json=json_list,
                                                    timeout=max_request_timeout)
                        response.close()
                    
                    #post
                    else:
                        response = requests.post(url, headers=header, files=img, json=json_list,
                                                    timeout=sensor_admission_timeout)
                        response.close()

                # no response is received
                # if response.status_code == 200 or response.status_code == 202:
                if response.ok:
                    if debug: logger.info('Reuest success ' + url)
                else:
                    logger.warning('Request failed - code ' + str(response.status_code))
                
            except Exception as e:
                logger.exception('Request for: ' + func_name + ': ' + file_name + ': sending failed.\n' + str(e) + '\nThis response object is not handled by code.')


        # Pioss: Send the image to Pioss. Then, it notifies the function.
        elif func_data == 'reference':
            #image path, not file
            img = (pics_folder + file_name if 'yolo3' in func_name or 'ssd' in func_name else None)
            #send to pioss and get response (if not sync, only submission response is received, but if sync, the execution response is received)
            response = pioss(func_name, file_name,'internal-write', img, sensor_id, workload_type)
            
            if isinstance(response, str):
                response = requests.Response
                response.status_code = 404

            # url = 'http://' + node_IP + ':5000/pioss/api/write/' + func_name + '/' + file_name
            # #???only ssd and yolo is accepted
            # img = (file if 'yolo3' in func_name or 'ssd' in func_name else None)
            # header = {'Sensor-ID': sensor_id}
 
            # try:
            #     if session_enabled:
            #         response = sessions[func_name].post(url, headers=header, timeout=int(sensor_admission_timeout), files=img)
            #     else:
            #         response = requests.post(url, headers=header, timeout=sensor_admission_timeout, files=img)
            # except Exception as e:
            #     logger.exception('post request: ' + str(e))

            # no response is received
            # finished when next operation (sending actual requst to function) is done.
        else:  # Minio
            pass

        # handle 404 error ?????
        # if response.status_code == 202 or response.status_code == 200:
        if response.ok: #status_code < 400

            now = datetime.datetime.now(datetime.timezone.utc).astimezone().timestamp()
            sample_elapsed = now - sample_started
            if debug: logger.info('submitted (' + str(round(sample_elapsed, 2)) + 's)')
            # Set admission duration. If sync, it is zero
            if 'async' in workload_type:
                sensor_log[sensor_id][2] = round(sample_elapsed, 2)

            #check submission overlapping
            if 'async' in workload_type:
                if (sample_elapsed) >= admission_deadline:
                    logger.warning('admission overlapped (' + str(sample_elapsed) + 's)')
                    if not overlapped_allowed:
                        logger.error('admission overlapped (' + str(sample_elapsed) + 's)')

        else: 
            #request failed
            if workload_type == 'sync':
                logger.warning('sensor_id=' + sensor_id + ' code=' + str(response.status_code))
            #submission failed
            else:
                logger.error('sensor_id=' + sensor_id + ' code=' + str(response.status_code))

        #if sync, set actuator because response contains the final response of request and no callback will be sent to actuator by function
        if workload_type == 'sync':
            owl_actuator(sensor_id, response)

    except requests.exceptions.ReadTimeout as ee:
        logger.error('ReadTimeout:' + func_name + '#' + str(counter) + '\n' + str(ee))
    except requests.exceptions.RequestException as e:
        logger.error('RequestException:' + func_name + '#' + str(counter) + '\n' + str(e))
    except Exception as eee:
        logger.exception('Exception:' + func_name + '#' + str(counter) + '\n' + str(eee) + '\ncluster_info=' +str(cluster_info))

endpoint_counter = 0
def event_bus(ip):
    global endpoint_counter 
    endpoint_counter += 1

    if endpoint_counter % 5 == 0:
        return '10.0.0.92'
    elif endpoint_counter % 5 == 1:
        return '10.0.0.93'
    elif endpoint_counter % 5 == 2:
        return '10.0.0.94'
    elif endpoint_counter % 5 == 3:
        return '10.0.0.95'
    elif endpoint_counter % 5 == 4:
        return '10.0.0.97'
    else:
        logger.error('endpoint_counter module / 5 out of range')

# Pi Object Storage System (Pioss)
# API-level and Method-level route decoration
@app.route('/pioss/api/write/<func_name>/<file_name>', methods=['POST'], endpoint='write_filename')
@app.route('/pioss/api/read/<func_name>/<file_name>', methods=['GET'], endpoint='read_filename')
def pioss(func_name, file_name,call_type='http', image_file=None, sensor_id=None, workload_type=None):
    global file_storage_folder
    global logger
    global lock
    global load_balancing
    global sensor_admission_timeout
    global debug
    global sessions
    global session_enabled
    global max_request_timeout

    #method
    if call_type == 'http':
        if request.method == 'POST':
            call_type = 'http-write'

    if call_type == 'internal-write':
        if image_file == None or sensor_id == None:
            logger.error('image_file and sensor_id are required for Pioss internal-write')


    # write operations
    if call_type == 'http-write' or call_type == 'internal-write':
        if debug: 
            logger.info('Pioss Write')

        # with lock:??
        try:
            # get image
            if call_type == 'http-write':
                image = request.files['image_file']
            else:
                image = image_file
        except:
            logger.error('pioss: ' + func_name + ': ' + file_name + ': unable to get')
            return 'pioss: ' + func_name + ': ' + file_name + ': unable to get'
        try:
            #store file
            # if received from http request, download it by save method. how about put in minio???
            if call_type == 'http-write':
                image.save(file_storage_folder + file_name)
            else:
                #if received internally, copy the file to the storage foled by its received path
                shutil.copyfile(image, file_storage_folder + file_name)

            if debug: logger.info('Pioss: write done - func:' + func_name + ' - ' + file_name)
        except Exception as e:
            logger.error('pioss: ' + func_name + ': ' + file_name + ': unable to download\n' + str(e))
            return 'pioss: ' + func_name + ': ' + file_name + ': unable to download'

        # notification: trigger the object detection function
        # curl -X POST -H "X-Callback-Url: http://10.0.0.91:5000/actuator" -H "Image-URL:http://10.0.0.91:5000/pioss/api/read/w1-ssd/pic_41.jpg" http://10.0.0.91:31112/async-function/yolo3
        #curl -X GET -i -H "Image-URL: http://localhostmachine:5500/pioss/api/read/w3-ssd/pic_41.jpg"  http://10.0.0.90:31112/function/w5-ssd/
        #hey -c 1 -z 5m -m GET -H "Image-URL:http://10.0.0.92:5005/" -t 15  http://10.0.0.90:31112/function/w2-ssd
        # Example: curl -X POST -F image_file=@./storage/pic_121.jpg  http://10.0.0.90:31112/function/yolo3
        # add sensor-id to -H

        # Trigger the function and pass Image_URL
            
        #url
        listeners = load_balancing['frontends'][0]['listeners']
        ip = listeners['ip']
        port = str(listeners['port'])
        path = listeners['path']
        postfix = listeners['postfix'] if listeners['postfix'] else ''
        #convert postfix to func_name
        postfix = func_name if postfix == 'func_name' else postfix
        url = 'http://' + ip + ':' + port + path + postfix

        ##if normal functions, the route is /function_name, but if trafficsplit is used, the gateway function is used (depicted in 'service' key of load_balancing, set by setup.py)
        # function_route = func_name if routes['function_route'] == 'func_name' else routes['function_route']

        # if workload_type == 'sync':
        #     #no async prefix
        #     url = 'http://' + gateway_IP + ':' + openfaas_gateway_port + '/function/' + function_route    
        # else:
        #     url = 'http://' + gateway_IP + ':' + openfaas_gateway_port + '/async-function/' + function_route
        
        #header
        #Sensor-ID
        header ={}
        header['Sensor-ID'] = str(request.headers.get('Sensor-ID')) if call_type == 'http-write' else sensor_id

        #X-Callback-Url
        if 'async' in workload_type:
            header['X-Callback-Url'] = 'http://' + node_IP + ':5000/actuator'

        #Use-Local-Image 
        if len(load_balancing['add_headers']) and 'Use-Local-Image' in load_balancing['add_headers']:
            header['Use-Local-Image'] = load_balancing['add_headers']['Use-Local-Image']

        #or Image-URL
        else:
            #internal headers
            #Connection
            if len(load_balancing['add_headers']) and 'Internal-Connection' in load_balancing['add_headers']:
                header['Internal-Connection'] = load_balancing['add_headers']['Internal-Connection']
            #Session
            if len(load_balancing['add_headers']) and 'Internal-Session' in load_balancing['add_headers']:
                header['Internal-Session'] = load_balancing['add_headers']['Internal-Session']

            #???replace all 5000 with admin port in load_balancing
            #build an API for given image
            #ip 
            #decentralized-tinyobj
            ip = ''
            if 'read' in load_balancing['object_storage'] and load_balancing['object_storage']['read']['type'] == 'decentralized-tinyobj':
                #local-generator
                if load_balancing['object_storage']['read']['ip'] == 'local-generator':
                    ip = node_IP
                #local-executor For test-purposes only. Ask function to download image from its local host.
                elif load_balancing['object_storage']['read']['ip'] == 'local-executor':
                    ip = 'localhostmachine'

                else:
                    logger.error( 'object-storage read ip ' + load_balancing['object_storage']['read']['ip'] + ' not found')
            #centralized-tinyobj
            elif 'read' in load_balancing['object_storage'] and load_balancing['object_storage']['read']['type'] == 'centralized-tinyobj':
                ip = load_balancing['object_storage']['read']['ip']
            #centralized-minio
            elif 'read' in load_balancing['object_storage'] and load_balancing['object_storage']['read']['type'] == 'centralized-minio':
                ip = load_balancing['object_storage']['read']['ip']
            #decentralized-minio
            elif 'read' in load_balancing['object_storage'] and load_balancing['object_storage']['read']['type'] == 'decentralized-minio':
                #local-generator
                if load_balancing['object_storage']['read']['ip'] == 'local-generator':
                    ip = node_IP
                #local-executor For test-purposes only. Ask function to download image from its local host.
                elif load_balancing['object_storage']['read']['ip'] == 'local-executor':
                    ip = 'localhostmachine'
                else:
                    logger.error( 'object-storage read ip ' + load_balancing['object_storage']['read']['ip'] + ' not found')

                ##temp?????
                # ip = event_bus(ip)

            else:
                logger.error('make sure object_storage info is correct')

            #port
            port = load_balancing['object_storage']['read']['port']

            
            #set Image-URL
            resource = '/pioss/api/read/'
            bucket = func_name
            object_name = file_name
            #minio address
            if load_balancing['object_storage']['read']['type'] == 'centralized-minio' or load_balancing['object_storage']['read']['type'] == 'decentralized-minio':
                resource = load_balancing['object_storage']['read']['resource']
                bucket = load_balancing['object_storage']['read']['bucket']

            header['Image-URL'] = 'http://' + ip + ':' + str(port) + resource + bucket + '/' + object_name
            
        #send
        try:
            #through session
            if session_enabled:
                #open connection   
                with sessions[func_name] as s:
                    #get
                    if workload_type == 'sync':
                        response = s.get(url, headers=header, timeout=max_request_timeout)    
                        #or
                        # header['Connection'] = 'close'
                        # response = sessions[func_name].get(url, headers=header, timeout=max_request_timeout)
                    #or post
                    else:
                        
                        response = s.post(url, headers=header, timeout=sensor_admission_timeout)
                #close connection

            #through requestes
            else:
                #get
                if workload_type == 'sync':
                    response = requests.get(url, headers=header, timeout=max_request_timeout)
                    response.close()
                
                #post
                else:
                    response = requests.post(url, headers=header, timeout=sensor_admission_timeout)
                    response.close()

            # no response is received
            # if response.status_code == 200 or response.status_code == 202:
            if response.ok:
                if debug: logger.info('Pioss: Notification Sent: ' + url)
            else:
                if workload_type == 'sync':
                    logger.warning('Pioss: Failed - code ' + str(response.status_code))
                else:
                    logger.error('Pioss: Failed - code ' + str(response.status_code))
            
            return response
            # return "write&notification done"
            
        except Exception as e:
            logger.exception('pioss: ' + func_name + ': ' + file_name + ': sending failed.\n' + str(e))
            return 'pioss: ' + func_name + ': ' + file_name + ': sending failed'
            

    # read operation
    elif request.method == 'GET':
        if debug: logger.info('Pioss Read')
        # get file
        img = open(file_storage_folder + file_name, 'rb').read()
        # preapare response (either make_response or send_file)
        response = make_response(img)
        response.headers.set('Content-Type', 'image/jpeg')
        response.headers.set(
            'Content-Disposition', 'attachment', filename=file_name)

        return response
        # return send_file(io.BytesIO(img), attachment_filename=file_name)
    else:
        logger.error('Pioss: operation not found')
        return "Failed"


#pioss_read
# @app.route('/pioss/api/read/<func_name>/<file_name>', methods=['GET'], endpoint='read_filename')
def pioss_read(func_name, file_name):
    global file_storage_folder

    # get file
    img = open(file_storage_folder + file_name, 'rb').read()
    # preapare response (either make_response or send_file)
    response = make_response(img)
    response.headers.set('Content-Type', 'image/jpeg')
    response.headers.set('Content-Disposition', 'attachment', filename=file_name)

    return response
    # return send_file(io.BytesIO(img), attachment_filename=file_name)


@app.route('/actuator', methods=['POST'])
def owl_actuator(sensor_id=None, response_obj=None):
    global logger
    global actuations
    global response_time
    global test_started
    global sensor_log
    global time_based_termination
    global apps
    global peers
    global suspended_replies
    global debug
    
    #if service mesh is used, returned X-Function-Name header shows the name of gateway function not the function that issued the requesy????
    with lock:
        #get headers
        headers = None
        try:
            if response_obj is None:
                headers = request.headers
            else:
                headers = response_obj.headers
        except:
            logger.error('owl_actuator: no headers object found in response because requests is not sent')

        if debug: logger.info('actuator:'
                              + ' sensor_id=' + str(headers.get('Sensor-Id')) 
                              + ', status_code=' + str(response_obj.status_code if response_obj else headers.get("X-Function-Status"))
                              + ', x-duration-seconds=' + str(round(float(headers.get('X-Duration-Seconds')), 2)
                                                        if headers.get('X-Duration-Seconds') 
                                                            and headers.get('X-Duration-Seconds') != "" else "--") + ' s'
                                + (', by ' + str(headers.get('X-POD-HOST-IP')) if headers.get('X-POD-HOST-IP') else '-')
                                + '/' + (str(headers.get('X-NODE-NAME')) if headers.get('X-NODE-NAME') else '-')
                                + '/' + (str(headers.get('X-POD-NAME')) if headers.get('X-POD-NAME') else '-')
                                + '/' + (str(headers.get('X-POD-IP')) if headers.get('X-POD-IP') else '-'))
        #get json data
        if response_obj is None:
            data = request.get_data(as_text=True)
        else:
            data = response_obj.text


        actuations += 1

        # get sensor id
        # X-Function-Status: 500
        # X-Function-Name: yolo3
        get_id = str(headers.get('Sensor-Id'))
        # print('get_id: ' + str(get_id))

        # if failed
        if get_id == 'None':
            # if debug: logger.warning('Actuator - Sensor-ID=None| app: ' +request.headers.get("X-Function-Name") + '| code: ' + request.headers.get("X-Function-Status") +' for #' + str(actuations))
            if debug: logger.warning("Actuator (failed) headers: " + str(headers))

            if response_obj is None: #not sync
                #sample for code 500 headers
                '''Host: 10.0.0.97:5000
                User-Agent: Go-http-client/1.1
                Content-Length: 0
                Date: Tue, 20 Sep 2022 04:02:26 GMT
                L5D-Proxy-Error: unexpected error
                X-Call-Id: fe13b0ed-542c-4f1b-8720-b152a4342498
                X-Duration-Seconds: 15.068210
                X-Function-Name: gw-func
                X-Function-Status: 500
                X-Start-Time: 1663646532641585182
                Accept-Encoding: gzip'''

                #???in service mesh, this returns the gateway function name not the actual function name.
                func_name = str(headers.get("X-Function-Name"))
                status = int(headers.get("X-Function-Status"))
                # IGNORED
                # NOTE: X-start-Time in headers is based on a different timeslot and format than my timestamp
                # sometimes X-Start-Time header is missed in replies with code 500, so set start_time=now
                if str(headers.get("X-Start-Time")) != 'None':
                    start_time = float(headers.get("X-Start-Time"))
                else:
                    start_time = datetime.datetime.now(datetime.timezone.utc).astimezone().timestamp()
                # END IGNORED

                stop_time = start_time = datetime.datetime.now(datetime.timezone.utc).astimezone().timestamp()
                exec_dur = float(headers.get("X-Duration-Seconds"))

                # add to suspended replies
                suspended_replies.append([func_name, status, stop_time, exec_dur])

            else: #sync
            #in sync, openfaas does not return its ALL built-in X-xxxx-xxx headers, only returns X-Duration-Seconds and X-Call-ID
                
                exec_dur = float(headers.get("X-Duration-Seconds") if headers.get("X-Duration-Seconds") else 0)

                sensor_log[sensor_id][4] = exec_dur
                sensor_log[sensor_id][5] = datetime.datetime.now(datetime.timezone.utc).astimezone().timestamp()
                sensor_log[sensor_id][6] = round(sensor_log[sensor_id][5] - sensor_log[sensor_id][1], 3) 
                sensor_log[sensor_id][7] = response_obj.status_code
                
                # [8] replies
                sensor_log[sensor_id][8] = sensor_log[sensor_id][8] + 1
                # increment received
                c = [index for index, app in enumerate(apps) if app[4] == sensor_log[sensor_id][0]]
                apps[c[0]][7] += 1
                
                # if repetitious
                if sensor_log[sensor_id][8] > 1:
                    logger.error('Actuator: a repetitious reply received: ' + str(sensor_log[sensor_id]))

        else:  # code=200
            # print('Actuator: Duration: ', str(headers.get('X-Duration-Seconds')))

            response_time.append(float(headers.get('X-Duration-Seconds')))
            # [0] function_name already set
            # [1]created time already set
            # [2]admission duration already set
            # [3] set NATstream queuing duration
            # NOTE: Openfaas X-Start-Time value is in 19 digits, not simillar to my timestamp
            # sensor_log[get_id][2]= float(request.headers.get('X-Start-Time')) - sensor_log[get_id][0] - sensor_log[get_id][1]
            sensor_log[get_id][3] = None
            # [4] set execution duration=given by openfaas
            sensor_log[get_id][4] = round(float(headers.get('X-Duration-Seconds')), 3)
            # [5] finished time=now
            now = datetime.datetime.now(datetime.timezone.utc).astimezone().timestamp()
            sensor_log[get_id][5] = now
            # [6]set response time (round trip)=finished time- created time
            sensor_log[get_id][6] = round(sensor_log[get_id][5] - sensor_log[get_id][1], 3)
            # [3] queuing=response time - admission dur. and execution dur.
            sensor_log[get_id][3] = round(sensor_log[get_id][6] - sensor_log[get_id][2] - sensor_log[get_id][4], 3)
            if sensor_log[get_id][3] < 0: sensor_log[get_id][3] = 0
            # [7] status code
            #in sync, openfaas does not return X-Function-Status
            if response_obj == None:
                sensor_log[get_id][7] = int(headers.get('X-Function-Status'))
            else:#sync
                sensor_log[get_id][7] = response_obj.status_code
            # [8] replies
            sensor_log[get_id][8] = sensor_log[get_id][8] + 1
            # increment received
            c = [index for index, app in enumerate(apps) if app[4] == sensor_log[get_id][0]]
            apps[c[0]][7] += 1
            
            # if repetitious
            if sensor_log[get_id][8] > 1:
                logger.error('Actuator: a repetitious reply received: ' + str(sensor_log[get_id]))

            #executor_host_ip
            sensor_log[get_id][9] = str(headers.get('X-POD-HOST-IP')) if headers.get('X-POD-HOST-IP') else "n/a"
            #executor_pod_ip
            sensor_log[get_id][10] = str(headers.get('X-POD-IP')) if headers.get('X-POD-IP') else "n/a"

            #detected objects
            try:
                if response_obj == None:
                    json_obj = request.json
                else:#sync
                    json_obj = response_obj.json()

                if json_obj:
                    if 'detected_objects' in json_obj:
                        #list of detected objects
                        detected_objects_list = json_obj['detected_objects']
                        for item in detected_objects_list:
                            sensor_log[get_id][11].append(item['object'])
                            sensor_log[get_id][12].append(int(item['confidence']))
            except Exception as e:
                logger.error("If doing object detection, callbacks sent to the actuator requires a body with this format\n request.json {'detected_objects': [{'object': 'person', 'confidence': 69}]}")
                
    return 'Actuator Sample Done'


# ---------------------------------------
def failure_handler():
    global logger
    global sensor_log
    global max_request_timeout
    global failure_handler_interval
    global suspended_replies
    global apps
    global under_test
    logger.info('failure_handler: start')
    # status codes:
    # 404: happens in create_sensor: not submitted to gateway as function does not exist (already removed)
    # 500: happens after submission: submitted but while executing, function started rescheduling to going down. Partial execution of task can happen here
    # 502: happens after submission: submitted but function is in scheduling process and is not up yet
    # 502: function timeout (especified in function yaml file)
    # 503: gateway timeout (especified in gateway yaml by kubectl edit deploy/gateway -n openfaas
    # note: queue-worker timeout seems ineffective
    # function and gateway have timeout settings.
    wrap_up = max_request_timeout + (failure_handler_interval * 2)

    while under_test or wrap_up > 0:
        # missed sensors
        missed_sensor_log = {}

        now = datetime.datetime.now(datetime.timezone.utc).astimezone().timestamp()
        # exist suspended replies, set on failed replies in owl_actuator
        if len(suspended_replies) > 0:
            # set missed sensors
            for key, sensor in sensor_log.items():
                # among those with no reply received by code
                if sensor[7] == -1:
                    # make sure it will not receive any reply
                    # and outdated (must have received a timeout reply at least, so it's missed)
                    if sensor[1] + max_request_timeout < now:
                        # add to missed sensors
                        missed_sensor_log[key] = sensor
            # sort missed sensors ascendingly by creation time
            # NOTE: sort, remove, etc. return None and should not be assigned to anything
            sorted(missed_sensor_log.items(), key=lambda e: e[1][1])

            # sort suspended replies ascendingly by stop_time
            suspended_replies.sort(key=lambda x: x[2])

            # assign suspended_replies to outdated missed_sensors
            for key, missed_sensor in missed_sensor_log.items():
                for reply in suspended_replies:
                    # As sorted, get the first match and break
                    # same application
                    # reply=[func_name, status, stop_time, exec_dur] #start_time is not used???? It is sometimes missed in replies 500 by OpenFaaS
                    if missed_sensor[0] == reply[0]:
                        # set exec_duration
                        missed_sensor[4] = reply[3]
                        # set status
                        missed_sensor[7] = reply[1]
                        # set reply counter
                        missed_sensor[8] = missed_sensor[8] + 1

                        # update sensor_log
                        sensor_log[key] = missed_sensor

                        # increment received
                        c = [index for index, app in enumerate(apps) if app[4] == missed_sensor[0]]
                        apps[c[0]][7] += 1

                        # removal of the suspended reply
                        suspended_replies.remove(reply)
                        break
        time.sleep(failure_handler_interval)

        if not under_test:
            # only first time run
            if wrap_up == max_request_timeout + (failure_handler_interval * 2):
                logger.info("failure_handler: wrapping up: " + str(wrap_up) + "sec...")
            if not all_apps_done():  # is all_apps_done, no need to wait for failure handler
                wrap_up -= failure_handler_interval
            else:
                break
            # only last time run
            if wrap_up <= 0:
                logger.info('failure_handler:missed' + str(missed_sensor_log))
                logger.info('failure_handler:suspended' + str(suspended_replies))
    logger.info('failure_handler: stop')


# monitoring
def monitor():
    logger.info('start')
    global monitor_interval
    global down_time
    global current_time
    global current_time_ts
    global response_time_accumulative
    global battery_charge
    global node_op
    if utils.what_device_is_it('raspberry pi 3') or utils.what_device_is_it('raspberry pi 4'): global pijuice
    global cpuUtil
    global cpu_temp
    global cpu_freq_curr
    global cpu_freq_max
    global cpu_freq_min
    global cpu_ctx_swt
    global cpu_inter
    global cpu_soft_inter
    global memory
    global disk_usage
    global disk_io_usage
    global bw_usage
    global power_usage
    global under_test
    global raspbian_upgrade_error
    global battery_cfg
    
    while under_test:
        
        # time
        # ct = datetime.datetime.now().strftime("%d%m%Y-%H%M%S")
        ct = datetime.datetime.now(datetime.timezone.utc).astimezone()  # local
        ct_ts = datetime.datetime.now(datetime.timezone.utc).astimezone().timestamp()  # local ts

        current_time.append(ct)
        current_time_ts.append(ct_ts)

        # response time
        if not response_time:
            response_time_accumulative.append(0)
        else:
            response_time_accumulative.append(round(sum(response_time) / len(response_time), 3))

        #battery_history (all units mWh)
        
        
        

        # read Pijuice battery
        if (utils.what_device_is_it('raspberry pi 3') or utils.what_device_is_it('raspberry pi 4')) and battery_operated:
            charge = pijuice.status.GetChargeLevel()
            battery_charge.append(int(charge['data']))

            #node_op
            operation_status = node_operation_status_getter(battery_cfg[12])
            
            #ADDED#
            node_op.append(operation_status)
            #DELETED node_op.append(battery_cfg[12])

        # battery sim
        elif battery_cfg[0] == True:
            
            #battery_charge (capped by max_battery_charge)
            max_battery_charge = battery_cfg[1] #mwh
            soc = battery_cfg[3] #mwh
            soc_percent = round(soc / max_battery_charge * 100) #%
            battery_charge.append(soc_percent) #%

            #node_op
            
            operation_status = node_operation_status_getter(battery_cfg[12])
            #ADDED#
            node_op.append(operation_status)
            #DELETED node_op.append(battery_cfg[12])

            
        else:
            battery_charge.append(-1)

            #node_op
            node_op.append(-1)

        # read cpu
        cpu = psutil.cpu_percent()
        #read GPU???for Jetson Nano
        cpuUtil.append(cpu)
        # cpu frequency
        freq = re.split(', |=', str(psutil.cpu_freq()).split(')')[0])
        cpu_freq_curr.append(int(freq[1].split('.')[0]))
        cpu_freq_min.append(int(freq[3].split('.')[0]))
        cpu_freq_max.append(int(freq[5].split('.')[0]))

        swt = re.split(', |=', str(psutil.cpu_stats()).split(')')[0])
        cpu_ctx_swt.append(int(swt[1]))
        cpu_inter.append(int(swt[3]))
        cpu_soft_inter.append(int(swt[5]))

        # read memory
        memory_tmp = psutil.virtual_memory().percent
        memory.append(memory_tmp)
        # read disk
        disk_usage_tmp = psutil.disk_usage("/").percent
        disk_usage.append(disk_usage_tmp)
        # read disk I/O: read_count, write_count, read_bytes, write_bytes
        if raspbian_upgrade_error:
            tmp = ['-1', '-1', '-1', '-1', '-1', '-1', '-1', '-1', ]
        else:
            tmp = str(psutil.disk_io_counters()).split("(")[1].split(")")[0]
            tmp = re.split(', |=', tmp)
        tmp_list = [int(tmp[1]), int(tmp[3]), int(tmp[5]), int(tmp[7])]
        disk_io_usage.append(tmp_list)
        # read cpu temperature
        sensors_temp = psutil.sensors_temperatures()
        if utils.what_device_is_it('raspberry pi'):
            cpu_temp_curr = sensors_temp['cpu_thermal'][0]
            cpu_temp_curr = re.split(', |=', str(cpu_temp_curr))[3]
        elif utils.what_device_is_it('nvidia jetson nano'):
            cpu_temp_curr = sensors_temp['thermal-fan-est'][0]
            cpu_temp_curr = re.split(', |=', str(cpu_temp_curr))[3]
        else:
            #??? cpu temperature for some devices like Intel NUC are not found in this way.
            cpu_temp_curr = "0"
        cpu_temp.append(cpu_temp_curr)
        # read bandwidth: packets_sent, packets_rec, bytes_sent, bytes_rec, bytes_dropin, bytes_dropout
        bw_tmp = [psutil.net_io_counters().packets_sent, psutil.net_io_counters().packets_recv,
                  psutil.net_io_counters().bytes_sent, psutil.net_io_counters().bytes_recv,
                  psutil.net_io_counters().dropin, psutil.net_io_counters().dropout]
        bw_usage.append(bw_tmp)
        
        # read usb power meter
        if usb_meter_involved:
            power_usage.append(read_power_meter())
        else:
            power_usage.append([-1, -1, -1, -1, -1, -1])
        
        time.sleep(monitor_interval)

    # close bluetooth connection
    if usb_meter_involved:
        sock.close()

    logger.info('done')


def read_power_meter():
    global lock
    global sock
    global logger
    output = []
    # Send request to USB meter
    d = b""
    with lock:
        while True:
            sock.send((0xF0).to_bytes(1, byteorder="big"))
            d += sock.recv(130)
            if len(d) != 130:
                continue
            else:
                break

    # read data
    data = {}
    data["Volts"] = struct.unpack(">h", d[2: 3 + 1])[0] / 1000.0  # volts
    data["Amps"] = struct.unpack(">h", d[4: 5 + 1])[0] / 10000.0  # amps
    data["Watts"] = struct.unpack(">I", d[6: 9 + 1])[0] / 1000.0  # watts
    data["temp_C"] = struct.unpack(">h", d[10: 11 + 1])[0]  # temp in C

    g = 0
    for i in range(16, 95, 8):
        ma, mw = struct.unpack(">II", d[i: i + 8])  # mAh,mWh respectively
        gs = str(g)

        data[gs + "_mAh"] = ma
        data[gs + "_mWh"] = mw
        g += 1

    temp = [data["0_mWh"], data["0_mAh"],
            data["Watts"], data["Amps"], data["Volts"],
            data["temp_C"]]

    output = temp

    return output


# connect to USB power meter
def usb_meter_connection():
    # python usbmeter --addr 00:15:A5:00:03:E7 --timeout 10 --interval 1 --out /home/pi/logsusb
    global sock
    global logger
    global bluetooth_addr
    sock = None
    addr = bluetooth_addr

    # Disconnect previous Bluetooth connection???
    # instead, do not reconnect after each test. Keep using previous connection
    # or shotdown() and then close() socket after each test
    # or use hcitool in python https://www.programcreek.com/python/example/14725/bluetooth.BluetoothSocket
    stoutdata = sp.getoutput("sudo hcitool dc " + bluetooth_addr)
    logger.info("Bluetooth disconnected")
    connected = False

    while True:
        try:
            sock = BluetoothSocket(RFCOMM)
        except Exception as e:
            logger.error(str(e))
            logger.error('Bluetooth driver might not be installed, or python is used instead of ***python3***')
        # sock.settimeout(10)
        try:
            logger.info("usb_meter_connection: Attempting connection...")
            res = sock.connect((addr, 1))
        except btcommon.BluetoothError as e:
            logger.warning("usb_meter_connection: attempt failed: " + str(e))
            connected = False
        except:
            logger.warning("usb_meter_connection: attempt failed2:" + addr)
            connected = False
        else:
            print("Connected OK")
            logger.info('usb_meter_connection: USB Meter Connected Ok (' + addr + ')')
            connected = True
            break
        time.sleep(3)

    # time.sleep(60)
    if connected == False:
        # wifi on
        cmd = "rfkill unblock all"
        print(cmd)
        logger.info(cmd)
        utils.shell(cmd)
        print('usb_meter_connection: ERROR-USB Meter Failed to connect!!!!!')
        logger.error('ERROR-USB Meter Failed to connect!!!!!')
        if battery_operated: battery_power('ON')
        # logger.error('usb_meter_connection: Node in Sleep...')
        # time.sleep(86400)

    return connected


# ---------------------------------

def save_reports():
    global metrics
    global node_name
    global apps
    global test_name
    global log_path
    global test_started
    global test_finished
    global sensor_log
    global node_role
    global snapshot_report
    global throughput
    global throughput2
    global down_time
    global functions
    global workers

    test_finished = datetime.datetime.now(datetime.timezone.utc).astimezone().timestamp()
    test_duration = round((test_finished - test_started) / 60, 0)

    metrics["info"] = {"test_name": test_name,
                       "test_duration": test_duration,
                       "test_started": test_started,
                       "test_finished": test_finished}
    # print logs
    logger.critical('save_reports: Test ' + test_name + ' lasted: '
                    + str(test_duration) + ' min')

    if node_role == "LOAD_GENERATOR" or node_role == "STANDALONE":
        # OVERALL

        # calculate response times
        app_name = []
        creation_time = []
        admission_duration = []
        queuing_duration = []
        execution_duration = []
        useless_execution_duration = []
        finished_time = []
        response_time_suc = []
        response_time_suc_fail = []
        #executors
        executor_host_ips=[]
        executor_pod_ips=[]
        #calculate detected objects
        detected_objects = []
        detected_objects_accuaracy = []

        # sensors
        created = 0
        sent = 0
        recv = 0
        for app in apps:  # ???index based on apps order, in future if apps change, it changes
            if app[1] == True:
                created += copy.deepcopy(app[6])
                recv += copy.deepcopy(app[7])

        logger.critical('created {} recv {}'.format(created, recv))

        # replies
        # actuator/reply counter
        replies_counter = [0] * len(apps)
        # reply status
        replies_status = [[0] * 6 for _ in range(len(apps))]  # *len(apps) #status code of 200, 500, 502, 503, others
        # dropped sensors per app 451
        dropped_sensors = [0] * len(apps)
        # dropped due to boot up per app 452
        dropped_sensors_in_boot_up = [0] * len(apps)
        #dropped due to no host available (maybe pending pod) 453
        dropped_sensors_no_host = [0] * len(apps)
        #dropped due to func host being down 454
        dropped_sensors_func_host_down = [0] * len(apps)
        #dropped due to func host being up but cluster_info saying status down 455
        dropped_sensors_func_local_host_down = [0] * len(apps)
        # dropped sensors by hiccups per app 450
        dropped_sensors_hiccup = [0] * len(apps)
        # dropped sensors by active_sensor_time_slots per app 449
        dropped_sensors_active_sensor = [0] * len(apps)
        # [0] func_name [1]created, [2]submitted/admission-dur, [3]queue-dur, [4]exec-dur. [5] finished, [6]rt
        sensor_data = []

        labels = ['func_name', 'created_at', 'admission', 'queue', 'exec', 'finished_at',
                  'round_trip', 'status', 'replies', 'executor_host_ip', 'executor_pod_ip', 'objects', 'accuracy']
        sensor_data.append(labels)

        for sensor in sensor_log.values():  # consider failed ones ?????
            # Get app index
            c = [index for index, app in enumerate(apps) if app[4] == sensor[0]]
            app_index = apps.index(apps[c[0]])

            if sensor[7] != 449 and sensor[7] != 450 and sensor[7] != 451 and sensor[7] != 452 and sensor[7] != 453 and sensor[7] != 454 and sensor[7] != 455:  # dropped (not sent) sensors are not involved in response time and replies
                # time and durations
                admission_duration.append(sensor[2])
                if sensor[7] == 200:  # only success sensors contribute in response time????? weight of failed ones???
                    creation_time.append(sensor[1])
                    finished_time.append(sensor[5])

                    queuing_duration.append(sensor[3])
                    execution_duration.append(sensor[4])

                    response_time_suc.append(sensor[6])
                    response_time_suc_fail.append(sensor[6])
                    #executor
                    executor_host_ips.append(sensor[9])
                    executor_pod_ips.append(sensor[10])
                    #detections
                    detected_objects.extend(sensor[11])
                    detected_objects_accuaracy.extend(sensor[12])

                else:
                    useless_execution_duration.append(sensor[4])
                    # app timeout = max exec time
                    func_info = apps[app_index][8]
                    func_timeout = int(func_info[12].split('s')[0])
                    response_time_suc_fail.append(func_timeout)
                # reply counter
                replies_counter[app_index] += sensor[8]

                # reply status
                if sensor[7] == 200:
                    replies_status[app_index][0] += 1
                elif sensor[7] == 500:
                    replies_status[app_index][1] += 1
                elif sensor[7] == 502:
                    replies_status[app_index][2] += 1
                elif sensor[7] == 503:
                    replies_status[app_index][3] += 1
                elif sensor[7] == -1:
                    replies_status[app_index][4] += 1
                else:  # others
                    replies_status[app_index][5] += 1

                # sent
                sent += 1

            # dropped sensor
            else:
                if sensor[7] == 451:
                    dropped_sensors[app_index] += 1
                elif sensor[7] == 452:
                    dropped_sensors_in_boot_up[app_index] += 1
                elif sensor[7] == 453:
                    dropped_sensors_no_host[app_index] +=1
                elif sensor[7] == 454:
                    dropped_sensors_func_host_down[app_index] +=1
                elif sensor[7] == 455:
                    dropped_sensors_func_local_host_down[app_index] +=1
                elif sensor[7] == 450:
                    dropped_sensors_hiccup[app_index] +=1
                elif sensor[7] == 449:
                    dropped_sensors_active_sensor[app_index] +=1
                else:
                    logger.error('unknown dropped_sensor')




            # data list
            sensor_data.append([str(sensor[0]), str(sensor[1]), str(sensor[2]),
                                str(sensor[3]), str(sensor[4]), str(sensor[5]),
                                str(sensor[6]), str(sensor[7]), str(sensor[8]),
                                str(sensor[9]), str(sensor[10]),
                                ','.join(sensor[11]), ','.join(map(str,sensor[12]))])

        # save sensor data
        log_index = log_path + "/" + node_name + "-sensors.csv"
        logger.critical('save_reports: ' + log_index)
        np.savetxt(log_index, sensor_data, delimiter=",", fmt="%s")

        # PRINT LOGS of METRICS
        logger.critical('METRICS: OVERALL****************************')

        # OVERALL created recv by replies (actuators)
        logger.critical('OVERALL: REQ. CREATED: ' + str(created)
                        + '     RECV (by apps): ' + str(recv) + '     RECV (by sensor[8] counter): ' + str(
            sum(replies_counter)))
        sent_percent = round(sent / created * 100, 2) if created > 0 else 0
        logger.critical('OVERALL: REQ. SENT: ' + str(sent) + ' (' + str(sent_percent) + ' %)')

        # OVERALL status codes
        code200 = 0
        code500 = 0
        code502 = 0
        code503 = 0
        code_1 = 0
        others = 0
        for row in replies_status:
            code200 += row[0]
            code500 += row[1]
            code502 += row[2]
            code503 += row[3]
            code_1 += row[4]
            others += row[5]
        success_rate = (round((code200 / sum([code200, code500, code502, code503, code_1, others])) * 100, 2)
                        if sum([code200, code500, code502, code503, code_1, others]) > 0 else 0)

        logger.critical("OVERALL: Success Rate (200/sent): {}%".format(success_rate))
        logger.critical(
            "OVERALL: Success Rate (200/sent) new: {}%".format(round(code200 / sent * 100, 2) if sent > 0 else 0))
        logger.critical("OVERALL: {0}{1}{2}{3}{4}{5}".format(
            'CODE200=' + str(code200) if code200 > 0 else ' ',
            ', CODE500=' + str(code500) if code500 > 0 else ' ',
            ', CODE502=' + str(code502) if code502 > 0 else ' ',
            ', CODE503=' + str(code503) if code503 > 0 else ' ',
            ', CODE-1=' + str(code_1) if code_1 > 0 else ' ',
            ', OTHERS=' + str(others) if others > 0 else ' '))
        #451
        dropped_sensors_sum = sum(dropped_sensors)
        dropped_sensors_percent = round((sum(dropped_sensors) / created) * 100, 2) if created > 0 else 0
        logger.critical("OVERALL: Dropped Sensors ****451*** (created, not sent): sum "
                        + str(dropped_sensors_sum) + " --- percent " + str(dropped_sensors_percent) + " %")
        #452
        dropped_sensors_in_boot_up_sum = sum(dropped_sensors_in_boot_up)
        dropped_sensors_in_boot_percent = round((sum(dropped_sensors_in_boot_up) / created) * 100,
                                                2) if created > 0 else 0
        logger.critical("OVERALL: Dropped Sensors in boot up ***452*** (created, not sent): "
                        + "sum(" + str(dropped_sensors_in_boot_up_sum) + ") "
                        + " --- percent " + str(dropped_sensors_in_boot_percent) + " %")

        #453
        dropped_sensors_no_host_sum = sum(dropped_sensors_no_host)
        dropped_sensors_no_host_percent = round((sum(dropped_sensors_no_host) / created) * 100, 2) if created > 0 else 0
        logger.critical("OVERALL: dropped_sensors_no_host ***453*** (created, not sent): sum "
                        + str(dropped_sensors_no_host_sum) + " --- percent " + str(dropped_sensors_no_host_percent) + " %")
        #454
        dropped_sensors_func_host_down_sum = sum(dropped_sensors_func_host_down)
        dropped_sensors_func_host_down_percent = round((sum(dropped_sensors_func_host_down) / created) * 100, 2) if created > 0 else 0
        logger.critical("OVERALL: dropped_sensors_func_host_down ***454*** (created, not sent): sum "
                        + str(dropped_sensors_func_host_down_sum) + " --- percent " + str(dropped_sensors_func_host_down_percent) + " %")
        
        #455
        dropped_sensors_func_local_host_down_sum = sum(dropped_sensors_func_local_host_down)
        dropped_sensors_func_local_host_down_percent = round((sum(dropped_sensors_func_local_host_down) / created) * 100, 2) if created > 0 else 0
        logger.critical("OVERALL: dropped_sensors_func_local_host_down ***455*** (created, not sent): sum "
                        + str(dropped_sensors_func_local_host_down_sum) + " --- percent " + str(dropped_sensors_func_local_host_down_percent) + " %")

        #450
        dropped_sensors_hiccup_sum = sum(dropped_sensors_hiccup)
        dropped_sensors_hiccup_percent = round((sum(dropped_sensors_hiccup) / created) * 100, 2) if created > 0 else 0
        logger.critical("OVERALL: dropped_sensors_hiccup ***450*** (created, not sent): sum "
                        + str(dropped_sensors_hiccup_sum) + " --- percent " + str(dropped_sensors_hiccup_percent) + " %")
        
        #449
        dropped_sensors_active_sensor_sum = sum(dropped_sensors_active_sensor)
        dropped_sensors_active_sensor_percent = round((sum(dropped_sensors_active_sensor) / created) * 100, 2) if created > 0 else 0
        logger.critical("OVERALL: dropped_sensors_active_sensor ***449*** (created, not sent): sum "
                        + str(dropped_sensors_active_sensor_sum) + " --- percent " + str(dropped_sensors_active_sensor_percent) + " %")
        
        # OVERALL response time
        admission_duration_avg = round(statistics.mean(admission_duration), 2) if len(admission_duration) else 0
        admission_duration_max = round(max(admission_duration), 2) if len(admission_duration) else 0
        queuing_duration_avg = round(statistics.mean(queuing_duration), 2) if len(queuing_duration) else 0
        queuing_duration_max = round(max(queuing_duration), 2) if len(queuing_duration) else 0

        execution_duration_avg = round(statistics.mean(execution_duration), 2) if len(execution_duration) else 0
        execution_duration_max = round(max(execution_duration), 2) if len(execution_duration) else 0

        response_time_suc_avg = round(statistics.mean(response_time_suc), 2) if len(response_time_suc) else 0
        response_time_suc_max = round(max(response_time_suc), 2) if len(response_time_suc) else 0

        response_time_suc_fail_avg = round(statistics.mean(response_time_suc_fail), 2) if len(
            response_time_suc_fail) else 0
        response_time_suc_fail_max = round(max(response_time_suc_fail), 2) if len(response_time_suc_fail) else 0

        useless_execution_duration_sum = round(sum(useless_execution_duration)) if len(
            useless_execution_duration) else 0

        logger.critical('OVERALL: avg. Adm. Dur. (sent only)---> ' + str(admission_duration_avg)
                        + '  (max= ' + str(admission_duration_max) + ')')
        logger.critical('OVERALL: avg. Q. Dur. (success only) ---> ' + str(queuing_duration_avg)
                        + '  (max= ' + str(queuing_duration_max) + ')')
        logger.critical('OVERALL: avg. Exec. +(scheduling) Dur. (success only) ---> '
                        + str(execution_duration_avg)
                        + '  (max= ' + str(execution_duration_max) + ')')
        logger.critical('OVERALL: avg. RT (success only) ---> ' + str(response_time_suc_avg)
                        + '  (max= ' + str(response_time_suc_max) + ')')
        logger.critical('OVERALL: avg. RT (success + fail) ---> ' + str(response_time_suc_fail_avg)
                        + '  (max= ' + str(response_time_suc_fail_max) + ')')
        logger.critical('OVERALL: sum Useless Exec. Dur. ---> ' + str(useless_execution_duration_sum))

        # Percentile
        percentiles_suc = (
            np.percentile(response_time_suc, [0, 25, 50, 75, 90, 95, 99, 99.9, 100]) if len(response_time_suc) else [0,
                                                                                                                     0,
                                                                                                                     0,
                                                                                                                     0,
                                                                                                                     0,
                                                                                                                     0,
                                                                                                                     0,
                                                                                                                     0,
                                                                                                                     0])
        percentiles_suc = ([round(num, 3) for num in percentiles_suc])

        percentiles_suc_fail = (np.percentile(response_time_suc_fail, [0, 25, 50, 75, 90, 95, 99, 99.9, 100]) if len(
            response_time_suc_fail) else [0, 0, 0, 0, 0, 0, 0, 0, 0])
        percentiles_suc_fail = ([round(num, 3) for num in percentiles_suc_fail])
        logger.critical('OVERALL: Percentiles (success only): ' + str(percentiles_suc))
        logger.critical('OVERALL: Percentiles (success success + fail): ' + str(percentiles_suc_fail))

        #executors
        #host
        #get a copy of all involved ips
        different_host_ips=list(set(executor_host_ips))
        #prepaer a counter associated to the ips in the obtained list
        host_ip_counter=[0]*len(different_host_ips)
        #search for the number of repetitions of each ip
        for ip_index in range(len(different_host_ips)):
            host_ip_counter[ip_index] = executor_host_ips.count(different_host_ips[ip_index])

        #pod
        #get a copy of all involved ips
        different_pod_ips=list(set(executor_pod_ips))
        #prepaer a counter associated to the ips in the obtained list
        pod_ip_counter=[0]*len(different_pod_ips)
        #search for the number of repetitions of each ip
        for ip_index in range(len(different_pod_ips)):
            pod_ip_counter[ip_index] = executor_pod_ips.count(different_pod_ips[ip_index])

        #print
        logger.critical('OVERALL: executor hosts\n' +
            str([str(different_host_ips[ip_index]) + '=' + str(host_ip_counter[ip_index])  for ip_index in range(len(different_host_ips))]))
            
        logger.critical('OVERALL: executor pods\n' + 
            str([str(different_pod_ips[ip_index]) + '=' + str(pod_ip_counter[ip_index]) for ip_index in range(len(different_pod_ips))]))

        #object detection
        detected_objects_sum = len(detected_objects)
        #assumed len detected_objects == len response_time_sec??
        detected_objects_avg = round(len(detected_objects) / len(response_time_suc), 2) if len(response_time_suc) and len(detected_objects) else 0
        detected_objects_accuaracy_avg = round(statistics.mean(detected_objects_accuaracy), 2) if len(detected_objects_accuaracy) else 0
        logger.critical('OVERALL: avg. Obj. Detection (success only) ---> sum obj= ' + str(detected_objects_sum)
                        + ',  avg= ' + str(detected_objects_avg) 
                        + ', accuracy= ' + str(detected_objects_accuaracy_avg))

        # Throughput (every 30sec)
        throughput = []
        throughput2 = []
        timer = test_started + 30

        while True:
            created_tmp = 0
            for time in creation_time:
                if time < timer and time > timer - 30:
                    created_tmp += 1

            finished = 0
            for time in finished_time:
                if time < timer and time > timer - 30:
                    finished += 1

            # avoid divided by zero
            if created_tmp == 0:
                throughput.append(0)
            else:
                throughput.append((finished / created_tmp) * 100)
            throughput2.append(finished / 30)

            if timer >= (test_finished):
                break
            else:
                timer += 30

        throughput_avg = round(statistics.mean(throughput), 2) if len(throughput) else 0
        throughput_max = round(max(throughput), 2) if len(throughput) else 0
        throughput2_avg = round(statistics.mean(throughput2), 2) if len(throughput2) else 0
        throughput2_max = round(max(throughput2), 2) if len(throughput2) else 0

        logger.critical('OVERALL:throughput (success only)---> ' + str(throughput_avg)
                        + '  (max= ' + str(throughput_max) + ')')
        logger.critical('OVERALL:throughput2 (success only)---> ' + str(throughput2_avg)
                        + '  (max= ' + str(throughput2_max) + ')')



        metrics["app_overall"] = {"created": created, "sent": {"sum": sent, "percent": sent_percent},
                                  "code200": {"sum": code200, "percent": success_rate},
                                  "code500": code500, "code502": code502, "code503": code503, "code-1": code_1,
                                  "others": others,
                                  "dropped": {"sum": dropped_sensors_sum, "percent": dropped_sensors_percent},
                                  "dropped_in_bootup": {"sum": dropped_sensors_in_boot_up_sum,
                                                        "percent": dropped_sensors_in_boot_percent},
                                
                                "dropped_sensors_no_host": {"sum": dropped_sensors_no_host_sum,
                                                        "percent": dropped_sensors_no_host_percent},
                                "dropped_sensors_func_host_down": {"sum": dropped_sensors_func_host_down_sum,
                                                        "percent": dropped_sensors_func_host_down_percent},
                                "dropped_sensors_func_local_host_down": {"sum": dropped_sensors_func_local_host_down_sum,
                                                        "percent": dropped_sensors_func_local_host_down_percent},
                                "dropped_sensors_hiccup": {"sum": dropped_sensors_hiccup_sum,
                                                        "percent": dropped_sensors_hiccup_percent},
                                "dropped_sensors_active_sensor": {"sum": dropped_sensors_active_sensor_sum,
                                                        "percent": dropped_sensors_active_sensor_percent},
                                  "admission_dur": {"avg": admission_duration_avg, "max": admission_duration_max},
                                  "queue_dur": {"avg": queuing_duration_avg, "max": queuing_duration_max},
                                  "exec_dur": {"avg": execution_duration_avg, "max": execution_duration_max},
                                  "round_trip_suc": {"avg": response_time_suc_avg, "max": response_time_suc_max},
                                  "round_trip_suc_fail": {"avg": response_time_suc_fail_avg,
                                                          "max": response_time_suc_fail_max},
                                  "useless_exec_dur": useless_execution_duration_sum,
                                  "percentiles_suc": {"p0": percentiles_suc[0], "p25": percentiles_suc[1],
                                                      "p50": percentiles_suc[2], "p75": percentiles_suc[3],
                                                      "p90": percentiles_suc[4], "p95": percentiles_suc[5],
                                                      "p99": percentiles_suc[6],
                                                      "p99.9": percentiles_suc[7], "p100": percentiles_suc[8]},
                                  "percentiles_suc_fail": {"p0": percentiles_suc_fail[0],
                                                           "p25": percentiles_suc_fail[1],
                                                           "p50": percentiles_suc_fail[2],
                                                           "p75": percentiles_suc_fail[3],
                                                           "p90": percentiles_suc_fail[4],
                                                           "p95": percentiles_suc_fail[5],
                                                           "p99": percentiles_suc_fail[6],
                                                           "p99.9": percentiles_suc_fail[7],
                                                           "p100": percentiles_suc_fail[8]},
                                    "executor_ips":{"hosts": {"ips": different_host_ips, "counter": host_ip_counter},
                                                    "pods": {"ips": different_pod_ips, "counter": pod_ip_counter}},
                                    "detected_objects": {"sum": detected_objects_sum,
                                                        "avg": detected_objects_avg,
                                                        "accuracy_avg": detected_objects_accuaracy_avg},
                                  "throughput2": {"avg": throughput2_avg, "max": throughput2_avg}}

        logger.critical('METRICS PER APP  ****************************')
        app_order = []

        # per app rt
        # how many apps?
        for app in apps:
            creation_time = []
            admission_duration = []
            queuing_duration = []
            execution_duration = []
            useless_execution_duration = []
            finished_time = []
            response_time_suc = []
            response_time_suc_fail = []
            #executor
            executor_host_ips = []
            executor_pod_ips = []
            #calculate detected objects
            detected_objects = []
            detected_objects_accuaracy = []

            reply = 0
            status = [0] * 6
            dropped_sensor = 0
            dropped_sensor_in_boot_up = 0
            dropped_sensor_no_host = 0
            dropped_sensor_func_host_down = 0
            dropped_sensor_func_local_host_down = 0
            dropped_sensor_hiccup = 0
            dropped_sensor_active_sensor = 0

            if app[1] == True:
                logger.critical('**************     ' + app[0] + '     **************')

                sent = 0

                for sensor in sensor_log.values():
                    # check function name
                    if sensor[0] == app[4]:
                        # dropped sensors are not considered in response time and replies
                        if sensor[7] != 449 and sensor[7] != 450 and sensor[7] != 451 and sensor[7] != 452 and sensor[7] != 453 and sensor[7] != 454 and sensor[7] != 455:

                            sent += 1

                            admission_duration.append(sensor[2])
                            reply += sensor[8]
                            if sensor[7] == 200:  # respoonse time only based on success tasks????weight of failed????
                                creation_time.append(sensor[1])
                                queuing_duration.append(sensor[3])
                                execution_duration.append(sensor[4])
                                finished_time.append(sensor[5])
                                response_time_suc.append(sensor[6])
                                response_time_suc_fail.append(sensor[6])
                                #executor
                                executor_host_ips.append(sensor[9])
                                executor_pod_ips.append(sensor[10])
                                #detections
                                detected_objects.extend(sensor[11])
                                detected_objects_accuaracy.extend(sensor[12])

                            else:
                                useless_execution_duration.append(sensor[4])
                                # app timeout = max exec time
                                func_info = app[8]
                                func_timeout = int(func_info[12].split('s')[0])
                                response_time_suc_fail.append(func_timeout)
                            # get status
                            if sensor[7] == 200:
                                status[0] += 1
                            elif sensor[7] == 500:
                                status[1] += 1
                            elif sensor[7] == 502:
                                status[2] += 1
                            elif sensor[7] == 503:
                                status[3] += 1
                            elif sensor[7] == -1:
                                status[4] += 1
                            else:  # others
                                status[5] += 1
                        # if dropped sensor
                        else:
                            if sensor[7] == 451:
                                dropped_sensor += 1
                            elif sensor[7] == 452:
                                dropped_sensor_in_boot_up += 1
                            elif sensor[7] == 453:
                                dropped_sensor_no_host +=1
                            elif sensor[7] == 454:
                                dropped_sensor_func_host_down += 1
                            elif sensor[7] == 455:
                                dropped_sensor_func_local_host_down += 1
                            elif sensor[7] == 450:
                                dropped_sensor_hiccup += 1
                            elif sensor[7] == 449:
                                dropped_sensor_active_sensor += 1
                            else:
                                logger.error('dropped sensor unknown')

                # calculate metrics of this app

                # OVERALL created recv by replies (actuators)
                created = app[6]
                recv = app[7]

                app_name = app[0]
                app_order.append(app_name)

                logger.critical('APP(' + app[4] + '): REQ. CREATED: ' + str(created)
                                + ' RECV (by apps): ' + str(recv) + ' RECV (by counter): ' + str(reply))
                sent_percent = round(sent / created * 100, ) if created > 0 else 0
                logger.critical('APP(' + app[4] + '): REQ. SENT: ' + str(sent) + ' (' + str(sent_percent) + ')')
                # status
                sum_s = sum([status[0], status[1], status[2], status[3], status[4], status[5]])
                success_rate = round(status[0] / sum_s * 100, 2) if sum_s > 0 else 0
                logger.critical("APP(" + app[4] + "): Success Rate (200/sent): {}%".format(success_rate))
                logger.critical("APP(" + app[4] + "): Success Rate (200/sent) new: {}%".format(
                    round(status[0] / sent * 100, 2) if sent > 0 else 0))
                logger.critical('APP(' + app[4] + '): {0}{1}{2}{3}{4}{5}'.format(
                    'CODE200=' + str(status[0]) if status[0] > 0 else ' ',
                    'CODE500=' + str(status[1]) if status[1] > 0 else ' ',
                    'CODE502=' + str(status[2]) if status[2] > 0 else ' ',
                    'CODE503=' + str(status[3]) if status[3] > 0 else ' ',
                    'CODE-1=' + str(status[4]) if status[4] > 0 else ' ',
                    'OTHERS=' + str(status[5]) if status[5] > 0 else ' '))
                #451
                dropped_sensor_sum = dropped_sensor
                dropped_sensor_percent = round((dropped_sensor / created) * 100, 2) if created > 0 else 0
                logger.critical("APP(" + app[4] + "): Dropped (created, not sent): {} - percent {}%".format(
                    dropped_sensor_sum, dropped_sensor_percent))
                #452
                dropped_sensor_in_boot_up_sum = dropped_sensor_in_boot_up
                dropped_sensor_in_boot_up_percent = round((dropped_sensor_in_boot_up_sum / created) * 100,
                                                          2) if created > 0 else 0
                logger.critical("APP(" + app[4] + "): Dropped inboot up(created, not sent): {} - percent {}%".
                                format(dropped_sensor_in_boot_up_sum, dropped_sensor_in_boot_up_percent))
                #453
                dropped_sensor_no_host_sum = dropped_sensor_no_host
                dropped_sensor_no_host_percent = round((dropped_sensor_no_host / created) * 100, 2) if created > 0 else 0
                logger.critical("APP(" + app[4] + "): dropped_sensor_no_host 453 (created, not sent): {} - percent {}%".format(
                    dropped_sensor_no_host_sum, dropped_sensor_no_host_percent))
                #454
                dropped_sensor_func_host_down_sum = dropped_sensor_func_host_down
                dropped_sensor_func_host_down_percent = round((dropped_sensor_func_host_down / created) * 100, 2) if created > 0 else 0
                logger.critical("APP(" + app[4] + "): dropped_sensor_func_host_down 454 (created, not sent): {} - percent {}%".format(
                    dropped_sensor_func_host_down_sum, dropped_sensor_func_host_down_percent))
                #455
                dropped_sensor_func_local_host_down_sum = dropped_sensor_func_local_host_down
                dropped_sensor_func_local_host_down_percent = round((dropped_sensor_func_local_host_down / created) * 100, 2) if created > 0 else 0
                logger.critical("APP(" + app[4] + "): dropped_sensor_func_local_host_down 455 (created, not sent): {} - percent {}%".format(
                    dropped_sensor_func_local_host_down_sum, dropped_sensor_func_local_host_down_percent))
                #450
                dropped_sensor_hiccup_sum = dropped_sensor_hiccup
                dropped_sensor_hiccup_percent = round((dropped_sensor_hiccup / created) * 100, 2) if created > 0 else 0
                logger.critical("APP(" + app[4] + "): dropped_sensor_hiccup 450 (created, not sent): {} - percent {}%".format(
                    dropped_sensor_hiccup_sum, dropped_sensor_hiccup_percent))
                #449
                dropped_sensor_active_sensor_sum = dropped_sensor_active_sensor
                dropped_sensor_active_sensor_percent = round((dropped_sensor_active_sensor / created) * 100, 2) if created > 0 else 0
                logger.critical("APP(" + app[4] + "): dropped_sensor_active_sensor 449 (created, not sent): {} - percent {}%".format(
                    dropped_sensor_active_sensor_sum, dropped_sensor_active_sensor_percent))

                
                # print per app: ???admission dur should only consider sent sensors, not createds
                admission_duration_avg = round(statistics.mean(admission_duration), 2) if len(admission_duration) else 0
                admission_duration_max = round(max(admission_duration), 2) if len(admission_duration) else 0
                queuing_duration_avg = round(statistics.mean(queuing_duration), 2) if len(queuing_duration) else 0
                queuing_duration_max = round(max(queuing_duration), 2) if len(queuing_duration) else 0
                execution_duration_avg = round(statistics.mean(execution_duration), 2) if len(execution_duration) else 0
                execution_duration_max = round(max(execution_duration), 2) if len(execution_duration) else 0
                response_time_suc_avg = round(statistics.mean(response_time_suc), 2) if len(response_time_suc) else 0
                response_time_suc_max = round(max(response_time_suc), 2) if len(response_time_suc) else 0
                response_time_suc_fail_avg = round(statistics.mean(response_time_suc_fail), 2) if len(
                    response_time_suc_fail) else 0
                response_time_suc_fail_max = round(max(response_time_suc_fail), 2) if len(response_time_suc_fail) else 0
                useless_execution_duration_avg = round(statistics.mean(useless_execution_duration), 2) if len(
                    useless_execution_duration) else 0

                logger.critical('APP(' + app[4] + '): Adm. Dur. (sent only): avg '
                                + str(admission_duration_avg) + ' --- max ' + str(admission_duration_max))

                logger.critical('APP(' + app[4] + '): Q. Dur. (success only): avg '
                                + str(queuing_duration_avg) + ' --- max ' + str(queuing_duration_max))
                logger.critical('APP(' + app[4] + '): Exec. +(scheduling) Dur. (success only): avg '
                                + str(execution_duration_avg) + ' --- max ' + str(execution_duration_max))
                logger.critical('APP(' + app[4] + '): RT (success only): avg '
                                + str(response_time_suc_avg) + ' --- max ' + str(response_time_suc_max))
                logger.critical('APP(' + app[4] + '): RT (success + fail): avg '
                                + str(response_time_suc_fail_avg) + ' --- max ' + str(response_time_suc_fail_max))
                logger.critical('APP(' + app[4] + '): Useless Exec. Dur.: sum '
                                + str(useless_execution_duration_avg))

                # Percentile
                percentiles_suc = (np.percentile(response_time_suc, [0, 25, 50, 75, 90, 95, 99, 99.9, 100]) if len(
                    response_time_suc) else [0, 0, 0, 0, 0, 0, 0, 0, 0])
                percentiles_suc = ([round(num, 3) for num in percentiles_suc])
                percentiles_suc_fail = (
                    np.percentile(response_time_suc_fail, [0, 25, 50, 75, 90, 95, 99, 99.9, 100]) if len(
                        response_time_suc_fail) else [0, 0, 0, 0, 0, 0, 0, 0, 0])
                percentiles_suc_fail = ([round(num, 3) for num in percentiles_suc_fail])
                logger.critical('APP(' + app[4] + '): Percentiles (success + fail): '
                                + str(percentiles_suc_fail))

                #executors
                #host
                #get a copy of all involved ips
                different_host_ips=list(set(executor_host_ips))
                #prepaer a counter associated to the ips in the obtained list
                host_ip_counter=[0]*len(different_host_ips)
                #search for the number of repetitions of each ip
                for ip_index in range(len(different_host_ips)):
                    host_ip_counter[ip_index] = executor_host_ips.count(different_host_ips[ip_index])

                #pod
                #get a copy of all involved ips
                different_pod_ips=list(set(executor_pod_ips))
                #prepaer a counter associated to the ips in the obtained list
                pod_ip_counter=[0]*len(different_pod_ips)
                #search for the number of repetitions of each ip
                for ip_index in range(len(different_pod_ips)):
                    pod_ip_counter[ip_index] = executor_pod_ips.count(different_pod_ips[ip_index])

                #print
                logger.critical('APP(' + app[4] + ') executor hosts\n' + 
                    str([str(different_host_ips[ip_index]) + '=' + str(host_ip_counter[ip_index]) for ip_index in range(len(different_host_ips))]))
                logger.critical('APP(' + app[4] + ') executor pods\n' + 
                    str([str(different_pod_ips[ip_index]) + '=' + str(pod_ip_counter[ip_index]) for ip_index in range(len(different_pod_ips))]))

                
                #object detection
                detected_objects_sum = len(detected_objects)
                #assumed len detected_objects == len response_time_sec??
                detected_objects_avg = round(len(detected_objects) / len(response_time_suc), 2) if len(response_time_suc) and len(detected_objects) else 0
                detected_objects_accuaracy_avg = round(statistics.mean(detected_objects_accuaracy), 2) if len(detected_objects_accuaracy) else 0
                logger.critical('APP(' + app[4] + ') avg. Obj. Detection (success only) ---> sum obj= ' + str(detected_objects_sum)
                        + ',  avg= ' + str(detected_objects_avg) 
                        + ', accuracy= ' + str(detected_objects_accuaracy_avg))
                # System Throughput (every 30sec)
                throughput = []
                throughput2 = []
                timer = test_started + 30

                while True:
                    created_tmp = 0
                    for time in creation_time:
                        if time < timer and time > timer - 30:
                            created_tmp += 1

                    finished = 0
                    for time in finished_time:
                        if time < timer and time > timer - 30:
                            finished += 1

                    # avoid divided by zero
                    if created_tmp == 0:
                        throughput.append(0)
                    else:
                        throughput.append((finished / created_tmp) * 100)
                    throughput2.append(finished / 30)

                    if timer >= (test_finished):
                        break
                    else:
                        timer += 30

                throughput_avg = round(statistics.mean(throughput), 2) if len(throughput) else 0
                throughput_max = round(max(throughput), 2) if len(throughput) else 0
                throughput2_avg = round(statistics.mean(throughput2), 2) if len(throughput2) else 0
                throughput2_max = round(max(throughput2), 2) if len(throughput2) else 0

                logger.critical('APP(' + app[4] + '):throughput (success only) avg '
                                + str(throughput_avg) + ' --- max ' + str(throughput_max))

                logger.critical('APP(' + app[4] + '): throughput2 (success only) avg '
                                + str(throughput2_avg) + ' --- max' + str(throughput2_max))



                metrics[app_name] = {"created": created, "sent": {"sum": sent, "percent": sent_percent},
                                     "code200": {"sum": status[0], "percent": success_rate},
                                     "code500": status[1], "code502": status[2], "code503": status[3],
                                     "code-1": status[4], "others": status[5],
                                     "dropped": {"sum": dropped_sensor_sum, "percent": dropped_sensor_percent},
                                     "dropped_in_bootup": {"sum": dropped_sensor_in_boot_up_sum,
                                                           "percent": dropped_sensor_in_boot_up_percent},
                                    "dropped_sensors_no_host": {"sum": dropped_sensor_no_host_sum, "percent": dropped_sensor_no_host_percent},
                                    "dropped_sensors_func_host_down": {"sum": dropped_sensor_func_host_down_sum, "percent": dropped_sensor_func_host_down_percent},
                                    "dropped_sensors_func_local_host_down": {"sum": dropped_sensor_func_local_host_down_sum, "percent": dropped_sensor_func_local_host_down_percent},
                                    "dropped_sensors_hiccup": {"sum": dropped_sensor_hiccup_sum, "percent": dropped_sensor_hiccup_percent},
                                    "dropped_sensors_active_sensor": {"sum": dropped_sensor_active_sensor_sum, "percent": dropped_sensor_active_sensor_percent},
                                     "admission_dur": {"avg": admission_duration_avg, "max": admission_duration_max},
                                     "queue_dur": {"avg": queuing_duration_avg, "max": queuing_duration_max},
                                     "exec_dur": {"avg": execution_duration_avg, "max": execution_duration_max},
                                     "round_trip_suc": {"avg": response_time_suc_avg, "max": response_time_suc_max},
                                     "round_trip_suc_fail": {"avg": response_time_suc_fail_avg,
                                                             "max": response_time_suc_fail_max},
                                     "useless_exec_dur": useless_execution_duration_avg,
                                     "percentiles_suc": {"p0": percentiles_suc[0], "p25": percentiles_suc[1],
                                                         "p50": percentiles_suc[2], "p75": percentiles_suc[3],
                                                         "p90": percentiles_suc[4], "p95": percentiles_suc[5],
                                                         "p99": percentiles_suc[6],
                                                         "p99.9": percentiles_suc[7], "p100": percentiles_suc[8]},
                                     "percentiles_suc_fail": {"p0": percentiles_suc_fail[0],
                                                              "p25": percentiles_suc_fail[1],
                                                              "p50": percentiles_suc_fail[2],
                                                              "p75": percentiles_suc_fail[3],
                                                              "p90": percentiles_suc_fail[4],
                                                              "p95": percentiles_suc_fail[5],
                                                              "p99": percentiles_suc_fail[6],
                                                              "p99.9": percentiles_suc_fail[7],
                                                              "p100": percentiles_suc_fail[8]},
                                    "executor_ips":{"hosts": {"ips": different_host_ips, "counter": host_ip_counter},
                                                    "pods": {"ips": different_pod_ips, "counter": pod_ip_counter}},
                                    "detected_objects": {"sum": detected_objects_sum,
                                                        "avg": detected_objects_avg,
                                                        "accuracy_avg": detected_objects_accuaracy_avg},
                                     "throughput2": {"avg": throughput2_avg, "max": throughput2_max}}

        # end per app
        if len(app_order):
            app_order.insert(0, 'app_overall')
        metrics["app_order"] = app_order

    # scheduler logs
    rescheduled_sum = 0
    if node_role == "MASTER":
        # scheduler logs
        rescheduled_sum = 0
        rescheduled_per_worker = [0] * len(workers)
        rescheduled_per_func = [0] * len(functions)

        for function in functions:
            versions = int(function[2][16])
            # sum
            rescheduled_sum += versions
            # per worker
            index = 0
            for worker in workers:
                if worker[0] == function[0][0]:
                    index = workers.index(worker)
                    break
            rescheduled_per_worker[index] += versions
            # per functions
            rescheduled_per_func[functions.index(function)] += versions
        # print
        logger.critical('Scheduler Logs:\n rescheduling: \n '
                        + 'Sum: ' + str(rescheduled_sum)
                        + '\nPer Worker: ' + ' -- '.join([str(str(workers[index][0]) + ': '
                                                              + str(rescheduled_per_worker[index])) for index in
                                                          range(len(rescheduled_per_worker))])
                        + '\nPer Function: ' + '\n'.join([str(str(functions[index][0][0]) + '-'
                                                              + str(functions[index][0][1]) + ': '
                                                              + str(rescheduled_per_func[index])) for index in
                                                          range(len(rescheduled_per_func))]))

        per_worker = {workers[index][0]: rescheduled_per_worker[index] for index in
                      range(len(rescheduled_per_worker))}
        logger.info(per_worker)

        per_function = {functions[index][0][0] + '-' + functions[index][0][1]:
                            rescheduled_per_func[index] for index in range(len(rescheduled_per_func))}
        # down per scheduling iterations
        down_counter = {worker[0]: 0 for worker in workers}
        # per scheduling_round
        for nodes in history["workers"]:
        #???
        # for key, value in history["workers"].items():
        #     scheudling_round = key
        #     nodes = value
            # evaluate all nodes SoC one at a time
            for node in nodes:
                soc = node[2]
                min_battery_charge = battery_cfg[8]
                # if node is down, increment its down_counter
                if soc < min_battery_charge:
                    name = node[0]
                    down_counter[name] += 1

        metrics["scheduler"] = {"placements": {"sum": rescheduled_sum,
                                               "workers": per_worker,
                                               "functions": per_function},
                                "down_counter": down_counter}

        logger.info(metrics["scheduler"])

        # save scheduler history to file
        with open(log_path + "/functions.txt", "w") as f:
            json.dump({"functions": history["functions"]}, f, indent=4, ensure_ascii=False, sort_keys=True)
        with open(log_path + "/workers.txt", "w") as w:
            json.dump({"workers": history["workers"]}, w, indent=4, ensure_ascii=False, sort_keys=True)
        # to read
        # functions = json.load(open(log_path + "/functions.txt", "r"))
        # workers = json.load(open(log_path + "/workers.txt", "r"))

        #load_balancer report
        
        #save history as json
        import jsonpickle
        with open(log_path + "/history.txt", "w") as f:
            json.dump(jsonpickle.encode(history), f, indent=4, ensure_ascii=False, sort_keys=True)

    # else any role

    log_index = log_path + "/" + node_name + "-monitor.csv"
    labels = ['time1', 'time2', 'rt_acc', 'node_op', 'battery', 'cpu_util', 'memory', 'disk',
              'cpu_temp', 'cpu_freq_curr', 'cpu_freq_min', 'cpu_freq_max', 'cpu_ctx_swt', 'cpu_inter', 'cpu_soft_inter',
              'io_read_count', 'io_write_count', 'io_read_bytes', 'io_write_bytes',
              'bw_pack_sent', 'bw_pack_rec', 'bw_bytes_sent', 'bw_bytes_rec', 'bw_bytes_dropin', 'bw_bytes_dropout']
    if usb_meter_involved:
        labels.extend(['mwh_new', 'mwh', 'mah', 'watts', 'amps', 'volts', 'temp'])

    monitor_data = []
    monitor_data.append(labels)
    # mwh (energy consumption)
    mwh_sum = 0
    mwh_first = power_usage[0][0]
    mwh_second = 0

    #watts (power consumption)

    # bw
    bw_usage_sum = [0] * len(bw_usage[0])
    bw_usage_first = bw_usage[0]
    bw_usage_second = [0] * len(bw_usage[0])
    if len(cpuUtil) != len(power_usage):
        logger.error('len (cpuUtil)= ' + str(len(cpuUtil)) + ' len (power_usage)= ' + str(len(power_usage)))

    for i in range(len(cpuUtil)):
        curr_list = []
        curr_list.append(str(current_time[i]))
        curr_list.append(str(current_time_ts[i]))
        curr_list.append(str(response_time_accumulative[i]))
        # ???Throughput accumulative
        curr_list.append(str(node_op[i]))
        curr_list.append(str(battery_charge[i]))
        curr_list.append(str(cpuUtil[i]))
        curr_list.append(str(memory[i]))
        curr_list.append(str(disk_usage[i]))
        curr_list.append(str(cpu_temp[i]))
        curr_list.append(str(cpu_freq_curr[i]))
        curr_list.append(str(cpu_freq_min[i]))
        curr_list.append(str(cpu_freq_max[i]))
        curr_list.append(str(cpu_ctx_swt[i]))
        curr_list.append(str(cpu_inter[i]))
        curr_list.append(str(cpu_soft_inter[i]))
        curr_list.append(str(disk_io_usage[i][0]))
        curr_list.append(str(disk_io_usage[i][1]))
        curr_list.append(str(disk_io_usage[i][2]))
        curr_list.append(str(disk_io_usage[i][3]))
        # bw usage new
        if i > 0:
            bw_usage_second = bw_usage[i]
            usage = [bw_usage_second[index] - bw_usage_first[index] for index in range(len(bw_usage[0]))]

            bw_usage_sum = [bw_usage_sum[index] + usage[index] for index in range(len(bw_usage[0]))]
            # exchange
            bw_usage_first = bw_usage_second

        curr_list.append(str(bw_usage_sum[0]))
        curr_list.append(str(bw_usage_sum[1]))
        curr_list.append(str(bw_usage_sum[2]))
        curr_list.append(str(bw_usage_sum[3]))
        curr_list.append(str(bw_usage_sum[4]))
        curr_list.append(str(bw_usage_sum[5]))

        if usb_meter_involved:
            # sometimes len power_usage is 1 index shorter than others ???
            if i < len(power_usage):
                # power usage new
                if i > 0:
                    # mwh
                    mwh_second = power_usage[i][0]
                    usage = mwh_second - mwh_first
                    if usage < 0:  # loop point
                        usage = (99999 - mwh_first) + (mwh_second - 97222)

                    mwh_sum += usage
                    # exchange
                    mwh_first = mwh_second

                curr_list.append(str(mwh_sum))

                curr_list.append(str(power_usage[i][0]))
                curr_list.append(str(power_usage[i][1]))
                curr_list.append(str(power_usage[i][2]))
                curr_list.append(str(power_usage[i][3]))
                curr_list.append(str(power_usage[i][4]))
                curr_list.append(str(power_usage[i][5]))
            else:
                logger.warning('save_reports: power_usage shorter than cpuUtil')
                curr_list.append(str(mwh_sum))

                curr_list.append(str(power_usage[i - 1][0]))
                curr_list.append(str(power_usage[i - 1][1]))
                curr_list.append(str(power_usage[i - 1][2]))
                curr_list.append(str(power_usage[i - 1][3]))
                curr_list.append(str(power_usage[i - 1][4]))
                curr_list.append(str(power_usage[i - 1][5]))


        monitor_data.append(curr_list)
    # save monitor.csv
    np.savetxt(log_index, monitor_data, delimiter=",", fmt="%s")

    logger.critical('Save_Reports: ' + log_index)


    #battery_history.csv

    log_index = log_path + "/" + node_name + "-battery_history.csv"
    labels = ['battery_time1', 'battery_time2', 'soc', 'soc_unlimited', 'battery_excess_input', 'renewable_input', 'energy_usage', 'min_battery_charge',
              'max_battery_charge', 
              'failed_status', 'failed_last_start', 'failed_total_duration', 'failed_switch_to_state_counter',
              'pending_status', 'pending_last_start', 'pending_total_duration', 'pending_switch_to_state_counter',
              'running_status', 'running_last_start', 'running_total_duration', 'running_switch_to_state_counter']

    battery_history_data = []
    battery_history_data.append(labels)

    for record in battery_history:
        #each record collected every x interval by battery_sim, like 10s
        #DELETED
        # data = [record['battery_time1'], 
        #                 record['battery_time2'], 
        #                 record['soc'], 
        #                 record['soc_unlimited'], 
        #                 record['battery_excess_input'], 
        #                 record['renewable_input'], 
        #                 record['energy_usage'], 
        #                 record['min_battery_charge'],
        #                 record['max_battery_charge'], 
        #                 record['status']]
        #ADDED
        data = [record['battery_time1'], 
                        record['battery_time2'], 
                        record['soc'], 
                        record['soc_unlimited'], 
                        record['battery_excess_input'], 
                        record['renewable_input'], 
                        record['energy_usage'], 
                        record['min_battery_charge'],
                        record['max_battery_charge'], 
                        record['status']['failed']['status'],
                        record['status']['failed']['last_start'],
                        record['status']['failed']['total_duration'],
                        record['status']['failed']['switch_to_state_counter'],
                        record['status']['pending']['status'],
                        record['status']['pending']['last_start'],
                        record['status']['pending']['total_duration'],
                        record['status']['pending']['switch_to_state_counter'],
                        record['status']['running']['status'],
                        record['status']['running']['last_start'],
                        record['status']['running']['total_duration'],
                        record['status']['running']['switch_to_state_counter'],]
        #add record to data
        battery_history_data.append(data)

    # save battery_history.csv
    np.savetxt(log_index, battery_history_data, delimiter=",", fmt="%s")

    #remove labels form list
    del battery_history_data[0]

    logger.critical('Save_Reports: ' + log_index)



    if len(response_time) == 0: response_time.append(1)
    logger.critical('METRICS********************')
    logger.critical('######Exec. time (only success) avg='
                    + str(round(sum(response_time) / len(response_time), 2)))
    logger.critical('######Exec. time (only success) accumulative= '
                    + str(sum(response_time_accumulative) / len(response_time_accumulative)))
    cpuUtil_avg = round(statistics.mean(cpuUtil), 2)
    cpuUtil_max = round(max(cpuUtil), 2)
    logger.critical('######cpu= '
                    + str(round(sum(cpuUtil) / len(cpuUtil), 2)) + ' max=' + str(max(cpuUtil)))
    cpuFreq_avg = round(statistics.mean(cpu_freq_curr), 2)

    cpuFreq_min = min(cpu_freq_curr)
    cpuFreq_max = max(cpu_freq_curr)
    logger.critical('######cpuFreq= '
                    + str(cpuFreq_avg)
                    + '  min=' + str(cpuFreq_min)
                    + '  max=' + str(cpuFreq_max))
    min_battery_charge_percent = (battery_cfg[8] / battery_cfg[1]) * 100
    cpuUtil_up = [cpuUtil[i] for i in range(len(cpuUtil)) if battery_charge[i] >= min_battery_charge_percent]
    cpuUtil_up_avg = round(statistics.mean(cpuUtil_up), 2) if len(cpuUtil_up) else 0
    cpuUtil_up_max = round(max(cpuUtil_up), 2) if len(cpuUtil_up) else 0
    logger.critical('######cpu (up)= '
                    + str(round(sum(cpuUtil_up) / len(cpuUtil_up), 2) if cpuUtil_up != [] else 0)
                    + ' max=' + str(max(cpuUtil_up) if cpuUtil_up != [] else 0))

    memory_avg = round(statistics.mean(memory), 2) if len(memory) else 0
    memory_max = round(max(memory), 2) if len(memory) else 0
    logger.critical('######memory=' + str(round(sum(memory) / len(memory), 2))
                    + ' max=' + str(max(memory)))

    logger.critical('######disk_io_usage_Kbyte_read= '
                    + str(round((disk_io_usage[-1][2] - disk_io_usage[0][2]) / 1024, 2)))
    logger.critical('######disk_io_usage_Kbyte_write= '
                    + str(round((disk_io_usage[-1][3] - disk_io_usage[0][3]) / 1024, 2)))
    # logger.critical('######bw_packet_sent=' + str(round(bw_usage[-1][0] - bw_usage[0][0],2)))
    # logger.critical('######bw_packet_recv=' + str(round(bw_usage[-1][1]- bw_usage[0][1],2)))
    logger.critical('######bw_Kbytes_sent= '
                    + str(round((bw_usage[-1][2] - bw_usage[0][2]) / 1024, 2)))
    logger.critical('######bw_Kbytes_recv= '
                    + str(round((bw_usage[-1][3] - bw_usage[0][3]) / 1024, 2)))
    # power usage
    power_usage_incremental = mwh_sum
    # remover?
    mwh_sum = 0
    mwh_first = power_usage[0][0]
    mwh_second = 0
    usage = 0
    for row in power_usage[1:]:
        mwh_second = row[0]
        usage = mwh_second - mwh_first
        if usage < 0:  # loop point
            usage = (99999 - mwh_first) + (mwh_second - 97222)

        mwh_sum += usage
        # exchange
        mwh_first = mwh_second

    logger.critical('######monitor_power_usage= '
                    + str(mwh_sum) + ' mWh --- inc. (' + str(power_usage_incremental) + ')')


    #battery_charge_avg %
    battery_charge_avg = round(sum(battery_charge) / len(battery_charge), 2)

    #battery_charge_min %
    battery_charge_min = round( min(battery_charge),2)

    #battery_charge_max %
    battery_charge_max = round(max(battery_charge),2)
    
    logger.critical('######monitor_battery_charge avg=' + str(battery_charge_avg) + ' %  min=' + str(battery_charge_min) + ' %  max=' + str(battery_charge_max))

    # down_time
    down_time_minute = 0
    down_time_percent = 0
    if battery_cfg[0] == True:
        test_duration = test_finished - test_started
        logger.info('test_duration= ' + str(round(test_duration)) + ' sec ('
                    + str(round(test_duration / 60)) + ' min)')
        down_time_minute = round((down_time) / 60, 2)
        down_time_percent = round(down_time / test_duration * 100, 0)
        logger.critical('######down_time= ' + str(down_time_minute)
                        + ' min  (=' + str(down_time_percent) + ' %)')

    #battery
    try:
        #list of battery data per metric
        battery_soc_list = [data[2] for data in battery_history_data] if battery_cfg[0] ==  True else []
        battery_soc_unlimited_list = [data[3] for data in battery_history_data] if battery_cfg[0] ==  True else []
        battery_excess_input_list = [data[4] for data in battery_history_data] if battery_cfg[0] ==  True else []
        battery_renewable_input_list = [data[5] for data in battery_history_data] if battery_cfg[0] ==  True else []
        battery_energy_usage_list = [data[6] for data in battery_history_data] if battery_cfg[0] ==  True else []
        #DELETED
        # battery_status_list = [data[9] for data in battery_history_data] if battery_cfg[0] ==  True else []
        #ADDED

        #failed status
        #number of times battery reported node in the status
        battery_status_failed_list = [data[9] for data in battery_history_data] if battery_cfg[0] ==  True else []
        #percent
        battery_status_failed_percent = round(len([status for status in battery_status_failed_list if status == 1]) / len(battery_status_failed_list) * 100, 2)  if battery_cfg[0] ==  True and len(battery_status_failed_list) > 0 else -1
        #longest time durtion node stayed in this state. Get list of values. Check the largest difference between two consecutive values
        battery_status_failed_last_start_list = [data[10] for data in battery_history_data if data[10] != 0 and data[10] != None] if battery_cfg[0] ==  True else []

        #total duration node has been in this state. get last value in the list
        battery_status_failed_total_duration = [data[11] for data in battery_history_data][-1] if battery_cfg[0] ==  True else 0

        #pick the longest time the duration has been incrementing
        battery_status_failed_longest_duration = 0
        current_longest = 0
        
        battery_status_failed_duration_list = [data[11] for data in battery_history_data] if battery_cfg[0] ==  True else []
        if len(battery_status_failed_duration_list):
            for i in range(1, len(battery_status_failed_duration_list)):
                if battery_status_failed_duration_list[i] > battery_status_failed_duration_list[i-1]:
                    current_longest += battery_status_failed_duration_list[i] - battery_status_failed_duration_list[i-1]
                else:
                    if current_longest > battery_status_failed_longest_duration:
                        battery_status_failed_longest_duration = current_longest
                    current_longest = 0              
        #if not update has been done on the battery_status_failed_longest_duration, pick the latest value of current_longest      
        if battery_status_failed_longest_duration == 0:
            battery_status_failed_longest_duration = current_longest
        
        #total number of times node switched to this state. get last value in the list
        battery_status_failed_switch_to_state_counter = [data[12] for data in battery_history_data][-1] if battery_cfg[0] ==  True else 0

        #pending status
        #number of times battery reported node in the status
        battery_status_pending_list = [data[13] for data in battery_history_data] if battery_cfg[0] ==  True else []
        #percent
        battery_status_pending_percent = round(len([status for status in battery_status_pending_list if status == 1]) / len(battery_status_pending_list) * 100, 2)  if battery_cfg[0] ==  True and len(battery_status_pending_list) > 0 else -1
        #longest time durtion node stayed in this state. Get list of values. Check the largest difference between two consecutive values
        battery_status_pending_last_start_list = [data[14] for data in battery_history_data if data[14] != 0 and data[14] != None ] if battery_cfg[0] ==  True else []

        #pick the longest time the duration has been incrementing
        battery_status_pending_longest_duration = 0
        current_longest = 0
        
        battery_status_pending_duration_list = [data[15] for data in battery_history_data] if battery_cfg[0] ==  True else []
        if len(battery_status_pending_duration_list):
            for i in range(1, len(battery_status_pending_duration_list)):
                if battery_status_pending_duration_list[i] > battery_status_pending_duration_list[i-1]:
                    current_longest += battery_status_pending_duration_list[i] - battery_status_pending_duration_list[i-1]
                else:
                    if current_longest > battery_status_pending_longest_duration:
                        battery_status_pending_longest_duration = current_longest
                    current_longest = 0
        #if not update has been done on the battery_status_pending_longest_duration, pick the latest value of current_longest      
        if battery_status_pending_longest_duration == 0:
            battery_status_pending_longest_duration = current_longest

        #total duration node has been in this state. get last value in the list
        battery_status_pending_total_duration = [data[15] for data in battery_history_data][-1] if battery_cfg[0] ==  True else 0
        #total number of times node switched to this state. get last value in the list
        battery_status_pending_switch_to_state_counter = [data[16] for data in battery_history_data][-1] if battery_cfg[0] ==  True else 0

        #running status
        #number of times battery reported node in the status
        battery_status_running_list = [data[17] for data in battery_history_data] if battery_cfg[0] ==  True else []
        #percent
        battery_status_running_percent = round(len([status for status in battery_status_running_list if status == 1]) / len(battery_status_running_list) * 100, 2)  if battery_cfg[0] ==  True and len(battery_status_running_list) > 0 else -1
        #longest time durtion node stayed in this state. Get list of values. Check the largest difference between two consecutive values
        battery_status_running_last_start_list = [data[18] for data in battery_history_data if data[18] != 0 and data[18] != None] if battery_cfg[0] ==  True else []
        
        #pick the longest time the duration has been incrementing
        battery_status_running_longest_duration = 0
        current_longest = 0
        
        battery_status_running_duration_list = [data[19] for data in battery_history_data] if battery_cfg[0] ==  True else []
        if len(battery_status_running_duration_list):
            for i in range(1, len(battery_status_running_duration_list)):
                if battery_status_running_duration_list[i] > battery_status_running_duration_list[i-1]:
                    current_longest += battery_status_running_duration_list[i] - battery_status_running_duration_list[i-1]
                else:
                    if current_longest > battery_status_running_longest_duration:
                        battery_status_running_longest_duration = current_longest
                    current_longest = 0
        #if not update has been done on the battery_status_running_longest_duration, pick the latest value of current_longest      
        if battery_status_running_longest_duration == 0:
            battery_status_running_longest_duration = current_longest

        #total duration node has been in this state. get last value in the list
        battery_status_running_total_duration = [data[19] for data in battery_history_data][-1] if battery_cfg[0] ==  True else 0
        #total number of times node switched to this state. get last value in the list
        battery_status_running_switch_to_state_counter = [data[20] for data in battery_history_data][-1] if battery_cfg[0] ==  True else 0

        # battery_status_pending_list = [data[10] for data in battery_history_data] if battery_cfg[0] ==  True else []
        # battery_status_running_list = [data[11] for data in battery_history_data] if battery_cfg[0] ==  True else []
        #avg max min

        battery_soc_avg = round(sum(battery_soc_list) / len(battery_soc_list) ,2) if battery_cfg[0] ==  True and len(battery_soc_list) > 0 else -1
        battery_soc_max = round( max(battery_soc_list),2) if battery_cfg[0] ==  True and len(battery_soc_list) > 0 else -1
        battery_soc_min = round( min(battery_soc_list),2)  if battery_cfg[0] ==  True and len(battery_soc_list) > 0 else -1
        logger.critical('######battery_charge avg mwh=' + str(battery_soc_avg) + '  min=' + str(battery_soc_min) + '  max=' + str(battery_soc_max))

        battery_soc_unlimited_avg = round(sum(battery_soc_unlimited_list) / len(battery_soc_unlimited_list) ,2)  if battery_cfg[0] ==  True and len(battery_soc_unlimited_list) > 0 else -1
        battery_soc_unlimited_max = round( max(battery_soc_unlimited_list),2) if battery_cfg[0] ==  True and len(battery_soc_unlimited_list) > 0 else -1
        battery_soc_unlimited_min = round( min(battery_soc_unlimited_list),2) if battery_cfg[0] ==  True and len(battery_soc_unlimited_list) > 0 else -1
        logger.critical('######battery_charge_unlimited mwh avg=' + str(battery_soc_unlimited_avg) + '  min=' + str(battery_soc_unlimited_min) + ' max=' + str(battery_soc_unlimited_max))

        battery_excess_input_sum = round(sum(battery_excess_input_list),2) if battery_cfg[0] ==  True and len(battery_excess_input_list) > 0 else -1
        logger.critical('######battery_excess_input_sum mwh=' + str(battery_excess_input_sum))

        battery_renewable_input_sum = round(sum(battery_renewable_input_list), 2)  if battery_cfg[0] ==  True and len(battery_renewable_input_list) > 0 else -1
        logger.critical('######battery_renewable_input_sum mwh=' + str(battery_renewable_input_sum))

        battery_energy_usage_sum = round(sum(battery_energy_usage_list),2) if battery_cfg[0] ==  True and len(battery_energy_usage_list) > 0 else -1
        logger.critical('######battery_energy_usage_sum mwh=' + str(battery_energy_usage_sum))
        #DELETED
        # battery_status_up_percent = round(len([status for status in battery_status_list if status == 1]) / len(battery_status_list) * 100, 2)  if battery_cfg[0] ==  True and len(battery_status_list) > 0 else -1
        # battery_status_down_percent = round(len([status for status in battery_status_list if status == 0]) / len(battery_status_list) * 100, 2) if battery_cfg[0] ==  True and len(battery_status_list) > 0 else -1
        # logger.critical('######battery_status_up_percent %=' + str(battery_status_up_percent))
        # logger.critical('######battery_status_down_percent %=' + str(battery_status_down_percent))
        #ADDED
        
        
        #DELETED
        # "battery_status_up_percent": battery_status_up_percent,
        # "battery_status_down_percent": battery_status_down_percent,
        #ADDED
        # "battery_status_failed_percent": battery_status_failed_percent,
        # "battery_status_pending_percent": battery_status_pending_percent,
        # "battery_status_running_percent": battery_status_running_percent,
        # metrics
        metrics["node"] = {"role": node_role, "name": node_name, "ip": node_IP,
                        "battery_soc_avg": battery_soc_avg,
                        "battery_soc_max": battery_soc_max,
                        "battery_soc_min": battery_soc_min,
                        "battery_soc_unlimited_avg": battery_soc_unlimited_avg,
                        "battery_soc_unlimited_max": battery_soc_unlimited_max,
                        "battery_soc_unlimited_min": battery_soc_unlimited_min,
                        "battery_excess_input_sum": battery_excess_input_sum,
                        "battery_renewable_input_sum": battery_renewable_input_sum,
                        "battery_energy_usage_sum": battery_energy_usage_sum,
                        "battery_status_failed_percent": battery_status_failed_percent,
                        "battery_status_failed_longest_duration": battery_status_failed_longest_duration,
                        "battery_status_failed_total_duration": battery_status_failed_total_duration,
                        "battery_status_failed_switch_to_state_counter": battery_status_failed_switch_to_state_counter,
                        "battery_status_pending_percent": battery_status_pending_percent,
                        "battery_status_pending_longest_duration": battery_status_pending_longest_duration,
                        "battery_status_pending_total_duration": battery_status_pending_total_duration,
                        "battery_status_pending_switch_to_state_counter": battery_status_pending_switch_to_state_counter,
                        "battery_status_running_percent": battery_status_running_percent,
                        "battery_status_running_longest_duration": battery_status_running_longest_duration,
                        "battery_status_running_total_duration": battery_status_running_total_duration,
                        "battery_status_running_switch_to_state_counter": battery_status_running_switch_to_state_counter,
                        "power_usage_incremental": power_usage_incremental,
                        "down_time": {"minute": down_time_minute, "percent": down_time_percent},
                        "replacements": rescheduled_sum,
                        "cpu_usage": {"avg": cpuUtil_avg, "max": cpuUtil_max},
                        "cpu_usage_up": {"avg": cpuUtil_up_avg, "max": cpuUtil_up_max},
                        "cpuFreq": {"avg": cpuFreq_avg, "min": cpuFreq_min, "max": cpuFreq_max},
                        "memory_usage": {"avg": memory_avg, "max": memory_max},
                        "bw_usage": {"sent_mb": round(bw_usage_sum[2] / 1024 / 1024),
                                        "recv_mb": round(bw_usage_sum[3] / 1024 / 1024)}}




        # save metrics
        with open(log_path + "/metrics.txt", "w") as m:
            json.dump(metrics, m, indent=8)

        # writing metrics to excel
        if node_role == 'LOAD_GENERATOR':
            # send to master
            metrics_sender(metrics)
        elif node_role == 'MASTER':
            # write locally using metrics_writer()
            cmd = 'metrics'
            sender = 'internal'
            main_handler(cmd, sender)
        else:
            logger.warning('skip metrics_sender()')
    except Exception as e:
        logger.exception(f'metrics_\n{e}')
    #reboot node


# from retrying import retry
# @retry(wait_fixed=1000, stop_max_attempt_number=3)
# def make_request(url, json_data, timeout):
#     response = requests.post(url=url, json= json_data, timeout=timeout)
#     response.raise_for_status()
#     return response

def metrics_sender(metrics):
    global logger
    global load_balancing
    global node_name
    global internal_session
    logger.info('metrics_sender: start')
    counter = 3
    while counter > 0:
        counter -= 1
        try:
            # to avoid multiple write operations on a single file
            # time.sleep(random.randint(1,3))
            # specific to node name pattern of string+digits ????
            node_id = [i for i in node_name if i.isdigit()]
            node_id = int(''.join(node_id))

            time.sleep(node_id * 3)
            # time.sleep(int(node_name.split('w')[1]) * 3)

            admin_ip = load_balancing['admin']['ip']
            sender = node_name
            
            url = 'http://' + admin_ip + ':5000/main_handler/metrics/' + sender
            json_data = metrics
            timeout = 10
            # response = make_request(url, json_data, timeout)
            response = internal_session.post('http://' + admin_ip + ':5000/main_handler/metrics/' + sender, json=metrics, timeout=60)
            # response = requests.post('http://' + admin_ip + ':5000/main_handler/metrics/' + sender, json=metrics, timeout=10)
            # response.close()

        except Exception as e:
            logger.exception('metrics_sender: exception:' + str(e))
            logger.info('metrics_sender: sleep')

            net_interface_manager_restart()

            time.sleep(random.randint(1, 3))
        # if no exception
        else:
            if response.text == "success" or response.text == "repeat-skipped":
                logger.info(f'metrics_sender: {response.text}')
                break
            else:
                logger.error('metrics_sender: failed. sleep...')
                time.sleep(random.randint(1, 3))
                logger.info('metrics_sender: retry')




#net_interface_manager_restart
def net_interface_manager_restart():
    logger.info('xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx')
    #restart network interfaces
    # cmd = "sudo ifdown --exclude=lo -a -v && sudo ifup --exclude=lo -a -v"
    # logger.info('restart network interfaces: ' + cmd)
    # out, error = utils.shell(cmd)
    # logger.info(f'out={out} error={error}')
    time.sleep(1)
    #restart network manager !!!This causes nodes to not be responsive anymoe
    # cmd = "sudo systemctl restart NetworkManager.service"
    # logger.info('restart network manager: ' + cmd)
    # out, error = utils.shell(cmd)
    # logger.info(f'out={out} error={error}')
    # logger.info('restarts done')
    return None

# #close connections after request to avoid close-wait connecitons
# import functools
# def close_socket_after_request(f):
#     @functools.wraps(f)
#     def wrapped(*args, **kwargs):
#         response = f(*args, **kwargs)
#         try:
#             if request.path == '/main_handler':
#                 request.environ.get('werkzeug.server.shutdown')()
#         except:
#             pass
#         return response
#     return wrapped
# @close_socket_after_request
@app.route('/main_handler/<cmd>/<sender>', methods=['POST', 'GET'])
def main_handler(cmd, sender, plan={}):
    
    global epoch
    global test_name
    global under_test
    global monitor_interval
    global logger
    global node_role
    global test_started
    global test_finished
    global battery_cfg
    global apps
    global time_based_termination
    global sensor_log
    global max_request_timeout
    global monitor_interval
    global node_op
    global battery_charge
    global lock
    logger.info('main_handler: cmd = ' + cmd + ', sender = ' + sender)
    # logger.info('***************************************************************************************************' +str(request.path))
    if cmd == 'plan':
        logger.info('plan is called')
        # ACTIONS BASED ON SENDER role or location
        # wait
        if under_test == True:
            under_test = False
            cooldown()

        # reset times, battery_cfg(current SoC), apps (created/recv), monitor, free up resources,
        reset()
        
        if node_role == "MASTER" or (not node_role and sender == 'INTERNAL'):
            network_openfaas_clean_up()

        # plan
        # set plan for LOAD_GENERATOR, MONITOR, STANDALONE by master node
        if sender == 'MASTER':
            plan = request.json

            # verify plan
            if plan == None:
                logger.warning('main_handler:plan:master:no plan received, so default values are used')
            else:
                logger.info(f'received plan= {plan}')
                verified = apply_plan(plan)
                if verified == False:
                    return "failed to set plan"
        # set plan for coordinator (master or standalone) by itself
        elif sender == "INTERNAL":
            if len(plan) > 0:
                verified = apply_plan(plan)
                if verified == False:
                    return "failed to set plan"
            else:
                logger.error('main_handler:plan:INTERNAL: no plan received for coordinator')
                return "main_handler: plan: no plan received for master"
        # set plan for MONITOR only in standalone tests by STANDALONE node
        elif sender == "STANDALONE":
            plan = request.json
            if plan == None:
                logger.warning('main_handler:plan:standalone: no plan received, so default values are used')
            else:
                apply_plan(plan)

            if node_role != "MONITOR":
                logger.error('main_handler:plan:standalone: no monitor role for monitor')
                return "main_handler:plan:standalone: no monitor role for monitor"
        else:
            logger.error("main_handler:plan:unknown sender")
            return "main_handler:plan:unknown sender"

            # show_plan()

        # verify usb meter connection
        if usb_meter_involved == True:
            if usb_meter_connection() == False:
                logger.error('main_handler:plan:usb_meter_connection:failed')
                return "main_handler:plan:usb_meter_connection:failed"

        return "success"

    # cmd=on
    elif cmd == 'on':
        # ACTIONS BASED ON assigned node_role
        # wait
        if under_test == True:
            under_test = False
            cooldown()

        # get plan
        show_plan()

        # under test
        under_test = True

        # set start time
        test_started = datetime.datetime.now(datetime.timezone.utc).astimezone().timestamp()

        # run monitor
        logger.info('start monitor thread...')
        thread_monitor = threading.Thread(target=monitor, args=())
        thread_monitor.name = "monitor"
        thread_monitor.start()
        logger.info('adter monitor........')
        # run battery_sim
        if battery_cfg[0] == True:

            if usb_meter_involved == False:
                logger.error('main_handler:on: USB Meter is needed for Battery Sim')
                return "main_handler:on: USB Meter is needed for Battery Sim"
            logger.info('start battery_sim thread...')
            thread_battery_sim = threading.Thread(target=battery_sim, args=())
            thread_battery_sim.name = "battery_sim"
            thread_battery_sim.start()

        # run timer
        if time_based_termination[0] == True:
            logger.info('start timer thread...')
            thread_timer = threading.Thread(target=timer, args=())
            thread_timer.name = "timer"
            thread_timer.start()

        # run failuer handler
        if node_role == 'LOAD_GENERATOR' or node_role == 'STANDALONE':
            logger.info('start failure_handler thread...')
            thread_failure_handler = threading.Thread(target=failure_handler, args=())
            thread_failure_handler.name = "failure_handler"
            thread_failure_handler.start()

        # run workload
        if node_role == "LOAD_GENERATOR" or node_role == 'STANDALONE':
            # per apps
            for my_app in apps:
                if my_app[1] == True:
                    logger.info('start app workload thread...')
                    thread_app = threading.Thread(target=workload, args=(my_app,))
                    thread_app.name = "workload-" + my_app[0]
                    thread_app.start()

        # run scheduler and autoscaler and load balancer
        if node_role == "MASTER":
            #scheduler
            thread_scheduler = threading.Thread(target=scheduler, args=())
            thread_scheduler.name = "scheduler"
            thread_scheduler.start()
            #autoscaler
            thread_autoscaler = threading.Thread(target=autoscaler, args=())
            thread_autoscaler.name = "autoscaler"
            thread_autoscaler.start()
            #load balancer
            thread_load_balancer = threading.Thread(target=load_balancer, args=())
            thread_load_balancer.name = "load_balancer"
            thread_load_balancer.start()

            #cluster_info_populator
            if setup.cluster_info_populate['enable']:
                thread_cluster_info_populator = threading.Thread(target=cluster_info_populator, args=())
                thread_cluster_info_populator.name = "cluster_info_populator"
                thread_cluster_info_populator.start()

        return 'success'

    # called if an app workload finishes
    elif cmd == 'app_done':
        if all_apps_done() == True:
            # avoid double stop at the same time
            if under_test == False:
                logger.info('main_handler:app_done: all apps done already or timer trigerred')
                return 'success'

            logger.info('main_handler:app_done: all apps done')

            if time_based_termination[0] == True:
                pass  # refer to timer
            # not time based
            else:
                if node_role == "STANDALONE":
                    peers_stop()
                # stop monitor and battery_sim
                under_test = False

                time.sleep(monitor_interval)
                logger.info('main_handler:app_done: call save reports')
                save_reports()
        else:
            logger.info('main_handler:app_done: a workload done, but not all apps yet')

    # metrics write
    elif cmd == 'metrics':
        with lock:
            if 'internal' in sender:
                data = metrics
            else:
                data = request.json

            # if it is a worker and it is already in the metrcis_received, skip it 
            if data["node"]["name"] != "master" and  data["node"]["name"]  in metrcis_received:
                return "repeat-skipped"
            
            #write

            #add node to list of metrcis_received
            metrcis_received.append(data["node"]["name"])
            
            #write
            logger.info('call excel_writer.write')
            logger.info('data')
            logger.info(data)
            logger.info('excel_file_path')
            logger.info(setup.excel_file_path)
            result, row = excel_writer.write(data, setup.excel_file_path)
            logger.info('call excel_writer.write done in row #' + str(row))

            #len of workers + master
            rows_count = 1 #1 = master
            for node in setup.nodes:
                #if node is PEER, which means involved in the test
                if node[0] == "PEER":
                    rows_count +=1

            #if all received
            if rows_count == len(metrcis_received):
                #write avg
                logger.info('call excel_writer.avg')
                row = excel_writer.write_avg(len(metrcis_received) - 1, setup.excel_file_path)
                logger.info('call excel_writer.avg done in row #' + str(row))



            # write avg of results if this is the last worker sending metrics
            #Assumption, nodes involved in experiments have mode on 'PEER' and name in the format of 'wstring#' where # is a number. Otherwise, writing to excel fails.
            #which node is the latest one? get largest number
            '''previous_node_id = -1
            previous_node_name = ""
            rows_count = 0
            for node in setup.nodes:
                #if node is PEER, which means involved in the test
                if node[0] == "PEER":
                    rows_count +=1

                    #get node id only
                    node_id = [i for i in node[1] if i.isdigit()]
                    node_id = int(''.join(node_id))

                    #get node id only of the first identified one
                    # get_latest_node_to_wrapup_id = ""
                    if node_id > previous_node_id:
                        previous_node_id = node_id
                        previous_node_name = node[1]
                        # get_latest_node_to_wrapup_id = int(''.join(get_latest_node_to_wrapup_id))

            #if current metrics belong to the latest (by node number) expected node, wrap average up
            if data["node"]["name"] == previous_node_name:
                logger.info('call excel_writer.avg')
                row = excel_writer.write_avg(rows_count, setup.excel_file_path)
                logger.info('call excel_writer.avg done in row #' + str(row))
'''
            logger.info('write is done')
            return result

    elif cmd == 'stop':
        # stop monitor and battery_sim
        logger.info('main_handler:stop: under_test=False')
        under_test = False
        # stop workload in background, workload waits for req timeout
        cooldown()

        if node_role == "STANDALONE":
            peers_stop()

        if node_role == "MONITOR":
            test_finished = datetime.datetime.now(datetime.timezone.utc).astimezone().timestamp()

        logger.info('main_handler:stop: call save_reports')
        save_reports()
        logger.info('Test ' + test_name + ' is done!')

        # thread to start a new test
        if node_role == "MASTER":
            # epoch
            epoch += 1

            #set epoch in config file if needed
            if setup.master_behavior_after_test_if_multiple_tests == 'reboot-before-starting-next-test':
                cmd = "echo epoch=" + str(epoch) + " > /home/ubuntu/logs/config.txt"
                logger.info(cmd)

                out, error = utils.shell(cmd)
                logger.info(out + error)

            #any other test left?
            if epoch < len(setup.test_name):
                logger.info('Sleep for another test ...')
                # clean up
                #avoid end of test clean up to allow remained workers to use functions while master is sleeping for next test.
                #Instead, at the start of each test, master runs network_openfaas_clean_up()
                # network_openfaas_clean_up()

                # cooldown
                cooldown(setup.intra_test_cooldown)

                node = [node for node in setup.nodes if
                        node[0] == "COORDINATOR" and node[1] == socket.gethostname() and node[2] == node_IP][0]
                logger.info('node: ' + str(node))

                #start new test in the same run (does not use config file for epoch)
                if setup.master_behavior_after_test_if_multiple_tests == 'continue':
                    thread_launcher = threading.Thread(target=launcher, args=(node,))
                    thread_launcher.name = "launcher"
                    thread_launcher.start()
                #reboot master (use config file for epoch upon log in) - then master in launcher can reboot peers
                elif setup.master_behavior_after_test_if_multiple_tests == 'reboot-before-starting-next-test':
                    logger.info('reboot the master. Then, when bootup, it runs launcher to check epoch')
                    cmd = "sudo reboot"
                    logger.info(cmd)

                    out, error = utils.shell(cmd)
                    logger.info(out + error)
                else:
                    logger.info(f'master_behavior_after_test_if_multiple_tests={setup.master_behavior_after_test_if_multiple_tests} NOT found')
            else:
                logger.info('All tests done.')
    #"push"                
    elif cmd == 'push'         :
        logger.info("main_handler:cmd=push: sender=" + str(sender) + ": start")
        
        if sender == 'INTERNAL' and plan:
            template = plan
        elif request.json:
            template = request.json
        else:
            logger.error('request.json is not provided or sender is not INTERNAL + plan not provided')
            return None
        

        logger.info(f'main_handler/push recevied {template}' )

        #get_data
        if 'cluster_info' in template:
            logger.info('cluster_info received')

            global cluster_info
            cluster_info = template['cluster_info']
            
            #if populator_config 
            if 'populator_config' in template:
                logger.info('populator_config recevied')
                #log_on_file
                populator_config = template['populator_config']
                if populator_config['log_on_file']['enable']:
                    logger.info('populator_config log_on_file enabled')
                    #check dir and file existence
                    #get all files path
                    nodes_path, functions_path, general_nodes_path, general_functions_path = check_cluster_info_dir_file_exist(populator_config)
                    logger.info(f'files path: nodes_path={nodes_path}, functions_path={functions_path}, general_nodes_path={general_nodes_path}, general_functions_path={general_functions_path}')

                    #append to file nodes
                    with open(nodes_path, 'a') as nodes_file, open(general_nodes_path, 'a') as general_nodes_file:
                        ##local timestamp excluding milliseconds
                        ct = datetime.datetime.now(datetime.timezone.utc).astimezone().strftime('%Y-%m-%d %H:%M:%S')  # local
                        #add timestamps line
                        nodes_file.write(str(ct) + '----------\n')
                        general_nodes_file.write(str(ct) + '----------\n')
                        #append new log to filea
                        for name, status in cluster_info['nodes'].items():
                            new_log = f'node={name},   status={status}\n'
                            nodes_file.write(new_log)
                            general_nodes_file.write(new_log)
                    #general
                    with open(functions_path, 'a') as functions_file, open(general_functions_path, 'a') as general_functions_file:
                        #local timestamp excluding milliseconds
                        ct = datetime.datetime.now(datetime.timezone.utc).astimezone().strftime('%Y-%m-%d %H:%M:%S')  # local
                        #add timestamps line
                        functions_file.write(str(ct) + '----------\n')
                        general_functions_file.write(str(ct) + '----------\n')
                        #append new log to filea
                        for function_name, its_hosts in cluster_info['functions'].items():
                            new_log = f'func={function_name},   hosts={",".join(its_hosts)}\n'
                            functions_file.write(new_log)
                            general_functions_file.write(new_log)


        return 'success'   
            
    # 'pull'
    elif cmd == "pull":
        logger.info("main_handler:cmd=pull: sender=" + str(sender) + ": start")
        if not request.json:
            logger.error('request.json is not provided')
            return None
        else:    
            template = request.json

        #get data
        if 'cpuUtil' in request.json:
            global cpuUtil
            template['cpuUtil'] = cpuUtil[-1] if cpuUtil else psutil.cpu_percent()
            

        if 'charge' in request.json:
            template['charge'] = round(battery_cfg[3], 2) if len(battery_cfg) else -2

        if 'node_status' in request.json:
            #if battery_cfg is set (test started)
            if 12 in range(len(battery_cfg)):
                #DELETED# template['node_status'] = battery_cfg[12]
                template['node_status'] = node_operation_status_getter(battery_cfg[12])
            #if not set yet
            else:
                template['node_status'] = -2

        logger.info("main_handler: response return to "
                    + str(sender) + ": " + str(template))


        response = make_response(json.dumps(template), 200)
        response.mimetype = "application/json"
        response.headers['Content-Type'] = 'application/json'
        response.headers['template'] = template

        return response
        # return jsonify(template)
        # logger.info("main_handler: cmd=pull: sender=" + str(sender) + ": done")
    else:
        logger.error('main_handler: unknown cmd')
        return 'failed'

    logger.info('main_handler: stop')

def check_cluster_info_dir_file_exist(populator_config):
    #achieve this: 
    #base /home/ubuntu/logs/cluster_info/

    # path/test_name/nodes.txt
    # path/test_name/functions.txt
    #path/nodes.txt
    #path/functions.txt
    
    base_path = populator_config['log_on_file']['path']
    test_path = base_path + test_name
    nodes_path =base_path + test_name + '/nodes.txt'
    functions_path = base_path + test_name + '/functions.txt'
    general_nodes_path = base_path  + 'nodes.txt'
    general_functions_path = base_path + 'functions.txt'

    logger.info('check_cluster_info_dir_file_exist start')
    #if base_path exists
    if not os.path.isdir(base_path):
        os.makedirs(base_path)
    #test_path exist
    if not os.path.isdir(test_path):
        os.makedirs(test_path)
    #nodes_path file exists
    if not os.path.isfile(nodes_path):
        open(nodes_path, 'w').close()
    #functions_path file exist
    if not os.path.isfile(functions_path):
        open(functions_path, 'w').close()
    
    #general location 
    #general_node_path file exist
    if not os.path.isfile(general_nodes_path):
        open(general_nodes_path, 'w').close()
    #general_functions_path file exist
    if not os.path.isfile(general_functions_path):
        open(general_functions_path, 'w').close()

    logger.info('check_cluster_info_dir_file_exist done')
    return nodes_path, functions_path, general_nodes_path, general_functions_path
# clean up is used at the start and end of experiments
def network_openfaas_clean_up():
    # clean up
    global logger
    logger.info('clean_up: start')
    try:
        print('#################################################################################################################')
        # #restart network interfaces
        # cmd = "sudo ifdown --exclude=lo -a -v && sudo ifup --exclude=lo -a -v"
        # logger.info('restart network interfaces: ' + cmd)
        # out, error = utils.shell(cmd)
        # logger.info(out + error)

        # #restart network manager
        # cmd = "sudo systemctl restart NetworkManager.service"
        # logger.info('restart network manager: ' + cmd)
        # out, error = utils.shell(cmd)
        # logger.info(out + error)
        net_interface_manager_restart()

        #restart k3s.service
        cmd = "sudo systemctl restart k3s.service"
        logger.info('restart k3s.service: ' + cmd)
        out, error = utils.shell(cmd)
        logger.info(out + error)

        #redeploy kube-system
        '''
        cmd = "kubectl -n kube-system rollout restart deploy"
        logger.info('redeploy kube-system: ' + cmd)
        out, error = utils.shell(cmd)
        logger.info(out + error)'''

        #delete hpa objects
        cmd = "kubectl delete hpa --all -n openfaas-fn"
        logger.info('clean up hpa objects: ' + cmd)
        out, error = utils.shell(cmd)
        logger.info(out + error)
        
        #delete profile objects. profiles are created in openfaas namespace, not openfaas-fn
        cmd = "kubectl delete profile --all -n openfaas"
        logger.info('clean up profile objects: ' + cmd)
        out, error = utils.shell(cmd)
        logger.info(out + error)
        
        #delete functions or set their replicas to 1????? to avoid leftover functions with extra replicas for the next test
        #now, scheduler deletes the function in the first scheduling round and then again creates it

        #delete helm chart
        cmd = "helm delete " + setup.function_chart[0]
        logger.info('clean up function chart: ' + cmd)
        out, error = utils.shell(cmd)
        logger.info(out + error)

        #restart nats
        cmd = "kubectl rollout restart -n openfaas deployment/nats"
        logger.info('clean up nats chart: ' + cmd)
        out, error = utils.shell(cmd)
        logger.info(out + error)

        #restart queue-worker ????? should get name of queues from a reliable variable
        if setup.multiple_queue:
            cmd = "kubectl rollout restart -n openfaas deployment/queue-worker-ssd"
            logger.info('clean up queue-worker: ' + cmd)
            out, error = utils.shell(cmd)
            if error:
                logger.error(out + error)
            else:
                logger.info(out + error)
            cmd = "kubectl rollout restart -n openfaas deployment/queue-worker-yolo3"
            logger.info('clean up queue-worker: ' + cmd)
            out, error = utils.shell(cmd)
            if error:
                logger.error(out + error)
            else:
                logger.info(out + error)
            cmd = "kubectl rollout restart -n openfaas deployment/queue-worker-irrigation"
            logger.info('clean up queue-worker: ' + cmd)
            out, error = utils.shell(cmd)
            if error:
                logger.error(out + error)
            else:
                logger.info(out + error)
            cmd = "kubectl rollout restart -n openfaas deployment/queue-worker-crop-monitor"
            logger.info('clean up queue-worker: ' + cmd)
            out, error = utils.shell(cmd)
            if error:
                logger.error(out + error)
            else:
                logger.info(out + error)
            cmd = "kubectl rollout restart -n openfaas deployment/queue-worker-short"
            logger.info('clean up queue-worker: ' + cmd)
            out, error = utils.shell(cmd)
            if error:
                logger.error(out + error)
            else:
                logger.info(out + error)
        else:
            cmd = "kubectl rollout restart -n openfaas deployment/queue-worker"
            logger.info('clean up queue-worker: ' + cmd)
            out, error = utils.shell(cmd)
            if error:
                logger.error(out + error)
            else:
                logger.info(out + error)
    except Exception as e:
        logger.exception('clean_up:\n' + str(e))

    logger.info('network_openfaas_clean_up: sleep 5 sec')
    time.sleep(5)
    logger.info('network_openfaas_clean_up: done')


# cooldown
def cooldown(intra_test_cooldown=0):
    global node_role
    global battery_cfg
    global monitor_interval
    global max_request_timeout
    global failure_handler_interval
    global apps
    global cpuFreq
    global logger
    logger.info('cooldown: start')
    wait = 0

    if node_role == "MONITOR" or node_role == "MASTER":
        if battery_cfg[0] == True:
            wait = sum([monitor_interval, battery_cfg[7]])
        else:
            wait = monitor_interval

    else:  # node_role == "STANDALONE or LOAD_GENERATOR"
        if battery_cfg[0] == True:
            wait = sum([monitor_interval, battery_cfg[7], failure_handler_interval,
                        max_request_timeout])  # sum get no more than 2 args
        else:
            wait = sum([monitor_interval, failure_handler_interval, max_request_timeout])
        # while any([True if app[1]==True and app[6]!=app[7] else False for app in apps ])==True:
        #    wait=3
        #    logger.info('cooldown: wait for ' + str(wait) + ' sec')
        #    time.sleep(wait)

        # reset cpu frequency settings
        stdout = sp.getoutput("sudo chown -R $USER /sys/devices/system/cpu/*")
        logger.info('output of sudo chown -R $USER /sys/devices/system/cpu/*: \n' + str(stdout))
        try:
            cpuFreq.reset()
        except:
            logger.error('cpuFreq.reset() ')

    if wait < intra_test_cooldown:
        wait = intra_test_cooldown

    logger.info('cooldown: wait for ' + str(wait) + ' sec...')
    time.sleep(wait)

    logger.info('cooldown: stop')


def show_plan():
    #
    global epoch
    global test_name
    global node_name
    global debug
    global load_balancing
    global bluetooth_addr
    global hiccups_injection
    global active_sensor_time_slots
    global apps
    global battery_cfg
    global time_based_termination
    global max_request_timeout
    global min_request_generation_interval
    global sensor_admission_timeout
    global node_down_sensor_hold_duration
    global node_role
    global peers
    global monitor_interval
    global failure_handler_interval
    global usb_meter_involved
    global battery_operated
    global node_IP
    global socket
    global max_cpu_capacity
    global raspbian_upgrade_error
    global boot_up_delay
    global usb_eth_ports
    global log_path
    # counters/variables
    global under_test
    global test_started
    global test_finished
    global sensor_log
    global workers
    global functions
    global history
    global suspended_replies
    global down_time
    # global network_name_server

    logger.info('show_plan: start')
    show_plan = ("test_name: " + test_name
                 + " node_name: " + str(socket.gethostname()) + " / " + str(node_name)
                 + "\n IP: " + node_IP
                 + "\n node_role: " + node_role
                 + "\n load_balancing: " + str(load_balancing)
                 + "\n Debug: " + str(debug)
                 + "\n bluetooth_addr: " + bluetooth_addr
                 + "\n hiccups_injection: " + str(hiccups_injection) 
                 + "\n active_sensor_time_slots: " + str(str(setup.active_sensor_time_slots) + "\npercent=" + str(setup.percent) if node_role == 'MASTER' else str(active_sensor_time_slots))
                 + "\n apps: " + '\n'.join([str(app) for app in apps])
                 + "\n peers: " + str(peers)
                 + "\n usb_meter_involved: " + str(usb_meter_involved)
                 + "\n battery_operated: " + str(battery_operated)
                 + "\n battery_cfg: " + str(battery_cfg)
                 + "\n time_based_termination: " + str(time_based_termination)
                 + "\n monitor_interval: " + str(monitor_interval)
                 + "\n failure_handler_interval: " + str(failure_handler_interval)
                 + "\n scheduling_interval: " + str(
                [setup.scheduling_interval[epoch if 'scheduling_interval' in setup.variable_parameters else 0] if node_role == 'MASTER' or node_role == 'STANDALONE' else 'null'][0])
                 + "\n max_request_timeout: " + str(max_request_timeout)
                 + "\n min_request_generation_interval: " + str(min_request_generation_interval)
                 + "\n sensor_admission_timeout: " + str(sensor_admission_timeout)
                 + "\n node_down_sensor_hold_duration: " + str(node_down_sensor_hold_duration)
                 + "\n max_cpu_capacity: " + str(max_cpu_capacity)
                 + "\n boot_up_delay: " + str(boot_up_delay)
                 + "\n log_path: " + str(log_path)
                 + "\n under_test: " + str(str(under_test))
                 + "\n test_started: " + str(str(test_started))
                 + "\n test_finished: " + str(str(test_finished))
                 + "\n sensor_log: " + str(str(sensor_log))
                 + "\n functions: " + str(str(functions))
                 + "\n workers: " + str(str(workers))
                 + "\n history: " + str(str(history))
                 + "\n suspended_replies: " + str(str(suspended_replies))
                 + "\n down_time: " + str(str(down_time))
                 + "\n raspbian_upgrade_error: " + str(raspbian_upgrade_error)
                 + "\n usb_eth_ports: " + str(usb_eth_ports))
    
                #+ "\n network_name_server: " + str(network_name_server)
    logger.info("show_plan: " + show_plan)

    logger.info('show_plan: stop')


def apply_plan(plan):
    global test_name
    global debug
    global load_balancing
    global bluetooth_addr
    global hiccups_injection
    global active_sensor_time_slots
    global apps
    global battery_cfg
    global time_based_termination
    global max_request_timeout
    global min_request_generation_interval
    global session_enabled
    global sensor_admission_timeout
    global node_down_sensor_hold_duration
    global node_role
    global peers
    global waitress_threads
    global monitor_interval
    global failure_handler_interval
    global usb_meter_involved
    global battery_operated
    global max_cpu_capacity
    global log_path
    global pics_folder
    global pics_num
    global file_storage_folder
    global boot_up_delay
    global usb_eth_ports
    global raspbian_upgrade_error
    global node_IP
    # global network_name_server
    logger.info('apply_plan: start')
    # create test_name
    test_name = socket.gethostname() + "_" + plan["test_name"]

    node_role = plan["node_role"]
    load_balancing = plan["load_balancing"]
    #run tinyobj.py if required and is not running
    #decoupled
    if 'read' in load_balancing['object_storage'] and load_balancing['object_storage']['read']['decoupled'] == True:
        #decentralized-tinyobj or centralized-tinyobj on this node
        if load_balancing['object_storage']['read']['type'] == 'decentralized-tinyobj' or (load_balancing['object_storage']['read']['type'] == 'centralized-tinyobj'
                        and load_balancing['object_storage']['read']['ip'] == node_IP):
            #run tinyobj.py if not running
            logger.info('pgrep -af python')
            out, err = utils.shell('pgrep -af python')
            if err:
                logger.error('pgrep ' + str(err))

            if 'tinyobj.py' not in out:
                logger.info('python3 tinyobj.py')
                out, err = utils.shell('python3 tinyobj.py &')
                if err:
                    logger.error('tinyobj.py & ' + str(err))

    debug = plan["debug"]
    bluetooth_addr = plan["bluetooth_addr"]
    hiccups_injection= plan["hiccups_injection"]
    active_sensor_time_slots = plan["active_sensor_time_slots"]
    apps = plan["apps"]
    peers = plan["peers"]
    usb_meter_involved = plan["usb_meter_involved"]
    # Either battery_operated or battery_cfg should be True, if the second, usb meter needs enabling
    battery_operated = plan["battery_operated"]
    # Battery simulation
    battery_cfg = plan["battery_cfg"]  
    
    # NOTE: apps and battery_cfg values change during execution
    time_based_termination = plan["time_based_termination"]  # end time-must be longer than actual test duration
    monitor_interval = plan["monitor_interval"]
    failure_handler_interval = plan["failure_handler_interval"]
    max_request_timeout = plan["max_request_timeout"]
    min_request_generation_interval = plan["min_request_generation_interval"]
    session_enabled = plan["session_enabled"]
    sensor_admission_timeout = plan["sensor_admission_timeout"]
    node_down_sensor_hold_duration = plan["node_down_sensor_hold_duration"]
    max_cpu_capacity = plan["max_cpu_capacity"]

    # get home directory
    home = expanduser("~")

    log_path = plan["log_path"]
    log_path = home + log_path + test_name
    # empty test_name folder (if not exist, ignore_errors)
    shutil.rmtree(log_path, ignore_errors=True)
    # create test_name folder
    if not os.path.exists(log_path): os.makedirs(log_path)

    # update logger fileHandler
    # default mode is append 'a' to existing log file. But, 'w' is write from scratch
    # change fileHandler file on the fly
    # another option: [%(funcName)s] ???
    formatter = logging.Formatter('%(asctime)s [%(threadName)s] [%(levelname)s] %(message)s')
    try:
        path_for_log= log_path + '/' + os.path.basename(__file__).split('.')[0] + '.log'

    except:
        import sys
        path_for_log= log_path + '/' + sys.argv[0].split('.')[0] + '.log'
        print(path_for_log)
    #file
    fileHandler = logging.FileHandler(path_for_log, mode='w')
    fileHandler.setFormatter(formatter)
    fileHandler.setLevel(logging.DEBUG)
    log = logging.getLogger()  # root logger
    for hndlr in log.handlers[:]:  # remove the existing file handlers
        log.removeHandler(hndlr)
    log.addHandler(fileHandler)  # set the new handler
    #console 
    consoleHandler = logging.StreamHandler()
    consoleHandler.setFormatter(formatter)
    consoleHandler.setLevel(logging.DEBUG)

    logger.addHandler(consoleHandler)

    if debug: log.setLevel(logging.DEBUG)


    #file general. logger in ~/logs/hedgi.py
    #home + /logs/ + file_name (e.g., hedgi.py) + .log
    path_for_log = home + plan["log_path"] + os.path.basename(__file__).split('.')[0] + '.log'
    fileHandlerGen = RotatingFileHandler(path_for_log, mode='a', maxBytes= 50 * 1024 *1024, backupCount=5)
    fileHandlerGen.setFormatter(formatter)
    fileHandlerGen.setLevel(logging.DEBUG)
    logger.addHandler(fileHandlerGen)

    pics_folder = home + plan["pics_folder"]
    if not os.path.exists(pics_folder):
        logger.error('apply_plan: no pics_folder directory found at ' + pics_folder)
        return False
    pics_num = plan["pics_num"]
    
    file_storage_folder = home + plan["file_storage_folder"]
    if not os.path.exists(file_storage_folder): os.makedirs(file_storage_folder)

    waitress_threads = plan["waitress_threads"]
    boot_up_delay = plan["boot_up_delay"]
    raspbian_upgrade_error = plan["raspbian_upgrade_error"]

    # set cpu frequency config, if the node_role is requested to affect
    if node_role in plan["cpu_freq_config"]["effect"]:
        apply_cpu_freq_config(plan["cpu_freq_config"])

    usb_eth_ports = plan["usb_eth_ports"]
    #apply usb_eth_ports command
    usb_eth_port_control(usb_eth_ports)

    # network_name_server = plan["network_name_server"]

    logger.info('apply_plan: stop')
    return True


# cpu frequency config
def apply_cpu_freq_config(config):
    global cpuFreq
    global logger
    stdout = sp.getoutput("sudo chown -R $USER /sys/devices/system/cpu/*")
    logger.info('output of sudo chown -R $USER /sys/devices/system/cpu/*: \n' + str(stdout))

    #run Jetson Nano on MAX power (10W)
    if utils.what_device_is_it('nvidia jetson nano'):
        #-m 0 = MAXN mode and it needs proper powering while -m 1 = 5V mode where 2 CPU cores will be off
        mode = None
        if config['jetson_nano_nvp_mode'] == 'max-10w':
            mode = '0'
        elif config['jetson_nano_nvp_mode'] == '5w':
            mode = '1'
        else:
            logger.error('jetson_nano_nvp_mode='  + str(config['jetson_nano_nvp_mode']) + ' not defined')
        
        cmd = 'sudo /usr/sbin/nvpmodel -m ' + mode
        logger.info('cmd= ' + cmd)
        
        output, error = utils.shell(cmd)
        if error:
            logger.error('NANO power mode:' + error)
        else:
            logger.info(output + '\nNano power mode is now ' + str(config['jetson_nano_nvp_mode']))
    
    #apply CPU config
    try:
        cpuFreq.reset()
        #CPU informations are in files located in 'cd /sys/devices/system/cpu/cpu0/cpufreq'
        #You may manually Collect informations by 'paste <(ls *) <(cat *) | column -s $'\t' -t'
        available_govs = cpuFreq.available_governors
        logger.info('available governors: ' + str(available_govs))
        govs = cpuFreq.get_governors()
        logger.info('default governors per core: ' + str(govs))
        #set governors
        logger.info(f'try to set cpu governor to {config["governors"]}')

        cpuFreq.set_governors(config['governors'])
        govs = cpuFreq.get_governors()
        logger.info('new governors per core: ' + str(govs))
        mismatch_governor = True if True in [True if config['governors'] != governor else False for core, governor in govs.items()] else False
        if mismatch_governor:
            logger.error('suggested governors (' + config['governors'] + ') != running governors (' + str(govs) + ')')

        available_freqs = cpuFreq.available_frequencies
        logger.info('available frequencies: ' + str(available_freqs))

        # set min and max frequencies. If min value is less than actual min, the actual min is set, and vise versa.
        #if set as 0, default min max are used.
        if config['set_min_frequencies'] != 0:
            cpuFreq.set_min_frequencies(config['set_min_frequencies'])
        if config['set_max_frequencies'] != 0:
            cpuFreq.set_max_frequencies(config['set_max_frequencies'])

        # only if governor is 'userspace' we can set fixed frequencies. It affects scaling_setspeed file
        if config['governors'] == 'userspace':
            cpuFreq.set_frequencies(config['set_frequencies'])

        # output
        govs = cpuFreq.get_governors()
        freq = re.split(', |=', str(psutil.cpu_freq()).split(')')[0])
        freq_curr = freq[1]
        freq_min = freq[3]
        freq_max = freq[5]
        logger.info('cpu config: ' + 'governors: ' + str(govs)
                    + 'curr= ' + str(freq_curr)
                    + '  min= ' + str(freq_min)
                    + '  max= ' + str(freq_max))
        if freq_min == freq_curr and freq_curr == freq_max:
            logger.error('freq_min, freq_curr and freq_max are all equal!\n'
                        + 'If this is not planned and the device is Jetson Nano, perhaps the jetson_clocks is running\n'
                        + 'You may disable that by sudo jetson_clocks --restore or restart the device')
            # if utils.what_device_is_it('nvidia jetson nano'):
            #     cmd = 'sudo jetson_clocks --restore'
            #     output, error = utils.shell(cmd)
            #     if error:
            #         logger.error('Failed to restor jetson_clock\n' + error)
            #     else:
            #         #verify if CPU frequencies:min, max and curr are correct now.

    except Exception as e:
        logger.exception(str(e))

# timer
def timer():
    global monitor_interval
    global max_request_timeout
    global failure_handler_interval
    global time_based_termination
    global test_started
    global under_test
    logger.info('start')

    while under_test:
        now = datetime.datetime.now(datetime.timezone.utc).astimezone().timestamp()
        elapsed = now - test_started
        if elapsed >= time_based_termination[1]:
            break
        else:
            time.sleep(min(failure_handler_interval, monitor_interval, max_request_timeout))

    if under_test == True:
        # alarm main_handler
        thread_terminator = threading.Thread(target=main_handler, args=('stop', 'INTERNAL',))
        thread_terminator.name = "terminator"
        thread_terminator.start()
    logger.info('stop')


# terminate who is "me" or "others" or "all"
@app.route('/terminate/<who>', methods=['GET', 'POST'])
def terminate(who):
    global internal_session
    if who == "me":
        main_handler('stop', 'INTERNAL')
    elif who == "others":
        for node in setup.nodes:
            if node[0] == "PEER":
                ip = node[2]
                try:
                    response = internal_session.post('http://' + ip + ':5000/main_handler/stop')
                    # response = requests.post('http://' + ip + ':5000/main_handler/stop')
                    # response.close()
                except:
                    logger.error('terminator: failed for ' + ip)
    elif who == "all":
        main_handler('stop', 'INTERNAL')

        for node in setup.nodes:
            if node[0] == "PEER":
                ip = node[2]
                try:
                    response = internal_session.post('http://' + ip + ':5000/main_handler/stop')
                    # response = requests.post('http://' + ip + ':5000/main_handler/stop')
                    # response.close()
                except:
                    logger.error('terminator: failed for ' + ip)
    else:
        logger.info('terminator: who is unknown')
        return 'failed'

    return "stopped"


def peers_stop():
    global logger
    global peers
    global internal_session
    logger.info('peers_stop: all_apps_done or time ended')
    # remote monitors stop
    reply = []
    try:
        for i in range(len(peers)):
            response = internal_session.get('http://10.0.0.' + peers[i] + ':5000/main_handler/stop/STANDALONE')
            # response = requests.get('http://10.0.0.' + peers[i] + ':5000/main_handler/stop/STANDALONE')
            # response.close()
            reply.append(response.text)
    except Exception as e:
        logger.error('peers_stop:error:' + peers[i] + ':' + str(s))

    if len([r for r in reply if "success" in r]) == len(peers):
        if len(peers) == 0:
            logger.info('peers_stop: No Peers')
        else:
            logger.info('peers_stop: Remote Peer Monitor Inactive')

    else:
        logger.error('peers_stop: Failed - remote peers monitors')


def battery_sim():
    global logger
    global under_test
    global battery_cfg
    global battery_history
    global down_time
    logger.info('Start')

    #status template initial
    battery_cfg[12] = {
    'failed':{'status': None,
        'last_start': None,
        'total_duration': 0,
        'switch_to_state_counter': 0},
    'pending':{'status': None,
        'last_start': None,
        'total_duration': 0,
        'switch_to_state_counter': 0},
    'running':{'status': None,
        'last_start': None,
        'total_duration': 0,
        'switch_to_state_counter': 0},}
    
    max_battery_charge = battery_cfg[1]  # theta: maximum battery capacity in mWh

    renewable_type = battery_cfg[4]

    renewable_inputs = []
    start_time = 0

    # get poisson
    if renewable_type == "poisson":

        # Generate renewable energy traces
        np.random.seed(battery_cfg[5][0])
        renewable_inputs = np.random.poisson(lam=battery_cfg[5][1], size=10000)
        # get real dataset
    elif renewable_type == "real":

        renewable_inputs = battery_cfg[6]

        start_time = datetime.datetime.now(datetime.timezone.utc).astimezone().timestamp()

    else:
        logger.error('renewable_type not found:' + str(renewable_type))

    previous_usb_meter = read_power_meter()[0]

    renewable_index = 0
    renewable_input = 0
    interval = battery_cfg[7]

    while under_test:
        # GET
        last_soc = battery_cfg[3]  # soc: previous observed SoC in Mwh
        last_unlimited_soc = battery_cfg[10]

        min_battery_charge = battery_cfg[8]
        last_status = 1 if last_soc > min_battery_charge else 0

        # last_soc = soc
        # renewable
        if renewable_type == "poisson":
            renewable_index += 1
            renewable_input = renewable_inputs[renewable_index]
        elif renewable_type == "real":
            # index and effect
            # index
            # hourly dataset, and scale 6 to 1, means each index is for 10 min
            now = datetime.datetime.now(datetime.timezone.utc).astimezone().timestamp()
            dur = now - start_time
            renewable_index = math.floor(dur / 600)  # if 601 sec, index = 1, if 200sec, index=0
            # if dataset finishs, it starts from the begining
            renewable_index = int(math.fmod(renewable_index, len(renewable_inputs))) if len(renewable_inputs) else 0
            # effect
            raw_input = renewable_inputs[renewable_index] if len(renewable_inputs) else 0

            #solar panel scaling
            solar_panel_scale = battery_cfg[17]
            raw_input = raw_input * solar_panel_scale

            # calculate the share for this interval

            renewable_input = (raw_input / (600 / interval)) 
        else:
            logger.error('unknown renewable_type  --> ' + str(renewable_type))

        #renewable_input
        battery_cfg[13] = renewable_input

        #energy_usage
        usb_meter = read_power_meter()[0]

        energy_usage = usb_meter - previous_usb_meter
        #a fix for mAh may be required also to avoid loops???
        # fix USB meter loop in 99999 to 97223. NOTE: INTERVALS SHOULD NOT BE TOO LONG: > 2500mWH
        if usb_meter - previous_usb_meter < 0:
            energy_usage = (99999 - previous_usb_meter) + (usb_meter - 97222)

        #energy_usage = 0 if node was down else energy_usage
        energy_usage = energy_usage * last_status
        battery_cfg[14] = energy_usage

        # soc
        # min to avoid overcharge. max to avoid undercharge
        soc = min(max_battery_charge, max(0, last_soc + renewable_input - energy_usage))

        #battery_excess_input calculation
        battery_excess_input = max(max(0, last_soc + renewable_input - energy_usage), max_battery_charge) - max_battery_charge
        battery_cfg[11]= battery_excess_input

        #max to avoid undercharge
        soc_unlimited = max(0, last_unlimited_soc + renewable_input - energy_usage)
        # soc_unlimited = soc + battery_excess_input
        battery_cfg[10] = soc_unlimited

        # check overcharging
        if battery_excess_input:
            logger.warning("battery_sim: battery_excess_input (" + str(battery_excess_input) + ") at " + str(
                soc) + ", but capped at max")

        battery_cfg[3] = soc

        # new status
        #DELETED battery_cfg[12] = 1 if soc >= battery_cfg[8] else 0
        #ADDED#
        logger.info(f'############################before##################################################### battery_cfg[12]= {battery_cfg[12]}')
        battery_cfg[12] = node_operation_status_setter(logger, last_soc, soc, battery_cfg, boot_up_delay)
        logger.info(f'#############################****after***########################################## battery_cfg[12]= {battery_cfg[12]}')

        # down_time
        # calculate down_time
        
        if soc < min_battery_charge:
            down_time += interval


        
#1:max,2:initial #3current SoC,
        #0: battery_sim True/False, 1:max (variable), 2:initial #3current SoC,
        #4: renewable type, 5:poisson seed&lambda,6:dataset, 7:interval, 8 min_battery_charge, 9 turned on at,10 soc_unlimited, 11 battery_excess_input per charge input mwh
        #12: status {}, 13: energy_input, 14: energy_consumed


        #temp log
        # time
        # ct = datetime.datetime.now().strftime("%d%m%Y-%H%M%S")
        ct = datetime.datetime.now(datetime.timezone.utc).astimezone()  # local
        ct_ts = datetime.datetime.now(datetime.timezone.utc).astimezone().timestamp()  # local ts

        battery_history_new = {'battery_time1': ct,
                                'battery_time2': ct_ts,
                                'max_battery_charge': battery_cfg[1],
                                'min_battery_charge': battery_cfg[8],
                                'soc': round(battery_cfg[3],2),
                                'soc_unlimited': round(battery_cfg[10],2),
                                'battery_excess_input': round(battery_cfg[11],2),
                                'status': battery_cfg[12],
                                'renewable_input': round(battery_cfg[13],2),
                                'energy_usage': round(battery_cfg[14],2),
                                }
        battery_history.append(battery_history_new)


        previous_usb_meter = usb_meter
        time.sleep(interval)

    logger.info('Stop')

def node_operation_status_getter(battery_cfg_12):
    status = None
    try:
        #test not started yet
        if not battery_cfg_12:
            status = -2
            return status

        #failed
        if battery_cfg_12['failed']['status'] == 1:
            status = 0
        #pending
        if battery_cfg_12['pending']['status'] == 1:
            
            if status == 0:
                logger.error(f'battery_cfg[12]_status_wrong11\nbattery_cfg[12]={battery_cfg[12]}\nbattery_cfg_12={battery_cfg_12}')
            status = 1
        #running
        if battery_cfg_12['running']['status'] == 1:
            if status == 0 or status == 1:
                logger.error(f'battery_cfg[12]_status_wrong22\nbattery_cfg[12]={battery_cfg[12]}\nbattery_cfg_12={battery_cfg_12}')
            status = 2

        return status
    except Exception as e:
        logger.exception(f'node_operation_status_getter -->{e}')

#set failed, pending or running state
def node_operation_status_setter(logger, last_soc, soc, battery_cfg, boot_up_delay):
    logger.info(f'node_operation_status_setter start last_soc={last_soc} soc={soc}')
    old_operation_status = copy.deepcopy(battery_cfg[12])

    #strategy for bootup
    battery_bootup_strategy = battery_cfg[15]
    #min_battery_charge_warmup
    min_battery_charge_warmup_percent = battery_cfg[16]
    min_battery_charge_warmup =  min_battery_charge_warmup_percent * battery_cfg[1] / 100

    min_battery_charge = battery_cfg[8]

    interval = battery_cfg[7]

    #at a time, only one state is 1
    new_operation_status = {}
    # {'failed':{'status': None,
    #     'last_start': None,
    #     'total_duration': 0,
    #     'switch_to_state_counter': 0},
    # 'pending':{'status': None,
    #     'last_start': None,
    #     'total_duration': 0,
    #     'switch_to_state_counter': 0},
    # 'running':{'status': None,
    #     'last_start': None,
    #     'total_duration': 0,
    #     'switch_to_state_counter': 0},}
    #failed
    try:
        new_status = None
        new_last_start = None
        new_total_duration = 0
        new_switch_to_state_counter = 0

        #status = 1 if soc > min else 0
        new_status = 1 if soc < min_battery_charge else 0
        
        #last_status = if old_status != 1 and new_status ==1 --> start is now else last_start no change
        now = datetime.datetime.now(datetime.timezone.utc).astimezone().timestamp()
        new_last_start = now if old_operation_status['failed']['status'] != 1 and new_status == 1 else old_operation_status['failed']['last_start']
        #get rid of None value by 0
        new_last_start = 0 if new_last_start == None else new_last_start

        #total_duration = total_duration + interval if status == 1 else no change
        new_total_duration = old_operation_status['failed']['total_duration'] + interval if new_status == 1 else old_operation_status['failed']['total_duration']

        #switch counter = + 1 if old_status == 0 and new == 1 else no change
        new_switch_to_state_counter = old_operation_status['failed']['switch_to_state_counter'] + 1 if old_operation_status['failed']['status'] != 1 and new_status == 1 else old_operation_status['failed']['switch_to_state_counter']

        #set new failed data
        new_failed_state = {'status': new_status,
                'last_start': new_last_start,
                'total_duration': new_total_duration,
                'switch_to_state_counter': new_switch_to_state_counter}
        

        #pending
        new_status = None
        new_last_start = None
        new_total_duration = 0
        new_switch_to_state_counter = 0

        #set pending status by a strategy: time-based or warmup-percent-based

        #time-based
        if battery_bootup_strategy == 'time-based':
            #status = 1 if (last_soc < min and soc >= min) OR ( last_status == 1 and now - last_start_time < boot) else 0
            
            #switch failed to pending . (last_soc < min and soc >= min)
            if last_soc < min_battery_charge and soc >= min_battery_charge:
                new_status = 1
                logger.info('node switched from failed to pending state! A')
            #battery soc percent based pending

            #or time-based pending 
            #( last_status == 1 and now - last_start_time < boot)
            #previously in pending
            if old_operation_status['pending']['status'] == 1:
                #still in pending
                if soc >= min_battery_charge:
                    #boot duration is not passed
                    now = datetime.datetime.now(datetime.timezone.utc).astimezone().timestamp()
                    last_start_time = old_operation_status['pending']['last_start'] if old_operation_status['pending']['last_start'] else now
                    if (now - last_start_time) < boot_up_delay:
                        new_status = 1
                        

            #else 0
            new_status = 0 if new_status == None else new_status

        #warmup-percent-based
        elif battery_bootup_strategy == 'warmup-percent-based':
            #status = 1 if (last_soc < min and soc >= min and soc < min_warmup) OR ( last_status == 1 and soc < min_battery_charge_warmup) else 0

             #switch failed to pending . (last_soc < min and soc >= min and soc < min_warmup)
            if last_soc < min_battery_charge and soc >= min_battery_charge and soc < min_battery_charge_warmup:
                new_status = 1
                logger.info('node switched from failed to pending state!')
            #( last_status == 1 and soc < min_battery_charge_warmup)
            #previously in pending. 
            if old_operation_status['pending']['status'] == 1:
                #still in pending (between min and min_warmup)
                if soc >= min_battery_charge:
                    if soc < min_battery_charge_warmup:
                        new_status = 1

            
            #else 0
            new_status = 0 if new_status == None else new_status

        #status pending determined

        #last_start
        new_last_start = now if old_operation_status['pending']['status'] != 1 and new_status == 1 else old_operation_status['pending']['last_start']
        #get rid of None value by 0
        new_last_start = 0 if new_last_start == None else new_last_start

        #total duration
        new_total_duration = old_operation_status['pending']['total_duration'] + interval if new_status == 1 else old_operation_status['pending']['total_duration']

        #switch counter = + 1 if old_status == 0 and new == 1 else no change
        new_switch_to_state_counter = old_operation_status['pending']['switch_to_state_counter'] + 1 if old_operation_status['pending']['status'] != 1 and new_status == 1 else old_operation_status['pending']['switch_to_state_counter']

        new_pending_state = {'status': new_status,
                'last_start': new_last_start,
                'total_duration':new_total_duration,
                'switch_to_state_counter': new_switch_to_state_counter}


        #running
        new_status = None
        new_last_start = None
        new_total_duration = 0
        new_switch_to_state_counter = 0

        #status = 1 if not failed or pending else 0
        new_status = 0 if new_failed_state['status'] or new_pending_state['status'] else 1

        new_last_start = now if old_operation_status['running']['status'] != 1 and new_status == 1 else old_operation_status['running']['last_start']
        #get rid of None value by 0
        new_last_start = 0 if new_last_start == None else new_last_start

        #total duration
        new_total_duration = old_operation_status['running']['total_duration'] + interval if new_status == 1 else old_operation_status['running']['total_duration']

        #switch counter = + 1 if old_status == 0 and new == 1 else no change
        new_switch_to_state_counter = old_operation_status['running']['switch_to_state_counter'] + 1 if old_operation_status['running']['status'] != 1 and new_status == 1 else old_operation_status['running']['switch_to_state_counter']

        new_running_state = {'status': new_status,
                'last_start': new_last_start,
                'total_duration':new_total_duration,
                'switch_to_state_counter': new_switch_to_state_counter}
        
        
        #prepare output
        new_operation_status['failed'] = new_failed_state
        new_operation_status['pending'] = new_pending_state
        new_operation_status['running'] = new_running_state

        return new_operation_status
    
    except Exception as e:
        logger.exception(f'node_operation_status_setter\n{e}')
# ---------------------------------

@app.route('/reset', methods=['POST'])
def reset():
    logger.info('reset:start')
    global test_name
    global metrics
    global under_test
    global load_balancing
    global test_started
    global test_finished
    global sensor_log
    global erro_collector
    global battery_cfg
    global workers
    global functions
    global history
    global apps
    global cpuFreq
    global failure_handler_interval
    global suspended_replies
    global down_time
    global boot_up_delay
    global usb_eth_ports
    global log_path
    global min_request_generation_interval
    global max_request_timeout
    global sensor_admission_timeout
    global node_down_sensor_hold_duration
    global metrcis_received
    global cluster_info

    # monitoring parameters
    global response_time
    # in monitor
    global response_time_accumulative

    global current_time
    global current_time_ts
    global node_op
    global battery_charge
    global battery_history
    global cpuUtil
    global cpu_temp
    global cpu_freq_curr
    global cpu_freq_max
    global cpu_freq_min
    global cpu_ctx_swt
    global cpu_inter
    global cpu_soft_inter
    global memory
    global disk_usage
    global disk_io_usage
    global bw_usage

    global power_usage
    global throughput
    global throughput2
    
    # preparation

    #fix DNS nameserver (helpful if after each host reboot the  value disappers)????the gateway IP must become first and then 8.8.8.8 in DNS list
    # cmd = f'echo "nameserver 8.8.8.8" | sudo  tee /etc/resolv.conf'
    # logger.info(cmd)
    # utils.shell(cmd)
    
    logger.info('reset: free up memory --HDMI is not disabled!')
    # Turn OFF HDMI output. ????tvservice is not enabled on devices always. An alternative solution is required.
    # cmd = "sudo /opt/vc/bin/tvservice -o"
    # out, error = utils.shell(cmd)
    # print(out + error)
    

    # free up memory
    # cache (e.g., PageCache, dentries and inodes) and swap
    cmd = "sudo echo 3 > sudo /proc/sys/vm/drop_caches && sudo swapoff -a && sudo swapon -a && printf '\n%s\n' 'Ram-cache and Swap Cleared'"
    out, error = utils.shell(cmd)
    if error:
        logger.error(out + error)

    # reset cpu frequency settings
    stdout = sp.getoutput("sudo chown -R $USER /sys/devices/system/cpu/*")
    logger.info('output of sudo chown -R $USER /sys/devices/system/cpu/*: \n' + str(stdout))
    try:
        cpuFreq.reset()
    except:
        logger.error('cpuFreq.reset() ')
    # variables
    test_name = "no_name"
    metrics = {}
    under_test = False
    load_balancing = {}
    test_started = None
    test_finished = None
    down_time = 0
    sensor_log = {}
    erro_collector = []
    home = expanduser("~")
    log_path = home + "/" + test_name
    cluster_info = None
    apps = []
    battery_cfg[3] = battery_cfg[2]  # current =initial
    metrcis_received = []
    # scheudler
    workers = []
    functions = []
    history = {'functions': [], 'workers': [], 'load_balancer': [], 'scheduler': [], 'autoscaler': []}
    suspended_replies = []
    boot_up_delay = 0
    usb_eth_ports = None
    # monitoring parameters
    # in owl_actuator
    response_time = []
    min_request_generation_interval = 0
    max_request_timeout = 30
    sensor_admission_timeout = 3
    node_down_sensor_hold_duration = 0
    # in monitor
    response_time_accumulative = []
    current_time = []
    current_time_ts = []
    node_op = []
    battery_charge = []
    battery_history = []
    cpuUtil = []
    cpu_temp = []
    cpu_freq_curr = []
    cpu_freq_max = []
    cpu_freq_min = []
    cpu_ctx_swt = []
    cpu_inter = []
    cpu_soft_inter = []
    memory = []
    disk_usage = []
    disk_io_usage = []
    bw_usage = []

    power_usage = []
    throughput = []
    throughput2 = []
    # network_name_server = {}

    logger.info('reset:stop')


def usb_eth_port_control(command):
    logger.info(f'usb_eth_port_control: command={command} start...')

    cmd =""
    # USB chip control
    #Pi 3B+: https://learn.pi-supply.com/make/how-to-save-power-on-your-raspberry-pi/#disable-wi-fi-bluetooth
    #https://core-electronics.com.au/guides/disable-features-raspberry-pi/#USB
    #Find the name of USB device by "lsblk" cmd and then you can find it in /dev/ 
    #To safety unmount USB device so it does not appear in lsusb results (despite the device being physically detached), run sudo apt install eject; sudo eject /dev/name_of_device_found_in_previous_cmd
    #watch USB power management  by "lsusb -v|grep -i power"
    #Linux USB power management https://www.kernel.org/doc/Documentation/usb/power-management.txt

    #get usb devices directory for a specific product:vendor id. Ref: https://github.com/movidius/ncsdk/blob/ncsdk2/extras/docker/docker_cmd.sh
    #all_devices=$(lsusb -d 03e7:f63b  | cut -d" " -f2,4 | cut -d":" -f1 |  sed 's/ /\//' | sed 's/^/\/dev\/bus\/usb\//')
    #devices_number=$(lsusb -d 03e7:f63b  | wc -l)
    #--device=$dev
    
    if utils.what_device_is_it('raspberry pi 3'):
        logger.info('temporarily turn USB hubs (and Ethernet port) on for accelerators detection')
        
        cmd = "echo '1-1' |sudo tee /sys/bus/usb/drivers/usb/bind"   
        #Below cmd works briefly then the power switches back on to the ports (although it does not seem), investigations are underway to find a solution. 
        # cmd = "sudo uhubctl -l 1-1 -a on"
        out, error = utils.shell(cmd)
        if error:
            logger.error(out + error)
        #verify USB status by sudo lsusb -v  2>&- | grep -E  'Bus 00|MaxPower'

        #wait a sec
        time.sleep(1)
        logger.warning('USB turn on/off on Pi 3 may not always function!')

        #Note: For the Raspberry Pi 3 and 4 the power on all USB ports is ganged together through port 2, so unfortunately it is not possible to power up/down an individual USB port. Ref: https://funprojects.blog/2021/04/26/control-usb-powered-devices/
        #turn on USBs if an accelerator device like TPU is detected.
        if (utils.attached_tpu_detected() and command == 'on_if_attachement') or command == 'on':
            cmd = "echo '1-1' |sudo tee /sys/bus/usb/drivers/usb/bind"    
            # cmd = "sudo uhubctl -l 1-1 -a on"

            #USB power status new
            #if TPU NOT attached, 
            #Total= 6 mA
            #if TPU is attached,
            #Total= 504 mA

        else:
            #turn off USBs
            cmd = "echo '1-1' |sudo tee /sys/bus/usb/drivers/usb/unbind"
            # cmd = "sudo uhubctl -l 1-1 -a off"

            #USB power status new
            #Total= 2 mA

    #Pi 4B: Ref: https://core-electronics.com.au/guides/disable-features-raspberry-pi/#USB
    elif utils.what_device_is_it('raspberry pi 4'):
        logger.info('temporarily turn USB hubs on for accelerators detection')
        
        cmd = "sudo uhubctl -l 1-1 -a on"    
        out, error = utils.shell(cmd)
        if error:
            logger.error(out + error)
        #verify USB status by sudo lsusb -v  2>&- | grep -E  'Bus 00|MaxPower'

        #wait a sec
        time.sleep(1)

        #Note: For the Raspberry Pi 3 and 4 the power on all USB ports + Ethernet is ganged together through port 2, so unfortunately it is not possible to power up/down an individual USB port. Ref: https://funprojects.blog/2021/04/26/control-usb-powered-devices/
        #turn on USBs if an attached accelerator like TPU is detected.
        if (utils.attached_tpu_detected() and command == 'on_if_attachement') or command == 'on':
        # if utils.attached_tpu_detected():
            #turn on
            cmd = "sudo uhubctl -l 1-1 -a on"

            #USB power status new
            #if TPU is attached to USB3 port:
            #Total= 996 mA
            #if TPU is attached to USB2 port:
            #Total= 598 mA
            #if TPU is not attached:
            #Total= 100 mA

        else:
            #turn off
            cmd = "sudo uhubctl -l 1-1 -a off"
            #USB status
            '''
            sudo lsusb -v  2>&- | grep -E  'Bus 00|MaxPower'
            Bus 002 Device 001: ID 1d6b:0003 Linux Foundation 3.0 root hub
                MaxPower                0mA
            Bus 001 Device 002: ID 2109:3431 VIA Labs, Inc. Hub
                MaxPower              100mA
            Bus 001 Device 001: ID 1d6b:0002 Linux Foundation 2.0 root hub
                MaxPower                0mA '''

            #total required power for USBs: https://funprojects.blog/2021/04/26/control-usb-powered-devices/
            
            #USB power status new
            #Total= 100 mA
            
            #Another solution to block power to USB ports through USB power conroller https://forums.raspberrypi.com/viewtopic.php?t=93463

    #Jetson Nano
    elif utils.what_device_is_it('nvidia jetson nano'):
        #Jetson Nano: bus 2-1 is the usb3.0 bus corresponding to the 4 ports on the dev kit. https://github.com/mvp/uhubctl/issues/258#issue-669452920

        logger.info('temporarily turn USB hubs on for accelerators detection')
        
        # cmd = "echo '2-1' |sudo tee /sys/bus/usb/drivers/usb/bind"    
        cmd = "sudo uhubctl -l 2-1 -a on"
        out, error = utils.shell(cmd)
        if error:
            logger.error(out + error)
        #verify USB status by sudo lsusb -v  2>&- | grep -E  'Bus 00|MaxPower'

        #wait a sec
        time.sleep(1)

        #turn on USBs if an attached device like TPU is detected.
        if (utils.attached_tpu_detected() and command == 'on_if_attachement') or command == 'on':
        # if utils.attached_tpu_detected():
            #turn on
            # cmd = "echo '2-1' |sudo tee /sys/bus/usb/drivers/usb/bind"
            cmd = "sudo uhubctl -l 2-1 -a on"

            #USB power status new
            #if TPU NOT attached, 
            #Total= 100 mA
            #if TPU is attached,
            #Total= 324 mA
        else:
            #turn off
            # cmd = "echo '2-1' |sudo tee /sys/bus/usb/drivers/usb/unbind"
            cmd = "sudo uhubctl -l 2-1 -a off"

            #USB power status new
            #Total= 100 mA 

    else:
        logger.warning('Device is not pi 3, 4 or jetson nano, so no USB is turned off/on')
    

    #usb cmd
    logger.info(cmd)

    #run           
    out, error = utils.shell(cmd)
    if error:
        logger.error(out + error)
        logger.warning('The USB device status may have been already equal to the requested status (or/off).')

    #verify USB power status
    #bash cmd
    #(sudo lsusb -v 2>&- | grep MaxPower | grep -o -E '[0-9]+' ) | awk '{ sum += $1} END {print "\nTotal= " sum " mA"}'
    cmd_verify = ''' (sudo lsusb -v 2>&- | grep MaxPower | grep -o -E \'[0-9]+\' ) | awk \'{ sum += $1} END {print "\\nTotal= " sum " mA"}\' '''
    results, err = utils.shell(cmd_verify)
    if err:
        logger.error('Device USB power new status\n' + err)
    else:
        logger.info('Device USB power new status: ' + results)


#test api
@app.route('/test', methods=['GET', 'POST'])
def test():
    return 'Test success on \n'


if __name__ == "__main__":
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s [%(threadName)s] [%(levelname)s] %(message)s')
    # default mode is append 'a' to existing log file. But, 'w' is write from scratch
    if not os.path.exists(log_path): os.makedirs(log_path)
    fileHandler = logging.FileHandler(log_path + '/' + os.path.basename(__file__).split('.')[0] + '.log', mode='w')
    fileHandler.setFormatter(formatter)
    fileHandler.setLevel(logging.DEBUG)

    consoleHandler = logging.StreamHandler()
    consoleHandler.setFormatter(formatter)
    consoleHandler.setLevel(logging.DEBUG)

    logger.addHandler(fileHandler)
    logger.addHandler(consoleHandler)

 

    # setup file exists?
    dir_path = os.path.dirname(os.path.realpath(__file__))
    if os.path.exists(dir_path + "/setup.py"):

        # run launcher if coordinator
        for node in setup.nodes:
            # find this node in nodes
            position = node[0]
            name = node[1]
            if name == socket.gethostname():
                # verify if this node's position is COORDINATOR
                if position == "COORDINATOR":
                    # just MASTER and STANDALONE are eligible to be a COORDINATOR                    
                    if setup.plans[name]["node_role"] == "MASTER" or setup.plans[name]["node_role"] == "STANDALONE":
                        logger.info('MAIN: Node position is coordinator')

                        #if it is automatically running as daemon but no test is planned, exit
                        if len(setup.test_name) == 0:
                            logger.info('exit as no test is planned in test_name')
                            sys.exit()
                        
                        #cal launcher
                        thread_launcher = threading.Thread(target=launcher, args=(node,))
                        thread_launcher.name = "launcher"
                        thread_launcher.start()
                        break
                    else:
                        logger.error('MAIN: Node role in its plan must be MASTER or STANDALONE')
                else:
                    logger.info('MAIN: Node position is ' + position)
    else:
        logger.info('MAIN: No setup found, so wait for a coordinator')

    try:
        # threads=number of requests can work concurrently in waitress; exceeded requests wait for a free thread
        serve(app, host='0.0.0.0', port='5000', threads=waitress_threads)
        
    except OSError as e:
        print(str(e) + '\nMake sure this port is not already given to someone else, e.g., docker ps -a.')
