# -*- coding: utf-8 -*-

import KBEngine
from interfaces.GameObject import *
from KBEDebug import *
import Helper

class DdzAvatar(KBEngine.Proxy,GameObject):
    """
    斗地主游戏实体
    """
    def __init__(self):
        KBEngine.Proxy.__init__(self)
        GameObject.__init__(self)

        self.bContinue = False

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

            self.cellData["cards"] = []
            self.cellData["cardCount"] = 0
            self.cellData["curScore"]  = -1
            self.cellData["showCards"] = []
            self.cellData["multiple"] = 1
            self.cellData["type"] = 0       # 0无身份 1地主 2农民
            self.cellData["tuoguan"] = 0    # 0正常 1托管
            self.cellData["cid"] = 0

            self.createCellEntity(space)

            self.bContinue = False

    def onLoseCell(self):
        """
        KBEngine method.
        """
        DEBUG_MSG("%r[%r]::onLoseCell()" % (self.className, self.id))

        if self.bContinue:
            self.reqEnterRoom()

        elif not self.client:
            self.exitGame()

        else:
            self.reqLeaveRoom()

    def onClientDeath(self):

        if self.state == 0:
            if self.cell:
                self.destroyCellEntity()
            else:
                self.exitGame()

    def onDestroy(self):

        DEBUG_MSG("%r[%r]::onDestroy() " %(self.className,self.id))


    def reqLeaveGame(self):

        super().reqLeaveGame()

        if self.client:
            self.giveClientTo(self.activeProxy)

        self.activeProxy.reqLeaveGame()
        self.destroy()

    def reqContinue(self):
        """
        继续游戏
        """
        INFO_MSG("%r[%r]::reqContinue()" % (self.className,self.id))

        if self.hall:
            self.hall.reqContinue(self)

    def set_gold(self, settleGold):

        self.activeProxy.gold += Helper.Round(settleGold)
        DEBUG_MSG("%r[%r]::set_gold() gold[%r] settleGold[%r]" %(self.className,self.id,self.activeProxy.gold,settleGold))
