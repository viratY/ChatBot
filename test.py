import json


import test_functions as tf

import json_data as js

json_data = js.json_data
# json_data.replace("\\n\\r"," ")
workflowInputs = js.workflowInputs

jsondata = json.loads(json_data)
workflowInput = json.loads(workflowInputs)

class WorkFlow():

  def __init__(self,json_data,jsonInputs={}):
    self.workflowInputs = jsonInputs["workflowInputs"]
    self.workflowOutputs = json_data["workflow"]["workflowOutputs"]
    self.workflowSteps = json_data["workflow"]["workflowSteps"]
    self.inputs = {item['id']:item for item in json_data["workflow"]["workflowSteps"]}

workFl = WorkFlow(jsondata,workflowInput)

# print(workFl.workflowSteps[4]["config"])

interOutputs = {'ws1':{"caseIdpk_int":True}}

# tf.setProperty(workFl.workflowSteps[2]["config"]["inputs"][0],
#                   workflowInput=workFl.workflowInputs,
#                   workflowOutput=workFl.workflowOutputs,
#                   interOutput=interOutputs)


# print(tf.takeDecision(workFl.workflowSteps[1]["config"]["inputs"],
#                  workflowInput=workFl.workflowInputs,workflowOutput=workFl.workflowOutputs))

# tf.apicall(workFl.workflowSteps[4]["config"],
#            workflowInput=workFl.workflowInputs,
#            workflowOutput=workFl.workflowOutputs,
#            interOutput=interOutputs)

def mainHandler(requestId,workflow,apiList,interOutputs):
  """
  :param requestId: workflow Step Id
  :param workflow: workflow Object
  :param apiList: List of api endpoints
  :param interOutputs: intermediate output values
  :return: nextStep of the workflowStep
  """

  workflowStepInput = next(item for item in workflow.workflowSteps if item["id"]==requestId)
  # print(workflowStepInput)
  type = int(workflowStepInput['type'])
  # print(type)
  api = '' if type == 4 or type == 5 else apiList[requestId]

  if type == 4:

    decision = tf.takeDecision(workflowStepInput["config"]["inputs"],
                                workflowInput=workflow.workflowInputs,
                                workflowOutput=workflow.workflowOutputs)

    nextStep = workflowStepInput["nextStepWhenTrue"] if decision == True else workflowStepInput["nextStepWhenFalse"]
    # print(nextStep)

  elif type == 5:
    # print(workflowStepInput)
    tf.setProperty(workflowStepInput["config"]["inputs"][0],
                      workflowInput=workflow.workflowInputs,
                      workflowOutput=workflow.workflowOutputs,
                      interOutput=interOutputs)

    nextStep = workflowStepInput['nextStep']

  else:
    api = apiList[requestId]
    output = tf.apicall(workflowStepInput["config"],
                           workflowInput=workflow.workflowInputs,
                           workflowOutput=workflow.workflowOutputs,
                           interOutput=interOutputs,
                           api=api)

    interOutputs[requestId] = output
    nextStep = workflowStepInput['nextStep']

  if nextStep is None:
    print('complete')
  else:
    nextStep = mainHandler(nextStep, workFl, js.apis, interOutputs)

  return nextStep

mainHandler("ws1",workFl,js.apis,interOutputs)

# print(interOutputs)
