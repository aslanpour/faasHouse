import yaml
import json
#read YAML as Json
with open("/home/ubuntu/envoy/envoy.yaml", 'r') as stream:
    try:
        parsed_yaml=yaml.safe_load(stream)
        print(parsed_yaml)
    except yaml.YAMLError as exc:
        print(exc)
#print Json
print(json.dumps(parsed_yaml, sort_keys=True, indent=4))
#edit Json
parsed_yaml["static_resources"]["clusters"][0]["load_assignment"]["endpoints"][0]["lb_endpoints"][0]["endpoint"]={"address": {"socket_address": {"address": "10.423..249.", "port_value": 5006}}}
'lb_endpoints' = [{"endpoint": {"address": {"socket_address": {"address": "10.423..249.", "port_value": 5006}}}, "load_balancing_weight": 50}]

with open(r'/home/ubuntu/envoy/envoy.yaml', 'w') as file:
#    documents = yaml.dump(dict_file, file)
    yaml.dump(parsed_yaml, file, default_flow_style=False, sort_keys=True)

