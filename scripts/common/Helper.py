
import socket
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



def comp(x, y):
    if x < y:
        return 1
    elif x > y:
        return -1
    else:
        return 0

test = []

data1 = 2
data2 = 1
data3 = 0

test.append(data1)
test.append(data2)
test.append(data3)

print(2 not in test)









