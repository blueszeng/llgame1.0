# -*- coding: utf-8 -*-
from interfaces.EntityCommon import *

class RoomEntity(EntityCommon):
    #Room cell 实体 基类

    def __init__(self):
        EntityCommon.__init__(self)

        KBEngine.globalData["Room_%i" % self.spaceID] = self.base

        self.players = {}

    def sendAllClients(self,action,json):
        """
        class method
        """
        for pp in self.players.values():
            if pp.client:
                pp.client.onMessage(0,action,json)

    def onDestroy(self):
        """
        KBEngine method
        """
        del KBEngine.globalData["Room_%i" % self.spaceID]