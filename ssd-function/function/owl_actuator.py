
from distutils.log import debug
from flask import Flask, request, send_file, make_response, json #pip3 install flask
from waitress import serve
import os


app = Flask(__name__)
app.config["DEBUG"] = True
app.debug=True



@app.route('/', methods=['POST', 'GET'])  
def owl_actuator(): 

    data = request.get_data(as_text=True)
    print(str(data))
    print(str(request.headers))

    return True

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5006)