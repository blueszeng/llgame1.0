# -*- coding: utf-8 -*-
import KBEngine
from KBEDebug import *
from d_config import *
from interfaces.BaseObject import *

class ZjhHall(KBEngine.Entity,BaseObject):
	"""
	大厅实体
	"""
	def __init__(self):
		KBEngine.Entity.__init__(self)
		BaseObject.__init__(self)

		self.lastNewRoomKey = 0

		#未满人房间
		self.notFullRooms = []

	def reqEnter(self,player):

		if player.cellData['gold'] < d_ZJH[self.cid]["limit"]:
			if player.client:
				player.client.onEnterHall("")
			WARNING_MSG("%r::reqEnter() Entity[%r] Gold < Limit" % (self.className, player.id))
			return

		super().reqEnter(player)
		if player.client:
			player.client.onEnterHall(self.className)

	def reqLeave(self,player):
		super().reqLeave(player)

		if player.client:
			player.client.onLeaveHall()

	def onRoomGetCell(self, roomMailbox, roomKey):
		"""
        Room的cell创建好了
        """
		#todo 未添加到def
		self.childs[roomKey]["roomMailbox"] = roomMailbox

		# space已经创建好了， 现在可以将之前请求进入的玩家全部丢到cell地图中
		for player in self.childs[roomKey]["players"]:

			if player.client:
				roomMailbox.reqEnter(player)
			else:
				del self.childs[roomKey]["players"][player]

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

		if roomKey in self.notFullRooms:
			del self.notFullRooms[self.notFullRooms.index(roomKey)]

	def reqEnterRoom(self, player):
		"""
		先查找空房间，如果没空房，则将玩家排队，再创建新房间
		"""
		roomKey = self.findNotFullRooms()

		if roomKey:
			room = self.childs[roomKey]["roomMailbox"]

			self.childs[roomKey]["players"].append(player)
			self.sortNotFullRooms(roomKey,self.childs[roomKey]["players"])

			room.reqEnter(player)
		else:
			self.lastNewRoomKey = self.lastNewRoomKey + 1
			params = {'parent': self,
					  'cid': self.lastNewRoomKey,
					  'state': 0,
					  'dizhu': d_ZJH[self.cid]['base'],
					  'jzList': json.dumps(d_ZJH[self.cid]['jzList']),
					  'taxRate': d_ZJH['taxRate']
					  }

			KBEngine.createEntityAnywhere("ZjhRoom", params, None)

			roomDatas = {"roomMailbox": None,
						 "players": [player]}

			self.childs[self.lastNewRoomKey] = roomDatas

			self.sortNotFullRooms(self.lastNewRoomKey,roomDatas["players"])

	def onRoomLosePlayer(self,roomkey,player):
		"""
		玩家丢失
		"""
		if roomkey in self.childs and player in self.childs[roomkey]['players']:
			index = self.childs[roomkey]['players'].index(player)
			del self.childs[roomkey]['players'][index]
			self.sortNotFullRooms(roomkey,self.childs[roomkey]['players'])

	def findNotFullRooms(self):
		"""
		查找人数最多的空房
		"""
		if len(self.notFullRooms) <= 0:
			return None
		else:
			return self.notFullRooms[0]

	def sortNotFullRooms(self,roomKey,players):
		"""
		优先把人数最多的房间置顶
		如果房间满人或者没人，则从队列中清理掉
		"""
		playersCount = len(players)

		if (playersCount == 0 or playersCount == 5) and roomKey in self.notFullRooms:
			del self.notFullRooms[self.notFullRooms.index(roomKey)]
			return

		if roomKey not in self.notFullRooms:
			self.notFullRooms.append(roomKey)

		self.notFullRooms.sort(key = lambda x:(-x))



