import KBEngine
import json
from interfaces.EntityCommon import *
import Rules_ZJH

class ZjhAvatar(KBEngine.Entity,EntityCommon):

    def __init__(self):

        KBEngine.Entity.__init__(self)
        EntityCommon.__init__(self)

        self.position = (self.cid, 0.0, 0.0)

        self.getCurrRoom().onEnter(self)

    def onDestroy(self):
        """
        KBEngine method
        """
        self.getCurrRoom().onLeave(self)

    def setGold(self,gold):

        self.base.setGold(gold)

    def setStatus(self, status):

        self.cellStatus = status
        self.base.setStatus(status)

    def reqMessageC(self,exposed,action,buf):
        if exposed != self.id:
            return

        if action == Rules_ZJH.ACTION_ROOM_KANPAI:
            self.lookcard = 2
        else:
            self.getCurrRoom().reqMessage(self, action, buf)
