from kubernetes import client, config
import time


def create_deployment_object():
    container = client.V1Container(
        name="nginx-sample",
        image="nginx",
        image_pull_policy="IfNotPresent",
        ports=[client.V1ContainerPort(container_port=80)],
    )
    # Template
    template = client.V1PodTemplateSpec(
        metadata=client.V1ObjectMeta(labels={"app": "nginx"}),
        spec=client.V1PodSpec(containers=[container]))
    # Spec
    spec = client.V1DeploymentSpec(
        replicas=1,
        selector=client.V1LabelSelector(
            match_labels={"app": "nginx"}
        ),
        template=template)
    # Deployment
    deployment = client.V1Deployment(
        api_version="apps/v1",
        kind="Deployment",
        metadata=client.V1ObjectMeta(name="deploy-nginx"),
        spec=spec)

    return deployment


def create_deployment(apps_v1_api, deployment_object):
    # Create the Deployment in default namespace
    # You can replace the namespace with you have created
    apps_v1_api.create_namespaced_deployment(
        namespace="default", body=deployment_object
    )




def main():
    # Loading the local kubeconfig
    config.load_kube_config()
    apps_v1_api = client.AppsV1Api()
    # deployment_obj = create_deployment_object()

    # create_deployment(apps_v1_api, deployment_obj)
    # time.sleep(1)
    before_annotating = apps_v1_api.read_namespaced_deployment(
        'w5-ssd', 'openfaas-fn')
    print('Before annotating, annotations: %s' %
          before_annotating.metadata.annotations)

    annotations = [
        {
            'op': 'add',  # You can try different operations like 'replace', 'add' and 'remove'
            'path': '/',
            'value': {'spec': {'template': {'spec': {'containers': [{'name': 'w5-ssd', 'image': 'aslanpour/ssd:cpu-tpu', 'ports': [{'containerPort': 8080, 'protocol': 'TCP'}], 'env': [{'name': 'MODEL_PRE_LOAD', 'value': 'cpu-only'}, {'name': 'MODEL_RUN_ON', 'value': 'cpu'}, {'name': 'handler_wait_duration', 'value': '10s'}, {'name': 'write_timeout', 'value': '10s'}, {'name': 'write_debug', 'value': 'true'}, {'name': 'MODEL_IMAGE_SAMPLE2', 'value': 'blue'}, {'name': 'REDIS_SERVER_IP', 'value': '10.43.242.161'}, {'name': 'REDIS_SERVER_PORT', 'value': '3679'}, {'name': 'exec_timeout', 'value': '10s'}, {'name': 'read_timeout', 'value': '10s'}], 'resources': {}, 'livenessProbe': {'failureThreshold': 3,
 'httpGet': {'path': '/_/health', 'port': 8080, 'scheme': 'HTTP'},
 'initialDelaySeconds': 2,
 'periodSeconds': 2,
 'successThreshold': 1,
 'timeoutSeconds': 1}, 'readinessProbe': {'failureThreshold': 3,
 'httpGet': {'path': '/_/health', 'port': 8080, 'scheme': 'HTTP'},
 'initialDelaySeconds': 2,
 'periodSeconds': 2,
 'successThreshold': 1,
 'timeoutSeconds': 1}, 'terminationMessagePath': '/dev/termination-log', 'terminationMessagePolicy': 'File', 'imagePullPolicy': 'Never', 'securityContext': {'allowPrivilegeEscalation': False, 'readOnlyRootFilesystem': False}}]}}}}

        }
    ]

    apps_v1_api.patch_namespaced_deployment(
        name='w5-ssd', namespace='openfaas-fn', body=annotations)

    time.sleep(1)
    after_annotating = apps_v1_api.read_namespaced_deployment(
        name='w5-ssd', namespace='openfaas-fn')
    print('After annotating, annotations: %s' %
          after_annotating.metadata.annotations)


if __name__ == "__main__":
    main()