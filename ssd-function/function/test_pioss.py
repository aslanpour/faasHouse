
from distutils.log import debug
from flask import Flask, request, send_file, make_response, json #pip3 install flask
from waitress import serve
import os


app = Flask(__name__)
app.config["DEBUG"] = True
app.debug=True



@app.route('/', methods=['POST', 'GET'])  
def pioss():   

    #get file
    img = open('/home/ubuntu/object-detection/ssd-gpu/images/image1.jpg', 'rb').read()
    
    response = make_response(img)
    response.headers.set('Content-Type', 'image/jpeg')
    response.headers.set(
        'Content-Disposition', 'attachment', filename= "image1.jpg")
    
    return response
    #return send_file(io.BytesIO(img), attachment_filename=file_name)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5005)
