import time
import numpy as np
import random

def what_device_is_it(name):
    import io
    name = name.lower()
    try:
        with io.open('/sys/firmware/devicetree/base/model', 'r') as m:
            if name in m.read().lower(): return True
    except Exception: pass
    return False

def attached_tpu_detected():
    usb_devices, error = shell('lsusb')
    if error: 
        print('ERROR:' + error, flush=True)
        return False
    else:
        #or by vendor:product through lsusb -d 0x1a6e:0x089a
        return True if 'Google Inc.' in usb_devices or 'Global Unichip Corp.' in usb_devices else False

#password= "", "any_password", "prompt"
def shell(cmd, password="", timeout=30):
    import subprocess
    output = ""
    error = ""
    popen = False
    if password:
        popen= True
    #else: check_output

    #run cmd
    try:
        #without password
        if not popen:
            #run
            output= subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT, timeout=timeout).decode("utf-8") 
        #with password
        else:
            #prompt password if required
            if password == "prompt":
                import getpass
                password = getpass.getpass(prompt='sudo password: ')
            #run
            cmd = cmd.split()
            p = subprocess.Popen(cmd, shell=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE,  stdin=subprocess.PIPE)
            output, error = p.communicate(input=(password+'\n').encode(),timeout=timeout)
            output = output.decode('utf-8')
            error = error.decode('utf-8')
    except subprocess.CalledProcessError as e:
        if not popen:
            error += 'ERROR: ' + e.output.decode("utf-8")
        else:
            error += 'ERROR: ' + str(e)
            p.kill()
    except subprocess.TimeoutExpired as e:
        if not popen:
            error += 'ERROR: ' + e.output.decode("utf-8")
        else:
            error += 'ERROR: ' + str(e)
            p.kill()
    except Exception as e:
        if not popen:
            error += 'ERROR: ' + e.output.decode("utf-8")
        else:
            error += 'ERROR: ' + str(e)
            p.kill()

    return output, error


######
import os
dir_path = os.path.dirname(os.path.realpath(__file__))
if os.path.exists(dir_path + "/pykubectl.py"): import pykubectl


#patch a function
def openfaas_function_customizations(logger, function_name, function_worker_name, accelerators, replacement_strategy, affinity, model_inference_model="", namespace='openfaas-fn', operation='get-json', patch_type='application/merge-patch+json'):
    results = None; msg = ""; error=""
    attempts_if_object_not_exists = 3
    delay_between_attempts = 5
    
    try:
        #get Deployment of the function as json
        manifest = {}

        patch_info = {
            "api_version": "apps/v1",
            "kind": "Deployment",
            "object_name": function_name,
            "manifest": manifest,
            "namespace": namespace,
            "operation": operation,
        }
        logger.info(f'utils.openfaas_function_customizations start... \npatch_info={patch_info}')

        #get
        while attempts_if_object_not_exists >= 0:
            attempts_if_object_not_exists -=1

            try:
                deployment_dict, msg, error = pykubectl.apply(**patch_info)
                if error or not deployment_dict:                
                    logger.exception(f"utils.openfaas_function_customizations.pykubectl.apply FAILED A \nerror={error}\npatch_info{patch_info}")

            except Exception as e:
                
                logger.exception(f"utils.openfaas_function_customizations.pykubectl.apply FAILED B \nerror={error}\npatch_info={patch_info}")
                logger.exception(f"utils.openfaas_function_customizations.pykubectl.apply EXCEPTION wait {delay_between_attempts} sec for another try ... ")
                time.sleep(delay_between_attempts)
            else:
                if not error and deployment_dict != None:
                    logger.info(f'Got deployment_dict={deployment_dict}')
                    break
                else:
                    
                    logger.exception(f"utils.openfaas_function_customizations.pykubectl.apply ERROR wait {delay_between_attempts} sec for another try ... ")
                    time.sleep(delay_between_attempts)

        #To avoid this error: "message":"Operation cannot be fulfilled on deployments.apps \\"homo1-ssd\\": the object has been modified; please apply your changes to the latest version and try again","reason":"Conflict" 409
        #remove instance specific data. Ref. https://stackoverflow.com/questions/51297136/kubectl-error-the-object-has-been-modified-please-apply-your-changes-to-the-la 
        logger.info('Delete creationTimestamp, resourceVersion, and uid from metadata section in deployment_dict')
        

        del deployment_dict['metadata']['creationTimestamp']
        del deployment_dict['metadata']['resourceVersion']
        del deployment_dict['metadata']['uid']


        #get main container (in case multi-container is enables using like service mesh side car)
        index=-1
        for container in deployment_dict['spec']['template']['spec']['containers']:
            if container['name'] == function_name:
                index = deployment_dict['spec']['template']['spec']['containers'].index(container)
                break
        if index ==-1:
            error += '\nA container with the name of function was not found in the deployment'
            return results, msg, error

        
        #customize fields

        #imagepullPolicy = Never. Do this carefully???
        deployment_dict['spec']['template']['spec']['containers'][index]['imagePullPolicy'] = 'Never'
        # deployment.spec.template.spec.containers[container_id].image_pull_policy = 'Never'
    
        #allowPrivilegeEscalation = True
        #privileged = True
        #runAsUser = 0
        # readOnlyRootFilesystem = False (openfaas adds this to functions, so include this to avoid loosing it upon patching securityContext)
        deployment_dict['spec']['template']['spec']['containers'][index]['securityContext'] = {"allowPrivilegeEscalation": True,
                                                                                            "privileged": True,
                                                                                                "runAsUser": 0,
                                                                                                "readOnlyRootFilesystem": False,
                                                                                                }

        #volumes hostPath
        deployment_dict['spec']['template']['spec']['volumes'] = [{"name": "usb-devices", "hostPath": {"path": "/dev/bus/usb"}}]
        # deployment.spec.template.spec.volumes = [{"name": "usb-devices", "hostPath": {"path": "/dev/bus/usb"}}]
        #'{"spec": {"template": {"spec": {"volumes": [{"name": "usb-devices", "hostPath": {"path": "/dev/bus/usb"}}]}}}}'

        #volumeMounts mountPath
        deployment_dict['spec']['template']['spec']['containers'][index]['volumeMounts'] = [{"mountPath": "/dev/bus/usb", "name": "usb-devices"}]
        # deployment.spec.template.spec.containers[container_id].volumeMounts = [{"mountPath": "/dev/bus/usb", "name": "usb-devices"}]
        #'{"spec": {"template": {"spec": {"containers": [{"name": "ssd-tpu", "volumeMounts":[{"mountPath": "/dev/bus/usb", "name": "usb-devices"}]}]}}}}'
        
        #env??????????????
        '''- name: REDIS_SERVER_PORT
            value: "3679"
            - name: read_timeout
            value: 15s
            - name: write_debug
            value: "true"
            - name: COUNTER
            value: "0"
            - name: REDIS_SERVER_IP
            value: 10.43.189.161
            - name: exec_timeout
            value: 15s
            - name: handler_wait_duration
            value: 15s
            - name: version
            value: "1"
            - name: write_timeout
            value: 15s'''

        deployment_dict['spec']['template']['spec']['containers'][index]['env'].append({'name': 'MODEL_PRE_LOAD', 'value': 'yes', 'value_from': None})
        #???these are not configurable from setup.py
        model_run_on = 'cpu'
        model_cpu_workers = 4
        flask_waitress_threads = 4
        if function_worker_name in accelerators: 
            if 'tpu' in accelerators[function_worker_name]:
                model_run_on = 'tpu'
                model_cpu_workers = 1
                flask_waitress_threads = 1
            elif 'gpu' in accelerators[function_worker_name]:
                model_run_on = 'gpu'
                model_cpu_workers = 1
                flask_waitress_threads = 4
        else:
            logger.error('ERROR: ' + function_worker_name + ' not found in accelerator= ' + str(accelerators))
            
        deployment_dict['spec']['template']['spec']['containers'][index]['env'].append({'name': 'MODEL_RUN_ON', 'value': model_run_on, 'value_from': None})
        #???
        deployment_dict['spec']['template']['spec']['containers'][index]['env'].append({'name': 'MODEL_CPU_WORKERS', 'value': str(model_cpu_workers), 'value_from': None})
        deployment_dict['spec']['template']['spec']['containers'][index]['env'].append({'name': 'WAITRESS_THREADS', 'value': str(flask_waitress_threads), 'value_from': None})

        deployment_dict['spec']['template']['spec']['containers'][index]['env'].append({'name': 'NODE_NAME', 'value': None, 'valueFrom': {'fieldRef': {'apiVersion': 'v1', 'fieldPath': 'spec.nodeName'}}})
        deployment_dict['spec']['template']['spec']['containers'][index]['env'].append({'name': 'POD_NAME', 'value': None, 'valueFrom': {'fieldRef': {'apiVersion': 'v1', 'fieldPath': 'metadata.name'}}})
        deployment_dict['spec']['template']['spec']['containers'][index]['env'].append({'name': 'POD_NAMESPACE', 'value': None, 'valueFrom': {'fieldRef': {'apiVersion': 'v1', 'fieldPath': 'metadata.namespace'}}})
        deployment_dict['spec']['template']['spec']['containers'][index]['env'].append({'name': 'POD_IP', 'value': None, 'valueFrom': {'fieldRef': {'apiVersion': 'v1', 'fieldPath': 'status.podIP'}}})
        deployment_dict['spec']['template']['spec']['containers'][index]['env'].append({'name': 'POD_IPS', 'value': None, 'valueFrom': {'fieldRef': {'apiVersion': 'v1', 'fieldPath': 'status.podIPs'}}})
        deployment_dict['spec']['template']['spec']['containers'][index]['env'].append({'name': 'POD_HOST_IP', 'value': None, 'valueFrom': {'fieldRef': {'apiVersion': 'v1', 'fieldPath': 'status.hostIP'}}})
        deployment_dict['spec']['template']['spec']['containers'][index]['env'].append({'name': 'POD_UID', 'value': None, 'valueFrom': {'fieldRef': {'apiVersion': 'v1', 'fieldPath': 'metadata.uid'}}})

        #model_inference_repeat
        if model_inference_model:
            deployment_dict['spec']['template']['spec']['containers'][index]['env'].append({'name': 'MODEL_INFERENCE_REPEAT', 'value': str(model_inference_model), 'value_from': None})

        #rollingUpdate issue in OpenFaaS solved by this.
        if replacement_strategy:
            deployment_dict['spec']['strategy'] = replacement_strategy

        #affinity
        deployment_dict['spec']['template']['spec']['affinity'] = affinity
        
        a='''
            - name: POD_HOST_IP
            valueFrom:
                fieldRef:
                fieldPath: status.hostIP
        '''

        #prepare
        patch_info = {
            "api_version": "apps/v1",
            "kind": "Deployment",
            "object_name": function_name,
            "manifest": deployment_dict,
            "namespace": namespace,
            "operation": 'patch',
            "patch_type": patch_type,
        }
        
        #patch
        logger.info(f'Customize ... \npatch_info={patch_info}')
        patched_deployment, msg_child, error = pykubectl.apply(**patch_info)
        msg += msg_child
        
        if error:
            logger.errir('utils.openfaas_function_customizations ERRORRRRRRRRRRRRRRRRRRRRRR ' + str(function_name))
            
        else:
            logger.info('utils.openfaas_function_customizations Success ' + str(function_name))

        # print(msg)
        # print('ERROR:' +error)
        results = patched_deployment
        return results, msg, error
    
    except Exception as e:
        logger.exception(f'weeeeeeeeeeeeee\n{e}')
        import sys
        sys.exit()

    
    


# openfaas_function_customizations('w5-ssd')
def interarrivals_generator(lower_bound, upper_bound, interarrival_rate, seed):
    np.random.seed(seed)
    random.seed(seed)

    #list of generated interarrivals
    interarrivals = []

    current_time = lower_bound
    while True:
        #Exponential
        interval = np.random.exponential(interarrival_rate, size=1)[0]

        #pick the value only if it is in range lower and upper bounds
        current_time += interval
        if current_time < upper_bound:
            interarrivals.append(current_time)
        else:
            break
 
    interarrivals = np.round(interarrivals).astype(int).tolist()

    return interarrivals


#calculate how long of the experiment time these triggers will cover given the event_duration
def coverage_duration(triggers, upper_bound, lower_bound, event_duration):
    coverage_duration_sum = 0
    for i in range(0, len(triggers) -1 ):
        if triggers[i] < triggers[i+1]:
            #the whole event_duration
            if triggers[i] + event_duration <= triggers[i+1]:
                coverage_duration_sum += event_duration
            else:
                #the diffrences
                coverage_duration_sum += triggers[i+1] - triggers[i]
        else:
            #equal
            pass

        #only the last one (space from upper to last one)
        if i == len(triggers)-2:
            coverage_duration_sum+= upper_bound - triggers[i+1]
    
    print(f'triggers={len(triggers)}, coverage_duration={coverage_duration_sum}')

    return coverage_duration_sum

#convert_interarrivals_to_timeslots
def convert_interarrivals_to_timeslots(triggers, upper_bound, lower_bound, event_duration):
    time_slots = []
    for arrival in triggers:
        time_slots.append({"start": arrival, "end": arrival + event_duration if arrival + event_duration <= upper_bound else upper_bound})

    return time_slots

#produce interarrivals ofr nodes
def active_time_slots_producer(**kwargs):
    #if not enabled, no produce active time_slots
    if not kwargs['enabled']:
        return kwargs, 100
    
    #set inputs
    lower_bound = kwargs['lower_bound']
    upper_bound = kwargs['upper_bound']
    interarrival_rate = kwargs['interarrival_rate']
    event_duration = kwargs['event_duration']
    seed = kwargs['seed_start']

    #determine
    nodes_time_slots = kwargs['time_slots']

    
    coverage_duration_sum_all = 0

    for node_name, time_slots in nodes_time_slots.items():
        seed +=1
        #A interarrivals_generator
        interarrivals = interarrivals_generator(lower_bound, upper_bound, interarrival_rate, seed)

        print("###############events start time:", interarrivals)
        
        #B coverage_duration_sum_all: calculate how long of the experiment time these triggers will cover given the event_duration
        coverage_duration_sum_all = coverage_duration(interarrivals, upper_bound, lower_bound, event_duration)

        #C prepare timeslots
        time_slots = convert_interarrivals_to_timeslots(interarrivals, upper_bound, lower_bound, event_duration)
        nodes_time_slots[node_name] = time_slots

    #output
    coverage_duration_sum_all_percent = (coverage_duration_sum_all/len(nodes_time_slots)) / (upper_bound-lower_bound)
    print(f'coverage_duration_sum={coverage_duration_sum_all/len(nodes_time_slots)}, percent={coverage_duration_sum_all_percent}')

    kwargs['time_slots'] = nodes_time_slots
    return kwargs, coverage_duration_sum_all_percent




# Example usage
'''
#test start time
lower_bound = 0
#test end time
upper_bound = 180 * 60
#expected mean of interarrivals (space between two consecutive events)
interarrival_rate = 2 * 60
#how long each event lasts - constant
event_duration = 5 * 60
#nodes
nodes = {"homo1":[], "homo2":[], "homo3":[], "homo4":[], "homo5":[], "homo6":[], "homo7":[], "homo8":[], "homo9":[], "homo10":[]}
#start seed (increments per node)
seed = 1

nodes, percent = active_time_slots_producer(lower_bound, upper_bound, interarrival_rate, event_duration, nodes, seed)
print(f'nactive_time_slots=\n{nodes}\npercent={percent}')

'''