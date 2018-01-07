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
        INFO_MSG("%r[%i]::onEntitiesEnabled()" % (self.className,self.id))

    def createCell(self, space):
        """
        export method.
        """
        if not self.cell:

            self.cellData["cid"] = 0
            self.cellData["cards"] = []
            self.cellData["cardCount"] = 0
            self.cellData["showCards"] = []

            self.cellData["cost"] = 0.0
            self.cellData["chip"] = 0.0
            self.cellData["lookcard"] = 1
            self.cellData["stateC"] = Rules_ZJH.PLAYER_STATE_GARK
            self.cellData["first"] = 0

            self.createCellEntity(space)

    def onLoseCell(self):
        """
        KBEngine method.
        """
        DEBUG_MSG("%r[%r]::onLoseCell()" % (self.className, self.id))

        if not self.client:
            self.ExitGame()
        else:
            self.reqLeaveRoom()

    def onClientDeath(self):

        if self.state != Rules_ZJH.PLAYER_STATE_INGAME:
            if self.cell:
                self.destroyCellEntity()
            else:
                self.ExitGame()

    def onDestroy(self):

        DEBUG_MSG("%r[%r]::onDestroy() " %(self.className,self.id))

    def reqLeaveGame(self):
        super().reqLeaveGame()

        if self.client:
            self.giveClientTo(self.activeProxy)

        self.activeProxy.reqLeaveGame()
        self.destroy()

    def set_gold(self, settleGold):

        gold = Helper.Round(settleGold)
        self.activeProxy.gold += gold
        self.gold = self.activeProxy.gold

        DEBUG_MSG("%r[%r]::set_gold() gold[%r] settleGold[%r]" %(self.className,self.id,self.gold,settleGold))

    def set_state(self,state):

        self.state = state

