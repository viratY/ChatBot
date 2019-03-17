import requests
import json
from requests.auth import HTTPBasicAuth
import time

import json_data as js
import actions as ac

start_time = time.time()

apis = {'wl23':'https://bpmdev.appcino.com/suite/webapi/FoR8Gg',
		'wl24':'https://bpmdev.appcino.com/suite/webapi/QcJTTQ',
		'wl25': 'https://bpmdev.appcino.com/suite/webapi/FoR8Gg',
		'wl26': 'https://bpmdev.appcino.com/suite/webapi/QcJTTQ',
		'wl27': 'https://bpmdev.appcino.com/suite/webapi/FoR8Gg'}

data = js.json_data
workflowInputs = data["workflow"]["workflowInputs"]
outputs = {}
workflowSteps = data["workflow"]["workflowSteps"]
inputs={}


# r = json.dumps(data)
# r1 = requests.post(url="https://bpmdev.appcino.com/suite/webapi/ex_BwA",
# 				   data=r,auth=('Aditya', 'NeverGiveUp:)'))
#

# response = r1.json()
# workflowSteps = response['workflowSteps']
# outputs = {}
# inputs = {}

# writeInput = workflowSteps[0]['config']
# write = requests.post(url='https://bpmdev.appcino.com/suite/webapi/FoR8Gg',data=json.dumps(writeInput),
# 			  auth=('Aditya', 'NeverGiveUp:)'))

for item in workflowSteps:
	key = item['id']
	value = item['config']
	inputs[key] = value


for item in inputs:
	api = apis[item]

	input = json.dumps(inputs[item])
	replacedInput =  js.replaceValue(input,outputs,js.searchValues(input),workflowInputs)
	input = input if replacedInput == '' else replacedInput
	r1 = requests.post(url=api,data=input,auth=('Aditya', 'NeverGiveUp:)'))
	outputs[item] = r1.json()

	# print('write')

print(outputs)

print("--- %s seconds ---" % (time.time() - start_time))

