
from interfaces.RoomEntity import *
import Rules_ZJH

class LogicZjh(RoomEntity):
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