import KBEngine
import Rules_DDZ
from KBEDebug import *
from interfaces.EntityCommon import EntityCommon

class DdzAvatar(KBEngine.Entity,EntityCommon):

    def __init__(self):

        KBEngine.Entity.__init__(self)
        EntityCommon.__init__(self)

        self.position = (self.cid, 0.0, 0.0)

        self.getCurrRoom().onEnter(self)

    def onDestroy(self):
        """
        KBEngine method
        """
        DEBUG_MSG("%r[%r].Cell::onDestroy()" % (self.className,self.id))

        room = self.getCurrRoom()
        if room:
            room.onLeave(self)

    def reqLeave(self):

        if self.cellStatus == Rules_DDZ.ROOM_STATE_INGAME:
            self.base.changeClient()
        else:
            self.getCurrRoom().onLeave(self)

    def set_gold(self,gold):

        self.base.set_gold(gold)

    def reqMessage(self,exposed,action,buf):

        if exposed != self.id:
            return

        DEBUG_MSG("%r[%r].Cell::reqMessageC() buf = %r" % (self.className, self.id,buf))

        if action == Rules_DDZ.ACTION_ROOM_TUOGUAN:
            self.tuoguan = int(buf)
        else:
            self.getCurrRoom().reqMessage(self,action,buf)