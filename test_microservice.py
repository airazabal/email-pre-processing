# from the list of test files
# pre-process and create a csv, so that it can be added to WKS


import requests, codecs, json, csv
import os
import pprint
pp = pprint.PrettyPrinter()
from email_thread import EmailThread, printlines

input_dir = "./data/"
test_files = os.listdir(input_dir)
URL = 'http://localhost:7000/api/pre_process_email'
##URL = 'https://email-thread-microservice.mybluemix.net/api/pre_process_email'
def post_message(email_string, email_id):
	POST_SUCCESS = 200
	request_message = {}
	request_message['source_id'] = email_id
	request_message['source_email'] = email_string
#-- PRINT MESSAGE
	headerinfo = {'content-type': 'application/json'}
	r = requests.post(URL, headers=headerinfo, data=json.dumps(request_message))
	# print("request encoding: ", r.encoding)
	# print(request_message)
	# print(r.status_code)
	if r.status_code == POST_SUCCESS:
		pre_processed_email = r.json()
		# print("***** POST SUCCESS *****")
		# pp.pprint(pre_processed_email)
		return pre_processed_email
	try:
		print()
	except Exception as e:
		print('--Exception')
		print(e)

test_files = os.listdir(input_dir)
## TODO: need to test utf8 characters better. might need to modify email_thread.py
##       to check utf-8 type instead of string...
##       ALTERNATIVELY - using python3 would make utf-8 inherent
passed = True
for file_name in test_files:
	with open (input_dir+file_name) as email_text:
		print("Testing file {}".format(file_name))
		## get test file from local email_thread
		email_string = email_text.read()
		email_id = file_name
		email_thread = EmailThread(email_id, email_string)

		## get test response from the microservice
		request_email = post_message(email_string, email_id)

		## re-encode everything to string
		request_email['source_id'] = request_email['source_id'].encode('utf-8')
		request_email['subject'] = request_email['subject'].encode('utf-8')
		request_email['body'] = request_email['body'].encode('utf-8')
		request_email['trimmed'] = request_email['trimmed'].encode('utf-8')
		request_email['cleansed'] = request_email['cleansed'].encode('utf-8')

		## begin testing object components
		print("---> \t\t originals match? *************************")
		source = email_thread.original_string
		target = request_email['body']
		passed &= source == target
		print(passed)

		print("---> \t\t subjects match? *************************")
		source = email_thread.subject
		target = request_email['subject']
		passed &= source == target
		print(passed)

		print("---> \t\t trimmeds match? *************************")
		source = email_thread.to_trimmed_string()
		target = request_email['trimmed']
		passed &= source == target
		print(passed)

		print("---> \t\t cleanseds match? *************************")
		source = email_thread.to_cleansed_string()
		target = request_email['cleansed']
		passed &= source == target
		print(passed)

if passed:
	print("All tests passed")
else:
	print("Tests failed")
