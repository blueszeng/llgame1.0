# -*- coding: utf-8 -*-
import KBEngine
import json
from Rules_DDZ import *
from interfaces.RoomEntity import *
import Helper

class DdzRoom(KBEngine.Entity,RoomEntity):

    def __init__(self):
        KBEngine.Entity.__init__(self)
        RoomEntity.__init__(self)

        self.position = (9999.0, 0.0, 0.0)

        self.players    = {}
        self.cards      = []
        self.curfen     = Helper.Round(self.difenC)
        self.multiple   = 1

        #房间时间
        self.roomtime   = 15
        self.curRoomtime = 0

        #当前玩家ID
        self.curCid     = 0
        self.beginCid   = 0
        self.dzCid      = 0
        self.curScore   = 0

        #叫牌不成次数
        self.giveupCount = 2

        #霸权ID
        self.powerCid   = 0
        self.powerCards = []

        KBEngine.setSpaceData(self.spaceID, "curfen", "%.2f" % self.curfen)
        KBEngine.setSpaceData(self.spaceID, "multiple", str(self.multiple))
        KBEngine.setSpaceData(self.spaceID, "roomtime", str(self.roomtime))
        KBEngine.setSpaceData(self.spaceID, "status", str(self.statusC))

    def setStatus(self, status):

        DEBUG_MSG("%r::setStatus() space[%r] status[%r]" % (self.className, self.spaceID, status))

        self.statusC = status

        for pp in self.players.values():
            pp.setStatus(status)

        KBEngine.setSpaceData(self.spaceID, "status", str(self.statusC))

        self.base.setStatus(status)

    def onEnter(self, player):

        #分配座位顺序
        for i in range(1, 4):
            have = False
            for pp in self.players.values():
                if i == pp.cid:
                    have = True
                    break
            if not have:
                player.cid= i
                break

        self.players[player.cid] = player

        DEBUG_MSG('%r::onEnter() space[%d] cid[%i]' % (self.className, self.spaceID, player.cid))

        #满足开局人数
        if len(self.players.values()) == 3:
            self.setStatus(ROOM_STATE_INGAME)
            self.addTimerMgr(1,0,ACTION_ROOM_DISPATCH)

    def onLeave(self, player):
        DEBUG_MSG('%r::onLeave() space[%d] cid[%i]' % (self.className, self.spaceID, player.cid))

        if player.cid in self.players:
            del self.players[player.cid]

            if len(self.players) == 0:
                self.destroy()

    def dispatchCards(self):
        """发牌"""
        DEBUG_MSG("%r::dispatchCards() space[%d]" % (self.className,self.spaceID))

        self.cards = reqRandomCards54()

        for pp in self.players.values():

            pp.cards        = getCardsby(self.cards, 17)
            pp.cardCount    = len(pp.cards)

    def nextPlayer(self,userArg):

        if self.curCid == 0:
            # 随机一位玩家先手
            self.curCid     = random.randint(1, len(self.players))
        else:
            self.curCid     = self.curCid % 3 + 1

        #重置房间时间
        self.curRoomtime = self.roomtime
        self.delTimerMgr(0)
        self.addTimerMgr(1, 1, userArg)

        if userArg == ACTION_ROOM_JIAOPAI_NEXT:

            data = {}
            data["curCid"]      = self.curCid
            data["curScore"]    = self.curScore
            data["type"]        = self.players[self.curCid].type

            KBEngine.setSpaceData(self.spaceID, "ACTION_ROOM_JIAOPAI_NEXT", json.dumps(data))

        elif userArg == ACTION_ROOM_NEXT:

            data = {}
            data["curCid"] = self.curCid
            data["powerCid"] = self.powerCid

            #如果又是自己，则powerCards为空
            if self.curCid == self.powerCid:
                data["powerCards"] = []
            else:
                data["powerCards"]  = copyList(self.powerCards)

            KBEngine.setSpaceData(self.spaceID, "ACTION_ROOM_NEXT", json.dumps(data))

    def reqMessage(self,player,action,buf):
        DEBUG_MSG("%r::reqMessage() %r space[%d] player[%r] buf[%r]"
                  % (self.className,DEBUG_ACTION_STRING.get(action),self.spaceID,player.cid,buf))

        #不是当前玩家，则默认为超时操作，不予处理
        if self.curCid != player.cid:
            return

        if action == ACTION_ROOM_JIAOPAI:
            self.onMessage_ACTION_ROOM_JIAOPAI(player,action,buf)

        elif action == ACTION_ROOM_CHUPAI:
            self.onMessage_ACTION_ROOM_CHUPAI(player,action,buf)

    def onMessage_ACTION_ROOM_JIAOPAI(self,player,action,value):

        score = int(value)
        player.curScore = score

        if score <= 3:

            if self.curScore < score:

                self.dzCid      = player.cid
                self.curScore   = score
                self.curfen     = self.difenC * score

                KBEngine.setSpaceData(self.spaceID, "curfen", "%.2f" % self.curfen)

            #分值最大的玩家成为地主
            if score == 3 or (getLastCid(self.beginCid) == player.cid and (self.curScore != 0 or self.giveupCount == 0)):

                #如果叫牌流程为0，且未确定dzCid，则beginCid为地主
                if self.giveupCount == 0 and self.dzCid == 0:
                    self.dzCid = self.beginCid

                DEBUG_MSG("DdzRoom::onMessage_ACTION_ROOM_JIAOPAI dzCid[%d] beginCid[%d]" % (self.dzCid,self.beginCid))

                self.curCid     = self.dzCid
                self.powerCid   = self.dzCid

                for pp in self.players.values():

                    if pp.cid != self.dzCid:
                        pp.type = 2
                    else:
                        threeCards  = getCardsby(self.cards,3)
                        pp.type     = 1

                        pp.cards.extend(threeCards)
                        pp.cards     = sortCards(pp.cards)
                        pp.cardCount = len(pp.cards)

                        data = {}
                        data["cards"] = threeCards
                        KBEngine.setSpaceData(self.spaceID, "threeCards", json.dumps(threeCards))

            elif getLastCid(self.beginCid) == player.cid and self.curScore == 0:
                #如果没人叫分，则重新发牌
                self.beginCid = 0
                self.giveupCount -= 1
                self.addTimerMgr(1, 0, ACTION_ROOM_DISPATCH)
                return

            elif self.beginCid == 0:
                #记录开始叫牌的玩家cid,用于判定是否结束叫分流程
                self.beginCid = player.cid

        elif score > 10 and score <= 12:

            player.multiple = (score - 10)

            if getLastCid(self.dzCid) == player.cid:

                self.nextPlayer(ACTION_ROOM_NEXT)
                return

        self.nextPlayer(ACTION_ROOM_JIAOPAI_NEXT)

    def onMessage_ACTION_ROOM_CHUPAI(self,player,action,buf):

        if buf == "":
            player.showCards = []
        else:
            player.showCards = json.loads(buf)

        cards = player.showCards
        if len(cards) > 0:

            self.powerCid   = player.cid
            self.powerCards = cards

            if checkCardType(cards) == CARDS_TYPE_AAAA or checkCardType(cards) == CARDS_TYPE_KING:

                self.multiple *= 2
                KBEngine.setSpaceData(self.spaceID, "multiple", str(self.multiple))

            #to do error
            handCards = player.cards

            for card in cards:
                handCards.remove(card)

            player.cards        = handCards
            player.cardCount    = len(player.cards)

            if player.cardCount == 0:
                self.addTimerMgr(1.5, 0, ACTION_ROOM_SETTLE)
            else:
                self.nextPlayer(ACTION_ROOM_NEXT)
        else:
            self.nextPlayer(ACTION_ROOM_NEXT)

    def onTimer(self, id, userArg):
        """
        KBEngine method
        """
        if userArg == ACTION_ROOM_DISPATCH:

            self.sendAllClients(ACTION_ROOM_DISPATCH, "")
            self.dispatchCards()

            self.addTimerMgr(1, 0, ACTION_ROOM_STARTGAME)

        if userArg == ACTION_ROOM_STARTGAME:

            self.nextPlayer(ACTION_ROOM_JIAOPAI_NEXT)

        elif userArg == ACTION_ROOM_JIAOPAI_NEXT or userArg == ACTION_ROOM_NEXT:

            self.curRoomtime -= 1
            player = self.players[self.curCid]

            if self.curRoomtime <= 0:

                self.delTimerMgr(0)
                self.onOuttime(userArg,player)

            elif player.tuoguan == 1:

                self.delTimerMgr(0)
                self.onAi(userArg, player)

        elif userArg == ACTION_ROOM_SETTLE:
            self.onSettle()

    def onOuttime(self,userArg,player):
        """超时处理"""

        if userArg == ACTION_ROOM_JIAOPAI_NEXT:

            if player.tuoguan == 0:
                player.tuoguan = 1

            if self.curScore < 3 and player.type == 0:
                value = "0"
            else:
                value = "11"

            self.reqMessage(player, ACTION_ROOM_JIAOPAI, value)

        elif userArg == ACTION_ROOM_NEXT:

            if player.tuoguan == 0:
                player.tuoguan = 1

                if player.cid == self.powerCid:
                    self.onAi(ACTION_ROOM_NEXT,player)
                else:
                    self.reqMessage(player, ACTION_ROOM_CHUPAI, "")

    def onAi(self,userArg,player):
        """托管"""

        if userArg == ACTION_ROOM_JIAOPAI_NEXT:
            self.onOuttime(userArg,player)

        elif userArg == ACTION_ROOM_NEXT:
            if self.curCid == self.powerCid:
                data = getMinCards(player.cards)
            else:
                data = getAICards(player.cards, self.powerCards)

            self.reqMessage(player, ACTION_ROOM_CHUPAI, json.dumps(data))

    def onSettle(self):

        winPlayer   = self.players[self.curCid]
        dzPlayer    = self.players[self.dzCid]

        baseGold    = round(self.curfen * self.multiple,2)
        allMult     = 0

        for pp in self.players.values():
            if pp.type == 2:
                allMult += pp.multiple

        datas = {}
        datas["multiple"]   = self.multiple
        datas["curfen"]     = self.curfen

        #地主赢
        if winPlayer.type == 1:

            canWinGold = baseGold * allMult
            realWinGold = 0.0

            if dzPlayer.gold < canWinGold:
                canWinGold = dzPlayer.gold

            newBaseGold = Helper.Round(canWinGold/allMult)

            for pp in self.players.values():

                settleGold = newBaseGold * pp.multiple

                if pp.type == 2 and pp.gold < settleGold:
                    settleGold  = Helper.Round(pp.gold)
                    realWinGold += settleGold
                    pp.gold    = 0.0

                elif pp.type == 2:
                    realWinGold += settleGold
                    pp.gold    -= settleGold

                pp.gold    = Helper.Round(pp.gold)

                data = {}
                data["settleGold"]    = -settleGold
                data["gold"]           = pp.gold
                data["cards"]          = copyList(pp.cards)

                datas[pp.cid]           = data
                pp.setGold(-settleGold)

            taxGold = round(realWinGold * self.taxRateC,2)
            KBEngine.globalData["Games"].addIncome(taxGold)

            realWinGold     -= taxGold
            dzPlayer.gold  += realWinGold

            dzPlayer.gold = Helper.Round(dzPlayer.gold)

            data = {}
            data["settleGold"]   = realWinGold
            data["gold"]         = dzPlayer.gold
            data["cards"]        = copyList(dzPlayer.cards)

            datas[dzPlayer.cid]   = data
            dzPlayer.setGold(realWinGold)

        else:
            newBaseGold = Helper.Round(dzPlayer.gold/allMult)
            realLoseGold = 0.0

            for pp in self.players.values():
                if pp.type == 2:

                    canWinGold = Helper.Round(baseGold * pp.multiple)

                    if pp.gold < canWinGold:
                        canWinGold = Helper.Round(pp.gold)

                    if canWinGold > (newBaseGold*pp.multiple):
                        canWinGold = (newBaseGold*pp.multiple)

                    realLoseGold += canWinGold
                    taxGold      =  round(canWinGold * self.taxRateC,2)
                    canWinGold   -= taxGold
                    pp.gold     += canWinGold
                    KBEngine.globalData["Games"].addIncome(taxGold)

                    pp.gold = Helper.Round(pp.gold)

                    data = {}
                    data["settleGold"]  = canWinGold
                    data["gold"]        = pp.gold
                    data["cards"]       = copyList(pp.cards)

                    datas[pp.cid] = data
                    pp.setGold(canWinGold)

            dzPlayer.gold -= realLoseGold

            #抹掉计算误差
            if self.players[self.dzCid].gold <= 0.01:
                self.players[self.dzCid].gold = 0.0

            dzPlayer.gold = Helper.Round(dzPlayer.gold)

            data = {}
            data["settleGold"]       = -realLoseGold
            data["gold"]             = dzPlayer.gold
            data["cards"]            = copyList(dzPlayer.cards)

            datas[self.dzCid]        = data
            dzPlayer.setGold(-realLoseGold)

        # 退出游戏状态
        self.setStatus(ROOM_STATE_FINISH)

        self.sendAllClients(ACTION_ROOM_SETTLE, json.dumps(datas))

        INFO_MSG("DdzRoom::onCompute() space[%d] data_json = [%r]" % (self.spaceID,json.dumps(datas)))

