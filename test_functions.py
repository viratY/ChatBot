import re
import json
import ast
import operator
import requests
from datetime import datetime


ops = { "+": operator.add, ">": operator.ge, "=": operator.eq, "<": operator.lt, "in":lambda a,b:a in b }

conversion = {"text":str, "number":int, "date":lambda s : datetime.strptime(s, '%Y-%m-%d'), "bool":lambda value: value.lower() in ("yes", "true", "t", "1") }

def convert(item):
    # print(item)
    dataType = item["dataType"]
    item["name"] = conversion[dataType](item["name"]) if isinstance(item["name"], str) else item["name"]
    item["data"] = conversion[dataType](item["data"]) if isinstance(item["data"], str) else item["data"]
    # print(ops[item["condition"]](item["name"],item["data"]))
    return item

def searchValues(s):
    """
    :param s:   string
    :return:    list of matched strings between {! }
    """
    return re.findall(r'{!(.*?)}', s)

def apicall(input,workflowInput={}, workflowOutput={}, interOutput={},api=""):
    """
    :param input:           input value
    :param workflowInput:   Input of the workflow
    :param workflowOutput:  Output of the workflow
    :param interOutput:     outputs of the intermediate steps
    :return: output of the api call
    """

    input = processValues(input,workflowInput,workflowOutput,interOutput)
    # print(input)
    r1 = requests.post(url=api, data=json.dumps(input), auth=('Aditya', 'NeverGiveUp:)'))
    return r1.json()[0]
    # r1 = requests.post(url=api, data=input, auth=('Aditya', 'NeverGiveUp:)'))

def setProperty(input,workflowInput={}, workflowOutput={}, interOutput={}):
    # print(input)
    key,value = searchValues(input["name"])[0].split(".")

    for item in workflowOutput:
        if item["name"] == value:
            item["value"] = processValues(input["data"],workflowInput,workflowOutput,interOutput)

    # print(workflowOutput)

def takeDecision(input,workflowInput,workflowOutput,interOutput={}):
    decision = ""
    for item in input:
        item = processValues(item,workflowInput,workflowOutput,interOutput)
        item = convert(item)
        decision = ops[item["condition"]](item["name"], item["data"])
        if decision == True:
            continue
        else:
            break

    return decision

def processValues(inDict, workflowInput={}, workflowOutput={}, interOutput={}):
    """
    :param inDict: input value
    :param workflowInput: Input of the workflow
    :param workflowOutput: Output of the workflow
    :param interOutput: outputs of the intermediate steps
    :return: preprocessed input value
    """
    # print("In processValues")

    replaceList = searchValues(json.dumps(inDict))

    if len(replaceList) == 0:                                   # Nothing to replace
        return inDict
    else:                                                       # Found values to replace
        # print(replaceList)

        item = replaceList[0]
        rpvalue = replaceValue(inDict,item,workflowInput,workflowOutput,interOutput)

        if len(replaceList)>0:
            rpvalue = processValues(rpvalue,workflowInput,workflowOutput,interOutput)
        else:
            pass
    # print(rpvalue)
    return rpvalue


def replaceValue(inDict,value,workflowInput={},workflowOutput={},interOutput={}):
    """
    :param  inDict: input value
    :param  value: value to be replaced
    :param  workflowInput: Input of the workflow
    :param  workflowOutput: Output of the workflow
    :param  interOutput: outputs of the intermediate steps
    :return: python object
    """
    # print(inDict)
    strRepr = json.dumps(value)                    # string representation of input
    # replacedValue = " "

    if strRepr.__contains__("workflowInput"):
        fetchValue = getValue(value, workflowInput)
        replacedValue = replaceChar(json.dumps(inDict), value, fetchValue)


    elif strRepr.__contains__("workflowOutputs"):
        fetchValue = getValue(value,workflowOutput)
         # '' if fetchValue is None else str.replace(json.dumps(inDict),'"{!'+value+'}"',str(fetchValue))
        replacedValue = replaceChar(json.dumps(inDict),value,fetchValue)

    else:

        key1,value1 =  value.split(".")
        # print(interOutput)
        fetchValue = interOutput[key1][value1]
        replacedValue = replaceChar(json.dumps(inDict),value,fetchValue)
        # print("Intermediate value")

    # print(replacedValue)

    return json.loads(replacedValue)


def getValue(value,source={}):
    """
    :param value:   value to be fetched
    :param source:      Source to get value from
    :return:    Dictionary
    """

    rawValue = value.split(".")
    # print(rawValue)
    if len(rawValue) == 3:
        for item in source:
            if item["name"] == rawValue[1]:
                # print(item["value"][rawValue[2]])
                return item["value"][rawValue[2]]

        # print("len in 3")
    else:
        # print(source)
        for item in source:
            if item["name"] == rawValue[1]:
                return item["value"]


def replaceChar(input,old,new):
    """
    :param input:   input string
    :param old:     value to be replaced
    :param new:     value to be replaced with
    :return: String
    """

    if new is None:
        val = str.replace(input,'"{!'+old+'}"','')
    elif isinstance(new,str):
        val = str.replace(input,'{!'+old+'}',new)
    else:
        # print(json.dumps(new))
        val = str.replace(input, '"{!' + old + '}"', json.dumps(new))

    # print(val)
    return val