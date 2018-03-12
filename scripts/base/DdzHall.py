
# -*- coding: utf-8 -*-
import KBEngine
from d_config import *
from GlobalConst import *
from interfaces.BaseObject import *

class DdzHall(KBEngine.Entity,BaseObject):
	"""
	大厅实体
	"""
	def __init__(self):
		KBEngine.Entity.__init__(self)
		BaseObject.__init__(self)

		self.lastNewRoomKey = 0

	def reqEnter(self,player):

		if player.cellData['gold'] < d_DDZ[self.cid]["limit"]:
			DEBUG_MSG("%r::reqEnter() Entity[%r] Gold < Limit" % (self.className, player.id))
			if player.client:
				player.client.onEnterHall("")
			return

		super().reqEnter(player)
		if player.client:
			player.client.onEnterHall(self.className)

	def reqLeave(self,player):
		super().reqLeave(player)

		if player.client:
			player.client.onLeaveHall()

	def onRoomGetCell(self, roomMailbox, lastNewRoomKey):
		"""
        Room的cell创建好了
        """
		#todo 未添加到def
		self.childs[lastNewRoomKey]["roomMailbox"] = roomMailbox

		# space已经创建好了， 现在可以将之前请求进入的玩家全部丢到cell地图中
		for player in self.childs[lastNewRoomKey]["players"]:
			if player.client:
				roomMailbox.reqEnter(player)
			else:
				del self.childs[lastNewRoomKey]["players"][player]

				#如果player已丢失client，则需要销毁该引用
				if player:
					player.destroy()

	def onRoomLoseCell(self,roomMailbox,roomKey):
		"""
		Room 销毁时，回调
		"""
		# todo 未添加到def
		if roomKey in self.childs:
			del self.childs[roomKey]

	def reqEnterRoom(self, player):
		"""
		先查找空房间，如果没空房，则将玩家排队，然后创建新房间
		"""
		for roomData in self.childs.values():

			if len(roomData['players']) < 3:
				roomData['players'].append(player)

				if roomData['roomMailbox']:
					roomData['roomMailbox'].reqEnter(player)

				return

		self.lastNewRoomKey = self.lastNewRoomKey + 1

		params = {'parent':self,
				  'cid': self.lastNewRoomKey,
				  'state': 0,
				  'difen': d_DDZ[self.cid]['base'],
				  'taxRate': d_DDZ['taxRate']}

		KBEngine.createEntityAnywhere("DdzRoom", params, None)

		roomDatas = {"roomMailbox": None,
					 "players": [player]}

		self.childs[self.lastNewRoomKey] = roomDatas

	def reqContinue(self,player):

		if not player.room:
			return

		if player.cellData['gold'] < d_DDZ[self.cid]["limit"]:

			DEBUG_MSG("%r[%r]::reqContinue() Entity[%d].gold < limit" % (self.className,self.id,player.id))
			player.room.reqLeave(player)

		else:
			player.room.reqContinue(player)




