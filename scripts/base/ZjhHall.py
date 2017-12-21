# -*- coding: utf-8 -*-
import KBEngine
from KBEDebug import *
from d_config import *
from interfaces.BaseObject import *

class ZjhHall(KBEngine.Base,BaseObject):
	"""
	大厅实体
	"""
	def __init__(self):
		KBEngine.Base.__init__(self)
		BaseObject.__init__(self)

		self.lastNewRoomKey = 0

		#未满人房间
		self.notFullRooms = []

	def reqEnter(self,player):

		if player.gold < d_ZJH[self.cid]["limit"]:

			if player.client:
				player.client.onEnterHall(-1)

			WARNING_MSG("%r::reqEnter() Entity[%r] Gold < Limit" % (self.className, player.id))
			return

		super().reqEnter(player)
		if player.client:
			player.client.onEnterHall(0)

	def reqLeave(self,player):
		super().reqLeave(player)

		if player.client:
			player.client.onLeaveHall(0)

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
			self.sortNotFullRooms(roomKey,self.childs[roomKey]['players'])
			del self.childs[roomKey]

	def reqEnterRoom(self, player):
		"""
		先查找空房间，如果没空房，则将玩家排队，再创建新房间
		"""

		sortData = self.findNotFullRooms()

		if sortData:
			roomKey = sortData["roomKey"]
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

			KBEngine.createBaseAnywhere("ZjhRoom", params, None)

			roomDatas = {"roomMailbox": None,
						 "players": [player]}

			self.childs[self.lastNewRoomKey] = roomDatas

			self.sortNotFullRooms(self.lastNewRoomKey,roomDatas["players"])

	def onRoomLosePlayer(self,roomkey,player):
		"""玩家丢失"""

		if roomkey in self.childs and player in self.childs[roomkey]['players']:
			del self.childs[roomkey]['players'][player]
			self.sortNotFullRooms(roomkey,self.childs[roomkey]['players'])

	def findNotFullRooms(self):
		"""
		查找人数最多的有位置房间
		"""
		if len(self.notFullRooms) <= 0:
			return None

		else:
			return self.notFullRooms[0]

	def sortNotFullRooms(self,roomKey,players):
		"""
		重新排列房间顺序，优先把人数最多的房间置顶
		"""
		playersCount = len(players)
		sortData = {"roomKey":roomKey,"playersCount":playersCount}

		#如果房间满人或者没人，则从队列中清理掉
		if (playersCount == 0 or playersCount == 5) and sortData in self.notFullRooms:
			del self.notFullRooms[self.notFullRooms.index(sortData)]
			return

		if len(self.notFullRooms) <= 0:
			self.notFullRooms.append(sortData)
			return

		#如果房间还有空位，则排队
		for notRoom in self.notFullRooms:

			if notRoom == sortData:
				break

			index = self.notFullRooms.index(notRoom)

			if playersCount > notRoom['playersCount']:
				self.notFullRooms.insert(index,sortData)
				break
			elif len(self.notFullRooms) == (index+1):
				self.notFullRooms.append(sortData)



