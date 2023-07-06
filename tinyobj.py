#curl -X GET -H "Image-URL: http://10.0.0.92:5500/pioss/api/read/w2-ssd/pic_1.jpg"  http://10.0.0.90:31112/function/w5-ssd/

from flask import Flask, request, send_file, make_response, json, jsonify  # pip3 install flask
from waitress import serve  # pip3 install waitres
import logging
import getpass
import os

app = Flask(__name__)
app.config["DEBUG"] = True
app.debug=True

file_storage_folder = "/home/" + getpass.getuser() + "/storage/"
if not os.path.exists(file_storage_folder):
    os.makedirs(file_storage_folder)

print('file_storage_folder=' + file_storage_folder)

#pioss_read
@app.route('/pioss/api/read/<func_name>/<file_name>', methods=['GET'], endpoint='read_filename')
def pioss_read(func_name, file_name):
    global file_storage_folder

    # get file
    img = open(file_storage_folder + file_name, 'rb').read()
    # preapare response (either make_response or send_file)
    response = make_response(img)
    response.headers.set('Content-Type', 'image/jpeg')
    response.headers.set('Content-Disposition', 'attachment', filename=file_name)

    return response
    # return send_file(io.BytesIO(img), attachment_filename=file_name)


@app.route('/test', methods=['GET', 'POST'])
def test():
    return 'Test success\n'


if __name__ == "__main__":
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    serve(app, host='0.0.0.0', port='5500')