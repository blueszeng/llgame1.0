# -*- coding: utf-8 -*-
import KBEngine
import socket
import json
from datetime import datetime,time
from KBEDebug import *
import Helper

class JbPoller:
	"""
	演示：
	可以向kbengine注册一个socket，由引擎层的网络模块处理异步通知收发。
	用法: 
	from Poller import Poller
	poller = Poller()
	
	开启(可在onBaseappReady执行)
	poller.start("localhost", 12345)
	
	停止
	poller.stop()
	"""
	def __init__(self):
		self._socket = None
		self._clients = {}
		self._orders = {}
		self.isAddOrder = True
		self.payid = ""

	def start(self, addr, port):
		"""
		virtual method.
		"""
		self._socket = socket.socket()
		self._socket.bind((addr, port))
		self._socket.listen(10)
		
		KBEngine.registerReadFileDescriptor(self._socket.fileno(), self.onRecv)
		
	def stop(self):
		if self._socket:
			KBEngine.deregisterReadFileDescriptor(self._socket.fileno())
			self._socket.close()
			self._socket = None
		
	def onWrite(self, fileno):
		pass
		
	def onRecv(self, fileno):
		if self._socket.fileno() == fileno:
			sock, addr = self._socket.accept()
			self._clients[sock.fileno()] = (sock, addr)
			KBEngine.registerReadFileDescriptor(sock.fileno(), self.onRecv)
			DEBUG_MSG("Poller::onRecv: new connect[%s/%i]" % (addr, sock.fileno()))
		else:
			sock, addr = self._clients.get(fileno, None)
			if sock is None:
				return
			
			data = sock.recv(2048)
			KBEngine.deregisterReadFileDescriptor(sock.fileno())

			DEBUG_MSG("Poller::onRecv: %s/%i get data, size=%i" % (addr, sock.fileno(), len(data)))

			self.processData(sock, addr, data)
			sock.close()

			del self._clients[fileno]
			
	def processData(self, sock, addr, datas):
		"""
		处理接收数据
		"""
		_recv_data = datas.decode()

		DEBUG_MSG("_recvBuf = %r"% _recv_data)

		order = {}
		payid = ""
		cutData = ""
		if _recv_data.find("IIII") != -1:

			cutData = Helper.cutInHttp(_recv_data, 'IIII', 'IIII')
			json_data = Helper.convertDict(cutData, ',', ':')
			payid = json_data["timestamp"]
			order["money"] = float(json_data["number"])
			order["account"] = json_data["account"]

		elif _recv_data.find("{") != -1:
			cutData = Helper.cutHttp(_recv_data, '{', '}')
			json_data = json.loads(cutData)
			payid = json_data["payid"]

			payerName = json_data["payerName"]
			index = payerName.find('|')
			order["money"] = float(json_data["amount"])
			order["account"] = payerName[index + 1:]

		DEBUG_MSG("cutData = %r" % (cutData))

		if not self.checkOrders(payid):
			DEBUG_MSG("orders is no problem!!!")
			orderStr = json.dumps(order)
			KBEngine.chargeResponse(payid, orderStr.encode(), KBEngine.SERVER_SUCCESS)
			self.send(sock,"success")

		self.send(sock,"no this order")

	def checkOrders(self,payid):
		#检测是否重复订单
		#同时清理存在超过30分钟的订单
		if payid == "":
			return True

		for key in self._orders.keys():
			if key == payid:
				return True
		self._orders[payid] = datetime.now()
		orderArray = []
		for key,value in self._orders.items():
			if (datetime.now() - value).seconds >= 36000:
				orderArray.append(key)

		for key in orderArray:
			del self._orders[key]
		return False

	# def send(self, sock):
    #
	# 	body = "success"
	# 	get_str = "HTTP/1.1 200 OK\r\n" \
	# 			  "Content-type: text/html;charset=UTF-8\r\n" \
	# 			  "Content-length: %d\r\n" \
	# 			  "\r\n" % (len(body))
    #
	# 	get_str += body
	# 	sock.send(get_str.encode())

	def send(self, sock,body):

		get_str = "HTTP/1.1 200 OK\r\n" \
				  "Content-type: text/html;charset=UTF-8\r\n" \
				  "Content-length: %d\r\n" \
				  "\r\n" % (len(body))

		get_str += body
		sock.send(get_str.encode('utf8'))
