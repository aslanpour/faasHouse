# Copyright (c) Alex Ellis 2017. All rights reserved.
# Licensed under the MIT license. See LICENSE file in the project root for full license information.

from distutils.log import debug
from flask import Flask, request, jsonify
from function import handler
from waitress import serve
import os
import subprocess
import configparser
import threading
import socket

lock = threading.Lock()

app = Flask(__name__)
app.config["DEBUG"] = True
app.debug=True

counter = 0

# distutils.util.strtobool() can throw an exception
def is_true(val):
    return len(val) > 0 and val.lower() == "true" or val == "1"

@app.before_request
def fix_transfer_encoding():
    """
    Sets the "wsgi.input_terminated" environment flag, thus enabling
    Werkzeug to pass chunked requests as streams.  The gunicorn server
    should set this, but it's not yet been implemented.
    """

    transfer_encoding = request.headers.get("Transfer-Encoding", None)
    if transfer_encoding == u"chunked":
        request.environ["wsgi.input_terminated"] = True

@app.route("/", defaults={"path": ""}, methods=["POST", "GET"])
#@app.route("/<path:path>", methods=["POST", "GET"])
def main_route(path):
    # raw_body = os.getenv("RAW_BODY", "false")

    # as_text = True

    # if is_true(raw_body):
    #     as_text = False
    # ret = handler.handle(request.get_data(as_text=as_text))
    global counter
    counter +=1

    ret, detected_objects, error = handler.handle(request, counter)
    if len(error)>0:
        return error, 400
    else:
        print(detected_objects, flush=True)
        return ret

#test api
@app.route("/test", methods=["POST", "GET"])
def test():
    return "Test Success"

#cmd api
@app.route("/cmd", methods =["POST", "GET"])
def cmd():
    cmd = ""
    # Check if cmd is specified in request query parameter
    if request.args.get('cmd'):
        cmd = str(request.args.get('cmd'))

    # Check if cmd is specified in request header
    elif request.headers.get('cmd'):
        cmd = str(request.headers.get('cmd'))
    
    # Check if cmd is specified in request body
    try:
        body_cmd = request.get_data().decode('UTF-8')
        
        if body_cmd:
            cmd = body_cmd
    except:
        pass

    #run the command
    if cmd != "":
        try:
            result = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT, timeout=30).decode("utf-8")
            print(result)
        except subprocess.CalledProcessError as e:
            print(e)
        except subprocess.TimeoutExpired as e:
            print(e)
    else:
        return "No cmd is received on server"



#config1 api
#Sample client side code to update config.
# import requests
# res = requests.post('http://localhost:5000/config', json={"config":{"Model": {"run_on": "tpu"}}})
# if res.ok:
#     print(res.json())
@app.route("/config/read", methods=['GET'], endpoint='read_config')
@app.route("/config/write", methods=['POST'], endpoint='write_config')
def config():
    #read
    if request.method == 'GET':
        #read local config file
        config = configparser.ConfigParser()
        config.read('/home/app/config.ini')
        updated_config = {s:dict(config.items(s)) for s in config.sections()}

        #append server info
        updated_config.update(server_info())

        return jsonify(updated_config)
    
    #write
    if request.method == 'POST':
        
        print('A config update started.', flush=True)
        if not request.is_json:
            return "mimetype does NOT indicate JSON data, either application/json or application/*+json", 400

        new_config = request.json
        if 'config' not in new_config:
            return 'Not a config key is found in the request.json', 400

        new_config = new_config['config']

        #read local config file
        config = configparser.ConfigParser()
        config.read('/home/app/config.ini')

        if config.read('/home/app/config.ini') == []: print('WARNING: config.ini file is empty')

        #Each key in new_cfg refers to a section of config file and the value refers to the subsection (key, value).
        #Sample config to be received: 
        #new_cfg = {'Section1': {'updateKeyX': 'updateValueX'},
        #    'Section2': {'updateKeyY': 'updateValueY'}}
        
            
        #update section: key:value (if config.ini does not exist, it creates a fresh one)
        for requestedSection, _ in new_config.items():
            #if requested section is not created already, create it now.
            if requestedSection not in config.sections():
                config.add_section(requestedSection)
            #update all keys/values in this section (or create newly requested keys/values)
            for updateKey, updateValue in new_config[requestedSection].items():
                if updateKey == 'WAITRESS_THREADS':
                    print('WAITRESS_THREADS is immutable; otherwise, you have to configure waitress to reload by a change in its config to apply this change.', flush=True)
                    return 'WAITRESS_THREADS is immutable; otherwise, you have to configure waitress to reload by a change in its config to apply this change.', 400
                config[requestedSection][updateKey] = updateValue
                
        #persist the updates
        with open('/home/app/config.ini', 'w') as configfile:
            config.write(configfile) 

        config.read('/home/app/config.ini')
        updated_config = {s:dict(config.items(s)) for s in config.sections()}
        return jsonify(updated_config)




def server_info():
    KUBERNETES_SERVICE_IP = os.getenv("KUBERNETES_SERVICE_HOST", os.getenv(os.getenv("DEPLOYMENT_NAME") + "_SERVICE_HOST" if os.getenv("DEPLOYMENT_NAME") else "", None))
    KUBERNETES_SERVICE_PORT = os.getenv("KUBERNETES_SERVICE_PORT", os.getenv(os.getenv("DEPLOYMENT_NAME") + "_SERVICE_PORT" if os.getenv("DEPLOYMENT_NAME") else "", None))

    collected_info = {
    "X-KUBERNETES_DEPLOYMENT_NAME": os.getenv("DEPLOYMENT_NAME", None),
    "X-KUBERNETES_SERVICE_IP": KUBERNETES_SERVICE_IP,
    "X-KUBERNETES_SERVICE_PORT": KUBERNETES_SERVICE_PORT,
    "X-Worker-Name": socket.gethostname(),
    "X-Worker-Ip": socket.gethostbyname(socket.gethostname()),
    "X-NODE-NAME": os.getenv("NODE_NAME", None),
    "X-POD-NAME": os.getenv("POD_NAME", None),
    "X-POD-NAMESPACE": os.getenv("POD_NAMESPACE", None),
    "X-POD-IP": os.getenv("POD_IP", None),
    "X-POD-IPS": os.getenv("POD_IPS", None),
    "X-POD-HOST-IP": os.getenv("POD_HOST_IP", None),
    "X-POD-UID": os.getenv("POD_UID", None),
    }


    return collected_info



if __name__ == '__main__':
    print("serve(app, host='0.0.0.0', port=5000, threads=" + str(int(os.getenv("WAITRESS_THREADS", 4))) + ")", flush=True)
    serve(app, host='0.0.0.0', port=5000, threads=int(os.getenv("WAITRESS_THREADS", 4)))
    #if app.run(...threaded=True)