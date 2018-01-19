# -*- coding: utf-8 -*-
import KBEngine
import random
import time
import json
import Functor
from KBEDebug import *

class Ranks(KBEngine.Base):
	"""
	排行榜管理器实体
	该实体管理该服务组上所有的游戏类型
	"""
	def __init__(self):
		KBEngine.Base.__init__(self)

		KBEngine.globalData["Ranks"] = self

		self.ranks = {}

	def reqRanksInfo(self,player):
		"""
		获取排行榜信息
		"""
		self.ranks = {}

		sql = "SELECT CASE WHEN @rowtotal = sm_gold+sm_bankGold THEN @rownum " \
			  "WHEN @rowtotal := sm_gold+sm_bankGold THEN @rownum :=@rownum + 1 " \
			  "WHEN @rowtotal = 0 THEN @rownum :=@rownum + 1 END AS rank," \
			  "sm_name,sm_gold+sm_bankGold AS totalGold FROM tbl_Player," \
			  "(SELECT @rownum :=0,@rowtotal := NULL) b ORDER BY totalGold DESC LIMIT 10"

		KBEngine.executeRawDatabaseCommand(sql, Functor.Functor(self.onRanksInfo, player))

		sql = "SELECT (SELECT count(1)+1 as rank  from tbl_Player WHERE " \
			  "(sm_gold+sm_bankGold) > (SELECT sm_gold+sm_bankGold FROM" \
			  " tbl_Player WHERE id = %i))AS rank ,sm_name,(sm_gold+sm_bankGold) " \
			  "AS totalGold FROM tbl_Player WHERE id=%i " % (player.databaseID, player.databaseID)

		KBEngine.executeRawDatabaseCommand(sql, Functor.Functor(self.onMyRankInfo, player))

	def onRanksInfo(self, player, result, rows, insertid, error):

		str_result = []
		for i in result:
			str_i = []
			for j in i:
				str_j = j.decode()
				str_i.append(str_j)
			str_result.append(str_i)

		self.ranks["ranks"] = str_result

		if "myRank" in self.ranks and player.client:
			player.client.onRanksInfo(json.dumps(self.ranks))

	def onMyRankInfo(self, player, result, rows, insertid, error):
		"""
        返回的数据库回掉
        """
		str_result = []
		for i in result:
			for j in i:
				str_j = j.decode()
				str_result.append(str_j)
		self.ranks["myRank"] = str_result

		if "ranks" in self.ranks and player.client:
			player.client.onRanksInfo(json.dumps(self.ranks))



