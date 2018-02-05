# -*- coding: utf-8 -*-
import KBEngine
import Helper
import json
from Functor import *
from d_game import *
from interfaces.BaseObject import *

class Games(KBEngine.Entity,BaseObject):
	"""
	游戏管理器实体
	该实体管理该服务组上所有的游戏类型
	"""
	def __init__(self):
		KBEngine.Entity.__init__(self)
		BaseObject.__init__(self)
		KBEngine.globalData["Games"] = self

		# 订单管理
		self.orders = {}

		# 通过添加一个定时器延时执行创建，确保一些状态在此期间能够初始化完毕
		self.addTimer(1,0,1)

	def onTimer(self, id, userArg):
		"""
		KBEngine method.
		使用addTimer后， 当时间到达则该接口被调用
		@param id		: addTimer 的返回值ID
		@param userArg	: addTimer 最后一个参数所给入的数据
		"""

		for key,value in d_games.items():
			params = {'parent':self,'cid': key,'open': value["open"]}
			KBEngine.createEntityAnywhere(value['sign']+"Game",params,Functor(self.onCreateBaseCallback,key))

	def onCreateBaseCallback(self,id,game):
		self.childs[id] = game

	def reqEnter(self,player):
		super().reqEnter(player)

		delList = []
		for name in self.orders.keys():
			if player.__ACCOUNT_NAME__ == name:

				player.gold += self.orders[name]
				delList.append(name)

				DEBUG_MSG("player[%r] online and charge money[%r] success" % (name,self.orders[name]))

		for name in delList:
			del self.orders[name]

	def reqGamesInfo(self,player):
		"""请求游戏信息"""
		results = []
		for game in self.childs.values():
			result = {}
			result["id"] = game.cid
			result["name"] = game.className
			result["players_count"] = game.reqPlayerCount()
			result["open"] = game.open
			results.append(result)

		if player.client:
			player.client.onGamesInfo(json.dumps(results))

	def reqChargeToPlayer(self,accountName,amount):
		"""请求充值"""
		chargeStatus = False
		for player in self.players.values():
			if(player.__ACCOUNT_NAME__ == accountName):
				player.gold += amount

				chargeStatus = True
				player.reqRefresh()
				break

		if not chargeStatus:
			INFO_MSG("charge account[%r] not online. but order is saved" % (accountName))
			self.orders[accountName] = amount
		else:
			INFO_MSG("charge account[%r] for amount[%r] is success" % (accountName,amount))

	def addIncome(self,add):
		"""收益统计"""
		income = Helper.Round(add)

		self.income += income

		self.writeToDB()
		INFO_MSG("Games::addIncome income[%r] add[%r]" % (self.income,income))



