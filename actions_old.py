import json
import requests
import operator
import re
import ast


ops = { "+": operator.add, ">": operator.ge, "=": operator.eq }

def replace(string,value,item):
    if value is None:
        return string.replace('{!' + item + '}', '')
    else:
        return string.replace('{!' + item + '}', str(value)) if isinstance(value,str) else string.replace('"{!' + item + '}"', str(value))

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
                    item = replace(json.dumps(item), output, a)
                    item = ast.literal_eval(item)

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

def setProperty(output,input,workflowInput):

    for item in input:
            outputValue = searchValues(str(item["data"]))
            key1,value1 = str(searchValues(item["name"])[0]).split(".")
            for items in output:
                if items["name"] == value1:
                    if str(outputValue).__contains__(".") and len(outputValue)>0:

                        for a in outputValue:
                            if str(a).__contains__("workflowInput"):
                                item = getdictValue(a, workflowInput, output, item)
                                outputValue = item["data"]
                                items["value"] = outputValue

                            else:
                                key2, value2 = str(outputValue[0]).split(".")
                                items["value"] = filterDict(output,"name","value",value2)
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
