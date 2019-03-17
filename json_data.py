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
					"caseNumber": null,
					"subject": null,
					"description": null
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
									"caseNumber": "{!workflowInput.slot.caseNumber}",
									"subject": "{!workflowInput.slot.subject}",
									"description": "{!workflowInput.slot.description}"									
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
								"intentName": "createcase",
								"slots": {
									"caseNumber": "{!workflowInput.slot.caseNumber}",
									"subject": "{!workflowInput.slot.subject}",
									"description": "{!workflowInput.slot.description}"	
								},
								"slotToElicit": "caseNumber",
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
							"caseNumber_txt": "{!workflowInput.slot.caseNumber}",
							"subject_txt": "{!workflowInput.slot.subject}",
							"description_txt": "{!workflowInput.slot.description}"							
						}
					}
				}
			},
			{
				"id": "ws5",
				"type": 1,
				"nextStep": "ws6",
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
			},
			{
				"id": "ws6",
				"type": 5,
				"desc": "description of workflow step 2",
				"nextStep": null,
				"config": {
					"inputs": [{
						"name": "{!workflowOutputs.dialogAction}",
						"data": {
							"sessionAttributes": {},
							"dialogAction": 
							{   "type": "Close",
								"fulfillmentState": "Fulfilled",								
								"message" : {
								"contentType": "PlainText",
								"content": "Thanks, I have placed your reservation. your case number is {!ws5.caseNumber_txt}"
								}														
							}
						}
					}]
				}
			},
			{  
   "id":"ws7",
   "type":6,
   "communicationType":"email",
   "desc":"description of workflow step 2",
   "nextStep":null,
   "config":{  
      "inputs":[  
         {  
            "name":"to",
            "data":"viraty@appcino.com"
         },
         {  
            "name":"from",
            "data":"appcinocustomercare@appcino.com"
         },
         {  
            "name":"subject",
            "data":"This is a test email from Appcino {!workflowInput.slot.subject}"
         },
         {  
            "name":"body",
            "data":"This is email body in html or plain text {!workflowInput.slot.subject}"
         },
         {  
            "name":"attachments",
            "data":[  
               25458,
               25460,
               21063
            ]
         }
      ]
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
									"caseNumber": "123",
					                "subject": "This is subject",
					                "description": "This is description"               
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
		'wl29': 'https://bpmdev.appcino.com/suite/webapi/FoR8Gg',
        'ws7':'https://bpmdev.appcino.com/suite/webapi/aiYPaA'}

def renderRequest(requestId,apis,inputs,outputs,workflowInputs,workflowOutputs):


  input = json.dumps(inputs[requestId]['config'])

  type = inputs[requestId]['type']
  api = '' if int(type) == 4 or int(type) == 5 else apis[requestId]
  nextStep = ac.takeDecision(inputs[requestId],workflowOutputs,workflowInputs) if int(type) == 4  else inputs[requestId]['nextStep']
  # print(nextStep)
  if int(type) == 4:
    # print(nextStep)
    pass

  elif int(type) == 5:
    input = json.loads(input)["inputs"]

    ac.setProperty(workflowOutputs,input,workflowInputs,outputs)

  else:
    replacedInput = ac.replaceValue(input, outputs, ac.searchValues(input), workflowInputs, workflowOutputs)
    input = input if replacedInput == '' else replacedInput

    r1 = requests.post(url=api, data=input, auth=('Aditya', 'NeverGiveUp:)'))
    print(r1)

    outputs[requestId] = r1.json()

  return nextStep

def mainHandler(requestId,apis,inputs,outputs,workflowInputs,workflowOutputs):

    nextStep = renderRequest(requestId,apis,inputs,outputs,workflowInputs,workflowOutputs)

    if nextStep is None:
      print('complete')

      for items in workflowOutputs:
        if str(items).__contains__("slots"):
          ls = items["value"]["dialogAction"]["slots"]
          for a in ls:
            if ls[a] == "":
              ls[a] = None

      return
    else:
      mainHandler(nextStep,apis,inputs,outputs,workflowInputs,workflowOutputs)


workFl = WorkFlow(jsondata,workflowInput)

# outputs = {"ws5":[{"caseNumber_txt":"def"}]}
outputs = {}


renderRequest("ws7",apis,workFl.inputs,outputs,workFl.workflowInputs,workFl.workflowOutputs)


# mainHandler("ws1",apis,workFl.inputs,outputs,workFl.workflowInputs,workFl.workflowOutputs)
#
print(workFl.workflowOutputs)



