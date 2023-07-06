#input
func_name = "w1-ssd"
nodeAffinity_required_filters = ['homo3']
nodeAffinity_preferred_sort = ['homo2', 'homo3']
podAntiAffinity_preferred_functionName = []
podAntiAffinity_required_functionName = []

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
print(manifest)
'''
{
    "apiVersion": "openfaas.com/v1",
    "kind": "Profile",
    "metadata": {
            },
    "spec": {
        "affinity": {
            "nodeAffinity": {
                "preferredDuringSchedulingIgnoredDuringExecution": [
                    {
                        "preference": {
                            "matchExpressions": [
                                {
                                    "key": "kubernetes.io/hostname",
                                    "operator": "In",
                                    "values": [
                                        "homo2"
                                    ]
                                }
                            ]
                        },
                        "weight": 50
                    }
                ],
                "requiredDuringSchedulingIgnoredDuringExecution": {
                    "nodeSelectorTerms": [
                        {
                            "matchExpressions": [
                                {
                                    "key": "kubernetes.io/hostname",
                                    "operator": "In",
                                    "values": [
                                        "homo1",
                                        "homo6",
                                        "homo8",
                                        "homo10",
                                        "homo7"
                                    ]
                                }
                            ]
                        }
                    ]
                }
            },
            "podAntiAffinity": {
                "preferredDuringSchedulingIgnoredDuringExecution": [
                    {
                        "podAffinityTerm": {
                            "labelSelector": {
                                "matchExpressions": [
                                    {
                                        "key": "faas_function",
                                        "operator": "In",
                                        "values": [
                                            "homo9"
                                        ]
                                    }
                                ]
                            },
                            "topologyKey": "kubernetes.io/hostname"
                        },
                        "weight": 50
                    }
                ],
                "requiredDuringSchedulingIgnoredDuringExecution": [
                    {
                        "labelSelector": {
                            "matchExpressions": [
                                {
                                    "key": "faas_function",
                                    "operator": "In",
                                    "values": [
                                        "homo3"
                                    ]
                                }
                            ]
                        },
                        "topologyKey": "kubernetes.io/hostname"
                    }
                ]
            }
        }
    }
}
'''