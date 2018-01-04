import KBEngine
import json
from Rules_ZJH import *
from interfaces.LogicZjh import *
import Helper

class ZjhRoom(KBEngine.Entity,LogicZjh):

    def __init__(self):
        KBEngine.Entity.__init__(self)
        LogicZjh.__init__(self)
        self.position = (9999.0, 0.0, 0.0)

        # 房间时间
        self.roomTime   = 10
        self.curRoomTime = 0

        #先手ID
        self.firstCid = 0
        self.winCid  = 0

        #重置房间数据
        self.reset()

        KBEngine.setSpaceData(self.spaceID, "jzList", self.jzListC)

    def reset(self):
        #当前玩家
        self.curCid = 0

        #当前回合
        self.curRound = 0

        #当前低注
        self.curDizhu = self.dizhuC

        #总下注
        self.totalzhu = 0

        #下注记录，用于给观战玩家生成筹码界面
        self.chipsList = []

        self.curAction = ACTION_ROOM_NONE

        self.set_state(ROOM_STATE_READY)

        KBEngine.setSpaceData(self.spaceID, "dizhu", str(self.dizhuC))
        KBEngine.setSpaceData(self.spaceID, "curDizhu", str(self.curDizhu))
        KBEngine.setSpaceData(self.spaceID, "totalzhu", str(self.totalzhu))
        KBEngine.setSpaceData(self.spaceID, "roomtime", str(self.roomTime))
        KBEngine.setSpaceData(self.spaceID, "curRound", str(self.curRound))
        KBEngine.setSpaceData(self.spaceID, "state", str(self.stateC))

    def set_state(self,state):
        DEBUG_MSG("ZjhRoom::set_state space[%r] state[%r]" % (self.spaceID,state))

        self.stateC = state
        self.base.set_state(state)

        if state == ROOM_STATE_INGAME:
            for pp in self.players.values():
                pp.stateC = PLAYER_STATE_INGAME

        KBEngine.setSpaceData(self.spaceID, "state", str(self.stateC))

    def onEnter(self, player):
        """分配座位顺序"""
        for i in range(1, 6):
            have = False
            for pp in self.players.values():
                if i == pp.cid:
                    have = True
                    break
            if not have:
                player.cid = i
                break

        self.players[player.cid] = player

        DEBUG_MSG('%r::onEnter() space[%d] cid[%i]' % (self.className, self.spaceID, player.cid))

        #如果该房已开始游戏，则后面加入的玩家设置为灰色状态
        if self.stateC != ROOM_STATE_INGAME:
            player.stateC = PLAYER_STATE_READY
            if len(self.players) >= 2:
                self.addTimerMgr(1, 0, ACTION_ROOM_TIME)
        else:
            player.stateC = PLAYER_STATE_GARK

    def onLeave(self, player):

        DEBUG_MSG('%r::onLeave() space[%d] cid[%i]' % (self.className, self.spaceID, player.cid))

        if player.cid in self.players:
            del self.players[player.cid]

            if len(self.players) == 0:
                self.destroy()

    def onDispatchCards(self):
        """ 发牌 """
        cards = reqRandomCards52()
        for pp in self.players.values():
            pp.cards        = getCardsby(cards, 3)
            pp.cardCount    = len(pp.cards)

            pp.goldC     -= self.curDizhu
            pp.cost      += self.curDizhu
            pp.chip       = self.curDizhu

            self.totalzhu += self.curDizhu
            self.chipsList.append(self.curDizhu)

            KBEngine.setSpaceData(self.spaceID, "totalzhu", str(self.totalzhu))

            DEBUG_MSG("ZjhRoom::onDispatchCards Player[%r]" % (pp.cid))

    def onNextPlayer(self):

        if self.curCid == 0:

            self.curCid = random.randint(1, len(self.players))
            self.firstCid = self.curCid
            self.players[self.curCid].first = 1
        else:
            for i in range(0, 5):
                tCid = (self.curCid + i) % 5 + 1
                if tCid in self.players:
                    if self.players[tCid].stateC == PLAYER_STATE_INGAME:
                        self.curCid = tCid
                        break

        #计算回合数
        if self.firstCid == self.curCid:
            self.curRound += 1
            if(self.curRound <= 15):
                KBEngine.setSpaceData(self.spaceID, "curRound", str(self.curRound))
            else:
                self.addTimerMgr(1, 0, ACTION_ROOM_AUTOBIPAI)

        # 重置房间时间
        self.curRoomTime = self.roomTime
        self.delTimerMgr(0)
        self.addTimerMgr(1, 1, ACTION_ROOM_NEXT)

        #如果金币不足2倍，则自动比牌
        if self.players[self.curCid].goldC < self.curDizhu * 2:
            self.addTimerMgr(1,0,ACTION_ROOM_AUTOBIPAI)
        else:
            self.curAction = ACTION_ROOM_NONE
            self.sendAllClients(ACTION_ROOM_NEXT, str(self.curCid))
            DEBUG_MSG("ACTION_ROOM_NEXT cid[%d]" % (self.curCid))

    def onTimer(self, id, userArg):
        """
        KBEngine method.
        使用addTimer后， 当时间到达则该接口被调用
        @param id		: addTimer 的返回值ID
        @param userArg	: addTimer 最后一个参数所给入的数据
        """
        # EntityCommon.onTimer(self,id,userArg)
        super().onTimer(id,userArg)

        if userArg == ACTION_ROOM_TIME:
            self.curRoomTime = self.roomTime
            self.set_state(ROOM_STATE_READY)

            self.addTimerMgr(1,1,ACTION_ROOM_READY)
            self.sendAllClients(ACTION_ROOM_READY, str(self.curRoomTime))

        elif userArg == ACTION_ROOM_READY:
            self.curRoomTime -= 1

            if self.curRoomTime <= 0:
                self.delTimerMgr(0)
                self.set_state(ROOM_STATE_INGAME)
                self.onDispatchCards()
                self.onNextPlayer()

        elif userArg == ACTION_ROOM_NEXT:
            self.curRoomTime -= 1

            if self.curRoomTime <= 0:
                self.delTimerMgr(0)
                self.onQipai(self.players[self.curCid], userArg)

        elif userArg == ACTION_ROOM_SETTLE:
            #重置场景及玩家数据
            self.reset()
            for pp in self.players.values():
                pp.cost = 0.0
                pp.cards = []
                pp.cardCount = 0
                pp.lookcard = 1
                pp.stateC = PLAYER_STATE_READY

            if len(self.players) >= 2:
                self.addTimerMgr(1, 0, ACTION_ROOM_TIME)

        elif userArg == ACTION_ROOM_AUTOBIPAI:
            self.delTimerMgr(0)
            self.onAutoCompare(self.players[self.curCid])

    def reqMessage(self, player, action, buf):

        DEBUG_MSG("ZjhRoom::reqMessage() %r space[%d] player[%r] buf[%r]" % (DEBUG_ACTION_STRING.get(action), self.spaceID, player.cid, buf))

        #过滤玩家的重复操作
        if self.curCid == player.cid and self.curAction == action:
            return

        self.curAction = action

        if action == ACTION_ROOM_GENZHU:
            self.delTimerMgr(0)
            self.onGenzhu(player,buf)

        elif action == ACTION_ROOM_JIAZHU:
            self.delTimerMgr(0)
            self.onPlus(player,buf)

        elif action == ACTION_ROOM_BIPAI:
            self.delTimerMgr(0)
            self.onCompare(player,buf)

        elif action == ACTION_ROOM_QIPAI:
            self.delTimerMgr(0)
            self.onQipai(player,buf)

    def onGenzhu(self,player,buf):
        """跟注"""

        curChip = self.curDizhu * player.lookcard

        player.goldC -= curChip
        player.cost  += curChip
        player.chip  = curChip

        self.totalzhu += curChip
        KBEngine.setSpaceData(self.spaceID, "totalzhu", str(self.totalzhu))
        KBEngine.setSpaceData(self.spaceID, "curDizhu", str(self.curDizhu))

        self.onNextPlayer()

    def onPlus(self,player,buf):
        """加注"""
        list = json.loads(self.jzListC)
        plusIdx = int(buf) - 1

        if plusIdx   < len(list) and plusIdx >= 0:

            self.curDizhu = list[plusIdx]

            curChip = list[plusIdx] * player.lookcard

            player.goldC -= curChip
            player.cost += curChip
            player.chip = curChip
        else:
            ERROR_MSG("onPlus plusIdx = %d outline" % (plusIdx))
            return

        self.totalzhu += curChip
        KBEngine.setSpaceData(self.spaceID, "totalzhu", str(self.totalzhu))
        KBEngine.setSpaceData(self.spaceID, "curDizhu", str(self.curDizhu))

        self.onNextPlayer()

    def onCompare(self,player,buf):
        """比牌"""

        #todo 需处理客户端多次发送
        tCid = int(buf)
        if tCid in self.players:
            target = self.players[tCid]
        else:
            ERROR_MSG("%r::onCompare() tCid[%d] not in self.players" % (self.className,tCid))
            return

        #看牌比不看，为4倍钱
        if player.lookcard == 2 and target.lookcard == 1:
            mult = 4
        else:
            mult = 2

        curChip = self.curDizhu * mult

        #比牌玩家钱不足分在客户端处理，如果服务端收到钱不足的情况，不予处理
        if player.goldC < curChip:
            return
        else:
            player.goldC -= curChip
            player.cost += curChip
            player.chip = curChip

        bResult = CompareCards(player.cards,target.cards)

        data = {}
        data["playerCid"] = player.cid
        data["targetCid"] = target.cid
        data["result"] = bResult

        KBEngine.setSpaceData(self.spaceID, "compareResult", json.dumps(data))

        self.invoke3(3,self.onLastCompare,player,target,bResult)

    def onLastCompare(self,player,target,result):
        """比牌之后"""
        DEBUG_MSG("%r::onLastCompare()" % (self.className))
        if result:
            target.stateC = PLAYER_STATE_GARK
        else:
            player.stateC = PLAYER_STATE_GARK

        if self.onCheckResult():
            self.onSettle()
        else:
            self.onNextPlayer()

    def onAutoCompare(self,player):
        """
        系统强制比牌
        """
        nCid = self.getNextCid(self.curCid)
        nPlayer = self.players[nCid]
        bResult = CompareCards(player.cards,nPlayer.cards)

        #todo 检测是否已经只剩下一个玩家，还有满回合数的情况
        if bResult:
            self.addTimerMgr(5,0,ACTION_ROOM_AUTOBIPAI)

        data = {}
        data["playerCid"] = player.cid
        data["targetCid"] = nPlayer.cid
        data["result"] = bResult

        KBEngine.setSpaceData(self.spaceID, "compareResult", json.dumps(data))
        self.invoke3(3, self.onLastCompare, player, nPlayer, bResult)

    def onQipai(self,player,buf):

        player.stateC = PLAYER_STATE_QIPAI

        if self.onCheckResult():
            self.onSettle()
        else:
            self.onNextPlayer()

    def onCheckResult(self):
        """检测当局是否有玩家获胜了"""

        count = 0
        for pp in self.players.values():
            if pp.stateC == PLAYER_STATE_INGAME:
                count += 1
                self.winCid = pp.cid

        if count == 1:
            return True
        elif count == 0:
            ERROR_MSG("%r::onCheckResult() count == 0" % (self.className))
        else:
            self.winCid = 0

        return False

    def onSettle(self):
        """结算"""
        player = self.players[self.winCid]
        taxGold = Helper.Round((self.totalzhu - player.cost) * self.taxRateC)

        self.totalzhu -= taxGold
        player.goldC += self.totalzhu

        #更新base进程数据及税收
        player.set_gold(self.totalzhu)

        for pp in self.players.values():
            pp.set_gold(-pp.cost)

        KBEngine.globalData["Games"].addIncome(taxGold)

        self.sendAllClients(ACTION_ROOM_SETTLE,str(self.winCid))
        self.set_state(ROOM_STATE_FINISH)
        self.addTimerMgr(2,0,ACTION_ROOM_SETTLE)











