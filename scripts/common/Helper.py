
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

notFullRooms = []

roomData = {"room":None,"players":[1]}


def sortNotFullRooms(notFullRooms, roomData):

    # 如果房间满人或者没人，则从队列中清理掉
    if (len(roomData['players']) == 0 or len(roomData['players']) == 5) and roomData in notFullRooms:

        del notFullRooms[notFullRooms.index(roomData)]
        print("count = %d %r" % (len(notFullRooms), notFullRooms))
        return

    if len(notFullRooms) <= 0:
        notFullRooms.append(roomData)
        print("count = %d %r" % (len(notFullRooms), notFullRooms))
        return

    # 如果房间还有空位，则排队
    for notRoom in notFullRooms:

        if notRoom == roomData:
            break

        index = notFullRooms.index(notRoom)

        if len(roomData['players']) > len(notRoom['players']):
            notFullRooms.insert(index, roomData)
            break
        elif len(notFullRooms) == (index + 1):
            notFullRooms.append(roomData)

    print("count = %d %r" % (len(notFullRooms),notFullRooms))

# sortNotFullRooms(notFullRooms,roomData)
#
# roomData2 = {"room":None,"players":[2]}
#
# sortNotFullRooms(notFullRooms,roomData2)

roomData = None

if roomData:
    print("test")







