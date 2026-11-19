#!/usr/bin/python
# -*- coding: UTF-8 -*-
from domain.order import Order
from Model2.Ordering import OrderStatus
from domain.order import Shipment
from domain.order import Payment
from typing import List

class OrderService(object):
	def getOrder(self, aOrderId : int) -> Order:
		pass

	def updateStatus(self, aOrderId : int, aStatus : OrderStatus) -> None:
		pass

	def getShipment(self, aOrderId : int) -> Shipment:
		pass

	def getPayment(self, aOrderId : int) -> Payment:
		pass

	def listOrders(self, aCustomerId : int) -> List:
		pass

