# -*- coding: utf-8 -*-
import KBEngine
from KBEDebug import *
from interfaces.BaseObject import *
import Rules_ZJH

class ZjhRoom(KBEngine.Base,BaseObject):
    """
	这是一个游戏房间
	该房间中记录了房间里所有玩家的mailbox，通过mailbox我们可以将信息推送到他们的客户端。
	"""
    def __init__(self):
        KBEngine.Base.__init__(self)
        BaseObject.__init__(self)

        self.players = {}

        self.status = Rules_ZJH.ROOM_STATE_READY
        self.cellData["dizhuC"]         = self.dizhu
        self.cellData["taxRateC"]       = self.taxRate
        self.cellData["jzListC"]        = self.jzList
        self.cellData["statusC"]        = self.status

        self.createInNewSpace(None)

    def setStatus(self, status):
        # 游戏结束，因为只能在base进程中检测client状态
        # 所以需要把游戏状态发回base进程
        self.status = status

        if status == Rules_ZJH.ROOM_STATE_FINISH:
            for pp in self.players.values():
                if not pp.client and pp.cell:
                    pp.destroyCellEntity()

    def onGetCell(self):
        """
        KBEngine method.
        entity的cell部分实体被创建成功
        """
        DEBUG_MSG("%r[%r]::onGetCell()" % (self.className, self.id))

        self.parent.onRoomGetCell(self, self.cid)

    def onLoseCell(self):
        """
        KBEngine method.
        entity的cell部分实体丢失
        """
        DEBUG_MSG("%r[%r]::onLoseCell()" % (self.className, self.id))

        self.parent.onRoomLoseCell(self, self.cid)

        self.destroy()

    def reqEnter(self, player):

        super().reqEnter(player)

        if not player.cell:
            player.createCell(self.cell)

    def reqLeave(self, player):
        super().reqLeave(player)

        self.parent.onRoomLosePlayer(self.cid,player)

