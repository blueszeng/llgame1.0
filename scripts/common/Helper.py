
import re

def Round(num):
    #去掉小数点后两位
    return float('%.2f' % num)

def cutHttp(str,start,end):
    index1 = str.find(start)
    index2 = str.rfind(end) + 1

    result = str[index1: index2]

    return result

def cutInHttp(str,start,end):
    slen = len(start)
    index1 = str.find(start)
    index2 = str.rfind(end)

    result = str[index1+slen: index2]
    print(result)

    return result

def convertDict(httpStr,str1,str2):
    if httpStr == '':
        return {}

    datas = re.split(str1,httpStr)
    # print(datas)

    result = {}
    for data in datas:
        list = re.split(str2,data)
        result[list[0]] = list[1]
    print(result)

    return result


import json
cards = [3,2,1]

data = json.loads(json.dumps(cards))
print(data[1])





