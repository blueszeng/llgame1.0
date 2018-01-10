
from interfaces.RoomEntity import *
import Rules_ZJH
import json

class ZjhLogic(RoomEntity):
    """炸金花玩法逻辑"""

    def __init__(self):
        RoomEntity.__init__(self)


    def getNextCid(self,curCid):
        """
        获取下一个正在游戏中玩家的Cid
        """
        for i in range(0, 5):
            nCid = (curCid + i) % 5 + 1
            if nCid in self.players:
                if self.players[nCid].stateC == Rules_ZJH.PLAYER_STATE_INGAME:
                    break
        return nCid

    def compareCards(self, player, tPlayer, auto):
        """比牌"""
        bResult = Rules_ZJH.CompareCards(player.cards,tPlayer.cards)

        data = {}
        data["playerCid"] = player.cid
        data["targetCid"] = tPlayer.cid
        data["result"] = bResult
        data["auto"] = auto

        KBEngine.setSpaceData(self.spaceID, "compareResult", json.dumps(data))
        self.invoke4(3, self.onLastCompareCards, player, tPlayer, auto, bResult)

    def onLastCompareCards(self, player, target, auto,result):
        """比牌之后"""
        DEBUG_MSG("%r::onLastCompareCards()" % (self.className))

        if result:
            target.set_state(Rules_ZJH.PLAYER_STATE_GARK)
        else:
            player.set_state(Rules_ZJH.PLAYER_STATE_GARK)

        if self.onCheckResult():
            self.onSettle()

        elif auto and result:
            #如果是系统自动比牌，并且玩家赢了，则继续执行自动比牌
            self.addTimerMgr(1, 0, Rules_ZJH.ACTION_ROOM_AUTOBIPAI)
        else:
            self.onNextPlayer()