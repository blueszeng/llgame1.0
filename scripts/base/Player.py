# -*- coding: utf-8 -*-
import KBEngine
from datetime import datetime,time
from d_game import *
from d_config import *
from interfaces.GameObject import *

class Player(KBEngine.Proxy,GameObject):
	"""
	玩家实体
	客户端登陆到服务端后，服务端将自动创建这个实体，通过这个实体与客户端进行交互
	"""
	def __init__(self):
		KBEngine.Proxy.__init__(self)
		GameObject.__init__(self)

	def onEntitiesEnabled(self):
		"""
		KBEngine method.
		该entity被正式激活为可使用， 此时entity已经建立了client对应实体， 可以在此创建它的
		cell部分。
		"""
		INFO_MSG("%r[%i]::onEntitiesEnabled(), accountName=%s" % (self.className, self.id, self.__ACCOUNT_NAME__))

		self.Games().reqEnter(self)

		#如果是机器人，则直接初始化属性
		if self.getClientType() == 6:
			self.name = "bots%r" % self.id
			self.gold = 1000.0
			self.sex  = 1
			self.head = 1

	def onLogOnAttempt(self, ip, port, password):
		"""
		KBEngine method.
		客户端登陆失败时会回调到这里
		"""
		return KBEngine.LOG_ON_ACCEPT

	def onClientDeath(self):
		"""
		KBEngine method.
		客户端对应实体已经销毁
		"""
		if self.activeProxy == None:
			self.destroy()

	def onDestroy(self):

		self.Games().reqLeave(self)

		if self.activeProxy:
			self.activeProxy.activeProxy = None
			self.activeProxy = None

		DEBUG_MSG("%r[%r]::onDestroy() " % (self.className, self.id))

	def reqReviseProperties(self,name,sex,head):
		"""
		Exposed
		设置玩家属性
		"""
		retcode = 0
		if self.name == "" or self.name is None:
			# 注册
			self.name = name
			self.sex  = sex
			self.head = head
			self.gold = 6.0
			self.writeToDB()

		elif name == "":
			#改名时值为""
			retcode = -1

		else:
			#修改属性成功
			self.name = name
			if sex > 0 and sex <= 2:
				self.sex = sex
			if head > 0:
				self.head = head

			self.writeToDB()

		self.client.onReviseProperties(retcode,self.name,self.sex,self.head)

	def reqAccessBank(self,access,offsetGold):
		"""
		Exposed
		银行存取
		access == 1 为存钱，== 2为取钱
		offsetGold 为金额
		"""
		retcode = -1
		if access == 1 and self.gold >= offsetGold:
			self.gold -= offsetGold
			self.bankGold += offsetGold
			retcode = 0
		elif access == 2 and self.bankGold>=offsetGold:
			self.gold += offsetGold
			self.bankGold -= offsetGold
			retcode = 0

		#retcode 0为存取成功，-1为存取失败，防止作弊
		self.client.onAccessBank(retcode,self.gold,self.bankGold)

	def reqGamesInfo(self):
		"""
		请求游戏类型，游戏信息，游戏在线人数
		"""
		self.streamFileToClient("data/d_config.xml","d_config")

		self.Games().reqGamesInfo(self)

	def reqRanksInfo(self):
		"""
		Exposed
		"""
		KBEngine.globalData["Ranks"].reqRanksInfo(self)

	def reqEnterGame(self, gameName):

		if self.activeProxy == None and gameName in d_games:

			className = d_games[gameName]['sign'] + "Avatar"

			avatar = KBEngine.createBaseLocally(className,{})
			if avatar:
				avatar.cellData["name"] = self.name
				avatar.cellData["gold"] = self.gold
				avatar.cellData["head"] = self.head
				avatar.cellData["addr"] = self.addr
				avatar.cellData["sex"] = self.sex

				self.activeProxy = avatar

				self.giveClientTo(avatar)

				avatar.reqEnterGame(gameName)
				avatar.activeProxy = self
		else:
			self.client.onEnterGame(1,self.activeProxy.game.className)

	def reqLeaveGame(self):

		if not self.client:
			self.destroy()
		else:
			self.activeProxy = None

	def reqCashInfo(self,amount):

		retcode = 0
		income  = 0

		if amount < 50:
			retcode = -2
		elif (self.gold - amount) >= d_users["base_money"]:
			if amount <= d_users["duixian_base"]:
				income = d_users["duixian_base_fee"]
			else:
				income += d_users["duixian_base_fee"]
				rate = (int)((amount - d_users["duixian_base"])/d_users["duixian_add"])
				remain = (int)((amount - d_users["duixian_base"]) % (int)(d_users["duixian_add"]))
				income += rate*d_users["duixian_add_fee"]
				if remain > 0 :
					income += d_users["duixian_add_fee"]
		else:
			retcode = -1
		INFO_MSG("amount:%r  income:%r" % (amount,income))

		self.client.onCashInfo(retcode,amount,int(income))

	def reqCash(self,amount,alipay):
		#请求兑现
		retcode = 0
		income  = 0
		if self.alipay != alipay:
			self.alipay = alipay

		#进行写入兑现数据表操作,并扣去玩家对应金额
		if(self.gold - amount) >= d_users["base_money"]:
			self.gold -= amount
			if amount <= d_users["duixian_base"]:
				income = d_users["duixian_base_fee"]
			else:
				income += d_users["duixian_base_fee"]
				rate = (int)((amount - d_users["duixian_base"]) / d_users["duixian_add"])
				remain = (int)((amount - d_users["duixian_base"]) % (int)(d_users["duixian_add"]))
				income += rate * d_users["duixian_add_fee"]
				if remain > 0:
					income += d_users["duixian_add_fee"]

			curAmount = amount - income
			KBEngine.globalData["Games"].addIncome(income)
			sql = "insert into TBL_WITHDDRAW(USER,ZHIFUBAO_NUMBER,ADDTIME,AMOUNT) values('%s','%s','%s','%s')" \
				  % (self.__ACCOUNT_NAME__,self.alipay,datetime.now(),str(curAmount))
			KBEngine.executeRawDatabaseCommand(sql, None)
		else:
			retcode = -1

		if self.client:
			self.client.onCash(retcode,self.gold,self.alipay)

	def reqRefresh(self):
		INFO_MSG(" Player::reqRefresh ")

		data = {}
		data["gold"] = self.gold
		json_string = json.dumps(data)

		if self.client:
			self.client.onRefresh(json_string)

	def reqRestoreGame(self):
		#请求恢复房间
		if self.client and self.activeProxy:
			self.client.onRestoreGame(self.activeProxy.game.className)
			self.giveClientTo(self.activeProxy)
		else:
			self.client.onRestoreGame("")

	def onStreamComplete(self,id,success):
		DEBUG_MSG("%r[%d]::onStreamComplete success = %r" % (self.className,id,success))

