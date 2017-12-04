import KBEngine
from KBEDebug import *
from Rules_DDZ import *
import random
import json

class Player(KBEngine.Entity):

	def __init__(self):
		KBEngine.Entity.__init__(self)

		self.base.reqEnterGame(1)

	def onGameInfo(self,data):
		pass
	def onGamesConfig(self,data):
		pass
	def onCash(self,retcode,alipay,phone):
		pass
	def onCharge(self, gold, amount):
		pass
	def onRefresh(self,data):
		pass
	def onCashInfo(self, retcode, glod, amount):
		pass
	def onStartGame(self):
		pass
	def onEnterGame(self,gameID,result):
		pass
	def onLeaveGame(self,gameID):
		pass
	def onEnterHall(self,hallID):
		pass
	def onLeaveHall(self,hallID):
		pass
	def onEnterRoom(self,data):
		pass
	def onLeaveRoom(self,retcode,chairID):
		pass
	def onContinue(self):
		pass
	def onRoomState(self,data):
		pass
	def onMessage(self,retcode,action,data):
		pass
	def onRegisterProperties(self,retcode):
		pass
	def onAccessBank(self,retcode,access,offsetGold):
		pass
	def onReviseProperties(self,retcode,name,sex,head):
		pass
	def onRanksInfo(self,data):
		pass
	def onMyRankInfo(self,data):
		pass
	def onNoticeInfos(self,data):
		pass
	def onSay(self,str):
		pass
	def onUpdateHalls(self,data):
		pass

