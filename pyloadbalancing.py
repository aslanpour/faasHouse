import datetime
import pymanifest
import yaml
import json
import pykubectl
import copy
import time
import utils

#pick and run a handler
def plan(**kwargs):
    results = None
    msg =""
    error= ""
    msg += '\nplan: started'

    if kwargs['type']['handler']:
        #linkerd or envoy
        if kwargs['type']['handler'] == 'linkerd' or kwargs['type']['handler'] == 'envoy':
            results, msg_child, error = handler(**kwargs)
            msg += msg_child

        #openfaas-gateway
        elif kwargs['type']['handler'] == 'openfaas-gateway':
            #do nothing
            results, msg_child, error = kwargs, 'Load balancing is handled by OpenFaaS or Kubernetes default', ''
            msg += msg_child
        else:
            error += 'The load balancing handler= ' + kwargs['type']['handler'] + ' is not defined'
    else:
        error += 'Load balancing type must be given as key type[handler]'

    msg += '\nplan: done'

    #update backends
    kwargs['backend_discovery']['backends'] = results

    return kwargs, msg, error


#initialize_handler
def initialize_handler(**kwargs) :
    results = None
    msg =""
    error= ""
    msg += '\ninitialize_handler: started'

    #handler linkerd 
    if kwargs['type']['handler'] == 'linkerd':
        #deploy a gateway deployment and service (or just an openfaas function)
        deployment = kwargs['deployments']['Function-linkerd']

        #manifest builder
        manifest, msg_child, error_child = pymanifest.manifest_builder(**deployment)
        msg += msg_child
        error += error_child
        if error_child:
            return kwargs, msg, error

        kwargs['deployments']['Function-linkerd']['manifest'] = copy.deepcopy(manifest)

        #deploy
        apply, msg_child, error_child = pykubectl.apply(**deployment)
        msg += msg_child
        error += error_child
        if error_child:
            return kwargs, msg, error

    #handler envoy
    elif kwargs['type']['handler'] == 'envoy':
        #deploy a Service, use its info to design envoy.yaml and use envoy.yaml to deploy a Deployment.
        #also, obtain and set gateway ip by envoy Service ip

        #[Servicre-envoy]

        #clean up
        msg += 'clean up service and deployment leftovers'

            #Service-envoy
        input_dict = {'operation': 'safe-delete', 'api_version': kwargs['deployments']['Service-envoy']['api_version'], 
                'kind': kwargs['deployments']['Service-envoy']['kind'],
                'object_name': kwargs['deployments']['Service-envoy']['object_name'], 
                'namespace': kwargs['deployments']['Service-envoy']['namespace']}
        print('exec111111111111111111')
        apply, msg_child, error_child = pykubectl.apply(**input_dict)
        print('exec22222222222')
        msg += msg_child
        error += error_child

            #Deployment-envoy
        input_dict = {'operation': 'safe-delete', 'api_version': kwargs['deployments']['Deployment-envoy']['api_version'], 
                'kind': kwargs['deployments']['Deployment-envoy']['kind'],
                'object_name': kwargs['deployments']['Deployment-envoy']['object_name'], 
                'namespace': kwargs['deployments']['Deployment-envoy']['namespace']}
        print('safe-delete envoy start ' + str(input_dict))
        print('exec33333333333')
        apply, msg_child, error_child = pykubectl.apply(**input_dict)
        print('exec44444444444444')
        msg += msg_child
        error += error_child

        #manifest builder for service
        manifest, msg_child, error_child = pymanifest.manifest_builder(**kwargs['deployments']['Service-envoy'])

        msg += msg_child
        error += error_child
        if error_child:
            return kwargs, msg, error

        kwargs['deployments']['Service-envoy']['manifest'] = copy.deepcopy(manifest)
        print('exec555555555555555')
        #deploy
        apply, msg_child, error_child = pykubectl.apply(**kwargs['deployments']['Service-envoy'])
        print('exec666666666666666666')
        msg += msg_child
        error += error_child
        if error_child:
            return kwargs, msg, error

        #obtain envoy service ip as gateway for workload_generator. Is pod ip better to reduce traffic to master???
        kwargs['frontends'][0]['listeners']['ip'] = apply['spec']['clusterIP']
        
        print('envoy service deployed (gateway ip is ' + apply['spec']['clusterIP'] + ')')
        

        #[envoy.yaml]
        kwargs, msg_child, error_child = update_envoy_config_file(**kwargs)
        msg += msg_child
        error += error_child
        if error_child:
            return kwargs, msg, error


        #[Deployment-envoy]
        deployment = kwargs['deployments']['Deployment-envoy']

        #manifest builder 
        manifest, msg_child, error_child = pymanifest.manifest_builder(**deployment)
        msg += msg_child
        error += error_child
        if error_child:
            return kwargs, msg, error

        kwargs['deployments']['Deployment-envoy']['manifest'] = copy.deepcopy(manifest)
        print('exec77777777777')
        #deploy
        apply, msg_child, error_child = pykubectl.apply(**kwargs['deployments']['Deployment-envoy'])
        print('exec888888888888888888')
        msg += msg_child
        error += error_child
        if error_child:
            return kwargs, msg, error          


        msg += 'kube_apply success\n'

        return kwargs, msg, error
    
    #openfaas-gateway
    elif kwargs['type']['handler'] == 'openfaas-gateway':
        msg += 'Load balancing handled by openfaas-gateway automatically'
        return kwargs, msg, error
        
    #not found
    else:
        error += 'handler not found'
    
    return kwargs, msg, error


#update_envoy_config_file
def update_envoy_config_file(**kwargs):
    results=None; msg=""; error=""
    msg += '\nupdate_envoy_config_file: started...'

    #read YAML as Json
    with open(kwargs['deployments']['Deployment-envoy']['volumes'][0]['hostPath']['path'], 'r') as stream:
        try:
            envoy_dict=yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            error += '\n' + str(exc)
            return results, msg, error

    #print Json
    # print(json.dumps(envoy_dict, sort_keys=True, indent=4))
    #edit Json

    #check backends' service availability. This is important because sometimes the first discovered service gets replaced by finishing the discovery of all since scheduler may be slow to redeploy functions
    #if envoy. yaml contains invalid endpoints, this uncooradination between scheduler and load balancer is the reason.
    for backend in kwargs['backend_discovery']['backends']:
        #backend info
        input_dict={'api_version': 'v1', 'kind': 'Service', 'operation': 'get-json', 'namespace': 'openfaas-fn', 'object_name': backend['service']}
        service_info = None
        #if not service_info, no Service object is discovered yet for the backend
        while not service_info:
            print('try to read backend services info...')
            service_info, msg_child, error_child = pykubectl.apply(**input_dict)
            if not service_info:
                time.sleep(1)
    print('all backends services are discovered.')


    
    #[backend/Cluster]

    #set clusters in envoy.yaml based on Service ips
    if kwargs['algorithm'] == 'static':
        #build endpoint_list
        endpoint_list = []
        for backend in kwargs['backend_discovery']['backends']:

            #obtain ip and port and weight of the service object associated with the backend info
            input_dict={'api_version': 'v1', 'kind': 'Service', 'operation': 'get-json', 'namespace': 'openfaas-fn', 'object_name': backend['service']}
            service_info = None
            while not service_info:
                print('try to read backend services info...')
                service_info, msg_child, error_child = pykubectl.apply(**input_dict)
                if not service_info:
                    time.sleep(3)


            port = service_info['spec']['ports'][0]['port']
            ip = service_info['spec']['clusterIP']
            weight = backend['weight']

            #create endpoint item
            endpoint_list.append({"endpoint": {
                                        "address": {
                                            "socket_address": {
                                                "address": ip, 
                                                "port_value": port}}}, 
                                "load_balancing_weight": weight})
        #update clusters
        envoy_dict["static_resources"]["clusters"][0]["load_assignment"]["endpoints"][0]["lb_endpoints"] = endpoint_list
        #cluster name
        envoy_dict["static_resources"]["clusters"][0]['name'] = kwargs['frontends'][0]['listeners']['cluster']
        envoy_dict["static_resources"]["clusters"][0]['load_assignment']['cluster_name'] = kwargs['frontends'][0]['listeners']['cluster']

        #lb_policy (round_robin is default or least_request)
        envoy_dict["static_resources"]["clusters"][0]['lb_policy'] = kwargs['lb_policy']

        #additional config for least_request
        if kwargs['lb_policy'].lower() == 'least_request':
            policy_notice = 'WARNING: lb_policy = ' + kwargs['lb_policy'] + ', so make sure weights of backends are equal; otherwise weighted least_request is applied.'
            msg += policy_notice
            print(policy_notice)
            
            #set least_request_lb_config
            #choice_count: sets the number of backends to pick randomly (default is 2) to apply power of two choices (P2C)
            #active_request_bias: (defaults to 1.0), if all host weights are not equal it takes effect. 
            #It involves weights upon choosing a least_request backend. If set to 0.0, least_request acts  like round robin. 
            ##active_request_bias is not taking affect yet

            envoy_dict["static_resources"]["clusters"][0]['least_request_lb_config'] = {
                'choice_count': kwargs['backend']['choice_count'],
                
            }
            #'active_request_bias': float(kwargs['backend']['active_request_bias'])

        #remove leftover clusters
        clusters_len = len(envoy_dict["static_resources"]["clusters"])
        while True:
            if len(envoy_dict["static_resources"]["clusters"]) > 1:
                del envoy_dict["static_resources"]["clusters"][-1]
            else:
                break

    #obtain clusters (backend) for local algorithm
    #a cluster per backend
    elif kwargs['algorithm'] == 'local':
        clusters = []
        for backend in kwargs['backend_discovery']['backends']:
            #obtain ip and port and weight
            input_dict={'api_version': 'v1', 'kind': 'Service', 'operation': 'get-json', 'namespace': 'openfaas-fn', 'object_name': backend['service']}
            service_info = None
            while not service_info:
                print('try to read backend services info...')
                service_info, msg_child, error_child = pykubectl.apply(**input_dict)
                if not service_info:
                    time.sleep(3)


            port = service_info['spec']['ports'][0]['port']
            ip = service_info['spec']['clusterIP']
            weight = backend['weight']

            #clusters backend
            cluster = {}
            cluster['name'] = backend['service']
            cluster['type'] = 'static'
            cluster['max_requests_per_connection'] = 1
            cluster['lb_policy'] = 'round_robin'
            load_assignment = {}
            #load_assignment cluster_name
            load_assignment['cluster_name'] = backend['service']

            lb_endpoints = []
            lb_endpoint = {}
            
            
            lb_endpoint = {"endpoint": {
                                    "address": {
                                        "socket_address": {
                                            "address": ip, 
                                            "port_value": port}}}, 
                            "load_balancing_weight": weight}
            
            lb_endpoints.append(lb_endpoint)
            
            #load_assignment endpoints
            load_assignment['endpoints'] = [
                {'lb_endpoints': lb_endpoints}
            ]

            cluster['load_assignment'] = load_assignment
            #append
            clusters.append(cluster)

        #clusters
        envoy_dict["static_resources"]["clusters"] = clusters
        
    else:
        error += 'algorithm ' + kwargs['algorithm'] + ' not found\n'
        return kwargs, msg, error



    #[listeners]    frontend   
    #address = 0.0.0.0         
    envoy_dict["static_resources"]['listeners'][0]['address']['socket_address']['port_value'] = str(kwargs['frontends'][0]['listeners']['port'])
    
    #static algorithm
    if kwargs['algorithm'] == 'static':
        #route match path or headers or both
        if kwargs['frontends'][0]['listeners']['route_by'] == 'path':
            #path
            routes = []
            route = {'match': kwargs['frontends'][0]['listeners']['match'], 
                'route': {'weighted_clusters': {'clusters': [{'name': kwargs['frontends'][0]['listeners']['cluster'], 'weight': 100}], 'runtime_key_prefix': 'routing.traffic_split.service'}, }
                }
            routes.append(route)

            print(json.dumps(envoy_dict["static_resources"]['listeners'][0], indent=4))
            envoy_dict["static_resources"]['listeners'][0]['filter_chains'][0]['filters'][0]['typed_config']['route_config']['virtual_hosts'][0]['routes'] = routes
        else:
            error += 'route error'
            return kwargs, msg, error


    #local algorithm
    #set routes per function path/header
    elif kwargs['algorithm'] == 'local':
        routes = []
        #assume functions name are equal to backend service ???
        for backend in kwargs['backend_discovery']['backends']:
            if kwargs['frontends'][0]['listeners']['route_by'] == 'path':
                #route, match '/function_name' ??? only? cal http://ip:port/w2-ssd
                #rewrite /function to /
                route = {'match': {'prefix': '/' + backend['service']}, 
                        'route': {
                            'weighted_clusters': {
                                'clusters': [{
                                    'name': backend['service'], 
                                    'weight': 100}], 
                                'runtime_key_prefix': 'routing.traffic_split.service'}, 
                            'prefix_rewrite': '/'}
                }

            else:
                error += 'route_by ' + kwargs['frontends'][0]['listeners']['route_by'] + ' not implemented'
                return kwargs, msg, error

            #append
            routes.append(route)
        #routes
        envoy_dict["static_resources"]['listeners'][0]['filter_chains'][0]['filters'][0]['typed_config']['route_config']['virtual_hosts'][0]['routes'] = routes
    
    #add envoy to load_balancing
    kwargs['deployments']['Deployment-envoy']['envoy-config'] = copy.deepcopy(envoy_dict)

    #save as Yaml
    with open(kwargs['deployments']['Deployment-envoy']['volumes'][0]['hostPath']['path'], 'w') as file:
        yaml.dump(envoy_dict, file, default_flow_style=False, sort_keys=True)

    #copy to host that will deploy envoy
    if kwargs['deployments']['Deployment-envoy']['nodeName'] != 'master':
        #e.g., scp /home/ubuntu/envoy.yaml ubuntu@10.0.0.91:/home/ubuntu/envoy.yaml
        cmd = ('scp ' + kwargs['deployments']['Deployment-envoy']['volumes'][0]['hostPath']['path'] + ' ' 
        + kwargs['deployments']['Deployment-envoy']['host_user_ip'] + ':' + kwargs['deployments']['Deployment-envoy']['volumes'][0]['hostPath']['path'])
        try:
            out, error_child = utils.shell(cmd)
            if error_child:
                error += 'scp ' + error_child
        except Exception as e:
            print('scp error ' + str(e))
            error += str(e)

    msg += '\nenvoy.yaml is updated and the configuration file is stored and is kept as dict in envoy-config key.'
    return kwargs, msg, error

#handler
def handler(**kwargs):
    results=None; msg=""; error=""
    msg += '\linkerd_handler: started'

    #get algorithm name
    if not 'algorithm' in kwargs: 
        error += '\nNo item as algorithm found in kwargs given to plan'
        return results, msg, error
    else:
        algorithm_name = kwargs['algorithm']

    

    #call an algorithm
    if algorithm_name == "even" or algorithm_name == 'local':
        updated_backend_list, msg_child, error = plan_even(**kwargs)
        msg += msg_child
    elif algorithm_name == 'static':
        updated_backend_list, msg_child, error = plan_static(**kwargs)
        msg += msg_child
    else:
        error += "\nalgorithm_name=" + algorithm_name + "NOT found"
        return results, msg, error

    msg += '\linkerd_handler: done'

    #return an updated list of backends
    return updated_backend_list, msg, error


#run static algorithm
#Sample --> 'backends':[{'service':'w5-ssd','weight': 1000}, {'service':'w6-ssd','weight': 0}]
def plan_static(**kwargs):
    start = datetime.datetime.now(datetime.timezone.utc).astimezone().timestamp()
    results = None
    msg =""
    error= ""

    msg += 'plan_static: algorithm started.'

    #get backends list
    backends_list = []
    if 'backend_discovery' in kwargs and 'backends' in kwargs['backend_discovery']:
        backends_list = kwargs['backend_discovery']['backends']
    else:
        error += '\nNo backends found in kwargs'
        return results, msg, error

    msg += '\nplan_static: backends_before_plan: ' + str(backends_list)

    #plan
    #do nothing
    msg += '\nNo change in weights'

    end = datetime.datetime.now(datetime.timezone.utc).astimezone().timestamp()
    elapsed = end - start
    msg += "\nelapsed= " + str(round(elapsed,2))
    msg += '\nplan_static: backends_after_plan: ' + str(backends_list)

    results = backends_list
    #return an updated list of backends
    return results, msg, error


#run even algorithm
#Sample --> 'backends':[{'service':'w5-ssd','weight': 1000}, {'service':'w6-ssd','weight': 0}]
def plan_even(**kwargs):
    start = datetime.datetime.now(datetime.timezone.utc).astimezone().timestamp()
    results = None
    msg =""
    error= ""

    msg += 'event_plan: algorithm even started.'
    #get backends list
    backends_list = []
    if 'backend_discovery' in kwargs and 'backends' in kwargs['backend_discovery']:
        backends_list = kwargs['backend_discovery']['backends']
    else:
        error += '\nNo backends found in kwargs'
        return results, msg, error

    msg += '\nplan_even:backends_before_plan: ' + str(backends_list)

    #plan
    #give all backends equal weights
    for i in range(len(backends_list)):
        #e.g., {'service':'w5-ssd','weight': 1000}
        backend = backends_list[i]

        #calculate the weight
        backend['weight'] = int(1000 / len(backends_list))

        backends_list[i]=backend

    end = datetime.datetime.now(datetime.timezone.utc).astimezone().timestamp()
    elapsed = end - start
    msg += "\nelapsed= " + str(round(elapsed,2))
    msg += '\nplan_even:backends_after_plan: ' + str(backends_list)

    results = backends_list
    #return an updated list of backends
    return results, msg, error


#deploy gateway function
def deploy_gateway_function(**kwargs):
    

    results=None; msg=""; error=""
    msg += 'deploy_gateway_function: started'

    #build function manifest
    gateway_function = kwargs
    manifest, msg_child, error = pymanifest.manifest_builder(**gateway_function)
    msg += msg_child
    if error:
        return manifest, msg, error

    gateway_function['manifest'] = manifest

    #deploy function
    gateway_function['operation'] = 'safe-patch'     
    results, msg_child, error = pykubectl.apply(**gateway_function)
    msg += msg_child
    msg += '\ndeploy_gateway_function: stopped'
    return results, msg, error




#by disabling USB on a device where a function is running and has loaded TPU model, the container (not Pod) will fail and restart.
#get acceleerators on a node
def has_accelerators(node_name, **kwargs):
    results=None; msg=""; error = ""
    results = []

    #verify if accelerators key exists
    if not 'accelerators' in kwargs:
        error += 'An accelerators key is missing from **kwargs'
        return results, msg, error

    #search
    #e.g., accelerators = {'w5': ['gpu', 'tpu']} is set by setup.py
    accelerators = kwargs['accelerators']
    if 'tpu' in accelerators[node_name]:
        results.append('tpu')
    elif 'gpu' in accelerators[node_name]:
        results.append('gpu')
    else:
        error += 'accelerators[node_name] found a value as ' + str(accelerators[node_name]) + ' that is not defined here.'

    return results, msg, error

    #by sending config read request
    # res = requests.get('http://10.0.0.90:31112/function/w5-ssd/config/read', json={})
    # if res.ok:
    #     config = res.json()

#execute
def execute(**kwargs):
    results=None; msg=""; error = ""

    #initialize the handler deployments in the first round
    if kwargs['load_balancing_round'] == 0:
        result_child, msg_child, error_child = initialize_handler(**kwargs)

        if error_child:
            error += 'initialize_handler failed. error= \n' + str(error_child)
            return kwargs, msg, error
        else:
            kwargs = result_child
            msg += 'initialize_handler success\n'


    if kwargs['type']['adaptive'] == False:
        msg += '\nNonadaptive load balancer, so no execution, except for the first initialization.'
        return kwargs, msg, error
    print('execute33333333333333333')
    #[build manifest]
    deployments=[]

    #handler openfaas-gateway
    if kwargs['type']['handler'] == 'openfaas-gateway':
        #do nothing
        return kwargs, msg, error
    
    #handler envoy
    elif kwargs['type']['handler'] == 'envoy':
        #do nothing
        return kwargs, msg, error


    #handler linkerd
    elif kwargs['type']['handler'] == 'linkerd':
        #template a trafficsplit resource
        deployment = kwargs['deployments']['TrafficSplit']
        #add new backends 
        deployment['backends'] = kwargs['backend_discovery']['backends']

        msg +='\nDeploy TrafficSplit...'
        #build manifest for new tradfficsplit, based on the especified 'Kind'
        manifest, msg_child, error_child = pymanifest.manifest_builder(**deployment)
        
        #update config with new deployment
        if not error_child:
            deployment['manifest'] = manifest
            deployments.append(deployment)
            kwargs['deployments']['TrafficSplit'] = copy.deepcopy(deployment)
        else:
            error +='load_balancing manifest builder failed \n' + str(error_child)
            error +='load_balancing manifest builder failed \n' + str(msg_child)

    else:
        error += 'handler not found'


    #[action]

    

    #apply
    msg += 'apply...'

    for deployment in deployments:
        print('exec3333311111111111111111')
        print(str(deployment))
        apply, msg_child, error_child = pykubectl.apply(**deployment)
        if not error:
            msg += 'kube_apply success\n' + msg_child
        else:
            error +='load_balancing execution failed. error= \n' + str(error_child)
            msg +='load_balancing execution failed. msg= \n' + str(msg_child)

    msg += '\nexecutor done.'
    return kwargs, msg, error


