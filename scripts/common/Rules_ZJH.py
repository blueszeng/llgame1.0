# -*- coding: utf-8 -*-

from KBEDebug import *
import random

#玩家状态
PLAYER_STATE_GARK  = 0   #灰色状态
PLAYER_STATE_READY = 1   #准备状态
PLAYER_STATE_INGAME = 2  #游戏中
PLAYER_STATE_QIPAI = 3   #放弃

#房间状态
ROOM_STATE_READY    =   0  #准备好了
ROOM_STATE_TIMER    =   1  #计时阶段
ROOM_STATE_INGAME   =   2   #正在游戏
ROOM_STATE_FINISH   =   3   #游戏结束,清理断线玩家

ACTION_ROOM_NONE               = 0  #空
ACTION_ROOM_TIME               = 1  #下发房间时间
ACTION_ROOM_TIMER			   = 10 #准备
ACTION_ROOM_DISPATCH           = 12 #发牌
ACTION_ROOM_GENZHU             = 13 #跟住
ACTION_ROOM_JIAZHU             = 14 #加注
ACTION_ROOM_KANPAI             = 15 #看牌
ACTION_ROOM_QIPAI              = 16 #弃牌
ACTION_ROOM_BIPAI              = 17 #比牌
ACTION_ROOM_NEXT               = 18 #下一位
ACTION_ROOM_SETTLE             = 19 #游戏结算
ACTION_ROOM_PUBLICH            = 20 #公布玩家的牌
ACTION_ROOM_AUTOBIPAI          = 21 #有玩家金钱不足时或回合数到达，则自动比牌



DEBUG_ACTION_STRING = {ACTION_ROOM_TIME:"ACTION_ROOM_TIME",
                       ACTION_ROOM_TIMER: "ACTION_ROOM_TIMER",
                       ACTION_ROOM_DISPATCH:"ACTION_ROOM_DISPATCH",
                       ACTION_ROOM_GENZHU:"ACTION_ROOM_GENZHU",
                       ACTION_ROOM_JIAZHU:"ACTION_ROOM_JIAZHU",
                       ACTION_ROOM_KANPAI:"ACTION_ROOM_KANPAI",
                       ACTION_ROOM_QIPAI:"ACTION_ROOM_QIPAI",
                       ACTION_ROOM_BIPAI: "ACTION_ROOM_BIPAI",
                       ACTION_ROOM_NEXT:"ACTION_ROOM_NEXT",
                       ACTION_ROOM_SETTLE:"ACTION_ROOM_SETTLE",
                       ACTION_ROOM_PUBLICH:"ACTION_ROOM_PUBLICH",
                       ACTION_ROOM_AUTOBIPAI:"ACTION_ROOM_AUTOBIPAI"
                       }


# 负责炸金花的游戏规则
def reqRandomCards52():
    cards = []
    for i in range(1,53):
        cards.append(i)
        i+=1

    for i in range(0,52):
        index = random.randint(0,51)
        #DEBUG_MSG("range i =%i,index = %i " %(i,index))
        tmp = cards[i]
        cards[i] = cards[index]
        cards[index] = tmp

    return cards

def getCardsby(array, length):
    """获取数组的前n位数，并删掉"""
    list = []
    for i in range(length):
        list.append(array.pop(0))
    list = sortCards(list)
    INFO_MSG("Room.getCardsby CardsSize:%i,remainSize:%i" % (len(list), len(array)))
    return list


def sortCards(cards):

    for i in range(0,len(cards)):
        for j in range(i+1,len(cards)):
            if cards[i] <cards[j]:
                tmp = cards[i]
                cards[i] = cards[j]
                cards[j] = tmp
    return cards

def IsA23(cards):
    #检查牌组是否存在A23的情况，因为A是多值，不做处理
    levs = [12,1,0]
    result1 = True
    for lev in levs:
        result2 = False
        for card in cards:
            if int((card-1)/4) == lev:
                result2 = True
        if not result2:
            return result2
    return result1



def SortCards(cards):

    for i in range(0,len(cards)):
        for j in range(i+1,len(cards)):
            if cards[i] <cards[j]:
                tmp = cards[i]
                cards[i] = cards[j]
                cards[j] = tmp
    return cards

def CompareCards(cards1,cards2):
    """比较牌形大小 A == 49~52,return True 则为cards1胜利"""

    level1 = analysisCardsLevel(cards1)
    level2 = analysisCardsLevel(cards2)

    #level越少，则越大
    if level1 < level2:
        return True

    elif level1 == level2:
        if analysisCardsBig(cards1, cards2, level1):          #不是对子，则从大到小比较即可
            return True

    return False


LEVEL_STRING = {0: "豹子",1:"顺金",2: "金花",3: "顺子",4: "对子",5: "单牌"}
def analysisCardsLevel(cards):

    #AAA
    if int((cards[0] -1)/4) == int((cards[1] -1)/4) == int((cards[2]-1)/4):
        return 0

    # 顺金,同花顺
    if int(cards[2] + 8) == int(cards[1] + 4) == int(cards[0]):
        return 1

    #金花,花色相同
    if int((cards[0]-1)%4)  == int((cards[1]-1)%4) == int((cards[2]-1)%4):
        return 2

    # 顺子
    if int(((cards[2]-1)/4)+1) == int(((cards[1]-1)/4)) \
            and  int(((cards[1]-1)/4)+1) == int((cards[0]-1)/4):
        return 3

    #对子
    if int((cards[0]-1)/4) == int((cards[1]-1)/4) or int((cards[1]-1)/4) == int((cards[2]-1)/4):
        return 4

    return 5


def analysisCardsBig(cards1, cards2, level):

    if level == 4:
        #如果是对子
        if getCardsLevel(cards1,2) > getCardsLevel(cards2,2):
            return True
        elif getCardsLevel(cards1,2) < getCardsLevel(cards2,2):
            return False
        elif getCardsLevel(cards1,1) > getCardsLevel(cards2,1):
            return True
        elif getCardsLevel(cards1, 1) < getCardsLevel(cards2, 1):
            return False
        else:
            return False
    else:
        # 从大到小比较
        for i in range(0, len(cards1)):
            if int((cards1[i] - 1) / 4) > int((cards2[i] - 1) / 4):
                return True
            elif int((cards1[i] - 1) / 4) < int((cards2[i] - 1) / 4):
                return False

    return False

def getCardsLevel(cards,num):
    levs = {}
    for i in range(0,len(cards)):
        lev = int((cards[i]-1)/4)
        if lev in levs:
            levs[lev] += 1
        else:
            levs[lev] = 1

    for key,value in levs.items():
        if value == num:
            return key
    return 0

# array = reqRandomCards52()
# tmp = []
# while len(array) > 3:
#     for i in range(3):
#         tmp.append(array.pop(0))
#     if not IsA23(tmp):
#         break
#     else:
#         tmp.clear()
# tmp = SortCards(tmp)
#
# print("cards = %r,array size = %r" % (tmp,len(array)))
