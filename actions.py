import json
import requests
import operator
import re
import ast
from datetime import datetime


ops = { "+": operator.add, ">": operator.ge, "=": operator.eq, "<": operator.lt, "in":lambda a,b:a in b }

conversion = {"text":str, "number":int, "date":lambda s : datetime.strptime(s, '%Y-%m-%d'), "bool":lambda value: value.lower() in ("yes", "true", "t", "1") }

def convert(item):
    dataType = item["dataType"]
    item["name"] = conversion[dataType](item["name"]) if isinstance(item["name"], str) else item["name"]
    item["data"] = conversion[dataType](item["data"]) if isinstance(item["data"], str) else item["data"]
    # print(ops[item["condition"]](item["name"],item["data"]))
    return item


def replace(string,value,item):
    if value is None:
        return string.replace('{!' + item + '}', '')
    else:
        stri = ""
        if isinstance(value,str):
            stri = string.replace('{!' + item + '}', str(value))
        else:
            stri = string.replace('"{!' + item + '}"', str(value))
            stri = string.replace("'{!" + item + "}'", str(value)) if stri.__contains__(item) else stri
        return stri

def searchValues(s):
	return re.findall(r'{!(.*?)}', s)


def checkDecision(input, outputs, workflowInput):
    for item in input:

        outputValue = searchValues(str(item))
        outputValue = item["data"] if len(outputValue) == 0 else outputValue
        output = ""
        if str(outputValue).__contains__("."):
            for a in outputValue:
                if str(a).__contains__("workflowInput"):
                    item = getdictValue(a, workflowInput, outputs, item)
                else:
                    key2, value2 = a.split(".")
                    for items in outputs:
                        if items["name"] == value2:
                            output = items["value"]
                    item = replace(str(item), output, a)
                    item = ast.literal_eval(item)

        # item = convert(item)
        decision = ops[item["condition"]](item["name"],item["data"])
        if decision == True:
            continue
        else:
            break
    return decision

def takeDecision(json_input,output,workflowInput):
    input = json_input["config"]["inputs"]
    decision = checkDecision(input,output,workflowInput)
    return json_input["nextStepWhenTrue"] if decision == True else json_input["nextStepWhenFalse"]

def setProperty(WorkFlowOutput,input,workflowInput,output):

    for item in input:
            outputValue = searchValues(str(item["data"]))
            key1,value1 = str(searchValues(item["name"])[0]).split(".")
            for items in WorkFlowOutput:
                if items["name"] == value1:
                    if str(outputValue).__contains__(".") and len(outputValue)>0:

                        for a in outputValue:
                            if str(a).__contains__("workflowInput"):
                                item = getdictValue(a, workflowInput, WorkFlowOutput, item)
                                items["value"] = outputValue

                            elif str(a).__contains__("workflowOutputs"):
                                key2, value2 = str(outputValue[0]).split(".")
                                items["value"] = filterDict(WorkFlowOutput,"name","value",value2)

                            else:
                                key2, value2 = str(outputValue[0]).split(".")
                                a = replace(str(item["data"]),output[key2][0][value2],outputValue[0])
                                items["value"] = a

                    else:
                        outputValue = item["data"]
                        items["value"] = outputValue



def filterDict(dict,key,value,keyvalue):
    return next(items[value] for items in dict if items[key]==keyvalue)


def getdictValue(value,workflowInputs,outputs,input,type=0):

    # print("workflowinput"+str(workflowInputs))

    valueList = value.split(".")
    # print("valueList" + str(valueList))

    try:

        if len(valueList) == 3:
            replacedValue =  next(items["value"][valueList[2]] for items in workflowInputs if items["name"]==valueList[1])
            # print("replaced" + str(replacedValue))
        else:
            replacedValue =  next(items["value"] for items in workflowInputs if items["name"] == valueList[1])

        s = replace(str(input),replacedValue,value)

        # json_acceptable_string = s.replace("'", "\"")
        d = ast.literal_eval(s)

    except StopIteration:
        d = ""

    if type == 4:
        return replacedValue
    else:
        return d


def replaceValue(input, output, params, workflowInputs, workflowOutput):
  if len(params)==0:
    return ''
  else:
    item = params[0]

    if str(item).__contains__("workflowInput"):
      input = json.dumps(getdictValue(item, workflowInputs, output, input))

    else:
      key, value = item.split('.')
      val = output[key][0][value]
      input = replace(str(input), val, item)

    params.remove(item)
    if len(params) > 0:
      replaceValue(input, output, params, workflowInputs, workflowOutput)
    else:
      pass
    return input


workflow= {
    "caseIdPk_int":"5",
    "case_text":"This is case text"
}

# setProperty(workflowOutput,input["config"]["inputs"],workflow)
# print(workflowOutput)
