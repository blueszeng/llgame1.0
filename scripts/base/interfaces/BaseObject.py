import KBEngine
from KBEDebug import *

class BaseObject():
    """
    Base实体基类 匹配机制下如 游戏大厅，游戏房间
    """

    def __init__(self):

        # 子空间管理，如一个游戏Game的子空间为游戏大厅Hall，游戏大厅Hall的子空间为房间Room
        self.childs = {}

        # 玩家管理
        self.players = {}

    def reqEnter(self,player):
        """
        进入对应的空间，需要实体添加对该空间的引用
        """

        self.players[player.id] = player
        DEBUG_MSG("%s[%d]::reqEnter() entity[%d]" % (self.className, self.id, player.id))

        for prop in player.propertys:
            if self.className.find(prop) != -1 and self.className != "Games":
                setattr(player,prop.lower(),self)

    def reqLeave(self,player):
        """
        离开对应的空间，需要确保清空实体对该空间的引用
        """

        if player.id in self.players:
            del self.players[player.id]
            DEBUG_MSG("%s[%d]::reqLeave() entity[%d]" % (self.className, self.id, player.id))

        for prop in player.propertys:
            if self.className.find(prop) != -1 and self.className != "Games":
                setattr(player, prop.lower(), None)

    def reqEnterChild(self,player,cid):
        """
        请求进入子空间
        """
        if cid in self.childs:
            self.childs[cid].reqEnter(player)

    def reqPlayerCount(self):
        """
        获取空间内玩家数量
        """
        return len(self.players)
