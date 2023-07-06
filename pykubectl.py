from kubernetes import client,config, dynamic
from kubernetes.client import api_client
import datetime

#[input]
#api_version, e.g., autoscaling/v2, split.smi-spec.io/v1alpha1, openfaas.com/v1, apps/v1
#kind, e.g., Deployment, Function, Pod, HorizontalPodAutoscaler, TrafficSplit
#object_name, e.g., sample_deployment
#namespace, e.g., openfaas-fn
#manifest, e.g., a json object for create, replace or patch operation
#operation, e.g., replace, safe_replace (if object not exists, first create it), create, patch, safe_patch (if object not exists, first create it), delete, get, get-json, get-all, get-all-json
#patch_type, e.g., application/merge-patch+json, application/json-patch+json, application/apply-patch+yaml


#required arguments:
#api_version, kind, object_name (unless operation is get-all), 
#semi-required arguments:
#manifest = {}
#optional arguments:
#namespace="default", operation= "safe_replace", patch_type= "application/merge-patch+json", 

#gets a resource as dict and returns object
import threading
lock = threading.Lock()
def apply(**kwargs):
    with lock:
        object_input = kwargs
        res, msg, err = run(**object_input)
        return res, msg, err
       
def run(**kwargs):
    # with lock:
    
    #start
    error = ""; msg = ""; results = None
    msg += 'Kubectl apply started \nInput:' + ("\n**kwargs= " + str({k:v for k,v in kwargs.items()}) if len(kwargs)>0 else "")
    #check input requirements
    if 'api_version' not in kwargs or 'kind' not in kwargs or ('object_name' not in kwargs and 'get-all' not in kwargs['operation']):
        error += '\nBasic input is not given, i.e., api_version, kind, or object_name'
        return results, msg, error
    #manifest sometimes is required, i.e., for replace, create or  patch operations.
    if 'operation' in kwargs and ('replace' in kwargs['operation'] or 'create' in kwargs['operation'] or 'patch' in kwargs['operation']):
        if 'manifest' not in kwargs or kwargs['manifest'] == {}:
            error += '\nManifest is not given, but is required.'
            return results, msg, error

    #set optional arguments to defaults, if not given by kwargs
    namespace = kwargs['namespace'] if 'namespace' in kwargs else "default"
    operation = kwargs['operation'] if 'operation' in kwargs else "safe_replace"
    patch_type = kwargs['patch_type'] if 'patch_type' in kwargs else "application/merge-patch+json"
    manifest = kwargs['manifest'] if 'manifest' in kwargs else {}

    
    #print the input
    aa =kwargs['object_name'] if 'object_name' in kwargs else ''
    msg +=("Collected arguments:"
        + "\n- api_version= " + kwargs['api_version']
        + "\n- kind= " + kwargs['kind']
        + "\n- object_name= " + aa
        + "\n- namespace= " + namespace
        + "\n- operation= " +  operation
        + "\n- patch_type= " + patch_type)

    
    #client
    try:
        # setup the kubernetes API
        client = dynamic.DynamicClient(api_client.ApiClient(configuration=config.load_kube_config()))
        api_resources = client.resources.get(api_version=kwargs['api_version'], kind=kwargs['kind'])
    except Exception as e:
        error += str(e) + "\nFailed to create a client using the kubeconfig file"
        return results, msg, error

    
    #operation

    #get all objects
    if 'get-all' in operation:
        import json
        all_objects = api_resources.get(namespace=namespace)
        if 'json' in operation:
            all_objects = all_objects.to_dict()
            
        return all_objects, msg, error

    #If the operation is 'replace/patch', verify if the object exists; otherwise a 'create' will be requested automatically if a safe operation is requested.
    object_already_exists = False
    if 'replace' in operation or 'patch' in operation or 'get' in operation or 'safe-delete' in operation:
        #for get operations only
        found_object = None
        

        for item in api_resources.get(namespace=namespace).items:
            #Check each by name
            #either as dictionery/json
            object_under_check = api_resources.get(name=item.metadata.name, namespace=namespace)
            
            object_under_check_name = object_under_check["metadata"]["name"]
            #or as Yaml
            object_under_check_name = item.metadata.name

            if object_under_check_name == kwargs['object_name']:
                object_already_exists = True
                msg += "\nObject " + kwargs['object_name'] + " exists."
                #for get operations only
                found_object = object_under_check
                break
        #check done
        if not object_already_exists:
            msg += "\nObject " + kwargs['object_name'] + " does NOT exists."
            #get operation
            if 'get' in operation:
                # error += '\nObject not found'
                return results, msg, error
        #only for get operation
        else:
            if 'get' in operation:
                if found_object == None:
                    msg += '\nfound_object == None'
                elif 'json' in operation:
                    found_object = found_object.to_dict()
                return found_object, msg, error

    #apply

    #replace or patch
    if 'replace' in operation or 'patch' in operation:
        #object exists
        if object_already_exists:
            #replace
            if 'replace' in operation:
                msg += "\nA replace operation is taken."
                try:
                    results = api_resources.replace(body=manifest, namespace=namespace, name=kwargs['object_name'])
                except Exception as e:
                    error += '\napi_resources.replace ' + str(e)
            #patch
            elif 'patch' in operation:
                msg += "\nA patch operation is taken."
                try:
                    results = api_resources.patch(body=manifest, namespace=namespace, name=kwargs['object_name'], content_type=patch_type)
                except Exception as e:
                    error += '\napi_resources.patch ' + str(e)
        #object NOT exists
        else:
            #if safe, 
            #create one for a requested replace 
            if 'safe' in operation and 'replace' in operation:
                msg += "\nA create operation is taken."
                try:
                    results = api_resources.create(body=manifest, namespace=namespace)
                except Exception as e:
                    error += '\napi_resources.create ' + str(e)
            #create one for a requested patch
            elif 'safe' in operation and 'patch' in operation:
                msg += "\nA create operation is taken."
                try:
                    results = api_resources.create(body=manifest, namespace=namespace)
                except Exception as e:
                    error += '\napi_resources.create ' + str(e)
            #no operation
            else:
                error += "\nThe action is dismissed since the object does not exist and operation is not a safe one."
                
    #create
    elif 'create' in operation:
        msg += "\nA create operation is taken."
        try:
            results = api_resources.create(body=manifest, namespace=namespace)
        except Exception as e:
            error += '\napi_resources.create ' + str(e)
    #delete
    elif 'delete' in operation or 'safe-delete' in operation:
        if 'safe-delete' in operation and not object_already_exists:
            msg += '\nObject did not exist, so the deletion is safely ignored'
        else: 
            msg += "\nA delete operation is taken."
            try:
                results = api_resources.delete(name=kwargs['object_name'], body={}, namespace=namespace)
            except Exception as e:
                error += '\n api_resources.delete' + str(e)
    #unknown
    else:
        error += "\nOperation =" + operation + " is not known"

    msg +='\nkubectl apply stopped'
    #return
    return results, msg, error





#sample trafficsplit
#create
'''
object_name= "function-split"
api_version= "split.smi-spec.io/v1alpha2"
kind= "TrafficSplit"
namespace="openfaas-fn"
operation= "safe_patch"
patch_type= "application/merge-patch+json"

#extra
service= "ssd-tpu"

manifest = {
    "apiVersion": api_version,
    "kind": kind,
    "metadata": {
        "name": object_name,
        "namespace": namespace
    },
    "spec": {
        "backends": [],
        "service": service
    }
}
'''
#patch
'''
manifest = {"spec": {
        "backends": [
            {
                "service": "ssd-tpu-blue",
                "weight": 1000
            }
        ],
        "service": "ssd-tpu"
    }
}
'''



#alternative way of patching a deployment
'''
from kubernetes import client, config

DEPLOYMENT_NAME = "ssd-tpu"
client.configuration.debug = True
config.load_kube_config()
apps_v1 = client.AppsV1Api()


#'{"spec": {"template": {"spec": {"containers": [{"name": "ssd-tpu","image": "aslanpour/ssd:cpu-tpu", "securityContext": {"allowPrivilegeEscalation": true}}]}}}}'
# patch = [{"op": "replace", "value": True, "path": "/spec/template/spec/containers/0/securityContext/allowPrivilegeEscalation"}]
#'{"spec": {"template": {"spec": {"volumes": [{"name": "usb-devices", "hostPath": {"path": "/dev/bus/usb"}}]}}}}'

patch = [{"op": "replace", "value": [{"name": "usb-devices", "hostPath": {"path": "/dev/bus/usb"}}], "path": "/spec/template/spec/volumes"}]
# patch the deployment
resp = apps_v1.patch_namespaced_deployment(
    name=DEPLOYMENT_NAME, namespace="openfaas-fn", body=patch
)
'''


#alternative way of patching by kubectl
'''
#Sample patch by kubectl
kubectl patch deployment -n openfaas-fn function_name --patch '{"spec": {"template": {"spec": {"containers": [{"name": "ssd-tpu","image": "aslanpour/ssd:cpu-tpu", "securityContext": {"privileged": true}}]}}}}'
'''

#patch by curl

#curl -X POST -i http://localhost:5000/config/write  -H 'Content-Type: application/json' -H 'Accept: application/json' -d '{"config":{"Model": {"run_on": "gpu"}}}'


####################
def patch_kubernetes_deployment(name, namespace = "default", enabling_tpu_gpu_access = False):
    from kubernetes import config, dynamic
    from kubernetes.client import api_client
    import datetime
    import pytz
    error = ""

    # Creating a dynamic client
    try:
        dynamic_api_client = dynamic.DynamicClient(
            api_client.ApiClient(configuration=config.load_kube_config())
        )
    except Exception as e:
        error += '\n' + str(e)
        error= 'Unable to get kubeconfig'
        return error, 400

    #Does the requested deployment exist?
    exists = False
    from kubernetes import client
    apps_v1 = client.AppsV1Api()
    deployments = apps_v1.list_namespaced_deployment(namespace=namespace)
    for i in deployments.items:
            #print(f'{i.status.available_replicas}\t\t{i.spec.replicas}\t\t{i.metadata.namespace}\t{i.metadata.name}')
            if i.metadata.name == name:
                exists = True
    if exists == False:
        error += '\n The requested deployment name=' + name + ' is not found in namespace=' + namespace
        return error, 400

    # fetching the deployment api
    dynamic_api = dynamic_api_client.resources.get(api_version="apps/v1", kind="Deployment")

    #get the deployment by name
    try:
        deployment = dynamic_api.get(name=name, namespace=namespace)
    except Exception as e:
        error += '\n' + str(e)
        error += '\nFailed to get the requested deployment -- name=' + name + ' namespace=' + namespace
        return error, 400
    
    if enabling_tpu_gpu_access:
        #update the fileds
        #allowPrivilegeEscalation = True
        #'{"spec": {"template": {"spec": {"containers": [{"name": "ssd-tpu","image": "aslanpour/ssd:cpu-tpu", "securityContext": {"allowPrivilegeEscalation": true}}]}}}}'
        deployment.spec.template.spec.containers[0].securityContext.allowPrivilegeEscalation = True
        #privileged = True
        #'{"spec": {"template": {"spec": {"containers": [{"name": "ssd-tpu","image": "aslanpour/ssd:cpu-tpu", "securityContext": {"privileged": true}}]}}}}'
        deployment.spec.template.spec.containers[0].securityContext.privileged = True
        #runAsUser = 0
        #'{"spec": {"template": {"spec": {"containers": [{"name": "ssd-tpu","image": "aslanpour/ssd:cpu-tpu", "securityContext": {"runAsUser": 0}}]}}}}'
        deployment.spec.template.spec.containers[0].securityContext.runAsUser = 0
        #volumes hostPath
        #'{"spec": {"template": {"spec": {"volumes": [{"name": "usb-devices", "hostPath": {"path": "/dev/bus/usb"}}]}}}}'
        deployment.spec.template.spec.volumes = [{"name": "usb-devices", "hostPath": {"path": "/dev/bus/usb"}}]
        #volumeMounts mountPath
        #'{"spec": {"template": {"spec": {"containers": [{"name": "ssd-tpu", "volumeMounts":[{"mountPath": "/dev/bus/usb", "name": "usb-devices"}]}]}}}}'
        deployment.spec.template.spec.containers[0].volumeMounts = [{"mountPath": "/dev/bus/usb", "name": "usb-devices"}]

        #get Pod info as env into the container
        deployment.spec.template.spec.containers[0].env = [{"name": "GREETING", "value": "WARM_GREETING"},
                                                            {"name": "NODE_NAME", "valueFrom": {"fieldRef":{"fieldPath": "spec.nodeName"}}},
                                                            {"name": "POD_NAME", "valueFrom": {"fieldRef":{"fieldPath": "metadata.name"}}},
                                                            {"name": "POD_NAMESPACE", "valueFrom": {"fieldRef":{"fieldPath": "metadata.namespace"}}},
                                                            {"name": "POD_IP", "valueFrom": {"fieldRef":{"fieldPath": "status.podIP"}}},
                                                            {"name": "POD_IPS", "valueFrom": {"fieldRef":{"fieldPath": "status.podIPs"}}},
                                                            {"name": "POD_HOST_IP", "valueFrom": {"fieldRef":{"fieldPath": "status.hostIP"}}},
                                                            {"name": "DEPLOYMENT_NAME", "valueFrom": {"fieldRef":{"fieldPath": "metadata.labels['app']"}}},
                                                            {"name": "POD_UID", "valueFrom": {"fieldRef":{"fieldPath": "metadata.uid"}}}]

    else:
        error += '\nPatching this field is not implemented yet.'
        return error, 400

    #patch
    try:
        result = dynamic_api.patch(body=deployment, name=name, namespace=namespace)
    except Exception as e:
        error += '\n' + str(e)
        error += '\nPatch failed -- name=' + name + ' namespace=' + namespace + ' body=' + deployment
        return error, 400
    return error, 200

    #alternative way of patching a deployment by Kubectl. ref: https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.24/#patch-deployment-v1-apps
    '''
    kubectl patch deployment deployment-example -p \
	'{"spec":{"template":{"spec":{"containers":[{"name":"nginx","image":"nginx:1.16"}]}}}}'
    '''
    
    #alternative way of patching a deployment by Curl. Ref: https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.24/#patch-deployment-v1-apps
    '''
    kubectl proxy

    $ curl -X PATCH -H 'Content-Type: application/strategic-merge-patch+json' --data '
        {"spec":{"template":{"spec":{"containers":[{"name":"nginx","image":"nginx:1.16"}]}}}}' \
	    'http://127.0.0.1:8001/apis/apps/v1/namespaces/default/deployments/deployment-example'

    '''

    #alternative way of patching a deployment in Python
    '''
    from kubernetes import client, config

    DEPLOYMENT_NAME = "ssd-tpu"
    client.configuration.debug = True
    config.load_kube_config()
    apps_v1 = client.AppsV1Api()


    #'{"spec": {"template": {"spec": {"containers": [{"name": "ssd-tpu","image": "aslanpour/ssd:cpu-tpu", "securityContext": {"allowPrivilegeEscalation": true}}]}}}}'
    # patch = [{"op": "replace", "value": True, "path": "/spec/template/spec/containers/0/securityContext/allowPrivilegeEscalation"}]
    #'{"spec": {"template": {"spec": {"volumes": [{"name": "usb-devices", "hostPath": {"path": "/dev/bus/usb"}}]}}}}'

    patch = [{"op": "replace", "value": [{"name": "usb-devices", "hostPath": {"path": "/dev/bus/usb"}}], "path": "/spec/template/spec/volumes"}]
    # patch the deployment
    resp = apps_v1.patch_namespaced_deployment(
        name=DEPLOYMENT_NAME, namespace="saas-fn", body=patch
    )
    '''

#######################
# patch_kubernetes_deployment('ssd-tpu', namespace = "openfaas-fn", enabling_tpu_gpu_access = True)

# data = {'type': 'trafficsplit',
#     'interval': 60,
#     'algorithm': 'even',
#     'backends':[{'service':'w5-ssd','weight': 1000}],
#     'api_version': 'split.smi-spec.io/v1alpha2',
#     'kind': 'TrafficSplit', 
#     'object_name': 'my-traffic-split',
#     'namespace': 'openfaas-fn',
#     'service': 'gw-func',
#     'operation': 'safe-patch',
# }

# import pymanifest
# manifest, msg, error = pymanifest.manifest_builder(**data)
# print('1111111111111111111')
# print(manifest)
# data['manifest'] = manifest
# results, msg, error = apply(**data)
# if not error:
#     print('RRRRRRRR:' + str(results))
# print('MMMMMMM:' + msg)
# print('ERRRRRRRR:' + error)
def create_openfaas_profile(logger, func_name, nodeAffinity_required_filters=[], nodeAffinity_preferred_sort=[], podAntiAffinity_preferred_functionName=[], podAntiAffinity_required_functionName=[]):
    logger.info(f"pykubectl:create_openfaas_profile: start for func_name={func_name}, \nnodeAffinity_required_filters={nodeAffinity_required_filters}, \nnodeAffinity_preferred_sort={nodeAffinity_preferred_sort},\npodAntiAffinity_preferred_functionName={podAntiAffinity_preferred_functionName}, \npodAntiAffinity_required_functionName={podAntiAffinity_required_functionName}")
    #input

    #fix key value for node affinity (input is only node name)
    # if nodeAffinity_required_filters:
    #     for i in range(len(nodeAffinity_required_filters)):
    #         nodeAffinity_required_filters[i] = "kubernetes.io/hostname=" + nodeAffinity_required_filters[i]

    affinity={}
    #nodeAffinity
    if nodeAffinity_required_filters or nodeAffinity_preferred_sort:
        affinity['nodeAffinity']={}

        #requiredDuringSchedulingIgnoredDuringExecution
        if nodeAffinity_required_filters:
            affinity["nodeAffinity"]['requiredDuringSchedulingIgnoredDuringExecution']={
                "nodeSelectorTerms": [
                    {
                        "matchExpressions": [
                            {
                                "key": "kubernetes.io/hostname",
                                "operator": "In",
                                "values": nodeAffinity_required_filters
                            }
                        ]
                    }
                ]
            }
        #preferredDuringSchedulingIgnoredDuringExecution
        if nodeAffinity_preferred_sort:
            affinity["nodeAffinity"]["preferredDuringSchedulingIgnoredDuringExecution"]=[
                        {
                            "preference": {
                                "matchExpressions": [
                                    {
                                        "key": "kubernetes.io/hostname",
                                        "operator": "In",
                                        "values": nodeAffinity_preferred_sort,
                                    }
                                ]
                            },
                            "weight": 50
                        }
                    ]

    #podAntiAffinity
    if podAntiAffinity_required_functionName or podAntiAffinity_preferred_functionName:
        affinity['podAntiAffinity']={}

        #requiredDuringSchedulingIgnoredDuringExecution
        if podAntiAffinity_required_functionName:
            affinity["podAntiAffinity"]["requiredDuringSchedulingIgnoredDuringExecution"] = [
                        {
                            "labelSelector": {
                                "matchExpressions": [
                                    {
                                        "key": "faas_function",
                                        "operator": "In",
                                        "values": podAntiAffinity_required_functionName,
                                    }
                                ]
                            },
                            "topologyKey": "kubernetes.io/hostname"
                        }
                    ]
        #preferredDuringSchedulingIgnoredDuringExecution
        if podAntiAffinity_preferred_functionName:
            affinity["podAntiAffinity"]["preferredDuringSchedulingIgnoredDuringExecution"] = [
                        {
                            "podAffinityTerm": {
                                "labelSelector": {
                                    "matchExpressions": [
                                        {
                                            "key": "faas_function",
                                            "operator": "In",
                                            "values": podAntiAffinity_preferred_functionName,
                                        }
                                    ]
                                },
                                "topologyKey": "kubernetes.io/hostname"
                            },
                            "weight": 50
                        }
                    ]                



    #create kubectl command

    api_version = "openfaas.com/v1"
    kind = "Profile"
    namespace = "openfaas"
    operation = "safe_patch"
    manifest={
        "metadata":{
            "name": func_name,
            "namespace": namespace,
        },
        "spec":{
            "affinity":affinity

        }
    }

    return api_version, kind, namespace, operation, manifest

def create_openfaas_function_manifest_for_patch(**kwargs):
    result = None
    msg = ""
    err=""
    try:
        api_version = "openfaas.com/v1"
        kind="Function"
        operation="safe_patch"
        namespace="openfaas-fn"
        '''
        annotations = {
                    "linkerd.io/inject": "disabled"
                }
        constraints = ["kubernetes.io/hostname=homo8", "kubernetes.io/hostname=homo9"]
        environment = {"COUNTER": "0",
                "REDIS_SERVER_IP": "10.43.189.161",
                "REDIS_SERVER_PORT": "3679",
                "exec_timeout": "15s",
                "handler_wait_duration": "15s",
                "read_timeout": "15s",
                "version": "3",
                "write_debug": "true",
                "write_timeout": "15s"}
        image = "aslanpour/ssd:cpu-tpu"
        labels = {
                    "com.openfaas.scale.factor": "0",
                    "com.openfaas.scale.max": "1",
                    "com.openfaas.scale.min": "1",
                }
        limits = {
                    "cpu": "3600m",
                    "memory": ""
                }
        requests = {
                    "cpu": "1800m",
                    "memory": ""
                }
        '''
        output = {}
        output['api_version'] = api_version
        output['kind']= kind
        output["operation"] = operation
        output["namespace"] = namespace
        
        output['object_name'] = kwargs["name"] 

        manifest={
            "apiVersion": api_version,
            "kind": kind,
            "metadata": {
                "name": kwargs["name"] ,
                "namespace": namespace,
            },
            "spec": {
                "annotations": kwargs["annotations"],
                "environment": kwargs["environment"],
                "image": kwargs["image"],
                "labels": kwargs["labels"],
                "limits": kwargs["limits"],
                "name": kwargs["name"],
                "requests": kwargs["requests"],
            }
        }

        #constraints. If empty, openfaas keeps restarting the func
        if kwargs['constraints'] != []:
            manifest["spec"]["constraints"] = kwargs["constraints"]

        output["manifest"]= manifest

        result = output
        msg = "success"
        
    except Exception as e:
        return None, "Failed", str(e)
    else:
        return result, msg, err
    


# affinity = {'nodeAffinity': {'requiredDuringSchedulingIgnoredDuringExecution': {'nodeSelectorTerms': [{'matchExpressions': [{'key': 'kubernetes.io/hostname', 'operator': 'In', 'values': ['kubernetes.io/hostname=homo1', 'kubernetes.io/hostname=homo2', 'kubernetes.io/hostname=homo3', 'kubernetes.io/hostname=homo4', 'kubernetes.io/hostname=homo5', 'kubernetes.io/hostname=homo6', 'kubernetes.io/hostname=homo7', 'kubernetes.io/hostname=homo8', 'kubernetes.io/hostname=homo9', 'kubernetes.io/hostname=homo10']}]}]}}}
# manifest={
#     "spec": {
#         "template": {
#             "spec": {
#                 "affinity": affinity
#             }
#         }
#     }
# }
# inp = {'object_name': "homo1-ssd", "api_version": "apps/v1", "namespace": "openfaas-fn", "operation": "safe_patch", "kind":"Deployment", "manifest": manifest}
# res, msg, err = apply(**inp)
# print(f'res={res}\nmsg={msg}\nerror={err}')