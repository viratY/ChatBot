import re
import json
import requests
import actions as ac

json_data = """{
	"workflow": {
		"workflowId": "3",
		"workflowName": "room type (RoomType)",
		"workflowDesc": "room type validation",
		"workflowInputs": [{
				"name": "slot",
				"dataType": "json",
				"value": {
					"CheckInDate": "2019-03-24",
					"Location": "new york",
					"Nights": "2",
					"RoomType": "king"
				}
			},
			{
				"name": "session",
				"dataType": "json",
				"value": null
			},
			{
				"name": "var1",
				"datatype": "text",
				"value": null
			}
		],
		"workflowOutputs": [{
				"name": "dialogAction",
				"dataType": "json"
			},
			{
				"name": "output2_bool",
				"dataType": "boolean",
				"value": true
			}
		],
		"workflowSteps": [{
				"id": "ws1",
				"type": 5,
				"desc": "description of workflow step 2",
				"nextStep": "ws2",
				"config": {
					"inputs": [{
						"name": "{!workflowOutputs.output2_bool}",
						"data": true
					}]
				}
			},
			{
				"id": "ws2",
				"type": 4,
				"desc": "description of workflow step 2",
				"nextStep": "ws3",
				"nextStepWhenTrue": "ws3.1",
				"nextStepWhenFalse": "ws3.2",
				"config": {
					"inputs": [{
						"name": "{!workflowOutputs.output2_bool}",
						"condition": "=",
						"data": true
					}]
				}
			},
			{
				"id": "ws3.1",
				"type": 5,
				"desc": "description of workflow step 2",
				"nextStep": "ws4",
				"config": {
					"inputs": [{
						"name": "{!workflowOutputs.dialogAction}",
						"data": {
							"sessionAttributes": {},
							"dialogAction": {
								"type": "Delegate",
								"slots": {
									"CheckInDate": "{!workflowInput.slot.CheckInDate}",
									"Location": "{!workflowInput.slot.Location}",
									"Nights": "{!workflowInput.slot.Nights}",
									"RoomType": "{!workflowInput.slot.RoomType}"
								}
							}
						}
					}]
				}
			},
			{
				"id": "ws3.2",
				"type": 5,
				"desc": "description of workflow step 2",
				"nextStep": "ws4",
				"config": {
					"inputs": [{
						"name": "{!workflowOutputs.dialogAction}",
						"data": {
							"sessionAttributes": {},
							"dialogAction": {
								"type": "ElicitSlot",
								"intentName": "BookHotel",
								"slots": {
									"CheckInDate": "{!workflowInput.slot.CheckInDate}",
									"Location": "{!workflowInput.slot.Location}",
									"Nights": "{!workflowInput.slot.Nights}",
									"RoomType": "{!workflowInputs.var1}"
								},
								"slotToElicit": "RoomType",
								"message": null
							}
						}
					}]
				}
			},
			{
				"id": "ws4",
				"type": 2,
				"nextStep": "ws5",
				"title": "read",
				"desc": "",
				"config": {
					"activityConfiguration": {
						"readObject": "CCS_case",
						"fields": {
							"caseIdPk_int": {},
							"caseNumber_txt": "plm",
							"originId_int": 9,
							"contactIdPk_int": {},
							"accountIdPk_int": {},
							"assetIdPk_int": {},
							"caseOwner_txt": "roopalir@appcino.com",
							"reasonId_int": {},
							"priorityId_int": {},
							"statusId_int": 2,
							"typeId_int": 20,
							"businessHoursId_int": {},
							"parentCaseIdPk_int": {},
							"isClose_bool": "zxf",
							"isCloseWhenCreated_bool": {},
							"isDeleted_bool": {},
							"isEscalated_bool": "def",
							"subject_txt": "Test for 11 :44 date 12/02",
							"description_txt": "abc",
							"webComapany_txt": "12/02",
							"webEmail_txt": {},
							"webName_txt": {},
							"webPhone_txt": {},
							"closedOn_dtm": "{}",
							"createdBy_txt": {},
							"createdOn_dtm": "",
							"lastModifiedBy_txt": {},
							"lastModifiedOn_dtm": ""
						}
					}
				}
			},
			{
				"id": "ws5",
				"type": 1,
				"nextStep": null,
				"title": "read",
				"desc": "",
				"config": {
					"activityConfiguration": {
						"readObject": "CCS_case",
						"inputs": [{
							"field": "caseIdPk_int",
							"operator": "=",
							"value": "{!ws4.caseIdPk_int}"
						}],
						"outputs": [
							"caseIdPk_int",
							"caseNumber_txt",
							"reasonId_int",
							"priorityId_int",
							"typeId_int",
							"subject_txt"

						]
					}
				}
			}
		]
	}
}"""


workflowInput = """
{
"workflowInputs":[
					{
						"name":"slot",
						"dataType":"json",
						"value":{
									"CheckInDate": "2",
									"Location": "new york",
									"Nights": null,
									"RoomType": null
								}
					},
					{
						"name":"session",
						"dataType":"json",
						"value":{
						          "value1" : "5"  
						        }
					},
		{
		"name" : "var1",  
		"value" : null
		}
				]
}
"""

class WorkFlow():

  def __init__(self,json_data,jsonInputs):
    self.workflowInputs = jsonInputs["workflowInputs"]
    self.workflowOutputs = json_data["workflow"]["workflowOutputs"]
    self.workflowSteps = json_data["workflow"]["workflowSteps"]
    self.inputs = {item['id']:item for item in json_data["workflow"]["workflowSteps"]}



json_data.replace("\\n\\r"," ")
workflowInput.replace("\\n\\r"," ")

jsondata = json.loads(json_data)
workflowInput = json.loads(workflowInput)

apis = {'ws4':'https://bpmdev.appcino.com/suite/webapi/FoR8Gg',
		'ws5':'https://bpmdev.appcino.com/suite/webapi/QcJTTQ',
		'wl27': 'https://bpmdev.appcino.com/suite/webapi/FoR8Gg',
		'wl28': 'https://bpmdev.appcino.com/suite/webapi/QcJTTQ',
		'wl29': 'https://bpmdev.appcino.com/suite/webapi/FoR8Gg'}

def renderRequest(requestId,apis,inputs,outputs,workflowInputs,workflowOutputs):


  input = json.dumps(inputs[requestId]['config'])

  type = inputs[requestId]['type']
  api = '' if int(type) == 4 or int(type) == 5 else apis[requestId]
  nextStep = ac.takeDecision(inputs[requestId],workflowOutputs,workflowInputs) if int(type) == 4  else inputs[requestId]['nextStep']

  if int(type) == 4:
    # print(nextStep)
    pass

  elif int(type) == 5:
    input = json.loads(input)["inputs"]

    ac.setProperty(workflowOutputs,input,workflowInputs)

  else:
    replacedInput = ac.replaceValue(input, outputs, ac.searchValues(input), workflowInputs, workflowOutputs)
    input = input if replacedInput == '' else replacedInput
    # return
    r1 = requests.post(url=api, data=input, auth=('Aditya', 'NeverGiveUp:)'))

    outputs[requestId] = r1.json()

  return nextStep

def mainHandler(requestId,apis,inputs,outputs,workflowInputs,workflowOutputs):

    nextStep = renderRequest(requestId,apis,inputs,outputs,workflowInputs,workflowOutputs)

    if nextStep is None:
      print('complete')

      for items in workflowOutputs:
        if str(items).__contains__("dialogAction"):
          ls = items["value"]["dialogAction"]["slots"]
          for a in ls:
            if ls[a] == "":
              ls[a] = None

      return
    else:
      mainHandler(nextStep,apis,inputs,outputs,workflowInputs,workflowOutputs)


workFl = WorkFlow(jsondata,workflowInput)

# outputs = {'ws1': [{'caseIdPk_int': 368, 'caseNumber_txt': 'def', 'originId_int': 9, 'caseOwner_txt': 'roopalir@appcino.com', 'caseAssignee_txt': '', 'priorityId_int': 2, 'typeId_int': 20, 'isClose_bool': True, 'subject_txt': 'abc', 'description_txt': '', 'webComapany_txt': '12/02', 'webEmail_txt': '[]', 'webName_txt': '[]', 'webPhone_txt': '[]', 'createdBy_txt': '[]', 'lastModifiedBy_txt': '[]'}]}
outputs = {}


# renderRequest("ws5",apis,workFl.inputs,outputs,workFl.workflowInputs,workFl.workflowOutputs)


mainHandler("ws1",apis,workFl.inputs,outputs,workFl.workflowInputs,workFl.workflowOutputs)

print(outputs)



