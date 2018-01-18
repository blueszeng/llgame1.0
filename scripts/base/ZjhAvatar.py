# -*- coding: utf-8 -*-

from interfaces.GameObject import *
from KBEDebug import *
import Helper
import Rules_ZJH

class ZjhAvatar(KBEngine.Proxy,GameObject):

    def __init__(self):
        KBEngine.Proxy.__init__(self)
        GameObject.__init__(self)

    def onEntitiesEnabled(self):
        """
        KBEngine method.
        该entity被正式激活为可使用， 此时entity已经建立了client对应实体， 可以在此创建它的
        cell部分。
        """
        DEBUG_MSG("%r[%i]::onEntitiesEnabled()" % (self.className,self.id))

    def createCell(self, space):
        """
        define method.
        """
        if not self.cell:
            self.createCellEntity(space)

    def onLoseCell(self):
        """
        KBEngine method.
        """
        # DEBUG_MSG("%r[%r]::onLoseCell()" % (self.className, self.id))

        if not self.client:
            self.exitGame()
        else:
            self.reqLeaveRoom()

    def onClientDeath(self):

        if self.status != Rules_ZJH.PLAYER_STATE_INGAME:
            if self.cell:
                self.destroyCellEntity()
            else:
                self.exitGame()

    def onDestroy(self):

        DEBUG_MSG("%r(%r)::onDestroy " % (self.className, self.id))

    def reqLeaveGame(self):
        super().reqLeaveGame()

        if self.client:
            self.giveClientTo(self.activeProxy)

        self.activeProxy.reqLeaveGame()
        self.destroy()

    def setGold(self, settleGold):

        self.activeProxy.gold += Helper.Round(settleGold)

        DEBUG_MSG("%r[%r]::setGold() gold[%r] settleGold[%r]" %(self.className,self.id,self.activeProxy.gold,settleGold))

    def setStatus(self, status):

        self.status = status

