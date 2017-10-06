# Copyright 2015 IBM Corp. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os, json
from flask import Flask, request, jsonify
from email_thread import EmailThread

app = Flask(__name__)
app.debug = True

@app.route('/')
def Welcome():
    return app.send_static_file('index.html')

@app.route('/api/pre_process_email', methods=['POST'])
def Pre_Process_Email():
    print(request.data)
    request_data_object = {}
    request_data_object['source_email'] = json.loads(request.data)['source_email'].encode('utf-8')
    request_data_object['source_id'] = json.loads(request.data)['source_id'].encode('utf-8')
    print(request_data_object['source_email'])
    print(type(request_data_object['source_email'].encode('utf-8')))
    print(request_data_object['source_id'])
    print(type(request_data_object['source_id']))
    response = {}
    response['source_id'] = request_data_object['source_id']
    response['body'] = request_data_object['source_email']
    email_thread = EmailThread(response['source_id'], response['body'])
    response['subject'] = email_thread.subject
    response['trimmed'] = email_thread.to_trimmed_string()
    response['cleansed'] = email_thread.to_cleansed_string()
    return jsonify(response)

@app.route('/myapp')
def WelcomeToMyapp():
    return 'Welcome again to my app running on Bluemix!'

@app.route('/api/people')
def GetPeople():
    list = [
        {'name': 'John', 'age': 28},
        {'name': 'Bill', 'val': 26}
    ]
    return jsonify(results=list)

@app.route('/api/people/<name>')
def SayHello(name):
    message = {
        'message': 'Hello ' + name
    }
    return jsonify(results=message)

port = os.getenv('PORT', '5000')
if __name__ == "__main__":
	app.run(host='0.0.0.0', port=int(port))
