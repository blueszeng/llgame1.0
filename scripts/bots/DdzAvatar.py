import KBEngine
from KBEDebug import *
from Rules_DDZ import *
import random
import json

class DdzAvatar(KBEngine.Entity):

	def __init__(self):
		KBEngine.Entity.__init__(self)

		DEBUG_MSG("DdzAvatar __init__")

	def onEnterSpace(self):
		"""
		KBEngine method.
		这个entity进入了一个新的space
		"""
		DEBUG_MSG("%s::onEnterSpace: %i" % (self.__class__.__name__, self.id))

	def onLeaveSpace(self):
		"""
		KBEngine method.
		这个entity将要离开当前space
		"""
		DEBUG_MSG("%s::onLeaveSpace: %i" % (self.__class__.__name__, self.id))

	def onBecomePlayer(self):
		"""
		KBEngine method.
		当这个entity被引擎定义为角色时被调用
		"""
		DEBUG_MSG("%s::onBecomePlayer: %i" % (self.__class__.__name__, self.id))

	def onContinue(self):
		pass

	def onMessage(self,retcode,action,data):
		pass

	def onSay(self,str):
		pass

	def onEnterGame(self,gameID,result):
		self.base.reqEnterHall(1)
		DEBUG_MSG("%s::onEnterGame: %i" % (self.__class__.__name__, self.id))
		pass

	def onLeaveGame(self,gameID):
		pass

	def onEnterHall(self,hallID):
		self.base.reqEnterRoom()
		DEBUG_MSG("%s::onEnterHall: %i" % (self.__class__.__name__, self.id))
		pass

	def onLeaveHall(self,hallID):
		pass

	def onEnterRoom(self,data):
		pass

	def onHallsInfo(self,data):
		pass


class PlayerDdzAvatar(DdzAvatar):

	def __init__(self):

		DEBUG_MSG("PlayerDdzAvatar __init__")
		pass

	def onBecomePlayer(self):
		"""
		KBEngine method.当这个entity被引擎定义为角色时被调用
		"""
		DEBUG_MSG("%s::onBecomePlayer: %i" % (self.__class__.__name__, self.id))

		# 注意：由于PlayerAvatar是引擎底层强制由Avatar转换过来，__init__并不会再调用
		# 这里手动进行初始化一下
		self.__init__()

		# 引擎时间
		# KBEngine.callback(1, self.update)

	def onEnterSpace(self):
		"""
		KBEngine method.
		这个entity进入了一个新的space
		"""
		DEBUG_MSG("%s::onEnterSpace: %i" % (self.__class__.__name__, self.id))

	def onLeaveSpace(self):
		"""
		KBEngine method.
		这个entity将要离开当前space
		"""
		DEBUG_MSG("%s::onLeaveSpace: %i" % (self.__class__.__name__, self.id))

	def onContinue(self):
		pass

	def onMessage(self,retcode,action,data):
		if action == ACTION_ROOM_SETTLE :
			self.base.reqContinue()

	def onEnterGame(self,gameID,result):

		DEBUG_MSG("%s::onEnterGame: %i" % (self.__class__.__name__, self.id))

	def onLeaveGame(self,gameID):
		pass

	def onEnterHall(self,hallID):

		DEBUG_MSG("%s::onEnterHall: %i" % (self.__class__.__name__, self.id))
		pass

	def onLeaveHall(self,hallID):
		pass

	def onEnterRoom(self,data):
		pass

	def onSay(self,str):
		pass