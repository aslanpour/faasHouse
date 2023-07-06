from kubernetes import client,config, dynamic
from kubernetes.client import api_client
import datetime



#Tip: function_name comes from Deployment name of the function.
#Note: All HPA parameters are based on the default Kubernetes, unless specified otherwise.
def auto_scaling_by_hpa(logger, function_name="test-function", min_replicas=1, max_replicas=10, avg_cpu_utilization=80, scale_down_stabilizationWindowSeconds=300):
    logger.info("Start HPA")
    
    try:
        # setup the kubernetes API
        client = dynamic.DynamicClient(api_client.ApiClient(configuration=config.load_kube_config()))
        api_autoscalingv2 = client.resources.get(api_version="autoscaling/v2", kind="HorizontalPodAutoscaler")
    except:
        logger.error("HPA failed to create a client using the kubeconfig file")
        return None

    #prepare the manifest for a HPA object
    hpa_manifest ={}
    hpa_manifest["apiVersion"]= "autoscaling/v2"
    hpa_manifest["kind"] = "HorizontalPodAutoscaler"
    hpa_manifest["metadata"] = {'name': function_name + '-hpa',
                                'namespace': 'openfaas-fn'
                                }
    hpa_manifest["spec"] = {}
    hpa_manifest["spec"]["scaleTargetRef"] = {'apiVersion': 'apps/v1',
                                              'kind': 'Deployment',
                                              'name': function_name
                                              }
    hpa_manifest["spec"]["minReplicas"] = min_replicas
    hpa_manifest["spec"]["maxReplicas"] = max_replicas
    hpa_manifest["spec"]["metrics"] = [{'type': 'Resource',
                                        'resource':
                                            {'name': 'cpu',
                                             'target':
                                                {'type': 'Utilization',
                                                 'averageUtilization': avg_cpu_utilization,
                                                 },
                                             },
                                        },
                                       ]

    hpa_manifest["spec"]["behavior"]={}
    hpa_manifest["spec"]["behavior"]["scaleDown"]={"stabilizationWindowSeconds": scale_down_stabilizationWindowSeconds,
                                                   "policies":[
                                                       {'type': 'Percent',
                                                        'value': 100,
                                                        'periodSeconds': 15,
                                                        }
                                                   ],
                                                   "selectPolicy": 'Max',
                                                   }
    hpa_manifest["spec"]["behavior"]["scaleUp"]={"stabilizationWindowSeconds": 0,
                                                 "policies":[
                                                     {"type": "Percent",
                                                      'value': 100,
                                                      "periodSeconds": 15
                                                      },
                                                     {"type": 'Pods',
                                                      'value': 1,
                                                      'periodSeconds': 15
                                                      },
                                                 ],
                                                 'selectPolicy': 'Max'
                                                 }


    #api_autoscalingv2.create, api_autoscalingv2.patch, api_autoscalingv2.delete,  api_autoscalingv2.replace    api_autoscalingv2.create_namespaced_deployment...

    #Verify if a HPA exists for the function
    hpa_name = ""
    hpa_already_exists = False
    for item in api_autoscalingv2.get(namespace="openfaas-fn").items:
        #either get HPA objects content as dictionery/json
        hpa_item = api_autoscalingv2.get(name=item.metadata.name, namespace="openfaas-fn")
        hpa_target_function = hpa_item["spec"]["scaleTargetRef"]["name"]
        #or get HPA objects as Yaml
        hpa_target_function = item.spec.scaleTargetRef.name

        if hpa_target_function == function_name:
            hpa_already_exists = True
            hpa_name = hpa_item["metadata"]["name"]
            break

    #perform the operation
    if hpa_already_exists:
        print('A HPA object (' + hpa_name + ') already exists for function ' + function_name)
        #either patch the HPA
        #e.g., update = {"spec": {"maxReplicas": 1}} #Note that patching is not always safe if the HPA objects from a previous test are remained.
        #update = hpa_manifest
        #hpa = api_autoscalingv2.patch(body=update, namespace="openfaas-fn", name = hpa_name, content_type="application/merge-patch+json")

        #or replace the HPA
        hpa = api_autoscalingv2.replace(body=hpa_manifest, namespace="openfaas-fn")
    else:
        print('No HPA object exists for function ' + function_name)
        print('Create one from the manifest')
        hpa = api_autoscalingv2.create(body=hpa_manifest, namespace="openfaas-fn")


    #Reference: A sample yaml file for HPA
    yaml_file="""
    #tutorial and algorithm https://github.com/kubernetes/enhancements/blob/master/keps/sig-autoscaling/853-configurable-hpa-scale-velocity/README.md
    apiVersion: autoscaling/v2
    kind: HorizontalPodAutoscaler
    metadata:
      name: figletcrd-hpa
      namespace: openfaas-fn
    #spec
    spec:
      #target reference
      scaleTargetRef:
        #apiVersion: openfaas.com/v1
        apiVersion: apps/v1
        kind: Deployment
        name: figletcrd
      #basic scaling config
      minReplicas: 1 #default=1
      maxReplicas: 10
      #1# desiredReplicas = AnyAlgorithmInHPAController
      #desiredReplicas = ceil[currentRepllicas * (currentMetricValue / desiredMetricValue)]
        #this is ran every 15 seconds by default by --horizontal-pod-autoscaler-sync-period
        #if currentMetricValue/desiredMetricValue is close to 1, scaling does not happen. Closeness set by --horizontal-pod-autoscaler-tolerance and efault is 0.1
      #metrics: desired condition
      metrics:
      - type: Resource
        resource:
          name: cpu #cpu or memory
          target:
            type: Utilization #or AverageValue (and averageValue instead of averageUtilization)
            averageUtilization: 80
      #behavior
      behavior:
        #2#if desiredReplicas > curReplicas
        scaleDown:
          #make a decision about recommendations every x seconds. HPA contoller calculates desired replicas every 15s and gives recommendations (e.g., 4,2,5 replicase as desired replica) but they are just collected and after stabilazation window time the largest (maybe for up, the smallest??) value is selected to perform the scaling. 
          #the scaleDown/Up gathers HPA recommendations (up or down) for x seconds, after that picks the largest one (number of replicas to scale) and performs scaling
          #cooldown - timestamp between scaling operations. Overwrites the scaling interval. A threshold 
          #if desired pods i s 6 and current is 7, a scale down happens only if during x seconds before there was no 7 replicas as current replicas.
          #the amount of time the HPA should consider previous recommendations to prevent flapping of the number of replicas
          #avoid false positive signals
          stabilizationWindowSeconds: 30 #default=300, >=0 <=3600
          policies:
          #x percent/pods (x= value: .. rounded up, e.g. 5.4pods to add/remove=6pods) of current replicas are allowed to scale down---at a time or in the past Y second (Y= periodSeconds)
          #3# replicas = append(replicas, curReplicas - policy.value)). If value is percent, append(curReplicas * (1 - policy.value/100))
          - type: Percent
            value: 100  #>0
            #scale Down/Up no more than x percent/pods per periodSeconds 
            #the length of time in the past for which the policy must hold true
            #perform the scaling operation, but x percent/pod (based on the x=value) replicas at a time (periodSeconds)
            periodSeconds: 15 # >0 <=1800
          #default=Max --> if multiple policiy types defined, use the one with maximum effect. or set 'Disabled' to disable the scaling operation entirely
          #4#scaleUpLimit = min if selectPolicy=Max or max if selectPolicy=Min (replicas) (*this is opposite scale up) then limitedReplicas = max(max, desiredReplicas) (*opposite in scale up)
          selectPolicy: Max
        #2#if deiredReplicas < curReplicas
        scaleUp:
          #performs like the one in scaleDown
          stabilizationWindowSeconds: 0 #default=0, >0 <=3600
          #perofrms like the one in scaleDown
          #3# replicas = append(replicas, curReplicas + policy.value)). If value is percent, append(curReplicas * (1 + policy.value/100))
          policies:
          #performs like the one in scale down
          - type: Percent
            value: 100
            periodSeconds: 15 #>0 <=1800
          - type: Pods
            value: 1
            #performs like the one in scaleDown
            periodSeconds: 15 #>0 <=1800
          #performs like the one is scaleDown
          #4#scaleUpLimit = max if selectPolicy=Max or min if selectPolicy=Min (replicas) (*oppiste in scale down) )then limitedReplicas = min(max, desiredReplicas) (*opposite in scale down)
          selectPolicy: Max 
    """
    
    logger.info("End HPA")
