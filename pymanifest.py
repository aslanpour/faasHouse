#build manifest 
#always required: api_version, kind, object_name, namespace
def manifest_builder(**kwargs):
    results = None
    msg =""
    error = ""

    msg += '\nmanifest_builder started.'

    #check basic requirements to build a manifest
    if 'api_version' not in kwargs or 'kind' not in kwargs or 'object_name' not in kwargs or 'namespace' not in kwargs:
        error += '\n required fields are not given, i.e., api_version, kind, object_name, or namespace.'
        return results, msg, error

    #pick a builder

    #TrafficSplit
    if kwargs['kind'] == 'TrafficSplit':
        manifest, msg_child, error = trafficSplit(**kwargs)
        msg += msg_child
    elif kwargs['kind'] == 'Function':
        manifest, msg_child, error = function(**kwargs)
        msg += msg_child
    elif kwargs['kind'] == 'Deployment':
        manifest, msg_child, error = deployment(**kwargs)
        msg += msg_child
    elif kwargs['kind'] == 'Service':
        manifest, msg_child, error = service(**kwargs)
        msg += msg_child
    else:
        error +='\nKind: ' + kwargs['kind'] + ' not implemented'
    
    msg += '\nmanifest_builder stopped'
    return manifest, msg, error



# manifest builder for trafficSplit
def trafficSplit(**kwargs):
    results= None; msg=""; error=""
    msg +="manifest builder for trafficSplit started."

    #verify especial fileds for a TrafficSplit, e.g., backend and service
    if not 'backends' in kwargs or not 'service' in kwargs:
        error += '\nNo backends and/or service are given in kwargs'
        return results, msg, error


    #manifest
    manifest = {
        "apiVersion": kwargs['api_version'],
        "kind": kwargs['kind'],
        "metadata": {
            "name": kwargs['object_name'],
            "namespace": kwargs['namespace']
        },
        "spec": {
            "backends": kwargs['backends'],
            "service": kwargs['service']
        }
    }

    msg += '\ntrafficSplit: stopped'
    return manifest, msg, error


# manifest builder for Function
def function(**kwargs):
    results= None; msg=""; error=""
    msg +="manifest builder for Function started."

    #verify especial fileds for a Function, e.g., image
    if not 'image' in kwargs:
        error += '\nNo image is given in kwargs'
        return results, msg, error


    #manifest
    manifest = {
        "apiVersion": kwargs['api_version'],
        "kind": kwargs['kind'],
        "metadata": {
            "name": kwargs['object_name'],
            "namespace": kwargs['namespace']
        },
        "spec": {
            "name": kwargs['object_name'],
            'image':  kwargs['image'],
            'labels': kwargs['labels'],
            'annotations': kwargs['annotations'],
            'constraints': kwargs['constraints'],
        }
    }

    msg +="\nmanifest builder for Function stopped"
    return manifest, msg, error


# manifest builder for Deployment
def deployment(**kwargs):
    results= None; msg=""; error=""
    msg +="manifest builder for Deployment started."

    #verify especial fileds for a Deployment, e.g., image
    if not 'image' in kwargs:
        error += '\nNo image is given in kwargs'
        return results, msg, error


    #manifest
    manifest = {
        "apiVersion": kwargs['api_version'],
        "kind": kwargs['kind'],
        "metadata": {
            "name": kwargs['object_name'],
            "namespace": kwargs['namespace'],
        },
        "spec": {
            "replicas": kwargs['replicas'] if 'replicas' in kwargs else 1,
            "selector": {
                "matchLabels": kwargs['matchLabels'] if 'matchLabels' in kwargs else {"app": kwargs['object_name']},
            },
            "template": {
                "metadata": {
                    "labels": kwargs['labels'] if 'labels' in kwargs else {"app": kwargs['object_name']},
                    "annotations": kwargs['annotations'] if 'annotations' in kwargs else {},
                },
                "spec":{
                    "hostNetwork": kwargs['hostNetwork'] if 'hostNetwork' in kwargs else False,
                    "nodeName": kwargs['nodeName'] if 'nodeName' in kwargs else "",
                    "containers": kwargs['containers'] if 'containers' in kwargs else [
                        {
                            "name": kwargs['container_name'] if 'container_name' in kwargs else kwargs['object_name'],
                            "image": kwargs['image'],
                            "imagePullPolicy": kwargs['imagePullPolicy'] if 'imagePullPolicy' in kwargs else 'IfNotPresent',
                            "ports": kwargs['ports'] if 'ports' in kwargs else 
                                [{"containerPort": 8080 },],
                            "env": kwargs['env'] if 'env' in kwargs else [],
                            "securityContext": kwargs['securityContext'] if 'securityContext' in kwargs else {},
                            "volumeMounts": kwargs['volumeMounts'] if 'volumeMounts' in kwargs else [],
                        }
                    ],
                    "volumes": kwargs['volumes'] if 'volumes' in kwargs else [],
                },
            },
        },
    }


          
    msg +="\nmanifest builder for Deployment stopped"
    return manifest, msg, error


# manifest builder for Service
def service(**kwargs):
    results= None; msg=""; error=""
    msg +="manifest builder for Service started."

    #manifest
    manifest = {
        "apiVersion": kwargs['api_version'],
        "kind": kwargs['kind'],
        "metadata": {
            "name": kwargs['object_name'],
            "namespace": kwargs['namespace']
        },
        "spec": {
            "clusterIP": kwargs['clusterIP'] if 'clusterIP' in kwargs else None,
            "clusterIPs": kwargs['clusterIPs'] if 'clusterIPs' in kwargs else [kwargs['clusterIP']] if 'clusterIP' in kwargs else None,
            "selector": kwargs['selector'] if 'selector' in kwargs else {"app": kwargs['object_name']},
            "ports": kwargs['ports'] if 'ports' in kwargs else [
                {'protocol': 'TCP',
                'port': 8080,
                'targetport': 8080},
            ],
        }
    }

    #clean manifest
    manifest = {k: v for k, v in manifest.items() if v is not None}
    
    msg +="\nmanifest builder for Service stopped"
    return manifest, msg, error
