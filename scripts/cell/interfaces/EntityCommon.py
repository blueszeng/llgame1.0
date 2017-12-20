# -*- coding: utf-8 -*-
import KBEngine
from KBEDebug import * 

class EntityCommon:
	"""
	服务端Cell实体的基础接口类
	"""
	def __init__(self):
		#定时器管理器
		self.timerMgr = {}
		self.callbackFunc = None

	def getCurrRoomBase(self):
		"""
		获得当前space的entity baseMailbox
		"""
		return KBEngine.globalData["Room_%i" % self.spaceID]

	def getCurrRoom(self):
		"""
		获得当前space的entity
		"""
		roomBase = self.getCurrRoomBase()
		if roomBase is None:
			return roomBase

		return KBEngine.entities.get(roomBase.id, None)

	def addTimerMgr(self, initialOffset, repeatOffset, userArg):

		tid = self.addTimer(initialOffset, repeatOffset, userArg)

		#先清理可能重复的定时器
		self.delTimerMgr(userArg)

		if repeatOffset > 0:
			self.timerMgr[userArg] = tid

	def delTimerMgr(self, userArg):

		if userArg == 0:
			DEBUG_MSG("%r clean all timers" % (self.className))

			for tt in self.timerMgr.values():
				self.delTimer(tt)

			self.timerMgr.clear()

		elif userArg in self.timerMgr:

			tid = self.timerMgr.pop(userArg)

			self.delTimer(tid)

	def invoke(self,callbackFunc,initialOffset):
		"""
		回调方法
		"""
		self.callbackFunc = callbackFunc
		self.addTimerMgr(initialOffset,0,0)

	def onTimer(self, id, userArg):
		"""
        KBEngine method.
        使用addTimer后， 当时间到达则该接口被调用
        @param id		: addTimer 的返回值ID
        @param userArg	: addTimer 最后一个参数所给入的数据
        """
		if userArg == 0 and self.callbackFunc is not None:
			self.callbackFunc
			self.callbackFunc = None
