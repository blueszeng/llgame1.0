from d_config import  *
from d_game import *
from Functor import *
from interfaces.BaseObject import *

class ZjhGame(KBEngine.Base,BaseObject):

    def __init__(self):
        KBEngine.Base.__init__(self)
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
        for i in range(d_games[self.cid]["hallCount"]):
            cid = i + 1
            KBEngine.createBaseAnywhere(d_games[self.cid]['sign'] + "Hall", {'parent': self, "cid": cid},
                                        Functor(self.onCreateBaseCallback, cid))

    def onCreateBaseCallback(self, id, mailbox):

        self.childs[id] = mailbox

    def reqEnter(self,player):
        super().reqEnter(player)

        #下发大厅信息
        results = []
        for hall in self.childs.values():

            result = {}
            result["id"] = hall.cid
            result["players_count"] = hall.reqPlayerCount()
            result["limit"] = d_ZJH[hall.cid]["limit"]
            result["base"] = d_ZJH[hall.cid]["base"]

            results.append(result)

        json_results = json.dumps(results)

        if player.client:
            player.client.onEnterGame(self.cid, json_results)

    def reqLeave(self,player):
        super().reqLeave(player)

        if player.client:
            player.client.onLeaveGame(0)

