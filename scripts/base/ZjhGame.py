from d_config import  *
from d_game import *
from Functor import *
from interfaces.BaseObject import *

class ZjhGame(KBEngine.Entity,BaseObject):

    def __init__(self):
        KBEngine.Entity.__init__(self)
        BaseObject.__init__(self)

        # 通过添加一个定时器延时执行游戏大厅的创建，确保一些状态在此期间能够初始化完毕
        self.addTimer(1, 0, 1)

    def onTimer(self, id, userArg):
        """
        KBEngine method.
        使用addTimer后， 当时间到达则该接口被调用
        @param id		: addTimer 的返回值ID
        @param userArg	: addTimer 最后一个参数所给入的数据
        """
        for i in range(d_games[self.className]["hallCount"]):
            cid = i + 1
            KBEngine.createEntityAnywhere(d_games[self.className]['sign'] + "Hall", {'parent': self, "cid": cid},
                                        Functor(self.onCreateBaseCallback, cid))

    def onCreateBaseCallback(self, id, mailbox):

        self.childs[id] = mailbox

    def reqEnter(self,player):
        super().reqEnter(player)

        if player.client:
            player.client.onEnterGame(0,self.className)

    def reqLeave(self,player):
        super().reqLeave(player)

        if player.client:
            player.client.onLeaveGame()

    def reqHallsInfo(self, player):
        """下发大厅信息"""
        results = []
        for hall in self.childs.values():
            result = {}
            result["id"] = hall.cid
            result["players_count"] = hall.reqPlayerCount()
            result["limit"] = d_ZJH[hall.cid]["limit"]
            result["base"] = d_ZJH[hall.cid]["base"]
            results.append(result)

        if player.client:
            player.client.onHallsInfo(json.dumps(results))

