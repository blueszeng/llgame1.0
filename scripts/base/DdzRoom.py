# -*- coding: utf-8 -*-
import KBEngine
from KBEDebug import *
from Rules_DDZ import *
from interfaces.BaseObject import *

class DdzRoom(KBEngine.Base,BaseObject):
    """
	这是一个游戏房间
	该房间中记录了房间里所有玩家的mailbox，通过mailbox我们可以将信息推送到他们的客户端。
	"""
    def __init__(self):
        KBEngine.Base.__init__(self)
        BaseObject.__init__(self)

        self.cellData["difenC"]         = self.difen
        self.cellData["taxRateC"]       = self.taxRate
        self.cellData["statusC"]         = self.status

        self.createInNewSpace(None)

    def set_state(self, status):

        self.status = status

        for pp in self.players.values():
            #游戏结束，因为只能在base进程中检测client状态
            #所以需要把游戏状态发回base进程
            if self.status == ROOM_STATE_FINISH :

                pp.state = ROOM_STATE_READY

                if not pp.client and pp.cell:
                    pp.destroyCellEntity()
            else:
                pp.state = status

    def onGetCell(self):
        """
        KBEngine method.
        entity的cell部分实体被创建成功
        """
        DEBUG_MSG("%r[%r]::onGetCell()" % (self.className,self.id))

        self.parent.onRoomGetCell(self,self.cid)

    def onLoseCell(self):
        """
        KBEngine method.
        entity的cell部分实体丢失
        """
        DEBUG_MSG("%r[%r]::onLoseCell()" % (self.className, self.cid))

        self.parent.onRoomLoseCell(self, self.cid)

        self.destroy()

    def reqEnter(self, player):

        if player.id in self.players:
            return

        super().reqEnter(player)

        if self.status == ROOM_STATE_READY:
            player.createCell(self.cell)

    def reqLeave(self,player):

        #如果房间正在游戏中，不予处理
        if self.status == ROOM_STATE_INGAME:
            return

        super().reqLeave(player)

        if player.cell:
            player.destroyCellEntity()

    def reqContinue(self, player):

        DEBUG_MSG("%r[%r]::reqContinue() Entity[%r] EntityCount[%r]" % (self.className,self.id,player.id, len(self.players)))

        # 如果房间正在游戏中，不予处理
        if self.status == ROOM_STATE_INGAME:
            return

        if player.cell:

            if player.client:
                player.bContinue = True
                player.client.onContinue()

            super().reqLeave(player)
            if player.cell:
                player.destroyCellEntity()

